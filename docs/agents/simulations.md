# Impact Simulations — ComptabilityProject

**Version:** 1.0
**Created:** 2026-01-20
**Purpose:** Phase 6 — Simulate effects of major decisions before implementation

---

## Simulation Methodology

For each proposed change:
1. Define the change
2. Identify first-order effects (immediate)
3. Identify second-order effects (ripples)
4. Identify third-order effects (emergent)
5. Make verdict: **IMPLEMENT** / **REJECT** / **DEFER** / **CONDITIONAL**

---

## Simulation 1: Enforce Yoni-First Rule

### Change Description
Every user request MUST go through yoni-orchestrator as entry point.

### First-Order Effects
| Effect | Impact |
|--------|--------|
| All requests are routed consistently | POSITIVE |
| Complexity triggers are always evaluated | POSITIVE |
| Simple tasks have routing overhead | NEGATIVE |

### Second-Order Effects
| Effect | Impact |
|--------|--------|
| Workflow selection becomes deterministic | POSITIVE |
| Agent ecosystem operates as designed | POSITIVE |
| Trivial tasks take longer | MINOR NEGATIVE |

### Third-Order Effects
| Effect | Impact |
|--------|--------|
| System behavior becomes predictable | POSITIVE |
| Users learn to expect consistent process | POSITIVE |
| May feel bureaucratic for simple changes | MINOR NEGATIVE |

### Simulation Verdict
**IMPLEMENT**: Benefits of consistent routing outweigh overhead for trivial tasks.

### Mitigated Alternative
For truly trivial tasks (typo fixes), Yoni can immediately dispatch to SKIP workflow.

---

## Simulation 2: Enforce Wealon-Last Rule

### Change Description
Every task completion MUST include wealon-regulatory-auditor audit.

### First-Order Effects
| Effect | Impact |
|--------|--------|
| All work is audited before completion | POSITIVE |
| Shortcuts are caught before commit | POSITIVE |
| Additional time per task | NEGATIVE |

### Second-Order Effects
| Effect | Impact |
|--------|--------|
| Quality improves over time | POSITIVE |
| Technical debt accumulation slows | POSITIVE |
| Velocity decreases short-term | NEGATIVE |

### Third-Order Effects
| Effect | Impact |
|--------|--------|
| Trust in system increases | POSITIVE |
| Fewer production issues | POSITIVE |
| May block urgent fixes | NEGATIVE |

### Simulation Verdict
**IMPLEMENT**: Quality assurance is critical for tax system. Velocity tradeoff acceptable.

### Mitigated Alternative
For hotfixes, Wealon can do abbreviated audit with follow-up comprehensive audit.

---

## Simulation 3: Integrate french-tax-optimizer as PRIMARY

### Change Description
Make french-tax-optimizer a PRIMARY agent (always active).

### First-Order Effects
| Effect | Impact |
|--------|--------|
| Tax expertise available for all requests | POSITIVE |
| Tax validation happens automatically | POSITIVE |
| Non-tax requests get unnecessary routing | NEGATIVE |

### Second-Order Effects
| Effect | Impact |
|--------|--------|
| All code gets tax-lens review | MIXED |
| Over-reliance on automated tax advice | NEGATIVE |
| Regulatory risk if advice is wrong | NEGATIVE |

### Third-Order Effects
| Effect | Impact |
|--------|--------|
| Users may trust system too much | NEGATIVE |
| Regulatory exposure increases | NEGATIVE |
| Domain expertise not validated | NEGATIVE |

### Simulation Verdict
**REJECT**: french-tax-optimizer should remain CONDITIONAL with human oversight.

### Mitigated Alternative
Keep as CONDITIONAL with explicit constraints:
- Advisory only
- Human approval for tax changes
- Source verification required

---

## Simulation 4: Remove Investment Recommendations Entirely

### Change Description
Remove LMNP, FCPI/FIP, Girardin recommendations from the system.

### First-Order Effects
| Effect | Impact |
|--------|--------|
| No regulatory risk for investment advice | POSITIVE |
| Reduced system value for users | NEGATIVE |
| Simpler system to maintain | POSITIVE |

### Second-Order Effects
| Effect | Impact |
|--------|--------|
| Users may go elsewhere for optimization | NEGATIVE |
| No CIF licensing concerns | POSITIVE |
| Reduced liability exposure | POSITIVE |

### Third-Order Effects
| Effect | Impact |
|--------|--------|
| Product differentiation reduced | NEGATIVE |
| Trust increases (system knows limits) | POSITIVE |
| Business model may need adjustment | NEGATIVE |

