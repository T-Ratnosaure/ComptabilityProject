# BMAD Workflows — ComptabilityProject

**Version:** 1.1
**Created:** 2026-01-20
**Updated:** 2026-01-20
**Status:** ACTIVE — Aligned with Global WORKFLOW_RULES.md v2.0

---

## Workflow Overview

| Workflow | Trigger | Complexity | Human Approval |
|----------|---------|------------|----------------|
| FULL_PLANNING | New feature, ≥2 files | HIGH | Required |
| TAX_REVIEW | Tax rule changes | HIGH | Required |
| LLM_REVIEW | LLM/prompt changes | HIGH | Required |
| INTEGRATION | Cross-domain changes | MEDIUM | Required |
| SECURITY_REVIEW | Security-sensitive | MEDIUM | Required |
| RESEARCH | Algorithm uncertainty > 0.5 | MEDIUM | Situational |
| OPTIMIZATION | Performance-critical code | MEDIUM | Situational |
| ADR | Infrastructure/config changes | MEDIUM | Required |
| SKIP | Simple, low-risk | LOW | Not required |

---

## 1. FULL_PLANNING Workflow

**Trigger:** `new_feature` (≥2 files affected)

### Stages

#### Stage 1: ANALYZE
**Agent:** yoni-orchestrator + Explore

**Inputs:**
- User request
- Current codebase state

**Outputs:**
- Scope definition
- Affected files list
- Risk assessment

**Checklist:**
- [ ] Requirements understood
- [ ] Scope boundaries defined
- [ ] Dependencies identified
- [ ] Risk level assessed

---

#### Stage 2: SCOPE
**Agent:** yoni-orchestrator

**Inputs:**
- Analysis results

**Outputs:**
- PRD-lite document
- Success criteria
- Test plan outline

**Checklist:**
- [ ] Acceptance criteria defined
- [ ] Out-of-scope documented
- [ ] Edge cases identified

---

#### Stage 3: ARCHITECT
**Agent:** Plan

**Inputs:**
- PRD-lite
- Codebase context

**Outputs:**
- Architecture document
- File change plan
- Interface definitions

**Checklist:**
- [ ] Architecture fits existing patterns
- [ ] No unnecessary complexity
- [ ] Interfaces defined

---

#### Stage 4: DECOMPOSE
**Agent:** yoni-orchestrator

**Inputs:**
- Architecture document

**Outputs:**
- Task breakdown
- Implementation order
- Test requirements per task

**Checklist:**
- [ ] Tasks are atomic
- [ ] Dependencies ordered
- [ ] Each task testable

---

#### Stage 5: IMPLEMENT
**Agents:** Direct implementation + quality-control-enforcer

**Outputs:**
- Code changes
- Tests
- Documentation updates

**Checklist:**
- [ ] Code follows patterns
- [ ] Tests pass
- [ ] Documentation updated

---

#### Stage 6: REVIEW
**Agents:** it-core-clovis + quality-control-enforcer

**Outputs:**
- Code review feedback
- Quality assessment

**Checklist:**
- [ ] Git workflow followed
- [ ] Code quality standards met
- [ ] No security issues

---

#### Stage 7: AUDIT
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Audit report
- Compliance assessment

**Checklist:**
- [ ] All stages completed
- [ ] Quality gates passed
- [ ] No blocking issues

---

## 2. TAX_REVIEW Workflow

**Trigger:** `tax_rule_change` (any change to tax_engine or analyzers)

### Stages

#### Stage 1: ANALYZE
**Agent:** yoni-orchestrator

**Outputs:**
- Change scope
- Affected calculations
- Regulatory implications

---

#### Stage 2: TAX_VALIDATION
**Agent:** french-tax-optimizer

**Outputs:**
- Tax rule interpretation
- Source citations
- Calculation verification

**Requirements:**
- Official source URL required
- Calculation example required

---

#### Stage 3: LEGAL_COMPLIANCE
**Agent:** legal-compliance-reviewer

**Outputs:**
- Compliance assessment
- Disclaimer requirements
- Regulatory risk evaluation

**Human Checkpoint:** Required before proceeding

---

#### Stage 4: IMPLEMENT
**Outputs:**
- Code changes
- Updated JSON rules
- Test cases

---

#### Stage 5: VERIFY
**Agent:** quality-control-enforcer

**Outputs:**
- Test results
- Coverage report
- Calculation verification

---

#### Stage 6: AUDIT
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Final compliance check
- Audit report

---

## 3. LLM_REVIEW Workflow

**Trigger:** `llm_prompt_change` (any change to prompts or LLM code)

### Stages

#### Stage 1: ANALYZE
**Agent:** yoni-orchestrator

**Outputs:**
- Change scope
- Behavior implications
- Risk assessment

---

#### Stage 2: NLP_REVIEW
**Agent:** antoine-nlp-expert

