# French Tax Optimization System for Freelancers

A comprehensive system that processes French tax documents, performs accurate tax calculations based on French tax law, detects optimization opportunities, and provides AI-powered conversational assistance through Anthropic Claude.

## Project Overview

This system helps French freelancers optimize their tax situation by:
- **Processing tax documents** (PDF/OCR) - Avis d'imposition, 2042, URSSAF, BNC/BIC, PER, LMNP, etc.
- **Calculating taxes accurately** - IR, quotient familial, social contributions
- **Detecting optimizations** - 7 strategies: Regime changes, PER, LMNP, Girardin (via Profina), FCPI/FIP, Deductions, Company structure + BONUS: 30-second quick simulation
- **AI assistance** - Conversational interface powered by Claude for tax questions and guidance
- **REST API** - Complete API for integration with other systems

## Tech Stack

- **Python 3.12** - Latest Python with modern async support
- **UV** - Fast Python package manager
- **FastAPI** - Modern async web framework for REST API
- **SQLAlchemy 2.0** - Async ORM with SQLite database
- **Alembic** - Database migrations
- **Pydantic v2** - Data validation and settings management
- **Anthropic Claude** - LLM for conversational AI (Phase 5)
- **pypdf + pytesseract** - Document processing (Phase 2)
- **pytest** - Testing framework with async support

## Implementation Plan

The project is implemented in 6 phases:

### Phase 1: Core Infrastructure - COMPLETE ✅

**Status:** Complete and merged
**Goal:** Establish project foundation

**Completed:**
- FastAPI application with async support
- SQLAlchemy 2.0 with async SQLite
- Alembic migrations setup
- Database models (FreelanceProfile, TaxDocument, TaxCalculation, Recommendation)
- Pydantic domain models with validation
- Repository pattern for data access
- Configuration management with pydantic-settings
- Health check endpoints
- Comprehensive test suite (12 tests, 88% coverage)
- CI/CD pipeline (GitHub Actions with Ruff formatting, linting, pytest)

**Key Files:**
- `src/main.py` - FastAPI application entry point
- `src/config.py` - Environment configuration
- `src/database/base.py` - SQLAlchemy base with timestamp fields
- `src/database/models/` - ORM models for all entities
- `src/models/` - Pydantic domain models
- `src/database/repositories/` - Data access layer
- `alembic/versions/` - Database migration scripts

### Phase 2: Document Extraction Pipeline - COMPLETE ✅

**Status:** Complete and ready for review
**Goal:** Extract data from French tax documents

**Completed:**
- PDF text extraction using pypdf
- OCR extraction using pytesseract + pdf2image for scanned documents
- Field parsers for 4 document types:
  - Avis d'Imposition (tax assessment) - extracts RFR, impôt, nombre de parts, taux de prélèvement
  - Declaration 2042 (income tax return) - extracts salaries, pensions, revenus fonciers
  - URSSAF (social contributions) - extracts chiffre d'affaires, cotisations sociales
  - BNC/BIC (profit declarations) - extracts recettes, charges, bénéfice with regime detection
- Document upload API endpoint with multipart/form-data support
- File storage service with organized directory structure (by year-month)
- Document processing service orchestrating extraction and parsing
- Graceful error handling (text extraction succeeds even if parsing fails)
- Comprehensive test suite (42 tests, 74% coverage)

**Key Files:**
- `src/extractors/pdf_extractor.py` - PDF text extraction
- `src/extractors/ocr_extractor.py` - OCR for scanned documents
- `src/extractors/field_parsers/` - Document-specific parsers
- `src/services/file_storage.py` - File management
- `src/services/document_service.py` - Document processing orchestration
- `src/api/routes/documents.py` - Upload and retrieval endpoints

### Phase 3: Tax Calculation Engine - COMPLETE ✅

**Status:** Complete and merged
**Goal:** Accurate French tax calculations

