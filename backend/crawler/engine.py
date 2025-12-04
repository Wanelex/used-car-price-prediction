"""
Nodriver Browser Automation Engine with Anti-Bot Protection
"""
import nodriver as uc
from typing import Optional, Dict, Any, List
import asyncio
import random
from loguru import logger
from fake_useragent import UserAgent
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from crawler.stealth import StealthScripts, HumanBehavior
from crawler.proxy_auth import ProxyAuthExtension


class BrowserEngine:
    """
    Nodriver-based browser automation with stealth capabilities
    """

    def __init__(self, headless: bool = True, use_proxy: Optional[str] = None):
        self.headless = headless
        self.proxy = use_proxy
        self.browser: Optional[Any] = None
        self.page: Optional[Any] = None
        self.ua = UserAgent()
        self.proxy_extension_manager: Optional[ProxyAuthExtension] = None
        self.proxy_extension_dir: Optional[str] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def start(self):
        """Initialize the browser with stealth settings"""
        try:
            logger.info("Starting Nodriver browser...")

            # Browser configuration for maximum stealth
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-web-security",
                "--disable-features=IsolateOrigins,site-per-process",
                "--allow-running-insecure-content",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-extensions",
                "--disable-background-networking",
                "--disable-default-apps",
                "--disable-sync",
                "--disable-translate",
                "--hide-scrollbars",
                "--metrics-recording-only",
                "--mute-audio",
                "--no-first-run",
                "--safebrowsing-disable-auto-update",
                "--disable-blink-features",
                f"--user-agent={self.get_random_user_agent()}"
            ]

            # Handle proxy configuration
            if self.proxy:
                if '@' in self.proxy:
                    # Proxy has authentication - create Chrome extension
                    logger.info("Proxy has authentication - creating proxy auth extension...")

                    self.proxy_extension_manager = ProxyAuthExtension()
                    self.proxy_extension_dir = self.proxy_extension_manager.create_extension(self.proxy)

                    if self.proxy_extension_dir:
                        logger.success(f"Proxy auth extension created successfully")
                    else:
                        logger.error("Failed to create proxy auth extension")
                        # Fall back to no proxy
                        self.proxy = None
                else:
                    # Proxy without authentication - use --proxy-server
                    proxy_server = self.proxy.rstrip('/')
                    browser_args.append(f"--proxy-server={proxy_server}")
                    logger.info(f"Using proxy: {proxy_server}")

            # Always load Turnstile injector extension
            turnstile_injector_dir = Path(__file__).parent / "turnstile_injector_extension"
            logger.info("Loading Turnstile injector extension...")

            # Collect all extensions to load
            extensions_to_load = []

            if self.proxy_extension_dir:
                extensions_to_load.append(self.proxy_extension_dir)
                logger.info("Will load proxy auth extension")

            if turnstile_injector_dir.exists():
                extensions_to_load.append(str(turnstile_injector_dir))
                logger.info("Will load Turnstile injector extension")
            else:
                logger.warning(f"Turnstile injector extension not found at: {turnstile_injector_dir}")

            # Start browser with extensions
            if extensions_to_load:
                logger.info(f"Starting browser with {len(extensions_to_load)} extension(s)...")
                self.browser = await uc.start(
                    headless=self.headless,
                    browser_args=browser_args,
                    extensions=extensions_to_load
                )
            else:
                # Start normally
                self.browser = await uc.start(
                    headless=self.headless,
                    browser_args=browser_args
                )

            # Get the first page/tab
            self.page = await self.browser.get("about:blank")

            # Inject comprehensive stealth scripts
            await self._inject_stealth_scripts()

            logger.info("Browser started successfully with stealth protection")

        except Exception as e:
            logger.error(f"Failed to start browser: {str(e)}")
            raise

    async def close(self):
        """Close the browser"""
        try:
            if self.browser:
                try:
                    # Try to stop the browser gracefully
                    stop_result = self.browser.stop()
                    if stop_result is not None:
                        await stop_result
                    logger.info("Browser closed")
                except Exception as e:
                    logger.debug(f"Browser already closed or error during stop: {str(e)}")

            # Cleanup proxy extension
            if self.proxy_extension_manager:
                self.proxy_extension_manager.cleanup()
                logger.debug("Proxy extension cleaned up")

        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")

    async def _inject_stealth_scripts(self):
        """
        Inject comprehensive stealth and anti-fingerprinting scripts
        """
        try:
            logger.info("Injecting stealth scripts...")

            # Get comprehensive stealth script
            stealth_script = StealthScripts.get_comprehensive_stealth_script()

            # Inject into page
            await self.page.evaluate(stealth_script)

            logger.success("All stealth scripts injected successfully")

        except Exception as e:
            logger.warning(f"Failed to inject some stealth scripts: {str(e)}")

    def get_random_user_agent(self) -> str:
        """Get a random realistic user agent"""
        return self.ua.random

    async def navigate(self, url: str, wait_time: int = 0) -> bool:
        """
        Navigate to a URL with human-like behavior

        Args:
            url: Target URL
            wait_time: Additional wait time after page load

        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Navigating to: {url}")

            # Random delay before navigation (human behavior)
            await self.random_delay()

            # Navigate to URL
            await self.page.get(url)

            # Wait for page to load initially
            await asyncio.sleep(3)

            # Check for security challenge page and wait for Cloudflare scripts
            page_text = await self.page.evaluate("document.body.innerText || ''")

            if any(indicator in page_text for indicator in [
                "Bir dakika lütfen",
                "Just a moment",
                "Aşağıdaki işlemi tamamlayarak",
                "Verify you are human"
            ]):
                logger.warning("Cloudflare challenge page detected! Waiting for Turnstile widget to load...")

                # Wait longer for Turnstile widget to fully render
                await asyncio.sleep(5)

                logger.info("Challenge page detected, CAPTCHA detection will handle it")

            # Additional wait time if specified
            if wait_time > 0:
                logger.info(f"Waiting additional {wait_time}s as requested")
                await asyncio.sleep(wait_time)

            # Random scrolling (human behavior)
            if settings.ENABLE_RANDOM_SCROLLING:
                await self.random_scroll()

            logger.info(f"Successfully navigated to: {url}")
            return True

        except Exception as e:
            logger.error(f"Navigation failed: {str(e)}")
            return False

    async def handle_security_check(self):
        """Handle security check pages (e.g., sahibinden.com)"""
        try:
            # Check if we're on a security check page
            page_text = await self.page.evaluate("document.body.innerText")

            if "Tarayıcınızı kontrol ediyoruz" in page_text or "Devam Et" in page_text:
                logger.warning("Security check page detected! Waiting...")

                # Wait longer for security check
                await asyncio.sleep(5)

                # Try to click "Devam Et" (Continue) button if present
                try:
                    button = await self.page.evaluate("""
                        () => {
                            const buttons = document.querySelectorAll('button, a');
                            for (const btn of buttons) {
                                if (btn.innerText.includes('Devam Et') || btn.innerText.includes('Continue')) {
                                    btn.click();
                                    return true;
                                }
                            }
                            return false;
                        }
                    """)

                    if button:
                        logger.info("Clicked continue button, waiting for redirect...")
                        await asyncio.sleep(5)
                except Exception as e:
                    logger.debug(f"Could not click continue button: {str(e)}")

        except Exception as e:
            logger.debug(f"Security check handler error: {str(e)}")

    async def get_page_content(self) -> Dict[str, Any]:
        """
        Extract all content from the current page

        Returns:
            Dict containing HTML, text, and other data
        """
        try:
            # Get full HTML
            html = await self.page.get_content()

            # Get page title
            title = await self.page.evaluate("document.title")

            # Get all text content
            text_content = await self.page.evaluate("""
                () => {
                    return document.body.innerText || document.body.textContent;
                }
            """)

            # Get current URL (after redirects)
            current_url = self.page.url

            # Get meta tags
            metadata = await self.extract_metadata()

            # Get all images
            images = await self.extract_images()

            # Get all links
            links = await self.extract_links()

            return {
                "html": html,
                "text": text_content,
                "title": title,
                "url": current_url,
                "metadata": metadata,
                "images": images,
                "links": links
            }

        except Exception as e:
            logger.error(f"Failed to extract page content: {str(e)}")
            raise

    async def extract_metadata(self) -> Dict[str, Optional[str]]:
        """Extract metadata from the page"""
        try:
            metadata = await self.page.evaluate("""
                () => {
                    const getMeta = (name) => {
                        const meta = document.querySelector(`meta[name="${name}"], meta[property="${name}"]`);
                        return meta ? meta.content : null;
                    };

                    return {
                        description: getMeta('description'),
                        keywords: getMeta('keywords'),
                        author: getMeta('author'),
                        og_title: getMeta('og:title'),
                        og_description: getMeta('og:description'),
                        og_image: getMeta('og:image'),
                        language: document.documentElement.lang,
                        charset: document.characterSet
                    };
                }
            """)

            return metadata

        except Exception as e:
            logger.error(f"Failed to extract metadata: {str(e)}")
            return {}

    async def extract_images(self) -> List[str]:
        """Extract all image URLs from the page"""
        try:
            images = await self.page.evaluate("""
                () => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    return imgs.map(img => img.src).filter(src => src);
                }
            """)

            return images

        except Exception as e:
            logger.error(f"Failed to extract images: {str(e)}")
            return []

    async def extract_links(self) -> List[str]:
        """Extract all links from the page"""
        try:
            links = await self.page.evaluate("""
                () => {
                    const anchors = Array.from(document.querySelectorAll('a[href]'));
                    return anchors.map(a => a.href).filter(href => href);
                }
            """)

            return links

        except Exception as e:
            logger.error(f"Failed to extract links: {str(e)}")
            return []

    async def wait_for_selector(self, selector: str, timeout: int = 30000) -> bool:
        """
        Wait for a specific element to appear

        Args:
            selector: CSS selector
            timeout: Timeout in milliseconds

        Returns:
            bool: Whether element appeared
        """
        try:
            element = await self.page.select(selector)
            if element:
                return True
            return False
        except Exception as e:
            logger.error(f"Element not found: {selector}")
            return False

    async def random_delay(self, min_delay: Optional[float] = None, max_delay: Optional[float] = None):
        """Add random delay to simulate human behavior"""
        min_d = min_delay or settings.MIN_DELAY
        max_d = max_delay or settings.MAX_DELAY
        delay = random.uniform(min_d, max_d)
        await asyncio.sleep(delay)

    async def random_scroll(self):
        """Perform realistic human-like scrolling"""
        try:
            # Get realistic scroll pattern
            scroll_pattern = HumanBehavior.get_scroll_pattern()

            for action in scroll_pattern:
                if action.get("type") == "pause":
                    await asyncio.sleep(action["duration"])
                else:
                    # Smooth scroll to position
                    await self.page.evaluate(f"""
                        window.scrollTo({{
                            top: {action['to']},
                            behavior: 'smooth'
                        }});
                    """)
                    await asyncio.sleep(action["duration"])

            logger.debug("Realistic scroll simulation completed")

        except Exception as e:
            logger.error(f"Random scroll failed: {str(e)}")

    async def simulate_mouse_movement(self, target_x: int = None, target_y: int = None):
        """
        Simulate realistic human-like mouse movements with curved paths
        """
        try:
            # Start from random position
            start_x = random.randint(100, 400)
            start_y = random.randint(100, 300)

            # Target position
            if target_x is None:
                target_x = random.randint(200, 800)
            if target_y is None:
                target_y = random.randint(200, 600)

            # Generate realistic curved path
            path = HumanBehavior.generate_mouse_path(start_x, start_y, target_x, target_y)

            # Move along the path
            for point in path:
                try:
                    await self.page.mouse.move(point["x"], point["y"])
                    await asyncio.sleep(random.uniform(0.01, 0.03))
                except:
                    pass  # Some positions might be invalid, continue

            # Random pause at destination
            await asyncio.sleep(HumanBehavior.get_random_pause())

            logger.debug(f"Mouse moved from ({start_x}, {start_y}) to ({target_x}, {target_y})")

        except Exception as e:
            logger.error(f"Mouse movement simulation failed: {str(e)}")

    async def check_for_captcha(self) -> bool:
        """
        Check if there's a CAPTCHA on the page

        Returns:
            bool: True if CAPTCHA detected
        """
        try:
            # Check page text for Cloudflare challenge indicators
            page_text = await self.page.evaluate("document.body.innerText || document.body.textContent || ''")

            # Cloudflare Turnstile challenge page indicators
            cloudflare_indicators = [
                "Aşağıdaki işlemi tamamlayarak insan olduğunuzu doğrulayın",
                "Verify you are human",
                "Checking your browser",
                "Tarayıcınızı kontrol ediyoruz",
                "Just a moment",
                "Bir dakika lütfen"
            ]

            for indicator in cloudflare_indicators:
                if indicator in page_text:
                    logger.warning(f"Cloudflare challenge page detected: '{indicator}'")
                    return True

            # Common CAPTCHA indicators
            captcha_selectors = [
                'iframe[src*="recaptcha"]',
                'iframe[src*="hcaptcha"]',
                'iframe[src*="captcha"]',
                'iframe[src*="turnstile"]',
                'iframe[src*="challenges.cloudflare"]',
                '.g-recaptcha',
                '.h-captcha',
                '[data-sitekey]',
                '#cf-chl-widget',
                'input[name="cf-turnstile-response"]'
            ]

            for selector in captcha_selectors:
                element = await self.page.select(selector)
                if element:
                    logger.warning(f"CAPTCHA detected: {selector}")
                    return True

            # Check for Cloudflare scripts
            has_cf_script = await self.page.evaluate("""
                () => {
                    const scripts = Array.from(document.scripts);
                    return scripts.some(s =>
                        s.src.includes('challenges.cloudflare.com') ||
                        s.src.includes('turnstile')
                    );
                }
            """)

            if has_cf_script:
                logger.warning("Cloudflare challenge script detected")
                return True

            return False

        except Exception as e:
            logger.error(f"CAPTCHA check failed: {str(e)}")
            return False

    async def screenshot(self, filepath: str):
        """Take a screenshot of the current page"""
        try:
            await self.page.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
        except Exception as e:
            logger.error(f"Screenshot failed: {str(e)}")

    async def execute_script(self, script: str) -> Any:
        """Execute JavaScript on the page"""
        try:
            result = await self.page.evaluate(script)
            return result
        except Exception as e:
            logger.error(f"Script execution failed: {str(e)}")
            return None

    async def inject_turnstile_solution(self, solution_token: str) -> bool:
        """
        Inject Cloudflare Turnstile solution token into the page

        Args:
            solution_token: The solved CAPTCHA token

        Returns:
            bool: Success status
        """
        try:
            logger.info("Submitting Turnstile token to sahibinden.com server...")

            # Based on reverse engineering csTLoading.js, we need to:
            # 1. POST the token to /ajax/cs/checkT/CS_LOADING
            # 2. Server validates and responds with success/failure
            # 3. If success, page redirects to returnUrl

            await self.page.evaluate(f"""
                (async function() {{
                    const token = '{solution_token}';
                    console.log('[Crawler] Submitting token to server:', token.substring(0, 20) + '...');

                    try {{
                        // Use jQuery if available (sahibinden.com has it)
                        if (typeof $ !== 'undefined') {{
                            console.log('[Crawler] Using jQuery to submit token');

                            $.ajax({{
                                type: "POST",
                                url: "/ajax/cs/checkT/CS_LOADING",
                                data: {{
                                    captchaValueEnterprise: token
                                }},
                                dataType: "json",
                                success: function(response) {{
                                    console.log('[Crawler] Server response:', response);

                                    if (response.success && response.data === true) {{
                                        console.log('[Crawler] ✅ Token validated! Redirecting...');

                                        // Get return URL
                                        const returnUrl = document.querySelector('#returnUrl')?.value;
                                        if (returnUrl) {{
                                            console.log('[Crawler] Redirecting to:', returnUrl);
                                            setTimeout(() => {{
                                                window.location.href = returnUrl;
                                            }}, 1000);
                                        }}
                                    }} else {{
                                        console.log('[Crawler] ❌ Token validation failed');
                                    }}
                                }},
                                error: function(xhr, status, error) {{
                                    console.error('[Crawler] ❌ AJAX error:', status, error);
                                }}
                            }});
                        }} else {{
                            // Fallback: Use fetch API
                            console.log('[Crawler] Using fetch API to submit token');

                            const formData = new FormData();
                            formData.append('captchaValueEnterprise', token);

                            const response = await fetch('/ajax/cs/checkT/CS_LOADING', {{
                                method: 'POST',
                                body: formData
                            }});

                            const data = await response.json();
                            console.log('[Crawler] Server response:', data);

                            if (data.success && data.data === true) {{
                                console.log('[Crawler] ✅ Token validated! Redirecting...');
                                const returnUrl = document.querySelector('#returnUrl')?.value;
                                if (returnUrl) {{
                                    window.location.href = returnUrl;
                                }}
                            }}
                        }}
                    }} catch (error) {{
                        console.error('[Crawler] Error submitting token:', error);
                    }}
                }})();
            """)

            logger.success("Turnstile token submitted to server")
            logger.info("Waiting for server validation and redirect...")
            await asyncio.sleep(10)  # Wait for validation and redirect

            # Now click the continue button
            clicked = await self._click_continue_button()

            if clicked:
                return True
            else:
                logger.warning("Continue button not clicked, but token was injected")
                return True

        except Exception as e:
            logger.error(f"Failed to inject Turnstile solution: {str(e)}")
            return False

    async def _click_continue_button(self) -> bool:
        """
        Find and click the continue button after CAPTCHA solving
        """
        try:
            logger.info("Looking for continue button...")

            # Use page.evaluate to click (even if it returns None, the click will happen)
            await self.page.evaluate("""
                (function() {
                    console.log('Searching for continue button...');

                    // Try direct selector first
                    let btn = document.querySelector('#btn-continue');
                    if (btn) {
                        console.log('Found button by ID: #btn-continue');
                        btn.click();
                        return;
                    }

                    // Try by value attribute
                    btn = document.querySelector('input[value="Devam Et"]');
                    if (btn) {
                        console.log('Found button by value: Devam Et');
                        btn.click();
                        return;
                    }

                    // Try all buttons and inputs
                    const allButtons = document.querySelectorAll('button, input[type="button"], input[type="submit"]');
                    console.log('Found ' + allButtons.length + ' buttons total');

                    for (const b of allButtons) {
                        const text = (b.innerText || b.value || '').toLowerCase();
                        if (text.includes('devam') || text.includes('continue')) {
                            console.log('Clicking button with text:', b.innerText || b.value);
                            b.click();
                            return;
                        }
                    }

                    console.log('No continue button found');
                })();
            """)

            logger.info("Continue button click attempted, waiting for navigation...")
            await asyncio.sleep(8)  # Wait longer for redirect
            return True

        except Exception as e:
            logger.error(f"Failed to click continue button: {str(e)}")
            return False
