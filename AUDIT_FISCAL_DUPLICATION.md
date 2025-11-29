# AUDIT COMPLET - DUPLICATIONS DE LOGIQUE FISCALE

**Date**: 2025-01-29
**Objectif**: Identifier toutes les duplications avant Phase 5 (LLM)
**Statut**: 🔴 CRITIQUE - Duplications majeures identifiées

---

## SYNTHÈSE EXÉCUTIVE

**Résultat**: 7 duplications critiques et importantes identifiées

| Duplication | Fichiers concernés | Risque | Impact Phase 5 |
|-------------|-------------------|--------|----------------|
| Plafonds réductions fiscales | `core.py` ↔ `optimization_rules.json` | 🔴 CRITIQUE | Incohérence LLM |
| Calcul plafond PER | `core.py` ↔ `per_strategy.py` | 🔴 CRITIQUE | Divergence calculs |
| Seuils micro/réel | `baremes_2024.json` ↔ `optimization_rules.json` | ⚠️ IMPORTANT | Redondance |
| Abattements micro | `baremes_2024.json` ↔ `optimization_rules.json` | ⚠️ IMPORTANT | Redondance |
| Taux URSSAF | `baremes_2024.json` ↔ Non utilisé ailleurs | ⚙️ MINEUR | OK |
| TMI calculation | Centralisé ✅ | ✅ OK | Pas de duplication |
| Barème IR | Centralisé ✅ | ✅ OK | Pas de duplication |

---

## 🔴 DUPLICATION #1: PLAFONDS ET TAUX DE RÉDUCTIONS FISCALES

### Localisation

**Fichier 1**: `src/tax_engine/core.py`
```python
# Lignes 215-241 - apply_tax_reductions()

# Dons (66% reduction, plafond 20% of revenu_imposable)
dons = reductions_data.get("dons", 0.0)
if dons > 0:
    plafond_dons = revenu_imposable * 0.20          # ⚠️ HARDCODÉ
    dons_eligible = min(dons, plafond_dons)
    reduction_dons = dons_eligible * 0.66           # ⚠️ HARDCODÉ

# Services à la personne (50% credit, plafond 12000€)
services = reductions_data.get("services_personne", 0.0)
if services > 0:
    plafond_services = 12000                        # ⚠️ HARDCODÉ
    services_eligible = min(services, plafond_services)
    credit_services = services_eligible * 0.50      # ⚠️ HARDCODÉ

# Frais de garde (50% credit, 3500€ per child under 6)
frais_garde = reductions_data.get("frais_garde", 0.0)
children_under_6 = reductions_data.get("children_under_6", 0)
if frais_garde > 0 and children_under_6 > 0:
    plafond_garde = 3500 * children_under_6         # ⚠️ HARDCODÉ
    garde_eligible = min(frais_garde, plafond_garde)
    credit_garde = garde_eligible * 0.50            # ⚠️ HARDCODÉ
```

**Fichier 2**: `src/analyzers/rules/optimization_rules.json`
```json
{
  "deductions": {
    "dons": {
      "reduction_rate": 0.66,        // ✅ En JSON
      "plafond_rate": 0.20,          // ✅ En JSON
    },
    "services_personne": {
      "credit_rate": 0.50,           // ✅ En JSON
      "plafond": 12000,              // ✅ En JSON
      "plafond_first_year": 15000,
    },
    "frais_garde": {
      "credit_rate": 0.50,           // ✅ En JSON
      "plafond_per_child": 3500,     // ✅ En JSON
      "age_limit": 6,
    }
  }
}
```

### Divergence

❌ **INCOHÉRENCE TOTALE**: Les valeurs sont en double!
- Le tax_engine a les valeurs **hardcodées** en Python
- Les analyzers ont les **mêmes valeurs** en JSON
- **Aucune source unique de vérité**

### Risque

🔴 **CRITIQUE** - Impact Phase 5:
- Si on modifie `optimization_rules.json`, le tax_engine ne voit PAS le changement
- Si on modifie `core.py`, les stratégies ne voient PAS le changement
- Le LLM pourrait recommander des optimisations avec des valeurs différentes du calcul réel
- **Résultats fiscaux faux possibles**

### Impact

- ❌ Les recommandations des stratégies (deductions_strategy.py) utilisent les valeurs JSON
- ❌ Le calcul d'impôt réel (compute_ir) utilise les valeurs hardcodées
- ❌ **Incohérence garantie entre recommandation et calcul**

---

