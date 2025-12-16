"""Field validators for car listing data"""

import re
from typing import Optional
from decimal import Decimal
from datetime import datetime
from loguru import logger


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def validate_year(year_str: str) -> Optional[int]:
    """
    Validate and convert year to integer
    Accepts: "2004", "2004.0", "2004 MODEL"
    Returns: int or None if invalid
    """
    if not year_str or isinstance(year_str, int):
        return year_str if isinstance(year_str, int) else None

    try:
        year_str = str(year_str).strip().split()[0]  # Get first part before space
        year = int(float(year_str))

        # Validate year is reasonable (1900-2025)
        if 1900 <= year <= 2025:
            return year
        logger.warning(f"Year out of reasonable range: {year}")
        return None
    except (ValueError, AttributeError):
        logger.debug(f"Could not parse year: {year_str}")
        return None


def validate_price(price_str: str) -> Optional[Decimal]:
    """
    Validate and convert price to Decimal
    Accepts: "850.000 TL", "850000", "850,000 TL"
    Returns: Decimal or None if invalid
    """
    if not price_str:
        return None

    try:
        # Remove non-numeric characters except comma and dot
        price_str = str(price_str).strip()

        # Handle Turkish format: "850.000 TL"
        if ',' in price_str:
            price_str = price_str.replace(',', '.')  # Convert comma to dot

        # Remove "TL" and other text
        price_str = re.sub(r'[^\d.]', '', price_str)

        # Handle Turkish thousand separator (dot) vs decimal separator
        if price_str.count('.') > 1:
            # Multiple dots: "850.000.00" -> convert to "850000.00"
            parts = price_str.split('.')
            price_str = ''.join(parts[:-1]) + '.' + parts[-1]
        elif price_str.count('.') == 1 and len(price_str.split('.')[-1]) != 2:
            # Single dot with non-2-digit decimal: "850.000" -> "850000"
            price_str = price_str.replace('.', '')

        if price_str:
            price = Decimal(price_str)
            if price > 0:
                return price

        return None
    except (ValueError, AttributeError):
        logger.debug(f"Could not parse price: {price_str}")
        return None


def validate_mileage(km_str: str) -> Optional[int]:
    """
    Validate and convert mileage to integer
    Accepts: "389.000", "389000", "389,000 km"
    Returns: int or None if invalid
    """
    if not km_str:
        return None

    try:
        km_str = str(km_str).strip()

        # Special case: "0 km" is valid for new cars
        if km_str.lower().startswith('0'):
            return 0

        # Remove non-numeric characters
        km_str = re.sub(r'[^\d]', '', km_str)

        if km_str:
            km = int(km_str)
            if 0 <= km <= 1000000:  # Reasonable range
                return km

        return None
    except (ValueError, AttributeError):
        logger.debug(f"Could not parse mileage: {km_str}")
        return None


def validate_boolean(value: str) -> Optional[bool]:
    """
    Convert Turkish/English boolean strings to bool
    Accepts: "Evet"/"Hayır", "Yes"/"No", "Var"/"Yok", "1"/"0"
    Returns: bool or None if invalid
    """
    if value is None:
        return None

    value_str = str(value).strip().lower()

    true_values = {'evet', 'yes', 'var', 'true', '1', 'y'}
    false_values = {'hayır', 'no', 'yok', 'false', '0', 'n'}

    if value_str in true_values:
        return True
    elif value_str in false_values:
        return False
    else:
        logger.debug(f"Could not parse boolean value: {value}")
        return None


def normalize_fuel_type(fuel: str) -> Optional[str]:
    """
    Normalize fuel type to standard values
    """
    if not fuel:
        return None

    fuel_lower = fuel.strip().lower()

    # Mapping of variations to standard names
    fuel_map = {
        'benzin': 'Benzin',
        'dizel': 'Dizel',
        'elektrikli': 'Elektrikli',
        'hibrit': 'Hibrit',
        'lpg': 'LPG',
        'benzin/lpg': 'Benzin/LPG',
        'dizel/lpg': 'Dizel/LPG',
        'doğalgaz': 'Doğalgaz',
        'cng': 'Doğalgaz',
    }

    for pattern, standard in fuel_map.items():
        if pattern in fuel_lower:
            return standard

    # Return original if no mapping found
    return fuel.strip() if fuel else None


def validate_listing_id(listing_id: str) -> Optional[str]:
    """
    Validate listing ID (ilan_no)
    Should be numeric string
    """
    if not listing_id:
        return None

    listing_id_str = str(listing_id).strip()

    if listing_id_str.isdigit() and len(listing_id_str) >= 8:
        return listing_id_str

    logger.warning(f"Invalid listing ID format: {listing_id}")
    return None


def validate_phone(phone: str) -> Optional[str]:
    """
    Validate phone number
    Turkish format: "543 728 77 68" or "5437287768"
    """
    if not phone:
        return None

    # Remove all non-digit characters
    phone_digits = re.sub(r'\D', '', phone)

    # Turkish phone should be 10 digits (0 prefix removed)
    if len(phone_digits) == 10 and phone_digits.startswith('5'):
        # Format as: "XXX XXX XX XX"
        return f"{phone_digits[:3]} {phone_digits[3:6]} {phone_digits[6:8]} {phone_digits[8:10]}"
    elif len(phone_digits) == 11 and phone_digits.startswith('0'):
        # With country code, remove 0 and retry
        return validate_phone(phone_digits[1:])

    # If no formatting could be applied, return original if looks like phone
    if re.search(r'\d{3}.*\d{3}.*\d{2}.*\d{2}', phone):
        return phone.strip()

    logger.debug(f"Could not validate phone number: {phone}")
    return None


def validate_required_fields(data: dict, required_fields: list[str]) -> tuple[bool, list[str]]:
    """
    Check if all required fields are present and non-empty
    Returns: (is_valid, list_of_missing_fields)
    """
    missing = []

    for field in required_fields:
        value = data.get(field)
        if value is None or value == '' or value == {} or value == []:
            missing.append(field)

    return len(missing) == 0, missing
