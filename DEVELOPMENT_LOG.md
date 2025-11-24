# Tour Guide - Development Log

This document records the prompts and development process used to build the Tour Guide system.

## Project Overview

**Goal:** Build a tour guide system that provides personalized recommendations (video, music, history) for each junction along a driving route.

**Architecture:** Modular Python package with 4 main components connected in a pipeline.

---

## Development Prompts & Responses

### Session Date: November 24, 2025

---

### Prompt 1: Initial Project Setup

**User Prompt:**
```
help me push the Tour_Guide directory to this git - https://github.com/volo10/Tour_Guide
```

**Action Taken:**
- Initialized git repository in Tour_Guide directory
- Added remote origin to GitHub
- Committed initial project files (agents, skills, documentation)
- Pushed to main branch

**Files Created:** Initial commit with existing project structure

---

### Prompt 2: Route Fetcher Module

**User Prompt:**
```
i want to create another module of the project, this module will have an api to google maps
and it will be able to give to google maps a source and destination addresses and from
google maps it will produce the route with the junctions, that will later go to the agents
we build before through another module i will build later
```

**Action Taken:**
Created `route_fetcher` module with:
- Google Maps Directions API client
- Junction extractor to parse routes into waypoints
- Data models (Route, Junction, Coordinates, TurnDirection)
- Output format matching Tour Guide agent requirements

**Files Created:**
- `route_fetcher/__init__.py`
- `route_fetcher/models.py`
- `route_fetcher/google_maps_client.py`
- `route_fetcher/junction_extractor.py`
- `route_fetcher/route_fetcher.py`
- `route_fetcher/example.py`
- `route_fetcher/README.md`

---

### Prompt 3: Junction Orchestrator (Tempo Controller)

**User Prompt:**
```
next module will set the tempo of the system, it will get the junctions from the recent
module and it will have an hyper parameter for what is the time difference between
passing another junction to the next module
```

**Action Taken:**
Created `junction_orchestrator` module with:
- Configurable `junction_interval_seconds` hyperparameter
- Tempo controller for timing between dispatches
- Callback system for downstream modules
- Support for pause/resume, async, and dynamic tempo changes
- Multiple dispatch modes (fixed interval, real-time, manual)

**Files Created:**
- `junction_orchestrator/__init__.py`
- `junction_orchestrator/models.py`
- `junction_orchestrator/tempo_controller.py`
- `junction_orchestrator/orchestrator.py`
- `junction_orchestrator/example.py`
- `junction_orchestrator/README.md`

---

### Prompt 4: Agent Orchestrator (Threading & Queue)

**User Prompt:**
```
now the last module connects the tempo orchestrator to the 4 agents (video, music, txt,
official) every time that the tempo controller releases a new junction, the new module -
agents orchestrator will open a thread for the junction. in each thread open 4 sub threads,
one for each agents. the 3 contestants will put their output in size 3 queue, and when
the queue is full, the fourth agent- the official will decide who wins and will pass the
winner to the final report of the winners per junction
```

**Action Taken:**
Created `agent_orchestrator` module with:
- 4 agents: VideoAgent, MusicAgent, HistoryAgent, JudgeAgent
- Threading architecture: junction thread spawns 3 agent sub-threads
- Size-3 queue to collect contestant results
- Judge evaluates and picks winner when queue is full
- FinalReport aggregates winners per junction

**Files Created:**
- `agent_orchestrator/__init__.py`
- `agent_orchestrator/models.py`
- `agent_orchestrator/base_agent.py`
- `agent_orchestrator/agents.py`
- `agent_orchestrator/junction_processor.py`
- `agent_orchestrator/agent_orchestrator.py`
- `agent_orchestrator/example.py`
- `agent_orchestrator/README.md`

---

### Prompt 5: User API Module

**User Prompt:**
```
please add a module of user api that ask the user for source and destination and gives
back the winner per route
```

**Action Taken:**
Created `user_api` module with:
- TourGuideAPI: Simple Python interface
- CLI: Command-line with interactive mode
- REST API: HTTP endpoints (requires Flask)
- Formatted output with winners per junction
- JSON export support

