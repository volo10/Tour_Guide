"""
Agent Implementations.

Contains the four agents:
- VideoAgent: Finds relevant videos for junctions
- MusicAgent: Finds music matching junction atmosphere
- HistoryAgent: Finds historical facts about junctions
- JudgeAgent: Evaluates and picks the winner
"""

import random
import time
import os
from typing import List, Optional

from ..route_fetcher.models import Junction
from .models import AgentResult, AgentType, JudgeDecision
from .base_agent import BaseAgent


class VideoAgent(BaseAgent):
    """
    Agent that finds relevant videos for a junction.

    Searches for street-level videos, walking tours,
    and location-specific content.
    """

    def __init__(self):
        super().__init__(AgentType.VIDEO, "Video Finder")
        self.youtube_api_key: Optional[str] = None

    def initialize(self, api_key: Optional[str] = None):
        """Initialize with optional YouTube API key."""
        super().initialize()
        self.youtube_api_key = api_key or os.environ.get("YOUTUBE_API_KEY")

    def process(self, junction: Junction) -> AgentResult:
        """
        Find a relevant video for the junction.

        In production, this would call YouTube API.
        Currently returns simulated results.
        """
        # Simulate API call delay
        time.sleep(random.uniform(0.1, 0.3))

        # Generate simulated result based on junction
        street = junction.street_name
        address = junction.address

        # Simulated video recommendations
        video_templates = [
            {
                "title": f"{street} Street Walking Tour",
                "description": f"A walking tour through {street}, showing local landmarks and street life.",
                "url": f"https://youtube.com/watch?v=simulated_{junction.junction_id}",
                "relevance": random.uniform(70, 95),
                "quality": random.uniform(75, 90),
            },
            {
                "title": f"Driving Through {address}",
                "description": f"Dash cam footage of driving through the {address} area.",
                "url": f"https://youtube.com/watch?v=drive_{junction.junction_id}",
                "relevance": random.uniform(65, 90),
                "quality": random.uniform(70, 85),
            },
            {
                "title": f"{street} - Local Guide",
                "description": f"A local's guide to the best spots around {street}.",
                "url": f"https://youtube.com/watch?v=guide_{junction.junction_id}",
                "relevance": random.uniform(75, 95),
                "quality": random.uniform(80, 95),
            },
        ]

        # Pick best simulated result
        best = max(video_templates, key=lambda x: x["relevance"] + x["quality"])

        return self._create_result(
            junction=junction,
            title=best["title"],
            description=best["description"],
            url=best["url"],
            relevance_score=best["relevance"],
            quality_score=best["quality"],
            confidence=random.uniform(70, 90),
        )


class MusicAgent(BaseAgent):
    """
    Agent that finds music matching the junction's atmosphere.

    Analyzes the location type and suggests appropriate music.
    """

    def __init__(self):
        super().__init__(AgentType.MUSIC, "Music Finder")
        self.spotify_api_key: Optional[str] = None

    def initialize(self, api_key: Optional[str] = None):
        """Initialize with optional Spotify API key."""
        super().initialize()
        self.spotify_api_key = api_key or os.environ.get("SPOTIFY_API_KEY")

    def process(self, junction: Junction) -> AgentResult:
        """
        Find music matching the junction's atmosphere.

        In production, this would call Spotify API.
        Currently returns simulated results.
        """
        # Simulate API call delay
        time.sleep(random.uniform(0.1, 0.3))

        street = junction.street_name.lower()

        # Determine atmosphere based on keywords
        if any(word in street for word in ["park", "garden", "green"]):
            mood = "calm"
            genre = "ambient"
        elif any(word in street for word in ["main", "central", "downtown"]):
            mood = "energetic"
            genre = "urban"
        elif any(word in street for word in ["beach", "sea", "coast"]):
            mood = "relaxing"
            genre = "chill"
        else:
            mood = "neutral"
            genre = "pop"

        # Simulated music recommendations
        music_templates = {
            "calm": [
                ("Peaceful Morning", "Ambient Sounds", 85, 88),
                ("Garden Breeze", "Nature Vibes", 82, 85),
            ],
            "energetic": [
                ("Urban Pulse", "City Beats", 88, 90),
                ("Downtown Energy", "Metro Mix", 85, 87),
            ],
            "relaxing": [
                ("Ocean Waves", "Beach Sounds", 90, 92),
                ("Coastal Sunset", "Chill Vibes", 87, 89),
            ],
            "neutral": [
                ("Road Trip Mix", "Various Artists", 80, 82),
                ("Driving Playlist", "Top Hits", 78, 80),
            ],
        }

        options = music_templates.get(mood, music_templates["neutral"])
        choice = random.choice(options)

        return self._create_result(
            junction=junction,
            title=choice[0],
            description=f"{genre.title()} music with a {mood} atmosphere, perfect for {junction.street_name}.",
            url=f"https://spotify.com/track/simulated_{junction.junction_id}",
            relevance_score=choice[2] + random.uniform(-5, 5),
            quality_score=choice[3] + random.uniform(-5, 5),
            confidence=random.uniform(75, 92),
        )


