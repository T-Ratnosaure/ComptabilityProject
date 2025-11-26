"""Tests for file storage service."""

import pytest

from src.services.file_storage import FileStorageService


class TestFileStorageService:
    """Tests for FileStorageService."""

    @pytest.mark.anyio
    async def test_save_file(self, tmp_path):
        """Test saving a file."""
        service = FileStorageService(base_path=tmp_path)

        file_content = b"Test PDF content"
        filename = "test_document.pdf"

        file_path, file_hash = await service.save_file(file_content, filename)

        assert file_path is not None
        assert file_hash is not None
        assert file_path.endswith(".pdf")

        # Verify file exists
        absolute_path = await service.get_file_path(file_path)
        assert absolute_path.exists()

        # Verify content
        with open(absolute_path, "rb") as f:
            saved_content = f.read()
        assert saved_content == file_content

    @pytest.mark.anyio
    async def test_get_file_path_not_found(self, tmp_path):
        """Test getting path for non-existent file."""
        service = FileStorageService(base_path=tmp_path)

        with pytest.raises(FileNotFoundError):
            await service.get_file_path("nonexistent/file.pdf")

    @pytest.mark.anyio
    async def test_delete_file(self, tmp_path):
        """Test deleting a file."""
        service = FileStorageService(base_path=tmp_path)

        file_content = b"Test content"
        filename = "test.pdf"

        file_path, _ = await service.save_file(file_content, filename)

        # Verify file exists
        absolute_path = await service.get_file_path(file_path)
        assert absolute_path.exists()

        # Delete file
        await service.delete_file(file_path)

        # Verify file is gone
        with pytest.raises(FileNotFoundError):
            await service.get_file_path(file_path)

    @pytest.mark.anyio
    async def test_delete_nonexistent_file(self, tmp_path):
        """Test deleting non-existent file."""
        service = FileStorageService(base_path=tmp_path)

        with pytest.raises(FileNotFoundError):
            await service.delete_file("nonexistent/file.pdf")
