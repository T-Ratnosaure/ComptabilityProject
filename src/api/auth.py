"""API authentication utilities."""

import hmac
import logging

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from src.config import settings

logger = logging.getLogger(__name__)

# API Key security scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
) -> str:
    """Verify API key for protected endpoints.

    Args:
        api_key: API key from X-API-Key header

    Returns:
        The validated API key

    Raises:
        HTTPException: If API key is missing or invalid
    """
    # In development mode with no key configured, allow bypass
    if settings.ENVIRONMENT == "development" and not settings.API_SECRET_KEY:
        logger.warning(
            "API authentication bypassed - no API_SECRET_KEY configured in development"
        )
        return "dev_bypass"

    # API key is required
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Include 'X-API-Key' header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Validate API key (constant-time comparison for security)
    if not settings.API_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server configuration error: API_SECRET_KEY not set",
        )

    if not hmac.compare_digest(api_key.encode(), settings.API_SECRET_KEY.encode()):
        logger.warning("Invalid API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key
