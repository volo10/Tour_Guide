"""
Unit tests for the junction_processor module.
"""

import pytest
import threading
import time
from unittest.mock import MagicMock, patch

from tour_guide.agent_orchestrator.junction_processor import (
    JunctionProcessor,
    ThreadedJunctionProcessor
)
from tour_guide.agent_orchestrator.models import AgentResult, AgentType, JunctionResults
from tour_guide.agent_orchestrator.agents import VideoAgent, MusicAgent, HistoryAgent, JudgeAgent
from tour_guide.route_fetcher.models import Junction, Coordinates, TurnDirection


@pytest.fixture
def mock_video_agent():
    """Create a mock video agent."""
    agent = MagicMock(spec=VideoAgent)
    agent.agent_type = AgentType.VIDEO
    agent.name = "Mock Video Agent"
    agent.process_with_timing.return_value = AgentResult(
        agent_type=AgentType.VIDEO,
        agent_name="Mock Video Agent",
        junction_id=1,
        junction_address="Test Address",
        title="Test Video",
        description="A test video",
        url="https://youtube.com/watch?v=test",
        relevance_score=85.0,
        quality_score=80.0,
        confidence=90.0,
        processing_time_ms=100.0,
    )
    return agent


@pytest.fixture
def mock_music_agent():
    """Create a mock music agent."""
    agent = MagicMock(spec=MusicAgent)
    agent.agent_type = AgentType.MUSIC
    agent.name = "Mock Music Agent"
    agent.process_with_timing.return_value = AgentResult(
        agent_type=AgentType.MUSIC,
        agent_name="Mock Music Agent",
        junction_id=1,
        junction_address="Test Address",
        title="Test Song",
        description="A test song",
        url="https://spotify.com/track/test",
        relevance_score=75.0,
        quality_score=85.0,
        confidence=88.0,
        processing_time_ms=150.0,
    )
    return agent


@pytest.fixture
def mock_history_agent():
    """Create a mock history agent."""
    agent = MagicMock(spec=HistoryAgent)
    agent.agent_type = AgentType.HISTORY
    agent.name = "Mock History Agent"
    agent.process_with_timing.return_value = AgentResult(
        agent_type=AgentType.HISTORY,
        agent_name="Mock History Agent",
        junction_id=1,
        junction_address="Test Address",
        title="Historical Facts",
        description="Some history",
        url="https://wikipedia.org/wiki/test",
        relevance_score=70.0,
        quality_score=90.0,
        confidence=85.0,
        processing_time_ms=200.0,
    )
    return agent


@pytest.fixture
def mock_judge_agent():
    """Create a mock judge agent."""
    agent = MagicMock(spec=JudgeAgent)
    agent.agent_type = AgentType.JUDGE
    agent.name = "Mock Judge Agent"
    return agent


class TestJunctionProcessorInit:
    """Tests for JunctionProcessor initialization."""

    def test_processor_creation_with_defaults(self):
        """Test creating processor with default agents."""
        processor = JunctionProcessor()
        assert processor.video_agent is not None
        assert processor.music_agent is not None
        assert processor.history_agent is not None
        assert processor.judge_agent is not None
        assert processor.timeout == 30.0

    def test_processor_creation_with_custom_timeout(self):
        """Test creating processor with custom timeout."""
        processor = JunctionProcessor(timeout_seconds=60.0)
        assert processor.timeout == 60.0

    def test_processor_creation_with_custom_agents(
        self,
        mock_video_agent,
        mock_music_agent,
        mock_history_agent,
        mock_judge_agent
    ):
        """Test creating processor with custom agents."""
        processor = JunctionProcessor(
            video_agent=mock_video_agent,
            music_agent=mock_music_agent,
            history_agent=mock_history_agent,
            judge_agent=mock_judge_agent,
        )
        assert processor.video_agent == mock_video_agent
        assert processor.music_agent == mock_music_agent
        assert processor.history_agent == mock_history_agent
        assert processor.judge_agent == mock_judge_agent


