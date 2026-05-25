# sample-reviewer

## Status

active

## Purpose

Review one random sample packet from a parser pass and return only actionable
sample issues. This role does not approve final dataset promotion by itself.

## Inputs

- Current review packet:
  `review_outputs/parser_reviews/<parser_name>/set_##/<dataset_name>_set_##_random_review.md`
- Current sample manifest:
  `review_outputs/parser_reviews/<parser_name>/set_##/sample_manifest.md`
- Optional parser context from [[../../Parsers/Parser Hub]] when needed to
  understand source naming or review history.

## Scope

- Inspect only the rows in the current random sample.
- Use only the criteria listed below.
- Do not review unrelated parser code unless the user explicitly asks.
- Do not introduce stricter rules than the listed criteria.
- Do not reject rows for mild thinness if they are coherent, source-faithful,
  and correctly formatted.

## Criteria

- Is the sample a complete enough conversation or teaching exchange with relevant
  context?
- Is it good training data for the current `conversation so far -> next reply`
  format?
- Are source artifacts, OCR debris, footnote bleed, headers, or malformed
  fragments still present?
- Is the row in the correct three-message chat format?
- Does the user prompt use `Participant A` / `Participant B` consistently?
- Does the assistant target match the requested participant or speaker?

## Response Rules

- If issues are found, return issues only.
- Group issues by record ID.
- Name the narrow criterion each issue violates.
- Keep fixes specific enough for [[parser-writer]] to act on.
- If no issues are found, return exactly: `No sample issues found.`

## Issue Format

```md
record_id_here
- Criterion: Row format.
- Issue: The prompt uses Participant A twice, but the assistant target is
  Participant B.
- Fix direction: Regenerate the row so the prompt and assistant target agree.
```

## Links

- [[../New Parser Review Pipeline]]: full parser pass loop.
- [[parser-writer]]: paired implementation role.
- [[../../Parsers/Parser Hub]]: parser status and durable review rules.
