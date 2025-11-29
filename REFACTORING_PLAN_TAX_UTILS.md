# PLAN DE REFACTORING COMPLET - TAX_UTILS.PY

**Objectif**: Éliminer toutes les duplications fiscales avant Phase 5
**Approche**: Créer un module `tax_utils.py` comme source unique de vérité

---

## 🧩 PARTIE 1: CONCEPTION TAX_UTILS.PY

### Architecture proposée

```
src/tax_engine/
├── core.py              # Calculs IR, sociales (GARDE les apply_bareme, compute_ir)
├── calculator.py        # Orchestration (inchangé)
├── rules.py             # Chargeur barèmes (inchangé)
├── tax_utils.py         # ✨ NOUVEAU - Fonctions utilitaires fiscales
└── data/
    └── baremes_2024.json  # ✨ ENRICHI - Devient source unique complète
```

### Contenu de tax_utils.py

```python
"""Utility functions for tax calculations - single source of truth.

This module provides reusable tax calculation utilities to avoid duplication
across the codebase. All fiscal logic should be centralized here or in core.py.

Key principles:
- Single source of truth: All values come from baremes JSON via TaxRules
- No hardcoded values: Everything is configurable
- Reusable: Used by both tax_engine and analyzers
- Testable: Pure functions with clear inputs/outputs
"""

from src.tax_engine.rules import TaxRules


def calculate_per_plafond(
    professional_income: float,
    rules: TaxRules,
    status: str = "salarie"
) -> float:
    """Calculate PER (Plan Épargne Retraite) deduction ceiling.

    Args:
        professional_income: Annual professional income (for plafond calculation)
        rules: Tax rules with PER plafonds
        status: Professional status ("salarie", "tns", "married_salarie")

    Returns:
        PER plafond in euros

    Example:
        >>> rules = get_tax_rules(2024)
        >>> calculate_per_plafond(50000, rules, "salarie")
        5000.0  # 10% of 50k, capped at min/max
    """
    per_plafonds = rules.per_plafonds
    base_rate = per_plafonds.get("base_rate", 0.10)

    # Calculate base plafond (10% of income)
    plafond = professional_income * base_rate

    # Get min/max limits from baremes
    min_plafond = per_plafonds.get("min_plafond", 4399)

    # Max depends on status
    max_key = f"max_{status}"
    max_plafond = per_plafonds.get(max_key, per_plafonds.get("max_salarie", 35194))

    # Apply limits
    plafond = max(min_plafond, min(plafond, max_plafond))

    return round(plafond, 2)


def get_tax_reduction_rate(reduction_type: str, rules: TaxRules) -> float:
    """Get tax reduction/credit rate for a specific type.

    Args:
        reduction_type: Type of reduction ("dons", "services_personne", "frais_garde")
        rules: Tax rules with reduction rates

    Returns:
        Reduction rate as decimal (e.g., 0.66 for 66%)

    Raises:
        KeyError: If reduction type not found
    """
    reductions = rules.tax_reductions  # NEW property in TaxRules
    if reduction_type not in reductions:
        raise KeyError(f"Unknown reduction type: {reduction_type}")
    return reductions[reduction_type]["rate"]


def get_tax_reduction_plafond(
    reduction_type: str,
    rules: TaxRules,
    revenu_imposable: float = 0.0,
    children_under_6: int = 0
) -> float:
    """Get tax reduction plafond (ceiling) for a specific type.

    Args:
        reduction_type: Type of reduction
        rules: Tax rules
        revenu_imposable: Taxable income (for percentage-based plafonds like dons)
        children_under_6: Number of children under 6 (for frais_garde)

    Returns:
        Plafond in euros

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_tax_reduction_plafond("dons", rules, 50000)
        10000.0  # 20% of 50k
        >>> get_tax_reduction_plafond("services_personne", rules)
        12000.0  # Fixed plafond
    """
    reductions = rules.tax_reductions
    reduction_config = reductions.get(reduction_type, {})

    if reduction_type == "dons":
        # Percentage-based plafond
        plafond_rate = reduction_config.get("plafond_rate", 0.20)
        return revenu_imposable * plafond_rate

    elif reduction_type == "services_personne":
        # Fixed plafond (first year has higher limit)
        return reduction_config.get("plafond", 12000)

    elif reduction_type == "frais_garde":
        # Per-child plafond
        plafond_per_child = reduction_config.get("plafond_per_child", 3500)
        return plafond_per_child * children_under_6

    else:
        raise KeyError(f"Unknown reduction type: {reduction_type}")


def calculate_tax_reduction(
    reduction_type: str,
    amount: float,
    rules: TaxRules,
    revenu_imposable: float = 0.0,
    children_under_6: int = 0
) -> tuple[float, float]:
    """Calculate tax reduction/credit with plafond.

    Args:
        reduction_type: Type of reduction
        amount: Amount spent/donated
        rules: Tax rules
        revenu_imposable: Taxable income (for percentage plafonds)
        children_under_6: Number of children under 6

    Returns:
        Tuple of (reduction_amount, amount_exceeding_plafond)

    Example:
        >>> rules = get_tax_rules(2024)
        >>> calculate_tax_reduction("dons", 1000, rules, 50000)
        (660.0, 0.0)  # 66% of 1000, within plafond
    """
    # Get rate and plafond
    rate = get_tax_reduction_rate(reduction_type, rules)
    plafond = get_tax_reduction_plafond(
        reduction_type, rules, revenu_imposable, children_under_6
    )

    # Calculate eligible amount (capped at plafond)
    eligible_amount = min(amount, plafond)
    excess_amount = max(0, amount - plafond)

    # Calculate reduction
    reduction = eligible_amount * rate

    return round(reduction, 2), round(excess_amount, 2)


def get_micro_threshold(regime_type: str, rules: TaxRules) -> int:
    """Get CA threshold for micro-regime.

    Args:
        regime_type: Type of regime ("bnc", "bic_service", "bic_vente")
        rules: Tax rules with plafonds_micro

    Returns:
        Threshold in euros

    Raises:
        KeyError: If regime type not found

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_micro_threshold("bnc", rules)
        77700
    """
    plafonds = rules.plafonds_micro
    if regime_type not in plafonds:
        raise KeyError(f"Unknown regime type: {regime_type}")
    return plafonds[regime_type]


def get_micro_abattement(regime_type: str, rules: TaxRules) -> float:
    """Get abattement rate for micro-regime.

    Args:
        regime_type: Full regime name (e.g., "micro_bnc", "micro_bic_service")
        rules: Tax rules with abattements

    Returns:
        Abattement rate as decimal (e.g., 0.34 for 34%)

    Raises:
        KeyError: If regime not found

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_micro_abattement("micro_bnc", rules)
        0.34
    """
    return rules.get_abattement(regime_type)


def check_micro_threshold_proximity(
    revenue: float,
    regime_type: str,
    rules: TaxRules,
    alert_threshold: float = 0.85
) -> dict[str, Any]:
    """Check if revenue is approaching micro-regime threshold.

    Args:
        revenue: Annual revenue
        regime_type: Type of regime ("bnc", "bic_service", "bic_vente")
        rules: Tax rules
        alert_threshold: Alert when revenue reaches this % of threshold (default 85%)

    Returns:
        Dict with:
            - approaching: bool, True if within alert zone
            - threshold: int, The threshold value
            - proximity_rate: float, revenue / threshold
            - remaining: float, euros remaining before threshold

    Example:
        >>> rules = get_tax_rules(2024)
        >>> check_micro_threshold_proximity(70000, "bnc", rules)
        {
            "approaching": True,
            "threshold": 77700,
            "proximity_rate": 0.90,
            "remaining": 7700.0
        }
    """
    threshold = get_micro_threshold(regime_type, rules)
    proximity_rate = revenue / threshold
    remaining = threshold - revenue

    return {
        "approaching": proximity_rate >= alert_threshold and proximity_rate < 1.0,
        "threshold": threshold,
        "proximity_rate": round(proximity_rate, 4),
        "remaining": round(remaining, 2)
    }


def get_lmnp_deduction_rate(regime: str, rules: TaxRules) -> float:
    """Get LMNP total deduction rate for estimations.

    Args:
        regime: LMNP regime ("micro" or "reel")
        rules: Tax rules

    Returns:
        Total deduction rate as decimal

    Note:
        - Micro: Fixed abattement (0.50)
        - Réel: Average total deduction from charges + amortization
        This is for ESTIMATION only. Real deduction varies by property.

    Example:
        >>> rules = get_tax_rules(2024)
        >>> get_lmnp_deduction_rate("reel", rules)
        0.85  # Average 85% deduction (charges + amortization)
    """
    # For LMNP, we need specific rules (not in baremes_2024.json)
    # This will be migrated to baremes when we consolidate
    if regime == "micro":
        return get_micro_abattement("micro_bic_service", rules)  # 0.50
    elif regime == "reel":
        # This should come from a lmnp section in baremes_2024.json
        # For now, return typical value (will be refactored)
        return 0.85  # TODO: Move to baremes_2024.json
    else:
        raise ValueError(f"Unknown LMNP regime: {regime}")


def estimate_lmnp_yield(rules: TaxRules) -> float:
    """Get estimated rental yield for LMNP.

    Args:
        rules: Tax rules

    Returns:
        Estimated annual yield as decimal (e.g., 0.04 for 4%)

    Note:
        This is a market estimate for calculations, not a guarantee.
        Real yield varies by location and property type.
    """
    # TODO: Move to baremes_2024.json or separate market data file
    return 0.04  # 4% typical yield
```

