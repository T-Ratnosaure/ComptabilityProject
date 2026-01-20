# ComptabilityProject Agent Ecosystem — Baseline v1.0

**Status:** FROZEN
**Freeze Date:** 2026-01-20
**Authority:** User (pending acknowledgment)

---

## Step 1: Baseline Declaration

### Frozen Documents

| Document | Path | Version | Purpose |
|----------|------|---------|---------|
| AGENTS.md | `docs/agents/AGENTS.md` | v1.0 | Governance master |
| project-context.md | `docs/project-context.md` | v1.0 | Domain bible |
| available-agents-inventory.md | `docs/agents/available-agents-inventory.md` | v1.0 | Full agent list |
| agent-relevance-matrix.md | `docs/agents/agent-relevance-matrix.md` | v1.0 | Selection rationale |
| expanded-inventory.md | `docs/agents/expanded-inventory.md` | v1.0 | Cognitive profiles |
| friction-map.md | `docs/agents/friction-map.md` | v1.0 | Overlaps, gaps |
| simulations.md | `docs/agents/simulations.md` | v1.0 | Impact analysis |
| yoni-perspective.md | `docs/agents/yoni-perspective.md` | v1.0 | Builder view |
| wealon-perspective.md | `docs/agents/wealon-perspective.md` | v1.0 | Auditor view |
| decisions.md | `docs/agents/decisions.md` | v1.0 | Design decisions |
| config.yaml | `_bmad/config.yaml` | v1.0 | Workflow config |
| workflows.md | `_bmad/workflows.md` | v1.0 | Workflow definitions |
| CLAUDE.md | `CLAUDE.md` | v1.0 | Project instructions |

### Frozen Assumptions

| ID | Assumption | Locked Value |
|----|------------|--------------|
| A1 | Users are French tax residents | TRUE |
| A2 | Tax rules are for 2024-2025 fiscal years | TRUE |
| A3 | LLM provides informational advice only | TRUE |
| A4 | Single-user application | TRUE |
| A5 | French jurisdiction only | TRUE |
| A6 | Professional accountant augmented, not replaced | TRUE |

### Non-Negotiable Scope Boundaries

```
SYSTEM IS:
├── French tax calculation tool
├── Tax optimization information provider
├── Document extraction system
├── Conversational tax Q&A interface
└── Informational tool for freelancers

SYSTEM IS NOT:
├── Licensed accountant (Expert-Comptable)
├── Professional tax advisor (Conseil Fiscal)
├── Investment advisor (CIF)
├── Tax filing service
├── Binding tax calculation
└── Multi-jurisdiction tax system
```

### Mandatory Agent Gates

| Gate | Trigger | Agent | Action |
|------|---------|-------|--------|
| AG-01 | Start of every task | yoni-orchestrator | Entry coordination |
| AG-02 | End of every task | wealon-regulatory-auditor | Exit audit |

### Mandatory Human Checkpoints

| Checkpoint | Trigger | Human Action Required |
|------------|---------|----------------------|
| HC-01 | Tax rule change | Approve interpretation and implementation |
| HC-02 | Barème update | Verify against official source |
| HC-03 | Investment recommendation change | Approve wording and disclaimers |
| HC-04 | LLM scope change | Approve advice boundaries |
| HC-05 | Disclaimer modification | Approve legal language |

---

## Step 2: Breaking Change Definitions

A **breaking change** requires:
1. New binding decision documented in decisions.md
2. New Wealon audit
3. Version increment to v2.0
4. Human approval

### Category A: Scope Expansion (BREAKING)

| Change | Why Breaking |
|--------|--------------|
| Add non-French tax jurisdiction | Fundamental scope expansion |
| Add professional tax advice | Regulatory boundary violation |
| Add tax filing capability | New regulated activity |
| Add investment management | CIF licensing required |

### Category B: Assumption Reversal (BREAKING)

| Change | Why Breaking |
|--------|--------------|
| Change LLM to prescriptive advice | Liability change |
| Remove human checkpoints | Governance weakening |
| Make Wealon audit optional | Quality gate removal |
| Add multi-tenant support | Architecture change |

