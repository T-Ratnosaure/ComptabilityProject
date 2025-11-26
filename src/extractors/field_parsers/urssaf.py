"""Parser for URSSAF documents."""

from src.extractors.field_parsers.base import BaseFieldParser


class URSSAFParser(BaseFieldParser):
    """Parse fields from URSSAF social contribution documents."""

    async def parse(self, text: str) -> dict[str, str | float | int]:
        """Parse URSSAF fields from text.

        Args:
            text: Raw text extracted from document

        Returns:
            Dictionary containing:
                - chiffre_affaires: Declared revenue (chiffre d'affaires)
                - cotisations_sociales: Total social contributions
                - cotisation_maladie: Health insurance contribution
                - cotisation_retraite: Retirement contribution
                - cotisation_allocations: Family allowance contribution
                - csg_crds: CSG-CRDS contribution
                - formation_professionnelle: Professional training contribution
                - periode: Period (e.g., "2024-01" for January 2024)
                - year: Year

        Raises:
            ValueError: If critical fields cannot be extracted
        """
        fields: dict[str, str | float | int] = {}

        # Extract chiffre d'affaires
        ca = self.extract_float(text, r"chiffre\s+d'affaires[:\s]+([0-9\s,\.]+)")
        if ca is not None:
            fields["chiffre_affaires"] = ca

        # Alternative pattern for revenue
        if "chiffre_affaires" not in fields:
            ca_alt = self.extract_float(
                text, r"revenus?\s+(?:d[ée]clar[ée]s?)?[:\s]+([0-9\s,\.]+)"
            )
            if ca_alt is not None:
                fields["chiffre_affaires"] = ca_alt

        # Extract total cotisations
        total_cotis = self.extract_float(
            text, r"total\s+(?:des\s+)?cotisations[:\s]+([0-9\s,\.]+)"
        )
        if total_cotis is not None:
            fields["cotisations_sociales"] = total_cotis

        # Extract cotisation maladie
        maladie = self.extract_float(
            text, r"(?:assurance\s+)?maladie[:\s]+([0-9\s,\.]+)"
        )
        if maladie is not None:
            fields["cotisation_maladie"] = maladie

        # Extract cotisation retraite
        retraite = self.extract_float(
            text, r"retraite\s+(?:de\s+base)?[:\s]+([0-9\s,\.]+)"
        )
        if retraite is not None:
            fields["cotisation_retraite"] = retraite

        # Extract allocations familiales
        allocations = self.extract_float(
            text, r"allocations\s+familiales[:\s]+([0-9\s,\.]+)"
        )
        if allocations is not None:
            fields["cotisation_allocations"] = allocations

        # Extract CSG-CRDS
        csg_crds = self.extract_float(text, r"CSG[-\s]*CRDS[:\s]+([0-9\s,\.]+)")
        if csg_crds is not None:
            fields["csg_crds"] = csg_crds

        # Extract formation professionnelle
        formation = self.extract_float(
            text, r"formation\s+professionnelle[:\s]+([0-9\s,\.]+)"
        )
        if formation is not None:
            fields["formation_professionnelle"] = formation

        # Extract period (e.g., "Janvier 2024" or "01/2024")
        periode_text = self.extract_string(text, r"p[ée]riode[:\s]+([a-zA-Z0-9\s/\-]+)")
        if periode_text:
            fields["periode"] = periode_text

        # Extract year
        year = self.extract_int(text, r"(?:ann[ée]e|exercice)[:\s]+([0-9]{4})")
        if year is not None:
            fields["year"] = year

        # Validation: ensure we have at least CA or total cotisations
        if "chiffre_affaires" not in fields and ("cotisations_sociales" not in fields):
            raise ValueError("Could not extract critical fields from URSSAF document")

        return fields
