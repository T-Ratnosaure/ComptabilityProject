"""Pydantic models for tax optimization recommendations."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RecommendationType(str, Enum):
    """Types of tax optimization recommendations."""

    REGIME_CHANGE = "regime_change"
    PER_CONTRIBUTION = "per_contribution"
    LMNP_INVESTMENT = "lmnp_investment"
    FCPI_FIP = "fcpi_fip"
    GIRARDIN = "girardin"
    COMPANY_STRUCTURE = "company_structure"
    DEDUCTION_OPTIMIZATION = "deduction_optimization"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk level of recommendation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecommendationBase(BaseModel):
    """Base recommendation model."""

    calculation_id: int
    type: RecommendationType
    title: str = Field(..., max_length=255)
    description: str

    # Financial impact
    estimated_tax_savings: float = Field(..., ge=0)
    required_investment: float = Field(default=0.0, ge=0)
    roi_percentage: float | None = Field(default=None, ge=0)

    # Risk and confidence
    risk_level: RiskLevel
    confidence_score: float = Field(..., ge=0.0, le=1.0)

    # Implementation details
    action_steps: list[str] = Field(default_factory=list)
    deadlines: dict[str, datetime] | None = None
    required_documents: list[str] = Field(default_factory=list)

    # Additional context
    eligibility_criteria: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class RecommendationCreate(RecommendationBase):
    """Model for creating a new recommendation."""

    pass


class Recommendation(RecommendationBase):
    """Complete recommendation model."""

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
