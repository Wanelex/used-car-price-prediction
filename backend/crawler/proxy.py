"""
Proxy Rotation and Management System
"""
from typing import List, Optional, Dict
import asyncio
from loguru import logger
import random
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.http_client import HTTPClient


class ProxyRotator:
    """
    Proxy rotation with validation and health monitoring
    """

    def __init__(self, proxies: List[str], test_url: str = "https://api.ipify.org?format=json"):
        self.proxies = proxies
        self.test_url = test_url
        self.valid_proxies: List[str] = []
        self.invalid_proxies: List[str] = []
        self.proxy_stats: Dict[str, Dict] = {}
        self.current_index = 0

    async def initialize(self):
        """Validate all proxies during initialization"""
        logger.info(f"Initializing proxy rotator with {len(self.proxies)} proxies...")

        if not self.proxies:
            logger.warning("No proxies provided!")
            return

        # Validate proxies
        await self.validate_all_proxies()

        logger.info(f"Proxy initialization complete: {len(self.valid_proxies)} valid, {len(self.invalid_proxies)} invalid")

    async def validate_proxy(self, proxy: str) -> bool:
        """
        Test if a proxy is working

        Args:
            proxy: Proxy string (e.g., "http://host:port" or "socks5://host:port")

        Returns:
            bool: Whether proxy is working
        """
        try:
            logger.debug(f"Testing proxy: {proxy}")

            with HTTPClient(proxy=proxy) as client:
                result = client.test_proxy(self.test_url)

                if result and result.get('status_code') == 200:
                    # Record stats
                    self.proxy_stats[proxy] = {
                        "last_tested": datetime.utcnow(),
                        "success_count": self.proxy_stats.get(proxy, {}).get("success_count", 0) + 1,
                        "fail_count": self.proxy_stats.get(proxy, {}).get("fail_count", 0),
                        "avg_response_time": result.get('elapsed', 0),
                        "ip": result.get('content', 'Unknown')
                    }

                    logger.success(f"Proxy valid: {proxy}")
                    return True

        except Exception as e:
            logger.error(f"Proxy validation failed for {proxy}: {str(e)}")

        # Record failure
        if proxy in self.proxy_stats:
            self.proxy_stats[proxy]["fail_count"] += 1
        else:
            self.proxy_stats[proxy] = {
                "last_tested": datetime.utcnow(),
                "success_count": 0,
                "fail_count": 1,
                "avg_response_time": 0,
                "ip": "Unknown"
            }

        return False

    async def validate_all_proxies(self):
        """Validate all proxies concurrently"""
        tasks = []
        for proxy in self.proxies:
            tasks.append(self.validate_proxy(proxy))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Categorize proxies
        for proxy, result in zip(self.proxies, results):
            if isinstance(result, bool) and result:
                self.valid_proxies.append(proxy)
            else:
                self.invalid_proxies.append(proxy)

    def get_next_proxy(self) -> Optional[str]:
        """
        Get the next proxy in rotation (round-robin)

        Returns:
            Proxy string or None if no valid proxies
        """
        if not self.valid_proxies:
            logger.warning("No valid proxies available!")
            return None

        proxy = self.valid_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.valid_proxies)

        return proxy

    def get_random_proxy(self) -> Optional[str]:
        """
        Get a random proxy

        Returns:
            Proxy string or None if no valid proxies
        """
        if not self.valid_proxies:
            logger.warning("No valid proxies available!")
            return None

        return random.choice(self.valid_proxies)

    def get_best_proxy(self) -> Optional[str]:
        """
        Get the best performing proxy based on stats

        Returns:
            Proxy string or None if no valid proxies
        """
        if not self.valid_proxies:
            return None

        # Sort by success rate and response time
        sorted_proxies = sorted(
            self.valid_proxies,
            key=lambda p: (
                self.proxy_stats.get(p, {}).get("success_count", 0) /
                max(self.proxy_stats.get(p, {}).get("fail_count", 1), 1),
                -self.proxy_stats.get(p, {}).get("avg_response_time", 999)
            ),
            reverse=True
        )

        return sorted_proxies[0] if sorted_proxies else None

    async def revalidate_invalid_proxies(self):
        """Retry validation for previously invalid proxies"""
        if not self.invalid_proxies:
            return

        logger.info(f"Revalidating {len(self.invalid_proxies)} invalid proxies...")

        to_retest = self.invalid_proxies.copy()
        self.invalid_proxies = []

        for proxy in to_retest:
            is_valid = await self.validate_proxy(proxy)
            if is_valid:
                self.valid_proxies.append(proxy)
            else:
                self.invalid_proxies.append(proxy)

    def mark_proxy_failed(self, proxy: str):
        """
        Mark a proxy as failed during actual use

        Args:
            proxy: The proxy that failed
        """
        if proxy in self.valid_proxies:
            logger.warning(f"Marking proxy as failed: {proxy}")
            self.valid_proxies.remove(proxy)
            self.invalid_proxies.append(proxy)

            if proxy in self.proxy_stats:
                self.proxy_stats[proxy]["fail_count"] += 1

    def get_stats(self) -> Dict:
        """Get proxy statistics"""
        return {
            "total_proxies": len(self.proxies),
            "valid_proxies": len(self.valid_proxies),
            "invalid_proxies": len(self.invalid_proxies),
            "proxy_details": self.proxy_stats
        }

    def add_proxy(self, proxy: str):
        """Add a new proxy to the pool"""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            logger.info(f"Added new proxy: {proxy}")

    def remove_proxy(self, proxy: str):
        """Remove a proxy from the pool"""
        if proxy in self.valid_proxies:
            self.valid_proxies.remove(proxy)
        if proxy in self.invalid_proxies:
            self.invalid_proxies.remove(proxy)
        if proxy in self.proxies:
            self.proxies.remove(proxy)
        if proxy in self.proxy_stats:
            del self.proxy_stats[proxy]

        logger.info(f"Removed proxy: {proxy}")


class ProxyManager:
    """
    High-level proxy management with automatic rotation strategies
    """

    def __init__(self, proxies: List[str]):
        self.rotator = ProxyRotator(proxies)
        self.strategy = "round_robin"  # Options: round_robin, random, best_performance

    async def initialize(self):
        """Initialize the proxy manager"""
        await self.rotator.initialize()

    def get_proxy(self) -> Optional[str]:
        """Get a proxy based on the current strategy"""
        if self.strategy == "round_robin":
            return self.rotator.get_next_proxy()
        elif self.strategy == "random":
            return self.rotator.get_random_proxy()
        elif self.strategy == "best_performance":
            return self.rotator.get_best_proxy()
        else:
            return self.rotator.get_next_proxy()

    def set_strategy(self, strategy: str):
        """Set the rotation strategy"""
        valid_strategies = ["round_robin", "random", "best_performance"]
        if strategy in valid_strategies:
            self.strategy = strategy
            logger.info(f"Proxy strategy set to: {strategy}")
        else:
            logger.error(f"Invalid strategy: {strategy}. Valid options: {valid_strategies}")

    async def health_check(self):
        """Perform health check on all proxies"""
        logger.info("Running proxy health check...")
        await self.rotator.revalidate_invalid_proxies()

    def get_stats(self) -> Dict:
        """Get proxy statistics"""
        return self.rotator.get_stats()
