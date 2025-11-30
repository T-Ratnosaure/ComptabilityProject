# Revue Technique Pré-Phase 5 : LLM Integration

**Date :** 2025-11-30
**Version :** 1.0
**Statut :** Revue complète avant développement Phase 5

---

## Executive Summary

Cette revue technique valide la préparation du projet ComptabilityProject pour l'intégration LLM (Phase 5). Le projet dispose d'une **base solide** (score 8/10) avec des modèles Pydantic complets, un sanitizer robuste, et une architecture async bien établie.

**Points forts :**
- ✅ Contexte fiscal structuré et validé (LLMContext, FiscalProfile, TaxCalculationSummary)
- ✅ Sécurité (sanitization PII, prompt injection detection)
- ✅ Infrastructure async complète (FastAPI, SQLAlchemy)
- ✅ Architecture découplée et testable

**Points d'attention :**
- ⚠️ Absence de client LLM API (Anthropic/OpenAI)
- ⚠️ Gestion de conversation non implémentée
- ⚠️ Prompts système non définis
- ⚠️ Token counting manquant

**Recommandation :** Développement Phase 5 peut démarrer après application des corrections ci-dessous.

---

## 1. Architecture Cible pour LLMService

### 1.1 État Actuel

**Existant :**
- `LLMContextBuilder` (src/llm/context_builder.py) : construit le contexte fiscal propre
- `LLMContext` (Pydantic model) : structure validée du contexte
- `LLMSanitizer` (src/security/llm_sanitizer.py) : nettoyage PII/injection

**Manquant :**
- Client API LLM (Anthropic, OpenAI, etc.)
- Service d'orchestration des appels LLM
- Gestion des prompts et templates
- Parsing et validation des réponses

### 1.2 Architecture Proposée

```
src/llm/
├── __init__.py                      # Exports publics
├── context_builder.py               # ✅ Existe - Builder de contexte fiscal
├── llm_client.py                    # ❌ À créer - Client API abstrait
├── llm_service.py                   # ❌ À créer - Service métier principal
├── conversation_manager.py          # ❌ À créer - Gestion sessions/historique
├── prompt_loader.py                 # ❌ À créer - Chargement prompts système
└── response_parser.py               # ❌ À créer - Parsing/validation réponses

prompts/
├── system/
│   ├── base.md                      # Prompt système de base
│   ├── tax_expert.md                # Instructions domaine fiscal
│   └── safety.md                    # Consignes sécurité/éthique
├── examples/
│   ├── few_shot_per.md              # Exemples PER
│   └── few_shot_regime.md           # Exemples micro/réel
└── templates/
    └── analysis_request.jinja2      # Template requête analyse
```

### 1.3 Interfaces Proposées

#### Interface `LLMClient` (Abstract)

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator

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
            {"content": "...", "usage": {...}, "stop_reason": "..."}

        Raises:
            LLMAPIError: On API failures
            LLMRateLimitError: On rate limits
            LLMTimeoutError: On timeout
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
        """Stream completion response."""
        pass

    @abstractmethod
    async def count_tokens(self, text: str, model: str) -> int:
        """Count tokens for given text and model."""
        pass
```

#### Implémentation `ClaudeClient`

```python
import httpx
from anthropic import AsyncAnthropic

class ClaudeClient(LLMClient):
    """Anthropic Claude API client."""

    def __init__(self, api_key: str, timeout: int = 60):
        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=httpx.Timeout(timeout, connect=10.0)
        )
        self.model_configs = {
            "claude-3-5-sonnet-20241022": {"max_tokens": 8192},
            "claude-3-opus-20240229": {"max_tokens": 4096},
        }

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Implement Claude API call with error handling."""
        try:
            response = await self.client.messages.create(
                model=model,
                messages=messages,
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
                "model": response.model,
            }

        except anthropic.RateLimitError as e:
            raise LLMRateLimitError(f"Rate limit exceeded: {e}")
        except anthropic.APITimeoutError as e:
            raise LLMTimeoutError(f"API timeout: {e}")
        except anthropic.APIError as e:
            raise LLMAPIError(f"API error: {e}")

    async def count_tokens(self, text: str, model: str) -> int:
        """Use anthropic.count_tokens() or tiktoken."""
        # Implementation avec anthropic.count_tokens() ou tiktoken
        pass
```

#### Service `LLMAnalysisService`

```python
from src.llm.llm_client import LLMClient
from src.llm.context_builder import LLMContextBuilder
from src.llm.prompt_loader import PromptLoader
from src.llm.conversation_manager import ConversationManager

class LLMAnalysisService:
    """High-level LLM analysis service for tax optimization."""

    def __init__(
        self,
        llm_client: LLMClient,
        context_builder: LLMContextBuilder,
        prompt_loader: PromptLoader,
        conversation_manager: ConversationManager,
    ):
        self.llm_client = llm_client
        self.context_builder = context_builder
        self.prompt_loader = prompt_loader
        self.conversation_manager = conversation_manager

    async def analyze_fiscal_situation(
        self,
        user_id: str,
        profile_data: dict,
        tax_result: dict,
        optimization_result: OptimizationResult | None = None,
        user_question: str | None = None,
    ) -> AnalysisResponse:
        """Analyze fiscal situation with LLM.

        Args:
            user_id: User identifier for conversation tracking
            profile_data: User fiscal profile
            tax_result: Tax calculation results
            optimization_result: Optimization recommendations
            user_question: Optional specific question

        Returns:
            AnalysisResponse with LLM analysis, sources, metadata
        """
        # 1. Build fiscal context
        llm_context = await self.context_builder.build_context(
            profile_data, tax_result, optimization_result
        )

        # 2. Load system prompts
        system_prompt = await self.prompt_loader.load_system_prompt()

        # 3. Get conversation history
        conversation = await self.conversation_manager.get_or_create(user_id)
        messages = await conversation.get_messages(limit=10)

        # 4. Build message list
        message_list = [
            {"role": "system", "content": system_prompt},
            *messages,  # Historical messages
            {
                "role": "user",
                "content": self._build_user_message(llm_context, user_question)
            }
        ]

        # 5. Call LLM API
        response = await self.llm_client.complete(
            messages=message_list,
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,
            max_tokens=4096,
        )

        # 6. Save to conversation history
        await conversation.add_message("user", message_list[-1]["content"])
        await conversation.add_message("assistant", response["content"])

        # 7. Parse and return
        return AnalysisResponse(
            analysis=response["content"],
            usage=response["usage"],
            conversation_id=conversation.id,
            metadata={"model": response["model"], "stop_reason": response["stop_reason"]}
        )

    def _build_user_message(
        self,
        llm_context: LLMContext,
        user_question: str | None
    ) -> str:
        """Build user message with context."""
        context_json = llm_context.model_dump_json(indent=2)

        if user_question:
            return f"""Question de l'utilisateur: {user_question}

Contexte fiscal:
{context_json}

Analyser la situation et répondre à la question."""
        else:
            return f"""Contexte fiscal:
{context_json}

