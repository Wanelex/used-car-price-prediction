"""
Example: How to use the crawler with real URLs
Shows multiple methods to crawl actual websites
"""
import asyncio
import json
from loguru import logger
from backend.crawler.crawler import Crawler

# Configure logging
logger.enable("backend")


async def example_1_simple_crawl():
    """
    Example 1: Simple HTTP crawl (fastest, for simple sites)
    """
    logger.info("=" * 80)
    logger.info("EXAMPLE 1: Simple HTTP Crawl (Fast)")
    logger.info("=" * 80)

    crawler = Crawler(
        use_stealth=False,      # Don't need browser for simple sites
        use_proxy=False,        # No proxy needed
        solve_captcha=False     # No CAPTCHA solving
    )

    await crawler.initialize()

    try:
        # Crawl a simple website
        result = await crawler.crawl(
            url="https://httpbin.org/html",  # Test site that returns HTML
            use_browser=False  # Use HTTP client (faster)
        )

        logger.success(f"Status: {result['status']}")
        logger.success(f"Title: {result['title']}")
        logger.success(f"Content length: {len(result['text'])} characters")
        logger.success(f"Links found: {len(result['links'])}")

        # Save result
        with open("example1_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("Result saved to example1_result.json")

    finally:
        await crawler.close()


async def example_2_javascript_site():
    """
    Example 2: Crawl JavaScript-heavy site (needs browser)
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 2: JavaScript-Heavy Site (Browser)")
    logger.info("=" * 80)

    crawler = Crawler(
        use_stealth=True,       # Enable stealth mode
        use_proxy=False,        # No proxy needed
        solve_captcha=False     # No CAPTCHA
    )

    await crawler.initialize()

    try:
        # Crawl a site that needs JavaScript rendering
        result = await crawler.crawl(
            url="https://example.com",
            use_browser=True,       # Use browser for JavaScript
            wait_time=2             # Wait 2 seconds after page loads
        )

        logger.success(f"Status: {result['status']}")
        logger.success(f"Title: {result['title']}")
        logger.success(f"Method used: {result['method']}")

        with open("example2_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("Result saved to example2_result.json")

    finally:
        await crawler.close()


async def example_3_with_captcha():
    """
    Example 3: Crawl site with CAPTCHA (requires API keys)
    Note: You need 2Captcha or Anti-Captcha API keys for this
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 3: Site with CAPTCHA Protection")
    logger.info("=" * 80)

    crawler = Crawler(
        use_stealth=True,       # Enable stealth
        use_proxy=False,
        solve_captcha=True      # Enable CAPTCHA solving
    )

    await crawler.initialize()

    try:
        # This will automatically detect and solve CAPTCHAs
        result = await crawler.crawl(
            url="https://example.com",
            use_browser=True,
            max_retries=3  # Retry if CAPTCHA fails
        )

        logger.success(f"Status: {result['status']}")
        logger.success(f"CAPTCHA detected: {result.get('captcha_detected', False)}")
        logger.success(f"CAPTCHA solved: {result.get('captcha_solved', False)}")

        with open("example3_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("Result saved to example3_result.json")

    finally:
        await crawler.close()


async def example_4_with_wait_selector():
    """
    Example 4: Wait for specific element to load
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 4: Wait for Specific Element")
    logger.info("=" * 80)

    crawler = Crawler(
        use_stealth=True,
        use_proxy=False,
        solve_captcha=False
    )

    await crawler.initialize()

    try:
        # Wait for a specific CSS selector to appear
        result = await crawler.crawl(
            url="https://example.com",
            use_browser=True,
            wait_for_selector="p",  # Wait for first paragraph
            wait_time=2
        )

        logger.success(f"Status: {result['status']}")
        logger.success(f"Content found: {len(result['text'])} characters")

        with open("example4_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("Result saved to example4_result.json")

    finally:
        await crawler.close()


async def example_5_extract_structured_data():
    """
    Example 5: Extract structured data from page
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 5: Extract Structured Data")
    logger.info("=" * 80)

    crawler = Crawler(
        use_stealth=True,
        use_proxy=False,
        solve_captcha=False
    )

    await crawler.initialize()

    try:
        result = await crawler.crawl(
            url="https://example.com",
            use_browser=False
        )

        logger.success(f"Title: {result['title']}")
        logger.success(f"Text preview: {result['text'][:200]}...")
        logger.success(f"Images found: {len(result['images'])}")
        logger.success(f"Links found: {len(result['links'])}")
        logger.success(f"Headings (h1): {len(result['headings'].get('h1', []))}")
        logger.success(f"Headings (h2): {len(result['headings'].get('h2', []))}")

        # Save full result with all extracted data
        with open("example5_structured.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("Structured data saved to example5_structured.json")

    finally:
        await crawler.close()


async def example_6_sahibinden_parser():
    """
    Example 6: Use specialized parser for sahibinden.com car listings
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 6: Specialized Parser (sahibinden.com)")
    logger.info("=" * 80)

    crawler = Crawler(
        use_stealth=True,
        use_proxy=False,
        solve_captcha=True
    )

    await crawler.initialize()

    try:
        # Example sahibinden.com car listing URL
        # In real use, replace with actual listing URL
        result = await crawler.crawl(
            url="https://example.com",  # Replace with real sahibinden URL
            use_browser=True,
            max_retries=3
        )

        # Check if specialized parser extracted data
        if "sahibinden_listing" in result:
            listing = result["sahibinden_listing"]
            logger.success(f"Brand: {listing.get('marka')}")
            logger.success(f"Model: {listing.get('model')}")
            logger.success(f"Year: {listing.get('yil')}")
            logger.success(f"Price: {listing.get('fiyat')}")
            logger.success(f"Mileage: {listing.get('km')}")

            with open("example6_sahibinden.json", "w", encoding="utf-8") as f:
                json.dump(listing, f, indent=2, ensure_ascii=False)
            logger.info("Sahibinden listing saved to example6_sahibinden.json")

    finally:
        await crawler.close()


async def main():
    """
    Run all examples
    Choose which ones to run based on your needs
    """
    print("\n" + "=" * 80)
    print("WEB CRAWLER - REAL URL EXAMPLES")
    print("=" * 80)
    print("\nThis script demonstrates 6 different ways to crawl websites:")
    print("1. Simple HTTP crawl (fastest)")
    print("2. JavaScript-heavy site (needs browser)")
    print("3. Site with CAPTCHA (requires API keys)")
    print("4. Wait for specific element")
    print("5. Extract structured data")
    print("6. Use specialized parser")
    print("=" * 80 + "\n")

    # Run examples (uncomment the ones you want to test)

    # Example 1: Simple crawl
    await example_1_simple_crawl()

    # Example 2: Browser crawl
    # await example_2_javascript_site()

    # Example 3: CAPTCHA (uncomment if you have API keys)
    # await example_3_with_captcha()

    # Example 4: Wait for selector
    # await example_4_with_wait_selector()

    # Example 5: Extract structured data
    # await example_5_extract_structured_data()

    # Example 6: Specialized parser
    # await example_6_sahibinden_parser()

    print("\n" + "=" * 80)
    print("Examples complete! Check the generated JSON files for results.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
