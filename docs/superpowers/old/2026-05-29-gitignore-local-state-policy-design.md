# Gitignore Local State Policy Design

## Status

proposed

## Problem

The repository is accumulating machine-local noise in version control. The
current `.gitignore` covers a few Python and editor artifacts, but it does not
adequately suppress local Obsidian state, logs, temporary folders, and other
non-durable workspace metadata.

This is already visible in tracked local-state churn such as
`Obsidian/.obsidian/graph.json`.

## Goals

- Ignore most local Obsidian application state under `Obsidian/.obsidian/`.
- Ignore common local logs, cache folders, temp folders, and machine metadata.
- Keep durable project artifacts tracked, especially dataset outputs, dashboard
  files, manifest data, vault notes, and parser evidence.
- Keep the `.gitignore` readable and repo-specific instead of replacing it with
  a giant generic template.

## Non-Goals

- Ignoring `review_outputs/`, `dashboard/`, or other durable generated project
  artifacts by default.
- Reorganizing tracked files outside `.gitignore`.
- Cleaning the entire worktree in this pass.

## Current State

The current `.gitignore` includes:

- Python bytecode and `__pycache__`
- `.venv/`
- a small number of local cache and tool entries
- `Obsidian/.obsidian/workspace.json`

It does not broadly cover the rest of local Obsidian state, and it does not
provide a clear policy boundary between durable repo content and transient local
machine content.

## Proposed Policy

### 1. Treat Most Of `Obsidian/.obsidian/` As Local State

Ignore most files under `Obsidian/.obsidian/` because they are machine-local UI
and workspace state rather than durable project memory.

Examples of the kind of files this should cover:

- graph/layout state
- workspace/session state
- local plugin UI state
- appearance or pane state that changes by machine or user workflow

The vault content under `Obsidian/` should remain tracked. The ignore rule
should target application-state files, not the notes themselves.

### 2. Ignore Routine Local Noise

Add explicit ignore patterns for:

- log files such as `*.log`
- temp files such as `*.tmp`, `*.temp`
- local cache directories
- folder metadata such as `.folder`-style files if present
- common OS/editor machine artifacts that are not already covered

The goal is to stop predictable local churn from appearing in `git status`.

### 3. Preserve Durable Project Artifacts

Do not ignore:

- `review_outputs/`
- `dashboard/`
- `config/dataset_manifest.json`
- vault notes under `Obsidian/Projects/`
- parser outputs that are used as evidence or candidate artifacts

This repo intentionally keeps some generated outputs as durable evidence, so the
ignore rules must not erase that distinction.

### 4. Prefer Explicit Rules Over Blanket Globs

The `.gitignore` should stay understandable. Rules should be grouped by purpose:

- Python/build state
- editor and workspace state
- Obsidian local state
- logs and temporary files
- OS metadata

That makes future cleanup easier and reduces the chance of hiding something
important by accident.

## Implementation Outline

1. Update `.gitignore` with grouped local-state sections.
2. Ignore most of `Obsidian/.obsidian/` while preserving the tracked vault
   content outside that directory.
3. Add explicit local-noise rules for logs, temp files, cache folders, and
   machine metadata.
4. Re-check `git status` to confirm that the noisy local-state files are no
   longer surfaced as untracked changes.

## Verification

The change is complete for this pass when:

- `.gitignore` clearly expresses the local-state policy
- local Obsidian state no longer dominates `git status`
- durable project artifacts remain visible to git when changed

Useful verification commands:

```text
git status --short
git check-ignore -v <path>
```

## Risks

- Ignoring too much under `Obsidian/.obsidian/` could hide a setting that the
  repo intentionally wanted to share.
- Ignoring too broadly outside Obsidian could accidentally hide durable project
  evidence.

## Recommendation

Proceed with the curated local-state policy: ignore most Obsidian application
state and routine local noise, but keep durable dataset, dashboard, manifest,
and vault artifacts tracked.
