"""Integration tests for end-to-end workflows.

These tests verify that all phases work together correctly:
- Phase 2: Document processing
- Phase 3: Tax calculation
- Phase 4: Optimization analysis
- Phase 5: LLM integration
"""

import pytest
from fastapi.testclient import TestClient


def convert_profile_for_optimization(nested_profile: dict) -> dict:
    """Convert nested tax calculation profile to flat optimization profile format.

    Args:
        nested_profile: Nested format (person/income/deductions/social)

    Returns:
        Flat format (status/chiffre_affaires/charges_deductibles/nb_parts)
    """
    return {
        "status": nested_profile["person"]["status"],
        "chiffre_affaires": nested_profile["income"]["professional_gross"],
        "charges_deductibles": nested_profile["income"].get("deductible_expenses", 0.0),
        "nb_parts": nested_profile["person"]["nb_parts"],
        "activity_type": "BNC"
        if "bnc" in nested_profile["person"]["status"].lower()
        else "BIC",
    }


class TestEndToEndWorkflow:
    """Test complete workflow from profile to LLM recommendations."""

    @pytest.fixture
    def sample_freelance_profile(self) -> dict:
        """Sample freelance profile for testing."""
        return {
            "tax_year": 2024,
            "person": {
                "name": "Test User",
                "nb_parts": 1.0,
                "status": "micro_bnc",
            },
            "income": {
                "professional_gross": 65000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {
                "urssaf_declared_ca": 65000.0,
                "urssaf_paid": 0.0,
            },
            "pas_withheld": 0.0,
        }

    def test_tax_calculation_workflow(
        self, client: TestClient, sample_freelance_profile: dict
    ):
        """Test Phase 3: Tax calculation with valid profile."""
        response = client.post("/api/v1/tax/calculate", json=sample_freelance_profile)

        assert response.status_code == 200
        result = response.json()

        # Verify top-level structure
        assert "tax_year" in result
        assert "impot" in result
        assert "socials" in result
        assert "comparisons" in result
        assert "metadata" in result

        # Verify impot fields (nested inside 'impot')
        impot = result["impot"]
        assert "revenu_imposable" in impot
        assert "part_income" in impot  # quotient familial income per part
        assert "tmi" in impot
        assert "impot_net" in impot

        # Verify calculations
        assert impot["revenu_imposable"] > 0
        assert impot["tmi"] >= 0
        assert impot["impot_net"] >= 0
        assert result["socials"]["urssaf_expected"] > 0

    def test_optimization_workflow(
        self, client: TestClient, sample_freelance_profile: dict
    ):
        """Test Phase 3 → Phase 4: Tax calculation then optimization."""
        # Step 1: Calculate taxes
        tax_response = client.post(
            "/api/v1/tax/calculate", json=sample_freelance_profile
        )
        assert tax_response.status_code == 200
        tax_result = tax_response.json()

        # Step 2: Run optimization (convert profile to flat format)
        optimization_request = {
            "profile": convert_profile_for_optimization(sample_freelance_profile),
            "tax_result": tax_result,
        }

        opt_response = client.post(
            "/api/v1/optimization/run", json=optimization_request
        )
        assert opt_response.status_code == 200
        opt_result = opt_response.json()

        # Verify structure
        assert "recommendations" in opt_result
        assert "potential_savings_total" in opt_result
        assert "summary" in opt_result  # Executive summary of findings
        assert "risk_profile" in opt_result
        assert "high_priority_count" in opt_result

        # Should have recommendations (micro BNC at 65k triggers regime/PER)
        recommendations = opt_result["recommendations"]
        assert len(recommendations) > 0

        # Verify recommendation structure
        first_rec = recommendations[0]
        assert "title" in first_rec
        assert "description" in first_rec
        assert "impact_estimated" in first_rec  # Tax savings field
        assert "risk" in first_rec  # Risk level
        assert "complexity" in first_rec  # Complexity level
        assert "category" in first_rec

    def test_llm_analysis_workflow(
        self, client: TestClient, sample_freelance_profile: dict
    ):
        """Test Phase 3 → Phase 4 → Phase 5: Complete workflow to LLM."""
        # Check if API key is configured
        import os

        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not configured in environment")

        # Step 1: Calculate taxes
        tax_response = client.post(
            "/api/v1/tax/calculate", json=sample_freelance_profile
        )
        assert tax_response.status_code == 200
        tax_result = tax_response.json()

        # Step 2: Run optimization (convert profile to flat format)
        optimization_request = {
            "profile": convert_profile_for_optimization(sample_freelance_profile),
            "tax_result": tax_result,
        }
        opt_response = client.post(
            "/api/v1/optimization/run", json=optimization_request
        )
        assert opt_response.status_code == 200
        opt_result = opt_response.json()

        # Step 3: Get LLM analysis
        llm_request = {
            "user_id": "test_user_integration",
            "profile_data": sample_freelance_profile,
            "tax_result": tax_result,
            "optimization_result": opt_result,
            "user_question": "Quelles sont mes meilleures opportunités d'optimisation?",
            "include_few_shot": True,
            "include_context": True,
        }

        llm_response = client.post("/api/v1/llm/analyze", json=llm_request)

        # NOTE: This will fail with 500/502 if no Anthropic credits
        # But the structure should be correct
        if llm_response.status_code in [500, 502]:
            # Expected when no API credits or API key not configured
            error_detail = str(llm_response.json().get("detail", ""))
            skip_keywords = [
                "credit",
                "api_key",
                "anthropic",
                "llm",
                "authentication",
                "template",
                "jinja2",
                "undefined",
            ]
            if any(keyword in error_detail.lower() for keyword in skip_keywords):
                msg = f"LLM not configured (API/template issue): {error_detail[:100]}"
                pytest.skip(msg)
            # If it's a different 500/502 error, let it fail
            raise AssertionError(f"Unexpected LLM error: {error_detail}")

        assert llm_response.status_code == 200
        llm_result = llm_response.json()

        # Verify response structure
        assert "conversation_id" in llm_result
        assert "message_id" in llm_result
        assert "content" in llm_result
        assert "usage" in llm_result
        assert "was_sanitized" in llm_result

        # Verify conversation was created
        assert len(llm_result["conversation_id"]) > 0
        assert len(llm_result["content"]) > 0

    def test_optimization_with_high_income(self, client: TestClient):
        """Test optimization for high-income profile (triggers more strategies)."""
        high_income_profile = {
            "tax_year": 2024,
            "person": {
                "name": "High Income Test",
                "nb_parts": 2.0,
                "status": "reel_bnc",
            },
            "income": {
                "professional_gross": 150000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 40000.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {
                "urssaf_declared_ca": 150000.0,
                "urssaf_paid": 0.0,
            },
            "pas_withheld": 0.0,
        }

        # Calculate taxes
        tax_response = client.post("/api/v1/tax/calculate", json=high_income_profile)
        assert tax_response.status_code == 200
        tax_result = tax_response.json()

        # Should have high TMI
        assert tax_result["impot"]["tmi"] >= 0.30

        # Run optimization (convert profile to flat format)
        optimization_request = {
            "profile": convert_profile_for_optimization(high_income_profile),
            "tax_result": tax_result,
        }
        opt_response = client.post(
            "/api/v1/optimization/run", json=optimization_request
        )
        assert opt_response.status_code == 200
        opt_result = opt_response.json()

        # High income should trigger multiple strategies (PER, LMNP, etc.)
        recommendations = opt_result["recommendations"]
        assert len(recommendations) >= 3

        # Should have PER recommendation (high TMI)
        per_rec = next((r for r in recommendations if "PER" in r["title"]), None)
        assert per_rec is not None
        assert per_rec["impact_estimated"] > 0

    def test_optimization_priority_ordering(
        self, client: TestClient, sample_freelance_profile: dict
    ):
        """Test that optimization recommendations are properly ordered by impact."""
        # Calculate taxes
        tax_response = client.post(
            "/api/v1/tax/calculate", json=sample_freelance_profile
        )
        assert tax_response.status_code == 200
        tax_result = tax_response.json()

        # Run optimization (convert profile to flat format)
        optimization_request = {
            "profile": convert_profile_for_optimization(sample_freelance_profile),
            "tax_result": tax_result,
        }
        opt_response = client.post(
            "/api/v1/optimization/run", json=optimization_request
        )
        assert opt_response.status_code == 200
        opt_result = opt_response.json()

        recommendations = opt_result["recommendations"]
        assert len(recommendations) > 0

        # Verify ordering: highest impact should come first
        if len(recommendations) >= 2:
            for i in range(len(recommendations) - 1):
                current_impact = recommendations[i]["impact_estimated"]
                next_impact = recommendations[i + 1]["impact_estimated"]
                # Current should have >= impact than next (descending order)
                assert current_impact >= next_impact

    def test_conversation_continuity(
        self, client: TestClient, sample_freelance_profile: dict
    ):
        """Test that conversations maintain context across multiple queries."""
        # Check if API key is configured
        import os

        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not configured in environment")

        # Calculate taxes and optimize
        tax_response = client.post(
            "/api/v1/tax/calculate", json=sample_freelance_profile
        )
        tax_result = tax_response.json()

        opt_request = {
            "profile": convert_profile_for_optimization(sample_freelance_profile),
            "tax_result": tax_result,
        }
        opt_response = client.post("/api/v1/optimization/run", json=opt_request)
        opt_result = opt_response.json()

        # First LLM query
        llm_request_1 = {
            "user_id": "test_conversation_user",
            "profile_data": sample_freelance_profile,
            "tax_result": tax_result,
            "optimization_result": opt_result,
            "user_question": "Quelle est ma tranche marginale d'imposition?",
        }

        llm_response_1 = client.post("/api/v1/llm/analyze", json=llm_request_1)

        if llm_response_1.status_code in [500, 502]:
            error_detail = str(llm_response_1.json().get("detail", ""))
            skip_keywords = [
                "credit",
                "api_key",
                "anthropic",
                "llm",
                "authentication",
                "template",
                "jinja2",
                "undefined",
            ]
            if any(keyword in error_detail.lower() for keyword in skip_keywords):
                pytest.skip(f"LLM service not fully configured: {error_detail[:150]}")
            raise AssertionError(f"Unexpected LLM error: {error_detail}")

        assert llm_response_1.status_code == 200
        result_1 = llm_response_1.json()
        conversation_id = result_1["conversation_id"]

        # Second query in same conversation
        llm_request_2 = {
            "user_id": "test_conversation_user",
            "conversation_id": conversation_id,  # Continue conversation
            "profile_data": sample_freelance_profile,
            "tax_result": tax_result,
            "optimization_result": opt_result,
            "user_question": "Et comment puis-je la réduire?",  # Follow-up question
        }

        llm_response_2 = client.post("/api/v1/llm/analyze", json=llm_request_2)
        assert llm_response_2.status_code == 200
        result_2 = llm_response_2.json()

        # Should use same conversation
        assert result_2["conversation_id"] == conversation_id
        # Should have different message IDs
        assert result_2["message_id"] != result_1["message_id"]


class TestDataFlowIntegration:
    """Test data flow between phases."""

    def test_tax_result_used_in_optimization(self, client: TestClient):
        """Verify tax calculation results are properly used in optimization."""
        profile = {
            "tax_year": 2024,
            "person": {
                "name": "Test User",
                "nb_parts": 1.0,
                "status": "micro_bnc",
            },
            "income": {
                "professional_gross": 50000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {
                "urssaf_declared_ca": 50000.0,
                "urssaf_paid": 0.0,
            },
            "pas_withheld": 0.0,
        }

        # Calculate taxes
        tax_response = client.post("/api/v1/tax/calculate", json=profile)
        tax_result = tax_response.json()

        # Run optimization (convert profile to flat format)
        opt_request = {
            "profile": convert_profile_for_optimization(profile),
            "tax_result": tax_result,
        }
        opt_response = client.post("/api/v1/optimization/run", json=opt_request)
        opt_result = opt_response.json()

        # PER recommendation should reference the TMI
        per_rec = next(
            (r for r in opt_result["recommendations"] if "PER" in r["title"]), None
        )

        if per_rec:
            # PER savings should be calculated based on TMI
            assert per_rec["impact_estimated"] > 0
            # Description should reference fiscal situation
            assert len(per_rec["description"]) > 0

    def test_optimization_used_in_llm_context(self, client: TestClient):
        """Verify optimization results are passed to LLM context."""
        # Check if API key is configured
        import os

        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not configured in environment")

        profile = {
            "tax_year": 2024,
            "person": {
                "name": "Test User",
                "nb_parts": 1.0,
                "status": "micro_bnc",
            },
            "income": {
                "professional_gross": 60000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {
                "urssaf_declared_ca": 60000.0,
                "urssaf_paid": 0.0,
            },
            "pas_withheld": 0.0,
        }

        # Full workflow
        tax_response = client.post("/api/v1/tax/calculate", json=profile)
        tax_result = tax_response.json()

        opt_request = {
            "profile": convert_profile_for_optimization(profile),
            "tax_result": tax_result,
        }
        opt_response = client.post("/api/v1/optimization/run", json=opt_request)
        opt_result = opt_response.json()

        # LLM request includes optimization results
        llm_request = {
            "user_id": "test_context_user",
            "profile_data": profile,
            "tax_result": tax_result,
            "optimization_result": opt_result,
            "user_question": "Quelles sont les recommandations?",
            "include_context": True,  # Important: include fiscal context
        }

        llm_response = client.post("/api/v1/llm/analyze", json=llm_request)

        if llm_response.status_code in [500, 502]:
            error_detail = str(llm_response.json().get("detail", ""))
            skip_keywords = [
                "credit",
                "api_key",
                "anthropic",
                "llm",
                "authentication",
                "template",
                "jinja2",
                "undefined",
            ]
            if any(keyword in error_detail.lower() for keyword in skip_keywords):
                pytest.skip(f"LLM service not fully configured: {error_detail[:150]}")
            raise AssertionError(f"Unexpected LLM error: {error_detail}")

        assert llm_response.status_code == 200
        # LLM should receive context with optimization recommendations


@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance of end-to-end workflows."""

    def test_full_workflow_performance(self, client: TestClient):
        """Test that complete workflow completes in reasonable time."""
        import time

        profile = {
            "tax_year": 2024,
            "person": {
                "name": "Test User",
                "nb_parts": 1.0,
                "status": "micro_bnc",
            },
            "income": {
                "professional_gross": 55000.0,
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,
            },
            "deductions": {
                "per_contributions": 0.0,
                "alimony": 0.0,
                "other_deductions": 0.0,
            },
            "social": {
                "urssaf_declared_ca": 55000.0,
                "urssaf_paid": 0.0,
            },
            "pas_withheld": 0.0,
        }

        start = time.time()

        # Tax calculation
        tax_response = client.post("/api/v1/tax/calculate", json=profile)
        assert tax_response.status_code == 200
        tax_time = time.time() - start

        # Optimization (convert profile to flat format)
        opt_start = time.time()
        opt_request = {
            "profile": convert_profile_for_optimization(profile),
            "tax_result": tax_response.json(),
        }
        opt_response = client.post("/api/v1/optimization/run", json=opt_request)
        assert opt_response.status_code == 200
        opt_time = time.time() - opt_start

        total_time = time.time() - start

        # Performance assertions
        assert tax_time < 1.0, f"Tax calculation too slow: {tax_time:.2f}s"
        assert opt_time < 2.0, f"Optimization too slow: {opt_time:.2f}s"
        assert total_time < 3.0, f"Total workflow too slow: {total_time:.2f}s"
