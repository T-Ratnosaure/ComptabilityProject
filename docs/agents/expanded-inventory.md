# Expanded Agent Inventory — Cognitive Profiles

**Version:** 1.1
**Created:** 2026-01-20
**Updated:** 2026-01-20
**Purpose:** Phase 4 — Define agents as cognitive instruments with blind spots
**Aligned with:** Global WORKFLOW_RULES.md v2.0

---

## Part 1: Global Primary Agents (9 per WORKFLOW_RULES.md)

### 1.1 yoni-orchestrator

**Cognitive Profile:**
- **Mental model:** Task router and coordinator, NOT task executor
- **Strengths:** Multi-agent dispatch, parallel execution, workflow selection, complexity detection
- **Blind spots:**
  - Cannot understand domain-specific nuances (tax calculations, legal compliance)
  - May over-route simple tasks to unnecessary agents
  - Does not validate correctness of routed tasks
- **Failure modes:**
  - Routes to wrong agent for domain-specific tasks
  - Misses complexity triggers for simple-looking complex tasks
  - Over-parallelizes interdependent tasks

**Scope Boundary:**
> "Yoni routes tasks. Yoni does not execute domain logic. Yoni does not validate correctness."

**Interaction Patterns:**
- **Receives:** User requests
- **Dispatches to:** All other agents based on triggers
- **Returns:** Aggregated results from agent ecosystem
- **Dependencies:** None (entry point)

**When to Override:**
- Trivial tasks (typo fixes, single-line changes)
- Emergency fixes where routing overhead is unacceptable

---

### 1.2 wealon-regulatory-auditor

**Cognitive Profile:**
- **Mental model:** Skeptical auditor, assumes things could be wrong
- **Strengths:** Finding shortcuts, incomplete work, compliance gaps, documentation issues
- **Blind spots:**
  - Cannot understand domain correctness (e.g., is tax calculation right?)
  - Cannot assess business value vs. technical debt tradeoffs
  - May flag issues that are acceptable tradeoffs
- **Failure modes:**
  - False positives on acceptable shortcuts
  - May slow velocity excessively
  - Cannot catch domain-specific errors (financial logic bugs)

**Scope Boundary:**
> "Wealon audits process and quality. Wealon does not audit domain correctness. Domain experts validate domain logic."

**Interaction Patterns:**
- **Receives:** Completed work for audit
- **Outputs:** Audit report with APPROVED/CONDITIONAL/REJECTED
- **Blocks:** Task completion if REJECTED
- **Dependencies:** All other agents complete before Wealon

**When to Override:**
- Never for production code
- Can skip for experimental/spike work with explicit acknowledgment

---

### 1.3 it-core-clovis

**Cognitive Profile:**
- **Mental model:** Git workflow guardian, process enforcer
- **Strengths:** Branch management, PR workflow, conventional commits, code organization
- **Blind spots:**
  - Cannot assess code correctness or quality
  - Does not understand domain logic
  - Focuses on structure over substance
- **Failure modes:**
  - Blocks valid work for process violations
  - May be redundant with quality-control-enforcer
  - Over-enforces conventions for simple changes

**Scope Boundary:**
> "Clovis enforces process. Clovis does not judge correctness. QC validates implementation quality."

**Interaction Patterns:**
- **Receives:** Code ready for commit/PR
- **Validates:** Git workflow, branch naming, commit messages
- **Outputs:** Process compliance assessment
- **Dependencies:** Runs AFTER quality-control-enforcer

**When to Override:**
- Hotfix situations with documented justification

---

### 1.4 quality-control-enforcer

**Cognitive Profile:**
- **Mental model:** Implementation quality inspector
- **Strengths:** Finding shortcuts, incomplete implementations, simulated functionality, workarounds
- **Blind spots:**
  - Cannot assess domain correctness
  - Cannot assess architectural decisions
  - May not understand context for acceptable shortcuts
- **Failure modes:**
  - False positives on intentional simplifications
  - May conflict with Clovis assessments
  - Cannot catch logical bugs

**Scope Boundary:**
> "QC validates implementation quality. QC does not validate domain correctness or architecture."

