"""
How to Use the REST API to Crawl Real URLs
This is the recommended production method
"""
import requests
import json
import time
from loguru import logger


# Configuration
API_BASE_URL = "http://localhost:8000"
API_HEADERS = {"Content-Type": "application/json"}


def example_1_simple_crawl_via_api():
    """
    Example 1: Simple crawl via REST API
    """
    logger.info("=" * 80)
    logger.info("EXAMPLE 1: Simple Crawl via REST API")
    logger.info("=" * 80)

    # Step 1: Make crawl request
    crawl_request = {
        "url": "https://httpbin.org/html",
        "use_stealth": False,
        "use_proxy": False,
        "solve_captcha": False,
        "timeout": 30,
        "max_retries": 3
    }

    logger.info(f"Starting crawl: {crawl_request['url']}")
    response = requests.post(
        f"{API_BASE_URL}/api/v1/crawl",
        json=crawl_request,
        headers=API_HEADERS
    )

    if response.status_code != 200:
        logger.error(f"Failed to start crawl: {response.status_code}")
        logger.error(response.text)
        return

    job_data = response.json()
    job_id = job_data["job_id"]
    logger.success(f"Crawl job started with ID: {job_id}")

    # Step 2: Check job status
    logger.info("Waiting for crawl to complete...")
    while True:
        status_response = requests.get(
            f"{API_BASE_URL}/api/v1/jobs/{job_id}/status",
            headers=API_HEADERS
        )

        status_data = status_response.json()
        status = status_data["status"]
        progress = status_data["progress"]

        logger.info(f"Status: {status} | Progress: {progress}%")

        if status in ["completed", "failed", "cancelled"]:
            break

        time.sleep(2)  # Check every 2 seconds

    # Step 3: Get results
    if status == "completed":
        result_response = requests.get(
            f"{API_BASE_URL}/api/v1/crawl/{job_id}/result",
            headers=API_HEADERS
        )

        result = result_response.json()
        logger.success(f"Title: {result.get('result', {}).get('title', 'N/A')}")
        logger.success(f"Status Code: {result.get('status_code', 'N/A')}")

        # Save result
        with open("api_example1.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info("Result saved to api_example1.json")
    else:
        logger.error(f"Crawl failed with status: {status}")

    return job_id


def example_2_crawl_with_browser():
    """
    Example 2: Crawl JavaScript-heavy site via API
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 2: JavaScript-Heavy Site via API")
    logger.info("=" * 80)

    crawl_request = {
        "url": "https://example.com",
        "use_stealth": True,
        "use_proxy": False,
        "solve_captcha": False,
        "wait_time": 2,  # Wait 2 seconds for JS to render
        "timeout": 60,
        "max_retries": 3
    }

    logger.info(f"Starting crawl with browser: {crawl_request['url']}")
    response = requests.post(
        f"{API_BASE_URL}/api/v1/crawl",
        json=crawl_request,
        headers=API_HEADERS
    )

    if response.status_code != 200:
        logger.error(f"Failed to start crawl: {response.status_code}")
        return

    job_data = response.json()
    job_id = job_data["job_id"]
    logger.success(f"Job ID: {job_id}")

    # Poll for completion
    logger.info("Waiting for browser-based crawl (this takes longer)...")
    max_wait = 120  # 2 minutes max
    start_time = time.time()

    while time.time() - start_time < max_wait:
        status_response = requests.get(
            f"{API_BASE_URL}/api/v1/jobs/{job_id}/status"
        )

        status_data = status_response.json()
        status = status_data["status"]

        if status in ["completed", "failed", "cancelled"]:
            logger.success(f"Crawl {status}!")
            break

        logger.info(f"Status: {status}")
        time.sleep(3)

    return job_id


def example_3_crawl_with_custom_headers():
    """
    Example 3: Crawl with custom headers
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 3: Crawl with Custom Headers")
    logger.info("=" * 80)

    crawl_request = {
        "url": "https://httpbin.org/html",
        "use_stealth": False,
        "custom_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Custom Agent"
        },
        "timeout": 30
    }

    logger.info("Starting crawl with custom headers...")
    response = requests.post(
        f"{API_BASE_URL}/api/v1/crawl",
        json=crawl_request
    )

    job_id = response.json()["job_id"]
    logger.success(f"Job started: {job_id}")

    return job_id


