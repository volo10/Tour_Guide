# Tour Guide System

An intelligent multi-agent tour guide system that provides personalized recommendations (video, music, history) for each junction along a driving route.

## Overview

Tour Guide processes driving routes from Google Maps and, for each junction/turn, runs three specialized agents in parallel to find relevant content. A judge agent then picks the winner for each junction.

**Architecture:**
```
Google Maps Route → Tempo Controller → Agent Orchestrator → Winners Report
                         │
                         ▼
                    Junction 1 ──▶ [Video] [Music] [History] → Judge → Winner
                    Junction 2 ──▶ [Video] [Music] [History] → Judge → Winner
                    Junction 3 ──▶ [Video] [Music] [History] → Judge → Winner
                         ...
```

## Installation

```bash
# Clone the repository
git clone https://github.com/volo10/Tour_Guide.git
cd Tour_Guide

# Install dependencies
pip3 install certifi requests
```

## API Keys Setup

The system requires API keys to fetch real content from YouTube, Spotify, and Google Maps.

**For detailed instructions, see [docs/API_KEYS_SETUP.md](docs/API_KEYS_SETUP.md)**

### Quick Setup

Set environment variables with your API keys:

```bash
# Linux/macOS
export GOOGLE_MAPS_API_KEY="your_google_maps_key"
export YOUTUBE_API_KEY="your_youtube_key"
export SPOTIFY_CLIENT_ID="your_spotify_client_id"
export SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"

# Windows (PowerShell)
$env:GOOGLE_MAPS_API_KEY="your_google_maps_key"
$env:YOUTUBE_API_KEY="your_youtube_key"
$env:SPOTIFY_CLIENT_ID="your_spotify_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_spotify_client_secret"
```

### Where to Get Keys

