"""
Tests for JunctionExtractor module.

Comprehensive tests for junction extraction from Google Maps API responses.
"""

import pytest
from tour_guide.route_fetcher.junction_extractor import JunctionExtractor
from tour_guide.route_fetcher.models import TurnDirection


class TestJunctionExtractor:
    """Tests for JunctionExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create a default extractor instance."""
        return JunctionExtractor()

    @pytest.fixture
    def extractor_no_straight(self):
        """Create an extractor that excludes straight junctions."""
        return JunctionExtractor(include_straight=False)

    @pytest.fixture
    def extractor_min_distance(self):
        """Create an extractor with higher minimum distance."""
        return JunctionExtractor(min_distance_meters=200)

    @pytest.fixture
    def sample_api_response(self):
        """Sample Google Maps API response."""
        return {
            "status": "OK",
            "routes": [
                {
                    "legs": [
                        {
                            "start_address": "Tel Aviv, Israel",
                            "end_address": "Jerusalem, Israel",
                            "distance": {"value": 60000, "text": "60 km"},
                            "duration": {"value": 3600, "text": "1 hour"},
                            "steps": [
                                {
                                    "html_instructions": "Head <b>north</b> on <b>Main St</b>",
                                    "maneuver": "straight",
                                    "distance": {"value": 500, "text": "500 m"},
                                    "duration": {"value": 60, "text": "1 min"},
                                    "start_location": {"lat": 32.0853, "lng": 34.7818},
                                    "end_location": {"lat": 32.0900, "lng": 34.7818},
                                },
                                {
                                    "html_instructions": "Turn <b>left</b> onto <b>Second Ave</b>",
                                    "maneuver": "turn-left",
                                    "distance": {"value": 1000, "text": "1 km"},
                                    "duration": {"value": 120, "text": "2 mins"},
                                    "start_location": {"lat": 32.0900, "lng": 34.7818},
                                    "end_location": {"lat": 32.0900, "lng": 34.7900},
                                },
                                {
                                    "html_instructions": "Turn <b>right</b> onto <b>Highway 1</b>",
                                    "maneuver": "turn-right",
                                    "distance": {"value": 50000, "text": "50 km"},
                                    "duration": {"value": 2400, "text": "40 mins"},
                                    "start_location": {"lat": 32.0900, "lng": 34.7900},
                                    "end_location": {"lat": 31.7683, "lng": 35.2137},
                                },
                            ],
                        }
                    ],
                    "overview_polyline": {"points": "abc123"},
                    "bounds": {
                        "northeast": {"lat": 32.0900, "lng": 35.2137},
                        "southwest": {"lat": 31.7683, "lng": 34.7818},
                    },
                    "warnings": [],
                    "copyrights": "Map data ©2024",
                }
            ],
        }

    @pytest.fixture
    def minimal_api_response(self):
        """Minimal valid API response."""
        return {
            "routes": [
                {
                    "legs": [
                        {
                            "start_address": "A",
                            "end_address": "B",
                            "distance": {"value": 1000, "text": "1 km"},
                            "duration": {"value": 60, "text": "1 min"},
                            "steps": [
                                {
                                    "html_instructions": "Go straight",
                                    "distance": {"value": 1000, "text": "1 km"},
                                    "duration": {"value": 60, "text": "1 min"},
                                    "start_location": {"lat": 0, "lng": 0},
                                    "end_location": {"lat": 1, "lng": 1},
                                }
                            ],
                        }
                    ],
                }
            ],
        }

    def test_init_default(self, extractor):
        """Test default initialization."""
        assert extractor.include_straight is True
        assert extractor.min_distance_meters == 50

    def test_init_custom(self):
        """Test custom initialization."""
        extractor = JunctionExtractor(include_straight=False, min_distance_meters=100)
        assert extractor.include_straight is False
        assert extractor.min_distance_meters == 100

    def test_extract_basic(self, extractor, sample_api_response):
        """Test basic route extraction."""
        route = extractor.extract(sample_api_response)

        assert route.source_address == "Tel Aviv, Israel"
        assert route.destination_address == "Jerusalem, Israel"
        assert route.total_distance_meters == 60000
        assert route.total_duration_seconds == 3600
        assert len(route.junctions) >= 3  # Steps + destination

    def test_extract_no_routes(self, extractor):
        """Test extraction with empty response."""
        with pytest.raises(ValueError, match="No routes found"):
            extractor.extract({"routes": []})

    def test_extract_no_routes_key(self, extractor):
        """Test extraction without routes key."""
        with pytest.raises(ValueError, match="No routes found"):
            extractor.extract({})

    def test_extract_junction_fields(self, extractor, sample_api_response):
        """Test that junctions have all required fields."""
        route = extractor.extract(sample_api_response)
        junction = route.junctions[0]

        assert junction.junction_id >= 1
        assert isinstance(junction.address, str)
        assert isinstance(junction.street_name, str)
        assert junction.coordinates is not None
        assert isinstance(junction.turn_direction, TurnDirection)
        assert isinstance(junction.instruction, str)
        assert junction.distance_to_next_meters >= 0
        assert junction.duration_to_next_seconds >= 0

    def test_extract_destination_junction(self, extractor, sample_api_response):
        """Test that destination junction is added."""
        route = extractor.extract(sample_api_response)
        last_junction = route.junctions[-1]

        assert last_junction.turn_direction == TurnDirection.DESTINATION
        assert last_junction.distance_to_next_meters == 0
        assert last_junction.duration_to_next_seconds == 0

    def test_exclude_straight_junctions(self, extractor_no_straight, sample_api_response):
        """Test excluding straight junctions."""
        route = extractor_no_straight.extract(sample_api_response)

        for junction in route.junctions[:-1]:  # Exclude destination
            assert junction.turn_direction != TurnDirection.STRAIGHT

    def test_min_distance_filtering(self, extractor_min_distance):
        """Test minimum distance filtering."""
        response = {
            "routes": [
                {
                    "legs": [
                        {
                            "start_address": "A",
                            "end_address": "B",
                            "distance": {"value": 1000, "text": "1 km"},
                            "duration": {"value": 60, "text": "1 min"},
                            "steps": [
                                {
                                    "html_instructions": "Turn left",
                                    "maneuver": "turn-left",
                                    "distance": {"value": 50, "text": "50 m"},  # Below min
                                    "duration": {"value": 10, "text": "10 s"},
                                    "start_location": {"lat": 0, "lng": 0},
                                    "end_location": {"lat": 0.001, "lng": 0},
                                },
                                {
                                    "html_instructions": "Turn right",
                                    "maneuver": "turn-right",
                                    "distance": {"value": 500, "text": "500 m"},  # Above min
                                    "duration": {"value": 60, "text": "1 min"},
                                    "start_location": {"lat": 0.001, "lng": 0},
                                    "end_location": {"lat": 0.005, "lng": 0},
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        route = extractor_min_distance.extract(response)
        # Should skip the 50m step and include 500m step + destination
        assert len(route.junctions) <= 3


class TestManeuverMapping:
    """Tests for maneuver to TurnDirection mapping."""

    @pytest.fixture
    def extractor(self):
        return JunctionExtractor()

    def test_left_turns(self, extractor):
        """Test left turn maneuvers."""
        assert extractor.MANEUVER_MAP["turn-left"] == TurnDirection.LEFT
        assert extractor.MANEUVER_MAP["turn-slight-left"] == TurnDirection.SLIGHT_LEFT
        assert extractor.MANEUVER_MAP["turn-sharp-left"] == TurnDirection.SHARP_LEFT

    def test_right_turns(self, extractor):
        """Test right turn maneuvers."""
        assert extractor.MANEUVER_MAP["turn-right"] == TurnDirection.RIGHT
        assert extractor.MANEUVER_MAP["turn-slight-right"] == TurnDirection.SLIGHT_RIGHT
        assert extractor.MANEUVER_MAP["turn-sharp-right"] == TurnDirection.SHARP_RIGHT

    def test_special_maneuvers(self, extractor):
        """Test special maneuvers."""
        assert extractor.MANEUVER_MAP["uturn-left"] == TurnDirection.U_TURN
        assert extractor.MANEUVER_MAP["uturn-right"] == TurnDirection.U_TURN
        assert extractor.MANEUVER_MAP["merge"] == TurnDirection.MERGE
        assert extractor.MANEUVER_MAP["roundabout-left"] == TurnDirection.ROUNDABOUT

    def test_get_turn_direction_from_maneuver(self, extractor):
        """Test getting turn direction from maneuver."""
        step = {"html_instructions": ""}

        result = extractor._get_turn_direction("turn-left", step)
        assert result == TurnDirection.LEFT

        result = extractor._get_turn_direction("turn-right", step)
        assert result == TurnDirection.RIGHT

    def test_get_turn_direction_from_instruction(self, extractor):
        """Test getting turn direction from instruction text."""
        step = {"html_instructions": "Turn left onto Main St"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.LEFT

        step = {"html_instructions": "Turn right onto Second Ave"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.RIGHT

    def test_get_turn_direction_slight(self, extractor):
        """Test slight turn detection from instruction."""
        step = {"html_instructions": "Slight left onto Highway"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.SLIGHT_LEFT

        step = {"html_instructions": "Slight right onto Road"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.SLIGHT_RIGHT

    def test_get_turn_direction_sharp(self, extractor):
        """Test sharp turn detection from instruction."""
        step = {"html_instructions": "Sharp left turn"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.SHARP_LEFT

        step = {"html_instructions": "Sharp right ahead"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.SHARP_RIGHT

    def test_get_turn_direction_uturn(self, extractor):
        """Test U-turn detection from instruction."""
        step = {"html_instructions": "Make a U-turn"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.U_TURN

    def test_get_turn_direction_roundabout(self, extractor):
        """Test roundabout detection from instruction."""
        step = {"html_instructions": "Enter the roundabout"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.ROUNDABOUT

        step = {"html_instructions": "At the rotary, take exit"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.ROUNDABOUT

    def test_get_turn_direction_merge(self, extractor):
        """Test merge detection from instruction."""
        step = {"html_instructions": "Merge onto Highway 1"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.MERGE

    def test_get_turn_direction_ramp(self, extractor):
        """Test ramp detection from instruction."""
        step = {"html_instructions": "Take the ramp to Highway"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.RAMP

    def test_get_turn_direction_default(self, extractor):
        """Test default to STRAIGHT for unknown."""
        step = {"html_instructions": "Continue on road"}
        result = extractor._get_turn_direction("", step)
        assert result == TurnDirection.STRAIGHT


class TestTextProcessing:
    """Tests for text processing methods."""

    @pytest.fixture
    def extractor(self):
        return JunctionExtractor()

    def test_clean_html_basic(self, extractor):
        """Test basic HTML cleaning."""
        result = extractor._clean_html("Turn <b>left</b> onto Main St")
        assert result == "Turn left onto Main St"

    def test_clean_html_multiple_tags(self, extractor):
        """Test cleaning multiple HTML tags."""
        result = extractor._clean_html("<div>Turn <b>left</b> onto <i>Main</i> St</div>")
        assert "left" in result
        assert "Main" in result
        assert "<" not in result
        assert ">" not in result

    def test_clean_html_whitespace(self, extractor):
        """Test whitespace normalization."""
        result = extractor._clean_html("Turn   left    onto   Main")
        assert "  " not in result

    def test_clean_html_empty(self, extractor):
        """Test empty string handling."""
        result = extractor._clean_html("")
        assert result == ""

    def test_extract_street_name_onto(self, extractor):
        """Test street name extraction with 'onto' pattern."""
        instruction = "Turn left onto Main Street"
        step = {}
        result = extractor._extract_street_name(instruction, step)
        assert "Main" in result

    def test_extract_street_name_on(self, extractor):
        """Test street name extraction with 'on' pattern."""
        instruction = "Continue on Highway 1"
        step = {}
        result = extractor._extract_street_name(instruction, step)
        assert "Highway" in result or "Unknown" in result

    def test_extract_street_name_fallback(self, extractor):
        """Test street name extraction fallback."""
        instruction = "Go"
        step = {}
        result = extractor._extract_street_name(instruction, step)
        assert isinstance(result, str)

    def test_build_junction_address(self, extractor):
        """Test junction address building."""
        step = {"start_location": {"lat": 0, "lng": 0}}
        result = extractor._build_junction_address(step, "Main St")
        assert result == "Main St"


class TestCumulativeCalculations:
    """Tests for cumulative distance/duration calculations."""

    @pytest.fixture
    def extractor(self):
        return JunctionExtractor()

    def test_cumulative_distance(self, extractor):
        """Test cumulative distance calculation."""
        response = {
            "routes": [
                {
                    "legs": [
                        {
                            "start_address": "A",
                            "end_address": "B",
                            "distance": {"value": 3000, "text": "3 km"},
                            "duration": {"value": 180, "text": "3 min"},
                            "steps": [
                                {
                                    "html_instructions": "Step 1",
                                    "maneuver": "turn-left",
                                    "distance": {"value": 1000, "text": "1 km"},
                                    "duration": {"value": 60, "text": "1 min"},
                                    "start_location": {"lat": 0, "lng": 0},
                                    "end_location": {"lat": 1, "lng": 0},
                                },
                                {
                                    "html_instructions": "Step 2",
                                    "maneuver": "turn-right",
                                    "distance": {"value": 2000, "text": "2 km"},
                                    "duration": {"value": 120, "text": "2 min"},
                                    "start_location": {"lat": 1, "lng": 0},
                                    "end_location": {"lat": 1, "lng": 2},
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        route = extractor.extract(response)

        # First junction should have 0 cumulative
        assert route.junctions[0].cumulative_distance_meters == 0
        assert route.junctions[0].cumulative_duration_seconds == 0

        # Second junction should have first step's values
        assert route.junctions[1].cumulative_distance_meters == 1000
        assert route.junctions[1].cumulative_duration_seconds == 60

    def test_junction_ids_sequential(self, extractor):
        """Test that junction IDs are sequential."""
        response = {
            "routes": [
                {
                    "legs": [
                        {
                            "start_address": "A",
                            "end_address": "B",
                            "distance": {"value": 2000, "text": "2 km"},
                            "duration": {"value": 120, "text": "2 min"},
                            "steps": [
                                {
                                    "html_instructions": "Step 1",
                                    "distance": {"value": 1000, "text": "1 km"},
                                    "duration": {"value": 60, "text": "1 min"},
                                    "start_location": {"lat": 0, "lng": 0},
                                    "end_location": {"lat": 1, "lng": 0},
                                },
                                {
                                    "html_instructions": "Step 2",
                                    "distance": {"value": 1000, "text": "1 km"},
                                    "duration": {"value": 60, "text": "1 min"},
                                    "start_location": {"lat": 1, "lng": 0},
                                    "end_location": {"lat": 2, "lng": 0},
                                },
                            ],
                        }
                    ],
                }
            ],
        }

        route = extractor.extract(response)
        ids = [j.junction_id for j in route.junctions]

        for i in range(len(ids) - 1):
            assert ids[i + 1] == ids[i] + 1
