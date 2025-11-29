"""SQLAlchemy model for tax calculations."""

from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class TaxCalculationModel(Base):
    """Tax calculation database model."""

    __tablename__ = "tax_calculations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("freelance_profiles.id"), nullable=False
    )
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Income components
    gross_income: Mapped[float] = mapped_column(Float, nullable=False)
    net_taxable_income: Mapped[float] = mapped_column(Float, nullable=False)

    # Family quotient
    nb_parts: Mapped[float] = mapped_column(Float, nullable=False)
    quotient_familial: Mapped[float] = mapped_column(Float, nullable=False)

    # Tax calculation (brackets stored as JSON for simplicity in Phase 1)
    brackets: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    gross_tax: Mapped[float] = mapped_column(Float, nullable=False)
    tax_reductions: Mapped[dict[str, float]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    net_tax: Mapped[float] = mapped_column(Float, nullable=False)

    # Reference fiscal
    revenu_fiscal_reference: Mapped[float] = mapped_column(Float, nullable=False)

    # Social contributions (cotisations sociales URSSAF)
    cotisations_sociales: Mapped[float] = mapped_column(Float, nullable=False)

    # Total
    total_fiscal_burden: Mapped[float] = mapped_column(Float, nullable=False)
    effective_rate: Mapped[float] = mapped_column(Float, nullable=False)

    def __repr__(self) -> str:
        """String representation of the model."""
        return (
            f"<TaxCalculation(id={self.id}, year={self.tax_year}, "
            f"net_tax={self.net_tax})>"
        )
