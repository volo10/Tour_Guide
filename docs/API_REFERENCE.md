# API Reference

Complete API documentation for the Tour Guide package.

## Table of Contents

- [tour_guide](#tour_guide)
- [tour_guide.route_fetcher](#tour_guideroute_fetcher)
- [tour_guide.junction_orchestrator](#tour_guidejunction_orchestrator)
- [tour_guide.agent_orchestrator](#tour_guideagent_orchestrator)
- [tour_guide.user_api](#tour_guideuser_api)

---

## tour_guide

Main package providing convenient imports.

### Imports

```python
from tour_guide import (
    # User API
    TourGuideAPI,
    TourGuideResult,
    run_cli,

    # Route Fetcher
    RouteFetcher,
    Route,
    Junction,

    # Junction Orchestrator
    JunctionOrchestrator,
    JunctionEvent,

    # Agent Orchestrator
    AgentOrchestrator,
    FinalReport,
    JunctionResults,
    VideoAgent,
    MusicAgent,
    HistoryAgent,
    JudgeAgent,
)
```

---

## tour_guide.route_fetcher

Google Maps integration for route fetching.

### Classes

#### `RouteFetcher`

Main interface for fetching routes.

```python
RouteFetcher(
    api_key: Optional[str] = None,
    include_straight_junctions: bool = True,
    min_junction_distance: int = 50,
)
```

**Parameters:**
- `api_key`: Google Maps API key (or set `GOOGLE_MAPS_API_KEY` env var)
- `include_straight_junctions`: Include "go straight" junctions
- `min_junction_distance`: Minimum meters between junctions

**Methods:**

```python
def fetch_route(
    self,
    source: str,
    destination: str,
    waypoints: Optional[List[str]] = None,
    avoid: Optional[List[str]] = None,
    with_traffic: bool = False,
) -> Route
```
Fetch a route and extract junctions.

```python
def fetch_route_for_agents(
    self,
    source: str,
    destination: str,
    **kwargs
) -> Dict[str, Any]
```
Get route in Tour Guide agent format.

```python
def validate_addresses(
    self,
    source: str,
    destination: str
) -> Dict[str, Any]
```
Validate that addresses can be geocoded and routed.

---

#### `Route`

Complete route with junctions.

```python
@dataclass
class Route:
    source_address: str
    destination_address: str
    total_distance_meters: int
    total_distance_text: str
    total_duration_seconds: int
    total_duration_text: str
    junctions: List[Junction]
    polyline: Optional[str] = None
    bounds: Optional[dict] = None
```

**Properties:**
- `junction_count: int` - Number of junctions

**Methods:**
- `to_dict() -> dict` - Convert to dictionary
- `to_yaml_format() -> dict` - Convert to agent-compatible format

---

#### `Junction`

Single junction/intersection.

```python
@dataclass
class Junction:
    junction_id: int
    address: str
    street_name: str
    coordinates: Coordinates
    turn_direction: TurnDirection
    instruction: str
    distance_to_next_meters: int
    distance_to_next_text: str
    duration_to_next_seconds: int
    duration_to_next_text: str
    cumulative_distance_meters: int = 0
    cumulative_duration_seconds: int = 0
    maneuver: Optional[str] = None
```

---

#### `Coordinates`

GPS coordinates.

```python
@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def to_list(self) -> List[float]
    def to_string(self) -> str
```

---

#### `TurnDirection`

Enum for turn types.

```python
class TurnDirection(Enum):
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
```

---

## tour_guide.junction_orchestrator

Tempo-controlled junction dispatch.

### Classes

#### `JunctionOrchestrator`

Controls junction dispatch timing.

```python
JunctionOrchestrator(
    config: Optional[OrchestratorConfig] = None,
    junction_interval_seconds: float = 30.0,
)
```

**Properties:**
- `state: OrchestratorState` - Current state (IDLE, RUNNING, PAUSED, COMPLETED)
- `interval: float` - Dispatch interval in seconds (read/write)

**Methods:**

```python
def register_callback(self, callback: Callable[[JunctionEvent], Any])
```
Register callback to receive junction events.

```python
@on_junction
def handler(event: JunctionEvent):
    ...
```
Decorator to register callback.

```python
def start(self, route: Route, blocking: bool = False)
```
Start orchestrating a route.

```python
def start_from_addresses(
    self,
    source: str,
    destination: str,
    blocking: bool = False,
    api_key: Optional[str] = None,
)
```
Fetch route and start orchestrating.

```python
def pause(self)
def resume(self)
def stop(self)
```
Control orchestration state.

```python
async def start_async(self, route: Route)
```
Async version of start.

---

#### `JunctionEvent`

Event dispatched for each junction.

```python
@dataclass
class JunctionEvent:
    junction: Junction
    dispatch_time: datetime
    scheduled_time: datetime
    junction_index: int
    total_junctions: int
    delay_seconds: float = 0.0
    is_first: bool = False
    is_last: bool = False
    progress_percent: float = 0.0
    elapsed_seconds: float = 0.0
    remaining_junctions: int = 0
    route: Optional[Route] = None
    previous_junction: Optional[Junction] = None
    next_junction: Optional[Junction] = None
```

---

#### `OrchestratorConfig`

Configuration for orchestrator.

```python
@dataclass
class OrchestratorConfig:
    junction_interval_seconds: float = 30.0
    mode: DispatchMode = DispatchMode.FIXED_INTERVAL
    time_scale: float = 1.0
    pre_dispatch_seconds: float = 5.0
    lookahead_count: int = 1
    include_route_context: bool = True
```

---

## tour_guide.agent_orchestrator

Multi-threaded agent processing.

### Classes

#### `AgentOrchestrator`

Connects tempo controller to agents.

```python
AgentOrchestrator(
    junction_interval_seconds: float = 30.0,
    agent_timeout_seconds: float = 30.0,
    video_agent: Optional[VideoAgent] = None,
    music_agent: Optional[MusicAgent] = None,
    history_agent: Optional[HistoryAgent] = None,
    judge_agent: Optional[JudgeAgent] = None,
)
```

**Properties:**
- `interval: float` - Dispatch interval (read/write)

**Methods:**

```python
def on_junction_complete(self, callback: Callable[[JunctionResults], None])
```
Register callback for junction completion.

```python
def on_route_complete(self, callback: Callable[[FinalReport], None])
```
Register callback for route completion.

```python
def start(
    self,
    route: Route,
    blocking: bool = True,
) -> Optional[FinalReport]
```
Start processing a route.

```python
def start_from_addresses(
    self,
    source: str,
    destination: str,
    blocking: bool = True,
    api_key: Optional[str] = None,
) -> Optional[FinalReport]
```
Fetch route and start processing.

```python
def get_report(self) -> Optional[FinalReport]
def get_progress(self) -> dict
```
Get current state.

---

#### `BaseAgent`

Abstract base class for agents.

```python
class BaseAgent(ABC):
    def __init__(self, agent_type: AgentType, name: str)

    @abstractmethod
    def process(self, junction: Junction) -> AgentResult
```

---

#### `VideoAgent`, `MusicAgent`, `HistoryAgent`

Contestant agents (extend BaseAgent).

```python
class VideoAgent(BaseAgent):
    def process(self, junction: Junction) -> AgentResult
```

---

#### `JudgeAgent`

Evaluates contestants and picks winner.

```python
class JudgeAgent(BaseAgent):
    def evaluate(
        self,
        junction: Junction,
        contestants: List[AgentResult]
    ) -> JudgeDecision
```

---

#### `AgentResult`

Result from an agent.

```python
@dataclass
class AgentResult:
    agent_type: AgentType
    agent_name: str
    junction_id: int
    junction_address: str
    title: str
    description: str
    url: Optional[str] = None
    relevance_score: float = 0.0
    quality_score: float = 0.0
    confidence: float = 0.0
    processing_time_ms: float = 0.0
    error: Optional[str] = None

    @property
    def is_success(self) -> bool
    @property
    def overall_score(self) -> float
```

---

#### `JudgeDecision`

Judge's verdict.

```python
@dataclass
class JudgeDecision:
    junction_id: int
    junction_address: str
    winner: AgentResult
    winner_type: AgentType
    winning_score: float
    contestants: List[AgentResult]
    reasoning: str
    judge_scores: Dict[str, float]
```

---

#### `FinalReport`

Complete results for a route.

```python
@dataclass
class FinalReport:
    source_address: str
    destination_address: str
    total_junctions: int
    junction_results: List[JunctionResults]
    video_wins: int = 0
    music_wins: int = 0
    history_wins: int = 0
    total_processing_time_seconds: float = 0.0

    @property
    def success_rate(self) -> float
    def print_summary(self)
```

---

## tour_guide.user_api

User-friendly interfaces.

### Classes

#### `TourGuideAPI`

Main user-facing API.

```python
TourGuideAPI(
    junction_interval_seconds: float = 5.0,
    google_maps_api_key: Optional[str] = None,
)
```

**Methods:**

```python
def get_tour(
    self,
    source: str,
    destination: str,
    verbose: bool = False,
) -> TourGuideResult
```
Get tour recommendations.

```python
def get_tour_json(
    self,
    source: str,
    destination: str,
) -> str
```
Get recommendations as JSON.

---

#### `TourGuideResult`

User-friendly result format.

```python
@dataclass
class TourGuideResult:
    source: str
    destination: str
    total_distance: str
    total_duration: str
    winners: List[JunctionWinner]
    total_junctions: int
    video_wins: int
    music_wins: int
    history_wins: int
    processing_time_seconds: float
    success: bool
    error: Optional[str]

    def to_dict(self) -> dict
    def to_json(self, indent: int = 2) -> str
    def print_winners(self)
```

---

#### `JunctionWinner`

Winner info for a junction.

```python
@dataclass
class JunctionWinner:
    junction_number: int
    junction_address: str
    turn_direction: str
    winner_type: str
    winner_title: str
    winner_description: str
    winner_url: Optional[str]
    score: float
```

---

### Functions

#### `run_cli()`

Run the command-line interface.

```python
def run_cli()
```

#### `interactive_mode()`

Run in interactive mode.

```python
def interactive_mode()
```

#### `get_tour_winners()`

Convenience function for quick usage.

```python
def get_tour_winners(
    source: str,
    destination: str,
    interval: float = 5.0,
    verbose: bool = True,
) -> TourGuideResult
```