## 🔴 DUPLICATION #2: CALCUL PLAFOND PER

### Localisation

**Fichier 1**: `src/tax_engine/core.py:160-191`
```python
def apply_per_deduction_with_limit(
    per_contribution: float,
    professional_income: float,
    rules: TaxRules,
) -> tuple[float, float]:
    """Apply PER deduction with plafond limit."""

    # Get PER plafond rules from baremes
    per_plafonds = rules.per_plafonds
    base_rate = per_plafonds.get("base_rate", 0.10)    # ⚠️ Fallback 0.10
    max_plafond = per_plafonds.get("max_salarie", 35194)  # ⚠️ Fallback 35194

    # Calculate plafond: 10% of professional income
    plafond = professional_income * base_rate

    # Apply min/max limits
    plafond = max(4399, min(plafond, max_plafond))     # ⚠️ HARDCODÉ 4399

    # ...
```

**Fichier 2**: `src/analyzers/strategies/per_strategy.py:96-101`
```python
def _calculate_plafond(self, revenu_prof: float) -> float:
    """Calculate PER plafond (10% of professional income)."""
    plafond = revenu_prof * self.rules["plafond_calculation"]["rate"]  # JSON: 0.10
    plafond = max(plafond, self.rules["plafond_calculation"]["min_plafond"])  # JSON: 4399
    plafond = min(plafond, self.rules["plafond_calculation"]["max_plafond"])  # JSON: 35200
    return plafond
```

**Fichier 3**: `src/analyzers/rules/per_rules.json`
```json
{
  "plafond_calculation": {
    "rate": 0.10,           // ✅ En JSON
    "min_plafond": 4399,    // ✅ En JSON
    "max_plafond": 35200,   // ✅ En JSON (différent de baremes_2024!)
  }
}
```

**Fichier 4**: `src/tax_engine/data/baremes_2024.json`
```json
{
  "per_plafonds": {
    "base_rate": 0.10,
    "max_tns": 83088,
    "max_salarie": 35194,    // ⚠️ DIFFÉRENT de per_rules.json (35200 vs 35194)
  }
}
```

### Divergence

❌ **INCOHÉRENCE MAJEURE**:
1. **Logique dupliquée**: Le calcul du plafond existe dans 2 fichiers Python
2. **Valeurs dupliquées**: Les plafonds existent dans 2 fichiers JSON
3. **VALEURS DIFFÉRENTES**:
   - `baremes_2024.json`: max_salarie = **35194€**
   - `per_rules.json`: max_plafond = **35200€**
   - **Différence de 6€** - laquelle est correcte?
4. **Fallback hardcodé**: `core.py` a 4399 en dur, `per_strategy.py` le lit du JSON

### Risque

🔴 **CRITIQUE** - Impact Phase 5:
- Deux calculs différents pour le même plafond PER
- Valeurs max différentes entre barèmes officiels et règles PER
- Si baremes_2024.json est mis à jour, per_rules.json reste obsolète
- Le LLM ne saura pas quelle valeur est la bonne

---

## ⚠️ DUPLICATION #3: SEUILS MICRO/RÉEL

### Localisation

**Fichier 1**: `src/tax_engine/data/baremes_2024.json`
```json
{
  "plafonds_micro": {
    "bnc": 77700,
    "bic_service": 77700,
    "bic_vente": 188700,
  }
}
```

**Fichier 2**: `src/analyzers/rules/optimization_rules.json`
```json
{
  "regime_thresholds": {
    "micro_bnc": {
      "threshold": 77700,
      "abattement": 0.34
    },
    "micro_bic_services": {
      "threshold": 77700,
      "abattement": 0.50
    },
    "micro_bic_ventes": {
      "threshold": 188700,
      "abattement": 0.71
    }
  }
}
```

**Fichier 3**: `src/analyzers/rules/lmnp_rules.json`
```json
{
  "regimes": {
    "micro": {
      "threshold": 77700,
      "abattement": 0.50,
    }
  }
}
```

### Divergence

