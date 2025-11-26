# French Tax Optimization System for Freelancers

A comprehensive system that processes French tax documents, performs accurate tax calculations based on French tax law, detects optimization opportunities, and provides AI-powered conversational assistance through Anthropic Claude.

## Project Overview

This system helps French freelancers optimize their tax situation by:
- **Processing tax documents** (PDF/OCR) - Avis d'imposition, 2042, URSSAF, BNC/BIC, PER, LMNP, etc.
- **Calculating taxes accurately** - IR, quotient familial, social contributions
- **Detecting optimizations** - Regime changes, PER contributions, LMNP investments, Girardin, FCPI/FIP, company structure changes
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

### Phase 3: Tax Calculation Engine

**Status:** Planned
**Goal:** Accurate French tax calculations

**Tasks:**
- Income tax calculator with tranches (2024/2025 baremes)
- Quotient familial calculation
- Social contributions calculator
- Regime comparison (micro vs reel)
- Tax deductions and reductions
- Calculation API endpoints

### Phase 4: Optimization Detection

**Status:** Planned
**Goal:** Identify tax optimization opportunities

**Tasks:**
- Regime optimization strategies (micro vs reel)
- PER contribution recommendations
- LMNP opportunity detection
- FCPI/FIP/Girardin analysis
- Company structure recommendations
- Recommendations API

### Phase 5: LLM Integration (Claude)

**Status:** Planned
**Goal:** AI-powered conversational assistance

**Tasks:**
- Anthropic Claude API integration
- Context building from user data
- Conversation management
- Chat API endpoint
- System prompts for French tax domain

### Phase 6: Integration & Polish

**Status:** Planned
**Goal:** Complete system integration and production readiness

**Tasks:**
- End-to-end workflows
- Error handling and validation
- Performance optimization
- Security hardening
- Documentation
- Deployment preparation

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

**Phase 2 is complete!** The document extraction pipeline is fully implemented with:
- PDF and OCR text extraction working end-to-end
- 4 specialized parsers for French tax documents (Avis d'Imposition, 2042, URSSAF, BNC/BIC)
- Document upload API with file storage management
- Graceful error handling and comprehensive testing
- 42 tests passing with 74% coverage
- All CI/CD checks passing

**Previous milestones:**
- ✅ Phase 1: Core infrastructure (FastAPI, SQLAlchemy, Alembic, repositories, tests, CI/CD)
- ✅ Phase 2: Document extraction pipeline (PDF/OCR extraction, field parsers, upload API)

**Next up: Phase 3** - Tax calculation engine with French baremes, quotient familial, and social contributions.

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
