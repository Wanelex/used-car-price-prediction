"""Day 3 Test: Content Extraction"""
import asyncio
from backend.crawler.engine import BrowserEngine
from backend.crawler.extractor import ContentExtractor
from loguru import logger

async def test_extraction():
    logger.info("Testing content extraction...")

    async with BrowserEngine(headless=False) as browser:
        await browser.navigate("https://example.com")
        page_data = await browser.get_page_content()

        # Extract structured content
        extractor = ContentExtractor(page_data["html"], page_data["url"])
        extracted = extractor.extract_all()

        logger.success(f"Title: {extracted['title']}")
        logger.success(f"Links found: {len(extracted['links'])}")
        logger.success(f"Images found: {len(extracted['images'])}")
        logger.success(f"Headings: {extracted['headings']}")

    logger.success("Extraction test completed!")

if __name__ == "__main__":
    asyncio.run(test_extraction())
