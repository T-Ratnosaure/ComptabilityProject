"""Build LLM context from application data.

This module provides utilities to build clean, validated LLM context
from application models and data structures.
"""

from datetime import datetime

from src.models.comparison import ComparisonMicroReel
from src.models.fiscal_profile import FiscalProfile
from src.models.llm_context import LLMContext, TaxCalculationSummary
from src.models.optimization import OptimizationResult
from src.models.tax_document import TaxDocument
from src.security.llm_sanitizer import sanitize_for_llm
from src.services.validation import validate_fiscal_profile_coherence


class LLMContextBuilder:
    """Build clean LLM context from application models.

    This builder:
    1. Consolidates data from multiple sources
    2. Excludes technical fields (id, timestamps, file_path)
    3. Sanitizes all text content (remove PII, paths, etc.)
    4. Validates output with Pydantic models
    """

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
            profile_data: User profile dict (from API or DB)
            tax_result: Tax calculation result dict (from tax engine)
            optimization_result: Optimization results (optional)
            documents: List of tax documents (optional)

        Returns:
            LLMContext ready for Claude

        Example:
            >>> builder = LLMContextBuilder()
            >>> context = await builder.build_context(
            ...     profile_data={'status': 'micro_bnc', ...},
            ...     tax_result={'impot': {...}, 'socials': {...}},
            ...     optimization_result=OptimizationResult(...),
            ...     documents=[doc1, doc2]
            ... )
            >>> # context is ready to send to Claude
        """
        # Build fiscal profile
        profil = self._build_fiscal_profile(profile_data, documents or [])

        # Build tax calculation summary
        calcul_fiscal = self._build_tax_summary(tax_result)

        # Validate fiscal profile coherence and add warnings
        validation_warnings = validate_fiscal_profile_coherence(profil.model_dump())
        if validation_warnings:
            # Add validation warnings to existing warnings
            calcul_fiscal.warnings.extend(validation_warnings)

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

    def _build_fiscal_profile(
        self, profile_data: dict, documents: list[TaxDocument]
    ) -> FiscalProfile:
        """Build FiscalProfile from profile data and documents.

        This method:
        1. Extracts fiscal data from profile_data
        2. Enriches with data from documents (RFR, situation_familiale, etc.)
        3. Maps field names to canonical form
        4. Returns validated FiscalProfile

        Args:
            profile_data: Profile dict (from API request or DB)
            documents: List of processed documents

        Returns:
            Validated FiscalProfile
        """
        # Extract data from Avis d'Imposition if available
        rfr = None
        impot_precedent = None
        situation_familiale = profile_data.get("situation_familiale", "celibataire")

        for doc in documents:
            if doc.type.value == "avis_imposition" and doc.extracted_fields:
                rfr = doc.extracted_fields.get("revenu_fiscal_reference")
                impot_precedent = doc.extracted_fields.get("impot_revenu")
                # Override with extracted value if available
                if "situation_familiale" in doc.extracted_fields:
                    situation_familiale = doc.extracted_fields["situation_familiale"]

        # Map profile_data fields to FiscalProfile
        # Use standardized French fiscal terms (chiffre_affaires, etc.)
        # with fallback to legacy English names for backward compatibility
        chiffre_affaires = (
            profile_data.get("chiffre_affaires")  # Standard (French fiscal term)
            or profile_data.get("annual_revenue")  # Legacy fallback
            or profile_data.get("professional_gross")  # Legacy fallback
            or 0.0
        )

        charges_deductibles = (
            profile_data.get("charges_deductibles")  # Standard (French fiscal term)
            or profile_data.get("annual_expenses")  # Legacy fallback
            or profile_data.get("deductible_expenses")  # Legacy fallback
            or 0.0
        )

        cotisations_sociales = (
            profile_data.get("cotisations_sociales")  # Standard (French fiscal term)
            or profile_data.get("social_contributions")  # Legacy fallback
            or 0.0
        )

        # Calculate benefice_net if not provided
        # benefice_net = chiffre_affaires - charges_deductibles
        benefice_net = profile_data.get("benefice_net")
        if benefice_net is None:
            # Auto-calculate from revenue and expenses
            benefice_net = chiffre_affaires - charges_deductibles

        # Extract additional fields from documents
        taux_prelevement = None
        for doc in documents:
            if (
                doc.type.value == "avis_imposition"
                and doc.extracted_fields
                and "taux_prelevement" in doc.extracted_fields
            ):
                taux_prelevement = doc.extracted_fields["taux_prelevement"]

        # Build charges_detail if available
        charges_detail = None
        if profile_data.get("charges_detail"):
            charges_detail = profile_data["charges_detail"]
        # Can also extract from BNC/BIC documents
        for doc in documents:
            if doc.type.value in ["bnc", "bic"] and doc.extracted_fields:
                if charges_detail is None:
                    charges_detail = {}
                # Build from extracted BNC/BIC fields
                if "amortissements" in doc.extracted_fields:
                    charges_detail["amortissements"] = doc.extracted_fields[
                        "amortissements"
                    ]
                if "loyer" in doc.extracted_fields:
                    charges_detail["loyer"] = doc.extracted_fields["loyer"]
                if "honoraires" in doc.extracted_fields:
                    charges_detail["honoraires"] = doc.extracted_fields["honoraires"]
                if "autres_charges" in doc.extracted_fields:
                    charges_detail["autres"] = doc.extracted_fields["autres_charges"]

        # Build FiscalProfile
        return FiscalProfile(
            annee_fiscale=profile_data.get("tax_year", datetime.now().year),
            situation_familiale=situation_familiale,
            nombre_parts=profile_data.get("nb_parts", 1.0),
            enfants_a_charge=profile_data.get("enfants_a_charge", 0),
            enfants_moins_6_ans=profile_data.get("children_under_6", 0),
            regime_fiscal=profile_data.get("status", "micro_bnc"),
            type_activite=profile_data.get("activity_type", "BNC"),
            chiffre_affaires=chiffre_affaires,
            charges_deductibles=charges_deductibles,
            benefice_net=benefice_net,
            charges_detail=charges_detail,
            cotisations_sociales=cotisations_sociales,
            salaires=profile_data.get("salary", 0.0),
            revenus_fonciers=profile_data.get("rental_income", 0.0),
            revenus_capitaux=profile_data.get("capital_income", 0.0),
            plus_values=profile_data.get("plus_values", 0.0),
            per_contributions=profile_data.get("per_contributed", 0.0),
            dons_declares=profile_data.get("dons_declared", 0.0),
            services_personne=profile_data.get("services_personne_declared", 0.0),
            frais_garde=profile_data.get("frais_garde_declared", 0.0),
            pension_alimentaire=profile_data.get("alimony", 0.0),
            revenu_fiscal_reference=rfr,
            impot_annee_precedente=impot_precedent,
            taux_prelevement_source=taux_prelevement,
            revenus_stables=profile_data.get("stable_income", False),
            strategie_patrimoniale=profile_data.get("patrimony_strategy", False),
            capacite_investissement=profile_data.get("investment_capacity", 0.0),
            tolerance_risque=profile_data.get("risk_tolerance", "moderate"),
        )

    def _build_tax_summary(self, tax_result: dict) -> TaxCalculationSummary:
        """Build TaxCalculationSummary from tax engine result.

        Args:
            tax_result: Tax calculation result dict from tax engine

        Returns:
            Validated TaxCalculationSummary
        """
        impot = tax_result.get("impot", {})
        socials = tax_result.get("socials", {})

        # Extract structured comparison (if available)
        comparaison_micro_reel = None
        comparisons_data = tax_result.get("comparisons", {})
        if comparisons_data and "micro_vs_reel" in comparisons_data:
            comparison_dict = comparisons_data["micro_vs_reel"]
            # Validate and convert to ComparisonMicroReel model
            try:
                comparaison_micro_reel = ComparisonMicroReel(**comparison_dict)
            except Exception:
                # If validation fails, leave as None
                # (backward compatibility with old dict format)
                comparaison_micro_reel = None

        # Calculate taux_effectif if not provided
        taux_effectif = impot.get("taux_effectif", 0.0)
        if taux_effectif == 0.0 and impot.get("revenu_imposable", 0.0) > 0:
            # Calculate: (impot_net + cotisations) / revenu_imposable
            charge_totale = impot.get("impot_net", 0.0) + socials.get(
                "urssaf_expected", 0.0
            )
            taux_effectif = charge_totale / impot["revenu_imposable"]

        return TaxCalculationSummary(
            impot_brut=impot.get("impot_brut", 0.0),
            impot_net=impot.get("impot_net", 0.0),
            cotisations_sociales=socials.get("urssaf_expected", 0.0),
            charge_fiscale_totale=impot.get("impot_net", 0.0)
            + socials.get("urssaf_expected", 0.0),
            tmi=impot.get("tmi", 0.0),
            taux_effectif=taux_effectif,
            revenu_imposable=impot.get("revenu_imposable", 0.0),
            quotient_familial=impot.get("part_income", 0.0),
            reductions_fiscales=impot.get("tax_reductions", {}),
            per_plafond_detail=impot.get("per_plafond_detail"),
            tranches_detail=impot.get("tranches_detail"),
            cotisations_detail=None,  # TODO: Add when detailed breakdown available
            comparaison_micro_reel=comparaison_micro_reel,
            warnings=tax_result.get("warnings", []),
        )

    def _build_sanitized_document_extracts(
        self, documents: list[TaxDocument]
    ) -> dict[str, dict]:
        """
        Build sanitized document extracts for LLM context.

        SECURITY: This method EXCLUDES:
        - file_path (prevents system path leakage)
        - id, created_at, updated_at (technical noise)
        - raw_text (too large, use extracted_fields instead)
        - error_message (internal debugging)
        - original_filename (may contain PII)

        INCLUDES:
        - type, year (metadata)
        - extracted_fields (sanitized for PII)

        Args:
            documents: List of TaxDocument models

        Returns:
            Dict mapping document keys to sanitized extracts
        """
        extracts = {}

        for doc in documents:
            # Create unique key for this document
            doc_key = f"{doc.type.value}_{doc.year}"

            # Sanitize extracted_fields (remove PII, technical data)
            sanitized_fields = {}
            for key, value in doc.extracted_fields.items():
                # Skip technical fields
                if key in [
                    "file_path",
                    "original_filename",
                    "raw_text",
                    "id",
                    "created_at",
                    "updated_at",
                ]:
                    continue

                # Sanitize string values for PII
                if isinstance(value, str):
                    value = sanitize_for_llm(value)

                sanitized_fields[key] = value

            # Build clean extract
            extracts[doc_key] = {
                "type": doc.type.value,
                "year": doc.year,
                "fields": sanitized_fields,
            }

        return extracts
