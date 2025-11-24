"""
Data models for Junction Orchestrator module.

Defines configuration, events, and state for tempo-controlled
junction dispatch.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable, Any, List
from enum import Enum
from datetime import datetime

from ..route_fetcher.models import Junction, Route


class DispatchMode(Enum):
    """How junctions are dispatched."""
    FIXED_INTERVAL = "fixed_interval"      # Fixed time between junctions
    REAL_TIME = "real_time"                # Based on actual driving time
    DISTANCE_BASED = "distance_based"      # Based on distance thresholds
    MANUAL = "manual"                      # Manual trigger only


class OrchestratorState(Enum):
    """Current state of the orchestrator."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class OrchestratorConfig:
    """
    Configuration for the Junction Orchestrator.

    The key hyperparameter is `junction_interval_seconds` which controls
    the tempo - how many seconds between dispatching each junction.
    """
    # Primary tempo control (hyperparameter)
    junction_interval_seconds: float = 30.0  # Time between junction dispatches

    # Dispatch mode
    mode: DispatchMode = DispatchMode.FIXED_INTERVAL

    # Real-time mode settings
    time_scale: float = 1.0  # 1.0 = real-time, 0.5 = 2x speed, 2.0 = half speed

    # Distance-based mode settings
    distance_threshold_meters: int = 500  # Dispatch when within this distance

    # Lookahead settings
    lookahead_count: int = 1  # How many junctions to dispatch ahead
    pre_dispatch_seconds: float = 5.0  # Dispatch this many seconds before arrival

    # Callback settings
    include_route_context: bool = True  # Include full route in callbacks
    include_progress: bool = True  # Include progress percentage

    # Error handling
    retry_on_error: bool = True
    max_retries: int = 3

    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.junction_interval_seconds <= 0:
            raise ValueError("junction_interval_seconds must be positive")
        if self.time_scale <= 0:
            raise ValueError("time_scale must be positive")
        if self.lookahead_count < 1:
            raise ValueError("lookahead_count must be at least 1")
        return True


@dataclass
class JunctionEvent:
    """
    Event dispatched when a junction is ready for processing.

    This is passed to the callback/next module when it's time
    to process a junction.
    """
    # Required fields (no defaults) - must come first
    junction: Junction
    dispatch_time: datetime
    scheduled_time: datetime
    junction_index: int
    total_junctions: int

    # Optional fields with defaults
    delay_seconds: float = 0.0
    is_first: bool = False
    is_last: bool = False
    progress_percent: float = 0.0
    elapsed_seconds: float = 0.0
    remaining_junctions: int = 0
    route: Optional[Route] = None
    previous_junction: Optional[Junction] = None
    next_junction: Optional[Junction] = None
    event_id: str = ""

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "junction": self.junction.to_dict(),
            "dispatch_time": self.dispatch_time.isoformat(),
            "junction_index": self.junction_index,
            "total_junctions": self.total_junctions,
            "is_first": self.is_first,
            "is_last": self.is_last,
            "progress_percent": self.progress_percent,
            "elapsed_seconds": self.elapsed_seconds,
            "remaining_junctions": self.remaining_junctions,
            "previous_junction": self.previous_junction.to_dict() if self.previous_junction else None,
            "next_junction": self.next_junction.to_dict() if self.next_junction else None,
        }


@dataclass
class OrchestratorStats:
    """Statistics from an orchestration run."""
    total_junctions: int = 0
    dispatched_count: int = 0
    error_count: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_duration_seconds: float = 0.0
    average_dispatch_interval: float = 0.0
    dispatch_times: List[datetime] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Percentage of successful dispatches."""
        if self.dispatched_count == 0:
            return 0.0
        return ((self.dispatched_count - self.error_count) / self.dispatched_count) * 100


# Type alias for junction callback
JunctionCallback = Callable[[JunctionEvent], Any]
