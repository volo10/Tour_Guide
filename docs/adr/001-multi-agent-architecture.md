# ADR 001: Multi-Agent Architecture for Content Recommendations

## Status
Accepted

## Date
2024-11-24

## Context

The Tour Guide system needs to provide relevant content recommendations (video, music, historical facts) for each junction along a driving route. We need to decide how to structure the recommendation system.

### Options Considered

1. **Single Monolithic Recommender**
   - One module handling all content types
   - Pros: Simple, single point of control
   - Cons: Hard to extend, tight coupling, no specialization

2. **Pipeline Architecture**
   - Sequential processing: Video → Music → History
   - Pros: Simple flow, easy debugging
   - Cons: Slow (sequential), can't leverage parallelism

3. **Multi-Agent Competition Architecture** (Selected)
   - Multiple specialized agents running in parallel
   - Judge agent selects the best recommendation
   - Pros: Parallel processing, extensible, specialized agents
   - Cons: More complex coordination, need for judge logic

## Decision

We chose the **Multi-Agent Competition Architecture** because:

1. **Parallelism**: Agents can search concurrently, reducing total processing time
2. **Specialization**: Each agent can be optimized for its content type
3. **Extensibility**: New agents can be added without modifying existing ones
4. **Competition**: Judge selection ensures only the best content is shown
5. **Fault Tolerance**: One agent's failure doesn't block others

## Architecture

```
Junction Input
     │
     ├──────────────┬──────────────┐
     ▼              ▼              ▼
┌─────────┐   ┌─────────┐   ┌─────────┐
│  Video  │   │  Music  │   │ History │
│  Agent  │   │  Agent  │   │  Agent  │
└────┬────┘   └────┬────┘   └────┬────┘
     │              │              │
     └──────────────┼──────────────┘
                    ▼
              ┌───────────┐
              │   Queue   │
              │ (size 3)  │
              └─────┬─────┘
                    ▼
              ┌───────────┐
              │   Judge   │
              │   Agent   │
              └─────┬─────┘
                    ▼
              Winner Output
```

## Consequences

### Positive
- 3x faster processing through parallelism
- Easy to add new content types (just add new agent)
- Clear separation of concerns
- Robust error handling per agent

### Negative
- More complex threading model
- Need to handle agent timeouts
- Judge logic must be fair and consistent

### Risks Mitigated
- Agent timeout: Configurable timeout with graceful handling
- Queue blocking: Bounded queue with timeout
- Resource exhaustion: Limited concurrent junctions

## References
- [Actor Model](https://en.wikipedia.org/wiki/Actor_model)
- [Competing Consumers Pattern](https://docs.microsoft.com/en-us/azure/architecture/patterns/competing-consumers)
