# Available Agents Inventory — ComptabilityProject

**Version:** 1.0
**Created:** 2026-01-20
**Purpose:** Phase 2 — Enumerate ALL available agents regardless of usage

---

## All Available Agents

| Agent | Domain | Intended Role | Strengths | Risks | Dependencies |
|-------|--------|---------------|-----------|-------|--------------|
| yoni-orchestrator | Orchestration | Task coordination & routing | Multi-agent dispatch, workflow selection | Over-routing simple tasks | None |
| it-core-clovis | Git/DevOps | Code quality, branch management | PR workflow, code review | Bureaucracy for small changes | Git |
| quality-control-enforcer | QA | Implementation quality checks | Catches shortcuts, validates completeness | May be redundant with Clovis | None |
| lamine-deployment-expert | CI/CD | Pipeline, TDD practices | CI/CD expertise, testing | Over-engineering deployment | CI system |
| wealon-regulatory-auditor | Compliance | Audit & regulatory review | Catches issues, ensures quality | May slow velocity | None |
| alexios-ml-predictor | ML | ML model design & optimization | Algorithm expertise, financial ML | Financial domain bias | ML libraries |
| dulcy-ml-engineer | ML Engineering | Training pipelines, implementation | Practical ML engineering | Implementation focus over theory | ML infrastructure |
| pierre-jean-ml-advisor | ML Advisory | ML guidance, fine-tuning advice | Practical ML advice | May over-complicate | None |
| antoine-nlp-expert | NLP | LLM, transformers, text analysis | NLP/LLM expertise | Not financial domain | NLP libraries |
| data-engineer-sophie | Data | ETL, data pipelines, quality | Data architecture | Over-engineering pipelines | Data infrastructure |
| cybersecurity-expert-maxime | Security | Security assessment, pen testing | Security expertise | May over-secure | Security tools |
| french-tax-optimizer | French Tax | Tax optimization strategies | French tax expertise | Regulatory advice risk | French tax knowledge |
| legal-compliance-reviewer | Legal | Regulatory compliance | Legal expertise | May be overly conservative | Legal knowledge |
| legal-team-lead | Legal Management | Legal team coordination | Oversight, escalation | Overhead | legal-compliance |
| research-remy-stocks | Equities | Stock research, stochastic calculus | Equity analysis | Wrong domain for tax | Financial data |
| iacopo-macro-futures-analyst | Macro/Futures | Economic analysis, futures | Macro expertise | Wrong domain for tax | Economic data |
| backtester-agent | Trading | Strategy backtesting | Simulation expertise | No trading in project | Historical data |
| trading-execution-engine | Trading | Order execution | Execution algorithms | No trading in project | Trading infrastructure |
| helena-execution-manager | Trading | Execution coordination | Trade management | No trading in project | Trading systems |
| nicolas-risk-manager | Risk | Portfolio risk management | Risk expertise | Investment focus, not tax | Risk models |
| portfolio-manager-jean-yves | Portfolio | Portfolio strategy | Strategic oversight | Investment focus, not tax | Portfolio data |
| pnl-validator | P&L | P&L validation | Financial accuracy | No P&L in project | Financial data |
| victor-pnl-manager | P&L | P&L management | P&L expertise | No P&L in project | Financial systems |
| cost-optimizer-lucas | Costs | Cost analysis & optimization | Cost reduction | Premature for this project | Cost data |
| data-research-liaison | Communication | Cross-team liaison | Communication | Single developer project | Multiple teams |
| gabriel-task-orchestrator | Task Management | Global task prioritization | Coordination | Single developer project | Multiple teams |
| jacques-head-manager | Management | Multi-team orchestration | Strategic oversight | Single developer project | Multiple teams |
| jean-david-it-core-manager | IT Management | IT team coordination | Team management | Single developer project | IT team |
| ml-production-engineer | ML Production | Research to production ML | Productionization | No ML models yet | ML infrastructure |
| Explore | System | Codebase navigation | Fast file/code search | Limited to search | Codebase |
| Plan | System | Architecture design | Planning capability | No execution | None |
| general-purpose | System | Multi-step tasks | Flexibility | May lack specialization | None |
| claude-code-guide | System | CLI guidance | Tool documentation | Limited scope | None |

