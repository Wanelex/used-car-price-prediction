"""
Application Settings and Configuration - Day 1
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration"""

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # Crawler Settings
    MAX_CONCURRENT_TASKS: int = 5
    DEFAULT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    # Rate Limiting (requests per minute per domain)
    DEFAULT_RATE_LIMIT: int = 30
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Data Export
    EXPORT_DIR: str = "./data/exports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
