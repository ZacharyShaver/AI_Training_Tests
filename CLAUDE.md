# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This repo extracts dialogue training data from Buddhist and esoteric/occult source texts. Each row becomes a three-message chat record: a system instruction, a user prompt showing "Conversation so far" with `Participant A / Participant B` labels, and an assistant message with the next source-grounded reply. The output is JSONL datasets used for LLM fine-tuning.

## Commands

### Environment setup

```powershell
python -m pip install ".[dev]"
pre-commit install
```

### Lint

```powershell
python -m ruff check src/ scripts/ tests/ tools/
python -m ruff format src/ scripts/ tests/ tools/
```

### Tests

```powershell
python -m pytest                      # all tests
python -m pytest tests/test_dialogue_schema.py -q   # single file
```

### Run a parser

```powershell
python src/ai_training_tests/extraction/parsers/milinda_panha.py
python scripts/extraction/parse_vimalakirti.py
```

Most parsers accept `--source`, `--output-dir`, `--max-history-turns`, `--min-target-words`, `--max-target-words`, and `--sample-count`. Run with `--help` for full options.

### Parser review pass (new pipeline)

```powershell
python tools/review_pipeline/run_new_parser_pass.py \
  --source-jsonl review_outputs/new_buddhist_sources/<dataset>.jsonl \
  --output-dir review_outputs/parser_reviews/<parser_name>/set_NN \
  --dataset-stem <dataset>_set_NN \
  --sample-size 10
```

Creates `sample_manifest.md`, `run_summary.md`, and a `*_random_review.md` packet under the set directory.

### Regenerate dashboard data

```powershell
python tools/dashboard/build_progress_data.py
```

Run after promoting any candidate rows to a final dataset. The static dashboard is at `dashboard/index.html`.

## Architecture

The repo is in an **incremental migration** from script-only code to a package-backed architecture.

### Package (`src/ai_training_tests/`)

| Module | Purpose |
|---|---|
| `domain/dialogue_schema.py` | Pydantic models: `DialogueRow`, `DialogueMetadata`, `DialogueMessage`. Enforces three-message format, role order, and `target_words` word-count match. |
| `domain/source_manifest.py` | `SourceBuildSpec` dataclass + `APPROVED_SOURCE_SPECS` tuple listing every approved source with its parser script and output group. |
| `extraction/common/text_cleaning.py` | `normalize_text`, `clean_dataset_text`, `count_dataset_words`, `make_record_id`. The canonical text pipeline for all parsers. |
| `extraction/common/jsonl_io.py` | `read_jsonl` / `write_jsonl` helpers. |
| `extraction/common/review_samples.py` | `SYSTEM_PROMPTS` dict, `build_messages`, `select_spread`. |
| `extraction/review/review_policy.py` | `assess_row`, `auto_hard_failures`, `auto_warnings` — automated quality checks for every row. |
| `extraction/parsers/milinda_panha.py` | Migrated parser (canonical pattern for new parsers). |
| `extraction/parsers/asclepius.py` | First migrated parser (esoteric). |

### Scripts (`scripts/extraction/`)

Compatibility entrypoints and legacy parsers that have not yet migrated into the package. The older `dialogue_schema.py` still lives here and is imported by `tests/test_dialogue_schema.py` until migration is complete.

### Tools (`tools/`)

- `review_pipeline/run_new_parser_pass.py` — orchestrates a single review pass: runs the parser, samples output, writes the review packet.
- `review_pipeline/random_sample.py` — seeded random sampling with manifest.
- `review_pipeline/render_review_packet.py` — formats sampled rows as Markdown for human review.
- `source_ingest/fetch_milinda_suttacentral.py` — fetches/cleans the SuttaCentral Milinda Panha source.
- `dashboard/build_progress_data.py` — regenerates `dashboard/project-progress-data.js` from live JSONL counts.

### Key paths

| Path | Role |
|---|---|
| `source_texts/` | Cleaned source texts (input to parsers). |
| `oritiginal text/` | Legacy raw source files (still referenced by `build_pilot_dialogue_dataset.py`). |
| `review_outputs/new_buddhist_sources/` | Candidate parser JSONL outputs. |
| `review_outputs/full_dialogue_dataset/` | Final promoted datasets. |
| `review_outputs/parser_reviews/<parser>/` | Per-parser review pass sets. |
| `config/dataset_manifest.json` | Source of truth for dashboard and dataset metadata. |
| `Obsidian/Projects/AI_Training_Tests/` | Human-readable project memory; read before making architectural decisions. |

## Parser Pattern

Every parser follows this structure (read in this order):

1. `DEFAULT_SOURCE` / `DEFAULT_OUTPUT_DIR` constants at the top.
2. Small dataclasses (`Line`, `Turn`, `Item`, …).
3. `clean_*` / `normalize_*` functions.
4. `parse_*` or `iter_*` functions that convert source text into turns/items.
5. `build_rows` that converts turns into three-message chat dicts.
6. `main()` that wires args, calls the above, and writes JSONL + Markdown review.

Parsers in `src/ai_training_tests/extraction/parsers/` are the migrated canonical form. Parsers still in `scripts/extraction/` are compatible legacy code.

## Row Format and Validation

Every output row must pass `DialogueRow.model_validate(row)`:

- Exactly three messages in `system → user → assistant` order.
- `user` content: `"Conversation so far:\n<turns>\n\nWrite Participant B's next reply."`
- Turns use `Participant A (Source Speaker): ...` format.
- `metadata.target_words` must equal the exact word count of the assistant text.
- `metadata.target_participant` must be `"Participant B"`.

`review_policy.py` defines additional automated checks: contamination markers, fragmentary targets, broken participant mapping, and scene-looseness warnings.

## Parser Promotion Rules

Do not promote candidate JSONL to the final datasets without:

1. Three consecutive clean random-sample review passes (default 10 rows each, fresh seed per pass).
2. Updating `config/dataset_manifest.json`.
3. Updating `dashboard/project-progress-data.js` (`python tools/dashboard/build_progress_data.py`).
4. Updating the relevant parser note under `Obsidian/Projects/AI_Training_Tests/Parsers/`.

A clean sample is not approval. Collapsed candidate pools (parser produces far fewer rows than expected after a change) are treated as failures.

## Obsidian Vault

`Obsidian/Projects/AI_Training_Tests/` is the authoritative project memory. Key notes:

- `Architecture/Repo Architecture.md` — current migration state and constraints.
- `Parsers/Parser Hub.md` — parser status table, review rules, next planned candidate.
- `Parsers/Parser Pseudocode Guide.md` — plain-language parser family overview.
- `Datasets/Training Data Style Guide.md` — row shape contract and review guardrails.
- `Datasets/Dataset Progress.md` — live totals and final output paths.
- `Pipelines/New Parser Review Pipeline.md` — step-by-step review loop.

## Constraints

- Do not delete or move `review_outputs/`, `source_texts/`, `Training Data/`, or `oritiginal text/` without explicit approval.
- Keep old `scripts/extraction/` paths working while the package migration is ongoing.
- Generated data paths referenced in `config/dataset_manifest.json` must not be renamed without updating the manifest.