Analyser la situation fiscale complète et proposer des optimisations."""
```

### 1.4 Découplage Logique Fiscale / Moteur LLM

**Principe :** Logique fiscale dans tax_engine, optimisation dans analyzers, LLM uniquement pour présentation/explication.

```
┌─────────────────────────────────────────────────┐
│           API Layer (FastAPI)                   │
│  /api/v1/tax/calculate                          │
│  /api/v1/optimization/analyze                   │
│  /api/v1/llm/explain        ← NEW               │
└─────────────────┬───────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
┌───────▼─────────┐  ┌──────▼──────────┐
│  Tax Engine     │  │  LLM Service    │
│  (Calcul pur)   │  │  (Explication)  │
│                 │  │                 │
│ - compute_ir()  │  │ - explain()     │
│ - compute_      │  │ - recommend()   │
│   socials()     │  │ - answer()      │
│ - compare_      │  │                 │
│   micro_reel()  │  │ Uses:           │
│                 │  │ - ContextBuilder│
│ NO LLM CALLS    │  │ - LLMClient     │
│ PURE FUNCTIONS  │  │ - PromptLoader  │
└─────────────────┘  └─────────────────┘
         │                    │
         │                    │
         └────────┬───────────┘
                  │
          ┌───────▼────────┐
          │  Data Models   │
          │  (Pydantic)    │
          │                │
          │ - FiscalProfile│
          │ - TaxCalc      │
          │   Summary      │
          │ - LLMContext   │
          └────────────────┘
```

**Garanties :**
1. Tax engine reste **pur** : pas de dépendance sur LLM
2. LLM service consomme outputs tax engine via LLMContext
3. Tests tax engine **indépendants** des tests LLM
4. Migration vers autre LLM = changement LLMClient uniquement

### 1.5 Corrections à Appliquer

#### ✅ **Correction 1.1** : Créer client LLM abstrait
```bash
# Fichier: src/llm/llm_client.py
# Créer ABC LLMClient + implémentation ClaudeClient
# Ajouter dépendances: anthropic>=0.40.0, tiktoken>=0.8.0
```

#### ✅ **Correction 1.2** : Créer LLMAnalysisService
```bash
# Fichier: src/llm/llm_service.py
# Service métier haut niveau pour analyse fiscale
```

#### ✅ **Correction 1.3** : Ajouter exceptions LLM
```bash
# Fichier: src/llm/exceptions.py
# LLMAPIError, LLMRateLimitError, LLMTimeoutError, LLMValidationError
```

#### ✅ **Correction 1.4** : Mettre à jour pyproject.toml
```toml
dependencies = [
    # ... existing deps
    "anthropic>=0.40.0",      # Claude API client
    "tiktoken>=0.8.0",        # Token counting
    "jinja2>=3.1.0",          # Prompt templating
]
```

### 1.6 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **Couplage fort LLM** | Élevé | Moyen | Interface abstraite LLMClient |
| **Coût API non contrôlé** | Élevé | Élevé | Token counting + limites |
| **Latence élevée** | Moyen | Élevé | Streaming + cache |
| **Migration modèle complexe** | Moyen | Faible | Abstraction via interface |

---

## 2. API Standardisée des Messages LLM

### 2.1 Format Standard (Anthropic Messages API)

**Structure validée :**
```python
messages: list[dict[str, str]] = [
    {"role": "system", "content": "Vous êtes un expert fiscal français..."},
    {"role": "user", "content": "Question utilisateur..."},
    {"role": "assistant", "content": "Réponse du LLM..."},
    {"role": "user", "content": "Question de suivi..."},
    {"role": "assistant", "content": "Réponse de suivi..."},
]
```

**Rôles autorisés :**
- `"system"` : Instructions pour le LLM (1 seul message, au début)
- `"user"` : Messages de l'utilisateur
- `"assistant"` : Réponses du LLM

### 2.2 Modèle Pydantic pour Validation

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class LLMMessage(BaseModel):
    """Single LLM message with role and content validation."""

    role: Literal["system", "user", "assistant"] = Field(
        ..., description="Message role (system/user/assistant)"
    )
    content: str = Field(
        ..., min_length=1, max_length=50000, description="Message content"
    )

    @field_validator("content")
    @classmethod
    def sanitize_content(cls, v: str) -> str:
        """Sanitize content for PII and prompt injection."""
        from src.security.llm_sanitizer import sanitize_for_llm
        return sanitize_for_llm(v)

    model_config = {"extra": "forbid"}

class LLMConversation(BaseModel):
    """Validated conversation history."""

    messages: list[LLMMessage] = Field(
        ..., min_length=1, max_length=100, description="Conversation messages"
    )

    @field_validator("messages")
    @classmethod
    def validate_message_sequence(cls, messages: list[LLMMessage]) -> list[LLMMessage]:
        """Ensure valid message sequence (system first, alternating user/assistant)."""
        if not messages:
            raise ValueError("Conversation must have at least one message")

        # System message must be first if present
        if messages[0].role == "system" and len(messages) > 1:
            # After system, must start with user
            if messages[1].role != "user":
                raise ValueError("After system message, must have user message")

        # User/assistant should alternate (after optional system)
        start_idx = 1 if messages[0].role == "system" else 0
        for i in range(start_idx, len(messages) - 1):
            current = messages[i].role
            next_role = messages[i + 1].role

            if current == "user" and next_role not in ["assistant"]:
                raise ValueError(f"User message must be followed by assistant, got {next_role}")
            if current == "assistant" and next_role not in ["user"]:
                raise ValueError(f"Assistant message must be followed by user, got {next_role}")

        return messages

    def to_api_format(self) -> list[dict[str, str]]:
        """Convert to API-compatible format."""
        return [msg.model_dump(exclude={"id", "created_at"}) for msg in self.messages]
```

### 2.3 Normalisation Interne

**Classe utilitaire pour normalisation :**

```python
class MessageNormalizer:
    """Normalize and validate LLM messages."""

    @staticmethod
    def from_db(db_messages: list[MessageModel]) -> LLMConversation:
        """Convert database messages to LLMConversation."""
        messages = [
            LLMMessage(role=msg.role, content=msg.content)
            for msg in db_messages
        ]
        return LLMConversation(messages=messages)

    @staticmethod
    def from_api_request(request_messages: list[dict]) -> LLMConversation:
        """Convert API request to LLMConversation."""
        messages = [LLMMessage(**msg) for msg in request_messages]
        return LLMConversation(messages=messages)

    @staticmethod
    def truncate_by_tokens(
        conversation: LLMConversation,
        max_tokens: int,
        model: str,
        llm_client: LLMClient,
    ) -> LLMConversation:
        """Truncate conversation to fit token limit."""
        # Keep system message always
        system_msgs = [m for m in conversation.messages if m.role == "system"]
        other_msgs = [m for m in conversation.messages if m.role != "system"]

        # Count tokens and remove oldest messages if needed
        total_tokens = 0
        kept_messages = []

        for msg in reversed(other_msgs):  # Start from most recent
            msg_tokens = await llm_client.count_tokens(msg.content, model)
            if total_tokens + msg_tokens > max_tokens:
                break
            kept_messages.insert(0, msg)
            total_tokens += msg_tokens

        return LLMConversation(messages=system_msgs + kept_messages)
```

### 2.4 Logging et Redressage

**Logging standardisé :**

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConversationLogger:
    """Log conversations for debugging and audit."""

    async def log_request(
        self,
        user_id: str,
        conversation_id: str,
        messages: LLMConversation,
        model: str,
    ) -> None:
        """Log outgoing LLM request."""
        logger.info(
            "LLM Request",
            extra={
                "user_id": user_id,
                "conversation_id": conversation_id,
                "model": model,
                "message_count": len(messages.messages),
                "total_chars": sum(len(m.content) for m in messages.messages),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def log_response(
        self,
        conversation_id: str,
        response: dict,
        latency_ms: float,
    ) -> None:
        """Log LLM response."""
        logger.info(
            "LLM Response",
            extra={
                "conversation_id": conversation_id,
                "input_tokens": response["usage"]["input_tokens"],
                "output_tokens": response["usage"]["output_tokens"],
                "stop_reason": response["stop_reason"],
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    async def log_error(
        self,
        conversation_id: str,
        error: Exception,
    ) -> None:
        """Log LLM error."""
        logger.error(
            "LLM Error",
            extra={
                "conversation_id": conversation_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "timestamp": datetime.utcnow().isoformat(),
            },
            exc_info=True,
        )
```

### 2.5 Corrections à Appliquer

#### ✅ **Correction 2.1** : Créer modèles Pydantic messages
```bash
# Fichier: src/models/llm_message.py
# LLMMessage, LLMConversation avec validation
```

#### ✅ **Correction 2.2** : Créer MessageNormalizer
```bash
# Fichier: src/llm/message_normalizer.py
# Conversion DB ↔ API ↔ Pydantic
```

#### ✅ **Correction 2.3** : Créer ConversationLogger
```bash
# Fichier: src/llm/conversation_logger.py
# Logging structuré des conversations
```

### 2.6 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **Messages mal formés** | Moyen | Moyen | Validation Pydantic stricte |
| **Logs contenant PII** | Élevé | Moyen | Sanitization avant logging |
| **Incohérence rôles** | Moyen | Faible | Validation sequence |

---

## 3. Gestion Propre de la Mémoire de Conversation

### 3.1 Modèle de Données

#### Schéma SQLAlchemy

```python
# File: src/database/models/conversation.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.database.models.base import Base

class ConversationModel(Base):
    """Conversation session storage."""

    __tablename__ = "conversations"

    id = Column(String, primary_key=True)  # UUID
    user_id = Column(String, nullable=False, index=True)
    title = Column(String(200), nullable=True)  # Auto-generated or user-set
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)

    # Metadata
    total_messages = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)

    # Relationships
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_user_updated', 'user_id', 'updated_at'),
    )

class MessageModel(Base):
    """Individual message storage."""

    __tablename__ = "messages"

    id = Column(String, primary_key=True)  # UUID
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # system, user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Token tracking
    token_count = Column(Integer, nullable=True)

    # Sanitization flag
    was_sanitized = Column(Boolean, default=False)

    # Relationships
    conversation = relationship("ConversationModel", back_populates="messages")

    # Indexes
    __table_args__ = (
        Index('idx_conversation_created', 'conversation_id', 'created_at'),
    )
```

#### Migration Alembic

```python
# alembic/versions/xxx_add_conversations.py

def upgrade():
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('total_messages', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_user_updated', 'user_id', 'updated_at'),
    )

    op.create_table(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('was_sanitized', sa.Boolean(), nullable=False, server_default='0'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.Index('idx_conversation_created', 'conversation_id', 'created_at'),
    )
```

### 3.2 ConversationManager

```python
# File: src/llm/conversation_manager.py

from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

class ConversationManager:
    """Manage conversation sessions and message history."""

    def __init__(
        self,
        db_session: AsyncSession,
        llm_client: LLMClient,
        max_messages_per_conversation: int = 100,
        max_tokens_per_conversation: int = 100000,
        conversation_ttl_days: int = 30,
    ):
        self.db = db_session
        self.llm_client = llm_client
        self.max_messages = max_messages_per_conversation
        self.max_tokens = max_tokens_per_conversation
        self.ttl_days = conversation_ttl_days

    async def create_conversation(self, user_id: str, title: str | None = None) -> ConversationModel:
        """Create new conversation session."""
        conversation = ConversationModel(
            id=str(uuid4()),
            user_id=user_id,
            title=title or "Nouvelle conversation",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def get_conversation(self, conversation_id: str, user_id: str) -> ConversationModel | None:
        """Get conversation by ID (with user verification)."""
        stmt = select(ConversationModel).where(
            ConversationModel.id == conversation_id,
            ConversationModel.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sanitize: bool = True,
    ) -> MessageModel:
        """Add message to conversation."""
        # Sanitize content if needed
        sanitized_content = content
        was_sanitized = False
        if sanitize and role == "user":
            from src.security.llm_sanitizer import sanitize_for_llm
            sanitized_content, metadata = sanitize_for_llm(content, return_metadata=True)
            was_sanitized = metadata["was_modified"]

        # Count tokens
        token_count = await self.llm_client.count_tokens(sanitized_content, "claude-3-5-sonnet-20241022")

        # Create message
        message = MessageModel(
            id=str(uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=sanitized_content,
            token_count=token_count,
            was_sanitized=was_sanitized,
            created_at=datetime.utcnow(),
        )
        self.db.add(message)

        # Update conversation metadata
        stmt = select(ConversationModel).where(ConversationModel.id == conversation_id)
        conversation = (await self.db.execute(stmt)).scalar_one()
        conversation.total_messages += 1
        conversation.total_tokens += token_count
        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(message)

        # Trigger cleanup if needed
        await self._cleanup_if_needed(conversation)

        return message

    async def get_messages(
        self,
        conversation_id: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[MessageModel]:
        """Get messages from conversation (most recent first by default)."""
        stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.asc())  # Chronological order
            .offset(offset)
        )
        if limit:
            stmt = stmt.limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _cleanup_if_needed(self, conversation: ConversationModel) -> None:
        """Auto-cleanup if limits exceeded."""
        # Check message count
        if conversation.total_messages > self.max_messages:
            await self._trim_old_messages(conversation.id, keep_last=self.max_messages)

        # Check token count
        if conversation.total_tokens > self.max_tokens:
            await self._trim_by_tokens(conversation.id, max_tokens=self.max_tokens)

    async def _trim_old_messages(self, conversation_id: str, keep_last: int) -> None:
        """Remove oldest messages, keeping last N."""
        # Get messages to delete
        stmt = (
            select(MessageModel.id)
            .where(MessageModel.conversation_id == conversation_id)
            .order_by(MessageModel.created_at.desc())
            .offset(keep_last)
        )
        result = await self.db.execute(stmt)
        message_ids = [row[0] for row in result.all()]

        if message_ids:
            delete_stmt = delete(MessageModel).where(MessageModel.id.in_(message_ids))
            await self.db.execute(delete_stmt)
            await self.db.commit()

            # Recalculate totals
            await self._recalculate_conversation_totals(conversation_id)

    async def _trim_by_tokens(self, conversation_id: str, max_tokens: int) -> None:
        """Remove oldest messages until under token limit."""
        messages = await self.get_messages(conversation_id)

        # Calculate from most recent
        total_tokens = 0
        keep_messages = []
        for msg in reversed(messages):
            if total_tokens + msg.token_count <= max_tokens:
                keep_messages.insert(0, msg)
                total_tokens += msg.token_count
            else:
                break

        # Delete messages not in keep list
        keep_ids = [m.id for m in keep_messages]
        all_ids = [m.id for m in messages]
        delete_ids = [mid for mid in all_ids if mid not in keep_ids]

        if delete_ids:
            delete_stmt = delete(MessageModel).where(MessageModel.id.in_(delete_ids))
            await self.db.execute(delete_stmt)
            await self.db.commit()

            await self._recalculate_conversation_totals(conversation_id)

    async def _recalculate_conversation_totals(self, conversation_id: str) -> None:
        """Recalculate total messages and tokens."""
        stmt = select(
            func.count(MessageModel.id),
            func.sum(MessageModel.token_count)
        ).where(MessageModel.conversation_id == conversation_id)

        result = await self.db.execute(stmt)
        count, total_tokens = result.one()

        update_stmt = (
            update(ConversationModel)
            .where(ConversationModel.id == conversation_id)
            .values(total_messages=count or 0, total_tokens=total_tokens or 0)
        )
        await self.db.execute(update_stmt)
        await self.db.commit()

    async def delete_old_conversations(self) -> int:
        """Delete conversations older than TTL (background task)."""
        cutoff_date = datetime.utcnow() - timedelta(days=self.ttl_days)

        stmt = delete(ConversationModel).where(
            ConversationModel.updated_at < cutoff_date
        )
        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount
```

### 3.3 Cache en RAM (optionnel)

```python
from cachetools import TTLCache
from threading import Lock

class ConversationCache:
    """In-memory cache for hot conversations."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self._cache: TTLCache = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self._lock = Lock()

    def get(self, conversation_id: str) -> list[MessageModel] | None:
        """Get cached messages."""
        with self._lock:
            return self._cache.get(conversation_id)

    def set(self, conversation_id: str, messages: list[MessageModel]) -> None:
        """Cache messages."""
        with self._lock:
            self._cache[conversation_id] = messages

    def invalidate(self, conversation_id: str) -> None:
        """Invalidate cache for conversation."""
        with self._lock:
            self._cache.pop(conversation_id, None)
