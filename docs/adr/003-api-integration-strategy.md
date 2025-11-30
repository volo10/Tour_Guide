# ADR 003: External API Integration Strategy

## Status
Accepted

## Date
2024-11-24

## Context

The Tour Guide agents need to fetch real content from external APIs:
- Google Maps Directions API (routes)
- YouTube Data API v3 (videos)
- Spotify Web API (music)
- Wikipedia API (historical facts)

We need to decide how to integrate these APIs safely and efficiently.

### Options Considered

1. **Direct API Calls in Agents**
   - Each agent makes raw HTTP requests
   - Pros: Simple, direct
   - Cons: Duplicated error handling, no abstraction

2. **Shared HTTP Client**
   - Single client with retry/timeout logic
   - Pros: Consistent behavior, DRY
   - Cons: Still coupled to specific APIs

3. **API Client Abstraction Layer** (Selected)
   - Dedicated client class per API
   - Common interface, specific implementations
   - Pros: Clean abstraction, testable, mockable
   - Cons: More code upfront

## Decision

We chose **API Client Abstraction Layer** because:

1. **Testability**: Easy to mock API responses in tests
2. **Error Handling**: Centralized retry and timeout logic
3. **Rate Limiting**: Can implement per-API rate limits
4. **Credential Management**: API keys in one place
5. **Maintainability**: API changes isolated to client class

## Implementation

```
┌─────────────────────────────────────────────────────┐
│                    Agent Layer                       │
│  ┌─────────┐   ┌─────────┐   ┌───────────┐         │
│  │  Video  │   │  Music  │   │  History  │         │
│  │  Agent  │   │  Agent  │   │   Agent   │         │
│  └────┬────┘   └────┬────┘   └─────┬─────┘         │
└───────┼─────────────┼──────────────┼───────────────┘
        │             │              │
┌───────┼─────────────┼──────────────┼───────────────┐
│       ▼             ▼              ▼               │
│  ┌─────────┐   ┌─────────┐   ┌───────────┐        │
│  │ YouTube │   │ Spotify │   │ Wikipedia │        │
│  │ Client  │   │ Client  │   │  Client   │        │
│  └────┬────┘   └────┬────┘   └─────┬─────┘        │
│       │             │              │               │
│                API Client Layer                    │
└───────┼─────────────┼──────────────┼───────────────┘
        │             │              │
        ▼             ▼              ▼
   YouTube API   Spotify API   Wikipedia API
```

### API Key Management

```python
# All keys from environment variables
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
SPOTIFY_CLIENT_ID = os.environ.get("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")
```

### Error Handling Strategy

| Error Type | Handling |
|------------|----------|
| Network timeout | Retry up to 3 times with backoff |
| Rate limit (429) | Wait and retry |
| Auth error (401/403) | Fail fast, log warning |
| Not found (404) | Return empty result |
| Server error (5xx) | Retry with backoff |

## Consequences

### Positive
- Clean separation between agents and APIs
- Easy to swap API providers
- Comprehensive error handling
- 100% testable with mocks

### Negative
- More classes to maintain
- Slight overhead from abstraction

### Security Measures
- API keys never in source code
- Keys validated at startup
- Credentials not logged
- HTTPS only

## References
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Gateway Pattern](https://microservices.io/patterns/apigateway.html)
