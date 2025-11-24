# User Guide

Guide for using the Tour Guide system.

## Installation

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

## Quick Start

### Python API

```python
from tour_guide import TourGuideAPI

api = TourGuideAPI(google_maps_api_key="YOUR_API_KEY")
result = api.get_tour(
    source="Tel Aviv Central Station",
    destination="Jaffa Port"
)

result.print_winners()
```

### Command Line

```bash
# Interactive mode
python -m tour_guide

# Or with arguments
tour-guide --source "Tel Aviv" --destination "Jerusalem"
```

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_MAPS_API_KEY` | Google Maps Directions API key |
| `YOUTUBE_API_KEY` | YouTube Data API key (optional) |
| `SPOTIFY_API_KEY` | Spotify API key (optional) |

### API Parameters

```python
TourGuideAPI(
    junction_interval_seconds=5.0,  # Time between junctions
    google_maps_api_key="...",      # Or use env var
)
```

## Usage Examples

### Basic Tour

```python
from tour_guide import TourGuideAPI

api = TourGuideAPI()
result = api.get_tour("Start Location", "End Location")

print(f"Total junctions: {result.total_junctions}")
print(f"Video wins: {result.video_wins}")
print(f"Music wins: {result.music_wins}")
print(f"History wins: {result.history_wins}")
```

### With Verbose Output

```python
result = api.get_tour(
    source="Tel Aviv",
    destination="Haifa",
    verbose=True  # Print progress
)
```

### Get JSON Output

```python
json_result = api.get_tour_json(
    source="Start",
    destination="End"
)
print(json_result)
```

### Using Individual Modules

#### Route Fetcher

```python
from tour_guide import RouteFetcher

fetcher = RouteFetcher(api_key="YOUR_KEY")
route = fetcher.fetch_route(
    source="Tel Aviv",
    destination="Jerusalem"
)

print(f"Route has {route.junction_count} junctions")
for junction in route.junctions:
    print(f"  {junction.junction_id}: {junction.street_name}")
```

#### Junction Orchestrator

```python
from tour_guide import JunctionOrchestrator

orchestrator = JunctionOrchestrator(
    junction_interval_seconds=10.0
)

@orchestrator.on_junction
def handle_junction(event):
    print(f"Junction {event.junction_index + 1}/{event.total_junctions}")
    print(f"  Street: {event.junction.street_name}")
    print(f"  Turn: {event.junction.turn_direction}")

orchestrator.start_from_addresses(
    source="Start",
    destination="End",
    blocking=True
)
```

#### Agent Orchestrator

```python
from tour_guide import AgentOrchestrator

orchestrator = AgentOrchestrator(
    junction_interval_seconds=5.0,
    agent_timeout_seconds=10.0
)

def on_junction_done(results):
    winner = results.judge_decision.winner
    print(f"Winner: {winner.agent_type.value} - {winner.title}")

orchestrator.on_junction_complete(on_junction_done)
report = orchestrator.start_from_addresses("Start", "End")
report.print_summary()
```

## Output Format

### TourGuideResult

```python
TourGuideResult(
    source="Start Location",
    destination="End Location",
    total_distance="15 km",
    total_duration="20 mins",
    winners=[
        JunctionWinner(
            junction_number=1,
            junction_address="Main St & 1st Ave",
            turn_direction="LEFT",
            winner_type="VIDEO",
            winner_title="City Tour Video",
            winner_description="...",
            winner_url="https://...",
            score=85.0
        ),
        # ... more winners
    ],
    total_junctions=5,
    video_wins=2,
    music_wins=2,
    history_wins=1,
    processing_time_seconds=25.0,
    success=True,
    error=None
)
```

### JSON Output

```json
{
  "source": "Start Location",
  "destination": "End Location",
  "total_distance": "15 km",
  "total_duration": "20 mins",
  "total_junctions": 5,
  "video_wins": 2,
  "music_wins": 2,
  "history_wins": 1,
  "winners": [
    {
      "junction_number": 1,
      "junction_address": "Main St & 1st Ave",
      "turn_direction": "LEFT",
      "winner_type": "VIDEO",
      "winner_title": "City Tour Video",
      "score": 85.0
    }
  ],
  "success": true
}
```

## Troubleshooting

### Common Issues

**No API Key Error**
```
GoogleMapsClientError: No API key provided
```
Solution: Set `GOOGLE_MAPS_API_KEY` environment variable or pass key directly.

**Route Not Found**
```
GoogleMapsClientError: ZERO_RESULTS
```
Solution: Verify addresses are valid and routable.

**Slow Processing**
- Reduce `junction_interval_seconds`
- Reduce `agent_timeout_seconds`

### Debug Mode

Enable verbose output to see processing details:

```python
result = api.get_tour(source, destination, verbose=True)
```
