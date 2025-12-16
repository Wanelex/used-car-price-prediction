"""
CAPTCHA Solving Integration
Supports 2Captcha and Anti-Captcha services
"""
from typing import Optional, Dict, Any
from loguru import logger
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import settings

try:
    from twocaptcha import TwoCaptcha
    TWOCAPTCHA_AVAILABLE = True
except ImportError:
    TWOCAPTCHA_AVAILABLE = False
    logger.warning("2Captcha library not available")

try:
    from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
    ANTICAPTCHA_AVAILABLE = True
except ImportError:
    ANTICAPTCHA_AVAILABLE = False
    logger.warning("Anti-Captcha library not available")


class CaptchaSolver:
    """
    Unified CAPTCHA solving interface
    Supports multiple providers with automatic fallback
    """

    def __init__(
        self,
        twocaptcha_key: Optional[str] = None,
        anticaptcha_key: Optional[str] = None,
        preferred_provider: str = "2captcha"
    ):
        self.twocaptcha_key = twocaptcha_key or settings.TWOCAPTCHA_API_KEY
        self.anticaptcha_key = anticaptcha_key or settings.ANTICAPTCHA_API_KEY
        self.preferred_provider = preferred_provider

        # Initialize clients
        self.twocaptcha_client = None
        self.anticaptcha_client = None

        if self.twocaptcha_key and TWOCAPTCHA_AVAILABLE:
            try:
                self.twocaptcha_client = TwoCaptcha(self.twocaptcha_key)
                logger.info("2Captcha client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize 2Captcha: {str(e)}")

        if self.anticaptcha_key and ANTICAPTCHA_AVAILABLE:
            try:
                self.anticaptcha_client = AnticaptchaClient(self.anticaptcha_key)
                logger.info("Anti-Captcha client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anti-Captcha: {str(e)}")

    def solve_recaptcha_v2(
        self,
        sitekey: str,
        url: str,
        invisible: bool = False
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v2

        Args:
            sitekey: The site key
            url: The page URL
            invisible: Whether it's invisible reCAPTCHA

        Returns:
            Solution token or None if failed
        """
        logger.info(f"Solving reCAPTCHA v2 for {url}")

        # Try preferred provider first
        if self.preferred_provider == "2captcha":
            result = self._solve_recaptcha_v2_twocaptcha(sitekey, url, invisible)
            if result:
                return result
            # Fallback to anti-captcha
            logger.warning("2Captcha failed, trying Anti-Captcha")
            return self._solve_recaptcha_v2_anticaptcha(sitekey, url)
        else:
            result = self._solve_recaptcha_v2_anticaptcha(sitekey, url)
            if result:
                return result
            # Fallback to 2captcha
            logger.warning("Anti-Captcha failed, trying 2Captcha")
            return self._solve_recaptcha_v2_twocaptcha(sitekey, url, invisible)

    def _solve_recaptcha_v2_twocaptcha(
        self,
        sitekey: str,
        url: str,
        invisible: bool = False
    ) -> Optional[str]:
        """Solve reCAPTCHA v2 using 2Captcha"""
        if not self.twocaptcha_client:
            logger.error("2Captcha client not available")
            return None

        try:
            logger.info("Solving with 2Captcha...")

            result = self.twocaptcha_client.recaptcha(
                sitekey=sitekey,
                url=url,
                invisible=1 if invisible else 0
            )

            if result and 'code' in result:
                logger.success("reCAPTCHA v2 solved with 2Captcha")
                return result['code']

        except Exception as e:
            logger.error(f"2Captcha solving failed: {str(e)}")

        return None

    def _solve_recaptcha_v2_anticaptcha(
        self,
        sitekey: str,
        url: str
    ) -> Optional[str]:
        """Solve reCAPTCHA v2 using Anti-Captcha"""
        if not self.anticaptcha_client:
            logger.error("Anti-Captcha client not available")
            return None

        try:
            logger.info("Solving with Anti-Captcha...")

            task = NoCaptchaTaskProxylessTask(
                website_url=url,
                website_key=sitekey
            )

            job = self.anticaptcha_client.createTask(task)
            job.join()

            if job.get_solution_response():
                logger.success("reCAPTCHA v2 solved with Anti-Captcha")
                return job.get_solution_response()

        except Exception as e:
            logger.error(f"Anti-Captcha solving failed: {str(e)}")

        return None

    def solve_recaptcha_v3(
        self,
        sitekey: str,
        url: str,
        action: str = "verify",
        min_score: float = 0.3
    ) -> Optional[str]:
        """
        Solve reCAPTCHA v3

        Args:
            sitekey: The site key
            url: The page URL
            action: The action name
            min_score: Minimum score required

        Returns:
            Solution token or None if failed
        """
        logger.info(f"Solving reCAPTCHA v3 for {url}")

        if not self.twocaptcha_client:
            logger.error("2Captcha client not available (required for v3)")
            return None

        try:
            result = self.twocaptcha_client.recaptcha(
                sitekey=sitekey,
                url=url,
                version='v3',
                action=action,
                score=min_score
            )

            if result and 'code' in result:
                logger.success("reCAPTCHA v3 solved")
                return result['code']

        except Exception as e:
            logger.error(f"reCAPTCHA v3 solving failed: {str(e)}")

        return None

    def solve_hcaptcha(
        self,
        sitekey: str,
        url: str
    ) -> Optional[str]:
        """
        Solve hCaptcha

        Args:
            sitekey: The site key
            url: The page URL

        Returns:
            Solution token or None if failed
        """
        logger.info(f"Solving hCaptcha for {url}")

        if not self.twocaptcha_client:
            logger.error("2Captcha client not available")
            return None

        try:
            result = self.twocaptcha_client.hcaptcha(
                sitekey=sitekey,
                url=url
            )

            if result and 'code' in result:
                logger.success("hCaptcha solved")
                return result['code']

        except Exception as e:
            logger.error(f"hCaptcha solving failed: {str(e)}")

        return None

    def solve_cloudflare_turnstile(
        self,
        sitekey: str,
        url: str,
        action: Optional[str] = None,
        data: Optional[str] = None
    ) -> Optional[str]:
        """
        Solve Cloudflare Turnstile challenge
        This is CRITICAL for sites like sahibinden.com

        Args:
            sitekey: The site key
            url: The page URL
            action: Optional action parameter
            data: Optional data parameter

        Returns:
            Solution token or None if failed
        """
        import re

        logger.info(f"Solving Cloudflare Turnstile for {url}")

        # Validate sitekey format before sending to solver
        if not sitekey or not isinstance(sitekey, str):
            logger.error(f"Invalid sitekey: not a string or empty")
            return None

        # Cloudflare sitekeys should be alphanumeric only, no special characters
        # Valid format: alphanumeric string, typically 20-40 chars
        if not re.match(r'^[0-9a-zA-Z]{20,}$', sitekey):
            logger.error(f"Invalid sitekey format: {sitekey}")
            logger.error(f"Sitekey must be alphanumeric only, got: {repr(sitekey)}")
            return None

        logger.info(f"Sitekey validation passed: {sitekey[:20]}...")

        # Try 2Captcha first (has best Turnstile support)
        if self.twocaptcha_client:
            try:
                logger.info("Solving Turnstile with 2Captcha...")

                result = self.twocaptcha_client.turnstile(
                    sitekey=sitekey,
                    url=url,
                    action=action,
                    data=data
                )

                if result and 'code' in result:
                    logger.success("Cloudflare Turnstile solved with 2Captcha!")
                    return result['code']

            except Exception as e:
                logger.error(f"2Captcha Turnstile solving failed: {str(e)}")

        # Fallback to Anti-Captcha if available
        if self.anticaptcha_client:
            try:
                logger.info("Trying Anti-Captcha for Turnstile...")
                # Note: Anti-Captcha support for Turnstile may vary
                # This is a fallback attempt

                from python_anticaptcha import AntiCaptchaTaskProtocol

                class TurnstileTask(AntiCaptchaTaskProtocol):
                    def __init__(self, website_url, website_key):
                        self.task = {
                            "type": "TurnstileTaskProxyless",
                            "websiteURL": website_url,
                            "websiteKey": website_key
                        }

                    def get_task_dict(self):
                        return self.task

                task = TurnstileTask(url, sitekey)
                job = self.anticaptcha_client.createTask(task)
                job.join()

                if job.get_solution_response():
                    logger.success("Cloudflare Turnstile solved with Anti-Captcha!")
                    return job.get_solution_response()

            except Exception as e:
                logger.error(f"Anti-Captcha Turnstile solving failed: {str(e)}")

        logger.error("All Turnstile solving attempts failed")
        return None

    def solve_image_captcha(
        self,
        image_path: str
    ) -> Optional[str]:
        """
        Solve image-based CAPTCHA

        Args:
            image_path: Path to the CAPTCHA image

        Returns:
            Solved text or None if failed
        """
        logger.info(f"Solving image CAPTCHA: {image_path}")

        if not self.twocaptcha_client:
            logger.error("2Captcha client not available")
            return None

        try:
            result = self.twocaptcha_client.normal(image_path)

            if result and 'code' in result:
                logger.success("Image CAPTCHA solved")
                return result['code']

        except Exception as e:
            logger.error(f"Image CAPTCHA solving failed: {str(e)}")

        return None

    def get_balance(self, provider: str = "2captcha") -> Optional[float]:
        """
        Get account balance

        Args:
            provider: Which provider to check ("2captcha" or "anticaptcha")

        Returns:
            Balance amount or None
        """
        try:
            if provider == "2captcha" and self.twocaptcha_client:
                balance = self.twocaptcha_client.balance()
                logger.info(f"2Captcha balance: ${balance}")
                return float(balance)
            elif provider == "anticaptcha" and self.anticaptcha_client:
                balance = self.anticaptcha_client.getBalance()
                logger.info(f"Anti-Captcha balance: ${balance}")
                return float(balance)
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")

        return None


class CaptchaDetector:
    """
    Detect CAPTCHA on web pages
    """

    @staticmethod
    async def detect_recaptcha_v2(page) -> Optional[Dict[str, str]]:
        """
        Detect reCAPTCHA v2 on page

        Args:
            page: Browser page object

        Returns:
            Dict with sitekey and URL or None
        """
        try:
            # Try to find reCAPTCHA iframe
            sitekey = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe[src*="recaptcha"]');
                    if (iframe) {
                        const src = iframe.src;
                        const match = src.match(/k=([^&]+)/);
                        return match ? match[1] : null;
                    }

                    // Try to find div with data-sitekey
                    const div = document.querySelector('.g-recaptcha, [data-sitekey]');
                    if (div) {
                        return div.getAttribute('data-sitekey');
                    }

                    return null;
                }
            """)

            if sitekey:
                return {
                    "type": "recaptcha_v2",
                    "sitekey": sitekey,
                    "url": page.url
                }

        except Exception as e:
            logger.error(f"Failed to detect reCAPTCHA v2: {str(e)}")

        return None

    @staticmethod
    async def detect_recaptcha_v3(page) -> Optional[Dict[str, str]]:
        """Detect reCAPTCHA v3 on page"""
        try:
            sitekey = await page.evaluate("""
                () => {
                    const scripts = Array.from(document.scripts);
                    for (const script of scripts) {
                        if (script.src.includes('recaptcha')) {
                            const match = script.src.match(/render=([^&]+)/);
                            if (match) return match[1];
                        }
                    }
                    return null;
                }
            """)

            if sitekey:
                return {
                    "type": "recaptcha_v3",
                    "sitekey": sitekey,
                    "url": page.url
                }

        except Exception as e:
            logger.error(f"Failed to detect reCAPTCHA v3: {str(e)}")

        return None

    @staticmethod
    async def detect_hcaptcha(page) -> Optional[Dict[str, str]]:
        """Detect hCaptcha on page"""
        try:
            sitekey = await page.evaluate("""
                () => {
                    const iframe = document.querySelector('iframe[src*="hcaptcha"]');
                    if (iframe) {
                        const src = iframe.src;
                        const match = src.match(/sitekey=([^&]+)/);
                        return match ? match[1] : null;
                    }

                    const div = document.querySelector('.h-captcha, [data-sitekey]');
                    if (div && div.getAttribute('data-sitekey')) {
                        return div.getAttribute('data-sitekey');
                    }

                    return null;
                }
            """)

            if sitekey:
                return {
                    "type": "hcaptcha",
                    "sitekey": sitekey,
                    "url": page.url
                }

        except Exception as e:
            logger.error(f"Failed to detect hCaptcha: {str(e)}")

        return None

    @staticmethod
    async def detect_cloudflare_turnstile(page) -> Optional[Dict[str, str]]:
        """
        Detect Cloudflare Turnstile on page
        This is critical for sites like sahibinden.com
        """
        try:
            result = await page.evaluate("""
                () => {
                    // Method 1: Check for Turnstile iframe
                    const iframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                    if (iframe) {
                        const src = iframe.src;
                        const match = src.match(/sitekey=([^&]+)/);
                        if (match) return { sitekey: match[1], source: 'iframe' };
                    }

                    // Method 2: Check for Turnstile div with ID
                    const turnstileDiv = document.querySelector('#turnStileWidget, [id*="turnstile"], [id*="cf-turnstile"]');
                    if (turnstileDiv) {
                        const sitekey = turnstileDiv.getAttribute('data-sitekey') ||
                                       document.querySelector('#sitekeyEnterprise')?.value ||
                                       document.querySelector('input[id*="sitekey"]')?.value;
                        if (sitekey) return { sitekey: sitekey, source: 'div' };
                    }

                    // Method 3: Check for Turnstile script
                    const scripts = Array.from(document.scripts);
                    for (const script of scripts) {
                        if (script.src.includes('challenges.cloudflare.com/turnstile')) {
                            // Try to find sitekey in page
                            const allInputs = document.querySelectorAll('input[type="hidden"]');
                            for (const input of allInputs) {
                                if (input.id.toLowerCase().includes('sitekey') ||
                                    input.id.toLowerCase().includes('site-key')) {
                                    return { sitekey: input.value, source: 'script' };
                                }
                            }
                        }
                    }

                    // Method 4: Check page text for Cloudflare challenge indicators
                    const bodyText = document.body.innerText || '';
                    if (bodyText.includes('Tarayıcınızı kontrol ediyoruz') ||
                        bodyText.includes('Checking your browser') ||
                        bodyText.includes('Cloudflare')) {
                        // Try to extract sitekey from any input
                        const sitekeyInput = document.querySelector('#sitekeyEnterprise, input[id*="sitekey"]');
                        if (sitekeyInput) {
                            return { sitekey: sitekeyInput.value, source: 'challenge' };
                        }
                    }

                    return null;
                }
            """)

            if result and result.get('sitekey'):
                logger.info(f"Cloudflare Turnstile detected (source: {result.get('source')})")
                return {
                    "type": "cloudflare_turnstile",
                    "sitekey": result['sitekey'],
                    "url": page.url,
                    "source": result.get('source')
                }

        except Exception as e:
            logger.error(f"Failed to detect Cloudflare Turnstile: {str(e)}")

        return None

    @staticmethod
    async def detect_any_captcha(page) -> Optional[Dict[str, str]]:
        """
        Detect any type of CAPTCHA on the page
        Returns first detected CAPTCHA
        """
        # Check in order of likelihood for sahibinden.com and similar sites
        detectors = [
            CaptchaDetector.detect_cloudflare_turnstile,
            CaptchaDetector.detect_recaptcha_v2,
            CaptchaDetector.detect_recaptcha_v3,
            CaptchaDetector.detect_hcaptcha
        ]

        for detector in detectors:
            try:
                result = await detector(page)
                if result:
                    logger.info(f"CAPTCHA detected: {result['type']}")
                    return result
            except Exception as e:
                logger.debug(f"Detector {detector.__name__} failed: {str(e)}")
                continue

        return None
