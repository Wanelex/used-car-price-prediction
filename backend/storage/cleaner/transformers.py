"""Data transformation utilities for cleaning raw data"""

import re
from typing import Optional, Any, Dict
from loguru import logger


def parse_turkish_number(value: str) -> Optional[int]:
    """
    Parse Turkish number format
    "389.000" -> 389000
    "850,5" -> 8505 (decimals removed)
    """
    if not value:
        return None

    try:
        value_str = str(value).strip()

        # Replace comma with dot for decimal handling
        value_str = value_str.replace(',', '.')

        # Handle multiple dots (thousands separators)
        if value_str.count('.') > 1:
            parts = value_str.split('.')
            # Assume last part is decimal if it's 2 digits, otherwise it's thousands sep
            if len(parts[-1]) == 2 and parts[-1].isdigit():
                value_str = ''.join(parts[:-1]) + '.' + parts[-1]
            else:
                value_str = ''.join(parts)

        # Convert to int (remove decimals)
        result = int(float(value_str))
        return result if result >= 0 else None
    except (ValueError, AttributeError):
        logger.debug(f"Could not parse Turkish number: {value}")
        return None


def parse_date(date_str: str) -> Optional[str]:
    """
    Parse Turkish date format
    "15 Aralık 2025" -> "2025-12-15"
    "15/12/2025" -> "2025-12-15"
    Returns ISO format string or None
    """
    if not date_str:
        return None

    try:
        date_str = str(date_str).strip()

        # Turkish month mapping
        month_map = {
            'ocak': '01', 'şubat': '02', 'mart': '03',
            'nisan': '04', 'mayıs': '05', 'haziran': '06',
            'temmuz': '07', 'ağustos': '08', 'eylül': '09',
            'ekim': '10', 'kasım': '11', 'aralık': '12'
        }

        # Try Turkish format: "15 Aralık 2025"
        for month_name, month_num in month_map.items():
            if month_name in date_str.lower():
                # Extract day and year
                parts = date_str.split()
                if len(parts) >= 3:
                    day = parts[0]
                    year = parts[-1]
                    return f"{year}-{month_num}-{day.zfill(2)}"

        # Try standard formats
        # "15/12/2025" or "15-12-2025"
        for sep in ['/', '-']:
            if sep in date_str:
                parts = date_str.split(sep)
                if len(parts) == 3:
                    day, month, year = parts
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        return None
    except (ValueError, AttributeError, IndexError):
        logger.debug(f"Could not parse date: {date_str}")
        return None


def extract_numeric(text: str) -> Optional[int]:
    """
    Extract first numeric value from text
    "231 hp" -> 231
    "2979 cc" -> 2979
    """
    if not text:
        return None

    try:
        # Find all numeric sequences
        numbers = re.findall(r'\d+', str(text))
        if numbers:
            return int(numbers[0])
        return None
    except (ValueError, AttributeError):
        logger.debug(f"Could not extract numeric value from: {text}")
        return None


def clean_whitespace(text: str) -> Optional[str]:
    """
    Clean and normalize whitespace
    Removes extra spaces, newlines, etc.
    """
    if not text:
        return None

    try:
        # Convert to string if needed
        text_str = str(text).strip()

        # Replace multiple spaces with single space
        text_str = re.sub(r'\s+', ' ', text_str)

        # Remove trailing/leading whitespace
        text_str = text_str.strip()

        return text_str if text_str else None
    except (AttributeError, TypeError):
        return None


def normalize_text(text: str) -> Optional[str]:
    """
    Normalize text: clean whitespace, remove special chars if needed
    """
    if not text:
        return None

    try:
        # Clean whitespace
        text = clean_whitespace(text)

        # Remove extra punctuation
        text = text.replace('  ,', ',')
        text = text.replace(' ,', ',')

        return text
    except (AttributeError, TypeError):
        return None


def parse_engine_specs(text: str) -> Optional[Dict[str, Any]]:
    """
    Parse engine specifications
    "1.6 16V" -> {"volume": 1.6, "valves": 16}
    "2979 cc" -> {"volume_cc": 2979}
    """
    if not text:
        return None

    try:
        specs = {}
        text = str(text).strip().lower()

        # Look for cc/ccm
        cc_match = re.search(r'(\d+)\s*(?:cc|ccm)', text)
        if cc_match:
            specs['volume_cc'] = int(cc_match.group(1))

        # Look for liters (1.6, 2.0, etc)
        liter_match = re.search(r'(\d+\.?\d*)\s*[lL]', text)
        if liter_match:
            specs['volume_l'] = float(liter_match.group(1))

        # Look for valves (16V, 8V, etc)
        valves_match = re.search(r'(\d+)\s*v(?:alves)?', text, re.IGNORECASE)
        if valves_match:
            specs['valves'] = int(valves_match.group(1))

        return specs if specs else None
    except (ValueError, AttributeError):
        logger.debug(f"Could not parse engine specs: {text}")
        return None


def split_by_comma_or_newline(text: str) -> Optional[list]:
    """
    Split text by comma or newline
    Cleans each item
    """
    if not text:
        return None

    try:
        # Replace newlines with comma for uniform splitting
        text = str(text).replace('\n', ',').replace(';', ',')

        # Split by comma
        items = [item.strip() for item in text.split(',')]

        # Filter empty items
        items = [item for item in items if item and len(item) > 0]

        return items if items else None
    except (AttributeError, TypeError):
        return None


def extract_location_parts(location_str: str) -> Optional[Dict[str, str]]:
    """
    Extract location parts from format like "Ankara / Çankaya / Aşıkpaşa"
    Returns: {city: "Ankara", district: "Çankaya", neighborhood: "Aşıkpaşa"}
    """
    if not location_str:
        return None

    try:
        parts = [p.strip() for p in location_str.split('/')]

        location_dict = {}
        if len(parts) >= 1:
            location_dict['city'] = parts[0]
        if len(parts) >= 2:
            location_dict['district'] = parts[1]
        if len(parts) >= 3:
            location_dict['neighborhood'] = parts[2]

        return location_dict if location_dict else None
    except (AttributeError, TypeError):
        return None
