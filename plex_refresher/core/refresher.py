import sys
import time
import logging
from typing import Dict, List
from plex_refresher.utils.config_loader import ConfigLoader
from plex_refresher.utils.logging_setup import LoggingSetup
from plex_refresher.core.plex_client import PlexClient
from plex_refresher.models.tba_item import TBAItem

class PlexMetadataRefresher:
    def __init__(self):
        self.config = ConfigLoader.load_and_validate()
        self.logger = LoggingSetup.setup_logging(self.config)
        self.dry_run = self.config['refresh'].get('dry_run', True)
        self.plex_client = PlexClient(
            self.config['plex']['url'],
            self.config['plex']['token'],
            self.logger
        )
        
        if self.dry_run:
            self.logger.info("=== DRY RUN MODE - NO CHANGES WILL BE MADE ===")

    def get_tba_items(self, library) -> List[TBAItem]:
        search_method = self.config['search']['method']
        if search_method == 'quick':
            return self._quick_search(library)
        else:
            return self._deep_search(library)

    def _quick_search(self, library) -> List[TBAItem]:
        """Perform a quick search using Plex's search API"""
        tba_items = []
        patterns = self.config['search']['patterns']
        case_sensitive = self.config['search'].get('case_sensitive', False)
        
        try:
            self.logger.info(f"Quick searching library: {library.title}")
            
            for pattern in patterns:
                self.logger.info(f"  Searching for pattern: '{pattern}'")
                
                # Use Plex's search API directly
                items = library.search(title=pattern)
                if items:
                    self.logger.info(f"    Found {len(items)} items matching '{pattern}'")
                    
                    for item in items:
                        if library.type == 'movie':
                            self.logger.info(f"      Found movie: {item.title} ({getattr(item, 'year', 'Unknown')})")
                            tba_items.append(TBAItem.from_movie(item))
                        elif library.type == 'show' and hasattr(item, 'type') and item.type == 'episode':
                            self.logger.info(f"      Found episode: {item.grandparentTitle} - S{item.seasonNumber:02d}E{item.episodeNumber:02d} - {item.title}")
                            tba_items.append(TBAItem.from_episode(item, item.show()))
                else:
                    self.logger.info(f"    No items found matching '{pattern}'")
                    
        except Exception as e:
            self.logger.error(f"Error quick searching items in library {library.title}: {str(e)}")
        
        return tba_items

    def _deep_search(self, library) -> List[TBAItem]:
        """Perform a deep search by scanning all items"""
        tba_items = []
        patterns = self.config['search']['patterns']
        case_sensitive = self.config['search'].get('case_sensitive', False)
        include_full_title = self.config['search'].get('include_full_title', False)
        episode_limit = self.config['search'].get('episode_scan_limit')
        
        try:
            if library.type == 'movie':
                self.logger.info(f"Deep scanning movie library: {library.title}")
                movies = library.all()
                total_movies = len(movies)
                self.logger.info(f"  Scanning {total_movies} movies")
                
                for idx, movie in enumerate(movies, 1):
                    title = movie.title if case_sensitive else movie.title.upper()
                    patterns_to_check = patterns if case_sensitive else [p.upper() for p in patterns]
                    
                    if any(pattern in title for pattern in patterns_to_check):
                        self.logger.info(f"    Found matching movie ({idx}/{total_movies}): {movie.title} ({getattr(movie, 'year', 'Unknown')})")
                        tba_items.append(TBAItem.from_movie(movie))
                    
                    if idx % 100 == 0:
                        self.logger.info(f"    Processed {idx}/{total_movies} movies...")
                
            elif library.type == 'show':
                shows = library.all()
                total_shows = len(shows)
                self.logger.info(f"Deep scanning TV library: {library.title} ({total_shows} shows)")
                
                for show_idx, show in enumerate(shows, 1):
                    self.logger.info(f"  Scanning show {show_idx}/{total_shows}: {show.title}")
                    episodes = show.episodes()
                    
                    if episode_limit:
                        episodes = episodes[:episode_limit]
                        self.logger.info(f"    Limited to {episode_limit} episodes per show")
                    
                    for episode in episodes:
                        # Check episode title
                        title = episode.title if case_sensitive else episode.title.upper()
                        patterns_to_check = patterns if case_sensitive else [p.upper() for p in patterns]
                        
                        # If configured, also check full title (Show Name - Episode Title)
                        if include_full_title:
                            full_title = f"{show.title} - {episode.title}"
                            title = full_title if case_sensitive else full_title.upper()
                        
                        if any(pattern in title for pattern in patterns_to_check):
                            self.logger.info(f"    Found matching episode: S{episode.seasonNumber:02d}E{episode.episodeNumber:02d} - {episode.title}")
                            tba_items.append(TBAItem.from_episode(episode, show))
                            
        except Exception as e:
            self.logger.error(f"Error deep scanning items in library {library.title}: {str(e)}")
        
        return tba_items

    def print_dry_run_summary(self, all_items: Dict[str, List[TBAItem]]):
        self.logger.info("\n=== DRY RUN SUMMARY ===")
        total_items = sum(len(items) for items in all_items.values())
        
        patterns = self.config['search']['patterns']
        self.logger.info(f"\nSearching for: {', '.join(patterns)}")
        self.logger.info(f"Case sensitive: {self.config['search'].get('case_sensitive', False)}")
        self.logger.info(f"\nTotal matching items found: {total_items}")
        
        for library_name, items in all_items.items():
            if not items:
                continue
                
            self.logger.info(f"\nLibrary: {library_name} ({len(items)} items)")
            
            # Group by type
            movies = [item for item in items if item.type == 'movie']
            episodes = [item for item in items if item.type == 'episode']
            
            if movies:
                self.logger.info("\nMovies:")
                for movie in movies:
                    self.logger.info(f"- {movie}")
                    
            if episodes:
                self.logger.info("\nTV Episodes:")
                for episode in episodes:
                    self.logger.info(f"- {episode}")

        if total_items == 0:
            self.logger.info("\nNo matching items found in any library")

        self.logger.info("\nTo perform the actual refresh, set dry_run: false in config.yaml")
        self.logger.info("=== END DRY RUN SUMMARY ===\n")

    def refresh_metadata(self):
        self.logger.info("\nStarting metadata refresh scan...")
        self.logger.info(f"Search method: {self.config['search']['method']}")
        plex = self.plex_client.connect()
        if not plex:
            return

        try:
            if 'libraries' not in self.config['plex']:
                libraries = plex.library.sections()
                self.logger.info("No specific libraries configured - processing all libraries")
            else:
                libraries = [plex.library.section(name) for name in self.config['plex']['libraries']]
                self.logger.info(f"Processing configured libraries: {', '.join(self.config['plex']['libraries'])}")

            # Filter for movie and TV show libraries
            valid_libraries = [lib for lib in libraries if lib.type in ('movie', 'show')]
            total_libraries = len(valid_libraries)
            
            self.logger.info(f"\nFound {total_libraries} valid libraries to scan")
            self.logger.info(f"Search patterns: {', '.join(self.config['search']['patterns'])}")
            self.logger.info(f"Case sensitive: {self.config['search'].get('case_sensitive', False)}\n")

            all_items = {}
            
            for index, library in enumerate(valid_libraries, 1):
                self.logger.info(f"\nProcessing library {index}/{total_libraries}: {library.title}")
                self.logger.info(f"Library type: {library.type}")
                
                tba_items = self.get_tba_items(library)
                all_items[library.title] = tba_items
                
                if not self.dry_run and tba_items:
                    self.logger.info(f"\nRefreshing metadata for {len(tba_items)} items in {library.title}")
                    for item_index, item in enumerate(tba_items, 1):
                        try:
                            self.logger.info(f"  Refreshing {item_index}/{len(tba_items)}: {item}")
                            item.item.refresh()
                            self.logger.info(f"  Refresh complete, waiting {self.config['refresh']['delay_between_items']} seconds...")
                            time.sleep(self.config['refresh']['delay_between_items'])
                        except Exception as e:
                            self.logger.error(f"  Failed to refresh {item}: {str(e)}")
                
                self.logger.info(f"Completed scanning library: {library.title}\n")
            
            if self.dry_run:
                self.print_dry_run_summary(all_items)

        except Exception as e:
            self.logger.error(f"Error during refresh: {str(e)}")

    def run(self):
        """Run the refresh process either once (dry run) or continuously (wet run)."""
        try:
            if self.dry_run:
                self.logger.info("Starting Plex metadata refresh service (DRY RUN - will run only once)")
                self.refresh_metadata()
                self.logger.info("Dry run completed. Exiting.")
                sys.exit(0)  # Exit cleanly after dry run
            else:
                self.logger.info("Starting Plex metadata refresh service (continuous mode)")
                while True:
                    self.refresh_metadata()
                    interval = self.config['refresh']['interval_seconds']
                    self.logger.info(f"Refresh cycle completed. Sleeping for {interval} seconds until next refresh")
                    time.sleep(interval)
                    self.logger.info("Wake up - starting next refresh cycle")
                    
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal. Exiting gracefully.")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Unexpected error in run: {str(e)}")
            if not self.dry_run:
                self.logger.info("Waiting 60 seconds before retrying...")
                time.sleep(60)
            else:
                self.logger.info("Exiting due to error in dry run mode.")
                sys.exit(1)