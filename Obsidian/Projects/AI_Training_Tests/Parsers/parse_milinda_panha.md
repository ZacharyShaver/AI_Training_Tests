# parse_milinda_panha.py

## Parser

- Code: `src/ai_training_tests/extraction/parsers/milinda_panha.py`
- Wrapper: `scripts/extraction/parse_milinda_panha.py`
- Canonical source: `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- Raw source cache: `source_texts/buddhist/raw/milindapanha_suttacentral/`
- Candidate outputs: `review_outputs/new_buddhist_sources/milinda_panha_dialogue.jsonl`
- Review pipeline: `review_outputs/parser_reviews/parse_milinda_panha/`

## Status

candidate

## Source And Outputs

This parser is the new Milinda path built on the SuttaCentral export rather than
the OCR-heavy legacy text under `oritiginal text/`. It is not the live final
Milinda path yet; the legacy base builder still supplies the current final rows
until this parser clears review.

## Current Snapshot

- Latest local smoke run: `55` turns parsed, `25` candidate rows written.
- First parser-review packet: `review_outputs/parser_reviews/parse_milinda_panha/set_01/`
- Current live final Milinda rows still come from [[base_dialogue_dataset]].

## Extraction Strategy

- Read stable `## mil...` section headings emitted by the SuttaCentral export.
- Recover alternating quoted exchanges between `King Milinda` and
  `Venerable Nāgasena`.
- Build Buddhist `conversation so far -> next reply` rows with `Nāgasena` as the
  target reply speaker.

## Durable Patterns That Worked

- SuttaCentral gives a much cleaner, almost pre-parsed corpus than OCR/PDF
  conversion and is a better long-term source-ingest path.
- Cache-first export plus a local canonical text file makes parser iteration
  reproducible.
- Same-paragraph cue-plus-quote lines can be recovered once the parser preserves
  raw section headers and consumes inline quoted turns directly.

## Known Current Limitations

- The candidate pool is still smaller than the old live Milinda coverage.
- Some exported text still shows mojibake such as `NÄgasena`, so the ingest or
  normalization layer needs another encoding pass.
- Multi-quote alternation needs review before promotion because some long
  same-line exchanges may still mis-assign speakers.

## Evidence

- `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- `review_outputs/new_buddhist_sources/milinda_panha_dialogue.jsonl`
- `review_outputs/parser_reviews/parse_milinda_panha/set_01/run_summary.md`
- `review_outputs/parser_reviews/parse_milinda_panha/set_01/milinda_panha_dialogue_set_01_random_review.md`

## Related Notes

- [[Parser Hub]]
- [[base_dialogue_dataset]]
- [[../Sources/Buddhist Sources]]
