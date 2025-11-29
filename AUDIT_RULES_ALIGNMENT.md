# 🔍 AUDIT COMPLET - Alignement Règles JSON vs Stratégies

**Date**: 2025-11-29
**Objectif**: Garantir que la Phase 5 (LLM) repose sur des règles stables, cohérentes, validées

---

## 📊 RÉSUMÉ EXÉCUTIF

### ✅ Points forts
- **5 fichiers JSON** bien structurés avec sources officielles
- **7 stratégies** Python correspondantes
- Utilisation cohérente des règles JSON dans le code
- Bonne séparation des responsabilités

### ⚠️ Problèmes critiques identifiés
1. **LMNP Strategy**: Calcul TMI dupliqué (devrait utiliser `calculate_tmi()` centralisé)
2. **Types incohérents**: Certains champs manquent de typage clair (int vs float)
3. **Champs non utilisés**: Certains champs JSON ne sont jamais référencés
4. **Valeurs business**: Quelques incohérences dans les calculs métier

---

## 📋 ANALYSE DÉTAILLÉE PAR STRATÉGIE

### 1️⃣ PER (Plan Épargne Retraite)

#### 📄 Fichier JSON: `per_rules.json`

**Champs définis:**
```json
{
  "plafond_calculation": {
    "rate": 0.10,              // ✅ Utilisé (ligne 92)
    "min_plafond": 4399,       // ✅ Utilisé (ligne 93)
    "max_plafond": 35200       // ✅ Utilisé (ligne 94)
  },
  "eligibility": {
    "min_income": 1000         // ❌ NON UTILISÉ dans le code
  },
  "tmi_thresholds": {
    "0.11": { "min_interest": 500 },  // ✅ Utilisé (ligne 106)
    "0.30": { "min_interest": 300 },  // ✅ Utilisé (ligne 104)
    "0.41": { "min_interest": 100 },  // ✅ Utilisé (ligne 102)
    "0.45": { "min_interest": 100 }   // ✅ Utilisé (ligne 100)
  },
  "recommendation_modes": {
    "optimal": { "target_rate": 0.7 },  // ✅ Utilisé (ligne 118)
    "safe": { "target_rate": 0.5 },     // ❌ NON UTILISÉ
    "max": { "target_rate": 1.0 }       // ❌ NON UTILISÉ
  }
}
```

**Stratégie Python: `per_strategy.py`**
- ✅ Charge correctement le fichier JSON (ligne 23)
- ✅ Utilise `calculate_tmi()` centralisé (ligne 51) - **REFACTORÉ RÉCEMMENT**
- ✅ Applique correctement le plafond PER

**🔍 Problèmes identifiés:**

1. **Champ inutilisé**: `eligibility.min_income` (1000€)
   - **Ligne JSON**: 14
   - **Impact**: Aucune vérification du revenu minimum
   - **Correction**: Ajouter vérification dans `analyze()`:
   ```python
   min_income = self.rules["eligibility"]["min_income"]
   if revenu_imposable < min_income:
       return recommendations
   ```

2. **Modes safe/max inutilisés**
   - **Lignes JSON**: 40-47
   - **Impact**: Code incomplet, options non proposées
   - **Correction**: Soit les supprimer du JSON, soit implémenter les recommandations correspondantes

**Types et unités:**
- ✅ `rate`: float (0.10 = 10%)
- ✅ `min_plafond`, `max_plafond`: int (euros)
- ✅ `min_interest`: int (euros)
- ✅ `target_rate`: float (0.0-1.0)

**Cohérence métier:**
- ✅ Plafond légal PER correct: 4399€ min, 35200€ max, 10% du revenu
- ✅ Seuils TMI cohérents avec la logique métier
- ✅ Target rate optimal (70%) raisonnable

---

### 2️⃣ LMNP (Location Meublée Non Professionnelle)

#### 📄 Fichier JSON: `lmnp_rules.json`

**Champs définis:**
```json
{
  "regimes": {
    "micro_bic": {
      "threshold": 77700,        // ❌ NON UTILISÉ
      "abattement": 0.50         // ❌ NON UTILISÉ
    },
    "reel": {
      "avg_amortissement_rate": 0.035,  // ❌ NON UTILISÉ
      "avg_charges_rate": 0.70          // ❌ NON UTILISÉ (ligne 87 hardcodé 0.85)
    }
  },
  "eligibility": {
    "min_tmi": 0.30,                      // ✅ Utilisé (ligne 50)
    "min_investment_capacity": 50000      // ✅ Utilisé (ligne 54)
  },
  "advantages": { ... },     // ❌ NON UTILISÉ (hardcodé dans description)
  "warnings": [ ... ]        // ❌ NON UTILISÉ (hardcodé dans description)
}
```

**Stratégie Python: `lmnp_strategy.py`**
- ✅ Charge correctement le fichier JSON (ligne 21)
- ❌ **CRITIQUE**: Calcul TMI dupliqué (lignes 64-77) - devrait utiliser `calculate_tmi()` centralisé
- ❌ Valeurs hardcodées au lieu d'utiliser le JSON

