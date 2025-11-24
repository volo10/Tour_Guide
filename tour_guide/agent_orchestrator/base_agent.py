"""
Base Agent Interface.

Defines the abstract interface that all agents must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional
import time

from ..route_fetcher.models import Junction
from .models import AgentResult, AgentType


class BaseAgent(ABC):
    """
    Abstract base class for all Tour Guide agents.

    Each agent (Video, Music, History, Judge) must implement
    the process() method to handle junction processing.
    """

    def __init__(self, agent_type: AgentType, name: str):
        """
        Initialize the agent.

        Args:
            agent_type: Type of agent (VIDEO, MUSIC, HISTORY, JUDGE)
            name: Human-readable name for the agent
        """
        self.agent_type = agent_type
        self.name = name
        self._is_initialized = False

    def initialize(self):
        """
        Initialize agent resources (API connections, etc.).

        Override this method to set up any required resources.
        """
        self._is_initialized = True

    def cleanup(self):
        """
        Clean up agent resources.

        Override this method to release any resources.
        """
        self._is_initialized = False

    @abstractmethod
    def process(self, junction: Junction) -> AgentResult:
        """
        Process a junction and return a result.

        This is the main method each agent must implement.

        Args:
            junction: The junction to process

        Returns:
            AgentResult with the agent's recommendation
        """
        pass

    def process_with_timing(self, junction: Junction) -> AgentResult:
        """
        Process a junction with timing measurement.

        Wraps the process() method to measure execution time.

        Args:
            junction: The junction to process

        Returns:
            AgentResult with processing_time_ms populated
        """
        start_time = time.time()

        try:
            result = self.process(junction)
            result.processing_time_ms = (time.time() - start_time) * 1000
            return result
        except Exception as e:
            # Return error result
            return AgentResult(
                agent_type=self.agent_type,
                agent_name=self.name,
                junction_id=junction.junction_id,
                junction_address=junction.address,
                title="",
                description="",
                processing_time_ms=(time.time() - start_time) * 1000,
                error=str(e),
            )

    def _create_result(
        self,
        junction: Junction,
        title: str,
        description: str,
        url: Optional[str] = None,
        relevance_score: float = 0.0,
        quality_score: float = 0.0,
        confidence: float = 0.0,
        raw_data: Optional[dict] = None,
    ) -> AgentResult:
        """
        Helper to create an AgentResult.

        Args:
            junction: The processed junction
            title: Title of the recommendation
            description: Description of the recommendation
            url: Optional URL to content
            relevance_score: Relevance to junction (0-100)
            quality_score: Quality of content (0-100)
            confidence: Agent's confidence (0-100)
            raw_data: Optional raw API response

        Returns:
            Populated AgentResult
        """
        return AgentResult(
            agent_type=self.agent_type,
            agent_name=self.name,
            junction_id=junction.junction_id,
            junction_address=junction.address,
            title=title,
            description=description,
            url=url,
            relevance_score=relevance_score,
            quality_score=quality_score,
            confidence=confidence,
            raw_data=raw_data,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.agent_type.value}, name='{self.name}')"
