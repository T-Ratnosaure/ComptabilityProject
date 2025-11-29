"""Test PER plafond synchronization across all sources.

This test ensures that the PER plafond values are consistent across:
- baremes_2024.json (source of truth)
- per_rules.json (strategies configuration)
- core.py (tax calculation engine)

Official source: https://www.service-public.fr/particuliers/vosdroits/F34982
Official values for 2024:
- Base rate: 10% of professional income
- Min plafond: 4,399 €
- Max plafond (salarié): 35,194 €
"""

import json
from pathlib import Path

import pytest

from src.tax_engine.core import apply_per_deduction_with_limit
from src.tax_engine.rules import get_tax_rules
from src.tax_engine.tax_utils import calculate_per_plafond


class TestPERPlafondSync:
    """Test PER plafond value synchronization."""

    def test_baremes_2024_has_correct_value(self):
        """Verify baremes_2024.json has the official value."""
        baremes_path = Path("src/tax_engine/data/baremes_2024.json")
        with open(baremes_path, encoding="utf-8") as f:
            baremes = json.load(f)

        per_plafonds = baremes["per_plafonds"]
        assert per_plafonds["base_rate"] == 0.10
        assert per_plafonds["max_salarie"] == 35194  # Official value

    def test_per_rules_has_correct_value(self):
        """Verify per_rules.json has the same value as baremes."""
        per_rules_path = Path("src/analyzers/rules/per_rules.json")
        with open(per_rules_path, encoding="utf-8") as f:
            per_rules = json.load(f)

        plafond_calc = per_rules["rules"]["plafond_calculation"]
        assert plafond_calc["rate"] == 0.10
        assert plafond_calc["min_plafond"] == 4399
        assert plafond_calc["max_plafond"] == 35194  # Must match baremes

    def test_core_uses_correct_value(self):
        """Verify core.py uses the value from baremes via TaxRules."""
        rules = get_tax_rules(2024)

        # Test with high income (should hit max plafond)
        per_contribution = 40000
        professional_income = 500000  # High income

        deductible, excess = apply_per_deduction_with_limit(
            per_contribution, professional_income, rules
        )

        # At 500k income, 10% = 50k, but capped at max_salarie (35194)
        # So excess should be: 40000 - 35194 = 4806
        assert deductible == 35194  # Max plafond for salarié
        assert excess == per_contribution - 35194

    def test_per_strategy_calculates_correctly(self):
        """Verify PER strategy uses correct plafond value."""
        rules = get_tax_rules(2024)

        # High income should hit max plafond
        plafond = calculate_per_plafond(500000, rules, status="salarie")
        assert plafond == 35194  # Max plafond

    def test_min_plafond_respected(self):
        """Verify minimum plafond is respected."""
        rules = get_tax_rules(2024)

        # Low income (less than 4399 / 0.10 = 43990)
        per_contribution = 5000
        professional_income = 10000  # 10% = 1000, but min is 4399

        deductible, excess = apply_per_deduction_with_limit(
            per_contribution, professional_income, rules
        )

        # Min plafond is 4399
        assert deductible == 4399
        assert excess == per_contribution - 4399

    def test_normal_case_10_percent(self):
        """Verify normal case: 10% of income."""
        rules = get_tax_rules(2024)

        professional_income = 50000
        per_contribution = 5000  # Exactly 10%

        deductible, excess = apply_per_deduction_with_limit(
            per_contribution, professional_income, rules
        )

        # 10% of 50k = 5000 (between min 4399 and max 35194)
        assert deductible == 5000
        assert excess == 0

    def test_per_strategy_min_plafond(self):
        """Verify PER strategy respects minimum plafond."""
        rules = get_tax_rules(2024)

        # Low income
        plafond = calculate_per_plafond(10000, rules, status="salarie")
        assert plafond == 4399  # Min plafond


@pytest.mark.parametrize(
    "professional_income,expected_plafond",
    [
        (10000, 4399),  # Below min (10% = 1000 < 4399)
        (50000, 5000),  # Normal (10% = 5000)
        (100000, 10000),  # Normal (10% = 10000)
        (300000, 30000),  # Normal (10% = 30000)
        (500000, 35194),  # Above max (10% = 50000 > 35194)
        (1000000, 35194),  # Way above max (10% = 100000 > 35194)
    ],
)
def test_per_plafond_calculation_scenarios(professional_income, expected_plafond):
    """Test PER plafond calculation across various income levels."""
    rules = get_tax_rules(2024)
    plafond = calculate_per_plafond(professional_income, rules, status="salarie")
    assert plafond == expected_plafond


def test_no_divergence_between_sources():
    """Verify all sources have exactly the same max plafond value."""
    # Read baremes_2024.json
    baremes_path = Path("src/tax_engine/data/baremes_2024.json")
    with open(baremes_path, encoding="utf-8") as f:
        baremes = json.load(f)
    max_from_baremes = baremes["per_plafonds"]["max_salarie"]

    # Read per_rules.json
    per_rules_path = Path("src/analyzers/rules/per_rules.json")
    with open(per_rules_path, encoding="utf-8") as f:
        per_rules = json.load(f)
    max_from_per_rules = per_rules["rules"]["plafond_calculation"]["max_plafond"]

    # They MUST be identical
    assert max_from_baremes == max_from_per_rules, (
        f"Divergence detected: baremes={max_from_baremes}, "
        f"per_rules={max_from_per_rules}"
    )

    # Verify it's the official value
    assert max_from_baremes == 35194, f"Expected 35194, got {max_from_baremes}"
    assert max_from_per_rules == 35194, f"Expected 35194, got {max_from_per_rules}"
