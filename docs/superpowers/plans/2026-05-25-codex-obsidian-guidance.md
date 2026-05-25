# Codex Obsidian Guidance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add project guidance that explains how to use Obsidian effectively with Codex CLI and tells future agents that this repo uses the local vault as a human-readable memory layer.

**Architecture:** Add one durable best-practices note inside `hermes_memory_vault/`, add one repo-root `AGENTS.md` with explicit vault usage guidance, and link the new note from the vault index so humans can find it quickly.

**Tech Stack:** Markdown, Obsidian wikilinks, repo guidance files

---

### Task 1: Add The Vault Best-Practices Note

**Files:**
- Create: `hermes_memory_vault/Projects/Codex_Obsidian_Best_Practices.md`

- [ ] **Step 1: Write the note content**

Create a concise note covering:

```md
# Codex + Obsidian Best Practices

## Purpose

Use this note as the operating guide for making the most of Codex CLI with this vault.
```

- [ ] **Step 2: Include concrete workflow guidance**

Document:

```md
- when Codex should consult the vault
- how to ask Codex to use the vault
- what belongs in durable project memory
- what should stay out of the vault
- note templates and status vocabulary
```

- [ ] **Step 3: Link the note into the vault graph**

Add links back to:

```md
[[00_Index]]
[[Hermes_Memory_Protocol]]
[[Projects/AI_Training_Tests]]
```

### Task 2: Add Repo-Root Agent Guidance

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Write project-level memory instructions**

Include:

```md
# AGENTS

## Project Memory

This repository uses `hermes_memory_vault/` as its human-readable project memory layer.
```

- [ ] **Step 2: Tell agents when to read and update the vault**

Specify:

```md
- check relevant vault notes before non-trivial work
- prefer summaries and links over copied artifacts
- update the vault when the user asks for durable project memory updates
```

### Task 3: Make The New Guidance Discoverable

**Files:**
- Modify: `hermes_memory_vault/00_Index.md`

- [ ] **Step 1: Add the new best-practices note to the main notes list**

Insert:

```md
- [[Projects/Codex_Obsidian_Best_Practices]]
```

### Task 4: Verify The Guidance Files

**Files:**
- Verify: `AGENTS.md`
- Verify: `hermes_memory_vault/Projects/Codex_Obsidian_Best_Practices.md`
- Verify: `hermes_memory_vault/00_Index.md`

- [ ] **Step 1: Verify files exist and links are present**

Run: `rg -n "Codex_Obsidian_Best_Practices|human-readable project memory layer|when Codex should consult the vault" AGENTS.md hermes_memory_vault/00_Index.md hermes_memory_vault/Projects/Codex_Obsidian_Best_Practices.md`

Expected: matching lines from all three files
