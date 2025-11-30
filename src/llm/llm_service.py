"""High-level LLM analysis service."""

from collections.abc import AsyncIterator

from src.llm.context_builder import LLMContextBuilder
from src.llm.conversation_manager import ConversationManager
from src.llm.llm_client import LLMClient
from src.llm.prompt_loader import PromptLoader
from src.models.llm_message import AnalysisRequest, AnalysisResponse
from src.models.optimization import OptimizationResult


class LLMAnalysisService:
    """High-level service for LLM fiscal analysis."""

    def __init__(
        self,
        llm_client: LLMClient,
        context_builder: LLMContextBuilder,
        prompt_loader: PromptLoader,
        conversation_manager: ConversationManager,
    ):
        """Initialize LLM analysis service.

        Args:
            llm_client: LLM API client
            context_builder: Fiscal context builder
            prompt_loader: Prompt loader
            conversation_manager: Conversation manager
        """
        self.llm_client = llm_client
        self.context_builder = context_builder
        self.prompt_loader = prompt_loader
        self.conversation_manager = conversation_manager

    async def analyze_fiscal_situation(
        self,
        request: AnalysisRequest,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
    ) -> AnalysisResponse:
        """Analyze fiscal situation and provide recommendations.

        Args:
            request: Analysis request with user data
            model: LLM model to use
            temperature: Sampling temperature

        Returns:
            Analysis response with recommendations
        """
        # 1. Get or create conversation
        if request.conversation_id:
            conversation = await self.conversation_manager.get_conversation(
                request.conversation_id
            )
            if not conversation:
                # Conversation not found, create new one
                conversation = await self.conversation_manager.create_conversation(
                    user_id=request.user_id, title="Analyse fiscale"
                )
        else:
            conversation = await self.conversation_manager.create_conversation(
                user_id=request.user_id, title="Analyse fiscale"
            )

        # 2. Build fiscal context
        llm_context = await self._build_context(request)

        # 3. Build messages
        messages = await self._build_messages(request, llm_context)

        # 4. Save user message to conversation
        if request.user_question:
            await self.conversation_manager.add_message(
                conversation_id=conversation.id,
                role="user",
                content=request.user_question,
                sanitize=True,
            )

        # 5. Call LLM
        llm_response = await self.llm_client.complete(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=4096,
        )

        # 6. Save assistant response to conversation
        message = await self.conversation_manager.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=llm_response["content"],
            sanitize=False,  # LLM output doesn't need sanitization
        )

        # 7. Build response
        return AnalysisResponse(
            conversation_id=conversation.id,
            message_id=message.id,
            content=llm_response["content"],
            usage=llm_response["usage"],
            was_sanitized=message.was_sanitized,
            warnings=[],
        )

    async def analyze_fiscal_situation_stream(
        self,
        request: AnalysisRequest,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """Analyze fiscal situation with streaming response.

        Args:
            request: Analysis request
            model: LLM model to use
            temperature: Sampling temperature

        Yields:
            Text chunks as they arrive
        """
        # 1. Get or create conversation
        if request.conversation_id:
            conversation = await self.conversation_manager.get_conversation(
                request.conversation_id
            )
            if not conversation:
                conversation = await self.conversation_manager.create_conversation(
                    user_id=request.user_id, title="Analyse fiscale"
                )
        else:
            conversation = await self.conversation_manager.create_conversation(
                user_id=request.user_id, title="Analyse fiscale"
            )

        # 2. Build context and messages
        llm_context = await self._build_context(request)
        messages = await self._build_messages(request, llm_context)

        # 3. Save user message
        if request.user_question:
            await self.conversation_manager.add_message(
                conversation_id=conversation.id,
                role="user",
                content=request.user_question,
                sanitize=True,
            )

        # 4. Stream LLM response
        full_response = ""
        async for chunk in self.llm_client.complete_stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=4096,
        ):
            full_response += chunk
            yield chunk

        # 5. Save complete response to conversation
        await self.conversation_manager.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=full_response,
            sanitize=False,
        )

    async def _build_context(self, request: AnalysisRequest) -> dict:
        """Build LLM context from request.

        Args:
            request: Analysis request

        Returns:
            LLM context dict
        """
        # Parse optimization result if provided
        optimization_result = None
        if request.optimization_result:
            try:
                optimization_result = OptimizationResult(**request.optimization_result)
            except Exception:
                # If parsing fails, ignore optimization result
                pass

        # Build context
        llm_context = await self.context_builder.build_context(
            profile_data=request.profile_data,
            tax_result=request.tax_result,
            optimization_result=optimization_result,
            documents=[],  # TODO: Add document support
        )

        return llm_context.model_dump()

    async def _build_messages(
        self, request: AnalysisRequest, llm_context: dict
    ) -> list[dict[str, str]]:
        """Build message list for LLM.

        Args:
            request: Analysis request
            llm_context: Fiscal context

        Returns:
            List of messages in Anthropic format
        """
        messages = []

        # 1. System prompt
        system_prompt = self.prompt_loader.load_system_prompt(variant="default")
        messages.append({"role": "system", "content": system_prompt})

        # 2. Few-shot examples (if requested)
        if request.include_few_shot:
            # Add PER examples if relevant
            if (
                llm_context.get("profil", {}).get("per_contributions", 0) > 0
                or request.user_question
                and "per" in request.user_question.lower()
            ):
                per_examples = self.prompt_loader.load_few_shot_examples("per")
                messages.append({"role": "system", "content": per_examples})

            # Add regime comparison examples if relevant
            if (
                llm_context.get("calcul_fiscal", {}).get("comparaison_micro_reel")
                or request.user_question
                and (
                    "micro" in request.user_question.lower()
                    or "réel" in request.user_question.lower()
                )
            ):
                regime_examples = self.prompt_loader.load_few_shot_examples("regime")
                messages.append({"role": "system", "content": regime_examples})

        # 3. Get conversation history (if exists)
        if request.conversation_id:
            history = await self.conversation_manager.get_recent_messages(
                request.conversation_id, limit=10
            )
            for msg in history:
                messages.append({"role": msg.role, "content": msg.content})

        # 4. User request with context
        if request.include_context:
            # Render context template
            user_message = self.prompt_loader.render_template(
                "analysis_request.jinja2",
                profil=llm_context.get("profil", {}),
                calcul_fiscal=llm_context.get("calcul_fiscal", {}),
                recommendations=llm_context.get("recommendations", []),
                warnings=llm_context.get("calcul_fiscal", {}).get("warnings", []),
                user_question=request.user_question,
            )
        else:
            # Simple question without full context
            user_message = request.user_question or "Analyser ma situation fiscale."

        # Only add user message if it's a new message (not already in history)
        if not request.conversation_id or request.user_question:
            messages.append({"role": "user", "content": user_message})

        return messages