**Completed:**
- Income tax calculator with progressive brackets (2024/2025 barèmes)
- Quotient familial calculation with French tax rules
- URSSAF social contributions calculator (BNC 21.8%, BIC 12.8%)
- Regime comparison engine (micro vs réel with recommendations)
- Micro regime abattements (BNC 34%, BIC prestations 50%, BIC ventes 71%)
- PER deduction support with plafond structure
- PAS (Prélèvement à la Source) reconciliation
- Warning system for thresholds and compliance issues
- Tax calculation API endpoints with type-safe Pydantic models
- Comprehensive test suite (26 tests, 78% coverage)
- Official sources documented (impots.gouv.fr, URSSAF)

**Key Files:**
- `src/tax_engine/calculator.py` - Main orchestration layer
- `src/tax_engine/core.py` - Core tax calculation functions
- `src/tax_engine/rules.py` - Versioned tax rules loader
- `src/tax_engine/data/baremes_2024.json` - 2024 tax rules
- `src/tax_engine/data/baremes_2025.json` - 2025 tax rules
- `src/api/routes/tax.py` - Tax calculation API endpoints
- `docs/sources.md` - Official reference documentation

### Phase 4: Tax Optimization Engine - COMPLETE ✅

**Status:** Complete and ready for review
**Goal:** Identify tax optimization opportunities

**Completed:**
- 7 comprehensive optimization strategies with ranked recommendations
- **Regime optimization** - Micro vs Réel comparison with threshold warnings
- **PER (Plan Épargne Retraite)** - Optimal contribution calculator with TMI estimation
- **LMNP (Location Meublée Non Professionnelle)** - Investment opportunity detection
- **Girardin Industriel** - 110% tax reduction via Profina (recommended operator)
- **FCPI/FIP** - Innovation investment funds with 18% reduction
- **Simple deductions** - Dons (66%), Services à la personne (50%), Frais de garde (50%)
- **Company structure** - SASU/EURL IS and Holding recommendations
- JSON-based rule system for maintainability and versioning
- Optimization orchestrator with impact-based ranking
- Complete API endpoints (/run, /strategies, /quick-simulation)
- **BONUS: Quick simulation** - Viral 30-second micro vs réel simulation for landing pages
- Comprehensive test suite (58 tests, 90-100% coverage on all modules)
- Official sources referenced (impots.gouv.fr, service-public.fr, Profina)

**Key Files:**
- `src/analyzers/optimizer.py` - Main optimization orchestrator
- `src/analyzers/strategies/` - 7 strategy modules (regime, per, lmnp, girardin, fcpi_fip, deductions, structure)
- `src/analyzers/rules/` - JSON rule files with versioned tax rules
- `src/models/optimization.py` - Pydantic models for recommendations
- `src/api/routes/optimization.py` - API endpoints including quick simulation
- `docs/phase4.md` - Complete architecture documentation
- `docs/LANDING_PAGE_FEATURE.md` - BONUS feature marketing strategy

### Phase 5: LLM Integration (Claude) - COMPLETE ✅

**Status:** Complete and ready for review
**Goal:** AI-powered conversational tax assistance

**Completed:**
- **Anthropic Claude 3.5 Sonnet integration** - Full async client with streaming support
- **Abstract LLM interface** - Multi-provider support (Claude, GPT, Mistral ready)
- **Conversation management** - Database storage with automatic cleanup (100 msg limit, 100k token limit, 30-day TTL)
- **System prompts** - French tax expert persona with safety guidelines and few-shot examples
- **Fiscal context builder** - LLMContext with complete tax calculation summary
- **Prompt loader** - File-based prompts with Jinja2 templating and caching
- **Token counting** - tiktoken integration for context management
- **Security** - PII sanitization + prompt injection prevention (existing sanitizer)
- **API endpoints** - `/api/v1/llm/analyze` (standard) + `/api/v1/llm/analyze/stream` (SSE streaming)
- **Conversation API** - GET/DELETE conversation endpoints with message history
- **Error handling** - Dedicated LLM exceptions (timeout, rate limit, API errors)
- **Database models** - ConversationModel + MessageModel with relationships
- **Complete test coverage** - All components tested and CI passing

