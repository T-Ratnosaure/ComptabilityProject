"""Conversation manager for LLM sessions."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database.models.conversation import ConversationModel, MessageModel
from src.llm.llm_client import LLMClient
from src.security.llm_sanitizer import sanitize_for_llm


class ConversationManager:
    """Manage LLM conversation sessions with automatic cleanup."""

    def __init__(
        self,
        db_session: AsyncSession,
        llm_client: LLMClient,
        max_messages_per_conversation: int = 100,
        max_tokens_per_conversation: int = 100000,
        conversation_ttl_days: int = 30,
    ):
        """Initialize conversation manager.

        Args:
            db_session: Database session
            llm_client: LLM client for token counting
            max_messages_per_conversation: Maximum messages before cleanup
            max_tokens_per_conversation: Maximum tokens before cleanup
            conversation_ttl_days: Days before conversation expires
        """
        self.db = db_session
        self.llm_client = llm_client
        self.max_messages = max_messages_per_conversation
        self.max_tokens = max_tokens_per_conversation
        self.ttl_days = conversation_ttl_days

    async def create_conversation(
        self, user_id: str, title: str | None = None
    ) -> ConversationModel:
        """Create new conversation.

        Args:
            user_id: User identifier
            title: Optional conversation title

        Returns:
            Created conversation
        """
        conversation = ConversationModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title or "Nouvelle conversation",
            total_messages=0,
            total_tokens=0,
        )

        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def get_conversation(self, conversation_id: str) -> ConversationModel | None:
        """Get conversation by ID with messages.

        Args:
            conversation_id: Conversation ID

        Returns:
            Conversation with messages or None
        """
        result = await self.db.execute(
            select(ConversationModel)
            .where(ConversationModel.id == conversation_id)
            .options(selectinload(ConversationModel.messages))
        )
        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sanitize: bool = True,
    ) -> MessageModel:
        """Add message to conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role (system/user/assistant)
            content: Message content
            sanitize: Whether to sanitize content

        Returns:
            Created message

        Raises:
            ValueError: If conversation not found
        """
        # Get conversation
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Sanitize content if requested
        was_sanitized = False
        if sanitize:
            original_content = content
            sanitized_result = sanitize_for_llm(content)
            content = sanitized_result["sanitized_text"]
            was_sanitized = sanitized_result["redacted_count"] > 0

        # Count tokens
        token_count = await self.llm_client.count_tokens(content, model="")

        # Create message
        message = MessageModel(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            token_count=token_count,
            was_sanitized=was_sanitized,
        )

        self.db.add(message)

        # Update conversation stats
        conversation.total_messages += 1
        conversation.total_tokens += token_count or 0
        conversation.last_message_at = datetime.now(UTC)
        conversation.updated_at = datetime.now(UTC)

        await self.db.commit()
        await self.db.refresh(message)

        # Check if cleanup needed
        await self._cleanup_if_needed(conversation)

        return message

    async def get_messages(
        self,
        conversation_id: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[MessageModel]:
        """Get messages for conversation.

        Args:
            conversation_id: Conversation ID
            limit: Maximum messages to return
            offset: Number of messages to skip

        Returns:
            List of messages (oldest first)
        """
        query = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at)
            .offset(offset)
        )

        if limit:
            query = query.limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_recent_messages(
        self, conversation_id: str, limit: int = 10
    ) -> list[MessageModel]:
        """Get recent messages for conversation.

        Args:
            conversation_id: Conversation ID
            limit: Number of recent messages

        Returns:
            List of recent messages (newest first)
        """
        query = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Return oldest first

    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete conversation and all messages.

        Args:
            conversation_id: Conversation ID

        Returns:
            True if deleted, False if not found
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False

        await self.db.delete(conversation)
        await self.db.commit()
        return True

    async def cleanup_old_conversations(self) -> int:
        """Delete conversations older than TTL.

        Returns:
            Number of conversations deleted
        """
        cutoff_date = datetime.now(UTC) - timedelta(days=self.ttl_days)

        result = await self.db.execute(
            delete(ConversationModel).where(ConversationModel.updated_at < cutoff_date)
        )
        await self.db.commit()

        return result.rowcount or 0

    async def _cleanup_if_needed(self, conversation: ConversationModel) -> None:
        """Cleanup conversation if limits exceeded.

        Args:
            conversation: Conversation to check
        """
        # Check message count limit
        if conversation.total_messages > self.max_messages:
            await self._trim_old_messages(
                conversation.id, keep_last=self.max_messages // 2
            )

        # Check token limit
        if conversation.total_tokens > self.max_tokens:
            await self._trim_by_tokens(conversation.id, max_tokens=self.max_tokens // 2)

    async def _trim_old_messages(self, conversation_id: str, keep_last: int) -> None:
        """Trim old messages from conversation.

        Args:
            conversation_id: Conversation ID
            keep_last: Number of recent messages to keep
        """
        # Get messages to delete
        messages = await self.get_messages(conversation_id)
        if len(messages) <= keep_last:
            return

        messages_to_delete = messages[: len(messages) - keep_last]
        deleted_tokens = sum(m.token_count or 0 for m in messages_to_delete)

        # Delete old messages
        message_ids = [m.id for m in messages_to_delete]
        await self.db.execute(
            delete(MessageModel).where(MessageModel.id.in_(message_ids))
        )

        # Update conversation stats
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.total_messages -= len(message_ids)
            conversation.total_tokens -= deleted_tokens

        await self.db.commit()

    async def _trim_by_tokens(self, conversation_id: str, max_tokens: int) -> None:
        """Trim messages to stay under token limit.

        Args:
            conversation_id: Conversation ID
            max_tokens: Maximum tokens to keep
        """
        messages = await self.get_messages(conversation_id)

        # Calculate tokens from newest to oldest
        total_tokens = 0
        messages_to_keep = []

        for message in reversed(messages):
            token_count = message.token_count or 0
            if total_tokens + token_count > max_tokens:
                break
            messages_to_keep.insert(0, message)
            total_tokens += token_count

        if len(messages_to_keep) == len(messages):
            return  # No trimming needed

        # Delete messages not in keep list
        keep_ids = [m.id for m in messages_to_keep]
        await self.db.execute(
            delete(MessageModel).where(
                MessageModel.conversation_id == conversation_id,
                MessageModel.id.notin_(keep_ids),
            )
        )

        # Update conversation stats
        conversation = await self.get_conversation(conversation_id)
        if conversation:
            conversation.total_messages = len(messages_to_keep)
            conversation.total_tokens = total_tokens

        await self.db.commit()
