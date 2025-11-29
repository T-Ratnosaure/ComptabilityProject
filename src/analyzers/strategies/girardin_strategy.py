"""Girardin optimization strategy with Profina recommendation."""

import json
import uuid
from pathlib import Path

from src.models.optimization import (
    ComplexityLevel,
    Recommendation,
    RecommendationCategory,
    RiskLevel,
)


class GirardinStrategy:
    """Analyzes Girardin investment optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the Girardin strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "girardin_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

    def analyze(
        self, tax_result: dict, profile: dict, context: dict
    ) -> list[Recommendation]:
        """
        Analyze Girardin optimization opportunities.

        Args:
            tax_result: Result from tax calculation engine
            profile: User profile
            context: Additional context (risk tolerance, stable income)

        Returns:
            List of Girardin recommendations
        """
        recommendations = []

        # Extract data
        impot_net = tax_result.get("impot", {}).get("impot_net", 0)
        risk_tolerance = context.get("risk_tolerance", "low")
        stable_income = context.get("stable_income", False)

        # Check eligibility
        min_impot = self.rules["eligibility"]["min_impot"]
        if impot_net < min_impot:
            return recommendations

        # Girardin requires medium to high risk tolerance
        if risk_tolerance not in ["medium", "high", "aggressive"]:
            return recommendations

        # Stable income is important
        if not stable_income:
            return recommendations

        # Generate Girardin Industriel recommendation (110% reduction)
        rec = self._create_girardin_industriel_recommendation(impot_net)
        recommendations.append(rec)

        return recommendations

    def _create_girardin_industriel_recommendation(
        self, impot_net: float
    ) -> Recommendation:
        """Create Girardin Industriel recommendation with Profina."""
        # Calculate optimal investment using rules from JSON
        industriel_rules = self.rules["types"]["industriel"]
        reduction_rate = industriel_rules["reduction_rate"]

        # Get investment parameters from JSON
        investment_rules = self.rules["recommended_investment"]
        target_reduction_rate = investment_rules["target_reduction_rate"]
        min_tax_remaining = investment_rules["min_tax_remaining"]

        # Calculate optimal investment
        target_reduction = min(
            impot_net * target_reduction_rate, impot_net - min_tax_remaining
        )
        optimal_investment = target_reduction / reduction_rate

        # Net gain = reduction - investment
        net_gain = target_reduction - optimal_investment

        # Get Profina info
        profina = self.rules["recommended_provider"]

        # Map risk level from JSON
        risk_level_map = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
        }
        risk = risk_level_map.get(industriel_rules["risk"], RiskLevel.HIGH)

        rendement_pct = (net_gain / optimal_investment) * 100
        commitment_years = industriel_rules["commitment_years"]

        description = (
            f"🌴 Girardin Industriel - Défiscalisation Outre-Mer via Profina\n\n"
            f"Le dispositif Girardin Industriel permet d'obtenir une réduction "
            f"d'impôt de **110%** du montant investi dans des équipements "
            f"productifs en Outre-Mer.\n\n"
            f"**Pour votre situation (impôt de {impot_net:.2f}€) :**\n"
            f"- Investissement recommandé : {optimal_investment:.2f}€\n"
            f"- Réduction d'impôt : {target_reduction:.2f}€\n"
            f"- Gain net : +{net_gain:.2f}€ (rendement {rendement_pct:.1f}%)\n\n"
            f"**Opérateur recommandé : {profina['name']}**\n"
            f"{profina['description']}\n\n"
            f"**Pourquoi Profina ?**\n"
        )

        for advantage in profina["advantages"]:
            description += f"- {advantage}\n"

        description += (
            f"\n🌐 Site : {profina['website']}\n\n"
            f"**⚠️ Important :** Le Girardin est un investissement à risque. "
            f"La réduction est acquise immédiatement, mais l'engagement est de "
            f"{commitment_years} ans. Profina sécurise les montages "
            f"mais le risque zéro n'existe pas."
        )

        action_steps = [
            f"Contacter Profina ({profina['website']})",
            "Demander une simulation personnalisée",
            "Vérifier l'agrément fiscal du projet proposé",
            "Lire attentivement la notice d'information",
            "Souscrire avant le 31 décembre pour bénéficier de la réduction",
            "Conserver les justificatifs pour la déclaration fiscale",
            "Déclarer la réduction sur votre déclaration 2042 C",
        ]

        warnings_list = self.rules["warnings"].copy()
        warnings_list.insert(
            0,
            "Profina recommandé : opérateur de confiance, vérifier le projet",
        )

        return Recommendation(
            id=str(uuid.uuid4()),
            title="Girardin Industriel via Profina - Réduction 110%",
            description=description,
            impact_estimated=net_gain,
            risk=risk,
            complexity=ComplexityLevel.MODERATE,
            confidence=0.75,
            category=RecommendationCategory.INVESTMENT,
            sources=self.rules.get(
                "sources",
                [
                    "https://www.economie.gouv.fr/particuliers/fiscalite-outre-mer-girardin",
                    "https://bofip.impots.gouv.fr/bofip/2194-PGP.html",
                    "https://www.profina.fr",
                ],
            ),
            action_steps=action_steps,
            required_investment=optimal_investment,
            eligibility_criteria=[
                f"Impôt sur le revenu >= {self.rules['eligibility']['min_impot']}€",
                "Revenus stables et récurrents",
                "Tolérance au risque moyenne à élevée",
                "Horizon d'engagement 5 ans",
            ],
            warnings=warnings_list,
            deadline="31 décembre de l'année en cours",
            roi_years=1.0,  # Immediate tax reduction, but 5-year commitment
        )
