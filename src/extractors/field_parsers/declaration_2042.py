"""Parser for Declaration 2042 documents."""

from src.extractors.field_parsers.base import BaseFieldParser
from src.models.extracted_fields import Declaration2042Extracted


class Declaration2042Parser(BaseFieldParser):
    """Parse fields from French Declaration 2042 (income tax return)."""

    async def parse(self, text: str) -> Declaration2042Extracted:
        """Parse Declaration 2042 fields from text.

        Args:
            text: Raw text extracted from document

        Returns:
            Dictionary containing income fields:
                - salaires_declarant1: Salaries for declarant 1 (1AJ)
                - salaires_declarant2: Salaries for declarant 2 (1BJ)
                - pensions_retraite: Retirement pensions (1AS/1BS)
                - revenus_fonciers: Rental income (4BA)
                - revenus_capitaux: Capital income (2TR)
                - plus_values: Capital gains (3VG)
                - charges_deductibles: Deductible expenses (6DD)
                - year: Tax year

        Raises:
            ValueError: If critical fields cannot be extracted
        """
        fields: dict[str, str | float | int] = {}

        # Extract salaires (1AJ, 1BJ boxes)
        salaire_1aj = self.extract_float(text, r"(?:1AJ|case\s+1AJ)[:\s]+([0-9\s,\.]+)")
        if salaire_1aj is not None:
            fields["salaires_declarant1"] = salaire_1aj

        salaire_1bj = self.extract_float(text, r"(?:1BJ|case\s+1BJ)[:\s]+([0-9\s,\.]+)")
        if salaire_1bj is not None:
            fields["salaires_declarant2"] = salaire_1bj

        # Extract pensions (1AS, 1BS boxes)
        pension_1as = self.extract_float(text, r"(?:1AS|case\s+1AS)[:\s]+([0-9\s,\.]+)")
        if pension_1as is not None:
            fields["pensions_declarant1"] = pension_1as

        pension_1bs = self.extract_float(text, r"(?:1BS|case\s+1BS)[:\s]+([0-9\s,\.]+)")
        if pension_1bs is not None:
            fields["pensions_declarant2"] = pension_1bs

        # Extract revenus fonciers (4BA box)
        revenus_fonciers = self.extract_float(
            text, r"(?:4BA|case\s+4BA)[:\s]+([0-9\s,\.]+)"
        )
        if revenus_fonciers is not None:
            fields["revenus_fonciers"] = revenus_fonciers

        # Extract revenus de capitaux mobiliers (2TR box)
        revenus_capitaux = self.extract_float(
            text, r"(?:2TR|case\s+2TR)[:\s]+([0-9\s,\.]+)"
        )
        if revenus_capitaux is not None:
            fields["revenus_capitaux"] = revenus_capitaux

        # Extract plus-values (3VG box)
        plus_values = self.extract_float(text, r"(?:3VG|case\s+3VG)[:\s]+([0-9\s,\.]+)")
        if plus_values is not None:
            fields["plus_values"] = plus_values

        # Extract charges déductibles (6DD box)
        charges = self.extract_float(text, r"(?:6DD|case\s+6DD)[:\s]+([0-9\s,\.]+)")
        if charges is not None:
            fields["charges_deductibles"] = charges

        # Extract year
        year = self.extract_int(text, r"(?:ann[ée]e|revenus?)[:\s]+([0-9]{4})")
        if year is not None:
            fields["year"] = year

        # Validation: ensure we have at least one income field
        income_fields = [
            "salaires_declarant1",
            "salaires_declarant2",
            "pensions_declarant1",
            "pensions_declarant2",
            "revenus_fonciers",
        ]
        if not any(field in fields for field in income_fields):
            raise ValueError(
                "Could not extract any income fields from Declaration 2042"
            )

        # Return validated Pydantic model
        return Declaration2042Extracted(**fields)
