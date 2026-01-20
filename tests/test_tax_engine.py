"""Tests for tax engine - IR calculation, socials, comparisons."""

import pytest

from src.tax_engine.calculator import TaxCalculator
from src.tax_engine.core import apply_bareme, compute_taxable_professional_income
from src.tax_engine.rules import get_tax_rules


class TestTaxRules:
    """Tests for tax rules loading."""

    def test_load_rules_2024(self):
        """Test loading 2024 tax rules."""
        rules = get_tax_rules(2024)

        assert rules.year == 2024
        assert len(rules.income_tax_brackets) == 5
        assert rules.abattements["micro_bnc"] == 0.34

    def test_load_rules_2025(self):
        """Test loading 2025 tax rules."""
        rules = get_tax_rules(2025)

        assert rules.year == 2025
        assert len(rules.income_tax_brackets) == 5

    def test_get_abattement(self):
        """Test getting abattement by regime."""
        rules = get_tax_rules(2024)

        assert rules.get_abattement("micro_bnc") == 0.34
        assert rules.get_abattement("micro_bic_service") == 0.50
        assert rules.get_abattement("micro_bic_vente") == 0.71

    def test_get_urssaf_rate(self):
        """Test getting URSSAF rate."""
        rules = get_tax_rules(2024)

        rate = rules.get_urssaf_rate("liberal_bnc")
        assert 0.20 < rate < 0.30


class TestTaxableIncomeCalculation:
    """Tests for taxable income computation."""

    def test_micro_bnc_abattement(self):
        """Test micro-BNC with 34% abattement."""
        rules = get_tax_rules(2024)

        taxable = compute_taxable_professional_income(
            regime="micro_bnc",
            professional_gross=28000.0,
            deductible_expenses=0.0,
            rules=rules,
        )

        # 28000 * (1 - 0.34) = 18480
        assert taxable == pytest.approx(18480.0)

    def test_micro_bic_service_abattement(self):
        """Test micro-BIC service with 50% abattement."""
        rules = get_tax_rules(2024)

        taxable = compute_taxable_professional_income(
            regime="micro_bic_service",
            professional_gross=40000.0,
            deductible_expenses=0.0,
            rules=rules,
        )

        # 40000 * (1 - 0.50) = 20000
        assert taxable == pytest.approx(20000.0)

    def test_reel_bnc_expenses(self):
        """Test réel regime with real expenses."""
        rules = get_tax_rules(2024)

        taxable = compute_taxable_professional_income(
            regime="reel_bnc",
            professional_gross=50000.0,
            deductible_expenses=20000.0,
            rules=rules,
        )

        # 50000 - 20000 = 30000
        assert taxable == 30000.0


