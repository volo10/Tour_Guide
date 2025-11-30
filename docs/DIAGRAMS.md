# Tour Guide Architecture Diagrams

This document contains C4 model diagrams and UML diagrams for the Tour Guide system.

## C4 Model Diagrams

### Level 1: System Context Diagram

```mermaid
C4Context
    title System Context Diagram - Tour Guide

    Person(user, "Driver/User", "A person using the Tour Guide for navigation enhancement")

    System(tourguide, "Tour Guide System", "Provides personalized video, music, and history recommendations for driving routes")

    System_Ext(googlemaps, "Google Maps API", "Provides route directions and junction data")
    System_Ext(youtube, "YouTube API", "Provides video content for locations")
    System_Ext(spotify, "Spotify API", "Provides music tracks for locations")
    System_Ext(wikipedia, "Wikipedia API", "Provides historical information")

    Rel(user, tourguide, "Requests tour recommendations", "CLI/REST API")
    Rel(tourguide, googlemaps, "Fetches route data", "HTTPS")
    Rel(tourguide, youtube, "Searches videos", "HTTPS")
    Rel(tourguide, spotify, "Searches music", "HTTPS")
    Rel(tourguide, wikipedia, "Searches history", "HTTPS")
```

### Level 2: Container Diagram

```mermaid
C4Container
    title Container Diagram - Tour Guide

    Person(user, "User")

    Container_Boundary(tourguide, "Tour Guide System") {
        Container(cli, "CLI Interface", "Python/Click", "Command-line interface for interactive use")
        Container(restapi, "REST API", "Python/Flask", "HTTP API for programmatic access")
        Container(coreapi, "TourGuideAPI", "Python", "Core orchestration logic")
        Container(routefetcher, "Route Fetcher", "Python", "Fetches and parses routes from Google Maps")
        Container(junctionorch, "Junction Orchestrator", "Python", "Controls tempo of junction processing")
        Container(agentorch, "Agent Orchestrator", "Python", "Multi-threaded agent processing")
        Container(agents, "Content Agents", "Python", "Video, Music, History agents")
        Container(judge, "Judge Agent", "Python", "Evaluates and selects winning content")
    }

    System_Ext(googlemaps, "Google Maps API")
    System_Ext(youtube, "YouTube API")
    System_Ext(spotify, "Spotify API")
    System_Ext(wikipedia, "Wikipedia API")

    Rel(user, cli, "Uses")
    Rel(user, restapi, "Calls")
    Rel(cli, coreapi, "Uses")
    Rel(restapi, coreapi, "Uses")
    Rel(coreapi, routefetcher, "Fetches route")
    Rel(coreapi, junctionorch, "Orchestrates tempo")
    Rel(junctionorch, agentorch, "Dispatches junctions")
    Rel(agentorch, agents, "Runs in parallel")
    Rel(agentorch, judge, "Evaluates results")
    Rel(routefetcher, googlemaps, "HTTPS")
    Rel(agents, youtube, "HTTPS")
    Rel(agents, spotify, "HTTPS")
    Rel(agents, wikipedia, "HTTPS")
```

### Level 3: Component Diagram - Agent Orchestrator

```mermaid
C4Component
    title Component Diagram - Agent Orchestrator

    Container_Boundary(agentorch, "Agent Orchestrator") {
        Component(processor, "JunctionProcessor", "Manages threading and queue")
        Component(baseagent, "BaseAgent", "Abstract agent interface")
        Component(videoagent, "VideoAgent", "YouTube content search")
        Component(musicagent, "MusicAgent", "Spotify music search")
        Component(historyagent, "HistoryAgent", "Wikipedia history search")
        Component(judgeagent, "JudgeAgent", "Result evaluation")
        Component(queue, "Result Queue", "Thread-safe queue (size 3)")
        Component(models, "Data Models", "AgentResult, JudgeDecision")
    }

    Rel(processor, baseagent, "Creates instances")
    Rel(videoagent, baseagent, "Extends")
    Rel(musicagent, baseagent, "Extends")
    Rel(historyagent, baseagent, "Extends")
    Rel(processor, queue, "Collects results")
    Rel(queue, judgeagent, "Provides contestants")
    Rel(judgeagent, models, "Creates JudgeDecision")
```

## UML Diagrams

### Class Diagram - Core Domain Model

