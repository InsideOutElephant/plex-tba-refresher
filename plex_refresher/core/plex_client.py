import logging
import time
from typing import Optional
from plexapi.server import PlexServer
import requests

class PlexClient:
    def __init__(self, url: str, token: str, logger: logging.Logger):
        self.url = url.rstrip('/')  # Remove trailing slash if present
        self.token = str(token).strip()  # Ensure token is string and stripped
        self.logger = logger
        
        # Log token format for debugging
        self.logger.debug(f"Token length: {len(self.token)}")
        self.logger.debug(f"Token preview: {self.token[:4]}...{self.token[-4:] if len(self.token) >= 8 else ''}")
        self.logger.debug(f"Token contains whitespace: {' ' in self.token}")
        self.logger.debug(f"Token is alphanumeric: {self.token.isalnum()}")

    def connect(self) -> Optional[PlexServer]:
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Attempting to connect to Plex server (attempt {attempt + 1}/{max_retries})")
                
                # Create session with explicit headers
                session = requests.Session()
                session.headers.update({
                    'X-Plex-Token': self.token,
                    'Accept': 'application/xml',
                    'X-Plex-Client-Identifier': 'plex-tba-refresher',
                    'X-Plex-Product': 'Plex TBA Refresher',
                    'X-Plex-Version': '1.0'
                })

                # Now create the PlexServer instance
                plex = PlexServer(
                    baseurl=self.url,
                    token=self.token,
                    session=session
                )
                
                if self.verify_connection(plex):
                    return plex
                    
            except Exception as e:
                self.logger.error(f"Connection attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    self.logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                
        self.logger.error("Failed to establish Plex connection after all retries")
        return None

    def verify_connection(self, plex: PlexServer) -> bool:
        try:
            server_info = {
                'friendly_name': plex.friendlyName,
                'version': plex.version,
                'platform': plex.platform
            }
            self.logger.info(f"Connected to Plex server: {server_info['friendly_name']} "
                          f"(Version: {server_info['version']}, Platform: {server_info['platform']}")
            
            libraries = plex.library.sections()
            self.logger.info(f"Found {len(libraries)} libraries: {', '.join(lib.title for lib in libraries)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify Plex connection: {str(e)}")
            return False