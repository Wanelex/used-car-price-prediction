"""
Crawl API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models.schemas import CrawlRequest, CrawlResponse, JobStatus, CrawlResult
from crawler.crawler import Crawler
from loguru import logger


router = APIRouter()


# Temporary in-memory storage (will be replaced with database)
jobs_storage: Dict[str, Dict[str, Any]] = {}


def parse_price(price_str: Any) -> Optional[float]:
    """Parse price string like '1.490.000 TL' to float"""
    if price_str is None:
        return None
    if isinstance(price_str, (int, float)):
        return float(price_str)
    if isinstance(price_str, str):
        # Remove "TL", spaces, and convert dots to nothing (thousand separator)
        cleaned = price_str.replace('TL', '').replace('.', '').replace(',', '.').strip()
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def parse_int(value: Any) -> Optional[int]:
    """Parse integer from string like '125.000' (km) or '2020'"""
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        # Remove dots (thousand separator) and other non-numeric chars
        cleaned = value.replace('.', '').replace(',', '').strip()
        # Extract only digits
        digits = ''.join(filter(str.isdigit, cleaned))
        try:
            return int(digits) if digits else None
        except ValueError:
            return None
    return None


def save_listing_to_firestore(sahibinden_data: Dict[str, Any], user_id: Optional[str], result_images: List[str] = None) -> bool:
    """Save the crawled listing to Firestore"""
    try:
        from storage.firebase_repository import FirestoreRepository

        repo = FirestoreRepository()

        # Prepare cleaned data for storage with proper type conversion
        cleaned_data = {
            'listing_id': sahibinden_data.get('ilan_no'),
            'brand': sahibinden_data.get('marka'),
            'series': sahibinden_data.get('seri'),
            'model': sahibinden_data.get('model'),
            'year': parse_int(sahibinden_data.get('yil')),
            'price': parse_price(sahibinden_data.get('fiyat')),
            'mileage': parse_int(sahibinden_data.get('km')),
            'fuel_type': sahibinden_data.get('yakit_tipi'),
            'transmission': sahibinden_data.get('vites'),
            'body_type': sahibinden_data.get('kasa_tipi'),
            'engine_power': sahibinden_data.get('motor_gucu'),
            'engine_volume': sahibinden_data.get('motor_hacmi'),
            'drive_type': sahibinden_data.get('cekis'),
            'color': sahibinden_data.get('renk'),
            'seller_type': sahibinden_data.get('kimden'),
            'location': sahibinden_data.get('il'),
            'title': sahibinden_data.get('baslik'),
            'description': sahibinden_data.get('aciklama'),
            'technical_specs': sahibinden_data.get('teknik_ozellikler'),
            'painted_parts': sahibinden_data.get('boyali_degisen'),
            'data_quality_score': 0.8,  # Default score
        }

        # Get images - prefer result_images, fallback to gorseller from sahibinden_data
        images = result_images or sahibinden_data.get('gorseller', [])
        logger.info(f"Saving listing with {len(images)} images")
        image_records = [{'url': img, 'is_primary': i == 0} for i, img in enumerate(images)]

        result = repo.create_listing(cleaned_data, images=image_records, user_id=user_id)

        if result:
            logger.success(f"Saved listing {cleaned_data['listing_id']} to Firestore for user {user_id}")
            return True
        return False

    except Exception as e:
        logger.error(f"Failed to save listing to Firestore: {str(e)}")
        return False


async def perform_crawl(job_id: str, request: CrawlRequest, user_id: Optional[str] = None):
    """
    Background task to perform the actual crawling with the real Crawler class
    """
    crawler = None
    try:
        # Update status to running
        jobs_storage[job_id]["status"] = JobStatus.RUNNING
        jobs_storage[job_id]["started_at"] = datetime.utcnow()

        # Initialize Crawler with request parameters
        crawler = Crawler(
            use_stealth=request.use_stealth,
            use_proxy=request.use_proxy,
            solve_captcha=request.solve_captcha,
            headless=True
        )
        await crawler.initialize()

        # Perform actual crawl
        result = await crawler.crawl(
            url=request.url,
            use_browser=True,
            wait_time=request.wait_time,
            wait_for_selector=request.wait_for_selector,
            custom_headers=request.custom_headers,
            max_retries=request.max_retries
        )

        # Map crawler result to job storage format
        if result.get("status") == "success":
            jobs_storage[job_id]["status"] = JobStatus.COMPLETED
            jobs_storage[job_id]["result"] = {
                "html": result.get("html"),
                "text": result.get("text"),
                "title": result.get("title"),
                "metadata": result.get("metadata"),
                "images": result.get("images", []),
                "links": result.get("links", []),
                "sahibinden_listing": result.get("sahibinden_listing"),  # FIX: Store sahibinden data
                "final_url": result.get("url"),
                "response_time": result.get("response_time"),
                "captcha_solved": result.get("captcha_solved", False),
                "method": result.get("method"),
                "crawl_duration": result.get("crawl_duration")
            }

            # Save to Firestore if we have sahibinden data
            sahibinden_data = result.get("sahibinden_listing")
            result_images = result.get("images", [])
            logger.info(f"Crawl completed. sahibinden_data present: {sahibinden_data is not None}, user_id: {user_id}, images count: {len(result_images)}")
            if sahibinden_data:
                logger.info(f"sahibinden_data keys: {sahibinden_data.keys() if isinstance(sahibinden_data, dict) else 'not a dict'}")
                logger.info(f"ilan_no: {sahibinden_data.get('ilan_no') if isinstance(sahibinden_data, dict) else 'N/A'}")
            if sahibinden_data and sahibinden_data.get("ilan_no"):
                save_listing_to_firestore(sahibinden_data, user_id, result_images=result_images)
            else:
                logger.warning(f"No sahibinden_listing data or missing ilan_no, skipping Firestore save")
        else:
            # Crawl failed
            jobs_storage[job_id]["status"] = JobStatus.FAILED
            jobs_storage[job_id]["error_message"] = result.get("error_message", "Unknown crawl error")

        # Update completed timestamp
        jobs_storage[job_id]["completed_at"] = datetime.utcnow()

    except Exception as e:
        # Handle unexpected errors
        jobs_storage[job_id]["status"] = JobStatus.FAILED
        jobs_storage[job_id]["error_message"] = str(e)
        jobs_storage[job_id]["completed_at"] = datetime.utcnow()
    finally:
        # Cleanup crawler resources
        if crawler:
            await crawler.close()


@router.post("/crawl", response_model=CrawlResponse)
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks, req: Request):
    """
    Start a new crawl job

    This endpoint accepts a URL and configuration options, then starts a background
    crawl task. Returns a job ID that can be used to check status and retrieve results.
    """
    # Get user_id from auth middleware
    user_id = getattr(req.state, "user_id", None)

    # Generate unique job ID
    job_id = str(uuid.uuid4())

    # Initialize job in storage
    jobs_storage[job_id] = {
        "job_id": job_id,
        "url": request.url,
        "status": JobStatus.PENDING,
        "created_at": datetime.utcnow(),
        "started_at": None,
        "completed_at": None,
        "config": request.dict(),
        "result": None,
        "error_message": None,
        "retry_count": 0,
        "user_id": user_id
    }

    # Add crawl task to background tasks (pass user_id)
    background_tasks.add_task(perform_crawl, job_id, request, user_id)

    return CrawlResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Crawl job queued successfully",
        estimated_time=30
    )


@router.post("/crawl/quick", response_model=Dict[str, Any])
async def quick_crawl(request: CrawlRequest):
    """
    Perform a quick synchronous crawl (not recommended for production)

    This endpoint performs the crawl synchronously and returns results immediately.
    Use for testing or simple use cases only. For production, use /crawl endpoint.
    """
    try:
        # Placeholder - will be implemented with actual crawler
        result = {
            "url": request.url,
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "title": "Placeholder Title",
                "text": "Placeholder content",
                "metadata": {}
            },
            "message": "This is a placeholder response. Actual crawler will be implemented."
        }

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/crawl/{job_id}/result", response_model=Dict[str, Any])
async def get_crawl_result(job_id: str):
    """
    Get the result of a completed crawl job
    """
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed yet. Current status: {job['status']}"
        )

    return {
        "job_id": job_id,
        "url": job["url"],
        "status": job["status"],
        "created_at": job["created_at"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "result": job["result"],
        "crawl_duration": (job["completed_at"] - job["started_at"]).total_seconds() if job["completed_at"] and job["started_at"] else None
    }


@router.delete("/crawl/{job_id}")
async def cancel_crawl(job_id: str):
    """
    Cancel a running crawl job
    """
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    if job["status"] in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in {job['status']} status"
        )

    # Mark job as cancelled
    job["status"] = JobStatus.CANCELLED
    job["completed_at"] = datetime.utcnow()

    return {
        "job_id": job_id,
        "status": job["status"],
        "message": "Job cancelled successfully"
    }
