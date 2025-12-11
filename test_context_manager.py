"""Test BrowserEngine as context manager to reproduce the error"""
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from crawler.engine import BrowserEngine

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def test_context_manager():
    """Test the actual usage pattern from crawler.py"""
    try:
        print("Testing BrowserEngine as async context manager...")

        async with BrowserEngine(headless=True, use_proxy=None) as browser:
            print("SUCCESS: Browser engine started via context manager!")
            print(f"Browser: {browser}")
            print(f"Browser.browser: {browser.browser}")
            print(f"Browser.page: {browser.page}")

            # Try navigation
            success = await browser.navigate("about:blank", wait_time=0)
            print(f"Navigation success: {success}")

        print("Context manager exited successfully")

    except Exception as e:
        print(f"ERROR: {e}")
        print(f"ERROR TYPE: {type(e).__name__}")
        print(f"ERROR str(e): '{str(e)}'")
        print(f"ERROR repr(e): {repr(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_context_manager())
