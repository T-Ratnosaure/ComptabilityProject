"""Tests for document extractors and parsers."""

import pytest

from src.extractors.field_parsers.avis_imposition import AvisImpositionParser
from src.extractors.field_parsers.bnc_bic import BNCBICParser
from src.extractors.field_parsers.declaration_2042 import Declaration2042Parser
from src.extractors.field_parsers.urssaf import URSSAFParser


class TestAvisImpositionParser:
    """Tests for Avis d'Imposition parser."""

    @pytest.mark.anyio
    async def test_parse_complete_document(self):
        """Test parsing a complete Avis d'Imposition."""
        text = """
        AVIS D'IMPOSITION SUR LES REVENUS 2023

        Situation de famille: marié
        Nombre de parts: 2.5

        Revenu fiscal de référence: 45000
        Revenu net imposable: 42000
        Impôt sur le revenu net: 3500
        Taux de prélèvement: 7.5 %

        Revenus de l'année: 2023
        """

        parser = AvisImpositionParser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["revenu_fiscal_reference"] == 45000
        assert fields["revenu_imposable"] == 42000
        assert fields["impot_revenu"] == 3500
        assert fields["nombre_parts"] == 2.5
        assert fields["taux_prelevement"] == 7.5
        assert fields["situation_familiale"] == "marié"
        assert fields["year"] == 2023

    @pytest.mark.anyio
    async def test_parse_minimal_document(self):
        """Test parsing with minimal required fields."""
        text = """
        Revenu fiscal de référence: 30000
        """

        parser = AvisImpositionParser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["revenu_fiscal_reference"] == 30000

    @pytest.mark.anyio
    async def test_parse_missing_critical_fields(self):
        """Test parsing fails when critical fields are missing."""
        text = """
        Taux de prélèvement: 5 %
        """

        parser = AvisImpositionParser()

        with pytest.raises(ValueError, match="Could not extract critical fields"):
            await parser.parse(text)


class TestDeclaration2042Parser:
    """Tests for Declaration 2042 parser."""

    @pytest.mark.anyio
    async def test_parse_salaries(self):
        """Test parsing salary income."""
        text = """
        DECLARATION DES REVENUS 2023

        Case 1AJ: 35000
        Case 1BJ: 28000
        """

        parser = Declaration2042Parser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["salaires_declarant1"] == 35000
        assert fields["salaires_declarant2"] == 28000

    @pytest.mark.anyio
    async def test_parse_pensions(self):
        """Test parsing pension income."""
        text = """
        Case 1AS: 15000
        Case 1BS: 12000
        Année: 2023
        """

        parser = Declaration2042Parser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["pensions_declarant1"] == 15000
        assert fields["pensions_declarant2"] == 12000
        assert fields["year"] == 2023

    @pytest.mark.anyio
    async def test_parse_missing_income(self):
        """Test parsing fails when no income fields found."""
        text = """
        Case 6DD: 5000
        """

        parser = Declaration2042Parser()

        with pytest.raises(ValueError, match="Could not extract any income fields"):
            await parser.parse(text)


class TestURSSAFParser:
    """Tests for URSSAF parser."""

    @pytest.mark.anyio
    async def test_parse_complete_document(self):
        """Test parsing complete URSSAF document."""
        text = """
        URSSAF - COTISATIONS SOCIALES

        Chiffre d'affaires: 50000
        Total des cotisations: 8500

        Détail:
        Assurance maladie: 3500
        Retraite de base: 2000
        Allocations familiales: 1500
        CSG-CRDS: 1000
        Formation professionnelle: 500

        Période: Janvier 2024
        Année: 2024
        """

        parser = URSSAFParser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["chiffre_affaires"] == 50000
        assert fields["cotisations_sociales"] == 8500
        assert fields["cotisation_maladie"] == 3500
        assert fields["cotisation_retraite"] == 2000
        assert fields["cotisation_allocations"] == 1500
        assert fields["csg_crds"] == 1000
        assert fields["formation_professionnelle"] == 500
        assert fields["year"] == 2024

    @pytest.mark.anyio
    async def test_parse_alternative_revenue_pattern(self):
        """Test parsing with alternative revenue pattern."""
        text = """
        Revenus déclarés: 25000
        """

        parser = URSSAFParser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["chiffre_affaires"] == 25000


class TestBNCBICParser:
    """Tests for BNC/BIC parser."""

    @pytest.mark.anyio
    async def test_parse_bnc_document(self):
        """Test parsing BNC (non-commercial profits) document."""
        text = """
        DECLARATION BNC - BENEFICES NON COMMERCIAUX
        MICRO-BNC

        Recettes brutes: 40000

        Année: 2023
        """

        parser = BNCBICParser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["regime"] == "micro_bnc"
        assert fields["recettes"] == 40000
        assert fields["year"] == 2023

    @pytest.mark.anyio
    async def test_parse_bic_document(self):
        """Test parsing BIC (commercial profits) document."""
        text = """
        DECLARATION BIC - BENEFICES COMMERCIAUX
        REGIME REEL

        Chiffre d'affaires: 80000
        Total des charges: 45000
        Bénéfice net: 35000

        Détail des charges:
        Loyer: 12000
        Honoraires: 8000
        Amortissements: 10000
        Autres charges: 15000

        Exercice: 2023
        """

        parser = BNCBICParser()
        result = await parser.parse(text)
        fields = result.model_dump(exclude_none=True)

        assert fields["regime"] == "reel_bic"
        assert fields["recettes"] == 80000
        assert fields["charges"] == 45000
        assert fields["benefice"] == 35000
        assert fields["loyer"] == 12000
        assert fields["honoraires"] == 8000
        assert fields["amortissements"] == 10000
        assert fields["autres_charges"] == 15000
        assert fields["year"] == 2023

    @pytest.mark.anyio
    async def test_parse_missing_critical_fields(self):
        """Test parsing fails when critical fields are missing."""
        text = """
        Loyer: 5000
        """

        parser = BNCBICParser()

        with pytest.raises(ValueError, match="Could not extract critical fields"):
            await parser.parse(text)
