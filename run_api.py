"""Day 5: Run the API Server"""
import sys
import asyncio

# CRITICAL: Set Windows event loop policy BEFORE anything else
# This is required for nodriver/browser automation subprocess to work on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn
from loguru import logger

if __name__ == "__main__":
    logger.info("Starting Crawler API Server...")
    logger.info("API will be available at: http://localhost:8000")
    logger.info("API Docs: http://localhost:8000/docs")

    # Note: reload=False is required on Windows for browser automation to work
    # The reload subprocess doesn't inherit the event loop policy
    # For development, restart the server manually after code changes
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False  # Must be False on Windows for nodriver to work
    )
