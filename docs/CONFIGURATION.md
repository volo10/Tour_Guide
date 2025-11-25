# Configuration Guide

Tour Guide uses a centralized configuration file for managing API keys and system settings.

## Quick Start

### Option 1: Edit config.py (Recommended)

Open `tour_guide/config.py` and set your API keys:

```python
# Google Maps API Key (Required)
GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"

# YouTube API Key (Optional - for real video search)
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"

# Spotify API Key (Optional - for real music search)
SPOTIFY_API_KEY = "YOUR_SPOTIFY_API_KEY"
```

That's it! Now you can use the API without passing keys:

```python
from tour_guide import TourGuideAPI

# API key automatically loaded from config.py
api = TourGuideAPI()
result = api.get_tour("Tel Aviv", "Jerusalem")
```

### Option 2: Environment Variables

Set environment variables (overrides config.py):

```bash
export GOOGLE_MAPS_API_KEY="your_key_here"
export YOUTUBE_API_KEY="your_key_here"
export SPOTIFY_API_KEY="your_key_here"
```

### Option 3: Pass Directly (Highest Priority)

```python
api = TourGuideAPI(google_maps_api_key="your_key_here")
```

## API Keys Priority

The system checks for API keys in this order:

1. **Directly passed parameter** (highest priority)
2. **Environment variable**
3. **config.py default value** (lowest priority)

Example:

```python
from tour_guide import TourGuideAPI

# Uses key from parameter (overrides everything)
api = TourGuideAPI(google_maps_api_key="key_from_param")

# Uses key from environment variable or config.py
api = TourGuideAPI()
```

## Getting API Keys

### Google Maps API Key (Required)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Directions API**
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the key to `config.py`

### YouTube API Key (Optional)

Currently not implemented - system uses simulated results.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **YouTube Data API v3**
3. Create API key
4. Copy to `config.py`

### Spotify API Key (Optional)

Currently not implemented - system uses simulated results.

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create an app
3. Copy Client ID and Client Secret
4. Copy to `config.py`

## Configuration Options

All configuration is in `tour_guide/config.py`:

### API Keys

```python
GOOGLE_MAPS_API_KEY = "your_key"
YOUTUBE_API_KEY = None
SPOTIFY_API_KEY = None
```

### System Settings

```python
# Default junction processing interval (seconds)
DEFAULT_JUNCTION_INTERVAL = 5.0

# Agent timeout (seconds)
AGENT_TIMEOUT_SECONDS = 30.0

# Maximum concurrent junctions to process
MAX_CONCURRENT_JUNCTIONS = 3
```

### Logging Settings

```python
# Default log level
DEFAULT_LOG_LEVEL = "INFO"

# Default log file for debug mode
DEFAULT_DEBUG_LOG_FILE = "tour_guide_debug.log"
```

## Helper Functions

Access configuration programmatically:

```python
from tour_guide import config

# Get API keys
google_key = config.get_google_maps_api_key()
youtube_key = config.get_youtube_api_key()
spotify_key = config.get_spotify_api_key()

# Access settings
interval = config.DEFAULT_JUNCTION_INTERVAL
timeout = config.AGENT_TIMEOUT_SECONDS
```

## Security Best Practices

### For Development

Edit `config.py` directly:

```python
GOOGLE_MAPS_API_KEY = "AIzaSyAgu_T79gjEJ2tVf5VLBSj7RjXByTDO7fo"
```

### For Production

Use environment variables:

```bash
# .env file (add to .gitignore!)
GOOGLE_MAPS_API_KEY=your_production_key
YOUTUBE_API_KEY=your_youtube_key
SPOTIFY_API_KEY=your_spotify_key
```

Load with python-dotenv:

```python
from dotenv import load_dotenv
load_dotenv()

from tour_guide import TourGuideAPI
api = TourGuideAPI()  # Automatically uses env vars
```

### Git Security

**IMPORTANT:** If you commit keys to `config.py`, add it to `.gitignore`:

```bash
# .gitignore
tour_guide/config.py
```

Create `config.example.py`:

```python
# tour_guide/config.example.py
GOOGLE_MAPS_API_KEY = "YOUR_KEY_HERE"
YOUTUBE_API_KEY = None
SPOTIFY_API_KEY = None
```

## Examples

### Basic Usage

```python
from tour_guide import TourGuideAPI

# Key loaded from config.py
api = TourGuideAPI()
result = api.get_tour("Start", "End")
```

### Override Config

```python
from tour_guide import TourGuideAPI

# Override with custom key
api = TourGuideAPI(google_maps_api_key="custom_key")
result = api.get_tour("Start", "End")
```

### Check Configuration

```python
from tour_guide import config

print(f"Google Maps Key: {config.GOOGLE_MAPS_API_KEY[:10]}...")
print(f"Junction Interval: {config.DEFAULT_JUNCTION_INTERVAL}s")
print(f"Agent Timeout: {config.AGENT_TIMEOUT_SECONDS}s")
```

### Modify Settings at Runtime

```python
from tour_guide import config, TourGuideAPI

# Change default interval
config.DEFAULT_JUNCTION_INTERVAL = 3.0

# Use custom timeout
api = TourGuideAPI(junction_interval_seconds=config.DEFAULT_JUNCTION_INTERVAL)
```

## Troubleshooting

### Error: "Google Maps API key not provided"

Solution:
1. Check `tour_guide/config.py` has `GOOGLE_MAPS_API_KEY` set
2. Or set environment variable: `export GOOGLE_MAPS_API_KEY="your_key"`
3. Or pass directly: `TourGuideAPI(google_maps_api_key="your_key")`

### Error: "REQUEST_DENIED"

Solution:
1. Enable Directions API in Google Cloud Console
2. Check API key is valid
3. Check billing is enabled for your project

### API key not being used

Check priority order:
1. Parameter > Environment Variable > config.py
2. Verify which one you're setting
3. Print to debug: `print(config.get_google_maps_api_key())`
