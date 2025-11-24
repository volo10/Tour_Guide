# User API Module

User-friendly interfaces for the Tour Guide system. Provides CLI, Python API, and REST API.

## Quick Start

### Command Line

```bash
# Simple usage
python -m user_api.cli "Tel Aviv" "Jerusalem"

# With options
python -m user_api.cli "Tel Aviv" "Haifa" --interval 5

# Interactive mode
python -m user_api.cli --interactive

# JSON output
python -m user_api.cli "Tel Aviv" "Jerusalem" --json
```

### Python API

```python
from user_api import TourGuideAPI

# Create API
api = TourGuideAPI(junction_interval_seconds=3.0)

# Get tour recommendations
result = api.get_tour(
    source="Tel Aviv, Israel",
    destination="Jerusalem, Israel"
)

# Print formatted results
result.print_winners()

# Access winners
for winner in result.winners:
    print(f"{winner.junction_number}. {winner.winner_type}: {winner.winner_title}")
```

### One-Line Usage

```python
from user_api import get_tour_winners

result = get_tour_winners("Tel Aviv", "Jerusalem", verbose=True)
```

### REST API

```bash
# Start server
python -m user_api.rest_api

# GET request
curl "http://localhost:5000/tour?source=Tel+Aviv&destination=Jerusalem"

# POST request
curl -X POST http://localhost:5000/tour \
  -H "Content-Type: application/json" \
  -d '{"source": "Tel Aviv", "destination": "Jerusalem"}'
```

## API Reference

### TourGuideAPI

```python
TourGuideAPI(
    junction_interval_seconds=5.0,  # Processing speed
    google_maps_api_key=None,       # Optional API key
)
```

#### Methods

**`get_tour(source, destination, verbose=False)`**

Get tour recommendations.

```python
result = api.get_tour("Tel Aviv", "Jerusalem", verbose=True)
```

Returns `TourGuideResult`.

**`get_tour_json(source, destination)`**

Get results as JSON string.

```python
json_str = api.get_tour_json("Tel Aviv", "Jerusalem")
```

### TourGuideResult

```python
result.source              # Starting address
result.destination         # Ending address
result.total_junctions     # Number of junctions
result.winners             # List of JunctionWinner
result.video_wins          # Count of video wins
result.music_wins          # Count of music wins
result.history_wins        # Count of history wins
result.success             # True if successful
result.error               # Error message if failed

result.print_winners()     # Print formatted output
result.to_dict()           # Convert to dictionary
result.to_json()           # Convert to JSON string
```

### JunctionWinner

```python
winner.junction_number     # 1, 2, 3, ...
winner.junction_address    # "Main St & 5th Ave"
winner.turn_direction      # "LEFT", "RIGHT", etc.
winner.winner_type         # "video", "music", or "history"
winner.winner_title        # "Street Walking Tour"
winner.winner_description  # Description text
winner.winner_url          # URL to content
winner.score               # 0-100
```

## CLI Reference

```
usage: python -m user_api.cli [-h] [-s SOURCE] [-d DESTINATION]
                              [-i INTERVAL] [--interactive] [--json] [-q]
                              [source] [destination]

Arguments:
  source              Starting address
  destination         Destination address

Options:
  -s, --source        Starting address (alternative)
  -d, --destination   Destination address (alternative)
  -i, --interval      Seconds between junctions (default: 3)
  --interactive       Run in interactive mode
  --json              Output as JSON
  -q, --quiet         Suppress progress output
```

## REST API Reference

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/tour` | Get recommendations (query params) |
| POST | `/tour` | Get recommendations (JSON body) |

### GET /tour

Query parameters:
- `source` (required): Starting address
- `destination` (required): Destination address
- `interval` (optional): Seconds per junction

```bash
curl "http://localhost:5000/tour?source=Tel+Aviv&destination=Jerusalem&interval=5"
```

### POST /tour

JSON body:
```json
{
  "source": "Tel Aviv",
  "destination": "Jerusalem",
  "interval": 5.0
}
```

### Response Format

```json
{
  "source": "Tel Aviv, Israel",
  "destination": "Jerusalem, Israel",
  "total_distance": "N/A",
  "total_duration": "N/A",
  "total_junctions": 4,
  "winners": [
    {
      "junction_number": 1,
      "junction_address": "Ayalon Highway",
      "turn_direction": "MERGE",
      "winner_type": "video",
      "winner_title": "Highway Street View",
      "winner_description": "...",
      "winner_url": "https://...",
      "score": 87.5
    }
  ],
  "summary": {
    "video_wins": 2,
    "music_wins": 1,
    "history_wins": 1
  },
  "processing_time_seconds": 15.3,
  "success": true,
  "error": null
}
```

## Example Output

```
============================================================
🚗 TOUR GUIDE RESULTS
============================================================
Route: Tel Aviv → Jerusalem
Distance: 62 km | Duration: 55 mins
============================================================

📍 WINNERS PER JUNCTION:

  1. Ayalon Highway
     Turn: MERGE
     🎬 VIDEO: Ayalon Highway Drive
     Score: 87/100
     URL: https://youtube.com/...

  2. Route 1 Junction
     Turn: RIGHT
     🎵 MUSIC: Road Trip Mix
     Score: 85/100
     URL: https://spotify.com/...

  3. Ma'ale Adumim
     Turn: STRAIGHT
     📖 HISTORY: The History of Route 1
     Score: 91/100
     URL: https://wikipedia.org/...

  4. Jerusalem Entrance
     Turn: LEFT
     🎬 VIDEO: Jerusalem City Tour
     Score: 89/100
     URL: https://youtube.com/...

============================================================
📊 SUMMARY:
   🎬 Video Wins:   2
   🎵 Music Wins:   1
   📖 History Wins: 1
   ⏱️  Processing:   12.45s
============================================================
```

## Files

```
user_api/
├── __init__.py        # Module exports
├── tour_guide_api.py  # Main Python API
├── cli.py             # Command line interface
├── rest_api.py        # REST API server (requires Flask)
└── README.md          # This file
```

## Requirements

- Python 3.7+
- For REST API: `pip install flask`
- Parent modules: route_fetcher, junction_orchestrator, agent_orchestrator

## Version

1.0.0 - Initial release
