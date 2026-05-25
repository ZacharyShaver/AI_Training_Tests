# parse_blue_cliff_record.py

## Parser

- Code: `scripts/extraction/parse_blue_cliff_record.py`
- Source: `source_texts/buddhist/raw/blue_cliff_record_wonderwheel_wayback.html`
- Outputs: `review_outputs/new_buddhist_sources/blue_cliff_record_*.jsonl`

## Status

candidate

## Source And Outputs

Blue Cliff Record has multiple candidate outputs: 10 dialogue rows, 31 ode rows,
and 227 internal dialogue candidates. These are not in the final dataset.

## Extraction Strategy

The parser splits case blocks, tracks case titles and numbers, and can emit
different row families for dialogue, ode, and internal-dialogue candidates.

## Durable Patterns That Worked

- Preserve case number and case title in metadata for review traceability.
- Mark the source scope as `personal_local_only_translation` where applicable.

## Durable Patterns That Failed

- Combining koan case, commentary, and verse material without row-family labels
  makes review criteria unclear.

## Current Review Snapshot

Candidate review samples exist, but the source has not been promoted into the
final dataset.

## Evidence

- `review_outputs/new_buddhist_sources/blue_cliff_record_dialogue.jsonl`: 10 rows.
- `review_outputs/new_buddhist_sources/blue_cliff_record_ode_dialogue.jsonl`: 31 rows.
- `review_outputs/new_buddhist_sources/blue_cliff_record_internal_dialogue_candidates.jsonl`: 227 rows.

## Related Parsers

- [[parse_gateless_gate]]: Shares koan case structure.
- [[parse_zen_koans_database]]: Shares compact Zen story extraction.

## Open Questions

- Which Blue Cliff row family should be reviewed first for promotion?
- Does the local-only source scope affect whether output should enter shared final data?

## Next Likely Improvements

- Run a fresh 10-row random sample on the intended candidate family.
- Keep row-family decisions explicit in the dataset manifest before promotion.

