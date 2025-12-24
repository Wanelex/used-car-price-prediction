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


class CloudflareDetectedError(Exception):
    """
    Raised when Cloudflare detects and blocks the crawl.
    This error indicates the site has detected bot behavior and
    the CAPTCHA cannot be solved automatically.
    """
    pass


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
        is_cloudflare_blocked = False

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

            except CloudflareDetectedError as e:
                last_error = str(e)
                is_cloudflare_blocked = True
                logger.warning(f"Cloudflare blocked crawl attempt {attempt}/{max_retries}: {last_error}")

                # For Cloudflare blocks, use longer backoff since the site has detected us
                if attempt < max_retries:
                    # Longer wait for Cloudflare: 10, 20, 40 seconds
                    base_wait = min(10 * (2 ** (attempt - 1)), 60)
                    jitter = base_wait * 0.25 * (2 * random.random() - 1)
                    wait_time = base_wait + jitter

                    logger.info(f"Cloudflare detected - waiting {wait_time:.1f}s before retry (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                last_error = str(e)
                is_cloudflare_blocked = False
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

        # Return user-friendly error for Cloudflare detection
        if is_cloudflare_blocked:
            return {
                "url": url,
                "status": "cloudflare_blocked",
                "error_message": "Listing site detected the crawl, try again.",
                "error_type": "cloudflare_detection",
                "timestamp": datetime.utcnow().isoformat(),
                "retry_count": max_retries
            }

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
                                    document.querySelector('[id*="turnstile"]') ||
                                    document.querySelector('[id*="cf-"]') ||
                                    document.querySelector('iframe[src*="challenges.cloudflare.com"]') ||
                                    document.querySelector('iframe[src*="turnstile"]') ||
                                    document.querySelector('.cf-turnstile') ||
                                    document.querySelector('[class*="turnstile"]') ||
                                    document.querySelector('.g-recaptcha') ||
                                    document.querySelector('.h-captcha') ||
                                    document.querySelector('[data-sitekey]')
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

                # Detect challenge type based on page text
                try:
                    challenge_info = await browser.page.evaluate("""
                        () => {
                            const bodyText = document.body.innerText || '';
                            const isManaged = bodyText.includes('Aşağıdaki işlemi tamamlayarak') ||
                                             bodyText.includes('Verify you are human');
                            const isRedirect = bodyText.includes('Tarayıcınızı kontrol ediyoruz') ||
                                              bodyText.includes('Checking your browser');
                            const isSolved = bodyText.includes('Doğrulama başarılı') ||
                                            bodyText.includes('Verification successful');
                            return { isManaged: isManaged, isRedirect: isRedirect, isSolved: isSolved };
                        }
                    """)
                except Exception as e:
                    logger.warning(f"Failed to detect challenge type: {e}")
                    challenge_info = {}

                is_managed_challenge = challenge_info.get('isManaged', False) if challenge_info else False
                is_already_solved = challenge_info.get('isSolved', False) if challenge_info else False

                if is_managed_challenge:
                    logger.info("Detected MANAGED challenge (inline) - waiting for auto-solve...")
                    # Managed challenges often auto-solve, wait longer for them
                    for auto_solve_attempt in range(15):  # Wait up to 30 seconds
                        await asyncio.sleep(2)
                        try:
                            check_result = await browser.page.evaluate("""
                                () => {
                                    const bodyText = document.body.innerText || '';
                                    return {
                                        solved: bodyText.includes('Doğrulama başarılı') || bodyText.includes('Verification successful'),
                                        stillChallenge: bodyText.includes('Aşağıdaki işlemi') || bodyText.includes('Verify you are human')
                                    };
                                }
                            """)
                            if not check_result:
                                check_result = {}
                        except Exception as e:
                            logger.debug(f"Check failed: {e}")
                            check_result = {}

                        if check_result.get('solved'):
                            is_already_solved = True
                            logger.success(f"Managed challenge auto-solved! (attempt {auto_solve_attempt + 1})")
                            break
                        if not check_result.get('stillChallenge', True):
                            # Page changed, might have redirected
                            logger.info("Challenge page changed, checking if redirected...")
                            break
                        logger.debug(f"Waiting for managed challenge to auto-solve... attempt {auto_solve_attempt + 1}")

                if is_already_solved:
                    logger.success("CAPTCHA solved! Waiting for redirect...")
                    captcha_solved = True

                    # Try clicking any continue button first
                    try:
                        clicked = await browser.page.evaluate("""
                            () => {
                                const btn = document.querySelector('button, input[type="submit"], .ctp-button');
                                if (btn) { btn.click(); return true; }
                                return false;
                            }
                        """)
                        if clicked:
                            logger.info("Clicked continue button")
                    except:
                        pass

                    # Wait for page to redirect
                    original_url = browser.page.url
                    for redirect_attempt in range(15):
                        await asyncio.sleep(2)
                        new_url = browser.page.url
                        page_text = await browser.page.evaluate("document.body.innerText || ''")

                        # Check if URL changed or page content changed
                        if new_url != original_url:
                            if 'Doğrulama başarılı' not in page_text and 'Verification successful' not in page_text:
                                logger.success(f"Redirected to: {new_url}")
                                break

                        # Check if we're now on the actual content page
                        if 'challenge' not in new_url.lower() and 'tloading' not in new_url.lower():
                            if 'Aşağıdaki işlemi' not in page_text:
                                logger.success(f"Page loaded: {new_url}")
                                break

                        logger.debug(f"Waiting for redirect... attempt {redirect_attempt + 1}")
                    else:
                        logger.warning("Page didn't redirect after CAPTCHA solved, continuing anyway")

                # Use comprehensive CAPTCHA detection
                if not captcha_solved:
                    logger.info("Identifying CAPTCHA type...")

                    # Extract sitekey directly from HTML (nodriver's page.evaluate() has issues)
                    manual_sitekey = None
                    try:
                        import re
                        # Get current URL
                        current_url = browser.page.url
                        logger.info(f"Current page URL: {current_url}")

                        # Method 0: Wait for Turnstile iframe to be created dynamically
                        # For managed challenges, the sitekey is in the iframe src after JS executes
                        logger.info("Waiting for Turnstile iframe to be created...")
                        for iframe_attempt in range(5):  # 5 attempts, 2 seconds apart
                            try:
                                # Try multiple ways to extract sitekey from iframe
                                iframe_sitekey = await browser.page.evaluate("""
                                    () => {
                                        // Check Turnstile iframe with proper URL pattern
                                        const iframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                                        if (iframe && iframe.src) {
                                            // Extract sitekey from URL parameters
                                            const url = new URL(iframe.src, window.location.origin);
                                            const sitekey = url.searchParams.get('sitekey');
                                            if (sitekey && sitekey.match(/^[0-9a-zA-Z]{20,}$/)) {
                                                return sitekey;
                                            }
                                            // Try alternative pattern
                                            const match = iframe.src.match(/sitekey=([0-9a-zA-Z_-]+)/);
                                            if (match && match[1].match(/^[0-9a-zA-Z]{20,}$/)) return match[1];
                                        }

                                        // Check window.turnstile if available
                                        if (window.turnstile && window.turnstile.sitekey) {
                                            return window.turnstile.sitekey;
                                        }

                                        // Check for data attributes
                                        const turnstileDiv = document.querySelector('[data-sitekey]');
                                        if (turnstileDiv) {
                                            const sitekey = turnstileDiv.getAttribute('data-sitekey');
                                            if (sitekey && sitekey.match(/^[0-9a-zA-Z]{20,}$/)) {
                                                return sitekey;
                                            }
                                        }

                                        return null;
                                    }
                                """)
                                if iframe_sitekey:
                                    manual_sitekey = iframe_sitekey
                                    logger.success(f"Extracted sitekey from Turnstile iframe: {manual_sitekey}")
                                    break
                            except Exception as e:
                                logger.debug(f"Iframe check attempt {iframe_attempt + 1} failed: {str(e)}")
                            await asyncio.sleep(2)

                        # Get HTML to check if sitekey is in the source
                        html = await browser.page.evaluate("document.documentElement.outerHTML")

                        if html and not manual_sitekey:
                            # Method 1: Check for sitekeyEnterprise element
                            if 'sitekeyEnterprise' in html:
                                match = re.search(r'id="sitekeyEnterprise"[^>]*value="([^"]+)"', html)
                                if match:
                                    manual_sitekey = match.group(1)
                                    logger.success(f"Extracted sitekey from sitekeyEnterprise: {manual_sitekey}")

                            # Method 2: Look for data-sitekey attribute
                            if not manual_sitekey:
                                match = re.search(r'data-sitekey="([0-9a-zA-Z_-]{30,})"', html)
                                if match:
                                    manual_sitekey = match.group(1)
                                    logger.success(f"Extracted sitekey from data-sitekey: {manual_sitekey}")

                            # Method 3: Look for sitekey in turnstile.render() calls
                            if not manual_sitekey:
                                match = re.search(r'turnstile\.render[^{]*\{[^}]*sitekey["\s:]+["\']([0-9a-zA-Z_-]{30,})["\']', html, re.IGNORECASE)
                                if match:
                                    manual_sitekey = match.group(1)
                                    logger.success(f"Extracted sitekey from turnstile.render: {manual_sitekey}")

                            # Method 4: Look for sitekey in inline script (common pattern)
                            if not manual_sitekey:
                                match = re.search(r'["\']sitekey["\'][:\s]+["\']([0-9a-zA-Z_-]{30,})["\']', html)
                                if match:
                                    manual_sitekey = match.group(1)
                                    logger.success(f"Extracted sitekey from inline script: {manual_sitekey}")

                            # Method 5: Look for sitekey in iframe src
                            if not manual_sitekey:
                                match = re.search(r'challenges\.cloudflare\.com[^"]*sitekey=([0-9a-zA-Z_-]+)', html)
                                if match:
                                    manual_sitekey = match.group(1)
                                    logger.success(f"Extracted sitekey from iframe src: {manual_sitekey}")

                            # Method 6: Generic sitekey pattern (Cloudflare format: 0x...)
                            # Cloudflare sitekeys are typically alphanumeric only, strict format: 0x followed by alphanumeric
                            if not manual_sitekey:
                                # More strict regex: 0x followed by ONLY alphanumeric (no dots, spaces, dashes, etc)
                                match = re.search(r'"?(0x[0-9a-zA-Z]{20,40})"?', html)
                                if match:
                                    candidate = match.group(1)
                                    # Strict validation: only alphanumeric after 0x, no special chars
                                    if re.match(r'^0x[0-9a-zA-Z]{20,40}$', candidate):
                                        manual_sitekey = candidate
                                        logger.success(f"Extracted sitekey via generic pattern: {manual_sitekey}")
                                    else:
                                        logger.debug(f"Rejected invalid sitekey format: {candidate}")

                            if not manual_sitekey and ('turnstile' in html.lower() or 'cloudflare' in html.lower()):
                                logger.warning("Turnstile detected but sitekey not found via any method")
                                # Save HTML for debugging
                                logger.debug(f"HTML length: {len(html)}")
                                # Find any potential sitekey-like strings
                                potential_keys = re.findall(r'["\']([0-9a-zA-Z_-]{30,50})["\']', html)
                                if potential_keys:
                                    logger.debug(f"Potential sitekey candidates: {potential_keys[:5]}")
                                # Save HTML to file for analysis
                                try:
                                    import os
                                    debug_dir = os.path.join(os.path.dirname(__file__), "debug")
                                    os.makedirs(debug_dir, exist_ok=True)
                                    debug_file = os.path.join(debug_dir, "captcha_page.html")
                                    with open(debug_file, "w", encoding="utf-8") as f:
                                        f.write(html)
                                    logger.info(f"Saved CAPTCHA page HTML to {debug_file} for debugging")
                                except Exception as save_err:
                                    logger.debug(f"Could not save debug HTML: {save_err}")
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
                        sitekey = captcha_info.get('sitekey', '')

                        logger.info(f"CAPTCHA type identified: {captcha_type}")
                        logger.info(f"Sitekey: {sitekey[:30]}..." if len(sitekey) > 30 else f"Sitekey: {sitekey}")
                        logger.info(f"URL: {captcha_info.get('url', 'N/A')}")

                        # Validate sitekey format before attempting to solve
                        import re
                        if not sitekey or not re.match(r'^[0-9a-zA-Z]{20,}$', sitekey):
                            logger.error(f"Invalid sitekey format detected: {repr(sitekey)}")
                            logger.warning("Cannot solve CAPTCHA with invalid sitekey")
                            sitekey = None

                        solution = None

                        # Handle different CAPTCHA types
                        if captcha_type == "cloudflare_turnstile" and sitekey:
                            logger.warning("Cloudflare Turnstile detected - solving...")
                            logger.info(f"Sending to 2Captcha: sitekey={sitekey}")
                            solution = self.captcha_solver.solve_cloudflare_turnstile(
                                sitekey=sitekey,
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
                            else:
                                logger.error("Failed to solve Turnstile CAPTCHA - may need human intervention or valid 2Captcha API key")

                        elif captcha_type == "recaptcha_v2" and sitekey:
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

                        elif captcha_type == "recaptcha_v3" and sitekey:
                            logger.warning("reCAPTCHA v3 detected - solving...")
                            solution = self.captcha_solver.solve_recaptcha_v3(
                                sitekey=sitekey,
                                url=captcha_info["url"]
                            )
                            if solution:
                                logger.success("reCAPTCHA v3 solved!")
                                captcha_solved = True

                        elif captcha_type == "hcaptcha" and sitekey:
                            logger.warning("hCaptcha detected - solving...")
                            solution = self.captcha_solver.solve_hcaptcha(
                                sitekey=sitekey,
                                url=captcha_info["url"]
                            )
                            if solution:
                                logger.success("hCaptcha solved!")
                                captcha_solved = True

                        if not solution and sitekey:
                            logger.error(f"Failed to solve {captcha_type} - 2Captcha may have timed out or returned an error")
                        elif not sitekey:
                            logger.error(f"Cannot solve {captcha_type} - invalid or missing sitekey")
                            # Save HTML for debugging when sitekey is rejected
                            try:
                                import os
                                debug_dir = os.path.join(os.path.dirname(__file__), "debug")
                                os.makedirs(debug_dir, exist_ok=True)
                                debug_file = os.path.join(debug_dir, "captcha_failed.html")
                                failed_html = await browser.page.evaluate("document.documentElement.outerHTML")
                                with open(debug_file, "w", encoding="utf-8") as f:
                                    f.write(failed_html)
                                logger.info(f"Saved failed CAPTCHA page HTML to {debug_file}")
                            except Exception as save_err:
                                logger.debug(f"Could not save debug HTML: {save_err}")
                    else:
                        logger.warning("CAPTCHA detected but could not identify type or extract sitekey")
                        logger.warning("Check that the CAPTCHA widget has loaded properly")

            # If CAPTCHA was detected but not solved, raise CloudflareDetectedError
            if captcha_detected and not captcha_solved:
                logger.error("Cloudflare detected the crawl and blocked access - CAPTCHA could not be bypassed")
                raise CloudflareDetectedError(
                    "Listing site detected the crawl. The page is protected by Cloudflare and requires human verification."
                )

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

                        # ===== AUTOMATIC DATA CLEANING & STORAGE =====
                        try:
                            from backend.storage.cleaner.sahibinden_cleaner import SahibindenDataCleaner
                            from backend.storage.image_service import ImageDownloadService
                            from config.settings import settings

                            # 1. Clean raw data
                            cleaner = SahibindenDataCleaner()
                            cleaned_data = cleaner.clean(sahibinden_data)
                            logger.info(f"Cleaned data with quality score: {cleaned_data.get('data_quality_score', 0):.2f}")

                            # 2. Download images
                            image_service = ImageDownloadService()
                            main_images = sahibinden_data.get('resimler', [])[:2]  # First 2 images
                            painted_images = sahibinden_data.get('boyali_degisen', {}).get('gorseller', [])
                            painted_url = painted_images[0] if painted_images else None

                            image_records = await image_service.download_listing_images(
                                listing_id=cleaned_data.get('listing_id', 'unknown'),
                                main_urls=main_images,
                                painted_url=painted_url
                            )
                            logger.info(f"Downloaded {len(image_records)} images")

                            # 3. Save to database (Firebase, PostgreSQL, or MongoDB)
                            try:
                                if settings.DATABASE_TYPE == 'firebase':
                                    from backend.storage.firebase_repository import FirestoreRepository
                                    repository = FirestoreRepository()
                                    db_listing = repository.create_listing(cleaned_data, image_records)
                                    db_id = db_listing.get('id') if db_listing else None
                                elif settings.DATABASE_TYPE == 'postgresql':
                                    from backend.storage.repository import CarListingRepository
                                    repository = CarListingRepository()
                                    db_listing = repository.create_listing(cleaned_data, image_records)
                                    db_id = db_listing.id if db_listing else None
                                else:
                                    logger.warning(f"Database type '{settings.DATABASE_TYPE}' not supported")
                                    db_listing = None
                                    db_id = None

                                if db_listing:
                                    logger.success(f"Saved listing to {settings.DATABASE_TYPE} database")
                                    # Store database ID in result for reference
                                    sahibinden_data['db_id'] = db_id
                                    sahibinden_data['data_quality_score'] = float(cleaned_data.get('data_quality_score', 0))
                                else:
                                    logger.error("Failed to save listing to database")
                                    sahibinden_data['db_error'] = "Failed to create database record"
                            except Exception as db_err:
                                logger.error(f"Database save error: {str(db_err)}")
                                sahibinden_data['db_error'] = str(db_err)

                        except ImportError as import_err:
                            logger.warning(f"Cleaning modules not available: {str(import_err)}")
                        except Exception as clean_err:
                            logger.error(f"Failed to clean/store listing: {str(clean_err)}")
                            # Don't fail the entire crawl - just log and continue
                            sahibinden_data['cleaning_error'] = str(clean_err)
                        # ===== END AUTOMATIC CLEANING =====

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
