"""
Google Maps API Client for Route Fetching.

Handles communication with Google Maps Directions API
to retrieve route data between addresses.
"""

import os
import json
import urllib.request
import urllib.parse
import urllib.error
from typing import Optional, Dict, Any, List


class GoogleMapsClientError(Exception):
    """Custom exception for Google Maps API errors."""
    pass


class GoogleMapsClient:
    """
    Client for Google Maps Directions API.

    Fetches route data including turn-by-turn directions,
    distances, durations, and waypoint coordinates.
    """

    BASE_URL = "https://maps.googleapis.com/maps/api/directions/json"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google Maps client.

        Args:
            api_key: Google Maps API key. If not provided,
                    reads from GOOGLE_MAPS_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")

        if not self.api_key:
            raise GoogleMapsClientError(
                "Google Maps API key not provided. "
                "Set GOOGLE_MAPS_API_KEY environment variable or pass api_key parameter."
            )

    def get_route(
        self,
        origin: str,
        destination: str,
        waypoints: Optional[List[str]] = None,
        avoid: Optional[List[str]] = None,
        departure_time: Optional[str] = None,
        alternatives: bool = False,
        units: str = "metric",
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Fetch route from Google Maps Directions API.

        Args:
            origin: Starting address or coordinates (lat,lng)
            destination: Ending address or coordinates (lat,lng)
            waypoints: Optional list of intermediate stops
            avoid: Optional list of features to avoid (tolls, highways, ferries)
            departure_time: Optional departure time for traffic-aware routing
            alternatives: Whether to request alternative routes
            units: "metric" or "imperial"
            language: Response language code

        Returns:
            Raw API response as dictionary

        Raises:
            GoogleMapsClientError: If API request fails
        """
        params = {
            "origin": origin,
            "destination": destination,
            "key": self.api_key,
            "units": units,
            "language": language,
        }

        if waypoints:
            params["waypoints"] = "|".join(waypoints)

        if avoid:
            params["avoid"] = "|".join(avoid)

        if departure_time:
            params["departure_time"] = departure_time

        if alternatives:
            params["alternatives"] = "true"

        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as e:
            raise GoogleMapsClientError(f"Network error: {e}")
        except urllib.error.HTTPError as e:
            raise GoogleMapsClientError(f"HTTP error {e.code}: {e.reason}")
        except json.JSONDecodeError as e:
            raise GoogleMapsClientError(f"Invalid JSON response: {e}")

        # Check API response status
        status = data.get("status", "UNKNOWN")

        if status != "OK":
            error_message = data.get("error_message", "Unknown error")
            raise GoogleMapsClientError(
                f"Google Maps API error: {status} - {error_message}"
            )

        return data

    def get_route_with_traffic(
        self,
        origin: str,
        destination: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch route with real-time traffic data.

        Automatically sets departure_time to "now" for traffic-aware routing.

        Args:
            origin: Starting address or coordinates
            destination: Ending address or coordinates
            **kwargs: Additional parameters passed to get_route

        Returns:
            Raw API response with traffic data
        """
        return self.get_route(
            origin=origin,
            destination=destination,
            departure_time="now",
            **kwargs
        )

    def geocode(self, address: str) -> Dict[str, float]:
        """
        Geocode an address to coordinates.

        Uses the Directions API response to extract coordinates.

        Args:
            address: Address to geocode

        Returns:
            Dictionary with 'lat' and 'lng' keys
        """
        # Use a simple route to self to get geocoded location
        data = self.get_route(address, address)

        if data.get("routes"):
            location = data["routes"][0]["legs"][0]["start_location"]
            return {"lat": location["lat"], "lng": location["lng"]}

        raise GoogleMapsClientError(f"Could not geocode address: {address}")

    def validate_api_key(self) -> bool:
        """
        Validate that the API key is working.

        Returns:
            True if API key is valid

        Raises:
            GoogleMapsClientError: If API key is invalid
        """
        try:
            # Make a simple request to validate the key
            self.get_route("New York, NY", "New York, NY")
            return True
        except GoogleMapsClientError as e:
            if "REQUEST_DENIED" in str(e) or "INVALID" in str(e):
                raise GoogleMapsClientError("Invalid API key")
            raise
