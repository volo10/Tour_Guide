"""
Detailed unit tests for agent implementations.

Tests for:
- VideoAgent query building and YouTube search
- MusicAgent Spotify integration
- HistoryAgent Wikipedia search
- JudgeAgent evaluation logic
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from tour_guide.agent_orchestrator.agents import (
    VideoAgent,
    MusicAgent,
    HistoryAgent,
    JudgeAgent,
)
from tour_guide.agent_orchestrator.models import AgentResult, AgentType, JudgeDecision
from tour_guide.route_fetcher.models import Junction, Coordinates, TurnDirection


@pytest.fixture
def tel_aviv_junction():
    """Create a junction in Tel Aviv for testing."""
    return Junction(
        junction_id=1,
        address="Rothschild Boulevard, Tel Aviv",
        street_name="Rothschild Boulevard",
        coordinates=Coordinates(32.0636, 34.7728),
        turn_direction=TurnDirection.LEFT,
        instruction="Turn left onto Rothschild Boulevard",
        distance_to_next_meters=500,
        distance_to_next_text="500 m",
        duration_to_next_seconds=60,
        duration_to_next_text="1 min",
    )


@pytest.fixture
def jerusalem_junction():
    """Create a junction in Jerusalem for testing."""
    return Junction(
        junction_id=2,
        address="King David Street, Jerusalem",
        street_name="King David Street",
        coordinates=Coordinates(31.7767, 35.2264),
        turn_direction=TurnDirection.RIGHT,
        instruction="Turn right onto King David Street",
        distance_to_next_meters=300,
        distance_to_next_text="300 m",
        duration_to_next_seconds=45,
        duration_to_next_text="45 sec",
    )


class TestVideoAgentQueryBuilding:
    """Tests for VideoAgent._build_creative_queries()."""

    def test_build_queries_for_tel_aviv(self, tel_aviv_junction):
        """Test query building for Tel Aviv location."""
        agent = VideoAgent()
        queries = agent._build_creative_queries(
            tel_aviv_junction.street_name,
            tel_aviv_junction.address
        )

        assert len(queries) > 0
        # Should include city-based queries
        assert any("Tel Aviv" in q for q in queries)

    def test_build_queries_for_jerusalem(self, jerusalem_junction):
        """Test query building for Jerusalem location."""
        agent = VideoAgent()
        queries = agent._build_creative_queries(
            jerusalem_junction.street_name,
            jerusalem_junction.address
        )

        assert len(queries) > 0
        assert any("Jerusalem" in q for q in queries)

    def test_build_queries_removes_navigation_instructions(self):
        """Test that navigation instructions are cleaned from queries."""
        agent = VideoAgent()
        queries = agent._build_creative_queries(
            "Turn left onto Main Street",
            "Main Street, Tel Aviv"
        )

        # Should not include "Turn left" in queries
        for query in queries:
            assert "Turn left" not in query

    def test_build_queries_limits_count(self):
        """Test that queries are limited."""
        agent = VideoAgent()
        queries = agent._build_creative_queries(
            "A very long street name with many words",
            "Address with city"
        )

        assert len(queries) <= 8


class TestVideoAgentSearch:
    """Tests for VideoAgent._search_youtube()."""

    @patch('tour_guide.agent_orchestrator.agents.requests.get')
    def test_search_youtube_success(self, mock_get, tel_aviv_junction):
        """Test successful YouTube search."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{
                "id": {"videoId": "abc123"},
                "snippet": {
                    "title": "Tel Aviv Walking Tour",
                    "description": "A beautiful tour of Tel Aviv",
                    "channelTitle": "Travel Channel"
                }
            }]
        }
        mock_get.return_value = mock_response

        agent = VideoAgent()
        agent.initialize(api_key="test_key")
        result = agent._search_youtube(
            tel_aviv_junction.street_name,
            tel_aviv_junction.address,
            tel_aviv_junction
        )

        assert result is not None
        assert result.agent_type == AgentType.VIDEO
        assert "youtube.com" in result.url

    @patch('tour_guide.agent_orchestrator.agents.requests.get')
    def test_search_youtube_no_results(self, mock_get, tel_aviv_junction):
        """Test YouTube search with no results."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": []}
        mock_get.return_value = mock_response

        agent = VideoAgent()
        agent.initialize(api_key="test_key")
        result = agent._search_youtube(
            tel_aviv_junction.street_name,
            tel_aviv_junction.address,
            tel_aviv_junction
        )

        assert result is None

    @patch('tour_guide.agent_orchestrator.agents.requests.get')
    def test_search_youtube_api_error(self, mock_get, tel_aviv_junction):
        """Test YouTube search with API error."""
        mock_get.side_effect = Exception("API Error")

        agent = VideoAgent()
        agent.initialize(api_key="test_key")
        result = agent._search_youtube(
            tel_aviv_junction.street_name,
            tel_aviv_junction.address,
            tel_aviv_junction
        )

        assert result is None


class TestMusicAgentQueryBuilding:
    """Tests for MusicAgent._build_search_queries()."""

    def test_build_queries_for_location(self, tel_aviv_junction):
        """Test query building for music search."""
        agent = MusicAgent()
        queries = agent._build_search_queries(
            tel_aviv_junction.street_name,
            tel_aviv_junction.address
        )

        assert len(queries) > 0

    def test_build_queries_includes_city(self, tel_aviv_junction):
        """Test that city is included in queries."""
        agent = MusicAgent()
        queries = agent._build_search_queries(
            tel_aviv_junction.street_name,
            tel_aviv_junction.address
        )

        assert any("Tel Aviv" in q for q in queries)

    def test_build_queries_with_word_associations(self):
        """Test word association queries."""
        agent = MusicAgent()
        queries = agent._build_search_queries(
            "Highway 1",
            "Highway 1, Israel"
        )

        # Should include highway-related songs
        assert any("highway" in q.lower() or "Highway" in q for q in queries)


class TestMusicAgentSpotifyAuth:
    """Tests for MusicAgent Spotify authentication."""

    @patch('tour_guide.agent_orchestrator.agents.requests.post')
    def test_get_spotify_token_success(self, mock_post):
        """Test successful Spotify token retrieval."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token_123",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        agent = MusicAgent()
        agent.initialize(client_id="test_id", client_secret="test_secret")
        token = agent._get_spotify_token()

        assert token == "test_token_123"

    @patch('tour_guide.agent_orchestrator.agents.requests.post')
    def test_get_spotify_token_caching(self, mock_post):
        """Test that Spotify token is cached."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token_123",
            "expires_in": 3600
        }
        mock_post.return_value = mock_response

        agent = MusicAgent()
        agent.initialize(client_id="test_id", client_secret="test_secret")

        # First call
        token1 = agent._get_spotify_token()
        # Second call should use cache
        token2 = agent._get_spotify_token()

        assert token1 == token2
        # Should only call API once
        assert mock_post.call_count == 1


class TestHistoryAgentSearchTerms:
    """Tests for HistoryAgent._get_search_terms()."""

    def test_get_search_terms_israeli_figures(self):
        """Test search terms for Israeli street names."""
        agent = HistoryAgent()
        terms = agent._get_search_terms(
            "Herzl Street",
            "Herzl Street, Tel Aviv"
        )

        # Should include Theodor Herzl
        assert any("Herzl" in t for t in terms)

    def test_get_search_terms_removes_navigation(self):
        """Test that navigation instructions are cleaned."""
        agent = HistoryAgent()
        terms = agent._get_search_terms(
            "Turn right onto Ben Gurion Blvd",
            "Ben Gurion Blvd, Tel Aviv"
        )

        for term in terms:
            assert "Turn right" not in term

    def test_get_search_terms_includes_city_history(self, tel_aviv_junction):
        """Test that city history is included as fallback."""
        agent = HistoryAgent()
        terms = agent._get_search_terms(
            tel_aviv_junction.street_name,
            tel_aviv_junction.address
        )

        assert any("Tel Aviv" in t for t in terms)


class TestHistoryAgentCleanHtml:
    """Tests for HistoryAgent._clean_html()."""

    def test_clean_html_removes_tags(self):
        """Test HTML tag removal."""
        agent = HistoryAgent()
        result = agent._clean_html("<b>Bold</b> text <a href='#'>link</a>")
        assert result == "Bold text link"

    def test_clean_html_decodes_entities(self):
        """Test HTML entity decoding."""
        agent = HistoryAgent()
        result = agent._clean_html("&quot;quoted&quot; &amp; more")
        assert result == '"quoted" & more'


class TestHistoryAgentScoring:
    """Tests for HistoryAgent._score_result()."""

    def test_score_result_direct_match(self):
        """Test scoring with direct street name match."""
        agent = HistoryAgent()
        score = agent._score_result(
            "Rothschild Boulevard Tel Aviv",
            "History of the famous boulevard",
            "Rothschild Boulevard"
        )

        # Should get bonus for direct match
        assert score > 50

    def test_score_result_historical_keywords(self):
        """Test scoring with historical keywords."""
        agent = HistoryAgent()
        score = agent._score_result(
            "History of Israel",
            "The history and establishment of the state",
            "Some Street"
        )

        # Should get points for historical keywords
        assert score > 30


class TestJudgeAgentEvaluation:
    """Tests for JudgeAgent.evaluate()."""

    def test_evaluate_picks_highest_score(self, sample_junction):
        """Test that judge picks the highest scoring result."""
        agent = JudgeAgent()

        contestants = [
            AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Video",
                junction_id=1,
                junction_address="Test",
                title="Video",
                description="Test",
                relevance_score=60.0,
                quality_score=60.0,
                confidence=60.0,
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
                confidence=90.0,
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
                confidence=70.0,
            ),
        ]

        decision = agent.evaluate(sample_junction, contestants)

        assert decision.winner_type == AgentType.MUSIC
        assert decision.winning_score > 0

    def test_evaluate_handles_failed_results(self, sample_junction):
        """Test evaluation with some failed results."""
        agent = JudgeAgent()

        contestants = [
            AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Video",
                junction_id=1,
                junction_address="Test",
                title="",  # Empty title = failure
                description="",
                error="API Error",
            ),
            AgentResult(
                agent_type=AgentType.MUSIC,
                agent_name="Music",
                junction_id=1,
                junction_address="Test",
                title="Good Music",
                description="A good song",
                relevance_score=80.0,
                quality_score=80.0,
            ),
        ]

        decision = agent.evaluate(sample_junction, contestants)

        # Should pick the non-failed result
        assert decision.winner_type == AgentType.MUSIC

    def test_evaluate_all_failed_returns_first(self, sample_junction):
        """Test evaluation when all results failed."""
        agent = JudgeAgent()

        contestants = [
            AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Video",
                junction_id=1,
                junction_address="Test",
                title="",
                description="",
                error="Error 1",
            ),
            AgentResult(
                agent_type=AgentType.MUSIC,
                agent_name="Music",
                junction_id=1,
                junction_address="Test",
                title="",
                description="",
                error="Error 2",
            ),
        ]

        decision = agent.evaluate(sample_junction, contestants)

        # Should return first with error note
        assert decision is not None
        assert "All agents failed" in decision.reasoning

    def test_evaluate_empty_contestants_raises(self, sample_junction):
        """Test that empty contestants list raises error."""
        agent = JudgeAgent()

        with pytest.raises(ValueError) as exc_info:
            agent.evaluate(sample_junction, [])

        assert "No contestants" in str(exc_info.value)

    def test_evaluate_includes_reasoning(self, sample_junction):
        """Test that evaluation includes reasoning."""
        agent = JudgeAgent()

        contestants = [
            AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Video",
                junction_id=1,
                junction_address="Test",
                title="Good Video",
                description="Test",
                relevance_score=85.0,
                quality_score=85.0,
            ),
        ]

        decision = agent.evaluate(sample_junction, contestants)

        assert decision.reasoning != ""
        assert len(decision.reasoning) > 10


class TestJudgeAgentReasoning:
    """Tests for JudgeAgent._generate_reasoning()."""

    def test_generate_reasoning_decisive_win(self, sample_junction):
        """Test reasoning for decisive win."""
        agent = JudgeAgent()

        contestants = [
            AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Video",
                junction_id=1,
                junction_address="Test",
                title="Great Video",
                description="Test",
                relevance_score=95.0,
                quality_score=95.0,
                confidence=95.0,
            ),
            AgentResult(
                agent_type=AgentType.MUSIC,
                agent_name="Music",
                junction_id=1,
                junction_address="Test",
                title="Music",
                description="Test",
                relevance_score=50.0,
                quality_score=50.0,
                confidence=50.0,
            ),
        ]

        decision = agent.evaluate(sample_junction, contestants)

        assert "decisively" in decision.reasoning.lower() or "wins" in decision.reasoning.lower()

    def test_generate_reasoning_narrow_win(self, sample_junction):
        """Test reasoning for narrow win."""
        agent = JudgeAgent()

        contestants = [
            AgentResult(
                agent_type=AgentType.VIDEO,
                agent_name="Video",
                junction_id=1,
                junction_address="Test",
                title="Video",
                description="Test",
                relevance_score=82.0,
                quality_score=82.0,
                confidence=82.0,
            ),
            AgentResult(
                agent_type=AgentType.MUSIC,
                agent_name="Music",
                junction_id=1,
                junction_address="Test",
                title="Music",
                description="Test",
                relevance_score=80.0,
                quality_score=80.0,
                confidence=80.0,
            ),
        ]

        decision = agent.evaluate(sample_junction, contestants)

        # Should mention close competition
        assert "narrowly" in decision.reasoning.lower() or "edges" in decision.reasoning.lower() or "wins" in decision.reasoning.lower()
