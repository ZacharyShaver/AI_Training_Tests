# Repo Architecture, Progress Dashboard, Vault, And Parser Review Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the project around a clearer dataset architecture, add a simple progress dashboard, populate the Obsidian vault, and define a two-agent parser creation and sample review pipeline.

**Architecture:** Keep implementation incremental and reversible. First create inventory and manifest files that describe the current state, then add the dashboard and vault notes from those manifests, then move code and data only after compatibility wrappers and tests are in place. No deletion happens automatically; deletion candidates are proposed, hash-checked, and removed only after explicit approval.

**Tech Stack:** Python 3.11, JSONL, pytest, Ruff, static HTML/CSS/JavaScript, Obsidian Markdown, Codex multi-agent workflow where available.

---

## Current Stocktake

### Current Top-Level Shape

- `.claude/`: untracked Claude-specific guidance and settings.
- `.codegraph/`: untracked CodeGraph index state, including `codegraph.db`.
- `.github/`: one Python quality workflow.
- `.vscode/`: editor settings.
- `ai_training_tests.egg-info/`: tracked generated package metadata.
- `docs/`: existing Superpowers specs and implementation plans.
- `Obsidian/`: new vault, currently only default Obsidian files and `Welcome.md`.
- `oritiginal text/`: legacy esoteric/original source folder, misspelled but still referenced by scripts.
- `review_outputs/`: generated datasets, review samples, and parser review runs.
- `scripts/`: current executable Python scripts.
- `source_texts/`: newer source text storage, mostly Buddhist raw and cleaned sources.
- `tests/`: small pytest suite for dialogue schema.
- `Training Data/`: legacy transcript and local chat training artifacts.

### Current Final Dataset Counts

Use actual JSONL line counts, not stale README counts:

| Dataset | Current Lines | Target Lines | Progress |
| --- | ---: | ---: | ---: |
| Buddhist final dataset | 854 | 1200 | 71.2% |
| Occult / esoteric final dataset | 423 | 1200 | 35.3% |
| Combined final dataset | 1277 | 2400 family target sum | 53.2% |

Current final paths:

- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`
- `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`
- `review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset.jsonl`

### Current Final Source Coverage

Buddhist final set:

- `Itivuttaka`: 107
- `Majjhima Nikaya`: 168 in split doc, 190 in current candidate output
- `Milinda Panha`: 73
- `Platform Sutra`: 19
- `Sutta Nipata`: 80
- `The Diamond Sutra`: 83
- `The Gateless Gate`: 129
- `Udana`: 80
- `Vimalakirti Nirdesa Sutra`: 17
- `Zen Koans Database`: 98

Occult / esoteric final set:

- `Asclepius`: 25
- `The Corpus Hermeticum`: 28
- `The Key to Theosophy`: 370

### Stale Documentation Found

These documents still report the older 862-row combined dataset state and must be refreshed from live counts:

- `README.md`
- `CODE_EXPLAINED.md`
- `project_intake_document.md`
- `project_memory.md`
- `review_outputs/full_dialogue_dataset/README.md`

`review_outputs/full_dialogue_dataset/full_dialogue_dataset_splits.md` is closer to current state and reports 1277 combined rows.

---

## Proposed Target Architecture

### Python Package And Script Layout

Create a package while preserving existing script entrypoints:

```text
src/ai_training_tests/
  __init__.py
  domain/
    dialogue_schema.py
    source_manifest.py
  extraction/
    common/
      text_cleaning.py
      review_samples.py
      jsonl_io.py
    parsers/
      asclepius.py
      blue_cliff_record.py
      dhammapada_commentary.py
      diamond_sutra.py
      gateless_gate.py
      itivuttaka.py
      majjhima_nikaya.py
      sutta_nipata.py
      udana.py
      vimalakirti.py
      zen_koans_database.py
    pipeline/
      build_full_dialogue_outputs.py
      combine_dialogue_datasets.py
      split_dialogue_dataset.py
      validate_dialogue_dataset.py
    review/
      review_policy.py
      random_sample.py
      review_packet.py
  data_prep/
  apps/
  dashboard/
