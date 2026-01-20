"""Core tax calculation functions - IR, socials, comparisons."""

from typing import Any

from src.tax_engine.rules import TaxRules
from src.tax_engine.tax_utils import calculate_tax_reduction


def compute_taxable_professional_income(
    regime: str,
    professional_gross: float,
    deductible_expenses: float,
    rules: TaxRules,
) -> float:
    """Compute taxable professional income based on regime.

    Args:
        regime: Tax regime (micro_bnc, micro_bic_service, reel_bnc, reel_bic)
        professional_gross: Gross professional revenue (CA)
        deductible_expenses: Real deductible expenses (for réel regime)
        rules: Tax rules for the year

    Returns:
        Taxable professional income after abattement or expenses

    Raises:
        KeyError: If regime not supported
    """
    regime_lower = regime.lower()

    if regime_lower.startswith("micro_"):
        # Apply forfait abattement
        abattement_rate = rules.get_abattement(regime_lower)
        return professional_gross * (1 - abattement_rate)
    elif regime_lower.startswith("reel_"):
        # Use real expenses
        return professional_gross - deductible_expenses
    else:
        raise KeyError(f"Unknown regime: {regime}")


def calculate_tmi(revenu_imposable: float, nb_parts: float, rules: TaxRules) -> float:
    """Calculate Taux Marginal d'Imposition (TMI) - centralized function.

    Args:
        revenu_imposable: Total taxable income
        nb_parts: Number of tax parts (quotient familial)
        rules: Tax rules with brackets

    Returns:
        TMI as decimal (0.0, 0.11, 0.30, 0.41, or 0.45)
    """
    part_income = revenu_imposable / nb_parts
    brackets = rules.income_tax_brackets

    # Find the bracket containing the part_income
    # TMI is the rate of the highest bracket that the income reaches
    current_tmi = 0.0

    for bracket in brackets:
        lower = bracket["lower_bound"]
        upper = bracket["upper_bound"]

        if upper is None:
            # Last bracket (no upper limit)
            if part_income > lower:
                current_tmi = bracket["rate"]
        else:
            if part_income > lower:
                current_tmi = bracket["rate"]

    return current_tmi


def apply_bareme(part_income: float, rules: TaxRules) -> float:
    """Apply progressive tax brackets to part income.

    Args:
        part_income: Income after quotient familial (revenu / nb_parts)
        rules: Tax rules with brackets

    Returns:
        Tax amount for one part
    """
    tax = 0.0
    brackets = rules.income_tax_brackets

    for bracket in brackets:
        rate = bracket["rate"]
        lower = bracket["lower_bound"]
        upper = bracket["upper_bound"]

        # Determine taxable income in this bracket
        if upper is None:
            # Last bracket (no upper limit)
            if part_income > lower:
                taxable_in_bracket = part_income - lower
                tax += taxable_in_bracket * rate
        else:
            if part_income > lower:
                taxable_in_bracket = min(part_income, upper) - lower
                tax += taxable_in_bracket * rate

    return tax


def apply_bareme_detailed(
    part_income: float, rules: TaxRules
) -> tuple[float, list[dict[str, float]]]:
    """Apply progressive tax brackets with detailed breakdown.

    Args:
        part_income: Income after quotient familial (revenu / nb_parts)
        rules: Tax rules with brackets

    Returns:
        Tuple of (total_tax, brackets_detail) where brackets_detail contains:
            - rate: Tax rate for this bracket
            - income_in_bracket: Amount of income taxed in this bracket
            - tax_in_bracket: Tax amount for this bracket
    """
    tax = 0.0
    brackets_detail = []
    brackets = rules.income_tax_brackets

    for bracket in brackets:
        rate = bracket["rate"]
        lower = bracket["lower_bound"]
        upper = bracket["upper_bound"]

        # Determine taxable income in this bracket
        if upper is None:
            # Last bracket (no upper limit)
            if part_income > lower:
                taxable_in_bracket = part_income - lower
                tax_in_bracket = taxable_in_bracket * rate
                tax += tax_in_bracket
                brackets_detail.append(
                    {
                        "rate": rate,
                        "income_in_bracket": round(taxable_in_bracket, 2),
                        "tax_in_bracket": round(tax_in_bracket, 2),
                    }
                )
        else:
            if part_income > lower:
                taxable_in_bracket = min(part_income, upper) - lower
                tax_in_bracket = taxable_in_bracket * rate
                tax += tax_in_bracket
                brackets_detail.append(
                    {
                        "rate": rate,
                        "income_in_bracket": round(taxable_in_bracket, 2),
                        "tax_in_bracket": round(tax_in_bracket, 2),
                    }
                )

    return tax, brackets_detail