def example_4_list_all_jobs():
    """
    Example 4: List all crawl jobs
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 4: List All Jobs")
    logger.info("=" * 80)

    response = requests.get(
        f"{API_BASE_URL}/api/v1/jobs?limit=10&offset=0"
    )

    jobs = response.json()
    logger.info(f"Total jobs found: {len(jobs)}")

    for job in jobs[:5]:  # Show first 5
        logger.info(f"  - {job['job_id']}: {job['url']} ({job['status']})")


def example_5_get_crawler_stats():
    """
    Example 5: Get overall crawler statistics
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 5: Get Crawler Statistics")
    logger.info("=" * 80)

    response = requests.get(f"{API_BASE_URL}/api/v1/stats")
    stats = response.json()

    logger.info(f"Total jobs: {stats['total_jobs']}")
    logger.info(f"Pending jobs: {stats['pending_jobs']}")
    logger.info(f"Running jobs: {stats['running_jobs']}")
    logger.info(f"Completed jobs: {stats['completed_jobs']}")
    logger.info(f"Failed jobs: {stats['failed_jobs']}")
    logger.info(f"Success rate: {stats['success_rate']}%")
    logger.info(f"Avg response time: {stats['average_response_time']}s")


def example_6_health_check():
    """
    Example 6: Check API health
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 6: Health Check")
    logger.info("=" * 80)

    response = requests.get(f"{API_BASE_URL}/health")
    health = response.json()

    logger.info(f"Status: {health['status']}")
    logger.info(f"Version: {health['version']}")
    logger.info(f"Services: {health['services']}")


def example_7_crawl_and_wait():
    """
    Example 7: Crawl URL and wait for result synchronously
    """
    logger.info("\n" + "=" * 80)
    logger.info("EXAMPLE 7: Crawl and Wait (Synchronous)")
    logger.info("=" * 80)

    crawl_request = {
        "url": "https://httpbin.org/html",
        "use_stealth": False,
        "solve_captcha": False,
        "timeout": 30
    }

    logger.info(f"Starting crawl: {crawl_request['url']}")
    response = requests.post(
        f"{API_BASE_URL}/api/v1/crawl",
        json=crawl_request
    )

    job_id = response.json()["job_id"]
    logger.info(f"Job ID: {job_id}")

    # Wait loop
    timeout = 120
    start = time.time()

    while time.time() - start < timeout:
        status_resp = requests.get(
            f"{API_BASE_URL}/api/v1/jobs/{job_id}/status"
        )
        status = status_resp.json()["status"]

        if status == "completed":
            # Get result
            result_resp = requests.get(
                f"{API_BASE_URL}/api/v1/crawl/{job_id}/result"
            )
            result = result_resp.json()

            logger.success("Crawl completed!")
            logger.success(f"Title: {result.get('result', {}).get('title', 'N/A')}")

            with open("api_example7.json", "w") as f:
                json.dump(result, f, indent=2)
            logger.info("Result saved to api_example7.json")
            return result

        elif status == "failed":
            logger.error("Crawl failed!")
            return None

        logger.info(f"Status: {status}, waiting...")
        time.sleep(2)

    logger.error("Timeout waiting for crawl")
    return None


def main():
    """
    Run API examples
    """
    print("\n" + "=" * 80)
    print("REST API - CRAWL EXAMPLES")
    print("=" * 80)
    print("\nMake sure API is running: python run_api.py")
    print("=" * 80 + "\n")

    try:
        # Check if API is available
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        logger.success("API is running!")
    except requests.exceptions.ConnectionError:
        logger.error("ERROR: API is not running!")
        logger.error("Start the API with: venv/Scripts/python.exe run_api.py")
        return

    # Run examples
    print("\nRunning API examples...\n")

    # Health check
    example_6_health_check()

    # Simple crawl
    example_1_simple_crawl_via_api()

    # List jobs
    example_4_list_all_jobs()

    # Get stats
    example_5_get_crawler_stats()

    # Uncomment other examples as needed:
    # example_2_crawl_with_browser()
    # example_3_crawl_with_custom_headers()
    # example_7_crawl_and_wait()

    print("\n" + "=" * 80)
    print("API examples complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
