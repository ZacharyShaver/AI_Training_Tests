# parse_zen_koans_database.py

## Parser

- Code: `scripts/extraction/parse_zen_koans_database.py`
- Source: `source_texts/buddhist/clean/zen_koans_database.json`
- Outputs: `review_outputs/new_buddhist_sources/zen_koans_database_clean_dialogue.jsonl`

## Status

final

## Source And Outputs

Zen Koans Database contributes 98 rows to the current final Buddhist dataset.
There are two identical-looking output paths that are cleanup candidates pending
hash and reference checks.

## Extraction Strategy

The parser downloads or reads cached koan pages, normalizes them into clean JSON,
and emits named-dialogue rows with source-file metadata.

## Durable Patterns That Worked

- Cache raw pages and keep a clean JSON source for reproducible parsing.
- Restrict output to named dialogue where possible.

## Durable Patterns That Failed

- Duplicate output names can create confusion about which JSONL file is canonical.

## Current Review Snapshot

The clean dialogue output is final. The non-clean output is listed as a cleanup
candidate only after hash and reference verification.

## Evidence

- `review_outputs/new_buddhist_sources/zen_koans_database_clean_dialogue.jsonl`: 98 rows.
- `review_outputs/new_buddhist_sources/zen_koans_database_dialogue.jsonl`: duplicate candidate.
- `docs/cleanup/delete_candidates.md`: cleanup gate for duplicate output.

## Related Parsers

- [[parse_gateless_gate]]: Shares Zen koan material.
- [[parse_blue_cliff_record]]: Shares case/story extraction concerns.

## Open Questions

- Which Zen Koans output path should remain canonical after hash checks?

## Next Likely Improvements

- Compare hashes and references before approving any cleanup action.

