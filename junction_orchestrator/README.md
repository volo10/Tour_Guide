# Junction Orchestrator Module

Controls the tempo of junction delivery in the Tour Guide system. Acts as the timing coordinator between route_fetcher and the agent processing modules.

## Overview

The Junction Orchestrator:

1. **Receives** route data from `route_fetcher` module
2. **Controls tempo** via configurable `junction_interval_seconds` hyperparameter
3. **Dispatches** junctions to registered callbacks at the set interval
4. **Supports** pause/resume, async operation, and multiple dispatch modes

## Key Hyperparameter

```python
junction_interval_seconds: float = 30.0  # Time between junction dispatches
```

This is the main tempo control - how many seconds between passing each junction to the next module.

## Quick Start

```python
from route_fetcher import RouteFetcher
from junction_orchestrator import JunctionOrchestrator, JunctionEvent

# Create orchestrator with 15-second interval
orchestrator = JunctionOrchestrator(junction_interval_seconds=15.0)

# Register callback for junction events
@orchestrator.on_junction
def process_junction(event: JunctionEvent):
    print(f"Junction {event.junction_index + 1}/{event.total_junctions}")
    print(f"  Turn: {event.junction.turn_direction.value}")
    print(f"  Street: {event.junction.street_name}")
    print(f"  Progress: {event.progress_percent:.1f}%")

    # This is where you'd call your agent module
    # agent_dispatcher.process(event.junction)

# Fetch route and start orchestration
fetcher = RouteFetcher()
route = fetcher.fetch_route("Tel Aviv", "Jerusalem")

# Start (non-blocking by default)
orchestrator.start(route)

# Or blocking mode
# orchestrator.start(route, blocking=True)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Junction Orchestrator                         │
│  ┌─────────────────┐    ┌──────────────────┐                    │
│  │ Tempo Controller │───▶│  Event Dispatcher │                   │
│  │                  │    │                   │                   │
│  │ interval: 30s    │    │  callbacks: [...]  │                  │
│  │ mode: fixed      │    │                   │                   │
│  └─────────────────┘    └────────┬──────────┘                   │
│                                   │                               │
└───────────────────────────────────┼───────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   Callback 1  │          │   Callback 2  │          │   Callback 3  │
│ (Agent Module)│          │   (Logger)    │          │  (Analytics)  │
└───────────────┘          └───────────────┘          └───────────────┘
```

## Configuration

### OrchestratorConfig

```python
from junction_orchestrator import OrchestratorConfig
from junction_orchestrator.models import DispatchMode

config = OrchestratorConfig(
    # Main tempo control
    junction_interval_seconds=30.0,  # Dispatch every 30 seconds

    # Dispatch mode
    mode=DispatchMode.FIXED_INTERVAL,  # or REAL_TIME, MANUAL

    # Real-time mode settings
    time_scale=1.0,  # 1.0 = real driving time, 0.5 = 2x speed
    pre_dispatch_seconds=5.0,  # Dispatch 5 seconds before arrival

    # Context settings
    include_route_context=True,  # Include full route in events
    include_progress=True,  # Include progress percentage
)

orchestrator = JunctionOrchestrator(config=config)
```

### Dispatch Modes

| Mode | Description |
|------|-------------|
| `FIXED_INTERVAL` | Dispatch every N seconds (default) |
| `REAL_TIME` | Based on actual driving duration from route |
| `MANUAL` | Only dispatch when explicitly triggered |

## API Reference

### JunctionOrchestrator

```python
# Create with default or custom interval
orchestrator = JunctionOrchestrator(junction_interval_seconds=30.0)

# Or with full config
orchestrator = JunctionOrchestrator(config=config)
```

#### Properties

```python
orchestrator.state      # OrchestratorState (IDLE, RUNNING, PAUSED, COMPLETED)
orchestrator.interval   # Current interval in seconds (read/write)
```

#### Methods

**`register_callback(callback)`** - Register function to receive junction events

**`on_junction`** - Decorator to register callback

**`start(route, blocking=False)`** - Start orchestrating a route

**`start_from_addresses(source, destination, blocking=False)`** - Fetch route and start

**`pause()`** - Pause orchestration

**`resume()`** - Resume paused orchestration

**`stop()`** - Stop orchestration

**`get_progress()`** - Get current progress info

**`get_stats()`** - Get orchestration statistics

