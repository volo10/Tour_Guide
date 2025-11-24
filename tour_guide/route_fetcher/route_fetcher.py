"""
Main Route Fetcher Interface.

High-level API for fetching routes and extracting junctions
from Google Maps for the Tour Guide system.
"""

import json
import logging
from typing import Optional, List, Dict, Any

from .models import Route, RouteRequest
from .google_maps_client import GoogleMapsClient, GoogleMapsClientError
from .junction_extractor import JunctionExtractor

logger = logging.getLogger(__name__)


class RouteFetcher:
    """
    Main interface for fetching and processing routes.

    Combines Google Maps API client and junction extraction
    to provide route data ready for Tour Guide agents.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        include_straight_junctions: bool = True,
        min_junction_distance: int = 50,
    ):
        """
        Initialize the Route Fetcher.

        Args:
            api_key: Google Maps API key (or set GOOGLE_MAPS_API_KEY env var)
            include_straight_junctions: Include "go straight" junctions
            min_junction_distance: Minimum meters between junctions to include
        """
        self.client = GoogleMapsClient(api_key=api_key)
        self.extractor = JunctionExtractor(
            include_straight=include_straight_junctions,
            min_distance_meters=min_junction_distance,
        )

    def fetch_route(
        self,
        source: str,
        destination: str,
        waypoints: Optional[List[str]] = None,
        avoid: Optional[List[str]] = None,
        with_traffic: bool = False,
    ) -> Route:
        """
        Fetch a route and extract junctions.

        Args:
            source: Starting address or coordinates
            destination: Ending address or coordinates
            waypoints: Optional intermediate stops
            avoid: Features to avoid (tolls, highways, ferries)
            with_traffic: Use real-time traffic data

        Returns:
            Route object with all junctions

        Raises:
            GoogleMapsClientError: If API request fails
            ValueError: If response parsing fails
        """
        logger.info(f"Fetching route from '{source}' to '{destination}'")
        logger.debug(f"Options: waypoints={waypoints}, avoid={avoid}, traffic={with_traffic}")

        try:
            # Fetch route from Google Maps
            if with_traffic:
                api_response = self.client.get_route_with_traffic(
                    origin=source,
                    destination=destination,
                    waypoints=waypoints,
                    avoid=avoid,
                )
            else:
                api_response = self.client.get_route(
                    origin=source,
                    destination=destination,
                    waypoints=waypoints,
                    avoid=avoid,
                )

            # Extract junctions
            route = self.extractor.extract(api_response)

            logger.info(f"Route fetched successfully: {route.junction_count} junctions, "
                       f"{route.total_distance_text}, {route.total_duration_text}")

            # Log each junction ID for tracking
            junction_ids = [j.junction_id for j in route.junctions]
            logger.debug(f"Junction IDs: {junction_ids}")

            return route

        except Exception as e:
            logger.error(f"Failed to fetch route: {e}", exc_info=True)
            raise

    def fetch_route_from_request(self, request: RouteRequest) -> Route:
        """
        Fetch a route using a RouteRequest object.

        Args:
            request: RouteRequest with all parameters

        Returns:
            Route object with all junctions
        """
        return self.fetch_route(
            source=request.source,
            destination=request.destination,
            waypoints=request.waypoints,
            avoid=request.avoid,
        )

    def fetch_route_json(
        self,
        source: str,
        destination: str,
        **kwargs
    ) -> str:
        """
        Fetch a route and return as JSON string.

        Args:
            source: Starting address
            destination: Ending address
            **kwargs: Additional parameters for fetch_route

        Returns:
            JSON string of the route
        """
        route = self.fetch_route(source, destination, **kwargs)
        return json.dumps(route.to_dict(), indent=2)

    def fetch_route_for_agents(
        self,
        source: str,
        destination: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Fetch a route in the format expected by Tour Guide agents.

        Returns the YAML-compatible format from TOUR_GUIDE_JUNCTION_SYSTEM.md

        Args:
            source: Starting address
            destination: Ending address
            **kwargs: Additional parameters for fetch_route

        Returns:
            Dictionary in Tour Guide agent format
        """
        route = self.fetch_route(source, destination, **kwargs)
        return route.to_yaml_format()

    def validate_addresses(self, source: str, destination: str) -> Dict[str, Any]:
        """
        Validate that addresses can be geocoded and routed.

        Args:
            source: Starting address
            destination: Ending address

        Returns:
            Dictionary with validation results
        """
        result = {
            "source_valid": False,
            "destination_valid": False,
            "route_possible": False,
            "source_geocoded": None,
            "destination_geocoded": None,
            "error": None,
        }

        try:
            # Try to geocode source
            source_coords = self.client.geocode(source)
            result["source_valid"] = True
            result["source_geocoded"] = source_coords
        except GoogleMapsClientError as e:
            result["error"] = f"Source geocoding failed: {e}"
            return result

        try:
            # Try to geocode destination
            dest_coords = self.client.geocode(destination)
            result["destination_valid"] = True
            result["destination_geocoded"] = dest_coords
        except GoogleMapsClientError as e:
            result["error"] = f"Destination geocoding failed: {e}"
            return result

        try:
            # Try to get a route
            self.client.get_route(source, destination)
            result["route_possible"] = True
        except GoogleMapsClientError as e:
            result["error"] = f"Route not possible: {e}"

        return result


def main():
    """
    Command-line interface for the Route Fetcher.

    Usage:
        python -m route_fetcher.route_fetcher "Source Address" "Destination Address"
    """
    import sys

    if len(sys.argv) < 3:
        print("Usage: python -m route_fetcher.route_fetcher <source> <destination>")
        print()
        print("Example:")
        print('  python -m route_fetcher.route_fetcher "Tel Aviv" "Jerusalem"')
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]

    try:
        fetcher = RouteFetcher()
        route = fetcher.fetch_route(source, destination)

        print(f"\n{'='*60}")
        print(f"ROUTE: {route.source_address}")
        print(f"    -> {route.destination_address}")
        print(f"{'='*60}")
        print(f"Distance: {route.total_distance_text}")
        print(f"Duration: {route.total_duration_text}")
        print(f"Junctions: {route.junction_count}")
        print(f"{'='*60}\n")

        for junction in route.junctions:
            print(f"Junction {junction.junction_id}: {junction.address}")
            print(f"  Turn: {junction.turn_direction.value}")
            print(f"  Instruction: {junction.instruction}")
            print(f"  Distance to next: {junction.distance_to_next_text}")
            print(f"  Coordinates: {junction.coordinates.to_string()}")
            print()

    except GoogleMapsClientError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
