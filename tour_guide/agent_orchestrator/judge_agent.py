"""
Judge Agent - Evaluates contestant results and picks a winner.
"""

import time
from typing import List

from ..route_fetcher.models import Junction
from .models import AgentResult, AgentType, JudgeDecision
from .base_agent import BaseAgent

# Scoring constant
FRESHNESS_MAX_TIME_MS = 500


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
            return self._create_failed_decision(junction, contestants, start_time)

        # Calculate scores and find winner
        judge_scores = self._calculate_scores(valid_contestants)
        winner = max(valid_contestants, key=lambda c: judge_scores[c.agent_type.value])
        winning_score = judge_scores[winner.agent_type.value]

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

    def _calculate_scores(self, contestants: List[AgentResult]) -> dict:
        """Calculate weighted scores for each contestant."""
        judge_scores = {}

        for contestant in contestants:
            # Weight configuration
            relevance_weight = 0.45
            quality_weight = 0.30
            confidence_weight = 0.15
            freshness_weight = 0.10

            # Calculate base score
            score = (
                contestant.relevance_score * relevance_weight +
                contestant.quality_score * quality_weight +
                contestant.confidence * confidence_weight
            )

            # Add freshness bonus (faster = better)
            freshness_bonus = max(
                0,
                (FRESHNESS_MAX_TIME_MS - contestant.processing_time_ms) / FRESHNESS_MAX_TIME_MS * 10
            )
            score += freshness_bonus * freshness_weight

            judge_scores[contestant.agent_type.value] = score

        return judge_scores

    def _create_failed_decision(
        self,
        junction: Junction,
        contestants: List[AgentResult],
        start_time: float
    ) -> JudgeDecision:
        """Create decision when all contestants failed."""
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

    def _generate_reasoning(
        self,
        winner: AgentResult,
        contestants: List[AgentResult],
        scores: dict
    ) -> str:
        """Generate explanation for the decision."""
        winner_type = winner.agent_type.value.title()
        winner_score = scores[winner.agent_type.value]

        others = [c for c in contestants if c != winner]
        if others:
            runner_up = max(others, key=lambda c: scores[c.agent_type.value])
            margin = winner_score - scores[runner_up.agent_type.value]

            if margin > 10:
                return (
                    f"{winner_type} wins decisively with a score of {winner_score:.1f}. "
                    f"'{winner.title}' offers the best combination of relevance and quality."
                )
            else:
                return (
                    f"{winner_type} narrowly wins with {winner_score:.1f} points. "
                    f"'{winner.title}' edges out the competition by {margin:.1f} points."
                )

        return f"{winner_type} wins by default with {winner_score:.1f} points."
