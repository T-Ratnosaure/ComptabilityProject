"""Tax rules loader - barèmes, abattements, URSSAF rates, PER plafonds."""

import json
from pathlib import Path
from typing import Any


class TaxRules:
    """Load and provide access to versioned French tax rules."""

    def __init__(self, year: int):
        """Initialize tax rules for a specific year.

        Args:
            year: Tax year (e.g., 2024, 2025)

        Raises:
            FileNotFoundError: If barème file for year doesn't exist
            ValueError: If barème file is invalid
        """
        self.year = year
        self.data = self._load_bareme(year)

    def _load_bareme(self, year: int) -> dict[str, Any]:
        """Load barème from JSON file.

        Args:
            year: Tax year

        Returns:
            Dictionary with all tax rules for the year

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid
        """
        bareme_path = Path(__file__).parent / "data" / f"baremes_{year}.json"

        if not bareme_path.exists():
            raise FileNotFoundError(
                f"Barème file not found for year {year}: {bareme_path}"
            )

        with open(bareme_path, encoding="utf-8") as f:
            data = json.load(f)

        # Validate structure
        required_keys = ["year", "income_tax_brackets", "abattements"]
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Invalid barème file: missing '{key}'")

        return data

    @property
    def income_tax_brackets(self) -> list[dict[str, Any]]:
        """Get income tax brackets (tranches).

        Returns:
            List of brackets with rate, lower_bound, upper_bound
        """
        return self.data["income_tax_brackets"]

    @property
    def abattements(self) -> dict[str, float]:
        """Get micro-régime abattements.

        Returns:
            Dict mapping regime type to abattement rate (0.34 = 34%)
        """
        return self.data["abattements"]

    @property
    def urssaf_rates(self) -> dict[str, float]:
        """Get URSSAF contribution rates.

        Returns:
            Dict mapping activity type to rate
        """
        return self.data.get("urssaf_rates", {})

    @property
    def per_plafonds(self) -> dict[str, Any]:
        """Get PER deduction limits.

        Returns:
            Dict with base_rate, max amounts by status
        """
        return self.data.get("per_plafonds", {})

    @property
    def plafonds_micro(self) -> dict[str, int]:
        """Get micro-régime CA thresholds.

        Returns:
            Dict with thresholds for BNC, BIC service, BIC vente
        """
        return self.data.get("plafonds_micro", {})

    @property
    def quotient_familial(self) -> dict[str, Any]:
        """Get quotient familial rules.

        Returns:
            Dict with parts by situation and plafonnement rules
        """
        return self.data.get("quotient_familial", {})

    @property
    def tax_reductions(self) -> dict[str, dict[str, Any]]:
        """Get tax reductions and credits configuration.

        Returns:
            Dict with dons, services_personne, frais_garde config
        """
        return self.data.get("tax_reductions", {})

    @property
    def lmnp(self) -> dict[str, Any]:
        """Get LMNP (Location Meublée Non Professionnelle) configuration.

        Returns:
            Dict with regimes, market_estimates, eligibility criteria
        """
        return self.data.get("lmnp", {})

    @property
    def source_url(self) -> str:
        """Get official source URL.

        Returns:
            URL of official tax authority page
        """
        return self.data.get("source", "")

    @property
    def source_date(self) -> str:
        """Get source publication date.

        Returns:
            Date string (YYYY-MM-DD)
        """
        return self.data.get("source_date", "")

    def get_abattement(self, regime: str) -> float:
        """Get abattement rate for a specific regime.

        Args:
            regime: Regime type (micro_bnc, micro_bic_service, etc.)

        Returns:
            Abattement rate (0.0 to 1.0)

        Raises:
            KeyError: If regime not found
        """
        regime_key = regime.lower().replace("-", "_")
        if regime_key not in self.abattements:
            raise KeyError(f"Unknown regime: {regime}")
        return self.abattements[regime_key]

    def get_urssaf_rate(self, activity: str) -> float:
        """Get URSSAF rate for activity type.

        Args:
            activity: Activity type (liberal_bnc, commercial_bic, etc.)

        Returns:
            URSSAF contribution rate (0.0 to 1.0)

        Raises:
            KeyError: If activity not found
        """
        activity_key = activity.lower().replace("-", "_")
        if activity_key not in self.urssaf_rates:
            raise KeyError(f"Unknown activity: {activity}")
        return self.urssaf_rates[activity_key]


# Singleton cache for loaded rules by year
_rules_cache: dict[int, TaxRules] = {}


def get_tax_rules(year: int) -> TaxRules:
    """Get tax rules for a year (cached).

    Args:
        year: Tax year

    Returns:
        TaxRules instance for the year
    """
    if year not in _rules_cache:
        _rules_cache[year] = TaxRules(year)
    return _rules_cache[year]
