"""Pydantic models for LLM messages and conversations."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from src.security.llm_sanitizer import sanitize_for_llm


class LLMMessage(BaseModel):
    """Single LLM message with role and content."""

    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=500000)

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Sanitize message content for LLM safety.

        Args:
            v: Raw content

        Returns:
            Sanitized content
        """
        return sanitize_for_llm(v)


class LLMConversation(BaseModel):
    """Complete conversation with message sequence validation."""

    messages: list[LLMMessage] = Field(min_length=1, max_length=100)

    @field_validator("messages")
    @classmethod
    def validate_message_sequence(cls, messages: list[LLMMessage]) -> list[LLMMessage]:
        """Validate conversation message sequence.

        Rules:
        1. System messages should come first (optional)
        2. After system messages, conversation should alternate user/assistant
        3. First non-system message must be from user
        4. Last message should be from user (for completion requests)

        Args:
            messages: List of messages

        Returns:
            Validated messages

        Raises:
            ValueError: If message sequence is invalid
        """
        if not messages:
            raise ValueError("Conversation must have at least one message")

        # Separate system messages from conversation
        system_messages = [m for m in messages if m.role == "system"]
        conversation_messages = [m for m in messages if m.role != "system"]

        # System messages must come first
        if system_messages:
            system_indices = [i for i, m in enumerate(messages) if m.role == "system"]
            if system_indices != list(range(len(system_messages))):
                raise ValueError("System messages must come first in conversation")

        # Must have at least one conversation message
        if not conversation_messages:
            raise ValueError("Conversation must have at least one non-system message")

        # First conversation message must be from user
        if conversation_messages[0].role != "user":
            raise ValueError("First conversation message must be from user")

        # Validate alternating user/assistant (relaxed: allow multiple user messages)
        for i in range(1, len(conversation_messages)):
            current = conversation_messages[i]
            previous = conversation_messages[i - 1]

            # Assistant messages must follow user messages
            if current.role == "assistant" and previous.role != "user":
                raise ValueError(
                    f"Assistant message at position {i} must follow user message"
                )

        return messages


class AnalysisRequest(BaseModel):
    """Request for LLM fiscal analysis."""

    user_id: str = Field(min_length=1, max_length=100)
    conversation_id: str | None = None  # None for new conversation
    user_question: str | None = Field(None, max_length=10000)
    profile_data: dict = Field(default_factory=dict)
    tax_result: dict = Field(default_factory=dict)
    optimization_result: dict | None = None
    include_few_shot: bool = True  # Include few-shot examples
    include_context: bool = True  # Include full fiscal context


class AnalysisResponse(BaseModel):
    """Response from LLM fiscal analysis."""

    conversation_id: str
    message_id: str
    content: str
    usage: dict[str, int]  # input_tokens, output_tokens
    was_sanitized: bool = False
    warnings: list[str] = Field(default_factory=list)
