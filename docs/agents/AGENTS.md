# Agent Governance — ComptabilityProject

**Version:** 1.1
**Created:** 2026-01-20
**Updated:** 2026-01-20
**Status:** ACTIVE — Aligned with Global WORKFLOW_RULES.md v2.0

---

## 1. Governance Principles

### 1.1 Entry/Exit Gates (NON-NEGOTIABLE — GLOBAL RULE)

| Gate | Agent | Rule |
|------|-------|------|
| **ENTRY** | yoni-orchestrator | EVERY user request goes through Yoni FIRST |
| **EXIT** | wealon-regulatory-auditor | EVERY task ends with Wealon audit |

**No exceptions.** If a task bypasses these gates, it is invalid.

> **Note:** Wealon-Last is a MANDATORY EXIT GATE for all projects, not just ComptabilityProject.

### 1.2 Analytical Mandate (Layer Separation)

This project involves financial data. The following separation is MANDATORY:

| Layer | Scope | Authority |
|-------|-------|-----------|
| **Layer 1: Descriptive** | Calculations, data extraction, comparisons | **AGENT-ALLOWED** |
| **Layer 2: Normative** | "Good", "bad", "optimal", "recommended" | **AGENT-ALLOWED with disclaimers** |
| **Layer 3: Prescriptive** | "You should do X", "Invest in Y" | **HUMAN-ONLY** |

**Key Rule:** Agents can describe and analyze. Agents can suggest with caveats. Only humans can decide.

---

## 2. Agent Classification

### 2.1 Global Primary Agents (Always Active — Per WORKFLOW_RULES.md)

These 9 agents are PRIMARY across ALL projects:

| Agent | Domain | Role | Invocation |
|-------|--------|------|------------|
| **yoni-orchestrator** | Orchestration | Entry gate, task coordination | **FIRST** for every request |
| **wealon-regulatory-auditor** | Compliance | Exit gate, final audit | **LAST** for every task |
| **it-core-clovis** | Structural Quality | Architecture, design patterns, git | Before commits/PRs |
| **quality-control-enforcer** | Implementation Quality | Correctness, edge cases, shortcuts | After code changes |
| **lamine-deployment-expert** | CI/CD & TDD | Pipelines, testing, deployment | Deployment tasks |
| **alexios-ml-predictor** | ML/Algorithms | Algorithm design, optimization, complexity | Algorithm decisions |
| **cybersecurity-expert-maxime** | Security Design | Threat modeling, secure coding | Security changes |
| **nicolas-risk-manager** | Risk Management | VaR, exposure, risk concepts | Risk assessment |
| **pierre-jean-ml-advisor** | ML Guidance | ML theory, interview framing | ML guidance |

### 2.2 Project-Specific Primary Agents (ComptabilityProject Only)

These agents are PRIMARY for this project due to domain requirements:

| Agent | Domain | Role | Invocation |
|-------|--------|------|------------|
| **french-tax-optimizer** | French Tax Law | Tax rule interpretation, optimization strategies | Tax-related changes |
| **legal-compliance-reviewer** | Regulatory Compliance | Tax/finance law compliance | Tax/investment changes |

**Total Primary Agents for ComptabilityProject: 11** (9 global + 2 project-specific)

### 2.3 Conditional Agents (Domain-Specific)

| Agent | Domain | Condition | Escalation Protocol |
|-------|--------|-----------|---------------------|
| **legal-team-lead** | Legal Management | Cross-domain legal questions | Escalate from legal-compliance |
| **data-engineer-sophie** | Data Pipelines | ETL, data quality issues | Pipeline changes |
| **antoine-nlp-expert** | NLP/LLM | Prompt engineering, LLM behavior | LLM changes |
| **research-remy-stocks** | Equities | Educational only, requires disclaimer | Finance education |
| **iacopo-macro-futures-analyst** | Macro/Futures | Educational only, requires disclaimer | Finance education |

### 2.4 System Agents (Meta-Level)

| Agent | Domain | Role |
|-------|--------|------|
| **Explore** | Codebase navigation | Find files, understand structure |
| **Plan** | Architecture design | Plan implementations |
| **general-purpose** | Multi-step tasks | Complex task execution |
| **claude-code-guide** | CLI guidance | Tool usage questions |

### 2.5 Available but NOT Integrated

| Agent | Reason |
|-------|--------|
| **dulcy-ml-engineer** | No ML training pipelines needed |
| **backtester-agent** | No trading strategies |
| **trading-execution-engine** | No trading |
| **helena-execution-manager** | No trading |
| **portfolio-manager-jean-yves** | Investment management, not tax |
| **pnl-validator** | P&L validation, not tax |
| **victor-pnl-manager** | P&L management, not tax |

