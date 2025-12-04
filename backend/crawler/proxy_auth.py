"""
Proxy Authentication Extension Manager for Chrome
Handles proxy authentication by creating and loading a Chrome extension
"""
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Dict
from loguru import logger


class ProxyAuthExtension:
    """
    Creates and manages Chrome extension for proxy authentication
    """

    def __init__(self):
        self.extension_dir = None
        self.temp_dir = None

    def parse_proxy_url(self, proxy_url: str) -> Optional[Dict[str, str]]:
        """
        Parse proxy URL to extract credentials and server info

        Args:
            proxy_url: Proxy URL (e.g., http://user:pass@host:port/)

        Returns:
            Dict with user, password, host, port, or None if invalid
        """
        try:
            # Handle URLs with and without authentication
            # Format: http://user:pass@host:port or http://host:port

            # Remove trailing slash
            proxy_url = proxy_url.rstrip('/')

            # Parse URL
            if '@' in proxy_url:
                # Has authentication
                # Split into protocol://user:pass and host:port
                protocol_and_auth = proxy_url.split('@')[0]
                host_and_port = proxy_url.split('@')[1]

                # Extract protocol
                protocol = protocol_and_auth.split('://')[0]

                # Extract user:pass
                auth_part = protocol_and_auth.split('://')[1]
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    logger.error("Invalid proxy format: missing password")
                    return None

                # Extract host:port
                if ':' in host_and_port:
                    host, port = host_and_port.rsplit(':', 1)
                else:
                    logger.error("Invalid proxy format: missing port")
                    return None

                return {
                    'protocol': protocol,
                    'username': username,
                    'password': password,
                    'host': host,
                    'port': port
                }
            else:
                # No authentication
                parsed = urlparse(proxy_url)
                return {
                    'protocol': parsed.scheme or 'http',
                    'username': '',
                    'password': '',
                    'host': parsed.hostname,
                    'port': str(parsed.port) if parsed.port else '80'
                }

        except Exception as e:
            logger.error(f"Failed to parse proxy URL: {str(e)}")
            return None

    def create_extension(self, proxy_url: str) -> Optional[str]:
        """
        Create a Chrome extension for proxy authentication

        Args:
            proxy_url: Proxy URL with authentication

        Returns:
            Path to extension directory, or None if failed
        """
        try:
            # Parse proxy URL
            proxy_info = self.parse_proxy_url(proxy_url)
            if not proxy_info:
                logger.error("Failed to parse proxy URL")
                return None

            logger.info(f"Creating proxy auth extension for {proxy_info['host']}:{proxy_info['port']}")

            # Create temporary directory for extension
            self.temp_dir = tempfile.mkdtemp(prefix="proxy_auth_ext_")
            self.extension_dir = self.temp_dir

            # Get the template extension directory
            template_dir = Path(__file__).parent / "proxy_auth_extension"

            if not template_dir.exists():
                logger.error(f"Template extension directory not found: {template_dir}")
                return None

            # Read manifest.json template
            manifest_template = template_dir / "manifest.json"
            with open(manifest_template, 'r') as f:
                manifest_content = f.read()

            # Read background.js template
            background_template = template_dir / "background.js"
            with open(background_template, 'r') as f:
                background_content = f.read()

            # Replace placeholders with actual values
            background_content = background_content.replace('PROXY_HOST', proxy_info['host'])
            background_content = background_content.replace('PROXY_PORT', proxy_info['port'])
            background_content = background_content.replace('PROXY_USER', proxy_info['username'])
            background_content = background_content.replace('PROXY_PASS', proxy_info['password'])

            # Write modified files to temp directory
            with open(os.path.join(self.extension_dir, 'manifest.json'), 'w') as f:
                f.write(manifest_content)

            with open(os.path.join(self.extension_dir, 'background.js'), 'w') as f:
                f.write(background_content)

            logger.success(f"Proxy auth extension created at: {self.extension_dir}")
            return self.extension_dir

        except Exception as e:
            logger.error(f"Failed to create proxy auth extension: {str(e)}")
            return None

    def cleanup(self):
        """Clean up temporary extension directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.debug(f"Cleaned up extension directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Failed to cleanup extension directory: {str(e)}")

    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()


# Helper function
def create_proxy_extension(proxy_url: str) -> Optional[str]:
    """
    Create a proxy authentication extension

    Args:
        proxy_url: Proxy URL with authentication

    Returns:
        Path to extension directory
    """
    manager = ProxyAuthExtension()
    return manager.create_extension(proxy_url)


logger.info("Proxy authentication module loaded")
