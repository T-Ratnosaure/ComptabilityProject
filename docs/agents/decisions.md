# Design Decisions — ComptabilityProject

**Version:** 1.0
**Created:** 2026-01-20
**Status:** ACTIVE

---

## Decision Log

### D001: Agent Ecosystem Scope

**Date:** 2026-01-20
**Status:** DECIDED

**Context:**
The BMAD methodology requires defining which agents to use. CartesSociete (gaming) rejected all financial domain agents. ComptabilityProject IS a financial domain project.

**Options Considered:**

| Option | Pros | Cons |
|--------|------|------|
| A. Use all financial agents | Domain expertise | Over-complex, regulatory risk |
| B. Use no financial agents | Simple | Missing domain expertise |
| C. Use selected financial agents with constraints | Balanced | Requires careful governance |

**Decision:** Option C — Use selected financial agents with constraints

**Rationale:**
- `french-tax-optimizer` provides domain expertise but must be advisory only
- `legal-compliance-reviewer` is essential for regulatory compliance
- Trading/investment agents (backtester, trading-engine, etc.) are NOT relevant
- Financial risk agents are not directly applicable to tax context

**Consequences:**
- Must define clear boundaries for financial agent usage
- Must implement disclaimers when financial agents provide output
- Must maintain human approval for tax rule interpretations

---

### D002: Investment Recommendation Approach

**Date:** 2026-01-20
**Status:** DECIDED

**Context:**
The system recommends LMNP, FCPI/FIP, and Girardin investments. This may constitute regulated investment advice (Conseil en Investissement Financier).

**Options:**

| Option | Description | Risk |
|--------|-------------|------|
| A. Remove all investment recommendations | Safe but reduced value | LOW |
| B. Keep with heavy disclaimers | User value preserved | MEDIUM |
| C. Keep as "informational scenarios" | Reframe as education | MEDIUM |
| D. Obtain CIF license | Full compliance | HIGH (cost/complexity) |

**Decision:** Option C — Reframe as informational scenarios

**Rationale:**
- Provides user value without crossing into advice
- Consistent with "tax optimization" vs "investment advice" framing
- Requires strong disclaimer language
- No commercial relationships with providers (OQ001 resolved)

**Implementation Required:**
- Change prescriptive language ("Investissez X€") to conditional ("Si vous investissiez X€...")
- Add "Exemple illustratif" framing to all investment scenarios
- Use "environ" prefix and round amounts (e.g., "environ 5 800€")
- Add CIF consultation disclaimer to all investment-related content
- Strengthen disclaimers given no professional liability insurance (OQ002)

**Approved:** 2026-01-20 by project owner

---

### D003: False Precision in Estimates

**Date:** 2026-01-20
**Status:** DECIDED

**Context:**
The system displays estimates like "Économie potentielle: 5 847€". This implies precision that doesn't exist.

**Options:**

| Option | Example | Pros | Cons |
|--------|---------|------|------|
| A. Keep precise numbers | 5 847€ | Looks professional | False precision |
| B. Use ranges | 5 000€ - 6 500€ | Honest | More complex UI |
| C. Use rounded numbers | ~5 800€ | Simple, honest | Less satisfying |
| D. Use qualitative + number | "Environ 5 800€" | French natural | Requires translation |

**Decision:** Option D — Use qualitative language with rounded numbers

**Implementation:**
- Change "Économie potentielle: 5 847€" to "Économie potentielle estimée : environ 5 800 €"
- Add note: "Cette estimation dépend de votre situation personnelle"

**Consequences:**
- UI must accommodate longer text
- All estimate displays must be updated
- LLM prompts must use same language

---

### D004: LLM Scope Boundaries

**Date:** 2026-01-20
**Status:** DECIDED

**Context:**
The LLM (Claude 3.5 Sonnet) can answer questions about tax. Users may ask questions that cross into professional advice territory.

**Decision:** Implement hard scope limits

**Allowed:**
- Explain tax concepts
- Describe how calculations work
- Compare regime options with numbers
- Explain what optimization strategies exist

**NOT Allowed:**
- Say "you should do X"
- Recommend specific investment products
- Provide personalized advice without disclaimers
- Claim to replace professional accountants

**Implementation:**
- Update system prompt with explicit boundaries
- Add response filtering for prescriptive language
- Include disclaimer in every LLM response

---

### D005: Data Retention Policy

**Date:** 2026-01-20
**Status:** DECIDED

**Context:**
User documents contain sensitive financial data. GDPR requires clear retention policy.

**Decision:**
| Data Type | Retention | Deletion |
|-----------|-----------|----------|
| Uploaded documents | 90 days | Auto-delete |
| Extracted data | 1 year | User can delete anytime |
| Conversations | 30 days | Auto-cleanup (already implemented) |
| Tax calculations | 2 years | User can delete anytime |

**Implementation:**
- Add scheduled cleanup job
- Add "Delete my data" button in UI
- Document retention policy in ToS

---

### D006: Barème Verification Process

**Date:** 2026-01-20
**Status:** DECIDED

**Context:**
Tax barèmes in JSON files are the source of truth. If wrong, all calculations are wrong.

**Decision:** Implement verification checklist

**Process:**
1. Before each tax year, manually verify against impots.gouv.fr
2. Document verification date in JSON file
3. Add source URL in JSON metadata
4. Require human approval for any barème change

