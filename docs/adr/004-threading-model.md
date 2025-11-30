# ADR 004: Threading Model for Parallel Processing

## Status
Accepted

## Date
2024-11-24

## Context

The Tour Guide system needs to process multiple agents concurrently for each junction, and potentially process multiple junctions in parallel. We need to decide on a concurrency model.

### Options Considered

1. **Synchronous (No Concurrency)**
   - Process agents one by one
   - Pros: Simple, no race conditions
   - Cons: Very slow (3x+ slower)

2. **asyncio (Coroutines)**
   - Python async/await model
   - Pros: Efficient for I/O, low overhead
   - Cons: Requires async libraries, viral async

3. **Multiprocessing**
   - Separate processes for each agent
   - Pros: True parallelism, GIL bypass
   - Cons: Heavy overhead, complex IPC

4. **Threading with Queue** (Selected)
   - Thread per agent, queue for coordination
   - Pros: Familiar pattern, good for I/O, simple IPC
   - Cons: GIL limits CPU parallelism

## Decision

We chose **Threading with Queue** because:

1. **I/O Bound**: Our workload is API calls (I/O), not CPU
2. **Simplicity**: Standard library, well-understood
3. **Queue Pattern**: Natural fit for producer-consumer
4. **Compatibility**: Works with all HTTP libraries
5. **Resource Efficiency**: Threads are lighter than processes

## Implementation

### Threading Hierarchy

```
Main Thread
    │
    └─► JunctionOrchestrator (Tempo Control)
            │
            └─► Junction Thread #1 ──► Junction Thread #2 ──► ...
                    │
                    ├──► Video Agent Thread
                    │         │
                    │         └──► YouTube API (I/O wait)
                    │
                    ├──► Music Agent Thread
                    │         │
                    │         └──► Spotify API (I/O wait)
                    │
                    └──► History Agent Thread
                              │
                              └──► Wikipedia API (I/O wait)

                    All agents put results in Queue(maxsize=3)

                    Judge waits for queue.full() then evaluates
```

### Thread Safety Measures

```python
# Queue for thread-safe communication
self.results_queue = Queue(maxsize=3)

# Lock for shared state
self._state_lock = threading.Lock()

# Event for signaling
self._stop_event = threading.Event()
```

### Configuration

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `agent_timeout_seconds` | 30.0 | Max time per agent |
| `max_concurrent_junctions` | 3 | Parallel junction limit |
| `queue_timeout_seconds` | 5.0 | Queue wait timeout |

## Consequences

### Positive
- 3x speedup for agent processing
- Non-blocking junction dispatch
- Clean producer-consumer pattern
- Graceful timeout handling

### Negative
- Thread debugging is harder
- Potential for deadlocks (mitigated by timeouts)
- GIL limits true parallelism

### Thread Safety Guarantees
- Queue operations are atomic
- State changes protected by lock
- Timeouts prevent infinite waits
- Daemon threads for cleanup

## Alternatives for Future

If CPU-bound processing is added:
- Consider `ProcessPoolExecutor` for compute tasks
- Keep threading for I/O tasks
- Hybrid approach possible

## References
- [Python Threading](https://docs.python.org/3/library/threading.html)
- [Queue](https://docs.python.org/3/library/queue.html)
- [Producer-Consumer Pattern](https://en.wikipedia.org/wiki/Producer%E2%80%93consumer_problem)
