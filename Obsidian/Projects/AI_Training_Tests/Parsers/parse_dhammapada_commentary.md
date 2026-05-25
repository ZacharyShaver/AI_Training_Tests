# parse_dhammapada_commentary.py

## Parser

- Code: `scripts/extraction/parse_dhammapada_commentary.py`
- Source: `source_texts/buddhist/clean/dhamma_verses_commentary.txt`
- Outputs: `review_outputs/new_buddhist_sources/dhammapada_commentary_dialogue_review_sample.md`

## Status

candidate

## Source And Outputs

Dhammapada Commentary has a parser and review sample artifact, but no final
dataset promotion is recorded in the current manifest.

## Extraction Strategy

The parser reads attributed turns from the clean commentary corpus, builds local
dialogue history, and writes reviewable chat rows.

## Durable Patterns That Worked

- Keep commentary extraction conservative and source-line anchored.
- Use source-specific turn parsing before row construction.

## Durable Patterns That Failed

- Commentary stories can look conversational while still lacking direct reply
  continuity.

## Current Review Snapshot

Review samples exist, including a very small Pesala commentary artifact that
should be treated as diagnostic rather than approval evidence.

## Evidence

- `scripts/extraction/parse_dhammapada_commentary.py`: parser code.
- `review_outputs/new_buddhist_sources/dhammapada_commentary_dialogue_review_sample.md`: review sample.
- `review_outputs/new_buddhist_sources/dhammapada_pesala_commentary_dialogue_review_sample.md`: tiny alternate sample.

## Related Parsers

- [[parse_sutta_nipata]]: Shares Buddhist teaching and verse-adjacent material.
- [[parse_udana]]: Shares risk of narrative context around teaching passages.

## Open Questions

- Does the candidate output have enough coherent direct replies for final use?

## Next Likely Improvements

- Generate a full JSONL candidate if missing, then sample it with the new review pipeline.

