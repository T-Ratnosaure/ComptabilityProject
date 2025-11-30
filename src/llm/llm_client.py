"""Abstract LLM client interface and implementations."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

import httpx
import tiktoken
from anthropic import AsyncAnthropic

from src.llm.exceptions import (
    LLMAPIError,
    LLMConfigurationError,
    LLMRateLimitError,
    LLMTimeoutError,
)


class LLMClient(ABC):
    """Abstract LLM client for multi-provider support."""

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Send completion request to LLM API.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            model: Model identifier (e.g., "claude-3-5-sonnet-20241022")
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            {
                "content": "...",
                "usage": {"input_tokens": ..., "output_tokens": ...},
                "stop_reason": "..."
            }

        Raises:
            LLMAPIError: On API failures
            LLMRateLimitError: On rate limits
            LLMTimeoutError: On timeouts
        """
        pass

    @abstractmethod
    async def complete_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Send streaming completion request to LLM API.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            model: Model identifier
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they arrive

        Raises:
            LLMAPIError: On API failures
            LLMRateLimitError: On rate limits
            LLMTimeoutError: On timeouts
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text for the given model.

        Args:
            text: Text to count tokens for
            model: Model identifier (encoding varies by model)

        Returns:
            Token count
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close client and release resources."""
        pass


class ClaudeClient(LLMClient):
    """Anthropic Claude client implementation."""

    def __init__(self, api_key: str, timeout: int = 60):
        """Initialize Claude client.

        Args:
            api_key: Anthropic API key
            timeout: Request timeout in seconds

        Raises:
            LLMConfigurationError: If API key is missing
        """
        if not api_key:
            raise LLMConfigurationError("Anthropic API key is required")

        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=httpx.Timeout(timeout, connect=10.0),
            max_retries=2,
        )

        # Token encoding for Claude (use cl100k_base as approximation)
        self.encoding = tiktoken.get_encoding("cl100k_base")

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Send completion request to Claude API.

        Args:
            messages: List of {"role": "system/user/assistant", "content": "..."}
            model: Claude model ID
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Returns:
            {
                "content": str,
                "usage": {"input_tokens": int, "output_tokens": int},
                "stop_reason": str
            }

        Raises:
            LLMAPIError: On API failures
            LLMRateLimitError: On rate limits (429)
            LLMTimeoutError: On timeouts
        """
        try:
            # Separate system messages from user/assistant messages
            system_messages = [m for m in messages if m["role"] == "system"]
            conversation_messages = [m for m in messages if m["role"] != "system"]

            # Combine system messages into single system prompt
            system_prompt = (
                "\n\n".join(m["content"] for m in system_messages)
                if system_messages
                else None
            )

            response = await self.client.messages.create(
                model=model,
                messages=conversation_messages,
                system=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return {
                "content": response.content[0].text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "stop_reason": response.stop_reason,
            }

        except httpx.TimeoutException as e:
            raise LLMTimeoutError(f"Request timed out: {e}") from e
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                raise LLMRateLimitError(f"Rate limit exceeded: {e}") from e
            raise LLMAPIError(f"Claude API error: {e}") from e

    async def complete_stream(
        self,
        messages: list[dict[str, str]],
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Send streaming completion request to Claude API.

        Args:
            messages: List of {"role": "system/user/assistant", "content": "..."}
            model: Claude model ID
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they arrive

        Raises:
            LLMAPIError: On API failures
            LLMRateLimitError: On rate limits
            LLMTimeoutError: On timeouts
        """
        try:
            # Separate system messages
            system_messages = [m for m in messages if m["role"] == "system"]
            conversation_messages = [m for m in messages if m["role"] != "system"]

            system_prompt = (
                "\n\n".join(m["content"] for m in system_messages)
                if system_messages
                else None
            )

            async with self.client.messages.stream(
                model=model,
                messages=conversation_messages,
                system=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except httpx.TimeoutException as e:
            raise LLMTimeoutError(f"Stream timed out: {e}") from e
        except Exception as e:
            error_str = str(e)
            if "rate_limit" in error_str.lower() or "429" in error_str:
                raise LLMRateLimitError(f"Rate limit exceeded: {e}") from e
            raise LLMAPIError(f"Claude API streaming error: {e}") from e

    async def count_tokens(
        self, text: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> int:
        """Count tokens in text using tiktoken.

        Args:
            text: Text to count tokens for
            model: Model identifier (not used, kept for interface compatibility)

        Returns:
            Approximate token count
        """
        return len(self.encoding.encode(text))

    async def close(self) -> None:
        """Close Claude client and release resources."""
        await self.client.close()
