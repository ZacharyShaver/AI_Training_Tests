# parse_sutta_nipata.py

## Parser

- Code: `scripts/extraction/parse_sutta_nipata.py`
- Source: `source_texts/buddhist/clean/sutta_nipata.txt`
- Outputs: `review_outputs/new_buddhist_sources/sutta_nipata_dialogue.jsonl`

## Status

final

## Source And Outputs

Sutta Nipata contributes 80 rows to the current final Buddhist dataset.

## Extraction Strategy

The parser segments clean text into sections, identifies target teaching or
dialogue passages, and writes chat rows with source-line evidence.

## Durable Patterns That Worked

- Section-level parsing keeps verse and prose context from drifting.
- Review samples next to candidate JSONL make source-specific checking easier.

## Durable Patterns That Failed

- Verse-heavy passages need careful prompt framing so the assistant target is
  not detached from the setup.

## Current Review Snapshot

The generated output is final and has a review sample artifact.

## Evidence

- `review_outputs/new_buddhist_sources/sutta_nipata_dialogue.jsonl`: 80 rows.
- `review_outputs/new_buddhist_sources/sutta_nipata_dialogue_review_sample.md`: review sample.
- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`: final dataset.

## Related Parsers

- [[parse_itivuttaka]]: Shares verse-adjacent teaching rows.
- [[parse_udana]]: Shares Buddhist teaching-block segmentation.

## Open Questions

- Should verse-adjacent rows have a shared review rubric note?

## Next Likely Improvements

- Re-sample under the new random-sample review pipeline if parser policy changes.

