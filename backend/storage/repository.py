"""Repository for database operations on car listings"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger

from .models import CarListing, ListingImage, SessionLocal
from .models.car_listing import CarListingSource


class CarListingRepository:
    """Repository for car listing database operations"""

    def __init__(self, db: Optional[Session] = None):
        """
        Initialize repository

        Args:
            db: SQLAlchemy session. If None, creates new session.
        """
        self.db = db
        self._owns_session = db is None
        self.logger = logger

    def _get_session(self) -> Session:
        """Get or create database session"""
        if self.db is None:
            self.db = SessionLocal()
        return self.db

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._owns_session and self.db:
            self.db.close()

    def create_listing(
        self,
        cleaned_data: Dict[str, Any],
        images: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[CarListing]:
        """
        Create or update car listing in database

        Args:
            cleaned_data: Cleaned listing data from cleaner
            images: List of image records with metadata

        Returns:
            CarListing object or None if failed
        """
        db = self._get_session()

        try:
            listing_id = cleaned_data.get('listing_id')

            if not listing_id:
                self.logger.error("Cannot create listing without listing_id")
                return None

            # Check if listing already exists
            existing = db.query(CarListing).filter_by(listing_id=listing_id).first()

            if existing:
                # Update existing listing
                return self.update_listing(existing.id, cleaned_data, images)

            # Create new listing
            listing = CarListing(
                listing_id=listing_id,
                url=cleaned_data.get('url'),
                source=cleaned_data.get('source', 'sahibinden'),

                # Overview
                brand=cleaned_data.get('brand'),
                series=cleaned_data.get('series'),
                model=cleaned_data.get('model'),
                year=cleaned_data.get('year'),
                price=cleaned_data.get('price'),
                mileage=cleaned_data.get('mileage'),
                listing_date=self._parse_datetime(cleaned_data.get('listing_date')),

                # Details
                fuel_type=cleaned_data.get('fuel_type'),
                transmission=cleaned_data.get('transmission'),
                body_type=cleaned_data.get('body_type'),
                engine_power=cleaned_data.get('engine_power'),
                engine_volume=cleaned_data.get('engine_volume'),
                drive_type=cleaned_data.get('drive_type'),
                color=cleaned_data.get('color'),
                vehicle_condition=cleaned_data.get('vehicle_condition'),

                # Seller Info
                seller_type=cleaned_data.get('seller_type'),
                location=cleaned_data.get('location'),
                warranty=cleaned_data.get('warranty'),
                heavy_damage=cleaned_data.get('heavy_damage'),
                plate_origin=cleaned_data.get('plate_origin'),
                trade_option=cleaned_data.get('trade_option'),
                title=cleaned_data.get('title'),
                description=cleaned_data.get('description'),
                phone=cleaned_data.get('phone'),

                # Structured data
                features=cleaned_data.get('features', {}),
                technical_specs=cleaned_data.get('technical_specs', {}),
                painted_parts=cleaned_data.get('painted_parts', {}),

                # Metadata
                data_quality_score=cleaned_data.get('data_quality_score', 0.0),
                has_images=bool(images),
                has_painted_diagram=self._has_painted_diagram(images),
            )

            db.add(listing)
            db.flush()  # Get the listing ID before adding images

            # Add images if provided
            if images:
                for img_data in images:
                    image = ListingImage(
                        listing_id=listing.id,
                        image_type=img_data.get('image_type'),
                        image_order=img_data.get('image_order'),
                        original_url=img_data.get('original_url'),
                        local_path=img_data.get('local_path'),
                        file_size=img_data.get('file_size'),
                        width=img_data.get('width'),
                        height=img_data.get('height'),
                    )
                    db.add(image)

            db.commit()
            self.logger.success(f"Created listing {listing_id} (ID: {listing.id}) with {len(images) if images else 0} images")

            return listing

        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Database error creating listing: {str(e)}")
            return None
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating listing: {str(e)}")
            return None

    def update_listing(
        self,
        listing_id: int,
        cleaned_data: Dict[str, Any],
        images: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[CarListing]:
        """
        Update existing listing

        Args:
            listing_id: Database ID of listing
            cleaned_data: Updated cleaned data
            images: New images list (replaces old)

        Returns:
            Updated CarListing or None
        """
        db = self._get_session()

        try:
            listing = db.query(CarListing).filter_by(id=listing_id).first()

            if not listing:
                self.logger.warning(f"Listing not found: ID {listing_id}")
                return None

            # Update fields
            listing.url = cleaned_data.get('url', listing.url)
            listing.brand = cleaned_data.get('brand', listing.brand)
            listing.series = cleaned_data.get('series', listing.series)
            listing.model = cleaned_data.get('model', listing.model)
            listing.year = cleaned_data.get('year', listing.year)
            listing.price = cleaned_data.get('price', listing.price)
            listing.mileage = cleaned_data.get('mileage', listing.mileage)

            listing.fuel_type = cleaned_data.get('fuel_type', listing.fuel_type)
            listing.transmission = cleaned_data.get('transmission', listing.transmission)
            listing.body_type = cleaned_data.get('body_type', listing.body_type)
            listing.color = cleaned_data.get('color', listing.color)

            listing.features = cleaned_data.get('features', listing.features)
            listing.technical_specs = cleaned_data.get('technical_specs', listing.technical_specs)
            listing.painted_parts = cleaned_data.get('painted_parts', listing.painted_parts)

            listing.data_quality_score = cleaned_data.get('data_quality_score', listing.data_quality_score)
            listing.cleaned_at = datetime.utcnow()

            # Update images if provided
            if images is not None:
                # Delete old images
                db.query(ListingImage).filter_by(listing_id=listing.id).delete()

                # Add new images
                for img_data in images:
                    image = ListingImage(
                        listing_id=listing.id,
                        image_type=img_data.get('image_type'),
                        image_order=img_data.get('image_order'),
                        original_url=img_data.get('original_url'),
                        local_path=img_data.get('local_path'),
                        file_size=img_data.get('file_size'),
                        width=img_data.get('width'),
                        height=img_data.get('height'),
                    )
                    db.add(image)

                listing.has_images = bool(images)
                listing.has_painted_diagram = self._has_painted_diagram(images)

            db.commit()
            self.logger.info(f"Updated listing {listing.listing_id} (ID: {listing_id})")

            return listing

        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Database error updating listing: {str(e)}")
            return None
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating listing: {str(e)}")
            return None

    def get_by_id(self, id: int) -> Optional[CarListing]:
        """Get listing by database ID"""
        db = self._get_session()
        try:
            return db.query(CarListing).filter_by(id=id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching listing by ID: {str(e)}")
            return None

    def get_by_listing_id(self, listing_id: str) -> Optional[CarListing]:
        """Get listing by ilan_no (listing_id)"""
        db = self._get_session()
        try:
            return db.query(CarListing).filter_by(listing_id=listing_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error fetching listing by listing_id: {str(e)}")
            return None

    def list_listings(
        self,
        limit: int = 100,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[CarListing]:
        """
        List listings with optional filters

        Args:
            limit: Max number of results
            offset: Number to skip
            filters: Dict of field=value filters

        Returns:
            List of listings
        """
        db = self._get_session()

        try:
            query = db.query(CarListing)

            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(CarListing, key):
                        query = query.filter(getattr(CarListing, key) == value)

            # Sort by crawled_at descending (newest first)
            query = query.order_by(CarListing.crawled_at.desc())

            # Limit and offset
            query = query.limit(limit).offset(offset)

            return query.all()

        except SQLAlchemyError as e:
            self.logger.error(f"Error listing listings: {str(e)}")
            return []

    def delete_listing(self, id: int) -> bool:
        """Delete listing by ID"""
        db = self._get_session()

        try:
            listing = db.query(CarListing).filter_by(id=id).first()

            if not listing:
                return False

            db.delete(listing)
            db.commit()
            self.logger.info(f"Deleted listing ID {id}")

            return True

        except SQLAlchemyError as e:
            db.rollback()
            self.logger.error(f"Error deleting listing: {str(e)}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about listings"""
        db = self._get_session()

        try:
            total = db.query(CarListing).count()
            avg_price = db.query(CarListing).with_entities(
                db.func.avg(CarListing.price)
            ).scalar()
            avg_quality = db.query(CarListing).with_entities(
                db.func.avg(CarListing.data_quality_score)
            ).scalar()

            return {
                'total_listings': total,
                'avg_price': float(avg_price) if avg_price else 0,
                'avg_quality_score': float(avg_quality) if avg_quality else 0,
            }

        except SQLAlchemyError as e:
            self.logger.error(f"Error getting statistics: {str(e)}")
            return {}

    @staticmethod
    def _parse_datetime(value: Any) -> Optional[datetime]:
        """Parse datetime value"""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                pass
        return None

    @staticmethod
    def _has_painted_diagram(images: Optional[List[Dict[str, Any]]]) -> bool:
        """Check if painted diagram image exists"""
        if not images:
            return False

        return any(img.get('image_type') == 'painted_diagram' for img in images)
