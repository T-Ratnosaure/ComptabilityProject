"""Main tax optimization orchestrator."""

from src.analyzers.strategies.deductions_strategy import DeductionsStrategy
from src.analyzers.strategies.fcpi_fip_strategy import FCPIFIPStrategy
from src.analyzers.strategies.girardin_strategy import GirardinStrategy
from src.analyzers.strategies.lmnp_strategy import LMNPStrategy
from src.analyzers.strategies.per_strategy import PERStrategy
from src.analyzers.strategies.regime_strategy import RegimeStrategy
from src.analyzers.strategies.structure_strategy import StructureStrategy
from src.config import settings
from src.models.optimization import (
    OptimizationProfile,
    OptimizationResult,
    Recommendation,
)
from src.models.strategy_interdependencies import StrategyInteractionChecker


class TaxOptimizer:
    """Main tax optimization engine orchestrator."""

    # Map recommendation categories to strategy identifiers for interdependency checking
    CATEGORY_TO_STRATEGY = {
        "regime": "regime_change",
        "epargne_retraite": "per",
        "investissement_locatif": "lmnp",
        "defiscalisation": "girardin",  # Also covers FCPI/FIP
        "investissement": "fcpi_fip",
        "deductions": "deductions",
        "structure": "structure_change",
    }

    def __init__(self) -> None:
        """Initialize all optimization strategies."""
        self.regime_strategy = RegimeStrategy()
        self.per_strategy = PERStrategy()
        self.lmnp_strategy = LMNPStrategy()
        self.girardin_strategy = GirardinStrategy()
        self.fcpi_fip_strategy = FCPIFIPStrategy()
        self.deductions_strategy = DeductionsStrategy()
        self.structure_strategy = StructureStrategy()

        self.recommendations: list[Recommendation] = []
        self.interaction_checker = StrategyInteractionChecker()

    async def run(
        self,
        tax_result: dict,
        profile: dict,
        context: dict | None = None,
    ) -> OptimizationResult:
        """
        Run complete optimization analysis.

        Args:
            tax_result: Tax calculation result from Phase 3
            profile: User profile with revenue, expenses, status
            context: Additional context for optimization
                - risk_tolerance: "low", "medium", "high", "aggressive"
                - investment_capacity: float
                - stable_income: bool
                - per_contributed: float
                - dons_declared: float
                - services_personne_declared: float
                - frais_garde_declared: float
                - children_under_6: int
                - patrimony_strategy: bool

        Returns:
            OptimizationResult with all recommendations and summary
        """
        if context is None:
            context = {}

        # Inject config settings into context
        if "show_partner_suggestions" not in context:
            context["show_partner_suggestions"] = settings.SHOW_PARTNER_SUGGESTIONS

        # Reset recommendations
        self.recommendations = []

        # Apply each strategy
        self._apply_regime_strategy(tax_result, profile, context)
        self._apply_per_strategy(tax_result, profile, context)
        self._apply_lmnp_strategy(tax_result, profile, context)
        self._apply_girardin_strategy(tax_result, profile, context)
        self._apply_fcpi_fip_strategy(tax_result, profile, context)
        self._apply_deductions_strategy(tax_result, profile, context)
        self._apply_structure_strategy(tax_result, profile, context)

        # Sort recommendations by impact (descending)
        self.recommendations.sort(key=lambda r: r.impact_estimated, reverse=True)

        # Generate result
        return self._generate_result(context)

    def _apply_regime_strategy(
        self, tax_result: dict, profile: dict, context: dict
    ) -> None:
        """Apply regime optimization strategy."""
        recs = self.regime_strategy.analyze(tax_result, profile, context)
        self.recommendations.extend(recs)

    def _apply_per_strategy(
        self, tax_result: dict, profile: dict, context: dict
    ) -> None:
        """Apply PER optimization strategy."""
        recs = self.per_strategy.analyze(tax_result, profile, context)
        self.recommendations.extend(recs)

    def _apply_lmnp_strategy(
        self, tax_result: dict, profile: dict, context: dict
    ) -> None:
        """Apply LMNP optimization strategy."""
        recs = self.lmnp_strategy.analyze(tax_result, profile, context)
        self.recommendations.extend(recs)

    def _apply_girardin_strategy(
        self, tax_result: dict, profile: dict, context: dict
    ) -> None:
        """Apply Girardin optimization strategy."""
        recs = self.girardin_strategy.analyze(tax_result, profile, context)
        self.recommendations.extend(recs)

    def _apply_fcpi_fip_strategy(
        self, tax_result: dict, profile: dict, context: dict
    ) -> None:
        """Apply FCPI/FIP optimization strategy."""
        recs = self.fcpi_fip_strategy.analyze(tax_result, profile, context)
        self.recommendations.extend(recs)

    def _apply_deductions_strategy(
        self, tax_result: dict, profile: dict, context: dict
    ) -> None:
        """Apply simple deductions optimization strategy."""
        recs = self.deductions_strategy.analyze(tax_result, profile, context)
        self.recommendations.extend(recs)

    def _apply_structure_strategy(
        self, tax_result: dict, profile: dict, context: dict
    ) -> None:
        """Apply company structure optimization strategy."""
        recs = self.structure_strategy.analyze(tax_result, profile, context)
        self.recommendations.extend(recs)

    def _generate_result(self, context: dict) -> OptimizationResult:
        """Generate final optimization result with summary."""
        # Extract strategy identifiers from recommendations
        active_strategies = self._get_active_strategies()

        # Check for strategy interactions
        interaction_warnings = self.interaction_checker.get_all_warnings(
            active_strategies
        )
        interaction_recommendations = self.interaction_checker.get_all_recommendations(
            active_strategies
        )
        conflicts = self.interaction_checker.check_conflicts(active_strategies)
        synergies = self.interaction_checker.check_synergies(active_strategies)

        # Calculate combined impact modifier
        impact_modifier = self.interaction_checker.calculate_combined_impact_modifier(
            active_strategies
        )

        # Calculate total potential savings (adjusted by interaction modifier)
        raw_savings = sum(rec.impact_estimated for rec in self.recommendations)
        total_savings = raw_savings * impact_modifier

        # Count high-priority recommendations (impact > 1000€ or easy + low risk)
        high_priority = sum(
            1
            for rec in self.recommendations
            if rec.impact_estimated > 1000
            or (rec.complexity.value == "easy" and rec.risk.value == "low")
        )

        # Determine risk profile
        risk_tolerance = context.get("risk_tolerance", "conservative")
        risk_profile = self._map_risk_profile(risk_tolerance)

        # Generate executive summary
        summary = self._generate_summary(total_savings, high_priority)

        # Build metadata with interaction information
        metadata = {
            "total_recommendations": len(self.recommendations),
            "by_category": self._count_by_category(),
            "by_risk": self._count_by_risk(),
            "by_complexity": self._count_by_complexity(),
            "strategy_interactions": {
                "active_strategies": active_strategies,
                "conflicts": [
                    {
                        "strategies": [c[0], c[1]],
                        "description": c[2].description,
                        "warning": c[2].warning_message,
                    }
                    for c in conflicts
                ],
                "synergies": [
                    {
                        "strategies": [s[0], s[1]],
                        "description": s[2].description,
                        "recommendation": s[2].recommendation,
                    }
                    for s in synergies
                ],
                "impact_modifier": round(impact_modifier, 2),
                "raw_savings": round(raw_savings, 2),
                "adjusted_savings": round(total_savings, 2),
            },
            "interaction_warnings": interaction_warnings,
            "interaction_recommendations": interaction_recommendations,
            "disclaimer": (
                "Ces scénarios sont des illustrations basées sur votre "
                "situation fiscale déclarée. Ils ne constituent pas un conseil "
                "en investissement ni un conseil fiscal personnalisé. "
                "Pour toute décision engageante, consultez un expert-comptable, "
                "un avocat fiscaliste, ou un CIF agréé ORIAS. "
                "Version Beta - Outil à vocation éducative uniquement."
            ),
        }

        return OptimizationResult(
            recommendations=self.recommendations,
            summary=summary,
            risk_profile=risk_profile,
            potential_savings_total=total_savings,
            high_priority_count=high_priority,
            metadata=metadata,
        )

    def _map_risk_profile(self, risk_tolerance: str) -> OptimizationProfile:
        """Map user risk tolerance to optimization profile."""
        if risk_tolerance in ["low", "conservative"]:
            return OptimizationProfile.CONSERVATIVE
        elif risk_tolerance in ["high", "aggressive"]:
            return OptimizationProfile.AGGRESSIVE
        else:
            return OptimizationProfile.MODERATE

    def _generate_summary(self, total_savings: float, high_priority: int) -> str:
        """Generate executive summary."""
        if len(self.recommendations) == 0:
            return (
                "Aucun scénario d'optimisation identifié. "
                "Votre situation fiscale semble déjà optimisée."
            )

        # Round total savings for educational display
        rounded_savings = round(total_savings, -2)

        summary = (
            f"🎯 {len(self.recommendations)} scénario(s) "
            f"d'optimisation identifié(s)\n\n"
            f"💰 Économies potentielles estimées : environ {rounded_savings:,.0f} €\n"
            f"⭐ Scénarios prioritaires : {high_priority}\n\n"
        )

        # Add top 3 recommendations
        top_recs = self.recommendations[:3]
        summary += "**Top 3 scénarios à explorer :**\n"
        for i, rec in enumerate(top_recs, 1):
            rounded_impact = round(rec.impact_estimated, -2)
            summary += (
                f"{i}. {rec.title} "
                f"(environ +{rounded_impact:,.0f} €, "
                f"risque: {rec.risk.value}, "
                f"complexité: {rec.complexity.value})\n"
            )

        return summary

    def _count_by_category(self) -> dict[str, int]:
        """Count recommendations by category."""
        counts: dict[str, int] = {}
        for rec in self.recommendations:
            cat = rec.category.value
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    def _count_by_risk(self) -> dict[str, int]:
        """Count recommendations by risk level."""
        counts: dict[str, int] = {}
        for rec in self.recommendations:
            risk = rec.risk.value
            counts[risk] = counts.get(risk, 0) + 1
        return counts

    def _count_by_complexity(self) -> dict[str, int]:
        """Count recommendations by complexity."""
        counts: dict[str, int] = {}
        for rec in self.recommendations:
            complexity = rec.complexity.value
            counts[complexity] = counts.get(complexity, 0) + 1
        return counts

    def _get_active_strategies(self) -> list[str]:
        """Extract unique strategy identifiers from recommendations.

        Returns:
            List of strategy identifiers for interaction checking
        """
        strategies: set[str] = set()
        for rec in self.recommendations:
            category = rec.category.value
            strategy = self.CATEGORY_TO_STRATEGY.get(category)
            if strategy:
                strategies.add(strategy)
        return list(strategies)
