"""Firebase Firestore repository for car listings"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger
import firebase_admin
from firebase_admin import credentials, firestore
from config.settings import settings


class FirestoreRepository:
    """Repository for car listing operations using Firebase Firestore"""

    def __init__(self):
        """Initialize Firestore repository"""
        self.logger = logger
        self.db = None
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Initialize with service account key
                cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                firebase_admin.initialize_app(cred)
                self.logger.success("Firebase initialized")

            self.db = firestore.client()
            self.logger.info("Firestore connected")

        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise

    def create_listing(
        self,
        cleaned_data: Dict[str, Any],
        images: Optional[List[Dict[str, Any]]] = None,
        user_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create or update car listing in Firestore

        Args:
            cleaned_data: Cleaned listing data from cleaner
            images: List of image records with metadata
            user_id: User who created this listing

        Returns:
            Created listing dict with ID or None if failed
        """
        try:
            listing_id = cleaned_data.get('listing_id')

            if not listing_id:
                self.logger.error("Cannot create listing without listing_id")
                return None

            # Prepare listing document
            listing_doc = {
                **cleaned_data,
                'images': images or [],
                'user_id': user_id,  # Store user who created it
                'crawled_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }

            # Convert Decimal to float for JSON serialization
            if 'price' in listing_doc and listing_doc['price'] is not None:
                listing_doc['price'] = float(listing_doc['price'])

            if 'data_quality_score' in listing_doc:
                listing_doc['data_quality_score'] = float(listing_doc['data_quality_score'])

            # Check if listing exists
            doc = self.db.collection('car_listings').document(listing_id).get()

            if doc.exists:
                # Update existing
                self.db.collection('car_listings').document(listing_id).update({
                    **listing_doc,
                    'updated_at': datetime.utcnow(),
                })
                self.logger.info(f"Updated listing {listing_id}")
                listing_doc['id'] = listing_id
                return listing_doc
            else:
                # Create new
                self.db.collection('car_listings').document(listing_id).set(listing_doc)
                self.logger.success(f"Created listing {listing_id} in Firestore")
                listing_doc['id'] = listing_id
                return listing_doc

        except Exception as e:
            self.logger.error(f"Error creating/updating listing: {str(e)}")
            return None

    def get_by_listing_id(self, listing_id: str) -> Optional[Dict[str, Any]]:
        """Get listing by ilan_no (listing_id)"""
        try:
            doc = self.db.collection('car_listings').document(listing_id).get()

            if doc.exists:
                data = doc.to_dict()
                data['id'] = listing_id
                return data

            return None

        except Exception as e:
            self.logger.error(f"Error fetching listing: {str(e)}")
            return None

    def list_listings(
        self,
        user_id: Optional[str] = None,
        limit: int = 100,
        order_by: str = 'crawled_at',
        direction: str = 'DESC'
    ) -> List[Dict[str, Any]]:
        """
        List listings from Firestore

        Args:
            user_id: Filter by user ID (if None, show all)
            limit: Max number of results
            order_by: Field to order by
            direction: 'DESC' or 'ASC'

        Returns:
            List of listings
        """
        try:
            query = self.db.collection('car_listings')

            # Filter by user if provided
            if user_id:
                query = query.where('user_id', '==', user_id)

            # Order by crawled_at descending (newest first)
            if direction.upper() == 'DESC':
                query = query.order_by(order_by, direction=firestore.Query.DESCENDING)
            else:
                query = query.order_by(order_by, direction=firestore.Query.ASCENDING)

            docs = query.limit(limit).stream()

            listings = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                listings.append(data)

            return listings

        except Exception as e:
            self.logger.error(f"Error listing listings: {str(e)}")
            return []

    def list_by_brand(self, brand: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List listings by brand"""
        try:
            docs = self.db.collection('car_listings').where(
                'brand', '==', brand
            ).limit(limit).stream()

            listings = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                listings.append(data)

            return listings

        except Exception as e:
            self.logger.error(f"Error listing by brand: {str(e)}")
            return []

    def list_by_year_range(
        self,
        min_year: int,
        max_year: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List listings by year range"""
        try:
            docs = self.db.collection('car_listings').where(
                'year', '>=', min_year
            ).where(
                'year', '<=', max_year
            ).limit(limit).stream()

            listings = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                listings.append(data)

            return listings

        except Exception as e:
            self.logger.error(f"Error listing by year: {str(e)}")
            return []

    def list_by_price_range(
        self,
        min_price: float,
        max_price: float,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List listings by price range"""
        try:
            docs = self.db.collection('car_listings').where(
                'price', '>=', min_price
            ).where(
                'price', '<=', max_price
            ).limit(limit).stream()

            listings = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                listings.append(data)

            return listings

        except Exception as e:
            self.logger.error(f"Error listing by price: {str(e)}")
            return []

    def delete_listing(self, listing_id: str) -> bool:
        """Delete listing"""
        try:
            self.db.collection('car_listings').document(listing_id).delete()
            self.logger.info(f"Deleted listing {listing_id}")
            return True

        except Exception as e:
            self.logger.error(f"Error deleting listing: {str(e)}")
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about listings"""
        try:
            docs = self.db.collection('car_listings').stream()

            total = 0
            total_price = 0
            total_quality = 0
            price_count = 0

            for doc in docs:
                total += 1
                data = doc.to_dict()

                if data.get('price'):
                    total_price += data['price']
                    price_count += 1

                if data.get('data_quality_score'):
                    total_quality += data['data_quality_score']

            return {
                'total_listings': total,
                'avg_price': total_price / price_count if price_count > 0 else 0,
                'avg_quality_score': total_quality / total if total > 0 else 0,
            }

        except Exception as e:
            self.logger.error(f"Error getting statistics: {str(e)}")
            return {}

    def get_images(self, listing_id: str) -> List[Dict[str, Any]]:
        """Get images for a listing"""
        try:
            doc = self.db.collection('car_listings').document(listing_id).get()

            if doc.exists:
                return doc.to_dict().get('images', [])

            return []

        except Exception as e:
            self.logger.error(f"Error getting images: {str(e)}")
            return []