### 2.6 Explicitly REJECTED

| Agent | Reason | Reconsideration Trigger |
|-------|--------|------------------------|
| **cost-optimizer-lucas** | Premature optimization | Only if cost becomes issue |
| **data-research-liaison** | No research team | Only if team structure changes |
| **gabriel-task-orchestrator** | Single developer project | Only if multi-team |
| **jacques-head-manager** | Single developer project | Only if multi-team |
| **jean-david-it-core-manager** | Single developer project | Only if multi-team |
| **ml-production-engineer** | No ML models in production | Only if ML deployed |

---

## 3. Workflow Integration

### 3.1 BMAD Workflow Triggers

| Trigger | Condition | Workflow | Agents Involved |
|---------|-----------|----------|-----------------|
| `new_feature` | Any new capability | FULL_PLANNING | yoni → alexios → clovis → qc → lamine → wealon |
| `domain_crossing` | ≥2 domains touched | INTEGRATION | yoni → clovis → qc → wealon |
| `file_impact` | ≥2 files changed | FULL_PLANNING | yoni → clovis → qc → wealon |
| `infrastructure` | Infra/config changes | ADR | yoni → lamine → clovis → wealon |
| `algorithm_unclear` | Uncertainty > 0.5 | RESEARCH | yoni → alexios → pierre-jean → wealon |
| `performance_risk` | Performance-critical | OPTIMIZATION | yoni → alexios → clovis → wealon |
| `security_sensitive` | Auth/crypto/input | SECURITY_REVIEW | yoni → maxime → wealon → qc |
| `tax_rule_change` | Tax engine/analyzer changes | TAX_REVIEW | yoni → french-tax → legal-compliance → qc → wealon |
| `llm_prompt_change` | Prompt/LLM code changes | LLM_REVIEW | yoni → antoine-nlp → maxime → legal-compliance → wealon |
| `simple_change` | Single file, low risk | SKIP | yoni → direct → clovis → wealon |

### 3.2 Workflows Defined

| Workflow | Stages | Output Artifacts |
|----------|--------|------------------|
| **FULL_PLANNING** | ANALYZE → SCOPE → ARCHITECT → DECOMPOSE | PRD-lite, architecture, task breakdown |
| **INTEGRATION** | ANALYZE → INTERFACE_MAPPING → CONTRACT_DEFINITION | Integration spec |
| **ADR** | CONTEXT → OPTIONS → DECISION → CONSEQUENCES | ADR document |
| **RESEARCH** | PROBLEM_DEFINITION → LITERATURE_REVIEW → PROTOTYPE_PLAN | Research brief, approach options |
| **OPTIMIZATION** | PROFILE → BENCHMARK → STRATEGY | Performance analysis, optimization plan |
| **SECURITY_REVIEW** | THREAT_MODEL → ATTACK_SURFACE → MITIGATIONS | Security review, threat model |
| **TAX_REVIEW** | ANALYZE → TAX_VALIDATION → LEGAL_COMPLIANCE → VERIFY | Tax interpretation, compliance check |
| **LLM_REVIEW** | ANALYZE → NLP_REVIEW → SECURITY_CHECK → LEGAL_COMPLIANCE | Prompt review, safety check |
| **SKIP** | Direct execution | None |

### 3.3 Agent Interaction Pattern

```
User Request
    ↓
[ENTRY] yoni-orchestrator
    ↓
Complexity Assessment
    ├── Triggers matched
    ├── Workflow selected
    └── Agents dispatched
    ↓
Workflow Execution
    ├── Domain agents consulted (parallel where possible)
    ├── Artifacts produced
    └── Implementation completed
    ↓
Review Phase
    ├── quality-control-enforcer (implementation quality)
    ├── it-core-clovis (structural quality, git)
    └── [domain agents as needed]
    ↓
[EXIT] wealon-regulatory-auditor
    ↓
Human Approval (if required)
    ↓
Task Complete
```

---

## 4. Tax Domain Special Rules

### 4.1 Tax Calculation Changes

**MANDATORY WORKFLOW (TAX_REVIEW) for any change to:**
- `src/tax_engine/*.py`
- `src/tax_engine/data/*.json`
- `src/analyzers/strategies/*.py`
- `src/analyzers/rules/*.json`

| Step | Agent | Check |
|------|-------|-------|
| 1 | french-tax-optimizer | Rule interpretation correct? |
| 2 | legal-compliance-reviewer | Regulatory compliance? |
| 3 | quality-control-enforcer | Test coverage? |
| 4 | wealon-regulatory-auditor | Final audit |

