"""Parser for Avis d'Imposition documents."""

from src.extractors.field_parsers.base import BaseFieldParser
from src.models.extracted_fields import AvisImpositionExtracted
from src.models.extraction_confidence import ExtractionConfidenceReport


class AvisImpositionParser(BaseFieldParser):
    """Parse fields from French Avis d'Imposition (tax assessment notice)."""

    # Define patterns for each field (multiple patterns for robustness)
    RFR_PATTERNS = [
        r"revenu\s+fiscal\s+de\s+r[ée]f[ée]rence[:\s]+([0-9\s,\.]+)",
        r"RFR[:\s]+([0-9\s,\.]+)",
        r"r[ée]f[ée]rence\s+fiscal[e]?[:\s]+([0-9\s,\.]+)",
    ]

    REVENU_IMPOSABLE_PATTERNS = [
        r"revenu\s+net\s+imposable[:\s]+([0-9\s,\.]+)",
        r"revenu\s+imposable[:\s]+([0-9\s,\.]+)",
        r"net\s+imposable[:\s]+([0-9\s,\.]+)",
    ]

    IMPOT_PATTERNS = [
        r"imp[ôo]t\s+sur\s+le\s+revenu\s+net[:\s]+([0-9\s,\.]+)",
        r"imp[ôo]t\s+net[:\s]+([0-9\s,\.]+)",
        r"montant\s+de\s+l'imp[ôo]t[:\s]+([0-9\s,\.]+)",
    ]

    PARTS_PATTERNS = [
        r"nombre\s+de\s+parts[:\s]+([0-9\s,\.]+)",
        r"parts\s+fiscales[:\s]+([0-9\s,\.]+)",
        r"quotient\s+familial[:\s]+([0-9\s,\.]+)\s+parts?",
    ]

    # Critical fields for this document type
    CRITICAL_FIELDS = ["revenu_fiscal_reference", "revenu_imposable"]

    async def parse(
        self, text: str
    ) -> tuple[AvisImpositionExtracted, ExtractionConfidenceReport]:
        """Parse Avis d'Imposition fields from text with confidence tracking.

        Args:
            text: Raw text extracted from document

        Returns:
            Tuple of (extracted data, confidence report)

        Raises:
            ValueError: If critical fields cannot be extracted
        """
        report = self.create_confidence_report("avis_imposition")
        report.critical_fields_total = len(self.CRITICAL_FIELDS)
        fields: dict[str, str | float | int] = {}

        # Extract Revenu Fiscal de Référence (RFR) with confidence
        rfr_result = self.extract_float_with_confidence(
            text, self.RFR_PATTERNS, "revenu_fiscal_reference"
        )
        if rfr_result.value is not None:
            fields["revenu_fiscal_reference"] = rfr_result.value
            report.critical_fields_extracted += 1
        report.add_field(
            "revenu_fiscal_reference",
            rfr_result.value,
            rfr_result.confidence_level,
            rfr_result.confidence_score,
            patterns_matched=rfr_result.patterns_matched,
            notes="Champ critique pour calculs CEHR/CDHR" if rfr_result.value else None,
        )

        # Extract Revenu net imposable with confidence
        revenu_result = self.extract_float_with_confidence(
            text, self.REVENU_IMPOSABLE_PATTERNS, "revenu_imposable"
        )
        if revenu_result.value is not None:
            fields["revenu_imposable"] = revenu_result.value
            report.critical_fields_extracted += 1
        report.add_field(
            "revenu_imposable",
            revenu_result.value,
            revenu_result.confidence_level,
            revenu_result.confidence_score,
            patterns_matched=revenu_result.patterns_matched,
        )

        # Extract Impôt sur le revenu with confidence
        impot_result = self.extract_float_with_confidence(
            text, self.IMPOT_PATTERNS, "impot_revenu"
        )
        if impot_result.value is not None:
            fields["impot_revenu"] = impot_result.value
        report.add_field(
            "impot_revenu",
            impot_result.value,
            impot_result.confidence_level,
            impot_result.confidence_score,
            patterns_matched=impot_result.patterns_matched,
        )

        # Extract Nombre de parts with confidence
        parts_result = self.extract_float_with_confidence(
            text, self.PARTS_PATTERNS, "nombre_parts"
        )
        if parts_result.value is not None:
            fields["nombre_parts"] = parts_result.value
        report.add_field(
            "nombre_parts",
            parts_result.value,
            parts_result.confidence_level,
            parts_result.confidence_score,
            patterns_matched=parts_result.patterns_matched,
        )

        # Extract Taux de prélèvement à la source (single pattern)
        taux = self.extract_float(
            text, r"taux\s+de\s+pr[ée]l[èe]vement[:\s]+([0-9\s,\.]+)\s*%"
        )
        if taux is not None:
            fields["taux_prelevement"] = taux
            report.add_field("taux_prelevement", taux, "medium", 0.75)
        else:
            report.add_field("taux_prelevement", None, "uncertain", 0.0)

        # Extract Situation familiale (single pattern)
        situation = self.extract_string(
            text,
            r"situation\s+(?:de\s+)?famille[:\s]+((?:mari[ée]|"
            r"c[ée]libataire|divorc[ée]|veuf|pacs[ée]|pacsé))",
        )
        if situation:
            fields["situation_familiale"] = situation.lower()
            report.add_field("situation_familiale", situation.lower(), "high", 0.90)
        else:
            report.add_field("situation_familiale", None, "uncertain", 0.0)

        # Extract year
        year = self.extract_int(text, r"revenus\s+de\s+l'ann[ée]e[:\s]+([0-9]{4})")
        if year is not None:
            fields["year"] = year
            report.add_field("year", year, "high", 0.95)
        else:
            report.add_field("year", None, "uncertain", 0.0)

        # Calculate overall confidence
        report.calculate_overall_confidence()

        # Validation: ensure we have at least RFR or revenu_imposable
        if "revenu_fiscal_reference" not in fields and (
            "revenu_imposable" not in fields
        ):
            report.warnings.append(
                "Impossible d'extraire les champs critiques (RFR ou revenu imposable)"
            )
            raise ValueError("Could not extract critical fields from Avis d'Imposition")

        # Return validated Pydantic model and confidence report
        return AvisImpositionExtracted(**fields), report

    async def parse_legacy(self, text: str) -> AvisImpositionExtracted:
        """Legacy parse method for backwards compatibility (no confidence).

        Args:
            text: Raw text extracted from document

        Returns:
            Extracted data without confidence report
        """
        result, _ = await self.parse(text)
        return result