```

### 3.4 Anonymisation

```python
class ConversationAnonymizer:
    """Anonymize conversations for export/analysis."""

    @staticmethod
    def anonymize_conversation(conversation: ConversationModel) -> dict:
        """Anonymize conversation data."""
        return {
            "id": conversation.id,
            "user_id": hash(conversation.user_id) % 1000000,  # Hashed user ID
            "created_at": conversation.created_at.isoformat(),
            "total_messages": conversation.total_messages,
            "messages": [
                {
                    "role": msg.role,
                    "content": anonymize_content(msg.content),  # Redact PII
                    "token_count": msg.token_count,
                }
                for msg in conversation.messages
            ]
        }

    @staticmethod
    def anonymize_content(content: str) -> str:
        """Anonymize message content."""
        from src.security.llm_sanitizer import sanitize_for_llm
        return sanitize_for_llm(content)  # Reuse sanitizer
```

### 3.5 Corrections à Appliquer

#### ✅ **Correction 3.1** : Créer modèles DB conversation
```bash
# Fichier: src/database/models/conversation.py
# ConversationModel, MessageModel
```

#### ✅ **Correction 3.2** : Migration Alembic
```bash
alembic revision --autogenerate -m "add_conversations"
alembic upgrade head
```

#### ✅ **Correction 3.3** : Créer ConversationManager
```bash
# Fichier: src/llm/conversation_manager.py
# Gestion CRUD + nettoyage automatique
```

#### ✅ **Correction 3.4** : Ajouter cachetools
```toml
dependencies = [
    # ... existing
    "cachetools>=5.3.0",  # TTL cache
]
```

#### ✅ **Correction 3.5** : Background task nettoyage
```python
# Fichier: src/tasks/cleanup_conversations.py
# Tâche périodique pour supprimer vieilles conversations
```

### 3.6 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **Croissance DB non contrôlée** | Élevé | Élevé | TTL + nettoyage auto |
| **Fuite PII dans messages** | Critique | Moyen | Sanitization systématique |
| **Token overflow** | Moyen | Élevé | Trim automatique |
| **Concurrence cache/DB** | Faible | Faible | Cache TTL court |

---

## 4. Structure Exacte du Contexte Fiscal

### 4.1 Champs Essentiels (audit validé)

**Référence :** `AUDIT_LLM_CONTEXT_FIELDS.md` (Score 94/100)

#### Profil Fiscal (FiscalProfile)
✅ **Obligatoires :**
- `annee_fiscale` : Année du calcul
- `situation_familiale` : celibataire/marie/pacse/divorce/veuf
- `nombre_parts` : Quotient familial (0.5-10)
- `regime_fiscal` : micro_bnc/micro_bic/reel_bnc/reel_bic
- `type_activite` : BNC/BIC
- `chiffre_affaires` : CA annuel
- `cotisations_sociales` : Total URSSAF

✅ **Importants :**
- `charges_deductibles` : Charges réelles
- `benefice_net` : Après charges
- `charges_detail` : {amortissements, loyer, honoraires, autres}
- `salaires`, `revenus_fonciers`, `revenus_capitaux`, `plus_values` : Autres revenus
- `per_contributions`, `dons_declares`, `pension_alimentaire` : Déductions

✅ **Référence fiscale :**
- `revenu_fiscal_reference` : RFR année N-1
- `impot_annee_precedente` : Impôt payé N-1
- `taux_prelevement_source` : Taux PAS actuel

#### Calcul Fiscal (TaxCalculationSummary)
✅ **Résultats principaux :**
- `impot_brut`, `impot_net` : Impôt sur le revenu
- `cotisations_sociales` : URSSAF
- `charge_fiscale_totale` : IR + URSSAF
- `tmi` : Taux marginal (0.11/0.30/0.41/0.45)
- `taux_effectif` : Charge totale / revenu
- `revenu_imposable` : Revenu net imposable
- `quotient_familial` : Revenu / nb_parts

✅ **Détails calcul :**
- `per_plafond_detail` : {applied, excess, plafond_max}
- `tranches_detail` : [{rate, income_in_bracket, tax_in_bracket}]
- `reductions_fiscales` : {dons, services_personne, frais_garde}
- `comparaison_micro_reel` : ComparisonMicroReel structuré

✅ **Alertes :**
- `warnings` : Liste des avertissements

#### Comparaison Régimes (ComparisonMicroReel)
✅ **Tous les champs :**
- `regime_actuel`, `regime_compare`
- `impot_actuel`, `impot_compare`, `delta_impot`
- `cotisations_actuelles`, `cotisations_comparees`, `delta_cotisations`
- `charge_totale_actuelle`, `charge_totale_comparee`, `delta_total`
- `economie_potentielle`, `pourcentage_economie`
- `recommendation`, `justification`
- `chiffre_affaires`, `charges_reelles`, `taux_abattement_micro`

#### Optimisations (Recommendation[])
✅ **Champs :**
- `id`, `title`, `description`
- `category` : regime/deduction/investment/other
- `priority` : high/medium/low
- `impact_estimated` : Économies potentielles
- `action_steps` : Liste des étapes
- `constraints`, `risks`

### 4.2 Champs à Filtrer (Sécurité)

❌ **INTERDITS (déjà filtrés par LLMContextBuilder) :**
- `id`, `profile_id`, `calculation_id` : IDs techniques
- `created_at`, `updated_at`, `processed_at` : Timestamps
- `file_path`, `original_filename` : Chemins système
- `raw_text` : Texte brut OCR (trop volumineux)
- `error_message` : Messages d'erreur internes
- `status` : Flags techniques

❌ **DANGEREUX (à ne jamais ajouter) :**
- Numéros sécurité sociale
- IBANs complets
- Noms/prénoms réels (utiliser "ANON")
- Adresses complètes
- API keys, tokens

### 4.3 Forme JSON Finale

```python
# Exemple de contexte fiscal complet pour le LLM

