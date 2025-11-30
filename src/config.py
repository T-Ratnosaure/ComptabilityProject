"""Application configuration using Pydantic settings."""

from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "ComptabilityProject"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/database/comptability.db"

    # File Storage
    UPLOAD_DIR: str = "./data/uploads"
    TEMP_DIR: str = "./data/temp"
    MAX_UPLOAD_SIZE_MB: int = 10

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # LLM Configuration
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-haiku-20240307"  # Claude 3 Haiku (fast, cost-effective)
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    LLM_TIMEOUT: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle JSON array string
            import json

            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Handle comma-separated string
                return [origin.strip() for origin in v.split(",")]
        return v

    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.TEMP_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        # Create database directory
        db_path = self.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()
