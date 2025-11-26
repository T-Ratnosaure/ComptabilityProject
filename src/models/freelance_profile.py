"""Pydantic models for freelance profiles."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FreelanceStatus(str, Enum):
    """French freelance tax status."""

    MICRO_BNC = "micro_bnc"
    MICRO_BIC = "micro_bic"
    REEL_BNC = "reel_bnc"
    REEL_BIC = "reel_bic"
    EURL = "eurl"
    SASU = "sasu"


class FamilySituation(str, Enum):
    """Family situation for quotient familial."""

    SINGLE = "single"
    MARRIED = "married"
    PACS = "pacs"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class FreelanceProfileBase(BaseModel):
    """Base freelance profile model."""

    status: FreelanceStatus
    family_situation: FamilySituation
    nb_parts: float = Field(..., gt=0, description="Nombre de parts fiscales")
    annual_revenue: float = Field(..., ge=0, description="Chiffre d'affaires annuel")
    annual_expenses: float = Field(
        default=0.0, ge=0, description="Charges déductibles (réel)"
    )
    social_contributions: float = Field(
        default=0.0, ge=0, description="Cotisations sociales"
    )
    other_income: float = Field(
        default=0.0, ge=0, description="Autres revenus (salaires, etc.)"
    )
    existing_deductions: dict[str, float] = Field(default_factory=dict)


class FreelanceProfileCreate(FreelanceProfileBase):
    """Model for creating a new freelance profile."""

    pass


class FreelanceProfileUpdate(BaseModel):
    """Model for updating a freelance profile."""

    status: FreelanceStatus | None = None
    family_situation: FamilySituation | None = None
    nb_parts: float | None = None
    annual_revenue: float | None = None
    annual_expenses: float | None = None
    social_contributions: float | None = None
    other_income: float | None = None
    existing_deductions: dict[str, float] | None = None


class FreelanceProfile(FreelanceProfileBase):
    """Complete freelance profile model."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
