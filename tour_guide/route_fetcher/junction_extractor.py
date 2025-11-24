"""
Junction Extractor for Route Data.

Parses Google Maps API response and extracts junction/waypoint
information in the format required by Tour Guide agents.
"""

import re
from typing import Dict, Any, List, Optional
from .models import Junction, Route, Coordinates, TurnDirection


class JunctionExtractor:
    """
    Extracts junctions from Google Maps Directions API response.

    Converts raw API data into structured Junction and Route objects
    that can be consumed by the Tour Guide agent system.
    """

    # Mapping from Google Maps maneuver types to TurnDirection
    MANEUVER_MAP = {
        "turn-left": TurnDirection.LEFT,
        "turn-right": TurnDirection.RIGHT,
        "turn-slight-left": TurnDirection.SLIGHT_LEFT,
        "turn-slight-right": TurnDirection.SLIGHT_RIGHT,
        "turn-sharp-left": TurnDirection.SHARP_LEFT,
        "turn-sharp-right": TurnDirection.SHARP_RIGHT,
        "uturn-left": TurnDirection.U_TURN,
        "uturn-right": TurnDirection.U_TURN,
        "straight": TurnDirection.STRAIGHT,
        "merge": TurnDirection.MERGE,
        "ramp-left": TurnDirection.RAMP,
        "ramp-right": TurnDirection.RAMP,
        "fork-left": TurnDirection.FORK,
        "fork-right": TurnDirection.FORK,
        "roundabout-left": TurnDirection.ROUNDABOUT,
        "roundabout-right": TurnDirection.ROUNDABOUT,
        "keep-left": TurnDirection.SLIGHT_LEFT,
        "keep-right": TurnDirection.SLIGHT_RIGHT,
    }

    def __init__(self, include_straight: bool = True, min_distance_meters: int = 50):
        """
        Initialize the junction extractor.

        Args:
            include_straight: Whether to include "go straight" junctions
            min_distance_meters: Minimum distance between junctions to include
        """
        self.include_straight = include_straight
        self.min_distance_meters = min_distance_meters

    def extract(self, api_response: Dict[str, Any]) -> Route:
        """
        Extract route and junctions from Google Maps API response.

        Args:
            api_response: Raw response from Google Maps Directions API

        Returns:
            Route object with all extracted junctions

        Raises:
            ValueError: If response doesn't contain valid route data
        """
        if not api_response.get("routes"):
            raise ValueError("No routes found in API response")

        route_data = api_response["routes"][0]
        leg = route_data["legs"][0]

        # Extract junctions from steps
        junctions = self._extract_junctions(leg["steps"])

        # Build route object
        route = Route(
            source_address=leg["start_address"],
            destination_address=leg["end_address"],
            total_distance_meters=leg["distance"]["value"],
            total_distance_text=leg["distance"]["text"],
            total_duration_seconds=leg["duration"]["value"],
            total_duration_text=leg["duration"]["text"],
            junctions=junctions,
            polyline=route_data.get("overview_polyline", {}).get("points"),
            bounds=route_data.get("bounds"),
            warnings=route_data.get("warnings", []),
            copyrights=route_data.get("copyrights"),
        )

        return route

    def _extract_junctions(self, steps: List[Dict[str, Any]]) -> List[Junction]:
        """
        Extract junctions from route steps.

        Args:
            steps: List of step objects from Google Maps API

        Returns:
            List of Junction objects
        """
        junctions = []
        cumulative_distance = 0
        cumulative_duration = 0
        junction_id = 1

        for i, step in enumerate(steps):
            # Get maneuver type (if available)
            maneuver = step.get("maneuver", "")

            # Determine turn direction
            turn_direction = self._get_turn_direction(maneuver, step)

            # Skip straight segments if not including them
            if not self.include_straight and turn_direction == TurnDirection.STRAIGHT:
                cumulative_distance += step["distance"]["value"]
                cumulative_duration += step["duration"]["value"]
                continue

            # Skip very short segments
            if step["distance"]["value"] < self.min_distance_meters and i < len(steps) - 1:
                cumulative_distance += step["distance"]["value"]
                cumulative_duration += step["duration"]["value"]
                continue

            # Extract street name from instruction
            instruction = self._clean_html(step.get("html_instructions", ""))
            street_name = self._extract_street_name(instruction, step)

            # Build junction address
            address = self._build_junction_address(step, street_name)

            # Get coordinates
            start_location = step["start_location"]
            coordinates = Coordinates(
                latitude=start_location["lat"],
                longitude=start_location["lng"]
            )

            # Calculate distance/duration to next junction
            distance_to_next = step["distance"]["value"]
            duration_to_next = step["duration"]["value"]

            # Create junction
            junction = Junction(
                junction_id=junction_id,
                address=address,
                street_name=street_name,
                coordinates=coordinates,
                turn_direction=turn_direction,
                instruction=instruction,
                distance_to_next_meters=distance_to_next,
                distance_to_next_text=step["distance"]["text"],
                duration_to_next_seconds=duration_to_next,
                duration_to_next_text=step["duration"]["text"],
                cumulative_distance_meters=cumulative_distance,
                cumulative_duration_seconds=cumulative_duration,
                maneuver=maneuver or None,
            )

            junctions.append(junction)
            junction_id += 1

            # Update cumulative counters
            cumulative_distance += distance_to_next
            cumulative_duration += duration_to_next

        # Add destination as final junction
        if steps:
            last_step = steps[-1]
            end_location = last_step["end_location"]

            destination_junction = Junction(
                junction_id=junction_id,
                address="Destination",
                street_name="Destination",
                coordinates=Coordinates(
                    latitude=end_location["lat"],
                    longitude=end_location["lng"]
                ),
                turn_direction=TurnDirection.DESTINATION,
                instruction="Arrive at destination",
                distance_to_next_meters=0,
                distance_to_next_text="0 m",
                duration_to_next_seconds=0,
                duration_to_next_text="0 mins",
                cumulative_distance_meters=cumulative_distance,
                cumulative_duration_seconds=cumulative_duration,
                maneuver="destination",
            )
            junctions.append(destination_junction)

        return junctions

    def _get_turn_direction(
        self,
        maneuver: str,
        step: Dict[str, Any]
    ) -> TurnDirection:
        """
        Determine turn direction from maneuver and step data.

        Args:
            maneuver: Google Maps maneuver type
            step: Step data from API

        Returns:
            TurnDirection enum value
        """
        # Try direct maneuver mapping
        if maneuver in self.MANEUVER_MAP:
            return self.MANEUVER_MAP[maneuver]

        # Parse from instruction text
        instruction = step.get("html_instructions", "").lower()

        if "turn left" in instruction or "left onto" in instruction:
            return TurnDirection.LEFT
        elif "turn right" in instruction or "right onto" in instruction:
            return TurnDirection.RIGHT
        elif "slight left" in instruction:
            return TurnDirection.SLIGHT_LEFT
        elif "slight right" in instruction:
            return TurnDirection.SLIGHT_RIGHT
        elif "sharp left" in instruction:
            return TurnDirection.SHARP_LEFT
        elif "sharp right" in instruction:
            return TurnDirection.SHARP_RIGHT
        elif "u-turn" in instruction:
            return TurnDirection.U_TURN
        elif "merge" in instruction:
            return TurnDirection.MERGE
        elif "roundabout" in instruction or "rotary" in instruction:
            return TurnDirection.ROUNDABOUT
        elif "ramp" in instruction:
            return TurnDirection.RAMP

        return TurnDirection.STRAIGHT

    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags from instruction text."""
        clean = re.sub(r'<[^>]+>', ' ', html_text)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()

    def _extract_street_name(
        self,
        instruction: str,
        step: Dict[str, Any]
    ) -> str:
        """
        Extract street name from instruction or step data.

        Args:
            instruction: Cleaned instruction text
            step: Step data from API

        Returns:
            Street name string
        """
        # Common patterns for street name extraction
        patterns = [
            r"onto (.+?)(?:\s*$|(?:toward|Destination))",
            r"on (.+?)(?:\s*$|(?:toward|Destination))",
            r"(?:Continue|Head|Go) (?:on|along) (.+?)(?:\s*$)",
            r"(?:Turn|Keep|Slight|Sharp) (?:left|right) (?:onto|on) (.+?)(?:\s*$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, instruction, re.IGNORECASE)
            if match:
                street = match.group(1).strip()
                # Clean up common suffixes
                street = re.sub(r'\s*toward\s+.+$', '', street)
                street = re.sub(r'\s*Pass by.+$', '', street)
                if street:
                    return street

        # Fallback: use the first reasonable segment
        words = instruction.split()
        if len(words) >= 3:
            return " ".join(words[-3:])

        return "Unknown Street"

    def _build_junction_address(
        self,
        step: Dict[str, Any],
        street_name: str
    ) -> str:
        """
        Build a descriptive junction address.

        Args:
            step: Step data from API
            street_name: Extracted street name

        Returns:
            Junction address string (e.g., "Main St & 5th Ave")
        """
        # For now, use the street name as the address
        # In a more advanced implementation, we could:
        # - Reverse geocode to get cross-street
        # - Use nearby landmarks
        # - Parse from instruction text

        return street_name
