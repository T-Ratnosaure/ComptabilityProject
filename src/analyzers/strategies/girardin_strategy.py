"""Girardin optimization strategy with optional partner recommendation."""

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
            context: Additional context (risk tolerance, stable income, etc.)

        Returns:
            List of Girardin recommendations
        """
        recommendations = []

        # Extract data
        impot_net = tax_result.get("impot", {}).get("impot_net", 0)
        risk_tolerance = context.get("risk_tolerance", "low")
        stable_income = context.get("stable_income", False)
        show_partners = context.get("show_partner_suggestions", False)

        # Check eligibility
        min_impot = self.rules["eligibility"]["min_impot"]
        if impot_net < min_impot:
            return recommendations

        # Girardin requires medium to high risk tolerance
        if risk_tolerance not in ["medium", "moderate", "high", "aggressive"]:
            return recommendations

        # Stable income is important
        if not stable_income:
            return recommendations

        # Generate Girardin Industriel recommendation (110% reduction)
        rec = self._create_girardin_industriel_recommendation(impot_net, show_partners)
        recommendations.append(rec)

        return recommendations

    def _create_girardin_industriel_recommendation(
        self, impot_net: float, show_partners: bool = False
    ) -> Recommendation:
        """Create Girardin Industriel recommendation."""
        # Calculate optimal investment using rules from JSON
        industriel_rules = self.rules["types"]["industriel"]
        reduction_rate = industriel_rules["reduction_rate"]

        # Get investment parameters from JSON
        investment_rules = self.rules["recommended_investment"]
        target_reduction_rate = investment_rules["target_reduction_rate"]
        min_tax_remaining = investment_rules["min_tax_remaining"]

        # Get legal ceiling from JSON (plafond de plein droit = 40 909€)
        plafonds = self.rules.get("plafonds", {})
        max_reduction_plein_droit = plafonds.get("plein_droit", {}).get(
            "max_reduction", 40909
        )

        # Calculate optimal investment with legal ceiling
        target_reduction = min(
            impot_net * target_reduction_rate,
            impot_net - min_tax_remaining,
            max_reduction_plein_droit,  # Apply legal ceiling
        )
        optimal_investment = target_reduction / reduction_rate

        # Net gain = reduction - investment
        net_gain = target_reduction - optimal_investment

        # Map risk level from JSON
        risk_level_map = {
            "low": RiskLevel.LOW,
            "medium": RiskLevel.MEDIUM,
            "high": RiskLevel.HIGH,
        }
        risk = risk_level_map.get(industriel_rules["risk"], RiskLevel.HIGH)

        rendement_pct = (net_gain / optimal_investment) * 100
        commitment_years = industriel_rules["commitment_years"]

        # Build description based on whether partner suggestions are enabled
        if show_partners:
            # Get Profina info
            profina = self.rules["recommended_provider"]
            description = (
                f"Girardin Industriel - Defiscalisation Outre-Mer via Profina\n\n"
                f"Le dispositif Girardin Industriel permet d'obtenir une reduction "
                f"d'impot de **110%** du montant investi dans des equipements "
                f"productifs en Outre-Mer.\n\n"
                f"**Pour votre situation (impot de {impot_net:.2f} EUR) :**\n"
                f"- Investissement recommande : {optimal_investment:.2f} EUR\n"
                f"- Reduction d'impot : {target_reduction:.2f} EUR\n"
                f"- Gain net : +{net_gain:.2f} EUR (rendement {rendement_pct:.1f}%)\n\n"
                f"**Operateur recommande : {profina['name']}**\n"
                f"{profina['description']}\n\n"
                f"**Pourquoi Profina ?**\n"
            )
            for advantage in profina["advantages"]:
                description += f"- {advantage}\n"
            description += (
                f"\nSite : {profina['website']}\n\n"
                f"**Important :** Le Girardin est un investissement a risque. "
                f"La reduction est acquise immediatement, mais l'engagement est de "
                f"{commitment_years} ans. Profina securise les montages "
                f"mais le risque zero n'existe pas."
            )
            title = "Girardin Industriel via Profina - Reduction 110%"
            action_steps = [
                f"Contacter Profina ({profina['website']})",
                "Demander une simulation personnalisee",
                "Verifier l'agrement fiscal du projet propose",
                "Lire attentivement la notice d'information",
                "Souscrire avant le 31 decembre pour beneficier de la reduction",
                "Conserver les justificatifs pour la declaration fiscale",
                "Declarer la reduction sur votre declaration 2042 C",
            ]
        else:
            # Generic description without partner info
            description = (
                f"🌴 Girardin Industriel - Outre-Mer\n\n"
                f"📊 **Résumé**\n"
                f"• Investissement : **{optimal_investment:.0f} €**\n"
                f"• Réduction d'impôt : **{target_reduction:.0f} €** (110%)\n"
                f"• Gain net : **+{net_gain:.0f} €**\n"
                f"• Rendement : {rendement_pct:.1f}%\n\n"
                f"⏳ **Engagement** : {commitment_years} ans\n"
                f"📋 **Plafond légal** : {max_reduction_plein_droit:,.0f} € max/an\n\n"
                f"⚠️ Choisissez un opérateur agréé avec garantie de bonne fin"
            )
            title = "Girardin Industriel - Reduction 110%"
            action_steps = [
                "Rechercher des operateurs Girardin agrees",
                "Comparer les offres et les garanties proposees",
                "Verifier l'agrement fiscal du projet propose",
                "Lire attentivement la notice d'information",
                "Souscrire avant le 31 decembre pour beneficier de la reduction",
                "Conserver les justificatifs pour la declaration fiscale",
                "Declarer la reduction sur votre declaration 2042 C",
            ]

        warnings_list = self.rules["warnings"].copy()

        return Recommendation(
            id=str(uuid.uuid4()),
            title=title,
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
                ],
            ),
            action_steps=action_steps,
            required_investment=optimal_investment,
            eligibility_criteria=[
                f"Impot sur le revenu >= {self.rules['eligibility']['min_impot']} EUR",
                "Revenus stables et recurrents",
                "Tolerance au risque moyenne a elevee",
                "Horizon d'engagement 5 ans",
            ],
            warnings=warnings_list,
            deadline="31 decembre de l'annee en cours",
            roi_years=1.0,  # Immediate tax reduction, but 5-year commitment
        )
