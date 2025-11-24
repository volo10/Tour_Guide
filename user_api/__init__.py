"""
User API Module for Tour Guide System

Provides user-friendly interfaces to run the Tour Guide system:
- CLI: Interactive command-line interface
- Python API: Simple function calls
- REST API: HTTP endpoints (optional, requires Flask)
"""

from .tour_guide_api import TourGuideAPI, TourGuideResult
from .cli import run_cli, interactive_mode

__all__ = [
    "TourGuideAPI",
    "TourGuideResult",
    "run_cli",
    "interactive_mode",
]

__version__ = "1.0.0"
