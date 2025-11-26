"""Core tax calculation functions - IR, socials, comparisons."""

from typing import Any

from src.tax_engine.rules import TaxRules


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


def compute_ir(
    person: dict[str, Any],
    income: dict[str, float],
    deductions: dict[str, float],
    rules: TaxRules,
) -> dict[str, float]:
    """Compute income tax (IR).

    Args:
        person: Person data with nb_parts, status
        income: Income data (professional_gross, salary, rental, capital)
        deductions: Deductions (PER, alimony, etc.)
        rules: Tax rules for year

    Returns:
        Dict with:
            - revenu_imposable: Taxable income
            - part_income: Income per part
            - impot_brut: Gross tax
            - impot_net: Net tax after reductions
    """
    # Compute taxable professional income
    taxable_prof = compute_taxable_professional_income(
        regime=person.get("status", "micro_bnc"),
        professional_gross=income.get("professional_gross", 0.0),
        deductible_expenses=income.get("deductible_expenses", 0.0),
        rules=rules,
    )

    # Sum all income sources
    revenu_imposable = (
        taxable_prof
        + income.get("salary", 0.0)
        + income.get("rental_income", 0.0)
        + income.get("capital_income", 0.0)
    )

    # Apply deductions (PER, etc.)
    per_contribution = deductions.get("per_contributions", 0.0)
    # TODO: Apply PER plafond limit
    revenu_imposable -= per_contribution
    revenu_imposable -= deductions.get("alimony", 0.0)
    revenu_imposable -= deductions.get("other_deductions", 0.0)

    revenu_imposable = max(0.0, revenu_imposable)

    # Quotient familial
    nb_parts = person.get("nb_parts", 1.0)
    part_income = revenu_imposable / nb_parts

    # Apply barème
    tax_per_part = apply_bareme(part_income, rules)
    impot_brut = tax_per_part * nb_parts

    # TODO: Apply tax reductions (dons, services, etc.)
    impot_net = max(0.0, impot_brut)

    return {
        "revenu_imposable": round(revenu_imposable, 2),
        "part_income": round(part_income, 2),
        "impot_brut": round(impot_brut, 2),
        "impot_net": round(impot_net, 2),
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
