"""Document upload and management API endpoints - SECURE VERSION."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_tax_document_repository
from src.config import settings
from src.models.tax_document import DocumentType
from src.security.file_validator import FileValidator
from src.services.document_service import DocumentProcessingService

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=dict[str, int])
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to upload")],
    document_type: Annotated[DocumentType, Form(description="Type of tax document")],
    year: Annotated[int, Form(description="Tax year")],
    use_ocr: Annotated[bool, Form(description="Use OCR for scanned documents")] = False,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> dict[str, int]:
    """Upload and process a tax document (SECURE VERSION).

    Security features:
    - File size validation with streaming
    - MIME type validation (magic bytes)
    - PDF structure validation
    - Malicious pattern detection
    - Path traversal prevention
    - Sanitized error messages

    Args:
        file: Uploaded PDF file
        document_type: Type of document (avis_imposition, declaration_2042, etc.)
        year: Tax year
        use_ocr: Whether to use OCR for text extraction
        session: Database session

    Returns:
        Dictionary with document_id

    Raises:
        HTTPException: If upload or processing fails (400, 413, 422)
    """
    # Validate filename exists
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Read file content with size limit (streaming to prevent OOM)
    try:
        file_content = bytearray()
        chunk_size = 1024 * 1024  # 1MB chunks
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            file_content.extend(chunk)
            # Early rejection if too large (prevent memory exhaustion)
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large (max {settings.MAX_UPLOAD_SIZE_MB}MB)",
                )

        file_content = bytes(file_content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail="Failed to read file content"
        ) from e

    # Validate file size
    try:
        FileValidator.validate_file_size(file_content, max_size)
    except ValueError as e:
        raise HTTPException(status_code=413, detail=str(e)) from e

    # Validate empty file
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Validate MIME type and PDF structure
    try:
        _pdf_info = FileValidator.validate_pdf(file_content)
        # PDF is valid, proceed with processing
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid PDF: {str(e)}") from e

    # Check for malicious patterns
    try:
        malicious_check = FileValidator.check_for_malicious_patterns(file_content)
        if not malicious_check["safe"]:
            # Log warnings but don't reject (could be false positives)
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                f"Malicious pattern warnings for upload: {malicious_check['warnings']}"
            )
    except ValueError as e:
        # Reject if definitely malicious (e.g., executable)
        raise HTTPException(status_code=422, detail=f"File rejected: {str(e)}") from e

    # Process document
    repository = await get_tax_document_repository(session)
    service = DocumentProcessingService(repository)

    try:
        document_id = await service.process_document(
            file_content=file_content,
            original_filename=file.filename,  # Safe: only used for extension validation
            document_type=document_type,
            year=year,
            use_ocr=use_ocr,
        )

        return {"document_id": document_id}

    except ValueError as e:
        # Business logic errors (safe to expose)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception:
        # Unexpected errors (sanitized by global exception handler)
        raise


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(get_db_session),  # noqa: B008
) -> dict:
    """Get document details by ID.

    Security: Does NOT return raw_text or file_path (internal only).

    Args:
        document_id: Document ID
        session: Database session

    Returns:
        Document details (sanitized)

    Raises:
        HTTPException: If document not found (404)
    """
    repository = await get_tax_document_repository(session)

    document = await repository.get(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return sanitized response (no raw_text, no file_path)
    return {
        "id": document.id,
        "type": document.type,
        "year": document.year,
        "status": document.status,
        "original_filename": document.original_filename,  # Safe: stored name only
        "extracted_fields": document.extracted_fields,  # Structured data only
        "error_message": document.error_message,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
        # NOT included: raw_text (PII risk), file_path (security risk)
    }
