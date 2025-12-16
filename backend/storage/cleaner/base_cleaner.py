"""Abstract base class for data cleaners"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, List
from loguru import logger


class BaseDataCleaner(ABC):
    """Abstract base class for data cleaning implementations"""

    def __init__(self):
        """Initialize cleaner"""
        self.logger = logger

    @abstractmethod
    def clean(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main cleaning method - must be implemented by subclasses

        Args:
            raw_data: Raw data dictionary from parser

        Returns:
            Cleaned and validated data dictionary
        """
        pass

    @abstractmethod
    def _validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate data - must be implemented by subclasses

        Returns:
            (is_valid: bool, errors: List[str])
        """
        pass

    @abstractmethod
    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate data quality score (0.0 to 1.0)
        Must be implemented by subclasses
        """
        pass

    def _count_non_empty_fields(self, data: Dict[str, Any], exclude_fields: List[str] = None) -> Tuple[int, int]:
        """
        Count non-empty fields vs total fields

        Returns:
            (non_empty_count, total_count)
        """
        if exclude_fields is None:
            exclude_fields = []

        total = 0
        non_empty = 0

        for key, value in data.items():
            if key in exclude_fields:
                continue

            total += 1

            # Consider field non-empty if it has a meaningful value
            if value is not None and value != '' and value != {} and value != []:
                non_empty += 1

        return non_empty, total

    def _log_cleaning_result(self, listing_id: str, original: Dict[str, Any], cleaned: Dict[str, Any], quality_score: float):
        """Log cleaning result for debugging"""
        orig_count = len([v for v in original.values() if v is not None])
        clean_count = len([v for v in cleaned.values() if v is not None])

        self.logger.info(
            f"Cleaned listing {listing_id}: "
            f"fields {orig_count}->{clean_count}, "
            f"quality_score={quality_score:.2f}"
        )
