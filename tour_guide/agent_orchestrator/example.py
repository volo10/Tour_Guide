#!/usr/bin/env python3
"""
Example usage of the Agent Orchestrator module.

Demonstrates:
1. Running the complete Tour Guide system with mock data
2. Processing junctions with parallel agent threads
3. Generating a final report with winners
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from route_fetcher.models import Route, Junction, Coordinates, TurnDirection
from agent_orchestrator import AgentOrchestrator, JunctionResults, FinalReport


def create_mock_route() -> Route:
    """Create a mock route for demo purposes."""
    junctions = [
        Junction(
            junction_id=1,
            address="Dizengoff St & Ben Yehuda",
            street_name="Dizengoff Street",
            coordinates=Coordinates(32.0853, 34.7740),
            turn_direction=TurnDirection.LEFT,
            instruction="Turn left onto Dizengoff Street",
            distance_to_next_meters=600,
            distance_to_next_text="600 m",
            duration_to_next_seconds=90,
            duration_to_next_text="1.5 mins",
        ),
        Junction(
            junction_id=2,
            address="Dizengoff Center",
            street_name="King George Street",
            coordinates=Coordinates(32.0750, 34.7750),
            turn_direction=TurnDirection.RIGHT,
            instruction="Turn right onto King George Street",
            distance_to_next_meters=800,
            distance_to_next_text="800 m",
            duration_to_next_seconds=120,
            duration_to_next_text="2 mins",
        ),
        Junction(
            junction_id=3,
            address="Rabin Square",
            street_name="Ibn Gabirol Street",
            coordinates=Coordinates(32.0800, 34.7810),
            turn_direction=TurnDirection.STRAIGHT,
            instruction="Continue onto Ibn Gabirol Street",
            distance_to_next_meters=500,
            distance_to_next_text="500 m",
            duration_to_next_seconds=60,
            duration_to_next_text="1 min",
        ),
        Junction(
            junction_id=4,
            address="Tel Aviv Museum",
            street_name="Destination",
            coordinates=Coordinates(32.0770, 34.7870),
            turn_direction=TurnDirection.DESTINATION,
            instruction="Arrive at Tel Aviv Museum",
            distance_to_next_meters=0,
            distance_to_next_text="0 m",
            duration_to_next_seconds=0,
            duration_to_next_text="0 mins",
        ),
    ]

    return Route(
        source_address="Ben Yehuda Street, Tel Aviv",
        destination_address="Tel Aviv Museum of Art",
        total_distance_meters=1900,
        total_distance_text="1.9 km",
        total_duration_seconds=270,
        total_duration_text="4.5 mins",
        junctions=junctions,
    )


def main():
    print("\n" + "=" * 60)
    print("🚗 TOUR GUIDE - Agent Orchestrator Demo")
    print("=" * 60)

    # Create mock route
    route = create_mock_route()
    print(f"\nRoute: {route.source_address}")
    print(f"    → {route.destination_address}")
    print(f"Distance: {route.total_distance_text}")
    print(f"Junctions: {len(route.junctions)}")

    # Create orchestrator with fast tempo for demo (2 seconds)
    orchestrator = AgentOrchestrator(
        junction_interval_seconds=2.0,  # Fast for demo
        agent_timeout_seconds=10.0,
    )

    print(f"\n⏱️  Tempo: {orchestrator.interval}s between junctions")
    print("-" * 60)
    print("\nProcessing junctions...")
    print("(Each junction spawns 3 agent threads + judge)\n")

    # Register callback to show progress
    @orchestrator.on_junction_complete
    def on_complete(result: JunctionResults):
        if result.decision:
            winner = result.decision.winner
            icon = {
                "video": "🎬",
                "music": "🎵",
                "history": "📖"
            }.get(result.decision.winner_type.value, "❓")

            print(f"  Junction {result.junction_index + 1}: {result.junction.address}")
            print(f"    {icon} Winner: {winner.title}")
            print(f"    Score: {result.decision.winning_score:.0f}/100")
            print(f"    Reason: {result.decision.reasoning}")
            print()
        else:
            print(f"  Junction {result.junction_index + 1}: ❌ No winner (errors)")

    # Run the orchestrator
    report = orchestrator.start(route, blocking=True)

    # Print final summary
    if report:
        report.print_summary()


def demo_with_callbacks():
    """Demo showing callback registration."""
    print("\n" + "=" * 60)
    print("🎯 Callback Demo")
    print("=" * 60)

    route = create_mock_route()
    orchestrator = AgentOrchestrator(junction_interval_seconds=1.0)

    # Track results
    results_log = []

    @orchestrator.on_junction_complete
    def log_junction(result: JunctionResults):
        results_log.append({
            "junction": result.junction.address,
            "winner": result.decision.winner_type.value if result.decision else None,
            "score": result.decision.winning_score if result.decision else 0,
        })

    @orchestrator.on_route_complete
    def on_done(report: FinalReport):
        print("\n✅ Route complete callback triggered!")
        print(f"   Processed {report.total_junctions} junctions")
        print(f"   Success rate: {report.success_rate:.0f}%")

    print("Running with callbacks...")
    orchestrator.start(route, blocking=True)

    print("\nResults log:")
    for entry in results_log:
        print(f"  {entry['junction']}: {entry['winner']} ({entry['score']:.0f})")


if __name__ == "__main__":
    main()
    demo_with_callbacks()
