# parse_milinda_panha.py

## Parser

- Code: `src/ai_training_tests/extraction/parsers/milinda_panha.py`
- Wrapper: `scripts/extraction/parse_milinda_panha.py`
- Canonical source: `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- Raw source cache: `source_texts/buddhist/raw/milindapanha_suttacentral/`
- Candidate outputs: `review_outputs/new_buddhist_sources/milinda_panha_dialogue.jsonl`
- Review pipeline: `review_outputs/parser_reviews/parse_milinda_panha/`

## Status

parked

## Source And Outputs

This parser is the new Milinda path built on the SuttaCentral export rather than
the OCR-heavy legacy text under `oritiginal text/`. It is not the live final
Milinda path; the legacy base builder still supplies the current final rows, and
this candidate line is now parked after a low-yield refresh.

## Current Snapshot

- Latest candidate refresh: `14` rows after source-boundary cleanup and a
  stricter minimum target floor.
- Review packets: `set_01/` baseline at `25` rows and `set_02/` refresh at
  `14` rows.
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
- Source-boundary mojibake cleanup is more reliable than trying to patch broken
  speaker names later inside parser-only logic.

## Durable Patterns That Failed

- Even after the cleaner export and speaker fixes, the candidate pool stayed too
  small to justify further Milinda-focused iteration right now.
- Tightening target quality removed several stock-reply rows, which improved the
  pool quality but confirmed the limited upside of this source.

## Current Review Snapshot

- `review_outputs/parser_reviews/parse_milinda_panha/pass_history.md` still
  shows `0` consecutive fully approved sets because this parser was parked
  rather than pushed through the full three-pass approval loop.
- This note should be treated as a non-final reference path, not the next
  Buddhist promotion target.

## Evidence

- `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- `review_outputs/new_buddhist_sources/milinda_panha_dialogue.jsonl`
- `review_outputs/parser_reviews/parse_milinda_panha/set_02/run_summary.md`
- `review_outputs/parser_reviews/parse_milinda_panha/set_02/milinda_panha_dialogue_set_02_random_review.md`

## Related Notes

- [[Parser Hub]]
- [[base_dialogue_dataset]]
- [[../Sources/Buddhist Sources]]

## Next Likely Improvements

- None scheduled. Revisit only if a broader Milinda objective returns or the
  Buddhist source backlog thins out.
