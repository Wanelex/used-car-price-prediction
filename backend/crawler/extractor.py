"""
Page Content Extractor
Parses HTML and extracts structured data
"""
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from loguru import logger
import re


class ContentExtractor:
    """Extract and structure content from HTML"""

    def __init__(self, html: str, base_url: str):
        self.html = html
        self.base_url = base_url
        self.soup = BeautifulSoup(html, 'html.parser')

    def extract_all(self) -> Dict[str, Any]:
        """
        Extract all available data from the page

        Returns:
            Dictionary with all extracted data
        """
        return {
            "title": self.extract_title(),
            "text": self.extract_text(),
            "metadata": self.extract_metadata(),
            "images": self.extract_images(),
            "links": self.extract_links(),
            "headings": self.extract_headings(),
            "tables": self.extract_tables(),
            "forms": self.extract_forms(),
            "scripts": self.extract_scripts(),
            "styles": self.extract_styles()
        }

    def extract_title(self) -> Optional[str]:
        """Extract page title"""
        try:
            title_tag = self.soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()

            # Try h1 as fallback
            h1_tag = self.soup.find('h1')
            if h1_tag:
                return h1_tag.get_text().strip()

            return None
        except Exception as e:
            logger.error(f"Failed to extract title: {str(e)}")
            return None

    def extract_text(self, clean: bool = True) -> str:
        """
        Extract all visible text from the page

        Args:
            clean: Whether to clean and normalize text

        Returns:
            Extracted text content
        """
        try:
            # Remove script and style elements
            for script in self.soup(["script", "style", "meta", "noscript"]):
                script.decompose()

            # Get text
            text = self.soup.get_text()

            if clean:
                # Clean up whitespace
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)

            return text

        except Exception as e:
            logger.error(f"Failed to extract text: {str(e)}")
            return ""

    def extract_metadata(self) -> Dict[str, Optional[str]]:
        """Extract metadata from meta tags"""
        try:
            metadata = {
                "description": None,
                "keywords": None,
                "author": None,
                "og_title": None,
                "og_description": None,
                "og_image": None,
                "og_url": None,
                "og_type": None,
                "twitter_card": None,
                "twitter_title": None,
                "twitter_description": None,
                "twitter_image": None,
                "canonical_url": None,
                "language": None,
                "charset": None,
                "robots": None,
                "viewport": None
            }

            # Standard meta tags
            for meta in self.soup.find_all('meta'):
                name = meta.get('name', '').lower()
                property_name = meta.get('property', '').lower()
                content = meta.get('content', '')

                # Standard meta tags
                if name == 'description':
                    metadata['description'] = content
                elif name == 'keywords':
                    metadata['keywords'] = content
                elif name == 'author':
                    metadata['author'] = content
                elif name == 'robots':
                    metadata['robots'] = content
                elif name == 'viewport':
                    metadata['viewport'] = content

                # Open Graph tags
                elif property_name == 'og:title':
                    metadata['og_title'] = content
                elif property_name == 'og:description':
                    metadata['og_description'] = content
                elif property_name == 'og:image':
                    metadata['og_image'] = content
                elif property_name == 'og:url':
                    metadata['og_url'] = content
                elif property_name == 'og:type':
                    metadata['og_type'] = content

                # Twitter Card tags
                elif name == 'twitter:card':
                    metadata['twitter_card'] = content
                elif name == 'twitter:title':
                    metadata['twitter_title'] = content
                elif name == 'twitter:description':
                    metadata['twitter_description'] = content
                elif name == 'twitter:image':
                    metadata['twitter_image'] = content

                # Charset
                if meta.get('charset'):
                    metadata['charset'] = meta.get('charset')

            # Canonical URL
            canonical = self.soup.find('link', rel='canonical')
            if canonical:
                metadata['canonical_url'] = canonical.get('href')

            # Language
            html_tag = self.soup.find('html')
            if html_tag:
                metadata['language'] = html_tag.get('lang')

            return metadata

        except Exception as e:
            logger.error(f"Failed to extract metadata: {str(e)}")
            return {}

    def extract_images(self, absolute_urls: bool = True) -> List[Dict[str, Optional[str]]]:
        """
        Extract all images with their attributes

        Args:
            absolute_urls: Convert relative URLs to absolute

        Returns:
            List of image dictionaries
        """
        try:
            images = []

            for img in self.soup.find_all('img'):
                src = img.get('src', '')
                if not src:
                    continue

                # Convert to absolute URL if needed
                if absolute_urls and not src.startswith(('http://', 'https://', 'data:')):
                    src = urljoin(self.base_url, src)

                image_data = {
                    "src": src,
                    "alt": img.get('alt', ''),
                    "title": img.get('title', ''),
                    "width": img.get('width'),
                    "height": img.get('height'),
                    "srcset": img.get('srcset', ''),
                    "loading": img.get('loading', '')
                }

                images.append(image_data)

            return images

        except Exception as e:
            logger.error(f"Failed to extract images: {str(e)}")
            return []

    def extract_links(self, absolute_urls: bool = True, filter_external: bool = False) -> List[Dict[str, str]]:
        """
        Extract all links with their attributes

        Args:
            absolute_urls: Convert relative URLs to absolute
            filter_external: Only include links from same domain

        Returns:
            List of link dictionaries
        """
        try:
            links = []
            base_domain = urlparse(self.base_url).netloc

            for anchor in self.soup.find_all('a', href=True):
                href = anchor.get('href', '')
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue

                # Convert to absolute URL
                if absolute_urls and not href.startswith(('http://', 'https://')):
                    href = urljoin(self.base_url, href)

                # Filter external links if requested
                if filter_external:
                    link_domain = urlparse(href).netloc
                    if link_domain != base_domain:
                        continue

                link_data = {
                    "href": href,
                    "text": anchor.get_text().strip(),
                    "title": anchor.get('title', ''),
                    "rel": anchor.get('rel', []),
                    "target": anchor.get('target', '')
                }

                links.append(link_data)

            return links

        except Exception as e:
            logger.error(f"Failed to extract links: {str(e)}")
            return []

    def extract_headings(self) -> Dict[str, List[str]]:
        """Extract all headings (h1-h6)"""
        try:
            headings = {
                "h1": [],
                "h2": [],
                "h3": [],
                "h4": [],
                "h5": [],
                "h6": []
            }

            for level in range(1, 7):
                tag = f"h{level}"
                for heading in self.soup.find_all(tag):
                    text = heading.get_text().strip()
                    if text:
                        headings[tag].append(text)

            return headings

        except Exception as e:
            logger.error(f"Failed to extract headings: {str(e)}")
            return {}

    def extract_tables(self) -> List[List[List[str]]]:
        """Extract all tables as nested lists"""
        try:
            tables = []

            for table in self.soup.find_all('table'):
                table_data = []

                for row in table.find_all('tr'):
                    row_data = []
                    for cell in row.find_all(['td', 'th']):
                        row_data.append(cell.get_text().strip())
                    if row_data:
                        table_data.append(row_data)

                if table_data:
                    tables.append(table_data)

            return tables

        except Exception as e:
            logger.error(f"Failed to extract tables: {str(e)}")
            return []

    def extract_forms(self) -> List[Dict[str, Any]]:
        """Extract all forms with their inputs"""
        try:
            forms = []

            for form in self.soup.find_all('form'):
                form_data = {
                    "action": form.get('action', ''),
                    "method": form.get('method', 'get').upper(),
                    "inputs": []
                }

                # Make action URL absolute
                if form_data['action'] and not form_data['action'].startswith(('http://', 'https://')):
                    form_data['action'] = urljoin(self.base_url, form_data['action'])

                # Extract inputs
                for input_tag in form.find_all(['input', 'textarea', 'select']):
                    input_data = {
                        "type": input_tag.get('type', 'text'),
                        "name": input_tag.get('name', ''),
                        "value": input_tag.get('value', ''),
                        "placeholder": input_tag.get('placeholder', ''),
                        "required": input_tag.has_attr('required')
                    }
                    form_data['inputs'].append(input_data)

                forms.append(form_data)

            return forms

        except Exception as e:
            logger.error(f"Failed to extract forms: {str(e)}")
            return []

    def extract_scripts(self) -> List[Dict[str, str]]:
        """Extract all script tags"""
        try:
            scripts = []

            for script in self.soup.find_all('script'):
                script_data = {
                    "src": script.get('src', ''),
                    "type": script.get('type', 'text/javascript'),
                    "inline": bool(script.string)
                }

                # Make src URL absolute
                if script_data['src'] and not script_data['src'].startswith(('http://', 'https://', '//')):
                    script_data['src'] = urljoin(self.base_url, script_data['src'])

                scripts.append(script_data)

            return scripts

        except Exception as e:
            logger.error(f"Failed to extract scripts: {str(e)}")
            return []

    def extract_styles(self) -> List[Dict[str, str]]:
        """Extract all stylesheet links"""
        try:
            styles = []

            for link in self.soup.find_all('link', rel='stylesheet'):
                href = link.get('href', '')

                # Make URL absolute
                if href and not href.startswith(('http://', 'https://', '//')):
                    href = urljoin(self.base_url, href)

                style_data = {
                    "href": href,
                    "media": link.get('media', 'all')
                }

                styles.append(style_data)

            return styles

        except Exception as e:
            logger.error(f"Failed to extract styles: {str(e)}")
            return []

    def extract_emails(self) -> List[str]:
        """Extract email addresses from text"""
        try:
            text = self.extract_text()
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            return list(set(emails))  # Remove duplicates
        except Exception as e:
            logger.error(f"Failed to extract emails: {str(e)}")
            return []

    def extract_phone_numbers(self) -> List[str]:
        """Extract phone numbers from text"""
        try:
            text = self.extract_text()
            # Simple phone number pattern (can be enhanced)
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = re.findall(phone_pattern, text)
            return list(set(phones))  # Remove duplicates
        except Exception as e:
            logger.error(f"Failed to extract phone numbers: {str(e)}")
            return []
