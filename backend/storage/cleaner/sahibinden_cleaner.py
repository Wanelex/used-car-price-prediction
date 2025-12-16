"""Sahibinden.com specific data cleaner"""

from typing import Any, Dict, Tuple, List, Optional
from decimal import Decimal
from loguru import logger

from .base_cleaner import BaseDataCleaner
from .validators import (
    validate_year, validate_price, validate_mileage, validate_boolean,
    normalize_fuel_type, validate_listing_id, validate_phone, validate_required_fields
)
from .transformers import (
    parse_turkish_number, parse_date, extract_numeric, clean_whitespace,
    parse_engine_specs, split_by_comma_or_newline, normalize_text
)
from config.settings import settings


class SahibindenDataCleaner(BaseDataCleaner):
    """Cleaner for sahibinden.com car listings"""

    def clean(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main cleaning method that processes all sections of raw data

        Args:
            raw_data: Raw parser output from sahibinden parser

        Returns:
            Cleaned and validated data dictionary
        """
        try:
            # Start with copy of raw data
            cleaned = raw_data.copy()

            # Clean each section
            cleaned = self._clean_overview(cleaned)
            cleaned = self._clean_details(cleaned)
            cleaned = self._clean_technical_specs(cleaned)
            cleaned = self._clean_features(cleaned)
            cleaned = self._clean_painted_parts(cleaned)

            # Validate and score
            is_valid, errors = self._validate(cleaned)
            quality_score = self._calculate_quality_score(cleaned)

            cleaned['data_quality_score'] = quality_score
            cleaned['is_valid'] = is_valid
            cleaned['validation_errors'] = errors

            # Log result
            self._log_cleaning_result(
                cleaned.get('listing_id', 'unknown'),
                raw_data,
                cleaned,
                quality_score
            )

            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning sahibinden data: {str(e)}")
            raise

    def _clean_overview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean overview section: listing ID, brand, model, year, price, mileage"""

        # listing_id (ilan_no)
        if 'ilan_no' in data:
            data['listing_id'] = validate_listing_id(data['ilan_no'])

        # Brand (marka)
        if 'marka' in data:
            data['brand'] = clean_whitespace(data['marka'])

        # Series (seri)
        if 'seri' in data:
            data['series'] = clean_whitespace(data['seri'])

        # Model
        if 'model' in data:
            data['model'] = clean_whitespace(data['model'])

        # Year (yil)
        if 'yil' in data:
            data['year'] = validate_year(data['yil'])

        # Price (fiyat)
        if 'fiyat' in data:
            data['price'] = validate_price(data['fiyat'])

        # Mileage (km)
        if 'km' in data:
            data['mileage'] = validate_mileage(data['km'])

        # Listing date (ilan_tarihi)
        if 'ilan_tarihi' in data:
            data['listing_date'] = parse_date(data['ilan_tarihi'])

        return data

    def _clean_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean details section: fuel type, transmission, body type, color, seller info"""

        # Fuel type (yakit_tipi)
        if 'yakit_tipi' in data:
            data['fuel_type'] = normalize_fuel_type(data['yakit_tipi'])

        # Transmission (vites)
        if 'vites' in data:
            data['transmission'] = clean_whitespace(data['vites'])

        # Body type (kasa_tipi)
        if 'kasa_tipi' in data:
            data['body_type'] = clean_whitespace(data['kasa_tipi'])

        # Engine power (motor_gucu)
        if 'motor_gucu' in data:
            data['engine_power'] = clean_whitespace(data['motor_gucu'])

        # Engine volume (motor_hacmi)
        if 'motor_hacmi' in data:
            data['engine_volume'] = clean_whitespace(data['motor_hacmi'])

        # Drive type (cekis)
        if 'cekis' in data:
            data['drive_type'] = clean_whitespace(data['cekis'])

        # Color (renk)
        if 'renk' in data:
            data['color'] = clean_whitespace(data['renk'])

        # Vehicle condition (arac_durumu)
        if 'arac_durumu' in data:
            data['vehicle_condition'] = clean_whitespace(data['arac_durumu'])

        # Seller type (kimden)
        if 'kimden' in data:
            data['seller_type'] = clean_whitespace(data['kimden'])

        # Location (konum)
        if 'konum' in data:
            data['location'] = clean_whitespace(data['konum'])

        # Warranty (garanti)
        if 'garanti' in data:
            data['warranty'] = clean_whitespace(data['garanti'])

        # Heavy damage (agir_hasar_kayitli)
        if 'agir_hasar_kayitli' in data:
            data['heavy_damage'] = validate_boolean(data['agir_hasar_kayitli'])

        # Plate origin (plaka_uyruk)
        if 'plaka_uyruk' in data:
            data['plate_origin'] = clean_whitespace(data['plaka_uyruk'])

        # Trade option (takas)
        if 'takas' in data:
            data['trade_option'] = validate_boolean(data['takas'])

        # Title (baslik)
        if 'baslik' in data:
            data['title'] = clean_whitespace(data['baslik'])

        # Description (aciklama)
        if 'aciklama' in data:
            data['description'] = normalize_text(data['aciklama'])

        # Phone (telefon)
        if 'telefon' in data:
            data['phone'] = validate_phone(data['telefon'])

        return data

    def _clean_technical_specs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and structure technical specifications"""

        if 'teknik_ozellikler' not in data or not data['teknik_ozellikler']:
            data['technical_specs'] = {}
            return data

        try:
            raw_specs = data['teknik_ozellikler']
            cleaned_specs = {}

            if isinstance(raw_specs, dict):
                # Already a dict, just clean values
                for key, value in raw_specs.items():
                    if value is not None and value != '':
                        cleaned_specs[clean_whitespace(key)] = clean_whitespace(str(value))

            data['technical_specs'] = cleaned_specs
            return data

        except Exception as e:
            logger.warning(f"Error cleaning technical specs: {str(e)}")
            data['technical_specs'] = {}
            return data

    def _clean_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and organize features (Güvenlik, Donanım, etc.)"""

        if 'ozellikler' not in data or not data['ozellikler']:
            data['features'] = {}
            return data

        try:
            raw_features = data['ozellikler']
            cleaned_features = {}

            if isinstance(raw_features, dict):
                # Already a dict structure
                for category, items in raw_features.items():
                    category_clean = clean_whitespace(category)

                    if isinstance(items, list):
                        # Already a list
                        cleaned_items = [clean_whitespace(item) for item in items if item]
                    elif isinstance(items, str):
                        # Parse comma-separated string
                        cleaned_items = split_by_comma_or_newline(items)
                    else:
                        continue

                    if cleaned_items:
                        cleaned_features[category_clean] = cleaned_items

            data['features'] = cleaned_features
            return data

        except Exception as e:
            logger.warning(f"Error cleaning features: {str(e)}")
            data['features'] = {}
            return data

    def _clean_painted_parts(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean painted and changed parts data"""

        if 'boyali_degisen' not in data or not data['boyali_degisen']:
            data['painted_parts'] = {}
            return data

        try:
            raw_painted = data['boyali_degisen']
            cleaned_painted = {}

            if isinstance(raw_painted, dict):
                # Clean boyali (painted parts)
                if 'boyali' in raw_painted and raw_painted['boyali']:
                    if isinstance(raw_painted['boyali'], list):
                        cleaned_painted['boyali'] = [
                            clean_whitespace(item) for item in raw_painted['boyali'] if item
                        ]
                    else:
                        items = split_by_comma_or_newline(raw_painted['boyali'])
                        if items:
                            cleaned_painted['boyali'] = items

                # Clean degisen (changed parts)
                if 'degisen' in raw_painted and raw_painted['degisen']:
                    if isinstance(raw_painted['degisen'], list):
                        cleaned_painted['degisen'] = [
                            clean_whitespace(item) for item in raw_painted['degisen'] if item
                        ]
                    else:
                        items = split_by_comma_or_newline(raw_painted['degisen'])
                        if items:
                            cleaned_painted['degisen'] = items

                # Keep image URLs if present
                if 'gorseller' in raw_painted and raw_painted['gorseller']:
                    if isinstance(raw_painted['gorseller'], list):
                        cleaned_painted['gorseller'] = [
                            url.strip() for url in raw_painted['gorseller'] if url and 'http' in url
                        ]

            data['painted_parts'] = cleaned_painted
            return data

        except Exception as e:
            logger.warning(f"Error cleaning painted parts: {str(e)}")
            data['painted_parts'] = {}
            return data

    def _validate(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate cleaned data

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        required_fields = settings.MIN_REQUIRED_FIELDS
        is_valid, missing = validate_required_fields(data, required_fields)

        if missing:
            errors.append(f"Missing required fields: {', '.join(missing)}")

        # Validate data types
        if data.get('year') is not None and not isinstance(data['year'], int):
            errors.append(f"Year should be int, got {type(data['year'])}")

        if data.get('price') is not None and not isinstance(data['price'], Decimal):
            errors.append(f"Price should be Decimal, got {type(data['price'])}")

        if data.get('mileage') is not None and not isinstance(data['mileage'], int):
            errors.append(f"Mileage should be int, got {type(data['mileage'])}")

        return len(errors) == 0, errors

    def _calculate_quality_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate data quality score based on:
        1. Completeness (% of fields filled)
        2. Critical fields presence (brand, model, year, price, mileage)

        Returns:
            Score from 0.0 to 1.0
        """
        try:
            # Count non-empty fields
            non_empty, total = self._count_non_empty_fields(
                data,
                exclude_fields=['cleaning_error', 'db_id']
            )

            # Completeness score
            completeness = non_empty / total if total > 0 else 0

            # Critical fields score
            critical_fields = ['listing_id', 'brand', 'model', 'year', 'price', 'mileage']
            critical_filled = sum(1 for f in critical_fields if data.get(f))
            critical_score = critical_filled / len(critical_fields)

            # Combined score: 60% completeness + 40% critical
            quality_score = (completeness * 0.6) + (critical_score * 0.4)

            return round(min(quality_score, 1.0), 2)

        except Exception as e:
            logger.warning(f"Error calculating quality score: {str(e)}")
            return 0.0
