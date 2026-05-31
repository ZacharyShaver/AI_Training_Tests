# `parse_transactions_blavatsky_lodge.py` Pass History

Current consecutive fully approved sets: `3` (set_01, set_02, set_03) — **APPROVED 2026-05-31**

## Context

Source: Transactions of the Blavatsky Lodge (1889–1891), HPB's spoken answers to
student questions about the Stanzas of Dzyan from The Secret Doctrine. Fetched from
theosophylib.com HTML and saved to `source_texts/occult/clean/transactions_blavatsky_lodge.txt`.

Format: `Q.` / `A.` at line-start. 317 Q/A pairs across 2172 lines (body: 208–2125).
Target speaker: Blavatsky (Participant B). Enquirer is Participant A.
Default: 2 history turns, 12–400 target words.

Key components:
- Source: `source_texts/occult/clean/transactions_blavatsky_lodge.txt`
- Parser: `src/ai_training_tests/extraction/parsers/transactions_blavatsky_lodge.py`
- Wrapper: `scripts/extraction/parse_transactions_blavatsky_lodge.py`
- Candidate JSONL: `review_outputs/new_esoteric_sources/transactions_blavatsky_lodge_dialogue.jsonl`

## Set Log

### Set 01

- Status: `pass`
- Output rows: `288`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1670254369`
- Review packet: `set_01/transactions_blavatsky_lodge_dialogue_set_01_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context` on all rows (expected for 2-turn Q/A format)
- Notes: Initial clean pass. Page-number artifacts ("N transactions") removed from source
  before run. Trailing book-closing text excluded by BODY_END=2125.

### Set 02

- Status: `pass`
- Output rows: `288`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1793031719`
- Review packet: `set_02/transactions_blavatsky_lodge_dialogue_set_02_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context` (expected)

### Set 03

- Status: `pass`
- Output rows: `288`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1957627725`
- Review packet: `set_03/transactions_blavatsky_lodge_dialogue_set_03_random_review.md`
- Hard failures: `0/10`
- Warnings: `minimal context` (expected)

Approval rule: `3` consecutive random sets at `100%` (0 hard failures). Met on set_03.
