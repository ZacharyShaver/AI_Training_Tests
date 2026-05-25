# New Parser Review Pipeline

## Status

active

## Purpose

This workflow creates or updates one parser at a time, then gates the output with
fresh random samples before any candidate rows are promoted into the final
datasets.

## Roles

- [[Agents/parser-writer]]: drafts or fixes parser code and regenerates output.
- [[Agents/sample-reviewer]]: reviews only the current random sample and returns
  issues only.

## Loop

1. The parser writer reads [[../Parsers/Parser Hub]], related parser notes, the
   source text, and the closest existing parser code.
2. The parser writer creates or updates one parser while preserving the project
   three-message chat format.
3. The parser output is generated as JSONL.
4. `tools/review_pipeline/run_new_parser_pass.py` creates a fresh random sample,
   sample manifest, review packet, and run summary under
   `review_outputs/parser_reviews/<parser_name>/set_##/`.
5. The sample reviewer inspects only the current sample packet.
6. If issues are found, the reviewer returns issues only, grouped by record ID.
7. The parser writer fixes only the reported issues, then starts a new pass with
   a new seed and fresh sample.
8. If no issues are found, the reviewer returns exactly `No sample issues found.`

## Reviewer Criteria

Do not introduce stricter rules than these criteria:

- Is the sample a complete enough conversation or teaching exchange with relevant
  context?
- Is it good training data for the current `conversation so far -> next reply`
  format?
- Are source artifacts, OCR debris, footnote bleed, headers, or malformed
  fragments still present?
- Is the row in the correct three-message chat format?
- Does the user prompt use `Participant A` / `Participant B` consistently?
- Does the assistant target match the requested participant or speaker?

Do not reject coherent rows for mild thinness if they preserve source continuity
and the target reply follows naturally from the prompt context.

## Sampling Rules

- Default sample size is 10 rows.
- Each pass uses a fresh random seed unless debugging requires a fixed seed.
- If the parser output has fewer than 10 rows, sample the full output and mark
  the manifest as `small population`.
- A clean sample does not automatically mean final approval; it means the parser
  passed the requested sample review gate.

## Output Shape

```text
review_outputs/parser_reviews/<parser_name>/
  pass_history.md
  status_marker.txt
  set_01/
    sample_manifest.md
    run_summary.md
    parser_fix_notes.md
    <dataset_name>_set_01.jsonl
    <dataset_name>_set_01_random_review.md
```

## Handoff Format

Parser writer handoff:

- parser changed
- source artifact
- output JSONL
- review pass directory
- test and generation commands run
- known limits or open questions

Sample reviewer handoff:

- `No sample issues found.`
- or issues only, grouped by record ID, with the narrow criterion each issue
  violates.

## Evidence

- `tools/review_pipeline/random_sample.py`: seeded sample selection and manifest.
- `tools/review_pipeline/render_review_packet.py`: review packet renderer.
- `tools/review_pipeline/run_new_parser_pass.py`: parser pass orchestration.
- `tests/test_review_pipeline_random_sample.py`: deterministic sampling coverage.
- `tests/test_review_pipeline_packet.py`: review packet format coverage.

## Links

- [[../Parsers/Parser Hub]]: parser status and current review rules.
- [[Agents/parser-writer]]: parser writer prompt.
- [[Agents/sample-reviewer]]: sample reviewer prompt.

## Open Questions

- Should parser approval continue to require three consecutive clean random
  samples, or should small-population parsers use a different approval rule?
