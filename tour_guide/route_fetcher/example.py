#!/usr/bin/env python3
"""
Example usage of the Route Fetcher module.

This script demonstrates how to:
1. Fetch a route between two addresses
2. Extract junction data
3. Format output for Tour Guide agents
"""

import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from route_fetcher import RouteFetcher, Route
from route_fetcher.google_maps_client import GoogleMapsClientError


def print_route_summary(route: Route):
    """Print a summary of the route."""
    print("\n" + "=" * 60)
    print("ROUTE SUMMARY")
    print("=" * 60)
    print(f"From: {route.source_address}")
    print(f"To:   {route.destination_address}")
    print(f"Distance: {route.total_distance_text}")
    print(f"Duration: {route.total_duration_text}")
    print(f"Total Junctions: {route.junction_count}")
    print("=" * 60)


def print_junctions(route: Route):
    """Print all junctions in the route."""
    print("\nJUNCTIONS:")
    print("-" * 60)

    for junction in route.junctions:
        print(f"\n[Junction {junction.junction_id}]")
        print(f"  📍 {junction.address}")
        print(f"  🔄 Turn: {junction.turn_direction.value}")
        print(f"  📝 {junction.instruction}")
        print(f"  📏 Distance to next: {junction.distance_to_next_text}")
        print(f"  ⏱️  Duration to next: {junction.duration_to_next_text}")
        print(f"  🌐 Coordinates: {junction.coordinates.to_string()}")


def print_agent_format(route: Route):
    """Print the route in Tour Guide agent format."""
    print("\n" + "=" * 60)
    print("TOUR GUIDE AGENT FORMAT (YAML-style)")
    print("=" * 60)

    agent_data = route.to_yaml_format()

    # Pretty print as YAML-like structure
    def print_yaml(data, indent=0):
        prefix = "  " * indent
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{prefix}{key}:")
                    print_yaml(value, indent + 1)
                else:
                    print(f"{prefix}{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                print_yaml(item, indent)

    print_yaml(agent_data)


def main():
    # Example addresses (Israel route from existing test)
    source = "Ramat HaSharon, Israel"
    destination = "Tel Aviv, Israel"

    # Check for custom addresses from command line
    if len(sys.argv) >= 3:
        source = sys.argv[1]
        destination = sys.argv[2]

    print(f"\n🚗 Fetching route from '{source}' to '{destination}'...")

    try:
        # Initialize the fetcher
        fetcher = RouteFetcher()

        # Fetch the route
        route = fetcher.fetch_route(source, destination)

        # Print results
        print_route_summary(route)
        print_junctions(route)
        print_agent_format(route)

        # Also save to JSON file
        output_file = "route_output.json"
        with open(output_file, "w") as f:
            json.dump(route.to_dict(), f, indent=2)
        print(f"\n✅ Full route data saved to: {output_file}")

    except GoogleMapsClientError as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you have set the GOOGLE_MAPS_API_KEY environment variable:")
        print("  export GOOGLE_MAPS_API_KEY='your-api-key-here'")
        sys.exit(1)


if __name__ == "__main__":
    main()
