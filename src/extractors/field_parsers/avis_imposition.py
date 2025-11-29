"""Parser for Avis d'Imposition documents."""

from src.extractors.field_parsers.base import BaseFieldParser
from src.models.extracted_fields import AvisImpositionExtracted


class AvisImpositionParser(BaseFieldParser):
    """Parse fields from French Avis d'Imposition (tax assessment notice)."""

    async def parse(self, text: str) -> AvisImpositionExtracted:
        """Parse Avis d'Imposition fields from text.

        Args:
            text: Raw text extracted from document

        Returns:
            Dictionary containing:
                - revenu_fiscal_reference: Revenu Fiscal de Référence (RFR)
                - revenu_imposable: Revenu net imposable
                - impot_revenu: Impôt sur le revenu net
                - nombre_parts: Nombre de parts fiscales
                - taux_prelevement: Taux de prélèvement à la source
                - situation_familiale: Situation familiale

        Raises:
            ValueError: If critical fields cannot be extracted
        """
        fields: dict[str, str | float | int] = {}

        # Extract Revenu Fiscal de Référence (RFR)
        rfr = self.extract_float(
            text, r"revenu\s+fiscal\s+de\s+r[ée]f[ée]rence[:\s]+([0-9\s,\.]+)"
        )
        if rfr is not None:
            fields["revenu_fiscal_reference"] = rfr

        # Extract Revenu net imposable
        revenu_imposable = self.extract_float(
            text, r"revenu\s+net\s+imposable[:\s]+([0-9\s,\.]+)"
        )
        if revenu_imposable is not None:
            fields["revenu_imposable"] = revenu_imposable

        # Extract Impôt sur le revenu
        impot = self.extract_float(
            text, r"imp[ôo]t\s+sur\s+le\s+revenu\s+net[:\s]+([0-9\s,\.]+)"
        )
        if impot is not None:
            fields["impot_revenu"] = impot

        # Extract Nombre de parts
        parts = self.extract_float(text, r"nombre\s+de\s+parts[:\s]+([0-9\s,\.]+)")
        if parts is not None:
            fields["nombre_parts"] = parts

        # Extract Taux de prélèvement à la source
        taux = self.extract_float(
            text, r"taux\s+de\s+pr[ée]l[èe]vement[:\s]+([0-9\s,\.]+)\s*%"
        )
        if taux is not None:
            fields["taux_prelevement"] = taux

        # Extract Situation familiale
        situation = self.extract_string(
            text,
            r"situation\s+(?:de\s+)?famille[:\s]+((?:mari[ée]|"
            r"c[ée]libataire|divorc[ée]|veuf|pacs[ée]|pacsé))",
        )
        if situation:
            fields["situation_familiale"] = situation.lower()

        # Extract year
        year = self.extract_int(text, r"revenus\s+de\s+l'ann[ée]e[:\s]+([0-9]{4})")
        if year is not None:
            fields["year"] = year

        # Validation: ensure we have at least RFR or revenu_imposable
        if "revenu_fiscal_reference" not in fields and (
            "revenu_imposable" not in fields
        ):
            raise ValueError("Could not extract critical fields from Avis d'Imposition")

        # Return validated Pydantic model
        return AvisImpositionExtracted(**fields)
