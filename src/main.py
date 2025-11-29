"""FastAPI application for French Tax Optimization System - SECURE VERSION."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import documents, optimization, tax
from src.config import settings

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan event handler for application startup and shutdown.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"API prefix: {settings.API_V1_PREFIX}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)


# Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all uncaught exceptions.

    Returns sanitized error response, logs full traceback internally.

    Args:
        request: FastAPI request
        exc: Exception raised

    Returns:
        JSON response with sanitized error
    """
    # Log full exception for debugging (not exposed to client)
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}",
        exc_info=exc,
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_host": request.client.host if request.client else None,
        },
    )

    # Return sanitized error (no stack trace)
    if settings.DEBUG:
        # In debug mode, include exception type
        detail = f"Internal server error: {exc.__class__.__name__}"
    else:
        # In production, generic message only
        detail = "An internal error occurred. Please try again later."

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "detail": detail,
            "request_id": id(request),  # For support/debugging
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors.

    Args:
        request: FastAPI request
        exc: Validation error

    Returns:
        JSON response with validation errors
    """
    logger.warning(
        f"Validation error on {request.method} {request.url.path}: {exc.errors()}"
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDATION_ERROR",
            "detail": "Invalid request data",
            "errors": exc.errors(),  # Include validation details
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle ValueError (business logic errors).

    Args:
        request: FastAPI request
        exc: ValueError

    Returns:
        JSON response with error detail
    """
    logger.warning(f"ValueError on {request.method} {request.url.path}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "INVALID_INPUT",
            "detail": str(exc),  # Safe to expose ValueError messages
        },
    )


@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(
    request: Request, exc: FileNotFoundError
) -> JSONResponse:
    """Handle FileNotFoundError.

    Args:
        request: FastAPI request
        exc: FileNotFoundError

    Returns:
        JSON response with 404 error
    """
    logger.warning(f"FileNotFoundError on {request.method} {request.url.path}: {exc}")

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "NOT_FOUND",
            "detail": "The requested resource was not found",
        },
    )


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(documents.router)
app.include_router(tax.router)
app.include_router(optimization.router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get(f"{settings.API_V1_PREFIX}/status", tags=["Health"])
async def api_status() -> dict[str, str]:
    """API status endpoint.

    Returns:
        dict: API status and configuration
    """
    return {
        "status": "operational",
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_V1_PREFIX,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint with API information.

    Returns:
        dict: API information
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# For development: run with `uvicorn src.main:app --reload`
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
