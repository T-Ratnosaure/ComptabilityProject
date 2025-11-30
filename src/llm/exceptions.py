"""LLM-specific exceptions for error handling."""


class LLMError(Exception):
    """Base exception for all LLM-related errors."""

    pass


class LLMAPIError(LLMError):
    """Exception for LLM API failures (500, connection errors, etc.)."""

    def __init__(self, message: str, status_code: int | None = None):
        """Initialize LLM API error.

        Args:
            message: Error message
            status_code: HTTP status code (if applicable)
        """
        self.status_code = status_code
        super().__init__(message)


class LLMRateLimitError(LLMError):
    """Exception for rate limit errors (429)."""

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        reset_time: int | None = None,
    ):
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
            reset_time: Unix timestamp when rate limit resets
        """
        self.retry_after = retry_after
        self.reset_time = reset_time
        super().__init__(message)


class LLMTimeoutError(LLMError):
    """Exception for timeout errors."""

    pass


class LLMValidationError(LLMError):
    """Exception for validation errors (invalid input/output)."""

    pass


class LLMConfigurationError(LLMError):
    """Exception for configuration errors (missing API key, etc.)."""

    pass


class LLMContextLengthError(LLMError):
    """Exception for context length exceeded errors."""

    def __init__(self, message: str, max_tokens: int, requested_tokens: int):
        """Initialize context length error.

        Args:
            message: Error message
            max_tokens: Maximum allowed tokens
            requested_tokens: Requested token count
        """
        self.max_tokens = max_tokens
        self.requested_tokens = requested_tokens
        super().__init__(message)
