# Hermes Memory Protocol

This protocol keeps the Obsidian vault useful as durable project memory for
`AI_Training_Tests`.

## Purpose

Use `Obsidian/` for human-readable project context that should survive across
sessions: decisions, subsystem maps, review state, workflow rules, and links to
evidence.

## Read Rules

Before non-trivial work, read the relevant vault notes when the task:

- depends on prior project decisions
- touches an existing subsystem with stored notes
- asks for consistency with prior work
- involves parser review, workflow history, or evidence tracking

For trivial, self-contained tasks, skip the vault unless the user asks for it.

## Write Rules

Update durable notes when:

- the user explicitly asks for project memory updates
- a durable workflow or decision changes
- a subsystem map, review state, or best-practice note would otherwise become misleading

Prefer concise summaries, status-driven notes, links to repo artifacts, and
cross-links between related notes.

## Do Not Store

- secrets or auth material
- large copied source passages
- full generated JSONL rows unless a compact example is necessary
- transient run logs unless the user explicitly asks for them

## Evidence Links

Link to real artifacts instead of duplicating them. Current high-value evidence
locations include:

- `config/dataset_manifest.json`
- `dashboard/index.html`
- `dashboard/project-progress-data.js`
- `docs/architecture/current_repo_inventory.md`
- `docs/cleanup/delete_candidates.md`
- `review_outputs/full_dialogue_dataset/`
- `review_outputs/parser_reviews/`

## Status Vocabulary

- `active`: current working source, parser, or workflow
- `final`: accepted into the current final dataset
- `candidate`: generated but not promoted
- `in review`: awaiting parser or sample review
- `blocked`: waiting on source, parser, or policy decision
- `stale`: known to be outdated and should not drive current decisions

