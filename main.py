#!/usr/bin/env python3
"""Twitter/X Asset Monitor - Entry point."""

import sys
from pathlib import Path

# Ensure the project root is in the path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import cli

if __name__ == "__main__":
    cli()
