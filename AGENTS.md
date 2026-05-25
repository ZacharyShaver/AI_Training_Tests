# AGENTS

## Project Memory

This repository uses `hermes_memory_vault/` as its human-readable project memory layer.

Primary entrypoints:

- `hermes_memory_vault/00_Index.md`
- `hermes_memory_vault/Hermes_Memory_Protocol.md`
- `hermes_memory_vault/Projects/AI_Training_Tests.md`

## When To Read The Vault

Check the relevant vault notes before non-trivial work, especially when:

- the task depends on prior project decisions
- the task touches an existing subsystem with stored notes
- the user asks for consistency with prior work
- the work involves parser review, workflow history, or evidence tracking

Skip the vault for trivial self-contained tasks unless the user asks for it.

## How To Use The Vault

Treat the vault as the durable, human-readable context layer.

Prefer:

- concise summaries
- status-driven notes
- links to repo artifacts
- cross-links between related notes

Avoid:

- copying large artifacts into the vault
- storing secrets or auth material
- turning notes into transient run logs unless the user explicitly wants that

## Updating The Vault

Update the relevant vault notes when:

- the user explicitly asks for project memory updates
- a durable workflow or decision has changed
- a subsystem map, review state, or best-practice note would otherwise become misleading

When updating, prefer summaries and links over copied content.

## Existing Guidance

For Codex/Obsidian workflow guidance, see:

- `hermes_memory_vault/Projects/Codex_Obsidian_Best_Practices.md`
