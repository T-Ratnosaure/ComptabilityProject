"""Strategy interdependency model for optimization recommendations.

This module defines how different tax optimization strategies interact,
including conflicts, synergies, and mutual dependencies.
"""

from enum import Enum

from pydantic import BaseModel, Field


class InteractionType(str, Enum):
    """Type of interaction between strategies."""

    CONFLICT = "conflict"  # Strategies are mutually exclusive or reduce each other
    SYNERGY = "synergy"  # Strategies work better together
    DEPENDENCY = "dependency"  # One strategy requires another
    NEUTRAL = "neutral"  # No significant interaction


class StrategyInteraction(BaseModel):
    """Defines an interaction between two strategies."""

    strategy_a: str = Field(description="First strategy identifier")
    strategy_b: str = Field(description="Second strategy identifier")
    interaction_type: InteractionType = Field(description="Type of interaction")
    description: str = Field(description="Explanation of the interaction")
    impact_modifier: float = Field(
        default=1.0,
        ge=0.0,
        le=2.0,
        description="Multiplier for combined impact (0.5 = halved, 1.5 = boosted)",
    )
    warning_message: str | None = Field(
        default=None, description="Warning to display when both are recommended"
    )
    recommendation: str | None = Field(
        default=None, description="Recommendation when both strategies apply"
    )


# Define all strategy interdependencies
STRATEGY_INTERACTIONS: list[StrategyInteraction] = [
    # PER vs LMNP - Synergy (both reduce taxable income)
    StrategyInteraction(
        strategy_a="per",
        strategy_b="lmnp",
        interaction_type=InteractionType.SYNERGY,
        description=(
            "PER et LMNP se complètent: le PER réduit le revenu imposable, "
            "le LMNP génère des revenus défiscalisés."
        ),
        impact_modifier=1.1,
        recommendation=(
            "Combiner PER (épargne retraite) et LMNP (revenus locatifs) "
            "permet une optimisation sur deux fronts."
        ),
    ),
    # PER vs Girardin - Potential conflict (both use fiscal capacity)
    StrategyInteraction(
        strategy_a="per",
        strategy_b="girardin",
        interaction_type=InteractionType.CONFLICT,
        description=(
            "Le PER réduit le revenu imposable, donc réduit l'impôt dû, "
            "ce qui peut limiter l'intérêt du Girardin."
        ),
        impact_modifier=0.85,
        warning_message=(
            "Attention: en réduisant votre impôt via le PER, "
            "vous réduisez la base utilisable pour le Girardin."
        ),
        recommendation=(
            "Calculez l'ordre optimal: généralement Girardin d'abord "
            "(réduction directe), puis PER (épargne long terme)."
        ),
    ),
    # PER vs FCPI/FIP - Conflict (plafond des niches fiscales)
    StrategyInteraction(
        strategy_a="per",
        strategy_b="fcpi_fip",
        interaction_type=InteractionType.NEUTRAL,
        description=(
            "Le PER ne compte pas dans le plafonnement des niches fiscales, "
            "mais mobilise la même épargne."
        ),
        impact_modifier=1.0,
        recommendation=(
            "Le PER et FCPI/FIP sont compatibles mais concurrencent "
            "la même capacité d'épargne."
        ),
    ),
    # Girardin vs FCPI/FIP - Conflict (plafond des niches fiscales)
    StrategyInteraction(
        strategy_a="girardin",
        strategy_b="fcpi_fip",
        interaction_type=InteractionType.CONFLICT,
        description=(
            "Girardin et FCPI/FIP partagent le plafond de 18 000 EUR "
            "des niches fiscales."
        ),
        impact_modifier=0.7,
        warning_message=(
            "Girardin et FCPI/FIP sont soumis au plafonnement global "
            "(10 000 EUR + 8 000 EUR Girardin/SOFICA)."
        ),
        recommendation=(
            "Priorisez le Girardin (rendement >100%) si vous avez "
            "suffisamment d'impôt. FCPI/FIP en complément."
        ),
    ),
    # Regime change vs PER - Dependency (TMI impact)
    StrategyInteraction(
        strategy_a="regime_change",
        strategy_b="per",
        interaction_type=InteractionType.DEPENDENCY,
        description=(
            "Le passage au réel peut modifier votre TMI, impactant l'intérêt du PER."
        ),
        impact_modifier=0.95,
        warning_message=(
            "Un changement de régime peut modifier votre TMI "
            "et donc l'économie réelle du PER."
        ),
        recommendation=(
            "Recalculez l'intérêt du PER après simulation du changement de régime."
        ),
    ),
    # Regime change vs LMNP - Synergy (expertise comptable mutualisée)
    StrategyInteraction(
        strategy_a="regime_change",
        strategy_b="lmnp",
        interaction_type=InteractionType.SYNERGY,
        description=(
            "Le passage au réel et le LMNP au réel "
            "utilisent une comptabilité similaire."
        ),
        impact_modifier=1.15,
        recommendation=(
            "Si vous passez au réel pour votre activité, le LMNP réel "
            "devient moins complexe (expert-comptable commun)."
        ),
    ),
    # LMNP vs Girardin - Synergy (diversification)
    StrategyInteraction(
        strategy_a="lmnp",
        strategy_b="girardin",
        interaction_type=InteractionType.SYNERGY,
        description=(
            "LMNP (patrimoine réel) et Girardin (défiscalisation pure) "
            "sont complémentaires."
        ),
        impact_modifier=1.05,
        recommendation=(
            "Le LMNP construit du patrimoine, le Girardin optimise l'impôt. "
            "Bonne diversification."
        ),
    ),
    # Deductions vs Girardin - Conflict (reduce tax base)
    StrategyInteraction(
        strategy_a="deductions",
        strategy_b="girardin",
        interaction_type=InteractionType.CONFLICT,
        description=(
            "Les déductions réduisent l'impôt, limitant l'intérêt du Girardin."
        ),
        impact_modifier=0.9,
        warning_message=(
            "Les déductions (dons, services à la personne) réduisent "
            "votre impôt et donc le potentiel Girardin."
        ),
    ),
    # Structure change vs all others - Major dependency
    StrategyInteraction(
        strategy_a="structure_change",
        strategy_b="per",
        interaction_type=InteractionType.DEPENDENCY,
        description=(
            "Le passage en société modifie complètement "
            "le calcul IR/IS et l'intérêt du PER."
        ),
        impact_modifier=0.5,
        warning_message=(
            "Un passage en société change fondamentalement votre situation fiscale."
        ),
        recommendation=(
            "Évaluez d'abord le passage en société avant d'optimiser en IR."
        ),
    ),
    StrategyInteraction(
        strategy_a="structure_change",
        strategy_b="lmnp",
        interaction_type=InteractionType.NEUTRAL,
        description=(
            "Le LMNP reste possible en société mais avec des modalités différentes."
        ),
        impact_modifier=1.0,
    ),
    StrategyInteraction(
        strategy_a="structure_change",
        strategy_b="girardin",
        interaction_type=InteractionType.DEPENDENCY,
        description="En société à l'IS, le Girardin personnel n'a plus d'intérêt.",
        impact_modifier=0.3,
        warning_message=(
            "Le Girardin vise l'IR personnel. En société à l'IS, "
            "cette stratégie ne s'applique plus."
        ),
    ),
]