---

## 🔄 PARTIE 2: MODIFICATIONS BAREMES_2024.JSON

### Ajouts requis

```json
{
  "year": 2024,
  "source": "https://www.impots.gouv.fr/particulier/calcul-de-limpot",
  "source_date": "2024-01-01",

  // ... existing income_tax_brackets, abattements, plafonds_micro ...

  // ✨ NOUVEAU: Réductions et crédits d'impôt
  "tax_reductions": {
    "dons": {
      "rate": 0.66,
      "plafond_rate": 0.20,
      "description": "Dons aux associations: 66% de réduction, plafonné à 20% du revenu imposable",
      "sources": ["https://www.service-public.fr/particuliers/vosdroits/F426"]
    },
    "services_personne": {
      "rate": 0.50,
      "plafond": 12000,
      "plafond_first_year": 15000,
      "description": "Services à la personne: 50% de crédit d'impôt, plafond 12k€ (15k€ 1ère année)",
      "examples": ["Ménage", "Garde d'enfants", "Jardinage", "Petits travaux", "Soutien scolaire"],
      "sources": ["https://www.service-public.fr/particuliers/vosdroits/F12"]
    },
    "frais_garde": {
      "rate": 0.50,
      "plafond_per_child": 3500,
      "age_limit": 6,
      "description": "Frais de garde: 50% de crédit d'impôt, 3500€ par enfant de moins de 6 ans",
      "sources": ["https://www.service-public.fr/particuliers/vosdroits/F8"]
    }
  },

  // ✨ AMÉLIORATION: PER plafonds avec min_plafond
  "per_plafonds": {
    "base_rate": 0.10,
    "min_plafond": 4399,        // ✨ AJOUTÉ
    "max_tns": 83088,
    "max_salarie": 35194,       // ⚠️ Vérifier: 35194 ou 35200?
    "max_married_salarie": 70388,
    "description": "Plafonds déduction PER: 10% revenus pro, min 4399€, plafonds selon statut",
    "sources": [
      "https://www.service-public.fr/particuliers/vosdroits/F34982",
      "https://www.impots.gouv.fr/particulier/le-plan-depargne-retraite-individuel-peri"
    ]
  },

  // ✨ NOUVEAU: Estimations LMNP (optionnel, pourrait être dans un fichier séparé)
  "lmnp_market_estimates": {
    "estimated_yield": 0.04,
    "reel_avg_total_deduction_rate": 0.85,
    "reel_avg_charges_rate": 0.70,
    "reel_avg_amortissement_rate": 0.035,
    "note": "Estimations de marché pour simulations. Résultats réels varient selon bien et location.",
    "disclaimer": "Ces valeurs sont des moyennes de marché, pas des garanties fiscales."
  }
}
```

