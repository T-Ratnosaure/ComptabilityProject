"""Tests for enhanced tax engine core functionality.

Tests for Phase 3 tax engine refactoring:
- calculate_tmi() centralized function
- apply_per_deduction_with_limit() for PER plafond
- apply_tax_reductions() for tax credits
- Enhanced compute_ir() with complete data
"""

import pytest

from src.tax_engine.core import (
    apply_per_deduction_with_limit,
    apply_tax_reductions,
    calculate_tmi,
    compute_ir,
)
from src.tax_engine.rules import get_tax_rules


class TestCalculateTMI:
    """Test centralized TMI calculation function."""

    @pytest.fixture
    def rules(self):
        """Load 2024 tax rules."""
        return get_tax_rules(2024)

    def test_tmi_bracket_0_percent(self, rules):
        """Test TMI at 0% bracket."""
        # Single person with 10k income
        tmi = calculate_tmi(10000, 1.0, rules)
        assert tmi == 0.0

    def test_tmi_bracket_11_percent(self, rules):
        """Test TMI at 11% bracket."""
        # Single person with 20k income (20k / 1 = 20k per part)
        tmi = calculate_tmi(20000, 1.0, rules)
        assert tmi == 0.11

    def test_tmi_bracket_30_percent(self, rules):
        """Test TMI at 30% bracket."""
        # Single person with 40k income
        tmi = calculate_tmi(40000, 1.0, rules)
        assert tmi == 0.30

    def test_tmi_bracket_41_percent(self, rules):
        """Test TMI at 41% bracket."""
        # Single person with 100k income
        tmi = calculate_tmi(100000, 1.0, rules)
        assert tmi == 0.41

    def test_tmi_bracket_45_percent(self, rules):
        """Test TMI at 45% bracket."""
        # Single person with 200k income
        tmi = calculate_tmi(200000, 1.0, rules)
        assert tmi == 0.45

    def test_tmi_with_quotient_familial(self, rules):
        """Test TMI calculation with quotient familial."""
        # Married couple (2 parts) with 80k income
        # 80k / 2 = 40k per part → 30% TMI
        tmi = calculate_tmi(80000, 2.0, rules)
        assert tmi == 0.30

        # Same income but single → 30% TMI (80k < 82341)
        tmi_single = calculate_tmi(80000, 1.0, rules)
        assert tmi_single == 0.30

    def test_tmi_at_bracket_boundary(self, rules):
        """Test TMI at exact bracket boundaries."""
        # At 11294 (boundary between 0% and 11%)
        tmi = calculate_tmi(11294, 1.0, rules)
        assert tmi == 0.0  # Still in 0% bracket

        # Just above boundary
        tmi = calculate_tmi(11295, 1.0, rules)
        assert tmi == 0.11


class TestApplyPERDeductionWithLimit:
    """Test PER deduction with plafond limit."""

    @pytest.fixture
    def rules(self):
        """Load 2024 tax rules."""
        return get_tax_rules(2024)

    def test_per_under_plafond(self, rules):
        """Test PER contribution under plafond limit."""
        # Professional income of 50k → plafond = 5k
        # Contribution of 3k → should be fully deductible
        deductible, excess = apply_per_deduction_with_limit(
            per_contribution=3000,
            professional_income=50000,
            rules=rules,
        )

        assert deductible == 3000
        assert excess == 0.0

    def test_per_over_plafond(self, rules):
        """Test PER contribution over plafond limit."""
        # Professional income of 50k → plafond = 5k
        # Contribution of 7k → only 5k deductible
        deductible, excess = apply_per_deduction_with_limit(
            per_contribution=7000,
            professional_income=50000,
            rules=rules,
        )

        assert deductible == 5000
        assert excess == 2000

    def test_per_minimum_plafond(self, rules):
        """Test PER minimum plafond (4399€)."""
        # Very low income (20k) → 10% = 2k, but min is 4399€
        deductible, excess = apply_per_deduction_with_limit(
            per_contribution=4000,
            professional_income=20000,
            rules=rules,
        )

        assert deductible == 4000
        assert excess == 0.0

    def test_per_maximum_plafond(self, rules):
        """Test PER maximum plafond (35200€ for salaried)."""
        # Very high income (500k) → 10% = 50k, but max is 35200€
        deductible, excess = apply_per_deduction_with_limit(
            per_contribution=40000,
            professional_income=500000,
            rules=rules,
        )

        # Should be limited to max plafond
        assert deductible <= 35200
        assert excess >= 4800

    def test_per_at_exact_plafond(self, rules):
        """Test PER contribution at exact plafond."""
        # Professional income of 50k → plafond = 5k
        deductible, excess = apply_per_deduction_with_limit(
            per_contribution=5000,
            professional_income=50000,
            rules=rules,
        )

        assert deductible == 5000
        assert excess == 0.0


