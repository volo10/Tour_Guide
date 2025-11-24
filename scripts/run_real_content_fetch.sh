#!/bin/bash

# Tour Guide Real Content Fetcher - Setup & Run Script
# This script helps you set up API keys and run the content fetcher

echo "========================================"
echo "🚗 Tour Guide Real Content Fetcher"
echo "========================================"
echo ""

# Check if API keys are already set
if [ -z "$YOUTUBE_API_KEY" ] || [ -z "$SPOTIFY_CLIENT_ID" ] || [ -z "$SPOTIFY_CLIENT_SECRET" ]; then
    echo "⚠️  API credentials not found in environment variables"
    echo ""
    echo "Do you have your API credentials ready?"
    echo "  - YouTube API Key"
    echo "  - Spotify Client ID"
    echo "  - Spotify Client Secret"
    echo ""
    read -p "Enter your YouTube API Key: " youtube_key
    read -p "Enter your Spotify Client ID: " spotify_id
    read -s -p "Enter your Spotify Client Secret (hidden): " spotify_secret
    echo ""
    echo ""

    # Export variables
    export YOUTUBE_API_KEY="$youtube_key"
    export SPOTIFY_CLIENT_ID="$spotify_id"
    export SPOTIFY_CLIENT_SECRET="$spotify_secret"
else
    echo "✓ API credentials found in environment variables"
    echo ""
fi

# Install required Python packages
echo "📦 Installing required Python packages..."
pip install -q requests base64

# Run the fetcher
echo ""
echo "🚀 Starting content fetcher..."
echo "   (This will search YouTube and Spotify for each junction)"
echo ""

python3 fetch_real_content.py

echo ""
echo "✅ Done! Check tour_guide_real_results.json for all results"
