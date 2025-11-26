"""Pydantic models for tax documents."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Types of French tax documents."""

    AVIS_IMPOSITION = "avis_imposition"
    DECLARATION_2042 = "declaration_2042"
    URSSAF = "urssaf"
    BNC = "bnc"
    BIC = "bic"
    PER = "per"
    ASSURANCE_VIE = "assurance_vie"
    LMNP = "lmnp"
    OTHER = "other"


class DocumentStatus(str, Enum):
    """Processing status of a document."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class TaxDocumentBase(BaseModel):
    """Base tax document model with common fields."""

    type: DocumentType
    year: int = Field(..., ge=2000, le=2100, description="Tax year")
    original_filename: str


class TaxDocumentCreate(TaxDocumentBase):
    """Model for creating a new tax document."""

    status: DocumentStatus = DocumentStatus.UPLOADED
    file_path: str
    extracted_fields: dict[str, Any] = Field(default_factory=dict)
    raw_text: str | None = None


class TaxDocumentUpdate(BaseModel):
    """Model for updating a tax document."""

    status: DocumentStatus | None = None
    extracted_fields: dict[str, Any] | None = None
    raw_text: str | None = None
    processed_at: datetime | None = None
    error_message: str | None = None


class TaxDocument(TaxDocumentBase):
    """Complete tax document model."""

    id: int
    status: DocumentStatus = DocumentStatus.UPLOADED
    file_path: str
    extracted_fields: dict[str, Any] = Field(default_factory=dict)
    raw_text: str | None = None
    created_at: datetime
    processed_at: datetime | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}
