# Testing Guide - French Tax Calculation API

## Quick Start

### 1. Start the Server

```bash
uv run uvicorn src.main:app --reload --port 8000
```

Server will be available at: **http://localhost:8000**

### 2. Open Interactive Documentation

Go to: **http://localhost:8000/docs**

This gives you a nice UI to test all endpoints!

## Valid Tax Regime Values

When using the API, the `person.status` field must be one of these **exact** values:

| Status Value | Description | Abattement | Activity Type |
|--------------|-------------|------------|---------------|
| `micro_bnc` | Micro-BNC (professions libérales) | 34% | Liberal professions |
| `micro_bic_service` | Micro-BIC prestations de services | 50% | Service activities |
| `micro_bic_vente` | Micro-BIC ventes de marchandises | 71% | Sales/commerce |
| `reel_bnc` | Réel BNC (with real expenses) | N/A | Liberal professions |
| `reel_bic` | Réel BIC (with real expenses) | N/A | Commercial activities |

## Example Requests

### Example 1: Simple Micro-BNC (Consultant/Freelancer)

```json
{
  "tax_year": 2024,
  "person": {
    "name": "ANON",
    "nb_parts": 1.0,
    "status": "micro_bnc"
  },
  "income": {
    "professional_gross": 28000.0,
    "salary": 0.0,
    "rental_income": 0.0,
    "capital_income": 0.0,
    "deductible_expenses": 0.0
  },
  "deductions": {
    "per_contributions": 2000.0,
    "alimony": 0.0,
    "other_deductions": 0.0
  },
  "social": {
    "urssaf_declared_ca": 28000.0,
    "urssaf_paid": 6000.0
  },
  "pas_withheld": 0.0
}
```

**Expected Result:**
- Revenu imposable: 16,480€ (after 34% abattement and 2,000€ PER)
- Impôt net: 570.46€
- URSSAF: 6,104€
- Recommendation: Micro (saves 1,047€ vs Réel)

### Example 2: Micro-BIC Service (IT Consultant, Designer)

```json
{
  "tax_year": 2024,
  "person": {
    "name": "ANON",
    "nb_parts": 1.0,
    "status": "micro_bic_service"
  },
  "income": {
    "professional_gross": 40000.0,
    "salary": 0.0,
    "rental_income": 0.0,
    "capital_income": 0.0,
    "deductible_expenses": 0.0
  },
  "deductions": {
    "per_contributions": 0.0,
    "alimony": 0.0,
    "other_deductions": 0.0
  },
  "social": {
    "urssaf_declared_ca": 40000.0,
    "urssaf_paid": 5120.0
  },
  "pas_withheld": 0.0
}
```

**Expected Result:**
- 50% abattement (better than BNC!)
- URSSAF rate: 12.8% (lower than BNC)

### Example 3: Family with 2 Parts (Couple with Children)

```json
{
  "tax_year": 2024,
  "person": {
    "name": "ANON",
    "nb_parts": 2.0,
    "status": "micro_bnc"
  },
  "income": {
    "professional_gross": 50000.0,
    "salary": 0.0,
    "rental_income": 0.0,
    "capital_income": 0.0,
    "deductible_expenses": 0.0
  },
  "deductions": {
    "per_contributions": 0.0,
    "alimony": 0.0,
    "other_deductions": 0.0
  },
  "social": {
    "urssaf_declared_ca": 50000.0,
    "urssaf_paid": 10900.0
  },
  "pas_withheld": 0.0
}
```

**Expected Result:**
- Much lower tax due to quotient familial
- Income divided by 2 for bracket calculation

### Example 4: High Expenses - Réel Better

```json
{
  "tax_year": 2024,
  "person": {
    "name": "ANON",
    "nb_parts": 1.0,
    "status": "micro_bnc"
  },
  "income": {
    "professional_gross": 50000.0,
    "salary": 0.0,
    "rental_income": 0.0,
    "capital_income": 0.0,
    "deductible_expenses": 20000.0
  },
  "deductions": {
    "per_contributions": 0.0,
    "alimony": 0.0,
    "other_deductions": 0.0
  },
  "social": {
    "urssaf_declared_ca": 50000.0,
    "urssaf_paid": 10900.0
  },
  "pas_withheld": 0.0
}
```

**Expected Result:**
- Warning: Réel regime would save money
- Micro: 50k × 66% = 33k taxable
- Réel: 50k - 20k = 30k taxable
- **Réel saves ~900€**