class TestJunctionProcessorProcess:
    """Tests for JunctionProcessor.process()."""

    def test_process_returns_junction_results(self, sample_junction):
        """Test that process returns JunctionResults."""
        processor = JunctionProcessor(timeout_seconds=5.0)
        result = processor.process(sample_junction, junction_index=0)

        assert isinstance(result, JunctionResults)
        assert result.junction == sample_junction
        assert result.junction_index == 0

    def test_process_includes_timing(self, sample_junction):
        """Test that process includes timing information."""
        processor = JunctionProcessor(timeout_seconds=5.0)
        result = processor.process(sample_junction, junction_index=0)

        assert result.started_at is not None
        assert result.completed_at is not None
        assert result.total_processing_time_ms > 0

    def test_process_collects_agent_results(
        self,
        sample_junction,
        mock_video_agent,
        mock_music_agent,
        mock_history_agent,
        mock_judge_agent
    ):
        """Test that process collects results from all agents."""
        # Setup mock judge to return a decision
        from tour_guide.agent_orchestrator.models import JudgeDecision
        mock_judge_agent.evaluate.return_value = JudgeDecision(
            junction_id=1,
            junction_address="Test",
            winner=mock_video_agent.process_with_timing.return_value,
            winner_type=AgentType.VIDEO,
            winning_score=85.0,
            contestants=[],
            reasoning="Video wins"
        )

        processor = JunctionProcessor(
            video_agent=mock_video_agent,
            music_agent=mock_music_agent,
            history_agent=mock_history_agent,
            judge_agent=mock_judge_agent,
            timeout_seconds=5.0,
        )
        result = processor.process(sample_junction, junction_index=0)

        # Verify agents were called
        mock_video_agent.process_with_timing.assert_called_once_with(sample_junction)
        mock_music_agent.process_with_timing.assert_called_once_with(sample_junction)
        mock_history_agent.process_with_timing.assert_called_once_with(sample_junction)

    def test_process_handles_agent_timeout(self, sample_junction):
        """Test that process handles agent timeouts gracefully."""
        # Create a slow agent
        slow_agent = MagicMock(spec=VideoAgent)
        slow_agent.agent_type = AgentType.VIDEO
        slow_agent.name = "Slow Agent"

        def slow_process(junction):
            time.sleep(10)  # Sleep longer than timeout
            return AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Slow Agent",
                junction_id=1,
                junction_address="Test",
                title="Late Result",
                description="",
            )

        slow_agent.process_with_timing.side_effect = slow_process

        processor = JunctionProcessor(
            video_agent=slow_agent,
            timeout_seconds=0.5,  # Short timeout
        )

        result = processor.process(sample_junction, junction_index=0)

        # Should complete without hanging
        assert result is not None
        # Should have errors about timeout
        assert len(result.errors) > 0 or result.video_result is None


class TestJunctionProcessorProcessAsync:
    """Tests for JunctionProcessor.process_async()."""

    def test_process_async_returns_thread(self, sample_junction):
        """Test that process_async returns a thread."""
        processor = JunctionProcessor(timeout_seconds=5.0)
        callback = MagicMock()

        thread = processor.process_async(sample_junction, 0, callback)

        assert isinstance(thread, threading.Thread)
        assert thread.is_alive()

        # Wait for completion
        thread.join(timeout=10.0)

    def test_process_async_calls_callback(self, sample_junction):
        """Test that process_async calls the callback."""
        processor = JunctionProcessor(timeout_seconds=5.0)
        callback = MagicMock()

        thread = processor.process_async(sample_junction, 0, callback)
        thread.join(timeout=10.0)

        callback.assert_called_once()
        args = callback.call_args[0]
        assert isinstance(args[0], JunctionResults)


class TestThreadedJunctionProcessor:
    """Tests for ThreadedJunctionProcessor."""

    def test_threaded_processor_creation(self):
        """Test creating threaded processor."""
        processor = ThreadedJunctionProcessor(max_concurrent_junctions=5)
        assert processor.max_concurrent == 5

    def test_process_batch_returns_ordered_results(self, sample_junctions):
        """Test that process_batch returns results in order."""
        processor = ThreadedJunctionProcessor(
            max_concurrent_junctions=2,
            timeout_seconds=5.0,
        )

        results = processor.process_batch(sample_junctions)

        assert len(results) == len(sample_junctions)
        for i, result in enumerate(results):
            assert result.junction_index == i

    def test_process_batch_with_callback(self, sample_junctions):
        """Test process_batch with completion callback."""
        processor = ThreadedJunctionProcessor(
            max_concurrent_junctions=2,
            timeout_seconds=5.0,
        )
        callback = MagicMock()

        results = processor.process_batch(sample_junctions, on_complete=callback)

        # Callback should be called for each junction
        assert callback.call_count == len(sample_junctions)


class TestJunctionProcessorAgentWorker:
    """Tests for JunctionProcessor._agent_worker()."""

    def test_agent_worker_puts_result_in_queue(
        self,
        sample_junction,
        mock_video_agent
    ):
        """Test that agent worker puts result in queue."""
        import queue

        processor = JunctionProcessor(
            video_agent=mock_video_agent,
            timeout_seconds=5.0,
        )
        results_queue = queue.Queue()

        processor._agent_worker(mock_video_agent, sample_junction, results_queue)

        assert not results_queue.empty()
        result = results_queue.get()
        assert result.agent_type == AgentType.VIDEO

    def test_agent_worker_handles_exception(self, sample_junction):
        """Test that agent worker handles exceptions."""
        import queue

        failing_agent = MagicMock(spec=VideoAgent)
        failing_agent.agent_type = AgentType.VIDEO
        failing_agent.name = "Failing Agent"
        failing_agent.process_with_timing.side_effect = Exception("Agent failed")

        processor = JunctionProcessor(
            video_agent=failing_agent,
            timeout_seconds=5.0,
        )
        results_queue = queue.Queue()

        processor._agent_worker(failing_agent, sample_junction, results_queue)

        # Should still put an error result
        assert not results_queue.empty()
        result = results_queue.get()
        assert result.error is not None
        assert "Agent failed" in result.error
