"""Confidence scoring models for document extraction.

These models provide transparency about extraction reliability,
helping users understand which data points are trustworthy.
"""

from enum import Enum

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    """Confidence levels for extracted data."""

    HIGH = "high"  # Multiple patterns matched, clear value
    MEDIUM = "medium"  # Single pattern matched, reasonable certainty
    LOW = "low"  # Weak match or inferred value
    UNCERTAIN = "uncertain"  # Fallback or best-guess


class FieldConfidence(BaseModel):
    """Confidence information for a single extracted field."""

    field_name: str = Field(description="Name of the extracted field")
    value: float | str | int | None = Field(description="Extracted value")
    confidence: ConfidenceLevel = Field(description="Confidence level")
    confidence_score: float = Field(
        ge=0.0, le=1.0, description="Numeric confidence score (0-1)"
    )
    extraction_method: str = Field(
        description="How the value was extracted (regex, ocr, inference)"
    )
    patterns_matched: int = Field(
        default=1, ge=0, description="Number of patterns that matched"
    )
    notes: str | None = Field(default=None, description="Additional notes or warnings")


class ExtractionConfidenceReport(BaseModel):
    """Overall confidence report for a document extraction."""

    document_type: str = Field(description="Type of document extracted")
    overall_confidence: ConfidenceLevel = Field(
        description="Overall extraction confidence"
    )
    overall_score: float = Field(
        ge=0.0, le=1.0, description="Weighted average confidence score"
    )
    fields: list[FieldConfidence] = Field(
        default_factory=list, description="Per-field confidence details"
    )
    critical_fields_extracted: int = Field(
        default=0, description="Number of critical fields successfully extracted"
    )
    critical_fields_total: int = Field(
        default=0, description="Total number of critical fields expected"
    )
    warnings: list[str] = Field(default_factory=list, description="Extraction warnings")
    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improving confidence"
    )

    def add_field(
        self,
        field_name: str,
        value: float | str | int | None,
        confidence: ConfidenceLevel,
        score: float,
        method: str = "regex",
        patterns_matched: int = 1,
        notes: str | None = None,
    ) -> None:
        """Add a field confidence entry."""
        self.fields.append(
            FieldConfidence(
                field_name=field_name,
                value=value,
                confidence=confidence,
                confidence_score=score,
                extraction_method=method,
                patterns_matched=patterns_matched,
                notes=notes,
            )
        )

    def calculate_overall_confidence(self) -> None:
        """Calculate overall confidence from field confidences."""
        if not self.fields:
            self.overall_confidence = ConfidenceLevel.UNCERTAIN
            self.overall_score = 0.0
            return

        # Calculate weighted average (critical fields weighted more)
        total_score = sum(f.confidence_score for f in self.fields)
        avg_score = total_score / len(self.fields)

        self.overall_score = round(avg_score, 2)

        # Map score to level
        if avg_score >= 0.85:
            self.overall_confidence = ConfidenceLevel.HIGH
        elif avg_score >= 0.65:
            self.overall_confidence = ConfidenceLevel.MEDIUM
        elif avg_score >= 0.40:
            self.overall_confidence = ConfidenceLevel.LOW
        else:
            self.overall_confidence = ConfidenceLevel.UNCERTAIN

        # Add recommendations based on confidence
        if self.overall_score < 0.7:
            self.recommendations.append(
                "Vérifiez manuellement les valeurs extraites avant utilisation"
            )
        if self.critical_fields_extracted < self.critical_fields_total:
            missing = self.critical_fields_total - self.critical_fields_extracted
            msg = f"{missing} champ(s) critique(s) non extrait(s) - saisie manuelle"
            self.recommendations.append(msg)


def score_to_level(score: float) -> ConfidenceLevel:
    """Convert numeric score to confidence level."""
    if score >= 0.85:
        return ConfidenceLevel.HIGH
    elif score >= 0.65:
        return ConfidenceLevel.MEDIUM
    elif score >= 0.40:
        return ConfidenceLevel.LOW
    return ConfidenceLevel.UNCERTAIN
