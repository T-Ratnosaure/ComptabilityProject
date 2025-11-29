"""Tests for path traversal prevention in file storage."""

import pytest

from src.services.file_storage import FileStorageService


class TestPathTraversalPrevention:
    """Test path traversal attack prevention."""

    @pytest.mark.anyio
    async def test_reject_path_traversal_in_filename(self, tmp_path):
        """Test that path traversal attempts in filename are rejected."""
        storage = FileStorageService(base_path=tmp_path)

        # Attempt path traversal via filename
        malicious_filenames = [
            "../../etc/passwd.pdf",
            "../../../secret.pdf",
            "..\\..\\windows\\system32\\config.pdf",
            "/etc/passwd.pdf",
            "C:\\Windows\\System32\\config.pdf",
        ]

        for filename in malicious_filenames:
            with pytest.raises(ValueError, match="path traversal"):
                await storage.save_file(b"test content", filename)

    @pytest.mark.anyio
    async def test_reject_path_traversal_in_relative_path(self, tmp_path):
        """Test that path traversal in relative_path is rejected."""
        storage = FileStorageService(base_path=tmp_path)

        # Save a legitimate file first
        file_path, _ = await storage.save_file(b"test", "test.pdf")

        # Attempt to read with path traversal
        malicious_paths = [
            "../../../etc/passwd",
            "../../secret.txt",
            "../..",
        ]

        for path in malicious_paths:
            with pytest.raises(ValueError, match="traversal"):
                await storage.get_file_path(path)

    @pytest.mark.anyio
    async def test_file_saved_within_base_path(self, tmp_path):
        """Test that files are always saved within base_path."""
        storage = FileStorageService(base_path=tmp_path)

        file_path, file_hash = await storage.save_file(b"test content", "test.pdf")

        # Get absolute path
        absolute_path = await storage.get_file_path(file_path)

        # Verify it's within base_path
        assert str(absolute_path).startswith(str(tmp_path))

    @pytest.mark.anyio
    async def test_filename_length_limit(self, tmp_path):
        """Test that overly long filenames are rejected."""
        storage = FileStorageService(base_path=tmp_path)

        # Generate filename longer than MAX_FILENAME_LENGTH (255)
        long_filename = "a" * 300 + ".pdf"

        with pytest.raises(ValueError, match="too long"):
            await storage.save_file(b"test", long_filename)

    @pytest.mark.anyio
    async def test_disallowed_extension(self, tmp_path):
        """Test that disallowed file extensions are rejected."""
        storage = FileStorageService(base_path=tmp_path)

        disallowed_files = [
            "test.exe",
            "malware.bat",
            "script.sh",
            "file.zip",
            "data.txt",
        ]

        for filename in disallowed_files:
            with pytest.raises(ValueError, match="not allowed"):
                await storage.save_file(b"test", filename)

    @pytest.mark.anyio
    async def test_allowed_extensions(self, tmp_path):
        """Test that allowed extensions work correctly."""
        storage = FileStorageService(base_path=tmp_path)

        allowed_files = ["test.pdf", "image.png", "photo.jpg", "pic.jpeg"]

        for filename in allowed_files:
            file_path, _ = await storage.save_file(b"test content", filename)
            assert file_path is not None

    @pytest.mark.anyio
    async def test_secure_filename_generation(self, tmp_path):
        """Test that filenames are securely generated (no user input)."""
        storage = FileStorageService(base_path=tmp_path)

        # User provides malicious filename
        user_filename = "../../evil.pdf"

        # Should fail validation
        with pytest.raises(ValueError):
            await storage.save_file(b"test", user_filename)

        # Valid filename should generate secure internal name
        file_path, _ = await storage.save_file(b"test", "normal.pdf")

        # Verify that the actual filename is NOT "normal.pdf"
        # It should be a UUID-based name
        assert "normal" not in file_path
        assert len(file_path.split("/")[-1]) > len("normal.pdf")  # UUID is longer

    @pytest.mark.anyio
    async def test_symlink_detection(self, tmp_path):
        """Test that symlinks outside base_path are rejected."""
        storage = FileStorageService(base_path=tmp_path)

        # This is a basic test; actual symlink attacks are OS-specific
        # The resolve() check in get_file_path should prevent this

        # Try to access a path that would resolve outside base_path
        with pytest.raises(ValueError, match="traversal"):
            await storage.get_file_path("../outside")

    @pytest.mark.anyio
    async def test_file_permissions(self, tmp_path):
        """Test that saved files have restricted permissions."""
        import os
        import stat

        storage = FileStorageService(base_path=tmp_path)

        file_path, _ = await storage.save_file(b"test content", "test.pdf")
        absolute_path = await storage.get_file_path(file_path)

        # Check file permissions (Unix systems)
        if os.name != "nt":  # Not Windows
            file_stat = os.stat(absolute_path)
            mode = stat.S_IMODE(file_stat.st_mode)

            # Should be 0644 (rw-r--r--)
            assert mode == 0o644

    @pytest.mark.anyio
    async def test_user_id_isolation(self, tmp_path):
        """Test that files are isolated by user_id."""
        storage = FileStorageService(base_path=tmp_path)

        # Save files for different users
        path1, _ = await storage.save_file(b"user1 data", "test.pdf", user_id="user1")
        path2, _ = await storage.save_file(b"user2 data", "test.pdf", user_id="user2")

        # Verify they're in different directories
        assert "user1" in path1
        assert "user2" in path2
        assert path1 != path2
