"""Tests for tax optimization engine (Phase 4)."""

import pytest

from src.analyzers.optimizer import TaxOptimizer
from src.analyzers.strategies.deductions_strategy import DeductionsStrategy
from src.analyzers.strategies.fcpi_fip_strategy import FCPIFIPStrategy
from src.analyzers.strategies.girardin_strategy import GirardinStrategy
from src.analyzers.strategies.lmnp_strategy import LMNPStrategy
from src.analyzers.strategies.per_strategy import PERStrategy
from src.analyzers.strategies.regime_strategy import RegimeStrategy
from src.analyzers.strategies.structure_strategy import StructureStrategy
from src.tax_engine.rules import get_tax_rules
from src.tax_engine.tax_utils import calculate_per_plafond

# ============================================================================
# REGIME OPTIMIZATION TESTS (6 tests)
# ============================================================================


def test_regime_micro_to_reel_recommendation():
    """Test regime recommendation when réel is better than micro."""
    strategy = RegimeStrategy()

    # Tax result with micro vs réel comparison
    tax_result = {
        "comparisons": {
            "micro_vs_reel": {
                "impot_micro": 2000,
                "impot_reel": 1200,
                "delta_total": 800,  # 800€ savings with réel
                "recommendation": "reel",
                "recommendation_reason": "Frais réels > abattement",
            }
        }
    }

    profile = {"status": "micro_bnc", "chiffre_affaires": 50000}
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    assert recs[0].category.value == "regime"
    assert recs[0].impact_estimated == 800
    assert "réel" in recs[0].title.lower()


def test_regime_reel_to_micro_recommendation():
    """Test regime recommendation when micro is better than réel."""
    strategy = RegimeStrategy()

    tax_result = {
        "comparisons": {
            "micro_vs_reel": {
                "impot_micro": 1000,
                "impot_reel": 1600,
                "delta_total": 600,
                "recommendation": "micro",
                "recommendation_reason": "Micro recommandé (simplicité)",
            }
        }
    }

    profile = {"status": "reel_bnc", "chiffre_affaires": 30000}
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    assert recs[0].impact_estimated == 600
    assert "micro" in recs[0].title.lower()


def test_regime_threshold_proximity_warning():
    """Test warning when approaching micro threshold."""
    strategy = RegimeStrategy()

    tax_result = {"comparisons": {}}

    # Revenue at 90% of threshold
    profile = {"status": "micro_bnc", "chiffre_affaires": 70000}
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    assert "seuil" in recs[0].title.lower() or "alerte" in recs[0].title.lower()


def test_regime_no_recommendation_when_similar():
    """Test no recommendation when micro and réel are similar."""
    strategy = RegimeStrategy()

    tax_result = {
        "comparisons": {
            "micro_vs_reel": {
                "impot_micro": 1500,
                "impot_reel": 1450,
                "delta_total": 50,  # Only 50€ difference - not significant
                "recommendation": "reel",
            }
        }
    }

    profile = {"status": "micro_bnc", "chiffre_affaires": 40000}
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0  # No recommendation for small difference


def test_regime_no_warning_when_below_threshold():
    """Test no warning when well below threshold."""
    strategy = RegimeStrategy()

    tax_result = {"comparisons": {}}
    profile = {"status": "micro_bnc", "chiffre_affaires": 40000}  # ~50% of threshold
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    # May have regime comparison but no threshold warning
    threshold_warnings = [
        r for r in recs if "seuil" in r.title.lower() or "alert" in r.title.lower()
    ]
    assert len(threshold_warnings) == 0


def test_regime_bic_services_threshold():
    """Test threshold warning for BIC services."""
    strategy = RegimeStrategy()

    tax_result = {"comparisons": {}}
    profile = {
        "status": "micro_bic_services",
        "chiffre_affaires": 72000,  # Close to 77,700 threshold
    }
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    threshold_warnings = [r for r in recs if "seuil" in r.title.lower()]
    assert len(threshold_warnings) == 1


# ============================================================================
# PER OPTIMIZATION TESTS (7 tests)
# ============================================================================


def test_per_recommendation_for_high_tmi():
    """Test PER recommendation for high marginal tax rate."""
    strategy = PERStrategy()

    # High income = high TMI
    tax_result = {"impot": {"revenu_imposable": 60000}}

    profile = {"nb_parts": 1.0}
    context = {"per_contributed": 0}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) > 0
    # With 60k revenue and TMI 30%, should recommend PER
    assert recs[0].category.value == "investment"
    assert recs[0].impact_estimated > 1000  # Adjusted to realistic value
    assert "PER" in recs[0].title


