"""
Unit tests for the REST API module.
"""

import pytest
import json
from unittest.mock import patch, MagicMock

# Skip all tests if Flask is not available
pytest.importorskip("flask")

from tour_guide.user_api.rest_api import create_app, FLASK_AVAILABLE
from tour_guide.user_api.tour_guide_api import TourGuideResult, JunctionWinner


@pytest.fixture
def app():
    """Create test Flask application."""
    app = create_app(default_interval=1.0)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestRestApiIndex:
    """Tests for the index endpoint."""

    def test_index_returns_api_info(self, client):
        """Test that index returns API information."""
        response = client.get('/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['name'] == 'Tour Guide API'
        assert 'version' in data
        assert 'endpoints' in data

    def test_index_includes_example(self, client):
        """Test that index includes example usage."""
        response = client.get('/')
        data = json.loads(response.data)

        assert 'example' in data
        assert 'url' in data['example']


class TestRestApiHealth:
    """Tests for the health check endpoint."""

    def test_health_returns_ok(self, client):
        """Test that health check returns healthy status."""
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestRestApiGetTour:
    """Tests for the GET /tour endpoint."""

    def test_get_tour_requires_source(self, client):
        """Test that source parameter is required."""
        response = client.get('/tour?destination=Jerusalem')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data
        assert 'source' in data['error']

    def test_get_tour_requires_destination(self, client):
        """Test that destination parameter is required."""
        response = client.get('/tour?source=Tel%20Aviv')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data
        assert 'destination' in data['error']

    def test_get_tour_success(self, app):
        """Test successful tour request."""
        with patch('tour_guide.user_api.tour_guide_api.TourGuideAPI.get_tour') as mock_get_tour:
            mock_get_tour.return_value = TourGuideResult(
                source="Tel Aviv",
                destination="Jerusalem",
                total_distance="60 km",
                total_duration="1 hour",
                winners=[],
                total_junctions=5,
                video_wins=2,
                music_wins=2,
                history_wins=1,
                processing_time_seconds=10.0,
                success=True,
            )

            client = app.test_client()
            response = client.get('/tour?source=Tel%20Aviv&destination=Jerusalem')
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['source'] == 'Tel Aviv'
            assert data['destination'] == 'Jerusalem'
            assert data['success'] is True

    def test_get_tour_with_custom_interval(self, app):
        """Test tour request with custom interval."""
        with patch('tour_guide.user_api.tour_guide_api.TourGuideAPI.get_tour') as mock_get_tour:
            mock_get_tour.return_value = TourGuideResult(
                source="A",
                destination="B",
                total_distance="",
                total_duration="",
                success=True,
            )

            client = app.test_client()
            response = client.get('/tour?source=A&destination=B&interval=10.0')
            assert response.status_code == 200


class TestRestApiPostTour:
    """Tests for the POST /tour endpoint."""

    def test_post_tour_requires_json(self, app):
        """Test that POST requires JSON body."""
        client = app.test_client()
        response = client.post('/tour', data='not json', content_type='text/plain')
        # Flask returns 415 for unsupported media type or 400 for invalid JSON
        assert response.status_code in [400, 415]

    def test_post_tour_requires_source(self, client):
        """Test that source field is required."""
        response = client.post(
            '/tour',
            data=json.dumps({'destination': 'Jerusalem'}),
            content_type='application/json'
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'source' in data['error']

    def test_post_tour_requires_destination(self, client):
        """Test that destination field is required."""
        response = client.post(
            '/tour',
            data=json.dumps({'source': 'Tel Aviv'}),
            content_type='application/json'
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'destination' in data['error']

    def test_post_tour_success(self, app):
        """Test successful POST tour request."""
        with patch('tour_guide.user_api.tour_guide_api.TourGuideAPI.get_tour') as mock_get_tour:
            mock_get_tour.return_value = TourGuideResult(
                source="Tel Aviv",
                destination="Jerusalem",
                total_distance="60 km",
                total_duration="1 hour",
                winners=[
                    JunctionWinner(
                        junction_number=1,
                        junction_address="Main St",
                        turn_direction="LEFT",
                        winner_type="video",
                        winner_title="Test Video",
                        winner_description="A test",
                        winner_url="https://example.com",
                        score=85.0,
                    )
                ],
                total_junctions=1,
                video_wins=1,
                music_wins=0,
                history_wins=0,
                processing_time_seconds=5.0,
                success=True,
            )

            client = app.test_client()
            response = client.post(
                '/tour',
                data=json.dumps({
                    'source': 'Tel Aviv',
                    'destination': 'Jerusalem',
                    'interval': 5.0
                }),
                content_type='application/json'
            )
            assert response.status_code == 200

            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['winners']) == 1


class TestRestApiErrorHandling:
    """Tests for REST API error handling."""

    def test_api_error_returns_error_response(self, app):
        """Test that API errors return error response."""
        with patch('tour_guide.user_api.tour_guide_api.TourGuideAPI.get_tour') as mock_get_tour:
            mock_get_tour.return_value = TourGuideResult(
                source="A",
                destination="B",
                total_distance="N/A",
                total_duration="N/A",
                success=False,
                error="Route not found",
            )

            client = app.test_client()
            response = client.get('/tour?source=A&destination=B')
            assert response.status_code == 200  # Still 200 but with error in body

            data = json.loads(response.data)
            assert data['success'] is False
            assert data['error'] == "Route not found"


class TestCreateApp:
    """Tests for create_app function."""

    def test_create_app_returns_flask_app(self):
        """Test that create_app returns a Flask app."""
        app = create_app()
        assert app is not None
        assert hasattr(app, 'route')

    def test_create_app_with_custom_interval(self):
        """Test create_app with custom default interval."""
        app = create_app(default_interval=10.0)
        assert app is not None


class TestFlaskAvailability:
    """Tests for Flask availability check."""

    def test_flask_available_flag(self):
        """Test FLASK_AVAILABLE flag is set correctly."""
        # Since we're running these tests, Flask must be available
        assert FLASK_AVAILABLE is True
