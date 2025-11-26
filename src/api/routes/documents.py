"""Document upload and management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db_session, get_tax_document_repository
from src.models.tax_document import DocumentType
from src.services.document_service import DocumentProcessingService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=dict[str, int])
async def upload_document(
    file: Annotated[UploadFile, File(description="PDF document to upload")],
    document_type: Annotated[DocumentType, Form(description="Type of tax document")],
    year: Annotated[int, Form(description="Tax year")],
    use_ocr: Annotated[bool, Form(description="Use OCR for scanned documents")] = False,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, int]:
    """Upload and process a tax document.

    Args:
        file: Uploaded PDF file
        document_type: Type of document (avis_imposition, declaration_2042, etc.)
        year: Tax year
        use_ocr: Whether to use OCR for text extraction
        session: Database session

    Returns:
        Dictionary with document_id

    Raises:
        HTTPException: If upload or processing fails
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}") from e

    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="File is empty")

    # Process document
    repository = await get_tax_document_repository(session)
    service = DocumentProcessingService(repository)

    try:
        document_id = await service.process_document(
            file_content=file_content,
            original_filename=file.filename,
            document_type=document_type,
            year=year,
            use_ocr=use_ocr,
        )

        return {"document_id": document_id}

    except ValueError as e:
        raise HTTPException(
            status_code=422, detail=f"Document processing failed: {e}"
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {e}"
        ) from e


@router.get("/{document_id}", response_model=dict)
async def get_document(
    document_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Get document details by ID.

    Args:
        document_id: Document ID
        session: Database session

    Returns:
        Document details

    Raises:
        HTTPException: If document not found
    """
    repository = await get_tax_document_repository(session)

    document = await repository.get(document_id)

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "type": document.type,
        "year": document.year,
        "status": document.status,
        "original_filename": document.original_filename,
        "extracted_fields": document.extracted_fields,
        "error_message": document.error_message,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.updated_at.isoformat(),
    }