def apply_per_deduction_with_limit(
    per_contribution: float,
    professional_income: float,
    rules: TaxRules,
) -> tuple[float, float, float]:
    """Apply PER deduction with plafond limit.

    Args:
        per_contribution: PER contribution amount declared
        professional_income: Professional income (for plafond calculation)
        rules: Tax rules with PER plafonds

    Returns:
        Tuple of (deductible_amount, excess_amount, plafond_calculated)
    """
    # Get PER plafond rules from baremes
    per_plafonds = rules.per_plafonds
    base_rate = per_plafonds.get("base_rate", 0.10)
    min_plafond = per_plafonds.get("min_plafond", 4399)
    max_plafond = per_plafonds.get("max_salarie", 35194)

    # Calculate plafond: 10% of professional income
    plafond = professional_income * base_rate

    # Apply min/max limits (min_plafond from config, not hardcoded)
    plafond = max(min_plafond, min(plafond, max_plafond))

    # Determine deductible and excess
    if per_contribution <= plafond:
        return per_contribution, 0.0, plafond
    else:
        return plafond, per_contribution - plafond, plafond


def apply_tax_reductions(
    impot_brut: float,
    revenu_imposable: float,
    reductions_data: dict[str, float],
    rules: TaxRules,
) -> tuple[float, dict[str, float]]:
    """Apply tax reductions and credits.

    Args:
        impot_brut: Gross tax amount
        revenu_imposable: Taxable income (for plafond calculations)
        reductions_data: Dict with reduction amounts:
            - dons: Donations amount
            - services_personne: Services à la personne expenses
            - frais_garde: Childcare expenses
            - children_under_6: Number of children under 6 (for garde plafond)
        rules: Tax rules with reduction rates and plafonds

    Returns:
        Tuple of (impot_net, reductions_applied_dict)
    """
    reductions_applied = {}
    total_reduction = 0.0

    # 1. Dons - Use centralized function
    dons = reductions_data.get("dons", 0.0)
    if dons > 0:
        reduction_dons, _ = calculate_tax_reduction(
            "dons", dons, rules, revenu_imposable=revenu_imposable
        )
        reductions_applied["dons"] = reduction_dons
        total_reduction += reduction_dons

    # 2. Services à la personne - Use centralized function
    services = reductions_data.get("services_personne", 0.0)
    if services > 0:
        credit_services, _ = calculate_tax_reduction(
            "services_personne", services, rules
        )
        reductions_applied["services_personne"] = credit_services
        total_reduction += credit_services

    # 3. Frais de garde - Use centralized function
    frais_garde = reductions_data.get("frais_garde", 0.0)
    children_under_6 = reductions_data.get("children_under_6", 0)
    if frais_garde > 0 and children_under_6 > 0:
        credit_garde, _ = calculate_tax_reduction(
            "frais_garde", frais_garde, rules, children_under_6=children_under_6
        )
        reductions_applied["frais_garde"] = credit_garde
        total_reduction += credit_garde

    # Apply reductions to gross tax
    impot_net = max(0.0, impot_brut - total_reduction)

    return impot_net, reductions_applied


