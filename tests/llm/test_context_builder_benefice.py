"""Tests for automatic benefice_net calculation in LLMContextBuilder."""


from src.llm.context_builder import LLMContextBuilder


class TestBeneficeNetCalculation:
    """Test automatic benefice_net calculation."""

    async def test_benefice_net_provided(self):
        """Test that provided benefice_net is used."""
        builder = LLMContextBuilder()

        profile_data = {
            "chiffre_affaires": 50000.0,
            "charges_deductibles": 10000.0,
            "benefice_net": 35000.0,  # Explicit value (different from CA - charges)
            "status": "micro_bnc",
            "nb_parts": 1.0,
            "cotisations_sociales": 10900.0,
        }

        tax_result = {
            "impot": {
                "impot_brut": 3500.0,
                "impot_net": 3500.0,
                "tmi": 0.30,
                "taux_effectif": 0.10,
                "revenu_imposable": 33000.0,
                "quotient_familial": 33000.0,
                "reductions": {},
            },
            "socials": {"expected": 10900.0, "paid": 10900.0, "delta": 0.0},
            "warnings": [],
        }

        context = await builder.build_context(
            profile_data=profile_data, tax_result=tax_result, documents=[]
        )

        # Should use provided value, not calculated
        assert context.profil.benefice_net == 35000.0

    async def test_benefice_net_calculated(self):
        """Test that benefice_net is calculated when not provided."""
        builder = LLMContextBuilder()

        profile_data = {
            "chiffre_affaires": 50000.0,
            "charges_deductibles": 10000.0,
            # benefice_net NOT provided
            "status": "micro_bnc",
            "nb_parts": 1.0,
            "cotisations_sociales": 10900.0,
        }

        tax_result = {
            "impot": {
                "impot_brut": 3500.0,
                "impot_net": 3500.0,
                "tmi": 0.30,
                "taux_effectif": 0.10,
                "revenu_imposable": 33000.0,
                "quotient_familial": 33000.0,
                "reductions": {},
            },
            "socials": {"expected": 10900.0, "paid": 10900.0, "delta": 0.0},
            "warnings": [],
        }

        context = await builder.build_context(
            profile_data=profile_data, tax_result=tax_result, documents=[]
        )

        # Should be calculated: 50000 - 10000 = 40000
        assert context.profil.benefice_net == 40000.0

    async def test_benefice_net_calculated_zero_charges(self):
        """Test benefice_net calculation with zero charges."""
        builder = LLMContextBuilder()

        profile_data = {
            "chiffre_affaires": 50000.0,
            "charges_deductibles": 0.0,
            # benefice_net NOT provided
            "status": "micro_bnc",
            "nb_parts": 1.0,
            "cotisations_sociales": 10900.0,
        }

        tax_result = {
            "impot": {
                "impot_brut": 3500.0,
                "impot_net": 3500.0,
                "tmi": 0.30,
                "taux_effectif": 0.10,
                "revenu_imposable": 33000.0,
                "quotient_familial": 33000.0,
                "reductions": {},
            },
            "socials": {"expected": 10900.0, "paid": 10900.0, "delta": 0.0},
            "warnings": [],
        }

        context = await builder.build_context(
            profile_data=profile_data, tax_result=tax_result, documents=[]
        )

        # Should be calculated: 50000 - 0 = 50000
        assert context.profil.benefice_net == 50000.0

    async def test_benefice_net_calculated_negative(self):
        """Test benefice_net calculation when result is negative (loss)."""
        builder = LLMContextBuilder()

        profile_data = {
            "chiffre_affaires": 30000.0,
            "charges_deductibles": 35000.0,  # More than revenue
            # benefice_net NOT provided
            "status": "reel_bnc",
            "nb_parts": 1.0,
            "cotisations_sociales": 5000.0,
        }

        tax_result = {
            "impot": {
                "impot_brut": 0.0,
                "impot_net": 0.0,
                "tmi": 0.0,
                "taux_effectif": 0.0,
                "revenu_imposable": 0.0,
                "quotient_familial": 0.0,
                "reductions": {},
            },
            "socials": {"expected": 5000.0, "paid": 5000.0, "delta": 0.0},
            "warnings": [],
        }

        context = await builder.build_context(
            profile_data=profile_data, tax_result=tax_result, documents=[]
        )

        # Should be calculated: 30000 - 35000 = -5000 (loss)
        assert context.profil.benefice_net == -5000.0

    async def test_benefice_net_with_fallback_field_names(self):
        """Test benefice_net calculation with legacy field names."""
        builder = LLMContextBuilder()

        profile_data = {
            # Using legacy field names
            "professional_gross": 50000.0,  # Instead of chiffre_affaires
            "deductible_expenses": 12000.0,  # Instead of charges_deductibles
            # benefice_net NOT provided
            "status": "reel_bnc",
            "nb_parts": 1.0,
            "social_contributions": 10000.0,  # Legacy name
        }

        tax_result = {
            "impot": {
                "impot_brut": 3500.0,
                "impot_net": 3500.0,
                "tmi": 0.30,
                "taux_effectif": 0.10,
                "revenu_imposable": 38000.0,
                "quotient_familial": 38000.0,
                "reductions": {},
            },
            "socials": {"expected": 10000.0, "paid": 10000.0, "delta": 0.0},
            "warnings": [],
        }

        context = await builder.build_context(
            profile_data=profile_data, tax_result=tax_result, documents=[]
        )

        # Should be calculated: 50000 - 12000 = 38000
        assert context.profil.benefice_net == 38000.0

    async def test_benefice_net_none_becomes_calculated(self):
        """Test that explicit None is replaced by calculation."""
        builder = LLMContextBuilder()

        profile_data = {
            "chiffre_affaires": 60000.0,
            "charges_deductibles": 15000.0,
            "benefice_net": None,  # Explicitly None
            "status": "reel_bnc",
            "nb_parts": 1.0,
            "cotisations_sociales": 12000.0,
        }

        tax_result = {
            "impot": {
                "impot_brut": 4500.0,
                "impot_net": 4500.0,
                "tmi": 0.30,
                "taux_effectif": 0.10,
                "revenu_imposable": 45000.0,
                "quotient_familial": 45000.0,
                "reductions": {},
            },
            "socials": {"expected": 12000.0, "paid": 12000.0, "delta": 0.0},
            "warnings": [],
        }

        context = await builder.build_context(
            profile_data=profile_data, tax_result=tax_result, documents=[]
        )

        # Should be calculated: 60000 - 15000 = 45000
        assert context.profil.benefice_net == 45000.0
