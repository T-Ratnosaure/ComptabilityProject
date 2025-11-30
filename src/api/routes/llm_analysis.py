"""LLM analysis API endpoints."""

import asyncio
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.api.dependencies import get_llm_service
from src.llm.exceptions import LLMAPIError, LLMRateLimitError, LLMTimeoutError
from src.llm.llm_service import LLMAnalysisService
from src.models.llm_message import AnalysisRequest

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])


class AnalyzeRequest(BaseModel):
    """Request for fiscal analysis."""

    user_id: str = Field(min_length=1, max_length=100)
    conversation_id: str | None = Field(None, description="Existing conversation ID")
    user_question: str | None = Field(
        None,
        max_length=10000,
        description="User question (optional, defaults to general analysis)",
    )
    profile_data: dict[str, Any] = Field(
        default_factory=dict, description="User fiscal profile"
    )
    tax_result: dict[str, Any] = Field(
        default_factory=dict, description="Tax calculation result"
    )
    optimization_result: dict[str, Any] | None = Field(
        None, description="Optimization recommendations"
    )
    include_few_shot: bool = Field(
        True, description="Include few-shot examples in prompt"
    )
    include_context: bool = Field(
        True, description="Include full fiscal context in prompt"
    )


class AnalyzeResponse(BaseModel):
    """Response from fiscal analysis."""

    conversation_id: str
    message_id: str
    content: str
    usage: dict[str, int]
    was_sanitized: bool
    warnings: list[str]


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_fiscal_situation(
    request: AnalyzeRequest,
    llm_service: LLMAnalysisService = Depends(get_llm_service),
) -> dict[str, Any]:
    """Analyze fiscal situation and provide recommendations.

    This endpoint:
    1. Builds a comprehensive fiscal context
    2. Sends it to Claude LLM with appropriate prompts
    3. Returns personalized tax optimization recommendations

    Args:
        request: Analysis request with user data
        llm_service: LLM analysis service (injected)

    Returns:
        Analysis response with recommendations

    Raises:
        HTTPException: On errors (timeout, rate limit, API failure)

    Example request:
        ```json
        {
          "user_id": "user123",
          "user_question": "Comment optimiser mes impôts avec le PER ?",
          "profile_data": {
            "tax_year": 2024,
            "nb_parts": 1.0,
            "status": "micro_bnc",
            "professional_gross": 50000
          },
          "tax_result": {
            "impot": {"impot_net": 5000, "tmi": 0.30},
            "socials": {"urssaf_expected": 11000}
          }
        }
        ```

    Example response:
        ```json
        {
          "conversation_id": "conv-123",
          "message_id": "msg-456",
          "content": "Votre situation fiscale...",
          "usage": {"input_tokens": 1500, "output_tokens": 800},
          "was_sanitized": false,
          "warnings": []
        }
        ```
    """
    try:
        # Convert to internal request model
        analysis_request = AnalysisRequest(
            user_id=request.user_id,
            conversation_id=request.conversation_id,
            user_question=request.user_question,
            profile_data=request.profile_data,
            tax_result=request.tax_result,
            optimization_result=request.optimization_result,
            include_few_shot=request.include_few_shot,
            include_context=request.include_context,
        )

        # Call LLM service with timeout
        response = await asyncio.wait_for(
            llm_service.analyze_fiscal_situation(analysis_request), timeout=90.0
        )

        return response.model_dump()

    except TimeoutError as e:
        raise HTTPException(
            status_code=504, detail="LLM request timed out after 90 seconds"
        ) from e
    except LLMTimeoutError as e:
        raise HTTPException(status_code=504, detail=f"LLM timeout: {e}") from e
    except LLMRateLimitError as e:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {e}") from e
    except LLMAPIError as e:
        raise HTTPException(status_code=502, detail=f"LLM API error: {e}") from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        ) from e


@router.post("/analyze/stream")
async def analyze_fiscal_situation_stream(
    request: AnalyzeRequest,
    llm_service: LLMAnalysisService = Depends(get_llm_service),
) -> StreamingResponse:
    """Analyze fiscal situation with streaming response.

    Same as /analyze but returns Server-Sent Events (SSE) stream.

    Args:
        request: Analysis request
        llm_service: LLM service (injected)

    Returns:
        Streaming response with text chunks

    Example:
        ```bash
        curl -N -X POST http://localhost:8000/api/v1/llm/analyze/stream \\
          -H "Content-Type: application/json" \\
          -d '{"user_id": "user123", "profile_data": {...}}'
        ```

        Stream output:
        ```
        data: Votre
        data:  situation
        data:  fiscale
        data: ...
        ```
    """

    async def event_generator():
        """Generate SSE events from LLM stream."""
        try:
            # Convert to internal request
            analysis_request = AnalysisRequest(
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                user_question=request.user_question,
                profile_data=request.profile_data,
                tax_result=request.tax_result,
                optimization_result=request.optimization_result,
                include_few_shot=request.include_few_shot,
                include_context=request.include_context,
            )

            # Stream from LLM
            async for chunk in llm_service.analyze_fiscal_situation_stream(
                analysis_request
            ):
                yield f"data: {chunk}\n\n"

            # Send completion event
            yield "data: [DONE]\n\n"

        except LLMTimeoutError as e:
            yield f"data: [ERROR] Timeout: {e}\n\n"
        except LLMRateLimitError as e:
            yield f"data: [ERROR] Rate limit: {e}\n\n"
        except LLMAPIError as e:
            yield f"data: [ERROR] API error: {e}\n\n"
        except Exception as e:
            yield f"data: [ERROR] Internal error: {e}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    llm_service: LLMAnalysisService = Depends(get_llm_service),
) -> dict[str, Any]:
    """Get conversation history.

    Args:
        conversation_id: Conversation ID
        llm_service: LLM service (injected)

    Returns:
        Conversation with messages

    Raises:
        HTTPException: If conversation not found
    """
    conversation = await llm_service.conversation_manager.get_conversation(
        conversation_id
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_at": conversation.created_at.isoformat(),
        "updated_at": conversation.updated_at.isoformat(),
        "total_messages": conversation.total_messages,
        "total_tokens": conversation.total_tokens,
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "token_count": msg.token_count,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in conversation.messages
        ],
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    llm_service: LLMAnalysisService = Depends(get_llm_service),
) -> dict[str, str]:
    """Delete conversation and all messages.

    Args:
        conversation_id: Conversation ID
        llm_service: LLM service (injected)

    Returns:
        Success message

    Raises:
        HTTPException: If conversation not found
    """
    deleted = await llm_service.conversation_manager.delete_conversation(
        conversation_id
    )

    if not deleted:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted successfully"}