---

## 🔄 PARTIE 3: MODIFICATIONS TAXRULES (rules.py)

### Ajout de propriétés

```python
# In src/tax_engine/rules.py

class TaxRules:
    # ... existing code ...

    @property
    def tax_reductions(self) -> dict[str, dict]:
        """Get tax reductions and credits configuration.

        Returns:
            Dict with dons, services_personne, frais_garde config
        """
        return self.data.get("tax_reductions", {})

    @property
    def lmnp_estimates(self) -> dict[str, float]:
        """Get LMNP market estimates for simulations.

        Returns:
            Dict with estimated_yield, deduction rates, etc.
        """
        return self.data.get("lmnp_market_estimates", {})
```

---

## ✂️ PARTIE 4: MODIFICATIONS CORE.PY

### apply_tax_reductions() - Utiliser tax_utils

**AVANT** (`core.py:193-246`):
```python
def apply_tax_reductions(
    impot_brut: float,
    revenu_imposable: float,
    reductions_data: dict[str, float],
) -> tuple[float, dict[str, float]]:
    reductions_applied = {}
    total_reduction = 0.0

    # 1. Dons (66% reduction, plafond 20% of revenu_imposable)
    dons = reductions_data.get("dons", 0.0)
    if dons > 0:
        plafond_dons = revenu_imposable * 0.20          # ❌ HARDCODÉ
        dons_eligible = min(dons, plafond_dons)
        reduction_dons = dons_eligible * 0.66           # ❌ HARDCODÉ
        reductions_applied["dons"] = round(reduction_dons, 2)
        total_reduction += reduction_dons

    # ... etc
```

