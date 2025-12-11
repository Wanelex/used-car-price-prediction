"""Test browser startup to identify the exact error"""
import asyncio
import nodriver as uc
import traceback
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def test_browser_with_extensions():
    try:
        print("\n=== Test 1: Browser with extensions and full browser_args ===")
        print("Attempting to start browser with extensions...")

        # Simulate the exact setup from engine.py
        turnstile_injector_dir = Path(__file__).parent / "backend" / "crawler" / "turnstile_injector_extension"

        # Use exact browser args from engine.py
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
            "--disable-extensions",  # <-- This might conflict!
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
        ]

        extensions_to_load = []
        if turnstile_injector_dir.exists():
            extensions_to_load.append(str(turnstile_injector_dir))
            print(f"Will load Turnstile injector extension: {turnstile_injector_dir}")
        else:
            print(f"WARNING: Turnstile extension not found at: {turnstile_injector_dir}")

        if extensions_to_load:
            print(f"Starting browser with {len(extensions_to_load)} extension(s)...")
            print(f"Using {len(browser_args)} browser args")
            browser = await uc.start(
                headless=True,
                browser_args=browser_args,
                extensions=extensions_to_load
            )
        else:
            print("Starting browser without extensions...")
            browser = await uc.start(
                headless=True,
                browser_args=browser_args
            )

        print("SUCCESS: Browser started!")

        # Try to get a page
        page = await browser.get("about:blank")
        print(f"Got page: {page}")

        # Properly close browser (don't await)
        stop_result = browser.stop()
        if stop_result is not None:
            await stop_result
        print("Browser closed successfully")

    except Exception as e:
        print(f"ERROR: {e}")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR REPR: {repr(e)}")
        if hasattr(e, 'args'):
            print(f"ERROR ARGS: {e.args}")
        print(f"ERROR str(e): '{str(e)}'")
        print(f"ERROR bool(str(e)): {bool(str(e))}")
        print("\n--- Full Traceback ---")
        traceback.print_exc()

async def test_browser_simple():
    try:
        print("\n=== Test 2: Simple browser (no extensions) ===")
        print("Attempting to start browser...")
        browser = await uc.start(headless=True)
        print("SUCCESS: Browser started!")

        # Properly close
        stop_result = browser.stop()
        if stop_result is not None:
            await stop_result
        print("Browser closed successfully")

    except Exception as e:
        print(f"ERROR: {e}")
        print(f"ERROR TYPE: {type(e).__name__}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_browser_with_extensions())
    asyncio.run(test_browser_simple())
