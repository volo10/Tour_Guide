# Logging Guide

Tour Guide includes comprehensive logging with junction ID tracking for effective debugging.

## Quick Start

### Enable Logging

```python
from tour_guide import setup_logging, TourGuideAPI

# Setup logging (default INFO level)
setup_logging(level="INFO")

# Now use the API - all logs will be shown
api = TourGuideAPI()
result = api.get_tour("Tel Aviv", "Jerusalem")
```

### Debug Logging

For detailed debugging with junction tracking:

```python
from tour_guide import setup_debug_logging, TourGuideAPI

# Enable debug logging (console + file)
setup_debug_logging(log_file="tour_guide_debug.log")

api = TourGuideAPI()
result = api.get_tour("Start", "End")
```

## Logging Levels

### INFO Level (Recommended)
Shows high-level flow and key events:

```
tour_guide.route_fetcher - INFO - Fetching route from 'Tel Aviv' to 'Jerusalem'
tour_guide.route_fetcher - INFO - Route fetched successfully: 8 junctions, 45.3 km, 48 mins
tour_guide.junction_orchestrator - INFO - Starting junction orchestration: 8 junctions, interval=5.0s
tour_guide.junction_orchestrator - INFO - [JID-1] Dispatching junction 1/8: Allenby St (LEFT)
tour_guide.agent_orchestrator - INFO - [JID-1] Spawning agent processing thread for junction 1
tour_guide.agent_orchestrator - INFO - [JID-1] Starting agent processing (Video, Music, History → Judge)
tour_guide.junction_processor - INFO - [JID-1] Processing junction: Allenby St & Rothschild Blvd
tour_guide.junction_processor - INFO - [JID-1] video completed: 'Walking Tour of Allenby St' (relevance: 82.0, quality: 85.0)
tour_guide.junction_processor - INFO - [JID-1] music completed: 'Tel Aviv Vibes' (relevance: 78.0, quality: 81.0)
tour_guide.junction_processor - INFO - [JID-1] history completed: 'History of Allenby Street' (relevance: 91.0, quality: 88.0)
tour_guide.junction_processor - INFO - [JID-1] Collected 3/3 agent results
tour_guide.junction_processor - INFO - [JID-1] Judge selected: history
tour_guide.junction_processor - INFO - [JID-1] Processing complete in 245.3ms
tour_guide.agent_orchestrator - INFO - [JID-1] Winner: history (score: 89.5)
```

### DEBUG Level
Shows detailed execution including thread spawning:

```
tour_guide.route_fetcher - DEBUG - Options: waypoints=None, avoid=None, traffic=False
tour_guide.route_fetcher - DEBUG - Junction IDs: [1, 2, 3, 4, 5, 6, 7, 8]
tour_guide.junction_orchestrator - DEBUG - [JID-1] Coordinates: 32.0653,34.7748, Progress: 12.5%
tour_guide.agent_orchestrator - DEBUG - [JID-1] Thread spawned: AgentOrch-J1, Total active threads: 1
tour_guide.junction_processor - DEBUG - [JID-1] Spawning 3 agent threads (video, music, history)
tour_guide.junction_processor - DEBUG - [JID-1] video agent thread started
tour_guide.junction_processor - DEBUG - [JID-1] music agent thread started
tour_guide.junction_processor - DEBUG - [JID-1] history agent thread started
tour_guide.junction_processor - DEBUG - [JID-1] Judge evaluating 3 results
```

## Junction ID Tracking

All logs related to a specific junction include `[JID-<junction_id>]` for easy filtering:

```bash
# View all logs for junction ID 3
cat tour_guide_debug.log | grep "\[JID-3\]"
```

Output:
```
[JID-3] Dispatching junction 3/8: Rothschild Blvd (RIGHT)
[JID-3] Spawning agent processing thread for junction 3
[JID-3] Starting agent processing (Video, Music, History → Judge)
[JID-3] Processing junction: Rothschild Blvd & Herzl St
[JID-3] video completed: 'Rothschild Boulevard Guide'
[JID-3] music completed: 'Israeli Pop Hits'
[JID-3] history completed: 'The Story of Rothschild Blvd'
[JID-3] Judge selected: history
[JID-3] Winner: history (score: 92.3)
```

## Logging Setup Functions

### `setup_logging(level, format_string, include_timestamp, log_file)`

Basic logging setup with customization:

```python
from tour_guide import setup_logging

# Custom setup
setup_logging(
    level="DEBUG",
    include_timestamp=True,
    log_file="my_tour.log"
)
```

### `setup_simple_logging()`

Quick setup for CLI usage (no timestamps):

```python
from tour_guide import setup_simple_logging

setup_simple_logging()
```

### `setup_debug_logging(log_file)`

Full debug logging to console and file:

```python
from tour_guide import setup_debug_logging

setup_debug_logging(log_file="debug.log")
```

### `setup_production_logging(log_file)`

INFO to console, DEBUG to file:

```python
from tour_guide import setup_production_logging

setup_production_logging(log_file="production.log")
```

## Log Format

Default format with timestamps:
```
2025-11-24 10:30:45 - tour_guide.module - LEVEL - [JID-X] Message
```

Simple format (no timestamps):
```
tour_guide.module - LEVEL - [JID-X] Message
```

## Parallel Processing Logs

When multiple junctions are processed in parallel, you'll see interleaved logs:

```
[JID-1] Dispatching junction 1/8
[JID-1] Spawning agent processing thread
[JID-2] Dispatching junction 2/8     # ← Junction 2 starts before Junction 1 finishes
[JID-1] Starting agent processing
[JID-2] Spawning agent processing thread
[JID-1] video completed
[JID-2] Starting agent processing
[JID-1] music completed
[JID-2] video completed
...
```

Use junction IDs to follow a specific junction through the system:
```bash
grep "\[JID-2\]" tour_guide.log
```

## Log Levels by Module

| Module | INFO Logs | DEBUG Logs |
|--------|-----------|------------|
| `route_fetcher` | Route fetch success/failure | API parameters, junction IDs |
| `junction_orchestrator` | Junction dispatch events | Coordinates, progress % |
| `agent_orchestrator` | Thread spawning, winners | Active thread count |
| `junction_processor` | Agent results, judge decision | Thread start/stop |
| `user_api` | API calls, final results | - |

## Example: Full Debug Session

```python
from tour_guide import setup_debug_logging, TourGuideAPI

# Enable debug logging
logger = setup_debug_logging("my_debug.log")

# Run tour
api = TourGuideAPI(junction_interval_seconds=5.0)
result = api.get_tour("Tel Aviv", "Haifa", verbose=True)

# Check logs
print("\nLogs written to: my_debug.log")
```

## Troubleshooting with Logs

### Junction Not Processing

Look for junction dispatch logs:
```bash
grep "Dispatching junction" tour_guide.log
```

### Agent Timeouts

Look for timeout warnings:
```bash
grep "timed out" tour_guide.log
```

### Missing Results

Check for judge errors:
```bash
grep "Judge error" tour_guide.log
```

### Thread Issues

View thread spawning:
```bash
grep "Thread spawned" tour_guide.log | grep DEBUG
```

## Disabling Logging

To disable all Tour Guide logging:

```python
import logging
logging.getLogger("tour_guide").setLevel(logging.CRITICAL)
```