```

Keep `scripts/` as thin wrappers during migration:

```text
scripts/extraction/parse_udana.py -> imports and calls ai_training_tests.extraction.parsers.udana.main
scripts/extraction/build_full_dialogue_outputs.py -> imports and calls ai_training_tests.extraction.pipeline.build_full_dialogue_outputs.main
```

This avoids breaking existing commands while giving the code a real architecture.

### Data And Output Layout

Introduce a clear target layout, then migrate in small steps:

```text
data/
  sources/
    buddhist/
      raw/
      clean/
    occult/
      raw/
      clean/
  legacy/
    original_text/

datasets/
  final/
    buddhist/
    occult/
    combined/
  candidates/
    buddhist/
    occult/

review_runs/
  parser_reviews/
```

Compatibility rule:

- Existing `review_outputs/`, `source_texts/`, `Training Data/`, and `oritiginal text/` paths remain until all scripts and docs are updated.
- Initial dashboard reads current paths.
- Later implementation can add a manifest mapping old paths to new paths and migrate with `git mv`.

---

## Deletion And Cleanup Proposals

No deletion should be performed until after explicit user approval. Each candidate requires either a hash comparison, an import check, or a one-line justification in `docs/cleanup/delete_candidates.md`.

### High-Confidence Delete Or Untrack Candidates

| Candidate | Why It Is Suspect | Required Check |
| --- | --- | --- |
| `ai_training_tests.egg-info/` | Generated package metadata should not be tracked. | Confirm package installs without tracked egg-info, add `*.egg-info/` to `.gitignore`. |
| `.codegraph/codegraph.db` | Generated local index, currently untracked. | Keep `.codegraph/.gitignore`; do not commit DB. |
| `Obsidian/.obsidian/workspace.json` | Local UI state, noisy in shared repo. | Add `.obsidian/workspace.json` to ignore if not already desired. |
| `review_outputs/full_dialogue_dataset/full_dialogue_dataset.jsonl` | Appears duplicate of `full_combined_dialogue_dataset.jsonl`. | Compare file hashes before deleting or replacing with docs pointer. |
| `review_outputs/new_buddhist_sources/zen_koans_database_dialogue.jsonl` | Appears duplicate of `zen_koans_database_clean_dialogue.jsonl`. | Compare file hashes and references. |

### Archive Or Delete After Review

| Candidate | Why It Is Suspect | Required Check |
| --- | --- | --- |
| `review_outputs/initial_dialogue_dataset/` | Older snapshot superseded by full dataset. | Confirm no unique records absent from final dataset. |
| `review_outputs/pilot_dialogue_dataset/` | Older pilot snapshot. | Confirm current full rebuild can regenerate needed base rows. |
| `Training Data/Test Conversations/dual_model_demo_*.jsonl` | Looks duplicated by `Training Data/cleaned_pipeline/cleaned_dialogue/`. | Compare hashes and keep one canonical transcript-derived folder. |
| `review_outputs/new_buddhist_sources/*_direct_review_sample.md` with tiny size | Likely empty sample or failed sample. | Open each file and confirm no durable review content. |
| `.claude/CLAUDE.md` | Tool-specific CodeGraph guidance overlaps `AGENTS.md`. | Either preserve as Claude-only, or move general CodeGraph note into `docs/tooling/codegraph.md`. |

### Rename Candidates

| Candidate | Issue | Proposed Destination |
| --- | --- | --- |
| `oritiginal text/` | Misspelled legacy folder. | `data/legacy/original_text/` after path migration. |
| `Training Data/` | Space in path and mixed concerns. | `data/legacy/training_data/` after path migration. |

---

## Dashboard Design

### Goal

Create a simple local webpage that shows current project progress at a glance:

- total line counts for final dataset files
- Buddhist and occult progress toward 1200 lines each
- per-source rows grouped by tradition
- document references and parser references
- current parser/review status
- "what's next" source candidates

### Files

- Create: `dashboard/index.html`
- Create: `dashboard/styles.css`
- Create: `dashboard/app.js`
- Create: `dashboard/project-progress-data.js`
- Create: `tools/dashboard/build_progress_data.py`
- Create: `tests/test_dashboard_progress_data.py`
- Create: `config/dataset_manifest.json`

### Data Contract

`tools/dashboard/build_progress_data.py` writes `dashboard/project-progress-data.js`:

```js
window.PROJECT_PROGRESS = {
  generated_at: "2026-05-25",
  goals: {
    buddhist_lines: 1200,
    occult_lines: 1200
  },
  totals: {
    buddhist_lines: 854,
    occult_lines: 423,
    combined_lines: 1277
  },
  sources: [
    {
      family: "buddhist",
      source: "The Gateless Gate",
      rows: 129,
      final_dataset: "review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl",
      parser: "scripts/extraction/parse_gateless_gate.py",
      vault_note: "Obsidian/Projects/AI_Training_Tests/Parsers/parse_gateless_gate.md",
      status: "final"
    }
  ],
  next_sources: [
    {
      family: "buddhist",
      source: "Blue Cliff Record",
      reason: "Candidate outputs already exist but are not final.",
      current_artifact: "review_outputs/new_buddhist_sources/blue_cliff_record_ode_dialogue.jsonl"
    }
  ]
};
```

### UI Layout

- Header: project name and generated date.
- Summary cards: Buddhist, occult, combined.
- Progress bars: Buddhist 854/1200 and occult 423/1200.
- Source table: grouped by Buddhist and occult, with rows, parser, output file, vault note, and status.
- What's Next: candidate source list with reason and current artifact.
- Cleanup Notice: stale docs and delete candidates listed as warnings until resolved.

### Future Source Candidates For UI

Near-term candidates already represented in repo artifacts:

- Buddhist: `Blue Cliff Record`
- Buddhist: `Dhammapada Commentary`
- Buddhist: `Udana` direct dialogue rows beyond final-only exclamation rows
- Buddhist: additional Majjhima Nikaya pass if current 190-row candidate is promoted into final split
- Occult: expanded `Asclepius` if more clean dialogue can be extracted

External candidates to evaluate later, with license/source verification before ingestion:

- Occult: additional Hermetic texts not yet in repo
- Occult: Theosophical dialogue or catechism-style texts that match the current `conversation so far -> next reply` format
- Buddhist: public-domain or permissively licensed dialogue-heavy sutra/commentary texts

---

## Obsidian Vault Population Plan

### Vault Root

Use `Obsidian/` as canonical, matching `AGENTS.md`.

### Files To Create

- Create: `Obsidian/00_Index.md`
- Create: `Obsidian/Hermes_Memory_Protocol.md`
- Create: `Obsidian/Projects/AI_Training_Tests.md`
- Create: `Obsidian/Projects/Codex_Obsidian_Best_Practices.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Architecture/Repo Architecture.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Datasets/Dataset Progress.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Datasets/Training Data Style Guide.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Datasets/Approved Examples.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Sources/Buddhist Sources.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Sources/Occult Sources.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- Create one parser note per active parser:
  - `parse_asclepius.md`
  - `parse_blue_cliff_record.md`
  - `parse_dhammapada_commentary.md`
  - `parse_diamond_sutra.md`
  - `parse_gateless_gate.md`
  - `parse_itivuttaka.md`
  - `parse_majjhima_nikaya.md`
  - `parse_sutta_nipata.md`
  - `parse_udana.md`
  - `parse_vimalakirti.md`
  - `parse_zen_koans_database.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/New Parser Review Pipeline.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/Agents/parser-writer.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/Agents/sample-reviewer.md`

### Parser Note Template

Each parser note should use the existing parser vault design:

```md
# parse_udana.py

## Parser

- Code: `scripts/extraction/parse_udana.py`
- Source: `source_texts/buddhist/clean/udana.txt`
- Outputs: `review_outputs/new_buddhist_sources/udana_exclamation_dialogue.jsonl`

## Status

Approved

## Source And Outputs

Short summary of source shape and current outputs.

## Extraction Strategy

Short summary of how turns or teaching blocks are found.

## Durable Patterns That Worked

- Concrete repeatable parser techniques.

## Durable Patterns That Failed

- Concrete extraction failure modes to avoid.

## Current Review Snapshot

Date-aware status summary with links to review artifacts.

## Evidence

- `path/to/file`: one-line significance.

## Related Parsers

- [[parse_sutta_nipata]]: Shares verse and teaching-block output shape.

## Open Questions

- One or two unresolved parser-specific questions.

## Next Likely Improvements

- One or two narrow improvements.
```

### Approved Examples Note

`Approved Examples.md` should include:

- record ID
- source
- family
- parser
- short reason it is a good style example
- short excerpt or one compact complete record only when needed
- link to full JSONL or review packet

Avoid copying large source passages into Obsidian. Link to `review_outputs/` for the full record.

---

## Two-Agent Parser Review Pipeline

### Goal

Create a repeatable workflow for new source parsers:

1. `parser-writer` drafts or updates the parser using existing parser notes and parser code as reference.
2. Parser output is generated.
3. A fresh random 10-row sample is extracted.
4. `sample-reviewer` checks only the requested criteria and returns issues only.
5. `parser-writer` fixes those issues.
6. Repeat with a new random sample until no issues are found.

### Reviewer Criteria

The reviewer must not introduce stricter rules beyond these:

- Is the sample a complete enough conversation or teaching exchange with relevant context?
- Is it good training data for the current `conversation so far -> next reply` format?
- Are source artifacts, OCR debris, footnote bleed, headers, or malformed fragments still present?
- Is the row in the correct three-message chat format?
- Does the user prompt use `Participant A` / `Participant B` consistently?
- Does the assistant target match the requested participant or speaker?

Output rule:

- If issues are found, return issues only.
- If no issues are found, return exactly: `No sample issues found.`

### Pipeline Files

- Create: `tools/review_pipeline/random_sample.py`
- Create: `tools/review_pipeline/render_review_packet.py`
- Create: `tools/review_pipeline/run_new_parser_pass.py`
- Create: `tests/test_review_pipeline_random_sample.py`
- Create: `tests/test_review_pipeline_packet.py`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/New Parser Review Pipeline.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/Agents/parser-writer.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/Agents/sample-reviewer.md`

### Review Run Output Shape

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
  set_02/
    ...
```

### Agent Prompt Files

`parser-writer.md` should say:

- read `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- read related parser notes
- inspect the source text and closest parser code
- create or update one parser
- preserve the project chat row format
- run the parser and schema tests
- wait for sample-reviewer issues before another edit pass

`sample-reviewer.md` should say:

- inspect only the current 10-row random sample
- use only the listed criteria
- do not reject rows for mild thinness if they are coherent and correctly formatted
- return issues only, grouped by record ID
- return `No sample issues found.` if clean

### Sampling Rules

- Default sample size: 10 rows.
- Each pass uses a fresh random seed.
- The sample manifest records seed, source file, row count, selected record IDs, and timestamp.
- If output has fewer than 10 rows, sample the full output and mark the run as `small population`.
- A clean sample does not automatically mean final approval; it means the parser passed the requested sample review gate.

---

## Implementation Tasks

### Session Checkpoint: 2026-05-25

Completed in the first implementation session:

- Task 1 completed and verified with the planned `rg` inventory reference check.
- Task 2 completed with `config/dataset_manifest.json` and passing manifest tests.
- Task 3 completed with the live JSONL dashboard data generator and passing generator tests.
- Task 4 completed with generated live dashboard data plus a static dashboard shell, UI rendering, and headless browser screenshot/rendered-DOM smoke checks.

Second implementation session completed Task 5: Populate Obsidian Entrypoints.
Second implementation session completed Task 6: Populate Parser Vault.
Second implementation session completed Task 7: Add Dataset Style And Approved Examples Notes.
Second implementation session completed Task 8: Create Review Pipeline Tools.
Task 9 completed with parser-writer, sample-reviewer, and pipeline overview notes.
Task 10 completed with the initial `src/ai_training_tests/` package spine,
compatibility wrappers, shared review/JSONL helpers, and the Asclepius parser
migration.
Task 11 completed by refreshing stale dataset counts and architecture references
in the top-level docs and full-dataset README.
Task 12 reached the cleanup approval gate: verification evidence is documented,
but no delete or move has been approved or performed.

Next session should start by deciding whether to approve any cleanup candidates
from `docs/cleanup/delete_candidates.md`.

Verification evidence captured in-session:

- `rg -n "1277|854|423|ai_training_tests.egg-info|full_dialogue_dataset.jsonl" docs\architecture\current_repo_inventory.md docs\cleanup\delete_candidates.md .gitignore`
- `.venv\Scripts\python -m pytest tests/test_dataset_manifest.py -q`
- `.venv\Scripts\python -m pytest tests/test_dashboard_progress_data.py -q`
- `py -3.13 tools\dashboard\build_progress_data.py`
- Headless Chromium rendered `dashboard/index.html` from disk and showed `854 / 1,200`, `423 / 1,200`, `1,277 / 2,400`, and grouped source tables.
- `rg -n "AI_Training_Tests|Parser Hub|Dataset Progress|Codex_Obsidian_Best_Practices" Obsidian`
- `Get-ChildItem -Recurse Obsidian\Projects\AI_Training_Tests\Parsers -File | Where-Object { $_.Length -gt 20000 }`
- `rg -n "record_id|review_outputs/full_dialogue_dataset|review_outputs/parser_reviews" Obsidian\Projects\AI_Training_Tests\Datasets`
- `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_review_pipeline_random_sample.py tests\test_review_pipeline_packet.py -q` (`3 passed`)
- `rg -n "Do not introduce stricter rules|No sample issues found|issues only|Participant A" Obsidian\Projects\AI_Training_Tests\Pipelines`
- `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_review_pipeline_random_sample.py tests\test_review_pipeline_packet.py -q` (`3 passed`, run outside sandbox after sandboxed venv import failed)
- `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests -q` (`17 passed`, run outside sandbox after sandboxed venv import failed)
- `.venv\Scripts\python -m ruff check src tests\test_package_architecture.py scripts\extraction\dialogue_schema.py scripts\extraction\dialogue_source_manifest.py scripts\extraction\review_policy.py scripts\extraction\parse_asclepius.py` (`All checks passed!`, run outside sandbox after sandboxed venv execution failed)
- `.venv\Scripts\python scripts\extraction\parse_asclepius.py --output-dir <temp> --dataset-name asclepius_smoke --sample-count 2` (`72` turns parsed, `25` rows written)
- `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" scripts\extraction\test_review_policy.py scripts\extraction\test_dialogue_source_expansion.py -q` (`19 passed`, run outside sandbox after sandboxed venv import failed)
- `rg -n "862|779|464|398" README.md CODE_EXPLAINED.md project_intake_document.md project_memory.md review_outputs\full_dialogue_dataset\README.md` (no stale-count matches)
- `Get-FileHash` confirmed duplicate SHA256 hashes for `full_dialogue_dataset.jsonl` vs `full_combined_dialogue_dataset.jsonl`, `zen_koans_database_dialogue.jsonl` vs `zen_koans_database_clean_dialogue.jsonl`, and `dual_model_demo_*.jsonl` vs cleaned dialogue outputs.
- Full planned Ruff command is not clean yet because of pre-existing legacy lint outside the migration scope; focused Ruff on new/touched package files passes.

### Task 1: Create Architecture Inventory And Cleanup Proposal

**Files:**
- Create: `docs/architecture/current_repo_inventory.md`
- Create: `docs/cleanup/delete_candidates.md`
- Modify: `.gitignore`

- [x] **Step 1: Write the repo inventory document**

Record current top-level folders, final dataset counts, stale docs, and current script families.

- [x] **Step 2: Write deletion candidates**

Create a table with candidate path, reason, required verification, and approval status.

- [x] **Step 3: Update ignore rules for generated/local state**

Add ignore entries for generated package metadata and local state:

```gitignore
*.egg-info/
.codegraph/codegraph.db
Obsidian/.obsidian/workspace.json
```

- [x] **Step 4: Verify inventory references**

Run:

```powershell
rg -n "1277|854|423|ai_training_tests.egg-info|full_dialogue_dataset.jsonl" docs\architecture\current_repo_inventory.md docs\cleanup\delete_candidates.md .gitignore
```

Expected: matches in inventory, cleanup proposal, and `.gitignore`.

### Task 2: Add Dataset Manifest

**Files:**
- Create: `config/dataset_manifest.json`
- Test: `tests/test_dataset_manifest.py`

- [x] **Step 1: Add manifest test**

Test that Buddhist and occult final dataset paths exist and targets are 1200 each.

- [x] **Step 2: Create manifest**

Include current final files, source group labels, parser paths, and vault note paths.

- [x] **Step 3: Run manifest test**

Run:

```powershell
python -m pytest tests/test_dataset_manifest.py -q
```

Expected: PASS.

### Task 3: Build Dashboard Data Generator

**Files:**
- Create: `tools/dashboard/build_progress_data.py`
- Create: `tests/test_dashboard_progress_data.py`
- Modify: `pyproject.toml`

- [x] **Step 1: Write tests for JSONL counting**

Test that the generator counts JSONL lines and groups them by family from `config/dataset_manifest.json`.

- [x] **Step 2: Implement generator**

Read the manifest, count rows from final JSONL files, parse per-source counts from row metadata, and write `dashboard/project-progress-data.js`.

- [x] **Step 3: Run generator tests**

Run:

```powershell
python -m pytest tests/test_dashboard_progress_data.py -q
```

Expected: PASS.

### Task 4: Build Static Progress Dashboard

**Files:**
- Create: `dashboard/index.html`
- Create: `dashboard/styles.css`
- Create: `dashboard/app.js`
- Generate: `dashboard/project-progress-data.js`

- [x] **Step 1: Generate current dashboard data**

Run:

```powershell
python tools/dashboard/build_progress_data.py
```

Expected: `dashboard/project-progress-data.js` exists and contains `window.PROJECT_PROGRESS`.

- [x] **Step 2: Create static HTML shell**

Use script tags for `project-progress-data.js` and `app.js` so the dashboard can open directly from disk.

- [x] **Step 3: Implement UI rendering**

Render summary cards, progress bars, grouped source tables, and "what's next" cards from `window.PROJECT_PROGRESS`.

- [x] **Step 4: Smoke test in browser**

Open `dashboard/index.html` and verify that Buddhist shows `854 / 1200`, occult shows `423 / 1200`, and the source tables render.

### Task 5: Populate Obsidian Entrypoints

**Files:**
- Create: `Obsidian/00_Index.md`
- Create: `Obsidian/Hermes_Memory_Protocol.md`
- Create: `Obsidian/Projects/AI_Training_Tests.md`
- Create: `Obsidian/Projects/Codex_Obsidian_Best_Practices.md`
- Delete after migration: `Obsidian/Welcome.md`

- [x] **Step 1: Create index and protocol notes**

Use concise vault rules from `AGENTS.md`: summarize, link, avoid copying large artifacts, update durable notes only.

- [x] **Step 2: Create project note**

Link to architecture, datasets, parsers, sources, and pipeline notes.

- [x] **Step 3: Remove the default welcome note**

Delete `Obsidian/Welcome.md` only after the new index exists.

- [x] **Step 4: Verify vault entrypoints**

Run:

```powershell
rg -n "AI_Training_Tests|Parser Hub|Dataset Progress|Codex_Obsidian_Best_Practices" Obsidian
```

Expected: matches in the new Obsidian notes.

### Task 6: Populate Parser Vault

**Files:**
- Create: `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- Create: parser notes listed in the vault population plan.

- [x] **Step 1: Create parser hub**

Group parsers by status: final, candidate, in review, blocked, unknown.

- [x] **Step 2: Create parser notes from code and review artifacts**

For each `scripts/extraction/parse_*.py`, write source, outputs, strategy, durable patterns, failures, evidence, related parsers, and next improvements.

- [x] **Step 3: Link related parser notes**

Use Obsidian wikilinks and one reason per relationship.

- [x] **Step 4: Verify no large artifacts were copied**

Run:

```powershell
Get-ChildItem -Recurse Obsidian\Projects\AI_Training_Tests\Parsers -File | Where-Object { $_.Length -gt 20000 }
```

Expected: no parser note over 20 KB.

### Task 7: Add Dataset Style And Approved Examples Notes

**Files:**
- Create: `Obsidian/Projects/AI_Training_Tests/Datasets/Dataset Progress.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Datasets/Training Data Style Guide.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Datasets/Approved Examples.md`

- [x] **Step 1: Create dataset progress note**

Mirror dashboard totals and link to the generated dashboard.

- [x] **Step 2: Create style guide**

Document the current three-message chat format, `conversation so far -> next reply`, and participant A/B conventions.

- [x] **Step 3: Add approved examples**

Add compact examples with record IDs and links to full JSONL rows or review samples. Keep copied text short and representative.

- [x] **Step 4: Verify examples link to real artifacts**

Run:

```powershell
rg -n "record_id|review_outputs/full_dialogue_dataset|review_outputs/parser_reviews" Obsidian\Projects\AI_Training_Tests\Datasets
```

Expected: approved examples include record IDs and artifact paths.

### Task 8: Create Review Pipeline Tools

**Files:**
- Create: `tools/review_pipeline/random_sample.py`
- Create: `tools/review_pipeline/render_review_packet.py`
- Create: `tools/review_pipeline/run_new_parser_pass.py`
- Create: `tests/test_review_pipeline_random_sample.py`
- Create: `tests/test_review_pipeline_packet.py`

- [x] **Step 1: Test random sample determinism**

Test that a fixed seed selects stable record IDs and a new seed can select a different sample.

- [x] **Step 2: Implement random sampling**

Read JSONL, choose 10 rows or full population if fewer than 10, write set JSONL and manifest.

- [x] **Step 3: Test review packet format**

Test that packets include record ID, source, prompt, assistant target, and reviewer criteria.

- [x] **Step 4: Implement review packet renderer**

Render a concise Markdown review packet from the sampled JSONL.

- [x] **Step 5: Implement parser pass runner**

Run a parser command, sample output, render a review packet, and write a run summary.

- [x] **Step 6: Run review pipeline tests**

Run:

```powershell
python -m pytest tests/test_review_pipeline_random_sample.py tests/test_review_pipeline_packet.py -q
```

Expected: PASS.

### Task 9: Create Parser Writer And Sample Reviewer Agent Notes

**Files:**
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/New Parser Review Pipeline.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/Agents/parser-writer.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Pipelines/Agents/sample-reviewer.md`

- [x] **Step 1: Write parser-writer instructions**

Define scope, inputs, expected edits, and handoff format.

- [x] **Step 2: Write sample-reviewer instructions**

Define the exact reviewer criteria and issues-only response format.

- [x] **Step 3: Write pipeline overview**

Document the alternating parser-writer and sample-reviewer loop, fresh random sampling per pass, and stopping condition.

- [x] **Step 4: Verify reviewer strictness guard**

Run:

```powershell
rg -n "Do not introduce stricter rules|No sample issues found|issues only|Participant A" Obsidian\Projects\AI_Training_Tests\Pipelines
```

Expected: matches in agent notes and pipeline overview.

### Task 10: Move Toward Package Architecture

**Files:**
- Create package files under `src/ai_training_tests/`
- Modify: `pyproject.toml`
- Modify: wrapper scripts under `scripts/`
- Test: existing tests plus parser smoke tests.

- [x] **Step 1: Move shared schema and manifest modules first**

Move `scripts/extraction/dialogue_schema.py` and `scripts/extraction/dialogue_source_manifest.py` into `src/ai_training_tests/domain/`.

- [x] **Step 2: Add compatibility wrappers**

Keep old imports working from `scripts/extraction/` while tests and scripts migrate.

- [x] **Step 3: Move review policy and JSONL helpers**

Move shared review and IO code before moving parser files.

- [x] **Step 4: Move parser modules one family at a time**

Start with one smaller parser, such as `parse_asclepius.py`, before larger parsers like `parse_udana.py`.

- [x] **Step 5: Verify after each move**

Run:

```powershell
python -m pytest tests -q
python -m ruff check src scripts tests
```

Expected: PASS after each migration batch.

### Task 11: Refresh Stale Docs

**Files:**
- Modify: `README.md`
- Modify: `CODE_EXPLAINED.md`
- Modify: `project_intake_document.md`
- Modify: `project_memory.md`
- Modify: `review_outputs/full_dialogue_dataset/README.md`

- [x] **Step 1: Replace stale counts**

Use live dashboard generator output as source of truth.

- [x] **Step 2: Update architecture descriptions**

Describe the new package, dashboard, vault, and review pipeline locations.

- [x] **Step 3: Verify stale count removal**

Run:

```powershell
rg -n "862|779|464|398" README.md CODE_EXPLAINED.md project_intake_document.md project_memory.md review_outputs\full_dialogue_dataset\README.md
```

Expected: no stale old-count references unless explicitly marked historical.

### Task 12: Cleanup Execution Gate

**Files:**
- Modify: `docs/cleanup/delete_candidates.md`
- Possible deletions only after approval.

- [x] **Step 1: Present cleanup candidates to user**

List each candidate with verification evidence.

- [ ] **Step 2: Wait for explicit approval**

Do not delete or move files until the user approves specific paths.

- [ ] **Step 3: Apply approved cleanup only**

Use `git rm` or `git mv` for tracked files and update docs/scripts in the same commit.

- [ ] **Step 4: Verify no broken references**

Run:

```powershell
python -m pytest tests -q
rg -n "oritiginal text|Training Data|full_dialogue_dataset.jsonl|zen_koans_database_dialogue.jsonl" README.md CODE_EXPLAINED.md project_memory.md scripts docs Obsidian
```

Expected: references are either intentionally preserved compatibility notes or migrated paths.

---

## Review Gates

1. User reviews this plan.
2. Implementation begins with inventory, manifest, and dashboard generator.
3. Dashboard must show live current counts before file migration.
4. Obsidian notes must link to real files and avoid large copied artifacts.
5. Parser review pipeline must produce fresh random samples each pass.
6. Deletions and path migrations require explicit approval after evidence is collected.

## Known Risks

- Moving source folders before wrapper scripts exist will break parsers.
- Copying too many output examples into Obsidian will make the vault noisy.
- Dashboard data can become stale unless generated from JSONL files.
- Reviewer agents can become too strict unless the prompt explicitly limits the review criteria.
- Existing docs disagree on counts, so live JSONL counts should be treated as the source of truth.

## Success Criteria

- The repo has a clear target architecture and current inventory.
- The dashboard opens locally and shows Buddhist and occult progress toward 1200 lines each.
- Obsidian has a useful index, project map, parser hub, source notes, dataset style guide, and approved examples.
- The parser review pipeline can run parser draft -> random 10-row sample -> sample review -> parser fix loop.
- Cleanup candidates are documented with verification evidence before any deletion.