```mermaid
classDiagram
    class Junction {
        +int junction_id
        +str address
        +str street_name
        +Coordinates coordinates
        +TurnDirection turn_direction
        +str instruction
        +int distance_to_next_meters
        +int duration_to_next_seconds
    }

    class Route {
        +str source_address
        +str destination_address
        +int total_distance_meters
        +int total_duration_seconds
        +List~Junction~ junctions
    }

    class AgentResult {
        +AgentType agent_type
        +str title
        +str description
        +str url
        +float relevance_score
        +float quality_score
        +float confidence
        +is_success() bool
        +overall_score() float
    }

    class JudgeDecision {
        +int junction_id
        +AgentResult winner
        +AgentType winner_type
        +float winning_score
        +str reasoning
    }

    class TourGuideResult {
        +str source
        +str destination
        +List~JunctionWinner~ winners
        +int video_wins
        +int music_wins
        +int history_wins
        +bool success
    }

    Route "1" *-- "*" Junction
    JudgeDecision "1" o-- "1" AgentResult
    TourGuideResult "1" o-- "*" JudgeDecision
```

### Class Diagram - Agent Hierarchy

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +AgentType agent_type
        +str name
        +initialize()*
        +process(Junction)* AgentResult
        #_create_result() AgentResult
        #_create_error_result() AgentResult
    }

    class VideoAgent {
        -str youtube_api_key
        +initialize(api_key)
        +process(Junction) AgentResult
        -_search_youtube() AgentResult
        -_build_creative_queries() List~str~
    }

    class MusicAgent {
        -str spotify_client_id
        -str spotify_client_secret
        -str spotify_token
        +initialize(client_id, client_secret)
        +process(Junction) AgentResult
        -_get_spotify_token() str
        -_search_spotify() AgentResult
    }

    class HistoryAgent {
        +initialize()
        +process(Junction) AgentResult
        -_search_wikipedia() AgentResult
        -_get_search_terms() List~str~
    }

    class JudgeAgent {
        +evaluate(Junction, List~AgentResult~) JudgeDecision
        -_calculate_score() float
    }

    BaseAgent <|-- VideoAgent
    BaseAgent <|-- MusicAgent
    BaseAgent <|-- HistoryAgent
```

### Sequence Diagram - Tour Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant API as TourGuideAPI
    participant RF as RouteFetcher
    participant JO as JunctionOrchestrator
    participant AO as AgentOrchestrator
    participant VA as VideoAgent
    participant MA as MusicAgent
    participant HA as HistoryAgent
    participant JA as JudgeAgent

    User->>API: get_tour(source, destination)
    API->>RF: fetch_route(source, destination)
    RF->>RF: Call Google Maps API
    RF-->>API: Route with Junctions

    API->>JO: start(route)

    loop For each Junction (at tempo interval)
        JO->>AO: process_junction(junction)

        par Parallel Agent Execution
            AO->>VA: process(junction)
            VA-->>AO: AgentResult (video)
        and
            AO->>MA: process(junction)
            MA-->>AO: AgentResult (music)
        and
            AO->>HA: process(junction)
            HA-->>AO: AgentResult (history)
        end

        AO->>JA: evaluate(junction, results)
        JA-->>AO: JudgeDecision (winner)
        AO-->>JO: JunctionResult
    end

    JO-->>API: All results collected
    API-->>User: TourGuideResult
```

### Sequence Diagram - Agent Processing Detail

```mermaid
sequenceDiagram
    participant JP as JunctionProcessor
    participant Q as ResultQueue
    participant VA as VideoAgent
    participant MA as MusicAgent
    participant HA as HistoryAgent
    participant JA as JudgeAgent

    Note over JP: Junction received

    JP->>JP: Create agent threads

    par Video Thread
        JP->>VA: process(junction)
        VA->>VA: _build_creative_queries()
        VA->>VA: _search_youtube()
        VA-->>Q: put(AgentResult)
    and Music Thread
        JP->>MA: process(junction)
        MA->>MA: _get_spotify_token()
        MA->>MA: _search_spotify()
        MA-->>Q: put(AgentResult)
    and History Thread
        JP->>HA: process(junction)
        HA->>HA: _get_search_terms()
        HA->>HA: _search_wikipedia()
        HA-->>Q: put(AgentResult)
    end

    Note over Q: Wait for all 3 results or timeout

    JP->>Q: get_all_results()
    Q-->>JP: List[AgentResult]

    JP->>JA: evaluate(junction, results)
    JA->>JA: _calculate_score() for each
    JA-->>JP: JudgeDecision
```

### Activity Diagram - Junction Processing

