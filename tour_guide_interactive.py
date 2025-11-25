#!/usr/bin/env python3
"""
Tour Guide - Interactive Mode

Simple interactive script that asks for source and destination,
then generates a tour guide report.

Usage:
    python3 tour_guide_interactive.py
"""

import sys
import os
from datetime import datetime
from tour_guide import TourGuideAPI, setup_simple_logging, config

def print_header():
    """Print welcome header."""
    print("\n" + "="*60)
    print("🚗 TOUR GUIDE - Interactive Mode")
    print("="*60)
    print("\nGenerate personalized tour recommendations for your route!")
    print("The system will find videos, music, and historical facts")
    print("for each junction along your journey.\n")

def check_api_key():
    """Check if API key is configured."""
    api_key = config.get_google_maps_api_key()

    if not api_key:
        print("❌ ERROR: Google Maps API key not configured!")
        print("\nPlease set your API key in one of these ways:")
        print("  1. Edit tour_guide/config.py")
        print("  2. Set GOOGLE_MAPS_API_KEY environment variable")
        print("\nGet API key at: https://console.cloud.google.com/")
        print("(Enable the Directions API)")
        sys.exit(1)

    print(f"✅ API Key configured: {api_key[:20]}...")
    return api_key

def get_user_input():
    """Get source and destination from user."""
    print("\n" + "-"*60)
    print("📍 Enter Your Route")
    print("-"*60)

    # Get source
    while True:
        source = input("\n🏁 Where are you starting from? (e.g., Tel Aviv, Technion, etc.)\n> ").strip()
        if source:
            break
        print("❌ Please enter a starting location.")

    # Get destination
    while True:
        destination = input("\n🎯 Where do you want to go? (e.g., Jerusalem, Ben Gurion Airport, etc.)\n> ").strip()
        if destination:
            break
        print("❌ Please enter a destination.")

    return source, destination

def get_settings():
    """Ask user for optional settings."""
    print("\n" + "-"*60)
    print("⚙️  Settings (optional)")
    print("-"*60)

    # Junction interval
    print("\n⏱️  Junction processing interval:")
    print("   How many seconds between processing each junction?")
    print("   (Default: 5 seconds)")
    interval_input = input("> ").strip()

    if interval_input:
        try:
            interval = float(interval_input)
        except ValueError:
            print("⚠️  Invalid input, using default (5 seconds)")
            interval = 5.0
    else:
        interval = 5.0

    # Verbose mode
    print("\n📢 Show progress while processing?")
    print("   (yes/no, default: yes)")
    verbose_input = input("> ").strip().lower()
    verbose = verbose_input != "no"

    # Enable debug logging
    print("\n📝 Save detailed debug logs?")
    print("   (yes/no, default: no)")
    debug_input = input("> ").strip().lower()
    enable_debug = debug_input == "yes"

    return interval, verbose, enable_debug

def confirm_route(source, destination, interval):
    """Show summary and ask for confirmation."""
    print("\n" + "="*60)
    print("📋 Route Summary")
    print("="*60)
    print(f"  🏁 From: {source}")
    print(f"  🎯 To:   {destination}")
    print(f"  ⏱️  Interval: {interval} seconds per junction")
    print("="*60)

    confirm = input("\n✅ Start processing? (yes/no) > ").strip().lower()
    return confirm in ['yes', 'y', '']

def run_tour(source, destination, interval, verbose, enable_debug):
    """Run the tour guide system."""
    print("\n" + "="*60)
    print("🚀 Processing Route...")
    print("="*60)

    # Setup logging
    if enable_debug:
        from tour_guide import setup_debug_logging
        log_filename = f"tour_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        setup_debug_logging(log_file=log_filename)
        print(f"📝 Debug logging enabled: {log_filename}")
    else:
        setup_simple_logging()

    # Create API
    api = TourGuideAPI(junction_interval_seconds=interval)

    # Run tour
    print(f"\n🗺️  Fetching route from Google Maps...")
    result = api.get_tour(
        source=source,
        destination=destination,
        verbose=verbose
    )

    return result

def save_results(result, source, destination):
    """Save results to JSON file."""
    # Create filename from locations and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_clean = source.replace(" ", "_").replace(",", "")[:20]
    dest_clean = destination.replace(" ", "_").replace(",", "")[:20]
    filename = f"tour_{source_clean}_to_{dest_clean}_{timestamp}.json"

    with open(filename, "w") as f:
        f.write(result.to_json())

    return filename

def print_results(result, json_filename):
    """Print final results."""
    # Print formatted winners
    print("\n")
    result.print_winners()

    # Print file info
    print(f"\n📁 Results saved to: {json_filename}")
    print(f"\n💡 View results:")
    print(f"   cat {json_filename}")
    print(f"   python3 -m json.tool {json_filename}")

def ask_continue():
    """Ask if user wants to process another route."""
    print("\n" + "="*60)
    response = input("🔄 Process another route? (yes/no) > ").strip().lower()
    return response in ['yes', 'y']

def main():
    """Main interactive loop."""
    print_header()

    # Check API key once
    check_api_key()

    while True:
        try:
            # Get user input
            source, destination = get_user_input()
            interval, verbose, enable_debug = get_settings()

            # Confirm
            if not confirm_route(source, destination, interval):
                print("\n❌ Cancelled.")
                if not ask_continue():
                    break
                continue

            # Run tour
            result = run_tour(source, destination, interval, verbose, enable_debug)

            # Check if successful
            if not result.success:
                print(f"\n❌ Error: {result.error}")
                print("\nPlease check:")
                print("  1. Source and destination are valid addresses")
                print("  2. Google Maps API key is correct")
                print("  3. Directions API is enabled in Google Cloud Console")

                if not ask_continue():
                    break
                continue

            # Save and display results
            json_filename = save_results(result, source, destination)
            print_results(result, json_filename)

            # Ask if user wants to continue
            if not ask_continue():
                break

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted by user.")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

            if not ask_continue():
                break

    print("\n" + "="*60)
    print("👋 Thank you for using Tour Guide!")
    print("="*60)
    print()

if __name__ == "__main__":
    main()
