"""OCR text extraction using pytesseract."""

from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image


class OCRExtractor:
    """Extract text from images and scanned PDFs using OCR."""

    def __init__(self, lang: str = "fra"):
        """Initialize OCR extractor.

        Args:
            lang: Tesseract language code (default: 'fra' for French)
        """
        self.lang = lang

    async def extract_from_image(self, image_path: str | Path) -> str:
        """Extract text from an image file using OCR.

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

        try:
            image = Image.open(str(path))
            text = pytesseract.image_to_string(image, lang=self.lang)
            return text

        except Exception as e:
            raise ValueError(f"Failed to extract text from image: {e}") from e

    async def extract_from_pdf(self, pdf_path: str | Path) -> str:
        """Extract text from a scanned PDF using OCR.

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
        """Extract text from scanned PDF, returning a list per page.

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
