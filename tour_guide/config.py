"""
Configuration and API Keys for Tour Guide System.

API keys must be set as environment variables for security.
Do NOT hardcode API keys in source code.

Required environment variables:
    - GOOGLE_MAPS_API_KEY: Google Maps Directions API key
    - YOUTUBE_API_KEY: YouTube Data API v3 key
    - SPOTIFY_CLIENT_ID: Spotify API client ID
    - SPOTIFY_CLIENT_SECRET: Spotify API client secret
"""

import os
import logging

logger = logging.getLogger(__name__)

# ============================================================
# API KEYS (loaded from environment variables only)
# ============================================================

# Google Maps API Key (for route fetching)
# Get from: https://console.cloud.google.com/
# Enable: Directions API
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

# YouTube API Key (for video agent)
# Get from: https://console.cloud.google.com/
# Enable: YouTube Data API v3
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# Spotify API Credentials (for music agent)
# Get from: https://developer.spotify.com/dashboard
# Create an app and get Client ID and Client Secret
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID", "")

SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET", "")

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
    """Get Google Maps API key from environment variable."""
    key = GOOGLE_MAPS_API_KEY
    if not key:
        logger.warning("GOOGLE_MAPS_API_KEY environment variable not set")
    return key

def get_youtube_api_key() -> str:
    """Get YouTube API key from environment variable."""
    key = YOUTUBE_API_KEY
    if not key:
        logger.warning("YOUTUBE_API_KEY environment variable not set")
    return key

def get_spotify_client_id() -> str:
    """Get Spotify Client ID from environment variable."""
    key = SPOTIFY_CLIENT_ID
    if not key:
        logger.warning("SPOTIFY_CLIENT_ID environment variable not set")
    return key

def get_spotify_client_secret() -> str:
    """Get Spotify Client Secret from environment variable."""
    key = SPOTIFY_CLIENT_SECRET
    if not key:
        logger.warning("SPOTIFY_CLIENT_SECRET environment variable not set")
    return key


def validate_api_keys() -> dict:
    """
    Validate that all required API keys are configured.

    Returns:
        dict with 'valid' (bool) and 'missing' (list of missing key names)
    """
    missing = []
    if not GOOGLE_MAPS_API_KEY:
        missing.append("GOOGLE_MAPS_API_KEY")
    if not YOUTUBE_API_KEY:
        missing.append("YOUTUBE_API_KEY")
    if not SPOTIFY_CLIENT_ID:
        missing.append("SPOTIFY_CLIENT_ID")
    if not SPOTIFY_CLIENT_SECRET:
        missing.append("SPOTIFY_CLIENT_SECRET")

    return {
        "valid": len(missing) == 0,
        "missing": missing
    }
