# Planning Templates — ComptabilityProject

**Version:** 1.0
**Created:** 2026-01-20

---

## Available Templates

| Template | Location | Purpose |
|----------|----------|---------|
| PRD-Lite | `_bmad/templates/prd-lite.md` | Product requirements document |
| Architecture | `_bmad/templates/architecture.md` | Technical architecture design |
| Task Breakdown | `_bmad/templates/task-breakdown.yaml` | Task decomposition |

---

## Template Usage

### When to Use PRD-Lite

Use for:
- New features
- Significant enhancements
- Any work touching ≥2 files

Output location: `docs/planning/prd-lite/{date}-{feature}.md`

### When to Use Architecture

Use for:
- New components
- Significant refactoring
- Cross-domain changes

Output location: `docs/planning/architecture/{date}-{feature}.md`

### When to Use Task Breakdown

Use for:
- Any planned feature
- Multi-step implementations
- Work requiring multiple agents

Output location: `docs/planning/task-breakdowns/{date}-{feature}.yaml`

---

## Tax Domain Extensions

All templates include tax-specific sections:

- **Tax Rules Affected:** Checklist of tax areas impacted
- **Source Verification:** Requirements for official source citation
- **Human Approval:** Flags for when human sign-off is required

---

## Workflow Integration

Templates are created during BMAD workflows:

| Workflow | Templates Created |
|----------|------------------|
| FULL_PLANNING | PRD-Lite, Architecture, Task Breakdown |
| INTEGRATION | Architecture, Task Breakdown |
| TAX_REVIEW | PRD-Lite (for tax rule changes) |
| LLM_REVIEW | PRD-Lite (for prompt changes) |
| SKIP | None |

---

## File Naming Convention

```
{date}-{feature-name}.{ext}

Examples:
- 2026-01-20-user-authentication.md
- 2026-01-20-tax-engine-update.yaml
```

---

## Required Sections

### PRD-Lite (Minimum)
- Problem Statement
- Proposed Solution
- Acceptance Criteria
- Tax Domain Considerations
- Risks

### Architecture (Minimum)
- Overview
- Components
- Data Flow
- File Changes
- Tax Domain Considerations

### Task Breakdown (Minimum)
- Feature metadata
- Implementation tasks
- QC task (id: 90)
- Git task (id: 91)
- Audit task (id: 99)

---

**Document Status:** Active — Update when templates change.