**APRÈS** (utiliser tax_utils):
```python
def apply_tax_reductions(
    impot_brut: float,
    revenu_imposable: float,
    reductions_data: dict[str, float],
    rules: TaxRules,  # ✨ AJOUTÉ
) -> tuple[float, dict[str, float]]:
    from src.tax_engine.tax_utils import calculate_tax_reduction  # ✨ IMPORT

    reductions_applied = {}
    total_reduction = 0.0

    # 1. Dons
    dons = reductions_data.get("dons", 0.0)
    if dons > 0:
        reduction_dons, _ = calculate_tax_reduction(
            "dons", dons, rules, revenu_imposable=revenu_imposable
        )  # ✨ UTILISE tax_utils
        reductions_applied["dons"] = reduction_dons
        total_reduction += reduction_dons

    # 2. Services à la personne
    services = reductions_data.get("services_personne", 0.0)
    if services > 0:
        credit_services, _ = calculate_tax_reduction(
            "services_personne", services, rules
        )  # ✨ UTILISE tax_utils
        reductions_applied["services_personne"] = credit_services
        total_reduction += credit_services

    # 3. Frais de garde
    frais_garde = reductions_data.get("frais_garde", 0.0)
    children_under_6 = reductions_data.get("children_under_6", 0)
    if frais_garde > 0 and children_under_6 > 0:
        credit_garde, _ = calculate_tax_reduction(
            "frais_garde", frais_garde, rules, children_under_6=children_under_6
        )  # ✨ UTILISE tax_utils
        reductions_applied["frais_garde"] = credit_garde
        total_reduction += credit_garde

    # Apply reductions to gross tax
    impot_net = max(0.0, impot_brut - total_reduction)

    return impot_net, reductions_applied
```

**Changement dans compute_ir()**:
```python
# Ligne 324 dans compute_ir()
impot_net, tax_reductions = apply_tax_reductions(
    impot_brut=impot_brut,
    revenu_imposable=revenu_imposable,
    reductions_data=reductions_data,
    rules=rules,  # ✨ AJOUTÉ
)
```

### apply_per_deduction_with_limit() - Utiliser tax_utils

**AVANT** (`core.py:160-191`):
```python
def apply_per_deduction_with_limit(
    per_contribution: float,
    professional_income: float,
    rules: TaxRules,
) -> tuple[float, float]:
    per_plafonds = rules.per_plafonds
    base_rate = per_plafonds.get("base_rate", 0.10)    # ❌ Fallback
    max_plafond = per_plafonds.get("max_salarie", 35194)  # ❌ Fallback

    plafond = professional_income * base_rate
    plafond = max(4399, min(plafond, max_plafond))     # ❌ HARDCODÉ 4399
    # ...
```

**APRÈS** (utiliser tax_utils):
```python
def apply_per_deduction_with_limit(
    per_contribution: float,
    professional_income: float,
    rules: TaxRules,
    status: str = "salarie",  # ✨ AJOUTÉ
) -> tuple[float, float]:
    from src.tax_engine.tax_utils import calculate_per_plafond  # ✨ IMPORT

    # ✨ UTILISE tax_utils - plus de valeurs hardcodées!
    plafond = calculate_per_plafond(professional_income, rules, status)

    # Determine deductible and excess
    if per_contribution <= plafond:
        return per_contribution, 0.0
    else:
        return plafond, per_contribution - plafond
```

---

## ✂️ PARTIE 5: SUPPRESSION DUPLICATIONS DANS STRATEGIES

### PER Strategy - Supprimer _calculate_plafond()

