# parse_udana.py

## Parser

- Code: `scripts/extraction/parse_udana.py`
- Source: `source_texts/buddhist/clean/udana.txt`
- Outputs: `review_outputs/new_buddhist_sources/udana_exclamation_dialogue.jsonl`

## Status

final, with candidate direct-dialogue rows

## Source And Outputs

The current final dataset uses 80 Udana exclamation rows. A separate
`udana_dialogue.jsonl` candidate output has 107 direct-dialogue rows and should
be reviewed separately before any promotion.

## Extraction Strategy

The parser segments source blocks, extracts inspired utterance items, and also
contains logic for direct dialogue turns.

## Durable Patterns That Worked

- Keep exclamation rows and direct-dialogue rows separate.
- Preserve block-level source lines for traceability.

## Durable Patterns That Failed

- Direct dialogue extraction can be tempting to promote prematurely because it
  has more rows, but it needs separate sample review.

## Current Review Snapshot

The exclamation output is final. The direct-dialogue output is a candidate noted
in `config/dataset_manifest.json`.

## Evidence

- `review_outputs/new_buddhist_sources/udana_exclamation_dialogue.jsonl`: 80 final rows.
- `review_outputs/new_buddhist_sources/udana_dialogue.jsonl`: 107 candidate rows.
- `review_outputs/new_buddhist_sources/udana_exclamation_dialogue_review_sample.md`: review sample.

## Related Parsers

- [[parse_itivuttaka]]: Shares prose-to-utterance shape.
- [[parse_sutta_nipata]]: Shares Buddhist teaching-block parsing.

## Open Questions

- Should direct-dialogue Udana rows be reviewed as a separate source family?

## Next Likely Improvements

- Run direct-dialogue candidates through the new random-sample review workflow.

