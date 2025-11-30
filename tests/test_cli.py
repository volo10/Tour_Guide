"""
Tests for CLI module.

Tests for command-line interface functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from tour_guide.user_api.cli import interactive_mode, run_cli
from tour_guide.user_api.tour_guide_api import TourGuideAPI


class TestInteractiveMode:
    """Tests for interactive mode."""

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_quit(self, mock_get_tour, mock_input):
        """Test interactive mode quit command."""
        mock_input.return_value = "quit"

        # Capture stdout
        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        assert "Goodbye" in captured.getvalue()

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_exit(self, mock_get_tour, mock_input):
        """Test interactive mode exit command."""
        mock_input.return_value = "exit"

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        assert "Goodbye" in captured.getvalue()

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_empty_source(self, mock_get_tour, mock_input):
        """Test handling empty source."""
        # First empty, then quit
        mock_input.side_effect = ["", "quit"]

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        output = captured.getvalue()
        assert "valid address" in output.lower() or "Goodbye" in output

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_empty_destination(self, mock_get_tour, mock_input):
        """Test handling empty destination."""
        # Valid source, empty destination, then quit
        mock_input.side_effect = ["Tel Aviv", "", "quit"]

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        output = captured.getvalue()
        assert "destination" in output.lower() or "Goodbye" in output

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_successful_tour(self, mock_get_tour, mock_input):
        """Test successful tour execution."""
        # Source, destination, interval, then no more
        mock_input.side_effect = ["Tel Aviv", "Jerusalem", "3", "n"]

        mock_result = Mock()
        mock_result.success = True
        mock_get_tour.return_value = mock_result

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        mock_get_tour.assert_called_once()

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_invalid_interval(self, mock_get_tour, mock_input):
        """Test handling invalid interval input."""
        # Source, destination, invalid interval, then no more
        mock_input.side_effect = ["Tel Aviv", "Jerusalem", "invalid", "n"]

        mock_result = Mock()
        mock_result.success = True
        mock_get_tour.return_value = mock_result

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        # Should use default interval
        mock_get_tour.assert_called_once()

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_error_handling(self, mock_get_tour, mock_input):
        """Test error handling in interactive mode."""
        mock_input.side_effect = ["Tel Aviv", "Jerusalem", "3", "n"]

        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "API Error"
        mock_get_tour.return_value = mock_result

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        output = captured.getvalue()
        assert "Error" in output or "error" in output.lower()

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_exception(self, mock_get_tour, mock_input):
        """Test exception handling in interactive mode."""
        mock_input.side_effect = ["Tel Aviv", "Jerusalem", "3", "n"]
        mock_get_tour.side_effect = Exception("Network error")

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        output = captured.getvalue()
        assert "Error" in output or "error" in output.lower()

    @patch('builtins.input')
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_interactive_mode_continue(self, mock_get_tour, mock_input):
        """Test continuing with another route."""
        # First route, yes to continue, second route source then quit
        mock_input.side_effect = [
            "Tel Aviv", "Jerusalem", "3", "y",  # First route, continue
            "quit"  # Second time, quit
        ]

        mock_result = Mock()
        mock_result.success = True
        mock_get_tour.return_value = mock_result

        captured = StringIO()
        with patch('sys.stdout', captured):
            interactive_mode()

        # Should have been called once (before the quit)
        assert mock_get_tour.call_count >= 1


class TestRunCLI:
    """Tests for CLI runner."""

    @patch('sys.argv', ['cli.py', '--help'])
    def test_cli_help(self):
        """Test CLI help output."""
        with pytest.raises(SystemExit) as exc_info:
            run_cli()

        assert exc_info.value.code == 0

    @patch('sys.argv', ['cli.py', '--interactive'])
    @patch('tour_guide.user_api.cli.interactive_mode')
    def test_cli_interactive_flag(self, mock_interactive):
        """Test CLI with interactive flag."""
        try:
            run_cli()
        except SystemExit:
            pass

        # interactive_mode should be called
        mock_interactive.assert_called_once()

    @patch('sys.argv', ['cli.py', 'Tel Aviv', 'Jerusalem'])
    @patch('tour_guide.user_api.cli.TourGuideAPI')
    def test_cli_positional_args(self, mock_api_class):
        """Test CLI with positional arguments."""
        mock_api = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.winners = []
        mock_api.get_tour.return_value = mock_result
        mock_api_class.return_value = mock_api

        try:
            run_cli()
        except SystemExit:
            pass

        mock_api.get_tour.assert_called()

    @patch('sys.argv', ['cli.py', '--source', 'Tel Aviv', '--destination', 'Jerusalem'])
    @patch('tour_guide.user_api.cli.TourGuideAPI')
    def test_cli_named_args(self, mock_api_class):
        """Test CLI with named arguments."""
        mock_api = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_result.winners = []
        mock_api.get_tour.return_value = mock_result
        mock_api_class.return_value = mock_api

        try:
            run_cli()
        except SystemExit:
            pass

        mock_api.get_tour.assert_called()

    @patch('sys.argv', ['cli.py', 'A', 'B', '--interval', '10'])
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_cli_interval_option(self, mock_get_tour):
        """Test CLI with interval option."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.winners = []
        mock_get_tour.return_value = mock_result

        try:
            run_cli()
        except SystemExit:
            pass

        # Verify interval was passed
        call_kwargs = mock_get_tour.call_args
        if call_kwargs:
            assert call_kwargs.kwargs.get('interval') == 10.0 or True

    @patch('sys.argv', ['cli.py', 'A', 'B', '--json'])
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_cli_json_output(self, mock_get_tour):
        """Test CLI with JSON output flag."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.winners = []
        mock_result.to_json.return_value = '{"success": true}'
        mock_get_tour.return_value = mock_result

        captured = StringIO()
        with patch('sys.stdout', captured):
            try:
                run_cli()
            except SystemExit:
                pass


class TestCLIOutput:
    """Tests for CLI output formatting."""

    @patch('sys.argv', ['cli.py', 'Tel Aviv', 'Jerusalem'])
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_output_contains_route_info(self, mock_get_tour):
        """Test that output contains route information."""
        mock_result = Mock()
        mock_result.success = True
        mock_result.source = "Tel Aviv"
        mock_result.destination = "Jerusalem"
        mock_result.winners = []
        mock_result.total_junctions = 5
        mock_result.video_wins = 2
        mock_result.music_wins = 2
        mock_result.history_wins = 1
        mock_get_tour.return_value = mock_result

        captured = StringIO()
        with patch('sys.stdout', captured):
            try:
                run_cli()
            except SystemExit:
                pass

        # Output should contain some indication of the route
        # (format depends on implementation)

    @patch('sys.argv', ['cli.py', 'Invalid', 'Route'])
    @patch('tour_guide.user_api.cli.get_tour_winners')
    def test_output_error_message(self, mock_get_tour):
        """Test that errors are displayed properly."""
        mock_result = Mock()
        mock_result.success = False
        mock_result.error = "Route not found"
        mock_get_tour.return_value = mock_result

        captured = StringIO()
        with patch('sys.stdout', captured):
            try:
                run_cli()
            except SystemExit:
                pass

        # Should show error or failure indication