**AVANT** (`per_strategy.py:96-101`):
```python
def _calculate_plafond(self, revenu_prof: float) -> float:
    """Calculate PER plafond (10% of professional income)."""
    plafond = revenu_prof * self.rules["plafond_calculation"]["rate"]
    plafond = max(plafond, self.rules["plafond_calculation"]["min_plafond"])
    plafond = min(plafond, self.rules["plafond_calculation"]["max_plafond"])
    return plafond
```

**APRÈS** (supprimer méthode, utiliser tax_utils):
```python
# ❌ SUPPRIMER _calculate_plafond()

# Dans analyze():
def analyze(...):
    # ...

    # AVANT:
    # plafond = self._calculate_plafond(revenu_imposable)

    # APRÈS:
    from src.tax_engine.tax_utils import calculate_per_plafond

    plafond = calculate_per_plafond(
        revenu_imposable,
        self.tax_rules,
        status="salarie"  # ou détecter depuis profile
    )

    # ...
```

### Deductions Strategy - Utiliser tax_utils

**AVANT** (`deductions_strategy.py:64-74`):
```python
# Calculate plafond (20% of taxable income)
plafond = revenu_imposable * dons_rules["plafond_rate"]

# Get recommendation thresholds from JSON
min_income = dons_rules["min_income_for_recommendation"]
suggested_amount = dons_rules["suggested_amount"]

if current_dons < plafond and revenu_imposable > min_income:
    suggested_don = min(suggested_amount, (plafond - current_dons) * 0.3)
    reduction = suggested_don * dons_rules["reduction_rate"]
```

**APRÈS** (utiliser tax_utils):
```python
from src.tax_engine.tax_utils import (
    get_tax_reduction_plafond,
    calculate_tax_reduction
)

# Calculate plafond using centralized function
plafond = get_tax_reduction_plafond(
    "dons", self.tax_rules, revenu_imposable=revenu_imposable
)

# Get recommendation thresholds (keep in optimization_rules.json - meta-config)
min_income = dons_rules["min_income_for_recommendation"]
suggested_amount = dons_rules["suggested_amount"]

if current_dons < plafond and revenu_imposable > min_income:
    suggested_don = min(suggested_amount, (plafond - current_dons) * 0.3)

    # Calculate reduction using centralized function
    reduction, _ = calculate_tax_reduction(
        "dons", suggested_don, self.tax_rules, revenu_imposable=revenu_imposable
    )
```

### Regime Strategy - Utiliser tax_utils

**AVANT** (`regime_strategy.py:151-160`):
```python
if "bnc" in status:
    threshold = self.rules["regime_thresholds"]["micro_bnc"]["threshold"]
    threshold_name = "micro-BNC"
elif "bic" in status and "service" in status:
    threshold = self.rules["regime_thresholds"]["micro_bic_services"]["threshold"]
    threshold_name = "micro-BIC prestations"
elif "bic" in status:
    threshold = self.rules["regime_thresholds"]["micro_bic_ventes"]["threshold"]
    threshold_name = "micro-BIC ventes"
```

**APRÈS** (utiliser tax_utils):
```python
from src.tax_engine.tax_utils import check_micro_threshold_proximity

# Detect regime type
if "bnc" in status:
    regime_type = "bnc"
    threshold_name = "micro-BNC"
elif "bic" in status and "service" in status:
    regime_type = "bic_service"
    threshold_name = "micro-BIC prestations"
elif "bic" in status:
    regime_type = "bic_vente"
    threshold_name = "micro-BIC ventes"
else:
    return None

# Check proximity using centralized function
proximity_check = check_micro_threshold_proximity(
    revenue, regime_type, self.tax_rules, alert_threshold=proximity_alert
)

if not proximity_check["approaching"]:
    return None

threshold = proximity_check["threshold"]
remaining = proximity_check["remaining"]
```

### LMNP Strategy - Utiliser tax_utils

**AVANT** (`lmnp_strategy.py:84-94`):
```python
# Get LMNP réel parameters from rules
reel_rules = self.rules["regimes"]["reel"]
estimated_yield = reel_rules["estimated_yield"]
total_deduction_rate = reel_rules["avg_total_deduction_rate"]

# Estimate annual rental income
estimated_rental = investment_capacity * estimated_yield

# Estimate tax savings with LMNP réel
estimated_savings = estimated_rental * tmi * total_deduction_rate
```

