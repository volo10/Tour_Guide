# Tour Guide Architecture

## System Overview

Tour Guide is a modular navigation enhancement system that provides personalized recommendations (video, music, history) for each junction along a driving route.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                     │
│  │     CLI     │    │  Python API │    │  REST API   │                     │
│  │             │    │             │    │   (Flask)   │                     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                     │
│         └──────────────────┼──────────────────┘                             │
│                            ▼                                                 │
│                    ┌───────────────┐                                        │
│                    │ TourGuideAPI  │                                        │
│                    └───────┬───────┘                                        │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────────┐
│                     ORCHESTRATION LAYER                                      │
├────────────────────────────┼────────────────────────────────────────────────┤
│                            ▼                                                 │
│         ┌─────────────────────────────────────┐                             │
│         │         Route Fetcher               │                             │
│         │   (Google Maps Directions API)      │                             │
│         └──────────────────┬──────────────────┘                             │
│                            │ Route + Junctions                              │
│                            ▼                                                 │
│         ┌─────────────────────────────────────┐                             │
│         │      Junction Orchestrator          │                             │
│         │   (Tempo Control: N sec interval)   │                             │
│         └──────────────────┬──────────────────┘                             │
│                            │ JunctionEvent (per interval)                   │
│                            ▼                                                 │
│         ┌─────────────────────────────────────┐                             │
│         │        Agent Orchestrator           │                             │
│         │   (Threading + Queue + Judge)       │                             │
│         └──────────────────┬──────────────────┘                             │
└────────────────────────────┼────────────────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────────────────┐
│                        AGENT LAYER                                           │
├────────────────────────────┼────────────────────────────────────────────────┤
│                            ▼                                                 │
│    ┌───────────────────────────────────────────────────────────────┐        │
│    │                  Junction Thread                               │        │
│    │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │        │
│    │  │ Video Agent │ │ Music Agent │ │History Agent│              │        │
│    │  │   Thread    │ │   Thread    │ │   Thread    │              │        │
│    │  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘              │        │
│    │         │               │               │                      │        │
│    │         └───────────────┼───────────────┘                      │        │
│    │                         ▼                                      │        │
│    │                ┌─────────────────┐                             │        │
│    │                │  Queue (size 3) │                             │        │
│    │                └────────┬────────┘                             │        │
│    │                         ▼                                      │        │
│    │                ┌─────────────────┐                             │        │
│    │                │   Judge Agent   │                             │        │
│    │                └────────┬────────┘                             │        │
│    │                         │ Winner                               │        │
│    └─────────────────────────┼──────────────────────────────────────┘        │
│                              ▼                                               │
│                     ┌─────────────────┐                                     │
│                     │  Final Report   │                                     │
│                     │ (Winners/Route) │                                     │
│                     └─────────────────┘                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### 1. Route Fetcher (`tour_guide.route_fetcher`)

**Purpose:** Fetch routes from Google Maps and extract junction data.

**Components:**
- `GoogleMapsClient`: HTTP client for Directions API
- `JunctionExtractor`: Parse route steps into Junction objects
- `RouteFetcher`: High-level interface combining both

**Data Flow:**
```
Source Address + Destination Address
         │
         ▼
    Google Maps API
         │
         ▼
    Route (with steps)
         │
         ▼
    Junction Extractor
         │
         ▼
    List[Junction] + Route metadata
```

### 2. Junction Orchestrator (`tour_guide.junction_orchestrator`)

**Purpose:** Control the tempo of junction processing.

**Key Hyperparameter:**
```python
junction_interval_seconds: float = 30.0  # Time between dispatches
```

**Components:**
- `TempoController`: Manages timing and scheduling
- `JunctionOrchestrator`: Dispatches JunctionEvents to callbacks

**Dispatch Modes:**
| Mode | Description |
|------|-------------|
| `FIXED_INTERVAL` | Dispatch every N seconds (default) |
| `REAL_TIME` | Based on actual driving duration |
| `MANUAL` | Only dispatch when triggered |

### 3. Agent Orchestrator (`tour_guide.agent_orchestrator`)

**Purpose:** Process junctions with multiple agents in parallel.

**Threading Model:**
```
Main Thread
    │
    └─▶ Junction Thread (per junction)
            │
            ├─▶ Video Agent Thread
            │
            ├─▶ Music Agent Thread
            │
            └─▶ History Agent Thread
                    │
                    └─▶ Queue (size 3)
                            │
                            └─▶ Judge (same thread as junction)
```

**Components:**
- `BaseAgent`: Abstract interface for all agents
- `VideoAgent`, `MusicAgent`, `HistoryAgent`: Contestant agents
- `JudgeAgent`: Evaluates and picks winner
- `JunctionProcessor`: Manages threading and queue

### 4. User API (`tour_guide.user_api`)

**Purpose:** User-friendly interfaces for the system.

**Interfaces:**
| Interface | Description |
|-----------|-------------|
| `TourGuideAPI` | Python class for programmatic use |
| `cli.py` | Command-line interface |
| `rest_api.py` | HTTP REST API (Flask) |

## Data Models

### Core Models

```python
# Junction - A single turn/intersection
Junction(
    junction_id: int,
    address: str,
    street_name: str,
    coordinates: Coordinates,
    turn_direction: TurnDirection,
    instruction: str,
    distance_to_next_meters: int,
    duration_to_next_seconds: int,
)

# Route - Complete route with junctions
Route(
    source_address: str,
    destination_address: str,
    total_distance_meters: int,
    total_duration_seconds: int,
    junctions: List[Junction],
)

# AgentResult - Output from an agent
AgentResult(
    agent_type: AgentType,
    title: str,
    description: str,
    url: Optional[str],
    relevance_score: float,  # 0-100
    quality_score: float,    # 0-100
)

# JudgeDecision - Winner selection
JudgeDecision(
    winner: AgentResult,
    winner_type: AgentType,
    winning_score: float,
    reasoning: str,
)

# FinalReport - Complete results
FinalReport(
    source_address: str,
    destination_address: str,
    junction_results: List[JunctionResults],
    video_wins: int,
    music_wins: int,
    history_wins: int,
)
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_MAPS_API_KEY` | Google Maps Directions API key | For real routes |
| `YOUTUBE_API_KEY` | YouTube Data API key | For video agent |
| `SPOTIFY_API_KEY` | Spotify API key | For music agent |

### Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `junction_interval_seconds` | 30.0 | Time between junction dispatches |
| `agent_timeout_seconds` | 30.0 | Max time for agent processing |
| `include_straight_junctions` | True | Include "go straight" turns |

## Error Handling

The system uses a layered error handling approach:

1. **API Level**: `GoogleMapsClientError` for API failures
2. **Agent Level**: `AgentResult.error` for agent failures
3. **Orchestrator Level**: `JunctionResults.errors` list
4. **Report Level**: `FinalReport.failed_junctions` count

## Extensibility

### Adding a New Agent

1. Extend `BaseAgent`:
```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.MY_TYPE, "My Agent")

    def process(self, junction: Junction) -> AgentResult:
        # Implementation
        return self._create_result(...)
```

2. Register in `JunctionProcessor`

### Adding a New Dispatch Mode

1. Add to `DispatchMode` enum
2. Implement in `TempoController.get_dispatch_time()`
