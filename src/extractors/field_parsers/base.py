"""Base class for document field parsers."""

import re
from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseFieldParser(ABC):
    """Abstract base class for parsing fields from document text."""

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
