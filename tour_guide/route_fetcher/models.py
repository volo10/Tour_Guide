"""
Data models for Route Fetcher module.

Defines the structure for routes, junctions, and API requests
that match the Tour Guide junction-based system requirements.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class TurnDirection(Enum):
    """Turn direction at a junction."""
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    STRAIGHT = "STRAIGHT"
    SLIGHT_LEFT = "SLIGHT_LEFT"
    SLIGHT_RIGHT = "SLIGHT_RIGHT"
    SHARP_LEFT = "SHARP_LEFT"
    SHARP_RIGHT = "SHARP_RIGHT"
    U_TURN = "U_TURN"
    MERGE = "MERGE"
    RAMP = "RAMP"
    FORK = "FORK"
    ROUNDABOUT = "ROUNDABOUT"
    DESTINATION = "DESTINATION"


@dataclass
class Coordinates:
    """GPS coordinates."""
    latitude: float
    longitude: float

    def to_list(self) -> List[float]:
        """Return coordinates as [lat, lng] list."""
        return [self.latitude, self.longitude]

    def to_string(self) -> str:
        """Return coordinates as 'lat,lng' string."""
        return f"{self.latitude},{self.longitude}"


@dataclass
class Junction:
    """
    Represents a single junction/intersection along a route.

    This is the primary data structure that will be passed to
    the Tour Guide agents for content discovery.
    """
    # Junction identification
    junction_id: int
    address: str  # e.g., "Main St & 5th Ave"
    street_name: str  # The street being turned onto

    # Location
    coordinates: Coordinates

    # Navigation details
    turn_direction: TurnDirection
    instruction: str  # Full navigation instruction from Google Maps

    # Distance and timing
    distance_to_next_meters: int
    distance_to_next_text: str  # e.g., "500 m" or "1.2 km"
    duration_to_next_seconds: int
    duration_to_next_text: str  # e.g., "2 mins"

    # Cumulative from start
    cumulative_distance_meters: int = 0
    cumulative_duration_seconds: int = 0

    # Additional context for agents
    maneuver: Optional[str] = None  # Google Maps maneuver type
    neighborhood: Optional[str] = None
    landmarks_nearby: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert junction to dictionary for JSON serialization."""
        return {
            "junction_id": self.junction_id,
            "address": self.address,
            "street_name": self.street_name,
            "coordinates": self.coordinates.to_list(),
            "turn": self.turn_direction.value,
            "instruction": self.instruction,
            "distance_to_next": self.distance_to_next_text,
            "distance_to_next_meters": self.distance_to_next_meters,
            "duration_to_next": self.duration_to_next_text,
            "duration_to_next_seconds": self.duration_to_next_seconds,
            "cumulative_distance_meters": self.cumulative_distance_meters,
            "cumulative_duration_seconds": self.cumulative_duration_seconds,
            "maneuver": self.maneuver,
            "neighborhood": self.neighborhood,
            "landmarks_nearby": self.landmarks_nearby,
        }


@dataclass
class Route:
    """
    Complete route with all junctions extracted.

    This is the output structure that will be passed to the
    module that coordinates the Tour Guide agents.
    """
    # Route identification
    source_address: str
    destination_address: str

    # Route summary
    total_distance_meters: int
    total_distance_text: str  # e.g., "8.5 km"
    total_duration_seconds: int
    total_duration_text: str  # e.g., "10 mins"

    # All junctions along the route
    junctions: List[Junction]

    # Route metadata
    polyline: Optional[str] = None  # Encoded polyline for map display
    bounds: Optional[dict] = None  # Northeast/Southwest bounds
    warnings: List[str] = field(default_factory=list)
    copyrights: Optional[str] = None

    @property
    def junction_count(self) -> int:
        """Number of junctions in the route."""
        return len(self.junctions)

    def to_dict(self) -> dict:
        """Convert route to dictionary for JSON serialization."""
        return {
            "source_address": self.source_address,
            "destination_address": self.destination_address,
            "total_distance": self.total_distance_text,
            "total_distance_meters": self.total_distance_meters,
            "total_duration": self.total_duration_text,
            "total_duration_seconds": self.total_duration_seconds,
            "junction_count": self.junction_count,
            "junctions": [j.to_dict() for j in self.junctions],
            "polyline": self.polyline,
            "bounds": self.bounds,
            "warnings": self.warnings,
            "copyrights": self.copyrights,
        }

    def to_yaml_format(self) -> dict:
        """
        Convert to the YAML format expected by Tour Guide agents.

        Matches the format in TOUR_GUIDE_JUNCTION_SYSTEM.md
        """
        waypoints = {}
        for junction in self.junctions:
            waypoints[f"junction_{junction.junction_id}"] = {
                "address": junction.address,
                "coordinates": junction.coordinates.to_list(),
                "turn": junction.turn_direction.value,
                "distance_to_next": junction.distance_to_next_text,
                "street_name": junction.street_name,
                "instruction": junction.instruction,
            }

        return {
            "Route": {
                "source": self.source_address,
                "destination": self.destination_address,
                "total_time": self.total_duration_text,
                "total_distance": self.total_distance_text,
                "waypoints": waypoints,
            }
        }


@dataclass
class RouteRequest:
    """Request parameters for fetching a route."""
    source: str  # Source address or coordinates
    destination: str  # Destination address or coordinates

    # Optional parameters
    waypoints: Optional[List[str]] = None  # Intermediate stops
    avoid: Optional[List[str]] = None  # e.g., ["tolls", "highways", "ferries"]
    departure_time: Optional[str] = None  # For traffic-aware routing
    alternatives: bool = False  # Request alternative routes
    units: str = "metric"  # "metric" or "imperial"
    language: str = "en"  # Response language

    def to_params(self) -> dict:
        """Convert to Google Maps API parameters."""
        params = {
            "origin": self.source,
            "destination": self.destination,
            "units": self.units,
            "language": self.language,
        }

        if self.waypoints:
            params["waypoints"] = "|".join(self.waypoints)

        if self.avoid:
            params["avoid"] = "|".join(self.avoid)

        if self.departure_time:
            params["departure_time"] = self.departure_time

        if self.alternatives:
            params["alternatives"] = "true"

        return params
