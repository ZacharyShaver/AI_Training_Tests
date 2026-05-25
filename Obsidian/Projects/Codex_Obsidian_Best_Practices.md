# Codex + Obsidian Best Practices

Use this note as the operating guide for making the most of Codex with the
`AI_Training_Tests` vault.

## When Codex Should Consult The Vault

Codex should read the relevant Obsidian notes before non-trivial work when:

- the task depends on prior project decisions
- the work touches an existing subsystem with stored notes
- the user asks for consistency with prior work
- the work involves parser review, workflow history, or evidence tracking

Primary entrypoints:

- [[00_Index]]
- [[Hermes_Memory_Protocol]]
- [[Projects/AI_Training_Tests]]

## How To Ask Codex To Use The Vault

Useful prompts:

- "Check the Obsidian vault first and keep the project memory current."
- "Update the relevant vault note with the durable decision."
- "Use the Parser Hub and related parser notes before changing this parser."
- "Link the evidence instead of copying generated artifacts into Obsidian."

## What Belongs In Durable Project Memory

- current architecture maps
- parser status, parser relationships, and durable extraction lessons
- dataset style guidance and approved examples
- review workflow rules and stopping conditions
- cleanup gates and explicit approval status
- links to source artifacts, generated outputs, tests, and plans

## What Should Stay Out

- secrets, tokens, and auth material
- large copied source passages
- large copied generated JSONL outputs
- transient command logs without a durable decision
- speculation that is not marked as an open question

## Note Pattern

Prefer this compact pattern:

```md
# Note Title

## Status

active | final | candidate | in review | blocked | stale

## Summary

Short durable context.

## Evidence

- `path/to/artifact`: why it matters

## Links

- [[Related Note]]: reason for the relationship

## Open Questions

- Narrow unresolved item.
```

## Parser Review Notes

For parser work, start at [[Projects/AI_Training_Tests/Parsers/Parser Hub]] and keep
individual parser notes concise. Link to `scripts/extraction/`,
`review_outputs/parser_reviews/`, and dataset artifacts rather than pasting long
samples into notes.

## Dataset Notes

For dataset work, start at [[Projects/AI_Training_Tests/Datasets/Dataset Progress]] and
`dashboard/index.html`. The dashboard should remain generated from live JSONL
counts, and stale documentation should not override the manifest or dashboard.
