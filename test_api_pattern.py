"""Test the crawler in the same pattern as the API uses it"""
import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from crawler.crawler import Crawler

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

async def test_api_crawl_pattern():
    """
    Simulate exactly how the API performs a crawl
    """
    print("=== Testing API Crawl Pattern ===\n")

    # Initialize Crawler (as in perform_crawl function)
    crawler = Crawler(
        use_stealth=True,
        use_proxy=False,
        solve_captcha=True,
        headless=True
    )

    try:
        print("Initializing crawler...")
        await crawler.initialize()
        print("✓ Crawler initialized\n")

        print("Starting crawl...")
        result = await crawler.crawl(
            url="https://www.madagencytr.com/",
            use_browser=True,
            wait_time=0,
            max_retries=3
        )

        print(f"\n✓ Crawl completed successfully!")
        print(f"Status: {result.get('status')}")
        print(f"Title: {result.get('title')}")
        print(f"URL: {result.get('url')}")
        print(f"Method: {result.get('method')}")
        print(f"Duration: {result.get('crawl_duration', 0):.2f}s")

    except Exception as e:
        print(f"\n✗ Crawl failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing crawler...")
        await crawler.close()
        print("✓ Crawler closed")

if __name__ == "__main__":
    asyncio.run(test_api_crawl_pattern())
