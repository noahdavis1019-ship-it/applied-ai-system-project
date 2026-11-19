"""
VibeAgent: turns a free-text request into music recommendations.

Workflow (every step is logged and recorded in the trace):
  1. GUARD     validate the request
  2. PLAN      pull out explicit hints (a named genre, "high energy", "acoustic")
  3. RETRIEVE  search the vibe-notes knowledge base (RAG)
  4. PROFILE   build a taste profile from the retrieved notes + explicit hints
  5. RANK      score the catalog with the Module 3 scorer, then diversify artists
  6. CHECK     score confidence and run output guardrails
  7. REVISE    if the check fails, try the next-best retrieved profile once
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from src.guardrails import (
    MIN_CONFIDENCE,
    check_output,
    clamp_energy,
    validate_query,
)
from src.recommender import load_songs, recommend_songs
from src.retriever import Hit, Retriever, load_notes, tokenize

log = logging.getLogger("vibefinder.agent")

MAX_SONG_SCORE = 5.0  # 2 genre + 1 mood + 1.5 energy + 0.5 acoustic
ARTIST_REPEAT_PENALTY = 0.75

HIGH_ENERGY_WORDS = {"hype", "energetic", "fast", "loud", "intense", "upbeat"}
LOW_ENERGY_WORDS = {"calm", "slow", "quiet", "soft", "mellow", "sleepy", "gentle"}

# Genres people ask for that the 20-song catalog does not have. Naming one should
# trigger a warning instead of silently matching a substring ("k-pop" -> "pop").
KNOWN_MISSING_GENRES = ["k-pop", "kpop", "j-pop", "punk", "techno", "house", "bluegrass",
                        "opera", "afrobeats", "drill", "trap", "grunge", "emo", "blues", "folk"]


def mentions(term: str, text: str) -> bool:
    """Whole-term match: 'pop' matches 'pop music' but not 'k-pop' or 'popular'."""
    return re.search(rf"(?<![\w-]){re.escape(term)}(?![\w-])", text) is not None


@dataclass
class AgentResult:
    query: str
    profile: Dict
    recommendations: List[Tuple[dict, float, str]]
    confidence: float
    sources: List[Hit]
    trace: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    revised: bool = False


class VibeAgent:
    def __init__(self, songs_path: str = "data/songs.csv", notes_path: str = "data/vibe_notes.json"):
        self.songs = load_songs(songs_path)
        self.retriever = Retriever(load_notes(notes_path))
        self.catalog_genres = sorted({s["genre"] for s in self.songs}, key=len, reverse=True)

    # ---- step 2 -------------------------------------------------------
    def plan(self, query: str) -> Dict:
        """Find explicit hints the user stated directly."""
        lowered = query.lower()
        hints: Dict = {}
        for genre in KNOWN_MISSING_GENRES + self.catalog_genres:  # catalog longest first
            if mentions(genre, lowered):
                hints["genre"] = genre
                break
        tokens = set(tokenize(query)) | set(lowered.split())
        if "high energy" in lowered or tokens & HIGH_ENERGY_WORDS:
            hints["energy"] = 0.9
        elif "low energy" in lowered or tokens & LOW_ENERGY_WORDS:
            hints["energy"] = 0.3
        if "no acoustic" in lowered or "electronic" in lowered:
            hints["likes_acoustic"] = False
        elif "acoustic" in lowered:
            hints["likes_acoustic"] = True
        return hints

    # ---- step 4 -------------------------------------------------------
    @staticmethod
    def profile_from_hit(hit: Hit) -> Dict:
        n = hit.note
        return {"genre": n.genre, "mood": n.mood, "energy": n.energy, "likes_acoustic": n.acoustic}

    def build_profile(self, hits: List[Hit], hints: Dict) -> Dict:
        """Genre/mood from the best note, energy/acoustic blended across notes, hints override."""
        if hits:
            profile = self.profile_from_hit(hits[0])
            total = sum(h.score for h in hits)
            profile["energy"] = sum(h.note.energy * h.score for h in hits) / total
            acoustic_weight = sum(h.score for h in hits if h.note.acoustic)
            profile["likes_acoustic"] = acoustic_weight >= total / 2
        else:
            profile = {"genre": None, "mood": None, "energy": 0.5, "likes_acoustic": False}
        profile.update(hints)
        profile["energy"] = round(clamp_energy(profile["energy"]), 2)
        return profile

    # ---- step 5 -------------------------------------------------------
    def rank(self, profile: Dict, k: int) -> List[Tuple[dict, float, str]]:
        """Score with the Module 3 scorer, then penalize repeat artists for variety."""
        candidates = recommend_songs(profile, self.songs, k=len(self.songs))
        chosen, seen_artists = [], {}
        for song, score, why in candidates:
            repeats = seen_artists.get(song["artist"], 0)
            adjusted = score - ARTIST_REPEAT_PENALTY * repeats
            if repeats:
                why = f"{why}, repeat artist (-{ARTIST_REPEAT_PENALTY * repeats:.2f})"
            chosen.append((song, adjusted, why))
            seen_artists[song["artist"]] = repeats + 1
        chosen.sort(key=lambda item: item[1], reverse=True)
        return chosen[:k]

    # ---- step 6 -------------------------------------------------------
    @staticmethod
    def confidence(hits: List[Hit], recs: List[Tuple[dict, float, str]], profile: Dict) -> float:
        """0 to 1. Retrieval strength gates everything: a weak match to the knowledge base
        cannot produce a confident answer, however well the songs fit the guessed profile."""
        if not recs:
            return 0.0
        retrieval = min(1.0, hits[0].score / 0.35) if hits else 0.0
        fit = max(0.0, recs[0][1]) / MAX_SONG_SCORE
        genre_hit = 1.0 if recs[0][0]["genre"] == profile.get("genre") else 0.0
        return round(retrieval * (0.6 * fit + 0.4 * genre_hit), 2)

    # ---- main loop ----------------------------------------------------
    def run(self, query, k: int = 5) -> AgentResult:
        trace: List[str] = []
        warnings: List[str] = []

        cleaned = validate_query(query)  # raises GuardrailError
        trace.append(f"GUARD: request accepted ({len(cleaned)} chars)")
        log.info("query=%r", cleaned)

        hints = self.plan(cleaned)
        trace.append(f"PLAN: explicit hints {hints or 'none'}")

        hits = self.retriever.search(cleaned, k=3)
        trace.append(
            "RETRIEVE: " + (", ".join(f"{h.note.id} {h.note.title} ({h.score:.2f})" for h in hits) or "no matching notes")
        )
        log.info("retrieved=%s", [(h.note.id, round(h.score, 3)) for h in hits])

        profile = self.build_profile(hits, hints)
        trace.append(f"PROFILE: {profile}")

        recs = self.rank(profile, k)
        conf = self.confidence(hits, recs, profile)
        problems = check_output(recs, k)
        trace.append(f"CHECK: confidence {conf:.2f}, output problems {problems or 'none'}")

        revised = False
        if (conf < MIN_CONFIDENCE or problems) and len(hits) > 1 and "genre" not in hints:
            alt_profile = self.build_profile(hits[1:], hints)
            alt_recs = self.rank(alt_profile, k)
            alt_conf = self.confidence(hits[1:], alt_recs, alt_profile)
            trace.append(f"REVISE: tried next note {hits[1].note.id}, confidence {alt_conf:.2f}")
            if alt_conf > conf and not check_output(alt_recs, k):
                profile, recs, conf, revised = alt_profile, alt_recs, alt_conf, True
                trace.append("REVISE: kept revised profile")
            else:
                trace.append("REVISE: kept original profile")

        if not hits:
            warnings.append("No vibe notes matched; showing a neutral mid-energy mix. Try naming an activity, mood or genre.")
        if conf < MIN_CONFIDENCE:
            warnings.append(f"Low confidence ({conf:.2f}). Results may not match what you meant.")
        if profile.get("genre") and profile["genre"] not in self.catalog_genres:
            warnings.append(f"Genre '{profile['genre']}' is not in the catalog.")
        for w in warnings:
            log.warning(w)
        log.info("confidence=%.2f top=%s", conf, [s["title"] for s, _, _ in recs[:3]])

        return AgentResult(cleaned, profile, recs, conf, hits, trace, warnings, revised)
