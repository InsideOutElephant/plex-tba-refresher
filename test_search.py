def test_search():
    """Utility script to test Plex search directly"""
    import sys
    import yaml
    from plexapi.server import PlexServer
    
    # Load config
    with open('data/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Connect to Plex
    plex = PlexServer(
        config['plex']['url'],
        config['plex']['token']
    )
    
    # Get libraries
    libraries = {lib.title: lib for lib in plex.library.sections()}
    print(f"\nFound libraries: {', '.join(libraries.keys())}")
    
    # Test search in each configured library
    for lib_name in config['plex'].get('libraries', libraries.keys()):
        if lib_name not in libraries:
            print(f"\nLibrary not found: {lib_name}")
            continue
            
        library = libraries[lib_name]
        print(f"\nTesting search in library: {lib_name}")
        print(f"Library type: {library.type}")
        
        for pattern in config['search']['patterns']:
            print(f"\n  Searching for: {pattern}")
            
            # Build and show the search URL
            search_url = f"{config['plex']['url']}/library/sections/{library.key}/search?query={pattern}&type={'4' if library.type == 'show' else '1'}"
            print(f"  Search URL: {search_url}")
            
            # Perform search
            if library.type == 'show':
                results = library.search(title=pattern, libtype='episode')
            else:
                results = library.search(title=pattern, libtype='movie')
            
            if results:
                print(f"    Found {len(results)} matches:")
                for item in results:
                    if library.type == 'movie':
                        print(f"      Movie: {item.title} ({getattr(item, 'year', 'Unknown')})")
                    elif hasattr(item, 'type') and item.type == 'episode':
                        print(f"      Episode: {item.grandparentTitle} - S{item.seasonNumber:02d}E{item.episodeNumber:02d} - {item.title}")
            else:
                print("    No matches found")

if __name__ == '__main__':
    test_search()