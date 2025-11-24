# Agent Orchestrator Module

Connects the tempo controller to the 4 Tour Guide agents. Processes each junction with parallel agent threads and determines winners.

## Overview

When the tempo controller releases a junction:

1. **Main thread** receives the junction event
2. **Junction thread** spawns for processing
3. **3 sub-threads** (Video, Music, History) run in parallel
4. Results collected in **size-3 queue**
5. **Judge agent** evaluates when queue is full
6. **Winner** added to final report

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Tempo Controller                                 │
│                 (junction_orchestrator)                              │
│                                                                      │
│    Dispatches JunctionEvent every N seconds                         │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼ JunctionEvent
┌─────────────────────────────────────────────────────────────────────┐
│                     Agent Orchestrator                               │
│                                                                      │
│  For each junction, spawns a processing thread:                     │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Junction Processing Thread                      │   │
│  │                                                              │   │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐                  │   │
│  │   │  Video   │  │  Music   │  │ History  │  ← 3 sub-threads │   │
│  │   │  Agent   │  │  Agent   │  │  Agent   │                  │   │
│  │   └────┬─────┘  └────┬─────┘  └────┬─────┘                  │   │
│  │        │             │             │                         │   │
│  │        └─────────────┼─────────────┘                         │   │
│  │                      ▼                                       │   │
│  │              ┌──────────────┐                                │   │
│  │              │ Results Queue│  (size 3)                      │   │
│  │              │              │                                │   │
│  │              └──────┬───────┘                                │   │
│  │                     │ (when full)                            │   │
│  │                     ▼                                        │   │
│  │              ┌──────────────┐                                │   │
│  │              │    Judge     │                                │   │
│  │              │    Agent     │                                │   │
│  │              └──────┬───────┘                                │   │
│  │                     │                                        │   │
│  │                     ▼                                        │   │
│  │              ┌──────────────┐                                │   │
│  │              │   Winner!    │ → Added to Final Report        │   │
│  │              └──────────────┘                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   Final Report   │
              │                  │
              │  Junction 1: 🎬  │
              │  Junction 2: 🎵  │
              │  Junction 3: 📖  │
              │  ...             │
              └──────────────────┘
```

## Quick Start

```python
from agent_orchestrator import AgentOrchestrator

# Create orchestrator with 10-second interval
orchestrator = AgentOrchestrator(junction_interval_seconds=10.0)

# Process a route
report = orchestrator.start_from_addresses(
    source="Tel Aviv, Israel",
    destination="Jerusalem, Israel",
    blocking=True
)

# Print results
report.print_summary()
```

## Simple Usage

```python
from agent_orchestrator import run_tour_guide

# One-liner to run the complete system
report = run_tour_guide(
    source="Tel Aviv",
    destination="Haifa",
    junction_interval=5.0,  # Fast demo
    verbose=True
)
```

## API Reference

### AgentOrchestrator

```python
AgentOrchestrator(
    junction_interval_seconds=30.0,  # Tempo between junctions
    agent_timeout_seconds=30.0,      # Max time for agents
    video_agent=None,                # Custom video agent
    music_agent=None,                # Custom music agent
    history_agent=None,              # Custom history agent
    judge_agent=None,                # Custom judge agent
)
```

#### Methods

**`start(route, blocking=True)`** - Start processing a Route object

**`start_from_addresses(source, destination, blocking=True)`** - Fetch route and start

**`pause()`** / **`resume()`** - Pause/resume processing

**`stop()`** - Stop all processing

**`get_report()`** - Get current FinalReport

**`get_progress()`** - Get progress info

#### Callbacks

```python
@orchestrator.on_junction_complete
def handle_junction(result: JunctionResults):
    print(f"Winner: {result.winner.title}")

@orchestrator.on_route_complete
def handle_complete(report: FinalReport):
    report.print_summary()
```

### Agents

Each agent implements the `BaseAgent` interface:

```python
class VideoAgent(BaseAgent):
    def process(self, junction: Junction) -> AgentResult:
        # Find relevant video
        return AgentResult(...)

class MusicAgent(BaseAgent):
    def process(self, junction: Junction) -> AgentResult:
        # Find matching music
        return AgentResult(...)

class HistoryAgent(BaseAgent):
    def process(self, junction: Junction) -> AgentResult:
        # Find historical facts
        return AgentResult(...)

