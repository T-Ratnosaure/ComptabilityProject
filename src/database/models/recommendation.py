"""SQLAlchemy model for tax optimization recommendations."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class RecommendationModel(Base):
    """Tax optimization recommendation database model."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    calculation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tax_calculations.id"), nullable=False
    )
    type: Mapped[str] = mapped_column(
        Enum(
            "regime_change",
            "per_contribution",
            "lmnp_investment",
            "fcpi_fip",
            "girardin",
            "company_structure",
            "deduction_optimization",
            "other",
            name="recommendation_type_enum",
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Financial impact
    estimated_tax_savings: Mapped[float] = mapped_column(Float, nullable=False)
    required_investment: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    roi_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Risk and confidence
    risk_level: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", name="risk_level_enum"), nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Implementation details (stored as JSON)
    action_steps: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    deadlines: Mapped[dict[str, datetime] | None] = mapped_column(JSON, nullable=True)
    required_documents: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )

    # Additional context
    eligibility_criteria: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    warnings: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)

    def __repr__(self) -> str:
        """String representation of the model."""
        return (
            f"<Recommendation(id={self.id}, type={self.type}, "
            f"savings={self.estimated_tax_savings})>"
        )