def compute_ir(
    person: dict[str, Any],
    income: dict[str, float],
    deductions: dict[str, float],
    rules: TaxRules,
) -> dict[str, Any]:
    """Compute income tax (IR).

    Args:
        person: Person data with:
            - nb_parts: Number of fiscal parts (quotient familial)
            - status: Tax regime (micro_bnc, micro_bic_service, reel_bnc, etc.)
            - situation_familiale: 'couple' (married/PACS joint) or 'celibataire'
              (single, divorced, widowed, separate filing). Used for CEHR brackets.
              Defaults to 'celibataire' if not provided.
        income: Income data (professional_gross, salary, rental, capital)
        deductions: Deductions (PER, alimony, etc.) and tax reductions data
        rules: Tax rules for year

    Returns:
        Dict with:
            - revenu_imposable: Taxable income after deductions
            - rfr: Revenu Fiscal de Référence (different from revenu_imposable)
            - part_income: Income per part
            - impot_brut: Gross tax before reductions
            - impot_net: Net tax after reductions (including CEHR and CDHR)
            - impot_ir_seul: IR without CEHR/CDHR
            - tmi: Marginal tax rate (0.0, 0.11, 0.30, 0.41, 0.45)
            - tax_reductions: Dict of applied reductions
            - brackets: List of bracket details
            - per_deduction_applied: PER amount actually deducted
            - per_deduction_excess: PER amount exceeding plafond
            - per_plafond_detail: Dict with {applied, excess, plafond_max}
            - cehr: CEHR amount (0 if below threshold)
            - cehr_detail: CEHR bracket details (empty if not applicable)
            - cdhr: CDHR amount (0 if below threshold or effective rate >= 20%)
            - cdhr_detail: CDHR calculation details (empty if not applicable)
    """
    # Compute taxable professional income
    taxable_prof = compute_taxable_professional_income(
        regime=person.get("status", "micro_bnc"),
        professional_gross=income.get("professional_gross", 0.0),
        deductible_expenses=income.get("deductible_expenses", 0.0),
        rules=rules,
    )

    # Sum all income sources (before deductions)
    total_income = (
        taxable_prof
        + income.get("salary", 0.0)
        + income.get("rental_income", 0.0)
        + income.get("capital_income", 0.0)
    )

    # Apply PER deduction with plafond limit
    per_contribution = deductions.get("per_contributions", 0.0)
    per_deduction, per_excess, per_plafond = apply_per_deduction_with_limit(
        per_contribution=per_contribution,
        professional_income=taxable_prof,
        rules=rules,
    )

    # Apply other deductions
    revenu_imposable = total_income - per_deduction
    revenu_imposable -= deductions.get("alimony", 0.0)
    revenu_imposable -= deductions.get("other_deductions", 0.0)

    revenu_imposable = max(0.0, revenu_imposable)

    # Quotient familial
    nb_parts = person.get("nb_parts", 1.0)
    part_income = revenu_imposable / nb_parts

    # Calculate TMI
    tmi = calculate_tmi(revenu_imposable, nb_parts, rules)

    # Apply barème with detailed breakdown
    tax_per_part, brackets_detail = apply_bareme_detailed(part_income, rules)
    impot_brut = tax_per_part * nb_parts

    # Apply tax reductions (dons, services à la personne, frais de garde)
    reductions_data = {
        "dons": deductions.get("dons_declared", 0.0),
        "services_personne": deductions.get("services_personne_declared", 0.0),
        "frais_garde": deductions.get("frais_garde_declared", 0.0),
        "children_under_6": deductions.get("children_under_6", 0),
    }
    impot_net, tax_reductions = apply_tax_reductions(
        impot_brut=impot_brut,
        revenu_imposable=revenu_imposable,
        reductions_data=reductions_data,
        rules=rules,
    )

    # Build PER plafond detail for LLM context
    per_plafond_detail = None
    if per_contribution > 0 or per_deduction > 0:
        per_plafond_detail = {
            "applied": round(per_deduction, 2),
            "excess": round(per_excess, 2),
            "plafond_max": round(per_plafond, 2),
        }

    # Calculate RFR (Revenu Fiscal de Référence)
    # RFR = revenu_imposable + items that were deducted but must be reintegrated
    # Key difference: PER contributions are deducted from RI but included in RFR
    rfr = revenu_imposable + per_deduction  # Reintegrate PER deduction
    # Note: Other items to reintegrate in real RFR: certain abattements,
    # plus-values with specific regimes, etc. Simplified here for main case.

    # Get situation_familiale for CEHR/CDHR brackets (not nb_parts!)
    # 'couple' = married/PACS with joint filing (imposition commune)
    # 'celibataire' = single, divorced, widowed, or separate filing
    situation_familiale = person.get("situation_familiale", "celibataire")

    # Compute CEHR (Contribution Exceptionnelle sur les Hauts Revenus)
    # CEHR is based on RFR, NOT revenu_imposable
    cehr_amount, cehr_detail = compute_cehr(rfr, situation_familiale, rules)

    # Compute CDHR (Contribution Différentielle sur les Hauts Revenus) - NEW 2025
    # CDHR ensures minimum 20% effective tax rate on high incomes
    cdhr_amount, cdhr_detail = compute_cdhr(
        rfr=rfr,
        impot_ir=impot_net,  # IR after reductions, before CEHR
        cehr=cehr_amount,
        situation_familiale=situation_familiale,
        rules=rules,
    )

    # Add CEHR and CDHR to total tax
    impot_total = impot_net + cehr_amount + cdhr_amount

    return {
        "revenu_imposable": round(revenu_imposable, 2),
        "rfr": round(rfr, 2),
        "part_income": round(part_income, 2),
        "impot_brut": round(impot_brut, 2),
        "impot_net": round(impot_total, 2),  # Total includes CEHR + CDHR
        "impot_ir_seul": round(impot_net, 2),  # IR without CEHR/CDHR
        "tmi": tmi,
        "tax_reductions": tax_reductions,
        "brackets": brackets_detail,
        "per_deduction_applied": round(per_deduction, 2),
        "per_deduction_excess": round(per_excess, 2),
        "per_plafond_detail": per_plafond_detail,
        "cehr": cehr_amount,
        "cehr_detail": cehr_detail,
        "cdhr": cdhr_amount,
        "cdhr_detail": cdhr_detail,
    }


