"""SQLAlchemy base configuration and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator
from config.settings import settings
from loguru import logger

# Create SQLAlchemy Base class for all models
Base = declarative_base()

# Create database engine
try:
    engine = create_engine(
        settings.SQLALCHEMY_DATABASE_URL,
        echo=settings.DEBUG,  # Log SQL queries in debug mode
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using them
    )
    logger.info(f"Database engine created: {settings.DATABASE_TYPE}")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator:
    """
    Dependency injection for database session
    Usage in FastAPI: Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    Base.metadata.create_all(bind=engine)
    logger.success("Database tables created/verified")
