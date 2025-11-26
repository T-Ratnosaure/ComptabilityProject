"""Tax calculation API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.tax_engine.calculator import calculate_tax

router = APIRouter(prefix="/tax", tags=["tax"])


class PersonData(BaseModel):
    """Person/taxpayer data."""

    name: str = Field(default="ANON", description="Name (anonymized)")
    nb_parts: float = Field(ge=0.5, le=10.0, description="Nombre de parts fiscales")
    status: str = Field(
        description="Tax regime (micro_bnc, micro_bic_service, reel_bnc, reel_bic)"
    )


class IncomeData(BaseModel):
    """Income data."""

    professional_gross: float = Field(
        ge=0, description="Professional gross revenue (CA)"
    )
    salary: float = Field(default=0.0, ge=0, description="Salary income")
    rental_income: float = Field(default=0.0, ge=0, description="Rental income")
    capital_income: float = Field(default=0.0, ge=0, description="Capital income")
    deductible_expenses: float = Field(
        default=0.0, ge=0, description="Deductible expenses (for réel regime)"
    )


class DeductionsData(BaseModel):
    """Deductions data."""

    per_contributions: float = Field(default=0.0, ge=0, description="PER contributions")
    alimony: float = Field(default=0.0, ge=0, description="Pension alimentaire")
    other_deductions: float = Field(default=0.0, ge=0, description="Other deductions")


class SocialData(BaseModel):
    """Social contributions data."""

    urssaf_declared_ca: float = Field(ge=0, description="Declared CA to URSSAF")
    urssaf_paid: float = Field(ge=0, description="URSSAF contributions paid")


class TaxCalculationRequest(BaseModel):
    """Tax calculation request."""

    tax_year: int = Field(ge=2024, le=2025, description="Tax year")
    person: PersonData
    income: IncomeData
    deductions: DeductionsData = Field(default_factory=DeductionsData)
    social: SocialData
    pas_withheld: float = Field(
        default=0.0, ge=0, description="PAS (prélèvement à la source) already paid"
    )


@router.post("/calculate", response_model=dict[str, Any])
async def calculate_taxes(request: TaxCalculationRequest) -> dict[str, Any]:
    """Calculate French income tax and social contributions.

    This endpoint calculates:
    - Income tax (IR) with progressive brackets and quotient familial
    - Social contributions (URSSAF)
    - Comparison between micro and réel regimes
    - PAS (prélèvement à la source) reconciliation
    - Warnings and recommendations

    Args:
        request: Tax calculation input data

    Returns:
        Complete tax calculation with:
            - impot: IR results (revenu_imposable, impot_brut, impot_net, due_now)
            - socials: URSSAF results (expected, paid, delta)
            - comparisons: micro vs réel comparison
            - warnings: List of alerts and recommendations
            - metadata: Sources and disclaimer

    Example:
        ```json
        {
          "tax_year": 2024,
          "person": {
            "name": "ANON",
            "nb_parts": 1.0,
            "status": "micro_bnc"
          },
          "income": {
            "professional_gross": 28000.0,
            "salary": 0.0,
            "rental_income": 0.0,
            "capital_income": 0.0,
            "deductible_expenses": 0.0
          },
          "deductions": {
            "per_contributions": 2000.0,
            "alimony": 0.0,
            "other_deductions": 0.0
          },
          "social": {
            "urssaf_declared_ca": 28000.0,
            "urssaf_paid": 6000.0
          },
          "pas_withheld": 0.0
        }
        ```

    Raises:
        HTTPException: If calculation fails
    """
    try:
        # Convert request to dict for calculator
        payload = request.model_dump()

        # Calculate
        result = await calculate_tax(payload)

        return result

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Tax year not supported: {e}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Tax calculation failed: {e}",
        ) from e


@router.get("/rules/{year}", response_model=dict[str, Any])
async def get_tax_rules(year: int) -> dict[str, Any]:
    """Get tax rules for a specific year.

    Args:
        year: Tax year (2024 or 2025)

    Returns:
        Tax rules including brackets, abattements, rates, sources

    Raises:
        HTTPException: If year not supported
    """
    try:
        from src.tax_engine.rules import get_tax_rules

        rules = get_tax_rules(year)

        return {
            "year": rules.year,
            "income_tax_brackets": rules.income_tax_brackets,
            "abattements": rules.abattements,
            "urssaf_rates": rules.urssaf_rates,
            "plafonds_micro": rules.plafonds_micro,
            "per_plafonds": rules.per_plafonds,
            "quotient_familial": rules.quotient_familial,
            "source": rules.source_url,
            "source_date": rules.source_date,
        }

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Tax rules not found for year {year}",
        ) from e
