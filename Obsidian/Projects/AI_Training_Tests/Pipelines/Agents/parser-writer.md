# parser-writer

## Status

active

## Purpose

Create or update one source parser, generate candidate dialogue rows, and fix
only the sample issues returned by [[sample-reviewer]] during the review loop.

## Required Reading

- [[../../Parsers/Parser Hub]]
- Related parser notes for the closest source shape.
- The source text or source artifact being parsed.
- The closest existing parser code in `scripts/extraction/`.
- [[../New Parser Review Pipeline]]

## Scope

- Work on one parser or one parser family per pass.
- Preserve the current three-message chat row format.
- Preserve the `conversation so far -> next reply` training objective.
- Use `Participant A` / `Participant B` consistently in user prompts.
- Keep source wording intact except for cleanup of OCR debris, headers,
  footnotes, malformed fragments, or local formatting artifacts.
- Do not promote rows to final datasets unless the user explicitly asks for that
  promotion and the manifest/dashboard/vault updates are included.

## Expected Edits

- Parser code under `scripts/extraction/` or the active package path after a
  future migration.
- Candidate JSONL under the appropriate `review_outputs/` path.
- Review pass artifacts under `review_outputs/parser_reviews/<parser_name>/`.
- Parser note updates when a durable extraction pattern, failure mode, or review
  state changes.

## Parser Pass

1. Inspect related parser code and notes before editing.
2. Make the narrow parser change needed for the current source.
3. Run the parser and schema checks available for that parser family.
4. Run `tools/review_pipeline/run_new_parser_pass.py` or the equivalent
   `random_sample.py` plus `render_review_packet.py` sequence.
5. Hand the review packet to [[sample-reviewer]].
6. Wait for reviewer issues before another parser edit pass.
7. If the reviewer returns `No sample issues found.`, record the clean sample
   status without treating it as automatic final approval.

## Handoff Format

```md
Parser: `scripts/extraction/parse_example.py`
Source: `source_texts/.../example.txt`
Output: `review_outputs/.../example_dialogue.jsonl`
Review pass: `review_outputs/parser_reviews/parse_example/set_01/`
Commands run:
- `python scripts/extraction/parse_example.py`
- `python tools/review_pipeline/run_new_parser_pass.py ...`
- `python -m pytest ...`
Known limits:
- Narrow unresolved item, or `None`.
```

## Fixing Reviewer Issues

- Treat reviewer findings as scoped sample feedback, not a request for broad
  parser redesign.
- Fix the root parser rule when multiple sampled rows show the same failure.
- If a reviewer issue conflicts with the listed criteria, pause and clarify
  instead of silently raising the standard.
- After each fix, generate a new random sample with a new seed.

## Links

- [[../New Parser Review Pipeline]]: alternating parser-writer and
  sample-reviewer loop.
- [[sample-reviewer]]: reviewer criteria and issues-only response format.
- [[../../Parsers/Parser Hub]]: parser status map and review rules.
