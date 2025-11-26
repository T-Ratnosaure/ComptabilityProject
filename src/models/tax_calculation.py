"""Pydantic models for tax calculations."""

from datetime import datetime

from pydantic import BaseModel, Field


class TaxBracket(BaseModel):
    """Individual tax bracket calculation."""

    rate: float = Field(..., ge=0, le=1, description="Tax rate (e.g., 0.11 for 11%)")
    lower_bound: float = Field(..., ge=0)
    upper_bound: float | None
    taxable_amount: float = Field(..., ge=0)
    tax_amount: float = Field(..., ge=0)


class TaxCalculationBase(BaseModel):
    """Base tax calculation model."""

    profile_id: int
    tax_year: int = Field(..., ge=2000, le=2100)

    # Income components
    gross_income: float = Field(..., ge=0)
    net_taxable_income: float = Field(..., ge=0)

    # Family quotient
    nb_parts: float = Field(..., gt=0)
    quotient_familial: float = Field(..., ge=0)

    # Tax calculation
    brackets: list[TaxBracket]
    gross_tax: float = Field(..., ge=0)
    tax_reductions: dict[str, float] = Field(default_factory=dict)
    net_tax: float = Field(..., ge=0)

    # Reference fiscal
    revenu_fiscal_reference: float = Field(..., ge=0)

    # Social contributions
    social_contributions: float = Field(..., ge=0)

    # Total
    total_fiscal_burden: float = Field(..., ge=0)
    effective_rate: float = Field(..., ge=0, le=1)


class TaxCalculationCreate(TaxCalculationBase):
    """Model for creating a new tax calculation."""

    pass


class TaxCalculation(TaxCalculationBase):
    """Complete tax calculation model."""

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
