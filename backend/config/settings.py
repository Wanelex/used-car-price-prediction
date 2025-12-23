from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration"""
    DEV_MODE: bool = False
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True

    # Database Settings - Choose one: firebase, postgresql, or mongodb
    DATABASE_TYPE: str = "firebase"  # Options: "firebase", "postgresql", "mongodb"

    # Firebase Configuration
    FIREBASE_CREDENTIALS_PATH: str = "./serviceAccountKey.json"  # Path to Firebase service account key

    # PostgreSQL Configuration (if DATABASE_TYPE = "postgresql")
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "crawler_user"
    POSTGRES_PASSWORD: str = "crawler_pass"
    POSTGRES_DB: str = "crawler_jobs"

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # MongoDB Configuration (if DATABASE_TYPE = "mongodb")
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "crawler_db"

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

    # Image Storage
    IMAGE_STORAGE_PATH: str = "./data/images"
    MAX_IMAGE_SIZE_MB: int = 10
    SUPPORTED_IMAGE_FORMATS: list[str] = ["jpg", "jpeg", "png", "webp"]
    IMAGE_DOWNLOAD_TIMEOUT: int = 30

    # Data Quality Thresholds
    MIN_REQUIRED_FIELDS: list[str] = ["listing_id", "brand", "model", "year", "price"]
    MIN_QUALITY_SCORE: float = 0.5  # 50% completeness threshold

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:8080"]

    # OpenAI Configuration (for LLM mechanical analysis)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo"
    OPENAI_TIMEOUT: int = 30
    OPENAI_MAX_RETRIES: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
