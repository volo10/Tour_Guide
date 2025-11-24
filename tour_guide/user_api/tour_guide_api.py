"""
Tour Guide API - Main Python Interface.

Provides a simple API for users to get tour guide recommendations
for a route between source and destination.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..route_fetcher import RouteFetcher
from ..route_fetcher.models import Route
from ..agent_orchestrator import AgentOrchestrator
from ..agent_orchestrator.models import FinalReport, JunctionResults, AgentType

logger = logging.getLogger(__name__)


@dataclass
class JunctionWinner:
    """Simplified winner info for a single junction."""
    junction_number: int
    junction_address: str
    turn_direction: str
    winner_type: str  # "video", "music", or "history"
    winner_title: str
    winner_description: str
    winner_url: Optional[str]
    score: float

    def to_dict(self) -> dict:
        return {
            "junction_number": self.junction_number,
            "junction_address": self.junction_address,
            "turn_direction": self.turn_direction,
            "winner_type": self.winner_type,
            "winner_title": self.winner_title,
            "winner_description": self.winner_description,
            "winner_url": self.winner_url,
            "score": self.score,
        }


@dataclass
class TourGuideResult:
    """
    Result from Tour Guide API containing winners per junction.

    This is the main output users receive.
    """
    # Route info
    source: str
    destination: str
    total_distance: str
    total_duration: str

    # Winners per junction
    winners: List[JunctionWinner] = field(default_factory=list)

    # Summary
    total_junctions: int = 0
    video_wins: int = 0
    music_wins: int = 0
    history_wins: int = 0

    # Timing
    processing_time_seconds: float = 0.0

    # Status
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source,
            "destination": self.destination,
            "total_distance": self.total_distance,
            "total_duration": self.total_duration,
            "total_junctions": self.total_junctions,
            "winners": [w.to_dict() for w in self.winners],
            "summary": {
                "video_wins": self.video_wins,
                "music_wins": self.music_wins,
                "history_wins": self.history_wins,
            },
            "processing_time_seconds": self.processing_time_seconds,
            "success": self.success,
            "error": self.error,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def print_winners(self):
        """Print formatted winners list."""
        icons = {"video": "🎬", "music": "🎵", "history": "📖"}

        print(f"\n{'='*60}")
        print(f"🚗 TOUR GUIDE RESULTS")
        print(f"{'='*60}")
        print(f"Route: {self.source} → {self.destination}")
        print(f"Distance: {self.total_distance} | Duration: {self.total_duration}")
        print(f"{'='*60}")

        print(f"\n📍 WINNERS PER JUNCTION:\n")
        for w in self.winners:
            icon = icons.get(w.winner_type, "❓")
            print(f"  {w.junction_number}. {w.junction_address}")
            print(f"     Turn: {w.turn_direction}")
            print(f"     {icon} {w.winner_type.upper()}: {w.winner_title}")
            print(f"     Score: {w.score:.0f}/100")
            if w.winner_url:
                print(f"     URL: {w.winner_url}")
            print()

        print(f"{'='*60}")
        print(f"📊 SUMMARY:")
        print(f"   🎬 Video Wins:   {self.video_wins}")
        print(f"   🎵 Music Wins:   {self.music_wins}")
        print(f"   📖 History Wins: {self.history_wins}")
        print(f"   ⏱️  Processing:   {self.processing_time_seconds:.2f}s")
        print(f"{'='*60}\n")


class TourGuideAPI:
    """
    Main API for the Tour Guide system.

    Provides a simple interface to get recommendations for a route.
    """

    def __init__(
        self,
        junction_interval_seconds: float = 5.0,
        google_maps_api_key: Optional[str] = None,
    ):
        """
        Initialize the Tour Guide API.

        Args:
            junction_interval_seconds: Time between processing junctions
            google_maps_api_key: Google Maps API key (or uses env var)
        """
        self.junction_interval = junction_interval_seconds
        self.api_key = google_maps_api_key

    def get_tour(
        self,
        source: str,
        destination: str,
        verbose: bool = False,
    ) -> TourGuideResult:
        """
        Get tour guide recommendations for a route.

        Args:
            source: Starting address
            destination: Ending address
            verbose: Print progress if True

        Returns:
            TourGuideResult with winners per junction
        """
        start_time = datetime.now()
        logger.info(f"TourGuideAPI.get_tour() called: '{source}' → '{destination}'")

        try:
            # Create orchestrator
            orchestrator = AgentOrchestrator(
                junction_interval_seconds=self.junction_interval
            )

            if verbose:
                print(f"\n🚗 Processing route: {source} → {destination}")
                print(f"⏱️  Tempo: {self.junction_interval}s per junction")
                print("-" * 40)

                @orchestrator.on_junction_complete
                def on_complete(result: JunctionResults):
                    if result.decision:
                        icon = {"video": "🎬", "music": "🎵", "history": "📖"}.get(
                            result.decision.winner_type.value, "❓"
                        )
                        print(f"  {icon} Junction {result.junction_index + 1}: {result.decision.winner.title}")

            # Run the system
            logger.info("Starting agent orchestrator...")
            report = orchestrator.start_from_addresses(
                source=source,
                destination=destination,
                blocking=True,
                api_key=self.api_key,
            )

            # Convert to TourGuideResult
            result = self._convert_report(report)
            result.processing_time_seconds = (datetime.now() - start_time).total_seconds()

            logger.info(f"Tour complete: {result.total_junctions} junctions, "
                       f"{result.video_wins} video / {result.music_wins} music / {result.history_wins} history wins")

            return result

        except Exception as e:
            logger.error(f"Error getting tour: {e}", exc_info=True)
            return TourGuideResult(
                source=source,
                destination=destination,
                total_distance="N/A",
                total_duration="N/A",
                success=False,
                error=str(e),
                processing_time_seconds=(datetime.now() - start_time).total_seconds(),
            )

    def _convert_report(self, report: FinalReport) -> TourGuideResult:
        """Convert FinalReport to TourGuideResult."""
        winners = []

        for jr in report.junction_results:
            if jr.decision:
                winner = JunctionWinner(
                    junction_number=jr.junction_index + 1,
                    junction_address=jr.junction.address,
                    turn_direction=jr.junction.turn_direction.value,
                    winner_type=jr.decision.winner_type.value,
                    winner_title=jr.decision.winner.title,
                    winner_description=jr.decision.winner.description,
                    winner_url=jr.decision.winner.url,
                    score=jr.decision.winning_score,
                )
                winners.append(winner)

        return TourGuideResult(
            source=report.source_address,
            destination=report.destination_address,
            total_distance="N/A",  # Could be fetched from route
            total_duration="N/A",
            winners=winners,
            total_junctions=report.total_junctions,
            video_wins=report.video_wins,
            music_wins=report.music_wins,
            history_wins=report.history_wins,
            success=True,
        )

    def get_tour_json(
        self,
        source: str,
        destination: str,
    ) -> str:
        """
        Get tour recommendations as JSON string.

        Args:
            source: Starting address
            destination: Ending address

        Returns:
            JSON string with results
        """
        result = self.get_tour(source, destination)
        return result.to_json()


# Convenience function
def get_tour_winners(
    source: str,
    destination: str,
    interval: float = 5.0,
    verbose: bool = True,
) -> TourGuideResult:
    """
    Simple function to get tour guide winners for a route.

    Args:
        source: Starting address
        destination: Ending address
        interval: Seconds between junction processing
        verbose: Print progress

    Returns:
        TourGuideResult with winners
    """
    api = TourGuideAPI(junction_interval_seconds=interval)
    result = api.get_tour(source, destination, verbose=verbose)

    if verbose:
        result.print_winners()

    return result