def test_per_max_recommendation():
    """Test PER max recommendation for very high income."""
    strategy = PERStrategy()

    tax_result = {"impot": {"revenu_imposable": 100000}}
    profile = {"nb_parts": 1.0}
    context = {"per_contributed": 0}

    recs = strategy.analyze(tax_result, profile, context)

    # Should get both optimal and max recommendations
    assert len(recs) >= 1
    assert any("max" in r.title.lower() for r in recs)


def test_per_with_existing_contribution():
    """Test PER when user already contributed some amount."""
    strategy = PERStrategy()

    tax_result = {"impot": {"revenu_imposable": 50000}}
    profile = {"nb_parts": 1.0}
    context = {"per_contributed": 2000}  # Already contributed 2k

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) >= 1
    # Plafond = 5000€, already contributed 2000€
    # Remaining = 3000€
    assert recs[0].required_investment < 5000


def test_per_no_recommendation_for_low_income():
    """Test no PER recommendation for low taxable income."""
    strategy = PERStrategy()

    tax_result = {"impot": {"revenu_imposable": 8000}}  # Below TMI 11%
    profile = {"nb_parts": 1.0}
    context = {"per_contributed": 0}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0


def test_per_plafond_calculation():
    """Test PER plafond calculation (10% of revenue)."""
    rules = get_tax_rules(2024)

    revenue = 40000
    plafond = calculate_per_plafond(revenue, rules, status="salarie")

    # 10% of 40k = 4000, but minimum is 4399
    assert plafond == 4399


def test_per_tmi_estimation():
    """Test TMI estimation using centralized function."""
    from src.tax_engine.core import calculate_tmi
    from src.tax_engine.rules import get_tax_rules

    rules = get_tax_rules(2024)

    # Test each bracket
    assert calculate_tmi(10000, 1.0, rules) == 0.0
    assert calculate_tmi(20000, 1.0, rules) == 0.11
    assert calculate_tmi(40000, 1.0, rules) == 0.30
    assert calculate_tmi(100000, 1.0, rules) == 0.41
    assert calculate_tmi(200000, 1.0, rules) == 0.45


def test_per_with_quotient_familial():
    """Test PER recommendation with multiple parts."""
    strategy = PERStrategy()

    tax_result = {"impot": {"revenu_imposable": 50000}}
    profile = {"nb_parts": 2.5}  # Married with 1 child
    context = {"per_contributed": 0}

    recs = strategy.analyze(tax_result, profile, context)

    # With 2.5 parts, revenu_par_part = 20k = TMI 11%
    # May still get recommendation but with lower impact
    if len(recs) > 0:
        assert recs[0].impact_estimated < 2000  # Lower than single person


# ============================================================================
# LMNP OPTIMIZATION TESTS (5 tests)
# ============================================================================


