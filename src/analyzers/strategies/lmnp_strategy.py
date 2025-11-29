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


class LMNPStrategy:
    """Analyzes LMNP investment optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the LMNP strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "lmnp_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

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
        tmi = self._estimate_tmi(revenu_imposable, nb_parts)

        # Check eligibility
        investment_capacity = context.get("investment_capacity", 0)
        risk_tolerance = context.get("risk_tolerance", "low")

        # LMNP is interesting for TMI >= 30%
        if tmi < self.rules["eligibility"]["min_tmi"]:
            return recommendations

        # Check investment capacity
        min_investment = self.rules["eligibility"]["min_investment_capacity"]
        if investment_capacity < min_investment:
            return recommendations

        # Generate LMNP recommendation
        rec = self._create_lmnp_recommendation(tmi, investment_capacity, risk_tolerance)
        recommendations.append(rec)

        return recommendations

    def _estimate_tmi(self, revenu_imposable: float, nb_parts: float) -> float:
        """Estimate marginal tax rate (TMI)."""
        revenu_par_part = revenu_imposable / nb_parts

        if revenu_par_part <= 11294:
            return 0.0
        elif revenu_par_part <= 28797:
            return 0.11
        elif revenu_par_part <= 82341:
            return 0.30
        elif revenu_par_part <= 177106:
            return 0.41
        else:
            return 0.45

    def _create_lmnp_recommendation(
        self, tmi: float, investment_capacity: float, risk_tolerance: str
    ) -> Recommendation:
        """Create LMNP investment recommendation."""
        # Estimate annual rental income (conservative 4% yield)
        estimated_rental = investment_capacity * 0.04

        # Estimate tax savings with LMNP réel
        # Average: 70% charges + amortissement = near-zero taxable income
        estimated_savings = estimated_rental * tmi * 0.85

        description = (
            f"🏠 LMNP (Location Meublée Non Professionnelle)\n"
            f"Investissement locatif optimisé\n\n"
            f"Avec votre TMI de {tmi * 100:.0f}% et une capacité d'investissement "
            f"de {investment_capacity:.2f}€, le LMNP en régime réel peut être "
            f"une excellente stratégie d'optimisation fiscale.\n\n"
            f"**Avantages fiscaux :**\n"
            f"- Amortissement du bien (3-4% par an)\n"
            f"- Déduction des charges réelles (travaux, intérêts, assurances)\n"
            f"- Imposition réduite voire nulle pendant la période d'amortissement\n"
            f"- Impact limité sur le RFR (revenus fonciers réduits)\n\n"
            f"**Estimation :** Pour un investissement de {investment_capacity:.2f}€ "
            f"générant ~{estimated_rental:.2f}€/an de loyers, vous pourriez "
            f"économiser environ {estimated_savings:.2f}€ d'impôt par an.\n\n"
            f"**Stratégie patrimoniale :**\n"
            f"- Constitution d'un patrimoine immobilier\n"
            f"- Revenus complémentaires à la retraite\n"
            f"- Transmission patrimoniale optimisée"
        )

        action_steps = [
            "Étudier le marché locatif de votre zone cible",
            "Définir votre budget d'investissement (apport + emprunt)",
            "Consulter un conseiller en gestion de patrimoine",
            "Sélectionner un bien avec bon potentiel locatif",
            "Opter pour le régime réel LMNP (plus avantageux que micro-BIC)",
            "Faire appel à un expert-comptable spécialisé LMNP",
            "Mettre en place la comptabilité et l'amortissement",
            "Louer le bien meublé (durée minimale 1 an recommandée)",
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
            title="LMNP - Investissement locatif meublé défiscalisé",
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
                f"TMI >= {self.rules['eligibility']['min_tmi'] * 100:.0f}%",
                f"Capacité investissement >= "
                f"{self.rules['eligibility']['min_investment_capacity']}€",
                "Horizon d'investissement long terme (10+ ans)",
            ],
            warnings=warnings,
            deadline=None,
            roi_years=15.0,  # Long-term investment
        )
