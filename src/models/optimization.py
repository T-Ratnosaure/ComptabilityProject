"""Pydantic models for tax optimization recommendations."""

from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Risk level for a recommendation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ComplexityLevel(str, Enum):
    """Implementation complexity for a recommendation."""

    EASY = "easy"
    MODERATE = "moderate"
    COMPLEX = "complex"


class RecommendationCategory(str, Enum):
    """Category of tax optimization."""

    REGIME = "regime"
    INVESTMENT = "investment"
    DEDUCTION = "deduction"
    STRUCTURE = "structure"
    FAMILY = "family"


class Recommendation(BaseModel):
    """Tax optimization recommendation."""

    id: str = Field(..., description="Unique identifier for the recommendation")
    title: str = Field(..., description="Short title of the recommendation")
    description: str = Field(
        ..., description="Detailed explanation of the optimization"
    )
    impact_estimated: float = Field(
        ..., description="Estimated tax savings in euros", ge=0
    )
    risk: RiskLevel = Field(..., description="Risk level of the recommendation")
    complexity: ComplexityLevel = Field(..., description="Implementation complexity")
    confidence: float = Field(..., description="Confidence score (0-1)", ge=0.0, le=1.0)
    category: RecommendationCategory = Field(
        ..., description="Category of optimization"
    )
    sources: list[str] = Field(
        default_factory=list, description="Official sources and references"
    )
    action_steps: list[str] = Field(
        default_factory=list, description="Steps to implement the recommendation"
    )
    required_investment: float = Field(
        default=0.0, description="Required upfront investment in euros", ge=0
    )
    eligibility_criteria: list[str] = Field(
        default_factory=list, description="Conditions to be eligible"
    )
    warnings: list[str] = Field(
        default_factory=list, description="Important warnings and disclaimers"
    )
    deadline: str | None = Field(
        default=None, description="Important deadline if applicable"
    )
    roi_years: float | None = Field(
        default=None, description="Return on investment in years", ge=0
    )


class OptimizationProfile(str, Enum):
    """User risk profile for optimization."""

    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class OptimizationResult(BaseModel):
    """Complete optimization analysis result."""

    recommendations: list[Recommendation] = Field(
        default_factory=list, description="List of detected optimizations"
    )
    summary: str = Field(..., description="Executive summary of findings")
    risk_profile: OptimizationProfile = Field(
        ..., description="Detected or user-specified risk profile"
    )
    potential_savings_total: float = Field(
        ..., description="Total potential savings in euros", ge=0
    )
    high_priority_count: int = Field(
        default=0, description="Number of high-priority recommendations", ge=0
    )
    metadata: dict = Field(
        default_factory=dict, description="Additional metadata and context"
    )