def test_lmnp_recommendation_for_eligible_profile():
    """Test LMNP for eligible profile (high TMI + investment capacity)."""
    strategy = LMNPStrategy()

    tax_result = {"impot": {"revenu_imposable": 60000}}
    profile = {"nb_parts": 1.0}
    context = {"investment_capacity": 100000, "risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    assert recs[0].category.value == "investment"
    assert "LMNP" in recs[0].title
    assert recs[0].risk.value == "medium"
    assert recs[0].complexity.value == "complex"


def test_lmnp_no_recommendation_for_low_tmi():
    """Test no LMNP for low TMI."""
    strategy = LMNPStrategy()

    tax_result = {"impot": {"revenu_imposable": 20000}}  # TMI 11%
    profile = {"nb_parts": 1.0}
    context = {"investment_capacity": 100000, "risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0


def test_lmnp_no_recommendation_for_low_investment_capacity():
    """Test no LMNP for insufficient investment capacity."""
    strategy = LMNPStrategy()

    tax_result = {"impot": {"revenu_imposable": 60000}}
    profile = {"nb_parts": 1.0}
    context = {"investment_capacity": 20000, "risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0


def test_lmnp_profina_warning():
    """Test LMNP includes important warnings."""
    strategy = LMNPStrategy()

    tax_result = {"impot": {"revenu_imposable": 70000}}
    profile = {"nb_parts": 1.0}
    context = {"investment_capacity": 150000, "risk_tolerance": "high"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    assert len(recs[0].warnings) > 0
    assert any("comptable" in w.lower() for w in recs[0].warnings)


def test_lmnp_estimated_savings():
    """Test LMNP estimated savings calculation."""
    strategy = LMNPStrategy()

    tax_result = {"impot": {"revenu_imposable": 80000}}  # TMI 41%
    profile = {"nb_parts": 1.0}
    context = {"investment_capacity": 200000, "risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    # With 200k investment, 4% yield = 8k rental
    # TMI 41% × 85% (reduction factor) = ~2700€ savings
    assert recs[0].impact_estimated > 2000


# ============================================================================
# GIRARDIN OPTIMIZATION TESTS (4 tests)
# ============================================================================


def test_girardin_recommendation_with_profina():
    """Test Girardin recommendation includes Profina."""
    strategy = GirardinStrategy()

    tax_result = {"impot": {"impot_net": 5000}}
    profile = {}
    context = {
        "risk_tolerance": "medium",
        "stable_income": True,
    }

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    assert "Girardin" in recs[0].title
    assert "Profina" in recs[0].title or "Profina" in recs[0].description
    assert recs[0].risk.value == "high"
    assert recs[0].category.value == "investment"


def test_girardin_110_percent_reduction():
    """Test Girardin 110% reduction calculation."""
    strategy = GirardinStrategy()

    tax_result = {"impot": {"impot_net": 6000}}
    profile = {}
    context = {"risk_tolerance": "high", "stable_income": True}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 1
    # Should have net positive gain due to 110% reduction
    assert recs[0].impact_estimated > 0


def test_girardin_no_recommendation_for_low_impot():
    """Test no Girardin for low tax."""
    strategy = GirardinStrategy()

    tax_result = {"impot": {"impot_net": 2000}}  # Below 3000€ minimum
    profile = {}
    context = {"risk_tolerance": "high", "stable_income": True}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0


def test_girardin_no_recommendation_for_low_risk_tolerance():
    """Test no Girardin for conservative profile."""
    strategy = GirardinStrategy()

    tax_result = {"impot": {"impot_net": 5000}}
    profile = {}
    context = {"risk_tolerance": "low", "stable_income": True}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0


# ============================================================================
# FCPI/FIP OPTIMIZATION TESTS (4 tests)
# ============================================================================


def test_fcpi_recommendation():
    """Test FCPI recommendation for eligible profile."""
    strategy = FCPIFIPStrategy()

    # Need sufficient impot for recommendation (30% * impot should be >= 1000)
    tax_result = {"impot": {"impot_net": 4000}}
    profile = {"nb_parts": 1.0}
    context = {"risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) >= 1  # May get 1 or more recommendations
    assert any("FCPI" in rec.title for rec in recs)
    # Check first FCPI rec
    fcpi_rec = [r for r in recs if "FCPI" in r.title][0]
    assert fcpi_rec.risk.value == "medium"
    # 18% reduction
    assert fcpi_rec.impact_estimated > 0


def test_fcpi_18_percent_reduction():
    """Test FCPI 18% reduction calculation."""
    strategy = FCPIFIPStrategy()

    # Need sufficient impot for recommendation
    tax_result = {"impot": {"impot_net": 5000}}
    profile = {"nb_parts": 1.0}
    context = {"risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) >= 1
    # Get FCPI recommendation
    fcpi_recs = [r for r in recs if "FCPI" in r.title]
    assert len(fcpi_recs) >= 1
    # Investment should result in 18% reduction
    reduction = fcpi_recs[0].impact_estimated
    investment = fcpi_recs[0].required_investment
    assert abs(reduction / investment - 0.18) < 0.01  # Should be ~18%


def test_fcpi_no_recommendation_for_low_impot():
    """Test no FCPI for low tax."""
    strategy = FCPIFIPStrategy()

    tax_result = {"impot": {"impot_net": 800}}  # Below 1000€ minimum
    profile = {"nb_parts": 1.0}
    context = {"risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0


def test_fcpi_couple_plafond():
    """Test FCPI plafond for couples (2+ parts)."""
    strategy = FCPIFIPStrategy()

    tax_result = {"impot": {"impot_net": 5000}}
    profile = {"nb_parts": 2.5}  # Couple
    context = {"risk_tolerance": "moderate"}

    recs = strategy.analyze(tax_result, profile, context)

    if len(recs) > 0:
        # Couple plafond is 24,000€ vs 12,000€ for single
        assert "24000" in recs[0].description or "24 000" in recs[0].description


# ============================================================================
# DEDUCTIONS STRATEGY TESTS (5 tests)
# ============================================================================


def test_dons_recommendation():
    """Test donation deduction recommendation."""
    strategy = DeductionsStrategy()

    tax_result = {"impot": {"revenu_imposable": 40000}}
    profile = {}
    context = {"dons_declared": 0}

    recs = strategy.analyze(tax_result, profile, context)

    dons_recs = [r for r in recs if "don" in r.title.lower()]
    assert len(dons_recs) == 1
    assert "66" in dons_recs[0].description  # 66% reduction


def test_services_personne_recommendation():
    """Test services à la personne recommendation."""
    strategy = DeductionsStrategy()

    tax_result = {"impot": {"impot_net": 2000}}
    profile = {}
    context = {"services_personne_declared": 0}

    recs = strategy.analyze(tax_result, profile, context)

    services_recs = [r for r in recs if "service" in r.title.lower()]
    assert len(services_recs) == 1
    assert "50" in services_recs[0].description  # 50% credit


def test_frais_garde_recommendation():
    """Test childcare deduction recommendation."""
    strategy = DeductionsStrategy()

    tax_result = {"impot": {"impot_net": 1500}}
    profile = {}
    context = {"children_under_6": 2, "frais_garde_declared": 0}

    recs = strategy.analyze(tax_result, profile, context)

    garde_recs = [r for r in recs if "garde" in r.title.lower()]
    assert len(garde_recs) == 1
    assert "2" in garde_recs[0].title  # 2 children


def test_no_garde_recommendation_without_children():
    """Test no childcare recommendation without young children."""
    strategy = DeductionsStrategy()

    tax_result = {"impot": {"impot_net": 2000}}
    profile = {}
    context = {"children_under_6": 0}

    recs = strategy.analyze(tax_result, profile, context)

    garde_recs = [r for r in recs if "garde" in r.title.lower()]
    assert len(garde_recs) == 0


def test_multiple_deductions():
    """Test multiple deduction recommendations."""
    strategy = DeductionsStrategy()

    tax_result = {"impot": {"revenu_imposable": 50000, "impot_net": 3000}}
    profile = {}
    context = {
        "dons_declared": 0,
        "services_personne_declared": 0,
        "children_under_6": 1,
        "frais_garde_declared": 0,
    }

    recs = strategy.analyze(tax_result, profile, context)

    # Should get dons, services, and garde
    assert len(recs) >= 2


# ============================================================================
# STRUCTURE STRATEGY TESTS (3 tests)
# ============================================================================


def test_sasu_recommendation_for_high_revenue():
    """Test SASU/EURL recommendation for high revenue."""
    strategy = StructureStrategy()

    tax_result = {}
    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 80000,
        "charges_deductibles": 25000,
    }
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) >= 1
    sasu_recs = [
        r for r in recs if "sasu" in r.title.lower() or "eurl" in r.title.lower()
    ]
    assert len(sasu_recs) == 1
    assert sasu_recs[0].complexity.value == "complex"


def test_holding_recommendation():
    """Test holding recommendation for very high revenue with patrimony strategy."""
    strategy = StructureStrategy()

    tax_result = {}
    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 150000,
        "charges_deductibles": 50000,
    }
    context = {"patrimony_strategy": True}

    recs = strategy.analyze(tax_result, profile, context)

    # Should recommend both SASU and holding
    assert len(recs) >= 1
    holding_recs = [r for r in recs if "holding" in r.title.lower()]
    assert len(holding_recs) == 1


def test_no_structure_recommendation_for_low_revenue():
    """Test no structure recommendation for low revenue."""
    strategy = StructureStrategy()

    tax_result = {}
    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 30000,
        "charges_deductibles": 5000,
    }
    context = {}

    recs = strategy.analyze(tax_result, profile, context)

    assert len(recs) == 0


# ============================================================================
# FULL OPTIMIZER INTEGRATION TESTS (6 tests)
# ============================================================================


@pytest.mark.anyio
async def test_optimizer_basic_scenario():
    """Test full optimizer with basic scenario."""
    optimizer = TaxOptimizer()

    tax_result = {
        "impot": {"revenu_imposable": 30000, "impot_net": 1500},
        "comparisons": {
            "micro_vs_reel": {
                "impot_micro": 1500,
                "impot_reel": 1200,
                "delta_total": 300,
                "recommendation": "reel",
            }
        },
    }

    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 30000,
        "charges_deductibles": 8000,
        "nb_parts": 1.0,
    }

    context = {"risk_tolerance": "conservative", "per_contributed": 0}

    result = await optimizer.run(tax_result, profile, context)

    assert result.potential_savings_total > 0
    assert len(result.recommendations) > 0
    assert result.summary != ""


@pytest.mark.anyio
async def test_optimizer_high_income_scenario():
    """Test full optimizer with high income scenario."""
    optimizer = TaxOptimizer()

    tax_result = {
        "impot": {"revenu_imposable": 100000, "impot_net": 25000},
        "comparisons": {},
    }

    profile = {
        "status": "reel_bnc",
        "chiffre_affaires": 120000,
        "charges_deductibles": 30000,
        "nb_parts": 1.0,
    }

    context = {
        "risk_tolerance": "aggressive",
        "investment_capacity": 200000,
        "stable_income": True,
        "per_contributed": 0,
    }

    result = await optimizer.run(tax_result, profile, context)

    # High income should trigger multiple recommendations
    assert len(result.recommendations) >= 3
    assert result.potential_savings_total > 5000


@pytest.mark.anyio
async def test_optimizer_conservative_profile():
    """Test optimizer with conservative risk profile."""
    optimizer = TaxOptimizer()

    tax_result = {"impot": {"revenu_imposable": 40000, "impot_net": 3000}}

    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 40000,
        "nb_parts": 1.0,
    }

    context = {"risk_tolerance": "conservative"}

    result = await optimizer.run(tax_result, profile, context)

    # Conservative should only get low-risk recommendations
    for rec in result.recommendations:
        assert rec.risk.value in ["low", "medium"]


@pytest.mark.anyio
async def test_optimizer_family_scenario():
    """Test optimizer with family (children)."""
    optimizer = TaxOptimizer()

    tax_result = {"impot": {"revenu_imposable": 50000, "impot_net": 2000}}

    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 50000,
        "nb_parts": 2.5,
    }

    context = {
        "children_under_6": 2,
        "frais_garde_declared": 0,
        "services_personne_declared": 0,
    }

    result = await optimizer.run(tax_result, profile, context)

    # Should include garde d'enfants recommendation
    garde_recs = [r for r in result.recommendations if "garde" in r.title.lower()]
    assert len(garde_recs) > 0


@pytest.mark.anyio
async def test_optimizer_sorting_by_impact():
    """Test recommendations are sorted by impact."""
    optimizer = TaxOptimizer()

    tax_result = {
        "impot": {"revenu_imposable": 80000, "impot_net": 10000},
        "comparisons": {},
    }

    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 100000,
        "charges_deductibles": 30000,
        "nb_parts": 1.0,
    }

    context = {
        "risk_tolerance": "moderate",
        "investment_capacity": 150000,
        "stable_income": True,
        "per_contributed": 0,
    }

    result = await optimizer.run(tax_result, profile, context)

    # Recommendations should be sorted by impact (descending)
    for i in range(len(result.recommendations) - 1):
        assert (
            result.recommendations[i].impact_estimated
            >= result.recommendations[i + 1].impact_estimated
        )