llm_context = {
    "profil": {
        "annee_fiscale": 2024,
        "situation_familiale": "celibataire",
        "nombre_parts": 1.0,
        "enfants_a_charge": 0,
        "regime_fiscal": "micro_bnc",
        "type_activite": "BNC",
        "chiffre_affaires": 50000.0,
        "charges_deductibles": 0.0,
        "benefice_net": 33000.0,
        "charges_detail": None,  # Null si micro
        "cotisations_sociales": 10900.0,
        "salaires": 0.0,
        "revenus_fonciers": 0.0,
        "revenus_capitaux": 0.0,
        "plus_values": 0.0,
        "per_contributions": 0.0,
        "dons_declares": 0.0,
        "services_personne": 0.0,
        "frais_garde": 0.0,
        "pension_alimentaire": 0.0,
        "revenu_fiscal_reference": 45000.0,
        "impot_annee_precedente": 3200.0,
        "taux_prelevement_source": 8.5,
        "revenus_stables": False,
        "strategie_patrimoniale": False,
        "capacite_investissement": 0.0,
        "tolerance_risque": "moderate"
    },
    "calcul_fiscal": {
        "impot_brut": 3500.0,
        "impot_net": 3500.0,
        "cotisations_sociales": 10900.0,
        "charge_fiscale_totale": 14400.0,
        "tmi": 0.30,
        "taux_effectif": 0.436,  # 14400 / 33000
        "revenu_imposable": 33000.0,
        "quotient_familial": 33000.0,
        "reductions_fiscales": {},
        "per_plafond_detail": None,  # Null si pas de PER
        "tranches_detail": [
            {"rate": 0.0, "income_in_bracket": 11294.0, "tax_in_bracket": 0.0},
            {"rate": 0.11, "income_in_bracket": 17503.0, "tax_in_bracket": 1925.33},
            {"rate": 0.30, "income_in_bracket": 4203.0, "tax_in_bracket": 1260.90}
        ],
        "cotisations_detail": None,  # TODO: future breakdown
        "comparaison_micro_reel": {
            "regime_actuel": "micro_bnc",
            "regime_compare": "reel_bnc",
            "impot_actuel": 3500.0,
            "impot_compare": 2800.0,
            "delta_impot": -700.0,
            "cotisations_actuelles": 10900.0,
            "cotisations_comparees": 10900.0,
            "delta_cotisations": 0.0,
            "charge_totale_actuelle": 14400.0,
            "charge_totale_comparee": 13700.0,
            "delta_total": -700.0,
            "economie_potentielle": 700.0,
            "pourcentage_economie": 4.86,
            "recommendation": "Passer au réel",
            "justification": "...",
            "chiffre_affaires": 50000.0,
            "charges_reelles": 17000.0,
            "taux_abattement_micro": 0.34
        },
        "warnings": [
            "Vous êtes proche du plafond micro-BNC (77700€). Surveillez votre CA."
        ]
    },
    "recommendations": [
        {
            "id": "per_optimal",
            "title": "PER - Versement optimal",
            "description": "Versez 2772€ sur un PER pour économiser 832€ d'impôts",
            "category": "deduction",
            "priority": "high",
            "impact_estimated": 832.0,
            "action_steps": [...],
            "constraints": [...],
            "risks": [...]
        }
    ],
    "total_economies_potentielles": 1532.0,
    "documents_extraits": {
        "avis_imposition_2024": {
            "type": "avis_imposition",
            "year": 2024,
            "fields": {
                "revenu_fiscal_reference": 45000.0,
                "impot_revenu": 3200.0,
                "taux_prelevement": 8.5
            }
        }
    },
    "metadata": {
        "version": "1.0",
        "calculation_date": "2024-11-30T10:00:00",
        "llm_context_version": "1.0"
    }
}
```

### 4.4 Cohérence FiscalContextModel

**Modèle interne validé :** `LLMContext` (Pydantic)

```python
# src/models/llm_context.py (DÉJÀ IMPLÉMENTÉ ✅)