**Outputs:**
- Prompt quality assessment
- Expected behavior changes
- Edge case analysis

---

#### Stage 3: SECURITY_CHECK
**Agent:** cybersecurity-expert-maxime

**Outputs:**
- Injection risk assessment
- Input validation check
- Output safety check

---

#### Stage 4: LEGAL_COMPLIANCE
**Agent:** legal-compliance-reviewer

**Outputs:**
- Advice scope assessment
- Disclaimer adequacy
- Regulatory compliance

**Human Checkpoint:** Required before proceeding

---

#### Stage 5: IMPLEMENT & TEST
**Outputs:**
- Prompt changes
- Test cases
- Safety checks

---

#### Stage 6: AUDIT
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Final audit
- Compliance confirmation

---

## 4. INTEGRATION Workflow

**Trigger:** `document_parser_change` or cross-domain changes

### Stages

#### Stage 1: ANALYZE
**Agent:** yoni-orchestrator

**Outputs:**
- Interface mapping
- Data flow analysis
- Breaking change assessment

---

#### Stage 2: INTERFACE_MAPPING
**Agent:** data-engineer-sophie

**Outputs:**
- Data contracts
- Validation rules
- Error handling plan

---

#### Stage 3: CONTRACT_DEFINITION
**Outputs:**
- Interface specifications
- Test contracts
- Migration plan (if needed)

---

#### Stage 4: IMPLEMENT
**Outputs:**
- Code changes
- Integration tests
- Documentation

---

#### Stage 5: AUDIT
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Integration verification
- Audit report

---

## 5. SECURITY_REVIEW Workflow

**Trigger:** `security_change` (any security-sensitive code)

### Stages

#### Stage 1: THREAT_MODEL
**Agent:** cybersecurity-expert-maxime

**Outputs:**
- Threat assessment
- Attack surface analysis
- Risk ranking

---

#### Stage 2: ATTACK_SURFACE
**Outputs:**
- Vulnerability scan results
- Input validation check
- Authentication review

---

#### Stage 3: MITIGATIONS
**Outputs:**
- Security controls
- Implementation plan
- Test cases

---

#### Stage 4: IMPLEMENT
**Outputs:**
- Security fixes
- Tests
- Documentation

---

#### Stage 5: AUDIT
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Security audit
- Compliance check

---

## 6. RESEARCH Workflow

**Trigger:** `algorithm_unclear` (uncertainty > 0.5 on algorithm choice)

### Purpose

Use this workflow when facing algorithm decisions with significant uncertainty. This ensures proper research and documentation before committing to an approach.

### Stages

#### Stage 1: PROBLEM_DEFINITION
**Agent:** yoni-orchestrator

**Outputs:**
- Clear problem statement
- Success criteria
- Constraints and requirements
- Uncertainty factors identified

**Checklist:**
- [ ] Problem boundaries defined
- [ ] Performance requirements specified
- [ ] Known constraints documented
- [ ] Uncertainty sources identified

---

#### Stage 2: LITERATURE_REVIEW
**Agents:** alexios-ml-predictor + pierre-jean-ml-advisor

**Outputs:**
- Algorithm options analysis
- Tradeoff comparison
- Relevant prior art
- Risk assessment per option

**Checklist:**
- [ ] Multiple approaches considered
- [ ] Complexity vs performance analyzed
- [ ] Edge cases identified
- [ ] Maintainability assessed

---

#### Stage 3: PROTOTYPE_PLAN
**Agents:** alexios-ml-predictor + yoni-orchestrator

**Outputs:**
- Recommended approach with rationale
- Prototype scope
- Validation criteria
- Fallback options

**Artifacts:**
- `docs/planning/research/{date}-{topic}.md` (research brief)
- `docs/planning/research/{date}-{topic}-options.md` (approach options)

**Checklist:**
- [ ] Approach justified
- [ ] Risks documented
- [ ] Validation plan defined
- [ ] Fallback identified

---

#### Stage 4: AUDIT
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Research quality audit
- Decision documentation review

---

## 7. OPTIMIZATION Workflow

**Trigger:** `performance_risk` (performance-critical code)

### Purpose

Use this workflow when modifying or creating performance-critical code. This ensures proper profiling, benchmarking, and strategy definition before implementation.

### Stages

#### Stage 1: PROFILE
**Agent:** alexios-ml-predictor

**Outputs:**
- Current performance baseline
- Bottleneck identification
- Resource utilization analysis
- Performance targets

**Checklist:**
- [ ] Baseline metrics captured
- [ ] Bottlenecks identified
- [ ] Target improvements defined
- [ ] Measurement methodology documented

---

#### Stage 2: BENCHMARK
**Agents:** alexios-ml-predictor + it-core-clovis

**Outputs:**
- Benchmark suite definition
- Comparison metrics
- Test data requirements
- Reproducibility plan

