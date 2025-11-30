"""Main tax calculator - orchestrates all calculations."""

from typing import Any

from src.tax_engine.core import (
    compare_micro_vs_reel,
    compute_ir,
    compute_pas_result,
    compute_socials,
)
from src.tax_engine.rules import get_tax_rules


class TaxCalculator:
    """Main tax calculator for French freelancers."""

    def __init__(self, tax_year: int):
        """Initialize calculator for a tax year.

        Args:
            tax_year: Tax year (e.g., 2024, 2025)
        """
        self.tax_year = tax_year
        self.rules = get_tax_rules(tax_year)

    async def calculate(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Calculate all tax metrics for a freelance profile.

        Args:
            payload: Input data with person, income, deductions, social

        Returns:
            Complete tax calculation result with:
                - impot: IR calculation
                - socials: URSSAF calculation
                - comparisons: micro vs réel
                - warnings: List of warnings/recommendations
                - metadata: Calculation metadata (sources, version)

        Example payload:
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
        """
        person = payload.get("person", {})
        income = payload.get("income", {})
        deductions = payload.get("deductions", {})
        social = payload.get("social", {})
        pas_withheld = payload.get("pas_withheld", 0.0)

        warnings = []

        # Compute IR
        ir_result = compute_ir(person, income, deductions, self.rules)

        # Compute PAS result
        pas_result = compute_pas_result(ir_result["impot_net"], pas_withheld)

        # Compute social contributions
        socials = compute_socials(person, income, social, self.rules)

        # Check for URSSAF inconsistency
        if abs(socials["delta"]) > 500:
            warnings.append(
                f"Attention: écart URSSAF de {socials['delta']:.2f}€ "
                f"(attendu: {socials['urssaf_expected']:.2f}€, "
                f"déclaré: {socials['urssaf_paid']:.2f}€)"
            )

        # Compare micro vs réel (pass current socials for accurate comparison)
        comparison = compare_micro_vs_reel(
            person, income, deductions, self.rules, socials_micro=socials
        )

        # Check if réel would be significantly better
        if comparison["delta"] < -500:
            warnings.append(
                f"Opportunité réel: économie potentielle de "
                f"{abs(comparison['delta']):.2f}€ en passant au régime réel"
            )

        # Check micro thresholds
        professional_gross = income.get("professional_gross", 0.0)
        status = person.get("status", "micro_bnc").lower()
        plafonds = self.rules.plafonds_micro

        if "bnc" in status and professional_gross > plafonds.get("bnc", 77700):
            warnings.append(
                f"Dépassement du plafond micro-BNC "
                f"({professional_gross:.2f}€ > {plafonds.get('bnc')}€)"
            )
        elif "bic" in status:
            if "service" in status and professional_gross > plafonds.get(
                "bic_service", 77700
            ):
                warnings.append(
                    f"Dépassement du plafond micro-BIC prestations "
                    f"({professional_gross:.2f}€ > {plafonds.get('bic_service')}€)"
                )
            elif professional_gross > plafonds.get("bic_vente", 188700):
                warnings.append(
                    f"Dépassement du plafond micro-BIC ventes "
                    f"({professional_gross:.2f}€ > {plafonds.get('bic_vente')}€)"
                )

        # Rename 'brackets' to 'tranches_detail' for consistency with Pydantic models
        ir_result_mapped = {**ir_result}
        if "brackets" in ir_result_mapped:
            ir_result_mapped["tranches_detail"] = ir_result_mapped.pop("brackets")

        # TODO: Add cotisations_detail breakdown when detailed URSSAF rates available
        # For now, cotisations_detail remains None (optional in TaxCalculationSummary)

        return {
            "tax_year": self.tax_year,
            "impot": {
                **ir_result_mapped,
                **pas_result,
            },
            "socials": socials,
            "comparisons": {"micro_vs_reel": comparison},
            "warnings": warnings,
            "metadata": {
                "source": self.rules.source_url,
                "source_date": self.rules.source_date,
                "rules_version": self.tax_year,
                "disclaimer": (
                    "Estimation fiscale - ne remplace pas un expert-comptable. "
                    "Toujours valider avec un professionnel pour cas complexes."
                ),
            },
        }


async def calculate_tax(payload: dict[str, Any]) -> dict[str, Any]:
    """Convenience function to calculate tax from payload.

    Args:
        payload: Input data (see TaxCalculator.calculate for format)

    Returns:
        Tax calculation result
    """
    tax_year = payload.get("tax_year", 2024)
    calculator = TaxCalculator(tax_year)
    return await calculator.calculate(payload)
