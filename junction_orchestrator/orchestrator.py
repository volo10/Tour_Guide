"""
Main Junction Orchestrator.

Coordinates tempo-controlled dispatch of junctions from route_fetcher
to downstream agent modules.
"""

import uuid
import threading
import asyncio
from datetime import datetime
from typing import Optional, Callable, Any, List
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from route_fetcher.models import Route, Junction
from route_fetcher import RouteFetcher

from .models import (
    OrchestratorConfig,
    OrchestratorState,
    JunctionEvent,
    OrchestratorStats,
    JunctionCallback,
    DispatchMode,
)
from .tempo_controller import TempoController


class JunctionOrchestrator:
    """
    Main orchestrator that controls junction dispatch tempo.

    Receives routes from route_fetcher and dispatches junctions
    at configurable intervals to the next processing module.
    """

    def __init__(
        self,
        config: Optional[OrchestratorConfig] = None,
        junction_interval_seconds: float = 30.0,
    ):
        """
        Initialize the Junction Orchestrator.

        Args:
            config: Full configuration object (optional)
            junction_interval_seconds: Shortcut to set the main tempo parameter
        """
        if config:
            self.config = config
        else:
            self.config = OrchestratorConfig(
                junction_interval_seconds=junction_interval_seconds
            )

        self.config.validate()
        self.tempo = TempoController(self.config)

        # State
        self._state = OrchestratorState.IDLE
        self._current_route: Optional[Route] = None
        self._current_index: int = 0
        self._callbacks: List[JunctionCallback] = []
        self._stats = OrchestratorStats()

        # Threading
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._executor = ThreadPoolExecutor(max_workers=4)

    @property
    def state(self) -> OrchestratorState:
        """Current orchestrator state."""
        return self._state

    @property
    def interval(self) -> float:
        """Current junction dispatch interval in seconds."""
        return self.config.junction_interval_seconds

    @interval.setter
    def interval(self, seconds: float):
        """
        Update the junction dispatch interval (tempo).

        This is the main hyperparameter controlling dispatch timing.

        Args:
            seconds: New interval between junction dispatches
        """
        self.config.junction_interval_seconds = seconds
        self.tempo.interval_seconds = seconds

    def register_callback(self, callback: JunctionCallback):
        """
        Register a callback to receive junction events.

        The callback will be invoked for each junction dispatch.
        Multiple callbacks can be registered.

        Args:
            callback: Function that accepts JunctionEvent
        """
        self._callbacks.append(callback)

    def unregister_callback(self, callback: JunctionCallback):
        """Remove a registered callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def on_junction(self, callback: JunctionCallback):
        """
        Decorator to register a junction callback.

        Usage:
            @orchestrator.on_junction
            def handle_junction(event: JunctionEvent):
                print(f"Processing {event.junction.address}")
        """
        self.register_callback(callback)
        return callback

    def _create_event(
        self,
        junction: Junction,
        index: int,
        scheduled_time: datetime,
    ) -> JunctionEvent:
        """Create a JunctionEvent for dispatch."""
        total = len(self._current_route.junctions) if self._current_route else 0
        now = datetime.now()

        event = JunctionEvent(
            junction=junction,
            dispatch_time=now,
            scheduled_time=scheduled_time,
            delay_seconds=(now - scheduled_time).total_seconds(),
            junction_index=index,
            total_junctions=total,
            is_first=(index == 0),
            is_last=(index == total - 1),
            progress_percent=(index / total) * 100 if total > 0 else 0,
            elapsed_seconds=self.tempo.elapsed_seconds,
            remaining_junctions=total - index - 1,
            event_id=str(uuid.uuid4())[:8],
        )

        # Add route context if configured
        if self.config.include_route_context and self._current_route:
            event.route = self._current_route
            if index > 0:
                event.previous_junction = self._current_route.junctions[index - 1]
            if index < total - 1:
                event.next_junction = self._current_route.junctions[index + 1]

        return event

    def _dispatch_event(self, event: JunctionEvent):
        """Dispatch event to all registered callbacks."""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception as e:
                self._stats.error_count += 1
                print(f"Callback error: {e}")

    def _run_sync(self):
        """Synchronous orchestration loop."""
        if not self._current_route:
            return

        junctions = self._current_route.junctions
        self._stats.total_junctions = len(junctions)
        self._stats.start_time = datetime.now()

        # Generate schedule
        schedule = list(self.tempo.generate_schedule(junctions, self._current_route))

        for index, junction, scheduled_time in schedule:
            # Check for stop signal
            if self._stop_event.is_set():
                break

            # Check for pause
            while self._state == OrchestratorState.PAUSED:
                if self._stop_event.is_set():
                    break
                self._stop_event.wait(0.1)

            # Wait until scheduled time
            self.tempo.wait_until(scheduled_time)

            # Create and dispatch event
            self._current_index = index
            event = self._create_event(junction, index, scheduled_time)
            self._dispatch_event(event)

            # Update stats
            self._stats.dispatched_count += 1
            self._stats.dispatch_times.append(event.dispatch_time)

        # Completed
        self._stats.end_time = datetime.now()
        if self._stats.start_time:
            self._stats.total_duration_seconds = (
                self._stats.end_time - self._stats.start_time
            ).total_seconds()

        if self._stats.dispatched_count > 1:
            self._stats.average_dispatch_interval = (
                self._stats.total_duration_seconds / (self._stats.dispatched_count - 1)
            )

        self._state = OrchestratorState.COMPLETED

    def start(self, route: Route, blocking: bool = False):
        """
        Start orchestrating a route.

        Args:
            route: Route object from route_fetcher
            blocking: If True, blocks until complete. If False, runs in background.
        """
        if self._state == OrchestratorState.RUNNING:
            raise RuntimeError("Orchestrator is already running")

        self._current_route = route
        self._current_index = 0
        self._state = OrchestratorState.RUNNING
        self._stop_event.clear()
        self._stats = OrchestratorStats()

        if blocking:
            self._run_sync()
        else:
            self._thread = threading.Thread(target=self._run_sync, daemon=True)
            self._thread.start()

    def start_from_addresses(
        self,
        source: str,
        destination: str,
        blocking: bool = False,
        api_key: Optional[str] = None,
    ):
        """
        Fetch route and start orchestrating.

        Convenience method that combines route_fetcher with orchestration.

        Args:
            source: Starting address
            destination: Ending address
            blocking: If True, blocks until complete
            api_key: Google Maps API key (optional, uses env var if not provided)
        """
        fetcher = RouteFetcher(api_key=api_key)
        route = fetcher.fetch_route(source, destination)
        self.start(route, blocking=blocking)

    def pause(self):
        """Pause the orchestration."""
        if self._state == OrchestratorState.RUNNING:
            self._state = OrchestratorState.PAUSED
            self.tempo.pause()

    def resume(self):
        """Resume paused orchestration."""
        if self._state == OrchestratorState.PAUSED:
            self._state = OrchestratorState.RUNNING
            self.tempo.resume()

    def stop(self):
        """Stop the orchestration."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._state = OrchestratorState.IDLE

    def skip_to_junction(self, index: int):
        """
        Skip to a specific junction index.

        Args:
            index: Junction index to skip to (0-based)
        """
        if self._current_route and 0 <= index < len(self._current_route.junctions):
            self._current_index = index

    def get_stats(self) -> OrchestratorStats:
        """Get current orchestration statistics."""
        return self._stats

    def get_progress(self) -> dict:
        """Get current progress information."""
        return self.tempo.get_progress(
            self._current_index,
            len(self._current_route.junctions) if self._current_route else 0
        )

    # Async support
    async def start_async(self, route: Route):
        """
        Start orchestrating a route asynchronously.

        Args:
            route: Route object from route_fetcher
        """
        if self._state == OrchestratorState.RUNNING:
            raise RuntimeError("Orchestrator is already running")

        self._current_route = route
        self._current_index = 0
        self._state = OrchestratorState.RUNNING
        self._stats = OrchestratorStats()
        self._stats.start_time = datetime.now()
        self._stats.total_junctions = len(route.junctions)

        schedule = list(self.tempo.generate_schedule(route.junctions, route))

        for index, junction, scheduled_time in schedule:
            if self._state != OrchestratorState.RUNNING:
                break

            # Async wait
            now = datetime.now()
            if scheduled_time > now:
                delay = (scheduled_time - now).total_seconds()
                await asyncio.sleep(delay)

            # Handle pause
            while self._state == OrchestratorState.PAUSED:
                await asyncio.sleep(0.1)

            # Create and dispatch event
            self._current_index = index
            event = self._create_event(junction, index, scheduled_time)
            self._dispatch_event(event)

            self._stats.dispatched_count += 1
            self._stats.dispatch_times.append(event.dispatch_time)

        self._stats.end_time = datetime.now()
        self._state = OrchestratorState.COMPLETED

    def run_once(self, route: Route) -> List[JunctionEvent]:
        """
        Run orchestration synchronously and return all events.

        Useful for testing or batch processing without callbacks.

        Args:
            route: Route to process

        Returns:
            List of all dispatched JunctionEvents
        """
        events = []

        def collect(event: JunctionEvent):
            events.append(event)

        self.register_callback(collect)
        self.start(route, blocking=True)
        self.unregister_callback(collect)

        return events


def create_orchestrator(
    interval_seconds: float = 30.0,
    mode: str = "fixed_interval",
) -> JunctionOrchestrator:
    """
    Factory function to create an orchestrator with common settings.

    Args:
        interval_seconds: Time between junction dispatches (main tempo parameter)
        mode: Dispatch mode ("fixed_interval", "real_time", "manual")

    Returns:
        Configured JunctionOrchestrator
    """
    mode_map = {
        "fixed_interval": DispatchMode.FIXED_INTERVAL,
        "real_time": DispatchMode.REAL_TIME,
        "manual": DispatchMode.MANUAL,
    }

    config = OrchestratorConfig(
        junction_interval_seconds=interval_seconds,
        mode=mode_map.get(mode, DispatchMode.FIXED_INTERVAL),
    )

    return JunctionOrchestrator(config=config)
