"""Parser for BNC and BIC declaration documents."""

from src.extractors.field_parsers.base import BaseFieldParser


class BNCBICParser(BaseFieldParser):
    """Parse fields from BNC (non-commercial profits) and BIC (commercial profits)."""

    async def parse(self, text: str) -> dict[str, str | float | int]:
        """Parse BNC/BIC declaration fields from text.

        Args:
            text: Raw text extracted from document

        Returns:
            Dictionary containing:
                - recettes: Total receipts (recettes brutes)
                - charges: Total expenses (charges déductibles)
                - benefice: Profit (bénéfice net)
                - amortissements: Depreciation
                - loyer: Rent expenses
                - honoraires: Professional fees
                - autres_charges: Other expenses
                - regime: Tax regime (micro-bnc, micro-bic, reel-bnc, reel-bic)
                - year: Tax year

        Raises:
            ValueError: If critical fields cannot be extracted
        """
        fields: dict[str, str | float | int] = {}

        # Detect regime type
        if "BNC" in text.upper() or "NON COMMERCIALE" in text.upper():
            if "MICRO" in text.upper():
                fields["regime"] = "micro_bnc"
            else:
                fields["regime"] = "reel_bnc"
        elif "BIC" in text.upper() or "COMMERCIALE" in text.upper():
            if "MICRO" in text.upper():
                fields["regime"] = "micro_bic"
            else:
                fields["regime"] = "reel_bic"

        # Extract recettes (total receipts)
        recettes = self.extract_float(
            text, r"recettes(?:\s+brutes)?[:\s]+([0-9\s,\.]+)"
        )
        if recettes is not None:
            fields["recettes"] = recettes

        # Alternative pattern for revenue
        if "recettes" not in fields:
            recettes_alt = self.extract_float(
                text, r"chiffre\s+d'affaires[:\s]+([0-9\s,\.]+)"
            )
            if recettes_alt is not None:
                fields["recettes"] = recettes_alt

        # Extract charges (total expenses)
        charges = self.extract_float(
            text, r"(?:total\s+des\s+)?charges[:\s]+([0-9\s,\.]+)"
        )
        if charges is not None:
            fields["charges"] = charges

        # Extract bénéfice (profit)
        benefice = self.extract_float(
            text, r"b[ée]n[ée]fice(?:\s+net)?[:\s]+([0-9\s,\.]+)"
        )
        if benefice is not None:
            fields["benefice"] = benefice

        # Extract amortissements (depreciation)
        amortissements = self.extract_float(text, r"amortissements[:\s]+([0-9\s,\.]+)")
        if amortissements is not None:
            fields["amortissements"] = amortissements

        # Extract loyer (rent)
        loyer = self.extract_float(text, r"loyer[:\s]+([0-9\s,\.]+)")
        if loyer is not None:
            fields["loyer"] = loyer

        # Extract honoraires (professional fees)
        honoraires = self.extract_float(text, r"honoraires[:\s]+([0-9\s,\.]+)")
        if honoraires is not None:
            fields["honoraires"] = honoraires

        # Extract autres charges
        autres_charges = self.extract_float(
            text, r"autres\s+charges[:\s]+([0-9\s,\.]+)"
        )
        if autres_charges is not None:
            fields["autres_charges"] = autres_charges

        # Extract year
        year = self.extract_int(text, r"(?:ann[ée]e|exercice)[:\s]+([0-9]{4})")
        if year is not None:
            fields["year"] = year

        # Validation: ensure we have at least recettes or benefice
        if "recettes" not in fields and "benefice" not in fields:
            raise ValueError("Could not extract critical fields from BNC/BIC document")

        return fields
