"""File storage management service - SECURE VERSION."""

import hashlib
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path


class FileStorageService:
    """Manage uploaded file storage with security controls."""

    # Allowed extensions
    ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
    MAX_FILENAME_LENGTH = 255

    def __init__(self, base_path: str | Path = "data/documents"):
        """Initialize file storage service.

        Args:
            base_path: Base directory for storing uploaded files
        """
        self.base_path = Path(base_path).resolve()  # Canonical path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _validate_filename(self, filename: str) -> str:
        """Validate and extract safe file extension.

        Args:
            filename: User-provided filename

        Returns:
            Validated extension (e.g., ".pdf")

        Raises:
            ValueError: If filename is invalid or unsafe
        """
        if not filename:
            raise ValueError("Filename cannot be empty")

        if len(filename) > self.MAX_FILENAME_LENGTH:
            raise ValueError(f"Filename too long (max {self.MAX_FILENAME_LENGTH})")

        # Check for path traversal attempts
        if ".." in filename or filename.startswith("/") or "\\" in filename:
            raise ValueError("Invalid filename: path traversal detected")

        # Extract extension
        ext = Path(filename).suffix.lower()

        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"File type not allowed. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )

        return ext

    async def save_file(
        self, file_content: bytes, original_filename: str, user_id: str = "anonymous"
    ) -> tuple[str, str]:
        """Save an uploaded file to storage.

        Args:
            file_content: Binary content of the file
            original_filename: Original filename from upload (UNTRUSTED)
            user_id: User ID for isolation (future use)

        Returns:
            Tuple of (file_path, file_hash)
                - file_path: Relative path where file was saved
                - file_hash: SHA256 hash of file content

        Raises:
            ValueError: If file cannot be saved or validation fails
        """
        # Validate extension from user input
        validated_ext = self._validate_filename(original_filename)

        # Generate secure filename (NEVER use user input directly)
        secure_id = uuid.uuid4().hex
        filename = f"{secure_id}{validated_ext}"

        # Create subdirectory structure: storage/{user_id}/{year}/
        year = datetime.now(UTC).strftime("%Y")
        storage_dir = self.base_path / user_id / year
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Build file path
        file_path = storage_dir / filename

        # Security check: ensure resolved path is within base_path
        resolved_path = file_path.resolve()
        if not str(resolved_path).startswith(str(self.base_path)):
            raise ValueError("Security error: path traversal detected")

        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Save file with restricted permissions
        try:
            with open(resolved_path, "wb") as f:
                f.write(file_content)
            # Set file permissions (read-only for group/others)
            os.chmod(resolved_path, 0o644)
        except Exception as e:
            raise ValueError(f"Failed to save file: {e}") from e

        # Return relative path (relative to base_path)
        relative_path = str(resolved_path.relative_to(self.base_path))
        return relative_path, file_hash

    async def get_file_path(self, relative_path: str) -> Path:
        """Get absolute path for a stored file.

        Args:
            relative_path: Relative path returned from save_file

        Returns:
            Absolute path to the file

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If path is invalid or attempts traversal
        """
        # Security: validate relative_path
        if ".." in relative_path or relative_path.startswith("/"):
            raise ValueError("Invalid path: traversal detected")

        # Normalize and resolve
        file_path = (self.base_path / relative_path).resolve()

        # Security check: ensure within base_path
        if not str(file_path).startswith(str(self.base_path)):
            raise ValueError("Security error: path outside storage")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        # Additional security: ensure it's a file, not a directory or symlink
        if not file_path.is_file():
            raise ValueError("Path is not a regular file")

        return file_path

    async def delete_file(self, relative_path: str) -> None:
        """Delete a stored file.

        Args:
            relative_path: Relative path of file to delete

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If path is invalid
        """
        # Use get_file_path which includes security checks
        file_path = await self.get_file_path(relative_path)
        file_path.unlink()
