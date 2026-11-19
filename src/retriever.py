"""
Retriever: a small TF-IDF search over the "vibe notes" knowledge base.

Each note links everyday language ("studying", "gym", "breakup") to a
genre, mood, energy level and acoustic preference. The agent retrieves the
notes that best match a free-text request and builds a taste profile from
them, so retrieval directly changes what gets recommended.

Pure standard library, so it runs anywhere without API keys.
"""

import json
import math
import re
from dataclasses import dataclass
from typing import Dict, List

STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "to", "of", "in", "on", "at", "is", "it",
    "i", "im", "i'm", "me", "my", "we", "you", "some", "something", "music", "songs",
    "song", "play", "want", "need", "give", "with", "that", "this", "like", "while",
    "please", "be", "am", "are", "feel", "feeling", "kind", "get", "can", "just",
}


def tokenize(text: str) -> List[str]:
    """Lowercase, split into words, drop stopwords, and apply light stemming."""
    words = re.findall(r"[a-z&']+", text.lower())
    tokens = []
    for w in words:
        w = w.strip("'")
        if not w or w in STOPWORDS:
            continue
        # light stemming so "studying" ~ "study", "workouts" ~ "workout"
        for suffix in ("ing", "es", "s"):
            if w.endswith(suffix) and len(w) - len(suffix) >= 4:
                w = w[: -len(suffix)]
                break
        tokens.append(w)
    return tokens


@dataclass
class Note:
    id: str
    title: str
    genre: str
    mood: str
    energy: float
    acoustic: bool
    text: str


@dataclass
class Hit:
    note: Note
    score: float
    matched_terms: List[str]


def load_notes(path: str) -> List[Note]:
    """Load the knowledge base JSON into Note objects."""
    with open(path) as f:
        raw = json.load(f)
    return [Note(**item) for item in raw]


class Retriever:
    """TF-IDF + cosine similarity retriever over vibe notes."""

    def __init__(self, notes: List[Note]):
        self.notes = notes
        # Index title + tags + body so "jazz" or "chill" match directly.
        self.doc_tokens = [
            tokenize(f"{n.title} {n.genre} {n.mood} {n.text}") for n in notes
        ]
        n_docs = len(notes)
        df: Dict[str, int] = {}
        for toks in self.doc_tokens:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        self.idf = {t: math.log((1 + n_docs) / (1 + c)) + 1 for t, c in df.items()}
        self.doc_vectors = [self._vector(toks) for toks in self.doc_tokens]

    def _vector(self, tokens: List[str]) -> Dict[str, float]:
        tf: Dict[str, float] = {}
        for t in tokens:
            if t in self.idf:
                tf[t] = tf.get(t, 0) + 1
        vec = {t: c * self.idf[t] for t, c in tf.items()}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
        return {t: v / norm for t, v in vec.items()}

    def search(self, query: str, k: int = 3) -> List[Hit]:
        """Return the top k notes with similarity > 0, best first."""
        q_tokens = tokenize(query)
        q_vec = self._vector(q_tokens)
        hits = []
        for note, d_vec in zip(self.notes, self.doc_vectors):
            sim = sum(w * d_vec.get(t, 0.0) for t, w in q_vec.items())
            if sim > 0:
                matched = sorted(t for t in q_vec if t in d_vec)
                hits.append(Hit(note=note, score=sim, matched_terms=matched))
        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:k]
