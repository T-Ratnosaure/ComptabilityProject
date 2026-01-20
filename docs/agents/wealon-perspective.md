# Auditor Perspective: Wealon's View

**Version:** 1.0
**Created:** 2026-01-20
**Perspective:** Auditor / Risk Assessor
**Bias:** "What could go wrong?"

---

## Executive Summary

From an audit perspective, ComptabilityProject has **significant unresolved risks** that require attention before production deployment. While the technical architecture is sound and the agent ecosystem is well-structured, the regulatory compliance, data accuracy, and liability exposure are concerning.

**Overall Assessment:** CONDITIONAL PASS — Acceptable for development, NOT READY for production without addressing critical findings.

---

## Part 1: Critical Findings

### Finding 1: CRITICAL — No Automated Tax Accuracy Verification

**Observation:** The system calculates French income tax based on JSON files (`baremes_2024.json`, `baremes_2025.json`) that are manually maintained.

**Evidence:**
- `src/tax_engine/data/baremes_2024.json`
- `src/tax_engine/data/baremes_2025.json`
- No verification mechanism against official sources

**Risk Assessment:** If these files contain errors, ALL tax calculations will be wrong. Users may make financial decisions based on incorrect information.

**What Could Go Wrong:**
- Barème values are transcribed incorrectly
- Tax law changes are missed
- Users lose money or face penalties
- Liability exposure for the project

**Recommendation:**
1. Add `verified_date` and `source_url` to JSON files
2. Create verification checklist with human sign-off
3. Consider automated verification for v2.0
4. Add disclaimer: "Verify calculations with official sources"

---

### Finding 2: CRITICAL — Investment Recommendations May Be Unauthorized

**Observation:** The system recommends investment strategies (LMNP, FCPI/FIP, Girardin) that may constitute regulated investment advice.

**Evidence:**
- `src/analyzers/strategies/lmnp_strategy.py`
- `src/analyzers/strategies/fcpi_fip_strategy.py`
- `src/analyzers/strategies/girardin_strategy.py`
- Recommendations include specific investment types with projected returns

**Risk Assessment:** Providing investment advice without proper licensing (CIF - Conseiller en Investissements Financiers) is illegal in France under AMF regulations.

**What Could Go Wrong:**
- Regulatory action from AMF
- User financial losses from following advice
- Legal liability for unauthorized practice
- Reputational damage

**Recommendation:**
1. **Immediate:** Legal review of investment recommendation features
2. **Option A:** Remove investment recommendations entirely
3. **Option B:** Reframe as "informational scenarios" with heavy disclaimers
4. **Option C:** Obtain CIF licensing (complex, expensive)
5. Add disclaimer: "This is not investment advice"

---

### Finding 3: HIGH — LLM Advice Scope Not Enforced

**Observation:** The LLM (Claude 3.5 Sonnet) can respond to tax questions without hard limits on prescriptive advice.

**Evidence:**
- `prompts/system/base.md` contains guidelines but not hard limits
- `src/llm/llm_service.py` does not filter prescriptive outputs
- No post-processing validation of LLM responses

**Risk Assessment:** Users may receive advice that sounds like professional tax counsel, leading to over-reliance and potential harm.

**What Could Go Wrong:**
- LLM gives prescriptive advice ("you should do X")
- User acts on advice without verification
- LLM hallucinates tax deductions/rules
- User faces penalties or financial loss

**Recommendation:**
1. Add explicit system prompt constraints
2. Implement output filtering for prescriptive language
3. Add disclaimer to every LLM response
4. Consider post-processing validation

---

### Finding 4: HIGH — Data Retention Policy Not Implemented

**Observation:** The system stores sensitive financial data without clear retention policy or deletion capability.

**Evidence:**
- User documents stored in `data/uploads/`
- Extracted financial data in database
- No automated cleanup
- No "delete my data" feature visible

**Risk Assessment:** GDPR (CNIL in France) requires clear data retention and user deletion rights.

**What Could Go Wrong:**
- CNIL audit finds violation
- Users cannot exercise deletion rights
- Data breach exposes financial information
- Regulatory fines

**Recommendation:**
1. Implement data retention policy (proposed: 90 days documents, 1 year calculations)
2. Add "Delete my data" button in UI
3. Implement automated cleanup jobs
4. Document retention policy in Terms of Service

---

### Finding 5: MEDIUM — Disclaimers Are Insufficient

**Observation:** Current disclaimers are present but may not be prominent or comprehensive enough.

**Evidence:**
- Disclaimers exist in some areas
- Not present on every page/result
- Investment recommendations lack specific disclaimers
- LLM responses lack disclaimers

**Risk Assessment:** Users may not see or understand disclaimers, leading to over-reliance.

**What Could Go Wrong:**
- User misses disclaimer
- User relies on system as professional advice
- Liability exposure when things go wrong

**Recommendation:**
1. Add disclaimer to every page with calculations
2. Add disclaimer to every LLM response
3. Add specific disclaimer for investment-related information
4. Require acknowledgment before using system

---

## Part 2: Process Audit

### Process 1: Tax Rule Change Process

**Current:**
1. Developer identifies need for tax rule change
2. french-tax-optimizer provides interpretation
3. legal-compliance reviews
4. Implementation
5. Testing
6. Human approval
7. Commit

**Audit Findings:**

| Step | Strength | Weakness |
|------|----------|----------|
| french-tax interpretation | Domain expertise | May be outdated |
| legal-compliance review | Risk identification | General, not French-specific |
| Human approval | Accountability | Potential bottleneck |
| Testing | Coverage | No verification against official sources |