### Category C: Agent Governance Changes (BREAKING)

| Change | Why Breaking |
|--------|--------------|
| Promote rejected agent to primary | Agent ecosystem change |
| Remove mandatory exit gate | Governance weakening |
| Change workflow triggers | Behavior change |

---

## Step 3: Allowed Change Paths

### Legal Evolution (Within v1.0)

| Change Type | Conditions | Process |
|-------------|------------|---------|
| Bug fix | Does not change scope or behavior | Normal PR |
| Documentation clarification | Does not change meaning | Normal PR |
| Test additions | Does not change functionality | Normal PR |
| Performance optimization | Does not change behavior | Normal PR + QC review |
| Dependency update | No breaking changes | Normal PR + security review |

### Requires Minor Version (v1.1, v1.2, etc.)

| Change Type | Conditions | Process |
|-------------|------------|---------|
| New conditional agent activation | Within existing framework | Document + Wealon audit |
| Workflow refinement | Does not change triggers | Document + Wealon audit |
| Template updates | Does not change structure | Document + Wealon audit |

### Illegal Changes (Require v2.0)

```
ILLEGAL WITHOUT v2.0:
├── Change Yoni-first or Wealon-last rules
├── Add or remove mandatory human checkpoints
├── Change scope boundaries (IS/IS NOT)
├── Reverse frozen assumptions
├── Promote rejected agents to active
├── Add new tax jurisdictions
├── Enable prescriptive advice
└── Remove quality gates
```

---

## Step 4: Review Triggers

### Automatic Re-Audit Triggers

| Trigger | Audit Scope |
|---------|-------------|
| Pre-production deployment | Full system audit |
| Tax year change (new barème) | Tax calculation audit |
| Major dependency update | Security audit |
| Quarterly review | Governance document review |

### System Freeze Triggers

| Trigger | Required Action |
|---------|-----------------|
| Baseline contradiction discovered | Freeze until resolved |
| Regulatory concern raised | Freeze affected area |
| Critical bug in tax calculation | Freeze tax features |
| Security vulnerability | Freeze affected endpoints |

---

## Step 5: Closure Statement

As of 2026-01-20, the design phase is **CLOSED**.

The system is now **operational** under governed change control.

### System Truth (Locked)

> ComptabilityProject is an INFORMATIONAL French tax optimization tool for freelancers.
> It extracts data from tax documents, calculates taxes using official barèmes, and provides
> optimization scenario information. It is NOT professional tax advice, NOT investment advice,
> and does NOT replace consultation with licensed professionals. All tax interpretations must
> be verified against official sources, and human approval is required for tax-related changes.

### Human Authority (Affirmed)

The human operator retains:
- **Final authority** over all tax rule interpretations
- **Veto power** over any agent recommendation
- **Responsibility** for verifying calculations against official sources
- **Approval authority** for baseline changes
- **Decision power** on investment recommendation scope

---

## Appendix: Human Acknowledgment

By using this system, the human operator acknowledges:

- [ ] I understand the system's scope limitations (IS/IS NOT)
- [ ] I accept responsibility for tax rule verification
- [ ] I will follow the change control process for baseline changes
- [ ] I understand that agent outputs require human validation
- [ ] I will obtain professional legal review before production deployment
- [ ] I acknowledge the open questions in decisions.md requiring resolution

---

## Appendix: Document Hashes (For Change Detection)

| Document | Hash (SHA-256) | Last Verified |
|----------|----------------|---------------|
| AGENTS.md | [compute on commit] | 2026-01-20 |
| project-context.md | [compute on commit] | 2026-01-20 |
| config.yaml | [compute on commit] | 2026-01-20 |
| workflows.md | [compute on commit] | 2026-01-20 |
| CLAUDE.md | [compute on commit] | 2026-01-20 |

*Note: Hashes will be computed at commit time to enable change detection.*

---

## Appendix: Version History

| Version | Date | Changes | Approved By |
|---------|------|---------|-------------|
| v1.0 | 2026-01-20 | Initial baseline | Pending |

---

**Document Status:** BASELINE v1.0 — FROZEN pending human acknowledgment
