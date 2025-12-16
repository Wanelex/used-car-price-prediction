#!/usr/bin/env python3


import sys
from loguru import logger

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

def init_database():
    """Initialize database and create all tables"""
    try:
        logger.info("Initializing database...")

        # Import after logger is configured
        from backend.storage.models.base import init_db

        # Create all tables
        init_db()

        logger.success("Database initialized successfully!")
        logger.info("Tables created:")
        logger.info("  - car_listings")
        logger.info("  - listing_images")

        return True

    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        logger.exception(e)
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