**Files Created:**
- `user_api/__init__.py`
- `user_api/__main__.py`
- `user_api/tour_guide_api.py`
- `user_api/cli.py`
- `user_api/rest_api.py`
- `user_api/example.py`
- `user_api/README.md`

---

### Prompt 6: Integration Testing

**User Prompt:**
```
please check that the entire flow of the data along the modules work
```

**Action Taken:**
Created comprehensive integration test (`test_full_flow.py`) that verifies:
1. Route Fetcher: Models and data structures
2. Junction Orchestrator: Tempo control and event dispatch
3. Agent Orchestrator: Threading, queue, and judge evaluation
4. User API: Result formatting and JSON export
5. End-to-End: Complete flow from route to final report

**Result:** All 5 tests passed ✅

**Files Created:**
- `test_full_flow.py`

---

### Prompt 7: Package Setup & Documentation

**User Prompt:**
```
please add documentation of the prompts i gave you and build the all project as a
package- with py_init and py_cache
```

**Action Taken:**
- Created this DEVELOPMENT_LOG.md
- Set up proper Python package structure
- Created pyproject.toml and setup.py
- Added requirements.txt
- Updated .gitignore for __pycache__

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER API                                  │
│  CLI: python -m tour_guide "Tel Aviv" "Jerusalem"                │
│  Python: api.get_tour(source, destination)                       │
│  REST: GET /tour?source=X&destination=Y                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      ROUTE FETCHER                                │
│  Google Maps API → Route with junctions                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                  JUNCTION ORCHESTRATOR                            │
│  Tempo control: dispatch junctions every N seconds                │
│  Hyperparameter: junction_interval_seconds                        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   AGENT ORCHESTRATOR                              │
│  Per junction:                                                    │
│    └─ Junction Thread                                             │
│         ├─ Video Agent Thread ──┐                                 │
│         ├─ Music Agent Thread ──┼─→ Queue (size 3) → Judge        │
│         └─ History Agent Thread─┘                                 │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FINAL REPORT                                 │
│  Winners per junction with scores                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Modular Architecture
Each module is self-contained with its own models, logic, and documentation. This allows:
- Independent testing
- Easy replacement of components
- Clear separation of concerns

### 2. Threading Model
- One thread per junction (allows parallel processing)
- Three sub-threads per junction (one per contestant agent)
- Queue-based synchronization (wait for all agents before judging)

### 3. Tempo Control
- Configurable interval as hyperparameter
- Supports real-time, fixed interval, and manual modes
- Can be adjusted dynamically during execution

### 4. Agent Interface
- Abstract BaseAgent class for extensibility
- Easy to add new agent types
- Consistent result format across all agents

---

## File Structure

```
Tour_Guide/
├── tour_guide/                  # Main package
│   ├── __init__.py
│   ├── route_fetcher/           # Google Maps integration
│   ├── junction_orchestrator/   # Tempo control
│   ├── agent_orchestrator/      # Agent threading & queue
│   └── user_api/                # User interfaces
├── agents/                      # Agent prompt definitions
├── skills/                      # Agent skill definitions
├── scripts/                     # Utility scripts
├── test_full_flow.py           # Integration tests
├── pyproject.toml              # Package configuration
├── setup.py                    # Backwards compatibility
├── requirements.txt            # Dependencies
├── README.md                   # Project documentation
└── DEVELOPMENT_LOG.md          # This file
```

---

## Running the System

### Quick Start
```bash
# Install package
pip install -e .

# Run CLI
python -m tour_guide "Tel Aviv" "Jerusalem"

# Run tests
python test_full_flow.py
```

### Python API
```python
from tour_guide import TourGuideAPI

api = TourGuideAPI(junction_interval_seconds=5.0)
result = api.get_tour("Tel Aviv", "Jerusalem")
result.print_winners()
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-24 | Initial release with all modules |

---

*Generated with Claude Code*
