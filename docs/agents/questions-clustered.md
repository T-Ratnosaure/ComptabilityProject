# Human Questions — Clustered & Prioritized

**Version:** 1.0
**Created:** 2026-01-20
**Source:** BMAD Analysis Phase 2

---

## Question Classification

| Priority | Definition | Action |
|----------|------------|--------|
| **BLOCKING** | Must be answered before implementation | Stop work |
| **CRITICAL** | High risk if ignored | Address in current phase |
| **IMPORTANT** | Should be addressed | Plan for resolution |
| **EXPLORATORY** | Nice to know | Defer if needed |

---

## Cluster 1: Regulatory & Liability (BLOCKING)

**Theme:** Is this system operating within legal boundaries?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q14 | If a user is audited and cites this tool, what is the legal position? | BLOCKING | OPEN |
| Q58 | What if a user loses money on a Girardin investment recommended by the system? | BLOCKING | OPEN |
| Q68 | Would a financial regulator view this as unauthorized investment advice? | BLOCKING | OPEN |
| A3 | (Assumption) LLM provides "informational" advice, not "professional" tax advice | BLOCKING | NEEDS VALIDATION |
| A8 | (Assumption) Professional accountant NOT replaced, only augmented | BLOCKING | NEEDS VALIDATION |

**Resolution Required:** Legal review of regulatory compliance before production launch.

---

## Cluster 2: Investment Recommendations (CRITICAL)

**Theme:** The system recommends investments — is this appropriate?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q76 | The system recommends investments (LMNP, FCPI) — is this appropriate for a tax tool? | CRITICAL | OPEN |
| Q63 | Could the system be manipulated to recommend specific products? | CRITICAL | OPEN |
| Q11 | Is there a commission relationship with Girardin/FCPI providers (Profina mentioned)? | CRITICAL | OPEN |
| Q4 | What happens if the tool recommends Girardin and the user loses money? Who is liable? | CRITICAL | OPEN |

**Resolution Required:** Decision on whether to keep, remove, or caveat investment recommendations.

---

## Cluster 3: Data Accuracy & Trust (CRITICAL)

**Theme:** Can users trust the calculations?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q34 | When was `baremes_2024.json` last verified against official sources? | CRITICAL | OPEN |
| Q35 | Are the URSSAF rates (21.8% BNC, 12.8% BIC) still current? | CRITICAL | OPEN |
| Q58 | What if the barème data is wrong and all calculations are incorrect? | CRITICAL | OPEN |
| Q72 | If shown "Économie potentielle: 5 847€", would a user believe it? | CRITICAL | OPEN |
| Q79 | The precision of estimates (e.g., "5 847€") implies false precision | CRITICAL | OPEN |

**Resolution Required:** Implement automated verification of tax data against official sources.

---

## Cluster 4: LLM Behavior & Safety (CRITICAL)

**Theme:** Is the LLM safe and appropriate?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q60 | What if the LLM hallucinates a non-existent tax deduction? | CRITICAL | OPEN |
| Q77 | The LLM gives "informational" advice — but users may treat it as professional advice | CRITICAL | OPEN |
| Q70 | What is the attack surface for prompt injection in the LLM? | CRITICAL | PARTIALLY ADDRESSED |
| Q82 | How does the user know what the LLM cannot do? | CRITICAL | OPEN |

**Resolution Required:** Implement LLM output validation and clear scope communication.

---

## Cluster 5: Document Extraction Quality (IMPORTANT)

**Theme:** Are extracted values reliable?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q61 | What if the OCR misreads a critical number? | IMPORTANT | OPEN |
| Q44 | What happens if OCR extracts "15 000" as "15000" vs "15,000"? | IMPORTANT | OPEN |
| Q46 | What is the confidence threshold for field extraction? | IMPORTANT | OPEN |
| Q40 | How does the system handle partial document extraction failures? | IMPORTANT | PARTIALLY ADDRESSED |
| Q41 | Is there a manual override for incorrectly extracted values? | IMPORTANT | OPEN |

**Resolution Required:** Add extraction confidence scores and manual override capability.

