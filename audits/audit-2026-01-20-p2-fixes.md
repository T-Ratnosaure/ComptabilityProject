# Audit Report: P2 Fixes - URSSAF Rate & PER Plafond

**Date:** 2026-01-20
**Branch:** `fix/p2-urssaf-and-per-plafond`
**Type:** Configuration & Mock Data Fixes
**Priority:** P2 (Important, Non-Critical)

## Executive Summary

This audit addresses two P2 issues from the Wealon security/code audit:
1. Hardcoded URSSAF rate in frontend mock data (should vary by professional status)
2. Hardcoded PER minimum plafond in tax engine (should come from configuration)

Both issues have been resolved with backward-compatible changes.

---

## Issue 1: URSSAF Rate in Mock Data

### Problem
The frontend mock data in `frontend/app/optimizations/page.tsx` used a hardcoded URSSAF rate of `0.218` (21.8%), which is only correct for BNC (liberal professions). BIC activities use `0.128` (12.8%).

### Solution
Added a `getUrssafRate()` function that returns the correct rate based on professional status:

```typescript
const getUrssafRate = (status: string): number => {
  switch (status) {
    case "micro_bnc":
      return 0.218 // 21.8% for liberal professions
    case "micro_bic_service":
    case "micro_bic_vente":
      return 0.128 // 12.8% for commercial activities
    case "reel_bnc":
      return 0.218 // Same as micro for comparison
    case "reel_bic":
      return 0.128 // Same as micro for comparison
    default:
      return 0.218
  }
}
```

### Files Modified
- `frontend/app/optimizations/page.tsx`

### Risk Assessment
- **Impact:** Low - Mock data only, real API returns correct values
- **Breaking Changes:** None

---

## Issue 2: PER Minimum Plafond Configuration

### Problem
The PER minimum plafond (4399) was hardcoded in two locations:
- `src/tax_engine/core.py:185`
- `src/tax_engine/tax_utils.py:44`

This violates the "single source of truth" principle and makes it harder to update for future years.

### Solution
1. Added `min_plafond` to the `per_plafonds` section in both baremes JSON files
2. Updated both Python files to read from configuration with fallback

### Configuration Changes
```json
"per_plafonds": {
  "base_rate": 0.10,
  "min_plafond": 4399,
  "max_tns": 85780,
  "max_salarie": 35794,
  ...
}
```

### Files Modified
- `src/tax_engine/data/baremes_2024.json`
- `src/tax_engine/data/baremes_2025.json`
- `src/tax_engine/core.py`
- `src/tax_engine/tax_utils.py`

### Risk Assessment
- **Impact:** Low - Backward compatible with fallback values
- **Breaking Changes:** None

---

## Test Results

```
324 tests passed
0 tests failed
Frontend build: SUCCESS
```

All existing tests continue to pass, confirming backward compatibility.

---

## Manual Testing Guide

### Test 1: URSSAF Rate by Status

**Objective:** Verify URSSAF rates vary correctly by professional status

**Steps:**
1. Start the frontend: `cd frontend && npm run dev`
2. Navigate to `/optimizations`
3. Open browser DevTools Console
4. Enter test profiles with different statuses:

| Status | Expected URSSAF Rate |
|--------|---------------------|
| micro_bnc | 21.8% |
| micro_bic_service | 12.8% |
| micro_bic_vente | 12.8% |

**Expected Result:** The displayed URSSAF expected amount should reflect the correct rate for each status.

### Test 2: PER Plafond Calculation

**Objective:** Verify PER minimum plafond is applied correctly

**Steps:**
1. Start the backend API
2. Test with low income (e.g., 30,000) that would calculate below min_plafond:
   ```bash
   curl -X POST http://localhost:8000/api/tax/calculate \
     -H "Content-Type: application/json" \
     -d '{"revenu_imposable": 30000, "situation_familiale": "celibataire"}'
   ```
3. Verify PER plafond recommendation uses minimum (4399) not calculated (3000)

**Expected Result:** PER plafond should be 4399 (minimum), not 10% of income (3000).

### Test 3: Configuration Source

**Objective:** Verify values come from baremes JSON, not hardcoded

**Steps:**
1. Temporarily modify `baremes_2025.json` to change `min_plafond` to 5000
2. Run: `uv run pytest tests/test_tax_engine.py -v`
3. Observe that calculations use the new value
4. Revert the change

**Expected Result:** Tax engine should use values from configuration files.

---

## Recommendations

### Completed
- [x] URSSAF rate now varies by professional status
- [x] PER min_plafond moved to configuration
- [x] All tests pass
- [x] Backward compatible with fallback values

### Future Considerations
- P3: Consider centralizing all URSSAF rates in a shared config
- P3: Add frontend tests for rate calculations
- Consider adding year-specific min_plafond values (they may change annually)

---

## Approval

- [ ] Code review approved
- [ ] Manual testing completed
- [ ] Ready to merge

**Reviewer:** _________________
**Date:** _________________
