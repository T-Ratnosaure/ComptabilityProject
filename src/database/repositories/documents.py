"""Repository for tax documents."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.tax_document import TaxDocumentModel
from src.database.repositories.base import BaseRepository
from src.models.tax_document import TaxDocumentCreate, TaxDocumentUpdate


class TaxDocumentRepository(
    BaseRepository[TaxDocumentModel, TaxDocumentCreate, TaxDocumentUpdate]
):
    """Repository for tax document operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with TaxDocumentModel."""
        super().__init__(TaxDocumentModel, db)

    async def get_by_year(self, year: int) -> list[TaxDocumentModel]:
        """
        Get all documents for a specific year.

        Args:
            year: Tax year

        Returns:
            List of documents for the year
        """
        result = await self.db.execute(
            select(self.model).where(self.model.year == year)
        )
        return list(result.scalars().all())

    async def get_by_type(self, doc_type: str) -> list[TaxDocumentModel]:
        """
        Get all documents of a specific type.

        Args:
            doc_type: Document type

        Returns:
            List of documents of the type
        """
        result = await self.db.execute(
            select(self.model).where(self.model.type == doc_type)
        )
        return list(result.scalars().all())

    async def get_by_status(self, status: str) -> list[TaxDocumentModel]:
        """
        Get all documents with a specific status.

        Args:
            status: Document status

        Returns:
            List of documents with the status
        """
        result = await self.db.execute(
            select(self.model).where(self.model.status == status)
        )
        return list(result.scalars().all())
