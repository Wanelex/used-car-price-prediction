"""ListingImage model - images associated with car listings"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .base import Base


class ImageType(str, enum.Enum):
    """Enum for image types"""
    MAIN = "main"  # Main listing image
    PAINTED_DIAGRAM = "painted_diagram"  # Painted/changed parts diagram


class ListingImage(Base):
    """
    Image table for car listing images
    Stores references to downloaded images with metadata
    """
    __tablename__ = "listing_images"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key relationship
    listing_id = Column(Integer, ForeignKey("car_listings.id", ondelete="CASCADE"), nullable=False, index=True)

    # Image metadata
    image_type = Column(String(50), default=ImageType.MAIN, nullable=False)  # main or painted_diagram
    image_order = Column(Integer, nullable=True)  # 0, 1 for first two main images; None for diagram

    # URL and local storage
    original_url = Column(String(500), nullable=False)  # Original URL from sahibinden
    local_path = Column(String(500), nullable=False, index=True)  # Relative path like "2025/01/1289077570/main_0.jpg"

    # Image metadata
    file_size = Column(Integer, nullable=True)  # In bytes
    width = Column(Integer, nullable=True)  # Image width in pixels
    height = Column(Integer, nullable=True)  # Image height in pixels

    # Timestamps
    downloaded_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationship back to listing
    listing = relationship("CarListing", back_populates="images")

    def __repr__(self):
        return f"<ListingImage({self.image_type}, order={self.image_order}, path={self.local_path})>"

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'image_type': self.image_type,
            'image_order': self.image_order,
            'local_path': self.local_path,
            'file_size': self.file_size,
            'width': self.width,
            'height': self.height,
            'downloaded_at': self.downloaded_at.isoformat() if self.downloaded_at else None,
        }