class TestBaremeApplication:
    """Tests for barème (progressive brackets) application."""

    def test_zero_income(self):
        """Test zero income."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(0.0, rules)

        assert tax == 0.0

    def test_first_bracket_only(self):
        """Test income in first bracket (0%)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(10000.0, rules)

        # Should be 0 (below 11294)
        assert tax == 0.0

    def test_second_bracket(self):
        """Test income in second bracket (11%)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(20000.0, rules)

        # (20000 - 11294) * 0.11 = 957.66
        expected = (20000 - 11294) * 0.11
        assert tax == pytest.approx(expected, abs=1.0)

    def test_multiple_brackets(self):
        """Test income spanning multiple brackets."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(50000.0, rules)

        # Bracket 1: 0 (up to 11294)
        # Bracket 2: (28797 - 11294) * 0.11 = 1925.33
        # Bracket 3: (50000 - 28797) * 0.30 = 6360.90
        # Total: 8286.23
        expected = (28797 - 11294) * 0.11 + (50000 - 28797) * 0.30
        assert tax == pytest.approx(expected, abs=1.0)

    def test_bracket_boundary(self):
        """Test income exactly at bracket boundary."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(28797.0, rules)

        # Exactly at boundary: (28797 - 11294) * 0.11
        expected = (28797 - 11294) * 0.11
        assert tax == pytest.approx(expected, abs=0.1)


class TestBracketBoundaryEdgeCases:
    """Edge case tests for tax bracket boundaries."""

    def test_exactly_at_first_bracket_limit(self):
        """Test income exactly at 0%/11% boundary (11294)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(11294.0, rules)

        # Exactly at 11294, tax should be 0
        assert tax == pytest.approx(0.0)

    def test_one_euro_above_first_bracket(self):
        """Test income 1 euro above first bracket (11295)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(11295.0, rules)

        # 1 euro in 11% bracket
        expected = 1.0 * 0.11
        assert tax == pytest.approx(expected, abs=0.01)

    def test_exactly_at_second_bracket_limit(self):
        """Test income exactly at 11%/30% boundary (28797)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(28797.0, rules)

        # Full 11% bracket: (28797 - 11294) * 0.11
        expected = (28797 - 11294) * 0.11
        assert tax == pytest.approx(expected, abs=0.1)

    def test_one_euro_above_second_bracket(self):
        """Test income 1 euro above second bracket (28798)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(28798.0, rules)

        # Full 11% bracket + 1 euro at 30%
        expected = (28797 - 11294) * 0.11 + 1.0 * 0.30
        assert tax == pytest.approx(expected, abs=0.1)

    def test_exactly_at_third_bracket_limit(self):
        """Test income exactly at 30%/41% boundary (82341)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(82341.0, rules)

        # Full 11% and 30% brackets
        expected = (28797 - 11294) * 0.11 + (82341 - 28797) * 0.30
        assert tax == pytest.approx(expected, abs=1.0)

    def test_one_euro_above_third_bracket(self):
        """Test income 1 euro above third bracket (82342)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(82342.0, rules)

        # Full 11%, 30% brackets + 1 euro at 41%
        expected = (28797 - 11294) * 0.11 + (82341 - 28797) * 0.30 + 1.0 * 0.41
        assert tax == pytest.approx(expected, abs=1.0)

    def test_exactly_at_fourth_bracket_limit(self):
        """Test income exactly at 41%/45% boundary (177106)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(177106.0, rules)

        # Full 11%, 30%, and 41% brackets
        expected = (
            (28797 - 11294) * 0.11 + (82341 - 28797) * 0.30 + (177106 - 82341) * 0.41
        )
        assert tax == pytest.approx(expected, abs=1.0)

    def test_one_euro_above_fourth_bracket(self):
        """Test income 1 euro above fourth bracket (177107)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(177107.0, rules)

        # All brackets + 1 euro at 45%
        expected = (
            (28797 - 11294) * 0.11
            + (82341 - 28797) * 0.30
            + (177106 - 82341) * 0.41
            + 1.0 * 0.45
        )
        assert tax == pytest.approx(expected, abs=1.0)

    def test_very_high_income_in_top_bracket(self):
        """Test very high income (1M) in top 45% bracket."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(1000000.0, rules)

        # All brackets filled + large amount in 45%
        expected = (
            (28797 - 11294) * 0.11
            + (82341 - 28797) * 0.30
            + (177106 - 82341) * 0.41
            + (1000000 - 177106) * 0.45
        )
        assert tax == pytest.approx(expected, abs=10.0)

    def test_negative_income_returns_zero(self):
        """Test that negative income returns zero tax (edge case)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(-1000.0, rules)

        # Negative income should result in 0 tax
        assert tax == 0.0

    def test_very_small_income(self):
        """Test very small income (1 euro)."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(1.0, rules)

        # 1 euro is in 0% bracket
        assert tax == 0.0

    def test_penny_amounts_handled(self):
        """Test fractional amounts (cents) are handled correctly."""
        rules = get_tax_rules(2024)
        tax = apply_bareme(11294.50, rules)

        # 0.50 euro in 11% bracket
        expected = 0.50 * 0.11
        assert tax == pytest.approx(expected, abs=0.01)


