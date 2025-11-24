#!/usr/bin/env python3
"""
Main entry point for user_api module.

Allows running as: python -m user_api
"""

from .cli import run_cli

if __name__ == "__main__":
    run_cli()