def compute_socials(
    person: dict[str, Any],
    income: dict[str, float],
    social_data: dict[str, float],
    rules: TaxRules,
) -> dict[str, float]:
    """Compute social contributions (URSSAF).

    Args:
        person: Person data with status
        income: Income data
        social_data: Declared URSSAF data
        rules: Tax rules

    Returns:
        Dict with:
            - urssaf_expected: Expected contributions
            - urssaf_paid: Declared paid contributions
            - delta: Difference (negative = underpaid)
    """
    status = person.get("status", "micro_bnc").lower()

    # Determine URSSAF rate based on activity
    if "bnc" in status:
        activity = "liberal_bnc"
    elif "bic" in status:
        activity = "commercial_bic"
    else:
        activity = "liberal_bnc"  # Default

    try:
        rate = rules.get_urssaf_rate(activity)
    except KeyError:
        rate = 0.22  # Default fallback

    # Calculate expected based on declared CA
    declared_ca = social_data.get("urssaf_declared_ca", 0.0)
    urssaf_expected = declared_ca * rate

    urssaf_paid = social_data.get("urssaf_paid", 0.0)
    delta = urssaf_paid - urssaf_expected

    return {
        "urssaf_expected": round(urssaf_expected, 2),
        "urssaf_paid": round(urssaf_paid, 2),
        "delta": round(delta, 2),
        "rate_used": rate,
    }


