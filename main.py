#!/usr/bin/env python3
import sys
import logging
from plex_refresher.core.refresher import PlexMetadataRefresher
from plex_refresher.exceptions.config_errors import ConfigurationError

def main():
    try:
        # Add basic logging until our full logging is set up
        logging.basicConfig(level=logging.INFO)
        logging.info("Starting Plex Metadata Refresher")
        
        refresher = PlexMetadataRefresher()
        refresher.run()  # Changed from run_forever to run
        
    except ConfigurationError as e:
        print(f"Configuration Error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nReceived shutdown signal. Exiting gracefully.", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()