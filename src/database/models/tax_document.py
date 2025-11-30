"""SQLAlchemy model for tax documents."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy import JSON, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.models.extracted_fields import (
    AvisImpositionExtracted,
    BNCBICExtracted,
    Declaration2042Extracted,
    URSSAFExtracted,
)


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

    def get_validated_fields(self) -> BaseModel:
        """
        Get extracted_fields as validated Pydantic model.

        This method re-validates the extracted_fields stored in the database
        using the appropriate Pydantic model based on the document type.

        Returns:
            Validated Pydantic model (type depends on document type)

        Raises:
            ValueError: If document type is unknown or validation fails

        Example:
            >>> document = await repository.get(doc_id)
            >>> validated = document.get_validated_fields()
            >>> # validated is AvisImpositionExtracted, URSSAFExtracted, etc.
        """
        # Map document types to Pydantic models
        type_to_model = {
            "avis_imposition": AvisImpositionExtracted,
            "urssaf": URSSAFExtracted,
            "bnc": BNCBICExtracted,
            "bic": BNCBICExtracted,
            "declaration_2042": Declaration2042Extracted,
        }

        if self.type not in type_to_model:
            raise ValueError(
                f"Unknown or unsupported document type for validation: {self.type}"
            )

        model_class = type_to_model[self.type]

        try:
            return model_class(**self.extracted_fields)
        except ValidationError as e:
            raise ValueError(
                f"Validation failed for {self.type} document (id={self.id}): {e}"
            ) from e