class TestApplyTaxReductions:
    """Test tax reductions and credits."""

    def test_dons_reduction_66_percent(self):
        """Test donations reduction (66%)."""
        impot_net, reductions = apply_tax_reductions(
            impot_brut=5000,
            revenu_imposable=50000,
            reductions_data={"dons": 1000},
        )

        # 1000€ dons → 660€ reduction
        assert reductions["dons"] == 660.0
        assert impot_net == 5000 - 660

    def test_dons_plafond_20_percent(self):
        """Test donations plafond (20% of taxable income)."""
        # Revenu imposable = 50k → plafond = 10k
        # Dons of 15k → only 10k eligible
        impot_net, reductions = apply_tax_reductions(
            impot_brut=5000,
            revenu_imposable=50000,
            reductions_data={"dons": 15000},
        )

        # Only 10k eligible → 6600€ reduction
        assert reductions["dons"] == 6600.0

    def test_services_personne_credit_50_percent(self):
        """Test services à la personne credit (50%)."""
        impot_net, reductions = apply_tax_reductions(
            impot_brut=5000,
            revenu_imposable=50000,
            reductions_data={"services_personne": 4000},
        )

        # 4000€ services → 2000€ credit
        assert reductions["services_personne"] == 2000.0
        assert impot_net == 5000 - 2000

    def test_services_personne_plafond_12000(self):
        """Test services à la personne plafond (12000€)."""
        impot_net, reductions = apply_tax_reductions(
            impot_brut=10000,
            revenu_imposable=100000,
            reductions_data={"services_personne": 20000},
        )

        # Only 12000€ eligible → 6000€ credit
        assert reductions["services_personne"] == 6000.0

    def test_frais_garde_credit_50_percent(self):
        """Test childcare expenses credit (50%)."""
        impot_net, reductions = apply_tax_reductions(
            impot_brut=5000,
            revenu_imposable=50000,
            reductions_data={
                "frais_garde": 3000,
                "children_under_6": 1,
            },
        )

        # 3000€ garde → 1500€ credit
        assert reductions["frais_garde"] == 1500.0
        assert impot_net == 5000 - 1500

    def test_frais_garde_plafond_per_child(self):
        """Test childcare plafond (3500€ per child)."""
        # 2 children → plafond = 7000€
        impot_net, reductions = apply_tax_reductions(
            impot_brut=10000,
            revenu_imposable=80000,
            reductions_data={
                "frais_garde": 10000,
                "children_under_6": 2,
            },
        )

        # Only 7000€ eligible → 3500€ credit
        assert reductions["frais_garde"] == 3500.0

    def test_no_garde_without_children(self):
        """Test no garde credit without children under 6."""
        impot_net, reductions = apply_tax_reductions(
            impot_brut=5000,
            revenu_imposable=50000,
            reductions_data={
                "frais_garde": 3000,
                "children_under_6": 0,
            },
        )

        # No children → no credit
        assert "frais_garde" not in reductions
        assert impot_net == 5000

    def test_multiple_reductions_combined(self):
        """Test combining multiple tax reductions."""
        impot_net, reductions = apply_tax_reductions(
            impot_brut=10000,
            revenu_imposable=80000,
            reductions_data={
                "dons": 2000,
                "services_personne": 4000,
                "frais_garde": 3000,
                "children_under_6": 1,
            },
        )

        # Dons: 2000 * 0.66 = 1320€
        # Services: 4000 * 0.50 = 2000€
        # Garde: 3000 * 0.50 = 1500€
        # Total: 4820€
        assert reductions["dons"] == 1320.0
        assert reductions["services_personne"] == 2000.0
        assert reductions["frais_garde"] == 1500.0
        assert impot_net == 10000 - 4820

    def test_reductions_cannot_make_negative_tax(self):
        """Test that reductions cannot make tax negative."""
        impot_net, reductions = apply_tax_reductions(
            impot_brut=1000,
            revenu_imposable=50000,
            reductions_data={
                "dons": 2000,  # Would give 1320€ reduction
                "services_personne": 2000,  # Would give 1000€ reduction
            },
        )

        # Total reduction would be 2320€, but tax is only 1000€
        # Result should be 0, not negative
        assert impot_net == 0.0


