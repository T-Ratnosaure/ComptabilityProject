"""FCPI/FIP optimization strategy."""

import json
import uuid
from pathlib import Path

from src.models.optimization import (
    ComplexityLevel,
    Recommendation,
    RecommendationCategory,
    RiskLevel,
)


class FCPIFIPStrategy:
    """Analyzes FCPI/FIP investment optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the FCPI/FIP strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "fcpi_fip_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

    def analyze(
        self, tax_result: dict, profile: dict, context: dict
    ) -> list[Recommendation]:
        """
        Analyze FCPI/FIP optimization opportunities.

        Args:
            tax_result: Result from tax calculation engine
            profile: User profile
            context: Additional context (risk tolerance)

        Returns:
            List of FCPI/FIP recommendations
        """
        recommendations = []

        # Extract data
        impot_net = tax_result.get("impot", {}).get("impot_net", 0)
        risk_tolerance = context.get("risk_tolerance", "low")
        nb_parts = profile.get("nb_parts", 1)

        # Check eligibility
        min_impot = self.rules["eligibility"]["min_impot"]
        if impot_net < min_impot:
            return recommendations

        # FCPI/FIP requires at least medium risk tolerance
        if risk_tolerance not in ["medium", "high", "aggressive", "moderate"]:
            return recommendations

        # Generate FCPI recommendation
        fcpi_rec = self._create_fcpi_recommendation(impot_net, nb_parts)
        if fcpi_rec:
            recommendations.append(fcpi_rec)

        return recommendations

    def _create_fcpi_recommendation(
        self, impot_net: float, nb_parts: float
    ) -> Recommendation | None:
        """Create FCPI recommendation."""
        fcpi_rules = self.rules["fcpi"]
        reduction_rate = fcpi_rules["reduction_rate"]

        # Determine plafond based on family situation
        plafond = (
            fcpi_rules["plafond_couple"]
            if nb_parts >= 2
            else fcpi_rules["plafond_individual"]
        )

        # Suggest investing 30-50% of plafond
        recommended_investment = min(plafond * 0.4, impot_net * 0.3)

        if recommended_investment < 1000:
            return None

        reduction = recommended_investment * reduction_rate
        effective_cost = recommended_investment - reduction

        description = (
            f"💼 FCPI (Fonds Communs de Placement dans l'Innovation)\n\n"
            f"Les FCPI permettent de bénéficier d'une réduction d'impôt de {reduction_rate * 100:.0f}% "
            f"tout en soutenant l'innovation française.\n\n"
            f"**Pour votre situation :**\n"
            f"- Plafond disponible : {plafond:.2f}€\n"
            f"- Investissement recommandé : {recommended_investment:.2f}€\n"
            f"- Réduction d'impôt : {reduction:.2f}€\n"
            f"- Coût réel après réduction : {effective_cost:.2f}€\n\n"
            f"**Avantages :**\n"
            f"- Réduction d'impôt immédiate de {reduction_rate * 100:.0f}%\n"
            f"- Soutien à l'innovation et aux PME françaises\n"
            f"- Diversification de votre patrimoine\n"
            f"- Potentiel de plus-value à long terme\n\n"
            f"**Engagement :** Les fonds sont bloqués pendant {fcpi_rules['commitment_years']} ans minimum."
        )

        action_steps = [
            "Comparer les FCPI disponibles (performances historiques, frais)",
            "Vérifier que le fonds est éligible à la réduction d'impôt",
            "Souscrire avant le 31 décembre",
            f"Investir entre {recommended_investment * 0.8:.2f}€ et {recommended_investment:.2f}€",
            "Conserver les justificatifs de souscription",
            "Déclarer l'investissement sur votre déclaration 2042 C",
            "Ne pas dépasser le plafond annuel",
        ]

        return Recommendation(
            id=str(uuid.uuid4()),
            title=f"FCPI - Réduction {reduction_rate * 100:.0f}% + Innovation",
            description=description,
            impact_estimated=reduction,
            risk=RiskLevel.MEDIUM,
            complexity=ComplexityLevel.MODERATE,
            confidence=0.80,
            category=RecommendationCategory.INVESTMENT,
            sources=self.rules.get(
                "sources",
                [
                    "https://www.service-public.fr/particuliers/vosdroits/F34272",
                    "https://www.amf-france.org/fr/espace-epargnants/comprendre-les-produits-financiers/supports-dinvestissement-assurance-vie-compte-titres-pea/fcpi-et-fip",
                ],
            ),
            action_steps=action_steps,
            required_investment=recommended_investment,
            eligibility_criteria=[
                f"Impôt >= {self.rules['eligibility']['min_impot']}€",
                "Tolérance au risque moyenne",
                f"Plafond annuel : {plafond}€",
            ],
            warnings=self.rules.get(
                "warnings",
                [
                    "Risque de perte en capital",
                    f"Blocage des fonds pendant {fcpi_rules['commitment_years']} ans minimum",
                    "Frais de gestion annuels (2-3%)",
                    "Performance non garantie",
                ],
            ),
            deadline="31 décembre de l'année en cours",
            roi_years=5.0,
        )
