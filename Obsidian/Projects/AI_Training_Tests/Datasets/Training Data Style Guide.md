# Training Data Style Guide

## Status

active

## Current Record Shape

The active format is direct-source chat training data with exactly three
messages:

1. `system`: a short instruction for a philosophical interlocutor.
2. `user`: `Conversation so far:` followed by source-grounded participant turns.
3. `assistant`: the next reply from the target participant.

The schema is enforced by `scripts/extraction/dialogue_schema.py` and tested in
`tests/test_dialogue_schema.py`.

## User Prompt Convention

Use this prompt shape:

```text
Conversation so far:
Participant A (Source Speaker): ...
Participant B (Source Speaker): ...

Write Participant A's next reply.
```

The target participant must match `metadata.target_participant`, and the
assistant message must be the next reply only.

## Participant Convention

- Use `Participant A`, `Participant B`, and additional participant letters only
  as stable training labels.
- Keep source speaker names in parentheses when available.
- Do not ask the model to answer as an abstract assistant when the source target
  is a named speaker.
- Do not merge multiple scenes into one prompt.

## Metadata Convention

Each row should include:

- `record_id`
- `kind`
- `source`
- `source_file`
- `source_lines`
- `target_speaker`
- `target_participant`
- `target_words`

`target_words` must match the assistant text word count.

## Approved Row Qualities

- The assistant target follows naturally from the prompt context.
- The row preserves source wording and source speaker identity.
- The prompt has enough context for the next reply.
- The row avoids page headers, footnotes, OCR bleed, and commentary contamination.
- The row does not invent transitions between unrelated source scenes.

## Review Guardrails

- Mildly thin context is acceptable when the row is coherent and correctly
  formatted.
- A clean sample does not automatically promote a parser; parser approval needs
  the configured review gate.
- Collapsed candidate pools are failures, not approvals.

## Links

- [[Projects/AI_Training_Tests/Datasets/Dataset Progress]]
- [[Projects/AI_Training_Tests/Datasets/Approved Examples]]
- [[Projects/AI_Training_Tests/Parsers/Parser Hub]]

