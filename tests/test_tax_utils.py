"""Tests for tax_utils.py - centralized fiscal functions."""

import pytest

from src.tax_engine.rules import get_tax_rules
from src.tax_engine.tax_utils import (
    calculate_per_plafond,
    calculate_tax_reduction,
    check_micro_threshold_proximity,
    get_lmnp_deduction_rate,
    get_lmnp_eligibility,
    get_lmnp_yield,
    get_micro_abattement,
    get_micro_threshold,
    get_tax_reduction_plafond,
    get_tax_reduction_rate,
)


class TestPERPlafond:
    """Test PER plafond calculations."""

    def test_calculate_per_plafond_basic(self):
        """Test basic PER plafond calculation (10%)."""
        rules = get_tax_rules(2024)
        plafond = calculate_per_plafond(50000, rules, "salarie")
        assert plafond == 5000.0  # 10% of 50k

    def test_calculate_per_plafond_min_limit(self):
        """Test PER plafond respects minimum (4399€)."""
        rules = get_tax_rules(2024)
        plafond = calculate_per_plafond(10000, rules, "salarie")
        assert plafond == 4399.0  # Min plafond

    def test_calculate_per_plafond_max_limit_salarie(self):
        """Test PER plafond respects maximum for salarié (35194€)."""
        rules = get_tax_rules(2024)
        plafond = calculate_per_plafond(500000, rules, "salarie")
        assert plafond == 35194.0  # Max for salarie

    @pytest.mark.parametrize(
        "income,expected",
        [
            (10000, 4399),  # Below min
            (50000, 5000),  # Normal case
            (100000, 10000),  # Normal case
            (300000, 30000),  # Normal case
            (500000, 35194),  # Above max
        ],
    )
    def test_calculate_per_plafond_scenarios(self, income, expected):
        """Test PER plafond for various income levels."""
        rules = get_tax_rules(2024)
        plafond = calculate_per_plafond(income, rules, "salarie")
        assert plafond == expected


class TestTaxReductionRates:
    """Test tax reduction rate retrieval."""

    def test_get_rate_dons(self):
        """Test getting dons reduction rate (66%)."""
        rules = get_tax_rules(2024)
        rate = get_tax_reduction_rate("dons", rules)
        assert rate == 0.66

    def test_get_rate_services_personne(self):
        """Test getting services à la personne rate (50%)."""
        rules = get_tax_rules(2024)
        rate = get_tax_reduction_rate("services_personne", rules)
        assert rate == 0.50

    def test_get_rate_frais_garde(self):
        """Test getting frais de garde rate (50%)."""
        rules = get_tax_rules(2024)
        rate = get_tax_reduction_rate("frais_garde", rules)
        assert rate == 0.50

    def test_get_rate_unknown_type(self):
        """Test error for unknown reduction type."""
        rules = get_tax_rules(2024)
        with pytest.raises(KeyError, match="Unknown reduction type"):
            get_tax_reduction_rate("unknown_type", rules)


class TestTaxReductionPlafonds:
    """Test tax reduction plafond calculations."""

    def test_plafond_dons_percentage_based(self):
        """Test dons plafond (20% of taxable income)."""
        rules = get_tax_rules(2024)
        plafond = get_tax_reduction_plafond("dons", rules, revenu_imposable=50000)
        assert plafond == 10000.0  # 20% of 50k

    def test_plafond_services_personne_fixed(self):
        """Test services à la personne plafond (12000€ fixed)."""
        rules = get_tax_rules(2024)
        plafond = get_tax_reduction_plafond("services_personne", rules)
        assert plafond == 12000.0

    def test_plafond_frais_garde_per_child(self):
        """Test frais de garde plafond (3500€ per child)."""
        rules = get_tax_rules(2024)
        plafond = get_tax_reduction_plafond("frais_garde", rules, children_under_6=2)
        assert plafond == 7000.0  # 3500 * 2

    def test_plafond_unknown_type(self):
        """Test error for unknown reduction type."""
        rules = get_tax_rules(2024)
        with pytest.raises(KeyError, match="Unknown reduction type"):
            get_tax_reduction_plafond("unknown_type", rules)