**Checklist:**
- [ ] Benchmarks representative
- [ ] Comparison baseline established
- [ ] Edge cases included
- [ ] Reproducible methodology

---

#### Stage 3: STRATEGY
**Agents:** alexios-ml-predictor + yoni-orchestrator

**Outputs:**
- Optimization strategy
- Implementation plan
- Expected improvements
- Risk mitigation

**Artifacts:**
- `docs/planning/research/{date}-{topic}-performance.md` (performance analysis)
- `docs/planning/research/{date}-{topic}-optimization.md` (optimization plan)

**Checklist:**
- [ ] Strategy justified
- [ ] Tradeoffs documented
- [ ] Maintenance impact assessed
- [ ] Regression plan defined

---

#### Stage 4: IMPLEMENT
**Agents:** Direct implementation + quality-control-enforcer

**Outputs:**
- Optimized code
- Benchmark results
- Documentation updates

**Checklist:**
- [ ] Performance targets met
- [ ] No regressions
- [ ] Code maintainability preserved

---

#### Stage 5: AUDIT
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Performance verification
- Audit report

---

## 8. ADR Workflow

**Trigger:** `infrastructure` (CI/CD or config changes)

### Purpose

Use this workflow for architectural decisions and infrastructure changes. Creates an Architecture Decision Record for traceability.

### Stages

#### Stage 1: CONTEXT
**Agent:** yoni-orchestrator + lamine-deployment-expert

**Outputs:**
- Decision context
- Current state analysis
- Problem statement
- Stakeholder impact

**Checklist:**
- [ ] Context fully described
- [ ] Problem clearly stated
- [ ] Stakeholders identified

---

#### Stage 2: OPTIONS
**Agents:** lamine-deployment-expert + it-core-clovis

**Outputs:**
- Option enumeration
- Pros/cons analysis
- Cost assessment
- Risk evaluation

**Checklist:**
- [ ] Multiple options considered
- [ ] Tradeoffs documented
- [ ] Costs estimated
- [ ] Risks identified

---

#### Stage 3: DECISION
**Agent:** yoni-orchestrator

**Outputs:**
- Chosen option
- Rationale
- Implementation plan
- Success criteria

**Human Checkpoint:** Required before proceeding

**Checklist:**
- [ ] Decision justified
- [ ] Rationale documented
- [ ] Implementation planned

---

#### Stage 4: CONSEQUENCES
**Agent:** wealon-regulatory-auditor

**Outputs:**
- Impact assessment
- Follow-up actions
- ADR document finalized

**Artifacts:**
- `docs/adr/{number}-{title}.md` (Architecture Decision Record)

**Checklist:**
- [ ] Consequences documented
- [ ] Follow-up actions listed
- [ ] ADR archived

---

## 9. SKIP Workflow

**Trigger:** `simple_change` (1 file, low risk, no tax/security impact)

### Stages

#### Stage 1: ENTRY
**Agent:** yoni-orchestrator

**Validation:**
- Confirm single file
- Confirm no tax impact
- Confirm no security impact

---

#### Stage 2: IMPLEMENT
**Direct implementation**

---

#### Stage 3: REVIEW
**Agent:** it-core-clovis

**Quick check:**
- Git workflow followed
- Basic quality

---

#### Stage 4: AUDIT
**Agent:** wealon-regulatory-auditor

**Light audit:**
- Verify skip criteria met
- No blocking issues

---

## Workflow Selection Matrix

| Condition | Workflow |
|-----------|----------|
| Changes tax_engine/** | TAX_REVIEW |
| Changes analyzers/** | TAX_REVIEW |
| Changes prompts/** | LLM_REVIEW |
| Changes src/llm/** | LLM_REVIEW |
| Changes src/security/** | SECURITY_REVIEW |
| Changes extractors/** | INTEGRATION |
| CI/CD or config changes | ADR |
| Algorithm uncertainty > 0.5 | RESEARCH |
| Performance-critical code | OPTIMIZATION |
| New feature, ≥2 files | FULL_PLANNING |
| Cross-domain (≥2 domains) | INTEGRATION |
| Single file, no tax/security/llm | SKIP |

---

## Parallel Execution Rules

**Can Run in Parallel:**
- Stage 1 analysis tasks (when independent)
- Test execution across modules
- Documentation updates
- RESEARCH literature review tasks

**Must Run Sequentially:**
- Stages within a workflow
- Human checkpoints
- Audit (always last)

---

## Entry/Exit Gates (NON-NEGOTIABLE)

| Gate | Agent | Rule |
|------|-------|------|
| **ENTRY** | yoni-orchestrator | EVERY workflow starts with Yoni |
| **EXIT** | wealon-regulatory-auditor | EVERY workflow ends with Wealon audit |

**No exceptions.** All workflows defined above include these gates.

---

**Document Status:** v1.1 — Aligned with WORKFLOW_RULES.md v2.0
