"""Tests for TaxDataMapper - centralized field mapping."""

from datetime import datetime

from src.api.routes.tax import TaxRegime
from src.models.tax_document import DocumentType, TaxDocument
from src.services.data_mapper import TaxDataMapper


class TestTaxDataMapper:
    """Test suite for TaxDataMapper."""

    def test_consolidate_single_document(self):
        """Test consolidation from a single document."""
        doc = TaxDocument(
            id=1,
            type=DocumentType.AVIS_IMPOSITION,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "nombre_parts": 1.0,
                "revenu_fiscal_reference": 45000.0,
                "impot_revenu": 3200.0,
            },
        )

        consolidated = TaxDataMapper.consolidate_extracted_fields([doc])

        assert consolidated["nombre_parts"] == 1.0
        assert consolidated["revenu_fiscal_reference"] == 45000.0
        assert consolidated["impot_revenu"] == 3200.0

    def test_consolidate_multiple_documents(self):
        """Test consolidation from multiple documents."""
        avis = TaxDocument(
            id=1,
            type=DocumentType.AVIS_IMPOSITION,
            year=2024,
            status="processed",
            file_path="/tmp/avis.pdf",
            original_filename="avis.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "nombre_parts": 1.0,
                "revenu_fiscal_reference": 45000.0,
            },
        )
        urssaf = TaxDocument(
            id=2,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/urssaf.pdf",
            original_filename="urssaf.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "chiffre_affaires": 50000.0,
                "cotisations_sociales": 10900.0,
            },
        )

        consolidated = TaxDataMapper.consolidate_extracted_fields([avis, urssaf])

        # Should have fields from both documents
        assert consolidated["nombre_parts"] == 1.0
        assert consolidated["revenu_fiscal_reference"] == 45000.0
        assert consolidated["chiffre_affaires"] == 50000.0
        assert consolidated["cotisations_sociales"] == 10900.0

    def test_field_aliases(self):
        """Test that field aliases are correctly applied."""
        doc = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "recettes": 50000.0,  # Alias for chiffre_affaires
                "nb_parts": 1.0,  # Alias for nombre_parts
            },
        )

        consolidated = TaxDataMapper.consolidate_extracted_fields([doc])

        # Should be mapped to canonical names
        assert consolidated["chiffre_affaires"] == 50000.0
        assert consolidated["nombre_parts"] == 1.0

    def test_map_to_tax_request_basic(self):
        """Test basic mapping to TaxCalculationRequest."""
        urssaf = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/urssaf.pdf",
            original_filename="urssaf.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "chiffre_affaires": 50000.0,
                "cotisations_sociales": 10900.0,
                "regime": "micro_bnc",
                "nombre_parts": 1.0,
            },
        )

        request = TaxDataMapper.map_to_tax_request([urssaf])

        assert request.tax_year == 2024
        assert request.person.nb_parts == 1.0
        assert request.person.status == TaxRegime.MICRO_BNC
        assert request.income.professional_gross == 50000.0
        assert request.social.urssaf_paid == 10900.0
        assert request.social.urssaf_declared_ca == 50000.0

    def test_map_to_tax_request_multiple_documents(self):
        """Test mapping from multiple documents."""
        avis = TaxDocument(
            id=1,
            type=DocumentType.AVIS_IMPOSITION,
            year=2024,
            status="processed",
            file_path="/tmp/avis.pdf",
            original_filename="avis.pdf",
            created_at=datetime.now(),
            extracted_fields={"nombre_parts": 1.0},
        )
        urssaf = TaxDocument(
            id=2,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/urssaf.pdf",
            original_filename="urssaf.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "chiffre_affaires": 50000.0,
                "cotisations_sociales": 10900.0,
            },
        )
        bnc = TaxDocument(
            id=3,
            type=DocumentType.BNC,
            year=2024,
            status="processed",
            file_path="/tmp/bnc.pdf",
            original_filename="bnc.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "charges": 10000.0,
                "regime": "reel_bnc",
            },
        )

        request = TaxDataMapper.map_to_tax_request([avis, urssaf, bnc])

        assert request.person.nb_parts == 1.0
        assert request.person.status == TaxRegime.REEL_BNC
        assert request.income.professional_gross == 50000.0
        assert request.income.deductible_expenses == 10000.0
        assert request.social.urssaf_paid == 10900.0

    def test_map_to_tax_request_with_overrides(self):
        """Test that user overrides take precedence."""
        doc = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "chiffre_affaires": 50000.0,
                "nombre_parts": 1.0,
            },
        )

        overrides = {
            "nombre_parts": 2.0,  # Override extracted value
            "regime": "reel_bnc",
        }

        request = TaxDataMapper.map_to_tax_request([doc], overrides)

        assert request.person.nb_parts == 2.0  # Override applied
        assert request.person.status == TaxRegime.REEL_BNC  # Override applied
        assert request.income.professional_gross == 50000.0  # Not overridden

    def test_map_declaration_2042_fields(self):
        """Test mapping of Declaration 2042 specific fields."""
        declaration = TaxDocument(
            id=1,
            type=DocumentType.DECLARATION_2042,
            year=2024,
            status="processed",
            file_path="/tmp/2042.pdf",
            original_filename="2042.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "salaires_declarant1": 20000.0,
                "salaires_declarant2": 15000.0,
                "revenus_fonciers": 5000.0,
                "revenus_capitaux": 1000.0,
                "autres_deductions": 2000.0,  # Tax deductions (not BNC expenses)
            },
        )

        request = TaxDataMapper.map_to_tax_request([declaration])

        # Salaries should be summed
        assert request.income.salary == 35000.0  # 20000 + 15000
        assert request.income.rental_income == 5000.0
        assert request.income.capital_income == 1000.0
        assert request.deductions.other_deductions == 2000.0

    def test_map_pensions_combined_with_salaries(self):
        """Test that pensions are combined with salaries."""
        declaration = TaxDocument(
            id=1,
            type=DocumentType.DECLARATION_2042,
            year=2024,
            status="processed",
            file_path="/tmp/2042.pdf",
            original_filename="2042.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "salaires_declarant1": 10000.0,
                "pensions_declarant1": 5000.0,
                "pensions_declarant2": 3000.0,
            },
        )

        request = TaxDataMapper.map_to_tax_request([declaration])

        # Salaries and pensions combined: 10000 + 5000 + 3000
        assert request.income.salary == 18000.0

    def test_extract_profile_data(self):
        """Test profile data extraction for optimization."""
        documents = [
            TaxDocument(
                id=1,
                type=DocumentType.URSSAF,
                year=2024,
                status="processed",
                file_path="/tmp/urssaf.pdf",
                original_filename="urssaf.pdf",
                created_at=datetime.now(),
                extracted_fields={
                    "chiffre_affaires": 50000.0,
                    "cotisations_sociales": 10900.0,
                    "regime": "micro_bnc",
                    "nombre_parts": 1.0,
                },
            ),
            TaxDocument(
                id=2,
                type=DocumentType.AVIS_IMPOSITION,
                year=2024,
                status="processed",
                file_path="/tmp/avis.pdf",
                original_filename="avis.pdf",
                created_at=datetime.now(),
                extracted_fields={
                    "revenu_fiscal_reference": 45000.0,
                    "situation_familiale": "celibataire",
                },
            ),
        ]

        profile = TaxDataMapper.extract_profile_data(documents)

        assert profile["status"] == "micro_bnc"
        assert profile["chiffre_affaires"] == 50000.0
        assert profile["nb_parts"] == 1.0
        assert profile["activity_type"] == "BNC"
        assert profile["cotisations_sociales"] == 10900.0
        assert profile["situation_familiale"] == "celibataire"
        assert profile["revenu_fiscal_reference"] == 45000.0

    def test_infer_activity_type_bnc(self):
        """Test activity type inference for BNC."""
        assert TaxDataMapper._infer_activity_type("micro_bnc") == "BNC"
        assert TaxDataMapper._infer_activity_type("reel_bnc") == "BNC"

    def test_infer_activity_type_bic(self):
        """Test activity type inference for BIC."""
        assert TaxDataMapper._infer_activity_type("micro_bic") == "BIC"
        assert TaxDataMapper._infer_activity_type("reel_bic") == "BIC"
        assert TaxDataMapper._infer_activity_type("micro_bic_service") == "BIC"

    def test_infer_activity_type_fallback(self):
        """Test activity type inference fallback."""
        assert TaxDataMapper._infer_activity_type("unknown") == "BNC"

    def test_get_missing_fields_empty(self):
        """Test missing fields detection when all present."""
        doc = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "chiffre_affaires": 50000.0,
                "nombre_parts": 1.0,
                "cotisations_sociales": 10900.0,
            },
        )

        missing = TaxDataMapper.get_missing_fields([doc])

        assert missing == []  # All critical fields present

    def test_get_missing_fields_some_missing(self):
        """Test missing fields detection when some are missing."""
        doc = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "chiffre_affaires": 50000.0,
                # Missing: nombre_parts, cotisations_sociales
            },
        )

        missing = TaxDataMapper.get_missing_fields([doc])

        assert "nombre_parts" in missing
        assert "cotisations_sociales" in missing
        assert "chiffre_affaires" not in missing

    def test_default_values_when_fields_missing(self):
        """Test that default values are used when fields are missing."""
        # Empty document
        doc = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={},
        )

        request = TaxDataMapper.map_to_tax_request([doc])

        # Should use defaults
        assert request.person.nb_parts == 1.0
        assert request.income.professional_gross == 0.0
        assert request.income.salary == 0.0
        assert request.income.rental_income == 0.0
        assert request.social.urssaf_paid == 0.0

    def test_regime_fallback_to_micro_bnc(self):
        """Test that invalid regimes fallback to micro_bnc."""
        doc = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "regime": "invalid_regime",  # Invalid
            },
        )

        request = TaxDataMapper.map_to_tax_request([doc])

        assert request.person.status == TaxRegime.MICRO_BNC  # Fallback