@pytest.mark.anyio
async def test_optimizer_metadata():
    """Test optimizer includes proper metadata."""
    optimizer = TaxOptimizer()

    tax_result = {"impot": {"revenu_imposable": 50000, "impot_net": 3000}}

    profile = {
        "status": "micro_bnc",
        "chiffre_affaires": 50000,
        "nb_parts": 1.0,
    }

    context = {"risk_tolerance": "moderate"}

    result = await optimizer.run(tax_result, profile, context)

    assert "total_recommendations" in result.metadata
    assert "by_category" in result.metadata
    assert "by_risk" in result.metadata
    assert "by_complexity" in result.metadata
    assert "disclaimer" in result.metadata
    assert result.metadata["total_recommendations"] == len(result.recommendations)


# ============================================================================
# QUICK SIMULATION TESTS (BONUS FEATURE - 6 tests)
# ============================================================================


@pytest.mark.anyio
async def test_quick_simulation_basic():
    """Test basic quick simulation with default values."""
    from src.api.routes.optimization import QuickSimulationInput, quick_simulation

    input_data = QuickSimulationInput(
        chiffre_affaires=50000,
        charges_reelles=10000,
        status="micro_bnc",
        situation_familiale="celibataire",
        enfants=0,
    )

    result = await quick_simulation(input_data)

    # Basic assertions
    assert result.impot_actuel_estime > 0
    assert result.impot_optimise >= 0
    assert result.economies_potentielles >= 0
    assert 0 <= result.tmi <= 0.45
    assert result.regime_actuel in ["Micro", "Réel"]
    assert result.regime_recommande in ["Micro", "Réel"]
    assert result.per_plafond >= 4399  # Minimum PER plafond
    assert len(result.quick_wins) > 0
    assert len(result.message_accroche) > 0


