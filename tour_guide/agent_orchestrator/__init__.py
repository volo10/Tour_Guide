"""
Agent Orchestrator Module for Tour Guide System

Connects the tempo controller to the 4 agents (Video, Music, History, Judge).
For each junction, spawns threads for contestant agents, collects results
in a queue, and has the Judge determine the winner.
"""

from .models import (
    AgentResult,
    JunctionResults,
    JudgeDecision,
    FinalReport,
    AgentType,
)
from .base_agent import BaseAgent
from .agents import VideoAgent, MusicAgent, HistoryAgent, JudgeAgent
from .junction_processor import JunctionProcessor
from .agent_orchestrator import AgentOrchestrator

__all__ = [
    "AgentResult",
    "JunctionResults",
    "JudgeDecision",
    "FinalReport",
    "AgentType",
    "BaseAgent",
    "VideoAgent",
    "MusicAgent",
    "HistoryAgent",
    "JudgeAgent",
    "JunctionProcessor",
    "AgentOrchestrator",
]

__version__ = "1.0.0"
