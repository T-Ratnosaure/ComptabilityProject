"""Quick test runner without pytest for validation."""

import sys
from datetime import datetime

from src.api.routes.tax import TaxRegime
from src.models.tax_document import DocumentType, TaxDocument
from src.services.data_mapper import TaxDataMapper


def test_consolidate_single_document():
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
    print("[OK] test_consolidate_single_document PASSED")


def test_map_to_tax_request_basic():
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
    print("[OK] test_map_to_tax_request_basic PASSED")


def test_field_aliases():
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
    print("[OK] test_field_aliases PASSED")


def main():
    """Run quick tests."""
    print("\n>>> Running quick validation tests...\n")

    try:
        test_consolidate_single_document()
        test_map_to_tax_request_basic()
        test_field_aliases()

        print("\n>>> All quick tests PASSED!\n")
        return 0
    except Exception as e:
        print(f"\n>>> Test FAILED: {e}\n")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
