# Friction Map — Agent Ecosystem Analysis

**Version:** 1.0
**Created:** 2026-01-20
**Purpose:** Phase 5 — Identify overlaps, gaps, handoffs, and conflicts

---

## Part 1: Overlaps

### Where do agents' responsibilities intersect?

| Overlap | Agents | Friction Type | Severity | Resolution |
|---------|--------|---------------|----------|------------|
| Code quality review | QC + Clovis | Dual review | MEDIUM | Sequential: QC first (substance), Clovis second (process) |
| Tax interpretation | french-tax-optimizer + legal-compliance | Domain overlap | MEDIUM | french-tax interprets, legal validates compliance |
| Audit authority | Wealon + QC | Scope overlap | LOW | QC: implementation quality. Wealon: overall completion |
| LLM content review | antoine-nlp + french-tax | Content vs. form | MEDIUM | antoine: prompt quality. french-tax: content accuracy |

### Overlap Details

#### Overlap 1: Code Quality Review (QC + Clovis)

**Agents involved:** quality-control-enforcer, it-core-clovis
**What overlaps:** Both review code before commit
**Why it's friction:** Potentially conflicting feedback, redundant checks
**Resolution:**
- QC runs FIRST — validates implementation quality, catches shortcuts
- Clovis runs SECOND — validates git workflow, process compliance
- If conflict: QC's substance concerns override Clovis's process concerns

#### Overlap 2: Tax Interpretation (french-tax + legal)

**Agents involved:** french-tax-optimizer, legal-compliance-reviewer
**What overlaps:** Both have opinions on tax-related features
**Why it's friction:** Tax optimizer may suggest features legal deems risky
**Resolution:**
- french-tax-optimizer provides domain interpretation
- legal-compliance validates regulatory compliance
- If conflict: legal-compliance has VETO power on regulatory risk

#### Overlap 3: LLM Content (antoine-nlp + french-tax)

**Agents involved:** antoine-nlp-expert, french-tax-optimizer
**What overlaps:** LLM prompts contain tax content
**Why it's friction:** Good prompt ≠ accurate tax advice
**Resolution:**
- antoine-nlp handles prompt engineering (form)
- french-tax validates tax content (substance)
- BOTH must approve for LLM changes

---

## Part 2: Gaps

### What capabilities are missing?

| Gap | Description | Severity | Current Mitigation |
|-----|-------------|----------|-------------------|
| Tax accuracy validation | No agent validates calculations against official sources | **CRITICAL** | Human verification, source documentation |
| Multi-year tax planning | No agent handles multi-year optimization | HIGH | Document as limitation |
| French legal expertise | legal-compliance is general, not French-specific | MEDIUM | Defer to human legal review |
| User trust assessment | No agent evaluates if users will trust correctly | MEDIUM | UX design, disclaimers |
| Real-time data verification | No automated barème verification | HIGH | Manual verification checklist |

### Gap Details

#### Gap 1: Tax Accuracy Validation (CRITICAL)

**What's missing:** No agent can verify if tax calculations match official DGFIP rules
**Why it matters:** Core value proposition depends on accuracy
**Severity:** CRITICAL
**Current mitigation:**
- Document official sources in `docs/sources.md`
- Require human verification for barème updates
- Include source citations in JSON files
**Future resolution:** Consider automated verification against impots.gouv.fr

#### Gap 2: Multi-Year Tax Planning (HIGH)

**What's missing:** All agents operate on single-year calculations
**Why it matters:** Many optimizations (PER, LMNP, Girardin) have multi-year effects
**Severity:** HIGH
**Current mitigation:**
- Document limitation explicitly to users
- Recommend professional accountant for multi-year planning
**Future resolution:** Out of scope for v1.0

#### Gap 3: French Legal Expertise (MEDIUM)

**What's missing:** legal-compliance-reviewer is general, not French-specific
**Why it matters:** French regulatory landscape (AMF, DGFIP, CNIL) is specific
**Severity:** MEDIUM
**Current mitigation:**
- Escalate to human for French-specific legal questions
- Document French regulatory bodies in project-context
**Future resolution:** Professional legal review before production

#### Gap 4: User Trust Assessment (MEDIUM)

**What's missing:** No agent evaluates if UI/UX will cause appropriate trust calibration
**Why it matters:** Users may over-trust (act on bad advice) or under-trust (ignore good advice)
**Severity:** MEDIUM
**Current mitigation:**
- Include disclaimers throughout
- Use ranges instead of precise numbers
- Add "verify with accountant" prompts
**Future resolution:** User testing

#### Gap 5: Real-Time Data Verification (HIGH)

**What's missing:** No automated verification of barème data against official sources
**Why it matters:** Outdated barèmes = all calculations wrong
**Severity:** HIGH
**Current mitigation:**
- Manual verification checklist
- Add `verified_date` to JSON files
**Future resolution:** Consider automated scraping/verification

