# parse_asclepius.py

## Parser

- Code: `scripts/extraction/parse_asclepius.py`
- Source: `oritiginal text/Asclepius.txt`
- Outputs: `review_outputs/new_esoteric_sources/asclepius_dialogue.jsonl`

## Status

final

## Source And Outputs

Asclepius currently contributes 25 rows to the final occult / esoteric dataset.
The parser writes a review sample next to its JSONL output.

## Extraction Strategy

The parser reads attributed turns, builds short dialogue histories, and targets
the next speaker reply while preserving source file and line metadata.

## Durable Patterns That Worked

- Use explicit speaker attribution rather than inferring from prose alone.
- Keep compact review samples beside generated JSONL.

## Durable Patterns That Failed

- Treating every adjacent quoted passage as a clean turn risks commentary bleed.

## Current Review Snapshot

The output is included in the final esoteric dataset. Expanded Asclepius is still
listed as a next-source opportunity in `config/dataset_manifest.json`.

## Evidence

- `review_outputs/new_esoteric_sources/asclepius_dialogue.jsonl`: 25 generated rows.
- `review_outputs/new_esoteric_sources/asclepius_dialogue_review_sample.md`: review sample.
- `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`: final dataset.

## Related Parsers

- [[base_dialogue_dataset]]: Shares esoteric direct-dialogue targets.

## Open Questions

- Can additional Asclepius rows be extracted cleanly without loosening context too far?

## Next Likely Improvements

- Run the new random-sample review pipeline against any expanded Asclepius output.

