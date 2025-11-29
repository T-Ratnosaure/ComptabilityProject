"""Unified fiscal profile model for LLM context.

This model consolidates data from multiple sources (documents, profile, calculations)
into a clean, complete representation optimized for LLM Phase 5.
"""

from pydantic import BaseModel, Field


class FiscalProfile(BaseModel):
    """
    Unified fiscal profile combining data from multiple sources.

    This model is optimized for LLM context:
    - Clean: No technical fields (id, timestamps, file_path)
    - Complete: All fiscal data needed for tax analysis
    - Validated: Pydantic ensures type safety and constraints
    - Documented: Every field has a clear description

    All monetary amounts are in euros.
    """

    # Identification
    annee_fiscale: int = Field(..., ge=2000, le=2100, description="Année fiscale")

    # Situation personnelle
    situation_familiale: str = Field(
        ...,
        description="Situation familiale: celibataire, marie, pacse, divorce, veuf",
    )
    nombre_parts: float = Field(
        ..., gt=0, le=10, description="Nombre de parts fiscales"
    )
    enfants_a_charge: int = Field(
        default=0, ge=0, le=10, description="Nombre d'enfants à charge"
    )
    enfants_moins_6_ans: int = Field(
        default=0, ge=0, le=10, description="Nombre d'enfants de moins de 6 ans"
    )

    # Activité professionnelle
    regime_fiscal: str = Field(
        ...,
        description=(
            "Régime fiscal: micro_bnc, micro_bic, reel_bnc, reel_bic, eurl, sasu"
        ),
    )
    type_activite: str = Field(
        ..., description="Type d'activité: BNC (libéral), BIC (commercial)"
    )
    chiffre_affaires: float = Field(
        ..., ge=0, description="Chiffre d'affaires annuel en euros"
    )
    charges_deductibles: float = Field(
        default=0.0, ge=0, description="Charges réelles déductibles en euros"
    )
    benefice_net: float | None = Field(
        default=None, description="Bénéfice net en euros (après charges)"
    )

    # Cotisations et charges sociales
    cotisations_sociales: float = Field(
        ..., ge=0, description="Total cotisations URSSAF en euros"
    )

    # Autres revenus
    salaires: float = Field(
        default=0.0,
        ge=0,
        description="Salaires (hors activité professionnelle) en euros",
    )
    revenus_fonciers: float = Field(
        default=0.0, ge=0, description="Revenus fonciers (location) en euros"
    )
    revenus_capitaux: float = Field(
        default=0.0, ge=0, description="Revenus de capitaux mobiliers en euros"
    )

    # Déductions existantes
    per_contributions: float = Field(
        default=0.0, ge=0, description="Versements PER (Plan Épargne Retraite) en euros"
    )
    dons_declares: float = Field(
        default=0.0, ge=0, description="Dons aux associations déclarés en euros"
    )
    services_personne: float = Field(
        default=0.0, ge=0, description="Services à la personne déclarés en euros"
    )
    frais_garde: float = Field(
        default=0.0, ge=0, description="Frais de garde d'enfants déclarés en euros"
    )
    pension_alimentaire: float = Field(
        default=0.0, ge=0, description="Pension alimentaire versée en euros"
    )

    # Références fiscales (si disponibles depuis documents)
    revenu_fiscal_reference: float | None = Field(
        default=None,
        ge=0,
        description="RFR (Revenu Fiscal de Référence) de l'année précédente en euros",
    )
    impot_annee_precedente: float | None = Field(
        default=None, ge=0, description="Impôt payé l'année précédente en euros"
    )

    # Métadonnées pour optimisation (non fiscales, utiles pour le LLM)
    revenus_stables: bool = Field(
        default=False, description="Revenus stables sur les 3 dernières années"
    )
    strategie_patrimoniale: bool = Field(
        default=False, description="Dispose d'une stratégie patrimoniale"
    )
    capacite_investissement: float = Field(
        default=0.0,
        ge=0,
        description="Capacité d'investissement disponible en euros",
    )
    tolerance_risque: str = Field(
        default="moderate",
        pattern="^(conservative|moderate|aggressive)$",
        description="Tolérance au risque: conservative, moderate, aggressive",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "annee_fiscale": 2024,
                "situation_familiale": "celibataire",
                "nombre_parts": 1.0,
                "enfants_a_charge": 0,
                "enfants_moins_6_ans": 0,
                "regime_fiscal": "micro_bnc",
                "type_activite": "BNC",
                "chiffre_affaires": 50000.0,
                "charges_deductibles": 0.0,
                "benefice_net": 33000.0,
                "cotisations_sociales": 10900.0,
                "salaires": 0.0,
                "revenus_fonciers": 0.0,
                "revenus_capitaux": 0.0,
                "per_contributions": 0.0,
                "dons_declares": 0.0,
                "services_personne": 0.0,
                "frais_garde": 0.0,
                "pension_alimentaire": 0.0,
                "revenu_fiscal_reference": 45000.0,
                "impot_annee_precedente": 3200.0,
                "revenus_stables": False,
                "strategie_patrimoniale": False,
                "capacite_investissement": 0.0,
                "tolerance_risque": "moderate",
            }
        }
    }