**Gap:** No step verifies calculation against official DGFIP sources.

**Recommendation:** Add verification step with checklist:
- [ ] Calculation matches impots.gouv.fr example
- [ ] Source URL documented
- [ ] Verified date recorded

---

### Process 2: LLM Change Process

**Current:**
1. Developer modifies prompt
2. antoine-nlp reviews
3. cybersecurity checks injection risk
4. legal-compliance reviews scope
5. Implementation
6. Testing
7. Commit

**Audit Findings:**

| Step | Strength | Weakness |
|------|----------|----------|
| antoine-nlp review | Prompt quality | No tax accuracy check |
| cybersecurity review | Injection prevention | Good |
| legal-compliance | Scope check | May miss edge cases |
| Testing | Functionality | No output validation |

**Gap:** No step validates that LLM outputs are factually correct for tax content.

**Recommendation:** Add output validation step:
- Test with known tax scenarios
- Verify responses are accurate
- Check for prescriptive language

---

## Part 3: Documentation Audit

### Document: AGENTS.md

**Strengths:**
- Clear classification of agents
- Explicit rejections with rationale
- Workflow integration documented

**Weaknesses:**
- Human checkpoints could be more explicit
- Escalation paths not fully defined
- Appeal process not documented

**Recommendation:** Add explicit escalation and appeal procedures.

---

### Document: project-context.md

**Strengths:**
- Comprehensive domain model
- Clear assumptions register
- Risk profile documented

**Weaknesses:**
- Non-goals could be more prominent
- Regulatory bodies section could be expanded
- Official sources section could include BOI references

**Recommendation:** Expand regulatory section with specific references.

---

### Document: decisions.md

**Strengths:**
- Good decision format with rationale
- Open questions documented
- Technical debt tracked

**Weaknesses:**
- Some critical decisions marked as "OPEN"
- Investment recommendation decision needs resolution
- Consequences not fully traced

**Recommendation:** Resolve critical open decisions before production.

---

## Part 4: Risk Register

| ID | Risk | Likelihood | Impact | Current Mitigation | Adequacy |
|----|------|------------|--------|-------------------|----------|
| R1 | Tax calculation incorrect | MEDIUM | HIGH | Manual JSON maintenance | INADEQUATE |
| R2 | Unauthorized investment advice | HIGH | CRITICAL | None | INADEQUATE |
| R3 | LLM provides bad advice | MEDIUM | HIGH | System prompts | PARTIAL |
| R4 | GDPR violation | MEDIUM | HIGH | None | INADEQUATE |
| R5 | User over-reliance | HIGH | MEDIUM | Disclaimers | PARTIAL |
| R6 | Barème outdated | MEDIUM | HIGH | Manual verification | PARTIAL |
| R7 | OCR extraction error | MEDIUM | MEDIUM | Graceful degradation | ADEQUATE |
| R8 | Prompt injection | LOW | MEDIUM | Sanitization | ADEQUATE |

### Risk Summary

- **INADEQUATE:** 3 risks (R1, R2, R4)
- **PARTIAL:** 3 risks (R3, R5, R6)
- **ADEQUATE:** 2 risks (R7, R8)

---

## Part 5: Comparison to Builder Perspective

| Topic | Builder (Yoni) Says | I (Wealon) Say |
|-------|---------------------|----------------|
| Overall readiness | 8/10, ready with checkpoints | 6/10, needs work before production |
| Tax accuracy | Acceptable with human oversight | Inadequate without verification |
| Investment recs | Keep with disclaimers | Remove or heavy legal review |
| Velocity tradeoff | Acceptable | Appropriate for domain |
| Agent ecosystem | Well-structured | Agree, but gaps exist |
| Human bottleneck | Necessary friction | Agree, but need SLA |

### Key Disagreements

1. **Tax accuracy:** Builder accepts human oversight as sufficient. I require verification mechanism.
2. **Investment recommendations:** Builder wants to keep with disclaimers. I recommend legal review and possible removal.
3. **Production readiness:** Builder says ready with checkpoints. I say NOT ready without addressing critical findings.

---

## Part 6: Audit Verdict

**Overall Assessment:** CONDITIONAL PASS

### Acceptable For:
- Development and testing
- Internal use
- Demo purposes
- Beta testing with informed users

### Inadequate For:
- Production deployment
- Public launch
- Users making real financial decisions

### Required Actions for Full Pass

| Priority | Action | Blocking |
|----------|--------|----------|
| 1 | Legal review of investment recommendations | YES |
| 2 | Add data verification mechanism for barèmes | YES |
| 3 | Implement GDPR data retention/deletion | YES |
| 4 | Strengthen disclaimers throughout | YES |
| 5 | Add LLM output validation | NO |
| 6 | Define human approval SLA | NO |

### Timeline for Resolution

| Action | Estimated Effort | Recommended Deadline |
|--------|------------------|---------------------|
| Legal review | External | Before production |
| Data verification | 1-2 days | Before production |
| GDPR compliance | 2-3 days | Before production |
| Disclaimer strengthening | 1 day | Before production |

---

## Part 7: Auditor's Bottom Line

**Can we ship this?** NOT YET.

**What must be fixed:**
1. Legal review of investment recommendations
2. Tax data verification mechanism
3. GDPR compliance features
4. Comprehensive disclaimers

**What I'm okay with:**
- Agent ecosystem structure
- Technical architecture
- Code quality processes
- Development workflows

**My recommendation:** DO NOT deploy to production until:
1. Critical findings are resolved
2. Legal review is completed
3. User can exercise data rights
4. Disclaimers are comprehensive

---

**Document Status:** Complete — Auditor perspective captured.
