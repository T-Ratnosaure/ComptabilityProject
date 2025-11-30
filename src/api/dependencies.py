"""FastAPI dependencies."""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.repositories.tax_document import TaxDocumentRepository
from src.database.session import AsyncSessionLocal
from src.llm.context_builder import LLMContextBuilder
from src.llm.conversation_manager import ConversationManager
from src.llm.llm_client import ClaudeClient, LLMClient
from src.llm.llm_service import LLMAnalysisService
from src.llm.prompt_loader import PromptLoader

# Singleton instances (created at app startup)
_llm_client: LLMClient | None = None
_prompt_loader: PromptLoader | None = None


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


async def get_llm_client() -> LLMClient:
    """Get LLM client singleton.

    Returns:
        LLM client instance

    Note:
        Client is created once and reused across requests
    """
    global _llm_client
    if _llm_client is None:
        _llm_client = ClaudeClient(
            api_key=settings.ANTHROPIC_API_KEY,
            timeout=settings.LLM_TIMEOUT,
        )
    return _llm_client


async def get_prompt_loader() -> PromptLoader:
    """Get prompt loader singleton.

    Returns:
        Prompt loader instance
    """
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader(prompts_dir="prompts")
    return _prompt_loader


async def get_conversation_manager(
    db: AsyncSession = Depends(get_db_session),
    llm_client: LLMClient = Depends(get_llm_client),
) -> ConversationManager:
    """Get conversation manager (per-request).

    Args:
        db: Database session
        llm_client: LLM client

    Returns:
        Conversation manager instance
    """
    return ConversationManager(
        db_session=db,
        llm_client=llm_client,
        max_messages_per_conversation=100,
        max_tokens_per_conversation=100000,
        conversation_ttl_days=30,
    )


async def get_llm_service(
    llm_client: LLMClient = Depends(get_llm_client),
    prompt_loader: PromptLoader = Depends(get_prompt_loader),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
) -> LLMAnalysisService:
    """Get LLM analysis service (per-request).

    Args:
        llm_client: LLM client
        prompt_loader: Prompt loader
        conversation_manager: Conversation manager

    Returns:
        LLM analysis service instance
    """
    return LLMAnalysisService(
        llm_client=llm_client,
        context_builder=LLMContextBuilder(),
        prompt_loader=prompt_loader,
        conversation_manager=conversation_manager,
    )