### JunctionEvent

The event passed to callbacks:

```python
event.junction           # Junction object
event.junction_index     # 0-based index
event.total_junctions    # Total junctions in route
event.is_first           # True if first junction
event.is_last            # True if last junction
event.progress_percent   # 0-100 progress
event.elapsed_seconds    # Time since start
event.remaining_junctions # Junctions left
event.previous_junction  # Previous junction (if available)
event.next_junction      # Next junction (if available)
event.route              # Full route (if configured)
```

## Examples

### Basic Usage

```python
from junction_orchestrator import JunctionOrchestrator

# 10-second intervals
orchestrator = JunctionOrchestrator(junction_interval_seconds=10.0)

def my_handler(event):
    print(f"Processing: {event.junction.address}")

orchestrator.register_callback(my_handler)
orchestrator.start_from_addresses("Tel Aviv", "Haifa", blocking=True)
```

### Dynamic Tempo Adjustment

```python
orchestrator = JunctionOrchestrator(junction_interval_seconds=30.0)

# Change tempo mid-run
orchestrator.interval = 15.0  # Speed up to 15 seconds

# Or slow down
orchestrator.interval = 60.0  # 1 minute between junctions
```

### Async Usage

```python
import asyncio
from junction_orchestrator import JunctionOrchestrator

async def main():
    orchestrator = JunctionOrchestrator(junction_interval_seconds=5.0)

    @orchestrator.on_junction
    def handle(event):
        print(f"Junction: {event.junction.street_name}")

    route = fetcher.fetch_route("A", "B")
    await orchestrator.start_async(route)

asyncio.run(main())
```

### Pause/Resume

```python
import time
import threading

orchestrator = JunctionOrchestrator(junction_interval_seconds=10.0)
orchestrator.start(route)

# Pause after 30 seconds
time.sleep(30)
orchestrator.pause()
print("Paused!")

# Resume after 10 seconds
time.sleep(10)
orchestrator.resume()
print("Resumed!")
```

### Integration with Agent Module

```python
from junction_orchestrator import JunctionOrchestrator, JunctionEvent
from route_fetcher import RouteFetcher
# from agent_dispatcher import AgentDispatcher  # Your next module

orchestrator = JunctionOrchestrator(junction_interval_seconds=20.0)
# dispatcher = AgentDispatcher()

@orchestrator.on_junction
def dispatch_to_agents(event: JunctionEvent):
    # Pass junction to agent system
    # results = dispatcher.process(event.junction)

    print(f"Dispatching junction {event.junction_index + 1}")
    print(f"  Address: {event.junction.address}")
    print(f"  Turn: {event.junction.turn_direction.value}")
    print(f"  Coords: {event.junction.coordinates.to_string()}")

    # Agents would process here:
    # - Video Finder
    # - Music Finder
    # - History Finder
    # - Judge

# Start the system
fetcher = RouteFetcher()
route = fetcher.fetch_route("Ramat HaSharon", "Tel Aviv")
orchestrator.start(route, blocking=True)
```

## Data Flow

```
User Input (Source → Destination)
         │
         ▼
┌─────────────────────┐
│    Route Fetcher    │  ← Fetches from Google Maps
│                     │
│  Returns: Route     │
│  - junctions[]      │
│  - distances        │
│  - durations        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Junction Orchestrator│  ← THIS MODULE
│                     │
│  interval: 30s      │  ← Hyperparameter
│  mode: fixed        │
│                     │
│  Dispatches         │
│  JunctionEvent      │
│  every 30 seconds   │
└──────────┬──────────┘
           │
           ▼ JunctionEvent
┌─────────────────────┐
│   Agent Dispatcher  │  ← Your next module
│   (To be built)     │
│                     │
│  For each junction: │
│  - Video Finder     │
│  - Music Finder     │
│  - History Finder   │
│  - Judge            │
└─────────────────────┘
```

## Files

```
junction_orchestrator/
├── __init__.py           # Module exports
├── models.py             # Data models (Config, Event, State)
├── tempo_controller.py   # Timing/tempo logic
├── orchestrator.py       # Main orchestrator class
├── example.py            # Example usage
└── README.md             # This file
```

## Requirements

- Python 3.7+
- `route_fetcher` module (sibling module)
- No external dependencies

## Version

1.0.0 - Initial release
