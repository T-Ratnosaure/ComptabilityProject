"""Utility functions for tax calculations - single source of truth.

This module provides reusable tax calculation utilities to avoid duplication
across the codebase. All fiscal logic should be centralized here or in core.py.

Key principles:
- Single source of truth: All values come from baremes JSON via TaxRules
- No hardcoded values: Everything is configurable
- Reusable: Used by both tax_engine and analyzers
- Testable: Pure functions with clear inputs/outputs
"""

from src.tax_engine.rules import TaxRules


def calculate_per_plafond(
    professional_income: float,
    rules: TaxRules,
    status: str = "salarie",
) -> float:
    """Calculate PER (Plan Épargne Retraite) deduction ceiling.

    Args:
        professional_income: Annual professional income (for plafond calculation)
        rules: Tax rules with PER plafonds
        status: Professional status ("salarie", "tns", "married_salarie")

    Returns:
        PER plafond in euros

    Example:
        >>> rules = get_tax_rules(2024)
        >>> calculate_per_plafond(50000, rules, "salarie")
        5000.0  # 10% of 50k, capped at min/max
    """
    per_plafonds = rules.per_plafonds
    base_rate = per_plafonds.get("base_rate", 0.10)

    # Calculate base plafond (10% of income)
    plafond = professional_income * base_rate

    # Get min/max limits from baremes
    # Note: min_plafond will be added to baremes_2024.json in future update
    min_plafond = 4399  # Official value for 2024

    # Max depends on status
    max_key = f"max_{status}"
    max_plafond = per_plafonds.get(max_key, per_plafonds.get("max_salarie", 35194))

    # Apply limits
    plafond = max(min_plafond, min(plafond, max_plafond))

    return round(plafond, 2)


def get_tax_reduction_rate(reduction_type: str, rules: TaxRules) -> float:
    """Get tax reduction/credit rate for a specific type.

    Args:
        reduction_type: Type of reduction ("dons", "services_personne", "frais_garde")
        rules: Tax rules with reduction rates

    Returns:
        Reduction rate as decimal (e.g., 0.66 for 66%)

    Raises:
        KeyError: If reduction type not found

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_tax_reduction_rate("dons", rules)
        0.66
    """
    reductions = rules.tax_reductions
    if reduction_type not in reductions:
        raise KeyError(f"Unknown reduction type: {reduction_type}")
    return reductions[reduction_type]["rate"]


def get_tax_reduction_plafond(
    reduction_type: str,
    rules: TaxRules,
    revenu_imposable: float = 0.0,
    children_under_6: int = 0,
) -> float:
    """Get tax reduction plafond (ceiling) for a specific type.

    Args:
        reduction_type: Type of reduction
        rules: Tax rules
        revenu_imposable: Taxable income (for percentage-based plafonds like dons)
        children_under_6: Number of children under 6 (for frais_garde)

    Returns:
        Plafond in euros

    Raises:
        KeyError: If reduction type not found

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_tax_reduction_plafond("dons", rules, 50000)
        10000.0  # 20% of 50k
        >>> get_tax_reduction_plafond("services_personne", rules)
        12000.0  # Fixed plafond
    """
    reductions = rules.tax_reductions
    if reduction_type not in reductions:
        raise KeyError(f"Unknown reduction type: {reduction_type}")

    reduction_config = reductions[reduction_type]

    if reduction_type == "dons":
        # Percentage-based plafond
        plafond_rate = reduction_config.get("plafond_rate", 0.20)
        return revenu_imposable * plafond_rate

    elif reduction_type == "services_personne":
        # Fixed plafond (first year has higher limit, but we use standard here)
        return reduction_config.get("plafond", 12000)

    elif reduction_type == "frais_garde":
        # Per-child plafond
        plafond_per_child = reduction_config.get("plafond_per_child", 3500)
        return plafond_per_child * children_under_6

    else:
        # Should not reach here if reduction_type validation passed
        raise KeyError(f"Unknown reduction type: {reduction_type}")


def calculate_tax_reduction(
    reduction_type: str,
    amount: float,
    rules: TaxRules,
    revenu_imposable: float = 0.0,
    children_under_6: int = 0,
) -> tuple[float, float]:
    """Calculate tax reduction/credit with plafond.

    Args:
        reduction_type: Type of reduction
        amount: Amount spent/donated
        rules: Tax rules
        revenu_imposable: Taxable income (for percentage plafonds)
        children_under_6: Number of children under 6

    Returns:
        Tuple of (reduction_amount, amount_exceeding_plafond)

    Example:
        >>> rules = get_tax_rules(2024)
        >>> calculate_tax_reduction("dons", 1000, rules, 50000)
        (660.0, 0.0)  # 66% of 1000, within plafond
    """
    # Get rate and plafond
    rate = get_tax_reduction_rate(reduction_type, rules)
    plafond = get_tax_reduction_plafond(
        reduction_type, rules, revenu_imposable, children_under_6
    )

    # Calculate eligible amount (capped at plafond)
    eligible_amount = min(amount, plafond)
    excess_amount = max(0.0, amount - plafond)

    # Calculate reduction
    reduction = eligible_amount * rate

    return round(reduction, 2), round(excess_amount, 2)


def get_micro_threshold(regime_type: str, rules: TaxRules) -> int:
    """Get CA threshold for micro-regime.

    Args:
        regime_type: Type of regime ("bnc", "bic_service", "bic_vente")
        rules: Tax rules with plafonds_micro

    Returns:
        Threshold in euros

    Raises:
        KeyError: If regime type not found

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_micro_threshold("bnc", rules)
        77700
    """
    plafonds = rules.plafonds_micro
    if regime_type not in plafonds:
        raise KeyError(f"Unknown regime type: {regime_type}")
    return plafonds[regime_type]


def get_micro_abattement(regime_type: str, rules: TaxRules) -> float:
    """Get abattement rate for micro-regime.

    Args:
        regime_type: Full regime name (e.g., "micro_bnc", "micro_bic_service")
        rules: Tax rules with abattements

    Returns:
        Abattement rate as decimal (e.g., 0.34 for 34%)

    Raises:
        KeyError: If regime not found

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_micro_abattement("micro_bnc", rules)
        0.34
    """
    return rules.get_abattement(regime_type)


def check_micro_threshold_proximity(
    revenue: float, regime_type: str, rules: TaxRules, alert_threshold: float = 0.85
) -> dict[str, float | bool]:
    """Check if revenue is approaching micro-regime threshold.

    Args:
        revenue: Annual revenue
        regime_type: Type of regime ("bnc", "bic_service", "bic_vente")
        rules: Tax rules
        alert_threshold: Alert when revenue reaches this % of threshold (default 85%)

    Returns:
        Dict with:
            - approaching: bool, True if within alert zone
            - threshold: int, The threshold value
            - proximity_rate: float, revenue / threshold
            - remaining: float, euros remaining before threshold

    Example:
        >>> rules = get_tax_rules(2024)
        >>> check_micro_threshold_proximity(70000, "bnc", rules)
        {
            "approaching": True,
            "threshold": 77700,
            "proximity_rate": 0.90,
            "remaining": 7700.0
        }
    """
    threshold = get_micro_threshold(regime_type, rules)
    proximity_rate = revenue / threshold if threshold > 0 else 0.0
    remaining = threshold - revenue

    return {
        "approaching": proximity_rate >= alert_threshold and proximity_rate < 1.0,
        "threshold": threshold,
        "proximity_rate": round(proximity_rate, 4),
        "remaining": round(remaining, 2),
    }