✅ **Valeurs cohérentes** (pour l'instant)
❌ **Triple duplication**: mêmes seuils dans 3 fichiers

### Risque

⚠️ **IMPORTANT** - Impact Phase 5:
- Si le seuil micro change (mise à jour fiscale), il faut modifier **3 fichiers**
- Risque d'oubli = incohérence
- Le LLM verra 3 sources différentes pour la même information

---

## ⚠️ DUPLICATION #4: ABATTEMENTS MICRO-RÉGIME

### Localisation

**Fichier 1**: `src/tax_engine/data/baremes_2024.json`
```json
{
  "abattements": {
    "micro_bnc": 0.34,
    "micro_bic_vente": 0.71,
    "micro_bic_service": 0.50,
  }
}
```

**Fichier 2**: `src/analyzers/rules/optimization_rules.json`
```json
{
  "regime_thresholds": {
    "micro_bnc": {
      "threshold": 77700,
      "abattement": 0.34    // ⚠️ DUPLICATION
    },
    "micro_bic_services": {
      "threshold": 77700,
      "abattement": 0.50    // ⚠️ DUPLICATION
    },
    "micro_bic_ventes": {
      "threshold": 188700,
      "abattement": 0.71    // ⚠️ DUPLICATION
    }
  }
}
```

**Fichier 3**: `src/analyzers/rules/lmnp_rules.json`
```json
{
  "regimes": {
    "micro": {
      "threshold": 77700,
      "abattement": 0.50,   // ⚠️ DUPLICATION (BIC service)
    }
  }
}
```

### Divergence

✅ **Valeurs cohérentes** (pour l'instant)
❌ **Triple duplication**: mêmes taux dans 3 fichiers

### Risque

⚠️ **IMPORTANT** - Impact Phase 5:
- Si taux d'abattement change, il faut modifier **3 fichiers**
- Le tax_engine utilise baremes_2024.json (source officielle)
- Les stratégies utilisent optimization_rules.json et lmnp_rules.json
- **Incohérence possible si mise à jour partielle**

---

## ⚙️ DUPLICATION #5: TAUX URSSAF

### Localisation

**Fichier 1**: `src/tax_engine/data/baremes_2024.json`
```json
{
  "urssaf_rates": {
    "liberal_bnc": 0.218,
    "commercial_bic": 0.128,
    "artisan_bic": 0.128,
  }
}
```

**Utilisation**:
- `tax_engine/core.py:374` - `rules.get_urssaf_rate(activity)`
- ✅ Utilisé par compute_socials() pour calculer les cotisations attendues
- ✅ Pas de duplication trouvée

### Risque

⚙️ **MINEUR** - Pas de duplication détectée
- Une seule source: baremes_2024.json
- Utilisé uniquement par le tax_engine

---

## ✅ PAS DE DUPLICATION: TMI (Taux Marginal d'Imposition)

### Localisation

**Source unique**: `src/tax_engine/core.py:41-71`
```python
def calculate_tmi(revenu_imposable: float, nb_parts: float, rules: TaxRules) -> float:
    """Calculate Taux Marginal d'Imposition (TMI) - centralized function."""
    part_income = revenu_imposable / nb_parts
    brackets = rules.income_tax_brackets
    # ... logique centralisée
```

**Utilisations**:
- `tax_engine/core.py:311` - compute_ir()
- `analyzers/strategies/per_strategy.py:57` - analyse PER
- `analyzers/strategies/lmnp_strategy.py:51` - analyse LMNP (depuis Phase 4.1)

### Statut

✅ **EXCELLENT** - Centralisé correctement
- ✅ Une seule fonction calculate_tmi()
- ✅ Toutes les stratégies l'importent et l'utilisent
- ✅ Source unique: baremes_2024.json via TaxRules

---

## ✅ PAS DE DUPLICATION: BARÈME IR

### Localisation

**Source unique**: `src/tax_engine/core.py:74-157`
```python
def apply_bareme(part_income: float, rules: TaxRules) -> float:
    """Apply progressive tax brackets to part income."""
    # ... logique centralisée

def apply_bareme_detailed(...) -> tuple[float, list[dict[str, float]]]:
    """Apply progressive tax brackets with detailed breakdown."""
    # ... logique centralisée
```

**Données**: `src/tax_engine/data/baremes_2024.json`
```json
{
  "income_tax_brackets": [
    {"rate": 0.0, "lower_bound": 0, "upper_bound": 11294},
    {"rate": 0.11, "lower_bound": 11294, "upper_bound": 28797},
    {"rate": 0.30, "lower_bound": 28797, "upper_bound": 82341},
    {"rate": 0.41, "lower_bound": 82341, "upper_bound": 177106},
    {"rate": 0.45, "lower_bound": 177106, "upper_bound": null}
  ]
}
```

### Statut

✅ **EXCELLENT** - Centralisé correctement
- ✅ Une seule fonction apply_bareme()
- ✅ Données dans un seul fichier: baremes_2024.json
- ✅ Utilisé uniquement par compute_ir() du tax_engine

---

## 📊 TABLEAU RÉCAPITULATIF DES DUPLICATIONS

| # | Type | Fichiers | Valeurs | Risque | Action requise |
|---|------|----------|---------|--------|----------------|
| 1 | Plafonds réductions | core.py ↔ optimization_rules.json | 0.66, 0.20, 12000, 0.50, 3500 | 🔴 CRITIQUE | Centraliser dans baremes_2024.json |
| 2 | Plafond PER | core.py ↔ per_strategy.py ↔ 2 JSON | 0.10, 4399, 35194/35200 | 🔴 CRITIQUE | Unifier calcul + résoudre divergence |
| 3 | Seuils micro | baremes_2024.json ↔ optimization_rules.json ↔ lmnp_rules.json | 77700, 188700 | ⚠️ IMPORTANT | Supprimer doublons JSON |
| 4 | Abattements | baremes_2024.json ↔ optimization_rules.json ↔ lmnp_rules.json | 0.34, 0.50, 0.71 | ⚠️ IMPORTANT | Supprimer doublons JSON |
| 5 | URSSAF | baremes_2024.json | 0.218, 0.128 | ✅ OK | Aucune |
| 6 | TMI | core.py + baremes_2024.json | Tranches IR | ✅ OK | Aucune |
| 7 | Barème IR | core.py + baremes_2024.json | Tranches IR | ✅ OK | Aucune |

---

## 🎯 IMPACT PHASE 5 (LLM)

### Problèmes identifiés

1. **Incohérence recommandations ↔ calculs réels**
   - Le LLM recommandera des optimisations basées sur `optimization_rules.json`
   - Le calcul fiscal réel utilisera `core.py` avec des valeurs différentes
   - **Résultat**: Recommandations fausses, perte de confiance utilisateur

2. **Source de vérité ambiguë**
   - Le LLM ne saura pas quelle source utiliser (4 fichiers JSON différents)
   - Risque de hallucinations basées sur des valeurs obsolètes

3. **Maintenance impossible**
   - Mise à jour fiscale 2025 = modifier 4-5 fichiers différents
   - Risque d'oubli = incohérences garanties

4. **Divergence PER critique**
   - 6€ de différence entre baremes_2024.json et per_rules.json
   - Quelle est la valeur officielle? Le système ne sait pas.

---

## ✅ POINTS POSITIFS

1. ✅ **TMI centralisé** - Excellent, déjà résolu en Phase 4.1
2. ✅ **Barème IR centralisé** - Parfait, une seule source
3. ✅ **URSSAF centralisé** - Pas de duplication
4. ✅ **Architecture tax_engine solide** - Bonne séparation core/rules/calculator

---

## 🚀 PRIORITÉS DE REFACTORING

### 🔴 CRITIQUE (Bloquer Phase 5)

1. **Centraliser plafonds/taux réductions fiscales**
   - Ajouter à `baremes_2024.json`:
     ```json
     "tax_reductions": {
       "dons": {"rate": 0.66, "plafond_rate": 0.20},
       "services_personne": {"rate": 0.50, "plafond": 12000, "plafond_first_year": 15000},
       "frais_garde": {"rate": 0.50, "plafond_per_child": 3500, "age_limit": 6}
     }
     ```
   - Modifier `core.py:apply_tax_reductions()` pour utiliser `rules.tax_reductions`
   - Supprimer de `optimization_rules.json` (ou le faire pointer vers baremes)

2. **Unifier calcul plafond PER**
   - Résoudre divergence: 35194€ ou 35200€? (Vérifier source officielle)
   - Créer fonction utilitaire `calculate_per_plafond()` dans `tax_utils.py`
   - Supprimer `per_strategy._calculate_plafond()`
   - Unifier les données JSON

### ⚠️ IMPORTANT (Phase 5.1)

3. **Centraliser seuils micro/réel**
   - Unique source: `baremes_2024.json.plafonds_micro`
   - Supprimer de `optimization_rules.json` et `lmnp_rules.json`
   - Créer fonction `get_micro_threshold(regime_type, rules)`

4. **Centraliser abattements**
   - Unique source: `baremes_2024.json.abattements`
   - Supprimer de `optimization_rules.json` et `lmnp_rules.json`
   - Fonction existante `rules.get_abattement()` est déjà bonne

---

## 📋 PLAN D'ACTION DÉTAILLÉ

Voir section suivante du rapport pour le plan complet de refactoring.
