"""SQLAlchemy models for LLM conversations."""

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.base import Base


class ConversationModel(Base):
    """Conversation database model for LLM sessions."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationship to messages
    messages: Mapped[list["MessageModel"]] = relationship(
        "MessageModel",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="MessageModel.created_at",
    )


class MessageModel(Base):
    """Message database model for conversation history."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)  # UUID
    conversation_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("conversations.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # system/user/assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    was_sanitized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    # Relationship to conversation
    conversation: Mapped["ConversationModel"] = relationship(
        "ConversationModel", back_populates="messages"
    )