---

## Cluster 6: Calculation Model Limitations (IMPORTANT)

**Theme:** Does the model accurately represent tax reality?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q50 | How are interdependent strategies (e.g., PER affects TMI affects Girardin) modeled? | IMPORTANT | OPEN |
| Q51 | Is the optimization ranking by impact reliable when impacts are correlated? | IMPORTANT | OPEN |
| Q52 | Can the system model multi-year optimization? | IMPORTANT | NO — Documented limitation |
| Q53 | How does the system handle uncertainty in projected savings? | IMPORTANT | OPEN |

**Resolution Required:** Document model limitations clearly; consider cascading calculations.

---

## Cluster 7: Accounting Semantics (IMPORTANT)

**Theme:** Are terms used correctly and consistently?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q17 | When the system says "Revenu Net Imposable", does it mean RNI before or after abattements? | IMPORTANT | NEEDS DEFINITION |
| Q18 | Is "Résultat BNC" gross revenue or profit after expenses? | IMPORTANT | NEEDS DEFINITION |
| Q20 | Is "TMI" the marginal rate or the effective rate? | IMPORTANT | NEEDS DEFINITION |
| Q32 | Are social contributions (CSG/CRDS) handled separately from income tax? | IMPORTANT | NEEDS VERIFICATION |

**Resolution Required:** Create glossary with official definitions.

---

## Cluster 8: Data Governance & Privacy (IMPORTANT)

**Theme:** Is user data handled appropriately?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q38 | What is the data retention policy for user documents? | IMPORTANT | OPEN |
| Q39 | Can users delete their data (GDPR Article 17)? | IMPORTANT | OPEN |
| Q67 | Would a CNIL audit find GDPR compliance issues? | IMPORTANT | OPEN |
| Q69 | Is PII (revenu, situation familiale) adequately protected? | IMPORTANT | PARTIALLY ADDRESSED |

**Resolution Required:** Implement explicit data retention policy and deletion workflow.

---

## Cluster 9: User Experience & Trust (EXPLORATORY)

**Theme:** Does the UX build appropriate trust?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q74 | Does the system explain WHY a recommendation is made? | EXPLORATORY | OPEN |
| Q75 | Can a user verify the calculation against their own knowledge? | EXPLORATORY | OPEN |
| Q80 | How does the user know the data sources for tax rules? | EXPLORATORY | OPEN |
| Q81 | How does the user know the limitations of the calculations? | EXPLORATORY | OPEN |

**Resolution Required:** Add "show calculation" and "learn more" features.

---

## Cluster 10: Business Model Questions (EXPLORATORY)

**Theme:** How does the business model affect product decisions?

| ID | Question | Priority | Status |
|----|----------|----------|--------|
| Q5 | Is the business model subscription-based, freemium, or one-time purchase? | EXPLORATORY | OPEN |
| Q10 | Who benefits financially if the savings estimates are optimistic? | EXPLORATORY | OPEN |
| Q12 | What is the commercial pressure to show high savings estimates? | EXPLORATORY | OPEN |
| Q13 | How will success be measured? | EXPLORATORY | OPEN |

**Resolution Required:** Define business model and success metrics.

---

## Summary: Action Items

| Cluster | Priority | Immediate Action |
|---------|----------|------------------|
| 1. Regulatory & Liability | BLOCKING | Schedule legal review |
| 2. Investment Recommendations | CRITICAL | Decision: keep/remove/caveat |
| 3. Data Accuracy | CRITICAL | Verify barèmes against sources |
| 4. LLM Safety | CRITICAL | Implement output validation |
| 5. Document Extraction | IMPORTANT | Add confidence scores |
| 6. Calculation Model | IMPORTANT | Document limitations |
| 7. Accounting Semantics | IMPORTANT | Create glossary |
| 8. Data Governance | IMPORTANT | GDPR compliance review |
| 9. User Experience | EXPLORATORY | Plan UX improvements |
| 10. Business Model | EXPLORATORY | Define metrics |

---

**Document Status:** Working document — update as questions are resolved.
