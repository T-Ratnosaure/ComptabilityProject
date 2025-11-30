"""Pytest configuration and fixtures."""

import os

# Set environment variables BEFORE importing app modules
# Prevents Git Bash from converting paths like /api/v1 to C:/Program Files/Git/api/v1
os.environ["MSYS_NO_PATHCONV"] = "1"
os.environ["API_V1_PREFIX"] = "/api/v1"

import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.base import Base
from src.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Use in-memory SQLite for testing
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session factory
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Provide session
    async with async_session() as session:
        yield session

    # Cleanup
    await engine.dispose()


@pytest.fixture
def client() -> TestClient:
    """Create FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_tax_document_data() -> dict:
    """Sample tax document data for testing."""
    return {
        "type": "avis_imposition",
        "year": 2024,
        "original_filename": "avis_2024.pdf",
        "file_path": "/test/path/avis_2024.pdf",
    }


@pytest.fixture
def sample_freelance_profile_data() -> dict:
    """Sample freelance profile data for testing."""
    return {
        "status": "micro_bnc",
        "family_situation": "single",
        "nb_parts": 1.0,
        "chiffre_affaires": 50000.0,
        "charges_deductibles": 0.0,
        "cotisations_sociales": 11100.0,
        "autres_revenus": 0.0,
        "existing_deductions": {},
    }
