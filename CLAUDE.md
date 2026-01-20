# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
GO THROUGH THIS FILE WITH SERIOUS. RESPECT IT ALL EVERY TIME.

## Project Overview

ComptabilityProject is a Python 3.12 application managed with UV (fast Python package manager). This project implements a French Tax Optimization System for freelancers.

## CRITICAL: Implementation Plan

**ALWAYS follow the implementation plan saved in `C:/Users/larai/.claude/plans/crispy-cooking-glade.md`**

- The plan defines 6 phases of implementation with clear structure and requirements
- **Phase 1 (Core Infrastructure)** is COMPLETE ✅
- Before starting any new feature, review the plan to understand the current phase
- Follow the phase order and implementation steps exactly as defined
- Do not deviate from the planned architecture without explicit user approval
- The plan is the source of truth for project structure, dependencies, and implementation approach

When exiting plan mode to begin implementation:
1. Ensure the plan is saved in `~/.claude/plans/` (already done)
2. Review the current phase requirements
3. Follow the implementation steps in order
4. Mark phase completion when all success criteria are met

## Development Commands

### Package Management
- Install dependencies: `uv sync`
- Add a new dependency: `uv add <package-name>`
- Add a dev dependency: `uv add --dev <package-name>`
- FORBIDDEN: `uv pip install`, `@latest` syntax
- ONLY use uv, NEVER pip

### Running the Application
- Run main script: `python main.py`
- Or with UV: `uv run python main.py`

## Project Structure

- `main.py` - Application entry point with basic setup
- `pyproject.toml` - Project configuration and dependencies
- `.python-version` - Python version (3.12)

## Core Development Rules

### Code Quality

- Type hints required for all code
- use pyrefly for type checking
  - run 'pyrefly init' to start
  - run 'pyrefly check' after every change and fix resultings errors
- Public APIs must have docstrings
- Functions must be focused and small
- Follow existing patterns exactly
- Line length: 88 chars maximum

### Testing Requirements
   - Framework: `uv run pytest`
   - Async testing: use anyio, not asyncio
   - Coverage: test edge cases and errors
   - New features require tests
   - Bug fixes require regression tests

### Code Style
    - PEP 8 naming (snake_case for functions/variables)
    - Class names in PascalCase
    - Constants in UPPER_SNAKE_CASE
    - Document with docstrings
    - Use f-strings for formatting

## Development Philosophy

- **Simplicity**: Write simple, straightforward code
- **Readability**: Make code easy to understand
- **Performance**: Consider performance without sacrificing readability
- **Maintainability**: Write code that's easy to update
- **Testability**: Ensure code is testable
- **Reusability**: Create reusable components and functions
- **Less Code = Less Debt**: Minimize code footprint

## Coding Best Practices

- **Early Returns**: Use to avoid nested conditions
- **Descriptive Names**: Use clear variable/function names (prefix handlers with "handle")
- **Constants Over Functions**: Use constants where possible
- **DRY Code**: Don't repeat yourself
- **Functional Style**: Prefer functional, immutable approaches when not verbose
- **Minimal Changes**: Only modify code related to the task at hand
- **Function Ordering**: Define composing functions before their components
- **TODO Comments**: Mark issues in existing code with "TODO:" prefix
- **Simplicity**: Prioritize simplicity and readability over clever solutions
- **Build Iteratively** Start with minimal functionality and verify it works before adding complexity
- **Run Tests**: Test your code frequently with realistic inputs and validate outputs
- **Build Test Environments**: Create testing environments for components that are difficult to validate directly
- **Functional Code**: Use functional and stateless approaches where they improve clarity
- **Clean logic**: Keep core logic clean and push implementation details to the edges
- **File Organsiation**: Balance file organization with simplicity - use an appropriate number of files for the project scale

## System Architecture

- use pydantic and langchain

## Documentation

### README.md
- **ALWAYS update the README.md** when completing a phase or adding major functionality
- Keep it synchronized with the current state of the project
- Include:
  - Project overview and goals
  - Implementation plan summary (phase progress)
  - Completed features and accomplishments
  - Setup instructions
  - Tech stack and dependencies
  - Usage examples (when applicable)

## Pull Requests

- Create a detailed message of what changed. Focus on the high level description of
  the problem it tries to solve, and how it is solved. Don't go into the specifics of the
  code unless it adds clarity.

## Git Workflow

- Always pull when comming back to the code
- Always use feature branches; do not commit directly to `main`
  - Name branches descriptively: `fix/XXX`, `feat/XXXX`, `chore/ruff-fixes`
  - Keep one logical change per branch to simplify review and rollback