**APRÈS** (utiliser tax_utils):
```python
from src.tax_engine.tax_utils import get_lmnp_deduction_rate, estimate_lmnp_yield

# Get LMNP parameters from centralized functions
estimated_yield = estimate_lmnp_yield(self.tax_rules)
total_deduction_rate = get_lmnp_deduction_rate("reel", self.tax_rules)

# Estimate annual rental income
estimated_rental = investment_capacity * estimated_yield

# Estimate tax savings with LMNP réel
estimated_savings = estimated_rental * tmi * total_deduction_rate
```

---

## ✂️ PARTIE 6: NETTOYER LES JSON DES ANALYZERS

### optimization_rules.json

**SUPPRIMER** (duplications avec baremes_2024.json):
```json
{
  // ❌ SUPPRIMER - maintenant dans baremes_2024.json
  "regime_thresholds": {
    "micro_bnc": {
      "threshold": 77700,
      "abattement": 0.34
    },
    // ...
  }
}
```

**GARDER** (meta-configuration spécifique aux recommandations):
```json
{
  "deductions": {
    "dons": {
      // ❌ SUPPRIMER rate et plafond_rate (dans baremes)
      // ✅ GARDER recommandation thresholds (logique business)
      "min_income_for_recommendation": 10000,
      "suggested_amount": 500,
      "description": "Dons aux associations"
    },
    "services_personne": {
      // ❌ SUPPRIMER rate et plafond (dans baremes)
      // ✅ GARDER thresholds
      "min_impot_for_recommendation": 500,
      "examples": [...]  // ✅ GARDER - info contextuelle
    },
    "frais_garde": {
      // ❌ SUPPRIMER rate et plafond_per_child (dans baremes)
      // ✅ Pas de thresholds spécifiques ici
    }
  },

  "regime_optimization": {
    // ✅ GARDER - logique de recommandation
    "min_delta_for_recommendation": 500,
    "threshold_proximity_alert": 0.85
  },

  "structure_thresholds": {
    // ✅ GARDER - pas dans baremes (logique business)
    "consider_sasu": {...},
    "consider_holding": {...}
  },

  "warnings": {
    // ✅ GARDER - messages généraux
    "general": [...]
  }
}
```

### per_rules.json

**SUPPRIMER**:
```json
{
  "plafond_calculation": {
    // ❌ SUPPRIMER - maintenant dans baremes_2024.json.per_plafonds
    "rate": 0.10,
    "min_plafond": 4399,
    "max_plafond": 35200
  }
}
```

**GARDER**:
```json
{
  "eligibility": {
    // ✅ GARDER - logique de recommandation
    "min_income": 1000
  },
  "tmi_thresholds": {
    // ✅ GARDER - seuils pour recommandations PER
    "0.11": {"min_interest": 500},
    "0.30": {"min_interest": 300},
    // ...
  },
  "recommendation_modes": {
    // ✅ GARDER - logique de recommandation
    "optimal": {"target_rate": 0.7}
  }
}
```

### lmnp_rules.json

**SUPPRIMER**:
```json
{
  "regimes": {
    "micro": {
      // ❌ SUPPRIMER threshold et abattement (dans baremes)
      "threshold": 77700,
      "abattement": 0.50
    },
    "reel": {
      // ❌ SUPPRIMER ou MIGRER vers baremes_2024.json.lmnp_market_estimates
      "avg_total_deduction_rate": 0.85,
      "estimated_yield": 0.04
    }
  }
}
```

**GARDER**:
```json
{
  "eligibility": {
    // ✅ GARDER - logique de recommandation LMNP
    "min_impot": 2000,
    "min_stable_income": true,
    "risk_tolerance": "medium"
  },
  "recommended_investment": {
    // ✅ GARDER - logique d'investissement
    "impot_multiplier_min": 3,
    "impot_multiplier_max": 5
  },
  // ✅ GARDER sources, warnings, advantages (contexte)
}
```

---

## 🧪 PARTIE 7: TESTS

### Tests pour tax_utils.py