**Implementation:**
- Add `verified_date` and `source_url` to JSON files
- Create verification checklist document
- Add CI check for verification date freshness

---

## Open Questions (Resolved)

### OQ001: Commercial Relationships

**Question:** Are there commission relationships with Girardin/FCPI providers?

**Impact:** If yes, must be disclosed. May affect recommendation credibility.

**Status:** DECIDED — 2026-01-20

**Answer:** No commercial relationships exist with any investment providers (Girardin, FCPI/FIP, etc.)

**Consequence:** No disclosure required. Recommendations can be presented as neutral educational information.

---

### OQ002: Professional Liability Insurance

**Question:** Does the project carry professional liability insurance?

**Impact:** Affects risk tolerance for advice features.

**Status:** DECIDED — 2026-01-20

**Answer:** No professional liability insurance.

**Consequence:**
- Must strengthen all disclaimers
- Must use educational framing (not advice)
- Beta designation required to reduce liability exposure
- All investment scenarios must include CIF consultation recommendation

---

### OQ003: Beta vs Production Designation

**Question:** Should the system be marked as "beta" to reduce liability?

**Impact:** User expectations, legal positioning.

**Status:** DECIDED — 2026-01-20

**Answer:** Yes — Mark as Beta.

**Implementation:**
- Add "Beta" badge to all page headers
- Update page titles to include "(Beta)"
- Add beta disclaimer in footer
- Communicate that tool is in development phase

---

## Rejected Alternatives

### R001: Full ML-based Tax Optimization

**Rejected because:** Current rule-based system is more auditable and explainable. ML would introduce black-box decisions in a high-stakes domain.

**Reconsider if:** Regulatory environment allows ML-based financial advice with appropriate disclosures.

---

### R002: Real-time Filing Integration

**Rejected because:** Would require certification and integration with DGFIP systems. Out of scope for current phase.

**Reconsider if:** Product strategy shifts to B2B accounting software.

---

### R003: Multi-tenant Architecture

**Rejected because:** Current use case is single-user. Adding multi-tenancy would complicate data isolation.

**Reconsider if:** B2B model requires accountant managing multiple clients.

---

## Technical Debt Register

| ID | Debt | Impact | Plan | Status |
|----|------|--------|------|--------|
| TD001 | Barème JSON manually maintained | Data accuracy risk | ~~Implement automated verification~~ | **RESOLVED** (PR #32) |
| TD002 | No extraction confidence scores | User trust | ~~Add to document extraction~~ | **RESOLVED** (PR #33) |
| TD003 | Strategy interdependencies not modeled | Calculation accuracy | ~~Future enhancement~~ | **RESOLVED** (PR #33) |
| TD004 | No audit trail for calculations | Compliance | ~~Add logging~~ | **RESOLVED** (PR #31) |
| TD005 | Glossary not implemented | User confusion | ~~Create glossary page~~ | **RESOLVED** (PR #32) |

### TD001 Resolution Details

**Resolved:** 2026-01-20
**Implementation:** PR #32 - feat(td005-td001): Add glossary and barème verification

Components added:
- Added verification metadata to barème JSON files (verified_date, sources, checklist)
- Created `scripts/verify_baremes.py` automated verification script
- Supports `--strict` mode for CI integration
- Verifies field completeness, freshness, and bracket consistency

### TD002 Resolution Details

**Resolved:** 2026-01-20
**Implementation:** PR #33 - feat(td002-td003): Add confidence scores and strategy interdependencies

Components added:
- `ConfidenceLevel` enum (HIGH/MEDIUM/LOW/UNCERTAIN) for extraction confidence
- `FieldConfidence` and `ExtractionConfidenceReport` Pydantic models
- Multi-pattern matching with confidence boosting in base parser
- Updated `AvisImpositionParser` to return confidence reports
- Per-field confidence tracking with extraction method metadata

### TD003 Resolution Details

**Resolved:** 2026-01-20
**Implementation:** PR #33 - feat(td002-td003): Add confidence scores and strategy interdependencies

Components added:
- `InteractionType` enum (CONFLICT/SYNERGY/DEPENDENCY/NEUTRAL)
- `StrategyInteraction` model with impact modifiers and warnings
- 11 predefined strategy interactions (PER, LMNP, Girardin, FCPI/FIP, etc.)
- `StrategyInteractionChecker` for conflict/synergy detection
- Integration with `TaxOptimizer._generate_result()` for interaction metadata

### TD004 Resolution Details

**Resolved:** 2026-01-20
**Implementation:** PR #31 - feat(audit): Implement TD004 audit trail for tax calculations

Components added:
- `AuditLog` and `AuditEntry` SQLAlchemy models with 5-year retention
- `AuditLogger` service for non-blocking audit logging
- Full integration with `TaxCalculator` tracking all calculation steps
- REST API endpoints for audit trail retrieval and export
- Compliance with French tax authority documentation requirements

### TD005 Resolution Details

**Resolved:** 2026-01-20
**Implementation:** PR #32 - feat(td005-td001): Add glossary and barème verification

Components added:
- Interactive glossary page at `/glossary` with 30+ French tax terms
- Categories: Revenus, Régimes, Impôt, Cotisations, Hauts revenus, Optimisation, Administratif
- Search and category filtering functionality
- Related terms navigation
- Glossary link added to main navigation

---

**Document Status:** Working document — update as decisions are made.
