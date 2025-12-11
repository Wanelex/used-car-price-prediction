"""
Crawl API Routes
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
from datetime import datetime
import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from api.models.schemas import CrawlRequest, CrawlResponse, JobStatus, CrawlResult
from crawler.crawler import Crawler


router = APIRouter()


# Temporary in-memory storage (will be replaced with database)
jobs_storage: Dict[str, Dict[str, Any]] = {}


async def perform_crawl(job_id: str, request: CrawlRequest):
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
                "final_url": result.get("url"),
                "response_time": result.get("response_time"),
                "captcha_solved": result.get("captcha_solved", False),
                "method": result.get("method"),
                "crawl_duration": result.get("crawl_duration")
            }
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
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    Start a new crawl job

    This endpoint accepts a URL and configuration options, then starts a background
    crawl task. Returns a job ID that can be used to check status and retrieve results.
    """
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
        "retry_count": 0
    }

    # Add crawl task to background tasks
    background_tasks.add_task(perform_crawl, job_id, request)

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
