# parse_vimalakirti.py

## Parser

- Code: `scripts/extraction/parse_vimalakirti.py`
- Source: `source_texts/buddhist/clean/vimalakirti_nirdesa_sutra.txt`
- Outputs: `review_outputs/new_buddhist_sources/vimalakirti_dialogue.jsonl`

## Status

final

## Source And Outputs

Vimalakirti Nirdesa Sutra contributes 17 rows to the current final Buddhist
dataset. The parser is machine-approved after three passing random samples.

## Extraction Strategy

The parser extracts attributed turns, applies continuity fixes, and keeps the
candidate pool small rather than allowing cross-scene row drift.

## Durable Patterns That Worked

- Adaptive context plus continuity fixes produced a small but substantive row pool.
- Three independent random samples passed at 100 percent before approval.

## Durable Patterns That Failed

- Earlier parser versions emitted one-turn rows, pronoun-speaker rows, long
  scene jumps, and incomplete quote fragments.

## Current Review Snapshot

`review_outputs/parser_reviews/parse_vimalakirti/status_marker.txt` reports
machine approval with `current_set: set_05` and `consecutive_passes: 3`.

## Evidence

- `review_outputs/parser_reviews/parse_vimalakirti/pass_history.md`: approval history.
- `review_outputs/parser_reviews/parse_vimalakirti/set_05/status_marker.txt`: final passing set.
- `review_outputs/new_buddhist_sources/vimalakirti_dialogue.jsonl`: 17 generated rows.

## Related Parsers

- [[parse_majjhima_nikaya]]: Shares approval-through-random-samples workflow.
- [[parse_diamond_sutra]]: Shares attributed sutra dialogue extraction.

## Open Questions

- Is 17 rows the right stable final pool, or should future work revisit source coverage?

## Next Likely Improvements

- Keep future expansions behind the same three-sample approval gate.

