"""
Main FastAPI Application
"""
import sys
import asyncio

# CRITICAL: Set Windows event loop policy at module load time
# This is required for nodriver/browser automation subprocess to work on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from api.models.schemas import HealthCheck
from api.routes import crawl, jobs, listings


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting Bulletproof Web Crawler API...")
    print(f"API URL: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    yield
    # Shutdown
    print("Shutting down Bulletproof Web Crawler API...")


# Initialize FastAPI app
app = FastAPI(
    title="Bulletproof Web Crawler API",
    description="""
    A comprehensive web crawler with advanced anti-bot protection bypass capabilities.

    Features:
    - Stealth browser automation (Nodriver + Playwright)
    - Automatic CAPTCHA solving (2Captcha, Anti-Captcha)
    - Proxy rotation with validation
    - Browser fingerprint randomization
    - Human behavior simulation
    - Real-time progress updates via WebSocket
    - Full page content extraction (HTML, text, metadata, images, links)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(crawl.router, prefix="/api/v1", tags=["Crawling"])
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(listings.router, prefix="/api/v1", tags=["Listings"])


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "name": "Bulletproof Web Crawler API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    return HealthCheck(
        status="ok",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "api": True,
            "redis": False,  # Will be implemented later
            "mongodb": False,  # Will be implemented later
        }
    )


@app.websocket("/ws/progress/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job progress updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()

            # Send job progress (will be implemented with actual job monitoring)
            await websocket.send_json({
                "job_id": job_id,
                "status": "running",
                "progress": 50.0,
                "message": "Crawling in progress..."
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "detail": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