**Key Files:**
- `src/llm/llm_client.py` - Abstract LLMClient + ClaudeClient implementation
- `src/llm/llm_service.py` - High-level LLMAnalysisService orchestration
- `src/llm/conversation_manager.py` - Conversation CRUD + automatic cleanup
- `src/llm/prompt_loader.py` - File-based prompt management with caching
- `src/llm/context_builder.py` - Fiscal context builder (existing, enhanced)
- `src/llm/exceptions.py` - LLM-specific exceptions
- `src/database/models/conversation.py` - ORM models for conversations + messages
- `src/models/llm_message.py` - Pydantic models (LLMMessage, LLMConversation, AnalysisRequest/Response)
- `src/api/routes/llm_analysis.py` - LLM analysis API endpoints
- `prompts/` - System prompts, examples, templates

### Phase 6: Integration & Polish - IN PROGRESS

**Status:** In Progress
**Goal:** Complete system integration and production readiness

**Completed:**
- Next.js 14 frontend with React 18 and TypeScript
- 6 interactive pages: Home, Dashboard, Simulator, Optimizations, Chat
- API client library with full TypeScript types
- UI components with Radix UI + Tailwind CSS
- Recharts integration for data visualization
- CORS configuration for frontend-backend communication
- ThreadPoolExecutor for non-blocking OCR/PDF processing
- Global error handlers in FastAPI
- End-to-end integration tests
- **CEHR/CDHR Tax Fixes** (January 2025):
  - CEHR now uses RFR (Revenu Fiscal de Référence) instead of revenu_imposable
  - Added `situation_familiale` parameter for couple/célibataire detection
  - Implemented CDHR (Contribution Différentielle 2025) - 20% minimum effective rate
  - Synchronized frontend tax brackets to 2025 values
- **Security Improvements**:
  - Fixed XSS vulnerability (removed dangerouslySetInnerHTML)
  - Switched from localStorage to sessionStorage for sensitive data
  - Added TypeScript interfaces for rfr, cdhr, cdhr_detail, situation_familiale
- **Legal Compliance**:
  - Added LegalDisclaimerBanner, HighNetWorthWarning, InvestmentRiskWarning components
  - ORIAS/AMF/OEC disclosure in footer
- **CI/CD**:
  - Added frontend build and lint job to GitHub Actions
- **Documentation**:
  - BMAD governance framework
  - Manual testing guides in `audits/` directory
- **Compliance (TD004)**:
  - Audit trail system for tax calculations (5-year retention)
  - AuditLog/AuditEntry models tracking all calculation steps
  - REST API for audit trail retrieval and export
  - Input hash verification for data integrity
- **Barème Verification (TD001)**:
  - Verification metadata in barème JSON files (verified_date, sources, checklist)
  - Automated verification script (`scripts/verify_baremes.py`)
  - CI-ready strict mode for freshness checks
- **Glossary (TD005)**:
  - Interactive glossary page with 30+ French tax terms
  - Search and category filtering
  - Related terms and examples

**In Progress:**
- Frontend-backend integration testing
- Performance optimization
- Final documentation

**Key Files:**
- `frontend/app/` - Next.js pages (home, dashboard, simulator, optimizations, chat)
- `frontend/components/ui/` - Reusable UI components (button, card, input, select, alert)
- `frontend/components/legal-disclaimer.tsx` - Legal compliance components
- `frontend/lib/api.ts` - TypeScript API client
- `frontend/.env.example` - Environment configuration template
- `audits/` - Regulatory audit reports with manual testing guides
- `src/audit/` - Audit trail service (AuditLogger, compliance tracking)
- `src/api/routes/audit.py` - Audit API endpoints
- `frontend/app/glossary/` - Interactive tax terms glossary
- `scripts/verify_baremes.py` - Barème verification script

## Project Structure