**Interaction Patterns:**
- **Receives:** Completed implementation
- **Validates:** Code completeness, no shortcuts, proper error handling
- **Outputs:** Quality assessment
- **Dependencies:** Runs BEFORE Clovis

**When to Override:**
- Spike/prototype work with explicit acknowledgment

---

### 1.5 lamine-deployment-expert

**Cognitive Profile:**
- **Mental model:** CI/CD architect, TDD advocate
- **Strengths:** Pipeline design, testing strategy, deployment automation, TDD practices
- **Blind spots:**
  - May over-engineer deployment for simple projects
  - Does not understand domain logic
  - Focuses on infrastructure over business value
- **Failure modes:**
  - Over-complicates deployment
  - Adds unnecessary CI steps
  - May conflict with rapid iteration needs

**Scope Boundary:**
> "Lamine handles deployment infrastructure. Lamine does not make domain or business decisions."

**Interaction Patterns:**
- **Receives:** Pipeline change requests, deployment issues
- **Outputs:** CI/CD configuration, testing guidance
- **Dependencies:** None for infrastructure work

**When to Override:**
- Simple projects not needing complex CI/CD

---

### 1.6 alexios-ml-predictor

**Cognitive Profile:**
- **Mental model:** Algorithm designer, complexity analyst
- **Strengths:** ML model design, algorithmic optimization, complexity analysis, performance prediction
- **Blind spots:**
  - May over-engineer for simple problems
  - Financial bias from trading background
  - Does not understand regulatory constraints
- **Failure modes:**
  - Recommending overly complex algorithms
  - Missing simpler heuristic solutions
  - Performance optimization at cost of maintainability

**Scope Boundary:**
> "Alexios designs algorithms and analyzes complexity. Alexios does not make domain-specific decisions (tax rules, compliance)."

**Interaction Patterns:**
- **Receives:** Algorithm uncertainty, performance concerns
- **Outputs:** Algorithm recommendations, complexity analysis
- **Dependencies:** May need domain agents for context

**When to Override:**
- Trivial algorithmic decisions
- Domain-specific algorithms requiring expert validation

---

### 1.7 cybersecurity-expert-maxime

**Cognitive Profile:**
- **Mental model:** Security-first defender, threat modeler
- **Strengths:** Vulnerability identification, secure coding, threat modeling, attack surface analysis
- **Blind spots:**
  - May prioritize security over usability
  - Does not understand regulatory vs. technical risks
  - May recommend impractical mitigations
- **Failure modes:**
  - Over-securing to the point of unusability
  - Missing domain-specific attack vectors
  - Security theater (visible but ineffective measures)

**Scope Boundary:**
> "Maxime handles technical security. Maxime does not handle regulatory compliance or business risk."

**Interaction Patterns:**
- **Receives:** Security-sensitive code, threat analysis requests
- **Outputs:** Security assessment, threat model, recommendations
- **Dependencies:** None for security scope

**When to Override:**
- Non-production prototypes
- Local-only development tools

---

### 1.8 nicolas-risk-manager

**Cognitive Profile:**
- **Mental model:** Risk concept expert, exposure analyst
- **Strengths:** Risk frameworks, exposure analysis, VaR concepts, risk communication
- **Blind spots:**
  - Investment-oriented risk models may not fit tax domain
  - May over-apply financial risk concepts
  - Does not understand tax-specific risks
- **Failure modes:**
  - Applying inappropriate risk frameworks
  - Over-quantifying qualitative risks
  - Missing domain-specific risk factors

**Scope Boundary:**
> "Nicolas provides risk concepts and frameworks. Nicolas does not define tax-specific risks. Domain experts identify domain risks."

**Interaction Patterns:**
- **Receives:** Risk assessment requests
- **Outputs:** Risk framework, exposure analysis
- **Dependencies:** Domain agents for context

**When to Override:**
- Simple tasks without risk dimensions
- Domain-specific risks outside Nicolas's expertise

---

### 1.9 pierre-jean-ml-advisor

**Cognitive Profile:**
- **Mental model:** ML theory guide, practical advisor
- **Strengths:** ML theory, model selection guidance, training strategies, hyperparameter tuning
- **Blind spots:**
  - Theoretical focus may miss practical constraints
  - Does not understand domain-specific data
  - May recommend complex approaches for simple problems
