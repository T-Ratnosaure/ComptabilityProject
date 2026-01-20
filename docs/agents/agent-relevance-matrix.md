# Agent Relevance Matrix — ComptabilityProject

**Version:** 1.1
**Created:** 2026-01-20
**Updated:** 2026-01-20
**Purpose:** Phase 3 — Classify agents by relevance to THIS project
**Aligned with:** Global WORKFLOW_RULES.md v2.0

---

## Classification Criteria

| Classification | Definition | Usage |
|----------------|------------|-------|
| **GLOBAL PRIMARY** | Core agents per WORKFLOW_RULES.md, always active | Use for every task |
| **PROJECT PRIMARY** | Project-specific core agents | Use when domain triggered |
| **CONDITIONAL** | Domain-specific, activated under constraints | Use when conditions met |
| **SYSTEM** | Meta/tooling agents | Use for exploration/planning |
| **AVAILABLE BUT INACTIVE** | Exists but not needed yet | Activate when trigger occurs |
| **EXPLICITLY REJECTED** | Wrong domain, never use | Never invoke |

---

## Relevance Matrix

| Agent | Domain | Relevance | Rationale | Risks | Conditions |
|-------|--------|-----------|-----------|-------|------------|
| yoni-orchestrator | Orchestration | **GLOBAL PRIMARY** | Entry gate (NON-NEGOTIABLE) | None | Always use FIRST |
| wealon-regulatory-auditor | Audit | **GLOBAL PRIMARY** | Exit gate (NON-NEGOTIABLE) | None | Always use LAST |
| it-core-clovis | Structural Quality | **GLOBAL PRIMARY** | Architecture, patterns, git | Overhead | Every commit/PR |
| quality-control-enforcer | Implementation Quality | **GLOBAL PRIMARY** | Catches shortcuts | May overlap with Clovis | After code changes |
| lamine-deployment-expert | CI/CD & TDD | **GLOBAL PRIMARY** | CI/CD, testing, deployment | Over-engineering | Pipeline changes |
| alexios-ml-predictor | ML/Algorithms | **GLOBAL PRIMARY** | Algorithm design, complexity | Financial bias | Algorithm decisions |
| cybersecurity-expert-maxime | Security Design | **GLOBAL PRIMARY** | Threat modeling, secure coding | Over-securing | Security changes |
| nicolas-risk-manager | Risk Management | **GLOBAL PRIMARY** | Risk concepts | Investment bias | Risk assessment |
| pierre-jean-ml-advisor | ML Guidance | **GLOBAL PRIMARY** | ML theory, guidance | None | ML guidance |
| french-tax-optimizer | French Tax Law | **PROJECT PRIMARY** | Core domain expertise | Regulatory advice risk | Tax rule changes |
| legal-compliance-reviewer | Regulatory | **PROJECT PRIMARY** | Tax has regulatory risk | Conservative bias | Tax/investment changes |
| legal-team-lead | Legal Management | **CONDITIONAL** | Escalation path | Overhead | Escalate from compliance |
| antoine-nlp-expert | NLP/LLM | **CONDITIONAL** | LLM prompt expertise | No financial knowledge | LLM/prompt changes |
| data-engineer-sophie | Data Pipelines | **CONDITIONAL** | Pipeline expertise | Over-engineering | Extraction changes |
| Explore | System | **SYSTEM** | Codebase navigation | Limited to search | File/code exploration |
| Plan | System | **SYSTEM** | Architecture design | No execution | Planning tasks |
| general-purpose | System | **SYSTEM** | Complex tasks | Lack specialization | Multi-step research |
| claude-code-guide | System | **SYSTEM** | Tool documentation | Limited scope | Tool questions |
| dulcy-ml-engineer | ML Engineering | **AVAILABLE** | No ML training pipelines | None | Activate if ML added |
| cost-optimizer-lucas | Cost Optimization | **AVAILABLE** | Premature for project | None | If cost becomes issue |
| research-remy-stocks | Equities | **REJECTED** | Wrong domain (stocks ≠ tax) | Domain mismatch | Never use |
| iacopo-macro-futures-analyst | Macro | **REJECTED** | Wrong domain (macro ≠ tax) | Domain mismatch | Never use |
| backtester-agent | Trading | **REJECTED** | No trading in project | Complete mismatch | Never use |
| trading-execution-engine | Trading | **REJECTED** | No trading in project | Complete mismatch | Never use |
| helena-execution-manager | Trading | **REJECTED** | No trading in project | Complete mismatch | Never use |
| portfolio-manager-jean-yves | Portfolio | **REJECTED** | Investment ≠ tax optimization | Domain confusion | Never use |
| pnl-validator | P&L | **REJECTED** | No P&L tracking | Complete mismatch | Never use |
| victor-pnl-manager | P&L | **REJECTED** | No P&L tracking | Complete mismatch | Never use |
| data-research-liaison | Communication | **REJECTED** | Single developer project | Overhead | Never use |
| gabriel-task-orchestrator | Management | **REJECTED** | Single developer project | Overhead | Never use |
| jacques-head-manager | Management | **REJECTED** | Single developer project | Overhead | Never use |
| jean-david-it-core-manager | Management | **REJECTED** | Single developer project | Overhead | Never use |
| ml-production-engineer | ML Production | **REJECTED** | No ML models in production | Premature | Never use |