```python
# tests/test_tax_utils.py

import pytest
from src.tax_engine.rules import get_tax_rules
from src.tax_engine.tax_utils import (
    calculate_per_plafond,
    get_tax_reduction_rate,
    get_tax_reduction_plafond,
    calculate_tax_reduction,
    get_micro_threshold,
    check_micro_threshold_proximity,
)


class TestPERPlafond:
    def test_calculate_per_plafond_basic(self):
        """Test basic PER plafond calculation."""
        rules = get_tax_rules(2024)
        plafond = calculate_per_plafond(50000, rules, "salarie")
        assert plafond == 5000.0  # 10% of 50k

    def test_calculate_per_plafond_min_limit(self):
        """Test PER plafond respects minimum."""
        rules = get_tax_rules(2024)
        plafond = calculate_per_plafond(10000, rules, "salarie")
        assert plafond == 4399.0  # Min plafond

    def test_calculate_per_plafond_max_limit(self):
        """Test PER plafond respects maximum."""
        rules = get_tax_rules(2024)
        plafond = calculate_per_plafond(500000, rules, "salarie")
        assert plafond == 35194.0  # Max for salarie


class TestTaxReductions:
    def test_get_tax_reduction_rate_dons(self):
        """Test getting reduction rate for dons."""
        rules = get_tax_rules(2024)
        rate = get_tax_reduction_rate("dons", rules)
        assert rate == 0.66

    def test_get_tax_reduction_plafond_dons(self):
        """Test plafond calculation for dons (percentage-based)."""
        rules = get_tax_rules(2024)
        plafond = get_tax_reduction_plafond("dons", rules, revenu_imposable=50000)
        assert plafond == 10000.0  # 20% of 50k

    def test_get_tax_reduction_plafond_services(self):
        """Test plafond for services (fixed)."""
        rules = get_tax_rules(2024)
        plafond = get_tax_reduction_plafond("services_personne", rules)
        assert plafond == 12000.0

    def test_calculate_tax_reduction_dons_within_plafond(self):
        """Test donation reduction within plafond."""
        rules = get_tax_rules(2024)
        reduction, excess = calculate_tax_reduction(
            "dons", 1000, rules, revenu_imposable=50000
        )
        assert reduction == 660.0  # 66% of 1000
        assert excess == 0.0

    def test_calculate_tax_reduction_dons_exceeds_plafond(self):
        """Test donation reduction exceeding plafond."""
        rules = get_tax_rules(2024)
        reduction, excess = calculate_tax_reduction(
            "dons", 15000, rules, revenu_imposable=50000
        )
        assert reduction == 6600.0  # 66% of 10k plafond
        assert excess == 5000.0  # 15k - 10k


class TestMicroRegime:
    def test_get_micro_threshold_bnc(self):
        """Test getting BNC threshold."""
        rules = get_tax_rules(2024)
        threshold = get_micro_threshold("bnc", rules)
        assert threshold == 77700

    def test_check_threshold_proximity_approaching(self):
        """Test proximity detection when approaching threshold."""
        rules = get_tax_rules(2024)
        result = check_micro_threshold_proximity(70000, "bnc", rules)
        assert result["approaching"] is True  # 70k is 90% of 77.7k
        assert result["threshold"] == 77700
        assert result["remaining"] == 7700.0

    def test_check_threshold_proximity_not_approaching(self):
        """Test proximity detection when far from threshold."""
        rules = get_tax_rules(2024)
        result = check_micro_threshold_proximity(50000, "bnc", rules)
        assert result["approaching"] is False  # 50k is 64% of 77.7k
```

### Tests de régression

**Important**: Tous les tests existants doivent continuer à passer!

```bash
# Vérifier qu'aucune régression
uv run pytest tests/ -v
```

---

## 📋 PARTIE 8: SÉQUENCE D'IMPLÉMENTATION

### Phase 1: Préparation (1h)

1. ✅ Créer branche `fix/eliminate-fiscal-duplication`
2. ✅ Créer `AUDIT_FISCAL_DUPLICATION.md`
3. ✅ Créer `REFACTORING_PLAN_TAX_UTILS.md`
4. 📝 **Résoudre divergence PER**: Vérifier source officielle pour 35194€ vs 35200€

### Phase 2: Enrichir baremes_2024.json (30min)

5. Ajouter section `tax_reductions`
6. Ajouter `min_plafond` à `per_plafonds`
7. Ajouter section `lmnp_market_estimates` (optionnel)
8. Commit: `feat(baremes): Add tax reductions and complete PER plafonds`

### Phase 3: Créer tax_utils.py (2h)

9. Créer `src/tax_engine/tax_utils.py`
10. Implémenter toutes les fonctions listées ci-dessus
11. Ajouter docstrings complètes
12. Commit: `feat(tax-engine): Create tax_utils.py with centralized fiscal functions`