class TestEnhancedComputeIR:
    """Test enhanced compute_ir with complete data."""

    @pytest.fixture
    def rules(self):
        """Load 2024 tax rules."""
        return get_tax_rules(2024)

    def test_compute_ir_with_tmi(self, rules):
        """Test that compute_ir returns TMI."""
        result = compute_ir(
            person={"nb_parts": 1.0, "status": "micro_bnc"},
            income={"professional_gross": 50000},
            deductions={},
            rules=rules,
        )

        assert "tmi" in result
        assert isinstance(result["tmi"], float)
        assert result["tmi"] in [0.0, 0.11, 0.30, 0.41, 0.45]

    def test_compute_ir_with_tax_reductions(self, rules):
        """Test that compute_ir returns tax reductions."""
        result = compute_ir(
            person={"nb_parts": 1.0, "status": "micro_bnc"},
            income={"professional_gross": 50000},
            deductions={
                "dons_declared": 1000,
                "services_personne_declared": 2000,
            },
            rules=rules,
        )

        assert "tax_reductions" in result
        assert isinstance(result["tax_reductions"], dict)

    def test_compute_ir_with_brackets_detail(self, rules):
        """Test that compute_ir returns bracket details."""
        result = compute_ir(
            person={"nb_parts": 1.0, "status": "micro_bnc"},
            income={"professional_gross": 50000},
            deductions={},
            rules=rules,
        )

        assert "brackets" in result
        assert isinstance(result["brackets"], list)
        # Should have at least one bracket with income
        assert len(result["brackets"]) > 0

    def test_compute_ir_with_per_deduction_info(self, rules):
        """Test that compute_ir returns PER deduction details."""
        result = compute_ir(
            person={"nb_parts": 1.0, "status": "micro_bnc"},
            income={"professional_gross": 50000},
            deductions={"per_contributions": 3000},
            rules=rules,
        )

        assert "per_deduction_applied" in result
        assert "per_deduction_excess" in result
        assert result["per_deduction_applied"] == 3000
        assert result["per_deduction_excess"] == 0.0

    def test_compute_ir_per_plafond_limit_applied(self, rules):
        """Test that PER plafond limit is actually applied."""
        # Professional income of 50k → taxable ≈ 33k (after 34% abattement)
        # PER plafond ≈ 3300€ (10% of 33k)
        # Try to contribute 10k → should be limited

        result = compute_ir(
            person={"nb_parts": 1.0, "status": "micro_bnc"},
            income={"professional_gross": 50000},
            deductions={"per_contributions": 10000},
            rules=rules,
        )

        # Should have excess amount
        assert result["per_deduction_excess"] > 0
        # Applied amount should be less than contributed amount
        assert result["per_deduction_applied"] < 10000

    def test_complete_calculation_with_all_features(self, rules):
        """Test complete calculation with all new features."""
        result = compute_ir(
            person={"nb_parts": 2.0, "status": "micro_bnc"},
            income={
                "professional_gross": 80000,
                "salary": 20000,
            },
            deductions={
                "per_contributions": 5000,
                "dons_declared": 1500,
                "services_personne_declared": 3000,
                "frais_garde_declared": 2000,
                "children_under_6": 1,
            },
            rules=rules,
        )

        # Verify all new fields are present
        assert "tmi" in result
        assert "tax_reductions" in result
        assert "brackets" in result
        assert "per_deduction_applied" in result
        assert "per_deduction_excess" in result

        # Verify tax reductions were applied
        assert result["impot_net"] < result["impot_brut"]
        assert len(result["tax_reductions"]) > 0

    def test_backward_compatibility_basic_fields(self, rules):
        """Test that basic fields are still present (backward compatibility)."""
        result = compute_ir(
            person={"nb_parts": 1.0, "status": "micro_bnc"},
            income={"professional_gross": 50000},
            deductions={},
            rules=rules,
        )

        # Old fields should still be there
        assert "revenu_imposable" in result
        assert "part_income" in result
        assert "impot_brut" in result
        assert "impot_net" in result
