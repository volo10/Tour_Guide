"""
Tests to improve coverage for agent_orchestrator/models.py.

Targets uncovered lines: to_dict methods, properties, print_summary.
"""

import pytest
from datetime import datetime
from io import StringIO
import sys

from tour_guide.agent_orchestrator.models import (
    AgentType,
    AgentResult,
    JudgeDecision,
    JunctionResults,
    FinalReport,
)
from tour_guide.route_fetcher.models import Junction, Coordinates, TurnDirection


@pytest.fixture
def sample_junction():
    """Create a sample junction for testing."""
    return Junction(
        junction_id=1,
        address="Main St & 1st Ave",
        street_name="Main St",
        coordinates=Coordinates(latitude=32.0, longitude=34.0),
        turn_direction=TurnDirection.LEFT,
        instruction="Turn left onto Main St",
        distance_to_next_meters=500,
        duration_to_next_seconds=60,
        distance_to_next_text="500 m",
        duration_to_next_text="1 min",
    )


@pytest.fixture
def sample_agent_result():
    """Create a sample agent result."""
    return AgentResult(
        agent_type=AgentType.VIDEO,
        agent_name="VideoAgent",
        junction_id=1,
        junction_address="Main St & 1st Ave",
        title="Walking Tour Video",
        description="A beautiful walking tour",
        url="https://youtube.com/watch?v=abc",
        relevance_score=80.0,
        quality_score=75.0,
        confidence=90.0,
        processing_time_ms=1500.0,
    )


class TestAgentResultMethods:
    """Tests for AgentResult methods and properties."""

    def test_overall_score_calculation(self, sample_agent_result):
        """Test overall_score property calculation."""
        result = sample_agent_result
        # Expected: 80*0.5 + 75*0.3 + 90*0.2 = 40 + 22.5 + 18 = 80.5
        expected = (80.0 * 0.5) + (75.0 * 0.3) + (90.0 * 0.2)
        assert result.overall_score == expected

    def test_to_dict_returns_all_fields(self, sample_agent_result):
        """Test to_dict includes all fields."""
        result_dict = sample_agent_result.to_dict()

        assert result_dict['agent_type'] == 'video'
        assert result_dict['agent_name'] == 'VideoAgent'
        assert result_dict['junction_id'] == 1
        assert result_dict['junction_address'] == 'Main St & 1st Ave'
        assert result_dict['title'] == 'Walking Tour Video'
        assert result_dict['description'] == 'A beautiful walking tour'
        assert result_dict['url'] == 'https://youtube.com/watch?v=abc'
        assert result_dict['relevance_score'] == 80.0
        assert result_dict['quality_score'] == 75.0
        assert result_dict['confidence'] == 90.0
        assert 'overall_score' in result_dict
        assert 'timestamp' in result_dict
        assert result_dict['is_success'] is True
        assert result_dict['error'] is None

    def test_to_dict_with_error(self):
        """Test to_dict with error result."""
        result = AgentResult(
            agent_type=AgentType.MUSIC,
            agent_name="MusicAgent",
            junction_id=2,
            junction_address="Test St",
            title="",
            description="",
            error="API timeout",
        )
        result_dict = result.to_dict()
        assert result_dict['is_success'] is False
        assert result_dict['error'] == "API timeout"


class TestJudgeDecisionMethods:
    """Tests for JudgeDecision methods."""

    def test_to_dict_returns_all_fields(self, sample_agent_result):
        """Test JudgeDecision.to_dict includes all fields."""
        decision = JudgeDecision(
            junction_id=1,
            junction_address="Main St & 1st Ave",
            winner=sample_agent_result,
            winner_type=AgentType.VIDEO,
            winning_score=80.5,
            contestants=[sample_agent_result],
            reasoning="Video had highest relevance score",
            judge_scores={"video": 80.5, "music": 70.0, "history": 65.0},
            decision_time_ms=50.0,
        )

        decision_dict = decision.to_dict()

        assert decision_dict['junction_id'] == 1
        assert decision_dict['junction_address'] == 'Main St & 1st Ave'
        assert decision_dict['winner_type'] == 'video'
        assert decision_dict['winning_score'] == 80.5
        assert decision_dict['reasoning'] == "Video had highest relevance score"
        assert len(decision_dict['contestants']) == 1
        assert 'timestamp' in decision_dict


