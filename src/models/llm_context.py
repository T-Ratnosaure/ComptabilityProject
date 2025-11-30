"""LLM context models for Phase 5 - Clean data for Claude.

These models provide a sanitized, validated context for LLM interactions,
excluding all technical fields, system paths, and sensitive data.
"""

from pydantic import BaseModel, Field

from src.models.comparison import ComparisonMicroReel
from src.models.fiscal_profile import FiscalProfile
from src.models.optimization import Recommendation


class TaxCalculationSummary(BaseModel):
    """Clean summary of tax calculation results for LLM.

    This model contains ONLY fiscal calculation results, no technical data.
    All monetary amounts are in euros, all rates are in decimal (0-1).
    """

    # Résultats principaux
    impot_brut: float = Field(
        ..., ge=0, description="Impôt sur le revenu brut en euros"
    )
    impot_net: float = Field(
        ..., ge=0, description="Impôt sur le revenu net (après réductions) en euros"
    )
    cotisations_sociales: float = Field(
        ..., ge=0, description="Total des cotisations URSSAF en euros"
    )
    charge_fiscale_totale: float = Field(
        ..., ge=0, description="Charge fiscale totale (IR + cotisations) en euros"
    )

    # Taux
    tmi: float = Field(
        ..., ge=0, le=1, description="Taux Marginal d'Imposition (0-1, ex: 0.30 = 30%)"
    )
    taux_effectif: float = Field(
        ..., ge=0, le=1, description="Taux effectif global (impôt/revenu, 0-1)"
    )

    # Détails du calcul
    revenu_imposable: float = Field(
        ..., ge=0, description="Revenu net imposable en euros"
    )
    quotient_familial: float = Field(
        ..., ge=0, description="Quotient familial (revenu/nb_parts) en euros"
    )
    reductions_fiscales: dict[str, float] = Field(
        default_factory=dict,
        description="Réductions fiscales appliquées (nom: montant en euros)",
    )

    # Détails PER (déduction retraite)
    per_plafond_detail: dict[str, float] | None = Field(
        default=None,
        description=(
            "Détail plafond PER: {applied: montant déductible, "
            "excess: montant excédant plafond, plafond_max: plafond calculé}"
        ),
    )

    # Détails tranches fiscales
    tranches_detail: list[dict[str, float]] | None = Field(
        default=None,
        description=(
            "Détail calcul par tranche: [{rate: taux, "
            "income_in_bracket: revenu dans tranche, tax_in_bracket: impôt tranche}]"
        ),
    )

    # Détails cotisations sociales
    cotisations_detail: dict[str, float] | None = Field(
        default=None,
        description=(
            "Détail cotisations URSSAF: {maladie, retraite, "
            "allocations, csg_crds, formation}"
        ),
    )

    # Comparaisons (optionnel)
    comparaison_micro_reel: ComparisonMicroReel | None = Field(
        default=None, description="Comparaison structurée micro vs réel si applicable"
    )

    # Avertissements
    warnings: list[str] = Field(
        default_factory=list, description="Alertes et avertissements fiscaux"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "impot_brut": 3500.0,
                "impot_net": 3500.0,
                "cotisations_sociales": 10900.0,
                "charge_fiscale_totale": 14400.0,
                "tmi": 0.30,
                "taux_effectif": 0.10,
                "revenu_imposable": 33000.0,
                "quotient_familial": 33000.0,
                "reductions_fiscales": {},
                "warnings": [
                    (
                        "Vous êtes proche du plafond micro-BNC (77700€)."
                        " Surveillez votre CA."
                    )
                ],
            }
        }
    }


class LLMContext(BaseModel):
    """
    Complete context for LLM Phase 5.

    This model contains ONLY fiscal data, no technical fields, no system paths.
    All data is validated, sanitized, and ready for Claude.

    EXCLUDED from this context:
    - Database IDs (id, profile_id, calculation_id)
    - Timestamps (created_at, updated_at, processed_at)
    - File system paths (file_path)
    - Raw extracted text (raw_text - too large, use extracted_fields instead)
    - Error messages (error_message - internal debugging)
    - Status flags (status - technical)

    INCLUDED in this context:
    - Fiscal profile with all relevant data
    - Tax calculation summary with key results
    - Optimization recommendations
    - Sanitized document extracts (fields only, no paths)
    - Metadata (year, date, version)
    """

    # Profil fiscal unifié
    profil: FiscalProfile = Field(
        ..., description="Profil fiscal complet de l'utilisateur"
    )

    # Calcul fiscal
    calcul_fiscal: TaxCalculationSummary = Field(
        ..., description="Résumé du calcul d'impôt et cotisations"
    )

    # Optimisations
    recommendations: list[Recommendation] = Field(
        default_factory=list,
        description="Liste des recommandations d'optimisation fiscale",
    )
    total_economies_potentielles: float = Field(
        default=0.0,
        ge=0,
        description="Total des économies potentielles identifiées en euros",
    )

    # Documents (extraits sanitizés uniquement)
    documents_extraits: dict[str, dict] = Field(
        default_factory=dict,
        description="Champs extraits des documents (SANS chemins, SANS raw_text)",
    )

    # Métadonnées
    metadata: dict = Field(
        default_factory=dict,
        description="Métadonnées non sensibles (année, date calcul, version)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "profil": {
                    "annee_fiscale": 2024,
                    "situation_familiale": "celibataire",
                    "nombre_parts": 1.0,
                    "regime_fiscal": "micro_bnc",
                    "chiffre_affaires": 50000.0,
                },
                "calcul_fiscal": {
                    "impot_net": 3500.0,
                    "cotisations_sociales": 10900.0,
                    "charge_fiscale_totale": 14400.0,
                    "tmi": 0.30,
                    "taux_effectif": 0.10,
                },
                "recommendations": [
                    {
                        "id": "per_optimal",
                        "title": "PER - Versement optimal",
                        "impact_estimated": 2772.0,
                    }
                ],
                "total_economies_potentielles": 2772.0,
                "documents_extraits": {
                    "avis_imposition_2024": {
                        "type": "avis_imposition",
                        "year": 2024,
                        "fields": {"revenu_fiscal_reference": 45000.0},
                    }
                },
                "metadata": {
                    "version": "1.0",
                    "calculation_date": "2024-11-29T10:30:00",
                },
            }
        }
    }