### Simulation Verdict
**CONDITIONAL**: Keep recommendations but reframe as "informational scenarios" with heavy disclaimers.

### Mitigated Alternative
- Rename "recommendations" to "informational scenarios"
- Add disclaimer: "This is not investment advice"
- Remove prescriptive language ("you should")
- Require legal-compliance review for any changes

---

## Simulation 5: Add Automated Barème Verification

### Change Description
Implement automated verification of barème data against impots.gouv.fr.

### First-Order Effects
| Effect | Impact |
|--------|--------|
| Barèmes verified automatically | POSITIVE |
| Development effort required | NEGATIVE |
| Dependency on external site structure | NEGATIVE |

### Second-Order Effects
| Effect | Impact |
|--------|--------|
| Reduced risk of outdated data | POSITIVE |
| Maintenance burden for scraper | NEGATIVE |
| May break if site changes | NEGATIVE |

### Third-Order Effects
| Effect | Impact |
|--------|--------|
| Trust in calculations increases | POSITIVE |
| Complexity increases | NEGATIVE |
| May provide false confidence if scraper fails | NEGATIVE |

### Simulation Verdict
**DEFER**: Important but not critical for v1.0. Implement in v2.0.

### Mitigated Alternative
For v1.0:
- Manual verification checklist
- Add `verified_date` to JSON files
- Add `source_url` to JSON files
- Require human sign-off for barème updates

---

## Simulation 6: Require Human Approval for All Tax Changes

### Change Description
Any change to tax_engine or analyzers requires explicit human approval.

### First-Order Effects
| Effect | Impact |
|--------|--------|
| All tax changes reviewed by human | POSITIVE |
| Velocity decreases for tax features | NEGATIVE |
| Accountability is clear | POSITIVE |

### Second-Order Effects
| Effect | Impact |
|--------|--------|
| Quality of tax features improves | POSITIVE |
| Bottleneck on human reviewer | NEGATIVE |
| Regulatory exposure reduced | POSITIVE |

### Third-Order Effects
| Effect | Impact |
|--------|--------|
| Trust in tax calculations justified | POSITIVE |
| Human expertise becomes critical path | NEGATIVE |
| Liability position clearer | POSITIVE |

### Simulation Verdict
**IMPLEMENT**: For a tax system, human oversight of tax logic is essential.

### Mitigated Alternative
None — this is a core governance requirement.

---

## Simulation 7: Replace Precise Estimates with Ranges

### Change Description
Change "Économie potentielle: 5,847€" to "Économie potentielle: 5,000€ - 6,500€".

### First-Order Effects
| Effect | Impact |
|--------|--------|
| More honest representation | POSITIVE |
| Less satisfying UI | NEGATIVE |
| Requires UI updates | NEGATIVE |

### Second-Order Effects
| Effect | Impact |
|--------|--------|
| Users calibrate trust appropriately | POSITIVE |
| May reduce conversions | NEGATIVE |
| Differentiates from competitors | POSITIVE |

### Third-Order Effects
| Effect | Impact |
|--------|--------|
| Builds reputation for honesty | POSITIVE |
| Users more likely to verify | POSITIVE |
| May be seen as uncertain | NEGATIVE |

### Simulation Verdict
**IMPLEMENT**: Honesty about uncertainty is essential for trust.

### Mitigated Alternative
Alternative: Use rounded numbers with qualifier (e.g., "Environ 5,800 €")

---

## Simulation Summary

### Approved Changes (IMPLEMENT)

| Change | Condition |
|--------|-----------|
| Yoni-First rule | None |
| Wealon-Last rule | None |
| Human approval for tax changes | None |
| Ranges/qualifiers for estimates | None |

### Rejected Changes

| Change | Reason |
|--------|--------|
| french-tax-optimizer as PRIMARY | Regulatory risk, over-reliance |

### Conditional Changes

| Change | Conditions |
|--------|------------|
| Keep investment recommendations | Reframe as "informational scenarios" + disclaimers |

### Deferred Changes

| Change | Revisit When |
|--------|--------------|
| Automated barème verification | v2.0 planning |

---

## Post-Simulation Governance Updates

Based on simulations, the following governance documents need updates:

| Document | Update Required |
|----------|----------------|
| AGENTS.md | french-tax-optimizer confirmed CONDITIONAL |
| config.yaml | Human checkpoint for tax changes |
| decisions.md | D002 confirmed (informational scenarios) |
| decisions.md | D003 confirmed (ranges/qualifiers) |

---

**Document Status:** Complete — Ready for Phase 7 multi-perspective audits.
