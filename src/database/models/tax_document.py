"""SQLAlchemy model for tax documents."""

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class TaxDocumentModel(Base):
    """Tax document database model."""

    __tablename__ = "tax_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(
        Enum(
            "avis_imposition",
            "declaration_2042",
            "urssaf",
            "bnc",
            "bic",
            "per",
            "assurance_vie",
            "lmnp",
            "other",
            name="document_type_enum",
        ),
        nullable=False,
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "uploaded",
            "processing",
            "processed",
            "failed",
            name="document_status_enum",
        ),
        nullable=False,
        default="uploaded",
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_fields: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<TaxDocument(id={self.id}, type={self.type}, year={self.year})>"
