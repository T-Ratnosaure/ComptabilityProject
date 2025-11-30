"""Regime optimization strategy (micro vs réel)."""

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
from src.tax_engine.tax_utils import check_micro_threshold_proximity


class RegimeStrategy:
    """Analyzes regime optimization opportunities (micro vs réel)."""

    def __init__(self) -> None:
        """Initialize the regime strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "optimization_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)

        # Load tax rules for centralized utilities
        self.tax_rules = get_tax_rules(2024)

    def analyze(
        self, tax_result: dict, profile: dict, context: dict
    ) -> list[Recommendation]:
        """
        Analyze regime optimization opportunities.

        Args:
            tax_result: Result from tax calculation engine
            profile: User profile with status, revenue, expenses
            context: Additional context (current regime, etc.)

        Returns:
            List of regime optimization recommendations
        """
        recommendations = []

        # Get regime optimization thresholds from JSON
        regime_opt = self.rules.get("regime_optimization", {})
        min_delta = regime_opt.get("min_delta_for_recommendation", 500)

        # Check if micro vs réel comparison is available
        if "comparisons" in tax_result and "micro_vs_reel" in tax_result["comparisons"]:
            comparison = tax_result["comparisons"]["micro_vs_reel"]

            # If delta is significant, recommend a switch
            if abs(comparison["delta_total"]) > min_delta:
                rec = self._create_regime_recommendation(comparison, profile, context)
                if rec:
                    recommendations.append(rec)

        # Check if user is approaching micro thresholds
        threshold_warning = self._check_threshold_proximity(profile)
        if threshold_warning:
            recommendations.append(threshold_warning)

        return recommendations

    def _create_regime_recommendation(
        self, comparison: dict, profile: dict, context: dict
    ) -> Recommendation | None:
        """Create recommendation based on regime comparison."""
        current_regime = profile.get("status", "unknown")
        recommended = comparison.get("recommendation", "")
        delta = comparison.get("delta_total", 0)

        # Only recommend if there's a clear winner different from current
        if not recommended or delta == 0:
            return None

        # Determine if we should recommend switching
        should_recommend_micro = (
            recommended == "micro" and "reel" in current_regime.lower()
        )
        should_recommend_reel = (
            recommended == "reel" and "micro" in current_regime.lower()
        )

        if not (should_recommend_micro or should_recommend_reel):
            return None

        # Build recommendation
        target_regime = "micro-BNC" if recommended == "micro" else "réel"
        impact = abs(delta)

        description = (
            f"Vous êtes actuellement en régime {current_regime}. "
            f"Un passage au régime {target_regime} pourrait vous faire économiser "
            f"environ {impact:.2f}€ d'impôt sur le revenu.\n\n"
            f"{comparison.get('recommendation_reason', '')}"
        )

        action_steps = []
        if recommended == "reel":
            action_steps = [
                "Tenir une comptabilité détaillée de vos charges professionnelles",
                "Conserver tous les justificatifs (factures, tickets)",
                "Faire appel à un expert-comptable",
                "Opter pour le régime réel lors de votre déclaration 2042-C-PRO",
                "L'option est valable 2 ans minimum",
            ]
        else:
            action_steps = [
                "Simplifier votre comptabilité (pas de livre de comptes)",
                "Déclarer uniquement votre chiffre d'affaires",
                "Bénéficier de l'abattement forfaitaire automatique",
                "Option à exercer lors de la déclaration annuelle",
            ]

        return Recommendation(
            id=str(uuid.uuid4()),
            title=f"Optimisation régime fiscal : passage au {target_regime}",
            description=description,
            impact_estimated=impact,
            risk=RiskLevel.LOW,
            complexity=(
                ComplexityLevel.MODERATE
                if recommended == "reel"
                else ComplexityLevel.EASY
            ),
            confidence=0.85,
            category=RecommendationCategory.REGIME,
            sources=[
                "https://www.impots.gouv.fr/particulier/questions/je-suis-en-regime-micro-bnc",
                "https://www.impots.gouv.fr/professionnel/questions/quelle-est-la-difference-entre-le-regime-reel-simplifie-et-le-regime",
            ],
            action_steps=action_steps,
            required_investment=0.0,
            eligibility_criteria=[
                f"Activité de type {profile.get('activity_type', 'BNC/BIC')}",
                "Chiffre d'affaires conforme aux seuils",
            ],
            warnings=[
                "Le changement de régime est valable au minimum 2 ans",
                "Calculer l'impact sur les cotisations sociales également",
                "Consulter un expert-comptable pour validation",
            ],
        )

    def _check_threshold_proximity(self, profile: dict) -> Recommendation | None:
        """Check if user is approaching micro regime thresholds."""
        # Support both standardized and legacy field names
        revenue = profile.get("chiffre_affaires") or profile.get("annual_revenue", 0)
        status = profile.get("status", "").lower()

        # Determine regime type for threshold check
        regime_type = None
        threshold_name = ""

        if "bnc" in status:
            regime_type = "bnc"
            threshold_name = "micro-BNC"
        elif "bic" in status and "service" in status:
            regime_type = "bic_service"
            threshold_name = "micro-BIC prestations"
        elif "bic" in status:
            regime_type = "bic_vente"
            threshold_name = "micro-BIC ventes"

        if not regime_type:
            return None

        # Get proximity alert threshold from JSON
        regime_opt = self.rules.get("regime_optimization", {})
        proximity_alert = regime_opt.get("threshold_proximity_alert", 0.85)

        # Use centralized function to check threshold proximity
        proximity_check = check_micro_threshold_proximity(
            revenue, regime_type, self.tax_rules, alert_threshold=proximity_alert
        )

        if proximity_check["approaching"]:
            threshold = proximity_check["threshold"]
            remaining = proximity_check["remaining"]
            description = (
                f"⚠️ Attention : votre chiffre d'affaires ({revenue:.2f}€) approche "
                f"le seuil du régime {threshold_name} ({threshold}€).\n\n"
                f"Il vous reste {remaining:.2f}€ de marge avant dépassement. "
                "Si vous dépassez ce seuil deux années consécutives, vous basculerez "
                "automatiquement au régime réel l'année suivante.\n\n"
                "Anticipez ce changement en préparant votre comptabilité."
            )

            return Recommendation(
                id=str(uuid.uuid4()),
                title=f"Alerte seuil {threshold_name}",
                description=description,
                impact_estimated=0.0,  # No direct savings, just a warning
                risk=RiskLevel.LOW,
                complexity=ComplexityLevel.EASY,
                confidence=1.0,
                category=RecommendationCategory.REGIME,
                sources=[
                    "https://www.impots.gouv.fr/professionnel/questions/quels-sont-les-seuils-du-regime-micro-entreprise"
                ],
                action_steps=[
                    "Surveiller votre CA en cours d'année",
                    "Anticiper le passage au réel si dépassement probable",
                    "Commencer à tenir une comptabilité détaillée",
                    "Consulter un expert-comptable",
                ],
                required_investment=0.0,
                eligibility_criteria=[],
                warnings=["Dépassement 2 ans consécutifs = basculement obligatoire"],
                deadline="31 décembre de l'année en cours",
            )

        return None
