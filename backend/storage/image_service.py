"""Image download and management service"""

import os
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from datetime import datetime
from PIL import Image
from loguru import logger

from config.settings import settings
from backend.crawler.http_client import HTTPClient


class ImageDownloadService:
    """
    Service for downloading and managing listing images
    Downloads first 2 main images + painted parts diagram
    Stores with metadata
    """

    def __init__(self):
        """Initialize image service"""
        self.storage_path = Path(settings.IMAGE_STORAGE_PATH)
        self.max_size_mb = settings.MAX_IMAGE_SIZE_MB
        self.supported_formats = settings.SUPPORTED_IMAGE_FORMATS
        self.timeout = settings.IMAGE_DOWNLOAD_TIMEOUT
        self.http_client = HTTPClient()
        self.logger = logger

        # Ensure storage directory exists
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Image storage initialized at: {self.storage_path}")

    async def download_listing_images(
        self,
        listing_id: str,
        main_urls: Optional[List[str]] = None,
        painted_url: Optional[str] = None,
    ) -> List[Dict[str, any]]:
        """
        Download first 2 main images and painted parts diagram

        Args:
            listing_id: Listing ID for organizing files
            main_urls: List of main listing image URLs
            painted_url: URL of painted parts diagram image

        Returns:
            List of successfully downloaded image records with metadata
        """
        image_records = []

        try:
            # Ensure listing directory exists
            listing_dir = self._create_listing_directory(listing_id)

            # Download main images (first 2)
            if main_urls:
                for idx, url in enumerate(main_urls[:2]):
                    if not url or not isinstance(url, str):
                        continue

                    try:
                        record = await self._download_image(
                            url=url,
                            listing_id=listing_id,
                            image_type="main",
                            image_order=idx,
                            save_dir=listing_dir
                        )
                        if record:
                            image_records.append(record)
                    except Exception as e:
                        self.logger.warning(f"Failed to download main image {idx}: {str(e)}")
                        continue

            # Download painted diagram (if available)
            if painted_url:
                if isinstance(painted_url, str) and painted_url.strip():
                    try:
                        record = await self._download_image(
                            url=painted_url,
                            listing_id=listing_id,
                            image_type="painted_diagram",
                            image_order=None,
                            save_dir=listing_dir
                        )
                        if record:
                            image_records.append(record)
                    except Exception as e:
                        self.logger.warning(f"Failed to download painted diagram: {str(e)}")

            if image_records:
                self.logger.info(f"Downloaded {len(image_records)} images for listing {listing_id}")
            else:
                self.logger.warning(f"No images downloaded for listing {listing_id}")

            return image_records

        except Exception as e:
            self.logger.error(f"Error downloading images for listing {listing_id}: {str(e)}")
            return image_records

    async def _download_image(
        self,
        url: str,
        listing_id: str,
        image_type: str,
        image_order: Optional[int],
        save_dir: Path,
    ) -> Optional[Dict[str, any]]:
        """
        Download single image with retry logic

        Args:
            url: Image URL
            listing_id: Listing ID
            image_type: Type of image (main, painted_diagram)
            image_order: Order of image (0, 1, None)
            save_dir: Directory to save image

        Returns:
            Image record dict with metadata or None if failed
        """
        if not url or not isinstance(url, str) or not url.startswith('http'):
            self.logger.debug(f"Invalid image URL: {url}")
            return None

        # Generate filename
        filename = self._generate_filename(image_type, image_order)

        # Download with retry
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Download image using HTTP client
                image_data = await self.http_client.fetch_content(
                    url,
                    timeout=self.timeout
                )

                if not image_data:
                    self.logger.warning(f"No data received for {url}")
                    continue

                # Validate image
                image_path = save_dir / filename
                if self._save_and_validate_image(image_data, image_path):
                    # Extract metadata
                    metadata = self._get_image_metadata(image_path)

                    # Calculate relative path for storage
                    rel_path = str(image_path.relative_to(self.storage_path))

                    record = {
                        'image_type': image_type,
                        'image_order': image_order,
                        'original_url': url,
                        'local_path': rel_path,
                        'file_size': metadata['file_size'],
                        'width': metadata['width'],
                        'height': metadata['height'],
                        'downloaded_at': datetime.utcnow().isoformat(),
                    }

                    self.logger.info(f"Downloaded image: {image_type}_{image_order} -> {rel_path}")
                    return record
                else:
                    self.logger.warning(f"Image validation failed for {url}")
                    continue

            except Exception as e:
                self.logger.debug(f"Attempt {attempt + 1}/{max_retries} failed for {url}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)  # Wait before retry
                continue

        self.logger.warning(f"Failed to download image after {max_retries} attempts: {url}")
        return None

    def _create_listing_directory(self, listing_id: str) -> Path:
        """
        Create directory structure for listing images
        Structure: images/{YYYY}/{MM}/{listing_id}/
        """
        now = datetime.utcnow()
        year = str(now.year)
        month = str(now.month).zfill(2)

        dir_path = self.storage_path / year / month / listing_id
        dir_path.mkdir(parents=True, exist_ok=True)

        return dir_path

    def _generate_filename(self, image_type: str, image_order: Optional[int]) -> str:
        """
        Generate filename for image
        main_0.jpg, main_1.jpg, painted_diagram.jpg
        """
        if image_type == "main":
            return f"main_{image_order}.jpg"
        elif image_type == "painted_diagram":
            return "painted_diagram.jpg"
        else:
            return f"{image_type}.jpg"

    def _save_and_validate_image(self, image_data: bytes, save_path: Path) -> bool:
        """
        Save and validate image data

        Returns:
            True if valid and saved, False otherwise
        """
        try:
            # Check file size
            file_size_mb = len(image_data) / (1024 * 1024)
            if file_size_mb > self.max_size_mb:
                self.logger.warning(f"Image too large: {file_size_mb:.2f}MB > {self.max_size_mb}MB")
                return False

            # Try to open with PIL to validate
            try:
                from io import BytesIO
                img = Image.open(BytesIO(image_data))
                img.verify()  # Verify image integrity
            except Exception as e:
                self.logger.warning(f"Image validation failed: {str(e)}")
                # Still try to save even if validation fails
                pass

            # Save to disk
            with open(save_path, 'wb') as f:
                f.write(image_data)

            # Verify file was written
            if save_path.exists() and save_path.stat().st_size > 0:
                return True

            return False

        except Exception as e:
            self.logger.error(f"Error saving/validating image: {str(e)}")
            return False

    def _get_image_metadata(self, image_path: Path) -> Dict[str, any]:
        """
        Extract image metadata (dimensions, file size)
        """
        try:
            metadata = {
                'file_size': image_path.stat().st_size,
                'width': None,
                'height': None,
            }

            # Try to get dimensions using PIL
            try:
                img = Image.open(image_path)
                metadata['width'] = img.width
                metadata['height'] = img.height
            except Exception as e:
                self.logger.debug(f"Could not extract image dimensions: {str(e)}")

            return metadata

        except Exception as e:
            self.logger.error(f"Error extracting image metadata: {str(e)}")
            return {
                'file_size': 0,
                'width': None,
                'height': None,
            }

    def cleanup_failed_downloads(self, listing_id: str):
        """
        Cleanup image files for failed download
        """
        try:
            # Find and remove all directories for this listing
            for year_dir in self.storage_path.iterdir():
                if not year_dir.is_dir():
                    continue
                for month_dir in year_dir.iterdir():
                    if not month_dir.is_dir():
                        continue
                    listing_dir = month_dir / listing_id
                    if listing_dir.exists():
                        import shutil
                        shutil.rmtree(listing_dir)
                        self.logger.info(f"Cleaned up images for failed listing: {listing_id}")

        except Exception as e:
            self.logger.warning(f"Error during cleanup: {str(e)}")

    def get_image_path(self, relative_path: str) -> Optional[Path]:
        """Get full path for a relative image path"""
        full_path = self.storage_path / relative_path
        if full_path.exists():
            return full_path
        return None