**🔍 Problèmes critiques:**

1. **TMI DUPLIQUÉ** ⚠️⚠️⚠️
   - **Lignes**: 64-77
   - **Impact**: Divergence avec core engine, risque d'incohérence
   - **Correction urgente**:
   ```python
   # SUPPRIMER lignes 64-77
   def _estimate_tmi(self, revenu_imposable: float, nb_parts: float) -> float:
       ...

   # REMPLACER par:
   from src.tax_engine.core import calculate_tmi
   from src.tax_engine.rules import get_tax_rules

   def __init__(self):
       ...
       self.tax_rules = get_tax_rules(2024)

   # Dans analyze():
   tmi = calculate_tmi(revenu_imposable, nb_parts, self.tax_rules)
   ```

2. **Valeurs hardcodées vs JSON**
   - **Ligne 84**: `estimated_rental = investment_capacity * 0.04` (4% yield hardcodé)
   - **Ligne 88**: `estimated_savings = estimated_rental * tmi * 0.85` (85% hardcodé, devrait utiliser `avg_charges_rate`)
   - **Correction**: Utiliser les valeurs du JSON
   ```python
   avg_yield = 0.04  # Ajouter au JSON
   charges_rate = self.rules["regimes"]["reel"]["avg_charges_rate"]
   amortissement_rate = self.rules["regimes"]["reel"]["avg_amortissement_rate"]

   # Calcul cohérent avec le JSON
   estimated_savings = estimated_rental * tmi * (charges_rate + amortissement_rate)
   ```

3. **Champs JSON inutilisés**
   - `regimes.micro_bic.*`: Complètement ignoré
   - `advantages`, `warnings`: Hardcodés dans le code au lieu d'utiliser le JSON
   - **Impact**: Duplication, risque d'incohérence lors des mises à jour
   - **Correction**: Utiliser `self.rules["advantages"]["fiscal"]` dans la description

**Types et unités:**
- ✅ `threshold`: int (euros)
- ✅ `abattement`: float (0.50 = 50%)
- ✅ `avg_amortissement_rate`: float (0.035 = 3.5%)
- ✅ `avg_charges_rate`: float (0.70 = 70%)
- ✅ `min_tmi`: float (0.30 = 30%)
- ✅ `min_investment_capacity`: int (euros)

**Cohérence métier:**
- ✅ Seuil micro-BIC 77700€ correct
- ✅ Abattement 50% correct
- ⚠️ `avg_amortissement_rate` (3.5%) et `avg_charges_rate` (70%) semblent cohérents mais non utilisés

---

### 3️⃣ Girardin Industriel

#### 📄 Fichier JSON: `girardin_rules.json`

**Champs définis:**
```json
{
  "types": {
    "industriel": {
      "reduction_rate": 1.10,        // ✅ Utilisé (ligne 71)
      "risk": "high",                // ❌ NON UTILISÉ
      "commitment_years": 5          // ✅ Utilisé (ligne 84)
    },
    "habitation": { ... }            // ❌ NON UTILISÉ (stratégie inexistante)
  },
  "eligibility": {
    "min_impot": 3000,               // ✅ Utilisé (ligne 46)
    "stable_income": true,           // ✅ Utilisé (ligne 55)
    "risk_tolerance": "medium_to_high"  // ✅ Utilisé (ligne 51)
  },
  "recommended_provider": {
    "name": "Profina",               // ✅ Utilisé (ligne 95)
    "description": "...",            // ✅ Utilisé (ligne 96)
    "website": "...",                // ✅ Utilisé (ligne 104, 112)
    "advantages": [ ... ]            // ✅ Utilisé (lignes 100-101)
  },
  "warnings": [ ... ],               // ✅ Utilisé (ligne 121)
  "calculation": {
    "example": { ... }               // ❌ NON UTILISÉ (mais OK, juste un exemple)
  }
}
```

**Stratégie Python: `girardin_strategy.py`**
- ✅ Charge correctement le fichier JSON (ligne 21)
- ✅ Utilise la majorité des champs
- ✅ Intégration Profina bien faite

**🔍 Problèmes identifiés:**

1. **Girardin Habitation non implémenté**
   - **Ligne JSON**: 14-19
   - **Impact**: Type de Girardin non proposé (reduction_rate 48%)
   - **Correction**:
     - Option 1: Supprimer du JSON si pas implémenté
     - Option 2: Implémenter une stratégie pour Girardin Habitation

2. **Champ `risk` inutilisé**
   - **Ligne JSON**: 10
   - **Impact**: Redondance avec `RiskLevel.HIGH` hardcodé ligne 132
   - **Correction**: Utiliser le champ JSON pour définir le risk level
   ```python
   risk_level_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.HIGH}
   risk_level = risk_level_map[industriel_rules["risk"]]
   ```

