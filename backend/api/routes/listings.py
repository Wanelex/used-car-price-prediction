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

# Import buyability prediction function
try:
    from src.predict_buyability import predict_buyability
    BUYABILITY_MODEL_AVAILABLE = True
except Exception as e:
    logger.warning(f"Buyability model not available: {e}")
    BUYABILITY_MODEL_AVAILABLE = False

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
        logger.info(f"Fetching listings for user_id: {user_id}")
        repo = get_firebase_repo()
        listings = repo.list_listings(
            user_id=user_id,
            limit=limit + skip  # Account for skip
        )
        logger.info(f"Found {len(listings)} listings for user {user_id}")

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


@router.post("/listings/{listing_id}/analyze", tags=["Listings"])
async def analyze_listing(
    listing_id: str,
    user_id: str = Header(..., description="User ID from Firebase")
):
    """
    Analyze a car listing for buyability based on vehicle features.

    Returns a risk score (0-100) where higher = safer to buy.
    Analysis is based on 6 numerical features: year, mileage, engine volume,
    engine power, vehicle age, and yearly mileage.

    - **listing_id**: The listing ID to analyze
    - **user_id**: Firebase user ID (from Authorization header)
    """
    if not BUYABILITY_MODEL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Buyability model not available. Please train the model first."
        )

    try:
        repo = get_firebase_repo()
        listing = repo.get_by_listing_id(listing_id)

        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")

        # Verify user owns this listing
        if listing.get('user_id') != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        # Extract features for prediction
        sample = {
            "Model Yıl": listing.get('year'),
            "Km": listing.get('mileage'),
            "CCM": listing.get('engine_volume'),
            "Beygir Gucu": listing.get('engine_power')
        }

        # Validate required fields
        if sample["Model Yıl"] is None or sample["Km"] is None:
            raise HTTPException(
                status_code=400,
                detail="Listing missing required fields (year, mileage) for analysis"
            )

        # Get buyability prediction
        analysis = predict_buyability(sample)

        return {
            "status": "success",
            "listing_id": listing_id,
            "analysis": analysis
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing listing {listing_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze", tags=["Listings"])
async def analyze_car_direct(
    # Core required fields for statistical model
    year: int = Query(..., description="Model year"),
    mileage: int = Query(..., description="Total mileage in km"),

    # Optional fields for statistical model
    engine_volume: Optional[str] = Query(None, description="Engine volume (e.g., '1600' or '1301-1600')"),
    engine_power: Optional[str] = Query(None, description="Engine power (e.g., '120' or '101-125')"),

    # Optional fields for LLM analysis (enhanced analysis)
    make: Optional[str] = Query(None, description="Car brand/make (e.g., 'BMW')"),
    series: Optional[str] = Query(None, description="Car series (e.g., '3 Serisi')"),
    model: Optional[str] = Query(None, description="Car model (e.g., '320d')"),
    fuel_type: Optional[str] = Query(None, description="Fuel type (e.g., 'Dizel')"),
    transmission: Optional[str] = Query(None, description="Transmission type (e.g., 'Otomatik')"),
    body_type: Optional[str] = Query(None, description="Body type (e.g., 'Sedan')"),
    drive_type: Optional[str] = Query(None, description="Drive type (e.g., 'Arkadan Itisli')"),
    price: Optional[str] = Query(None, description="Price if available"),

    # Crash score fields - painted/changed parts (comma-separated)
    painted_parts: Optional[str] = Query(None, description="Comma-separated list of painted (boyali) parts"),
    changed_parts: Optional[str] = Query(None, description="Comma-separated list of changed (degisen) parts"),
    local_painted_parts: Optional[str] = Query(None, description="Comma-separated list of locally painted (lokal boyali) parts"),
):
    """
    Hybrid car buyability analysis combining statistical ML model, LLM expert analysis, and crash score.

    Returns:
    - **Statistical Health Score** (ML-based, existing model) - Based on year, mileage, engine specs
    - **LLM Mechanical Reliability Score** (GPT-4 based expert analysis) - Based on specific engine/transmission knowledge
    - **Crash Score** (rule-based) - Based on painted/changed/locally-painted parts

    Core fields (year, mileage) are required.
    Additional fields (make, model, etc.) enhance the LLM analysis quality.
    Parts fields (painted_parts, changed_parts, local_painted_parts) enable crash score calculation.

    No authentication required.
    """
    if not BUYABILITY_MODEL_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Buyability model not available. Please train the model first."
        )

    try:
        # ===== 1. STATISTICAL ANALYSIS (existing model) =====
        sample = {
            "Model Yıl": year,
            "Km": mileage,
            "CCM": engine_volume if engine_volume else "1500",
            "Beygir Gucu": engine_power if engine_power else "100"
        }

        # Get statistical buyability prediction
        statistical_result = predict_buyability(sample)

        # ===== 2. LLM MECHANICAL ANALYSIS (new) =====
        llm_result = None

        # Build comprehensive car data for LLM
        car_data = {
            "Model Yıl": year,
            "Km": mileage,
            "marka": make,
            "seri": series,
            "model": model,
            "yakit_tipi": fuel_type,
            "vites": transmission,
            "kasa_tipi": body_type,
            "motor_hacmi": engine_volume,
            "motor_gucu": engine_power,
            "cekis": drive_type,
            "fiyat": price
        }

        # Only call LLM if we have enough data (at least make and model)
        if make or model:
            try:
                from api.services.llm_service import llm_analyzer
                llm_result = await llm_analyzer.analyze_mechanical_reliability(car_data)
            except Exception as llm_error:
                logger.warning(f"LLM analysis failed: {llm_error}")
                # Continue without LLM analysis - graceful degradation
        else:
            logger.info("Skipping LLM analysis - no make/model provided")

        # ===== 3. CRASH SCORE ANALYSIS (new) =====
        crash_score_result = None

        # Parse comma-separated parts lists
        parsed_painted = [p.strip() for p in painted_parts.split(',')] if painted_parts else None
        parsed_changed = [p.strip() for p in changed_parts.split(',')] if changed_parts else None
        parsed_local_painted = [p.strip() for p in local_painted_parts.split(',')] if local_painted_parts else None

        # Calculate crash score if any parts data is provided
        if parsed_painted or parsed_changed or parsed_local_painted:
            try:
                from api.services.crash_score_service import calculate_crash_score, crash_score_to_dict
                crash_result = calculate_crash_score(
                    painted_parts=parsed_painted,
                    changed_parts=parsed_changed,
                    local_painted_parts=parsed_local_painted
                )
                crash_score_result = crash_score_to_dict(crash_result)
            except Exception as crash_error:
                logger.warning(f"Crash score calculation failed: {crash_error}")
                # Continue without crash score - graceful degradation
        else:
            # No parts data provided - return perfect score (100)
            crash_score_result = {
                "score": 100,
                "total_deduction": 0,
                "deductions": [],
                "summary": "Boyali veya degisen parca bilgisi mevcut degil. Arac orijinal durumda kabul edildi.",
                "risk_level": "Bilinmiyor",
                "verdict": "Parca bilgisi yok - Orijinal kabul edildi"
            }

        # ===== 4. CALCULATE BUYABILITY SCORE =====
        # Extract individual scores for buyability calculation
        statistical_score = statistical_result.get('risk_score') if statistical_result else None
        mechanical_score_val = None
        if llm_result and llm_result.get('scores'):
            mechanical_score_val = llm_result['scores'].get('mechanical_score')
        crash_score_val = crash_score_result.get('score') if crash_score_result else None

        # Calculate comprehensive buyability score
        buyability_result = None
        try:
            from api.services.buyability_score_service import calculate_buyability_score, buyability_score_to_dict
            buyability_calc = calculate_buyability_score(
                statistical_score=statistical_score,
                mechanical_score=mechanical_score_val,
                crash_score=crash_score_val
            )
            buyability_result = buyability_score_to_dict(buyability_calc)
        except Exception as buyability_error:
            logger.warning(f"Buyability score calculation failed: {buyability_error}")
            # Continue without buyability score - graceful degradation

        # ===== 5. BUILD HYBRID RESPONSE =====
        from datetime import datetime

        response = {
            "status": "success",
            "input": {
                "year": year,
                "mileage": mileage,
                "engine_volume": engine_volume,
                "engine_power": engine_power,
                "make": make,
                "series": series,
                "model": model,
                "fuel_type": fuel_type,
                "transmission": transmission,
                "body_type": body_type,
                "drive_type": drive_type,
                "price": price,
                "painted_parts": parsed_painted,
                "changed_parts": parsed_changed,
                "local_painted_parts": parsed_local_painted
            },
            "buyability_score": buyability_result,
            "statistical_analysis": statistical_result,
            "llm_analysis": llm_result,
            "crash_score_analysis": crash_score_result,
            "timestamp": datetime.utcnow().isoformat()
        }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing car: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
