# parse_diamond_sutra.py

## Parser

- Code: `scripts/extraction/parse_diamond_sutra.py`
- Source: `source_texts/buddhist/diamond_sutra_gutenberg.txt`
- Outputs: `review_outputs/new_buddhist_sources/diamond_sutra_dialogue.jsonl`

## Status

final

## Source And Outputs

The Diamond Sutra contributes 83 rows to the current final Buddhist dataset.

## Extraction Strategy

The parser isolates the main body, extracts attributed turns, and builds rows
from short histories where the target reply follows the prompt context.

## Durable Patterns That Worked

- Strip source boilerplate before dialogue extraction.
- Preserve line ranges and source filename in metadata.

## Durable Patterns That Failed

- Attributed religious discourse can contain nested quotations that should not
  be mistaken for speaker turns.

## Current Review Snapshot

The generated output is final and has a review sample artifact.

## Evidence

- `review_outputs/new_buddhist_sources/diamond_sutra_dialogue.jsonl`: 83 rows.
- `review_outputs/new_buddhist_sources/diamond_sutra_dialogue_review_sample.md`: review sample.
- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`: final dataset.

## Related Parsers

- [[parse_vimalakirti]]: Shares attributed sutra dialogue concerns.
- [[parse_sutta_nipata]]: Shares Buddhist source format and conservative row construction.

## Open Questions

- Should the review sample be re-run through the newer random-sample protocol?

## Next Likely Improvements

- Add parser-specific approval history if this parser is re-reviewed.

