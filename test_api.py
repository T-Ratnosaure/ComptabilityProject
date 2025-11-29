"""Quick script to test the tax calculation API."""

import httpx

# Test data
payload = {
    "tax_year": 2024,
    "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
    "income": {
        "professional_gross": 28000.0,
        "salary": 0.0,
        "rental_income": 0.0,
        "capital_income": 0.0,
        "deductible_expenses": 0.0,
    },
    "deductions": {
        "per_contributions": 2000.0,
        "alimony": 0.0,
        "other_deductions": 0.0,
    },
    "social": {"urssaf_declared_ca": 28000.0, "urssaf_paid": 6000.0},
    "pas_withheld": 0.0,
}

# Make request
response = httpx.post(
    "http://localhost:8000/api/v1/tax/calculate", json=payload, timeout=10.0
)

# Print results
print("Status Code:", response.status_code)
print("\n" + "=" * 60)
print("TAX CALCULATION RESULTS")
print("=" * 60)

result = response.json()

# Income Tax
print("\nINCOME TAX (IR)")
print(f"   Revenu imposable: {result['impot']['revenu_imposable']:,.2f} EUR")
print(f"   Impot brut: {result['impot']['impot_brut']:,.2f} EUR")
print(f"   Impot net: {result['impot']['impot_net']:,.2f} EUR")
print(f"   Montant du: {result['impot']['due_now']:,.2f} EUR")

# Social Contributions
print("\nSOCIAL CONTRIBUTIONS (URSSAF)")
print(f"   Attendu: {result['socials']['urssaf_expected']:,.2f} EUR")
print(f"   Paye: {result['socials']['urssaf_paid']:,.2f} EUR")
print(f"   Ecart: {result['socials']['delta']:,.2f} EUR")

# Comparison
comp = result["comparisons"]["micro_vs_reel"]
print("\nMICRO vs REEL COMPARISON")
print(f"   Impot micro: {comp['impot_micro']:,.2f} EUR")
print(f"   Impot reel: {comp['impot_reel']:,.2f} EUR")
print(f"   Difference: {comp['delta']:,.2f} EUR")
print(f"   Recommandation: {comp['recommendation'].upper()}")
print(f"   {comp['recommendation_reason']}")

# Warnings
if result["warnings"]:
    print("\nWARNINGS")
    for warning in result["warnings"]:
        print(f"   - {warning}")
else:
    print("\nNo warnings")

print("\n" + "=" * 60)
print(f"Source: {result['metadata']['source']}")
print(f"Disclaimer: {result['metadata']['disclaimer']}")
print("=" * 60)
