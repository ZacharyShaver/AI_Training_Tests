# parse_transactions_blavatsky_lodge

## Status

final — **APPROVED 2026-05-31**

## Source

"Transactions of the Blavatsky Lodge" (HPB, 1889–1891). HPB's spoken answers to
student questions about the Stanzas of Dzyan from The Secret Doctrine.
Fetched from theosophylib.com HTML.

- Source file: `source_texts/occult/clean/transactions_blavatsky_lodge.txt`
- Parser: `src/ai_training_tests/extraction/parsers/transactions_blavatsky_lodge.py`
- Wrapper: `scripts/extraction/parse_transactions_blavatsky_lodge.py`
- Candidate JSONL: `review_outputs/new_esoteric_sources/transactions_blavatsky_lodge_dialogue.jsonl`
- Pass history: `review_outputs/parser_reviews/parse_transactions_blavatsky_lodge/pass_history.md`

## Format

Q./A. at line-start. 317 Q/A pairs. Body: lines 208–2125.
Target speaker: Blavatsky (Participant B). Enquirer = Participant A.

## Rows

288 rows promoted to `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`
