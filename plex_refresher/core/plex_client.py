# plex_refresher/core/plex_client.py
import logging
import time
from typing import Optional
from plexapi.server import PlexServer

class PlexClient:
    def __init__(self, url: str, token: str, logger: logging.Logger):
        self.url = url
        self.token = token
        self.logger = logger

    def verify_connection(self, plex: PlexServer) -> bool:
        try:
            server_info = {
                'friendly_name': plex.friendlyName,
                'version': plex.version,
                'platform': plex.platform
            }
            self.logger.info(f"Connected to Plex server: {server_info['friendly_name']} "
                          f"(Version: {server_info['version']}, Platform: {server_info['platform']})")
            
            libraries = plex.library.sections()
            self.logger.info(f"Found {len(libraries)} libraries: {', '.join(lib.title for lib in libraries)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to verify Plex connection: {str(e)}")
            return False

    def connect(self) -> Optional[PlexServer]:
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                plex = PlexServer(self.url, self.token)
                
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