@pytest.mark.anyio
async def test_quick_simulation_high_savings():
    """Test quick simulation with high potential savings."""
    from src.api.routes.optimization import QuickSimulationInput, quick_simulation

    # High revenue with low expenses = high potential savings
    input_data = QuickSimulationInput(
        chiffre_affaires=80000,
        charges_reelles=15000,
        status="micro_bnc",
        situation_familiale="celibataire",
        enfants=0,
    )

    result = await quick_simulation(input_data)

    # Should generate high savings message
    assert (
        "💣 ALERTE" in result.message_accroche
        or "💡 Bonne nouvelle" in result.message_accroche
    )
    assert result.economies_potentielles > 500
    assert len(result.quick_wins) >= 2  # Should have multiple recommendations


@pytest.mark.anyio
async def test_quick_simulation_married_with_children():
    """Test quick simulation with married couple and children."""
    from src.api.routes.optimization import QuickSimulationInput, quick_simulation

    input_data = QuickSimulationInput(
        chiffre_affaires=60000,
        charges_reelles=12000,
        status="micro_bnc",
        situation_familiale="marie",
        enfants=2,
    )

    result = await quick_simulation(input_data)

    # nb_parts should be 2 (married) + 2 * 0.5 (children) = 3
    # Lower TMI expected due to higher nb_parts
    assert result.tmi < 0.30  # Should be lower with 3 parts
    assert result.impot_actuel_estime < 5000  # Lower tax with more parts


