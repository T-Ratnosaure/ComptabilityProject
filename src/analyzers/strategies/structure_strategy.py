"""Company structure optimization strategy."""

import json
import uuid
from pathlib import Path

from src.models.optimization import (
    ComplexityLevel,
    Recommendation,
    RecommendationCategory,
    RiskLevel,
)


class StructureStrategy:
    """Analyzes company structure optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the structure strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "optimization_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["structure_thresholds"]

    def analyze(
        self, tax_result: dict, profile: dict, context: dict
    ) -> list[Recommendation]:
        """
        Analyze company structure optimization opportunities.

        Args:
            tax_result: Result from tax calculation engine
            profile: User profile with revenue and expenses
            context: Additional context

        Returns:
            List of structure recommendations
        """
        recommendations = []

        # Extract data with support for both standardized and legacy field names
        annual_revenue = profile.get("chiffre_affaires") or profile.get(
            "annual_revenue", 0
        )
        annual_expenses = profile.get("charges_deductibles") or profile.get(
            "annual_expenses", 0
        )

        # Calculate charges rate
        charges_rate = annual_expenses / annual_revenue if annual_revenue > 0 else 0

        current_status = profile.get("status", "").lower()

        # Check if user is currently a micro-entrepreneur or individual
        is_individual = any(
            keyword in current_status for keyword in ["micro", "bnc", "bic", "auto"]
        )

        if not is_individual:
            # Already has a company structure
            return recommendations

        # Check SASU/EURL threshold
        sasu_threshold = self.rules["consider_sasu"]
        if (
            annual_revenue >= sasu_threshold["ca_min"]
            and charges_rate >= sasu_threshold["charges_rate_min"]
        ):
            rec = self._create_sasu_eurl_recommendation(
                annual_revenue, charges_rate, tax_result
            )
            recommendations.append(rec)

        # Check holding threshold (more advanced)
        holding_threshold = self.rules["consider_holding"]
        if annual_revenue >= holding_threshold["ca_min"]:
            holding_rec = self._create_holding_recommendation(annual_revenue, context)
            if holding_rec:
                recommendations.append(holding_rec)

        return recommendations

    def _create_sasu_eurl_recommendation(
        self, annual_revenue: float, charges_rate: float, tax_result: dict
    ) -> Recommendation:
        """Create SASU/EURL recommendation."""
        charges_pct = charges_rate * 100
        rounded_revenue = round(annual_revenue, -3)
        description = (
            f"🏢 Structuration en société - Comment ça fonctionne\n\n"
            f"📊 **Exemple illustratif basé sur votre profil**\n"
            f"Avec un CA d'environ {rounded_revenue:,.0f}€ et un taux de charges "
            f"d'environ {charges_pct:.0f}%, une société soumise à l'IS "
            f"(Impôt sur les Sociétés) pourrait potentiellement optimiser "
            f"votre fiscalité.\n\n"
            f"**Avantages fiscaux :**\n"
            f"- IS à 15% jusqu'à 42 500€ de bénéfice (puis 25%)\n"
            f"- Arbitrage rémunération/dividendes optimisable\n"
            f"- Déduction de nombreuses charges (véhicule, loyer bureau, etc.)\n"
            f"- Possibilité de lisser les revenus dans le temps\n"
            f"- Protection patrimoniale (séparation patrimoine pro/perso)\n\n"
            f"**SASU (Société par Actions Simplifiée Unipersonnelle) :**\n"
            f"- Président assimilé salarié (régime général)\n"
            f"- Cotisations sociales ~65% du salaire net\n"
            f"- Flexibilité des statuts\n"
            f"- Cession facilitée\n\n"
            f"**EURL (Entreprise Unipersonnelle à Responsabilité Limitée) :**\n"
            f"- Gérant majoritaire = TNS (Travailleur Non Salarié)\n"
            f"- Cotisations sociales ~45% du salaire net\n"
            f"- Moins de charges sociales mais moins de protection\n\n"
            f"**⚠️ Important :** Ce type de transformation nécessite une étude "
            f"approfondie par un expert-comptable et un avocat fiscaliste. "
            f"Les informations ci-dessus sont fournies à titre éducatif uniquement."
        )

        action_steps = [
            "Consulter un expert-comptable spécialisé",
            "Faire une simulation complète (IS vs IR)",
            "Évaluer l'impact sur les cotisations sociales",
            "Comparer SASU vs EURL selon votre situation",
            "Préparer le business plan et les statuts",
            "Anticiper les coûts de création et de gestion",
            "Planifier la transition (timing, fiscalité)",
            "Ne pas décider uniquement pour la fiscalité",
        ]

        # Get estimated savings and costs from JSON
        sasu_rules = self.rules["consider_sasu"]
        estimated_savings_rate = sasu_rules["estimated_savings_rate"]
        creation_cost = sasu_rules["creation_cost"]

        # Estimated savings are hard to calculate without full simulation
        estimated_savings = annual_revenue * estimated_savings_rate

        return Recommendation(
            id=str(uuid.uuid4()),
            title="Structure SASU/EURL IS - Scénario optimisation",
            description=description,
            impact_estimated=estimated_savings,
            risk=RiskLevel.MEDIUM,
            complexity=ComplexityLevel.COMPLEX,
            confidence=0.60,  # Requires detailed analysis
            category=RecommendationCategory.STRUCTURE,
            sources=[
                "https://www.service-public.fr/professionnels-entreprises/vosdroits/F23266",
                "https://www.impots.gouv.fr/professionnel/limpot-sur-les-societes-is",
            ],
            action_steps=action_steps,
            required_investment=creation_cost,
            eligibility_criteria=[
                f"CA >= {self.rules['consider_sasu']['ca_min']}€",
                f"Taux charges >= "
                f"{self.rules['consider_sasu']['charges_rate_min'] * 100:.0f}%",
                "Activité pérenne et récurrente",
            ],
            warnings=[
                "Coûts de création (1 500 - 3 000€)",
                "Coûts de gestion annuels (expert-comptable obligatoire)",
                "Complexité administrative accrue",
                "Obligations comptables et juridiques",
                "Nécessite une étude approfondie avant décision",
                "Consulter OBLIGATOIREMENT un expert-comptable ET un avocat fiscaliste",
            ],
            deadline=None,
            roi_years=2.0,
        )

    def _create_holding_recommendation(
        self, annual_revenue: float, context: dict
    ) -> Recommendation | None:
        """Create holding structure recommendation."""
        # Only suggest if user has patrimony strategy
        has_patrimony_strategy = context.get("patrimony_strategy", False)

        if not has_patrimony_strategy:
            return None

        rounded_revenue = round(annual_revenue, -3)
        description = (
            f"🏛️ Holding patrimoniale - Structuration avancée\n\n"
            f"📊 **Information générale**\n"
            f"Avec un CA d'environ {rounded_revenue:,.0f}€ et une stratégie "
            f"patrimoniale, une holding peut offrir des avantages.\n\n"
            f"**Structure type :**\n"
            f"- HOLDING (SASU ou EURL) détient 100% de l'EXPLOITATION\n"
            f"- + éventuellement SCI pour l'immobilier professionnel\n\n"
            f"**Avantages :**\n"
            f"- Remontée de dividendes mère-fille en quasi-franchise d'impôt (1,67%)\n"
            f"- Mutualisation de trésorerie entre filiales\n"
            f"- Optimisation transmission (pacte Dutreil)\n"
            f"- Protection patrimoniale renforcée\n"
            f"- Investissements via la holding (LBO, participations)\n\n"
            f"**⚠️ ATTENTION :** Montage complexe réservé aux situations :\n"
            f"- CA > 100k€ stable\n"
            f"- Stratégie patrimoniale long terme\n"
            f"- Conseil d'expert-comptable ET avocat fiscaliste indispensable\n\n"
            f"📌 *Ces informations sont fournies à titre éducatif. "
            f"Une étude personnalisée par des professionnels est indispensable.*"
        )

        # Get estimated savings and costs from JSON
        holding_rules = self.rules["consider_holding"]
        estimated_savings_rate = holding_rules["estimated_savings_rate"]
        creation_cost = holding_rules["creation_cost"]

        return Recommendation(
            id=str(uuid.uuid4()),
            title="Holding patrimoniale - Scénario structure avancée",
            description=description,
            impact_estimated=annual_revenue * estimated_savings_rate,
            risk=RiskLevel.MEDIUM,
            complexity=ComplexityLevel.COMPLEX,
            confidence=0.50,  # Highly situation-dependent
            category=RecommendationCategory.STRUCTURE,
            sources=[
                "https://www.service-public.fr/professionnels-entreprises/vosdroits/F31963",
                "https://bofip.impots.gouv.fr/bofip/4802-PGP.html",
            ],
            action_steps=[
                "Définir votre stratégie patrimoniale à 10+ ans",
                "Consulter un cabinet spécialisé en ingénierie patrimoniale",
                "Faire une simulation complète des flux financiers",
                "Évaluer les coûts de structure (création + gestion annuelle)",
                "Anticiper les aspects juridiques et fiscaux",
                "Ne jamais décider seul - expertise obligatoire",
            ],
            required_investment=creation_cost,
            eligibility_criteria=[
                f"CA >= {self.rules['consider_holding']['ca_min']}€",
                "Stratégie patrimoniale long terme",
                "Vision entrepreneuriale multi-activités",
            ],
            warnings=[
                "Montage très complexe",
                "Coûts de structure élevés (création + gestion)",
                "Obligations comptables multiples",
                "Expertise professionnelle INDISPENSABLE",
                "Pas adapté à tous les profils",
            ],
            deadline=None,
            roi_years=5.0,
        )
