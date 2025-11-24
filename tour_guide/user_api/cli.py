#!/usr/bin/env python3
"""
Command Line Interface for Tour Guide.

Provides interactive and command-line modes for users to
get tour recommendations.
"""

import sys
import argparse

from .tour_guide_api import TourGuideAPI, get_tour_winners


def interactive_mode():
    """
    Run Tour Guide in interactive mode.

    Prompts user for source and destination, then shows results.
    """
    print("\n" + "=" * 60)
    print("🚗 TOUR GUIDE - Interactive Mode")
    print("=" * 60)
    print("Get personalized recommendations (video, music, history)")
    print("for each junction along your route!")
    print("=" * 60)

    while True:
        print("\n" + "-" * 40)

        # Get source
        source = input("\n📍 Enter starting address (or 'quit' to exit):\n> ").strip()
        if source.lower() in ('quit', 'exit', 'q'):
            print("\n👋 Goodbye!\n")
            break

        if not source:
            print("❌ Please enter a valid address.")
            continue

        # Get destination
        destination = input("\n🎯 Enter destination address:\n> ").strip()
        if not destination:
            print("❌ Please enter a valid destination.")
            continue

        # Get optional settings
        try:
            interval_input = input("\n⏱️  Processing speed (seconds per junction, default 3): ").strip()
            interval = float(interval_input) if interval_input else 3.0
        except ValueError:
            interval = 3.0

        print("\n" + "=" * 60)
        print("🔄 Processing your route...")
        print("=" * 60)

        # Run tour guide
        try:
            result = get_tour_winners(
                source=source,
                destination=destination,
                interval=interval,
                verbose=True,
            )

            if not result.success:
                print(f"\n❌ Error: {result.error}")

        except Exception as e:
            print(f"\n❌ Error: {e}")

        # Ask to continue
        again = input("\n🔄 Process another route? (y/n): ").strip().lower()
        if again not in ('y', 'yes'):
            print("\n👋 Goodbye!\n")
            break


def run_cli():
    """
    Run Tour Guide from command line with arguments.

    Usage:
        python -m user_api.cli "Tel Aviv" "Jerusalem"
        python -m user_api.cli --source "Tel Aviv" --destination "Jerusalem"
        python -m user_api.cli --interactive
    """
    parser = argparse.ArgumentParser(
        description="Tour Guide - Get recommendations for your route",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m user_api.cli "Tel Aviv" "Jerusalem"
  python -m user_api.cli --source "Tel Aviv" --destination "Jerusalem" --interval 5
  python -m user_api.cli --interactive
  python -m user_api.cli "Tel Aviv" "Haifa" --json

Output Formats:
  Default: Formatted text with emojis
  --json: JSON output for programmatic use
        """
    )

    parser.add_argument(
        'source',
        nargs='?',
        help='Starting address'
    )
    parser.add_argument(
        'destination',
        nargs='?',
        help='Destination address'
    )
    parser.add_argument(
        '-s', '--source',
        dest='source_opt',
        help='Starting address (alternative to positional)'
    )
    parser.add_argument(
        '-d', '--destination',
        dest='dest_opt',
        help='Destination address (alternative to positional)'
    )
    parser.add_argument(
        '-i', '--interval',
        type=float,
        default=3.0,
        help='Seconds between junctions (default: 3)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress progress output'
    )

    args = parser.parse_args()

    # Interactive mode
    if args.interactive:
        interactive_mode()
        return

    # Get source and destination
    source = args.source or args.source_opt
    destination = args.destination or args.dest_opt

    if not source or not destination:
        parser.print_help()
        print("\n❌ Error: Both source and destination are required.")
        print("   Use --interactive for guided input.")
        sys.exit(1)

    # Run tour guide
    api = TourGuideAPI(junction_interval_seconds=args.interval)

    if not args.quiet and not args.json:
        print(f"\n🚗 Tour Guide: {source} → {destination}")
        print(f"⏱️  Interval: {args.interval}s per junction")
        print("-" * 40)

    result = api.get_tour(
        source=source,
        destination=destination,
        verbose=not args.quiet and not args.json,
    )

    if args.json:
        print(result.to_json())
    else:
        result.print_winners()

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    run_cli()
