"""PDF text extraction using pypdf."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pypdf import PdfReader


class PDFTextExtractor:
    """Extract text from PDF documents.

    Uses ThreadPoolExecutor to prevent blocking the event loop
    during I/O-intensive PDF reading operations.
    """

    def __init__(self, max_workers: int = 4):
        """Initialize PDF text extractor.

        Args:
            max_workers: Maximum worker threads for PDF extraction (default: 4)
        """
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)

    async def extract_text(self, file_path: str | Path) -> str:
        """Extract all text from a PDF file (async).

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

        # Run PDF extraction in executor to avoid blocking event loop (500ms-2s)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._extract_text_sync, path)

    def _extract_text_sync(self, path: Path) -> str:
        """Synchronous PDF text extraction (runs in thread).

        Args:
            path: Path object to the PDF file

        Returns:
            Extracted text content

        Raises:
            ValueError: If the file is not a valid PDF
        """
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
        """Extract text from PDF, returning a list per page (async).

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

        # Run PDF extraction in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._extract_text_by_page_sync, path
        )

    def _extract_text_by_page_sync(self, path: Path) -> list[str]:
        """Synchronous PDF text extraction by page (runs in thread).

        Args:
            path: Path object to the PDF file

        Returns:
            List of text content, one entry per page

        Raises:
            ValueError: If the file is not a valid PDF
        """
        try:
            reader = PdfReader(str(path))
            pages = []

            for page in reader.pages:
                text = page.extract_text()
                pages.append(text if text else "")

            return pages

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}") from e
