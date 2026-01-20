"""Base class for document field parsers."""

import re
from abc import ABC, abstractmethod

from pydantic import BaseModel

from src.models.extraction_confidence import (
    ConfidenceLevel,
    ExtractionConfidenceReport,
    score_to_level,
)


class ExtractionResult:
    """Result of an extraction with confidence metadata."""

    def __init__(
        self,
        value: float | str | int | None,
        confidence_score: float,
        patterns_matched: int = 1,
        method: str = "regex",
    ):
        self.value = value
        self.confidence_score = confidence_score
        self.confidence_level = score_to_level(confidence_score)
        self.patterns_matched = patterns_matched
        self.method = method


class BaseFieldParser(ABC):
    """Abstract base class for parsing fields from document text."""

    def __init__(self) -> None:
        """Initialize parser with confidence report."""
        self.confidence_report: ExtractionConfidenceReport | None = None

    @abstractmethod
    async def parse(self, text: str) -> BaseModel:
        """Parse fields from document text.

        Args:
            text: Raw text extracted from document

        Returns:
            Validated Pydantic model with parsed fields

        Raises:
            ValueError: If required fields cannot be extracted
        """
        pass

    def extract_float(self, text: str, pattern: str) -> float | None:
        """Extract a float value using regex.

        Args:
            text: Text to search
            pattern: Regex pattern with one capture group

        Returns:
            Extracted float value or None if not found
        """
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value_str = match.group(1).strip()
            # Remove spaces and replace comma with period
            value_str = value_str.replace(" ", "").replace(",", ".")
            try:
                return float(value_str)
            except ValueError:
                return None
        return None

    def extract_int(self, text: str, pattern: str) -> int | None:
        """Extract an integer value using regex.

        Args:
            text: Text to search
            pattern: Regex pattern with one capture group

        Returns:
            Extracted integer value or None if not found
        """
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            value_str = match.group(1).strip()
            # Remove spaces
            value_str = value_str.replace(" ", "")
            try:
                return int(value_str)
            except ValueError:
                return None
        return None

    def extract_string(self, text: str, pattern: str) -> str | None:
        """Extract a string value using regex.

        Args:
            text: Text to search
            pattern: Regex pattern with one capture group

        Returns:
            Extracted string value or None if not found
        """
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def extract_float_with_confidence(
        self, text: str, patterns: list[str], field_name: str
    ) -> ExtractionResult:
        """Extract a float using multiple patterns, tracking confidence.

        Args:
            text: Text to search
            patterns: List of regex patterns to try (in priority order)
            field_name: Name of the field being extracted

        Returns:
            ExtractionResult with value and confidence metadata
        """
        matches_found = 0
        extracted_value: float | None = None
        last_match_score = 0.0

        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                matches_found += 1
                value_str = match.group(1).strip()
                value_str = value_str.replace(" ", "").replace(",", ".")
                try:
                    value = float(value_str)
                    if extracted_value is None:
                        extracted_value = value
                        # First pattern gets highest score, decreasing for later
                        last_match_score = 0.95 - (i * 0.1)
                    elif abs(value - extracted_value) < 0.01:
                        # Multiple patterns agree - boost confidence
                        last_match_score = min(1.0, last_match_score + 0.1)
                except ValueError:
                    continue

        if extracted_value is not None:
            # Boost confidence if multiple patterns matched
            if matches_found > 1:
                boost = (matches_found - 1) * 0.05
                last_match_score = min(1.0, last_match_score + boost)
            return ExtractionResult(
                value=extracted_value,
                confidence_score=last_match_score,
                patterns_matched=matches_found,
            )

        return ExtractionResult(value=None, confidence_score=0.0, patterns_matched=0)

    def extract_int_with_confidence(
        self, text: str, patterns: list[str], field_name: str
    ) -> ExtractionResult:
        """Extract an integer using multiple patterns, tracking confidence.

        Args:
            text: Text to search
            patterns: List of regex patterns to try
            field_name: Name of the field being extracted

        Returns:
            ExtractionResult with value and confidence metadata
        """
        matches_found = 0
        extracted_value: int | None = None
        last_match_score = 0.0

        for i, pattern in enumerate(patterns):
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                matches_found += 1
                value_str = match.group(1).strip().replace(" ", "")
                try:
                    value = int(value_str)
                    if extracted_value is None:
                        extracted_value = value
                        last_match_score = 0.95 - (i * 0.1)
                    elif value == extracted_value:
                        last_match_score = min(1.0, last_match_score + 0.1)
                except ValueError:
                    continue

        if extracted_value is not None:
            return ExtractionResult(
                value=extracted_value,
                confidence_score=last_match_score,
                patterns_matched=matches_found,
            )

        return ExtractionResult(value=None, confidence_score=0.0, patterns_matched=0)

    def create_confidence_report(
        self, document_type: str
    ) -> ExtractionConfidenceReport:
        """Create a new confidence report for an extraction.

        Args:
            document_type: Type of document being extracted

        Returns:
            New ExtractionConfidenceReport instance
        """
        self.confidence_report = ExtractionConfidenceReport(
            document_type=document_type,
            overall_confidence=ConfidenceLevel.UNCERTAIN,
            overall_score=0.0,
        )
        return self.confidence_report
