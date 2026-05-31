# `parse_theosophy_explained_pavri.py` Pass History

Current consecutive fully approved sets: `3` (set_01, set_02, set_03) — **APPROVED 2026-05-31**

## Context

Source: "Theosophy Explained in Questions and Answers" by P. Pavri, B.Sc. (Theosophical
Publishing House, Adyar). DjVu OCR text from Internet Archive (dli.ministry.23793).
Format: Q./Ans. at line-start; 519 turns (245 Q + ~285 Ans) across body lines 1749–21800.
Target speaker: Pavri (Participant B). Enquirer is Participant A.
Filters: min 12 words, max 500 words; odd-quote-count and terminal-colon rows excluded.

Key components:
- Source: `source_texts/occult/raw/theosophy_explained_pavri_djvu.txt`
- Parser: `src/ai_training_tests/extraction/parsers/theosophy_explained_pavri.py`
- Wrapper: `scripts/extraction/parse_theosophy_explained_pavri.py`
- Candidate JSONL: `review_outputs/new_esoteric_sources/theosophy_explained_pavri_dialogue.jsonl`

Notes on OCR quality: source is DjVu scan with typical OCR artifacts (hyphenated words,
occasional garbled page headers, stray characters). Parser applies all-caps noise filter
and OCR quote normalization. Some residual OCR noise in history turns is acceptable.

## Set Log

### Set 01

- Status: `pass`
- Output rows: `97`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1895112112`
- Review packet: `set_01/theosophy_explained_pavri_dialogue_set_01_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context`, `slight local scene looseness` (expected)

### Set 02

- Status: `pass`
- Output rows: `97`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `247180124`
- Review packet: `set_02/theosophy_explained_pavri_dialogue_set_02_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context`, `slight local scene looseness` (expected)

### Set 03

- Status: `pass`
- Output rows: `97`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `658503723`
- Review packet: `set_03/theosophy_explained_pavri_dialogue_set_03_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context`, `slight local scene looseness` (expected)

Approval rule: `3` consecutive random sets at `100%` (0 hard failures). Met on set_03.
