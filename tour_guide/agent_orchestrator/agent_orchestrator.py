"""
Main Agent Orchestrator.

Connects the tempo controller to the agent system.
When tempo controller releases a junction, spawns a thread
to process it with all agents.
"""

import logging
import threading
from datetime import datetime
from typing import Optional, Callable, List

from ..route_fetcher.models import Route
from ..route_fetcher import RouteFetcher

from ..junction_orchestrator import JunctionOrchestrator, JunctionEvent
from ..junction_orchestrator.models import OrchestratorConfig

from .models import FinalReport, JunctionResults
from .junction_processor import JunctionProcessor
from .agents import VideoAgent, MusicAgent, HistoryAgent, JudgeAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Main orchestrator connecting tempo controller to agents.

    Architecture:
    1. Receives JunctionEvents from JunctionOrchestrator (tempo controller)
    2. For each junction, spawns a new processing thread
    3. Each processing thread spawns 3 sub-threads (Video, Music, History)
    4. Results collected in queue, Judge picks winner
    5. Winner added to final report
    """

    def __init__(
        self,
        junction_interval_seconds: float = 30.0,
        agent_timeout_seconds: float = 30.0,
        video_agent: Optional[VideoAgent] = None,
        music_agent: Optional[MusicAgent] = None,
        history_agent: Optional[HistoryAgent] = None,
        judge_agent: Optional[JudgeAgent] = None,
    ):
        """
        Initialize the Agent Orchestrator.

        Args:
            junction_interval_seconds: Tempo - seconds between junctions
            agent_timeout_seconds: Max time for agents to respond
            video_agent: Custom video agent (or default)
            music_agent: Custom music agent (or default)
            history_agent: Custom history agent (or default)
            judge_agent: Custom judge agent (or default)
        """
        # Create tempo controller
        self.tempo_orchestrator = JunctionOrchestrator(
            junction_interval_seconds=junction_interval_seconds
        )

        # Create junction processor with agents
        self.processor = JunctionProcessor(
            video_agent=video_agent,
            music_agent=music_agent,
            history_agent=history_agent,
            judge_agent=judge_agent,
            timeout_seconds=agent_timeout_seconds,
        )

        # State
        self._final_report: Optional[FinalReport] = None
        self._active_threads: List[threading.Thread] = []
        self._results_lock = threading.Lock()

        # Callbacks
        self._on_junction_complete: Optional[Callable[[JunctionResults], None]] = None
        self._on_route_complete: Optional[Callable[[FinalReport], None]] = None

        # Register our handler with tempo orchestrator
        self.tempo_orchestrator.register_callback(self._handle_junction_event)

    @property
    def interval(self) -> float:
        """Current junction dispatch interval."""
        return self.tempo_orchestrator.interval

    @interval.setter
    def interval(self, seconds: float):
        """Update junction dispatch interval."""
        self.tempo_orchestrator.interval = seconds

    def on_junction_complete(self, callback: Callable[[JunctionResults], None]):
        """
        Register callback for when a junction is fully processed.

        Args:
            callback: Function receiving JunctionResults
        """
        self._on_junction_complete = callback

    def on_route_complete(self, callback: Callable[[FinalReport], None]):
        """
        Register callback for when entire route is processed.

        Args:
            callback: Function receiving FinalReport
        """
        self._on_route_complete = callback

    def _handle_junction_event(self, event: JunctionEvent):
        """
        Handle junction event from tempo controller.

        Spawns a new thread to process the junction with agents.
        """
        logger.info(f"[JID-{event.junction.junction_id}] Spawning agent processing thread for junction {event.junction_index + 1}")

        # Spawn thread for this junction
        thread = threading.Thread(
            target=self._process_junction_thread,
            args=(event,),
            name=f"AgentOrch-J{event.junction.junction_id}",
            daemon=True,
        )
        self._active_threads.append(thread)
        thread.start()

        logger.debug(f"[JID-{event.junction.junction_id}] Thread spawned: {thread.name}, "
                    f"Total active threads: {len([t for t in self._active_threads if t.is_alive()])}")

    def _process_junction_thread(self, event: JunctionEvent):
        """
        Thread worker that processes a junction with all agents.

        This is where the 4 sub-threads are spawned (inside processor.process).
        """
        junction_id = event.junction.junction_id
        logger.info(f"[JID-{junction_id}] Starting agent processing (Video, Music, History → Judge)")

        try:
            # Process junction (spawns 3 agent threads internally)
            result = self.processor.process(
                junction=event.junction,
                junction_index=event.junction_index,
            )

            # Add to final report (thread-safe)
            with self._results_lock:
                if self._final_report:
                    self._final_report.add_junction_result(result)

            # Log result
            if result.decision:
                logger.info(f"[JID-{junction_id}] Winner: {result.decision.winner_type.value} "
                           f"(score: {result.decision.winning_score:.1f})")
            else:
                logger.warning(f"[JID-{junction_id}] No winner selected")

            # Call user callback if registered
            if self._on_junction_complete:
                try:
                    self._on_junction_complete(result)
                except Exception as e:
                    logger.error(f"[JID-{junction_id}] Junction callback error: {e}", exc_info=True)

            # Check if this was the last junction
            if event.is_last:
                logger.info(f"[JID-{junction_id}] Last junction - finalizing report")
                self._finalize_report()

        except Exception as e:
            logger.error(f"[JID-{junction_id}] Error processing junction: {e}", exc_info=True)

    def _finalize_report(self):
        """Finalize the report when all junctions are processed."""
        # Wait for all processing threads to complete (except current thread)
        current_thread = threading.current_thread()
        for thread in self._active_threads:
            if thread != current_thread and thread.is_alive():
                thread.join(timeout=5.0)

        with self._results_lock:
            if self._final_report:
                self._final_report.completed_at = datetime.now()
                if self._final_report.started_at:
                    self._final_report.total_processing_time_seconds = (
                        self._final_report.completed_at -
                        self._final_report.started_at
                    ).total_seconds()

        # Call route complete callback
        if self._on_route_complete and self._final_report:
            try:
                self._on_route_complete(self._final_report)
            except Exception as e:
                print(f"Route complete callback error: {e}")

    def start(
        self,
        route: Route,
        blocking: bool = True,
    ) -> Optional[FinalReport]:
        """
        Start processing a route.

        Args:
            route: Route from route_fetcher
            blocking: Wait for completion if True

        Returns:
            FinalReport if blocking, None otherwise
        """
        # Initialize final report
        self._final_report = FinalReport(
            source_address=route.source_address,
            destination_address=route.destination_address,
            total_junctions=len(route.junctions),
            started_at=datetime.now(),
        )
        self._active_threads = []

        # Start tempo orchestrator
        self.tempo_orchestrator.start(route, blocking=blocking)

        if blocking:
            # Wait for all processing to complete
            for thread in self._active_threads:
                thread.join(timeout=60.0)

            self._finalize_report()
            return self._final_report

        return None

    def start_from_addresses(
        self,
        source: str,
        destination: str,
        blocking: bool = True,
        api_key: Optional[str] = None,
    ) -> Optional[FinalReport]:
        """
        Fetch route and start processing.

        Args:
            source: Starting address
            destination: Ending address
            blocking: Wait for completion if True
            api_key: Google Maps API key (optional)

        Returns:
            FinalReport if blocking, None otherwise
        """
        fetcher = RouteFetcher(api_key=api_key)
        route = fetcher.fetch_route(source, destination)
        return self.start(route, blocking=blocking)

    def pause(self):
        """Pause junction dispatching."""
        self.tempo_orchestrator.pause()

    def resume(self):
        """Resume junction dispatching."""
        self.tempo_orchestrator.resume()

    def stop(self):
        """Stop all processing."""
        self.tempo_orchestrator.stop()

    def get_report(self) -> Optional[FinalReport]:
        """Get the current final report."""
        return self._final_report

    def get_progress(self) -> dict:
        """Get current processing progress."""
        tempo_progress = self.tempo_orchestrator.get_progress()

        with self._results_lock:
            processed = len(self._final_report.junction_results) if self._final_report else 0

        return {
            **tempo_progress,
            "junctions_processed": processed,
            "active_threads": len([t for t in self._active_threads if t.is_alive()]),
        }


def run_tour_guide(
    source: str,
    destination: str,
    junction_interval: float = 10.0,
    api_key: Optional[str] = None,
    verbose: bool = True,
) -> FinalReport:
    """
    Convenience function to run the complete Tour Guide system.

    Args:
        source: Starting address
        destination: Ending address
        junction_interval: Seconds between junction dispatches
        api_key: Google Maps API key (optional)
        verbose: Print progress if True

    Returns:
        FinalReport with all results
    """
    orchestrator = AgentOrchestrator(
        junction_interval_seconds=junction_interval
    )

    if verbose:
        @orchestrator.on_junction_complete
        def on_complete(result: JunctionResults):
            winner = result.winner
            if winner:
                icon = {"video": "🎬", "music": "🎵", "history": "📖"}.get(
                    result.decision.winner_type.value, "❓"
                )
                print(f"  {icon} Junction {result.junction_index + 1}: "
                      f"{winner.title} ({result.decision.winning_score:.0f}/100)")
            else:
                print(f"  ❌ Junction {result.junction_index + 1}: No winner")

    if verbose:
        print(f"\n🚗 Tour Guide: {source} → {destination}")
        print(f"⏱️  Tempo: {junction_interval}s between junctions")
        print("-" * 50)

    report = orchestrator.start_from_addresses(
        source=source,
        destination=destination,
        blocking=True,
        api_key=api_key,
    )

    if verbose and report:
        report.print_summary()

    return report


# CLI entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python agent_orchestrator.py <source> <destination> [interval]")
        print("Example: python agent_orchestrator.py 'Tel Aviv' 'Jerusalem' 5")
        sys.exit(1)

    source = sys.argv[1]
    destination = sys.argv[2]
    interval = float(sys.argv[3]) if len(sys.argv) > 3 else 10.0

    run_tour_guide(source, destination, junction_interval=interval)
