"""OCR text extraction using pytesseract."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


class OCRExtractor:
    """Extract text from images and scanned PDFs using OCR.

    Uses ThreadPoolExecutor to prevent blocking the event loop
    during CPU-intensive OCR operations.
    """

    def __init__(self, lang: str = "fra", max_workers: int = 2):
        """Initialize OCR extractor.

        Args:
            lang: Tesseract language code (default: 'fra' for French)
            max_workers: Maximum number of worker threads for OCR (default: 2)
        """
        self.lang = lang
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, "executor"):
            self.executor.shutdown(wait=False)

    async def extract_from_image(self, image_path: str | Path) -> str:
        """Extract text from an image file using OCR (async).

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If the image file doesn't exist
            ValueError: If the file cannot be processed
        """
        path = Path(image_path)

        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Run OCR in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._extract_from_image_sync, path
        )

    def _extract_from_image_sync(self, path: Path) -> str:
        """Synchronous OCR extraction from image (runs in thread).

        Args:
            path: Path object to the image file

        Returns:
            Extracted text content

        Raises:
            ValueError: If the file cannot be processed
        """
        try:
            image = Image.open(str(path))
            text = pytesseract.image_to_string(image, lang=self.lang)
            return text

        except Exception as e:
            raise ValueError(f"Failed to extract text from image: {e}") from e

    async def extract_from_pdf(self, pdf_path: str | Path) -> str:
        """Extract text from a scanned PDF using OCR (async).

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file cannot be processed
        """
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")

        # Run OCR in executor to avoid blocking event loop (5-30 seconds!)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._extract_from_pdf_sync, path
        )

    def _extract_from_pdf_sync(self, path: Path) -> str:
        """Synchronous OCR extraction from PDF (runs in thread).

        Args:
            path: Path object to the PDF file

        Returns:
            Extracted text content

        Raises:
            ValueError: If the file cannot be processed
        """
        try:
            # Convert PDF pages to images
            images = convert_from_path(str(path))

            # Extract text from each page
            text_parts = []
            for image in images:
                text = pytesseract.image_to_string(image, lang=self.lang)
                if text:
                    text_parts.append(text)

            return "\n\n".join(text_parts)

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}") from e

    async def extract_from_pdf_by_page(self, pdf_path: str | Path) -> list[str]:
        """Extract text from scanned PDF, returning a list per page (async).

        Args:
            pdf_path: Path to the PDF file

        Returns:
            List of text content, one entry per page

        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            ValueError: If the file cannot be processed
        """
        path = Path(pdf_path)

        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {pdf_path}")

        # Run OCR in executor to avoid blocking event loop
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self._extract_from_pdf_by_page_sync, path
        )

    def _extract_from_pdf_by_page_sync(self, path: Path) -> list[str]:
        """Synchronous OCR extraction from PDF by page (runs in thread).

        Args:
            path: Path object to the PDF file

        Returns:
            List of text content, one entry per page

        Raises:
            ValueError: If the file cannot be processed
        """
        try:
            # Convert PDF pages to images
            images = convert_from_path(str(path))

            # Extract text from each page
            pages = []
            for image in images:
                text = pytesseract.image_to_string(image, lang=self.lang)
                pages.append(text if text else "")

            return pages

        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {e}") from e