class TestCalculateTaxReduction:
    """Test complete tax reduction calculations."""

    def test_dons_within_plafond(self):
        """Test dons reduction within plafond."""
        rules = get_tax_rules(2024)
        reduction, excess = calculate_tax_reduction(
            "dons", 1000, rules, revenu_imposable=50000
        )
        assert reduction == 660.0  # 66% of 1000
        assert excess == 0.0  # Within plafond

    def test_dons_exceeds_plafond(self):
        """Test dons reduction exceeding plafond."""
        rules = get_tax_rules(2024)
        # Plafond is 20% of 50k = 10k
        # So 15k donation exceeds by 5k
        reduction, excess = calculate_tax_reduction(
            "dons", 15000, rules, revenu_imposable=50000
        )
        assert reduction == 6600.0  # 66% of 10k (plafond)
        assert excess == 5000.0  # 15k - 10k

    def test_services_personne_within_plafond(self):
        """Test services à la personne within plafond."""
        rules = get_tax_rules(2024)
        reduction, excess = calculate_tax_reduction("services_personne", 5000, rules)
        assert reduction == 2500.0  # 50% of 5000
        assert excess == 0.0

    def test_services_personne_exceeds_plafond(self):
        """Test services à la personne exceeding plafond."""
        rules = get_tax_rules(2024)
        reduction, excess = calculate_tax_reduction("services_personne", 15000, rules)
        assert reduction == 6000.0  # 50% of 12k (plafond)
        assert excess == 3000.0  # 15k - 12k

    def test_frais_garde_per_child(self):
        """Test frais de garde for multiple children."""
        rules = get_tax_rules(2024)
        reduction, excess = calculate_tax_reduction(
            "frais_garde", 6000, rules, children_under_6=2
        )
        assert reduction == 3000.0  # 50% of 6k (within 7k plafond)
        assert excess == 0.0

    def test_frais_garde_exceeds_plafond(self):
        """Test frais de garde exceeding plafond."""
        rules = get_tax_rules(2024)
        # Plafond is 3500 per child = 7k for 2 children
        reduction, excess = calculate_tax_reduction(
            "frais_garde", 10000, rules, children_under_6=2
        )
        assert reduction == 3500.0  # 50% of 7k (plafond)
        assert excess == 3000.0  # 10k - 7k


class TestMicroRegime:
    """Test micro-regime thresholds and abattements."""

    def test_get_micro_threshold_bnc(self):
        """Test BNC threshold (77700€)."""
        rules = get_tax_rules(2024)
        threshold = get_micro_threshold("bnc", rules)
        assert threshold == 77700

    def test_get_micro_threshold_bic_service(self):
        """Test BIC service threshold (77700€)."""
        rules = get_tax_rules(2024)
        threshold = get_micro_threshold("bic_service", rules)
        assert threshold == 77700

    def test_get_micro_threshold_bic_vente(self):
        """Test BIC vente threshold (188700€)."""
        rules = get_tax_rules(2024)
        threshold = get_micro_threshold("bic_vente", rules)
        assert threshold == 188700

    def test_get_micro_threshold_unknown(self):
        """Test error for unknown regime type."""
        rules = get_tax_rules(2024)
        with pytest.raises(KeyError, match="Unknown regime type"):
            get_micro_threshold("unknown", rules)

    def test_get_micro_abattement_bnc(self):
        """Test BNC abattement (34%)."""
        rules = get_tax_rules(2024)
        abattement = get_micro_abattement("micro_bnc", rules)
        assert abattement == 0.34

    def test_get_micro_abattement_bic_service(self):
        """Test BIC service abattement (50%)."""
        rules = get_tax_rules(2024)
        abattement = get_micro_abattement("micro_bic_service", rules)
        assert abattement == 0.50

    def test_get_micro_abattement_bic_vente(self):
        """Test BIC vente abattement (71%)."""
        rules = get_tax_rules(2024)
        abattement = get_micro_abattement("micro_bic_vente", rules)
        assert abattement == 0.71


class TestMicroThresholdProximity:
    """Test micro threshold proximity detection."""

    def test_approaching_threshold(self):
        """Test detection when approaching threshold (85%+)."""
        rules = get_tax_rules(2024)
        result = check_micro_threshold_proximity(70000, "bnc", rules)
        assert result["approaching"] is True  # 70k is 90% of 77.7k
        assert result["threshold"] == 77700
        assert result["remaining"] == 7700.0
        assert 0.90 <= result["proximity_rate"] <= 0.91

    def test_not_approaching_threshold(self):
        """Test when far from threshold (<85%)."""
        rules = get_tax_rules(2024)
        result = check_micro_threshold_proximity(50000, "bnc", rules)
        assert result["approaching"] is False  # 50k is 64% of 77.7k
        assert result["threshold"] == 77700
        assert result["remaining"] == 27700.0

    def test_at_threshold(self):
        """Test when exactly at threshold."""
        rules = get_tax_rules(2024)
        result = check_micro_threshold_proximity(77700, "bnc", rules)
        assert (
            result["approaching"] is False
        )  # At 100%, not approaching (already there)
        assert result["proximity_rate"] == 1.0
        assert result["remaining"] == 0.0

    def test_custom_alert_threshold(self):
        """Test with custom alert threshold (90%)."""
        rules = get_tax_rules(2024)
        result = check_micro_threshold_proximity(
            70000, "bnc", rules, alert_threshold=0.95
        )
        assert result["approaching"] is False  # 90% < 95%

        result2 = check_micro_threshold_proximity(
            74000, "bnc", rules, alert_threshold=0.95
        )
        assert result2["approaching"] is True  # 95%+