---

## Agent Categories

### Orchestration Agents
| Agent | Status | Notes |
|-------|--------|-------|
| yoni-orchestrator | **REQUIRED** | Entry point for all requests |

### Development Agents
| Agent | Status | Notes |
|-------|--------|-------|
| it-core-clovis | **REQUIRED** | Git workflow enforcement |
| quality-control-enforcer | **REQUIRED** | Code quality validation |
| lamine-deployment-expert | **REQUIRED** | CI/CD and TDD |

### Audit Agents
| Agent | Status | Notes |
|-------|--------|-------|
| wealon-regulatory-auditor | **REQUIRED** | Mandatory exit gate |

### ML/Data Agents
| Agent | Status | Notes |
|-------|--------|-------|
| alexios-ml-predictor | Available | No ML models in project |
| dulcy-ml-engineer | Available | No ML models in project |
| pierre-jean-ml-advisor | Available | No ML models in project |
| antoine-nlp-expert | Available | Relevant for LLM integration |
| data-engineer-sophie | Available | Relevant for extraction pipeline |
| ml-production-engineer | Available | No ML models in project |

### Security/Compliance Agents
| Agent | Status | Notes |
|-------|--------|-------|
| cybersecurity-expert-maxime | Available | Activate for security changes |
| legal-compliance-reviewer | **REQUIRED** | Tax domain has regulatory risk |
| legal-team-lead | Available | Escalation path |

### Domain-Specific Agents (Financial)
| Agent | Status | Notes |
|-------|--------|-------|
| french-tax-optimizer | **CRITICAL** | Core domain expertise |
| research-remy-stocks | Available | Wrong domain (equities, not tax) |
| iacopo-macro-futures-analyst | Available | Wrong domain (macro, not tax) |
| backtester-agent | Not Relevant | No trading strategies |
| trading-execution-engine | Not Relevant | No trading |
| helena-execution-manager | Not Relevant | No trading |
| nicolas-risk-manager | Available | Different risk focus |
| portfolio-manager-jean-yves | Available | Investment focus, not tax |
| pnl-validator | Not Relevant | No P&L tracking |
| victor-pnl-manager | Not Relevant | No P&L tracking |
| cost-optimizer-lucas | Available | Premature optimization |

### Management Agents
| Agent | Status | Notes |
|-------|--------|-------|
| data-research-liaison | Not Relevant | Single developer |
| gabriel-task-orchestrator | Not Relevant | Single developer |
| jacques-head-manager | Not Relevant | Single developer |
| jean-david-it-core-manager | Not Relevant | Single developer |

### System/Meta Agents
| Agent | Status | Notes |
|-------|--------|-------|
| Explore | **REQUIRED** | Codebase navigation |
| Plan | **REQUIRED** | Architecture planning |
| general-purpose | Available | Complex multi-step tasks |
| claude-code-guide | Available | Tool guidance |

---

## Undocumented Agents (Governance Risk)

**None identified.** All agents in the environment have documented purposes.

---

## Agent Count Summary

| Category | Total | Required | Available | Not Relevant |
|----------|-------|----------|-----------|--------------|
| Orchestration | 1 | 1 | 0 | 0 |
| Development | 3 | 3 | 0 | 0 |
| Audit | 1 | 1 | 0 | 0 |
| ML/Data | 6 | 0 | 6 | 0 |
| Security/Compliance | 3 | 1 | 2 | 0 |
| Domain (Financial) | 10 | 1 | 4 | 5 |
| Management | 4 | 0 | 0 | 4 |
| System | 4 | 2 | 2 | 0 |
| **TOTAL** | **32** | **9** | **14** | **9** |

---

**Document Status:** Complete — Ready for Phase 3 relevance analysis.