| API | Get Key From | Free Tier |
|-----|--------------|-----------|
| Google Maps Directions | [Google Cloud Console](https://console.cloud.google.com/) | $200/month credit |
| YouTube Data API v3 | [Google Cloud Console](https://console.cloud.google.com/) | 10,000 units/day |
| Spotify Web API | [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) | Unlimited |

### Verify Setup

```python
from tour_guide.config import validate_api_keys

result = validate_api_keys()
if result['valid']:
    print("All API keys configured!")
else:
    print(f"Missing: {result['missing']}")
```

**📖 New to Tour Guide? Read [GETTING_STARTED.md](GETTING_STARTED.md) for a complete walkthrough!**

## Quick Start

### Step 1: Setup .env File

```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your API keys
notepad .env
```

### Step 2: Run Demo (One Command!)

```bash
python run_demo.py
```

Or specify custom route:
```bash
python run_demo.py "Tel Aviv" "Jerusalem"
```

### Interactive Mode

For a guided experience:

```bash
python tour_guide_interactive.py
```

The script will ask:
- **Where are you starting from?** (e.g., Tel Aviv, Technion)
- **Where do you want to go?** (e.g., Jerusalem, Haifa)
- Then it generates your personalized tour report!

See [INTERACTIVE_MODE.md](INTERACTIVE_MODE.md) for details.

### Run Pre-Made Demo

```bash
python demo_technion_to_tau.py
```

### Python API

```python
from tour_guide import TourGuideAPI

# Create API instance (API key loaded from config.py)
api = TourGuideAPI(junction_interval_seconds=5.0)

# Get tour recommendations
result = api.get_tour(
    source="Tel Aviv Central Station",
    destination="Jaffa Port",
    verbose=True
)

# Print winners
result.print_winners()

# Or get as JSON
json_result = api.get_tour_json(source, destination)
```

### Command Line

```bash
# Interactive mode
python -m tour_guide

# Enter source and destination when prompted
```

### Using Individual Modules

```python
# Route Fetcher - Get route with junctions from Google Maps
from tour_guide import RouteFetcher

fetcher = RouteFetcher(api_key="YOUR_KEY")
route = fetcher.fetch_route("Tel Aviv", "Jerusalem")
print(f"Route has {route.junction_count} junctions")

# Junction Orchestrator - Control tempo of junction dispatch
from tour_guide import JunctionOrchestrator

orchestrator = JunctionOrchestrator(junction_interval_seconds=10.0)

@orchestrator.on_junction
def handle_junction(event):
    print(f"Junction {event.junction_index + 1}: {event.junction.street_name}")

orchestrator.start(route, blocking=True)

# Agent Orchestrator - Full processing with agents
from tour_guide import AgentOrchestrator

orchestrator = AgentOrchestrator(junction_interval_seconds=5.0)
report = orchestrator.start(route, blocking=True)
report.print_summary()
```

## Project Structure

```
tour_guide/
├── __init__.py                 # Main package exports
├── __main__.py                 # CLI entry point
├── route_fetcher/              # Google Maps integration
│   ├── models.py               # Route, Junction, Coordinates
│   ├── google_maps_client.py   # API client
│   ├── junction_extractor.py   # Parse routes into junctions
│   └── route_fetcher.py        # Main interface
├── junction_orchestrator/      # Tempo control
│   ├── models.py               # Config, Event, State enums
│   ├── tempo_controller.py     # Timing logic
│   └── orchestrator.py         # JunctionOrchestrator
├── agent_orchestrator/         # Multi-threaded agent processing
│   ├── models.py               # AgentResult, JudgeDecision, FinalReport
│   ├── agents.py               # Video, Music, History, Judge agents
│   ├── junction_processor.py   # Threading + queue logic
│   └── agent_orchestrator.py   # AgentOrchestrator
└── user_api/                   # User-friendly interfaces
    ├── tour_guide_api.py       # TourGuideAPI class
    └── cli.py                  # Command-line interface

tests/                          # Unit tests (130 tests)
├── conftest.py                 # Pytest fixtures
├── test_route_fetcher.py
├── test_junction_orchestrator.py
├── test_agent_orchestrator.py
├── test_user_api.py
├── test_google_maps_client.py  # Google Maps API client tests
├── test_junction_processor.py  # Junction processor tests
├── test_rest_api.py            # REST API endpoint tests
└── test_agents_detailed.py     # Detailed agent tests

docs/                           # Documentation
├── ARCHITECTURE.md             # System architecture diagrams
├── API_REFERENCE.md            # Complete API documentation
├── API_KEYS_SETUP.md           # How to get and configure API keys
├── USER_GUIDE.md               # Usage guide
└── DEVELOPER_GUIDE.md          # How to extend the system
```

## Module Overview

### 1. Route Fetcher (`tour_guide.route_fetcher`)

Fetches routes from Google Maps Directions API and extracts junctions.

```python
from tour_guide import RouteFetcher, Route, Junction

fetcher = RouteFetcher(api_key="YOUR_KEY")
route = fetcher.fetch_route("Start Address", "End Address")

# Route contains:
# - source_address, destination_address
# - total_distance_meters, total_duration_seconds
# - junctions: List[Junction]

for junction in route.junctions:
    print(f"{junction.junction_id}: {junction.street_name}")
    print(f"  Turn: {junction.turn_direction.value}")
    print(f"  Coordinates: {junction.coordinates.to_string()}")
```

### 2. Junction Orchestrator (`tour_guide.junction_orchestrator`)

Controls the tempo of junction dispatch with a configurable interval.

```python
from tour_guide import JunctionOrchestrator

# Key hyperparameter: junction_interval_seconds
orchestrator = JunctionOrchestrator(junction_interval_seconds=30.0)

# Register callback for junction events
@orchestrator.on_junction
def on_junction(event):
    print(f"Junction {event.junction_index + 1}/{event.total_junctions}")
    print(f"  Street: {event.junction.street_name}")
    print(f"  Is First: {event.is_first}, Is Last: {event.is_last}")

# Start dispatching (blocking or non-blocking)
orchestrator.start(route, blocking=True)

# Control methods
orchestrator.pause()
orchestrator.resume()
orchestrator.stop()
```

### 3. Agent Orchestrator (`tour_guide.agent_orchestrator`)

Processes junctions with multiple agents in parallel using threading.

**Threading Model:**
```
Tempo Controller releases junction
         │
         ▼
    Junction Thread (new thread per junction)
         │
         ├──▶ Video Agent Thread
         ├──▶ Music Agent Thread
         └──▶ History Agent Thread
                    │
                    ▼
              Queue (size 3)
                    │
                    ▼
              Judge Agent (picks winner)
                    │
                    ▼
              Final Report
```

**Parallel Processing:** When a new junction is released, a new thread is spawned immediately - even if the previous junction is still being processed. This enables parallel processing of multiple junctions.

```python
from tour_guide import AgentOrchestrator, FinalReport

orchestrator = AgentOrchestrator(
    junction_interval_seconds=5.0,
    agent_timeout_seconds=10.0
)

# Callbacks
@orchestrator.on_junction_complete
def on_junction(results):
    if results.decision:
        print(f"Winner: {results.decision.winner.title}")

@orchestrator.on_route_complete
def on_complete(report):
    print(f"Video wins: {report.video_wins}")
    print(f"Music wins: {report.music_wins}")
    print(f"History wins: {report.history_wins}")

# Process route
report = orchestrator.start(route, blocking=True)
```

### 4. User API (`tour_guide.user_api`)

Simple, user-friendly interface combining all modules.

```python
from tour_guide import TourGuideAPI, TourGuideResult

api = TourGuideAPI(junction_interval_seconds=5.0)
result = api.get_tour("Start", "End", verbose=True)

# Result contains:
# - winners: List[JunctionWinner]
# - video_wins, music_wins, history_wins
# - total_junctions, processing_time_seconds
# - success, error

result.print_winners()  # Formatted output
result.to_json()        # JSON string
result.to_dict()        # Dictionary
```

## Agents

### Video Agent
Finds relevant YouTube videos for each junction location.

### Music Agent
Finds Spotify tracks matching the street's atmosphere.

### History Agent
Discovers historical facts about the junction location.

### Judge Agent
Evaluates all three contestants and picks the winner based on:
- Relevance score
- Quality score
- Confidence level

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_MAPS_API_KEY` | Google Maps Directions API key | Yes |
| `YOUTUBE_API_KEY` | YouTube Data API v3 key | Yes (for Video Agent) |
| `SPOTIFY_CLIENT_ID` | Spotify App Client ID | Yes (for Music Agent) |
| `SPOTIFY_CLIENT_SECRET` | Spotify App Client Secret | Yes (for Music Agent) |

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `junction_interval_seconds` | 30.0 | Time between junction dispatches |
| `agent_timeout_seconds` | 30.0 | Max time for agent processing |
| `include_straight_junctions` | True | Include "go straight" turns |

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific module tests
pytest tests/test_route_fetcher.py

# Run with coverage
pytest --cov=tour_guide
```

**Test Coverage:** 130 unit tests covering all modules.

## Documentation

- [API Keys Setup](docs/API_KEYS_SETUP.md) - How to get and configure API keys
- [Architecture](docs/ARCHITECTURE.md) - System architecture and data flow diagrams
- [API Reference](docs/API_REFERENCE.md) - Complete API documentation
- [User Guide](docs/USER_GUIDE.md) - Usage examples and troubleshooting
- [Developer Guide](docs/DEVELOPER_GUIDE.md) - How to extend and customize

## Example Output

```
============================================================
🚗 TOUR GUIDE RESULTS
============================================================
Route: Tel Aviv Central Station → Jaffa Port
Distance: 5.2 km | Duration: 12 mins
============================================================

📍 WINNERS PER JUNCTION:

  1. Allenby St & Rothschild Blvd
     Turn: LEFT
     🎬 VIDEO: Walking Tour of Rothschild Boulevard
     Score: 85/100

  2. Rothschild Blvd & Herzl St
     Turn: RIGHT
     📖 HISTORY: The History of Herzl Street
     Score: 91/100

  3. Herzl St & Jaffa Port
     Turn: DESTINATION
     🎵 MUSIC: Mediterranean Vibes Playlist
     Score: 88/100

============================================================
📊 SUMMARY:
   🎬 Video Wins:   1
   🎵 Music Wins:   1
   📖 History Wins: 1
   ⏱️  Processing:   15.23s
============================================================
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

See [Developer Guide](docs/DEVELOPER_GUIDE.md) for details.