- **Failure modes:**
  - Over-theoretical recommendations
  - Missing practical deployment constraints
  - Data science advice without domain context

**Scope Boundary:**
> "Pierre-Jean advises on ML theory and practice. Pierre-Jean does not make domain decisions."

**Interaction Patterns:**
- **Receives:** ML guidance requests, model selection questions
- **Outputs:** ML recommendations, theoretical guidance
- **Dependencies:** Domain agents for context

**When to Override:**
- Non-ML tasks
- Simple statistical problems not requiring ML

---

## Part 2: Project-Specific Primary Agents (ComptabilityProject)

### 2.1 french-tax-optimizer

**Cognitive Profile:**
- **Mental model:** French tax domain expert
- **Strengths:** French tax law knowledge, optimization strategy identification, regulatory awareness
- **Blind spots:**
  - May not be current with latest tax changes
  - Cannot validate against official sources
  - May provide advice that crosses regulatory boundaries
- **Failure modes:**
  - Outdated information
  - Advice that constitutes unauthorized practice
  - Over-confident recommendations

**Scope Boundary:**
> "French-tax-optimizer provides ADVISORY information only. All tax interpretations MUST be verified against official sources. Human approval required for tax rule changes."

**Interaction Patterns:**
- **Receives:** Tax rule change requests, interpretation questions
- **Outputs:** Tax interpretation, optimization scenarios, source citations
- **Dependencies:** Works with legal-compliance-reviewer for regulatory check

**Constraints:**
1. Output is advisory, not prescriptive
2. Must cite official sources where possible
3. Cannot recommend "you should do X"
4. Human approval required before implementing tax changes

**Domain Translation Required:** None (native domain)

---

### 2.2 legal-compliance-reviewer

**Cognitive Profile:**
- **Mental model:** Regulatory compliance checker
- **Strengths:** Identifying regulatory risks, compliance requirements, disclaimer adequacy
- **Blind spots:**
  - May be overly conservative
  - May not understand business tradeoffs
  - Cannot provide definitive legal opinions
- **Failure modes:**
  - Over-blocks valid features
  - False positives on compliant code
  - May miss edge-case violations

**Scope Boundary:**
> "Legal-compliance identifies risks and requirements. Legal-compliance does not provide legal advice. Professional legal review required for production deployment."

**Interaction Patterns:**
- **Receives:** Tax/investment changes, compliance review requests
- **Outputs:** Compliance assessment, disclaimer requirements, risk evaluation
- **Dependencies:** Works with french-tax-optimizer for domain context

**Constraints:**
1. Output is risk identification, not legal advice
2. Escalate uncertain issues to human
3. Cannot approve for production without human review

---

## Part 3: Conditional Agents

### 3.1 antoine-nlp-expert

**Cognitive Profile:**
- **Mental model:** LLM/NLP specialist
- **Strengths:** Prompt engineering, LLM behavior analysis, NLP implementation
- **Blind spots:**
  - Does not understand financial domain
  - Cannot assess tax correctness of LLM outputs
  - May optimize for linguistic quality over accuracy
- **Failure modes:**
  - Prompts that sound good but give wrong tax information
  - Over-engineering prompt complexity
  - Missing domain-specific validation needs

**Scope Boundary:**
> "Antoine handles LLM/NLP implementation. Antoine does not validate financial correctness. Domain experts must review LLM outputs for accuracy."

**Activation Conditions:**
- Changes to `prompts/**`
- Changes to `src/llm/**`
- LLM behavior issues

**Domain Translation Required:**
- Must work with french-tax-optimizer for tax-related prompts
- Must work with legal-compliance-reviewer for advice scope

---

### 3.2 data-engineer-sophie

**Cognitive Profile:**
- **Mental model:** Data pipeline architect
- **Strengths:** ETL design, data quality, extraction pipelines, data validation
- **Blind spots:**
  - Does not understand document content semantics
  - Cannot validate financial accuracy of extracted data
  - May over-engineer for simple extractions
- **Failure modes:**
  - Complex pipelines for simple needs
  - Missing edge cases in extraction
  - Data quality issues from misunderstanding domain

**Scope Boundary:**
> "Sophie handles data pipelines and extraction. Sophie does not validate financial meaning of extracted values."

