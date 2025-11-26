"""Document processing service."""

from src.database.repositories.tax_document import TaxDocumentRepository
from src.extractors.field_parsers.avis_imposition import AvisImpositionParser
from src.extractors.field_parsers.bnc_bic import BNCBICParser
from src.extractors.field_parsers.declaration_2042 import Declaration2042Parser
from src.extractors.field_parsers.urssaf import URSSAFParser
from src.extractors.ocr_extractor import OCRExtractor
from src.extractors.pdf_extractor import PDFTextExtractor
from src.models.tax_document import (
    DocumentStatus,
    DocumentType,
    TaxDocumentCreate,
)
from src.services.file_storage import FileStorageService


class DocumentProcessingService:
    """Service for processing uploaded tax documents."""

    def __init__(self, repository: TaxDocumentRepository):
        """Initialize document processing service.

        Args:
            repository: Repository for tax documents
        """
        self.repository = repository
        self.file_storage = FileStorageService()
        self.pdf_extractor = PDFTextExtractor()
        self.ocr_extractor = OCRExtractor(lang="fra")

        # Map document types to parsers
        self.parsers = {
            DocumentType.AVIS_IMPOSITION: AvisImpositionParser(),
            DocumentType.DECLARATION_2042: Declaration2042Parser(),
            DocumentType.URSSAF: URSSAFParser(),
            DocumentType.BNC: BNCBICParser(),
            DocumentType.BIC: BNCBICParser(),
        }

    async def process_document(
        self,
        file_content: bytes,
        original_filename: str,
        document_type: DocumentType,
        year: int,
        use_ocr: bool = False,
    ) -> int:
        """Process an uploaded document.

        Args:
            file_content: Binary content of the file
            original_filename: Original filename
            document_type: Type of document
            year: Tax year
            use_ocr: Whether to use OCR (for scanned documents)

        Returns:
            ID of the created document record

        Raises:
            ValueError: If document processing fails
        """
        # Save file to storage
        file_path, _ = await self.file_storage.save_file(
            file_content, original_filename
        )

        # Create initial document record
        doc_data = TaxDocumentCreate(
            type=document_type,
            year=year,
            status=DocumentStatus.UPLOADED,
            file_path=file_path,
            original_filename=original_filename,
            extracted_fields={},
        )

        doc_model = await self.repository.create(doc_data)

        # Update status to processing
        doc_model = await self.repository.update(
            doc_model, {"status": DocumentStatus.PROCESSING}
        )

        try:
            # Get absolute file path for extraction
            absolute_path = await self.file_storage.get_file_path(file_path)

            # Extract text
            if use_ocr:
                text = await self.ocr_extractor.extract_from_pdf(absolute_path)
            else:
                text = await self.pdf_extractor.extract_text(absolute_path)

            # Parse fields if parser available
            extracted_fields = {}
            error_message = None

            if document_type in self.parsers:
                try:
                    parser = self.parsers[document_type]
                    extracted_fields = await parser.parse(text)
                except ValueError as parse_error:
                    # Parsing failed but text extraction succeeded
                    # Store error message but don't fail the entire process
                    error_message = f"Field parsing failed: {parse_error}"

            # Update document with extracted data
            doc_model = await self.repository.update(
                doc_model,
                {
                    "raw_text": text,
                    "extracted_fields": extracted_fields,
                    "status": DocumentStatus.PROCESSED,
                    "error_message": error_message,
                },
            )

            return doc_model.id

        except Exception as e:
            # Update document with error (for extraction failures)
            await self.repository.update(
                doc_model,
                {
                    "status": DocumentStatus.FAILED,
                    "error_message": f"Text extraction failed: {e}",
                },
            )
            raise ValueError(f"Document processing failed: {e}") from e
