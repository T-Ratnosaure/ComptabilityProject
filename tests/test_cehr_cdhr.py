"""Tests for CEHR and CDHR (high-income contributions).

CEHR: Contribution Exceptionnelle sur les Hauts Revenus
CDHR: Contribution Différentielle sur les Hauts Revenus (NEW 2025)

These tests validate:
1. CEHR calculation with correct brackets (single vs couple)
2. CEHR uses RFR, not revenu_imposable
3. CDHR ensures 20% minimum effective rate
4. CDHR is cumulative with CEHR
"""

import pytest

from src.tax_engine.core import compute_cdhr, compute_cehr, compute_ir
from src.tax_engine.rules import get_tax_rules


class TestCEHRBrackets:
    """Tests for CEHR bracket validation."""

    @pytest.fixture
    def rules_2025(self):
        """Get 2025 tax rules."""
        return get_tax_rules(2025)

    # === Single (Célibataire) Tests ===

    def test_cehr_single_below_threshold(self, rules_2025):
        """Single with RFR below 250k pays no CEHR."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=249_999.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cehr == 0.0
        assert detail == []

    def test_cehr_single_at_threshold(self, rules_2025):
        """Single exactly at 250k threshold pays no CEHR (exclusive)."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=250_000.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cehr == 0.0

    def test_cehr_single_first_bracket(self, rules_2025):
        """Single with 300k RFR: CEHR = (300k - 250k) × 3% = 1,500€."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=300_000.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cehr == pytest.approx(1_500.0)
        assert len(detail) == 1
        assert detail[0]["rate"] == 0.03

    def test_cehr_single_both_brackets(self, rules_2025):
        """Single with 600k RFR: CEHR = 7,500 + 4,000 = 11,500€."""
        # First bracket: (500k - 250k) × 3% = 7,500€
        # Second bracket: (600k - 500k) × 4% = 4,000€
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=600_000.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cehr == pytest.approx(11_500.0)
        assert len(detail) == 2

    # === Couple Tests ===

    def test_cehr_couple_below_threshold(self, rules_2025):
        """Couple with RFR below 500k pays no CEHR."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=499_999.0,
            situation_familiale="couple",
            rules=rules_2025,
        )
        assert cehr == 0.0

    def test_cehr_couple_first_bracket(self, rules_2025):
        """Couple with 700k RFR: CEHR = (700k - 500k) × 3% = 6,000€."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=700_000.0,
            situation_familiale="couple",
            rules=rules_2025,
        )
        assert cehr == pytest.approx(6_000.0)

    def test_cehr_couple_both_brackets(self, rules_2025):
        """Couple with 1.2M RFR: CEHR = 15,000 + 8,000 = 23,000€."""
        # First bracket: (1M - 500k) × 3% = 15,000€
        # Second bracket: (1.2M - 1M) × 4% = 8,000€
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=1_200_000.0,
            situation_familiale="couple",
            rules=rules_2025,
        )
        assert cehr == pytest.approx(23_000.0)


class TestCEHRSituationFamiliale:
    """Tests that situation_familiale is used correctly, NOT nb_parts."""

    @pytest.fixture
    def rules_2025(self):
        return get_tax_rules(2025)

    def test_single_parent_with_children_uses_celibataire_brackets(self, rules_2025):
        """A single parent with 2 children (nb_parts=2.0) uses célibataire brackets.

        This is a critical test - the old code incorrectly used nb_parts >= 2.0
        to determine couple status, which would apply wrong brackets to single parents.
        """
        # Single parent with 2 children has RFR of 280k
        # Should use célibataire bracket (250k threshold), NOT couple (500k threshold)
        cehr, _ = compute_cehr(
            revenu_fiscal_reference=280_000.0,
            situation_familiale="celibataire",  # Single parent explicitly
            rules=rules_2025,
        )
        # CEHR = (280k - 250k) × 3% = 900€
        assert cehr == pytest.approx(900.0)

        # If we had wrongly used couple brackets, CEHR would be 0
        # because 280k < 500k (couple threshold)


class TestCEHRWithRFR:
    """Tests that CEHR correctly uses RFR (including PER reintegration)."""

    @pytest.fixture
    def rules_2025(self):
        return get_tax_rules(2025)

    def test_rfr_includes_per_contribution(self, rules_2025):
        """CEHR should be calculated on RFR, which includes PER contributions.

        Example:
        - Professional income: 330,000€
        - PER contribution: 33,000€
        - Revenu imposable: 297,000€ (after PER deduction)
        - RFR: 330,000€ (PER is reintegrated)

        Old code would have calculated CEHR on 297k (wrong)
        New code calculates CEHR on 330k (correct)
        """
        # Using compute_ir which now calculates RFR properly
        result = compute_ir(
            person={
                "nb_parts": 1.0,
                "status": "micro_bnc",
                "situation_familiale": "celibataire",
            },
            income={
                "professional_gross": 500_000.0,  # Will result in ~330k taxable
            },
            deductions={
                "per_contributions": 33_000.0,
            },
            rules=rules_2025,
        )

        # Verify RFR is present in result
        assert "rfr" in result
        # RFR should be higher than revenu_imposable by the PER amount
        assert result["rfr"] > result["revenu_imposable"]


class TestCDHR:
    """Tests for CDHR (Contribution Différentielle - NEW 2025)."""

    @pytest.fixture
    def rules_2025(self):
        return get_tax_rules(2025)

    def test_cdhr_below_threshold(self, rules_2025):
        """CDHR does not apply below 250k threshold."""
        cdhr, detail = compute_cdhr(
            rfr=200_000.0,
            impot_ir=40_000.0,
            cehr=0.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cdhr == 0.0
        assert detail == {}

    def test_cdhr_not_needed_if_effective_rate_above_20(self, rules_2025):
        """CDHR = 0 if effective tax rate already >= 20%."""
        # RFR = 300k, IR = 60k → effective rate = 20%
        cdhr, detail = compute_cdhr(
            rfr=300_000.0,
            impot_ir=60_000.0,  # 20% effective rate
            cehr=0.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cdhr == 0.0
        assert detail.get("applicable") is False

    def test_cdhr_applies_when_effective_rate_below_20(self, rules_2025):
        """CDHR brings effective rate up to 20%.

        Example:
        - RFR = 300,000€
        - IR = 30,000€ (10% effective rate due to heavy optimization)
        - CEHR = 1,500€
        - Total before CDHR = 31,500€
        - Target = 20% × 300k = 60,000€
        - CDHR = 60,000 - 31,500 = 28,500€
        """
        cdhr, detail = compute_cdhr(
            rfr=300_000.0,
            impot_ir=30_000.0,  # Low IR due to optimizations
            cehr=1_500.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cdhr == pytest.approx(28_500.0)
        assert detail["applicable"] is True
        assert detail["taux_cible"] == 0.20

    def test_cdhr_couple_threshold(self, rules_2025):
        """Couple CDHR threshold is 500k, not 250k."""
        # At 400k, couple is below threshold
        cdhr, detail = compute_cdhr(
            rfr=400_000.0,
            impot_ir=40_000.0,  # Only 10% effective
            cehr=0.0,
            situation_familiale="couple",
            rules=rules_2025,
        )
        assert cdhr == 0.0


class TestCEHRCDHRCumulative:
    """Tests that CEHR and CDHR apply cumulatively."""

    @pytest.fixture
    def rules_2025(self):
        return get_tax_rules(2025)

    def test_both_contributions_in_compute_ir(self, rules_2025):
        """compute_ir should return both CEHR and CDHR."""
        result = compute_ir(
            person={
                "nb_parts": 1.0,
                "status": "micro_bnc",
                "situation_familiale": "celibataire",
            },
            income={
                "professional_gross": 400_000.0,  # High income
            },
            deductions={},
            rules=rules_2025,
        )

        # Both should be present in result
        assert "cehr" in result
        assert "cdhr" in result
        assert "cehr_detail" in result
        assert "cdhr_detail" in result

        # Total tax should include both
        ir_only = result["impot_ir_seul"]
        total = result["impot_net"]
        assert total == pytest.approx(ir_only + result["cehr"] + result["cdhr"])


class TestEdgeCases:
    """Edge case tests for CEHR/CDHR."""

    @pytest.fixture
    def rules_2025(self):
        return get_tax_rules(2025)

    def test_cehr_exactly_at_bracket_boundary(self, rules_2025):
        """CEHR at exactly 500k (end of first bracket for single)."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=500_000.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        # Only first bracket applies: (500k - 250k) × 3% = 7,500€
        assert cehr == pytest.approx(7_500.0)
        assert len(detail) == 1

    def test_cehr_just_above_bracket_boundary(self, rules_2025):
        """CEHR at 500,001€ (both brackets apply for single)."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=500_001.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        # First bracket: 7,500€
        # Second bracket: 1€ × 4% = 0.04€
        assert cehr == pytest.approx(7_500.04)
        assert len(detail) == 2

    def test_zero_rfr(self, rules_2025):
        """CEHR with zero RFR returns 0."""
        cehr, detail = compute_cehr(
            revenu_fiscal_reference=0.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cehr == 0.0

    def test_cdhr_cannot_be_negative(self, rules_2025):
        """CDHR cannot be negative even if effective rate > 20%."""
        cdhr, detail = compute_cdhr(
            rfr=300_000.0,
            impot_ir=70_000.0,  # 23% effective rate
            cehr=1_500.0,
            situation_familiale="celibataire",
            rules=rules_2025,
        )
        assert cdhr == 0.0
