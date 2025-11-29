"""Test different tax scenarios."""

import httpx

BASE_URL = "http://localhost:8000/api/v1/tax/calculate"

# Scenario 1: Simple Micro-BNC (from documentation)
scenario_1 = {
    "name": "Cas A: Simple Micro-BNC",
    "payload": {
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
            "per_contributions": 0.0,
            "alimony": 0.0,
            "other_deductions": 0.0,
        },
        "social": {"urssaf_declared_ca": 28000.0, "urssaf_paid": 6000.0},
        "pas_withheld": 0.0,
    },
}

# Scenario 2: High expenses - Réel better (Cas B from doc)
scenario_2 = {
    "name": "Cas B: Reel Better (High Expenses)",
    "payload": {
        "tax_year": 2024,
        "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
        "income": {
            "professional_gross": 50000.0,
            "salary": 0.0,
            "rental_income": 0.0,
            "capital_income": 0.0,
            "deductible_expenses": 20000.0,  # High expenses
        },
        "deductions": {
            "per_contributions": 0.0,
            "alimony": 0.0,
            "other_deductions": 0.0,
        },
        "social": {"urssaf_declared_ca": 50000.0, "urssaf_paid": 10000.0},
        "pas_withheld": 0.0,
    },
}

# Scenario 3: Family with 2 parts
scenario_3 = {
    "name": "Family (2 parts - quotient familial)",
    "payload": {
        "tax_year": 2024,
        "person": {"name": "ANON", "nb_parts": 2.0, "status": "micro_bnc"},
        "income": {
            "professional_gross": 50000.0,
            "salary": 0.0,
            "rental_income": 0.0,
            "capital_income": 0.0,
            "deductible_expenses": 0.0,
        },
        "deductions": {
            "per_contributions": 0.0,
            "alimony": 0.0,
            "other_deductions": 0.0,
        },
        "social": {"urssaf_declared_ca": 50000.0, "urssaf_paid": 10000.0},
        "pas_withheld": 0.0,
    },
}

# Scenario 4: Mixed income sources
scenario_4 = {
    "name": "Mixed Income (freelance + salary + rental)",
    "payload": {
        "tax_year": 2024,
        "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
        "income": {
            "professional_gross": 20000.0,
            "salary": 15000.0,
            "rental_income": 5000.0,
            "capital_income": 2000.0,
            "deductible_expenses": 0.0,
        },
        "deductions": {
            "per_contributions": 0.0,
            "alimony": 0.0,
            "other_deductions": 0.0,
        },
        "social": {"urssaf_declared_ca": 20000.0, "urssaf_paid": 4000.0},
        "pas_withheld": 0.0,
    },
}

# Scenario 5: BIC service (different abattement)
scenario_5 = {
    "name": "Micro-BIC Service (50% abattement)",
    "payload": {
        "tax_year": 2024,
        "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bic_service"},
        "income": {
            "professional_gross": 40000.0,
            "salary": 0.0,
            "rental_income": 0.0,
            "capital_income": 0.0,
            "deductible_expenses": 0.0,
        },
        "deductions": {
            "per_contributions": 0.0,
            "alimony": 0.0,
            "other_deductions": 0.0,
        },
        "social": {"urssaf_declared_ca": 40000.0, "urssaf_paid": 5120.0},
        "pas_withheld": 0.0,
    },
}

# Scenario 6: Above micro threshold (warning)
scenario_6 = {
    "name": "Above Threshold (Warning Expected)",
    "payload": {
        "tax_year": 2024,
        "person": {"name": "ANON", "nb_parts": 1.0, "status": "micro_bnc"},
        "income": {
            "professional_gross": 80000.0,  # Above 77,700
            "salary": 0.0,
            "rental_income": 0.0,
            "capital_income": 0.0,
            "deductible_expenses": 0.0,
        },
        "deductions": {
            "per_contributions": 0.0,
            "alimony": 0.0,
            "other_deductions": 0.0,
        },
        "social": {"urssaf_declared_ca": 80000.0, "urssaf_paid": 17000.0},
        "pas_withheld": 0.0,
    },
}

scenarios = [scenario_1, scenario_2, scenario_3, scenario_4, scenario_5, scenario_6]

print("=" * 80)
print("FRENCH TAX CALCULATION - TEST SCENARIOS")
print("=" * 80)

for i, scenario in enumerate(scenarios, 1):
    print(f"\n{i}. {scenario['name']}")
    print("-" * 80)

    try:
        response = httpx.post(BASE_URL, json=scenario["payload"], timeout=10.0)
        response.raise_for_status()
        result = response.json()

        # Print key results
        print(
            f"   CA/Revenue: {scenario['payload']['income']['professional_gross']:,.0f} EUR"
        )
        print(f"   Revenu imposable: {result['impot']['revenu_imposable']:,.2f} EUR")
        print(f"   Impot net: {result['impot']['impot_net']:,.2f} EUR")
        print(f"   URSSAF expected: {result['socials']['urssaf_expected']:,.2f} EUR")

        # Comparison
        comp = result["comparisons"]["micro_vs_reel"]
        better = "MICRO" if comp["delta"] > 0 else "REEL"
        savings = abs(comp["delta"])
        print(f"   Best regime: {better} (saves {savings:,.2f} EUR)")

        # Warnings
        if result["warnings"]:
            print("   WARNINGS:")
            for warning in result["warnings"]:
                print(f"      - {warning}")
        else:
            print("   No warnings")

    except Exception as e:
        print(f"   ERROR: {e}")

print("\n" + "=" * 80)
print("All scenarios tested!")
print("=" * 80)
