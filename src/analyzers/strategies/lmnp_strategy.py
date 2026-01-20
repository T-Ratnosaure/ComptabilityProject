"""LMNP (Location Meublée Non Professionnelle) optimization strategy."""

import json
import uuid
from pathlib import Path

from src.models.optimization import (
    ComplexityLevel,
    Recommendation,
    RecommendationCategory,
    RiskLevel,
)
from src.tax_engine.core import calculate_tmi
from src.tax_engine.rules import get_tax_rules
from src.tax_engine.tax_utils import (
    get_lmnp_deduction_rate,
    get_lmnp_eligibility,
    get_lmnp_yield,
)


class LMNPStrategy:
    """Analyzes LMNP investment optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the LMNP strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "lmnp_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

        # Load tax rules for TMI calculation
        self.tax_rules = get_tax_rules(2024)

    def analyze(
        self, tax_result: dict, profile: dict, context: dict
    ) -> list[Recommendation]:
        """
        Analyze LMNP optimization opportunities.

        Args:
            tax_result: Result from tax calculation engine
            profile: User profile
            context: Additional context (investment capacity, risk tolerance)

        Returns:
            List of LMNP recommendations
        """
        recommendations = []

        # Extract data
        revenu_imposable = tax_result.get("impot", {}).get("revenu_imposable", 0)
        nb_parts = profile.get("nb_parts", 1)

        # Use centralized TMI calculation
        tmi = calculate_tmi(revenu_imposable, nb_parts, self.tax_rules)

        # Check eligibility using centralized function
        investment_capacity = context.get("investment_capacity", 0)
        risk_tolerance = context.get("risk_tolerance", "low")
        eligibility = get_lmnp_eligibility(self.tax_rules)

        # LMNP is interesting for TMI >= 30%
        if tmi < eligibility["min_tmi"]:
            return recommendations

        # Check investment capacity
        if investment_capacity < eligibility["min_investment_capacity"]:
            return recommendations
        # LMNP requires at least moderate risk tolerance (medium-risk investment)
        if risk_tolerance not in ["medium", "moderate", "high", "aggressive"]:
            return recommendations

        # Generate LMNP recommendation
        rec = self._create_lmnp_recommendation(tmi, investment_capacity, risk_tolerance)
        recommendations.append(rec)

        return recommendations

    def _create_lmnp_recommendation(
        self, tmi: float, investment_capacity: float, risk_tolerance: str
    ) -> Recommendation:
        """Create LMNP investment recommendation."""
        # Use centralized functions for LMNP parameters
        estimated_yield = get_lmnp_yield(self.tax_rules)
        total_deduction_rate = get_lmnp_deduction_rate("reel", self.tax_rules)
        eligibility = get_lmnp_eligibility(self.tax_rules)

        # Estimate annual rental income
        estimated_rental = investment_capacity * estimated_yield

        # Estimate tax savings with LMNP réel
        estimated_savings = estimated_rental * tmi * total_deduction_rate

        # Round amounts for educational display
        rounded_investment = round(investment_capacity, -3)  # Round to nearest 1000
        rounded_savings = round(estimated_savings, -2)
        rounded_rental = round(estimated_rental, -2)

        description = (
            f"🏠 LMNP - Comment ça fonctionne\n\n"
            f"📊 **Exemple illustratif basé sur votre profil**\n"
            f"• Si vous investissiez ~**{rounded_investment:,.0f} €**\n"
            f"• Économie potentielle : ~**{rounded_savings:,.0f} €/an**\n"
            f"• Loyers estimés : ~{rounded_rental:,.0f} €/an\n"
            f"• Votre TMI : {tmi * 100:.0f}%\n\n"
            f"✅ **Principes du régime réel**\n"
            f"• Amortissement du bien (~3-4% par an)\n"
            f"• Charges déductibles (travaux, intérêts)\n"
            f"• Imposition réduite pendant plusieurs années\n\n"
            f"📌 **AVERTISSEMENT** : Exemple informatif uniquement. "
            f"L'immobilier comporte des risques. "
            f"Consultez un CGP ou CIF agréé avant toute décision."
        )

        action_steps = [
            "Étudier le marché locatif de votre zone cible",
            "Définir votre budget d'investissement (apport + emprunt)",
            "Consulter un conseiller en gestion de patrimoine (CGP) agréé",
            "Sélectionner un bien avec bon potentiel locatif",
            "Étudier le régime réel LMNP avec un expert-comptable",
            "Faire appel à un expert-comptable spécialisé LMNP",
            "Mettre en place la comptabilité et l'amortissement",
            "Louer le bien meublé (durée minimale généralement 1 an)",
        ]

        warnings = [
            "Investissement immobilier = engagement long terme",
            "Risque locatif (vacance, impayés)",
            "Charges de copropriété et entretien à prévoir",
            "Frais de gestion si délégation à une agence",
            "Bien étudier le marché avant d'investir",
            "Ne pas investir uniquement pour la défiscalisation",
            "Consulter un expert-comptable LMNP obligatoire",
        ]

        return Recommendation(
            id=str(uuid.uuid4()),
            title="LMNP - Scénario investissement locatif meublé",
            description=description,
            impact_estimated=estimated_savings,
            risk=RiskLevel.MEDIUM,
            complexity=ComplexityLevel.COMPLEX,
            confidence=0.70,
            category=RecommendationCategory.INVESTMENT,
            sources=self.rules.get(
                "sources",
                [
                    "https://www.service-public.fr/particuliers/vosdroits/F32744",
                    "https://bofip.impots.gouv.fr/bofip/5773-PGP.html",
                ],
            ),
            action_steps=action_steps,
            required_investment=investment_capacity,
            eligibility_criteria=[
                f"TMI >= {eligibility['min_tmi'] * 100:.0f}%",
                f"Capacité investissement >= {eligibility['min_investment_capacity']}€",
                "Horizon d'investissement long terme (10+ ans)",
            ],
            warnings=warnings,
            deadline=None,
            roi_years=15.0,  # Long-term investment
        )
