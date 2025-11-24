"""
Pytest configuration and fixtures for Tour Guide tests.
"""

import pytest
from datetime import datetime

from tour_guide.route_fetcher.models import (
    Route, Junction, Coordinates, TurnDirection
)


@pytest.fixture
def sample_coordinates():
    """Sample GPS coordinates."""
    return Coordinates(latitude=32.0853, longitude=34.7818)


@pytest.fixture
def sample_junction(sample_coordinates):
    """Sample junction for testing."""
    return Junction(
        junction_id=1,
        address="Main St & 1st Ave",
        street_name="Main Street",
        coordinates=sample_coordinates,
        turn_direction=TurnDirection.LEFT,
        instruction="Turn left onto Main Street",
        distance_to_next_meters=500,
        distance_to_next_text="500 m",
        duration_to_next_seconds=60,
        duration_to_next_text="1 min",
    )


@pytest.fixture
def sample_junctions():
    """List of sample junctions for testing."""
    junctions = []
    directions = [TurnDirection.LEFT, TurnDirection.RIGHT, TurnDirection.STRAIGHT, TurnDirection.DESTINATION]
    streets = ["Main Street", "Oak Avenue", "Park Boulevard", "Destination"]

    for i in range(4):
        junctions.append(Junction(
            junction_id=i + 1,
            address=f"Junction {i + 1}",
            street_name=streets[i],
            coordinates=Coordinates(32.0 + i * 0.01, 34.7 + i * 0.01),
            turn_direction=directions[i],
            instruction=f"Navigate to {streets[i]}",
            distance_to_next_meters=500 if i < 3 else 0,
            distance_to_next_text="500 m" if i < 3 else "0 m",
            duration_to_next_seconds=60 if i < 3 else 0,
            duration_to_next_text="1 min" if i < 3 else "0 mins",
            cumulative_distance_meters=i * 500,
            cumulative_duration_seconds=i * 60,
        ))

    return junctions


@pytest.fixture
def sample_route(sample_junctions):
    """Sample route for testing."""
    return Route(
        source_address="Start Location, Tel Aviv",
        destination_address="End Location, Tel Aviv",
        total_distance_meters=1500,
        total_distance_text="1.5 km",
        total_duration_seconds=180,
        total_duration_text="3 mins",
        junctions=sample_junctions,
    )


@pytest.fixture
def minimal_route():
    """Minimal route with 2 junctions."""
    junctions = [
        Junction(
            junction_id=1,
            address="Start",
            street_name="Start Street",
            coordinates=Coordinates(32.0, 34.7),
            turn_direction=TurnDirection.STRAIGHT,
            instruction="Start",
            distance_to_next_meters=100,
            distance_to_next_text="100 m",
            duration_to_next_seconds=30,
            duration_to_next_text="30 sec",
        ),
        Junction(
            junction_id=2,
            address="End",
            street_name="End Street",
            coordinates=Coordinates(32.01, 34.71),
            turn_direction=TurnDirection.DESTINATION,
            instruction="Arrive",
            distance_to_next_meters=0,
            distance_to_next_text="0 m",
            duration_to_next_seconds=0,
            duration_to_next_text="0 mins",
        ),
    ]

    return Route(
        source_address="Start",
        destination_address="End",
        total_distance_meters=100,
        total_distance_text="100 m",
        total_duration_seconds=30,
        total_duration_text="30 sec",
        junctions=junctions,
    )
