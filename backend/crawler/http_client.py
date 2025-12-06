"""
Curl_cffi HTTP Client with TLS Fingerprinting
For faster requests when JavaScript rendering is not required
"""
from curl_cffi import requests
from typing import Optional, Dict, Any
from loguru import logger
from fake_useragent import UserAgent
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings


class HTTPClient:
    """
    HTTP Client with TLS fingerprinting using curl_cffi
    Much faster than browser automation when JS rendering not needed
    """

    def __init__(self, proxy: Optional[str] = None):
        self.proxy = proxy
        self.ua = UserAgent()
        self.session = None

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def start(self):
        """Initialize the session"""
        self.session = requests.Session()

    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()

    def get_random_user_agent(self) -> str:
        """Get a random realistic user agent"""
        return self.ua.random

    def get_impersonate_browser(self) -> str:
        """
        Get a random browser to impersonate
        Randomization helps avoid detection
        """
        # Using older Chrome versions that are universally supported
        browsers = [
            "chrome110",
            "chrome107",
            "chrome104",
            "chrome101",
            "chrome100",
            "chrome99"
        ]
        return random.choice(browsers)

    def build_headers(self, custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build realistic HTTP headers"""
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "User-Agent": self.get_random_user_agent()
        }

        # Merge custom headers
        if custom_headers:
            headers.update(custom_headers)

        return headers

    def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30,
        allow_redirects: bool = True,
        verify: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch a URL with TLS fingerprinting

        Args:
            url: Target URL
            method: HTTP method (GET, POST, etc.)
            headers: Custom headers
            data: POST data
            timeout: Request timeout
            allow_redirects: Follow redirects
            verify: Verify SSL certificates

        Returns:
            Dict with response data
        """
        try:
            logger.info(f"Fetching URL with curl_cffi: {url}")

            # Build headers
            request_headers = self.build_headers(headers)

            # Prepare proxy config
            proxies = None
            if self.proxy:
                proxies = {
                    "http": self.proxy,
                    "https": self.proxy
                }

            # Impersonate a real browser for TLS fingerprinting
            impersonate = self.get_impersonate_browser()

            # Make request
            if method.upper() == "GET":
                response = requests.get(
                    url,
                    headers=request_headers,
                    proxies=proxies,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                    verify=verify,
                    impersonate=impersonate
                )
            elif method.upper() == "POST":
                response = requests.post(
                    url,
                    headers=request_headers,
                    data=data,
                    proxies=proxies,
                    timeout=timeout,
                    allow_redirects=allow_redirects,
                    verify=verify,
                    impersonate=impersonate
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            # Build response dict
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.text,
                "url": response.url,
                "cookies": dict(response.cookies),
                "encoding": response.encoding,
                "elapsed": response.elapsed.total_seconds() if hasattr(response.elapsed, 'total_seconds') else 0
            }

            logger.info(f"Request successful: {response.status_code}")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """Convenience method for GET requests"""
        return self.fetch(url, method="GET", **kwargs)

    def post(self, url: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Convenience method for POST requests"""
        return self.fetch(url, method="POST", data=data, **kwargs)

    def test_proxy(self, test_url: str = "https://api.ipify.org?format=json") -> Optional[Dict[str, Any]]:
        """
        Test if the proxy is working
        Args:
            test_url: URL to test with

        Returns:
             Dict with IP info or None if failed
        """
        try:
            result = self.get(test_url, timeout=10)
            logger.info(f"Proxy test successful: {result['content']}")
            return result
        except Exception as e:
            logger.error(f"Proxy test failed: {str(e)}")
            return None
