"""File validation with MIME type checking and structure verification."""

from io import BytesIO
from typing import Any

# Deferred imports to avoid loading python-magic at module level (hangs on Windows)
# Import magic only when actually needed in validate_mime_type()
MAGIC_AVAILABLE = False
PYPDF_AVAILABLE = False
PIL_AVAILABLE = False

try:
    from pypdf import PdfReader

    PYPDF_AVAILABLE = True
except ImportError:
    pass

try:
    from PIL import Image

    PIL_AVAILABLE = True
except ImportError:
    pass


class FileValidator:
    """Validate uploaded files (MIME, structure, content)."""

    # Allowed MIME types
    ALLOWED_MIMES = {
        "application/pdf",
        "image/png",
        "image/jpeg",
    }

    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def validate_mime_type(file_content: bytes, expected_mime: str) -> bool:
        """Validate file MIME type using magic bytes.

        Args:
            file_content: File binary content
            expected_mime: Expected MIME type (e.g., "application/pdf")

        Returns:
            True if MIME matches

        Raises:
            ValueError: If MIME type doesn't match or file invalid
        """
        # Always use fallback on Windows (python-magic hangs on DLL load)
        return FileValidator._validate_mime_fallback(file_content, expected_mime)

    @staticmethod
    def _validate_mime_fallback(file_content: bytes, expected_mime: str) -> bool:
        """Fallback MIME validation using magic bytes.

        Used when python-magic is not available.
        """
        # Check magic bytes for common file types
        if len(file_content) < 4:
            raise ValueError("File too small to validate")

        # PDF magic bytes
        if file_content.startswith(b"%PDF"):
            detected_mime = "application/pdf"
        # PNG magic bytes
        elif file_content.startswith(b"\x89PNG\r\n\x1a\n"):
            detected_mime = "image/png"
        # JPEG magic bytes
        elif file_content.startswith(b"\xff\xd8\xff"):
            detected_mime = "image/jpeg"
        else:
            # Provide helpful error message about what file types are allowed
            raise ValueError(
                "File type not allowed. Only PDF, PNG, and JPEG files are supported."
            )

        if expected_mime and detected_mime != expected_mime:
            raise ValueError(
                f"MIME type mismatch: expected {expected_mime}, got {detected_mime}"
            )

        return True

    @staticmethod
    def validate_pdf(file_content: bytes) -> dict[str, Any]:
        """Validate PDF structure and extract metadata.

        Args:
            file_content: PDF file binary content

        Returns:
            Dict with validation results and metadata

        Raises:
            ValueError: If file is not a valid PDF
        """
        # First check MIME
        FileValidator.validate_mime_type(file_content, "application/pdf")

        if not PYPDF_AVAILABLE:
            # Basic validation only
            if not file_content.startswith(b"%PDF"):
                raise ValueError("Not a valid PDF file (missing PDF header)")
            return {
                "valid": True,
                "num_pages": None,
                "has_text": None,
                "encrypted": False,
                "validation_level": "basic",
            }

        # Validate PDF structure with pypdf
        try:
            pdf_file = BytesIO(file_content)
            reader = PdfReader(pdf_file)

            # Basic validation
            num_pages = len(reader.pages)
            if num_pages == 0:
                raise ValueError("PDF has no pages")

            # Check if encrypted
            if reader.is_encrypted:
                raise ValueError("Encrypted PDFs not supported")

            # Try to extract text from first page (validates structure)
            first_page_text = reader.pages[0].extract_text()

            return {
                "valid": True,
                "num_pages": num_pages,
                "has_text": len(first_page_text.strip()) > 0,
                "encrypted": False,
                "validation_level": "full",
            }

        except Exception as e:
            raise ValueError(f"Invalid PDF structure: {e}") from e

    @staticmethod
    def validate_image(file_content: bytes) -> dict[str, Any]:
        """Validate image file.

        Args:
            file_content: Image file binary content

        Returns:
            Dict with validation results

        Raises:
            ValueError: If file is not a valid image
        """
        # Check MIME using magic bytes (python-magic disabled on Windows)
        if file_content.startswith(b"\x89PNG"):
            mime = "image/png"
        elif file_content.startswith(b"\xff\xd8\xff"):
            mime = "image/jpeg"
        else:
            raise ValueError("Unknown image format")

        if mime not in ["image/png", "image/jpeg"]:
            raise ValueError(f"Image type not allowed: {mime}")

        if not PIL_AVAILABLE:
            return {
                "valid": True,
                "format": mime.split("/")[1].upper(),
                "size": None,
                "validation_level": "basic",
            }

        # Validate with PIL
        try:
            img_file = BytesIO(file_content)
            img = Image.open(img_file)
            img.verify()  # Verify it's an actual image

            # Reopen to get size (verify() closes the file)
            img_file.seek(0)
            img = Image.open(img_file)

            return {
                "valid": True,
                "format": img.format,
                "size": img.size,
                "mode": img.mode,
                "validation_level": "full",
            }

        except Exception as e:
            raise ValueError(f"Invalid image file: {e}") from e

    @staticmethod
    def validate_file_size(file_content: bytes, max_size: int | None = None) -> bool:
        """Validate file size.

        Args:
            file_content: File content
            max_size: Maximum allowed size in bytes (default: MAX_FILE_SIZE)

        Returns:
            True if size valid

        Raises:
            ValueError: If file too large
        """
        if max_size is None:
            max_size = FileValidator.MAX_FILE_SIZE

        size = len(file_content)
        if size > max_size:
            max_mb = max_size // 1024 // 1024
            raise ValueError(
                f"File too large: {size} bytes (max {max_size} bytes / {max_mb}MB)"
            )
        return True

    @staticmethod
    def check_for_malicious_patterns(file_content: bytes) -> dict[str, Any]:
        """Check for common malicious patterns in file content.

        Args:
            file_content: File binary content

        Returns:
            Dict with check results

        Raises:
            ValueError: If malicious patterns detected
        """
        warnings = []

        # Check for executable signatures (MZ header, ELF, Mach-O)
        if file_content.startswith(b"MZ"):
            raise ValueError("Executable file detected (Windows PE)")
        if file_content.startswith(b"\x7fELF"):
            raise ValueError("Executable file detected (Linux ELF)")
        if file_content.startswith(b"\xfe\xed\xfa"):
            raise ValueError("Executable file detected (Mach-O)")

        # Check for script tags in first 1KB (polyglot attacks)
        first_kb = file_content[:1024].lower()
        if b"<script" in first_kb or b"javascript:" in first_kb:
            warnings.append("Potential JavaScript detected in file header")

        # Check for PHP/ASP tags
        if b"<?php" in first_kb or b"<%@" in first_kb:
            warnings.append("Potential server-side script detected")

        return {
            "safe": len(warnings) == 0,
            "warnings": warnings,
        }