def compare_micro_vs_reel(
    person: dict[str, Any],
    income: dict[str, float],
    deductions: dict[str, float],
    rules: TaxRules,
    socials_micro: dict | None = None,
    socials_reel: dict | None = None,
) -> dict[str, Any]:
    """Compare micro vs réel regime tax impact.

    Args:
        person: Person data
        income: Income data with professional_gross and deductible_expenses
        deductions: Deductions
        rules: Tax rules
        socials_micro: Pre-calculated social contributions for micro (optional)
        socials_reel: Pre-calculated social contributions for réel (optional)

    Returns:
        Dict with complete comparison data compatible with ComparisonMicroReel:
            - regime_actuel: Current regime
            - regime_compare: Compared regime
            - impot_actuel/compare: Tax amounts
            - cotisations_actuelles/comparees: Social contributions
            - delta_impot/cotisations/total: Differences
            - economie_potentielle: Absolute savings
            - pourcentage_economie: Savings percentage
            - recommendation: Regime recommendation
            - justification: Detailed explanation
            - chiffre_affaires: Revenue used
            - charges_reelles: Real expenses
            - taux_abattement_micro: Micro abattement rate
    """
    # Detect current regime type (BNC or BIC)
    current_regime = person.get("status", "micro_bnc").lower()
    if "bnc" in current_regime:
        micro_regime = "micro_bnc"
        reel_regime = "reel_bnc"
        abattement_rate = rules.get_abattement("micro_bnc")
    else:
        # Default to service for BIC
        micro_regime = "micro_bic_service"
        reel_regime = "reel_bic"
        abattement_rate = rules.get_abattement("micro_bic_service")

    # Determine actual vs compared regime
    is_currently_micro = "micro" in current_regime
    regime_actuel = micro_regime if is_currently_micro else reel_regime
    regime_compare = reel_regime if is_currently_micro else micro_regime

    # Compute IR with micro regime
    person_micro = {**person, "status": micro_regime}
    ir_micro = compute_ir(person_micro, income, deductions, rules)

    # Compute IR with réel regime
    person_reel = {**person, "status": reel_regime}
    ir_reel = compute_ir(person_reel, income, deductions, rules)

    # Get social contributions (same for both regimes normally)
    cotis_micro = socials_micro.get("urssaf_expected", 0.0) if socials_micro else 0.0
    cotis_reel = socials_reel.get("urssaf_expected", 0.0) if socials_reel else 0.0

    # Calculate deltas
    delta_impot = ir_reel["impot_net"] - ir_micro["impot_net"]
    delta_cotis = cotis_reel - cotis_micro
    delta_total = delta_impot + delta_cotis

    # Total charges
    charge_micro = ir_micro["impot_net"] + cotis_micro
    charge_reel = ir_reel["impot_net"] + cotis_reel

    # Determine recommendation
    economie_potentielle = abs(delta_total)
    pourcentage_economie = (
        (economie_potentielle / max(charge_micro, 1)) * 100 if charge_micro > 0 else 0.0
    )

    if delta_total < -100:
        recommendation = "Passer au réel"
        justification = (
            f"Économie de {economie_potentielle:.0f}€ ({pourcentage_economie:.1f}%) "
            f"en passant au régime réel."
        )
    elif delta_total > 100:
        recommendation = "Rester en micro"
        justification = (
            f"Économie de {economie_potentielle:.0f}€ ({pourcentage_economie:.1f}%) "
            f"en restant en micro."
        )
    else:
        recommendation = "Rester en micro"
        justification = (
            "Différence négligeable. Le micro est recommandé pour sa simplicité."
        )

    # Extract context
    chiffre_affaires = income.get("professional_gross", 0.0)
    charges_reelles = income.get("deductible_expenses", 0.0)

    return {
        "regime_actuel": regime_actuel,
        "regime_compare": regime_compare,
        "impot_actuel": (
            ir_micro["impot_net"] if is_currently_micro else ir_reel["impot_net"]
        ),
        "impot_compare": (
            ir_reel["impot_net"] if is_currently_micro else ir_micro["impot_net"]
        ),
        "delta_impot": round(delta_impot, 2),
        "cotisations_actuelles": cotis_micro if is_currently_micro else cotis_reel,
        "cotisations_comparees": cotis_reel if is_currently_micro else cotis_micro,
        "delta_cotisations": round(delta_cotis, 2),
        "charge_totale_actuelle": (
            round(charge_micro, 2) if is_currently_micro else round(charge_reel, 2)
        ),
        "charge_totale_comparee": (
            round(charge_reel, 2) if is_currently_micro else round(charge_micro, 2)
        ),
        "delta_total": round(delta_total, 2),
        "economie_potentielle": round(economie_potentielle, 2),
        "pourcentage_economie": round(pourcentage_economie, 2),
        "recommendation": recommendation,
        "justification": justification,
        "chiffre_affaires": chiffre_affaires,
        "charges_reelles": charges_reelles,
        "taux_abattement_micro": abattement_rate,
    }


def compute_cehr(
    revenu_fiscal_reference: float,
    situation_familiale: str,
    rules: TaxRules,
) -> tuple[float, list[dict[str, Any]]]:
    """Compute CEHR (Contribution Exceptionnelle sur les Hauts Revenus).

    Args:
        revenu_fiscal_reference: Revenu fiscal de référence (RFR)
            Note: RFR includes PER contributions and other items deducted from
            revenu_imposable. It is NOT the same as revenu_imposable.
        situation_familiale: Family status for CEHR bracket selection.
            'couple' for married/PACS with joint filing (imposition commune)
            'celibataire' for single, divorced, widowed, or separate filing
        rules: Tax rules with CEHR brackets

    Returns:
        Tuple of (cehr_amount, brackets_detail)

    Note:
        CEHR brackets differ between single (250k/500k thresholds) and
        couple (500k/1M thresholds). The situation_familiale determines
        which brackets apply, NOT the number of parts (nb_parts).
        A single parent with 2 children (nb_parts=2.0) uses 'celibataire' brackets.
    """
    cehr_config = rules.cehr
    if not cehr_config:
        return 0.0, []

    # Use explicit situation_familiale - do NOT infer from nb_parts
    # A single parent with children (nb_parts >= 2) still uses celibataire brackets
    is_couple = situation_familiale.lower() == "couple"
    brackets = cehr_config.get("couple" if is_couple else "celibataire", [])

    cehr = 0.0
    brackets_detail = []

    for bracket in brackets:
        rate = bracket["rate"]
        lower = bracket["lower_bound"]
        upper = bracket.get("upper_bound")

        if upper is None:
            # Last bracket (no upper limit)
            if revenu_fiscal_reference > lower:
                taxable_in_bracket = revenu_fiscal_reference - lower
                tax_in_bracket = taxable_in_bracket * rate
                cehr += tax_in_bracket
                brackets_detail.append(
                    {
                        "rate": rate,
                        "income_in_bracket": round(taxable_in_bracket, 2),
                        "cehr_in_bracket": round(tax_in_bracket, 2),
                    }
                )
        else:
            if revenu_fiscal_reference > lower:
                taxable_in_bracket = min(revenu_fiscal_reference, upper) - lower
                tax_in_bracket = taxable_in_bracket * rate
                cehr += tax_in_bracket
                brackets_detail.append(
                    {
                        "rate": rate,
                        "income_in_bracket": round(taxable_in_bracket, 2),
                        "cehr_in_bracket": round(tax_in_bracket, 2),
                    }
                )

    return round(cehr, 2), brackets_detail


