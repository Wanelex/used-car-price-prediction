"""
Listings API Routes
Endpoints for fetching and managing user's crawled car listings
"""
from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List, Dict, Any
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import settings
from loguru import logger

router = APIRouter()

# Fields to return to frontend (cleaned data only)
CLEAN_FIELDS = [
    'id', 'listing_id', 'brand', 'series', 'model', 'year', 'price', 'mileage',
    'listing_date', 'fuel_type', 'transmission', 'body_type', 'engine_power',
    'engine_volume', 'drive_type', 'color', 'vehicle_condition', 'seller_type',
    'location', 'warranty', 'heavy_damage', 'plate_origin', 'trade_option',
    'title', 'description', 'phone', 'technical_specs', 'features', 'painted_parts',
    'data_quality_score', 'is_valid', 'images', 'user_id', 'crawled_at', 'updated_at'
]


def filter_clean_data(listing: Dict[str, Any]) -> Dict[str, Any]:
    """Filter listing to return only cleaned fields"""
    return {key: listing[key] for key in CLEAN_FIELDS if key in listing}


def get_firebase_repo():
    """Get Firebase repository instance"""
    try:
        from storage.firebase_repository import FirestoreRepository
        return FirestoreRepository()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase repository: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection failed")


@router.get("/listings", tags=["Listings"])
async def get_listings(
    user_id: str = Header(..., description="User ID from Firebase"),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0)
):
    """
    Get user's car listings from Firestore

    - **user_id**: Firebase user ID (from Authorization header)
    - **limit**: Maximum number of listings to return (1-200)
    - **skip**: Number of listings to skip for pagination
    """
    try:
        repo = get_firebase_repo()
        listings = repo.list_listings(
            user_id=user_id,
            limit=limit + skip  # Account for skip
        )

        # Apply skip
        listings = listings[skip:skip + limit]

        # Filter to return only cleaned data
        clean_listings = [filter_clean_data(l) for l in listings]

        return {
            "status": "success",
            "count": len(clean_listings),
            "data": clean_listings
        }
    except Exception as e:
        logger.error(f"Error fetching listings for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listings/{listing_id}", tags=["Listings"])
async def get_listing(
    listing_id: str,
    user_id: str = Header(..., description="User ID from Firebase")
):
    """
    Get a specific car listing by ID

    - **listing_id**: The listing ID (ilan_no from sahibinden)
    - **user_id**: Firebase user ID (from Authorization header)
    """
    try:
        repo = get_firebase_repo()
        listing = repo.get_by_listing_id(listing_id)

        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")

        # Verify user owns this listing
        if listing.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        return {
            "status": "success",
            "data": filter_clean_data(listing)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching listing {listing_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/listings/{listing_id}", tags=["Listings"])
async def delete_listing(
    listing_id: str,
    user_id: str = Header(..., description="User ID from Firebase")
):
    """
    Delete a car listing by ID

    - **listing_id**: The listing ID (ilan_no from sahibinden)
    - **user_id**: Firebase user ID (from Authorization header)
    """
    try:
        repo = get_firebase_repo()
        listing = repo.get_by_listing_id(listing_id)

        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")

        # Verify user owns this listing
        if listing.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        # Delete the listing
        success = repo.delete_listing(listing_id)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete listing")

        return {
            "status": "success",
            "message": f"Listing {listing_id} deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting listing {listing_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listings/stats/summary", tags=["Listings"])
async def get_listings_stats(
    user_id: str = Header(..., description="User ID from Firebase")
):
    """
    Get statistics about user's listings

    - **user_id**: Firebase user ID (from Authorization header)
    """
    try:
        repo = get_firebase_repo()
        listings = repo.list_listings(user_id=user_id, limit=1000)

        if not listings:
            return {
                "status": "success",
                "data": {
                    "total_listings": 0,
                    "avg_price": 0,
                    "avg_quality_score": 0,
                    "price_range": {"min": 0, "max": 0},
                    "year_range": {"min": 0, "max": 0}
                }
            }

        # Calculate statistics
        total_listings = len(listings)
        total_price = 0
        price_count = 0
        total_quality = 0
        prices = []
        years = []

        for listing in listings:
            if listing.get('price'):
                total_price += listing['price']
                price_count += 1
                prices.append(listing['price'])

            if listing.get('data_quality_score'):
                total_quality += listing['data_quality_score']

            if listing.get('year'):
                years.append(listing['year'])

        stats = {
            "total_listings": total_listings,
            "avg_price": total_price / price_count if price_count > 0 else 0,
            "avg_quality_score": total_quality / total_listings if total_listings > 0 else 0,
            "price_range": {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0
            },
            "year_range": {
                "min": min(years) if years else 0,
                "max": max(years) if years else 0
            }
        }

        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error fetching stats for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/listings/search", tags=["Listings"])
async def search_listings(
    user_id: str = Header(..., description="User ID from Firebase"),
    brand: Optional[str] = Query(None),
    min_year: Optional[int] = Query(None),
    max_year: Optional[int] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    limit: int = Query(50, ge=1, le=200)
):
    """
    Search user's listings with filters

    - **user_id**: Firebase user ID (from Authorization header)
    - **brand**: Filter by car brand
    - **min_year**: Filter by minimum year
    - **max_year**: Filter by maximum year
    - **min_price**: Filter by minimum price
    - **max_price**: Filter by maximum price
    - **limit**: Maximum number of results
    """
    try:
        repo = get_firebase_repo()

        # Get all user listings first
        listings = repo.list_listings(user_id=user_id, limit=1000)

        # Apply filters
        filtered = listings

        if brand:
            filtered = [l for l in filtered if l.get('brand', '').lower() == brand.lower()]

        if min_year:
            filtered = [l for l in filtered if l.get('year', 0) >= min_year]

        if max_year:
            filtered = [l for l in filtered if l.get('year', 9999) <= max_year]

        if min_price is not None:
            filtered = [l for l in filtered if l.get('price', 0) >= min_price]

        if max_price is not None:
            filtered = [l for l in filtered if l.get('price', float('inf')) <= max_price]

        # Apply limit
        filtered = filtered[:limit]

        # Filter to return only cleaned data
        clean_listings = [filter_clean_data(l) for l in filtered]

        return {
            "status": "success",
            "count": len(clean_listings),
            "filters_applied": {
                "brand": brand,
                "min_year": min_year,
                "max_year": max_year,
                "min_price": min_price,
                "max_price": max_price
            },
            "data": clean_listings
        }
    except Exception as e:
        logger.error(f"Error searching listings for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
