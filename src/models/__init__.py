"""Pydantic domain models."""

from src.models.comparison import ComparisonMicroReel
from src.models.extracted_fields import (
    AvisImpositionExtracted,
    BNCBICExtracted,
    Declaration2042Extracted,
    URSSAFExtracted,
)
from src.models.fiscal_profile import FiscalProfile
from src.models.freelance_profile import (
    FamilySituation,
    FreelanceProfile,
    FreelanceProfileCreate,
    FreelanceProfileUpdate,
    FreelanceStatus,
)
from src.models.llm_context import LLMContext, TaxCalculationSummary
from src.models.optimization import (
    ComplexityLevel,
    OptimizationProfile,
    OptimizationResult,
    Recommendation,
    RecommendationCategory,
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
    # Optimization (Phase 4)
    "Recommendation",
    "RiskLevel",
    "ComplexityLevel",
    "RecommendationCategory",
    "OptimizationProfile",
    "OptimizationResult",
    # Extracted Fields (Phase 2 - Validated)
    "AvisImpositionExtracted",
    "URSSAFExtracted",
    "BNCBICExtracted",
    "Declaration2042Extracted",
    # LLM Context (Phase 5)
    "FiscalProfile",
    "TaxCalculationSummary",
    "LLMContext",
    # Comparisons
    "ComparisonMicroReel",
]
