"""End-to-End Demo Script for ComptabilityProject.

This script demonstrates the complete workflow:
1. Upload a tax document (PDF)
2. Parse and extract fiscal data
3. Calculate taxes (IR, social contributions)
4. Run optimization analysis (PER, LMNP, etc.)
5. Get AI-powered recommendations from Claude

Run with: uv run python demo_end_to_end.py
"""

import asyncio
import json
from pathlib import Path

import httpx


class TaxOptimizationDemo:
    """End-to-end demo of the tax optimization system."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize demo client.

        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=90.0)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()

    async def check_health(self) -> dict:
        """Check if API is healthy.

        Returns:
            Health check response
        """
        print("[INFO] Checking API health...")
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        data = response.json()
        print(f"[OK] API Status: {data['status']} (v{data['version']})")
        return data

    async def upload_document(
        self, file_path: str, document_type: str, year: int, use_ocr: bool = False
    ) -> dict:
        """Upload a tax document.

        Args:
            file_path: Path to PDF file
            document_type: Type of document (avis_imposition, declaration_2042, etc.)
            year: Tax year
            use_ocr: Whether to use OCR

        Returns:
            Upload response with document_id
        """
        print(f"\n[DOC] Uploading {document_type} for year {year}...")

        # Read file
        pdf_path = Path(file_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Upload
        with open(pdf_path, "rb") as f:
            files = {"file": (pdf_path.name, f, "application/pdf")}
            data = {
                "document_type": document_type,
                "year": year,
                "use_ocr": str(use_ocr).lower(),
            }

            response = await self.client.post(
                f"{self.base_url}/api/v1/documents/upload", files=files, data=data
            )
            response.raise_for_status()

        result = response.json()
        print(f"[OK] Document uploaded successfully (ID: {result['document_id']})")
        return result

    async def get_document(self, document_id: int) -> dict:
        """Retrieve document details.

        Args:
            document_id: Document ID

        Returns:
            Document details with extracted fields
        """
        print(f"\n[INFO] Retrieving document {document_id}...")
        response = await self.client.get(
            f"{self.base_url}/api/v1/documents/{document_id}"
        )
        response.raise_for_status()

        doc = response.json()
        print(f"[OK] Document type: {doc['type']}")
        print(f"   Status: {doc['status']}")

        if doc["extracted_fields"]:
            print(f"   Extracted fields: {len(doc['extracted_fields'])} fields")
            # Show key extracted data
            for key, value in list(doc["extracted_fields"].items())[:5]:
                print(f"   - {key}: {value}")

        return doc

    async def calculate_taxes(self, profile_data: dict) -> dict:
        """Calculate taxes for a fiscal profile.

        Args:
            profile_data: Fiscal profile data

        Returns:
            Tax calculation results
        """
        print("\n[CALC] Calculating taxes...")
        response = await self.client.post(
            f"{self.base_url}/api/v1/tax/calculate", json=profile_data
        )
        response.raise_for_status()

        result = response.json()
        impot = result.get("impot", {})
        socials = result.get("socials", {})

        print(f"[OK] Tax calculation complete:")
        print(f"   Revenu imposable: {result.get('revenu_imposable', 0):,.0f} €")
        print(
            f"   Quotient familial: {result.get('quotient_familial', 0):,.0f} € / part"
        )
        print(f"   TMI: {impot.get('tmi', 0) * 100:.0f}%")
        print(f"   Impôt net: {impot.get('impot_net', 0):,.0f} €")
        print(f"   Cotisations sociales: {socials.get('urssaf_expected', 0):,.0f} €")
        print(f"   Charge fiscale totale: {result.get('charge_totale', 0):,.0f} €")

        return result

    async def run_optimization(self, profile_data: dict, tax_result: dict) -> dict:
        """Run tax optimization analysis.

        Args:
            profile_data: Fiscal profile (nested format)
            tax_result: Tax calculation results

        Returns:
            Optimization recommendations
        """
        print("\n[OPT] Running optimization analysis...")

        # Convert nested profile to flat format for optimization endpoint
        flat_profile = {
            "status": profile_data["person"]["status"],
            "chiffre_affaires": profile_data["income"]["professional_gross"],
            "charges_deductibles": profile_data["income"].get(
                "deductible_expenses", 0.0
            ),
            "nb_parts": profile_data["person"]["nb_parts"],
            "activity_type": "BNC"
            if "bnc" in profile_data["person"]["status"].lower()
            else "BIC",
        }

        request_data = {"profile": flat_profile, "tax_result": tax_result}

        response = await self.client.post(
            f"{self.base_url}/api/v1/optimization/run", json=request_data
        )
        response.raise_for_status()

        result = response.json()
        recommendations = result.get("recommendations", [])

        print(f"[OK] Found {len(recommendations)} optimization opportunities:")
        print(
            f"   Total potential savings: {result.get('potential_savings_total', 0):,.0f} €"
        )

        # Show top 3 recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            print(
                f"\n   {i}. {rec['title']} (Risk: {rec['risk']}, Complexity: {rec['complexity']})"
            )
            print(f"      [CALC] Savings: {rec['impact_estimated']:+,.0f} €")
            try:
                # Try to print description, skip if encoding fails
                desc = (
                    rec["description"][:100]
                    .encode("ascii", errors="ignore")
                    .decode("ascii")
                )
                if desc:
                    print(f"      [NOTE] {desc}...")
            except Exception:
                pass  # Skip description if encoding fails

        return result

    async def get_llm_analysis(
        self,
        user_id: str,
        profile_data: dict,
        tax_result: dict,
        optimization_result: dict,
        user_question: str = None,
    ) -> dict:
        """Get AI-powered fiscal analysis from Claude.

        Args:
            user_id: User identifier
            profile_data: Fiscal profile
            tax_result: Tax calculation results
            optimization_result: Optimization recommendations
            user_question: Optional specific question

        Returns:
            LLM analysis response
        """
        print("\n[AI] Getting AI analysis from Claude...")

        request_data = {
            "user_id": user_id,
            "profile_data": profile_data,
            "tax_result": tax_result,
            "optimization_result": optimization_result,
            "user_question": user_question,
            "include_few_shot": True,
            "include_context": True,
        }

        response = await self.client.post(
            f"{self.base_url}/api/v1/llm/analyze", json=request_data
        )
        response.raise_for_status()

        result = response.json()

        print(f"[OK] Claude analysis complete:")
        print(f"   Conversation ID: {result['conversation_id']}")
        print(f"   Message ID: {result['message_id']}")
        print(
            f"   Tokens used: {result['usage']['input_tokens']} input + {result['usage']['output_tokens']} output"
        )
        print(f"\n[NOTE] Claude's Response:")
        print("-" * 80)
        try:
            # Handle emojis by encoding to ASCII and ignoring non-ASCII chars
            clean_content = (
                result["content"].encode("ascii", errors="ignore").decode("ascii")
            )
            print(clean_content)
        except Exception:
            print(
                "[Note: Response contains special characters that cannot be displayed]"
            )
            print(f"Response length: {len(result['content'])} characters")
        print("-" * 80)

        return result


async def run_complete_demo():
    """Run complete end-to-end demo."""
    demo = TaxOptimizationDemo()

    try:
        # Step 1: Check API health
        await demo.check_health()

        # Step 2: Define a sample freelance profile
        print("\n" + "=" * 80)
        print("[DATA] SAMPLE FREELANCE PROFILE")
        print("=" * 80)

        profile_data = {
            "tax_year": 2024,
            "person": {
                "name": "Demo User",
                "nb_parts": 1.0,
                "status": "micro_bnc",
            },
            "income": {
                "professional_gross": 65000.0,  # 65k CA
                "salary": 0.0,
                "rental_income": 0.0,
                "capital_income": 0.0,
                "deductible_expenses": 0.0,  # Micro regime
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

        print(json.dumps(profile_data, indent=2, ensure_ascii=False))

        # Step 3: Calculate taxes
        tax_result = await demo.calculate_taxes(profile_data)

        # Step 4: Run optimization
        optimization_result = await demo.run_optimization(profile_data, tax_result)

        # Step 5: Get LLM analysis
        await demo.get_llm_analysis(
            user_id="demo_user",
            profile_data=profile_data,
            tax_result=tax_result,
            optimization_result=optimization_result,
            user_question="Quelles sont mes meilleures opportunités d'optimisation fiscale ?",
        )

        print("\n" + "=" * 80)
        print("[OK] END-TO-END DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 80)

    except httpx.HTTPStatusError as e:
        print(f"\n[ERROR] HTTP Error: {e.response.status_code}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
    finally:
        await demo.close()


async def run_document_upload_demo():
    """Run demo with document upload (requires a PDF file)."""
    demo = TaxOptimizationDemo()

    try:
        await demo.check_health()

        # Example: Upload an Avis d'Imposition
        # NOTE: You need a real PDF file for this to work
        pdf_path = "path/to/your/avis_imposition_2024.pdf"

        result = await demo.upload_document(
            file_path=pdf_path,
            document_type="avis_imposition",
            year=2024,
            use_ocr=False,
        )

        # Retrieve uploaded document
        doc = await demo.get_document(result["document_id"])

        # Use extracted fields for tax calculation
        if doc["extracted_fields"]:
            # Map extracted fields to profile
            profile_data = {
                "tax_year": doc["year"],
                "revenu_fiscal_reference": doc["extracted_fields"].get(
                    "revenu_fiscal_reference"
                ),
                # Add other fields...
            }

            print("\n[DATA] Using extracted fields for tax calculation...")
            # Continue with tax calculation, optimization, and LLM analysis

    except FileNotFoundError as e:
        print(f"\n[WARN]  {e}")
        print("   Update the pdf_path variable with a real PDF file path.")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
    finally:
        await demo.close()


def main():
    """Main entry point."""
    print("=" * 80)
    print("[FR] FRENCH TAX OPTIMIZATION SYSTEM - END-TO-END DEMO")
    print("=" * 80)
    print("\nStarting API server check and demo workflow...\n")

    # Run the complete demo (without document upload)
    asyncio.run(run_complete_demo())

    print("\n" + "=" * 80)
    print("[INFO] NEXT STEPS:")
    print("=" * 80)
    print("1. Add Anthropic credits to your API key")
    print("2. Run with a real PDF: modify run_document_upload_demo()")
    print("3. Try different optimization scenarios")
    print("4. Test streaming endpoint: /api/v1/llm/analyze/stream")
    print("=" * 80)


if __name__ == "__main__":
    main()
