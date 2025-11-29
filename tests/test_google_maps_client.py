"""
Unit tests for the Google Maps client module.
"""

import pytest
from unittest.mock import patch, MagicMock
import json

from tour_guide.route_fetcher.google_maps_client import (
    GoogleMapsClient,
    GoogleMapsClientError
)


class TestGoogleMapsClientInit:
    """Tests for GoogleMapsClient initialization."""

    def test_client_creation_with_api_key(self):
        """Test creating client with explicit API key."""
        client = GoogleMapsClient(api_key="test_key_123")
        assert client.api_key == "test_key_123"

    @patch('tour_guide.route_fetcher.google_maps_client.get_google_maps_api_key')
    def test_client_creation_from_config(self, mock_get_key):
        """Test creating client with key from config."""
        mock_get_key.return_value = "config_key_456"
        client = GoogleMapsClient()
        assert client.api_key == "config_key_456"

    @patch('tour_guide.route_fetcher.google_maps_client.get_google_maps_api_key')
    def test_client_creation_without_key_raises_error(self, mock_get_key):
        """Test that missing API key raises error."""
        mock_get_key.return_value = ""
        with pytest.raises(GoogleMapsClientError) as exc_info:
            GoogleMapsClient()
        assert "API key not provided" in str(exc_info.value)


class TestGoogleMapsClientGetRoute:
    """Tests for GoogleMapsClient.get_route()."""

    @patch('urllib.request.urlopen')
    def test_get_route_success(self, mock_urlopen):
        """Test successful route fetching."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "OK",
            "routes": [{
                "legs": [{
                    "start_location": {"lat": 32.0, "lng": 34.0},
                    "end_location": {"lat": 32.1, "lng": 34.1},
                    "distance": {"text": "10 km", "value": 10000},
                    "duration": {"text": "15 mins", "value": 900},
                    "steps": []
                }]
            }]
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="test_key")
        result = client.get_route("Tel Aviv", "Jerusalem")

        assert result["status"] == "OK"
        assert "routes" in result

    @patch('urllib.request.urlopen')
    def test_get_route_api_error(self, mock_urlopen):
        """Test handling of API error response."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "REQUEST_DENIED",
            "error_message": "Invalid API key"
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="invalid_key")
        with pytest.raises(GoogleMapsClientError) as exc_info:
            client.get_route("Tel Aviv", "Jerusalem")
        assert "REQUEST_DENIED" in str(exc_info.value)

    @patch('urllib.request.urlopen')
    def test_get_route_with_waypoints(self, mock_urlopen):
        """Test route fetching with waypoints."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "OK",
            "routes": [{"legs": []}]
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="test_key")
        client.get_route(
            "Tel Aviv",
            "Jerusalem",
            waypoints=["Haifa", "Netanya"]
        )

        # Verify the URL contains waypoints
        call_args = mock_urlopen.call_args
        url = call_args[0][0]
        assert "waypoints" in url

    @patch('urllib.request.urlopen')
    def test_get_route_with_avoid(self, mock_urlopen):
        """Test route fetching with avoid options."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "OK",
            "routes": [{"legs": []}]
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="test_key")
        client.get_route(
            "Tel Aviv",
            "Jerusalem",
            avoid=["tolls", "highways"]
        )

        call_args = mock_urlopen.call_args
        url = call_args[0][0]
        assert "avoid" in url


class TestGoogleMapsClientGetRouteWithTraffic:
    """Tests for GoogleMapsClient.get_route_with_traffic()."""

    @patch('urllib.request.urlopen')
    def test_get_route_with_traffic_sets_departure_time(self, mock_urlopen):
        """Test that traffic-aware routing sets departure_time."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "OK",
            "routes": [{"legs": []}]
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="test_key")
        client.get_route_with_traffic("Tel Aviv", "Jerusalem")

        call_args = mock_urlopen.call_args
        url = call_args[0][0]
        assert "departure_time=now" in url


class TestGoogleMapsClientGeocode:
    """Tests for GoogleMapsClient.geocode()."""

    @patch('urllib.request.urlopen')
    def test_geocode_success(self, mock_urlopen):
        """Test successful geocoding."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "OK",
            "routes": [{
                "legs": [{
                    "start_location": {"lat": 32.0853, "lng": 34.7818}
                }]
            }]
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="test_key")
        result = client.geocode("Tel Aviv")

        assert result["lat"] == 32.0853
        assert result["lng"] == 34.7818

    @patch('urllib.request.urlopen')
    def test_geocode_no_routes_raises_error(self, mock_urlopen):
        """Test geocode with no routes raises error."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "OK",
            "routes": []
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="test_key")
        with pytest.raises(GoogleMapsClientError) as exc_info:
            client.geocode("Invalid Address XYZ123")
        assert "Could not geocode" in str(exc_info.value)


class TestGoogleMapsClientValidateApiKey:
    """Tests for GoogleMapsClient.validate_api_key()."""

    @patch('urllib.request.urlopen')
    def test_validate_valid_key(self, mock_urlopen):
        """Test validation of valid API key."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "OK",
            "routes": [{"legs": [{"start_location": {"lat": 0, "lng": 0}}]}]
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="valid_key")
        assert client.validate_api_key() is True

    @patch('urllib.request.urlopen')
    def test_validate_invalid_key(self, mock_urlopen):
        """Test validation of invalid API key."""
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "status": "REQUEST_DENIED",
            "error_message": "Invalid API key"
        }).encode('utf-8')
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="invalid_key")
        with pytest.raises(GoogleMapsClientError) as exc_info:
            client.validate_api_key()
        assert "Invalid API key" in str(exc_info.value)


class TestGoogleMapsClientErrorHandling:
    """Tests for error handling in GoogleMapsClient."""

    @patch('urllib.request.urlopen')
    def test_network_error_handling(self, mock_urlopen):
        """Test handling of network errors."""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")

        client = GoogleMapsClient(api_key="test_key")
        with pytest.raises(GoogleMapsClientError) as exc_info:
            client.get_route("Tel Aviv", "Jerusalem")
        assert "Network error" in str(exc_info.value)

    @patch('urllib.request.urlopen')
    def test_invalid_json_handling(self, mock_urlopen):
        """Test handling of invalid JSON response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b"not valid json"
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GoogleMapsClient(api_key="test_key")
        with pytest.raises(GoogleMapsClientError) as exc_info:
            client.get_route("Tel Aviv", "Jerusalem")
        assert "Invalid JSON" in str(exc_info.value)
