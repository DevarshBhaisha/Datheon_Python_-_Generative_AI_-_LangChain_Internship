
"""CLI entry point for the Multi-Tool Autonomous AI Agent."""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from agent import build_agent, run_agent

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Multi-Tool Autonomous AI Agent"
    )

    parser.add_argument(
        "--query",
        help="Run a single query instead of interactive mode",
    )

    args = parser.parse_args()

    if not os.getenv("GOOGLE_API_KEY"):
        print(
            "Missing GOOGLE_API_KEY. Copy .env.example to .env "
            "and add your Gemini API key.",
            file=sys.stderr,
        )
        return 2

    try:
        agent = build_agent()

    except Exception as exc:
        print(
            f"Could not initialize the agent: {exc}",
            file=sys.stderr,
        )
        return 1

    if args.query is not None:
        query = args.query.strip()

        if not query:
            print("Error: Query cannot be empty.", file=sys.stderr)
            return 2

        answer = run_agent(agent, query)

        if answer.startswith("Agent run failed:"):
            return 1

        return 0

    print("\nMulti-Tool Autonomous AI Agent")
    print("Tools: DuckDuckGo search | safe calculator | local file reader")
    print("Type 'help' for instructions.")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            query = input("You > ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not query:
            continue

        if query.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if query.lower() == "help":
            print(
                "\nAsk a multi-step research question."
                "\nLocal files must be inside ./data."
                "\nAvailable tools: web search, calculator, file reader.\n"
            )
            continue

        answer = run_agent(agent, query)

        if answer.startswith("Agent run failed:"):
            print("The request failed. You can try again.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
