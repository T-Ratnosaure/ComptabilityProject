"""Optimization API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.analyzers.optimizer import TaxOptimizer
from src.models.optimization import OptimizationResult

router = APIRouter(prefix="/optimization", tags=["optimization"])


class ProfileInput(BaseModel):
    """User profile for optimization."""

    status: str = Field(..., description="Tax status (micro_bnc, reel_bnc, etc.)")
    annual_revenue: float = Field(..., description="Annual revenue in euros", ge=0)
    annual_expenses: float = Field(
        default=0, description="Annual expenses in euros", ge=0
    )
    nb_parts: float = Field(default=1.0, description="Number of tax parts", gt=0)
    activity_type: str = Field(default="BNC", description="Activity type (BNC/BIC)")


class OptimizationContext(BaseModel):
    """Additional context for optimization."""

    risk_tolerance: str = Field(
        default="moderate",
        description="Risk tolerance (conservative, moderate, aggressive)",
    )
    investment_capacity: float = Field(
        default=0, description="Investment capacity in euros", ge=0
    )
    stable_income: bool = Field(default=False, description="Whether income is stable")
    per_contributed: float = Field(
        default=0, description="PER contributions this year", ge=0
    )
    dons_declared: float = Field(
        default=0, description="Donations already declared", ge=0
    )
    services_personne_declared: float = Field(
        default=0, description="Services à la personne already declared", ge=0
    )
    frais_garde_declared: float = Field(
        default=0, description="Childcare expenses already declared", ge=0
    )
    children_under_6: int = Field(
        default=0, description="Number of children under 6", ge=0
    )
    patrimony_strategy: bool = Field(
        default=False, description="Has a patrimony strategy"
    )


class OptimizationRequest(BaseModel):
    """Complete optimization request."""

    tax_result: dict = Field(..., description="Tax calculation result from Phase 3")
    profile: ProfileInput = Field(..., description="User profile")
    context: OptimizationContext = Field(
        default_factory=OptimizationContext,
        description="Additional optimization context",
    )


@router.post("/run", response_model=OptimizationResult)
async def run_optimization(
    request: OptimizationRequest,
) -> OptimizationResult:
    """
    Run complete tax optimization analysis.

    Analyzes the user's tax situation and returns personalized
    optimization recommendations including:
    - Regime optimization (micro vs réel)
    - PER contributions
    - LMNP investment
    - Girardin (via Profina)
    - FCPI/FIP
    - Simple deductions (dons, services, garde)
    - Company structure (SASU, EURL, holding)

    Args:
        request: Optimization request with tax result, profile, and context

    Returns:
        OptimizationResult with ranked recommendations and summary

    Raises:
        HTTPException: If optimization fails
    """
    try:
        optimizer = TaxOptimizer()

        result = await optimizer.run(
            tax_result=request.tax_result,
            profile=request.profile.model_dump(),
            context=request.context.model_dump(),
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Optimization failed: {str(e)}",
        ) from e


@router.get("/strategies", response_model=dict)
async def list_strategies() -> dict:
    """
    List all available optimization strategies.

    Returns:
        Dictionary of strategies with descriptions
    """
    return {
        "strategies": [
            {
                "name": "regime",
                "description": "Optimisation du régime fiscal (micro vs réel)",
                "category": "regime",
            },
            {
                "name": "per",
                "description": "Plan Épargne Retraite (PER)",
                "category": "investment",
            },
            {
                "name": "lmnp",
                "description": "Location Meublée Non Professionnelle",
                "category": "investment",
            },
            {
                "name": "girardin",
                "description": "Girardin Industriel (via Profina)",
                "category": "investment",
            },
            {
                "name": "fcpi_fip",
                "description": "FCPI / FIP",
                "category": "investment",
            },
            {
                "name": "deductions",
                "description": "Déductions simples (dons, services, garde)",
                "category": "deduction",
            },
            {
                "name": "structure",
                "description": "Structuration entreprise (SASU, EURL, holding)",
                "category": "structure",
            },
        ]
    }


# 💣 BONUS: Quick Simulation for Landing Page / Acquisition
# This is the viral feature: "Calcule combien tu paies trop d'impôts"


class QuickSimulationInput(BaseModel):
    """Minimal input for quick 30-second simulation."""

    chiffre_affaires: float = Field(
        ..., description="Annual revenue (CA) in euros", ge=0, le=500000
    )
    charges_reelles: float = Field(
        default=0,
        description="Real expenses in euros (0 if unknown)",
        ge=0,
    )
    status: str = Field(
        default="micro_bnc",
        description="Current status (micro_bnc, micro_bic, reel_bnc, reel_bic)",
    )
    situation_familiale: str = Field(
        default="celibataire",
        description="Family situation (celibataire, marie, pacse)",
    )
    enfants: int = Field(default=0, description="Number of children", ge=0, le=10)


class QuickSimulationResult(BaseModel):
    """Quick simulation result with key insights."""

    # Headline numbers
    impot_actuel_estime: float = Field(
        ..., description="Estimated current tax amount"
    )
    impot_optimise: float = Field(..., description="Optimized tax amount")
    economies_potentielles: float = Field(
        ..., description="Total potential savings"
    )

    # Key insights
    tmi: float = Field(..., description="Marginal tax rate (TMI)")
    regime_actuel: str = Field(..., description="Current regime")
    regime_recommande: str = Field(..., description="Recommended regime")
    changement_regime_gain: float = Field(
        ..., description="Savings from regime change"
    )

    # PER recommendation
    per_plafond: float = Field(..., description="PER plafond for the year")
    per_versement_optimal: float = Field(..., description="Optimal PER contribution")
    per_economie: float = Field(..., description="Tax savings from PER")

    # Quick wins
    quick_wins: list[str] = Field(
        default_factory=list, description="List of quick actionable wins"
    )

    # Call to action
    message_accroche: str = Field(..., description="Catchy message for user")


@router.post("/quick-simulation", response_model=QuickSimulationResult)
async def quick_simulation(input_data: QuickSimulationInput) -> QuickSimulationResult:
    """
    🧨 VIRAL FEATURE: Quick 30-second tax simulation.

    Perfect for landing pages with "Calcule combien tu paies trop d'impôts".

    This endpoint provides instant insights:
    - Current vs optimized tax amount
    - TMI (marginal tax rate)
    - Micro vs Réel comparison
    - PER recommendation
    - Total potential savings

    Args:
        input_data: Minimal input (CA, charges, status, family)

    Returns:
        Quick simulation with headline numbers and quick wins

    Example:
        Input: CA 50k€, charges 10k€, célibataire
        Output: "Vous payez 2,500€ d'impôts. Vous pourriez économiser 1,200€!"
    """
    # Calculate nb_parts from family situation
    nb_parts = 1.0
    if input_data.situation_familiale in ["marie", "pacse"]:
        nb_parts = 2.0
    nb_parts += input_data.enfants * 0.5

    # Determine if BNC or BIC
    is_bnc = "bnc" in input_data.status.lower()
    activity_type = "BNC" if is_bnc else "BIC"

    # Get abattement rate for micro
    if is_bnc:
        abattement_rate = 0.34  # BNC
    else:
        abattement_rate = 0.50  # BIC services (conservative)

    # Calculate micro taxable income
    revenu_micro = input_data.chiffre_affaires * (1 - abattement_rate)

    # Calculate réel taxable income
    revenu_reel = input_data.chiffre_affaires - input_data.charges_reelles

    # Estimate TMI based on income
    revenu_par_part_micro = revenu_micro / nb_parts
    if revenu_par_part_micro <= 11294:
        tmi = 0.0
    elif revenu_par_part_micro <= 28797:
        tmi = 0.11
    elif revenu_par_part_micro <= 82341:
        tmi = 0.30
    elif revenu_par_part_micro <= 177106:
        tmi = 0.41
    else:
        tmi = 0.45

    # Quick tax calculation (simplified)
    def calculate_simple_tax(revenu_imposable: float, nb_parts: float) -> float:
        """Simplified tax calculation."""
        revenu_par_part = revenu_imposable / nb_parts

        # Apply brackets
        tax_par_part = 0.0
        if revenu_par_part > 11294:
            tax_par_part += min(revenu_par_part - 11294, 28797 - 11294) * 0.11
        if revenu_par_part > 28797:
            tax_par_part += min(revenu_par_part - 28797, 82341 - 28797) * 0.30
        if revenu_par_part > 82341:
            tax_par_part += min(revenu_par_part - 82341, 177106 - 82341) * 0.41
        if revenu_par_part > 177106:
            tax_par_part += (revenu_par_part - 177106) * 0.45

        return tax_par_part * nb_parts

    # Calculate tax for both regimes
    impot_micro = calculate_simple_tax(revenu_micro, nb_parts)
    impot_reel = calculate_simple_tax(revenu_reel, nb_parts)

    # Determine current and recommended regime
    regime_actuel = "Micro" if "micro" in input_data.status.lower() else "Réel"

    if impot_micro < impot_reel:
        regime_recommande = "Micro"
        impot_actuel = impot_micro if regime_actuel == "Micro" else impot_reel
        impot_optimise_regime = impot_micro
    else:
        regime_recommande = "Réel"
        impot_actuel = impot_micro if regime_actuel == "Micro" else impot_reel
        impot_optimise_regime = impot_reel

    changement_regime_gain = abs(impot_micro - impot_reel)

    # PER calculation
    per_plafond = max(4399, min(35200, revenu_micro * 0.10))
    per_versement_optimal = per_plafond * 0.70  # 70% of plafond
    per_economie = per_versement_optimal * tmi

    # Total optimized tax (with PER)
    revenu_apres_per = revenu_micro - per_versement_optimal
    impot_avec_per = calculate_simple_tax(revenu_apres_per, nb_parts)

    # Total savings
    economies_regime = (
        changement_regime_gain if regime_actuel != regime_recommande else 0
    )
    economies_totales = economies_regime + per_economie

    # Optimized tax amount
    impot_optimise = impot_actuel - economies_totales

    # Generate quick wins
    quick_wins = []

    if regime_actuel != regime_recommande and changement_regime_gain > 500:
        quick_wins.append(
            f"💰 Passer au régime {regime_recommande} → "
            f"économie de {changement_regime_gain:.0f}€"
        )

    if per_economie > 500:
        quick_wins.append(
            f"🎯 Verser {per_versement_optimal:.0f}€ au PER → "
            f"économie de {per_economie:.0f}€"
        )

    if tmi >= 0.30:
        quick_wins.append(
            f"📊 Votre TMI est de {tmi*100:.0f}% → "
            f"Chaque euro déduit = {tmi:.2f}€ économisé"
        )

    if input_data.charges_reelles == 0 and regime_actuel == "Micro":
        quick_wins.append(
            "📝 Astuce : Déclarez vos frais réels pour potentiellement "
            "économiser encore plus"
        )

    if not quick_wins:
        quick_wins.append(
            "✅ Votre situation semble déjà optimisée ! "
            "Consultez notre analyse complète pour plus de détails."
        )

    # Generate catchy message
    if economies_totales > 1000:
        message = (
            f"💣 ALERTE : Vous pourriez économiser {economies_totales:.0f}€ "
            f"d'impôts cette année !"
        )
    elif economies_totales > 500:
        message = (
            f"💡 Bonne nouvelle : {economies_totales:.0f}€ d'économies "
            f"possibles sur vos impôts !"
        )
    else:
        message = (
            "✅ Votre situation est déjà bien optimisée ! "
            "Découvrez nos conseils personnalisés."
        )

    return QuickSimulationResult(
        impot_actuel_estime=impot_actuel,
        impot_optimise=max(0, impot_optimise),
        economies_potentielles=economies_totales,
        tmi=tmi,
        regime_actuel=regime_actuel,
        regime_recommande=regime_recommande,
        changement_regime_gain=changement_regime_gain,
        per_plafond=per_plafond,
        per_versement_optimal=per_versement_optimal,
        per_economie=per_economie,
        quick_wins=quick_wins,
        message_accroche=message,
    )