class TestFullCalculation:
    """Tests for complete tax calculations."""

    @pytest.mark.anyio
    async def test_simple_micro_bnc_case(self):
        """Test simple micro-BNC case (Cas A from doc)."""
        calculator = TaxCalculator(2024)

        payload = {
            "tax_year": 2024,
            "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
            "income": {
                "professional_gross": 28000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {"urssaf_declared_ca": 28000.0, "urssaf_paid": 6000.0},
            "pas_withheld": 0.0,
        }

        result = await calculator.calculate(payload)

        # Check structure
        assert "impot" in result
        assert "socials" in result
        assert "comparisons" in result
        assert "warnings" in result

        # Check taxable income: 28000 * (1 - 0.34) = 18480
        assert result["impot"]["revenu_imposable"] == pytest.approx(18480.0)

        # Check URSSAF: 28000 * 0.218 ≈ 6104
        assert result["socials"]["urssaf_expected"] == pytest.approx(6104.0, abs=10.0)

    @pytest.mark.anyio
    async def test_with_per_deduction(self):
        """Test with PER contribution deduction."""
        calculator = TaxCalculator(2024)

        payload = {
            "tax_year": 2024,
            "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
            "income": {
                "professional_gross": 28000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 2000.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {"urssaf_declared_ca": 28000.0, "urssaf_paid": 6000.0},
            "pas_withheld": 0.0,
        }

        result = await calculator.calculate(payload)

        # Taxable: 18480 - 2000 = 16480
        assert result["impot"]["revenu_imposable"] == pytest.approx(16480.0)

    @pytest.mark.anyio
    async def test_quotient_familial(self):
        """Test with quotient familial (2 parts)."""
        calculator = TaxCalculator(2024)

        payload = {
            "tax_year": 2024,
            "person": {"name": "ANON", "nb_parts": 2.0, "status": "micro_bnc"},
            "income": {
                "professional_gross": 50000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {"urssaf_declared_ca": 50000.0, "urssaf_paid": 10000.0},
            "pas_withheld": 0.0,
        }

        result = await calculator.calculate(payload)

        # Taxable pro: 50000 * (1 - 0.34) = 33000
        assert result["impot"]["revenu_imposable"] == pytest.approx(33000.0)

        # Part income: 33000 / 2 = 16500
        assert result["impot"]["part_income"] == pytest.approx(16500.0)

    @pytest.mark.anyio
    async def test_reel_vs_micro_comparison(self):
        """Test comparison when réel is better (Cas B from doc)."""
        calculator = TaxCalculator(2024)

        payload = {
            "tax_year": 2024,
            "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
            "income": {
                "professional_gross": 50000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 20000.0,  # High expenses
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {"urssaf_declared_ca": 50000.0, "urssaf_paid": 10000.0},
            "pas_withheld": 0.0,
        }

        result = await calculator.calculate(payload)

        comparison = result["comparisons"]["micro_vs_reel"]

        # Micro: 50000 * 0.66 = 33000 taxable
        # Réel: 50000 - 20000 = 30000 taxable
        # Réel should be better (lower tax)
        assert comparison["delta_total"] < 0  # Negative = réel better

    @pytest.mark.anyio
    async def test_mixed_income(self):
        """Test with multiple income sources."""
        calculator = TaxCalculator(2024)

        payload = {
            "tax_year": 2024,
            "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
            "income": {
                "professional_gross": 20000.0,
                "salary": 15000.0,
                "rental_income": 5000.0,
                "capital_income": 2000.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {"urssaf_declared_ca": 20000.0, "urssaf_paid": 4000.0},
            "pas_withheld": 0.0,
        }

        result = await calculator.calculate(payload)

        # Taxable pro: 20000 * 0.66 = 13200
        # Total: 13200 + 15000 + 5000 + 2000 = 35200
        assert result["impot"]["revenu_imposable"] == pytest.approx(35200.0)

    @pytest.mark.anyio
    async def test_urssaf_warning(self):
        """Test URSSAF inconsistency warning."""
        calculator = TaxCalculator(2024)

        payload = {
            "tax_year": 2024,
            "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
            "income": {
                "professional_gross": 28000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {"urssaf_declared_ca": 28000.0, "urssaf_paid": 3000.0},  # Low
            "pas_withheld": 0.0,
        }

        result = await calculator.calculate(payload)

        # Should have warning about URSSAF underpayment
        assert len(result["warnings"]) > 0
        assert any("URSSAF" in w for w in result["warnings"])

    @pytest.mark.anyio
    async def test_micro_threshold_warning(self):
        """Test warning when exceeding micro threshold."""
        calculator = TaxCalculator(2024)

        payload = {
            "tax_year": 2024,
            "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
            "income": {
                "professional_gross": 80000.0,  # Above threshold
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {"urssaf_declared_ca": 80000.0, "urssaf_paid": 17000.0},
            "pas_withheld": 0.0,
        }

        result = await calculator.calculate(payload)

        # Should have warning about threshold
        assert any("plafond" in w.lower() for w in result["warnings"])