### Phase 4: Modifier TaxRules (15min)

13. Ajouter propriétés `tax_reductions` et `lmnp_estimates`
14. Commit: `feat(tax-engine): Add tax_reductions and lmnp_estimates to TaxRules`

### Phase 5: Modifier core.py (1h)

15. Modifier `apply_tax_reductions()` pour utiliser tax_utils
16. Modifier `apply_per_deduction_with_limit()` pour utiliser tax_utils
17. Modifier signature de `compute_ir()` si nécessaire
18. Commit: `refactor(tax-engine): Use tax_utils in core.py, eliminate hardcoded values`

### Phase 6: Tests tax_utils (1h)

19. Créer `tests/test_tax_utils.py`
20. Implémenter tous les tests unitaires
21. Vérifier couverture ≥ 90%
22. Commit: `test(tax-engine): Add comprehensive tests for tax_utils`

### Phase 7: Modifier strategies (2h)

23. Modifier `per_strategy.py` - supprimer `_calculate_plafond()`
24. Modifier `deductions_strategy.py` - utiliser tax_utils
25. Modifier `regime_strategy.py` - utiliser tax_utils
26. Modifier `lmnp_strategy.py` - utiliser tax_utils
27. Commit: `refactor(analyzers): Use tax_utils in all strategies, eliminate duplication`

### Phase 8: Nettoyer JSON (30min)

28. Nettoyer `optimization_rules.json` - supprimer duplications
29. Nettoyer `per_rules.json` - supprimer plafond_calculation
30. Nettoyer `lmnp_rules.json` - migrer vers baremes si pertinent
31. Commit: `refactor(analyzers): Remove duplicated fiscal data from rules JSON`

### Phase 9: Tests de régression (1h)

32. Exécuter `pytest tests/ -v --tb=short`
33. Vérifier que TOUS les tests passent
34. Si échecs: corriger et re-tester
35. Vérifier couverture globale maintenue

### Phase 10: Validation finale (30min)

36. Exécuter tests manuels sur scénarios critiques
37. Vérifier cohérence baremes ↔ tax_utils ↔ strategies
38. Formater code: `uv run ruff format .`
39. Linter: `uv run ruff check . --fix`

### Phase 11: Documentation et PR (1h)

40. Mettre à jour README si nécessaire
41. Créer PR détaillé avec:
    - Lien vers AUDIT_FISCAL_DUPLICATION.md
    - Lien vers ce plan
    - Résumé des changements
    - Tests passing ✅
    - Before/After examples
42. Commit final et push

---

## ✅ CRITÈRES DE SUCCÈS

- [ ] ✅ Zéro valeur fiscale hardcodée dans `core.py`
- [ ] ✅ Zéro duplication de calcul fiscal entre tax_engine et analyzers
- [ ] ✅ Source unique: `baremes_2024.json` pour TOUTES les valeurs officielles
- [ ] ✅ Module `tax_utils.py` avec fonctions réutilisables bien documentées
- [ ] ✅ Tous les tests passent (153+ tests, 0 régression)
- [ ] ✅ Couverture ≥ 80% maintenue
- [ ] ✅ Divergence PER résolue (35194€ ou 35200€ - valeur officielle confirmée)
- [ ] ✅ JSON des analyzers nettoyés (seulement logique métier, pas de données fiscales)
- [ ] ✅ Documentation claire dans tax_utils.py (docstrings, exemples)
- [ ] ✅ Code formaté (ruff)
- [ ] ✅ Prêt pour Phase 5 LLM

---

## 🎯 IMPACT PHASE 5

Après ce refactoring:

✅ **LLM aura une source unique de vérité**
- Toutes les valeurs fiscales dans `baremes_2024.json`
- Fonctions utilitaires dans `tax_utils.py`
- Pas de confusion entre fichiers

✅ **Cohérence garantie**
- Recommandations = même source que calculs réels
- Impossible d'avoir valeurs divergentes

✅ **Maintenance simplifiée**
- Mise à jour 2025: modifier **1 seul fichier** (baremes_2025.json)
- Zéro risque d'oubli

✅ **Fiabilité maximale**
- Tests couvrant toutes les fonctions utilitaires
- Régression impossible (tests bloquent)

---

**Temps estimé total**: 10-12 heures
**Complexité**: Moyenne-Élevée
**Risque**: Faible (si tests passent, pas de régression)
**Priorité**: 🔴 CRITIQUE pour Phase 5
