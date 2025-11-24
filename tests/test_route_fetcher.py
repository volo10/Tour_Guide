"""
Unit tests for the route_fetcher module.
"""

import pytest
from tour_guide.route_fetcher.models import (
    Route, Junction, Coordinates, TurnDirection
)


class TestCoordinates:
    """Tests for Coordinates dataclass."""

    def test_coordinates_creation(self):
        """Test creating coordinates."""
        coords = Coordinates(latitude=32.0853, longitude=34.7818)
        assert coords.latitude == 32.0853
        assert coords.longitude == 34.7818

    def test_to_list(self):
        """Test converting to list."""
        coords = Coordinates(latitude=32.0853, longitude=34.7818)
        assert coords.to_list() == [32.0853, 34.7818]

    def test_to_string(self):
        """Test converting to string."""
        coords = Coordinates(latitude=32.0853, longitude=34.7818)
        assert coords.to_string() == "32.0853,34.7818"


class TestTurnDirection:
    """Tests for TurnDirection enum."""

    def test_all_directions_exist(self):
        """Test that all expected directions exist."""
        directions = [
            TurnDirection.LEFT,
            TurnDirection.RIGHT,
            TurnDirection.STRAIGHT,
            TurnDirection.SLIGHT_LEFT,
            TurnDirection.SLIGHT_RIGHT,
            TurnDirection.SHARP_LEFT,
            TurnDirection.SHARP_RIGHT,
            TurnDirection.U_TURN,
            TurnDirection.MERGE,
            TurnDirection.RAMP,
            TurnDirection.FORK,
            TurnDirection.ROUNDABOUT,
            TurnDirection.DESTINATION,
        ]
        for direction in directions:
            assert direction.value is not None

    def test_direction_values(self):
        """Test direction enum values."""
        assert TurnDirection.LEFT.value == "LEFT"
        assert TurnDirection.RIGHT.value == "RIGHT"
        assert TurnDirection.STRAIGHT.value == "STRAIGHT"


class TestJunction:
    """Tests for Junction dataclass."""

    def test_junction_creation(self, sample_coordinates):
        """Test creating a junction."""
        junction = Junction(
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
        assert junction.junction_id == 1
        assert junction.street_name == "Main Street"
        assert junction.turn_direction == TurnDirection.LEFT

    def test_junction_to_dict(self, sample_junction):
        """Test converting junction to dictionary."""
        result = sample_junction.to_dict()
        assert result["junction_id"] == 1
        assert result["street_name"] == "Main Street"
        assert "coordinates" in result

    def test_junction_default_values(self, sample_coordinates):
        """Test junction default values."""
        junction = Junction(
            junction_id=1,
            address="Test",
            street_name="Test St",
            coordinates=sample_coordinates,
            turn_direction=TurnDirection.STRAIGHT,
            instruction="Go straight",
            distance_to_next_meters=100,
            distance_to_next_text="100 m",
            duration_to_next_seconds=30,
            duration_to_next_text="30 sec",
        )
        assert junction.cumulative_distance_meters == 0
        assert junction.cumulative_duration_seconds == 0
        assert junction.maneuver is None


class TestRoute:
    """Tests for Route dataclass."""

    def test_route_creation(self, sample_route):
        """Test creating a route."""
        assert sample_route.source_address == "Start Location, Tel Aviv"
        assert sample_route.destination_address == "End Location, Tel Aviv"
        assert sample_route.total_distance_meters == 1500

    def test_route_junction_count(self, sample_route):
        """Test junction count property."""
        assert sample_route.junction_count == 4

    def test_route_to_dict(self, sample_route):
        """Test converting route to dictionary."""
        result = sample_route.to_dict()
        assert result["source_address"] == "Start Location, Tel Aviv"
        assert "junctions" in result
        assert len(result["junctions"]) == 4

    def test_route_to_yaml_format(self, sample_route):
        """Test converting route to YAML format."""
        result = sample_route.to_yaml_format()
        # The actual implementation uses "Route" not "route"
        assert "Route" in result
        assert "waypoints" in result["Route"]

    def test_minimal_route(self, minimal_route):
        """Test minimal route with 2 junctions."""
        assert minimal_route.junction_count == 2
        assert minimal_route.total_distance_meters == 100