- Create pull requests for all changes
  - Open a draft PR early for visibility; convert to ready when complete
  - Ensure tests pass locally before marking ready for review
  - Use PRs to trigger CI/CD and enable async reviews
- Link issues
  - Before starting, reference an existing issue or create one
  - Use commit/PR messages like `Fixes #123` for auto-linking and closure
- Commit practices
  - Make atomic commits (one logical change per commit)
  - Prefer conventional commit style: `type(scope): short description`
    - Examples: `feat(eval): group OBS logs per test`, `fix(cli): handle missing API key`
  - Squash only when merging to `main`; keep granular history on the feature branch
- Practical workflow
  1. Create or reference an issue
  2. `git checkout -b feat/issue-123-description`
  3. Commit in small, logical increments
  4. `git push` and open a draft PR early
  5. Convert to ready PR when functionally complete and tests pass
  6. Merge after reviews and checks pass

## Python Tools

- use context7 mcp to check details of libraries

## Code Formatting

1. Ruff
   - Format: `uv run ruff format .`
   - Check: `uv run ruff check .`
   - Fix: `uv run ruff check . --fix`
   - Critical issues:
     - Line length (88 chars)
     - Import sorting (I001)
     - Unused imports
   - Line wrapping:
     - Strings: use parentheses
     - Function calls: multi-line with proper indent
     - Imports: split into multiple lines

2. Type Checking
  - run `pyrefly init` to start
  - run `pyrefly check` after every change and fix resultings errors
   - Requirements:
     - Explicit None checks for Optional
     - Type narrowing for strings
     - Version warnings can be ignored if checks pass


## Error Resolution

1. CI Failures
   - Fix order:
     1. Formatting
     2. Type errors
     3. Linting
   - Type errors:
     - Get full line context
     - Check Optional types
     - Add type narrowing
     - Verify function signatures

2. Common Issues
   - Line length:
     - Break strings with parentheses
     - Multi-line function calls
     - Split imports
   - Types:
     - Add None checks
     - Narrow string types
     - Match existing patterns

3. Best Practices
   - Check git status before commits
   - Run formatters before type checks
   - Keep changes minimal
   - Follow existing patterns
   - Document public APIs
   - Test thoroughly

---

## MANDATORY WORKFLOW: BMAD + AGENTIC

> **BMAD is a behavior, not a structure.**
> Every user request goes through Yoni, who determines the appropriate workflow.

### ⚠️ Regulatory-First Interpretation of Global Workflows

**This is a TAX COMPLIANCE project, not a trading or ML experimentation platform.**

Global workflows from WORKFLOW_RULES.md must be interpreted through a regulatory lens:

| Workflow/Trigger | Global Intent | **ComptabilityProject Interpretation** |
|------------------|---------------|----------------------------------------|
| RESEARCH | Algorithm exploration | **Tax rule interpretation, legal ambiguity resolution, accounting semantics** |
| OPTIMIZATION | Performance maximization | **Risk reduction, clarity, explainability, conservative compliance** |
| algorithm_unclear | ML model selection | **Tax calculation method uncertainty, regulatory interpretation** |
| performance_risk | Latency/throughput | **Audit trail integrity, calculation accuracy, source verification** |

**Key Principle:** Presence of ML agents (alexios, pierre-jean) ≠ encouragement to use ML.

- Deterministic logic is **PREFERRED** unless ML is explicitly justified
- "Optimization" means **reducing regulatory risk**, not maximizing tax savings
- "Research" means **understanding official sources**, not experimenting with models

> **If in doubt:** Choose the simpler, more auditable, more conservative approach.

---

### 1. ALWAYS CALL YONI FIRST

**FOR EVERY USER REQUEST**, you MUST call `yoni-orchestrator` via the Task tool.

- Yoni coordinates all specialized agents
- Yoni selects the appropriate BMAD workflow
- **NEVER** try to handle complex tasks yourself
- **This is the MOST IMPORTANT rule**

### 2. ALWAYS CALL WEALON LAST

**AT THE END OF EVERY TASK**, you MUST call `wealon-regulatory-auditor`.

- Wealon audits all work before completion
- Wealon catches shortcuts and workarounds
- **No task is complete until Wealon has reviewed it**

### Mandatory Workflow Pattern

```
USER REQUEST
     ↓
┌────────────────────────────────────┐
│  1. YONI (Entry)                   │
│     - Detect triggers              │
│     - Select BMAD workflow         │
│     - Coordinate agents            │
└────────────────────────────────────┘
     ↓
┌────────────────────────────────────┐
│  2. PLANNING + EXECUTION           │
│     - BMAD workflow artifacts      │
│     - Agent delegation             │
│     - Implementation               │
└────────────────────────────────────┘
     ↓
┌────────────────────────────────────┐
│  3. WEALON (Exit)                  │
│     - Audit all changes            │
│     - Review for shortcuts         │
│     - Verify completeness          │
│     - Flag issues                  │
└────────────────────────────────────┘
     ↓
TASK COMPLETE (only after Wealon approval)
```