@pytest.mark.anyio
async def test_quick_simulation_reel_status():
    """Test quick simulation when already on réel regime."""
    from src.api.routes.optimization import QuickSimulationInput, quick_simulation

    input_data = QuickSimulationInput(
        chiffre_affaires=50000,
        charges_reelles=20000,
        status="reel_bnc",
        situation_familiale="celibataire",
        enfants=0,
    )

    result = await quick_simulation(input_data)

    assert result.regime_actuel == "Réel"
    # With high charges (40%), réel should be recommended
    assert result.changement_regime_gain >= 0


@pytest.mark.anyio
async def test_quick_simulation_no_charges():
    """Test quick simulation with no charges declared."""
    from src.api.routes.optimization import QuickSimulationInput, quick_simulation

    input_data = QuickSimulationInput(
        chiffre_affaires=50000,
        charges_reelles=0,  # No charges
        status="micro_bnc",
        situation_familiale="celibataire",
        enfants=0,
    )

    result = await quick_simulation(input_data)

    # Should recommend declaring charges if on micro
    assert any("frais réels" in win.lower() for win in result.quick_wins)


@pytest.mark.anyio
async def test_quick_simulation_per_recommendation():
    """Test PER recommendation calculation in quick simulation."""
    from src.api.routes.optimization import QuickSimulationInput, quick_simulation

    input_data = QuickSimulationInput(
        chiffre_affaires=70000,
        charges_reelles=10000,
        status="micro_bnc",
        situation_familiale="celibataire",
        enfants=0,
    )

    result = await quick_simulation(input_data)

    # PER plafond should be 10% of revenue (micro income)
    # revenu_micro = 70000 * (1 - 0.34) = 46200
    # per_plafond = max(4399, min(35200, 46200 * 0.10)) = 4620
    assert result.per_plafond > 4399
    assert result.per_plafond <= 35200

    # Optimal contribution is 70% of plafond
    assert result.per_versement_optimal == pytest.approx(
        result.per_plafond * 0.70, rel=0.01
    )

    # Savings should be versement * TMI
    assert result.per_economie == pytest.approx(
        result.per_versement_optimal * result.tmi, rel=0.01
    )
