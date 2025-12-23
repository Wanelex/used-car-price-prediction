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


# ===== BUYABILITY ANALYSIS MODELS =====

class CarIdentification(BaseModel):
    """LLM-identified car components"""
    engine_code: str = Field(..., description="Specific engine code (e.g., N47D20, 2ZR-FE)")
    transmission_name: str = Field(..., description="Transmission name (e.g., ZF 8HP, Aisin U660E)")
    generation: Optional[str] = Field(None, description="Car generation (e.g., F30, W212)")


class ExpertAnalysis(BaseModel):
    """LLM expert analysis sections"""
    general_comment: str = Field(..., description="Overall assessment")
    engine_reliability: str = Field(..., description="Engine reliability analysis")
    transmission_reliability: str = Field(..., description="Transmission reliability analysis")
    km_endurance_check: str = Field(..., description="Mileage endurance assessment")


class Recommendation(BaseModel):
    """LLM buying recommendation"""
    verdict: str = Field(..., description="Detailed recommendation")
    buy_or_pass: str = Field(..., description="Clear verdict (High/Medium/Low Risk)")


class MechanicalScores(BaseModel):
    """LLM mechanical scores"""
    mechanical_score: int = Field(..., ge=0, le=100, description="Mechanical buyability score (0-100)")
    reasoning_for_score: str = Field(..., description="Score calculation reasoning")


class LLMMechanicalAnalysis(BaseModel):
    """Complete LLM mechanical analysis response"""
    car_identification: CarIdentification
    expert_analysis: ExpertAnalysis
    recommendation: Recommendation
    scores: MechanicalScores


class FeatureScore(BaseModel):
    """Individual feature contribution"""
    feature: str
    value: float
    importance: float


class StatisticalAnalysis(BaseModel):
    """Statistical buyability analysis (existing ML model)"""
    risk_score: int = Field(..., ge=0, le=100, description="Statistical risk score")
    decision: str = Field(..., description="BUYABLE or NOT BUYABLE")
    probability: float = Field(..., ge=0, le=1)
    health_score: float = Field(..., ge=0, le=1)
    risk_factors: List[str] = Field(default_factory=list)
    feature_scores: Dict[str, float] = Field(default_factory=dict)
    top_features: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str


class HybridAnalysisResponse(BaseModel):
    """Combined response with both statistical and LLM analysis"""
    status: str = Field(default="success")
    input: Dict[str, Any] = Field(..., description="Input parameters")
    statistical_analysis: StatisticalAnalysis = Field(..., description="ML-based statistical analysis")
    llm_analysis: Optional[LLMMechanicalAnalysis] = Field(None, description="LLM mechanical analysis (None if unavailable)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ===== CRASH SCORE MODELS =====

class PartDeduction(BaseModel):
    """Details of a single part deduction in crash score"""
    part_name: str = Field(..., description="Name of the part in Turkish")
    condition: str = Field(..., description="Condition: degisen, boyali, or lokal_boyali")
    deduction: int = Field(..., ge=0, description="Points deducted for this part")
    advice: str = Field(..., description="Expert advice for this specific part condition")


class CrashScoreAnalysis(BaseModel):
    """Crash score analysis based on painted/changed parts"""
    score: int = Field(..., ge=0, le=100, description="Crash score (100 = pristine, 0 = severe damage)")
    total_deduction: int = Field(..., ge=0, description="Total points deducted")
    deductions: List[PartDeduction] = Field(default_factory=list, description="List of individual part deductions")
    summary: str = Field(..., description="Overall summary of crash history")
    risk_level: str = Field(..., description="Risk level classification")
    verdict: str = Field(..., description="Final recommendation")


# ===== BUYABILITY SCORE MODELS =====

class ComponentScores(BaseModel):
    """Individual component scores used in buyability calculation"""
    statistical: Optional[int] = Field(None, ge=0, le=100, description="ML-based statistical health score")
    mechanical: Optional[int] = Field(None, ge=0, le=100, description="LLM-based mechanical reliability score")
    crash: Optional[int] = Field(None, ge=0, le=100, description="Rule-based crash/damage score")


class CalculationBreakdown(BaseModel):
    """Breakdown of buyability score calculation"""
    weighted_average: float = Field(..., description="Initial weighted average of component scores")
    min_score: int = Field(..., description="Minimum of all component scores")
    blended_score: float = Field(..., description="Score after min pull and GM dampener")
    penalty_applied: int = Field(..., ge=0, description="Penalty points deducted for low scores")
    bonus_applied: int = Field(..., ge=0, description="Bonus points added for safe cars")


class BuyabilityScore(BaseModel):
    """
    Comprehensive buyability score combining all three analyses.

    Formula:
    1. Weighted average: S*0.25 + M*0.40 + C*0.35
    2. Min pull: blend with min_score (alpha=0.30)
    3. GM dampener: penalize imbalance (beta=0.05)
    4. Critical failure penalties
    5. Tier classification
    """
    final_score: int = Field(..., ge=0, le=100, description="Final buyability score (0-100)")
    tier: str = Field(..., description="Tier classification (KACIN, RISKLI, DIKKAT, NORMAL, GUVENLI)")
    tier_label_tr: str = Field(..., description="Turkish label for the tier")
    component_scores: ComponentScores = Field(..., description="Individual component scores")
    calculation_breakdown: CalculationBreakdown = Field(..., description="Calculation details")
    calculation_summary: str = Field(..., description="Human-readable calculation summary")
    warning_message: Optional[str] = Field(None, description="Warning if any score is critically low")
