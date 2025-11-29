"""SQLAlchemy model for freelance profiles."""

from sqlalchemy import JSON, Enum, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class FreelanceProfileModel(Base):
    """Freelance profile database model."""

    __tablename__ = "freelance_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(
        Enum(
            "micro_bnc",
            "micro_bic",
            "reel_bnc",
            "reel_bic",
            "eurl",
            "sasu",
            name="freelance_status_enum",
        ),
        nullable=False,
    )
    family_situation: Mapped[str] = mapped_column(
        Enum(
            "single",
            "married",
            "pacs",
            "divorced",
            "widowed",
            name="family_situation_enum",
        ),
        nullable=False,
    )
    nb_parts: Mapped[float] = mapped_column(Float, nullable=False)
    chiffre_affaires: Mapped[float] = mapped_column(Float, nullable=False)
    charges_deductibles: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    cotisations_sociales: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    autres_revenus: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    existing_deductions: Mapped[dict[str, float]] = mapped_column(
        JSON, nullable=False, default=dict
    )

    def __repr__(self) -> str:
        """String representation of the model."""
        return (
            f"<FreelanceProfile(id={self.id}, status={self.status}, "
            f"revenue={self.chiffre_affaires})>"
        )
