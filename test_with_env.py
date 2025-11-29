#!/usr/bin/env python3
"""
Test script that loads API keys from raf.env and validates them.

Usage:
    python test_with_env.py
"""

from dotenv import load_dotenv
import os

# Load environment variables from raf.env
load_dotenv("raf.env")

print("=" * 50)
print("API Keys Validation")
print("=" * 50)

# Check each key
keys = {
    "GOOGLE_MAPS_API_KEY": os.environ.get("GOOGLE_MAPS_API_KEY", ""),
    "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY", ""),
    "SPOTIFY_CLIENT_ID": os.environ.get("SPOTIFY_CLIENT_ID", ""),
    "SPOTIFY_CLIENT_SECRET": os.environ.get("SPOTIFY_CLIENT_SECRET", ""),
}

all_valid = True
for name, value in keys.items():
    if value:
        # Show first 8 chars only for security
        masked = value[:8] + "..." if len(value) > 8 else value
        print(f"  {name}: {masked}")
    else:
        print(f"  {name}: MISSING")
        all_valid = False

print("=" * 50)

if all_valid:
    print("All API keys are configured!")
    print("\nRunning Tour Guide validation...")
    print("=" * 50)

    # Now test with Tour Guide
    from tour_guide.config import validate_api_keys
    result = validate_api_keys()

    if result['valid']:
        print("Tour Guide validation: PASSED")

        # Try a quick test
        print("\nWould you like to run a quick test? (This will make API calls)")
        print("Run: python -c \"from dotenv import load_dotenv; load_dotenv('raf.env'); from tour_guide import TourGuideAPI; api = TourGuideAPI(); result = api.get_tour('Tel Aviv', 'Jaffa', verbose=True); result.print_winners()\"")
    else:
        print(f"Tour Guide validation: FAILED")
        print(f"Missing keys: {result['missing']}")
else:
    print("Some API keys are missing!")
