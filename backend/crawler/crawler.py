"""
Main Crawler Orchestrator
Coordinates all crawler components with anti-bot protection
"""
import asyncio
import random
from typing import Optional, Dict, Any
from loguru import logger
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crawler.engine import BrowserEngine
from crawler.http_client import HTTPClient
from crawler.extractor import ContentExtractor
from crawler.proxy import ProxyManager
from crawler.bypass.captcha import CaptchaSolver, CaptchaDetector
from crawler.parsers.sahibinden_parser import parse_sahibinden_listing
from utils.rate_limiter import rate_limiter
from config.settings import settings


class Crawler:
    """
    Main crawler class with full anti-bot protection
    """

    def __init__(
        self,
        use_stealth: bool = True,
        use_proxy: bool = False,
        solve_captcha: bool = True,
        headless: bool = True
    ):
        self.use_stealth = use_stealth
        self.use_proxy = use_proxy
        self.solve_captcha = solve_captcha
        self.headless = headless

        # Components
        self.browser: Optional[BrowserEngine] = None
        self.http_client: Optional[HTTPClient] = None
        self.proxy_manager: Optional[ProxyManager] = None
        self.captcha_solver: Optional[CaptchaSolver] = None

        # Initialize proxy manager if enabled
        if self.use_proxy and settings.PROXY_LIST:
            self.proxy_manager = ProxyManager(settings.PROXY_LIST)

        # Initialize CAPTCHA solver if enabled
        if self.solve_captcha:
            self.captcha_solver = CaptchaSolver()

    async def initialize(self):
        """Initialize crawler components"""
        logger.info("Initializing crawler...")

        # Initialize proxy manager
        if self.proxy_manager:
            await self.proxy_manager.initialize()

    async def crawl(
        self,
        url: str,
        use_browser: bool = True,
        wait_time: int = 0,
        wait_for_selector: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Main crawl method with full anti-bot protection

        Args:
            url: Target URL
            use_browser: Use browser automation (True) or HTTP client (False)
            wait_time: Additional wait time after page load
            wait_for_selector: CSS selector to wait for
            custom_headers: Custom HTTP headers
            max_retries: Maximum retry attempts

        Returns:
            Crawl result dictionary
        """
        start_time = datetime.utcnow()
        attempt = 0
        last_error = None

        logger.info(f"Starting crawl: {url}")

        while attempt < max_retries:
            try:
                attempt += 1
                logger.info(f"Crawl attempt {attempt}/{max_retries}")

                # Apply rate limiting
                await rate_limiter.wait_if_needed(url)

                # Get proxy if enabled
                proxy = None
                if self.proxy_manager:
                    proxy = self.proxy_manager.get_proxy()
                    logger.info(f"Using proxy: {proxy}")

                # Choose crawling method
                if use_browser or self.use_stealth:
                    result = await self._crawl_with_browser(
                        url=url,
                        proxy=proxy,
                        wait_time=wait_time,
                        wait_for_selector=wait_for_selector
                    )
                else:
                    result = await self._crawl_with_http(
                        url=url,
                        proxy=proxy,
                        headers=custom_headers
                    )

                # Calculate crawl duration
                end_time = datetime.utcnow()
                crawl_duration = (end_time - start_time).total_seconds()

                # Add metadata
                result["crawl_duration"] = crawl_duration
                result["retry_count"] = attempt - 1
                result["timestamp"] = end_time.isoformat()
                result["proxy_used"] = proxy

                logger.success(f"Crawl successful: {url} (took {crawl_duration:.2f}s)")
                return result

            except Exception as e:
                last_error = str(e)
                logger.error(f"Crawl attempt {attempt} failed: {last_error}")

                # Mark proxy as failed if used
                if self.proxy_manager and proxy:
                    logger.warning(f"Marking proxy as failed: {proxy}")
                    self.proxy_manager.rotator.mark_proxy_failed(proxy)

                    # Try to get a different proxy for next attempt
                    if attempt < max_retries:
                        new_proxy = self.proxy_manager.get_proxy()
                        if new_proxy and new_proxy != proxy:
                            logger.info(f"Switching to different proxy for retry: {new_proxy}")

                # Wait before retry (exponential backoff with jitter)
                if attempt < max_retries:
                    # Exponential backoff: 2, 4, 8, 16... seconds (capped at 60)
                    base_wait = min(settings.RETRY_DELAY * (2 ** (attempt - 1)), 60)

                    # Add random jitter (±25%) to avoid thundering herd
                    jitter = base_wait * 0.25 * (2 * random.random() - 1)
                    wait_time = base_wait + jitter

                    logger.info(f"Waiting {wait_time:.1f}s before retry (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(wait_time)

                    # Every 3rd retry, try health check on proxies
                    if attempt % 3 == 0 and self.proxy_manager:
                        logger.info("Running proxy health check...")
                        await self.proxy_manager.health_check()

        # All attempts failed
        logger.error(f"All crawl attempts failed for {url}")
        return {
            "url": url,
            "status": "failed",
            "error_message": last_error,
            "timestamp": datetime.utcnow().isoformat(),
            "retry_count": max_retries
        }

    async def _crawl_with_browser(
        self,
        url: str,
        proxy: Optional[str] = None,
        wait_time: int = 0,
        wait_for_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """Crawl using browser automation (Nodriver)"""
        logger.info("Crawling with browser automation (Nodriver)...")

        async with BrowserEngine(headless=self.headless, use_proxy=proxy) as browser:
            # Navigate to URL
            success = await browser.navigate(url, wait_time=wait_time)
            if not success:
                raise Exception("Navigation failed")

            # Wait for specific element if requested
            if wait_for_selector:
                logger.info(f"Waiting for selector: {wait_for_selector}")
                await browser.wait_for_selector(wait_for_selector)

            # Check for CAPTCHA - use unified detector
            captcha_detected = await browser.check_for_captcha()
            captcha_solved = False
            captcha_type = None

            if captcha_detected and self.captcha_solver:
                logger.warning("CAPTCHA detected! Waiting for CAPTCHA widget to load...")

                # Wait for Turnstile widget to load (it uses defer so takes time)
                # Give it more time to fully render
                logger.info("Waiting 5 seconds for widget to fully load...")
                await asyncio.sleep(5)

                # Try waiting for the widget using simple polling
                widget_loaded = False
                for attempt in range(10):  # 10 attempts, 1 second apart
                    try:
                        has_widget = await browser.page.evaluate("""
                            () => {
                                return !!(
                                    document.querySelector('#turnStileWidget') ||
                                    document.querySelector('iframe[src*="challenges.cloudflare.com"]') ||
                                    document.querySelector('.g-recaptcha') ||
                                    document.querySelector('.h-captcha')
                                );
                            }
                        """)
                        if has_widget:
                            widget_loaded = True
                            logger.info("CAPTCHA widget detected in DOM")
                            break
                    except Exception as e:
                        logger.debug(f"Widget check attempt {attempt + 1} failed: {str(e)}")

                    await asyncio.sleep(1)

                if not widget_loaded:
                    logger.warning("Widget not found in DOM after 10 seconds, but continuing anyway")

                # Use comprehensive CAPTCHA detection
                logger.info("Identifying CAPTCHA type...")

                # Extract sitekey directly from HTML (nodriver's page.evaluate() has issues)
                manual_sitekey = None
                try:
                    # Get current URL
                    current_url = browser.page.url
                    logger.info(f"Current page URL: {current_url}")

                    # Get HTML to check if sitekey is in the source
                    html = await browser.page.evaluate("document.documentElement.outerHTML")
                    if html and 'sitekeyEnterprise' in html:
                        import re
                        match = re.search(r'id="sitekeyEnterprise"[^>]*value="([^"]+)"', html)
                        if match:
                            manual_sitekey = match.group(1)
                            logger.success(f"Manually extracted sitekey from HTML: {manual_sitekey}")
                        else:
                            logger.warning("sitekeyEnterprise element found but couldn't extract value")
                    elif html and ('turnstile' in html.lower() or 'cloudflare' in html.lower()):
                        logger.warning("sitekeyEnterprise not found but Turnstile detected in HTML")
                except Exception as e:
                    logger.error(f"Could not extract manual sitekey: {str(e)}")

                # Try automatic detection first
                captcha_info = await CaptchaDetector.detect_any_captcha(browser.page)

                # If automatic detection failed but we have manual sitekey, use it
                if not captcha_info and manual_sitekey:
                    logger.info("Automatic detection failed, using manually extracted sitekey")
                    captcha_info = {
                        "type": "cloudflare_turnstile",
                        "sitekey": manual_sitekey,
                        "url": current_url,
                        "source": "manual_extraction"
                    }

                if captcha_info:
                    captcha_type = captcha_info["type"]
                    logger.info(f"CAPTCHA type identified: {captcha_type}")
                    logger.info(f"Sitekey: {captcha_info.get('sitekey', 'N/A')}")
                    logger.info(f"URL: {captcha_info.get('url', 'N/A')}")

                    solution = None

                    # Handle different CAPTCHA types
                    if captcha_type == "cloudflare_turnstile":
                        logger.warning("Cloudflare Turnstile detected - solving...")
                        logger.info(f"Sending to 2Captcha: sitekey={captcha_info['sitekey']}")
                        solution = self.captcha_solver.solve_cloudflare_turnstile(
                            sitekey=captcha_info["sitekey"],
                            url=captcha_info["url"]
                        )

                        if solution:
                            logger.success(f"Got solution from 2Captcha: {solution[:50]}...")
                            logger.success("Turnstile solved! Injecting solution...")
                            captcha_solved = await browser.inject_turnstile_solution(solution)
                            if captcha_solved:
                                logger.success("Turnstile solution injected successfully!")
                                # Wait for page to process and redirect
                                await asyncio.sleep(5)
                            else:
                                logger.error("Failed to inject Turnstile solution")

                    elif captcha_type == "recaptcha_v2":
                        logger.warning("reCAPTCHA v2 detected - solving...")
                        solution = self.captcha_solver.solve_recaptcha_v2(
                            sitekey=captcha_info["sitekey"],
                            url=captcha_info["url"]
                        )

                        if solution:
                            logger.success("reCAPTCHA v2 solved!")
                            # Inject reCAPTCHA solution
                            await browser.page.evaluate(f"""
                                document.getElementById('g-recaptcha-response').innerHTML = '{solution}';
                            """)
                            captcha_solved = True

                    elif captcha_type == "recaptcha_v3":
                        logger.warning("reCAPTCHA v3 detected - solving...")
                        solution = self.captcha_solver.solve_recaptcha_v3(
                            sitekey=captcha_info["sitekey"],
                            url=captcha_info["url"]
                        )
                        if solution:
                            logger.success("reCAPTCHA v3 solved!")
                            captcha_solved = True

                    elif captcha_type == "hcaptcha":
                        logger.warning("hCaptcha detected - solving...")
                        solution = self.captcha_solver.solve_hcaptcha(
                            sitekey=captcha_info["sitekey"],
                            url=captcha_info["url"]
                        )
                        if solution:
                            logger.success("hCaptcha solved!")
                            captcha_solved = True

                    if not solution:
                        logger.error(f"Failed to solve {captcha_type} - 2Captcha may have timed out or returned an error")
                else:
                    logger.warning("CAPTCHA detected but could not identify type or extract sitekey")
                    logger.warning("Check that the CAPTCHA widget has loaded properly")

            # Extract page content
            page_data = await browser.get_page_content()

            # Parse and extract structured data
            extractor = ContentExtractor(page_data["html"], page_data["url"])
            extracted_data = extractor.extract_all()

            # Check if this is a sahibinden.com car listing and parse it
            sahibinden_data = None
            if "sahibinden.com" in page_data["url"] and "/ilan/vasita" in page_data["url"]:
                logger.info("Detected sahibinden.com car listing - using specialized parser")
                try:
                    sahibinden_data = parse_sahibinden_listing(page_data["html"], page_data["url"])
                    if sahibinden_data:
                        logger.success(f"Extracted structured data for listing: {sahibinden_data.get('ilan_no', 'Unknown')}")
                except Exception as e:
                    logger.error(f"Failed to parse sahibinden.com listing: {str(e)}")

            # Combine data
            result = {
                "url": page_data["url"],
                "status": "success",
                "html": page_data["html"],
                "text": extracted_data["text"],
                "title": extracted_data["title"],
                "metadata": extracted_data["metadata"],
                "images": [img["src"] for img in extracted_data["images"]],
                "links": [link["href"] for link in extracted_data["links"]],
                "headings": extracted_data["headings"],
                "captcha_detected": captcha_detected,
                "captcha_solved": captcha_solved,
                "method": "browser"
            }

            # Add sahibinden structured data if available
            if sahibinden_data:
                result["sahibinden_listing"] = sahibinden_data

            return result

    async def _crawl_with_http(
        self,
        url: str,
        proxy: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Crawl using HTTP client (curl_cffi)"""
        logger.info("Crawling with HTTP client (curl_cffi)...")

        with HTTPClient(proxy=proxy) as client:
            # Fetch page
            response = client.get(url, headers=headers)

            # Check status code
            if response["status_code"] != 200:
                logger.warning(f"Non-200 status code: {response['status_code']}")

            # Adjust rate limiter based on response
            rate_limiter.adjust_for_response(url, response["status_code"])

            # Extract content
            html = response["content"]
            extractor = ContentExtractor(html, response["url"])
            extracted_data = extractor.extract_all()

            # Combine data
            result = {
                "url": response["url"],
                "status": "success",
                "status_code": response["status_code"],
                "html": html,
                "text": extracted_data["text"],
                "title": extracted_data["title"],
                "metadata": extracted_data["metadata"],
                "images": [img["src"] for img in extracted_data["images"]],
                "links": [link["href"] for link in extracted_data["links"]],
                "headings": extracted_data["headings"],
                "response_time": response["elapsed"],
                "method": "http"
            }

            return result

    async def close(self):
        """Clean up resources"""
        logger.info("Closing crawler...")
        # Cleanup if needed


# Convenience function
async def crawl_url(
    url: str,
    use_stealth: bool = True,
    use_proxy: bool = False,
    solve_captcha: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to crawl a single URL

    Args:
        url: Target URL
        use_stealth: Use stealth mode
        use_proxy: Use proxy rotation
        solve_captcha: Auto-solve CAPTCHAs
        **kwargs: Additional arguments for crawl()

    Returns:
        Crawl result
    """
    crawler = Crawler(
        use_stealth=use_stealth,
        use_proxy=use_proxy,
        solve_captcha=solve_captcha
    )

    await crawler.initialize()

    try:
        result = await crawler.crawl(url, **kwargs)
        return result
    finally:
        await crawler.close()
