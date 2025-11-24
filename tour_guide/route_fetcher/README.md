# Route Fetcher Module

Google Maps integration module for the Tour Guide system. Fetches routes between addresses and extracts junction/waypoint data for the Tour Guide agents.

## Overview

This module provides:

1. **Google Maps API Client** - Communicates with Google Maps Directions API
2. **Junction Extractor** - Parses route data into structured junctions
3. **Route Fetcher** - High-level interface combining both components

## Output Format

The module outputs route data in the format expected by Tour Guide agents:

```yaml
Route:
  source: "Ramat HaSharon, Israel"
  destination: "Tel Aviv, Israel"
  total_time: "15 mins"
  total_distance: "8.5 km"
  waypoints:
    junction_1:
      address: "Jabotinsky St"
      coordinates: [32.1234, 34.5678]
      turn: "LEFT"
      distance_to_next: "500 m"
      street_name: "Jabotinsky St"
      instruction: "Turn left onto Jabotinsky St"
    junction_2:
      address: "Ayalon Highway"
      coordinates: [32.0987, 34.5432]
      turn: "MERGE"
      distance_to_next: "2.5 km"
      ...
```

## Quick Start

```python
from route_fetcher import RouteFetcher

# Initialize (reads GOOGLE_MAPS_API_KEY from environment)
fetcher = RouteFetcher()

# Fetch a route
route = fetcher.fetch_route(
    source="Ramat HaSharon, Israel",
    destination="Tel Aviv, Israel"
)

# Access route data
print(f"Distance: {route.total_distance_text}")
print(f"Duration: {route.total_duration_text}")
print(f"Junctions: {route.junction_count}")

# Iterate through junctions
for junction in route.junctions:
    print(f"{junction.junction_id}: {junction.turn_direction.value} onto {junction.street_name}")

# Get format for Tour Guide agents
agent_format = route.to_yaml_format()
```

## Installation

### 1. Set up Google Maps API Key

```bash
export GOOGLE_MAPS_API_KEY="your-api-key-here"
```

Or pass directly:

```python
fetcher = RouteFetcher(api_key="your-api-key-here")
```

### 2. Getting a Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the **Directions API**
4. Create credentials (API Key)
5. (Recommended) Restrict the key to Directions API only

## API Reference

### RouteFetcher

Main interface for fetching routes.

```python
RouteFetcher(
    api_key: str = None,           # API key (or use env var)
    include_straight_junctions: bool = True,  # Include "go straight" turns
    min_junction_distance: int = 50,          # Min meters between junctions
)
```

#### Methods

**`fetch_route(source, destination, waypoints=None, avoid=None, with_traffic=False)`**

Fetch a route and return a `Route` object.

```python
route = fetcher.fetch_route(
    source="Tel Aviv",
    destination="Jerusalem",
    avoid=["tolls"],          # Avoid tolls
    with_traffic=True         # Use real-time traffic
)
```

**`fetch_route_for_agents(source, destination, **kwargs)`**

Get route in Tour Guide agent format.

```python
agent_data = fetcher.fetch_route_for_agents("Tel Aviv", "Jerusalem")
# Returns dict matching TOUR_GUIDE_JUNCTION_SYSTEM.md format
```

**`fetch_route_json(source, destination, **kwargs)`**

Get route as JSON string.

```python
json_str = fetcher.fetch_route_json("Tel Aviv", "Jerusalem")
```

**`validate_addresses(source, destination)`**

Check if addresses are valid and routable.

```python
result = fetcher.validate_addresses("Tel Aviv", "Jerusalem")
if result["route_possible"]:
    print("Route is valid!")
```

### Route

Represents a complete route.

```python
route.source_address          # Starting address
route.destination_address     # Ending address
route.total_distance_text     # e.g., "8.5 km"
route.total_duration_text     # e.g., "15 mins"
route.junctions              # List of Junction objects
route.junction_count         # Number of junctions

route.to_dict()              # Convert to dictionary
route.to_yaml_format()       # Convert to Tour Guide agent format
```

### Junction

Represents a single junction/intersection.

```python
junction.junction_id          # Sequential ID
junction.address             # Junction address
junction.street_name         # Street being turned onto
junction.coordinates         # Coordinates object (lat, lng)
junction.turn_direction      # TurnDirection enum
junction.instruction         # Full navigation instruction
junction.distance_to_next_text    # e.g., "500 m"
junction.duration_to_next_text    # e.g., "2 mins"
junction.maneuver            # Google Maps maneuver type

junction.to_dict()           # Convert to dictionary
```

### TurnDirection

Enum for turn types:

- `LEFT`, `RIGHT`, `STRAIGHT`
- `SLIGHT_LEFT`, `SLIGHT_RIGHT`
- `SHARP_LEFT`, `SHARP_RIGHT`
- `U_TURN`, `MERGE`, `RAMP`, `FORK`
- `ROUNDABOUT`, `DESTINATION`

## Command Line Usage

```bash
cd /path/to/Tour_Guide
python -m route_fetcher.route_fetcher "Tel Aviv" "Jerusalem"
```

Output:
```
============================================================
ROUTE: Tel Aviv, Israel
    -> Jerusalem, Israel
============================================================
Distance: 62.5 km
Duration: 55 mins
Junctions: 12
============================================================

Junction 1: Ayalon Highway
  Turn: MERGE
  Instruction: Merge onto Ayalon Highway
  Distance to next: 5.2 km
  Coordinates: 32.0853,34.7818
...
```

## Integration with Tour Guide Agents

The route data flows to agents like this:

```
┌─────────────────┐
│  Route Fetcher  │
│  (This Module)  │
└────────┬────────┘
         │
         ▼ Route with Junctions
┌─────────────────┐
│  Agent Router   │  ← Your next module
│  (To be built)  │
└────────┬────────┘
         │
    ┌────┴────┬─────────┬──────────┐
    ▼         ▼         ▼          ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│ Video │ │ Music │ │History│ │ Judge │
│Finder │ │Finder │ │Finder │ │       │
└───────┘ └───────┘ └───────┘ └───────┘
```

## Error Handling

```python
from route_fetcher import RouteFetcher
from route_fetcher.google_maps_client import GoogleMapsClientError

try:
    fetcher = RouteFetcher()
    route = fetcher.fetch_route("Invalid Address XYZ", "Nowhere")
except GoogleMapsClientError as e:
    print(f"API Error: {e}")
```

## Files

```
route_fetcher/
├── __init__.py              # Module exports
├── models.py                # Data models (Route, Junction, etc.)
├── google_maps_client.py    # Google Maps API client
├── junction_extractor.py    # Route parsing logic
├── route_fetcher.py         # Main interface
└── README.md                # This file
```

## Requirements

- Python 3.7+
- Google Maps API key with Directions API enabled
- No external dependencies (uses only standard library)

## Version

1.0.0 - Initial release
