# base_dialogue_dataset.py

## Parser

- Code: `scripts/extraction/build_pilot_dialogue_dataset.py`
- Sources: `oritiginal text/Milinda Panha.txt`, `oritiginal text/Platform Sutra .txt`,
  `oritiginal text/The Corpus Hermeticum.txt`, `oritiginal text/the_key-to-theosophy.txt`
- Outputs: final rows inside `review_outputs/full_dialogue_dataset/`

## Status

final

## Source And Outputs

This legacy builder supplies the current final rows for Milinda Panha, Platform
Sutra, The Corpus Hermeticum, and The Key to Theosophy. It still depends on the
misspelled `oritiginal text/` path, so do not move source files until compatibility
paths and reference updates are in place.

## Extraction Strategy

The script builds direct-source dialogue rows from explicit speaker cues and
selected Buddhist cue blocks, then writes chat records using the shared dialogue
schema helpers.

## Durable Patterns That Worked

- Use source-specific speaker maps instead of assuming generic Q/A labels.
- Preserve source wording and line evidence in row metadata.
- Select spread-out examples rather than only the first matching passages.

## Durable Patterns That Failed

- Treating mixed narrative, commentary, and quotation blocks as ordinary dialogue
  creates weak rows.
- Moving or renaming legacy source folders before wrappers exist breaks current
  rebuild paths.

## Current Review Snapshot

The rows are part of the current final datasets, but this builder predates the
new parser-specific random-sample approval notes.

## Evidence

- `scripts/extraction/build_pilot_dialogue_dataset.py`: current legacy builder.
- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`:
  contains Milinda Panha and Platform Sutra final rows.
- `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`:
  contains Corpus Hermeticum and Key to Theosophy final rows.

## Related Parsers

- [[parse_asclepius]]: Esoteric parser using explicit dialogue turns.
- [[parse_vimalakirti]]: Buddhist parser where conservative context gates matter.

## Open Questions

- Should the legacy builder be split into source-specific parser modules during
  package migration?

## Next Likely Improvements

- Add a compatibility wrapper before moving `oritiginal text/`.
- Add parser-specific review packets for each legacy source.

