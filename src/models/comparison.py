"""Pydantic models for tax regime comparisons."""

from pydantic import BaseModel, Field


class ComparisonMicroReel(BaseModel):
    """Structured comparison between micro and réel tax regimes.

    This model provides a validated, complete comparison to help users
    understand the financial impact of switching tax regimes.
    """

    regime_actuel: str = Field(
        ..., description="Current tax regime (e.g., micro_bnc, micro_bic)"
    )
    regime_compare: str = Field(
        ..., description="Compared tax regime (e.g., reel_bnc, reel_bic)"
    )

    # Tax comparison
    impot_actuel: float = Field(
        ..., ge=0, description="Income tax under current regime in euros"
    )
    impot_compare: float = Field(
        ..., ge=0, description="Income tax under compared regime in euros"
    )
    delta_impot: float = Field(
        ..., description="Tax difference (compare - current) in euros"
    )

    # Social contributions comparison
    cotisations_actuelles: float = Field(
        ..., ge=0, description="Social contributions under current regime in euros"
    )
    cotisations_comparees: float = Field(
        ..., ge=0, description="Social contributions under compared regime in euros"
    )
    delta_cotisations: float = Field(
        ..., description="Social contributions difference in euros"
    )

    # Total comparison
    charge_totale_actuelle: float = Field(
        ..., ge=0, description="Total fiscal burden (IR + social) current regime"
    )
    charge_totale_comparee: float = Field(
        ..., ge=0, description="Total fiscal burden (IR + social) compared regime"
    )
    delta_total: float = Field(
        ...,
        description=(
            "Total difference in euros (negative = economy with compared regime)"
        ),
    )

    # Recommendation
    economie_potentielle: float = Field(
        ..., ge=0, description="Potential savings in absolute value in euros"
    )
    pourcentage_economie: float = Field(
        ..., ge=0, le=100, description="Potential savings as percentage"
    )
    recommendation: str = Field(
        ...,
        description="Clear recommendation: 'Rester en micro' or 'Passer au réel'",
    )
    justification: str = Field(
        ..., description="Detailed justification for the recommendation"
    )

    # Context
    chiffre_affaires: float = Field(
        ..., ge=0, description="Revenue used for comparison in euros"
    )
    charges_reelles: float = Field(
        default=0.0, ge=0, description="Real expenses (for réel regime) in euros"
    )
    taux_abattement_micro: float = Field(
        default=0.34,
        ge=0,
        le=1,
        description="Abattement rate for micro regime (decimal)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "regime_actuel": "micro_bnc",
                "regime_compare": "reel_bnc",
                "impot_actuel": 3500.0,
                "impot_compare": 2000.0,
                "delta_impot": -1500.0,
                "cotisations_actuelles": 10900.0,
                "cotisations_comparees": 10900.0,
                "delta_cotisations": 0.0,
                "charge_totale_actuelle": 14400.0,
                "charge_totale_comparee": 12900.0,
                "delta_total": -1500.0,
                "economie_potentielle": 1500.0,
                "pourcentage_economie": 10.4,
                "recommendation": "Passer au réel",
                "justification": (
                    "Économie de 1500€ (10.4%) en passant au régime réel. "
                    "Vos charges réelles (10000€) dépassent l'abattement "
                    "micro (34% = 17000€ sur CA de 50000€)."
                ),
                "chiffre_affaires": 50000.0,
                "charges_reelles": 10000.0,
                "taux_abattement_micro": 0.34,
            }
        }
    }