class TestIntegration:
    """Integration tests combining multiple tax_utils functions."""

    def test_full_tax_reduction_workflow(self):
        """Test complete workflow: rate + plafond + calculation."""
        rules = get_tax_rules(2024)

        # Step 1: Get rate
        rate = get_tax_reduction_rate("dons", rules)
        assert rate == 0.66

        # Step 2: Get plafond
        plafond = get_tax_reduction_plafond("dons", rules, revenu_imposable=50000)
        assert plafond == 10000.0

        # Step 3: Calculate reduction
        reduction, excess = calculate_tax_reduction(
            "dons", 5000, rules, revenu_imposable=50000
        )
        assert reduction == 3300.0  # 66% of 5k
        assert excess == 0.0

    def test_per_and_micro_coherence(self):
        """Test that PER plafond and micro thresholds are coherent."""
        rules = get_tax_rules(2024)

        # Both should use same underlying baremes
        per_plafond = calculate_per_plafond(77700, rules)
        micro_threshold = get_micro_threshold("bnc", rules)

        # Per plafond for 77.7k income should be 7770 (10%)
        assert per_plafond == 7770.0

        # Micro threshold should be 77700
        assert micro_threshold == 77700


class TestLMNP:
    """Test LMNP (Location Meublée Non Professionnelle) utilities."""

    def test_get_lmnp_deduction_rate_micro(self):
        """Test LMNP micro regime deduction rate (50%)."""
        rules = get_tax_rules(2024)
        rate = get_lmnp_deduction_rate("micro", rules)
        assert rate == 0.50  # Micro-BIC abattement

    def test_get_lmnp_deduction_rate_reel(self):
        """Test LMNP réel regime deduction rate (~85%)."""
        rules = get_tax_rules(2024)
        rate = get_lmnp_deduction_rate("reel", rules)
        assert rate == 0.85  # Average total deduction (charges + amortization)

    def test_get_lmnp_deduction_rate_unknown(self):
        """Test error for unknown LMNP regime."""
        rules = get_tax_rules(2024)
        with pytest.raises(ValueError, match="Unknown LMNP regime"):
            get_lmnp_deduction_rate("unknown", rules)

    def test_get_lmnp_yield(self):
        """Test LMNP estimated yield (4%)."""
        rules = get_tax_rules(2024)
        yield_rate = get_lmnp_yield(rules)
        assert yield_rate == 0.04  # 4% typical yield

    def test_get_lmnp_eligibility(self):
        """Test LMNP eligibility criteria."""
        rules = get_tax_rules(2024)
        eligibility = get_lmnp_eligibility(rules)

        assert eligibility["min_tmi"] == 0.30  # Min TMI 30%
        assert eligibility["min_investment_capacity"] == 50000  # Min 50k€

    def test_lmnp_estimation_workflow(self):
        """Test complete LMNP estimation workflow."""
        rules = get_tax_rules(2024)

        # Scenario: 100k€ investment, réel regime
        investment = 100000
        yield_rate = get_lmnp_yield(rules)
        deduction_rate = get_lmnp_deduction_rate("reel", rules)

        # Estimated annual rental income
        annual_rental = investment * yield_rate
        assert annual_rental == 4000.0  # 4% of 100k

        # With TMI 41%, estimate tax savings
        tmi = 0.41
        estimated_savings = annual_rental * tmi * deduction_rate
        assert estimated_savings == 1394.0  # 4000 * 0.41 * 0.85

    def test_lmnp_micro_vs_reel_comparison(self):
        """Test comparing micro vs réel LMNP regimes."""
        rules = get_tax_rules(2024)

        # Micro: 50% abattement
        micro_rate = get_lmnp_deduction_rate("micro", rules)
        assert micro_rate == 0.50

        # Réel: 85% deduction (charges + amortization)
        reel_rate = get_lmnp_deduction_rate("reel", rules)
        assert reel_rate == 0.85

        # Réel is more advantageous (higher deduction rate)
        assert reel_rate > micro_rate
