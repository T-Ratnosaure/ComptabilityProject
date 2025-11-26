"""PDF text extraction using pypdf."""

from pathlib import Path

from pypdf import PdfReader


class PDFTextExtractor:
    """Extract text from PDF documents."""

    async def extract_text(self, file_path: str | Path) -> str:
        """Extract all text from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {file_path}")

        try:
            reader = PdfReader(str(path))
            text_parts = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n\n".join(text_parts)

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}") from e

    async def extract_text_by_page(self, file_path: str | Path) -> list[str]:
        """Extract text from PDF, returning a list per page.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of text content, one entry per page

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file is not a valid PDF
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if not path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {file_path}")

        try:
            reader = PdfReader(str(path))
            pages = []

            for page in reader.pages:
                text = page.extract_text()
                pages.append(text if text else "")

            return pages

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}") from e
