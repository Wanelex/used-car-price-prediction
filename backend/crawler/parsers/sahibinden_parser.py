"""
Specialized parser for sahibinden.com car listings
Extracts structured data from vehicle detail pages
"""
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from loguru import logger
import re
import json


class SahibindenCarParser:
    """Parser for sahibinden.com car listing pages"""

    def __init__(self, html: str, url: str):
        self.html = html
        self.url = url
        self.soup = BeautifulSoup(html, 'html.parser')
        self.json_data = self._extract_json_data()

    def _extract_json_data(self) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from pageTrackData JSON in the page
        This is the most reliable method as sahibinden.com includes all data in a script tag
        """
        try:
            # Find script tags containing pageTrackData
            scripts = self.soup.find_all('script')
            for script in scripts:
                script_text = script.string
                if script_text and 'pageTrackData' in script_text:
                    # Extract the JSON data
                    # Pattern: var pageTrackData = {...};
                    match = re.search(r'var pageTrackData = ({.*?});', script_text, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                        data = json.loads(json_str)

                        # Extract customVars which contains all the listing details
                        if 'customVars' in data:
                            # Convert customVars array to dict
                            result = {}
                            for var in data['customVars']:
                                if 'name' in var and 'value' in var:
                                    result[var['name']] = var['value']
                            logger.success(f"Extracted {len(result)} fields from pageTrackData JSON")
                            return result
            return None
        except Exception as e:
            logger.debug(f"Could not extract JSON data: {str(e)}")
            return None

    def _extract_from_list(self, label: str) -> Optional[str]:
        """
        Extract attribute from classified-info-list
        Fallback method if JSON extraction fails
        """
        try:
            # Find the UL with class="classified-info-list"
            info_list = self.soup.find('ul', class_='classified-info-list')
            if not info_list:
                return None

            # Find all LI items
            items = info_list.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                # Check if this item starts with the label
                if text.startswith(label):
                    # Remove the label to get the value
                    value = text.replace(label, '', 1).strip()
                    return value if value else None

            return None
        except Exception as e:
            logger.debug(f"Could not extract '{label}' from list: {str(e)}")
            return None

    def parse(self) -> Dict[str, Any]:
        """
        Parse all car listing data

        Returns:
            Dict with all extracted fields
        """
        try:
            data = {
                # Basic Info
                'ilan_no': self.extract_listing_number(),
                'ilan_tarihi': self.extract_listing_date(),
                'url': self.url,

                # Vehicle Details
                'marka': self.extract_brand(),
                'seri': self.extract_series(),
                'model': self.extract_model(),
                'yil': self.extract_year(),
                'yakit_tipi': self.extract_fuel_type(),
                'vites': self.extract_transmission(),
                'arac_durumu': self.extract_vehicle_condition(),
                'km': self.extract_mileage(),
                'kasa_tipi': self.extract_body_type(),
                'motor_gucu': self.extract_engine_power(),
                'motor_hacmi': self.extract_engine_volume(),
                'cekis': self.extract_drive_type(),
                'renk': self.extract_color(),

                # Seller Info
                'garanti': self.extract_warranty(),
                'agir_hasar_kayitli': self.extract_heavy_damage(),
                'plaka_uyruk': self.extract_plate_origin(),
                'kimden': self.extract_seller_type(),
                'takas': self.extract_trade(),

                # Price
                'fiyat': self.extract_price(),

                # Description
                'baslik': self.extract_title(),
                'aciklama': self.extract_description(),

                # Images
                'resimler': self.extract_images(),

                # Location
                'konum': self.extract_location(),

                # Contact
                'telefon': self.extract_phone(),

                # Detailed sections
                'ozellikler': self.extract_features(),
                'boyali_degisen': self.extract_painted_parts(),
                'teknik_ozellikler': self.extract_technical_specs(),
            }

            logger.success(f"Successfully parsed sahibinden.com listing: {data.get('ilan_no', 'Unknown')}")
            return data

        except Exception as e:
            logger.error(f"Error parsing sahibinden.com listing: {str(e)}")
            return {}

    def extract_listing_number(self) -> Optional[str]:
        """Extract İlan No"""
        # Method 1: From JSON
        if self.json_data and 'İlan No' in self.json_data:
            return self.json_data['İlan No']

        # Method 2: From list
        value = self._extract_from_list('İlan No')
        if value:
            return value

        # Method 3: From URL
        match = re.search(r'/(\d+)/detay', self.url)
        if match:
            return match.group(1)

        return None

    def extract_listing_date(self) -> Optional[str]:
        """Extract İlan Tarihi"""
        # Method 1: From JSON
        if self.json_data and 'İlan Tarihi' in self.json_data:
            return self.json_data['İlan Tarihi']

        # Method 2: From list
        return self._extract_from_list('İlan Tarihi')

    def extract_brand(self) -> Optional[str]:
        """Extract Marka"""
        # Method 1: From JSON
        if self.json_data and 'Marka' in self.json_data:
            return self.json_data['Marka']

        # Method 2: From list
        return self._extract_from_list('Marka')

    def extract_series(self) -> Optional[str]:
        """Extract Seri"""
        # Method 1: From JSON
        if self.json_data and 'Seri' in self.json_data:
            return self.json_data['Seri']

        # Method 2: From list
        return self._extract_from_list('Seri')

    def extract_model(self) -> Optional[str]:
        """Extract Model"""
        # Method 1: From JSON
        if self.json_data and 'Model' in self.json_data:
            return self.json_data['Model']

        # Method 2: From list
        return self._extract_from_list('Model')

    def extract_year(self) -> Optional[str]:
        """Extract Yıl"""
        # Method 1: From JSON
        if self.json_data and 'Yıl' in self.json_data:
            return self.json_data['Yıl']

        # Method 2: From list
        return self._extract_from_list('Yıl')

    def extract_fuel_type(self) -> Optional[str]:
        """Extract Yakıt Tipi"""
        # Method 1: From JSON
        if self.json_data and 'Yakıt Tipi' in self.json_data:
            return self.json_data['Yakıt Tipi']

        # Method 2: From list
        value = self._extract_from_list('Yakıt')
        if not value:
            value = self._extract_from_list('Yakıt Tipi')
        return value

    def extract_transmission(self) -> Optional[str]:
        """Extract Vites"""
        # Method 1: From JSON
        if self.json_data and 'Vites' in self.json_data:
            return self.json_data['Vites']

        # Method 2: From list
        return self._extract_from_list('Vites')

    def extract_vehicle_condition(self) -> Optional[str]:
        """Extract Araç Durumu"""
        # Method 1: From JSON
        if self.json_data and 'vehicleCondition' in self.json_data:
            return self.json_data['vehicleCondition']

        # Method 2: From list
        value = self._extract_from_list('Araç Durumu')
        if not value:
            value = self._extract_from_list('Durumu')
        return value

    def extract_mileage(self) -> Optional[str]:
        """Extract KM"""
        # Method 1: From JSON
        if self.json_data and 'KM' in self.json_data:
            return self.json_data['KM']

        # Method 2: From list
        return self._extract_from_list('KM')

    def extract_body_type(self) -> Optional[str]:
        """Extract Kasa Tipi"""
        # Method 1: From JSON
        if self.json_data and 'Kasa Tipi' in self.json_data:
            return self.json_data['Kasa Tipi']

        # Method 2: From list
        return self._extract_from_list('Kasa Tipi')

    def extract_engine_power(self) -> Optional[str]:
        """Extract Motor Gücü"""
        # Method 1: From JSON
        if self.json_data and 'Motor Gücü' in self.json_data:
            return self.json_data['Motor Gücü']

        # Method 2: From list
        return self._extract_from_list('Motor Gücü')

    def extract_engine_volume(self) -> Optional[str]:
        """Extract Motor Hacmi"""
        # Method 1: From JSON
        if self.json_data and 'Motor Hacmi' in self.json_data:
            return self.json_data['Motor Hacmi']

        # Method 2: From list
        return self._extract_from_list('Motor Hacmi')

    def extract_drive_type(self) -> Optional[str]:
        """Extract Çekiş"""
        # Method 1: From JSON
        if self.json_data and 'Çekiş' in self.json_data:
            return self.json_data['Çekiş']

        # Method 2: From list
        return self._extract_from_list('Çekiş')

    def extract_color(self) -> Optional[str]:
        """Extract Renk"""
        # Method 1: From JSON
        if self.json_data and 'Renk' in self.json_data:
            return self.json_data['Renk']

        # Method 2: From list
        return self._extract_from_list('Renk')

    def extract_warranty(self) -> Optional[str]:
        """Extract Garanti"""
        # Method 1: From JSON
        if self.json_data and 'Garanti' in self.json_data:
            return self.json_data['Garanti']

        # Method 2: From list
        value = self._extract_from_list('Garanti')
        if not value:
            value = self._extract_from_list('Garantisi')
        return value

    def extract_heavy_damage(self) -> Optional[str]:
        """Extract Ağır Hasar Kayıtlı"""
        # Method 1: From JSON
        if self.json_data and 'Ağır Hasar Kayıtlı' in self.json_data:
            return self.json_data['Ağır Hasar Kayıtlı']

        # Method 2: From list
        value = self._extract_from_list('Ağır Hasar Kayıtlı')
        if not value:
            value = self._extract_from_list('Hasar Kayıtlı')
        return value

    def extract_plate_origin(self) -> Optional[str]:
        """Extract Plaka / Uyruk"""
        # Method 1: From JSON
        if self.json_data and 'Plaka / Uyruk' in self.json_data:
            return self.json_data['Plaka / Uyruk']

        # Method 2: From list
        value = self._extract_from_list('Plaka')
        if not value:
            value = self._extract_from_list('Uyruk')
        if not value:
            value = self._extract_from_list('Plaka / Uyruk')
        return value

    def extract_seller_type(self) -> Optional[str]:
        """Extract Kimden"""
        # Method 1: From JSON
        if self.json_data and 'Kimden' in self.json_data:
            return self.json_data['Kimden']

        # Method 2: From list
        return self._extract_from_list('Kimden')

    def extract_trade(self) -> Optional[str]:
        """Extract Takas"""
        # Method 1: From JSON
        if self.json_data and 'Takas' in self.json_data:
            return self.json_data['Takas']

        # Method 2: From list
        value = self._extract_from_list('Takas')
        if not value:
            value = self._extract_from_list('Takasa Uygun')
        return value

    def extract_price(self) -> Optional[str]:
        """Extract price"""
        try:
            # Method 1: From JSON
            if self.json_data and 'ilan_fiyat' in self.json_data:
                return self.json_data['ilan_fiyat'].strip()

            # Method 2: From list
            value = self._extract_from_list('Fiyat')
            if value:
                return value

            # Method 3: Look for price in specific div/h3
            price_elements = self.soup.find_all(['h3', 'div'])
            for elem in price_elements:
                text = elem.get_text(strip=True)
                if 'TL' in text and any(c.isdigit() for c in text):
                    # Make sure it's not too long (to avoid getting descriptions)
                    if len(text) < 50:
                        return text

            return None
        except Exception as e:
            logger.debug(f"Could not extract price: {str(e)}")
            return None

    def extract_title(self) -> Optional[str]:
        """Extract listing title"""
        try:
            # Method 1: Page title
            title_tag = self.soup.find('title')
            if title_tag:
                title = title_tag.get_text()
                # Clean up
                title = title.replace(' sahibinden.com\'da', '')
                title = title.replace(' sahibinden.comda', '')
                title = re.sub(r'\s*-\s*\d+\s*$', '', title)
                return title.strip()

            # Method 2: H1 tag
            h1 = self.soup.find('h1')
            if h1:
                return h1.get_text(strip=True)

            return None
        except Exception as e:
            logger.debug(f"Could not extract title: {str(e)}")
            return None

    def extract_description(self) -> Optional[str]:
        """Extract listing description"""
        try:
            # Look for description div
            desc_div = self.soup.find('div', {'id': 'classifiedDescription'})
            if desc_div:
                return desc_div.get_text(strip=True)

            # Alternative class names
            desc = self.soup.find('div', class_='description')
            if desc:
                return desc.get_text(strip=True)

            return None
        except Exception as e:
            logger.debug(f"Could not extract description: {str(e)}")
            return None

    def extract_images(self) -> list:
        """Extract all image URLs"""
        try:
            images = []

            # Method 1: Look in image gallery
            gallery = self.soup.find('ul', class_='thumbnails')
            if gallery:
                imgs = gallery.find_all('img')
                for img in imgs:
                    src = img.get('src') or img.get('data-src')
                    if src and 'http' in src and 'sahibinden' in src:
                        # Convert thumbnail to full size
                        src = src.replace('/thmb/', '/orginal/')
                        if src not in images:
                            images.append(src)

            # Method 2: Look for carousel images
            carousel = self.soup.find('div', class_=lambda x: x and 'carousel' in x.lower() if x else False)
            if carousel:
                imgs = carousel.find_all('img')
                for img in imgs:
                    src = img.get('src') or img.get('data-src')
                    if src and 'http' in src and 'sahibinden' in src and 'logo' not in src.lower():
                        src = src.replace('/thmb/', '/orginal/')
                        if src not in images:
                            images.append(src)

            return images
        except Exception as e:
            logger.debug(f"Could not extract images: {str(e)}")
            return []

    def extract_location(self) -> Optional[str]:
        """Extract location"""
        try:
            # Method 1: From JSON (combine location fields)
            if self.json_data:
                loc_parts = []
                for key in ['loc2', 'loc3', 'loc4']:  # City, District, Neighborhood
                    if key in self.json_data:
                        loc_parts.append(self.json_data[key])
                if loc_parts:
                    return ' / '.join(loc_parts)

            # Method 2: Look in breadcrumb or location element
            breadcrumb = self.soup.find('ul', class_='breadcrumb')
            if breadcrumb:
                items = breadcrumb.find_all('li')
                # Get last few items (likely location)
                if len(items) >= 3:
                    location = ' / '.join([item.get_text(strip=True) for item in items[-3:]])
                    return location

            return None
        except Exception as e:
            logger.debug(f"Could not extract location: {str(e)}")
            return None

    def extract_phone(self) -> Optional[str]:
        """Extract phone number (if available)"""
        try:
            # Phone might be hidden initially or require interaction
            phone_elem = self.soup.find('span', {'id': 'phoneNumber'})
            if phone_elem:
                return phone_elem.get_text(strip=True)

            # Look for phone pattern in any element
            phone_pattern = re.compile(r'\d{3}\s*\d{3}\s*\d{2}\s*\d{2}')
            phone_match = self.soup.find(string=phone_pattern)
            if phone_match:
                return phone_match.strip()

            return None
        except Exception as e:
            logger.debug(f"Could not extract phone: {str(e)}")
            return None

    def extract_features(self) -> Dict[str, list]:
        """
        Extract Özellikler sections:
        - Güvenlik (Safety)
        - İç Donanım (Interior Equipment)
        - Dış Donanım (Exterior Equipment)
        - Multimedya (Multimedia)
        """
        try:
            features = {}

            # Find all detail-group sections
            detail_groups = self.soup.find_all('ul', class_='detail-group')

            for group in detail_groups:
                # Find the h3 title
                h3 = group.find('h3')
                if not h3:
                    continue

                title = h3.get_text(strip=True)

                # Find the li containing the items
                li = group.find('li')
                if not li:
                    continue

                # Get the text content (excluding the h3)
                h3_copy = li.find('h3')
                if h3_copy:
                    h3_copy.extract()  # Remove h3 temporarily to get only items

                content = li.get_text(strip=True)

                # Split by comma to get individual items
                if ',' in content:
                    items = [item.strip() for item in content.split(',') if item.strip()]
                    features[title] = items
                elif content:
                    # Single item
                    features[title] = [content]

            logger.debug(f"Extracted {len(features)} feature sections")
            return features

        except Exception as e:
            logger.debug(f"Could not extract features: {str(e)}")
            return {}

    def extract_painted_parts(self) -> Optional[Dict[str, Any]]:
        """
        Extract Boyalı veya Değişen Parça (Painted or Changed Parts) section
        This can include text description and possibly images/visual representation
        """
        try:
            painted_section = {}

            # Find the selected-damage li
            damage_li = self.soup.find('li', class_='selected-damage')
            if damage_li:
                # Get text description
                text = damage_li.get_text(strip=True)
                if text:
                    painted_section['aciklama'] = text

                # Look for images (visual representation of damaged/painted parts)
                images = []
                imgs = damage_li.find_all('img')
                for img in imgs:
                    src = img.get('src') or img.get('data-src')
                    if src and 'http' in src:
                        images.append(src)

                if images:
                    painted_section['gorseller'] = images

                # Look for canvas/svg (might be car diagram)
                canvas = damage_li.find('canvas')
                svg = damage_li.find('svg')
                if canvas or svg:
                    painted_section['has_visual_diagram'] = True

                return painted_section if painted_section else None

            return None

        except Exception as e:
            logger.debug(f"Could not extract painted parts: {str(e)}")
            return None

    def extract_technical_specs(self) -> Dict[str, str]:
        """
        Extract Teknik Özellikler (Technical Specifications)
        These are in table.spec-container elements with values in adjacent <span>
        """
        try:
            specs = {}

            # Find all spec-container tables
            spec_tables = self.soup.find_all('table', class_='spec-container')

            for table in spec_tables:
                # Get the label from the table
                label_td = table.find('td')
                if not label_td:
                    continue

                label = label_td.get_text(strip=True)

                # Check if this is a multi-line label
                sub_title_td = table.find('td', class_='sub-title')
                if sub_title_td:
                    # Combine main label and sub-title
                    sub_label = sub_title_td.get_text(strip=True)
                    label = f"{label} {sub_label}".strip()

                # Get the value from the next sibling span
                next_span = table.find_next_sibling('span')
                if next_span:
                    value = next_span.get_text(strip=True)
                    if value:
                        specs[label] = value

            logger.debug(f"Extracted {len(specs)} technical specifications")
            return specs

        except Exception as e:
            logger.debug(f"Could not extract technical specs: {str(e)}")
            return {}


def parse_sahibinden_listing(html: str, url: str) -> Dict[str, Any]:
    """
    Parse a sahibinden.com car listing page

    Args:
        html: The HTML content
        url: The listing URL

    Returns:
        Dict with all extracted fields
    """
    parser = SahibindenCarParser(html, url)
    return parser.parse()
