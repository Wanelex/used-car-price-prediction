"""
Main FastAPI Application
"""

import sys
import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager

# -------------------------------------------------
# PATH FIX (IMPORTLARDAN ÖNCE)
# -------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -------------------------------------------------
# WINDOWS EVENT LOOP FIX (nodriver için)
# -------------------------------------------------
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# -------------------------------------------------
# FASTAPI IMPORTS
# -------------------------------------------------
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

# -------------------------------------------------
# PROJECT IMPORTS
# -------------------------------------------------
#from middleware.auth_middleware import AuthMiddleware
from config.settings import settings
from api.models.schemas import HealthCheck
from api.routes import jobs, listings

# -------------------------------------------------
# WEBSOCKET MANAGER
# -------------------------------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()

# -------------------------------------------------
# LIFESPAN
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(" Starting Bulletproof Web Crawler API")
    print(f" API: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f" Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    yield
    print(" Shutting down API")

# -------------------------------------------------
# FASTAPI APP
# -------------------------------------------------
app = FastAPI(
    title="CarVisor API",
    description="Firebase Auth protected API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# -------------------------------------------------
#  CORS (HER ZAMAN AUTH’TAN ÖNCE)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # local dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],          # Authorization dahil
)

# -------------------------------------------------
#  AUTH
# -------------------------------------------------
#app.add_middleware(AuthMiddleware)

# -------------------------------------------------
# ROUTERS
# -------------------------------------------------
app.include_router(jobs.router, prefix="/api/v1", tags=["Jobs"])
app.include_router(listings.router, prefix="/api/v1", tags=["Listings"])

# -------------------------------------------------
# ROOT
# -------------------------------------------------
@app.get("/")
async def root():
    return {
        "name": "CarVisor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }

# -------------------------------------------------
# HEALTH
# -------------------------------------------------
@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(
        status="ok",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "api": True,
            "redis": False,
            "mongodb": False,
        },
    )

# -------------------------------------------------
# WEBSOCKET
# -------------------------------------------------
@app.websocket("/ws/progress/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
            await websocket.send_json({
                "job_id": job_id,
                "status": "running",
                "progress": 50,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# -------------------------------------------------
# GLOBAL ERROR HANDLER
# -------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
        },
    )

# -------------------------------------------------
# SWAGGER AUTH ( Authorize BUTONU)
# -------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="CarVisor API",
        version="1.0.0",
        description="Firebase Auth protected API",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi

# -------------------------------------------------
# LOCAL RUN
# -------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
