#!/usr/bin/env python3
"""
Demo: Tour Guide from Technion to Tel Aviv University

This demonstrates the complete Tour Guide system with:
- Real route fetching from Google Maps
- Junction ID tracking through all modules
- Parallel agent processing
- Judge decision making
- Comprehensive logging

Usage:
    # API key automatically loaded from tour_guide/config.py
    python3 demo_technion_to_tau.py

    # Or override with environment variable:
    export GOOGLE_MAPS_API_KEY='your_key'
    python3 demo_technion_to_tau.py

    # Or pass as argument:
    python3 demo_technion_to_tau.py YOUR_API_KEY
"""

import sys
import os
from tour_guide import TourGuideAPI, setup_debug_logging

def main():
    # Get API key from command line, environment, or config.py
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print(f"Using API key from command line argument")
    elif os.environ.get('GOOGLE_MAPS_API_KEY'):
        print(f"Using API key from GOOGLE_MAPS_API_KEY environment variable")
    else:
        print(f"Using API key from tour_guide/config.py")

    # Enable debug logging to see junction ID tracking
    print("Setting up debug logging...")
    setup_debug_logging(log_file="technion_to_tau_debug.log")

    print("\n" + "="*60)
    print("TOUR GUIDE DEMO: Technion → Tel Aviv University")
    print("="*60)
    print("\nThis will:")
    print("  1. Fetch route from Google Maps")
    print("  2. Process each junction with Video/Music/History agents")
    print("  3. Have Judge pick winner for each junction")
    print("  4. Show junction ID tracking in logs")
    print("\n" + "="*60 + "\n")

    # Create API - key automatically loaded if not provided
    api = TourGuideAPI(
        junction_interval_seconds=5.0,
        google_maps_api_key=api_key  # None = use config.py
    )

    # Run the tour with verbose output
    result = api.get_tour(
        source="Technion",
        destination="Tel Aviv University",
        verbose=True
    )

    # Print formatted results to terminal
    print("\n")
    result.print_winners()

    # Save results to JSON file
    json_file = "technion_to_tau_results.json"
    with open(json_file, "w") as f:
        f.write(result.to_json())

    print(f"✅ Results saved to: {json_file}")

    # Summary
    print(f"\n📁 FILES CREATED:")
    print(f"   - {json_file} (Final report in JSON format)")
    print(f"   - technion_to_tau_debug.log (Debug logs with junction tracking)")
    print(f"\n💡 TIPS:")
    print(f"   View specific junction logs:")
    print(f"     cat technion_to_tau_debug.log | grep '[JID-3]'")
    print(f"   View final report:")
    print(f"     cat {json_file}")
    print(f"\n🔧 API KEY CONFIGURATION:")
    print(f"   Set your Google Maps API key in tour_guide/config.py")
    print(f"   See docs/CONFIGURATION.md for details")
    print()

if __name__ == "__main__":
    main()
