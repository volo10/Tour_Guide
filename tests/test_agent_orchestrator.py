"""
Unit tests for the agent_orchestrator module.
"""

import pytest
from tour_guide.agent_orchestrator.models import AgentType, AgentResult, JudgeDecision, FinalReport
from tour_guide.agent_orchestrator.agents import VideoAgent, MusicAgent, HistoryAgent, JudgeAgent
from tour_guide.agent_orchestrator.agent_orchestrator import AgentOrchestrator


class TestAgentType:
    """Tests for AgentType enum."""

    def test_all_types_exist(self):
        """Test that all agent types exist."""
        assert AgentType.VIDEO is not None
        assert AgentType.MUSIC is not None
        assert AgentType.HISTORY is not None
        assert AgentType.JUDGE is not None

    def test_type_values(self):
        """Test that types have string values."""
        assert AgentType.VIDEO.value == "video"
        assert AgentType.MUSIC.value == "music"
        assert AgentType.HISTORY.value == "history"
        assert AgentType.JUDGE.value == "judge"


class TestAgentResult:
    """Tests for AgentResult dataclass."""

    def test_result_creation(self):
        """Test creating an agent result."""
        result = AgentResult(
            agent_type=AgentType.VIDEO,
            agent_name="Video Agent",
            junction_id=1,
            junction_address="Main St",
            title="Test Video",
            description="A test video",
            url="https://example.com/video",
            relevance_score=80.0,
            quality_score=90.0,
            confidence=0.85,
        )
        assert result.agent_type == AgentType.VIDEO
        assert result.title == "Test Video"
        assert result.relevance_score == 80.0

    def test_is_success_property(self):
        """Test is_success property."""
        success_result = AgentResult(
            agent_type=AgentType.VIDEO,
            agent_name="Video Agent",
            junction_id=1,
            junction_address="Main St",
            title="Test",
            description="Test",
        )
        assert success_result.is_success is True

        error_result = AgentResult(
            agent_type=AgentType.VIDEO,
            agent_name="Video Agent",
            junction_id=1,
            junction_address="Main St",
            title="Test",
            description="Test",
            error="Something went wrong",
        )
        assert error_result.is_success is False


class TestVideoAgent:
    """Tests for VideoAgent."""

    def test_agent_creation(self):
        """Test creating video agent."""
        agent = VideoAgent()
        assert agent.agent_type == AgentType.VIDEO
        # Name may vary - just check it exists
        assert agent.name is not None

    def test_process_returns_result(self, sample_junction):
        """Test processing returns an AgentResult."""
        agent = VideoAgent()
        result = agent.process(sample_junction)

        assert isinstance(result, AgentResult)
        assert result.agent_type == AgentType.VIDEO
        assert result.junction_id == sample_junction.junction_id

    def test_process_includes_location_info(self, sample_junction):
        """Test that result includes location information."""
        agent = VideoAgent()
        result = agent.process(sample_junction)

        assert result.junction_address == sample_junction.address


class TestMusicAgent:
    """Tests for MusicAgent."""

    def test_agent_creation(self):
        """Test creating music agent."""
        agent = MusicAgent()
        assert agent.agent_type == AgentType.MUSIC
        assert agent.name is not None

    def test_process_returns_result(self, sample_junction):
        """Test processing returns an AgentResult."""
        agent = MusicAgent()
        result = agent.process(sample_junction)

        assert isinstance(result, AgentResult)
        assert result.agent_type == AgentType.MUSIC


class TestHistoryAgent:
    """Tests for HistoryAgent."""

    def test_agent_creation(self):
        """Test creating history agent."""
        agent = HistoryAgent()
        assert agent.agent_type == AgentType.HISTORY
        assert agent.name is not None

    def test_process_returns_result(self, sample_junction):
        """Test processing returns an AgentResult."""
        agent = HistoryAgent()
        result = agent.process(sample_junction)

        assert isinstance(result, AgentResult)
        assert result.agent_type == AgentType.HISTORY


class TestJudgeAgent:
    """Tests for JudgeAgent."""

    def test_agent_creation(self):
        """Test creating judge agent."""
        agent = JudgeAgent()
        assert agent.agent_type == AgentType.JUDGE
        assert agent.name is not None

    def test_evaluate_picks_winner(self, sample_junction):
        """Test that evaluate picks a winner."""
        agent = JudgeAgent()

        contestants = [
            AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Video",
                junction_id=1,
                junction_address="Test",
                title="Video",
                description="Test",
                relevance_score=80.0,
                quality_score=80.0,
            ),
            AgentResult(
                agent_type=AgentType.MUSIC,
                agent_name="Music",
                junction_id=1,
                junction_address="Test",
                title="Music",
                description="Test",
                relevance_score=90.0,
                quality_score=90.0,
            ),
            AgentResult(
                agent_type=AgentType.HISTORY,
                agent_name="History",
                junction_id=1,
                junction_address="Test",
                title="History",
                description="Test",
                relevance_score=70.0,
                quality_score=70.0,
            ),
        ]

        decision = agent.evaluate(sample_junction, contestants)

        assert isinstance(decision, JudgeDecision)
        assert decision.winner is not None


class TestAgentOrchestrator:
    """Tests for AgentOrchestrator."""

    def test_orchestrator_creation(self):
        """Test creating an agent orchestrator."""
        orchestrator = AgentOrchestrator(
            junction_interval_seconds=5.0,
            agent_timeout_seconds=10.0,
        )
        assert orchestrator.interval == 5.0

    def test_orchestrator_default_values(self):
        """Test default values."""
        orchestrator = AgentOrchestrator()
        assert orchestrator.interval == 30.0

    def test_interval_property(self):
        """Test interval property setter."""
        orchestrator = AgentOrchestrator(junction_interval_seconds=5.0)
        orchestrator.interval = 10.0
        assert orchestrator.interval == 10.0

    def test_start_returns_report(self, minimal_route):
        """Test that start returns a final report."""
        orchestrator = AgentOrchestrator(junction_interval_seconds=0.05)
        report = orchestrator.start(minimal_route, blocking=True)

        assert isinstance(report, FinalReport)
        assert report.total_junctions == minimal_route.junction_count

    def test_get_report(self, minimal_route):
        """Test getting report after completion."""
        orchestrator = AgentOrchestrator(junction_interval_seconds=0.05)
        orchestrator.start(minimal_route, blocking=True)

        report = orchestrator.get_report()
        assert report is not None
        assert isinstance(report, FinalReport)


class TestAgentOrchestratorIntegration:
    """Integration tests for agent orchestrator."""

    def test_full_route_processing(self, sample_route):
        """Test processing a full route."""
        orchestrator = AgentOrchestrator(junction_interval_seconds=0.05)
        report = orchestrator.start(sample_route, blocking=True)

        assert report.total_junctions == sample_route.junction_count
        assert len(report.junction_results) == sample_route.junction_count

    def test_report_has_results(self, minimal_route):
        """Test that report has junction results."""
        orchestrator = AgentOrchestrator(junction_interval_seconds=0.05)
        report = orchestrator.start(minimal_route, blocking=True)

        # Should have results for each junction
        assert len(report.junction_results) > 0
