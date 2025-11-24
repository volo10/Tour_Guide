"""
Data models for Agent Orchestrator module.

Defines agent results, judge decisions, and final report structures.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime

from ..route_fetcher.models import Junction


class AgentType(Enum):
    """Types of agents in the system."""
    VIDEO = "video"
    MUSIC = "music"
    HISTORY = "history"
    JUDGE = "judge"


@dataclass
class AgentResult:
    """
    Result from a single agent processing a junction.

    This is what each contestant agent (Video, Music, History)
    puts into the queue for the Judge to evaluate.
    """
    # Agent identification
    agent_type: AgentType
    agent_name: str

    # The junction that was processed
    junction_id: int
    junction_address: str

    # Result content
    title: str  # e.g., "Main Street Walking Tour" or "Urban Energy Mix"
    description: str  # Brief description of the recommendation
    url: Optional[str] = None  # Link to video/song/article

    # Scoring (agent's self-assessment)
    relevance_score: float = 0.0  # 0-100
    quality_score: float = 0.0  # 0-100
    confidence: float = 0.0  # 0-100, how confident the agent is

    # Metadata
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: Optional[Dict[str, Any]] = None  # Full API response if any
    error: Optional[str] = None  # Error message if failed

    @property
    def is_success(self) -> bool:
        """Whether the agent successfully produced a result."""
        return self.error is None and self.title != ""

    @property
    def overall_score(self) -> float:
        """Combined score for quick comparison."""
        return (self.relevance_score * 0.5 +
                self.quality_score * 0.3 +
                self.confidence * 0.2)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "agent_type": self.agent_type.value,
            "agent_name": self.agent_name,
            "junction_id": self.junction_id,
            "junction_address": self.junction_address,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "relevance_score": self.relevance_score,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
            "overall_score": self.overall_score,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
            "is_success": self.is_success,
            "error": self.error,
        }


@dataclass
class JudgeDecision:
    """
    Decision made by the Judge agent after evaluating all contestants.
    """
    # The junction being judged
    junction_id: int
    junction_address: str

    # Winner
    winner: AgentResult
    winner_type: AgentType
    winning_score: float

    # All contestants (for reference)
    contestants: List[AgentResult] = field(default_factory=list)

    # Judge's reasoning
    reasoning: str = ""

    # Scores assigned by judge (may differ from self-assessment)
    judge_scores: Dict[str, float] = field(default_factory=dict)

    # Metadata
    decision_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "junction_id": self.junction_id,
            "junction_address": self.junction_address,
            "winner": self.winner.to_dict(),
            "winner_type": self.winner_type.value,
            "winning_score": self.winning_score,
            "contestants": [c.to_dict() for c in self.contestants],
            "reasoning": self.reasoning,
            "judge_scores": self.judge_scores,
            "decision_time_ms": self.decision_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class JunctionResults:
    """
    Complete results for a single junction processing.

    Contains all agent results and the judge's final decision.
    """
    # Junction info
    junction: Junction
    junction_index: int

    # Results from all agents
    video_result: Optional[AgentResult] = None
    music_result: Optional[AgentResult] = None
    history_result: Optional[AgentResult] = None

    # Judge decision
    decision: Optional[JudgeDecision] = None

    # Timing
    total_processing_time_ms: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Status
    is_complete: bool = False
    errors: List[str] = field(default_factory=list)

    @property
    def all_results(self) -> List[AgentResult]:
        """Get all non-None agent results."""
        results = []
        if self.video_result:
            results.append(self.video_result)
        if self.music_result:
            results.append(self.music_result)
        if self.history_result:
            results.append(self.history_result)
        return results

    @property
    def winner(self) -> Optional[AgentResult]:
        """Get the winning result."""
        return self.decision.winner if self.decision else None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "junction_id": self.junction.junction_id,
            "junction_address": self.junction.address,
            "junction_index": self.junction_index,
            "video_result": self.video_result.to_dict() if self.video_result else None,
            "music_result": self.music_result.to_dict() if self.music_result else None,
            "history_result": self.history_result.to_dict() if self.history_result else None,
            "decision": self.decision.to_dict() if self.decision else None,
            "total_processing_time_ms": self.total_processing_time_ms,
            "is_complete": self.is_complete,
            "errors": self.errors,
        }


@dataclass
class FinalReport:
    """
    Final report containing winners for all junctions in a route.

    This is the output of the entire agent orchestration process.
    """
    # Route info
    source_address: str
    destination_address: str
    total_junctions: int

    # Results per junction
    junction_results: List[JunctionResults] = field(default_factory=list)

    # Summary statistics
    total_processing_time_seconds: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Winner counts
    video_wins: int = 0
    music_wins: int = 0
    history_wins: int = 0

    # Errors
    failed_junctions: int = 0
    total_errors: int = 0

    @property
    def success_rate(self) -> float:
        """Percentage of successfully processed junctions."""
        if self.total_junctions == 0:
            return 0.0
        return ((self.total_junctions - self.failed_junctions) /
                self.total_junctions) * 100

    @property
    def winners_summary(self) -> Dict[str, int]:
        """Summary of wins per agent type."""
        return {
            "video": self.video_wins,
            "music": self.music_wins,
            "history": self.history_wins,
        }

    def add_junction_result(self, result: JunctionResults):
        """Add a junction result and update statistics."""
        self.junction_results.append(result)

        if result.decision:
            if result.decision.winner_type == AgentType.VIDEO:
                self.video_wins += 1
            elif result.decision.winner_type == AgentType.MUSIC:
                self.music_wins += 1
            elif result.decision.winner_type == AgentType.HISTORY:
                self.history_wins += 1

        if result.errors:
            self.total_errors += len(result.errors)

        if not result.is_complete:
            self.failed_junctions += 1

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "source_address": self.source_address,
            "destination_address": self.destination_address,
            "total_junctions": self.total_junctions,
            "junction_results": [jr.to_dict() for jr in self.junction_results],
            "total_processing_time_seconds": self.total_processing_time_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "winners_summary": self.winners_summary,
            "success_rate": self.success_rate,
            "failed_junctions": self.failed_junctions,
            "total_errors": self.total_errors,
        }

    def print_summary(self):
        """Print a formatted summary of the report."""
        print("\n" + "=" * 60)
        print("TOUR GUIDE FINAL REPORT")
        print("=" * 60)
        print(f"Route: {self.source_address} → {self.destination_address}")
        print(f"Total Junctions: {self.total_junctions}")
        print(f"Success Rate: {self.success_rate:.1f}%")
        print(f"Processing Time: {self.total_processing_time_seconds:.2f}s")
        print("-" * 60)
        print("WINNER SUMMARY:")
        print(f"  🎬 Video Wins:   {self.video_wins}")
        print(f"  🎵 Music Wins:   {self.music_wins}")
        print(f"  📖 History Wins: {self.history_wins}")
        print("-" * 60)
        print("JUNCTION WINNERS:")
        for jr in self.junction_results:
            if jr.decision:
                winner = jr.decision.winner
                icon = {"video": "🎬", "music": "🎵", "history": "📖"}.get(
                    jr.decision.winner_type.value, "❓"
                )
                print(f"  {jr.junction_index + 1}. {jr.junction.address}")
                print(f"     {icon} Winner: {winner.title} ({jr.decision.winning_score:.0f}/100)")
        print("=" * 60)
