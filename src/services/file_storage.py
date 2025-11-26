"""File storage management service."""

import hashlib
import uuid
from datetime import UTC, datetime
from pathlib import Path


class FileStorageService:
    """Manage uploaded file storage."""

    def __init__(self, base_path: str | Path = "data/documents"):
        """Initialize file storage service.

        Args:
            base_path: Base directory for storing uploaded files
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_file(
        self, file_content: bytes, original_filename: str
    ) -> tuple[str, str]:
        """Save an uploaded file to storage.

        Args:
            file_content: Binary content of the file
            original_filename: Original filename from upload

        Returns:
            Tuple of (file_path, file_hash)
                - file_path: Relative path where file was saved
                - file_hash: SHA256 hash of file content

        Raises:
            ValueError: If file cannot be saved
        """
        # Generate unique filename
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = Path(original_filename).suffix

        # Create subdirectory by year-month
        year_month = datetime.now(UTC).strftime("%Y-%m")
        storage_dir = self.base_path / year_month
        storage_dir.mkdir(parents=True, exist_ok=True)

        # Build filename
        filename = f"{timestamp}_{unique_id}{file_extension}"
        file_path = storage_dir / filename

        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Save file
        try:
            with open(file_path, "wb") as f:
                f.write(file_content)
        except Exception as e:
            raise ValueError(f"Failed to save file: {e}") from e

        # Return relative path (relative to base_path)
        relative_path = str(file_path.relative_to(self.base_path))
        return relative_path, file_hash

    async def get_file_path(self, relative_path: str) -> Path:
        """Get absolute path for a stored file.

        Args:
            relative_path: Relative path returned from save_file

        Returns:
            Absolute path to the file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.base_path / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        return file_path.absolute()

    async def delete_file(self, relative_path: str) -> None:
        """Delete a stored file.

        Args:
            relative_path: Relative path of file to delete

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.base_path / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        file_path.unlink()
