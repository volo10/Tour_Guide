# ADR 002: Tempo Control System for Junction Dispatch

## Status
Accepted

## Date
2024-11-24

## Context

The Tour Guide system needs to dispatch junctions to agents at a controlled rate. The rate should be configurable to match different use cases (real-time driving, demo mode, testing).

### Options Considered

1. **Immediate Dispatch**
   - Process all junctions as fast as possible
   - Pros: Fastest total time
   - Cons: No pacing, overwhelming for users, unrealistic

2. **Real-Time GPS-Based**
   - Dispatch based on actual GPS location
   - Pros: Most realistic
   - Cons: Requires GPS hardware, complex integration

3. **Fixed Interval Timer** (Selected)
   - Configurable time interval between dispatches
   - Pros: Predictable, testable, flexible
   - Cons: Not tied to actual driving

4. **Distance-Based**
   - Dispatch when within certain distance of junction
   - Pros: Location-aware
   - Cons: Requires continuous position updates

## Decision

We chose **Fixed Interval Timer** as the primary mode because:

1. **Simplicity**: Easy to implement and test
2. **Flexibility**: Interval is a hyperparameter users can tune
3. **Demo-Friendly**: Works without GPS or real driving
4. **Testability**: Deterministic for unit tests

We also implemented support for other modes as future extensions.

## Implementation

```python
class OrchestratorConfig:
    junction_interval_seconds: float = 30.0  # Primary hyperparameter
    mode: DispatchMode = DispatchMode.FIXED_INTERVAL
```

### Dispatch Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `FIXED_INTERVAL` | Fixed seconds between dispatches | Default, demos |
| `REAL_TIME` | Based on junction duration | Simulation |
| `DISTANCE_BASED` | GPS proximity trigger | Real driving |
| `MANUAL` | User-triggered dispatch | Testing |

## Consequences

### Positive
- Clear hyperparameter for tuning
- Works in any environment (no GPS needed)
- Easy to test with short intervals
- Supports future GPS integration

### Negative
- Not perfectly synchronized with actual driving
- Users must estimate appropriate interval

### Trade-offs
- Default 30 seconds balances realism and responsiveness
- Shorter intervals (5s) for demos
- Longer intervals (60s+) for real driving approximation

## References
- [Reactor Pattern](https://en.wikipedia.org/wiki/Reactor_pattern)
- [Rate Limiting Patterns](https://cloud.google.com/architecture/rate-limiting-strategies-techniques)
