"""Tests for file validation (MIME, structure, malicious patterns)."""

import pytest

from src.security.file_validator import FileValidator


class TestMIMEValidation:
    """Test MIME type validation."""

    def test_validate_pdf_magic_bytes(self):
        """Test PDF validation using magic bytes."""
        # Valid PDF header
        pdf_content = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"  # PDF header

        # Should not raise (uses fallback if magic not available)
        result = FileValidator.validate_mime_type(pdf_content, "application/pdf")
        assert result is True

    def test_reject_non_pdf_as_pdf(self):
        """Test that non-PDF files are rejected."""
        # HTML file
        html_content = b"<html><body>Not a PDF</body></html>"

        with pytest.raises(ValueError, match="mismatch|not allowed|Unknown"):
            FileValidator.validate_mime_type(html_content, "application/pdf")

    def test_detect_executable_as_pdf(self):
        """Test that executable files are rejected."""
        # Windows PE executable (MZ header)
        exe_content = b"MZ\x90\x00" + b"\x00" * 100

        with pytest.raises(ValueError):
            FileValidator.validate_mime_type(exe_content, "application/pdf")

    def test_validate_png_magic_bytes(self):
        """Test PNG validation using magic bytes."""
        # Valid PNG header
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 10

        result = FileValidator.validate_mime_type(png_content, "image/png")
        assert result is True

    def test_validate_jpeg_magic_bytes(self):
        """Test JPEG validation using magic bytes."""
        # Valid JPEG header
        jpeg_content = b"\xff\xd8\xff\xe0" + b"\x00" * 10

        result = FileValidator.validate_mime_type(jpeg_content, "image/jpeg")
        assert result is True

    def test_file_too_small(self):
        """Test that very small files are rejected."""
        tiny_file = b"AB"

        with pytest.raises(ValueError, match="too small"):
            FileValidator._validate_mime_fallback(tiny_file, "application/pdf")


class TestPDFStructureValidation:
    """Test PDF structure validation."""

    def test_pdf_without_header(self):
        """Test that files without PDF header are rejected."""
        fake_pdf = b"Not a real PDF file"

        with pytest.raises(ValueError, match="PDF"):
            FileValidator.validate_pdf(fake_pdf)

    def test_minimal_pdf_validation(self):
        """Test basic PDF validation."""
        # Minimal PDF header
        minimal_pdf = b"%PDF-1.4\n"

        # Should validate with basic mode (no pypdf)
        result = FileValidator.validate_pdf(minimal_pdf)
        assert result["valid"] is True


class TestFileSizeValidation:
    """Test file size validation."""

    def test_file_within_limit(self):
        """Test that files within limit are accepted."""
        small_file = b"A" * 1000  # 1KB

        result = FileValidator.validate_file_size(small_file)
        assert result is True

    def test_file_exceeds_limit(self):
        """Test that files exceeding limit are rejected."""
        large_file = b"A" * (11 * 1024 * 1024)  # 11MB

        with pytest.raises(ValueError, match="too large"):
            FileValidator.validate_file_size(large_file)

    def test_custom_size_limit(self):
        """Test custom size limit."""
        file_content = b"A" * 2000  # 2KB

        # Should pass with 3KB limit
        FileValidator.validate_file_size(file_content, max_size=3000)

        # Should fail with 1KB limit
        with pytest.raises(ValueError):
            FileValidator.validate_file_size(file_content, max_size=1000)


class TestMaliciousPatternDetection:
    """Test malicious pattern detection."""

    def test_detect_windows_executable(self):
        """Test detection of Windows PE executable."""
        # MZ header (Windows PE)
        exe_content = b"MZ\x90\x00" + b"\x00" * 100

        with pytest.raises(ValueError, match="Executable.*Windows"):
            FileValidator.check_for_malicious_patterns(exe_content)

    def test_detect_linux_executable(self):
        """Test detection of Linux ELF executable."""
        # ELF header
        elf_content = b"\x7fELF" + b"\x00" * 100

        with pytest.raises(ValueError, match="Executable.*Linux"):
            FileValidator.check_for_malicious_patterns(elf_content)

    def test_detect_javascript_in_header(self):
        """Test detection of JavaScript in file header."""
        # PDF with embedded JavaScript
        js_pdf = b"%PDF-1.4\n<script>alert(1)</script>"

        result = FileValidator.check_for_malicious_patterns(js_pdf)

        assert result["safe"] is False
        assert len(result["warnings"]) > 0
        assert any("JavaScript" in w for w in result["warnings"])

    def test_detect_php_tag(self):
        """Test detection of PHP tags."""
        php_content = b"<?php system($_GET['cmd']); ?>"

        result = FileValidator.check_for_malicious_patterns(php_content)

        assert result["safe"] is False
        assert any("script" in w for w in result["warnings"])

    def test_clean_file(self):
        """Test that clean files pass all checks."""
        clean_pdf = b"%PDF-1.4\nThis is normal PDF content"

        result = FileValidator.check_for_malicious_patterns(clean_pdf)

        assert result["safe"] is True
        assert len(result["warnings"]) == 0


class TestPolyglotAttacks:
    """Test detection of polyglot file attacks."""

    def test_pdf_javascript_polyglot(self):
        """Test PDF/HTML polyglot detection."""
        # File that's both PDF and HTML
        polyglot = b"%PDF-1.4\n<html><script>evil()</script></html>"

        # Should pass PDF validation (has PDF header)
        FileValidator.validate_mime_type(polyglot, "application/pdf")

        # But should trigger malicious pattern warning
        result = FileValidator.check_for_malicious_patterns(polyglot)
        assert result["safe"] is False

    def test_pdf_executable_polyglot(self):
        """Test that executables disguised as PDFs are rejected."""
        # Starts with MZ (executable) but has .pdf extension
        fake_pdf = b"MZ\x90\x00%PDF-1.4\n"

        # Should be rejected as executable
        with pytest.raises(ValueError, match="Executable"):
            FileValidator.check_for_malicious_patterns(fake_pdf)


class TestImageValidation:
    """Test image file validation."""

    def test_validate_png_basic(self):
        """Test PNG validation."""
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100

        result = FileValidator.validate_image(png_content)
        assert result["valid"] is True

    def test_validate_jpeg_basic(self):
        """Test JPEG validation."""
        jpeg_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        result = FileValidator.validate_image(jpeg_content)
        assert result["valid"] is True

    def test_reject_non_image(self):
        """Test that non-image files are rejected."""
        text_content = b"Not an image"

        with pytest.raises(ValueError):
            FileValidator.validate_image(text_content)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_file(self):
        """Test handling of empty files."""
        empty = b""

        with pytest.raises(ValueError):
            FileValidator.validate_mime_type(empty, "application/pdf")

    def test_very_large_file(self):
        """Test handling of very large files."""
        # 100MB file
        large_file = b"A" * (100 * 1024 * 1024)

        with pytest.raises(ValueError, match="too large"):
            FileValidator.validate_file_size(large_file)

    def test_null_bytes(self):
        """Test handling of null bytes."""
        null_pdf = b"%PDF-1.4\n\x00\x00\x00\x00"

        # Should still validate as PDF (null bytes are allowed)
        result = FileValidator.validate_mime_type(null_pdf, "application/pdf")
        assert result is True
