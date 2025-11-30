"""
Agent Implementations.

This module re-exports all agent classes for backwards compatibility.
Each agent is now in its own file for better maintainability.

Agents:
- VideoAgent: Finds relevant videos for junctions (YouTube API)
- MusicAgent: Finds music matching junction atmosphere (Spotify API)
- HistoryAgent: Finds historical facts about junctions (Wikipedia API)
- JudgeAgent: Evaluates and picks the winner
"""

# Re-export all agents from their individual modules
from .video_agent import VideoAgent
from .music_agent import MusicAgent
from .history_agent import HistoryAgent
from .judge_agent import JudgeAgent

# Scoring constants (kept here for backwards compatibility)
BASE_VIDEO_SCORE = 70
VIDEO_SCORE_VARIANCE = 20
MAX_RELEVANCE_SCORE = 95
FRESHNESS_MAX_TIME_MS = 500

__all__ = [
    "VideoAgent",
    "MusicAgent",
    "HistoryAgent",
    "JudgeAgent",
    "BASE_VIDEO_SCORE",
    "VIDEO_SCORE_VARIANCE",
    "MAX_RELEVANCE_SCORE",
    "FRESHNESS_MAX_TIME_MS",
]
