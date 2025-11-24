#!/usr/bin/env python3
"""
Full System Integration Test

Tests the complete data flow:
1. route_fetcher: Create/fetch route with junctions
2. junction_orchestrator: Tempo-controlled dispatch
3. agent_orchestrator: Threading, queue, judge
4. user_api: Final formatted output
"""

import sys
import os
import time
from datetime import datetime

# Ensure all modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 70)
print("TOUR GUIDE - FULL SYSTEM INTEGRATION TEST")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Track test results
tests_passed = 0
tests_failed = 0
errors = []

def test(name, func):
    """Run a test and track results."""
    global tests_passed, tests_failed
    print(f"\n{'─' * 50}")
    print(f"TEST: {name}")
    print(f"{'─' * 50}")
    try:
        func()
        print(f"✅ PASSED: {name}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"❌ FAILED: {name}")
        print(f"   Error: {e}")
        tests_failed += 1
        errors.append((name, str(e)))
        return False


# =============================================================================
# TEST 1: Route Fetcher Module
# =============================================================================

def test_route_fetcher():
    """Test route_fetcher models and data structures."""
    from route_fetcher.models import Route, Junction, Coordinates, TurnDirection

    # Create mock junction
    junction = Junction(
        junction_id=1,
        address="Test St & Main Ave",
        street_name="Test Street",
        coordinates=Coordinates(32.0853, 34.7818),
        turn_direction=TurnDirection.LEFT,
        instruction="Turn left onto Test Street",
        distance_to_next_meters=500,
        distance_to_next_text="500 m",
        duration_to_next_seconds=60,
        duration_to_next_text="1 min",
    )

    assert junction.junction_id == 1, "Junction ID mismatch"
    assert junction.coordinates.latitude == 32.0853, "Latitude mismatch"
    assert junction.turn_direction == TurnDirection.LEFT, "Turn direction mismatch"

    # Test to_dict
    junction_dict = junction.to_dict()
    assert "junction_id" in junction_dict, "to_dict missing junction_id"
    assert junction_dict["turn"] == "LEFT", "to_dict turn mismatch"

    # Create mock route
    route = Route(
        source_address="Source City",
        destination_address="Dest City",
        total_distance_meters=10000,
        total_distance_text="10 km",
        total_duration_seconds=600,
        total_duration_text="10 mins",
        junctions=[junction],
    )

    assert route.junction_count == 1, "Junction count mismatch"
    assert route.source_address == "Source City", "Source address mismatch"

    # Test to_yaml_format
    yaml_format = route.to_yaml_format()
    assert "Route" in yaml_format, "YAML format missing Route key"
    assert "waypoints" in yaml_format["Route"], "YAML format missing waypoints"

    print(f"   Created junction: {junction.address}")
    print(f"   Created route: {route.source_address} → {route.destination_address}")
    print(f"   Junction count: {route.junction_count}")

test("Route Fetcher - Models", test_route_fetcher)


# =============================================================================
# TEST 2: Junction Orchestrator Module
# =============================================================================

def test_junction_orchestrator():
    """Test junction_orchestrator tempo control."""
    from route_fetcher.models import Route, Junction, Coordinates, TurnDirection
    from junction_orchestrator import JunctionOrchestrator, JunctionEvent
    from junction_orchestrator.models import OrchestratorState

    # Create mock route with 3 junctions
    junctions = []
    for i in range(3):
        junctions.append(Junction(
            junction_id=i + 1,
            address=f"Junction {i + 1}",
            street_name=f"Street {i + 1}",
            coordinates=Coordinates(32.0 + i * 0.01, 34.7 + i * 0.01),
            turn_direction=TurnDirection.LEFT,
            instruction=f"Turn at junction {i + 1}",
            distance_to_next_meters=500,
            distance_to_next_text="500 m",
            duration_to_next_seconds=60,
            duration_to_next_text="1 min",
        ))

    route = Route(
        source_address="Start",
        destination_address="End",
        total_distance_meters=1500,
        total_distance_text="1.5 km",
        total_duration_seconds=180,
        total_duration_text="3 mins",
        junctions=junctions,
    )

    # Create orchestrator with fast tempo
    orchestrator = JunctionOrchestrator(junction_interval_seconds=0.5)

    assert orchestrator.interval == 0.5, "Interval not set correctly"
    assert orchestrator.state == OrchestratorState.IDLE, "Initial state should be IDLE"

    # Track dispatched events
    dispatched_events = []

    @orchestrator.on_junction
    def track_event(event: JunctionEvent):
        dispatched_events.append(event)
        print(f"   Dispatched: Junction {event.junction_index + 1}/{event.total_junctions}")

    # Run orchestrator
    start_time = time.time()
    orchestrator.start(route, blocking=True)
    elapsed = time.time() - start_time

    assert len(dispatched_events) == 3, f"Expected 3 events, got {len(dispatched_events)}"
    assert dispatched_events[0].is_first, "First event should have is_first=True"
    assert dispatched_events[-1].is_last, "Last event should have is_last=True"

    print(f"   Dispatched {len(dispatched_events)} events in {elapsed:.2f}s")
    print(f"   Final state: {orchestrator.state.value}")

test("Junction Orchestrator - Tempo Control", test_junction_orchestrator)


# =============================================================================
# TEST 3: Agent Orchestrator Module
# =============================================================================

def test_agent_orchestrator():
    """Test agent_orchestrator threading and queue."""
    from route_fetcher.models import Route, Junction, Coordinates, TurnDirection
    from agent_orchestrator import AgentOrchestrator, JunctionResults
    from agent_orchestrator.models import AgentType

    # Create mock route
    junctions = []
    for i in range(2):  # Just 2 junctions for speed
        junctions.append(Junction(
            junction_id=i + 1,
            address=f"Agent Test Junction {i + 1}",
            street_name=f"Agent Street {i + 1}",
            coordinates=Coordinates(32.0 + i * 0.01, 34.7 + i * 0.01),
            turn_direction=TurnDirection.RIGHT,
            instruction=f"Turn right at junction {i + 1}",
            distance_to_next_meters=500,
            distance_to_next_text="500 m",
            duration_to_next_seconds=60,
            duration_to_next_text="1 min",
        ))

    route = Route(
        source_address="Agent Test Start",
        destination_address="Agent Test End",
        total_distance_meters=1000,
        total_distance_text="1 km",
        total_duration_seconds=120,
        total_duration_text="2 mins",
        junctions=junctions,
    )

    # Create orchestrator with fast tempo
    orchestrator = AgentOrchestrator(
        junction_interval_seconds=0.5,
        agent_timeout_seconds=10.0,
    )

    # Track results
    junction_results = []

    @orchestrator.on_junction_complete
    def track_result(result: JunctionResults):
        junction_results.append(result)
        if result.decision:
            print(f"   Junction {result.junction_index + 1}: Winner = {result.decision.winner_type.value}")
        else:
            print(f"   Junction {result.junction_index + 1}: No decision")

    # Run
    report = orchestrator.start(route, blocking=True)

    assert report is not None, "Report should not be None"
    assert len(junction_results) == 2, f"Expected 2 results, got {len(junction_results)}"

    # Check each result has all agent outputs
    for jr in junction_results:
        assert jr.video_result is not None, "Video result missing"
        assert jr.music_result is not None, "Music result missing"
        assert jr.history_result is not None, "History result missing"
        assert jr.decision is not None, "Judge decision missing"
        assert jr.decision.winner is not None, "Winner missing"

    print(f"   Processed {len(junction_results)} junctions")
    print(f"   Video wins: {report.video_wins}, Music wins: {report.music_wins}, History wins: {report.history_wins}")

test("Agent Orchestrator - Threading & Queue", test_agent_orchestrator)


# =============================================================================
# TEST 4: User API Module
# =============================================================================

def test_user_api():
    """Test user_api result formatting."""
    from user_api.tour_guide_api import TourGuideAPI, TourGuideResult, JunctionWinner

    # Create mock result
    winners = [
        JunctionWinner(
            junction_number=1,
            junction_address="API Test Junction 1",
            turn_direction="LEFT",
            winner_type="video",
            winner_title="Test Video",
            winner_description="A test video",
            winner_url="https://example.com/video",
            score=85.5,
        ),
        JunctionWinner(
            junction_number=2,
            junction_address="API Test Junction 2",
            turn_direction="RIGHT",
            winner_type="music",
            winner_title="Test Music",
            winner_description="A test song",
            winner_url="https://example.com/music",
            score=82.0,
        ),
    ]

    result = TourGuideResult(
        source="API Test Start",
        destination="API Test End",
        total_distance="5 km",
        total_duration="10 mins",
        winners=winners,
        total_junctions=2,
        video_wins=1,
        music_wins=1,
        history_wins=0,
        processing_time_seconds=5.5,
    )

    assert result.success, "Result should be successful"
    assert len(result.winners) == 2, "Should have 2 winners"
    assert result.video_wins == 1, "Video wins mismatch"
    assert result.music_wins == 1, "Music wins mismatch"

    # Test to_dict
    result_dict = result.to_dict()
    assert "winners" in result_dict, "to_dict missing winners"
    assert "summary" in result_dict, "to_dict missing summary"

    # Test to_json
    json_str = result.to_json()
    assert "API Test Start" in json_str, "JSON missing source"
    assert "Test Video" in json_str, "JSON missing winner title"

    print(f"   Created result: {result.source} → {result.destination}")
    print(f"   Winners: {len(result.winners)}")
    print(f"   JSON length: {len(json_str)} chars")

test("User API - Result Formatting", test_user_api)


# =============================================================================
# TEST 5: Complete End-to-End Integration
# =============================================================================

def test_end_to_end():
    """Test complete system flow from route to final report."""
    from route_fetcher.models import Route, Junction, Coordinates, TurnDirection
    from agent_orchestrator import AgentOrchestrator
    from user_api.tour_guide_api import TourGuideResult, JunctionWinner

    print("   Creating route with 3 junctions...")

    # Create realistic route
    junctions = [
        Junction(
            junction_id=1,
            address="Dizengoff & Ben Yehuda",
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
            street_name="Destination",
            coordinates=Coordinates(32.0800, 34.7810),
            turn_direction=TurnDirection.DESTINATION,
            instruction="Arrive at Rabin Square",
            distance_to_next_meters=0,
            distance_to_next_text="0 m",
            duration_to_next_seconds=0,
            duration_to_next_text="0 mins",
        ),
    ]

    route = Route(
        source_address="Ben Yehuda Street, Tel Aviv",
        destination_address="Rabin Square, Tel Aviv",
        total_distance_meters=1400,
        total_distance_text="1.4 km",
        total_duration_seconds=210,
        total_duration_text="3.5 mins",
        junctions=junctions,
    )

    print(f"   Route: {route.source_address} → {route.destination_address}")
    print(f"   Distance: {route.total_distance_text}, Duration: {route.total_duration_text}")

    # Run through agent orchestrator
    print("   Running agent orchestrator...")
    orchestrator = AgentOrchestrator(junction_interval_seconds=0.5)

    report = orchestrator.start(route, blocking=True)

    assert report is not None, "Report is None"
    assert len(report.junction_results) == 3, f"Expected 3 results, got {len(report.junction_results)}"

    # Convert to user-friendly result
    print("   Converting to user API format...")
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

    assert result.success, "Result should be successful"
    assert len(result.winners) == 3, f"Expected 3 winners, got {len(result.winners)}"

    print(f"\n   ✓ End-to-end flow completed successfully!")
    print(f"   ✓ Processed {result.total_junctions} junctions")
    print(f"   ✓ Winners: Video={result.video_wins}, Music={result.music_wins}, History={result.history_wins}")
    print(f"   ✓ Processing time: {result.processing_time_seconds:.2f}s")

    # Print summary
    print(f"\n   WINNERS:")
    for w in result.winners:
        icon = {"video": "🎬", "music": "🎵", "history": "📖"}.get(w.winner_type, "❓")
        print(f"     {w.junction_number}. {w.junction_address}: {icon} {w.winner_title} ({w.score:.0f}/100)")

test("End-to-End Integration", test_end_to_end)


# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Total tests: {tests_passed + tests_failed}")
print(f"Passed: {tests_passed} ✅")
print(f"Failed: {tests_failed} ❌")

if errors:
    print("\nFailed tests:")
    for name, error in errors:
        print(f"  - {name}: {error}")

print("\n" + "=" * 70)
if tests_failed == 0:
    print("🎉 ALL TESTS PASSED - System is working correctly!")
else:
    print("⚠️  SOME TESTS FAILED - Please check the errors above")
print("=" * 70 + "\n")

sys.exit(0 if tests_failed == 0 else 1)