### 3. Yoni Decision Transparency

When dispatching, Yoni SHOULD log:

```
YONI ROUTING:
├── Request: "{brief summary}"
├── Triggers: [trigger1: YES, trigger2: NO, ...]
├── Workflow: [WORKFLOW_NAME]
├── Agents: [agent list]
└── Rationale: [why this workflow]
```

---

## Agent Governance

**Full governance:** `docs/agents/AGENTS.md`
**Aligned with:** Global WORKFLOW_RULES.md v2.0

### Global Primary Agents (9 — Always Active)

| Agent | Specialty | When to Call |
|-------|-----------|--------------|
| yoni-orchestrator | Coordination | **EVERY request** - FIRST (ENTRY GATE) |
| wealon-regulatory-auditor | Audit | **EVERY task** - LAST (EXIT GATE) |
| it-core-clovis | Structural Quality | Git, PR, architecture review |
| quality-control-enforcer | Implementation Quality | After code changes |
| lamine-deployment-expert | CI/CD & TDD | Pipelines, testing, deployment |
| alexios-ml-predictor | ML/Algorithms | Algorithm decisions, complexity |
| cybersecurity-expert-maxime | Security Design | Auth, crypto, input handling |
| nicolas-risk-manager | Risk Management | Risk assessment concepts |
| pierre-jean-ml-advisor | ML Guidance | ML theory, guidance |

### Project-Specific Primary Agents (2 — ComptabilityProject Only)

| Agent | Specialty | When to Call |
|-------|-----------|--------------|
| french-tax-optimizer | French Tax Law | Tax rule changes (ADVISORY ONLY) |
| legal-compliance-reviewer | Regulatory Compliance | Tax/investment changes |

**Total Primary Agents: 11** (9 global + 2 project-specific)

### Conditional Agents

| Agent | Specialty | Condition |
|-------|-----------|-----------|
| antoine-nlp-expert | NLP/LLM | Prompt changes |
| data-engineer-sophie | Data pipelines | Extraction changes |
| legal-team-lead | Legal Management | Cross-domain legal questions |

### Rejected Agents (NEVER USE)

- research-remy-stocks — Wrong domain (equities ≠ tax)
- iacopo-macro-futures-analyst — Wrong domain (macro ≠ tax)
- backtester-agent, trading-execution-engine, helena-execution-manager — No trading
- portfolio-manager-jean-yves, pnl-validator, victor-pnl-manager — Investment ≠ tax
- gabriel-task-orchestrator, jacques-head-manager, jean-david-it-core-manager — Single developer
- cost-optimizer-lucas — Premature optimization
- ml-production-engineer — No ML models in production

---

## BMAD + AGENTIC Planning Framework

### Activation

Planning Mode activates when:
1. User says **"use BMAD+AGENTIC workflow"**
2. Yoni detects complexity triggers (automatic)

### Complexity Triggers

| Trigger | Condition | Workflow |
|---------|-----------|----------|
| `new_feature` | Any new capability | FULL_PLANNING |
| `tax_rule_change` | Changes to tax_engine or analyzers | TAX_REVIEW |
| `llm_prompt_change` | Changes to prompts or LLM code | LLM_REVIEW |
| `file_impact` | >= 2 files changed | FULL_PLANNING |
| `domain_crossing` | >= 2 domains touched | INTEGRATION |
| `infrastructure` | CI/CD or config changes | ADR |
| `algorithm_unclear` | Uncertainty > 0.5 on algorithm | RESEARCH |
| `performance_risk` | Performance-critical code | OPTIMIZATION |
| `security_sensitive` | Auth/crypto/input handling | SECURITY_REVIEW |
| `simple_change` | Single file, low risk | SKIP |

### Workflow Definitions

**FULL_PLANNING**
```
ANALYZE → SCOPE → ARCHITECT → DECOMPOSE
Artifacts: prd-lite.md, architecture.md, task-breakdown.yaml
```

**TAX_REVIEW**
```
ANALYZE → TAX_VALIDATION → LEGAL_COMPLIANCE → IMPLEMENT → VERIFY → AUDIT
Human checkpoint required before implementation
```

**LLM_REVIEW**
```
ANALYZE → NLP_REVIEW → SECURITY_CHECK → LEGAL_COMPLIANCE → IMPLEMENT → AUDIT
Human checkpoint required before implementation
```