def compute_cdhr(
    rfr: float,
    impot_ir: float,
    cehr: float,
    situation_familiale: str,
    rules: TaxRules,
) -> tuple[float, dict[str, Any]]:
    """Compute CDHR (Contribution Différentielle sur les Hauts Revenus) - NEW 2025.

    The CDHR ensures a minimum effective tax rate of 20% on high incomes.
    It applies when (IR + CEHR) / RFR < 20% for high-income taxpayers.

    Args:
        rfr: Revenu Fiscal de Référence
        impot_ir: Income tax amount (after reductions, before CEHR)
        cehr: CEHR amount already calculated
        situation_familiale: 'couple' or 'celibataire' for threshold selection
        rules: Tax rules with CDHR configuration

    Returns:
        Tuple of (cdhr_amount, detail_dict)

    Note:
        CDHR was introduced in 2025 (Loi de Finances 2025).
        It is CUMULATIVE with CEHR - both can apply to the same taxpayer.

    Sources:
        - https://www.impots.gouv.fr/actualite/contribution-differentielle-sur-les-hauts-revenus-cdhr
        - Loi de Finances 2025
    """
    cdhr_config = rules.cdhr
    if not cdhr_config:
        return 0.0, {}

    # Get threshold based on situation (same logic as CEHR)
    is_couple = situation_familiale.lower() == "couple"
    threshold = cdhr_config.get(
        "seuil_couple" if is_couple else "seuil_celibataire", 250000
    )
    target_rate = cdhr_config.get("taux_cible", 0.20)  # 20% minimum effective rate

    # CDHR only applies above the threshold
    if rfr <= threshold:
        return 0.0, {}

    # Calculate current effective tax rate
    # Effective rate = (IR + CEHR) / RFR
    total_tax_before_cdhr = impot_ir + cehr
    effective_rate = total_tax_before_cdhr / rfr if rfr > 0 else 0.0

    # If effective rate is already >= 20%, no CDHR needed
    if effective_rate >= target_rate:
        return 0.0, {
            "applicable": False,
            "reason": "Taux effectif déjà >= 20%",
            "taux_effectif": round(effective_rate, 4),
            "taux_cible": target_rate,
        }

    # CDHR = (target_rate × RFR) - (IR + CEHR)
    # This brings the total tax up to 20% of RFR
    target_tax = target_rate * rfr
    cdhr_amount = target_tax - total_tax_before_cdhr

    # CDHR cannot be negative
    cdhr_amount = max(0.0, cdhr_amount)

    detail = {
        "applicable": True,
        "rfr": round(rfr, 2),
        "seuil": threshold,
        "ir_avant_cdhr": round(impot_ir, 2),
        "cehr": round(cehr, 2),
        "taux_effectif_avant": round(effective_rate, 4),
        "taux_cible": target_rate,
        "impot_cible": round(target_tax, 2),
        "cdhr": round(cdhr_amount, 2),
        "taux_effectif_apres": round((total_tax_before_cdhr + cdhr_amount) / rfr, 4),
    }

    return round(cdhr_amount, 2), detail


def compute_pas_result(impot_net: float, pas_withheld: float) -> dict[str, float]:
    """Compute PAS (prélèvement à la source) result.

    Args:
        impot_net: Net tax owed
        pas_withheld: Amount already withheld via PAS

    Returns:
        Dict with:
            - impot_net: Total tax owed
            - pas_withheld: Amount already paid
            - due_now: Amount due (or refund if negative)
    """
    due = impot_net - pas_withheld

    return {
        "impot_net": round(impot_net, 2),
        "pas_withheld": round(pas_withheld, 2),
        "due_now": round(due, 2),
    }
