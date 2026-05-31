# `parse_corpus_hermeticum.py` Pass History

Current consecutive fully approved sets: `3` (set_01, set_02, set_03) — **APPROVED 2026-05-31**

## Context

Source: The Corpus Hermeticum (GRS Mead translation, from Thelemapedia/public domain).
Source file: `oritiginal text/The Corpus Hermeticum.txt`
13 tractates, body lines 400–2900. Speaker labels: H:/Hermes:, A:/Asclepius:, T:/Tat:,
Mind:, Pimander:, Workman: — canonical form Hermes, Asclepius, Tat, Mind.
Target speaker: Hermes or Mind (the teacher). 2 history turns, 12–400 target words.

This is a NEW standalone parser distinct from the pilot `build_pilot_dialogue_dataset.py`
which also used this source. The new parser produces 44 rows vs the original 28, using
more complete turn boundaries and cleaned section-number prefixes.

Key components:
- Source: `oritiginal text/The Corpus Hermeticum.txt`
- Parser: `src/ai_training_tests/extraction/parsers/corpus_hermeticum.py`
- Wrapper: `scripts/extraction/parse_corpus_hermeticum.py`
- Candidate JSONL: `review_outputs/new_esoteric_sources/corpus_hermeticum_v2_dialogue.jsonl`

## Set Log

### Set 01

- Status: `pass`
- Output rows: `44`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `2018232829`
- Review packet: `set_01/corpus_hermeticum_v2_dialogue_set_01_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context` (expected for 2-turn format)

### Set 02

- Status: `pass`
- Output rows: `44`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `723627678`
- Review packet: `set_02/corpus_hermeticum_v2_dialogue_set_02_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context`, `slight local scene looseness` (acceptable)

### Set 03

- Status: `pass`
- Output rows: `44`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1024955978`
- Review packet: `set_03/corpus_hermeticum_v2_dialogue_set_03_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context`, `slight local scene looseness` (acceptable)

Approval rule: `3` consecutive random sets at `100%` (0 hard failures). Met on set_03.
