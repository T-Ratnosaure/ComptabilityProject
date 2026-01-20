# Project Context — ComptabilityProject Domain Bible

**Version:** 1.0
**Created:** 2026-01-20
**Status:** ACTIVE

---

## 1. Project Overview

**Name:** ComptabilityProject
**Type:** French Tax Optimization System for Freelancers
**Domain:** Personal taxation, French fiscal law, financial planning
**Jurisdiction:** France (exclusively)

### 1.1 Core Purpose

Provide French freelancers with:
1. **Document Extraction** — Parse tax documents (Avis d'Imposition, 2042, URSSAF, BNC/BIC)
2. **Tax Calculation** — Apply official French tax rules (barèmes 2024/2025)
3. **Optimization Analysis** — Identify potential savings strategies
4. **Conversational Interface** — LLM-powered Q&A about tax situations

### 1.2 What This System Is NOT

| NOT This | Why |
|----------|-----|
| Licensed accountant (Expert-Comptable) | Regulated profession, requires license |
| Professional tax advisor (Conseil Fiscal) | Regulated activity under French law |
| Investment advisor (CIF) | Requires AMF registration |
| Tax filing service | Does not submit to DGFIP |
| Binding tax calculation | Only informational |

### 1.3 Regulatory-First Interpretation

**This project uses global BMAD workflows (WORKFLOW_RULES.md v2.0), but they must be interpreted through a tax compliance lens:**

| Global Concept | Tax Domain Interpretation |
|----------------|---------------------------|
| **RESEARCH workflow** | Tax rule interpretation, legal ambiguity resolution, accounting semantics — NOT ML experimentation |
| **OPTIMIZATION workflow** | Risk reduction, clarity, explainability, conservative compliance — NOT aggressive tax minimization |
| **algorithm_unclear trigger** | Tax calculation method uncertainty, regulatory interpretation — NOT ML model selection |
| **performance_risk trigger** | Audit trail integrity, calculation accuracy, source verification — NOT latency optimization |
| **ML agents (alexios, pierre-jean)** | Available for complexity analysis — NOT encouragement to use ML models |

**Core Principle:** Deterministic, auditable logic is ALWAYS preferred over ML approaches unless explicitly justified and approved.

> "Optimization" in this project means **reducing regulatory risk and improving clarity**, not maximizing tax savings.

---

## 2. Domain Model

### 2.1 Core Entities

| Entity | Description | Source of Truth |
|--------|-------------|-----------------|
| **FreelanceProfile** | User's fiscal identity (régime, revenus, parts) | User input + extracted documents |
| **TaxDocument** | Uploaded tax documents | OCR/PDF extraction |
| **TaxCalculation** | Computed tax liability | Tax engine (barèmes JSON) |
| **Recommendation** | Optimization strategy suggestion | Rules engine |
| **Conversation** | LLM interaction history | Database |

### 2.2 Tax Regimes Supported

| Régime | Type | URSSAF Rate | Abattement |
|--------|------|-------------|------------|
| Micro-BNC | Liberal profession | 21.8% | 34% |
| Micro-BIC (services) | Commercial services | 21.8% | 50% |
| Micro-BIC (ventes) | Commercial sales | 12.8% | 71% |
| Réel simplifié | Full accounting | Variable | Actual expenses |

### 2.3 Optimization Strategies

| Strategy | Type | Risk Level | Regulatory Concern |
|----------|------|------------|-------------------|
| Régime comparison | Tax regime choice | LOW | None |
| PER (Plan Épargne Retraite) | Retirement savings | LOW | None |
| Simple deductions | Dons, services | LOW | None |
| LMNP | Real estate investment | MEDIUM | May require CIF advice |
| FCPI/FIP | Innovation funds | MEDIUM | May require CIF advice |
| Girardin Industriel | Overseas investment | HIGH | May require CIF advice |
| Company structure | SASU/EURL/Holding | HIGH | Requires professional advice |

---

## 3. Stakeholders

### 3.1 Primary Users

| Persona | Description | Sophistication |
|---------|-------------|----------------|
| Solo freelancer | Micro-entrepreneur, simple situation | LOW |
| Established freelancer | BNC/BIC, accountant relationship | MEDIUM |
| High-earning freelancer | Complex optimization needs | HIGH |

### 3.2 Regulatory Bodies

| Body | Concern | Risk |
|------|---------|------|
| DGFIP | Tax accuracy, compliance | HIGH |
| AMF | Investment advice licensing | CRITICAL |
| CNIL | Personal data protection | MEDIUM |
| Ordre des Experts-Comptables | Unauthorized practice | MEDIUM |

---

## 4. Architecture Overview

### 4.1 Backend (Python/FastAPI)

```
src/
├── api/routes/          # REST endpoints
├── models/              # Pydantic domain models
├── database/            # SQLAlchemy ORM
├── extractors/          # Document processing
├── tax_engine/          # Calculation core
├── analyzers/           # Optimization strategies
├── llm/                 # Claude integration
└── security/            # PII protection
```

### 4.2 Frontend (Next.js)

```
frontend/
├── app/                 # Pages (dashboard, simulator, chat)
├── components/          # React components
└── lib/                 # API client
```

### 4.3 Data Flow

```
User Document → OCR/PDF Extraction → Field Parsing → Validation
                                          ↓
                                   FreelanceProfile
                                          ↓
Tax Calculation ← barèmes JSON ← Official Sources (impots.gouv.fr)
      ↓
Optimization Analysis ← Rules JSON
      ↓
Recommendations → LLM Context → Conversational Response
```

---

## 5. Constraints & Assumptions

### 5.1 Hard Constraints

| Constraint | Impact |
|------------|--------|
| French jurisdiction only | No international tax |
| Individual taxation only | No corporate tax (IS) |
| 2024-2025 fiscal years | No historical calculations |
| Informational only | No filing capability |

### 5.2 Assumptions (Flagged)

| ID | Assumption | Confidence | Risk |
|----|------------|------------|------|
| A1 | User is a French tax resident | HIGH | Wrong calculations |
| A2 | Document extraction is accurate | MEDIUM | Cascading errors |
| A3 | Tax rules in JSON are current | MEDIUM | Outdated advice |
| A4 | User understands disclaimers | LOW | Liability exposure |
| A5 | LLM does not hallucinate | LOW | False advice |

---

## 6. Risk Profile

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Barème out of date | MEDIUM | HIGH | Automated verification |
| OCR extraction error | MEDIUM | MEDIUM | Confidence scores |
| LLM hallucination | MEDIUM | HIGH | Scope limits, validation |
| Database data loss | LOW | HIGH | Backups |

### 6.2 Regulatory Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Unlicensed tax advice | MEDIUM | CRITICAL | Disclaimers, scope limits |
| Unlicensed investment advice | HIGH | CRITICAL | Remove/caveat investment recs |
| GDPR violation | LOW | HIGH | Consent workflow, data retention |
| DGFIP challenge | LOW | MEDIUM | Source citations |

### 6.3 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| User financial loss | MEDIUM | HIGH | Strong disclaimers |
| Reputation damage | MEDIUM | HIGH | Quality controls |
| Liability claims | LOW | CRITICAL | Legal review, ToS |

---

## 7. Non-Goals (Explicitly Out of Scope)

1. **Corporate taxation** (IS, TVA)
2. **International taxation** (non-resident rules)
3. **Real-time tax filing** (submission to DGFIP)
4. **Multi-year planning** (beyond current + previous year)
5. **Inheritance and succession planning**
6. **Wealth management beyond tax optimization**

---

## 8. Expected Evolution

### Phase 7+ Possibilities (NOT YET PLANNED)

| Evolution | Dependency |
|-----------|------------|
| Multi-year projections | Model complexity |
| API for accountants | B2B pivot |
| Mobile application | Frontend rewrite |
| Additional document types | Extraction development |
| Real filing capability | Regulatory approval |

---

## 9. Source Documentation

### Official Sources (Authoritative)

| Source | URL | Used For |
|--------|-----|----------|
| impots.gouv.fr | https://www.impots.gouv.fr | Barèmes, rules |
| URSSAF | https://www.urssaf.fr | Social contributions |
| BOFiP (Bulletin Officiel des Finances Publiques) | https://bofip.impots.gouv.fr | Official interpretations |
| Légifrance | https://www.legifrance.gouv.fr | Tax code text |

---

**Document Status:** BASELINE v1.0 — Changes require versioning and approval.
