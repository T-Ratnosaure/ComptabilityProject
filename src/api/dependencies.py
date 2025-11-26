"""FastAPI dependencies."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repositories.tax_document import TaxDocumentRepository
from src.database.session import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_tax_document_repository(
    session: AsyncSession,
) -> TaxDocumentRepository:
    """Get tax document repository dependency.

    Args:
        session: Database session

    Returns:
        TaxDocumentRepository instance
    """
    return TaxDocumentRepository(session)