## Testing Methods

### Method 1: Browser (Easiest)
1. Go to http://localhost:8000/docs
2. Find `/api/v1/tax/calculate` endpoint
3. Click "Try it out"
4. Select a valid `status` from dropdown
5. Fill in other fields
6. Click "Execute"

### Method 2: curl (Command Line)
```bash
curl -X POST http://localhost:8000/api/v1/tax/calculate \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### Method 3: Python Script
```bash
# Single test
uv run python test_api.py

# All scenarios
uv run python test_scenarios.py
```

### Method 4: Unit Tests
```bash
# All tax tests
uv run pytest tests/test_tax_engine.py -v

# Specific test
uv run pytest tests/test_tax_engine.py::TestFullCalculation::test_simple_micro_bnc_case -v
```

## Common Mistakes

### ❌ Wrong: Using "string" as status
```json
{
  "person": {
    "status": "string"  // ❌ This will fail!
  }
}
```

### ✅ Correct: Using valid regime
```json
{
  "person": {
    "status": "micro_bnc"  // ✅ Valid!
  }
}
```

### ❌ Wrong: Typo in regime name
```json
{
  "person": {
    "status": "micro-bnc"  // ❌ Wrong (uses dash instead of underscore)
  }
}
```

### ✅ Correct: Exact value
```json
{
  "person": {
    "status": "micro_bnc"  // ✅ Correct (underscore)
  }
}
```

## Number of Parts (nb_parts)

Valid values: 0.5 to 10.0

Common scenarios:
- **1.0** - Single person
- **1.5** - Single parent with 1 child
- **2.0** - Married couple
- **2.5** - Couple with 1 child
- **3.0** - Couple with 2 children
- **3.5** - Couple with 3 children

## Response Structure

```json
{
  "tax_year": 2024,
  "impot": {
    "revenu_imposable": 16480.0,    // Taxable income after abattements
    "part_income": 16480.0,          // Per-part income (for quotient familial)
    "impot_brut": 570.46,            // Gross tax
    "impot_net": 570.46,             // Net tax (after reductions)
    "pas_withheld": 0.0,             // Already withheld
    "due_now": 570.46                // Amount to pay now
  },
  "socials": {
    "urssaf_expected": 6104.0,       // Expected URSSAF
    "urssaf_paid": 6000.0,           // What you declared
    "delta": -104.0,                 // Difference
    "rate_used": 0.218               // Rate applied (21.8%)
  },
  "comparisons": {
    "micro_vs_reel": {
      "impot_micro": 570.46,         // Tax with micro
      "impot_reel": 1617.66,         // Tax with réel
      "delta": 1047.2,               // Difference (positive = micro better)
      "recommendation": "micro",      // Which is better
      "recommendation_reason": "..."  // Why
    }
  },
  "warnings": [],                    // Alerts (thresholds, inconsistencies)
  "metadata": {
    "source": "...",                 // Official source URL
    "rules_version": 2024,           // Tax year
    "disclaimer": "..."              // Legal disclaimer
  }
}
```

## Other Endpoints

### Get Tax Rules
```bash
# 2024 rules
curl http://localhost:8000/api/v1/tax/rules/2024

# 2025 rules
curl http://localhost:8000/api/v1/tax/rules/2025
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Troubleshooting

### Error: "Unknown regime: string"
**Solution:** Use one of the valid status values: `micro_bnc`, `micro_bic_service`, `micro_bic_vente`, `reel_bnc`, `reel_bic`

### Error: "Field required"
**Solution:** Make sure all required fields are present in the request body

### Error: "Connection refused"
**Solution:** Start the server first: `uv run uvicorn src.main:app --reload --port 8000`

### Server not reloading?
**Solution:** Make sure you used the `--reload` flag when starting the server

## Files Available

- `test_request.json` - Sample request (micro-BNC)
- `test_api.py` - Single test with formatted output
- `test_scenarios.py` - 6 comprehensive scenarios
- `TESTING_GUIDE.md` - This file

## Need Help?

- **API Docs:** http://localhost:8000/docs (interactive!)
- **ReDoc:** http://localhost:8000/redoc (detailed documentation)
- **Source Code:** Check `src/tax_engine/` for implementation details
- **Official Sources:** See `docs/sources.md` for tax rules references

---

**Happy Testing!** 🎉
