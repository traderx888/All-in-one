"""CLI entry point for the multi-agent system."""

from __future__ import annotations

import argparse
import asyncio
import sys

from .config import Config
from .orchestrator import Orchestrator


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aio",
        description="All-in-one: Multi-agent hierarchical system for one-person teams",
    )
    parser.add_argument(
        "request",
        nargs="?",
        help="The task to send to the orchestrator agent",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the orchestrator model",
    )
    parser.add_argument(
        "--specialist-model",
        default=None,
        help="Override the specialist model",
    )
    args = parser.parse_args()

    config = Config.from_env()
    if args.model:
        config.orchestrator_model = args.model
    if args.specialist_model:
        config.specialist_model = args.specialist_model

    if not config.api_key:
        print("Error: Set ANTHROPIC_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    # Get request from argument or stdin
    request = args.request
    if not request:
        if sys.stdin.isatty():
            print("Enter your request (Ctrl+D to send):")
        request = sys.stdin.read().strip()

    if not request:
        print("Error: No request provided.", file=sys.stderr)
        sys.exit(1)

    orchestrator = Orchestrator(config)
    result = asyncio.run(orchestrator.run(request))
    print("\n" + "=" * 60)
    print("INTEGRATED OUTPUT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
