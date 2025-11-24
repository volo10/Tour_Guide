"""
Logging configuration for Tour Guide system.

Provides easy setup for logging with junction ID tracking.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
    log_file: Optional[str] = None,
):
    """
    Setup logging for the Tour Guide system.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        format_string: Custom format string (optional)
        include_timestamp: Include timestamp in logs
        log_file: Optional file path to write logs to

    Example:
        >>> from tour_guide.logging_config import setup_logging
        >>> setup_logging(level="DEBUG")
        >>> # Now all Tour Guide logs will be shown
    """
    # Default format with junction ID tracking
    if format_string is None:
        if include_timestamp:
            format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            format_string = "%(name)s - %(levelname)s - %(message)s"

    # Configure root logger for tour_guide package
    logger = logging.getLogger("tour_guide")
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(logging.Formatter(format_string))
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(logging.Formatter(format_string))
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def setup_simple_logging():
    """
    Quick setup for simple logging output.

    Shows only INFO level and above, without timestamps.
    Good for command-line usage.
    """
    return setup_logging(level="INFO", include_timestamp=False)


def setup_debug_logging(log_file: str = "tour_guide_debug.log"):
    """
    Setup detailed debug logging.

    Logs everything to both console and file with timestamps.

    Args:
        log_file: Path to log file (default: tour_guide_debug.log)
    """
    return setup_logging(level="DEBUG", include_timestamp=True, log_file=log_file)


def setup_production_logging(log_file: str = "tour_guide.log"):
    """
    Setup production logging.

    INFO level to console, DEBUG level to file.

    Args:
        log_file: Path to log file (default: tour_guide.log)
    """
    logger = logging.getLogger("tour_guide")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # Console: INFO level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File: DEBUG level
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    logger.propagate = False
    return logger


# Example usage patterns
if __name__ == "__main__":
    # Test different logging configurations
    print("=== Simple Logging ===")
    logger = setup_simple_logging()
    logger.info("This is an info message")
    logger.debug("This debug won't show (INFO level)")

    print("\n=== Debug Logging ===")
    logger = setup_debug_logging()
    logger.debug("This debug message shows")
    logger.info("Junction ID tracking: [JID-123]")
