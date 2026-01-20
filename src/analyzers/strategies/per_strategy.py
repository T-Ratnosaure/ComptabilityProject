"""PER (Plan Épargne Retraite) optimization strategy."""

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
from src.tax_engine.tax_utils import calculate_per_plafond


class PERStrategy:
    """Analyzes PER contribution optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the PER strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "per_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

        # Load tax rules for TMI calculation
        self.tax_rules = get_tax_rules(2024)

    def analyze(
        self, tax_result: dict, profile: dict, context: dict
    ) -> list[Recommendation]:
        """
        Analyze PER optimization opportunities.

        Args:
            tax_result: Result from tax calculation engine
            profile: User profile with revenue and deductions
            context: Additional context (savings capacity, etc.)

        Returns:
            List of PER recommendations
        """
        recommendations = []

        # Extract data from tax result
        revenu_imposable = tax_result.get("impot", {}).get("revenu_imposable", 0)
        per_contributed = context.get("per_contributed", 0)

        # Check minimum income eligibility from JSON
        min_income = self.rules["eligibility"]["min_income"]
        if revenu_imposable < min_income:
            # Not eligible for PER recommendation
            return recommendations

        # Get marginal tax rate (TMI) using centralized function
        nb_parts = profile.get("nb_parts", 1.0)
        tmi = calculate_tmi(revenu_imposable, nb_parts, self.tax_rules)

        if tmi < 0.11:
            # Not worth it for non-taxable people
            return recommendations

        # Calculate PER plafond using centralized function
        plafond = calculate_per_plafond(
            revenu_imposable, self.tax_rules, status="salarie"
        )

        # Calculate remaining room
        remaining_room = max(0, plafond - per_contributed)

        if remaining_room < self.rules["tmi_thresholds"]["0.11"]["min_interest"]:
            # Not enough room to be interesting
            return recommendations

        # Calculate potential gain
        potential_gain = remaining_room * tmi

        # Check if gain is significant enough
        min_interest = self._get_min_interest_for_tmi(tmi)
        if potential_gain < min_interest:
            return recommendations

        # Generate recommendations based on different modes
        optimal_rec = self._create_optimal_recommendation(
            remaining_room, plafond, per_contributed, tmi, potential_gain
        )
        recommendations.append(optimal_rec)

        # If TMI is high, also suggest max contribution
        if tmi >= 0.30 and remaining_room > 5000:
            max_rec = self._create_max_recommendation(
                remaining_room, tmi, potential_gain
            )
            recommendations.append(max_rec)

        return recommendations

    def _get_min_interest_for_tmi(self, tmi: float) -> float:
        """Get minimum interest threshold for a given TMI."""
        if tmi >= 0.45:
            return self.rules["tmi_thresholds"]["0.45"]["min_interest"]
        elif tmi >= 0.41:
            return self.rules["tmi_thresholds"]["0.41"]["min_interest"]
        elif tmi >= 0.30:
            return self.rules["tmi_thresholds"]["0.30"]["min_interest"]
        else:
            return self.rules["tmi_thresholds"]["0.11"]["min_interest"]

    def _create_optimal_recommendation(
        self,
        remaining_room: float,
        plafond: float,
        per_contributed: float,
        tmi: float,
        potential_gain: float,
    ) -> Recommendation:
        """Create optimal PER recommendation (70% of remaining room)."""
        optimal_mode = self.rules["recommendation_modes"]["optimal"]
        recommended_amount = remaining_room * optimal_mode["target_rate"]
        estimated_gain = recommended_amount * tmi

        # Round amounts for educational display
        rounded_amount = round(recommended_amount, -2)
        rounded_gain = round(estimated_gain, -2)
        rounded_room = round(remaining_room, -2)

        description = (
            f"💰 PER (Plan Épargne Retraite) - Comment ça fonctionne\n\n"
            f"📊 **Exemple illustratif basé sur votre profil**\n"
            f"• Si vous versiez environ **{rounded_amount:,.0f} €** sur un PER\n"
            f"• Réduction d'impôt potentielle : environ **{rounded_gain:,.0f} €**\n"
            f"• Votre TMI estimé : {tmi * 100:.0f}%\n"
            f"• Plafond restant approximatif : {rounded_room:,.0f} €\n\n"
            f"⚠️ **Épargne bloquée** jusqu'à la retraite\n"
            f"(sauf achat résidence principale, invalidité, décès)\n\n"
            f"📌 *Ces chiffres sont des estimations. "
            f"Consultez un CIF agréé ORIAS avant toute décision.*"
        )

        action_steps = [
            "Choisir un contrat PER (banque, assurance, mutuelle)",
            f"Effectuer un versement de {recommended_amount:.2f}€ avant le 31/12",
            "Déclarer le versement sur votre déclaration 2042 (case 6NS ou 6NT)",
            "Conserver les justificatifs de versement",
            "Choisir le mode de gestion (libre, pilotée, sécurisée)",
        ]

        return Recommendation(
            id=str(uuid.uuid4()),
            title="PER - Scénario versement optimal",
            description=description,
            impact_estimated=estimated_gain,
            risk=RiskLevel.LOW,
            complexity=ComplexityLevel.EASY,
            confidence=0.90,
            category=RecommendationCategory.INVESTMENT,
            sources=self.rules.get(
                "sources",
                [
                    "https://www.service-public.fr/particuliers/vosdroits/F34982",
                    "https://www.impots.gouv.fr/particulier/le-plan-depargne-retraite-individuel-peri",
                ],
            ),
            action_steps=action_steps,
            required_investment=recommended_amount,
            eligibility_criteria=[
                "Avoir des revenus professionnels imposables",
                f"Tranche marginale d'imposition de {tmi * 100:.0f}%",
            ],
            warnings=[
                "Épargne bloquée jusqu'à la retraite (sauf cas exceptionnels)",
                "Fiscalité à la sortie : rente ou capital imposable",
                "Comparer les frais entre différents contrats PER",
                "Ne pas mettre en PER l'argent nécessaire à court/moyen terme",
            ],
            deadline="31 décembre de l'année en cours",
            roi_years=None,  # Long-term retirement savings
        )

    def _create_max_recommendation(
        self, remaining_room: float, tmi: float, potential_gain: float
    ) -> Recommendation:
        """Create maximum PER recommendation (100% of remaining room)."""
        # Round amounts for educational display
        rounded_room = round(remaining_room, -2)
        rounded_gain = round(potential_gain, -2)

        description = (
            f"🚀 PER - Scénario maximisation du plafond\n\n"
            f"📊 **Exemple illustratif**\n"
            f"• Si vous versiez environ **{rounded_room:,.0f} €**\n"
            f"• Réduction d'impôt potentielle : environ **{rounded_gain:,.0f} €**\n"
            f"• TMI estimé : {tmi * 100:.0f}%\n\n"
            f"💡 Mécanisme : chaque euro versé réduit votre base imposable\n\n"
            f"⚠️ **Attention** : vérifiez vos liquidités avant tout versement. "
            f"Épargne bloquée jusqu'à la retraite.\n\n"
            f"📌 *Consultez un CIF agréé ORIAS avant toute décision d'investissement.*"
        )

        return Recommendation(
            id=str(uuid.uuid4()),
            title="PER - Scénario maximisation plafond",
            description=description,
            impact_estimated=potential_gain,
            risk=RiskLevel.LOW,
            complexity=ComplexityLevel.EASY,
            confidence=0.85,
            category=RecommendationCategory.INVESTMENT,
            sources=[
                "https://www.service-public.fr/particuliers/vosdroits/F34982",
                "https://www.impots.gouv.fr/particulier/le-plan-depargne-retraite-individuel-peri",
            ],
            action_steps=[
                f"Effectuer un versement maximum de {remaining_room:.2f}€",
                "Vérifier votre capacité d'épargne avant le versement",
                "Déclarer en case 6NS/6NT de la 2042",
                "Documenter pour l'administration fiscale",
            ],
            required_investment=remaining_room,
            eligibility_criteria=[
                f"Capacité d'épargne de {remaining_room:.2f}€",
                f"TMI de {tmi * 100:.0f}%",
            ],
            warnings=[
                "Stratégie agressive - vérifier vos liquidités",
                "Épargne bloquée jusqu'à la retraite",
                "Bien choisir le contrat (frais, performances)",
            ],
            deadline="31 décembre de l'année en cours",
        )