class TestJunctionResultsMethods:
    """Tests for JunctionResults methods and properties."""

    def test_all_results_with_all_agents(self, sample_junction, sample_agent_result):
        """Test all_results returns all non-None results."""
        video_result = sample_agent_result
        music_result = AgentResult(
            agent_type=AgentType.MUSIC,
            agent_name="MusicAgent",
            junction_id=1,
            junction_address="Main St",
            title="Jazz Playlist",
            description="Smooth jazz",
            relevance_score=70.0,
            quality_score=80.0,
            confidence=85.0,
        )
        history_result = AgentResult(
            agent_type=AgentType.HISTORY,
            agent_name="HistoryAgent",
            junction_id=1,
            junction_address="Main St",
            title="History of Main St",
            description="Founded in 1900",
            relevance_score=75.0,
            quality_score=70.0,
            confidence=80.0,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            video_result=video_result,
            music_result=music_result,
            history_result=history_result,
        )

        all_results = jr.all_results
        assert len(all_results) == 3
        assert video_result in all_results
        assert music_result in all_results
        assert history_result in all_results

    def test_all_results_with_partial_results(self, sample_junction, sample_agent_result):
        """Test all_results with only some agents returning results."""
        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            video_result=sample_agent_result,
            music_result=None,
            history_result=None,
        )

        all_results = jr.all_results
        assert len(all_results) == 1
        assert sample_agent_result in all_results

    def test_winner_property_with_decision(self, sample_junction, sample_agent_result):
        """Test winner property when decision exists."""
        decision = JudgeDecision(
            junction_id=1,
            junction_address="Main St",
            winner=sample_agent_result,
            winner_type=AgentType.VIDEO,
            winning_score=80.0,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            video_result=sample_agent_result,
            decision=decision,
        )

        assert jr.winner == sample_agent_result

    def test_winner_property_without_decision(self, sample_junction):
        """Test winner property when no decision."""
        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
        )
        assert jr.winner is None

    def test_to_dict_complete(self, sample_junction, sample_agent_result):
        """Test JunctionResults.to_dict with all data."""
        decision = JudgeDecision(
            junction_id=1,
            junction_address="Main St & 1st Ave",
            winner=sample_agent_result,
            winner_type=AgentType.VIDEO,
            winning_score=80.0,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            video_result=sample_agent_result,
            music_result=None,
            history_result=None,
            decision=decision,
            total_processing_time_ms=2000.0,
            is_complete=True,
            errors=[],
        )

        jr_dict = jr.to_dict()

        assert jr_dict['junction_id'] == 1
        assert jr_dict['junction_index'] == 0
        assert jr_dict['video_result'] is not None
        assert jr_dict['music_result'] is None
        assert jr_dict['history_result'] is None
        assert jr_dict['decision'] is not None
        assert jr_dict['is_complete'] is True


