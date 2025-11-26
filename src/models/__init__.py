"""Pydantic domain models."""

from src.models.freelance_profile import (
    FamilySituation,
    FreelanceProfile,
    FreelanceProfileCreate,
    FreelanceProfileUpdate,
    FreelanceStatus,
)
from src.models.recommendation import (
    Recommendation,
    RecommendationCreate,
    RecommendationType,
    RiskLevel,
)
from src.models.tax_calculation import (
    TaxBracket,
    TaxCalculation,
    TaxCalculationCreate,
)
from src.models.tax_document import (
    DocumentStatus,
    DocumentType,
    TaxDocument,
    TaxDocumentCreate,
    TaxDocumentUpdate,
)

__all__ = [
    # Tax Document
    "DocumentType",
    "DocumentStatus",
    "TaxDocument",
    "TaxDocumentCreate",
    "TaxDocumentUpdate",
    # Freelance Profile
    "FreelanceStatus",
    "FamilySituation",
    "FreelanceProfile",
    "FreelanceProfileCreate",
    "FreelanceProfileUpdate",
    # Tax Calculation
    "TaxBracket",
    "TaxCalculation",
    "TaxCalculationCreate",
    # Recommendation
    "RecommendationType",
    "RiskLevel",
    "Recommendation",
    "RecommendationCreate",
]
