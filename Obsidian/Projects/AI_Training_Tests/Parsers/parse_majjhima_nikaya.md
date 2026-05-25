# parse_majjhima_nikaya.py

## Parser

- Code: `scripts/extraction/parse_majjhima_nikaya.py`
- Source: `source_texts/buddhist/clean/majjhima_nikaya_dhammatalks_selected.txt`
- Outputs: `review_outputs/new_buddhist_sources/majjhima_nikaya_dialogue.jsonl`

## Status

final

## Source And Outputs

Majjhima Nikaya contributes 168 rows to the current final Buddhist dataset. The
latest candidate output has 190 rows and reached machine approval after parser
redesign and three passing random samples.

## Extraction Strategy

The parser downloads or reads selected pages, builds a clean consolidated text,
extracts attributed local exchange windows, and filters malformed speaker labels.

## Durable Patterns That Worked

- Broader local exchange windows avoided the earlier one-row candidate collapse.
- Speaker attribution searches narration around reporting verbs after stripping
  embedded quote content.
- Rejecting malformed speaker labels before row construction improved review quality.

## Durable Patterns That Failed

- A strict continuity gate produced a one-row population; the project treats that
  as `machine-blocked`, not a pass.

## Current Review Snapshot

`review_outputs/parser_reviews/parse_majjhima_nikaya/status_marker.txt` reports
`machine-approved`. The pass history records three consecutive passing random
sets after the rewrite.

## Evidence

- `review_outputs/parser_reviews/parse_majjhima_nikaya/pass_history.md`: approval history.
- `review_outputs/parser_reviews/parse_majjhima_nikaya/set_05/status_marker.txt`: final passing set.
- `review_outputs/new_buddhist_sources/majjhima_nikaya_dialogue.jsonl`: 190 candidate rows.

## Related Parsers

- [[parse_vimalakirti]]: Shares approval-through-random-samples workflow.
- [[parse_diamond_sutra]]: Shares attributed sutra dialogue concerns.

## Open Questions

- Should the final dataset be refreshed from 168 to the 190-row approved output?

## Next Likely Improvements

- If final rows are refreshed, regenerate dashboard data and dataset notes.

