"""Pydantic models for validated document extraction.

These models provide validation for data extracted from tax documents,
ensuring type safety and data integrity before processing.
"""

from pydantic import BaseModel, Field


class AvisImpositionExtracted(BaseModel):
    """Validated extraction from Avis d'Imposition (tax assessment notice)."""

    revenu_fiscal_reference: float | None = Field(
        default=None, ge=0, description="Revenu Fiscal de Référence en euros"
    )
    revenu_imposable: float | None = Field(
        default=None, ge=0, description="Revenu net imposable en euros"
    )
    impot_revenu: float | None = Field(
        default=None, ge=0, description="Impôt sur le revenu net en euros"
    )
    nombre_parts: float | None = Field(
        default=None, gt=0, le=10, description="Nombre de parts fiscales"
    )
    taux_prelevement: float | None = Field(
        default=None, ge=0, le=100, description="Taux de prélèvement à la source (%)"
    )
    situation_familiale: str | None = Field(
        default=None, description="Situation familiale"
    )
    year: int | None = Field(
        default=None, ge=2000, le=2100, description="Année fiscale"
    )

    model_config = {"extra": "forbid"}


class URSSAFExtracted(BaseModel):
    """Validated extraction from URSSAF social contribution documents."""

    chiffre_affaires: float | None = Field(
        default=None, ge=0, description="Chiffre d'affaires déclaré en euros"
    )
    cotisations_sociales: float | None = Field(
        default=None, ge=0, description="Total des cotisations sociales en euros"
    )
    cotisation_maladie: float | None = Field(
        default=None, ge=0, description="Cotisation maladie en euros"
    )
    cotisation_retraite: float | None = Field(
        default=None, ge=0, description="Cotisation retraite en euros"
    )
    cotisation_allocations: float | None = Field(
        default=None, ge=0, description="Cotisation allocations familiales en euros"
    )
    csg_crds: float | None = Field(default=None, ge=0, description="CSG-CRDS en euros")
    formation_professionnelle: float | None = Field(
        default=None, ge=0, description="Formation professionnelle en euros"
    )
    periode: str | None = Field(default=None, description="Période (ex: 2024-01)")
    year: int | None = Field(
        default=None, ge=2000, le=2100, description="Année fiscale"
    )

    model_config = {"extra": "forbid"}


class BNCBICExtracted(BaseModel):
    """Validated extraction from BNC/BIC declaration documents."""

    recettes: float | None = Field(
        default=None, ge=0, description="Recettes brutes en euros"
    )
    charges: float | None = Field(
        default=None, ge=0, description="Charges déductibles en euros"
    )
    benefice: float | None = Field(
        default=None, description="Bénéfice net en euros (peut être négatif)"
    )
    regime: str | None = Field(
        default=None,
        pattern="^(micro_bnc|micro_bic|reel_bnc|reel_bic)$",
        description="Régime fiscal",
    )
    amortissements: float | None = Field(
        default=None, ge=0, description="Amortissements en euros"
    )
    loyer: float | None = Field(default=None, ge=0, description="Loyer en euros")
    honoraires: float | None = Field(
        default=None, ge=0, description="Honoraires en euros"
    )
    autres_charges: float | None = Field(
        default=None, ge=0, description="Autres charges en euros"
    )
    year: int | None = Field(
        default=None, ge=2000, le=2100, description="Année fiscale"
    )

    model_config = {"extra": "forbid"}


class Declaration2042Extracted(BaseModel):
    """Validated extraction from Declaration 2042 (income tax return)."""

    salaires_declarant1: float | None = Field(
        default=None, ge=0, description="Salaires déclarant 1 (case 1AJ) en euros"
    )
    salaires_declarant2: float | None = Field(
        default=None, ge=0, description="Salaires déclarant 2 (case 1BJ) en euros"
    )
    pensions_declarant1: float | None = Field(
        default=None, ge=0, description="Pensions déclarant 1 (case 1AS) en euros"
    )
    pensions_declarant2: float | None = Field(
        default=None, ge=0, description="Pensions déclarant 2 (case 1BS) en euros"
    )
    revenus_fonciers: float | None = Field(
        default=None, ge=0, description="Revenus fonciers (case 4BA) en euros"
    )
    revenus_capitaux: float | None = Field(
        default=None, ge=0, description="Revenus de capitaux (case 2TR) en euros"
    )
    plus_values: float | None = Field(
        default=None, ge=0, description="Plus-values (case 3VG) en euros"
    )
    charges_deductibles: float | None = Field(
        default=None, ge=0, description="Charges déductibles (case 6DD) en euros"
    )
    year: int | None = Field(
        default=None, ge=2000, le=2100, description="Année fiscale"
    )

    model_config = {"extra": "forbid"}
