#!/usr/bin/env python3
"""
Example usage of the Junction Orchestrator module.

Demonstrates:
1. Creating an orchestrator with custom tempo
2. Registering callbacks
3. Processing junctions at intervals
"""

import sys
import os
import time

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from junction_orchestrator import JunctionOrchestrator, JunctionEvent, OrchestratorConfig
from junction_orchestrator.models import DispatchMode


def simple_example():
    """Simple example with mock junctions."""
    print("\n" + "=" * 60)
    print("JUNCTION ORCHESTRATOR - Simple Example")
    print("=" * 60)

    # Create mock route data for demo (without API call)
    from route_fetcher.models import Route, Junction, Coordinates, TurnDirection

    mock_junctions = [
        Junction(
            junction_id=1,
            address="Main St & 1st Ave",
            street_name="Main Street",
            coordinates=Coordinates(32.0853, 34.7818),
            turn_direction=TurnDirection.LEFT,
            instruction="Turn left onto Main Street",
            distance_to_next_meters=500,
            distance_to_next_text="500 m",
            duration_to_next_seconds=60,
            duration_to_next_text="1 min",
        ),
        Junction(
            junction_id=2,
            address="Main St & 2nd Ave",
            street_name="Second Avenue",
            coordinates=Coordinates(32.0860, 34.7825),
            turn_direction=TurnDirection.RIGHT,
            instruction="Turn right onto Second Avenue",
            distance_to_next_meters=800,
            distance_to_next_text="800 m",
            duration_to_next_seconds=90,
            duration_to_next_text="1.5 mins",
        ),
        Junction(
            junction_id=3,
            address="2nd Ave & Park Blvd",
            street_name="Park Boulevard",
            coordinates=Coordinates(32.0870, 34.7830),
            turn_direction=TurnDirection.STRAIGHT,
            instruction="Continue straight onto Park Boulevard",
            distance_to_next_meters=1200,
            distance_to_next_text="1.2 km",
            duration_to_next_seconds=120,
            duration_to_next_text="2 mins",
        ),
        Junction(
            junction_id=4,
            address="Destination",
            street_name="Destination",
            coordinates=Coordinates(32.0880, 34.7840),
            turn_direction=TurnDirection.DESTINATION,
            instruction="Arrive at destination",
            distance_to_next_meters=0,
            distance_to_next_text="0 m",
            duration_to_next_seconds=0,
            duration_to_next_text="0 mins",
        ),
    ]

    mock_route = Route(
        source_address="Start Location, Tel Aviv",
        destination_address="End Location, Tel Aviv",
        total_distance_meters=2500,
        total_distance_text="2.5 km",
        total_duration_seconds=270,
        total_duration_text="4.5 mins",
        junctions=mock_junctions,
    )

    # Create orchestrator with 3-second intervals (for demo)
    orchestrator = JunctionOrchestrator(junction_interval_seconds=3.0)

    print(f"\nTempo: {orchestrator.interval} seconds between junctions")
    print(f"Route: {mock_route.source_address} → {mock_route.destination_address}")
    print(f"Total junctions: {len(mock_junctions)}")
    print("\n" + "-" * 60)

    # Register callback
    @orchestrator.on_junction
    def handle_junction(event: JunctionEvent):
        print(f"\n⏰ [{event.dispatch_time.strftime('%H:%M:%S')}] Junction {event.junction_index + 1}/{event.total_junctions}")
        print(f"   📍 {event.junction.address}")
        print(f"   🔄 Turn: {event.junction.turn_direction.value}")
        print(f"   📝 {event.junction.instruction}")
        print(f"   📊 Progress: {event.progress_percent:.0f}%")

        if event.is_first:
            print("   🚀 Starting route!")
        if event.is_last:
            print("   🏁 Arrived at destination!")

        # Simulate agent processing
        print("   ⚙️  [Agents would process here: Video, Music, History, Judge]")

    # Start orchestration (blocking)
    print("\nStarting orchestration...")
    orchestrator.start(mock_route, blocking=True)

    # Show stats
    stats = orchestrator.get_stats()
    print("\n" + "-" * 60)
    print("STATISTICS:")
    print(f"  Total junctions: {stats.total_junctions}")
    print(f"  Dispatched: {stats.dispatched_count}")
    print(f"  Duration: {stats.total_duration_seconds:.1f} seconds")
    print(f"  Avg interval: {stats.average_dispatch_interval:.1f} seconds")


def tempo_change_example():
    """Example showing dynamic tempo changes."""
    print("\n" + "=" * 60)
    print("JUNCTION ORCHESTRATOR - Dynamic Tempo Example")
    print("=" * 60)

    from route_fetcher.models import Route, Junction, Coordinates, TurnDirection

    # Create 5 mock junctions
    junctions = []
    for i in range(5):
        junctions.append(Junction(
            junction_id=i + 1,
            address=f"Junction {i + 1}",
            street_name=f"Street {i + 1}",
            coordinates=Coordinates(32.0 + i * 0.01, 34.7 + i * 0.01),
            turn_direction=TurnDirection.LEFT if i % 2 == 0 else TurnDirection.RIGHT,
            instruction=f"Turn at junction {i + 1}",
            distance_to_next_meters=500,
            distance_to_next_text="500 m",
            duration_to_next_seconds=60,
            duration_to_next_text="1 min",
        ))

    route = Route(
        source_address="Start",
        destination_address="End",
        total_distance_meters=2500,
        total_distance_text="2.5 km",
        total_duration_seconds=300,
        total_duration_text="5 mins",
        junctions=junctions,
    )

    # Start with 2-second interval
    orchestrator = JunctionOrchestrator(junction_interval_seconds=2.0)

    @orchestrator.on_junction
    def handle(event: JunctionEvent):
        print(f"[{event.dispatch_time.strftime('%H:%M:%S')}] Junction {event.junction_index + 1} (interval: {orchestrator.interval}s)")

        # Change tempo mid-route
        if event.junction_index == 1:
            print("  >>> Speeding up tempo to 1 second!")
            orchestrator.interval = 1.0
        elif event.junction_index == 3:
            print("  >>> Slowing down tempo to 3 seconds!")
            orchestrator.interval = 3.0

    orchestrator.start(route, blocking=True)
    print("\nDone!")


def main():
    print("\n🚗 Junction Orchestrator Examples")
    print("=" * 60)

    # Run simple example
    simple_example()

    # Run tempo change example
    tempo_change_example()


if __name__ == "__main__":
    main()
