# 🔍 Audit Complet des Modèles Pydantic - Phase 5 LLM Readiness

**Date**: 2025-11-29
**Branch**: `review/code-improvements`
**Objectif**: Garantir que le LLM recevra un contexte propre, complet et sans bruit

---

## 📋 Table des Matières

1. [Inventaire Complet des Modèles](#1-inventaire-complet-des-modèles)
2. [Problèmes Critiques Détectés](#2-problèmes-critiques-détectés)
3. [Analyse par Critère](#3-analyse-par-critère)
4. [Chaîne de Données Complète](#4-chaîne-de-données-complète)
5. [Plan de Correction](#5-plan-de-correction)
6. [Proposition LLMContextModel](#6-proposition-llmcontextmodel)

---

## 1. Inventaire Complet des Modèles

### 1.1 Modèles de Domaine (`src/models/`)

| Fichier | Modèles Pydantic | Utilisation | Phase 5 Ready? |
|---------|------------------|-------------|----------------|
| `freelance_profile.py` | `FreelanceProfileBase`, `FreelanceProfileCreate`, `FreelanceProfileUpdate`, `FreelanceProfile` | Phase 1 - Profil utilisateur | ⚠️ PARTIEL |
| `tax_document.py` | `TaxDocumentBase`, `TaxDocumentCreate`, `TaxDocumentUpdate`, `TaxDocument` | Phase 2 - Documents | ⚠️ PARTIEL |
| `tax_calculation.py` | `TaxBracket`, `TaxCalculationBase`, `TaxCalculationCreate`, `TaxCalculation` | Phase 3 - Calculs | ⚠️ PARTIEL |
| `recommendation.py` | `RecommendationBase`, `RecommendationCreate`, `Recommendation` | Phase 1 - Recommandations (OBSOLÈTE) | ❌ NON |
| `optimization.py` | `Recommendation`, `OptimizationResult` | Phase 4 - Optimisations (ACTUEL) | ✅ OUI |

### 1.2 Modèles API (`src/api/routes/`)

| Fichier | Modèles Pydantic | Utilisation | Phase 5 Ready? |
|---------|------------------|-------------|----------------|
| `tax.py` | `TaxRegime`, `PersonData`, `IncomeData`, `DeductionsData`, `SocialData`, `TaxCalculationRequest` | Phase 3 - API Calcul Tax | ✅ OUI |
| `optimization.py` | `ProfileInput`, `OptimizationContext`, `OptimizationRequest`, `QuickSimulationInput`, `QuickSimulationResult` | Phase 4 - API Optimisation | ✅ OUI |

### 1.3 Parsers d'Extraction (`src/extractors/field_parsers/`)

| Fichier | Type Retour | Validation Pydantic? | Phase 5 Ready? |
|---------|-------------|----------------------|----------------|
| `avis_imposition.py` | `dict[str, str \| float \| int]` | ❌ NON | ❌ NON |
| `urssaf.py` | `dict[str, str \| float \| int]` | ❌ NON | ❌ NON |
| `bnc_bic.py` | `dict[str, str \| float \| int]` | ❌ NON | ❌ NON |
| `declaration_2042.py` | `dict[str, str \| float \| int]` | ❌ NON | ❌ NON |

### 1.4 Enums

| Enum | Localisation | Utilisé? | Cohérent? |
|------|--------------|----------|-----------|
| `FreelanceStatus` | `models/freelance_profile.py` | ✅ OUI | ⚠️ PARTIEL |
| `FamilySituation` | `models/freelance_profile.py` | ✅ OUI | ✅ OUI |
| `DocumentType` | `models/tax_document.py` | ✅ OUI | ✅ OUI |
| `DocumentStatus` | `models/tax_document.py` | ✅ OUI | ✅ OUI |
| `RecommendationType` | `models/recommendation.py` | ❌ NON (obsolète) | ❌ NON |
| `RiskLevel` | `models/recommendation.py` ET `models/optimization.py` | 🔴 **DUPLICATION** | ❌ NON |
| `TaxRegime` | `api/routes/tax.py` | ✅ OUI | ⚠️ PARTIEL |
| `ComplexityLevel` | `models/optimization.py` | ✅ OUI | ✅ OUI |
| `RecommendationCategory` | `models/optimization.py` | ✅ OUI | ✅ OUI |
| `OptimizationProfile` | `models/optimization.py` | ✅ OUI | ✅ OUI |

---

## 2. Problèmes Critiques Détectés

### 🔴 CRITIQUES (Bloquant Phase 5)

#### 2.1 Duplication de Modèles `Recommendation`

**Fichiers**:
- `src/models/recommendation.py` (Phase 1 - OBSOLÈTE)
- `src/models/optimization.py` (Phase 4 - ACTUEL)

**Problème**:
Deux modèles avec le même nom `Recommendation` mais des structures **complètement différentes**.

**Impact Phase 5**:
- ❌ Confusion pour le LLM sur quel format utiliser
- ❌ Risque d'incohérence dans le contexte envoyé
- ❌ Impossibilité de merger les données des deux modèles

**Exemple**:
```python
# ANCIEN (recommendation.py) - OBSOLÈTE
class Recommendation(BaseModel):
    id: int
    calculation_id: int
    type: RecommendationType  # Enum différent
    title: str
    description: str
    estimated_tax_savings: float
    required_investment: float
    roi_percentage: float | None
    risk_level: RiskLevel
    confidence_score: float
    action_steps: list[str]
    deadlines: dict[str, datetime] | None  # datetime objects
    required_documents: list[str]
    eligibility_criteria: dict[str, Any]
    warnings: list[str]
    created_at: datetime

# NOUVEAU (optimization.py) - ACTUEL
class Recommendation(BaseModel):
    id: str  # 🔴 Différent: str vs int
    title: str
    description: str
    impact_estimated: float  # 🔴 Différent: nom du champ
    risk: RiskLevel
    complexity: ComplexityLevel  # 🔴 Nouveau champ
    confidence: float  # 🔴 Différent: pas de "score"
    category: RecommendationCategory  # 🔴 Nouveau type
    sources: list[str]  # 🔴 Nouveau
    action_steps: list[str]
    required_investment: float
    eligibility_criteria: list[str]  # 🔴 Différent: list vs dict
    warnings: list[str]
    deadline: str | None  # 🔴 Différent: str vs datetime
    roi_years: float | None  # 🔴 Nouveau
```

**Solution**:
- ✅ Supprimer `models/recommendation.py` (obsolète)
- ✅ Migrer toutes les références vers `models/optimization.py`

---

#### 2.2 Duplication Enum `RiskLevel`

**Problème**:
```python
# Dans models/recommendation.py
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Dans models/optimization.py (identique)
class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

**Impact Phase 5**:
- ❌ Import ambigu
- ❌ Duplication inutile

**Solution**:
- ✅ Garder uniquement dans `models/optimization.py`
- ✅ Supprimer de `models/recommendation.py`

---

#### 2.3 Parsers Retournent `dict` Sans Validation Pydantic

**Fichiers**:
- `extractors/field_parsers/avis_imposition.py`
- `extractors/field_parsers/urssaf.py`
- `extractors/field_parsers/bnc_bic.py`
- `extractors/field_parsers/declaration_2042.py`

**Problème**:
```python
async def parse(self, text: str) -> dict[str, str | float | int]:
    """Parse fields from document text."""
    fields: dict[str, str | float | int] = {}
    fields["revenu_fiscal_reference"] = rfr  # Aucune validation
    return fields
```

**Impact Phase 5**:
- ❌ Pas de garantie de type
- ❌ Champs manquants non détectés
- ❌ Valeurs invalides possibles (négatifs, None, etc.)
- ❌ Difficile de générer un contexte LLM propre

**Solution**:
Créer des modèles Pydantic pour chaque type de document:
```python
class AvisImpositionExtracted(BaseModel):
    """Validated extraction from Avis d'Imposition."""
    revenu_fiscal_reference: float | None = Field(None, ge=0)
    revenu_imposable: float | None = Field(None, ge=0)
    impot_revenu: float | None = Field(None, ge=0)
    nombre_parts: float | None = Field(None, gt=0)
    taux_prelevement: float | None = Field(None, ge=0, le=100)
    situation_familiale: str | None = None
    year: int | None = Field(None, ge=2000, le=2100)
```

---

#### 2.4 Incohérence des Noms de Champs

**Problème**: Les mêmes concepts ont des noms différents selon les modèles.

| Concept | `FreelanceProfile` | `IncomeData` (API) | `Parsers` | Recommandation |
|---------|-------------------|-------------------|-----------|----------------|
| Revenu annuel | `annual_revenue` | `professional_gross` | `chiffre_affaires` / `recettes` | 🔴 Incohérent |
| Charges | `annual_expenses` | `deductible_expenses` | `charges` | 🔴 Incohérent |
| Cotisations sociales | `social_contributions` | - (dans `SocialData`) | `cotisations_sociales` | ⚠️ Partiel |
| Autres revenus | `other_income` | `salary` + `rental_income` + `capital_income` | - | 🔴 Incohérent |

**Impact Phase 5**:
- ❌ Le LLM ne sait pas que `annual_revenue` = `professional_gross` = `chiffre_affaires`
- ❌ Nécessite mapping manuel complexe
- ❌ Risque de perte de données

**Solution**:
Standardiser les noms sur **la terminologie française fiscale**:
- `chiffre_affaires` (CA)
- `charges_deductibles`
- `cotisations_sociales`
- `revenus_autres` (avec breakdown: `salaires`, `revenus_fonciers`, `revenus_capitaux`)

---

### 🟠 IMPORTANTS (Qualité Phase 5)

#### 2.5 Utilisation de `float` au lieu de `Decimal`

**Problème**:
Tous les montants monétaires utilisent `float`, ce qui pose des problèmes de précision.

```python
# Exemple actuel
annual_revenue: float = Field(..., ge=0)  # ❌ Perte de précision

# Recommandation
from decimal import Decimal
annual_revenue: Decimal = Field(..., ge=0, decimal_places=2)  # ✅ Précis
```

**Impact Phase 5**:
- ⚠️ Erreurs d'arrondi dans le contexte LLM
- ⚠️ Incohérence entre calculs

**Solution**:
- Migrer progressivement vers `Decimal` pour les montants
- Garder `float` pour les ratios/pourcentages

---

#### 2.6 Valeurs par Défaut Dangereuses

**Problème**: Certains champs ont des valeurs par défaut `0.0` au lieu de `None`.

```python
# DANGEREUX
annual_expenses: float = Field(default=0.0, ge=0)  # ❌ 0 != "non renseigné"
other_income: float = Field(default=0.0, ge=0)     # ❌ Fausse le calcul

# RECOMMANDÉ
annual_expenses: float | None = Field(default=None, ge=0)  # ✅ Explicite
```

**Impact Phase 5**:
- ⚠️ Le LLM ne peut pas distinguer "0€ de charges" vs "charges non renseignées"
- ⚠️ Contexte ambigu

**Liste des champs concernés**:
- `FreelanceProfile.annual_expenses` → devrait être `Optional`
- `FreelanceProfile.social_contributions` → devrait être `Optional`
- `FreelanceProfile.other_income` → devrait être `Optional`
- `IncomeData.salary` → OK (0 est valide)
- `DeductionsData.per_contributions` → OK (0 est valide)

---

#### 2.7 Champs Techniques dans les Modèles de Domaine

**Problème**: Certains champs techniques ne devraient pas être exposés au LLM.

| Modèle | Champ | Type | Utile LLM? | Recommandation |
|--------|-------|------|-----------|----------------|
| `TaxDocument` | `id` | int | ❌ NON | Exclure du contexte LLM |
| `TaxDocument` | `file_path` | str | ❌ NON (sécurité) | **CRITIQUE** - Exclure |
| `TaxDocument` | `raw_text` | str | ⚠️ PARTIEL | Sanitizer avec LLMSanitizer |
| `TaxDocument` | `created_at` | datetime | ❌ NON | Exclure |
| `TaxDocument` | `processed_at` | datetime | ❌ NON | Exclure |
| `TaxDocument` | `error_message` | str | ❌ NON | Exclure |
| `FreelanceProfile` | `id` | int | ❌ NON | Exclure |
| `FreelanceProfile` | `created_at` | datetime | ❌ NON | Exclure |
| `FreelanceProfile` | `updated_at` | datetime | ❌ NON | Exclure |
| `TaxCalculation` | `id` | int | ❌ NON | Exclure |
| `TaxCalculation` | `created_at` | datetime | ❌ NON | Exclure |

**Impact Phase 5**:
- ⚠️ Bruit dans le contexte LLM
- 🔴 **SÉCURITÉ**: `file_path` pourrait leaker des chemins système

**Solution**:
Créer un modèle `LLMContextModel` qui exclut ces champs.

---

### 🟡 MINEURS (Cosmétique)

#### 2.8 Manque de Docstrings sur Certains Champs

**Problème**: Certains champs n'ont pas de `description` Pydantic.

```python
# MAUVAIS
nb_parts: float  # ❌ Pas de description

# BON
nb_parts: float = Field(..., gt=0, description="Nombre de parts fiscales")  # ✅
```

**Impact Phase 5**:
- 🟡 Le LLM ne comprend pas la sémantique du champ

---

#### 2.9 Incohérence dans les Unités

**Problème**: Les pourcentages sont parfois en décimal (0.11 = 11%), parfois en entier (11).

| Champ | Modèle | Format | Recommandation |
|-------|--------|--------|----------------|
| `taux_prelevement` | Parser Avis | `float` (11.5 = 11.5%) | ✅ OK |
| `TaxBracket.rate` | TaxCalculation | `float` (0.11 = 11%) | ✅ OK |
| `effective_rate` | TaxCalculation | `float` (0.25 = 25%) | ✅ OK |
| `tmi` | API Response | `float` (0.30 = 30%) | ✅ OK |

**Conclusion**: Globalement cohérent (décimal pour les taux internes, entier pour les UI).

---

## 3. Analyse par Critère

### 🔍 3.1 Cohérence des Champs

**Chaîne**: Extraction → Models → Tax Engine → Optimization Engine → API

#### 3.1.1 Flux "Revenu Professionnel"

| Étape | Nom du Champ | Type | Notes |
|-------|--------------|------|-------|
| Parser URSSAF | `chiffre_affaires` | `float` | ✅ |
| Parser BNC/BIC | `recettes` | `float` | ⚠️ Nom différent |
| API Tax Request | `professional_gross` | `float` | ⚠️ Nom différent |
| FreelanceProfile | `annual_revenue` | `float` | ⚠️ Nom différent |
| Optimizer ProfileInput | `annual_revenue` | `float` | ✅ Cohérent avec Profile |

**Problème**: 4 noms différents pour le même concept → **Incohérence critique**

---

#### 3.1.2 Flux "Charges Déductibles"

| Étape | Nom du Champ | Type | Notes |
|-------|--------------|------|-------|
| Parser BNC/BIC | `charges` | `float` | ✅ |
| API Tax Request | `deductible_expenses` | `float` | ⚠️ Nom différent |
| FreelanceProfile | `annual_expenses` | `float` | ⚠️ Nom différent |
| Optimizer ProfileInput | `annual_expenses` | `float` | ✅ Cohérent avec Profile |

**Problème**: 3 noms différents → **Incohérence**

---

#### 3.1.3 Champs Manquants dans la Chaîne

| Champ Source | Présent dans... | Absent de... |
|--------------|-----------------|--------------|
| `nombre_parts` (Avis) | ✅ API Tax (`nb_parts`) | ⚠️ FreelanceProfile (existe mais pas lié) |
| `situation_familiale` (Avis) | ❌ Nulle part | ❌ FreelanceProfile (existe mais pas extrait) |
| `revenus_fonciers` (2042) | ⚠️ API Tax (`rental_income`) | ❌ FreelanceProfile |
| `cotisations_sociales` (URSSAF) | ⚠️ API Tax (`urssaf_paid`) | ✅ FreelanceProfile |

---

### 🔍 3.2 Types Pydantic

| Catégorie | Type Actuel | Type Recommandé | Raison |
|-----------|-------------|-----------------|--------|
| Montants monétaires | `float` | `Decimal` | Précision |
| Pourcentages (0-1) | `float` | `float` | OK |
| Pourcentages (0-100) | `float` | `confloat(ge=0, le=100)` | Validation |
| IDs | `int` ou `str` | `str` (UUID) | Phase 4 utilise `str` |
| Dates | `datetime` | `datetime` | OK |
| Enums | `str, Enum` | `str, Enum` | OK |
| Dicts non typés | `dict[str, Any]` | Pydantic Model | Validation |

---

### 🔍 3.3 Valeurs par Défaut

#### Problèmes Identifiés

```python
# ❌ DANGEREUX: 0 silencieux
annual_expenses: float = Field(default=0.0, ge=0)

# ✅ RECOMMANDÉ: Optional explicite
annual_expenses: float | None = Field(default=None, ge=0)

# ✅ OK: 0 est une valeur valide
salary: float = Field(default=0.0, ge=0, description="0 si pas de salaire")
```

---

### 🔍 3.4 Champs Inutiles pour le LLM

#### Catégories de Bruit

1. **IDs techniques**: `id`, `profile_id`, `calculation_id`
2. **Timestamps**: `created_at`, `updated_at`, `processed_at`
3. **Chemins système**: `file_path` (**SÉCURITÉ**)
4. **Métadonnées parsing**: `raw_text` (sauf si sanitized), `error_message`
5. **Status techniques**: `status` (DocumentStatus)

#### Champs Utiles pour le LLM

```python
# ✅ Données fiscales
revenu_fiscal_reference: float
impot_revenu: float
nombre_parts: float
cotisations_sociales: float

# ✅ Calculs
gross_tax: float
net_tax: float
effective_rate: float
tmi: float

# ✅ Recommandations
title: str
description: str
impact_estimated: float
action_steps: list[str]
```

---

### 🔍 3.5 Relations entre Modèles

#### Chaîne Complète

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. EXTRACTION (Phase 2)                                         │
│    Parsers → dict[str, str | float | int]                       │
│    ❌ Pas de validation Pydantic                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. STOCKAGE (Phase 1)                                           │
│    TaxDocument.extracted_fields: dict[str, Any]                 │
│    ❌ Pas de structure garantie                                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. CALCUL TAX (Phase 3)                                         │
│    TaxCalculationRequest (API) → Tax Engine → dict result       │
│    ⚠️ Modèle API ≠ Modèle Domaine                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. OPTIMISATION (Phase 4)                                       │
│    OptimizationRequest → Optimizer → OptimizationResult         │
│    ✅ Modèles Pydantic propres                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. LLM (Phase 5) - À IMPLÉMENTER                                │
│    LLMContextModel ???                                          │
│    ❌ Pas encore défini                                          │
└─────────────────────────────────────────────────────────────────┘
```

#### Problèmes dans la Chaîne

1. **Perte de données**: Les parsers extraient des champs qui ne sont pas dans `FreelanceProfile`
2. **Transformation manuelle**: Mapping entre `TaxCalculationRequest` et modèles internes
3. **Pas de modèle unifié**: Chaque phase a ses propres structures

---

### 🔍 3.6 Conventions et Noms

#### Snake_case
✅ **Respecté partout**

#### Unités

| Type | Convention Actuelle | Recommandation |
|------|---------------------|----------------|
| Montants | `float` (euros) | ✅ OK - Ajouter docstring "en euros" |
| Pourcentages internes | `float` (0-1) | ✅ OK |
| Pourcentages UI | `float` (0-100) | ✅ OK |
| Années | `int` | ✅ OK |

#### Arrondis

❌ **Pas de politique d'arrondi définie**

**Recommandation**:
```python
from decimal import Decimal, ROUND_HALF_UP

def round_euro(amount: Decimal) -> Decimal:
    """Round to nearest euro (banker's rounding)."""
    return amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
```

---

## 4. Chaîne de Données Complète

### 4.1 Scénario: Upload Avis d'Imposition → Calcul → Optimisation → LLM

```python
# ÉTAPE 1: Upload Document
POST /api/v1/documents/upload
→ file: avis_imposition_2024.pdf

# ÉTAPE 2: Extraction (Parser)
AvisImpositionParser.parse(text)
→ dict {
    "revenu_fiscal_reference": 45000.0,
    "impot_revenu": 3500.0,
    "nombre_parts": 1.0,
    "situation_familiale": "celibataire",
    "year": 2024
}

# ÉTAPE 3: Stockage
TaxDocument(
    type="avis_imposition",
    year=2024,
    status="processed",
    file_path="/data/uploads/user123/2024/abc123.pdf",  # ⚠️ NE PAS ENVOYER AU LLM
    extracted_fields={  # ⚠️ dict non validé
        "revenu_fiscal_reference": 45000.0,
        "impot_revenu": 3500.0,
        ...
    },
    raw_text="...",  # ⚠️ À sanitizer pour LLM
)

# ÉTAPE 4: Calcul Tax (API Request)
TaxCalculationRequest(
    tax_year=2024,
    person=PersonData(
        name="ANON",
        nb_parts=1.0,  # ⚠️ Nom différent de "nombre_parts"
        status="micro_bnc"
    ),
    income=IncomeData(
        professional_gross=50000.0,  # ⚠️ Nom différent de "revenu"
        salary=0.0,
        ...
    ),
    ...
)

# ÉTAPE 5: Résultat Tax Engine
→ dict {
    "impot": {
        "revenu_imposable": 33000.0,
        "impot_brut": 3500.0,
        "impot_net": 3500.0,
        "tmi": 0.30,
        ...
    },
    "socials": {...},
    "comparisons": {...},
    "warnings": [...]
}

# ÉTAPE 6: Optimisation
OptimizationRequest(
    tax_result={...},  # dict from step 5
    profile=ProfileInput(
        status="micro_bnc",
        annual_revenue=50000.0,  # ⚠️ Encore un autre nom
        ...
    )
)

# ÉTAPE 7: Résultat Optimisation
OptimizationResult(
    recommendations=[
        Recommendation(
            id="per_optimal",
            title="PER - Versement optimal",
            impact_estimated=2100.0,
            ...
        ),
        ...
    ],
    summary="...",
    potential_savings_total=5000.0
)

# ÉTAPE 8: Contexte LLM (À CRÉER)
LLMContextModel(
    # ❌ ACTUELLEMENT: Pas de modèle unifié
    # ❌ Risque: Mélange de dicts, champs techniques, chemins système

    # ✅ RECOMMANDÉ:
    fiscal_situation={
        "revenu_fiscal_reference": 45000.0,
        "nombre_parts": 1.0,
        "situation_familiale": "celibataire"
    },
    tax_calculation={
        "impot_net": 3500.0,
        "tmi": 0.30,
        "effective_rate": 0.078
    },
    recommendations=[...],  # Liste propre
    metadata={
        "year": 2024,
        "calculation_date": "2024-11-29"
    }
)
```

---

## 5. Plan de Correction

### Phase 1: Nettoyage (CRITIQUE - Avant Phase 5)

#### 1.1 Supprimer les Modèles Obsolètes
- ❌ Supprimer `src/models/recommendation.py`
- ❌ Supprimer enum `RecommendationType`
- ❌ Supprimer la duplication `RiskLevel`
- ✅ Migrer toutes les références vers `models/optimization.py`

#### 1.2 Créer des Modèles d'Extraction Validés

**Nouveau fichier**: `src/models/extracted_fields.py`

```python
"""Pydantic models for validated document extraction."""

from pydantic import BaseModel, Field

class AvisImpositionExtracted(BaseModel):
    """Validated extraction from Avis d'Imposition."""

    revenu_fiscal_reference: float | None = Field(None, ge=0, description="RFR en euros")
    revenu_imposable: float | None = Field(None, ge=0, description="Revenu net imposable en euros")
    impot_revenu: float | None = Field(None, ge=0, description="Impôt sur le revenu net en euros")
    nombre_parts: float | None = Field(None, gt=0, le=10, description="Nombre de parts fiscales")
    taux_prelevement: float | None = Field(None, ge=0, le=100, description="Taux PAS en %")
    situation_familiale: str | None = Field(None, description="Situation familiale")
    year: int | None = Field(None, ge=2000, le=2100, description="Année fiscale")

class URSSAFExtracted(BaseModel):
    """Validated extraction from URSSAF."""

    chiffre_affaires: float | None = Field(None, ge=0, description="CA déclaré en euros")
    cotisations_sociales: float | None = Field(None, ge=0, description="Total cotisations en euros")
    cotisation_maladie: float | None = Field(None, ge=0)
    cotisation_retraite: float | None = Field(None, ge=0)
    cotisation_allocations: float | None = Field(None, ge=0)
    csg_crds: float | None = Field(None, ge=0)
    formation_professionnelle: float | None = Field(None, ge=0)
    periode: str | None = None
    year: int | None = Field(None, ge=2000, le=2100)

class BNCBICExtracted(BaseModel):
    """Validated extraction from BNC/BIC."""

    recettes: float | None = Field(None, ge=0, description="Recettes brutes en euros")
    charges: float | None = Field(None, ge=0, description="Charges déductibles en euros")
    benefice: float | None = Field(None, description="Bénéfice net en euros")
    regime: str | None = Field(None, pattern="^(micro_bnc|micro_bic|reel_bnc|reel_bic)$")
    amortissements: float | None = Field(None, ge=0)
    loyer: float | None = Field(None, ge=0)
    honoraires: float | None = Field(None, ge=0)
    autres_charges: float | None = Field(None, ge=0)
    year: int | None = Field(None, ge=2000, le=2100)

class Declaration2042Extracted(BaseModel):
    """Validated extraction from Declaration 2042."""

    salaires_declarant1: float | None = Field(None, ge=0)
    salaires_declarant2: float | None = Field(None, ge=0)
    pensions_declarant1: float | None = Field(None, ge=0)
    pensions_declarant2: float | None = Field(None, ge=0)
    revenus_fonciers: float | None = Field(None, ge=0)
    revenus_capitaux: float | None = Field(None, ge=0)
    plus_values: float | None = Field(None, ge=0)
    charges_deductibles: float | None = Field(None, ge=0)
    year: int | None = Field(None, ge=2000, le=2100)
```

**Modification des Parsers**:
```python
# AVANT
async def parse(self, text: str) -> dict[str, str | float | int]:
    ...

# APRÈS
async def parse(self, text: str) -> AvisImpositionExtracted:
    fields_dict = {...}  # Extraction existante
    return AvisImpositionExtracted(**fields_dict)  # Validation Pydantic
```

#### 1.3 Standardiser les Noms de Champs

**Fichier**: `src/models/field_mapping.py`

```python
"""Canonical field names for fiscal data."""

# Terminologie française officielle
CANONICAL_FIELDS = {
    # Revenus
    "revenue": "chiffre_affaires",  # Remplace: annual_revenue, professional_gross, recettes
    "expenses": "charges_deductibles",  # Remplace: annual_expenses, deductible_expenses, charges
    "net_income": "benefice_net",  # Revenu après charges

    # Cotisations
    "social_contributions": "cotisations_sociales",  # Standard

    # Autres revenus
    "salary": "salaires",
    "rental_income": "revenus_fonciers",
    "capital_income": "revenus_capitaux",

    # Famille
    "nb_parts": "nombre_parts",  # OK partout
    "family_situation": "situation_familiale",
}
```

---

### Phase 2: Consolidation (IMPORTANT)

#### 2.1 Créer un Modèle Unifié de Profil Fiscal

**Nouveau fichier**: `src/models/fiscal_profile.py`

```python
"""Unified fiscal profile for LLM context."""

from decimal import Decimal
from pydantic import BaseModel, Field

class FiscalProfile(BaseModel):
    """
    Unified fiscal profile combining data from multiple sources.
    This model is optimized for LLM context (clean, complete, no noise).
    """

    # Identification
    annee_fiscale: int = Field(..., ge=2000, le=2100, description="Année fiscale")

    # Situation personnelle
    situation_familiale: str = Field(..., description="Celibataire, Marie, Pacse, Divorce, Veuf")
    nombre_parts: float = Field(..., gt=0, le=10, description="Nombre de parts fiscales")
    enfants_a_charge: int = Field(default=0, ge=0, le=10, description="Nombre d'enfants")
    enfants_moins_6_ans: int = Field(default=0, ge=0, description="Enfants de moins de 6 ans")

    # Activité professionnelle
    regime_fiscal: str = Field(..., description="micro_bnc, micro_bic, reel_bnc, reel_bic, eurl, sasu")
    type_activite: str = Field(..., description="BNC (libéral), BIC (commercial)")
    chiffre_affaires: Decimal = Field(..., ge=0, description="CA annuel en euros")
    charges_deductibles: Decimal = Field(default=Decimal("0"), ge=0, description="Charges réelles en euros")
    benefice_net: Decimal = Field(..., description="Bénéfice net en euros")

    # Cotisations et charges sociales
    cotisations_sociales: Decimal = Field(..., ge=0, description="Total cotisations URSSAF en euros")

    # Autres revenus
    salaires: Decimal = Field(default=Decimal("0"), ge=0, description="Salaires (hors activité pro)")
    revenus_fonciers: Decimal = Field(default=Decimal("0"), ge=0, description="Revenus fonciers")
    revenus_capitaux: Decimal = Field(default=Decimal("0"), ge=0, description="Revenus de capitaux mobiliers")

    # Déductions existantes
    per_contributions: Decimal = Field(default=Decimal("0"), ge=0, description="Versements PER")
    dons_declares: Decimal = Field(default=Decimal("0"), ge=0, description="Dons aux associations")
    services_personne: Decimal = Field(default=Decimal("0"), ge=0, description="Services à la personne")
    frais_garde: Decimal = Field(default=Decimal("0"), ge=0, description="Frais de garde d'enfants")
    pension_alimentaire: Decimal = Field(default=Decimal("0"), ge=0, description="Pension alimentaire versée")

    # Références fiscales (si disponibles depuis Avis)
    revenu_fiscal_reference: Decimal | None = Field(None, ge=0, description="RFR de l'année précédente")
    impot_annee_precedente: Decimal | None = Field(None, ge=0, description="Impôt payé l'année précédente")

    # Métadonnées (non fiscales, utiles pour le LLM)
    revenus_stables: bool = Field(default=False, description="Revenus stables sur 3 ans")
    strategie_patrimoniale: bool = Field(default=False, description="A une stratégie patrimoniale")
    capacite_investissement: Decimal = Field(default=Decimal("0"), ge=0, description="Capacité d'investissement en euros")
    tolerance_risque: str = Field(default="moderate", pattern="^(conservative|moderate|aggressive)$")
```

#### 2.2 Migrer vers `Decimal` pour les Montants

**Phase 2a** (Immédiat):
- Garder `float` dans les modèles existants
- Créer `FiscalProfile` avec `Decimal`
- Conversion à la frontière LLM

**Phase 2b** (Plus tard):
- Migrer progressivement tous les modèles vers `Decimal`

---

### Phase 3: LLMContextModel (Phase 5)

#### 3.1 Créer le Modèle de Contexte LLM

**Nouveau fichier**: `src/models/llm_context.py`

```python
"""LLM context models - Clean data for Claude."""

from pydantic import BaseModel, Field
from src.models.fiscal_profile import FiscalProfile
from src.models.optimization import Recommendation

class TaxCalculationSummary(BaseModel):
    """Clean summary of tax calculation for LLM."""

    # Résultats principaux
    impot_brut: float = Field(..., ge=0, description="Impôt brut en euros")
    impot_net: float = Field(..., ge=0, description="Impôt net après réductions en euros")
    cotisations_sociales: float = Field(..., ge=0, description="Total cotisations URSSAF en euros")
    charge_fiscale_totale: float = Field(..., ge=0, description="IR + cotisations en euros")

    # Taux
    tmi: float = Field(..., ge=0, le=1, description="Taux marginal d'imposition (0-1)")
    taux_effectif: float = Field(..., ge=0, le=1, description="Taux effectif (impôt/revenu)")

    # Détails
    revenu_imposable: float = Field(..., ge=0, description="Revenu net imposable en euros")
    quotient_familial: float = Field(..., ge=0, description="Quotient familial en euros")
    reductions_fiscales: dict[str, float] = Field(default_factory=dict, description="Réductions appliquées")

    # Comparaisons
    comparaison_micro_reel: dict | None = Field(None, description="Comparaison micro vs réel si applicable")

    # Avertissements
    warnings: list[str] = Field(default_factory=list, description="Alertes et avertissements")

class LLMContext(BaseModel):
    """
    Complete context for LLM Phase 5.

    This model contains ONLY fiscal data, no technical fields, no system paths.
    All data is validated, sanitized, and ready for Claude.
    """

    # Profil fiscal unifié
    profil: FiscalProfile = Field(..., description="Profil fiscal complet de l'utilisateur")

    # Calcul fiscal
    calcul_fiscal: TaxCalculationSummary = Field(..., description="Résumé du calcul d'impôt")

    # Optimisations
    recommendations: list[Recommendation] = Field(
        default_factory=list,
        description="Liste des recommandations d'optimisation"
    )
    total_economies_potentielles: float = Field(
        default=0.0,
        ge=0,
        description="Total des économies potentielles en euros"
    )

    # Documents (extraits sanitizés uniquement)
    documents_extraits: dict[str, dict] = Field(
        default_factory=dict,
        description="Champs extraits des documents (sans chemins, sans raw_text)"
    )

    # Métadonnées
    metadata: dict = Field(
        default_factory=dict,
        description="Métadonnées non sensibles (année, date calcul, version)"
    )

    # Configuration
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "profil": {
                    "annee_fiscale": 2024,
                    "situation_familiale": "celibataire",
                    "nombre_parts": 1.0,
                    "regime_fiscal": "micro_bnc",
                    "chiffre_affaires": 50000.0,
                    ...
                },
                "calcul_fiscal": {
                    "impot_net": 3500.0,
                    "tmi": 0.30,
                    ...
                },
                "recommendations": [...],
                "total_economies_potentielles": 2500.0,
            }
        }
```

#### 3.2 Créer le Builder de Contexte LLM

**Nouveau fichier**: `src/llm/context_builder.py`

```python
"""Build LLM context from application data."""

from decimal import Decimal
from src.models.llm_context import LLMContext, TaxCalculationSummary, FiscalProfile
from src.models.tax_document import TaxDocument
from src.models.optimization import OptimizationResult
from src.security.llm_sanitizer import sanitize_for_llm

class LLMContextBuilder:
    """Build clean LLM context from application models."""

    async def build_context(
        self,
        profile_data: dict,
        tax_result: dict,
        optimization_result: OptimizationResult | None = None,
        documents: list[TaxDocument] | None = None,
    ) -> LLMContext:
        """
        Build complete LLM context from application data.

        Args:
            profile_data: User profile dict
            tax_result: Tax calculation result dict
            optimization_result: Optimization results (optional)
            documents: List of tax documents (optional)

        Returns:
            LLMContext ready for Claude
        """
        # Build fiscal profile
        profil = self._build_fiscal_profile(profile_data, documents or [])

        # Build tax calculation summary
        calcul_fiscal = self._build_tax_summary(tax_result)

        # Extract recommendations
        recommendations = []
        total_economies = 0.0
        if optimization_result:
            recommendations = optimization_result.recommendations
            total_economies = optimization_result.potential_savings_total

        # Build sanitized document extracts (NO file_path, NO raw_text)
        documents_extraits = self._build_sanitized_document_extracts(documents or [])

        # Metadata
        metadata = {
            "version": "1.0",
            "calculation_date": datetime.now().isoformat(),
            "llm_context_version": "1.0",
        }

        return LLMContext(
            profil=profil,
            calcul_fiscal=calcul_fiscal,
            recommendations=recommendations,
            total_economies_potentielles=total_economies,
            documents_extraits=documents_extraits,
            metadata=metadata,
        )

    def _build_fiscal_profile(self, profile_data: dict, documents: list[TaxDocument]) -> FiscalProfile:
        """Build FiscalProfile from profile data and documents."""
        # TODO: Implement mapping logic
        pass

    def _build_tax_summary(self, tax_result: dict) -> TaxCalculationSummary:
        """Build TaxCalculationSummary from tax engine result."""
        impot = tax_result.get("impot", {})
        socials = tax_result.get("socials", {})

        return TaxCalculationSummary(
            impot_brut=impot.get("impot_brut", 0.0),
            impot_net=impot.get("impot_net", 0.0),
            cotisations_sociales=socials.get("expected", 0.0),
            charge_fiscale_totale=impot.get("impot_net", 0) + socials.get("expected", 0),
            tmi=impot.get("tmi", 0.0),
            taux_effectif=impot.get("taux_effectif", 0.0),
            revenu_imposable=impot.get("revenu_imposable", 0.0),
            quotient_familial=impot.get("quotient_familial", 0.0),
            reductions_fiscales=impot.get("reductions", {}),
            comparaison_micro_reel=tax_result.get("comparisons"),
            warnings=tax_result.get("warnings", []),
        )

    def _build_sanitized_document_extracts(self, documents: list[TaxDocument]) -> dict:
        """
        Build sanitized document extracts.

        EXCLUDES:
        - file_path (security)
        - id, created_at, updated_at (technical noise)
        - raw_text (too large, use extracted_fields instead)
        - error_message (internal)

        INCLUDES:
        - type, year (metadata)
        - extracted_fields (sanitized)
        """
        extracts = {}

        for doc in documents:
            doc_key = f"{doc.type.value}_{doc.year}"

            # Sanitize extracted_fields (remove PII, technical data)
            sanitized_fields = {}
            for key, value in doc.extracted_fields.items():
                # Skip technical fields
                if key in ["file_path", "original_filename", "raw_text"]:
                    continue

                # Sanitize string values
                if isinstance(value, str):
                    value = sanitize_for_llm(value)

                sanitized_fields[key] = value

            extracts[doc_key] = {
                "type": doc.type.value,
                "year": doc.year,
                "fields": sanitized_fields,
            }

        return extracts
```

---

## 6. Proposition LLMContextModel

### 6.1 Structure Recommandée

```json
{
  "profil": {
    "annee_fiscale": 2024,
    "situation_familiale": "celibataire",
    "nombre_parts": 1.0,
    "enfants_a_charge": 0,
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
    "dons_declares": 0.0
  },
  "calcul_fiscal": {
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
      "Vous êtes proche du plafond micro-BNC (77700€). Surveillez votre CA."
    ]
  },
  "recommendations": [
    {
      "id": "per_optimal",
      "title": "PER - Versement optimal",
      "description": "Verser 9240€ au PER pour réduire votre TMI",
      "impact_estimated": 2772.0,
      "risk": "low",
      "complexity": "easy",
      "confidence": 0.95,
      "category": "investment",
      "action_steps": [
        "Ouvrir un PER si pas déjà fait",
        "Verser 9240€ avant le 31/12/2024"
      ],
      "required_investment": 9240.0,
      "deadline": "2024-12-31"
    }
  ],
  "total_economies_potentielles": 2772.0,
  "documents_extraits": {
    "avis_imposition_2024": {
      "type": "avis_imposition",
      "year": 2024,
      "fields": {
        "revenu_fiscal_reference": 45000.0,
        "impot_revenu": 3200.0,
        "nombre_parts": 1.0
      }
    }
  },
  "metadata": {
    "version": "1.0",
    "calculation_date": "2024-11-29T10:30:00",
    "llm_context_version": "1.0"
  }
}
```

### 6.2 Avantages de ce Modèle

✅ **Pas de bruit technique**: Aucun `id`, `created_at`, `file_path`
✅ **Pas de données sensibles**: Chemins système exclus, PII sanitized
✅ **Structure claire**: Sections logiques (profil, calcul, recommendations)
✅ **Complet**: Toutes les données fiscales pertinentes
✅ **Validé**: Pydantic garantit la cohérence des types
✅ **Documenté**: Descriptions sur chaque champ
✅ **Versionné**: `metadata.llm_context_version` pour évolutions futures

---

## 7. Récapitulatif des Actions

### 🔴 Actions CRITIQUES (Avant Phase 5)

| # | Action | Fichiers | Priorité |
|---|--------|----------|----------|
| 1 | Supprimer `models/recommendation.py` (obsolète) | 1 fichier | P0 |
| 2 | Supprimer duplication `RiskLevel` | 1 fichier | P0 |
| 3 | Créer `models/extracted_fields.py` avec validation Pydantic | 1 nouveau | P0 |
| 4 | Modifier parsers pour retourner modèles validés | 4 fichiers | P0 |
| 5 | Créer `models/llm_context.py` | 1 nouveau | P0 |
| 6 | Créer `llm/context_builder.py` | 1 nouveau | P0 |

### 🟠 Actions IMPORTANTES (Qualité)

| # | Action | Fichiers | Priorité |
|---|--------|----------|----------|
| 7 | Standardiser noms de champs (mapping canonical) | Tous | P1 |
| 8 | Créer `models/fiscal_profile.py` (modèle unifié) | 1 nouveau | P1 |
| 9 | Ajouter docstrings manquantes | Tous | P1 |
| 10 | Migrer vers `Decimal` pour montants | Progressif | P2 |

### 🟡 Actions MINEURES (Nice to have)

| # | Action | Fichiers | Priorité |
|---|--------|----------|----------|
| 11 | Politique d'arrondi standardisée | Utils | P3 |
| 12 | Améliorer exemples dans docstrings | Tous | P3 |

---

## 8. Estimation Effort

| Phase | Actions | Temps Estimé | Risque |
|-------|---------|--------------|--------|
| **Phase 1: Nettoyage** | Actions 1-6 | 4-6 heures | ⚠️ MOYEN (breaking changes) |
| **Phase 2: Consolidation** | Actions 7-9 | 6-8 heures | 🟡 FAIBLE (ajouts) |
| **Phase 3: LLM Context** | Action 6 détaillée | 8-10 heures | 🟢 TRÈS FAIBLE (nouveau) |
| **TOTAL** | - | **18-24 heures** | - |

---

## 9. Conclusion

### État Actuel
- ⚠️ **Incohérences critiques**: Duplication modèles, noms de champs, types non validés
- ⚠️ **Bruit technique**: IDs, timestamps, file_paths dans les modèles
- ⚠️ **Pas de modèle LLM**: Aucun contexte propre défini pour Phase 5

### Après Corrections
- ✅ **Cohérence totale**: Modèles unifiés, noms standardisés, validation Pydantic partout
- ✅ **Sécurité**: Aucune donnée sensible dans le contexte LLM
- ✅ **Qualité**: Contexte propre, complet, structuré pour Claude
- ✅ **Maintenabilité**: Structure claire, versionnée, documentée

### Recommandation Finale

**BLOQUER LA PHASE 5 JUSQU'À COMPLETION DE PHASE 1 (Actions 1-6)**

Raisons:
1. 🔴 Duplication modèles = confusion LLM
2. 🔴 Pas de validation extraction = données invalides possibles
3. 🔴 Pas de contexte unifié = risque de leak données sensibles

**Temps nécessaire**: 4-6 heures pour débloquer Phase 5 proprement.

---

**Auteur**: Claude Code
**Date**: 2025-11-29
**Version**: 1.0
**Statut**: PRÊT POUR REVIEW