```mermaid
flowchart TD
    A[Receive Junction] --> B{Agents Initialized?}
    B -->|No| C[Initialize Agents]
    C --> D
    B -->|Yes| D[Create Agent Threads]

    D --> E[Start Video Thread]
    D --> F[Start Music Thread]
    D --> G[Start History Thread]

    E --> H{YouTube API Success?}
    H -->|Yes| I[Create Video Result]
    H -->|No| J[Create Error Result]
    I --> K[Put in Queue]
    J --> K

    F --> L{Spotify API Success?}
    L -->|Yes| M[Create Music Result]
    L -->|No| N[Create Error Result]
    M --> O[Put in Queue]
    N --> O

    G --> P{Wikipedia API Success?}
    P -->|Yes| Q[Create History Result]
    P -->|No| R[Create Error Result]
    Q --> S[Put in Queue]
    R --> S

    K --> T{All Results Ready?}
    O --> T
    S --> T

    T -->|Yes| U[Judge Evaluates]
    T -->|Timeout| V[Use Available Results]
    V --> U

    U --> W[Select Winner]
    W --> X[Return JudgeDecision]
```

### State Diagram - Orchestrator States

```mermaid
stateDiagram-v2
    [*] --> IDLE

    IDLE --> RUNNING : start(route)
    RUNNING --> PAUSED : pause()
    PAUSED --> RUNNING : resume()
    RUNNING --> COMPLETED : all junctions processed
    RUNNING --> IDLE : stop()
    PAUSED --> IDLE : stop()
    COMPLETED --> IDLE : reset()

    RUNNING --> ERROR : exception
    ERROR --> IDLE : reset()
```

## Deployment Diagram

```mermaid
flowchart TB
    subgraph "User Environment"
        CLI[CLI Application]
        REST[REST Client]
    end

    subgraph "Tour Guide Application"
        subgraph "User API Layer"
            CLIIF[CLI Interface]
            RESTAPI[Flask REST API]
            TGAPI[TourGuideAPI]
        end

        subgraph "Orchestration Layer"
            RF[Route Fetcher]
            JO[Junction Orchestrator]
            AO[Agent Orchestrator]
        end

        subgraph "Agent Layer"
            VA[Video Agent]
            MA[Music Agent]
            HA[History Agent]
            JA[Judge Agent]
        end
    end

    subgraph "External Services"
        GM[Google Maps API]
        YT[YouTube API]
        SP[Spotify API]
        WK[Wikipedia API]
    end

    CLI --> CLIIF
    REST --> RESTAPI
    CLIIF --> TGAPI
    RESTAPI --> TGAPI
    TGAPI --> RF
    TGAPI --> JO
    JO --> AO
    AO --> VA
    AO --> MA
    AO --> HA
    AO --> JA
    RF --> GM
    VA --> YT
    MA --> SP
    HA --> WK
```

## Data Flow Diagram

```mermaid
flowchart LR
    subgraph Input
        U[User Input]
        SRC[Source Address]
        DST[Destination]
    end

    subgraph Processing
        RF[Route Fetcher]
        JE[Junction Extractor]
        JO[Junction Orchestrator]
        VA[Video Agent]
        MA[Music Agent]
        HA[History Agent]
        JA[Judge]
    end

    subgraph Output
        RES[Results]
        WIN[Winners List]
        STATS[Statistics]
    end

    U --> SRC
    U --> DST
    SRC --> RF
    DST --> RF
    RF --> JE
    JE --> JO
    JO -->|Junction 1| VA
    JO -->|Junction 1| MA
    JO -->|Junction 1| HA
    VA -->|Video Result| JA
    MA -->|Music Result| JA
    HA -->|History Result| JA
    JA --> WIN
    WIN --> RES
    RES --> STATS
```

## Notes

### Diagram Rendering

These diagrams use [Mermaid](https://mermaid.js.org/) notation and can be rendered:

1. **GitHub**: Renders automatically in markdown files
2. **VS Code**: Use "Markdown Preview Mermaid Support" extension
3. **Online**: Use [Mermaid Live Editor](https://mermaid.live/)
4. **Documentation**: Use mkdocs with mermaid plugin

### C4 Model Levels

| Level | Name | Purpose |
|-------|------|---------|
| 1 | Context | System boundaries and external actors |
| 2 | Container | High-level technology decisions |
| 3 | Component | Internal structure of containers |
| 4 | Code | Class-level detail (see class diagrams) |

### Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture description
- [API_REFERENCE.md](API_REFERENCE.md) - API documentation
- [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Development guide
