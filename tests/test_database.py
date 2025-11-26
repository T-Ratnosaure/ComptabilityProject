"""Tests for database models and operations."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.documents import TaxDocumentRepository
from src.models.tax_document import TaxDocumentCreate


@pytest.mark.asyncio
async def test_create_tax_document(
    db_session: AsyncSession, sample_tax_document_data: dict
) -> None:
    """Test creating a tax document."""
    # Create repository
    repo = TaxDocumentRepository(db_session)

    # Create document
    document_create = TaxDocumentCreate(**sample_tax_document_data)
    document = await repo.create(document_create)

    # Verify
    assert document.id is not None
    assert document.type == sample_tax_document_data["type"]
    assert document.year == sample_tax_document_data["year"]
    assert document.status == "uploaded"


@pytest.mark.asyncio
async def test_get_tax_document(
    db_session: AsyncSession, sample_tax_document_data: dict
) -> None:
    """Test retrieving a tax document by ID."""
    repo = TaxDocumentRepository(db_session)

    # Create document
    document_create = TaxDocumentCreate(**sample_tax_document_data)
    created = await repo.create(document_create)

    # Retrieve document
    retrieved = await repo.get(created.id)

    # Verify
    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.type == created.type


@pytest.mark.asyncio
async def test_get_documents_by_year(
    db_session: AsyncSession, sample_tax_document_data: dict
) -> None:
    """Test retrieving documents by year."""
    repo = TaxDocumentRepository(db_session)

    # Create multiple documents
    doc1 = TaxDocumentCreate(**sample_tax_document_data)
    doc2_data = sample_tax_document_data.copy()
    doc2_data["year"] = 2023
    doc2 = TaxDocumentCreate(**doc2_data)

    await repo.create(doc1)
    await repo.create(doc2)

    # Get documents for 2024
    docs_2024 = await repo.get_by_year(2024)
    assert len(docs_2024) == 1
    assert docs_2024[0].year == 2024

    # Get documents for 2023
    docs_2023 = await repo.get_by_year(2023)
    assert len(docs_2023) == 1
    assert docs_2023[0].year == 2023


@pytest.mark.asyncio
async def test_delete_tax_document(
    db_session: AsyncSession, sample_tax_document_data: dict
) -> None:
    """Test deleting a tax document."""
    repo = TaxDocumentRepository(db_session)

    # Create document
    document_create = TaxDocumentCreate(**sample_tax_document_data)
    created = await repo.create(document_create)
    doc_id = created.id

    # Delete document
    result = await repo.delete(doc_id)
    assert result is True

    # Verify deletion
    deleted = await repo.get(doc_id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_multi_with_pagination(
    db_session: AsyncSession, sample_tax_document_data: dict
) -> None:
    """Test retrieving multiple documents with pagination."""
    repo = TaxDocumentRepository(db_session)

    # Create 5 documents
    for i in range(5):
        doc_data = sample_tax_document_data.copy()
        doc_data["original_filename"] = f"doc_{i}.pdf"
        doc = TaxDocumentCreate(**doc_data)
        await repo.create(doc)

    # Get first 3
    docs_page1 = await repo.get_multi(skip=0, limit=3)
    assert len(docs_page1) == 3

    # Get next 2
    docs_page2 = await repo.get_multi(skip=3, limit=3)
    assert len(docs_page2) == 2
