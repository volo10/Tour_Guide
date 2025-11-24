"""
Tour Guide - A navigation enhancement system.

Provides personalized recommendations (video, music, history) for each
junction along a driving route.

Modules:
    route_fetcher: Google Maps API integration for route fetching
    junction_orchestrator: Tempo-controlled junction dispatch
    agent_orchestrator: Multi-threaded agent processing with queue
    user_api: User-friendly interfaces (CLI, Python API, REST)

Quick Start:
    from tour_guide import TourGuideAPI

    api = TourGuideAPI(junction_interval_seconds=5.0)
    result = api.get_tour("Tel Aviv", "Jerusalem")
    result.print_winners()

CLI Usage:
    python -m tour_guide "Tel Aviv" "Jerusalem"
    python -m tour_guide --interactive
"""

# Version
__version__ = "1.0.0"
__author__ = "Tour Guide Team"

# Import main classes for convenience
from .route_fetcher import RouteFetcher, Route, Junction
from .junction_orchestrator import JunctionOrchestrator, JunctionEvent
from .agent_orchestrator import (
    AgentOrchestrator,
    FinalReport,
    JunctionResults,
    VideoAgent,
    MusicAgent,
    HistoryAgent,
    JudgeAgent,
)
from .user_api import TourGuideAPI, TourGuideResult, run_cli

__all__ = [
    # Version
    "__version__",
    # Route Fetcher
    "RouteFetcher",
    "Route",
    "Junction",
    # Junction Orchestrator
    "JunctionOrchestrator",
    "JunctionEvent",
    # Agent Orchestrator
    "AgentOrchestrator",
    "FinalReport",
    "JunctionResults",
    "VideoAgent",
    "MusicAgent",
    "HistoryAgent",
    "JudgeAgent",
    # User API
    "TourGuideAPI",
    "TourGuideResult",
    "run_cli",
]
