"""
Unit tests for the user_api module.
"""

import pytest
import json

from tour_guide.user_api.tour_guide_api import TourGuideResult, JunctionWinner, TourGuideAPI


class TestJunctionWinner:
    """Tests for JunctionWinner dataclass."""

    def test_winner_creation(self):
        """Test creating a junction winner."""
        winner = JunctionWinner(
            junction_number=1,
            junction_address="Main St & 1st Ave",
            turn_direction="LEFT",
            winner_type="VIDEO",
            winner_title="Travel Guide Video",
            winner_description="A video about this location",
            winner_url="https://example.com/video",
            score=85.0,
        )
        assert winner.junction_number == 1
        assert winner.winner_type == "VIDEO"
        assert winner.score == 85.0

    def test_winner_optional_url(self):
        """Test winner with no URL."""
        winner = JunctionWinner(
            junction_number=1,
            junction_address="Main St",
            turn_direction="RIGHT",
            winner_type="HISTORY",
            winner_title="Historical Facts",
            winner_description="History of this area",
            winner_url=None,
            score=90.0,
        )
        assert winner.winner_url is None

    def test_winner_to_dict(self):
        """Test winner to_dict method."""
        winner = JunctionWinner(
            junction_number=1,
            junction_address="Main St",
            turn_direction="LEFT",
            winner_type="VIDEO",
            winner_title="Video Title",
            winner_description="Description",
            winner_url="https://example.com",
            score=85.0,
        )
        result = winner.to_dict()
        assert result["junction_number"] == 1
        assert result["winner_type"] == "VIDEO"


class TestTourGuideResult:
    """Tests for TourGuideResult dataclass."""

    def test_result_creation(self):
        """Test creating a tour guide result."""
        winners = [
            JunctionWinner(
                junction_number=1,
                junction_address="Start",
                turn_direction="STRAIGHT",
                winner_type="VIDEO",
                winner_title="Video 1",
                winner_description="Desc 1",
                winner_url=None,
                score=80.0,
            ),
        ]
        result = TourGuideResult(
            source="Start Location",
            destination="End Location",
            total_distance="10 km",
            total_duration="15 mins",
            winners=winners,
            total_junctions=5,
            video_wins=2,
            music_wins=2,
            history_wins=1,
            processing_time_seconds=5.5,
            success=True,
            error=None,
        )
        assert result.source == "Start Location"
        assert result.total_junctions == 5
        assert result.success is True

    def test_result_with_error(self):
        """Test result with error."""
        result = TourGuideResult(
            source="Start",
            destination="End",
            total_distance="",
            total_duration="",
            winners=[],
            total_junctions=0,
            video_wins=0,
            music_wins=0,
            history_wins=0,
            processing_time_seconds=0.0,
            success=False,
            error="Failed to fetch route",
        )
        assert result.success is False
        assert result.error == "Failed to fetch route"

    def test_to_dict(self):
        """Test converting to dictionary."""
        result = TourGuideResult(
            source="Start",
            destination="End",
            total_distance="5 km",
            total_duration="10 mins",
            winners=[],
            total_junctions=3,
            video_wins=1,
            music_wins=1,
            history_wins=1,
            processing_time_seconds=3.0,
            success=True,
            error=None,
        )
        data = result.to_dict()

        assert data["source"] == "Start"
        assert data["destination"] == "End"
        assert data["total_junctions"] == 3
        assert "winners" in data

    def test_to_json(self):
        """Test converting to JSON."""
        result = TourGuideResult(
            source="Start",
            destination="End",
            total_distance="5 km",
            total_duration="10 mins",
            winners=[],
            total_junctions=3,
            video_wins=1,
            music_wins=1,
            history_wins=1,
            processing_time_seconds=3.0,
            success=True,
            error=None,
        )
        json_str = result.to_json()

        # Should be valid JSON
        data = json.loads(json_str)
        assert data["source"] == "Start"

    def test_to_json_with_indent(self):
        """Test JSON with custom indent."""
        result = TourGuideResult(
            source="Start",
            destination="End",
            total_distance="5 km",
            total_duration="10 mins",
            winners=[],
            total_junctions=3,
            video_wins=1,
            music_wins=1,
            history_wins=1,
            processing_time_seconds=3.0,
            success=True,
            error=None,
        )
        json_str = result.to_json(indent=4)

        # Should have indentation (multiple lines)
        assert "\n" in json_str


class TestTourGuideAPI:
    """Tests for TourGuideAPI."""

    def test_api_creation(self):
        """Test creating the API."""
        api = TourGuideAPI(junction_interval_seconds=5.0)
        assert api is not None

    def test_api_default_interval(self):
        """Test default interval."""
        api = TourGuideAPI()
        # Default should be set
        assert api.junction_interval == 5.0

    def test_api_with_api_key(self):
        """Test API with Google Maps key."""
        api = TourGuideAPI(google_maps_api_key="test_key")
        assert api.api_key == "test_key"


class TestTourGuideResultPrinting:
    """Tests for result printing methods."""

    def test_print_winners_no_error(self, capsys):
        """Test print_winners when successful."""
        winners = [
            JunctionWinner(
                junction_number=1,
                junction_address="Main St",
                turn_direction="LEFT",
                winner_type="video",
                winner_title="Great Video",
                winner_description="A great video",
                winner_url="https://example.com",
                score=90.0,
            ),
        ]
        result = TourGuideResult(
            source="Start",
            destination="End",
            total_distance="5 km",
            total_duration="10 mins",
            winners=winners,
            total_junctions=1,
            video_wins=1,
            music_wins=0,
            history_wins=0,
            processing_time_seconds=1.0,
            success=True,
            error=None,
        )

        result.print_winners()
        captured = capsys.readouterr()

        # Should print something
        assert len(captured.out) > 0
        assert "Start" in captured.out
        assert "End" in captured.out