**Activation Conditions:**
- Changes to `src/extractors/**`
- Data quality issues
- New document type support

---

### 3.3 legal-team-lead

**Cognitive Profile:**
- **Mental model:** Legal escalation coordinator
- **Strengths:** Cross-domain legal coordination, escalation management
- **Blind spots:**
  - Higher-level view may miss details
  - Not specialized in tax law
- **Failure modes:**
  - Over-escalation of simple issues
  - Coordination overhead

**Scope Boundary:**
> "Legal-team-lead coordinates legal escalations. Only invoke via legal-compliance-reviewer."

**Activation Conditions:**
- Escalation from legal-compliance-reviewer
- Cross-domain legal questions

---

## Part 4: System Agents

### 4.1 Explore

**Usage:** Direct call OK for:
- Finding files by pattern
- Searching code for keywords
- Understanding codebase structure

**When to use Yoni instead:**
- Complex exploration requiring multiple rounds
- Exploration that might need other agents

### 4.2 Plan

**Usage:** Direct call OK for:
- Architecture design
- Implementation planning
- Technical documentation

**When to use Yoni instead:**
- Planning that affects multiple domains
- Planning requiring domain expertise

### 4.3 general-purpose

**Usage:** Multi-step research tasks, complex file operations

**When to use Yoni instead:**
- Tasks requiring specialized domain agents

### 4.4 claude-code-guide

**Usage:** Questions about Claude Code tools and features

**When to use Yoni instead:**
- Generally use directly, no Yoni needed

---

## Part 5: Agent Interaction Patterns

### 5.1 The Standard Development Flow

```
User Request
    ↓
yoni-orchestrator (ENTRY)
    ↓
[Implementation Work]
    ↓
quality-control-enforcer
    ↓
it-core-clovis
    ↓
wealon-regulatory-auditor (EXIT)
    ↓
Complete
```

### 5.2 The Tax Change Flow

```
Tax Change Request
    ↓
yoni-orchestrator (ENTRY)
    ↓
french-tax-optimizer (interpretation)
    ↓
legal-compliance-reviewer (risk check)
    ↓
[Implementation]
    ↓
quality-control-enforcer
    ↓
it-core-clovis
    ↓
wealon-regulatory-auditor (EXIT)
    ↓
HUMAN APPROVAL REQUIRED
    ↓
Complete
```

### 5.3 The LLM Change Flow

```
LLM/Prompt Change
    ↓
yoni-orchestrator (ENTRY)
    ↓
antoine-nlp-expert (prompt quality)
    ↓
cybersecurity-expert-maxime (injection risk)
    ↓
legal-compliance-reviewer (advice scope)
    ↓
[Implementation]
    ↓
quality-control-enforcer
    ↓
wealon-regulatory-auditor (EXIT)
    ↓
Complete
```

### 5.4 The Data Pipeline Flow

```
Extraction Change
    ↓
yoni-orchestrator (ENTRY)
    ↓
data-engineer-sophie (pipeline design)
    ↓
[Implementation]
    ↓
quality-control-enforcer
    ↓
it-core-clovis
    ↓
wealon-regulatory-auditor (EXIT)
    ↓
Complete
```

### 5.5 The RESEARCH Flow (algorithm_unclear)

```
Algorithm Uncertainty
    ↓
yoni-orchestrator (ENTRY)
    ↓
alexios-ml-predictor (algorithm analysis)
    ↓
pierre-jean-ml-advisor (ML guidance)
    ↓
[Research artifacts: research-brief.md, approach-options.md]
    ↓
wealon-regulatory-auditor (EXIT)
    ↓
Complete
```

### 5.6 The OPTIMIZATION Flow (performance_risk)

```
Performance-Critical Change
    ↓
yoni-orchestrator (ENTRY)
    ↓
alexios-ml-predictor (profiling, benchmarking)
    ↓
it-core-clovis (code quality)
    ↓
[Implementation with performance targets]
    ↓
quality-control-enforcer
    ↓
wealon-regulatory-auditor (EXIT)
    ↓
Complete
```

---

**Document Status:** v1.1 — Aligned with WORKFLOW_RULES.md v2.0
