import pytest

from src.agent import VibeAgent, mentions
from src.guardrails import GuardrailError, check_output, clamp_energy, validate_query
from src.retriever import Retriever, load_notes, tokenize


@pytest.fixture(scope="module")
def agent():
    return VibeAgent()


# ---- retriever -------------------------------------------------------

def test_tokenize_stems_and_drops_stopwords():
    assert tokenize("I need music for studying") == ["study"]


def test_retriever_finds_matching_note():
    r = Retriever(load_notes("data/vibe_notes.json"))
    hits = r.search("songs for the gym", k=3)
    assert hits[0].note.id == "n03"
    assert "gym" in hits[0].matched_terms


def test_retriever_returns_nothing_for_gibberish():
    r = Retriever(load_notes("data/vibe_notes.json"))
    assert r.search("asdf qwerty") == []


# ---- guardrails ------------------------------------------------------

@pytest.mark.parametrize("bad", ["", "   ", "!!!", "x" * 301, None, 42])
def test_validate_query_rejects_bad_input(bad):
    with pytest.raises(GuardrailError):
        validate_query(bad)


def test_validate_query_collapses_whitespace():
    assert validate_query("  chill   vibes ") == "chill vibes"


def test_clamp_energy():
    assert clamp_energy(1.7) == 1.0
    assert clamp_energy(-0.2) == 0.0


def test_check_output_flags_duplicates_and_bad_order():
    song = {"id": 1}
    assert "duplicate songs in results" in check_output([(song, 2.0, ""), (song, 1.0, "")], 2)
    assert "results are not sorted by score" in check_output([({"id": 1}, 1.0, ""), ({"id": 2}, 2.0, "")], 2)


# ---- agent -----------------------------------------------------------

def test_mentions_uses_whole_terms():
    assert mentions("pop", "some pop please")
    assert not mentions("pop", "k-pop bangers")
    assert not mentions("pop", "popular songs")


def test_retrieval_changes_the_profile(agent):
    study = agent.run("music for studying")
    gym = agent.run("music for the gym")
    assert study.profile["genre"] == "lofi"
    assert gym.profile["genre"] == "pop"
    assert gym.profile["energy"] > study.profile["energy"]


def test_explicit_genre_overrides_retrieval(agent):
    res = agent.run("rock for studying")
    assert res.profile["genre"] == "rock"


def test_results_cite_sources_and_trace_every_step(agent):
    res = agent.run("chill music for studying")
    assert res.sources, "answer should be grounded in retrieved notes"
    steps = [t.split(":")[0] for t in res.trace]
    for step in ["GUARD", "PLAN", "RETRIEVE", "PROFILE", "CHECK"]:
        assert step in steps


def test_results_pass_output_guardrails(agent):
    res = agent.run("party with friends", k=5)
    assert len(res.recommendations) == 5
    assert check_output(res.recommendations, 5) == []


def test_artist_diversity_penalty(agent):
    res = agent.run("lofi for studying", k=3)
    artists = [s["artist"] for s, _, _ in res.recommendations]
    repeated = [why for s, _, why in res.recommendations if "repeat artist" in why]
    assert len(repeated) == len(artists) - len(set(artists))


def test_strong_request_is_confident(agent):
    assert agent.run("breakup, feeling sad and alone").confidence >= 0.8


def test_gibberish_is_low_confidence_and_warns(agent):
    res = agent.run("asdf qwerty")
    assert res.confidence < 0.45
    assert res.warnings


def test_missing_genre_warns_instead_of_substituting(agent):
    res = agent.run("k-pop bangers")
    assert any("not in the catalog" in w for w in res.warnings)


def test_low_confidence_triggers_revision_step(agent):
    res = agent.run("quiet piano")
    assert any(t.startswith("REVISE") for t in res.trace)
