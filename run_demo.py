#!/usr/bin/env python3
"""
Tour Guide Demo - Simple Test Script
=====================================

Run with: python run_demo.py

This script:
1. Loads API keys from .env file
2. Runs a test tour from Ramat HaSharon to Tel Aviv
3. Displays the results

Setup:
1. Copy .env.example to .env
2. Add your API keys to .env
3. Run: python run_demo.py
"""

import sys
import os

def main():
    print("=" * 60)
    print("  TOUR GUIDE DEMO")
    print("=" * 60)
    
    # Step 1: Load .env file
    print("\n[1/4] Loading environment variables...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("      .env file loaded")
    except ImportError:
        print("      python-dotenv not installed, using system env vars")
    
    # Step 2: Check API keys
    print("\n[2/4] Checking API keys...")
    keys = {
        "GOOGLE_MAPS_API_KEY": os.environ.get("GOOGLE_MAPS_API_KEY"),
        "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY"),
        "SPOTIFY_CLIENT_ID": os.environ.get("SPOTIFY_CLIENT_ID"),
        "SPOTIFY_CLIENT_SECRET": os.environ.get("SPOTIFY_CLIENT_SECRET"),
    }
    
    missing = [k for k, v in keys.items() if not v]
    if missing:
        print(f"      ERROR: Missing API keys: {', '.join(missing)}")
        print("\n      Please create a .env file with your API keys:")
        print("        1. copy .env.example .env")
        print("        2. Edit .env and add your keys")
        print("        3. Run this script again")
        sys.exit(1)
    
    print("      All API keys found!")
    
    # Step 3: Run the tour
    print("\n[3/4] Running tour...")
    source = sys.argv[1] if len(sys.argv) > 1 else "Ramat HaSharon, Israel"
    destination = sys.argv[2] if len(sys.argv) > 2 else "Tel Aviv, Israel"
    
    print(f"      From: {source}")
    print(f"      To:   {destination}")
    print()
    
    from tour_guide import TourGuideAPI
    
    api = TourGuideAPI(junction_interval_seconds=2.0)
    result = api.get_tour(source, destination, verbose=True)
    
    # Step 4: Display results
    print("\n[4/4] Results")
    print("=" * 60)
    
    if result.success:
        print(f"  Status:     SUCCESS")
        print(f"  Distance:   {result.total_distance}")
        print(f"  Duration:   {result.total_duration}")
        print(f"  Junctions:  {result.total_junctions}")
        print()
        print("  Winner Distribution:")
        print(f"    Video:   {result.video_wins} wins")
        print(f"    Music:   {result.music_wins} wins")
        print(f"    History: {result.history_wins} wins")
        print()
        print(f"  Processing Time: {result.processing_time_seconds:.1f} seconds")
        
        if result.winners:
            print()
            print("  Top Recommendations:")
            for i, w in enumerate(result.winners[:3], 1):
                print(f"    {i}. [{w.winner_type:7}] {w.winner_title[:45]}...")
    else:
        print(f"  Status: FAILED")
        print(f"  Error:  {result.error}")
    
    print()
    print("=" * 60)
    print("  Demo complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