---

## Part 3: Handoffs

### How do agents transfer work to each other?

| Handoff | From | To | Trigger | Contract |
|---------|------|-----|---------|----------|
| Entry → Work | yoni-orchestrator | Domain agents | Request routing | Task description |
| Tax interpretation | french-tax-optimizer | Implementation | Interpretation approved | Verified tax logic |
| Code → QC | Implementation | quality-control | Code complete | PR-ready code |
| QC → Clovis | quality-control | it-core-clovis | QC passed | QC approval |
| Review → Audit | it-core-clovis | wealon | Clovis passed | Review approval |
| LLM prompt → Tax | antoine-nlp | french-tax-optimizer | Prompt drafted | Prompt for review |

### Handoff Contract: Tax Change

```yaml
handoff:
  from: french-tax-optimizer
  to: implementation
  trigger: Tax interpretation provided
  required_artifacts:
    - Tax rule interpretation
    - Source citations (BOI, CGI)
    - Confidence assessment
  acceptance_criteria:
    - Official source cited
    - Interpretation clear and implementable
    - No prescriptive advice
```

### Handoff Contract: Code Review

```yaml
handoff:
  from: quality-control-enforcer
  to: it-core-clovis
  trigger: QC review complete
  required_artifacts:
    - QC assessment (PASS/FAIL)
    - Issues list (if any)
  acceptance_criteria:
    - All CRITICAL issues resolved
    - HIGH issues addressed or documented
    - Code is complete, not shortcut
```

### Handoff Contract: Final Audit

```yaml
handoff:
  from: it-core-clovis
  to: wealon-regulatory-auditor
  trigger: Process review complete
  required_artifacts:
    - Clovis assessment (PASS/FAIL)
    - Git workflow compliance
  acceptance_criteria:
    - Process followed
    - Ready for final audit
```

---

## Part 4: Conflicts

### Where might agents disagree?

| Conflict | Agents | Scenario | Resolution |
|----------|--------|----------|------------|
| Quality vs. Process | QC vs. Clovis | QC says incomplete, Clovis says process OK | QC takes precedence (substance > process) |
| Risk tolerance | french-tax vs. legal | Tax optimizer suggests feature, legal says risky | Legal has VETO on regulatory risk |
| Velocity vs. Quality | Any vs. Wealon | Agents approve, Wealon finds issues | Wealon BLOCKS until resolved |
| LLM content | antoine-nlp vs. french-tax | Good prompt, wrong tax content | french-tax takes precedence for content |

### Conflict Resolution Hierarchy

When agents disagree, follow this hierarchy:

1. **Regulatory/Compliance** (legal-compliance, wealon) — ABSOLUTE PRIORITY
2. **Domain Accuracy** (french-tax-optimizer) — HIGH PRIORITY for tax content
3. **Implementation Quality** (quality-control) — Should be resolved
4. **Process Compliance** (it-core-clovis) — Can be overridden with justification
5. **Optimization** (any other) — Lowest priority

### Conflict Example: Tax Feature Risk

**Scenario:** french-tax-optimizer suggests implementing Girardin recommendations with estimated returns. legal-compliance-reviewer says this may constitute unauthorized investment advice.

**Resolution:**
1. legal-compliance has VETO
2. Options:
   - Remove feature
   - Add sufficient disclaimers for legal approval
   - Escalate to human for legal review
3. Cannot proceed without legal clearance

---

## Part 5: Friction Severity Summary

| Category | Count | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Overlaps | 4 | 0 | 0 | 3 | 1 |
| Gaps | 5 | 1 | 2 | 2 | 0 |
| Handoffs | 6 | 0 | 0 | 0 | 0 |
| Conflicts | 4 | 0 | 1 | 2 | 1 |
| **TOTAL** | **19** | **1** | **3** | **7** | **2** |

### Critical Items Requiring Attention

1. **Gap: Tax Accuracy Validation** — No automated verification of calculations
   - Impact: Core value proposition at risk
   - Mitigation: Human verification + source documentation
   - Action: Consider automated verification for v2.0

---

## Part 6: Friction Resolution Action Plan

| Priority | Friction | Resolution | Owner |
|----------|----------|------------|-------|
| 1 | Tax accuracy gap | Manual verification checklist + sources | Human |
| 2 | Legal compliance conflict | Legal VETO authority established | Documented |
| 3 | QC/Clovis overlap | Sequential execution defined | Documented |
| 4 | Multi-year planning gap | Document as limitation | Documentation |
| 5 | Real-time verification gap | Add verified_date to JSON | Implementation |

---

**Document Status:** Complete — Ready for Phase 6 simulations.
