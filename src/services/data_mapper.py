"""Centralized data mapping between phases.

This module provides utilities to map extracted document fields
to tax calculation requests, ensuring consistent field mapping
and reducing code duplication.
"""

from src.api.routes.tax import (
    DeductionsData,
    IncomeData,
    PersonData,
    SocialData,
    TaxCalculationRequest,
    TaxRegime,
)
from src.models.tax_document import TaxDocument


class TaxDataMapper:
    """Map extracted fields to tax engine inputs."""

    # Map document extraction field names to canonical names
    FIELD_ALIASES = {
        # Revenue fields
        "recettes": "chiffre_affaires",
        "professional_gross": "chiffre_affaires",
        "annual_revenue": "chiffre_affaires",
        # Expense fields
        "deductible_expenses": "charges_deductibles",
        "annual_expenses": "charges_deductibles",
        # Social contribution fields
        "social_contributions": "cotisations_sociales",
        "urssaf_paid": "cotisations_sociales",
        # Parts fields
        "nb_parts": "nombre_parts",
        # Salary fields
        "salary": "salaires_declarant1",
    }

    @staticmethod
    def consolidate_extracted_fields(
        documents: list[TaxDocument],
    ) -> dict[str, float | str | int]:
        """
        Consolidate extracted_fields from multiple documents.

        Args:
            documents: List of processed tax documents

        Returns:
            Consolidated dict with canonical field names

        Example:
            >>> avis = TaxDocument(
            ...     type=AVIS, extracted_fields={"nombre_parts": 1.0}
            ... )
            >>> urssaf = TaxDocument(
            ...     type=URSSAF,
            ...     extracted_fields={"chiffre_affaires": 50000.0}
            ... )
            >>> consolidated = TaxDataMapper.consolidate_extracted_fields(
            ...     [avis, urssaf]
            ... )
            >>> consolidated["nombre_parts"]  # 1.0
            >>> consolidated["chiffre_affaires"]  # 50000.0
        """
        consolidated: dict[str, float | str | int] = {}

        for doc in documents:
            if not doc.extracted_fields:
                continue

            # Copy all fields
            for key, value in doc.extracted_fields.items():
                # Apply aliases if exists
                canonical_key = TaxDataMapper.FIELD_ALIASES.get(key, key)
                consolidated[canonical_key] = value

        return consolidated

    @staticmethod
    def map_to_tax_request(
        documents: list[TaxDocument],
        user_overrides: dict | None = None,
    ) -> TaxCalculationRequest:
        """
        Build TaxCalculationRequest from extracted documents.

        This is the centralized mapping function that ensures consistency
        between document extraction (Phase 2) and tax calculation (Phase 3).

        Args:
            documents: List of processed tax documents
            user_overrides: User-provided values that override extracted data

        Returns:
            Validated TaxCalculationRequest

        Raises:
            ValueError: If required fields are missing

        Example:
            >>> documents = [avis_doc, urssaf_doc, bnc_doc]
            >>> overrides = {"regime": "reel_bnc"}
            >>> request = TaxDataMapper.map_to_tax_request(documents, overrides)
            >>> # Request is ready for tax engine
        """
        # Consolidate all extracted_fields
        consolidated = TaxDataMapper.consolidate_extracted_fields(documents)

        # Apply user overrides (higher priority)
        if user_overrides:
            consolidated.update(user_overrides)

        # Extract and validate regime
        regime = consolidated.get("regime", "micro_bnc")
        if isinstance(regime, str):
            try:
                regime_enum = TaxRegime(regime.lower())
            except ValueError:
                # Fallback to micro_bnc if invalid
                regime_enum = TaxRegime.MICRO_BNC
        else:
            regime_enum = TaxRegime.MICRO_BNC

        # Build PersonData
        person = PersonData(
            name="ANON",  # Anonymized
            nb_parts=float(consolidated.get("nombre_parts", 1.0)),
            status=regime_enum,
        )

        # Build IncomeData
        # Sum salaries from both declarants
        salary_1 = float(consolidated.get("salaires_declarant1", 0.0))
        salary_2 = float(consolidated.get("salaires_declarant2", 0.0))
        total_salary = salary_1 + salary_2

        # Sum pensions from both declarants
        pension_1 = float(consolidated.get("pensions_declarant1", 0.0))
        pension_2 = float(consolidated.get("pensions_declarant2", 0.0))
        total_pensions = pension_1 + pension_2

        income = IncomeData(
            professional_gross=float(consolidated.get("chiffre_affaires", 0.0)),
            salary=total_salary + total_pensions,  # Combine salary and pensions
            rental_income=float(consolidated.get("revenus_fonciers", 0.0)),
            capital_income=float(consolidated.get("revenus_capitaux", 0.0)),
            deductible_expenses=float(consolidated.get("charges_deductibles", 0.0)),
        )

        # Build DeductionsData
        deductions = DeductionsData(
            per_contributions=float(consolidated.get("per_contributions", 0.0)),
            alimony=float(consolidated.get("pension_alimentaire", 0.0)),
            other_deductions=float(consolidated.get("autres_deductions", 0.0)),
        )

        # Build SocialData
        social = SocialData(
            urssaf_declared_ca=float(consolidated.get("chiffre_affaires", 0.0)),
            urssaf_paid=float(consolidated.get("cotisations_sociales", 0.0)),
        )

        # Build TaxCalculationRequest
        tax_year = int(consolidated.get("year", 2024))

        return TaxCalculationRequest(
            tax_year=tax_year,
            person=person,
            income=income,
            deductions=deductions,
            social=social,
            pas_withheld=float(consolidated.get("pas_withheld", 0.0)),
        )

    @staticmethod
    def extract_profile_data(documents: list[TaxDocument]) -> dict:
        """
        Extract profile data for optimization engine.

        Args:
            documents: List of processed tax documents

        Returns:
            Profile dict ready for optimization engine

        Example:
            >>> profile = TaxDataMapper.extract_profile_data(documents)
            >>> profile["chiffre_affaires"]  # 50000.0
            >>> profile["nb_parts"]  # 1.0
        """
        consolidated = TaxDataMapper.consolidate_extracted_fields(documents)

        # Map to profile format (used by optimization engine)
        regime = str(consolidated.get("regime", "micro_bnc"))

        return {
            "status": regime,
            "chiffre_affaires": consolidated.get("chiffre_affaires", 0.0),
            "charges_deductibles": consolidated.get("charges_deductibles", 0.0),
            "nb_parts": consolidated.get("nombre_parts", 1.0),
            "activity_type": TaxDataMapper._infer_activity_type(regime),
            "cotisations_sociales": consolidated.get("cotisations_sociales", 0.0),
            "situation_familiale": consolidated.get(
                "situation_familiale", "celibataire"
            ),
            "revenus_fonciers": consolidated.get("revenus_fonciers", 0.0),
            "revenus_capitaux": consolidated.get("revenus_capitaux", 0.0),
            "revenu_fiscal_reference": consolidated.get("revenu_fiscal_reference"),
            "impot_annee_precedente": consolidated.get("impot_revenu"),
        }

    @staticmethod
    def _infer_activity_type(regime: str) -> str:
        """
        Infer activity type from regime.

        Args:
            regime: Tax regime (micro_bnc, micro_bic, etc.)

        Returns:
            Activity type: "BNC" or "BIC"
        """
        if "bnc" in regime.lower():
            return "BNC"
        elif "bic" in regime.lower():
            return "BIC"
        else:
            return "BNC"  # Default fallback

    @staticmethod
    def get_missing_fields(documents: list[TaxDocument]) -> list[str]:
        """
        Identify critical fields missing from extracted documents.

        Args:
            documents: List of processed tax documents

        Returns:
            List of missing critical field names

        Example:
            >>> missing = TaxDataMapper.get_missing_fields(documents)
            >>> if missing:
            ...     print(f"Missing fields: {missing}")
        """
        consolidated = TaxDataMapper.consolidate_extracted_fields(documents)

        critical_fields = [
            "chiffre_affaires",
            "nombre_parts",
            "cotisations_sociales",
        ]

        missing = []
        for field in critical_fields:
            if field not in consolidated or consolidated[field] is None:
                missing.append(field)

        return missing