class StrategyInteractionChecker:
    """Checks and reports on strategy interactions."""

    def __init__(self) -> None:
        """Initialize with predefined interactions."""
        self.interactions = {
            (i.strategy_a, i.strategy_b): i for i in STRATEGY_INTERACTIONS
        }
        # Also index reverse direction
        for i in STRATEGY_INTERACTIONS:
            self.interactions[(i.strategy_b, i.strategy_a)] = i

    def get_interaction(
        self, strategy_a: str, strategy_b: str
    ) -> StrategyInteraction | None:
        """Get the interaction between two strategies.

        Args:
            strategy_a: First strategy identifier
            strategy_b: Second strategy identifier

        Returns:
            StrategyInteraction or None if no defined interaction
        """
        return self.interactions.get((strategy_a, strategy_b))

    def check_conflicts(
        self, strategies: list[str]
    ) -> list[tuple[str, str, StrategyInteraction]]:
        """Check for conflicts among a list of strategies.

        Args:
            strategies: List of strategy identifiers

        Returns:
            List of (strategy_a, strategy_b, interaction) tuples for conflicts
        """
        conflicts = []
        for i, strat_a in enumerate(strategies):
            for strat_b in strategies[i + 1 :]:
                interaction = self.get_interaction(strat_a, strat_b)
                is_conflict = (
                    interaction
                    and interaction.interaction_type == InteractionType.CONFLICT
                )
                if is_conflict:
                    conflicts.append((strat_a, strat_b, interaction))
        return conflicts

    def check_synergies(
        self, strategies: list[str]
    ) -> list[tuple[str, str, StrategyInteraction]]:
        """Check for synergies among a list of strategies.

        Args:
            strategies: List of strategy identifiers

        Returns:
            List of (strategy_a, strategy_b, interaction) tuples for synergies
        """
        synergies = []
        for i, strat_a in enumerate(strategies):
            for strat_b in strategies[i + 1 :]:
                interaction = self.get_interaction(strat_a, strat_b)
                is_synergy = (
                    interaction
                    and interaction.interaction_type == InteractionType.SYNERGY
                )
                if is_synergy:
                    synergies.append((strat_a, strat_b, interaction))
        return synergies

    def get_all_warnings(self, strategies: list[str]) -> list[str]:
        """Get all warning messages for a set of strategies.

        Args:
            strategies: List of strategy identifiers

        Returns:
            List of warning messages
        """
        warnings = []
        seen = set()
        for i, strat_a in enumerate(strategies):
            for strat_b in strategies[i + 1 :]:
                key = tuple(sorted([strat_a, strat_b]))
                if key in seen:
                    continue
                seen.add(key)

                interaction = self.get_interaction(strat_a, strat_b)
                if interaction and interaction.warning_message:
                    warnings.append(interaction.warning_message)
        return warnings

    def get_all_recommendations(self, strategies: list[str]) -> list[str]:
        """Get all recommendations for a set of strategies.

        Args:
            strategies: List of strategy identifiers

        Returns:
            List of recommendations
        """
        recommendations = []
        seen = set()
        for i, strat_a in enumerate(strategies):
            for strat_b in strategies[i + 1 :]:
                key = tuple(sorted([strat_a, strat_b]))
                if key in seen:
                    continue
                seen.add(key)

                interaction = self.get_interaction(strat_a, strat_b)
                if interaction and interaction.recommendation:
                    recommendations.append(interaction.recommendation)
        return recommendations

    def calculate_combined_impact_modifier(self, strategies: list[str]) -> float:
        """Calculate the combined impact modifier for a set of strategies.

        Args:
            strategies: List of strategy identifiers

        Returns:
            Combined impact modifier (product of all interaction modifiers)
        """
        modifier = 1.0
        seen = set()
        for i, strat_a in enumerate(strategies):
            for strat_b in strategies[i + 1 :]:
                key = tuple(sorted([strat_a, strat_b]))
                if key in seen:
                    continue
                seen.add(key)

                interaction = self.get_interaction(strat_a, strat_b)
                if interaction:
                    modifier *= interaction.impact_modifier
        return modifier
