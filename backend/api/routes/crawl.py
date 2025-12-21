"""
Crawl API Routes
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import uuid
from datetime import datetime

from api.models.schemas import (
    CrawlRequest,
    CrawlResponse,
    JobStatus,
)

from crawler.crawler import Crawler
from api.storage import jobs_storage   # ✅ TEK ve ORTAK STORAGE


router = APIRouter()


# ============================================================
# Background crawl task
# ============================================================

async def perform_crawl(job_id: str, request: CrawlRequest):
    """
    Background task that performs the actual crawl using the real Crawler.
    """
    crawler: Crawler | None = None

    try:
        # --- mark job as running
        jobs_storage[job_id]["status"] = JobStatus.RUNNING
        jobs_storage[job_id]["started_at"] = datetime.utcnow()

        # --- init crawler
        crawler = Crawler(
            use_stealth=request.use_stealth,
            use_proxy=request.use_proxy,
            solve_captcha=request.solve_captcha,
            headless=True,
        )
        await crawler.initialize()

        # --- run crawl
        result = await crawler.crawl(
            url=request.url,
            use_browser=True,
            wait_time=request.wait_time,
            wait_for_selector=request.wait_for_selector,
            custom_headers=request.custom_headers,
            max_retries=request.max_retries,
        )

        # --- handle result
        if result.get("status") == "success":
            jobs_storage[job_id]["status"] = JobStatus.COMPLETED
            jobs_storage[job_id]["result"] = {
                "html": result.get("html"),
                "text": result.get("text"),
                "title": result.get("title"),
                "metadata": result.get("metadata"),
                "images": result.get("images", []),
                "links": result.get("links", []),
                "sahibinden_listing": result.get("sahibinden_listing"),
                "final_url": result.get("url"),
                "response_time": result.get("response_time"),
                "captcha_solved": result.get("captcha_solved", False),
                "method": result.get("method"),
                "crawl_duration": result.get("crawl_duration"),
            }
        else:
            jobs_storage[job_id]["status"] = JobStatus.FAILED
            jobs_storage[job_id]["error_message"] = result.get(
                "error_message", "Unknown crawl error"
            )

        jobs_storage[job_id]["completed_at"] = datetime.utcnow()

    except Exception as e:
        jobs_storage[job_id]["status"] = JobStatus.FAILED
        jobs_storage[job_id]["error_message"] = str(e)
        jobs_storage[job_id]["completed_at"] = datetime.utcnow()

    finally:
        if crawler:
            await crawler.close()


# ============================================================
# API endpoints
# ============================================================

@router.post("/crawl", response_model=CrawlResponse)
async def start_crawl(
    request: CrawlRequest,
    background_tasks: BackgroundTasks,
):
    """
    Start a new crawl job (ASYNC – recommended).
    """
    job_id = str(uuid.uuid4())

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
    }

    background_tasks.add_task(perform_crawl, job_id, request)

    return CrawlResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Crawl job queued successfully",
        estimated_time=30,
    )


@router.get("/crawl/{job_id}/result")
async def get_crawl_result(job_id: str):
    """
    Get result of a completed crawl job.
    """
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    if job["status"] != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Job not completed yet (status: {job['status']})",
        )

    return {
        "job_id": job_id,
        "url": job["url"],
        "status": job["status"],
        "created_at": job["created_at"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
        "result": job["result"],
        "crawl_duration": (
            (job["completed_at"] - job["started_at"]).total_seconds()
            if job["completed_at"] and job["started_at"]
            else None
        ),
    }


@router.delete("/crawl/{job_id}")
async def cancel_crawl(job_id: str):
    """
    Cancel a running crawl job.
    """
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    if job["status"] in (JobStatus.COMPLETED, JobStatus.FAILED):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel job in {job['status']} state",
        )

    job["status"] = JobStatus.CANCELLED
    job["completed_at"] = datetime.utcnow()

    return {
        "job_id": job_id,
        "status": job["status"],
        "message": "Job cancelled successfully",
    }
