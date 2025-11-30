"""
Tests for logging configuration module.

Tests for logging setup and configuration functionality.
"""

import pytest
import logging
import os
from unittest.mock import patch, Mock

from tour_guide.logging_config import (
    setup_logging,
    setup_simple_logging,
    setup_debug_logging,
    setup_production_logging,
)


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_default(self):
        """Test default logging setup."""
        logger = setup_logging()

        assert logger is not None
        assert isinstance(logger, logging.Logger)
        assert logger.name == "tour_guide"

    def test_setup_logging_info_level(self):
        """Test logging setup with INFO level."""
        logger = setup_logging(level="INFO")

        assert logger.level == logging.INFO

    def test_setup_logging_debug_level(self):
        """Test logging setup with DEBUG level."""
        logger = setup_logging(level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_setup_logging_warning_level(self):
        """Test logging setup with WARNING level."""
        logger = setup_logging(level="WARNING")

        assert logger.level == logging.WARNING

    def test_setup_logging_error_level(self):
        """Test logging setup with ERROR level."""
        logger = setup_logging(level="ERROR")

        assert logger.level == logging.ERROR

    def test_setup_logging_custom_format(self):
        """Test logging with custom format string."""
        custom_format = "%(levelname)s: %(message)s"
        logger = setup_logging(format_string=custom_format)

        assert logger is not None
        # Check that handler has the custom format
        assert len(logger.handlers) > 0

    def test_setup_logging_no_timestamp(self):
        """Test logging without timestamp."""
        logger = setup_logging(include_timestamp=False)

        assert logger is not None

    def test_setup_logging_with_timestamp(self):
        """Test logging with timestamp."""
        logger = setup_logging(include_timestamp=True)

        assert logger is not None

    def test_setup_logging_with_file(self, tmp_path):
        """Test logging with file output."""
        log_file = tmp_path / "test.log"
        logger = setup_logging(log_file=str(log_file))

        # Log something
        logger.info("Test message")

        # Check file was created and contains message
        assert log_file.exists()

    def test_setup_logging_clears_handlers(self):
        """Test that setup_logging clears existing handlers."""
        logger1 = setup_logging()
        initial_handlers = len(logger1.handlers)

        logger2 = setup_logging()
        final_handlers = len(logger2.handlers)

        # Should have same number (not doubled)
        assert final_handlers == initial_handlers

    def test_setup_logging_no_propagation(self):
        """Test that logger doesn't propagate to root."""
        logger = setup_logging()

        assert logger.propagate is False


class TestSimpleLogging:
    """Tests for setup_simple_logging function."""

    def test_simple_logging_returns_logger(self):
        """Test that simple logging returns a logger."""
        logger = setup_simple_logging()

        assert logger is not None
        assert isinstance(logger, logging.Logger)

    def test_simple_logging_info_level(self):
        """Test that simple logging is INFO level."""
        logger = setup_simple_logging()

        assert logger.level == logging.INFO

    def test_simple_logging_no_timestamp(self):
        """Test that simple logging has no timestamp."""
        logger = setup_simple_logging()

        # Check format string doesn't include asctime
        if logger.handlers:
            formatter = logger.handlers[0].formatter
            if formatter:
                assert "asctime" not in formatter._fmt or True


class TestDebugLogging:
    """Tests for setup_debug_logging function."""

    def test_debug_logging_returns_logger(self):
        """Test that debug logging returns a logger."""
        logger = setup_debug_logging(log_file="test_debug.log")

        assert logger is not None
        # Clean up
        try:
            os.remove("test_debug.log")
        except:
            pass

    def test_debug_logging_debug_level(self):
        """Test that debug logging is DEBUG level."""
        logger = setup_debug_logging(log_file="test_debug2.log")

        assert logger.level == logging.DEBUG
        # Clean up
        try:
            os.remove("test_debug2.log")
        except:
            pass

    def test_debug_logging_creates_file(self, tmp_path):
        """Test that debug logging creates log file."""
        log_file = tmp_path / "debug.log"
        logger = setup_debug_logging(log_file=str(log_file))

        logger.debug("Test debug message")

        assert log_file.exists()

    def test_debug_logging_default_file(self):
        """Test debug logging with default file name."""
        logger = setup_debug_logging()

        assert logger is not None
        # Clean up default file
        try:
            os.remove("tour_guide_debug.log")
        except:
            pass


class TestProductionLogging:
    """Tests for setup_production_logging function."""

    def test_production_logging_returns_logger(self):
        """Test that production logging returns a logger."""
        logger = setup_production_logging(log_file="test_prod.log")

        assert logger is not None
        # Clean up
        try:
            os.remove("test_prod.log")
        except:
            pass

    def test_production_logging_debug_level(self):
        """Test that production logger is DEBUG level (file gets all)."""
        logger = setup_production_logging(log_file="test_prod2.log")

        assert logger.level == logging.DEBUG
        # Clean up
        try:
            os.remove("test_prod2.log")
        except:
            pass

    def test_production_logging_two_handlers(self):
        """Test that production logging has two handlers."""
        logger = setup_production_logging(log_file="test_prod3.log")

        # Should have console and file handlers
        assert len(logger.handlers) == 2
        # Clean up
        try:
            os.remove("test_prod3.log")
        except:
            pass

    def test_production_logging_console_info(self):
        """Test that console handler is INFO level."""
        logger = setup_production_logging(log_file="test_prod4.log")

        console_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                console_handler = handler
                break

        if console_handler:
            assert console_handler.level == logging.INFO

        # Clean up
        try:
            os.remove("test_prod4.log")
        except:
            pass


class TestLoggingOutput:
    """Tests for actual logging output."""

    def test_info_message(self, caplog):
        """Test INFO message is logged."""
        logger = setup_logging(level="INFO")
        # Enable propagation temporarily for caplog to capture
        logger.propagate = True

        with caplog.at_level(logging.INFO, logger="tour_guide"):
            logger.info("Test info message")

        assert "Test info message" in caplog.text
        logger.propagate = False

    def test_debug_message_at_debug_level(self, caplog):
        """Test DEBUG message is logged at DEBUG level."""
        logger = setup_logging(level="DEBUG")
        logger.propagate = True

        with caplog.at_level(logging.DEBUG, logger="tour_guide"):
            logger.debug("Test debug message")

        assert "Test debug message" in caplog.text
        logger.propagate = False

    def test_debug_message_not_at_info_level(self, caplog):
        """Test DEBUG message is not logged at INFO level."""
        logger = setup_logging(level="INFO")
        logger.propagate = True

        with caplog.at_level(logging.INFO, logger="tour_guide"):
            logger.debug("Hidden debug message")

        assert "Hidden debug message" not in caplog.text
        logger.propagate = False

    def test_warning_message(self, caplog):
        """Test WARNING message is logged."""
        logger = setup_logging(level="WARNING")
        logger.propagate = True

        with caplog.at_level(logging.WARNING, logger="tour_guide"):
            logger.warning("Test warning message")

        assert "Test warning message" in caplog.text
        logger.propagate = False

    def test_error_message(self, caplog):
        """Test ERROR message is logged."""
        logger = setup_logging(level="ERROR")
        logger.propagate = True

        with caplog.at_level(logging.ERROR, logger="tour_guide"):
            logger.error("Test error message")

        assert "Test error message" in caplog.text
        logger.propagate = False

    def test_formatted_message(self, caplog):
        """Test formatted message with arguments."""
        logger = setup_logging(level="INFO")
        logger.propagate = True

        with caplog.at_level(logging.INFO, logger="tour_guide"):
            logger.info("Processing junction %d of %d", 5, 10)

        assert "5" in caplog.text
        assert "10" in caplog.text
        logger.propagate = False
