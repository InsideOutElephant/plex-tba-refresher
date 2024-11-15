# Plex TBA Metadata Refresher

A Docker-based tool to automatically refresh metadata for Plex media items with TBA (To Be Announced) or TBD (To Be Determined) in their titles.

## Features

- Automatic scanning of Plex libraries for TBA/TBD content
- Multiple search methods (quick API-based search or deep scanning)
- Configurable search patterns
- Dry run mode for testing
- Detailed logging
- Docker-based deployment

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/plex-tba-refresher.git
cd plex-tba-refresher
```

2. Copy the example config file:
```bash
cp data/config.yaml.example data/config.yaml
```

3. Edit the config file with your Plex details:
```yaml
plex:
  url: "http://localhost:32400"  # Your Plex server URL
  token: "your-plex-token"       # Your Plex token
  libraries:                     # Libraries to scan
    - "Movies"
    - "TV Shows"
```

4. Build and run with Docker Compose:
```bash
docker-compose up -d
```

## Configuration

### Search Methods

The tool supports two search methods:

1. Quick Search (`method: "quick"`):
   - Uses Plex's search API
   - Faster but might miss some items
   - Best for regular checking

2. Deep Search (`method: "deep"`):
   - Scans all items in selected libraries
   - More thorough but slower
   - Best for initial setup or periodic deep scans

Example configuration:
```yaml
search:
  method: "quick"              # 'quick' or 'deep'
  patterns:
    - "TBA"
    - "TBD"
    - "To Be Announced"
  case_sensitive: false
  include_full_title: false    # Search in show name + episode title (deep search only)
  episode_scan_limit: null     # Limit episodes per show, null for no limit (deep search only)
```

### Schedule Configuration

```yaml
refresh:
  interval_seconds: 3600       # Run every hour
  delay_between_items: 2       # Wait 2 seconds between refreshing items
  dry_run: true               # Set to false to perform actual refresh
```

## Getting Your Plex Token

You can get your Plex token using one of these methods:

1. From Plex Web App:
   - Log into app.plex.tv/desktop
   - Open any media item
   - Click the three dots menu (...)
   - Click "Get Info" or "View XML"
   - Find X-Plex-Token in the URL

2. From Browser Developer Tools:
   - Open app.plex.tv/desktop
   - Press F12 for Developer Tools
   - Go to Network tab
   - Find any request to plex.tv
   - Look for X-Plex-Token in request headers

## Logging

Logs are written to `data/logs/plex_refresh.log` by default. Configure logging in the config file:

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: "/app/data/logs/plex_refresh.log"
  max_size_mb: 10
  backup_count: 3
```

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](LICENSE)