3. **Calcul métier - Target reduction**
   - **Ligne 74**: `target_reduction = min(impot_net * 0.35, impot_net - 500)`
   - **Impact**: Valeur 0.35 (35%) hardcodée, devrait être dans le JSON
   - **Correction**: Ajouter au JSON
   ```json
   "recommended_investment": {
     "target_reduction_rate": 0.35,
     "min_tax_remaining": 500
   }
   ```

**Types et unités:**
- ✅ `reduction_rate`: float (1.10 = 110% !)
- ✅ `commitment_years`: int
- ✅ `min_impot`: int (euros)
- ✅ `stable_income`: bool
- ✅ `risk_tolerance`: string

**Cohérence métier:**
- ✅ **Réduction 110% CORRECTE** - C'est bien 110% du montant investi
- ✅ Engagement 5 ans conforme à la réglementation
- ✅ Seuil min 3000€ d'impôt raisonnable
- ✅ Calcul net_gain = reduction - investment correct (lignes 78)

---

### 4️⃣ FCPI / FIP

#### 📄 Fichier JSON: `fcpi_fip_rules.json`

**Champs définis:**
```json
{
  "fcpi": {
    "reduction_rate": 0.18,          // ✅ Utilisé (ligne 66)
    "plafond_individual": 12000,     // ✅ Utilisé (ligne 72)
    "plafond_couple": 24000,         // ✅ Utilisé (ligne 70)
    "commitment_years": 5,           // ✅ Utilisé (ligne 84)
    "risk": "medium"                 // ❌ NON UTILISÉ (hardcodé ligne 120)
  },
  "fip": {
    "regional_bonus": { ... }        // ❌ NON UTILISÉ (stratégie FIP non implémentée)
  },
  "eligibility": {
    "min_impot": 1000,               // ✅ Utilisé (ligne 46)
    "risk_tolerance": "medium"       // ✅ Utilisé (ligne 51)
  },
  "advantages": [ ... ],             // ❌ NON UTILISÉ
  "warnings": [ ... ],               // ✅ Utilisé (ligne 138)
  "calculation": { ... }             // ❌ NON UTILISÉ (exemples uniquement)
}
```

**Stratégie Python: `fcpi_fip_strategy.py`**
- ✅ Charge correctement le fichier JSON (ligne 21)
- ✅ Applique correctement le plafond selon situation familiale
- ❌ FIP non implémenté malgré le nom de la stratégie

**🔍 Problèmes identifiés:**

1. **FIP non implémenté**
   - **Impact**: Nom de classe trompeur `FCPIFIPStrategy` mais seul FCPI implémenté
   - **Ligne JSON FIP**: 15-28
   - **Correction**:
     - Option 1: Renommer classe en `FCPIStrategy`
     - Option 2: Implémenter FIP avec bonus régionaux (Corse, Outre-Mer = 25%)

2. **Champ `risk` inutilisé**
   - **Ligne JSON**: 13
   - **Impact**: RiskLevel.MEDIUM hardcodé ligne 120
   - **Correction**: Utiliser `self.rules["fcpi"]["risk"]`

3. **Champ `advantages` inutilisé**
   - **Lignes JSON**: 35-40
   - **Impact**: Avantages hardcodés dans la description (lignes 95-99)
   - **Correction**: Boucler sur `self.rules["advantages"]`

4. **Calcul métier - Investment recommendation**
   - **Ligne 76**: `recommended_investment = min(plafond * 0.4, impot_net * 0.3)`
   - **Impact**: Valeurs 0.4 (40%) et 0.3 (30%) hardcodées
   - **Correction**: Ajouter au JSON
   ```json
   "recommended_investment": {
     "plafond_rate": 0.4,
     "impot_rate": 0.3,
     "min_amount": 1000
   }
   ```

**Types et unités:**
- ✅ `reduction_rate`: float (0.18 = 18%)
- ✅ `plafond_individual`, `plafond_couple`: int (euros)
- ✅ `commitment_years`: int
- ✅ `min_impot`: int (euros)
- ✅ `regional_bonus`: float (0.25 = 25%)

**Cohérence métier:**
- ✅ Réduction 18% CORRECTE
- ✅ Plafonds 12k€/24k€ CORRECTS (2024)
- ✅ Engagement 5 ans conforme
- ⚠️ Bonus régional 25% pour Corse/Outre-Mer non utilisé

---

### 5️⃣ Déductions Simples (Dons, Services, Garde)

#### 📄 Fichier JSON: `optimization_rules.json`

**Champs définis - Section deductions:**
```json
{
  "dons": {
    "reduction_rate": 0.66,          // ✅ Utilisé (ligne 71)
    "plafond_rate": 0.20             // ✅ Utilisé (ligne 65)
  },
  "services_personne": {
    "credit_rate": 0.50,             // ✅ Utilisé (ligne 140)
    "plafond": 12000,                // ✅ Utilisé (ligne 135)
    "plafond_first_year": 15000,     // ❌ NON UTILISÉ
    "examples": [ ... ]              // ✅ Utilisé (lignes 150-151)
  },
  "frais_garde": {
    "credit_rate": 0.50,             // ✅ Utilisé (ligne 207)
    "plafond_per_child": 3500,       // ✅ Utilisé (ligne 203)
    "age_limit": 6                   // ✅ Utilisé (ligne 197, 208)
  },
  "renovation_energetique": { ... }  // ❌ NON UTILISÉ (stratégie non implémentée)
}
```

