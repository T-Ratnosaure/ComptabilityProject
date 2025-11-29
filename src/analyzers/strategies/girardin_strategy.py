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
        # Calculate optimal investment
        # Aim for ~30-50% of annual tax with 110% return
        industriel_rules = self.rules["types"]["industriel"]
        reduction_rate = industriel_rules["reduction_rate"]

        # Suggest investing to get 30-40% of tax back
        target_reduction = min(impot_net * 0.35, impot_net - 500)
        optimal_investment = target_reduction / reduction_rate

        # Net gain = reduction - investment
        net_gain = target_reduction - optimal_investment

        # Get Profina info
        profina = self.rules["recommended_provider"]

        description = (
            f"🌴 Girardin Industriel - Défiscalisation Outre-Mer via Profina\n\n"
            f"Le dispositif Girardin Industriel permet d'obtenir une réduction d'impôt "
            f"de **110%** du montant investi dans des équipements productifs en Outre-Mer.\n\n"
            f"**Pour votre situation (impôt de {impot_net:.2f}€) :**\n"
            f"- Investissement recommandé : {optimal_investment:.2f}€\n"
            f"- Réduction d'impôt : {target_reduction:.2f}€\n"
            f"- Gain net : +{net_gain:.2f}€ (rendement {(net_gain / optimal_investment) * 100:.1f}%)\n\n"
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
            f"{industriel_rules['commitment_years']} ans. Profina sécurise les montages "
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
            "Recommandation Profina : opérateur de confiance mais toujours vérifier le projet",
        )

        return Recommendation(
            id=str(uuid.uuid4()),
            title="Girardin Industriel via Profina - Réduction 110%",
            description=description,
            impact_estimated=net_gain,
            risk=RiskLevel.HIGH,
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
