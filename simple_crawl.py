#!/usr/bin/env python3
"""
SIMPLEST WAY TO CRAWL A URL
Just 10 lines of code!
"""
import asyncio
from backend.crawler.crawler import Crawler


async def main():
    # Create crawler
    crawler = Crawler(
        use_stealth=False,
        use_proxy=False,
        solve_captcha=False
    )

    # Initialize
    await crawler.initialize()

    try:
        # Crawl!
        print("Crawling https://example.com...")
        result = await crawler.crawl(
            url="https://example.com",
            use_browser=False
        )

        # Print results
        print(f"\nTitle: {result['title']}")
        print(f"Status: {result['status']}")
        print(f"Text length: {len(result['text'])} characters")
        print(f"Links found: {len(result['links'])}")
        print(f"Images found: {len(result['images'])}")

        # Save to file
        import json
        with open("crawl_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nFull result saved to crawl_result.json")

    finally:
        await crawler.close()


if __name__ == "__main__":
    asyncio.run(main())
