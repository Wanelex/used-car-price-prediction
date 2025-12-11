"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CrawlRequest(BaseModel):
    """Request model for starting a crawl job"""
    url: str = Field(..., description="The URL to crawl")
    use_stealth: bool = Field(default=True, description="Enable stealth mode")
    use_proxy: bool = Field(default=False, description="Use proxy rotation")
    solve_captcha: bool = Field(default=True, description="Auto-solve CAPTCHAs")
    timeout: int = Field(default=30, description="Request timeout in seconds", ge=5, le=300)
    max_retries: int = Field(default=3, description="Maximum retry attempts", ge=0, le=10)
    wait_for_selector: Optional[str] = Field(default=None, description="CSS selector to wait for")
    wait_time: int = Field(default=0, description="Additional wait time in seconds after page load", ge=0, le=60)
    extract_images: bool = Field(default=True, description="Extract image URLs")
    extract_links: bool = Field(default=True, description="Extract all links")
    custom_headers: Optional[Dict[str, str]] = Field(default=None, description="Custom HTTP headers")


class CrawlResponse(BaseModel):
    """Response model after initiating a crawl"""
    job_id: str = Field(..., description="Unique job identifier")
    status: JobStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    estimated_time: Optional[int] = Field(default=None, description="Estimated completion time in seconds")


class JobInfo(BaseModel):
    """Job information model"""
    job_id: str
    url: str
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    progress: float = Field(default=0.0, ge=0.0, le=100.0)


class PageMetadata(BaseModel):
    """Metadata extracted from a web page"""
    title: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[List[str]] = None
    author: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None
    language: Optional[str] = None
    charset: Optional[str] = None


class CrawlResult(BaseModel):
    """Complete crawl result"""
    job_id: str
    url: str
    status: JobStatus
    timestamp: datetime

    # Page Content
    html: Optional[str] = Field(default=None, description="Full HTML content")
    text: Optional[str] = Field(default=None, description="Extracted text content")
    metadata: Optional[PageMetadata] = Field(default=None, description="Page metadata")

    # Extracted Data
    images: Optional[List[str]] = Field(default=None, description="List of image URLs")
    links: Optional[List[str]] = Field(default=None, description="List of all links")

    # Request Info
    final_url: Optional[str] = Field(default=None, description="Final URL after redirects")
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    response_time: Optional[float] = Field(default=None, description="Response time in seconds")

    # Crawl Stats
    crawl_duration: Optional[float] = Field(default=None, description="Total crawl duration in seconds")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    proxy_used: Optional[str] = Field(default=None, description="Proxy IP used")
    captcha_solved: bool = Field(default=False, description="Whether CAPTCHA was encountered and solved")

    # Error Info
    error_message: Optional[str] = None
    error_type: Optional[str] = None


class ProxyConfig(BaseModel):
    """Proxy configuration"""
    enabled: bool = False
    proxies: List[str] = []
    rotation_enabled: bool = True
    test_url: str = "https://api.ipify.org?format=json"


class CrawlerStats(BaseModel):
    """Overall crawler statistics"""
    total_jobs: int
    pending_jobs: int
    running_jobs: int
    completed_jobs: int
    failed_jobs: int
    success_rate: float
    average_response_time: float
    total_pages_crawled: int


class HealthCheck(BaseModel):
    """Health check response"""
    status: str = "ok"
    version: str = "1.0.0"
    timestamp: datetime
    services: Dict[str, bool] = Field(default_factory=dict)
