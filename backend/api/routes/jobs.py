"""
Jobs Management API Routes
"""

from fastapi import APIRouter, Depends, Request, HTTPException, Query
from typing import List, Optional
from middleware.auth_middleware import auth_middleware

#from api.middlewares.auth_middleware import auth_middleware
from api.models.schemas import JobInfo, JobStatus
from datetime import datetime
from pydantic import BaseModel
import uuid
import sys
import os
from fastapi import BackgroundTasks
import asyncio


# Add parent directories to path
#sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
#from api.storage import jobs_storage

from api.models.schemas import JobInfo, JobStatus, CrawlerStats
#from api.routes.crawl import jobs_storage
class JobCreate(BaseModel):
    url: str

jobs_storage = {}  # TEMP: crawler disabled

#router = APIRouter()

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
    dependencies=[Depends(auth_middleware)]  
)
@router.post("", response_model=JobInfo)
async def create_job(
    payload: JobCreate,
    request: Request,
    background_tasks: BackgroundTasks
):

    """
    Create a new crawl job
    """
    job_id = str(uuid.uuid4())
    now = datetime.utcnow()

    job = {
        "job_id": job_id,
        "url": payload.url,
        "status": JobStatus.PENDING,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "error_message": None,
        "retry_count": 0,
        "user_id": request.state.user_id,  # 🔐 auth_middleware'den geliyor
    }

    jobs_storage[job_id] = job
    background_tasks.add_task(run_fake_crawler, job_id)

    return JobInfo(
        job_id=job_id,
        url=job["url"],
        status=job["status"],
        created_at=job["created_at"],
        started_at=None,
        completed_at=None,
        error_message=None,
        retry_count=0,
        progress=0.0
    )

@router.get("", response_model=list[JobInfo])
async def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip")
):
    """
    List all crawl jobs with optional filtering
    """
    jobs = list(jobs_storage.values())

    # Filter by status if provided
    if status:
        jobs = [job for job in jobs if job["status"] == status]

    # Sort by created_at descending (newest first)
    jobs.sort(key=lambda x: x["created_at"], reverse=True)

    # Apply pagination
    jobs = jobs[offset:offset + limit]

    # Convert to JobInfo model
    result = []
    for job in jobs:
        result.append(JobInfo(
            job_id=job["job_id"],
            url=job["url"],
            status=job["status"],
            created_at=job["created_at"],
            started_at=job.get("started_at"),
            completed_at=job.get("completed_at"),
            error_message=job.get("error_message"),
            retry_count=job.get("retry_count", 0),
            progress=calculate_progress(job)
        ))

    return result


@router.get("/{job_id}", response_model=JobInfo)
async def get_job(job_id: str):
    """
    Get detailed information about a specific job
    """
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    return JobInfo(
        job_id=job["job_id"],
        url=job["url"],
        status=job["status"],
        created_at=job["created_at"],
        started_at=job.get("started_at"),
        completed_at=job.get("completed_at"),
        error_message=job.get("error_message"),
        retry_count=job.get("retry_count", 0),
        progress=calculate_progress(job)
    )


@router.get("/{job_id}/status")
async def get_job_status(job_id: str):
    """
    Get the current status of a job
    """
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_storage[job_id]

    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": calculate_progress(job),
        "message": get_status_message(job)
    }


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job and its results
    """
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Job not found")

    del jobs_storage[job_id]

    return {
        "job_id": job_id,
        "message": "Job deleted successfully"
    }


@router.delete("")
async def delete_all_jobs(
    status: Optional[JobStatus] = Query(None, description="Delete only jobs with this status")
):
    """
    Delete multiple jobs

    WARNING: Use with caution
    """
    if status:
        # Delete only jobs with specific status
        to_delete = [job_id for job_id, job in jobs_storage.items() if job["status"] == status]
    else:
        # Delete all jobs
        to_delete = list(jobs_storage.keys())

    for job_id in to_delete:
        del jobs_storage[job_id]

    return {
        "message": f"Deleted {len(to_delete)} jobs",
        "deleted_count": len(to_delete)
    }


@router.get("/stats", response_model=CrawlerStats)
async def get_stats():
    """
    Get overall crawler statistics
    """
    jobs = list(jobs_storage.values())

    total_jobs = len(jobs)
    pending_jobs = sum(1 for job in jobs if job["status"] == JobStatus.PENDING)
    running_jobs = sum(1 for job in jobs if job["status"] == JobStatus.RUNNING)
    completed_jobs = sum(1 for job in jobs if job["status"] == JobStatus.COMPLETED)
    failed_jobs = sum(1 for job in jobs if job["status"] == JobStatus.FAILED)

    success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0.0

    # Calculate average response time
    response_times = []
    for job in jobs:
        if job["status"] == JobStatus.COMPLETED and job.get("started_at") and job.get("completed_at"):
            duration = (job["completed_at"] - job["started_at"]).total_seconds()
            response_times.append(duration)

    average_response_time = sum(response_times) / len(response_times) if response_times else 0.0

    return CrawlerStats(
        total_jobs=total_jobs,
        pending_jobs=pending_jobs,
        running_jobs=running_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        success_rate=success_rate,
        average_response_time=average_response_time,
        total_pages_crawled=completed_jobs
    )


def calculate_progress(job: dict) -> float:
    """Calculate job progress percentage"""
    status = job["status"]

    if status == JobStatus.PENDING:
        return 0.0
    elif status == JobStatus.RUNNING:
        # Could be enhanced with actual task progress
        return 50.0
    elif status in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
        return 100.0
    elif status == JobStatus.FAILED:
        return 100.0  # Failed but processing complete

    return 0.0


def get_status_message(job: dict) -> str:
    """Get human-readable status message"""
    status = job["status"]

    messages = {
        JobStatus.PENDING: "Job is queued and waiting to start",
        JobStatus.RUNNING: "Crawling in progress...",
        JobStatus.COMPLETED: "Crawl completed successfully",
        JobStatus.FAILED: f"Crawl failed: {job.get('error_message', 'Unknown error')}",
        JobStatus.CANCELLED: "Job was cancelled by user"
    }

    return messages.get(status, "Unknown status")
async def run_fake_crawler(job_id: str):
    """
    Simulates a crawler process
    """
    # RUNNING
    jobs_storage[job_id]["status"] = JobStatus.RUNNING
    jobs_storage[job_id]["started_at"] = datetime.utcnow()

    # simulate crawling
    await asyncio.sleep(5)

    # COMPLETED
    jobs_storage[job_id]["status"] = JobStatus.COMPLETED
    jobs_storage[job_id]["completed_at"] = datetime.utcnow()
