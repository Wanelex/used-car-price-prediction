"""
Rate Limiting System
Per-domain rate limiting to avoid being blocked
"""
import time
import asyncio
from typing import Dict, Optional
from urllib.parse import urlparse
from loguru import logger
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


class RateLimiter:
    """
    Token bucket rate limiter with per-domain tracking
    """

    def __init__(self):
        # Store last request time and request count per domain
        self.domain_data: Dict[str, Dict] = {}
        self.default_rate_limit = settings.DEFAULT_RATE_LIMIT
        self.rate_limit_window = settings.RATE_LIMIT_WINDOW

    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc or parsed.path
        except Exception:
            return url

    async def wait_if_needed(self, url: str, rate_limit: Optional[int] = None):
        """
        Wait if rate limit is exceeded

        Args:
            url: Target URL
            rate_limit: Custom rate limit for this domain (requests per window)
        """
        domain = self.get_domain(url)
        rate_limit = rate_limit or self.default_rate_limit

        # Initialize domain data if not exists
        if domain not in self.domain_data:
            self.domain_data[domain] = {
                "request_count": 0,
                "window_start": time.time(),
                "last_request": 0
            }

        data = self.domain_data[domain]
        current_time = time.time()

        # Reset window if needed
        if current_time - data["window_start"] >= self.rate_limit_window:
            data["request_count"] = 0
            data["window_start"] = current_time

        # Check if rate limit exceeded
        if data["request_count"] >= rate_limit:
            wait_time = self.rate_limit_window - (current_time - data["window_start"])
            if wait_time > 0:
                logger.warning(f"Rate limit reached for {domain}. Waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)
                # Reset after waiting
                data["request_count"] = 0
                data["window_start"] = time.time()

        # Increment request count
        data["request_count"] += 1
        data["last_request"] = current_time

    def get_stats(self, domain: Optional[str] = None) -> Dict:
        """
        Get rate limiting statistics

        Args:
            domain: Specific domain or None for all

        Returns:
            Statistics dictionary
        """
        if domain:
            return self.domain_data.get(domain, {})

        return {
            "domains": len(self.domain_data),
            "data": self.domain_data
        }

    def reset_domain(self, domain: str):
        """Reset rate limit for a specific domain"""
        if domain in self.domain_data:
            del self.domain_data[domain]
            logger.info(f"Rate limit reset for domain: {domain}")

    def reset_all(self):
        """Reset all rate limits"""
        self.domain_data.clear()
        logger.info("All rate limits reset")


class AdaptiveRateLimiter(RateLimiter):
    """
    Adaptive rate limiter that adjusts based on response codes
    """

    def __init__(self):
        super().__init__()
        self.domain_limits: Dict[str, int] = {}

    async def wait_if_needed(self, url: str, rate_limit: Optional[int] = None):
        """Wait with adaptive rate limiting"""
        domain = self.get_domain(url)

        # Use adaptive limit if available
        if domain in self.domain_limits:
            rate_limit = self.domain_limits[domain]

        await super().wait_if_needed(url, rate_limit)

    def adjust_for_response(self, url: str, status_code: int):
        """
        Adjust rate limit based on response

        Args:
            url: The URL that was requested
            status_code: HTTP response status code
        """
        domain = self.get_domain(url)
        current_limit = self.domain_limits.get(domain, self.default_rate_limit)

        # Rate limited (429) or Too Many Requests
        if status_code == 429:
            new_limit = max(1, current_limit // 2)
            self.domain_limits[domain] = new_limit
            logger.warning(f"Rate limit hit for {domain}. Reducing to {new_limit} req/min")

        # Successful response - gradually increase
        elif status_code == 200:
            # Increase limit by 10% (max 2x default)
            new_limit = min(self.default_rate_limit * 2, int(current_limit * 1.1))
            if new_limit != current_limit:
                self.domain_limits[domain] = new_limit
                logger.info(f"Increasing rate limit for {domain} to {new_limit} req/min")

        # Server errors - be more conservative
        elif 500 <= status_code < 600:
            new_limit = max(1, current_limit // 3)
            self.domain_limits[domain] = new_limit
            logger.warning(f"Server error for {domain}. Reducing to {new_limit} req/min")


# Global rate limiter instance
rate_limiter = AdaptiveRateLimiter()
