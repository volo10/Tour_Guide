"""
Tempo Controller for Junction Dispatch.

Manages timing and scheduling of junction dispatches
based on configurable tempo settings.
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, List, Generator

from ..route_fetcher.models import Junction, Route
from .models import OrchestratorConfig, DispatchMode


class TempoController:
    """
    Controls the tempo/timing of junction dispatches.

    The main hyperparameter is `junction_interval_seconds` which
    determines how frequently junctions are dispatched.
    """

    def __init__(self, config: OrchestratorConfig):
        """
        Initialize the tempo controller.

        Args:
            config: Orchestrator configuration with tempo settings
        """
        self.config = config
        self._start_time: Optional[datetime] = None
        self._pause_time: Optional[datetime] = None
        self._paused_duration: float = 0.0
        self._is_paused: bool = False

    @property
    def interval_seconds(self) -> float:
        """Current interval between junction dispatches."""
        return self.config.junction_interval_seconds

    @interval_seconds.setter
    def interval_seconds(self, value: float):
        """Update the dispatch interval (tempo)."""
        if value <= 0:
            raise ValueError("Interval must be positive")
        self.config.junction_interval_seconds = value

    def start(self):
        """Mark the start of orchestration."""
        self._start_time = datetime.now()
        self._paused_duration = 0.0
        self._is_paused = False

    def pause(self):
        """Pause the tempo controller."""
        if not self._is_paused:
            self._pause_time = datetime.now()
            self._is_paused = True

    def resume(self):
        """Resume the tempo controller."""
        if self._is_paused and self._pause_time:
            self._paused_duration += (datetime.now() - self._pause_time).total_seconds()
            self._is_paused = False
            self._pause_time = None

    @property
    def elapsed_seconds(self) -> float:
        """Seconds elapsed since start (excluding paused time)."""
        if not self._start_time:
            return 0.0
        total = (datetime.now() - self._start_time).total_seconds()
        if self._is_paused and self._pause_time:
            total -= (datetime.now() - self._pause_time).total_seconds()
        return total - self._paused_duration

    def get_dispatch_time(self, junction_index: int) -> datetime:
        """
        Calculate when a junction should be dispatched.

        Args:
            junction_index: 0-based index of the junction

        Returns:
            Scheduled dispatch time
        """
        if not self._start_time:
            self._start_time = datetime.now()

        if self.config.mode == DispatchMode.FIXED_INTERVAL:
            offset = junction_index * self.config.junction_interval_seconds
            return self._start_time + timedelta(seconds=offset)

        # For other modes, default to fixed interval
        return self._start_time + timedelta(
            seconds=junction_index * self.config.junction_interval_seconds
        )

    def get_dispatch_time_realtime(
        self,
        junction: Junction,
        route: Route
    ) -> datetime:
        """
        Calculate dispatch time based on real driving duration.

        Uses cumulative duration from route data, scaled by time_scale.

        Args:
            junction: The junction to dispatch
            route: Full route for context

        Returns:
            Scheduled dispatch time based on driving duration
        """
        if not self._start_time:
            self._start_time = datetime.now()

        # Use cumulative duration, scaled
        scaled_duration = junction.cumulative_duration_seconds / self.config.time_scale

        # Subtract pre-dispatch time (dispatch before arrival)
        adjusted_duration = max(0, scaled_duration - self.config.pre_dispatch_seconds)

        return self._start_time + timedelta(seconds=adjusted_duration)

    def wait_until(self, target_time: datetime) -> float:
        """
        Wait until the target time, respecting pause state.

        Args:
            target_time: Time to wait until

        Returns:
            Actual delay in seconds (may be 0 if already past)
        """
        while self._is_paused:
            time.sleep(0.1)  # Check pause state periodically

        now = datetime.now()
        if now >= target_time:
            return 0.0

        delay = (target_time - now).total_seconds()
        time.sleep(delay)
        return delay

    def wait_interval(self) -> float:
        """
        Wait for the configured interval duration.

        Returns:
            Actual time waited in seconds
        """
        start = time.time()

        # Handle pause state
        while self._is_paused:
            time.sleep(0.1)

        remaining = self.config.junction_interval_seconds
        while remaining > 0:
            if self._is_paused:
                while self._is_paused:
                    time.sleep(0.1)
            sleep_time = min(remaining, 0.5)  # Check every 0.5s for pause
            time.sleep(sleep_time)
            remaining -= sleep_time

        return time.time() - start

    def generate_schedule(
        self,
        junctions: List[Junction],
        route: Optional[Route] = None
    ) -> Generator[tuple, None, None]:
        """
        Generate a schedule of (junction, dispatch_time) pairs.

        Args:
            junctions: List of junctions to schedule
            route: Optional route for real-time mode

        Yields:
            Tuple of (junction_index, junction, scheduled_datetime)
        """
        self.start()

        for i, junction in enumerate(junctions):
            if self.config.mode == DispatchMode.REAL_TIME and route:
                dispatch_time = self.get_dispatch_time_realtime(junction, route)
            else:
                dispatch_time = self.get_dispatch_time(i)

            yield (i, junction, dispatch_time)

    def calculate_total_duration(self, junction_count: int) -> float:
        """
        Calculate total orchestration duration for given junction count.

        Args:
            junction_count: Number of junctions

        Returns:
            Total duration in seconds
        """
        if junction_count <= 0:
            return 0.0
        # First junction dispatches immediately
        return (junction_count - 1) * self.config.junction_interval_seconds

    def get_progress(self, current_index: int, total: int) -> dict:
        """
        Get current progress information.

        Args:
            current_index: Current junction index (0-based)
            total: Total number of junctions

        Returns:
            Progress dictionary
        """
        return {
            "current_index": current_index,
            "total": total,
            "percent": (current_index / total) * 100 if total > 0 else 0,
            "remaining": total - current_index - 1,
            "elapsed_seconds": self.elapsed_seconds,
            "estimated_remaining_seconds": (total - current_index - 1) * self.config.junction_interval_seconds,
            "is_paused": self._is_paused,
        }
