"""
Guardrails: validate input before the agent runs and sanity-check output after.
"""

import re
from typing import List, Tuple

MAX_QUERY_CHARS = 300
MIN_CONFIDENCE = 0.45


class GuardrailError(ValueError):
    """Raised when a request cannot be processed safely."""


def validate_query(query) -> str:
    """Return a cleaned query or raise GuardrailError with a user-facing reason."""
    if not isinstance(query, str):
        raise GuardrailError("Request must be text.")
    cleaned = " ".join(query.split())
    if not cleaned:
        raise GuardrailError("Request is empty. Try something like 'chill music for studying'.")
    if len(cleaned) > MAX_QUERY_CHARS:
        raise GuardrailError(f"Request is too long ({len(cleaned)} chars, max {MAX_QUERY_CHARS}).")
    if not re.search(r"[a-zA-Z]", cleaned):
        raise GuardrailError("Request has no words to understand.")
    return cleaned


def clamp_energy(value: float) -> float:
    """Keep energy targets inside the 0 to 1 range the catalog uses."""
    return max(0.0, min(1.0, float(value)))


def check_output(recommendations: List[Tuple[dict, float, str]], k: int) -> List[str]:
    """Return a list of problems found in a recommendation list (empty = OK)."""
    problems = []
    if len(recommendations) < min(k, 1):
        problems.append("no recommendations returned")
    ids = [song["id"] for song, _, _ in recommendations]
    if len(ids) != len(set(ids)):
        problems.append("duplicate songs in results")
    scores = [score for _, score, _ in recommendations]
    if scores != sorted(scores, reverse=True):
        problems.append("results are not sorted by score")
    return problems