**Human checkpoint required before implementation.**

### 4.2 LLM Prompt Changes

**MANDATORY WORKFLOW (LLM_REVIEW) for any change to:**
- `prompts/*.txt`
- `prompts/*.md`
- `src/llm/*.py`

| Step | Agent | Check |
|------|-------|-------|
| 1 | antoine-nlp-expert | Prompt quality? |
| 2 | cybersecurity-expert-maxime | Injection risk? |
| 3 | legal-compliance-reviewer | Advice scope appropriate? |
| 4 | wealon-regulatory-auditor | Final audit |

### 4.3 Investment Recommendation Changes

**HIGH ALERT** — Any change to investment-related recommendations requires:

| Check | Requirement |
|-------|-------------|
| french-tax-optimizer | MANDATORY |
| legal-compliance-reviewer | MANDATORY |
| Human approval | MANDATORY |
| Disclaimer audit | MANDATORY |

Affected strategies:
- LMNP (real estate)
- FCPI/FIP (innovation funds)
- Girardin Industriel (overseas investment)
- Company structure (SASU/EURL/Holding)

---

## 5. Human Authority Retention

### 5.1 Decisions Requiring Human Approval

| Decision Type | Agent Can Propose | Human Must Approve |
|---------------|-------------------|-------------------|
| Tax rule interpretation | YES | **YES** |
| Investment recommendation wording | YES | **YES** |
| Disclaimer language | YES | **YES** |
| New optimization strategy | YES | **YES** |
| LLM system prompt changes | YES | **YES** |
| Barème data updates | YES | **YES** |

### 5.2 Agent Limitations

Agents **CANNOT**:
- Approve changes to tax rules without human verification
- Modify disclaimers to reduce liability protection
- Add investment recommendations without legal review
- Change LLM scope to provide "professional advice"
- Override Wealon audit findings

---

## 6. Review Conflict Resolution Hierarchy

When agents disagree, follow this hierarchy (per WORKFLOW_RULES.md):

```
1. Security/Regulatory (Wealon, Maxime) → ABSOLUTE PRIORITY
2. Structural (Clovis) → Must resolve or create ADR
3. Implementation (QC) → Resolve or track as tech debt
4. Domain-specific (french-tax, legal-compliance) → Escalate to human
```

---

## 7. Change Control

### 7.1 Versioning

| Change Type | Process |
|-------------|---------|
| Add project-specific PRIMARY agent | Document + human approval |
| Move agent to REJECTED | Document + human approval |
| Modify workflow triggers | Update config.yaml + document |
| Update agent conditions | Document in changelog |

### 7.2 Changelog

| Date | Version | Change | Approved By |
|------|---------|--------|-------------|
| 2026-01-20 | 1.0 | Initial baseline | User |
| 2026-01-20 | 1.1 | Aligned with WORKFLOW_RULES.md v2.0: 9 global PRIMARY + 2 project-specific PRIMARY, added RESEARCH/OPTIMIZATION workflows, added algorithm_unclear/performance_risk triggers | User |

---

## 8. Escalation Rules

### 8.1 When to Stop and Ask Human

| Situation | Action |
|-----------|--------|
| Tax rule interpretation unclear | STOP — ask human |
| Investment recommendation scope | STOP — ask human |
| Regulatory compliance uncertain | STOP — ask human |
| Wealon audit fails | STOP — human must resolve |
| Multiple valid approaches | STOP — human chooses |
| Uncertainty > 0.5 on significant decision | STOP — ask human |

### 8.2 Escalation Path

```
Agent Uncertainty
    ↓
Escalate to yoni-orchestrator
    ↓
yoni cannot resolve?
    ↓
Escalate to Human
    ↓
Human Decision
    ↓
Document in decisions.md
```

---

## 9. Quality Standards

All agent outputs must be:

- **Auditable** — Can be reviewed by external parties
- **Traceable** — Source of truth documented
- **Defensible** — Can withstand scrutiny
- **Reversible** — Changes can be undone

---

## 10. Key References

- **Global Rules:** `~/.claude/WORKFLOW_RULES.md` (v2.0)
- **Workflow Config:** `_bmad/config.yaml`
- **Workflow Details:** `_bmad/workflows.md`
- **Project Context:** `docs/project-context.md`
- **Templates:** `_bmad/templates/`

---

**Document Status:** v1.1 — Aligned with Global WORKFLOW_RULES.md
**Next Review:** After major scope change or global rule update
