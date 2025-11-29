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
) -> tuple[float, float]:
    """Apply PER deduction with plafond limit.

    Args:
        per_contribution: PER contribution amount declared
        professional_income: Professional income (for plafond calculation)
        rules: Tax rules with PER plafonds

    Returns:
        Tuple of (deductible_amount, excess_amount)
    """
    # Get PER plafond rules from baremes
    per_plafonds = rules.per_plafonds
    base_rate = per_plafonds.get("base_rate", 0.10)
    max_plafond = per_plafonds.get("max_salarie", 35194)

    # Calculate plafond: 10% of professional income
    plafond = professional_income * base_rate

    # Apply min/max limits
    plafond = max(4399, min(plafond, max_plafond))

    # Determine deductible and excess
    if per_contribution <= plafond:
        return per_contribution, 0.0
    else:
        return plafond, per_contribution - plafond


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
        person: Person data with nb_parts, status
        income: Income data (professional_gross, salary, rental, capital)
        deductions: Deductions (PER, alimony, etc.) and tax reductions data
        rules: Tax rules for year

    Returns:
        Dict with:
            - revenu_imposable: Taxable income after deductions
            - part_income: Income per part
            - impot_brut: Gross tax before reductions
            - impot_net: Net tax after reductions
            - tmi: Marginal tax rate (0.0, 0.11, 0.30, 0.41, 0.45)
            - tax_reductions: Dict of applied reductions
            - brackets: List of bracket details
            - per_deduction_applied: PER amount actually deducted
            - per_deduction_excess: PER amount exceeding plafond
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
    per_deduction, per_excess = apply_per_deduction_with_limit(
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

    return {
        "revenu_imposable": round(revenu_imposable, 2),
        "part_income": round(part_income, 2),
        "impot_brut": round(impot_brut, 2),
        "impot_net": round(impot_net, 2),
        "tmi": tmi,
        "tax_reductions": tax_reductions,
        "brackets": brackets_detail,
        "per_deduction_applied": round(per_deduction, 2),
        "per_deduction_excess": round(per_excess, 2),
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
) -> dict[str, Any]:
    """Compare micro vs réel regime tax impact.

    Args:
        person: Person data
        income: Income data with professional_gross and deductible_expenses
        deductions: Deductions
        rules: Tax rules

    Returns:
        Dict with:
            - impot_micro: Tax with micro regime
            - impot_reel: Tax with réel regime
            - delta: Difference (negative = réel is better)
            - recommendation: Which regime is recommended
    """
    # Detect current regime type (BNC or BIC)
    current_regime = person.get("status", "micro_bnc").lower()
    if "bnc" in current_regime:
        micro_regime = "micro_bnc"
        reel_regime = "reel_bnc"
    else:
        # Default to service for BIC
        micro_regime = "micro_bic_service"
        reel_regime = "reel_bic"

    # Compute IR with micro regime
    person_micro = {**person, "status": micro_regime}
    ir_micro = compute_ir(person_micro, income, deductions, rules)

    # Compute IR with réel regime
    person_reel = {**person, "status": reel_regime}
    ir_reel = compute_ir(person_reel, income, deductions, rules)

    delta = ir_reel["impot_net"] - ir_micro["impot_net"]

    recommendation = "reel" if delta < -100 else "micro"
    recommendation_reason = (
        "Réel recommandé (économie fiscale significative)"
        if delta < -100
        else "Micro recommandé (simplicité et avantage fiscal)"
    )

    return {
        "impot_micro": ir_micro["impot_net"],
        "impot_reel": ir_reel["impot_net"],
        "delta": round(delta, 2),
        "recommendation": recommendation,
        "recommendation_reason": recommendation_reason,
    }


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
