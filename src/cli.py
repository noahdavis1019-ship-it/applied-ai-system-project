"""
VibeFinder 2.0 command line.

Usage:
  python -m src.cli "chill music for studying"
  python -m src.cli "gym playlist" --k 3 --trace
  python -m src.cli            (interactive mode, blank line to quit)
"""

import argparse
import logging
import os
import sys

from src.agent import VibeAgent
from src.guardrails import GuardrailError


def setup_logging(path: str = "logs/vibefinder.log") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    logging.basicConfig(
        filename=path,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def render(result, show_trace: bool) -> str:
    lines = [f'Request: "{result.query}"']
    p = result.profile
    lines.append(
        f"Profile: genre={p['genre']}, mood={p['mood']}, energy={p['energy']}, acoustic={p['likes_acoustic']}"
        + ("  (revised)" if result.revised else "")
    )
    if result.sources:
        lines.append("Based on: " + "; ".join(
            f"[{h.note.id}] {h.note.title} (matched: {', '.join(h.matched_terms)})" for h in result.sources
        ))
    lines.append(f"Confidence: {result.confidence:.2f}")
    lines.append("")
    for i, (song, score, why) in enumerate(result.recommendations, 1):
        lines.append(f"{i}. {song['title']} by {song['artist']} [{song['genre']}, {song['mood']}] score {score:.2f}")
        lines.append(f"   why: {why}")
    for w in result.warnings:
        lines.append(f"WARNING: {w}")
    if show_trace:
        lines.append("")
        lines.append("Agent trace:")
        lines.extend(f"  {t}" for t in result.trace)
    return "\n".join(lines)


def handle(agent: VibeAgent, query: str, k: int, trace: bool) -> int:
    try:
        print(render(agent.run(query, k=k), trace))
        return 0
    except GuardrailError as e:
        logging.getLogger("vibefinder.cli").warning("rejected: %s", e)
        print(f"Sorry, I can't run that request: {e}")
        return 2


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="VibeFinder 2.0: describe a vibe, get songs.")
    parser.add_argument("query", nargs="?", help="what you want to listen to")
    parser.add_argument("--k", type=int, default=5, help="number of songs (default 5)")
    parser.add_argument("--trace", action="store_true", help="show the agent's step-by-step trace")
    args = parser.parse_args(argv)

    setup_logging()
    agent = VibeAgent()

    if args.query is not None:
        return handle(agent, args.query, args.k, args.trace)

    print("VibeFinder 2.0. Describe a vibe (blank line to quit).")
    while True:
        try:
            query = input("> ")
        except EOFError:
            break
        if not query.strip():
            break
        handle(agent, query, args.k, args.trace)
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