class TestFinalReportMethods:
    """Tests for FinalReport methods and properties."""

    def test_success_rate_with_junctions(self):
        """Test success_rate calculation."""
        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=10,
            failed_junctions=2,
        )
        # (10-2)/10 * 100 = 80%
        assert report.success_rate == 80.0

    def test_success_rate_with_zero_junctions(self):
        """Test success_rate with zero junctions."""
        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=0,
        )
        assert report.success_rate == 0.0

    def test_winners_summary_property(self):
        """Test winners_summary returns correct dict."""
        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=10,
            video_wins=4,
            music_wins=3,
            history_wins=3,
        )

        summary = report.winners_summary
        assert summary == {"video": 4, "music": 3, "history": 3}

    def test_add_junction_result_video_win(self, sample_junction, sample_agent_result):
        """Test add_junction_result with VIDEO winner."""
        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=1,
        )

        decision = JudgeDecision(
            junction_id=1,
            junction_address="Main St",
            winner=sample_agent_result,
            winner_type=AgentType.VIDEO,
            winning_score=80.0,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            video_result=sample_agent_result,
            decision=decision,
            is_complete=True,
        )

        report.add_junction_result(jr)

        assert report.video_wins == 1
        assert report.music_wins == 0
        assert report.history_wins == 0
        assert len(report.junction_results) == 1

    def test_add_junction_result_music_win(self, sample_junction):
        """Test add_junction_result with MUSIC winner."""
        music_result = AgentResult(
            agent_type=AgentType.MUSIC,
            agent_name="MusicAgent",
            junction_id=1,
            junction_address="Main St",
            title="Jazz Vibes",
            description="Smooth jazz playlist",
            relevance_score=85.0,
            quality_score=80.0,
            confidence=90.0,
        )

        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=1,
        )

        decision = JudgeDecision(
            junction_id=1,
            junction_address="Main St",
            winner=music_result,
            winner_type=AgentType.MUSIC,
            winning_score=85.0,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            music_result=music_result,
            decision=decision,
            is_complete=True,
        )

        report.add_junction_result(jr)

        assert report.video_wins == 0
        assert report.music_wins == 1
        assert report.history_wins == 0

    def test_add_junction_result_history_win(self, sample_junction):
        """Test add_junction_result with HISTORY winner."""
        history_result = AgentResult(
            agent_type=AgentType.HISTORY,
            agent_name="HistoryAgent",
            junction_id=1,
            junction_address="Main St",
            title="Historic Main St",
            description="Founded in 1850",
            relevance_score=90.0,
            quality_score=85.0,
            confidence=95.0,
        )

        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=1,
        )

        decision = JudgeDecision(
            junction_id=1,
            junction_address="Main St",
            winner=history_result,
            winner_type=AgentType.HISTORY,
            winning_score=90.0,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            history_result=history_result,
            decision=decision,
            is_complete=True,
        )

        report.add_junction_result(jr)

        assert report.video_wins == 0
        assert report.music_wins == 0
        assert report.history_wins == 1

    def test_add_junction_result_with_errors(self, sample_junction):
        """Test add_junction_result increments error counts."""
        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=1,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            is_complete=False,
            errors=["Timeout", "API Error"],
        )

        report.add_junction_result(jr)

        assert report.total_errors == 2
        assert report.failed_junctions == 1

    def test_to_dict_complete(self, sample_junction, sample_agent_result):
        """Test FinalReport.to_dict with all data."""
        report = FinalReport(
            source_address="Tel Aviv",
            destination_address="Jerusalem",
            total_junctions=5,
            total_processing_time_seconds=30.0,
            started_at=datetime(2024, 1, 1, 10, 0, 0),
            completed_at=datetime(2024, 1, 1, 10, 0, 30),
            video_wins=2,
            music_wins=2,
            history_wins=1,
            failed_junctions=0,
            total_errors=0,
        )

        report_dict = report.to_dict()

        assert report_dict['source_address'] == 'Tel Aviv'
        assert report_dict['destination_address'] == 'Jerusalem'
        assert report_dict['total_junctions'] == 5
        assert report_dict['total_processing_time_seconds'] == 30.0
        assert report_dict['started_at'] == '2024-01-01T10:00:00'
        assert report_dict['completed_at'] == '2024-01-01T10:00:30'
        assert report_dict['winners_summary'] == {"video": 2, "music": 2, "history": 1}
        assert report_dict['success_rate'] == 100.0
        assert report_dict['failed_junctions'] == 0
        assert report_dict['total_errors'] == 0

    def test_to_dict_with_none_timestamps(self):
        """Test to_dict handles None timestamps."""
        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=1,
            started_at=None,
            completed_at=None,
        )

        report_dict = report.to_dict()
        assert report_dict['started_at'] is None
        assert report_dict['completed_at'] is None

    def test_print_summary_outputs_correctly(self, sample_junction, sample_agent_result):
        """Test print_summary produces expected output."""
        decision = JudgeDecision(
            junction_id=1,
            junction_address="Main St & 1st Ave",
            winner=sample_agent_result,
            winner_type=AgentType.VIDEO,
            winning_score=80.0,
        )

        jr = JunctionResults(
            junction=sample_junction,
            junction_index=0,
            video_result=sample_agent_result,
            decision=decision,
            is_complete=True,
        )

        report = FinalReport(
            source_address="Tel Aviv",
            destination_address="Jerusalem",
            total_junctions=1,
            total_processing_time_seconds=15.5,
            video_wins=1,
            music_wins=0,
            history_wins=0,
        )
        report.junction_results.append(jr)

        # Capture stdout
        captured = StringIO()
        sys.stdout = captured

        report.print_summary()

        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        # Verify output contains expected elements
        assert "TOUR GUIDE FINAL REPORT" in output
        assert "Tel Aviv" in output
        assert "Jerusalem" in output
        assert "Video Wins" in output
        assert "Music Wins" in output
        assert "History Wins" in output
        assert "JUNCTION WINNERS" in output
        assert "Walking Tour Video" in output

    def test_print_summary_no_decisions(self):
        """Test print_summary with no decisions."""
        report = FinalReport(
            source_address="A",
            destination_address="B",
            total_junctions=0,
        )

        # Should not raise even with empty results
        captured = StringIO()
        sys.stdout = captured

        report.print_summary()

        sys.stdout = sys.__stdout__
        output = captured.getvalue()

        assert "TOUR GUIDE FINAL REPORT" in output