class LLMContext(BaseModel):
    """Complete context for LLM Phase 5."""

    profil: FiscalProfile
    calcul_fiscal: TaxCalculationSummary
    recommendations: list[Recommendation] = Field(default_factory=list)
    total_economies_potentielles: float = Field(default=0.0, ge=0)
    documents_extraits: dict[str, dict] = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)

    model_config = {"extra": "forbid"}  # Stricte validation
```

**Garanties :**
- ✅ Validation Pydantic complète
- ✅ Types stricts (float, int, str, enums)
- ✅ Contraintes (ge=0, le=100, patterns)
- ✅ Descriptions pour documentation
- ✅ Exemples JSON schema

### 4.5 Corrections à Appliquer

#### ✅ **Correction 4.1** : Aucune (modèles déjà complets)
Les modèles `LLMContext`, `FiscalProfile`, `TaxCalculationSummary` sont déjà à 94/100 après audit Phase 5.

#### ⚠️ **Correction 4.2** : Documenter champs LLM
```bash
# Fichier: docs/LLM_CONTEXT_SPEC.md
# Documentation complète des champs pour développeurs LLM
```

### 4.6 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **Contexte trop volumineux** | Moyen | Moyen | Token counting + priorisation |
| **Champs ambigus pour LLM** | Faible | Faible | Descriptions claires |
| **Évolution schéma** | Faible | Moyen | Versioning metadata |

---

## 5. Chargement Propre des Prompts Système

### 5.1 Structure de Fichiers Proposée

```
prompts/
├── system/
│   ├── base.md                          # Prompt système principal
│   ├── tax_expert_persona.md            # Personnalité expert fiscal
│   ├── safety_guidelines.md             # Consignes sécurité
│   └── output_format.md                 # Format de réponse attendu
├── examples/
│   ├── per_deduction.md                 # Few-shot PER
│   ├── regime_comparison.md             # Few-shot micro/réel
│   ├── tax_reduction.md                 # Few-shot réductions fiscales
│   └── investment_recommendation.md     # Few-shot investissements
├── templates/
│   ├── analysis_request.jinja2          # Template requête analyse
│   ├── followup_question.jinja2         # Template question suivi
│   └── explanation_request.jinja2       # Template explication
└── metadata.json                        # Index des prompts + versions
```

### 5.2 Exemple de Prompts

#### `prompts/system/base.md`

```markdown
# Rôle

Vous êtes un expert-comptable français spécialisé en fiscalité des indépendants (BNC/BIC).

# Domaine d'expertise

- Régimes fiscaux : micro-BNC, micro-BIC, réel simplifié, réel normal
- Cotisations sociales URSSAF
- Optimisation fiscale légale
- PER (Plan Épargne Retraite)
- Réductions et crédits d'impôt
- Comparaison micro vs réel

# Règles strictes

1. **Exactitude fiscale** : Respecter scrupuleusement le Code général des impôts 2024
2. **Sources officielles** : Référencer impots.gouv.fr, service-public.fr, BOFIP
3. **Pas de conseil juridique** : Recommander un expert-comptable pour cas complexes
4. **Transparence** : Expliquer clairement les calculs et hypothèses
5. **Neutralité** : Présenter objectivement avantages et inconvénients
6. **Sécurité** : Ne JAMAIS demander d'informations personnelles (nom, SSN, IBAN)

# Ton

- Professionnel mais accessible
- Pédagogique : expliquer termes techniques
- Concis : éviter jargon inutile
- Bienveillant : pas de jugement

# Format de réponse

1. **Résumé** (2-3 phrases)
2. **Analyse détaillée** (par points)
3. **Recommandations** (priorisées)
4. **Prochaines étapes** (actions concrètes)
5. **Sources** (liens officiels)

# Contexte fiscal fourni

Vous recevrez un objet JSON contenant :
- `profil` : Situation fiscale complète
- `calcul_fiscal` : Résultats calculs IR/URSSAF
- `recommendations` : Optimisations identifiées
- `documents_extraits` : Données issues de documents fiscaux

Utilisez UNIQUEMENT ces données pour vos analyses. Ne supposez rien.
```

#### `prompts/system/safety_guidelines.md`

```markdown
# Consignes de sécurité

## Données sensibles

**INTERDIT :**
- Demander nom/prénom/adresse
- Demander numéro sécurité sociale
- Demander IBAN/coordonnées bancaires
- Demander coordonnées fiscales complètes
- Stocker ou mémoriser données personnelles

**AUTORISÉ :**
- Utiliser données du contexte JSON fourni
- Utiliser identifiant anonyme "ANON"
- Parler en termes généraux

## Recommandations

**INTERDIT :**
- Fraude fiscale ou évasion
- Montages agressifs
- Dissimulation revenus
- Fausses déclarations

**AUTORISÉ :**
- Optimisation légale
- Choix de régime adapté
- Déductions légitimes
- Investissements défiscalisants

## En cas de doute

Recommander de consulter :
1. Expert-comptable agréé
2. Centre des impôts
3. URSSAF
```

### 5.3 PromptLoader

```python
# File: src/llm/prompt_loader.py

from pathlib import Path
from typing import Any
from jinja2 import Environment, FileSystemLoader, select_autoescape
import json