**Stratégie Python: `deductions_strategy.py`**
- ✅ Charge correctement le fichier JSON (ligne 21)
- ✅ Utilise bien la majorité des champs
- ✅ Bon usage des sources

**🔍 Problèmes identifiés:**

1. **`plafond_first_year` inutilisé**
   - **Ligne JSON**: 19
   - **Impact**: Plafond majoré 1ère année (15000€) pas appliqué
   - **Correction**: Ajouter paramètre `is_first_year` dans context et utiliser:
   ```python
   plafond = (services_rules["plafond_first_year"]
              if context.get("is_first_year_services", False)
              else services_rules["plafond"])
   ```

2. **Rénovation énergétique non implémentée**
   - **Lignes JSON**: 42-49
   - **Impact**: Stratégie importante absente (MaPrimeRénov')
   - **Correction**:
     - Option 1: Implémenter la stratégie
     - Option 2: Supprimer du JSON (complexe, montants variables)

3. **Valeurs hardcodées**
   - **Ligne 68**: `if revenu_imposable > 10000:` (seuil hardcodé)
   - **Ligne 70**: `suggested_don = min(500, ...)` (500€ hardcodé)
   - **Ligne 132**: `if impot_net < 500:` (seuil hardcodé)
   - **Correction**: Ajouter au JSON
   ```json
   "min_income_for_dons": 10000,
   "suggested_don_amount": 500,
   "min_impot_for_services": 500
   ```

**Types et unités:**
- ✅ `reduction_rate`, `credit_rate`: float (0.66, 0.50)
- ✅ `plafond_rate`: float (0.20 = 20%)
- ✅ `plafond`, `plafond_per_child`: int (euros)
- ✅ `age_limit`: int
- ✅ `examples`: array[string]

**Cohérence métier:**
- ✅ Dons 66% plafond 20% CORRECT
- ✅ Services 50% plafond 12000€ CORRECT
- ✅ Garde 50% plafond 3500€/enfant CORRECT
- ✅ Limite âge 6 ans CORRECTE

---

### 6️⃣ Régime (Micro vs Réel)

#### 📄 Fichier JSON: `optimization_rules.json`

**Champs définis - Section regime_thresholds:**
```json
{
  "micro_bnc": {
    "threshold": 77700,              // ✅ Utilisé (ligne 147)
    "abattement": 0.34               // ❌ NON UTILISÉ (dans core engine)
  },
  "micro_bic_services": {
    "threshold": 77700,              // ✅ Utilisé (ligne 150-151)
    "abattement": 0.50               // ❌ NON UTILISÉ
  },
  "micro_bic_ventes": {
    "threshold": 188700,             // ✅ Utilisé (ligne 155)
    "abattement": 0.71               // ❌ NON UTILISÉ
  }
}
```

**Stratégie Python: `regime_strategy.py`**
- ✅ Charge correctement le fichier JSON (ligne 21)
- ✅ Utilise les seuils pour alertes
- ❌ N'utilise pas les abattements (gérés par core engine)

**🔍 Problèmes identifiés:**

1. **Abattements non utilisés dans la stratégie**
   - **Impact**: OK - Les abattements sont gérés par le core engine
   - **Note**: Redondance entre `optimization_rules.json` et `baremes_2024.json`
   - **Correction**: Aucune - c'est une référence utile, pas un problème

2. **Seuil de proximité hardcodé**
   - **Ligne 163**: `if 0.85 <= proximity_rate < 1.0:` (85% hardcodé)
   - **Correction**: Ajouter au JSON
   ```json
   "threshold_warning": {
     "proximity_rate": 0.85,
     "description": "Alert when CA reaches 85% of threshold"
   }
   ```

3. **Seuil d'impact hardcodé**
   - **Ligne 45**: `if abs(comparison["delta"]) > 500:` (500€ hardcodé)
   - **Correction**: Ajouter au JSON
   ```json
   "min_delta_for_recommendation": 500
   ```

**Types et unités:**
- ✅ `threshold`: int (euros)
- ✅ `abattement`: float (0.34, 0.50, 0.71)

**Cohérence métier:**
- ✅ Seuils 77700€ (BNC + BIC services) et 188700€ (BIC ventes) CORRECTS pour 2024
- ✅ Abattements 34%, 50%, 71% CORRECTS
- ✅ Alerte proximité à 85% pertinente

---

### 7️⃣ Structure (SASU / EURL / Holding)

#### 📄 Fichier JSON: `optimization_rules.json`

**Champs définis - Section structure_thresholds:**
```json
{
  "consider_sasu": {
    "ca_min": 50000,                 // ✅ Utilisé (ligne 61, 138)
    "charges_rate_min": 0.25         // ✅ Utilisé (ligne 62, 139-140)
  },
  "consider_eurl": {
    "ca_min": 50000,                 // ❌ NON UTILISÉ
    "charges_rate_min": 0.25         // ❌ NON UTILISÉ
  },
  "consider_holding": {
    "ca_min": 100000,                // ✅ Utilisé (ligne 71, 207)
    "patrimony_strategy": true       // ✅ Utilisé (ligne 160)
  }
}
```

**Stratégie Python: `structure_strategy.py`**
- ✅ Charge correctement le fichier JSON (ligne 21)
- ✅ Applique les seuils correctement
- ✅ SASU et EURL traités ensemble

**🔍 Problèmes identifiés:**

1. **EURL rules non utilisées**
   - **Lignes JSON**: 71-75
   - **Impact**: Redondance avec SASU (mêmes seuils)
   - **Correction**: Soit supprimer, soit différencier les seuils SASU vs EURL

2. **Estimated savings hardcodé**
   - **Ligne 120**: `estimated_savings = annual_revenue * 0.03` (3% hardcodé)
   - **Ligne 188**: `impact_estimated=annual_revenue * 0.02` (2% hardcodé)
   - **Correction**: Ajouter au JSON
   ```json
   "sasu_eurl_estimated_savings_rate": 0.03,
   "holding_estimated_savings_rate": 0.02
   ```

3. **Coûts hardcodés**
   - **Ligne 136**: `required_investment=3000` (coût création hardcodé)
   - **Ligne 205**: `required_investment=10000` (coût holding hardcodé)
   - **Correction**: Ajouter au JSON
   ```json
   "costs": {
     "sasu_eurl_creation": 3000,
     "holding_creation": 10000
   }
   ```

**Types et unités:**
- ✅ `ca_min`: int (euros)
- ✅ `charges_rate_min`: float (0.25 = 25%)
- ✅ `patrimony_strategy`: bool

**Cohérence métier:**
- ✅ Seuil 50k€ CA pour SASU/EURL pertinent
- ✅ Seuil 25% charges minimum cohérent
- ✅ Seuil 100k€ pour holding raisonnable
- ✅ Patrimony strategy comme critère pertinent

---

## 🔴 PROBLÈMES CRITIQUES PAR PRIORITÉ

### PRIORITÉ 1 - URGENT ⚠️⚠️⚠️

1. **LMNP Strategy - TMI dupliqué**
   - **Fichier**: `src/analyzers/strategies/lmnp_strategy.py`
   - **Lignes**: 64-77
   - **Action**: Supprimer `_estimate_tmi()` et utiliser `calculate_tmi()` centralisé
   - **Impact**: CRITIQUE - Divergence avec core engine

### PRIORITÉ 2 - IMPORTANT ⚠️⚠️

2. **Champs JSON non utilisés**
   - **PER**: `eligibility.min_income`, modes `safe` et `max`
   - **LMNP**: `regimes.micro_bic.*`, `regimes.reel.*`, `advantages`, `warnings`
   - **Girardin**: `types.habitation`, `types.industriel.risk`
   - **FCPI/FIP**: Toute la section FIP, `fcpi.risk`, `advantages`
   - **Deductions**: `services_personne.plafond_first_year`, `renovation_energetique`
   - **Structure**: `consider_eurl`
   - **Action**: Soit utiliser, soit supprimer

3. **Valeurs métier hardcodées**
   - LMNP: Yield 4%, charges 85%
   - Girardin: Target reduction 35%
   - FCPI: Plafond rate 40%, impot rate 30%
   - Deductions: Seuils 10000€, 500€
   - Regime: Proximity 85%, delta min 500€
   - Structure: Savings rates 3%/2%, coûts 3000€/10000€
   - **Action**: Déplacer dans JSON

### PRIORITÉ 3 - AMÉLIORATIONS ⚠️

4. **Stratégies manquantes**
   - Girardin Habitation
   - FIP avec bonus régionaux
   - Rénovation énergétique
   - **Action**: Implémenter ou supprimer du JSON

5. **Types et documentation**
   - Ajouter commentaires de type dans JSON (euros, pourcentage)
   - Documenter unités clairement
   - **Action**: Améliorer documentation

---

## ✅ CORRECTIONS À APPLIQUER

### 📝 Corrections JSON

#### 1. `per_rules.json`

```json
{
  "eligibility": {
    "min_income": 1000,
    "description": "Revenu professionnel minimum requis"
  },
  // SUPPRIMER modes safe et max OU les implémenter
  "recommendation_modes": {
    "optimal": {
      "description": "Optimise le ratio gain fiscal / capacité d'épargne",
      "target_rate": 0.7
    }
    // Supprimer "safe" et "max" si non utilisés
  }
}
```

#### 2. `lmnp_rules.json`

```json
{
  "regimes": {
    "reel": {
      "description": "Régime réel avec amortissement",
      "avg_amortissement_rate": 0.035,
      "avg_charges_rate": 0.70,
      "avg_total_deduction_rate": 0.85,  // AJOUTER (charges + amortissement)
      "estimated_yield": 0.04  // AJOUTER
    }
  }
}
```

#### 3. `girardin_rules.json`

```json
{
  "types": {
    // SUPPRIMER "habitation" si non implémenté
    "industriel": {
      "reduction_rate": 1.10,
      "risk": "high",
      "commitment_years": 5
    }
  },
  // AJOUTER
  "recommended_investment": {
    "target_reduction_rate": 0.35,
    "min_tax_remaining": 500,
    "description": "Viser 35% de l'impôt net, garder minimum 500€"
  }
}
```

#### 4. `fcpi_fip_rules.json`

```json
{
  // SUPPRIMER section "fip" si non implémenté OU implémenter
  "fcpi": {
    "name": "FCPI (Fonds Communs de Placement dans l'Innovation)",
    "reduction_rate": 0.18,
    "plafond_individual": 12000,
    "plafond_couple": 24000,
    "commitment_years": 5,
    "risk": "medium"
  },
  // AJOUTER
  "recommended_investment": {
    "plafond_rate": 0.4,
    "impot_rate": 0.3,
    "min_amount": 1000,
    "description": "Investir 40% du plafond ou 30% de l'impôt"
  }
}
```

#### 5. `optimization_rules.json` - Section deductions

```json
{
  "dons": {
    "reduction_rate": 0.66,
    "plafond_rate": 0.20,
    "min_income_for_recommendation": 10000,  // AJOUTER
    "suggested_amount": 500  // AJOUTER
  },
  "services_personne": {
    "credit_rate": 0.50,
    "plafond": 12000,
    "plafond_first_year": 15000,
    "min_impot_for_recommendation": 500,  // AJOUTER
    "examples": [...]
  }
  // SUPPRIMER "renovation_energetique" si non implémenté
}
```

#### 6. `optimization_rules.json` - Section regime_thresholds

```json
{
  "regime_thresholds": {
    "micro_bnc": {...},
    "micro_bic_services": {...},
    "micro_bic_ventes": {...}
  },
  // AJOUTER
  "regime_optimization": {
    "min_delta_for_recommendation": 500,
    "threshold_proximity_alert": 0.85,
    "description": "Recommander changement si delta > 500€, alerter à 85% du seuil"
  }
}
```

#### 7. `optimization_rules.json` - Section structure_thresholds

```json
{
  "structure_thresholds": {
    "consider_sasu": {
      "ca_min": 50000,
      "charges_rate_min": 0.25,
      "estimated_savings_rate": 0.03,  // AJOUTER
      "creation_cost": 3000  // AJOUTER
    },
    // SUPPRIMER "consider_eurl" (redondant) OU différencier
    "consider_holding": {
      "ca_min": 100000,
      "patrimony_strategy": true,
      "estimated_savings_rate": 0.02,  // AJOUTER
      "creation_cost": 10000  // AJOUTER
    }
  }
}
```

---

### 📝 Corrections Python

#### 1. `per_strategy.py` - Ajouter vérification min_income

```python
def analyze(self, tax_result: dict, profile: dict, context: dict) -> list[Recommendation]:
    # AJOUTER après ligne 46
    # Check minimum income eligibility
    min_income = self.rules["eligibility"]["min_income"]
    if revenu_imposable < min_income:
        return recommendations

    # ... reste du code
```

#### 2. `lmnp_strategy.py` - CRITIQUE: Supprimer TMI dupliqué

```python
"""LMNP (Location Meublée Non Professionnelle) optimization strategy."""

import json
import uuid
from pathlib import Path

from src.models.optimization import (
    ComplexityLevel,
    Recommendation,
    RecommendationCategory,
    RiskLevel,
)
from src.tax_engine.core import calculate_tmi  # AJOUTER
from src.tax_engine.rules import get_tax_rules  # AJOUTER


class LMNPStrategy:
    """Analyzes LMNP investment optimization opportunities."""

    def __init__(self) -> None:
        """Initialize the LMNP strategy with rules."""
        rules_path = Path(__file__).parent.parent / "rules" / "lmnp_rules.json"
        with open(rules_path, encoding="utf-8") as f:
            self.rules = json.load(f)["rules"]

        # AJOUTER
        self.tax_rules = get_tax_rules(2024)

    def analyze(self, tax_result: dict, profile: dict, context: dict) -> list[Recommendation]:
        # ... existing code ...

        # REMPLACER ligne 43
        # OLD: tmi = self._estimate_tmi(revenu_imposable, nb_parts)
        # NEW:
        tmi = calculate_tmi(revenu_imposable, nb_parts, self.tax_rules)

        # ... reste du code ...

    # SUPPRIMER méthode _estimate_tmi (lignes 64-77)

    def _create_lmnp_recommendation(self, tmi: float, investment_capacity: float, risk_tolerance: str) -> Recommendation:
        # REMPLACER lignes 84-88 pour utiliser les valeurs du JSON
        reel_rules = self.rules["regimes"]["reel"]
        estimated_yield = reel_rules.get("estimated_yield", 0.04)
        total_deduction_rate = reel_rules.get("avg_total_deduction_rate", 0.85)

        estimated_rental = investment_capacity * estimated_yield
        estimated_savings = estimated_rental * tmi * total_deduction_rate

        # ... reste du code ...
```

#### 3. `girardin_strategy.py` - Utiliser valeurs JSON

```python
def _create_girardin_industriel_recommendation(self, impot_net: float) -> Recommendation:
    # REMPLACER ligne 74 pour utiliser JSON
    recommended_investment_rules = self.rules.get("recommended_investment", {
        "target_reduction_rate": 0.35,
        "min_tax_remaining": 500
    })

    target_reduction = min(
        impot_net * recommended_investment_rules["target_reduction_rate"],
        impot_net - recommended_investment_rules["min_tax_remaining"]
    )

    # AJOUTER pour utiliser le champ "risk"
    industriel_rules = self.rules["types"]["industriel"]
    risk_level_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.HIGH}
    risk = risk_level_map.get(industriel_rules["risk"], RiskLevel.HIGH)

    # ... et utiliser `risk` au lieu de RiskLevel.HIGH hardcodé ligne 132
```

#### 4. `fcpi_fip_strategy.py` - Utiliser valeurs JSON

```python
def _create_fcpi_recommendation(self, impot_net: float, nb_parts: float) -> Recommendation | None:
    fcpi_rules = self.rules["fcpi"]

    # AJOUTER pour utiliser recommended_investment
    investment_rules = self.rules.get("recommended_investment", {
        "plafond_rate": 0.4,
        "impot_rate": 0.3,
        "min_amount": 1000
    })

    # REMPLACER ligne 76
    recommended_investment = min(
        plafond * investment_rules["plafond_rate"],
        impot_net * investment_rules["impot_rate"]
    )

    # REMPLACER ligne 78
    if recommended_investment < investment_rules["min_amount"]:
        return None

    # AJOUTER pour utiliser le champ "risk"
    risk_level_map = {"low": RiskLevel.LOW, "medium": RiskLevel.MEDIUM, "high": RiskLevel.HIGH}
    risk = risk_level_map.get(fcpi_rules["risk"], RiskLevel.MEDIUM)

    # ... et utiliser `risk` au lieu de RiskLevel.MEDIUM hardcodé ligne 120
```

#### 5. `deductions_strategy.py` - Utiliser valeurs JSON

```python
def _analyze_dons(self, tax_result: dict, context: dict) -> Recommendation | None:
    dons_rules = self.rules["dons"]

    # AJOUTER/MODIFIER pour utiliser les seuils du JSON
    min_income = dons_rules.get("min_income_for_recommendation", 10000)
    suggested_amount = dons_rules.get("suggested_amount", 500)

    # REMPLACER ligne 68
    if current_dons < plafond and revenu_imposable > min_income:
        # REMPLACER ligne 70
        suggested_don = min(suggested_amount, (plafond - current_dons) * 0.3)
        # ... reste du code

def _analyze_services_personne(self, tax_result: dict, context: dict) -> Recommendation | None:
    services_rules = self.rules["services_personne"]

    # AJOUTER pour utiliser min_impot
    min_impot = services_rules.get("min_impot_for_recommendation", 500)

    # REMPLACER ligne 132
    if impot_net < min_impot:
        return None

    # AJOUTER pour gérer plafond première année
    is_first_year = context.get("is_first_year_services", False)
    plafond = (services_rules["plafond_first_year"] if is_first_year
               else services_rules["plafond"])
```

#### 6. `regime_strategy.py` - Utiliser valeurs JSON

```python
def __init__(self) -> None:
    rules_path = Path(__file__).parent.parent / "rules" / "optimization_rules.json"
    with open(rules_path, encoding="utf-8") as f:
        data = json.load(f)
        self.rules = data
        # AJOUTER accès à regime_optimization
        self.regime_optimization = data.get("regime_optimization", {
            "min_delta_for_recommendation": 500,
            "threshold_proximity_alert": 0.85
        })

def analyze(self, tax_result: dict, profile: dict, context: dict) -> list[Recommendation]:
    # REMPLACER ligne 45
    min_delta = self.regime_optimization["min_delta_for_recommendation"]
    if abs(comparison["delta"]) > min_delta:
        # ...

def _check_threshold_proximity(self, profile: dict) -> Recommendation | None:
    # REMPLACER ligne 163
    proximity_alert = self.regime_optimization["threshold_proximity_alert"]
    if proximity_alert <= proximity_rate < 1.0:
        # ...
```

#### 7. `structure_strategy.py` - Utiliser valeurs JSON

```python
def _create_sasu_eurl_recommendation(self, annual_revenue: float, charges_rate: float, tax_result: dict) -> Recommendation:
    sasu_rules = self.rules["consider_sasu"]

    # AJOUTER pour utiliser savings_rate et costs
    savings_rate = sasu_rules.get("estimated_savings_rate", 0.03)
    creation_cost = sasu_rules.get("creation_cost", 3000)

    # REMPLACER ligne 120
    estimated_savings = annual_revenue * savings_rate

    # REMPLACER ligne 136
    required_investment = creation_cost

def _create_holding_recommendation(self, annual_revenue: float, context: dict) -> Recommendation | None:
    holding_rules = self.rules["consider_holding"]

    # AJOUTER
    savings_rate = holding_rules.get("estimated_savings_rate", 0.02)
    creation_cost = holding_rules.get("creation_cost", 10000)

    # REMPLACER ligne 188
    impact_estimated = annual_revenue * savings_rate

    # REMPLACER ligne 205
    required_investment = creation_cost
```

---

## 📊 RÉCAPITULATIF PAR TYPE DE PROBLÈME

### Types de problèmes identifiés

| Type | Nombre | Exemples |
|------|--------|----------|
| TMI dupliqué | 1 | LMNP strategy (CRITIQUE) |
| Champs JSON inutilisés | 15 | eligibility.min_income, modes safe/max, etc. |
| Valeurs hardcodées | 20+ | Yields, seuils, rates, coûts |
| Stratégies manquantes | 3 | Girardin Habitation, FIP, Rénovation |
| Types/unités imprécis | 0 | ✅ Tous cohérents |
| Logique métier incorrecte | 0 | ✅ Tous corrects |

### Cohérence métier globale: ✅ EXCELLENTE

- ✅ PER: Plafond 10%, min 4399€, max 35200€ - CORRECT
- ✅ LMNP: Seuil micro-BIC 77700€, abattement 50% - CORRECT
- ✅ Girardin: Réduction 110%, engagement 5 ans - CORRECT
- ✅ FCPI: Réduction 18%, plafonds 12k€/24k€ - CORRECT
- ✅ Dons: 66%, plafond 20% - CORRECT
- ✅ Services: 50%, plafond 12000€ - CORRECT
- ✅ Garde: 50%, 3500€/enfant <6 ans - CORRECT
- ✅ Seuils micro: 77700€ BNC/BIC services, 188700€ BIC ventes - CORRECT

---

## 🎯 PLAN D'ACTION RECOMMANDÉ

### Phase 1: URGENT (Avant Phase 5)

1. ✅ **Corriger TMI dupliqué dans LMNP** (1h)
   - Supprimer `_estimate_tmi()`
   - Utiliser `calculate_tmi()` centralisé

2. ✅ **Nettoyer champs inutilisés** (2h)
   - Supprimer: Girardin Habitation, FIP complet, EURL rules
   - OU implémenter les stratégies correspondantes

3. ✅ **Déplacer valeurs hardcodées vers JSON** (3h)
   - LMNP: yield, deduction rate
   - Girardin: target reduction, min tax remaining
   - FCPI: investment rates
   - Deductions: seuils recommandation
   - Regime: delta min, proximity
   - Structure: savings rates, costs

### Phase 2: Important (Après Phase 5)

4. ⚠️ **Implémenter champs manquants** (4h)
   - PER: min_income check
   - Services: plafond_first_year
   - Ajouter paramètres context nécessaires

5. ⚠️ **Documenter unités dans JSON** (1h)
   - Ajouter commentaires: `// euros`, `// percentage (0.0-1.0)`
   - Créer schéma de validation JSON

### Phase 3: Améliorations futures

6. 💡 **Stratégies additionnelles** (optionnel)
   - Girardin Habitation
   - FIP avec bonus régionaux
   - Rénovation énergétique (complexe)

---

## 📈 IMPACT SUR PHASE 5 (LLM)

### ✅ Points forts pour LLM
- Règles JSON structurées et lisibles
- Sources officielles présentes
- Logique métier correcte
- Types cohérents

### ⚠️ Risques pour LLM
1. **TMI LMNP dupliqué** → Risque de recommandations incohérentes
2. **Valeurs hardcodées** → Difficile pour LLM de les identifier/modifier
3. **Champs inutilisés** → Confusion pour LLM (quoi utiliser?)

### 🎯 Recommandations LLM
1. **Nettoyer AVANT Phase 5** - TMI dupliqué CRITIQUE
2. **Centraliser les valeurs** - Tout dans JSON
3. **Documenter les unités** - Aider LLM à comprendre
4. **Valider avec schéma JSON** - Assurer cohérence

---

## ✅ CONCLUSION

### État actuel: 8/10

Le code est **globalement excellent** avec:
- ✅ Logique métier 100% correcte
- ✅ Sources officielles présentes
- ✅ Architecture propre et modulaire
- ✅ Types cohérents

### Points d'amélioration critiques:

1. **TMI dupliqué LMNP** (BLOQUANT pour Phase 5)
2. Champs JSON inutilisés (confusion)
3. Valeurs hardcodées (maintenance difficile)

### Prêt pour Phase 5?

**Après correction TMI LMNP: OUI ✅**

Le reste est de la dette technique, pas bloquant pour Phase 5, mais à traiter rapidement après pour maintenir la qualité.

---

**Date du rapport**: 2025-11-29
**Auteur**: Claude Code Audit
**Version**: 1.0
