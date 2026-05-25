# parse_itivuttaka.py

## Parser

- Code: `scripts/extraction/parse_itivuttaka.py`
- Source: `source_texts/buddhist/clean/itivuttaka_thanissaro.txt`
- Outputs: `review_outputs/new_buddhist_sources/itivuttaka_dialogue.jsonl`

## Status

final

## Source And Outputs

Itivuttaka contributes 107 rows to the current final Buddhist dataset.

## Extraction Strategy

The parser identifies prose-to-verse teaching items and writes rows that ask for
the next reply in the source-grounded teaching sequence.

## Durable Patterns That Worked

- Segment by source item before constructing dialogue rows.
- Preserve source line ranges across the full teaching block.

## Durable Patterns That Failed

- Treating every verse as an ordinary conversational answer can create weak
  context unless the prompt establishes the teaching setup.

## Current Review Snapshot

The output is final and has a review sample artifact.

## Evidence

- `review_outputs/new_buddhist_sources/itivuttaka_dialogue.jsonl`: 107 rows.
- `review_outputs/new_buddhist_sources/itivuttaka_dialogue_review_sample.md`: review sample.
- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`: final dataset.

## Related Parsers

- [[parse_udana]]: Shares prose-to-inspired-utterance structure.
- [[parse_sutta_nipata]]: Shares verse-adjacent Buddhist source material.

## Open Questions

- Should future review distinguish verse-target rows from direct dialogue rows?

## Next Likely Improvements

- Add approval history if re-sampled under the newer parser review protocol.