class PromptLoader:
    """Load and manage system prompts."""

    def __init__(self, prompts_dir: Path | str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.prompts_dir / "templates"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self._cache: dict[str, str] = {}
        self._metadata = self._load_metadata()

    def _load_metadata(self) -> dict:
        """Load prompts metadata."""
        metadata_path = self.prompts_dir / "metadata.json"
        if metadata_path.exists():
            with open(metadata_path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    async def load_system_prompt(self, variant: str = "default") -> str:
        """Load complete system prompt.

        Args:
            variant: Prompt variant (default, concise, detailed)

        Returns:
            Complete system prompt string
        """
        cache_key = f"system_{variant}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load components
        base = await self._load_file("system/base.md")
        persona = await self._load_file("system/tax_expert_persona.md")
        safety = await self._load_file("system/safety_guidelines.md")
        output_format = await self._load_file("system/output_format.md")

        # Combine
        system_prompt = f"""{base}

{persona}

{safety}

{output_format}
"""

        # Validate no unresolved variables
        if "{{" in system_prompt or "}}" in system_prompt:
            raise ValueError("Unresolved template variables in system prompt")

        self._cache[cache_key] = system_prompt
        return system_prompt

    async def load_few_shot_examples(self, category: str) -> list[dict[str, str]]:
        """Load few-shot examples for a category.

        Args:
            category: Example category (per_deduction, regime_comparison, etc.)

        Returns:
            List of {"user": "...", "assistant": "..."} examples
        """
        examples_file = self.prompts_dir / "examples" / f"{category}.md"
        if not examples_file.exists():
            return []

        content = await self._load_file(f"examples/{category}.md")

        # Parse examples (format: ## User\n...\n## Assistant\n...)
        examples = []
        sections = content.split("## ")

        current_example = {}
        for section in sections:
            if section.startswith("User"):
                current_example["user"] = section.replace("User\n", "").strip()
            elif section.startswith("Assistant"):
                current_example["assistant"] = section.replace("Assistant\n", "").strip()
                examples.append(current_example)
                current_example = {}

        return examples

    async def render_template(self, template_name: str, **variables: Any) -> str:
        """Render Jinja2 template with variables.

        Args:
            template_name: Template file name (e.g., "analysis_request.jinja2")
            **variables: Variables to inject

        Returns:
            Rendered template string
        """
        template = self.jinja_env.get_template(template_name)
        rendered = template.render(**variables)

        # Validate no unresolved variables
        if "{{" in rendered or "}}" in rendered:
            raise ValueError(f"Unresolved variables in template {template_name}")

        return rendered

    async def _load_file(self, relative_path: str) -> str:
        """Load file content."""
        file_path = self.prompts_dir / relative_path
        if not file_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            return f.read()

    def get_version(self) -> str:
        """Get prompts version from metadata."""
        return self._metadata.get("version", "unknown")
```

#### `prompts/metadata.json`

```json
{
  "version": "1.0.0",
  "last_updated": "2024-11-30",
  "prompts": {
    "system": {
      "base": {
        "path": "system/base.md",
        "description": "Main system prompt",
        "tokens_estimate": 500
      },
      "safety": {
        "path": "system/safety_guidelines.md",
        "description": "Safety and ethical guidelines",
        "tokens_estimate": 200
      }
    },
    "examples": {
      "per_deduction": {
        "path": "examples/per_deduction.md",
        "count": 3,
        "tokens_estimate": 800
      }
    }
  }
}
```

### 5.4 Template Jinja2

#### `prompts/templates/analysis_request.jinja2`

```jinja2
Analyser la situation fiscale suivante et proposer des optimisations.

# Situation fiscale

**Année :** {{ profil.annee_fiscale }}
**Régime :** {{ profil.regime_fiscal }}
**Chiffre d'affaires :** {{ profil.chiffre_affaires | int }} €
**Impôt net :** {{ calcul_fiscal.impot_net | int }} €
**Cotisations sociales :** {{ calcul_fiscal.cotisations_sociales | int }} €
**Charge totale :** {{ calcul_fiscal.charge_fiscale_totale | int }} €

{% if user_question %}
# Question spécifique

{{ user_question }}
{% endif %}

# Demande

1. Analyser la situation
2. Identifier optimisations possibles
3. Prioriser recommandations
4. Expliquer étapes d'action
```

### 5.5 Stratégie Templating

**Recommandation : Jinja2**

| Critère | .format() | Jinja2 | Manuel |
|---------|-----------|--------|--------|
| **Lisibilité** | Moyenne | Haute | Faible |
| **Maintenabilité** | Faible | Haute | Faible |
| **Sécurité** | Moyenne | Haute | Haute |
| **Flexibilité** | Faible | Haute | Haute |
| **i18n support** | Non | Oui | Non |
| **Auto-escape** | Non | Oui | Manuel |

**Verdict :** **Jinja2** pour templates dynamiques, **Fichiers .md statiques** pour prompts système.

### 5.6 Compatibilité i18n (FR/EN)

```
prompts/
├── fr/              # Français (défaut)
│   ├── system/
│   ├── examples/
│   └── templates/
├── en/              # English (futur)
│   ├── system/
│   ├── examples/
│   └── templates/
└── metadata.json    # Index multilingue
```

```python
class PromptLoader:
    def __init__(self, prompts_dir: Path, locale: str = "fr"):
        self.locale = locale
        self.prompts_dir = Path(prompts_dir) / locale
        # ...
```

### 5.7 Corrections à Appliquer

#### ✅ **Correction 5.1** : Créer structure prompts
```bash
mkdir -p prompts/{system,examples,templates}
# Créer fichiers .md et .jinja2
```

#### ✅ **Correction 5.2** : Créer PromptLoader
```bash
# Fichier: src/llm/prompt_loader.py
```

#### ✅ **Correction 5.3** : Ajouter Jinja2
```toml
dependencies = [
    # ... existing
    "jinja2>=3.1.0",
]
```

#### ✅ **Correction 5.4** : Écrire prompts système
```bash
# prompts/system/base.md
# prompts/system/safety_guidelines.md
# etc.
```

### 5.8 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **Variables non résolues** | Moyen | Moyen | Validation post-render |
| **Prompts coupés** | Moyen | Faible | Tests chargement |
| **Incohérence versions** | Faible | Moyen | metadata.json + versioning |
| **Injection template** | Élevé | Faible | Auto-escape Jinja2 |

---

## 6. Compatibilité Async Complète avec FastAPI

### 6.1 État Actuel (Audit)

#### ✅ Infrastructure Async Complète

**FastAPI :**
```python
# src/main.py (DÉJÀ ASYNC ✅)

from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async lifespan for startup/shutdown."""
    # Startup
    yield
    # Shutdown
    await db_engine.dispose()

app = FastAPI(lifespan=lifespan)
```

**SQLAlchemy Async :**
```python
# src/database/session.py (DÉJÀ ASYNC ✅)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("sqlite+aiosqlite:///tax_calculator.db")
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

**Services Async :**
```python
# Exemples déjà async ✅

async def calculate_tax(payload: dict) -> dict:
    # Tax calculation

async def process_document(file: UploadFile) -> TaxDocument:
    # Document processing with OCR

class TaxOptimizer:
    async def run(self, tax_result: dict, profile: dict, context: dict):
        # Optimization analysis
```

**Routes Async :**
```python
# src/api/routes/tax.py (DÉJÀ ASYNC ✅)

@router.post("/calculate")
async def calculate_taxes(request: TaxCalculationRequest) -> dict:
    result = await calculate_tax(payload)
    return result
```

#### ⚠️ LLM Service : À Implémenter en Async

### 6.2 Architecture LLMClient Async

```python
# File: src/llm/llm_client.py

import httpx
from abc import ABC, abstractmethod
from typing import AsyncIterator, Any

class LLMClient(ABC):
    """Abstract async LLM client."""

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any
    ) -> dict[str, Any]:
        """Async completion request."""
        pass

    @abstractmethod
    async def complete_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        **kwargs: Any
    ) -> AsyncIterator[str]:
        """Async streaming completion."""
        pass

class ClaudeClient(LLMClient):
    """Anthropic Claude async client."""

    def __init__(self, api_key: str, timeout: int = 60):
        # AsyncAnthropic est déjà async ✅
        from anthropic import AsyncAnthropic

        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=httpx.Timeout(timeout, connect=10.0)
        )

    async def complete(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict[str, Any]:
        """Non-blocking async API call."""
        response = await self.client.messages.create(  # await ✅
            model=model,
            messages=messages,
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

    async def complete_stream(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Async streaming."""
        async with self.client.messages.stream(  # async context manager ✅
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        ) as stream:
            async for text in stream.text_stream:  # async iteration ✅
                yield text
```

### 6.3 Gestion httpx.AsyncClient

```python
# File: src/llm/llm_client.py (enhanced)

class ClaudeClient(LLMClient):
    """Claude client with connection pool management."""

    def __init__(
        self,
        api_key: str,
        timeout: int = 60,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
    ):
        # Connection pool limits ✅
        limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
        )

        # Timeout configuration ✅
        timeout_config = httpx.Timeout(
            timeout=timeout,
            connect=10.0,  # Connection timeout
            read=60.0,     # Read timeout
            write=10.0,    # Write timeout
            pool=5.0,      # Pool timeout
        )

        self.client = AsyncAnthropic(
            api_key=api_key,
            timeout=timeout_config,
            http_client=httpx.AsyncClient(limits=limits),
        )

    async def close(self) -> None:
        """Close client and release connections."""
        await self.client.close()  # Properly close ✅
```

### 6.4 Intégration FastAPI avec Dependency Injection

```python
# File: src/api/dependencies.py (NEW)

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db_session
from src.llm.llm_client import ClaudeClient, LLMClient
from src.llm.llm_service import LLMAnalysisService
from src.llm.context_builder import LLMContextBuilder
from src.llm.prompt_loader import PromptLoader
from src.llm.conversation_manager import ConversationManager
from src.config import get_settings

settings = get_settings()

# Singleton instances (created at startup)
_llm_client: LLMClient | None = None
_prompt_loader: PromptLoader | None = None

async def get_llm_client() -> LLMClient:
    """Get LLM client singleton."""
    global _llm_client
    if _llm_client is None:
        _llm_client = ClaudeClient(
            api_key=settings.anthropic_api_key,
            timeout=60,
        )
    return _llm_client

async def get_prompt_loader() -> PromptLoader:
    """Get prompt loader singleton."""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader(prompts_dir="prompts")
    return _prompt_loader

async def get_conversation_manager(
    db: AsyncSession = Depends(get_db_session),
    llm_client: LLMClient = Depends(get_llm_client),
) -> ConversationManager:
    """Get conversation manager (per-request)."""
    return ConversationManager(
        db_session=db,
        llm_client=llm_client,
        max_messages_per_conversation=100,
        max_tokens_per_conversation=100000,
    )

async def get_llm_service(
    llm_client: LLMClient = Depends(get_llm_client),
    prompt_loader: PromptLoader = Depends(get_prompt_loader),
    conversation_manager: ConversationManager = Depends(get_conversation_manager),
) -> LLMAnalysisService:
    """Get LLM analysis service (per-request)."""
    return LLMAnalysisService(
        llm_client=llm_client,
        context_builder=LLMContextBuilder(),
        prompt_loader=prompt_loader,
        conversation_manager=conversation_manager,
    )
```

### 6.5 Route FastAPI avec Gestion Timeouts

```python
# File: src/api/routes/llm_analysis.py (NEW)

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import asyncio

from src.api.dependencies import get_llm_service
from src.llm.llm_service import LLMAnalysisService

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

class AnalysisRequest(BaseModel):
    user_id: str
    profile_data: dict
    tax_result: dict
    user_question: str | None = None

@router.post("/analyze")
async def analyze_fiscal_situation(
    request: AnalysisRequest,
    llm_service: LLMAnalysisService = Depends(get_llm_service),
) -> dict:
    """Analyze fiscal situation with LLM.

    Async endpoint with timeout protection.
    """
    try:
        # Set timeout to prevent hanging ✅
        response = await asyncio.wait_for(
            llm_service.analyze_fiscal_situation(
                user_id=request.user_id,
                profile_data=request.profile_data,
                tax_result=request.tax_result,
                user_question=request.user_question,
            ),
            timeout=90.0  # 90 seconds max
        )

        return response.model_dump()

    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="LLM analysis timeout (>90s)"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM analysis failed: {str(e)}"
        )