class TestDataMapperIntegration:
    """Integration tests for full mapping workflow."""

    def test_full_workflow_freelancer(self):
        """Test complete workflow for a typical freelancer."""
        # Simulate a freelancer with URSSAF + BNC + Avis d'Imposition
        avis = TaxDocument(
            id=1,
            type=DocumentType.AVIS_IMPOSITION,
            year=2023,
            status="processed",
            file_path="/tmp/avis.pdf",
            original_filename="avis.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "revenu_fiscal_reference": 40000.0,
                "impot_revenu": 2800.0,
                "nombre_parts": 1.0,
                "situation_familiale": "celibataire",
            },
        )

        urssaf = TaxDocument(
            id=2,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/urssaf.pdf",
            original_filename="urssaf.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "chiffre_affaires": 55000.0,
                "cotisations_sociales": 12000.0,
            },
        )

        bnc = TaxDocument(
            id=3,
            type=DocumentType.BNC,
            year=2024,
            status="processed",
            file_path="/tmp/bnc.pdf",
            original_filename="bnc.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "recettes": 55000.0,
                "charges": 8000.0,
                "benefice": 47000.0,
                "regime": "reel_bnc",
            },
        )

        documents = [avis, urssaf, bnc]

        # Map to tax request
        request = TaxDataMapper.map_to_tax_request(documents)

        assert request.tax_year == 2024
        assert request.person.nb_parts == 1.0
        assert request.person.status == TaxRegime.REEL_BNC
        assert request.income.professional_gross == 55000.0
        assert request.income.deductible_expenses == 8000.0
        assert request.social.urssaf_paid == 12000.0

        # Extract profile
        profile = TaxDataMapper.extract_profile_data(documents)

        assert profile["chiffre_affaires"] == 55000.0
        assert profile["charges_deductibles"] == 8000.0
        assert profile["cotisations_sociales"] == 12000.0
        assert profile["revenu_fiscal_reference"] == 40000.0
        assert profile["situation_familiale"] == "celibataire"

    def test_year_from_documents(self):
        """Test that year is correctly extracted from documents."""
        doc = TaxDocument(
            id=1,
            type=DocumentType.URSSAF,
            year=2024,
            status="processed",
            file_path="/tmp/test.pdf",
            original_filename="test.pdf",
            created_at=datetime.now(),
            extracted_fields={
                "year": 2025,  # Explicit year in extracted fields
            },
        )

        request = TaxDataMapper.map_to_tax_request([doc])

        assert request.tax_year == 2025  # Should use explicit year
