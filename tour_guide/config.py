"""
Configuration and API Keys for Tour Guide System.

Store your API keys here for easy access across all modules.
Alternatively, set them as environment variables.
"""

import os

# ============================================================
# API KEYS
# ============================================================

# Google Maps API Key (for route fetching)
# Get from: https://console.cloud.google.com/
# Enable: Directions API
GOOGLE_MAPS_API_KEY = os.environ.get(
    "GOOGLE_MAPS_API_KEY",
    "AIzaSyAgu_T79gjEJ2tVf5VLBSj7RjXByTDO7fo"  # Default key
)

# YouTube API Key (for video agent - optional)
# Get from: https://console.cloud.google.com/
# Enable: YouTube Data API v3
YOUTUBE_API_KEY = os.environ.get(
    "YOUTUBE_API_KEY",
    None  # Set to your key or leave None for simulated results
)

# Spotify API Credentials (for music agent - optional)
# Get from: https://developer.spotify.com/dashboard
# Create an app and get Client ID and Client Secret
SPOTIFY_CLIENT_ID = os.environ.get(
    "SPOTIFY_CLIENT_ID",
    None  # Set to your client ID or leave None for fallback results
)

SPOTIFY_CLIENT_SECRET = os.environ.get(
    "SPOTIFY_CLIENT_SECRET",
    None  # Set to your client secret or leave None for fallback results
)

# ============================================================
# SYSTEM CONFIGURATION
# ============================================================

# Default junction processing interval (seconds)
DEFAULT_JUNCTION_INTERVAL = 5.0

# Agent timeout (seconds)
AGENT_TIMEOUT_SECONDS = 30.0

# Maximum concurrent junctions to process
MAX_CONCURRENT_JUNCTIONS = 3

# ============================================================
# LOGGING CONFIGURATION
# ============================================================

# Default log level
DEFAULT_LOG_LEVEL = "INFO"

# Default log file for debug mode
DEFAULT_DEBUG_LOG_FILE = "tour_guide_debug.log"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_google_maps_api_key() -> str:
    """Get Google Maps API key from config or environment."""
    return GOOGLE_MAPS_API_KEY

def get_youtube_api_key() -> str:
    """Get YouTube API key from config or environment."""
    return YOUTUBE_API_KEY

def get_spotify_client_id() -> str:
    """Get Spotify Client ID from config or environment."""
    return SPOTIFY_CLIENT_ID

def get_spotify_client_secret() -> str:
    """Get Spotify Client Secret from config or environment."""
    return SPOTIFY_CLIENT_SECRET