class JudgeAgent(BaseAgent):
    def evaluate(self, junction, contestants) -> JudgeDecision:
        # Pick the winner
        return JudgeDecision(...)
```

### Custom Agents

Create custom agents by extending BaseAgent:

```python
from agent_orchestrator import BaseAgent, AgentResult, AgentType

class MyVideoAgent(BaseAgent):
    def __init__(self):
        super().__init__(AgentType.VIDEO, "My Video Finder")
        self.api = YouTubeAPI()

    def process(self, junction):
        # Real API call
        videos = self.api.search(junction.street_name)
        best = videos[0]

        return self._create_result(
            junction=junction,
            title=best.title,
            description=best.description,
            url=best.url,
            relevance_score=90,
            quality_score=85,
            confidence=88,
        )

# Use custom agent
orchestrator = AgentOrchestrator(
    video_agent=MyVideoAgent()
)
```

### Data Models

**AgentResult** - Output from each agent:
```python
result.agent_type      # VIDEO, MUSIC, HISTORY
result.title           # "Street Walking Tour"
result.description     # Description text
result.url             # Link to content
result.relevance_score # 0-100
result.quality_score   # 0-100
result.confidence      # 0-100
result.overall_score   # Combined score
```

**JudgeDecision** - Judge's verdict:
```python
decision.winner        # Winning AgentResult
decision.winner_type   # VIDEO, MUSIC, or HISTORY
decision.winning_score # Final score
decision.reasoning     # Explanation
decision.contestants   # All results evaluated
```

**JunctionResults** - Complete junction processing:
```python
jr.junction           # The Junction object
jr.video_result       # VideoAgent result
jr.music_result       # MusicAgent result
jr.history_result     # HistoryAgent result
jr.decision           # JudgeDecision
jr.winner             # Shortcut to winning result
```

**FinalReport** - Complete route results:
```python
report.source_address
report.destination_address
report.total_junctions
report.junction_results    # List of JunctionResults
report.video_wins          # Count of video wins
report.music_wins          # Count of music wins
report.history_wins        # Count of history wins
report.success_rate        # Percentage successful
report.print_summary()     # Print formatted report
```

## Example Output

```
🚗 Tour Guide: Tel Aviv → Jerusalem
⏱️  Tempo: 5s between junctions
--------------------------------------------------
  🎬 Junction 1: Ayalon Highway Street View (87/100)
  🎵 Junction 2: Urban Pulse (85/100)
  📖 Junction 3: The History of Route 1 (91/100)
  🎬 Junction 4: Jerusalem Entrance Tour (89/100)

============================================================
TOUR GUIDE FINAL REPORT
============================================================
Route: Tel Aviv, Israel → Jerusalem, Israel
Total Junctions: 4
Success Rate: 100.0%
Processing Time: 22.45s
------------------------------------------------------------
WINNER SUMMARY:
  🎬 Video Wins:   2
  🎵 Music Wins:   1
  📖 History Wins: 1
------------------------------------------------------------
JUNCTION WINNERS:
  1. Ayalon Highway
     🎬 Winner: Ayalon Highway Street View (87/100)
  2. Route 1 Junction
     🎵 Winner: Urban Pulse (85/100)
  3. Ma'ale Adumim
     📖 Winner: The History of Route 1 (91/100)
  4. Jerusalem Entrance
     🎬 Winner: Jerusalem Entrance Tour (89/100)
============================================================
```

## Threading Model

```
Main Thread
    │
    └─→ Tempo Controller Thread
            │
            ├─→ Junction 1 Thread
            │       ├─→ Video Agent Thread
            │       ├─→ Music Agent Thread
            │       └─→ History Agent Thread
            │               │
            │               └─→ Queue (size 3)
            │                       │
            │                       └─→ Judge (same thread)
            │
            ├─→ Junction 2 Thread
            │       └─→ ...
            │
            └─→ Junction N Thread
                    └─→ ...
```

## Files

```
agent_orchestrator/
├── __init__.py           # Module exports
├── models.py             # Data models
├── base_agent.py         # Abstract agent interface
├── agents.py             # Video, Music, History, Judge agents
├── junction_processor.py # Threading and queue logic
├── agent_orchestrator.py # Main orchestrator
├── example.py            # Usage example
└── README.md             # This file
```

## Requirements

- Python 3.7+
- `route_fetcher` module
- `junction_orchestrator` module
- No external dependencies

## Version

1.0.0 - Initial release