**RESEARCH**
```
PROBLEM_DEFINITION → LITERATURE_REVIEW → PROTOTYPE_PLAN
Artifacts: research-brief.md, approach-options.md
Agents: alexios-ml-predictor, pierre-jean-ml-advisor
```

**OPTIMIZATION**
```
PROFILE → BENCHMARK → STRATEGY
Artifacts: performance-analysis.md, optimization-plan.md
Agents: alexios-ml-predictor, it-core-clovis
```

**ADR**
```
CONTEXT → OPTIONS → DECISION → CONSEQUENCES
Artifact: docs/adr/{number}-{title}.md
Agents: lamine-deployment-expert, it-core-clovis
```

### Artifact Output Locations

| Artifact Type | Location |
|---------------|----------|
| PRD-lite | `docs/planning/prd-lite/{date}-{feature}.md` |
| Architecture | `docs/planning/architecture/{date}-{feature}.md` |
| Task Breakdown | `docs/planning/task-breakdowns/{date}-{feature}.yaml` |
| Audit Reports | `audits/audit-{date}-{topic}.md` |

### Key References

- **Agent Governance:** `docs/agents/AGENTS.md`
- **Workflow Config:** `_bmad/config.yaml`
- **Workflow Details:** `_bmad/workflows.md`
- **Templates:** `_bmad/templates/`
- **Project Context:** `docs/project-context.md`

---

## Tax Domain Special Rules

### Human Approval Required For

1. Any change to `src/tax_engine/**`
2. Any change to `src/analyzers/**`
3. Any change to `src/tax_engine/data/*.json` (barèmes)
4. Any change to investment recommendations
5. Any change to LLM system prompts affecting advice scope

### Source Citation Required For

1. Tax rule changes
2. Barème updates
3. URSSAF rate changes
4. New optimization strategies

### Verification Checklist

Before committing tax changes:
- [ ] Official source cited (impots.gouv.fr, BOI, etc.)
- [ ] Calculation verified against source
- [ ] `verified_date` updated in JSON files
- [ ] Tests added/updated
- [ ] Human approval obtained

---

## Anti-Patterns (NEVER DO)

### Agent Anti-Patterns
1. **NEVER** skip calling Yoni for user requests
2. **NEVER** skip calling Wealon at task completion
3. **NEVER** create PRs without review agents
4. **NEVER** use rejected agents
5. **NEVER** bypass BMAD workflows for complex tasks
6. **NEVER** mark a task complete without Wealon audit

### Tax Domain Anti-Patterns
1. **NEVER** change tax rules without source citation
2. **NEVER** provide prescriptive advice ("you should do X")
3. **NEVER** skip human approval for tax changes
4. **NEVER** update barèmes without verification
5. **NEVER** remove or weaken disclaimers

---

## Example Planning Flow

```
User: "Add support for ISF calculation"

┌─────────────────────────────────────────────────────┐
│ ENTRY: YONI                                         │
├─────────────────────────────────────────────────────┤
│ Yoni detects:                                       │
│ ├── new_feature: true (ISF support)                 │
│ ├── tax_rule_change: true (new tax calculation)     │
│ ├── domains: [tax_engine, analyzers]                │
│ └── estimated_files: 3+                             │
│                                                     │
│ Triggers:                                           │
│ ├── TAX_REVIEW (tax rule change)                    │
│ └── FULL_PLANNING (new feature)                     │
│                                                     │
│ Selected: TAX_REVIEW + FULL_PLANNING (combined)     │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ PLANNING + EXECUTION                                │
├─────────────────────────────────────────────────────┤
│ TAX_REVIEW:                                         │
│ ├── french-tax-optimizer: ISF rules interpretation  │
│ ├── legal-compliance: Regulatory check              │
│ └── HUMAN CHECKPOINT: Approve interpretation        │
│                                                     │
│ FULL_PLANNING:                                      │
│ ├── PRD-lite created                                │
│ ├── Architecture designed                           │
│ └── Tasks decomposed                                │
│                                                     │
│ Implementation:                                     │
│ └── Code changes with tests                         │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ EXIT: WEALON                                        │
├─────────────────────────────────────────────────────┤
│ Wealon audits:                                      │
│ ├── Tax source citations present                    │
│ ├── Human approval obtained                         │
│ ├── Tests adequate                                  │
│ ├── No shortcuts taken                              │
│ └── Compliance check passed                         │
│                                                     │
│ Result:                                             │
│ ├── APPROVED → Task complete                        │
│ └── ISSUES → Fix and re-audit                       │
└─────────────────────────────────────────────────────┘
```

---

**Remember:**
- **ALWAYS call yoni-orchestrator FIRST**
- **ALWAYS call wealon-regulatory-auditor LAST**
- **BMAD workflows ensure proper planning and execution**
- **Tax changes require human approval and source citation**