class HistoryAgent(BaseAgent):
    """
    Agent that finds historical facts about a junction.

    Researches the history of streets, buildings, and events
    at the location.
    """

    def __init__(self):
        super().__init__(AgentType.HISTORY, "History Finder")

    def process(self, junction: Junction) -> AgentResult:
        """
        Find historical facts about the junction.

        In production, this would search Wikipedia/historical databases.
        Currently returns simulated results.
        """
        # Simulate API call delay
        time.sleep(random.uniform(0.1, 0.4))

        street = junction.street_name
        coords = junction.coordinates

        # Simulated historical facts
        history_templates = [
            {
                "title": f"The History of {street}",
                "description": f"{street} was established in the early 20th century as part of the city's expansion. "
                              f"The street was named after a prominent local figure and has been a key commercial area.",
                "relevance": random.uniform(75, 95),
                "quality": random.uniform(80, 95),
            },
            {
                "title": f"Historical Landmarks at {junction.address}",
                "description": f"This intersection has been a gathering point since the 1920s. "
                              f"Several historic buildings still stand in the area, preserving the architectural heritage.",
                "relevance": random.uniform(70, 90),
                "quality": random.uniform(75, 90),
            },
            {
                "title": f"Local Stories from {street}",
                "description": f"Legend has it that this corner of {street} was where local merchants first "
                              f"set up their stalls in the 1890s, beginning the commercial tradition that continues today.",
                "relevance": random.uniform(80, 95),
                "quality": random.uniform(85, 95),
            },
        ]

        # Pick best simulated result
        best = max(history_templates, key=lambda x: x["relevance"] + x["quality"])

        return self._create_result(
            junction=junction,
            title=best["title"],
            description=best["description"],
            url=f"https://wikipedia.org/wiki/{street.replace(' ', '_')}",
            relevance_score=best["relevance"],
            quality_score=best["quality"],
            confidence=random.uniform(80, 95),
        )


class JudgeAgent(BaseAgent):
    """
    Agent that evaluates contestant results and picks a winner.

    Receives results from Video, Music, and History agents
    and determines which provides the best recommendation.
    """

    def __init__(self):
        super().__init__(AgentType.JUDGE, "Judge")

    def process(self, junction: Junction) -> AgentResult:
        """Not used directly - use evaluate() instead."""
        raise NotImplementedError("JudgeAgent uses evaluate(), not process()")

    def evaluate(
        self,
        junction: Junction,
        contestants: List[AgentResult]
    ) -> JudgeDecision:
        """
        Evaluate contestant results and determine a winner.

        Args:
            junction: The junction being judged
            contestants: List of AgentResults from Video, Music, History agents

        Returns:
            JudgeDecision with the winner and reasoning
        """
        start_time = time.time()

        if not contestants:
            raise ValueError("No contestants to evaluate")

        # Filter out failed results
        valid_contestants = [c for c in contestants if c.is_success]

        if not valid_contestants:
            # All failed - pick first as "winner" with error note
            return JudgeDecision(
                junction_id=junction.junction_id,
                junction_address=junction.address,
                winner=contestants[0],
                winner_type=contestants[0].agent_type,
                winning_score=0,
                contestants=contestants,
                reasoning="All agents failed to produce valid results.",
                decision_time_ms=(time.time() - start_time) * 1000,
            )

        # Calculate judge scores for each contestant
        judge_scores = {}
        for contestant in valid_contestants:
            # Weight the scores
            relevance_weight = 0.45
            quality_weight = 0.30
            confidence_weight = 0.15
            freshness_weight = 0.10  # Bonus for faster processing

            # Calculate weighted score
            score = (
                contestant.relevance_score * relevance_weight +
                contestant.quality_score * quality_weight +
                contestant.confidence * confidence_weight
            )

            # Add freshness bonus (faster = better)
            max_time = 500  # ms
            freshness_bonus = max(0, (max_time - contestant.processing_time_ms) / max_time * 10)
            score += freshness_bonus * freshness_weight

            judge_scores[contestant.agent_type.value] = score

        # Find winner
        winner = max(valid_contestants, key=lambda c: judge_scores[c.agent_type.value])
        winning_score = judge_scores[winner.agent_type.value]

        # Generate reasoning
        reasoning = self._generate_reasoning(winner, valid_contestants, judge_scores)

        return JudgeDecision(
            junction_id=junction.junction_id,
            junction_address=junction.address,
            winner=winner,
            winner_type=winner.agent_type,
            winning_score=winning_score,
            contestants=contestants,
            reasoning=reasoning,
            judge_scores=judge_scores,
            decision_time_ms=(time.time() - start_time) * 1000,
        )

    def _generate_reasoning(
        self,
        winner: AgentResult,
        contestants: List[AgentResult],
        scores: dict
    ) -> str:
        """Generate explanation for the decision."""
        winner_type = winner.agent_type.value.title()
        winner_score = scores[winner.agent_type.value]

        # Find runners up
        others = [c for c in contestants if c != winner]
        if others:
            runner_up = max(others, key=lambda c: scores[c.agent_type.value])
            margin = winner_score - scores[runner_up.agent_type.value]

            if margin > 10:
                return (f"{winner_type} wins decisively with a score of {winner_score:.1f}. "
                       f"'{winner.title}' offers the best combination of relevance and quality.")
            else:
                return (f"{winner_type} narrowly wins with {winner_score:.1f} points. "
                       f"'{winner.title}' edges out the competition by {margin:.1f} points.")

        return f"{winner_type} wins by default with {winner_score:.1f} points."
