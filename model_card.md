# Model Card: VibeFinder 2.0

The Module 3 model card for VibeFinder 1.0 is preserved in [`model_card_module3.md`](model_card_module3.md).

## 1. System Overview

**Name:** VibeFinder 2.0
**Base project:** Music Recommender Simulation (Module 3)
**Task:** Turn a free-text request ("chill music for studying") into the top k songs from a 20-song catalog, with reasons, cited knowledge-base notes, a confidence score, and warnings.
**Components:** TF-IDF retriever over 19 hand-written vibe notes (RAG), a rule-based agent (guard, plan, retrieve, profile, rank, self-check, revise), the Module 3 scoring function, input and output guardrails, logging, 27 unit tests, and a 14-case evaluation harness.
**No external model or API is used.** All "intelligence" is retrieval plus transparent rules, chosen so every output is reproducible and explainable.

## 2. Intended Use

- Classroom demonstration of RAG, agentic self-checking, and reliability testing.
- Exploring how a recommender turns everyday language into ranked results.

**Not intended for:** real music products, decisions that affect artists' exposure or income, or anyone who needs recommendations from a real catalog.

## 3. Data

- `data/songs.csv`: 20 fictional songs, 17 genres, 15 moods. Most genres have one song.
- `data/vibe_notes.json`: 19 notes I wrote that map activities and feelings to a genre, mood, energy, and acoustic preference. These reflect my own assumptions (for example, that studying means lofi), not data from real listeners.

## 4. Limitations and Biases

- **The knowledge base encodes my taste.** I decided that "studying" means lofi and "gym" means pop. A listener who studies to classical or lifts to metal is steered away from what they want unless they name the genre. Every mapping is a cultural assumption, and the system presents it with high confidence.
- **Vocabulary gaps.** Retrieval only understands words I wrote into the notes. "Quiet piano" gets confidence 0.40 because "piano" appears in two notes that disagree. Slang, other languages, and misspellings mostly fail, which disadvantages users who do not phrase requests the way I do.
- **Catalog imbalance.** Lofi has 3 songs and most genres have 1, so lofi and pop requests get rich lists while country or gospel requests get one real match plus energy-based filler.
- **Inherited scoring bias.** The Module 3 rule still gives genre 2 points and uses exact string matching, so "indie pop" earns nothing for a pop fan.
- **Known-missing genre list is hand-maintained.** "k-pop" is caught, but a genre I did not list (for example "shoegaze") is silently ignored rather than flagged.
- **Confidence is a heuristic, not a probability.** 0.98 means "strong keyword match and a song that fits," not "98% chance you will like this."

## 5. Misuse and Safeguards

The realistic risks for a system like this are low-stakes but real: a scaled-up version could quietly steer listeners toward the genres its designers assumed, and a confident-sounding wrong answer can erode trust. Safeguards in this version:

- Every answer shows the notes it relied on and the per-song point breakdown, so a user can see why it chose what it did and disagree.
- Explicit user words override retrieval, so the system cannot overrule a user who names a genre.
- Low confidence and out-of-catalog genres produce visible warnings rather than silent substitutions.
- Input guardrails reject empty, oversized, or wordless input, and all queries and warnings are logged for review.
- The system collects no personal data and stores only the query text in a local log file.

## 6. Testing Results and Surprises

- 27 out of 27 unit tests pass; 14 out of 14 evaluation cases pass (`eval/results.md`). Average confidence is 0.94 on in-catalog requests and 0.00 to 0.35 on gibberish, vague, or out-of-catalog requests.
- **First eval run: 13 out of 14.** "k-pop bangers" was read as "pop" through substring matching and returned 0.97 confidence with no warning. That surprised me most, because the output looked completely reasonable. Whole-word matching plus a known-missing-genres list fixed it.
- **The first confidence formula was too generous.** It averaged retrieval and song fit, and since the scorer can always find a song that fits whatever profile was guessed, weak queries like "quiet piano" scored 0.70. Making retrieval strength a multiplier dropped that to 0.40 and triggered a warning.
- **The revise step rarely changes the answer.** When the best note is weak, the next one is usually weaker. It still earns its place because it records in the trace that the agent checked an alternative.

## 7. AI Collaboration
I used an AI coding assistant (Claude) as a resource while developing this project. I used it to help think through the structure of the retriever, agent, and evaluation system, but I made the implementation decisions, tested the code, and reviewed the results myself.

- Helpful use of AI: I used AI to brainstorm ways to connect retrieved notes to the user's taste profile. One particularly useful suggestion was to have the retrieved notes directly influence the profile rather than simply display them alongside the recommendations. This made the RAG feature more meaningful because changing a note could actually change the recommended songs. I also used AI to help organize evaluation results into a markdown table.

- AI suggestion I had to correct: One suggestion involved using a basic substring check to identify genres and calculating confidence using a weighted average of retrieval quality and song fit. Although this seemed reasonable initially, testing revealed problems. For example, "k-pop" was incorrectly identified as "pop" with 0.97 confidence, while vague searches received confidence scores around 70%. I adjusted the matching logic to recognize whole words and changed the confidence calculation so weak retrieval would limit the overall score. This taught me that AI-generated suggestions still need to be tested against unusual examples rather than just straightforward inputs.

## 8. Future Work

- Replace hand-written notes with notes generated from real listening data, and measure retrieval quality against labeled requests.
- Add synonym expansion or small embeddings so "lifting weights" and "piano" retrieve well without hard-coding words.
- Partial genre credit ("indie pop" counts partly as "pop").
- Ask a clarifying question instead of guessing when confidence is low.
