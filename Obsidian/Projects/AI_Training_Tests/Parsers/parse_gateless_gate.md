# parse_gateless_gate.py

## Parser

- Code: `scripts/extraction/parse_gateless_gate.py`
- Source: `source_texts/buddhist/gateless_gate_wikisource_raw.json`
- Outputs: `review_outputs/new_buddhist_sources/gateless_gate_dialogue.jsonl`

## Status

final

## Source And Outputs

The Gateless Gate contributes 129 rows to the current final Buddhist dataset.
An additional internal-dialogue output exists as a separate candidate artifact.

## Extraction Strategy

The parser reads koan cases, preserves case numbers and titles, and emits
koan-to-commentary style rows plus optional internal-dialogue candidates.

## Durable Patterns That Worked

- Use case number as the source locator when line-based evidence is unavailable.
- Keep internal-dialogue candidates separate from final dialogue rows.

## Durable Patterns That Failed

- Blending case, comment, and verse material without labels weakens review.

## Current Review Snapshot

The main dialogue output is final; internal-dialogue rows remain candidate-only.

## Evidence

- `review_outputs/new_buddhist_sources/gateless_gate_dialogue.jsonl`: 129 rows.
- `review_outputs/new_buddhist_sources/gateless_gate_internal_dialogue.jsonl`: 31 candidate rows.
- `review_outputs/new_buddhist_sources/gateless_gate_dialogue_review_sample.md`: review sample.

## Related Parsers

- [[parse_blue_cliff_record]]: Shares koan case parsing.
- [[parse_zen_koans_database]]: Shares Zen story format.

## Open Questions

- Are internal-dialogue rows useful enough to review separately?

## Next Likely Improvements

- Keep internal candidates out of final data until sampled and approved.

