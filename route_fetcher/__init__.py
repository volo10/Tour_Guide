"""
Route Fetcher Module for Tour Guide System

This module provides Google Maps integration to fetch routes between
source and destination addresses, extracting junctions/waypoints
for the Tour Guide agent system.
"""

from .models import Junction, Route, RouteRequest
from .google_maps_client import GoogleMapsClient
from .junction_extractor import JunctionExtractor
from .route_fetcher import RouteFetcher

__all__ = [
    "Junction",
    "Route",
    "RouteRequest",
    "GoogleMapsClient",
    "JunctionExtractor",
    "RouteFetcher",
]

__version__ = "1.0.0"