---

## Selection Summary

### Global Primary Agents (9 total — per WORKFLOW_RULES.md v2.0)

| # | Agent | Reason | Invocation |
|---|-------|--------|------------|
| 1 | yoni-orchestrator | Entry gate (NON-NEGOTIABLE) | FIRST for every request |
| 2 | wealon-regulatory-auditor | Exit gate (NON-NEGOTIABLE) | LAST for every task |
| 3 | it-core-clovis | Structural quality, git workflow | Before commits/PRs |
| 4 | quality-control-enforcer | Implementation quality | After code changes |
| 5 | lamine-deployment-expert | CI/CD & TDD expertise | Pipeline tasks |
| 6 | alexios-ml-predictor | Algorithm design, complexity | Algorithm decisions |
| 7 | cybersecurity-expert-maxime | Threat modeling, secure coding | Security changes |
| 8 | nicolas-risk-manager | Risk concepts | Risk assessment |
| 9 | pierre-jean-ml-advisor | ML theory, guidance | ML guidance |

### Project-Specific Primary Agents (2 total — ComptabilityProject only)

| # | Agent | Reason | Invocation |
|---|-------|--------|------------|
| 1 | french-tax-optimizer | Core domain expertise (French tax) | Tax rule changes |
| 2 | legal-compliance-reviewer | Tax has regulatory risk | Tax/investment changes |

**Total PRIMARY Agents for ComptabilityProject: 11** (9 global + 2 project-specific)

### Conditional Agents (3 total)

| # | Agent | Condition | Constraint |
|---|-------|-----------|------------|
| 1 | legal-team-lead | Legal escalation | Only via legal-compliance |
| 2 | antoine-nlp-expert | LLM/prompt changes | No financial advice |
| 3 | data-engineer-sophie | Extraction pipeline | ETL scope only |

### System Agents (4 total)

| # | Agent | Usage |
|---|-------|-------|
| 1 | Explore | Codebase search and navigation |
| 2 | Plan | Architecture and implementation planning |
| 3 | general-purpose | Complex multi-step research tasks |
| 4 | claude-code-guide | Claude Code tool questions |

### Available but Inactive (2 total)

| # | Agent | Activate When |
|---|-------|---------------|
| 1 | dulcy-ml-engineer | If ML training pipelines needed |
| 2 | cost-optimizer-lucas | If infrastructure costs become concern |

### Explicitly Rejected (13 total)

| # | Agent | Reason |
|---|-------|--------|
| 1 | research-remy-stocks | Equity research ≠ tax optimization |
| 2 | iacopo-macro-futures-analyst | Macro analysis ≠ tax optimization |
| 3 | backtester-agent | No trading strategies |
| 4 | trading-execution-engine | No trading execution |
| 5 | helena-execution-manager | No trade management |
| 6 | portfolio-manager-jean-yves | Investment ≠ tax |
| 7 | pnl-validator | No P&L tracking |
| 8 | victor-pnl-manager | No P&L management |
| 9 | data-research-liaison | Single developer project |
| 10 | gabriel-task-orchestrator | Single developer project |
| 11 | jacques-head-manager | Single developer project |
| 12 | jean-david-it-core-manager | Single developer project |
| 13 | ml-production-engineer | No ML models in production |

---

## Key Decision: Financial Agents

**Context:** CartesSociete (gaming project) rejected ALL financial agents. ComptabilityProject IS a financial project — but it's tax, not trading.

**Decision:** Selective integration with constraints

| Agent Category | Decision | Rationale |
|----------------|----------|-----------|
| Tax-specific (french-tax-optimizer) | **PROJECT PRIMARY** | Core domain expertise |
| Legal (legal-compliance-reviewer) | **PROJECT PRIMARY** | Tax has regulatory risk |
| Equities/Trading | **REJECT** | Different financial domain |
| Portfolio/P&L | **REJECT** | Different financial domain |
| Risk (nicolas-risk-manager) | **GLOBAL PRIMARY** | General risk concepts (not investment-specific) |

**Constraint on french-tax-optimizer:**
- Output is ADVISORY ONLY
- Must verify against official sources
- Cannot make prescriptive recommendations
- Human approval required for tax rule changes

---

## Activation Matrix

| Trigger | Agents Activated |
|---------|-----------------|
| Any user request | yoni-orchestrator (FIRST) |
| Task completion | wealon-regulatory-auditor (LAST) |
| Code changes | quality-control-enforcer |
| Git operations | it-core-clovis |
| Tax engine changes | french-tax-optimizer + legal-compliance-reviewer |
| LLM/prompt changes | antoine-nlp-expert |
| Extraction changes | data-engineer-sophie |
| Security changes | cybersecurity-expert-maxime |
| Pipeline changes | lamine-deployment-expert |
| Algorithm uncertainty > 0.5 | alexios-ml-predictor + pierre-jean-ml-advisor |
| Performance-critical code | alexios-ml-predictor + it-core-clovis |
| Risk assessment | nicolas-risk-manager |

---

**Document Status:** v1.1 — Aligned with WORKFLOW_RULES.md v2.0