```
ComptabilityProject/
├── src/
│   ├── config.py                     # Configuration management
│   ├── main.py                       # FastAPI application entry
│   │
│   ├── api/                          # REST API layer (Future)
│   │   ├── dependencies.py
│   │   └── routes/
│   │
│   ├── models/                       # Pydantic domain models
│   │   ├── tax_document.py
│   │   ├── freelance_profile.py
│   │   ├── tax_calculation.py
│   │   └── recommendation.py
│   │
│   ├── database/                     # Database layer
│   │   ├── base.py                   # SQLAlchemy base config
│   │   ├── session.py                # Session management
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   └── repositories/             # Data access layer
│   │
│   ├── extractors/                   # Document extraction (Phase 2)
│   ├── tax_engine/                   # Tax calculations (Phase 3)
│   ├── analyzers/                    # Optimization detection (Phase 4)
│   └── llm/                          # Claude integration (Phase 5)
│
├── alembic/                          # Database migrations
│   ├── versions/
│   └── env.py
│
├── tests/                            # Test suite
│   ├── conftest.py
│   ├── test_api_health.py
│   └── test_database.py
│
├── data/                             # Data directory (gitignored)
│   └── database/
│
├── .github/workflows/                # CI/CD
│   └── ci.yml
│
├── pyproject.toml                    # Dependencies and project config
├── alembic.ini                       # Alembic configuration
└── README.md                         # This file
```

## Getting Started

### Prerequisites

- Python 3.12+
- UV package manager ([installation guide](https://github.com/astral-sh/uv))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/T-Ratnosaure/ComptabilityProject.git
cd ComptabilityProject
```

2. Install dependencies:
```bash
uv sync
```

3. Run database migrations:
```bash
uv run alembic upgrade head
```

### Running the Application

Start the FastAPI development server:
```bash
uv run uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Running Tests

```bash
# Run all tests with coverage
uv run pytest -v --cov --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_database.py -v

# Run with verbose output
uv run pytest -vv
```

### Code Quality

```bash
# Format code with Ruff
uv run ruff format .

# Lint code
uv run ruff check .

# Fix linting issues automatically
uv run ruff check . --fix
```

## Development

### Adding Dependencies

```bash
# Add runtime dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>
```

### Database Migrations

```bash
# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1
```

### Git Workflow

1. Create feature branch: `git checkout -b feat/your-feature`
2. Make changes and commit: `git commit -m "feat: description"`
3. Push and create PR: `git push origin feat/your-feature`
4. Ensure CI passes before merging

See `CLAUDE.md` for complete development guidelines.

## Current Status

**Phase 6 is in progress!** Integration & Polish for production readiness.

### Recent Updates (January 2025)
- ✅ **CEHR/CDHR Tax Fixes** - Critical tax calculation corrections for high-income users
- ✅ **CDHR Implementation** - New 2025 contribution ensuring 20% minimum effective rate
- ✅ **Security Hardening** - XSS fix, sessionStorage for sensitive data
- ✅ **Legal Compliance** - Disclaimer components and regulatory warnings
- ✅ **Frontend CI/CD** - Automated build and lint checks

### Current Focus
- ✨ End-to-end workflow testing (Document → Tax → Optimization → LLM)
- 🧪 Integration test suite development
- 📝 Demo script creation
- 🔍 Production readiness assessment

### Completed Phases

**✅ Phase 5: LLM Integration** (Merged 2025-11-30)
- Claude 3.5 Sonnet integration with async client
- Multi-provider LLM interface (ready for GPT, Mistral)
- Conversation management with database storage + automatic cleanup
- French tax expert system prompts with few-shot examples
- Complete fiscal context building from tax calculations
- File-based prompt management with Jinja2 templating
- Token counting and context window management (tiktoken)
- Security: PII sanitization + prompt injection prevention
- REST API endpoints: `/analyze` (standard) + `/analyze/stream` (SSE)
- Conversation history API (GET/DELETE)
- Error handling with LLM-specific exceptions (timeout, rate limit, API errors)
- All CI/CD checks passing ✅

**Previous milestones:**
- ✅ Phase 1: Core infrastructure (FastAPI, SQLAlchemy, Alembic, repositories, tests, CI/CD)
- ✅ Phase 2: Document extraction pipeline (PDF/OCR extraction, field parsers, upload API)
- ✅ Phase 3: Tax calculation engine (IR, quotient familial, social contributions, regime comparison)
- ✅ Phase 4: Tax optimization engine (7 strategies, personalized recommendations, Profina integration)

## Contributing

Please follow the guidelines in `CLAUDE.md` for:
- Code style and formatting
- Testing requirements
- Git workflow
- Documentation standards

## License

[To be determined]

## Contact

[To be determined]
