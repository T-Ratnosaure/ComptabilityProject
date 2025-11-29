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
