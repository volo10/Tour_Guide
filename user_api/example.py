#!/usr/bin/env python3
"""
Example usage of the User API module.

Demonstrates the different ways to use the Tour Guide API.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from route_fetcher.models import Route, Junction, Coordinates, TurnDirection
from agent_orchestrator import AgentOrchestrator
from user_api.tour_guide_api import TourGuideAPI, TourGuideResult, JunctionWinner


def create_mock_route() -> Route:
    """Create a mock route for demonstration."""
    junctions = [
        Junction(
            junction_id=1,
            address="Ayalon Highway Entrance",
            street_name="Ayalon Highway",
            coordinates=Coordinates(32.0853, 34.7818),
            turn_direction=TurnDirection.MERGE,
            instruction="Merge onto Ayalon Highway",
            distance_to_next_meters=5000,
            distance_to_next_text="5 km",
            duration_to_next_seconds=300,
            duration_to_next_text="5 mins",
        ),
        Junction(
            junction_id=2,
            address="Route 1 Interchange",
            street_name="Route 1",
            coordinates=Coordinates(31.9500, 34.8500),
            turn_direction=TurnDirection.RIGHT,
            instruction="Take exit onto Route 1 towards Jerusalem",
            distance_to_next_meters=25000,
            distance_to_next_text="25 km",
            duration_to_next_seconds=1200,
            duration_to_next_text="20 mins",
        ),
        Junction(
            junction_id=3,
            address="Sha'ar HaGai",
            street_name="Route 1",
            coordinates=Coordinates(31.8000, 35.0500),
            turn_direction=TurnDirection.STRAIGHT,
            instruction="Continue on Route 1",
            distance_to_next_meters=15000,
            distance_to_next_text="15 km",
            duration_to_next_seconds=900,
            duration_to_next_text="15 mins",
        ),
        Junction(
            junction_id=4,
            address="Jerusalem - City Center",
            street_name="Jaffa Road",
            coordinates=Coordinates(31.7800, 35.2200),
            turn_direction=TurnDirection.DESTINATION,
            instruction="Arrive at Jerusalem",
            distance_to_next_meters=0,
            distance_to_next_text="0 m",
            duration_to_next_seconds=0,
            duration_to_next_text="0 mins",
        ),
    ]

    return Route(
        source_address="Tel Aviv, Israel",
        destination_address="Jerusalem, Israel",
        total_distance_meters=62000,
        total_distance_text="62 km",
        total_duration_seconds=3300,
        total_duration_text="55 mins",
        junctions=junctions,
    )


def demo_api_with_mock():
    """Demonstrate API with mock route data."""
    print("\n" + "=" * 60)
    print("🚗 TOUR GUIDE API - Demo with Mock Data")
    print("=" * 60)

    # Create mock route
    route = create_mock_route()
    print(f"\nRoute: {route.source_address} → {route.destination_address}")
    print(f"Distance: {route.total_distance_text}")
    print(f"Duration: {route.total_duration_text}")
    print(f"Junctions: {len(route.junctions)}")

    # Create orchestrator and process
    orchestrator = AgentOrchestrator(junction_interval_seconds=1.0)

    print("\n" + "-" * 40)
    print("Processing junctions...")

    @orchestrator.on_junction_complete
    def on_complete(result):
        if result.decision:
            icon = {"video": "🎬", "music": "🎵", "history": "📖"}.get(
                result.decision.winner_type.value, "❓"
            )
            print(f"  {icon} {result.junction.address}: {result.decision.winner.title}")

    report = orchestrator.start(route, blocking=True)

    # Convert to user-friendly result
    winners = []
    for jr in report.junction_results:
        if jr.decision:
            winners.append(JunctionWinner(
                junction_number=jr.junction_index + 1,
                junction_address=jr.junction.address,
                turn_direction=jr.junction.turn_direction.value,
                winner_type=jr.decision.winner_type.value,
                winner_title=jr.decision.winner.title,
                winner_description=jr.decision.winner.description,
                winner_url=jr.decision.winner.url,
                score=jr.decision.winning_score,
            ))

    result = TourGuideResult(
        source=route.source_address,
        destination=route.destination_address,
        total_distance=route.total_distance_text,
        total_duration=route.total_duration_text,
        winners=winners,
        total_junctions=len(route.junctions),
        video_wins=report.video_wins,
        music_wins=report.music_wins,
        history_wins=report.history_wins,
        processing_time_seconds=report.total_processing_time_seconds,
    )

    # Print results
    result.print_winners()

    # Show JSON output
    print("\n📄 JSON Output:")
    print("-" * 40)
    print(result.to_json())


def demo_python_api():
    """Demonstrate the simple Python API usage."""
    print("\n" + "=" * 60)
    print("🐍 Python API Usage Example")
    print("=" * 60)

    print("""
# Simple usage:
from user_api import TourGuideAPI

api = TourGuideAPI(junction_interval_seconds=5.0)
result = api.get_tour("Tel Aviv", "Jerusalem")
result.print_winners()

# Access individual winners:
for winner in result.winners:
    print(f"{winner.junction_number}. {winner.winner_type}: {winner.winner_title}")

# Get JSON:
json_data = result.to_json()
""")


def demo_cli_usage():
    """Show CLI usage examples."""
    print("\n" + "=" * 60)
    print("💻 CLI Usage Examples")
    print("=" * 60)

    print("""
# Basic usage:
python -m user_api.cli "Tel Aviv" "Jerusalem"

# With custom interval:
python -m user_api.cli "Tel Aviv" "Haifa" --interval 5

# Interactive mode:
python -m user_api.cli --interactive

# JSON output:
python -m user_api.cli "Tel Aviv" "Jerusalem" --json

# Quiet mode (no progress):
python -m user_api.cli "Tel Aviv" "Jerusalem" --quiet
""")


def demo_rest_api():
    """Show REST API usage examples."""
    print("\n" + "=" * 60)
    print("🌐 REST API Usage Examples")
    print("=" * 60)

    print("""
# Start server:
python -m user_api.rest_api

# GET request:
curl "http://localhost:5000/tour?source=Tel+Aviv&destination=Jerusalem"

# POST request:
curl -X POST http://localhost:5000/tour \\
  -H "Content-Type: application/json" \\
  -d '{"source": "Tel Aviv", "destination": "Jerusalem", "interval": 5}'

# Health check:
curl http://localhost:5000/health
""")


if __name__ == "__main__":
    demo_api_with_mock()
    demo_python_api()
    demo_cli_usage()
    demo_rest_api()
