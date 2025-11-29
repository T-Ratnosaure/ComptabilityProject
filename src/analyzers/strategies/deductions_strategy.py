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


class DeductionsStrategy:
    """Analyzes simple deduction optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the deductions strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "optimization_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["deductions"]

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

        # Calculate plafond (20% of taxable income)
        plafond = revenu_imposable * dons_rules["plafond_rate"]

        # If user hasn't maxed out and has some income
        if current_dons < plafond and revenu_imposable > 10000:
            # Suggest modest donation
            suggested_don = min(500, (plafond - current_dons) * 0.3)
            reduction = suggested_don * dons_rules["reduction_rate"]

            description = (
                f"🎁 Dons aux associations - Réduction d'impôt 66%\n\n"
                f"Les dons aux associations ouvrent droit à une réduction d'impôt "
                f"de {dons_rules['reduction_rate'] * 100:.0f}%, plafonné à {dons_rules['plafond_rate'] * 100:.0f}% "
                f"de votre revenu imposable.\n\n"
                f"**Votre situation :**\n"
                f"- Plafond disponible : {plafond:.2f}€\n"
                f"- Dons déjà déclarés : {current_dons:.2f}€\n"
                f"- Marge restante : {plafond - current_dons:.2f}€\n\n"
                f"**Exemple :** Un don de {suggested_don:.2f}€ vous coûterait "
                f"réellement {suggested_don - reduction:.2f}€ après réduction d'impôt "
                f"({reduction:.2f}€ de réduction)."
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
                    f"Plafond : {dons_rules['plafond_rate'] * 100:.0f}% du revenu imposable",
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

        # Only recommend if user has tax to pay
        if impot_net < 500:
            return None

        plafond = services_rules["plafond"]

        if current_services < plafond * 0.5:  # User hasn't used much yet
            # Suggest using services
            suggested_expense = min(2000, plafond - current_services)
            credit = suggested_expense * services_rules["credit_rate"]

            description = (
                f"🏡 Services à la personne - Crédit d'impôt 50%\n\n"
                f"Les services à la personne ouvrent droit à un crédit d'impôt "
                f"de {services_rules['credit_rate'] * 100:.0f}%, plafonné à {plafond:.2f}€/an.\n\n"
                f"**Services éligibles :**\n"
            )

            for service in services_rules["examples"]:
                description += f"- {service}\n"

            description += (
                f"\n**Exemple :** Des dépenses de {suggested_expense:.2f}€ "
                f"vous donneraient un crédit d'impôt de {credit:.2f}€.\n"
                f"Coût réel : {suggested_expense - credit:.2f}€"
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

            description = (
                f"👶 Frais de garde d'enfants - Crédit 50%\n\n"
                f"Les frais de garde d'enfants de moins de {garde_rules['age_limit']} ans "
                f"ouvrent droit à un crédit d'impôt de {garde_rules['credit_rate'] * 100:.0f}%, "
                f"plafonné à {garde_rules['plafond_per_child']}€ par enfant.\n\n"
                f"**Votre situation :**\n"
                f"- Nombre d'enfants < 6 ans : {children_under_6}\n"
                f"- Plafond total : {plafond_total}€\n"
                f"- Frais déclarés : {current_frais:.2f}€\n\n"
                f"**Exemple :** {suggested_expense:.2f}€ de frais de garde "
                f"= {credit:.2f}€ de crédit d'impôt."
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
                    "Utiliser une crèche, assistante maternelle agréée, ou garde à domicile",
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
