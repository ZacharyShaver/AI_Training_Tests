# `parse_plato_gorgias.py` Pass History

Current consecutive fully approved sets: `3` (set_01, set_02, set_03) — **APPROVED 2026-05-31**

## Context

Source: Plato's Gorgias, translated by Benjamin Jowett, from Project Gutenberg (ID 1672).
Source file: `source_texts/occult/raw/plato_gorgias_jowett.txt`
Speakers: SOCRATES (530 turns), CALLICLES (236), POLUS (207), GORGIAS (97), CHAEREPHON (15).
Target: Socrates (Participant B). Others (Callicles, Polus, Gorgias, Chaerephon) = Participant A.
Body lines 700–13000. Default: 2 history turns, 12–500 target words.

Classification: Plato's dialogues are considered foundational esoteric/Neoplatonic texts
by Theosophists (theosophylib.com includes The Republic alongside core Theosophical texts).

Key components:
- Source: `source_texts/occult/raw/plato_gorgias_jowett.txt`
- Parser: `src/ai_training_tests/extraction/parsers/plato_gorgias.py`
- Wrapper: `scripts/extraction/parse_plato_gorgias.py`
- Candidate JSONL: `review_outputs/new_esoteric_sources/plato_gorgias_dialogue.jsonl`

## Set Log

### Set 01

- Status: `pass`
- Output rows: `262`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `2053439493`
- Review packet: `set_01/plato_gorgias_dialogue_set_01_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context` (expected for 2-turn format)

### Set 02

- Status: `pass`
- Output rows: `262`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1056887753`
- Review packet: `set_02/plato_gorgias_dialogue_set_02_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context`, `slight local scene looseness` (acceptable)

### Set 03

- Status: `pass`
- Output rows: `262`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `864416625`
- Review packet: `set_03/plato_gorgias_dialogue_set_03_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context`, `slight local scene looseness` (acceptable)

Approval rule: `3` consecutive random sets at `100%` (0 hard failures). Met on set_03.
