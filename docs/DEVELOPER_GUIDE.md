# Developer Guide

Guide for extending and customizing the Tour Guide system.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/volo10/Tour_Guide.git
cd Tour_Guide

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## Project Structure

```
tour_guide/
├── __init__.py              # Main package exports
├── __main__.py              # CLI entry point
├── route_fetcher/           # Google Maps integration
│   ├── __init__.py
│   ├── models.py            # Route, Junction, Coordinates
│   ├── client.py            # GoogleMapsClient
│   ├── extractor.py         # JunctionExtractor
│   └── fetcher.py           # RouteFetcher (main interface)
├── junction_orchestrator/   # Tempo control
│   ├── __init__.py
│   ├── models.py            # Config, Event, State enums
│   ├── tempo_controller.py  # Timing logic
│   └── orchestrator.py      # JunctionOrchestrator
├── agent_orchestrator/      # Multi-threaded processing
│   ├── __init__.py
│   ├── models.py            # AgentResult, JudgeDecision, etc.
│   ├── agents.py            # BaseAgent and implementations
│   ├── junction_processor.py # Threading + queue logic
│   └── agent_orchestrator.py # AgentOrchestrator
└── user_api/                # User interfaces
    ├── __init__.py
    ├── models.py            # TourGuideResult, JunctionWinner
    ├── api.py               # TourGuideAPI
    └── cli.py               # Command-line interface
```

## Adding a New Agent

### Step 1: Define Agent Type

Add to `agent_orchestrator/models.py`:

```python
class AgentType(Enum):
    VIDEO = "VIDEO"
    MUSIC = "MUSIC"
    HISTORY = "HISTORY"
    JUDGE = "JUDGE"
    MY_AGENT = "MY_AGENT"  # Add new type
```

### Step 2: Create Agent Class

Create in `agent_orchestrator/agents.py`:

```python
class MyAgent(BaseAgent):
    """Custom agent implementation."""

    def __init__(self):
        super().__init__(AgentType.MY_AGENT, "My Agent")

    def process(self, junction: Junction) -> AgentResult:
        """Process a junction and return recommendation."""
        # Your implementation here
        title = f"Recommendation for {junction.street_name}"
        description = "Generated recommendation..."

        return self._create_result(
            junction=junction,
            title=title,
            description=description,
            url="https://example.com",
            relevance_score=85.0,
            quality_score=90.0,
        )
```

### Step 3: Register Agent

Update `junction_processor.py` to include your agent:

```python
class JunctionProcessor:
    def __init__(
        self,
        # ... existing params
        my_agent: Optional[MyAgent] = None,
    ):
        self.my_agent = my_agent or MyAgent()
```

### Step 4: Update Queue Size

If adding a contestant agent, update queue size:

```python
QUEUE_SIZE = 4  # Was 3, now 4 for new agent
```

## Adding a New Dispatch Mode

### Step 1: Add Mode Enum

In `junction_orchestrator/models.py`:

```python
class DispatchMode(Enum):
    FIXED_INTERVAL = "fixed_interval"
    REAL_TIME = "real_time"
    MANUAL = "manual"
    ADAPTIVE = "adaptive"  # New mode
```

### Step 2: Implement Logic

In `tempo_controller.py`:

```python
def get_dispatch_time(self, junction_index: int) -> float:
    if self.config.mode == DispatchMode.ADAPTIVE:
        # Custom timing logic
        base_interval = self.config.junction_interval_seconds
        # Adjust based on junction complexity, traffic, etc.
        return base_interval * self._calculate_factor(junction_index)
    # ... existing modes
```

## Customizing the Judge

The judge evaluates contestant results and picks a winner.

### Custom Scoring Logic

```python
class CustomJudgeAgent(JudgeAgent):
    """Custom judge with different scoring."""

    def evaluate(
        self,
        junction: Junction,
        contestants: List[AgentResult]
    ) -> JudgeDecision:
        # Custom scoring weights
        weights = {
            AgentType.VIDEO: 1.2,   # Prefer video
            AgentType.MUSIC: 1.0,
            AgentType.HISTORY: 1.1,
        }

        scored = []
        for result in contestants:
            weight = weights.get(result.agent_type, 1.0)
            score = result.overall_score * weight
            scored.append((result, score))

        # Sort by weighted score
        scored.sort(key=lambda x: x[1], reverse=True)
        winner, winning_score = scored[0]

        return JudgeDecision(
            junction_id=junction.junction_id,
            junction_address=junction.address,
            winner=winner,
            winner_type=winner.agent_type,
            winning_score=winning_score,
            contestants=contestants,
            reasoning="Custom weighted scoring",
            judge_scores={r.agent_name: s for r, s in scored},
        )
```

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_route_fetcher.py

# With coverage
pytest --cov=tour_guide

# Verbose output
pytest -v
```

### Writing Tests

Use fixtures from `conftest.py`:

```python
def test_my_agent(sample_junction):
    """Test custom agent."""
    agent = MyAgent()
    result = agent.process(sample_junction)

    assert result.agent_type == AgentType.MY_AGENT
    assert result.is_success
```

### Mocking External APIs

```python
from unittest.mock import patch, Mock

@patch("tour_guide.route_fetcher.client.requests.get")
def test_with_mock_api(mock_get):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "OK", "routes": []}
    mock_get.return_value = mock_response

    # Your test code
```

## API Integration

### Adding New External API

1. Create client class in appropriate module
2. Add environment variable for API key
3. Implement error handling
4. Add to agent implementation

Example:

```python
class SpotifyClient:
    """Client for Spotify API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SPOTIFY_API_KEY")

    def search_tracks(self, query: str) -> List[dict]:
        # Implementation
        pass
```

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public methods
- Keep functions focused and small

### Pull Request Process

1. Fork the repository
2. Create feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request

### Commit Messages

Follow conventional commits:

```
feat: add adaptive dispatch mode
fix: handle empty route response
docs: update API reference
test: add junction processor tests
```
