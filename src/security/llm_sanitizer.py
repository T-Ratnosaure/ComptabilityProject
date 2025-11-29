"""Sanitization utilities for LLM prompts to prevent data leaks."""

import re
from typing import Any


class LLMSanitizer:
    """Sanitize text before sending to LLM APIs."""

    # Maximum context length for LLM (characters)
    MAX_CONTEXT_CHARS = 50000

    # Patterns to redact
    PATTERNS = {
        # File paths (Unix and Windows)
        "file_path": re.compile(r"(?:[A-Za-z]:[/\\]|/)[^\s<>\"'|?*\n]+", re.IGNORECASE),
        # Email addresses
        "email": re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", re.IGNORECASE
        ),
        # French SSN (Numéro de Sécurité Sociale - 15 digits)
        "french_ssn": re.compile(
            r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b"
        ),
        # French fiscal number (Numéro fiscal - 13 digits)
        "french_fiscal": re.compile(r"\b\d{13}\b"),
        # IBAN (International Bank Account Number)
        "iban": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b"),
        # Credit card numbers (basic pattern)
        "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
        # IP addresses
        "ip_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
        # API keys/tokens (common patterns)
        "api_key": re.compile(
            r"(?:api[_-]?key|token|secret|password)['\"]?\s*[:=]\s*['\"]?[\w\-]{20,}",
            re.IGNORECASE,
        ),
    }

    @staticmethod
    def sanitize_for_llm(
        text: str,
        max_length: int | None = None,
        redact_patterns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Sanitize text before sending to LLM API.

        Args:
            text: Raw text to sanitize
            max_length: Maximum length (default: MAX_CONTEXT_CHARS)
            redact_patterns: List of pattern names to redact (default: all)

        Returns:
            Dict with:
                - sanitized_text: Cleaned text
                - redacted_count: Number of items redacted
                - truncated: Whether text was truncated
                - original_length: Original text length
                - redactions: Dict of redaction counts by type
        """
        if max_length is None:
            max_length = LLMSanitizer.MAX_CONTEXT_CHARS

        original_length = len(text)
        sanitized = text
        redactions = {}

        # Determine which patterns to apply
        if redact_patterns is None:
            patterns_to_use = LLMSanitizer.PATTERNS.items()
        else:
            patterns_to_use = [
                (name, pattern)
                for name, pattern in LLMSanitizer.PATTERNS.items()
                if name in redact_patterns
            ]

        # Apply redaction patterns
        for name, pattern in patterns_to_use:
            matches = pattern.findall(sanitized)
            if matches:
                redactions[name] = len(matches)
                # Redact with placeholder
                sanitized = pattern.sub(f"[REDACTED_{name.upper()}]", sanitized)

        # Truncate if too long
        truncated = False
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "\n\n[... CONTENT TRUNCATED ...]"
            truncated = True

        return {
            "sanitized_text": sanitized,
            "redacted_count": sum(redactions.values()),
            "truncated": truncated,
            "original_length": original_length,
            "final_length": len(sanitized),
            "redactions": redactions,
        }

    @staticmethod
    def redact_partial_fiscal_number(text: str) -> str:
        """Partially redact French fiscal numbers (keep first 4, last 2 digits).

        Args:
            text: Text containing fiscal numbers

        Returns:
            Text with partially redacted fiscal numbers

        Example:
            "1234567890123" → "1234*******23"
        """

        def partial_redact(match: re.Match) -> str:
            number = match.group(0)
            if len(number) == 13:
                return f"{number[:4]}*******{number[-2:]}"
            return "[REDACTED_FISCAL]"

        return re.sub(r"\b\d{13}\b", partial_redact, text)

    @staticmethod
    def remove_prompt_injection(text: str) -> str:
        """Remove potential prompt injection attempts.

        Args:
            text: Text to clean

        Returns:
            Text with prompt injection patterns removed
        """
        # Common injection patterns
        injection_patterns = [
            # Ignore previous instructions
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"disregard\s+(all\s+)?previous\s+instructions",
            # System prompts
            r"<\s*system\s*>.*?<\s*/\s*system\s*>",
            r"\[\s*system\s*\].*?\[\s*/\s*system\s*\]",
            # Role manipulation
            r"you\s+are\s+now\s+a\s+",
            r"act\s+as\s+a\s+",
            r"pretend\s+to\s+be\s+",
            # Command-like structures
            r"```\s*system\s*.*?```",
        ]

        cleaned = text
        for pattern in injection_patterns:
            cleaned = re.sub(
                pattern, "[REMOVED]", cleaned, flags=re.IGNORECASE | re.DOTALL
            )

        return cleaned

    @staticmethod
    def create_safe_summary(
        extracted_text: str, max_summary_length: int = 5000
    ) -> dict[str, Any]:
        """Create a safe summary for LLM context.

        Args:
            extracted_text: Full extracted text
            max_summary_length: Maximum summary length

        Returns:
            Dict with safe summary and metadata
        """
        # First, sanitize the text
        sanitized_result = LLMSanitizer.sanitize_for_llm(
            extracted_text, max_length=max_summary_length
        )

        # Remove potential injection attempts
        safe_text = LLMSanitizer.remove_prompt_injection(
            sanitized_result["sanitized_text"]
        )

        # Extract key information only (first and last parts)
        lines = safe_text.split("\n")
        if len(lines) > 100:
            # Take first 50 and last 50 lines
            summary_lines = (
                lines[:50] + ["\n[... MIDDLE SECTION OMITTED ...]\n"] + lines[-50:]
            )
            summary = "\n".join(summary_lines)
        else:
            summary = safe_text

        return {
            "safe_summary": summary,
            "original_length": len(extracted_text),
            "summary_length": len(summary),
            "redactions": sanitized_result["redactions"],
            "truncated": sanitized_result["truncated"],
        }


# Convenience function
def sanitize_for_llm(
    text: str, max_length: int | None = None, redact_patterns: list[str] | None = None
) -> dict[str, Any]:
    """Convenience wrapper for LLMSanitizer.sanitize_for_llm.

    Args:
        text: Raw text to sanitize
        max_length: Maximum length (default: 50000 chars)
        redact_patterns: List of pattern names to redact (default: all)

    Returns:
        Dict with sanitized text and metadata
    """
    return LLMSanitizer.sanitize_for_llm(text, max_length, redact_patterns)
