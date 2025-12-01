"""Simple deductions and tax credits optimization strategy."""

import json
import uuid
from pathlib import Path

from src.models.optimization import (
    ComplexityLevel,
    Recommendation,
    RecommendationCategory,
    RiskLevel,
)
from src.tax_engine.rules import get_tax_rules
from src.tax_engine.tax_utils import (
    calculate_tax_reduction,
    get_tax_reduction_plafond,
)


class DeductionsStrategy:
    """Analyzes simple deduction optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the deductions strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "optimization_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["deductions"]

        # Load tax rules for centralized fiscal values
        self.tax_rules = get_tax_rules(2024)

    def analyze(
        self, tax_result: dict, profile: dict, context: dict
    ) -> list[Recommendation]:
        """
        Analyze deduction optimization opportunities.

        Args:
            tax_result: Result from tax calculation engine
            profile: User profile
            context: Additional context (family situation, services used)

        Returns:
            List of deduction recommendations
        """
        recommendations = []

        # Check for donations opportunity
        dons_rec = self._analyze_dons(tax_result, context)
        if dons_rec:
            recommendations.append(dons_rec)

        # Check for services à la personne
        services_rec = self._analyze_services_personne(tax_result, context)
        if services_rec:
            recommendations.append(services_rec)

        # Check for childcare credits
        garde_rec = self._analyze_frais_garde(tax_result, context)
        if garde_rec:
            recommendations.append(garde_rec)

        return recommendations

    def _analyze_dons(self, tax_result: dict, context: dict) -> Recommendation | None:
        """Analyze donation deduction opportunities."""
        dons_rules = self.rules["dons"]

        current_dons = context.get("dons_declared", 0)
        revenu_imposable = tax_result.get("impot", {}).get("revenu_imposable", 0)

        # Calculate plafond using centralized function
        plafond = get_tax_reduction_plafond(
            "dons", self.tax_rules, revenu_imposable=revenu_imposable
        )

        # Get recommendation thresholds from JSON (business logic)
        min_income = dons_rules["min_income_for_recommendation"]
        suggested_amount = dons_rules["suggested_amount"]

        # If user hasn't maxed out and has some income
        if current_dons < plafond and revenu_imposable > min_income:
            # Suggest modest donation
            suggested_don = min(suggested_amount, (plafond - current_dons) * 0.3)

            # Calculate reduction using centralized function
            reduction, _ = calculate_tax_reduction(
                "dons", suggested_don, self.tax_rules, revenu_imposable=revenu_imposable
            )

            # Get rates from centralized source for display
            tax_red_config = self.tax_rules.tax_reductions["dons"]
            reduction_pct = tax_red_config["rate"] * 100
            plafond_pct = tax_red_config["plafond_rate"] * 100
            description = (
                f"🎁 Faites un don à une association\n\n"
                f"📊 **Résumé**\n"
                f"• Don suggéré : **{suggested_don:.0f} €**\n"
                f"• Réduction d'impôt : **{reduction:.0f} €** ({reduction_pct:.0f}%)\n"
                f"• Coût réel : {suggested_don - reduction:.0f} €\n"
                f"• Plafond restant : {plafond - current_dons:.0f} €\n\n"
                f"💡 Un don de {suggested_don:.0f} € ne vous coûte "
                f"que {suggested_don - reduction:.0f} € !"
            )

            return Recommendation(
                id=str(uuid.uuid4()),
                title="Dons aux associations - Réduction 66%",
                description=description,
                impact_estimated=reduction,
                risk=RiskLevel.LOW,
                complexity=ComplexityLevel.EASY,
                confidence=0.95,
                category=RecommendationCategory.DEDUCTION,
                sources=dons_rules.get(
                    "sources",
                    ["https://www.service-public.fr/particuliers/vosdroits/F426"],
                ),
                action_steps=[
                    "Choisir une association reconnue d'utilité publique",
                    "Effectuer votre don avant le 31 décembre",
                    "Conserver le reçu fiscal",
                    "Déclarer en case 7UF de la déclaration 2042 RICI",
                ],
                required_investment=suggested_don,
                eligibility_criteria=[
                    "Association reconnue d'intérêt général",
                    f"Plafond : {plafond_pct:.0f}% du revenu imposable",
                ],
                warnings=[
                    "Conserver les justificatifs pendant 3 ans",
                    "Vérifier l'éligibilité de l'association",
                ],
                deadline="31 décembre de l'année en cours",
            )

        return None

    def _analyze_services_personne(
        self, tax_result: dict, context: dict
    ) -> Recommendation | None:
        """Analyze services à la personne credit opportunities."""
        services_rules = self.rules["services_personne"]

        current_services = context.get("services_personne_declared", 0)
        impot_net = tax_result.get("impot", {}).get("impot_net", 0)

        # Get recommendation threshold from JSON
        min_impot = services_rules["min_impot_for_recommendation"]

        # Only recommend if user has tax to pay
        if impot_net < min_impot:
            return None

        plafond = services_rules["plafond"]

        if current_services < plafond * 0.5:  # User hasn't used much yet
            # Suggest using services
            suggested_expense = min(2000, plafond - current_services)
            credit = suggested_expense * services_rules["credit_rate"]
            credit_pct = services_rules["credit_rate"] * 100

            description = (
                f"🏠 Services à la personne\n\n"
                f"📊 **Résumé**\n"
                f"• Dépenses suggérées : **{suggested_expense:.0f} €**\n"
                f"• Crédit d'impôt : **{credit:.0f} €** ({credit_pct:.0f}%)\n"
                f"• Coût réel : {suggested_expense - credit:.0f} €\n"
                f"• Plafond annuel : {plafond:.0f} €\n\n"
                f"✅ **Services éligibles**\n"
                f"• Ménage, repassage\n"
                f"• Jardinage, bricolage\n"
                f"• Garde d'enfants\n"
                f"• Aide aux personnes âgées"
            )

            return Recommendation(
                id=str(uuid.uuid4()),
                title="Services à la personne - Crédit 50%",
                description=description,
                impact_estimated=credit,
                risk=RiskLevel.LOW,
                complexity=ComplexityLevel.EASY,
                confidence=0.90,
                category=RecommendationCategory.DEDUCTION,
                sources=services_rules.get(
                    "sources",
                    ["https://www.service-public.fr/particuliers/vosdroits/F12"],
                ),
                action_steps=[
                    "Choisir un prestataire agréé services à la personne",
                    "Utiliser CESU ou virement pour le paiement",
                    "Conserver les attestations fiscales",
                    "Déclarer en case 7DB de la 2042 RICI",
                ],
                required_investment=suggested_expense,
                eligibility_criteria=[
                    "Prestataire agréé services à la personne",
                    f"Plafond annuel : {plafond}€",
                ],
                warnings=[
                    "Le crédit d'impôt est versé même si vous n'êtes pas imposable",
                    "Conserver les justificatifs",
                ],
            )

        return None

    def _analyze_frais_garde(
        self, tax_result: dict, context: dict
    ) -> Recommendation | None:
        """Analyze childcare expense credit opportunities."""
        garde_rules = self.rules["frais_garde"]

        children_under_6 = context.get("children_under_6", 0)

        if children_under_6 == 0:
            return None

        current_frais = context.get("frais_garde_declared", 0)
        plafond_total = garde_rules["plafond_per_child"] * children_under_6

        if current_frais < plafond_total * 0.5:
            suggested_expense = min(3000, (plafond_total - current_frais) * 0.6)
            credit = suggested_expense * garde_rules["credit_rate"]
            credit_pct = garde_rules["credit_rate"] * 100
            plafond_per_child = garde_rules["plafond_per_child"]

            description = (
                f"👶 Frais de garde d'enfants\n\n"
                f"📊 **Résumé**\n"
                f"• Frais déclarables : **{suggested_expense:.0f} €**\n"
                f"• Crédit d'impôt : **{credit:.0f} €** ({credit_pct:.0f}%)\n"
                f"• Plafond : {plafond_per_child} € par enfant\n\n"
                f"👨‍👩‍👧 **Votre situation**\n"
                f"• {children_under_6} enfant(s) de moins de 6 ans\n"
                f"• Plafond total : {plafond_total:.0f} €"
            )

            return Recommendation(
                id=str(uuid.uuid4()),
                title=f"Frais de garde ({children_under_6} enfant(s)) - Crédit 50%",
                description=description,
                impact_estimated=credit,
                risk=RiskLevel.LOW,
                complexity=ComplexityLevel.EASY,
                confidence=0.95,
                category=RecommendationCategory.DEDUCTION,
                sources=garde_rules.get(
                    "sources",
                    ["https://www.service-public.fr/particuliers/vosdroits/F8"],
                ),
                action_steps=[
                    "Crèche, assistante maternelle agréée, ou garde à domicile",
                    "Conserver les attestations",
                    "Déclarer en case 7GA/7GB/7GC de la 2042 RICI",
                ],
                required_investment=suggested_expense,
                eligibility_criteria=[
                    f"Enfant(s) de moins de {garde_rules['age_limit']} ans",
                    f"Plafond : {garde_rules['plafond_per_child']}€/enfant",
                ],
                warnings=[
                    "Garde à domicile hors du domicile non éligible",
                    "Conserver les justificatifs",
                ],
            )

        return None