```

### 6.6 Streaming Response

```python
from fastapi.responses import StreamingResponse

@router.post("/analyze/stream")
async def analyze_fiscal_situation_stream(
    request: AnalysisRequest,
    llm_service: LLMAnalysisService = Depends(get_llm_service),
) -> StreamingResponse:
    """Stream LLM analysis response."""

    async def event_generator():
        """Generate SSE events."""
        try:
            async for chunk in llm_service.analyze_fiscal_situation_stream(
                user_id=request.user_id,
                profile_data=request.profile_data,
                tax_result=request.tax_result,
                user_question=request.user_question,
            ):
                yield f"data: {chunk}\n\n"  # SSE format
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
```

### 6.7 Lifespan Management

```python
# src/main.py (ENHANCED)

from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.dependencies import get_llm_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Async lifespan with LLM client management."""
    # Startup
    llm_client = await get_llm_client()
    logger.info("LLM client initialized")

    yield

    # Shutdown
    await llm_client.close()  # Close HTTP connections ✅
    await db_engine.dispose()  # Close DB connections ✅
    logger.info("Resources released")

app = FastAPI(lifespan=lifespan)
```

### 6.8 Tests Async

```python
# tests/llm/test_llm_service.py

import pytest
from httpx import AsyncClient

@pytest.mark.anyio  # ✅ Anyio pour async tests
async def test_analyze_endpoint():
    """Test LLM analysis endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/llm/analyze",
            json={
                "user_id": "test_user",
                "profile_data": {...},
                "tax_result": {...},
            }
        )

    assert response.status_code == 200
    assert "analysis" in response.json()
