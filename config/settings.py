from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration"""

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # Database Settings
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "crawler_db"

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "crawler_user"
    POSTGRES_PASSWORD: str = "crawler_pass"
    POSTGRES_DB: str = "crawler_jobs"

    # Redis Settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # CAPTCHA Service API Keys
    TWOCAPTCHA_API_KEY: Optional[str] = None
    ANTICAPTCHA_API_KEY: Optional[str] = None

    # Proxy Settings
    PROXY_ENABLED: bool = False
    PROXY_LIST: list[str] = []
    PROXY_ROTATION_ENABLED: bool = True

    # Crawler Settings
    MAX_CONCURRENT_TASKS: int = 5
    DEFAULT_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    # Rate Limiting (requests per minute per domain)
    DEFAULT_RATE_LIMIT: int = 30
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # Human Behavior Simulation
    MIN_DELAY: float = 1.0  # seconds
    MAX_DELAY: float = 3.0  # seconds
    ENABLE_MOUSE_MOVEMENT: bool = True
    ENABLE_RANDOM_SCROLLING: bool = True

    # Data Export
    EXPORT_DIR: str = "./data/exports"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
