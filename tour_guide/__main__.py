#!/usr/bin/env python3
"""
Main entry point for the tour_guide package.

Allows running as: python -m tour_guide
"""

from .user_api.cli import run_cli

if __name__ == "__main__":
    run_cli()