```

### 6.9 Corrections à Appliquer

#### ✅ **Correction 6.1** : Créer ClaudeClient async
```bash
# Fichier: src/llm/llm_client.py
# Utiliser AsyncAnthropic avec httpx.AsyncClient
```

#### ✅ **Correction 6.2** : Créer dependencies LLM
```bash
# Fichier: src/api/dependencies.py
# get_llm_client, get_llm_service avec Depends()
```

#### ✅ **Correction 6.3** : Routes LLM async
```bash
# Fichier: src/api/routes/llm_analysis.py
# Endpoints async avec timeout
```

#### ✅ **Correction 6.4** : Lifespan management
```bash
# Mettre à jour src/main.py
# Fermer LLM client au shutdown
```

#### ✅ **Correction 6.5** : Tests async
```bash
# tests/llm/test_llm_service.py
# Utiliser @pytest.mark.anyio
```

### 6.10 Risques Identifiés

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| **Blocage worker FastAPI** | Critique | Faible | 100% async, timeouts |
| **Connection pool épuisé** | Élevé | Moyen | Limits configurés |
| **Memory leak streams** | Moyen | Faible | Context managers |
| **Deadlock DB/LLM** | Moyen | Faible | Separate sessions |

---

## 7. Checklist de Conformité Phase 5

### 7.1 Architecture ✅

- [ ] Interface `LLMClient` abstraite créée
- [ ] Implémentation `ClaudeClient` avec async
- [ ] Service `LLMAnalysisService` métier
- [ ] `ConversationManager` pour sessions
- [ ] `PromptLoader` pour prompts système
- [ ] Exceptions LLM personnalisées
- [ ] Documentation architecture

**Risques bloquants :** Aucun
**Dépendances :** anthropic, httpx, jinja2

### 7.2 API Messages ✅

- [ ] Modèles Pydantic `LLMMessage`, `LLMConversation`
- [ ] Validation stricte rôles (system/user/assistant)
- [ ] Validation séquence messages
- [ ] `MessageNormalizer` pour conversions
- [ ] `ConversationLogger` pour audit
- [ ] Sanitization automatique
- [ ] Tests validation

**Risques bloquants :** Aucun
**Dépendances :** Pydantic (déjà présent)

### 7.3 Conversation Memory ✅

- [ ] Modèles DB `ConversationModel`, `MessageModel`
- [ ] Migration Alembic
- [ ] CRUD conversation
- [ ] Nettoyage automatique (messages, tokens, TTL)
- [ ] Cache RAM optionnel
- [ ] Anonymisation export
- [ ] Background task cleanup
- [ ] Tests CRUD

**Risques bloquants :** Migration DB
**Dépendances :** SQLAlchemy async, cachetools

### 7.4 Contexte Fiscal ✅

- [ ] Validation audit LLM context (94/100 ✅ FAIT)
- [ ] Documentation champs LLM
- [ ] Token counting
- [ ] Priorisation contexte si overflow
- [ ] Tests sérialisation

**Risques bloquants :** Aucun (déjà validé)
**Dépendances :** tiktoken

### 7.5 Prompts Système ✅

- [ ] Structure dossiers `prompts/`
- [ ] Prompts système écrits (base, safety, persona)
- [ ] Few-shot examples
- [ ] Templates Jinja2
- [ ] `PromptLoader` implémenté
- [ ] metadata.json versioning
- [ ] Validation variables résolues
- [ ] Tests chargement

**Risques bloquants :** Qualité prompts (itératif)
**Dépendances :** Jinja2

### 7.6 Async FastAPI ✅

- [ ] `ClaudeClient` 100% async
- [ ] Dependencies injection LLM
- [ ] Routes async avec timeouts
- [ ] Streaming SSE
- [ ] Lifespan management (startup/shutdown)
- [ ] Connection pool configuré
- [ ] Tests async (@pytest.mark.anyio)
- [ ] Monitoring latency

**Risques bloquants :** Aucun (infra déjà async)
**Dépendances :** anthropic, httpx

### 7.7 Configuration ✅

- [ ] `ANTHROPIC_API_KEY` dans settings
- [ ] `LLM_MODEL` configurable
- [ ] Timeouts configurables
- [ ] Token limits configurables
- [ ] Validation .env au démarrage
- [ ] Documentation configuration

**Risques bloquants :** API key manquante
**Dépendances :** pydantic-settings

### 7.8 Tests ✅

- [ ] Tests unitaires `LLMClient` (mock)
- [ ] Tests `LLMAnalysisService`
- [ ] Tests `ConversationManager`
- [ ] Tests `PromptLoader`
- [ ] Tests endpoints LLM
- [ ] Tests streaming
- [ ] Tests error scenarios
- [ ] Coverage >80%

**Risques bloquants :** Aucun
**Dépendances :** pytest-asyncio, httpx (test client)

### 7.9 Monitoring ✅

- [ ] Logging structuré LLM calls
- [ ] Métriques tokens (input/output)
- [ ] Métriques latency
- [ ] Métriques erreurs
- [ ] Dashboard usage
- [ ] Alertes coût API

**Risques bloquants :** Aucun (nice-to-have)
**Dépendances :** prometheus-client (optionnel)

---

## 8. Risques Globaux et Mitigations

### 8.1 Tableau Récapitulatif

| Risque | Impact | Prob. | Phase | Mitigation |
|--------|--------|-------|-------|------------|
| **Coût API non contrôlé** | Critique | Élevé | Runtime | Token counting + quotas + alertes |
| **Latence >10s** | Élevé | Moyen | Runtime | Streaming + timeout + cache |
| **Fuite PII** | Critique | Faible | Dev | Sanitization systématique + tests |
| **Prompts inefficaces** | Moyen | Moyen | Dev | Itération + A/B testing |
| **DB overflow conversations** | Élevé | Élevé | Runtime | TTL + nettoyage auto + monitoring |
| **Blocage workers FastAPI** | Critique | Faible | Runtime | 100% async + timeouts |
| **Migration LLM provider** | Moyen | Faible | Futur | Interface abstraite |
| **Hallucinations fiscales** | Élevé | Moyen | Runtime | Validation réponses + sources |

### 8.2 Plan de Mitigation Détaillé

#### Coût API
```python
class TokenBudgetManager:
    """Limit API costs."""

    async def check_budget(self, user_id: str, estimated_tokens: int) -> bool:
        """Check if user has budget."""
        usage = await self.get_monthly_usage(user_id)
        if usage + estimated_tokens > MONTHLY_LIMIT:
            raise BudgetExceededError()
        return True
```

#### Validation Réponses
```python
class ResponseValidator:
    """Validate LLM responses for accuracy."""

    async def validate_fiscal_response(self, response: str, context: LLMContext) -> bool:
        """Check for hallucinations."""
        # Vérifier cohérence montants
        # Vérifier références lois fiscales
        # Vérifier calculs
        pass
```

---

## 9. Plan d'Implémentation Phase 5

### 9.1 Sprint 1 : Infrastructure (5 jours)

**Tâches :**
1. Créer `src/llm/llm_client.py` (ClaudeClient)
2. Créer `src/llm/exceptions.py`
3. Ajouter dépendances (anthropic, tiktoken, jinja2, cachetools)
4. Créer modèles DB (ConversationModel, MessageModel)
5. Migration Alembic
6. Tests unitaires client

**Livrables :**
- Client LLM fonctionnel
- DB conversations prête

### 9.2 Sprint 2 : Conversation & Prompts (5 jours)

**Tâches :**
1. Créer `ConversationManager`
2. Créer structure `prompts/`
3. Écrire prompts système
4. Créer `PromptLoader`
5. Tests CRUD conversations
6. Tests chargement prompts

**Livrables :**
- Gestion conversations complète
- Prompts système v1.0

### 9.3 Sprint 3 : Service & API (5 jours)

**Tâches :**
1. Créer `LLMAnalysisService`
2. Créer routes API `/api/v1/llm/analyze`
3. Intégration dependencies FastAPI
4. Streaming SSE
5. Lifespan management
6. Tests end-to-end

**Livrables :**
- Service LLM complet
- API fonctionnelle

### 9.4 Sprint 4 : Monitoring & Polish (3 jours)

**Tâches :**
1. Logging structuré
2. Métriques tokens/latency
3. Background task cleanup
4. Documentation API
5. Tests coverage >80%

**Livrables :**
- Monitoring opérationnel
- Documentation complète

**Total : 18 jours de développement**

---

## 10. Conclusion

### 10.1 Synthèse

Le projet ComptabilityProject est **prêt à 80%** pour l'intégration LLM Phase 5 :

**Forces ✅**
- Infrastructure async complète
- Modèles Pydantic validés (score 94/100)
- Sécurité (sanitization robuste)
- Architecture découplée

**À Compléter ⚠️**
- Client API LLM (3 jours)
- Gestion conversations (5 jours)
- Prompts système (3 jours)
- Service métier (5 jours)
- Monitoring (2 jours)

### 10.2 Recommandations Finales

1. **Démarrer par infrastructure** (Sprint 1) : ClaudeClient + DB conversations
2. **Itérer sur prompts** : Commencer simple, améliorer progressivement
3. **Monitorer coûts dès J1** : Token counting + alertes
4. **Tests robustes** : Mock LLM API pour tests rapides
5. **Documentation continue** : Chaque composant documenté

### 10.3 Feu Vert

🟢 **VALIDATION : Le développement Phase 5 peut démarrer**

**Conditions :**
- Appliquer corrections listées dans ce document
- Suivre checklist section 7
- Respecter plan implémentation section 9

**Score de préparation : 8/10**

---

**Document rédigé par :** Claude Code
**Date :** 2025-11-30
**Prochaine revue :** Post-Sprint 2 (validation prompts système)
