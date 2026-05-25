# Current Repo Inventory

Updated: 2026-05-25

This inventory records the current repository shape before package migration, data
layout migration, or cleanup. Counts below are live JSONL line counts from the
current final dataset files, not stale README counts.

## Top-Level Folders

| Path | Current role | Notes |
| --- | --- | --- |
| `.claude/` | Tool-specific local guidance | Untracked local state. Preserve unless the user explicitly approves a cleanup action. |
| `.codegraph/` | CodeGraph index state | `.codegraph/codegraph.db` is generated local state and should stay ignored. |
| `.github/` | GitHub Actions workflows | Contains Python quality workflow configuration. |
| `.vscode/` | Editor settings | Local/editor project settings. |
| `ai_training_tests.egg-info/` | Generated package metadata | Tracked generated output candidate; document before any untracking. |
| `docs/` | Specs, Superpowers plans, architecture and cleanup docs | This inventory and cleanup proposal live here. |
| `Obsidian/` | Human-readable project memory vault | Currently has default Obsidian state and `Welcome.md`; planned entrypoints do not exist yet. |
| `oritiginal text/` | Legacy original source texts | Misspelled legacy path still referenced by scripts. Do not move until compatibility paths are in place. |
| `review_outputs/` | Generated datasets, samples, parser reviews | Current final JSONL outputs live here. |
| `scripts/` | Current executable Python scripts | Existing entrypoints remain active during migration. |
| `source_texts/` | Newer Buddhist source storage | Contains raw and clean Buddhist source files. |
| `tests/` | Pytest suite | Current baseline has `tests/test_dialogue_schema.py`. |
| `Training Data/` | Legacy transcript and chat training artifacts | Space in path; candidate for later legacy data migration after reference checks. |

## Current Final Dataset Counts

| Dataset | Path | Live lines | Target lines | Progress |
| --- | --- | ---: | ---: | ---: |
| Buddhist final dataset | `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl` | 854 | 1200 | 71.2% |
| Occult / esoteric final dataset | `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl` | 423 | 1200 | 35.3% |
| Combined final dataset | `review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset.jsonl` | 1277 | 2400 | 53.2% |

Compatibility note: `review_outputs/full_dialogue_dataset/full_dialogue_dataset.jsonl`
also exists and appears to be an older compatibility or duplicate combined output.
It is a cleanup candidate only after hash and reference checks.

## Current Script Families

| Family | Current files | Role |
| --- | --- | --- |
| Extraction parsers | `scripts/extraction/parse_*.py`, `platform_sutra_dialogue.py` | Source-specific JSONL generation. |
| Extraction pipeline | `build_full_dialogue_outputs.py`, `combine_dialogue_datasets.py`, `split_dialogue_dataset.py`, `validate_dialogue_dataset.py` | Build, combine, split, and validate dialogue outputs. |
| Extraction review helpers | `make_review_sample.py`, `preview_dialogue_examples.py`, `review_policy.py`, `test_review_policy.py` | Sampling, preview, and review policy support. |
| Extraction domain helpers | `dialogue_schema.py`, `dialogue_source_manifest.py` | Current shared schema and source manifest modules. |
| Data prep | `scripts/data_prep/*.py` | Legacy/local chat transcript conversion and MLX/Alpaca prep. |
| Apps | `scripts/apps/streamlit_lmstudio_dual_chat.py` | Local Streamlit dual-chat app. |

## Current Final Source Coverage

The current final source coverage reported by
`review_outputs/full_dialogue_dataset/full_dialogue_dataset_splits.md` is:

### Buddhist

| Source | Rows |
| --- | ---: |
| Itivuttaka | 107 |
| Majjhima Nikaya | 168 in the split report; current candidate output has 190 rows |
| Milinda Panha | 73 |
| Platform Sutra | 19 |
| Sutta Nipata | 80 |
| The Diamond Sutra | 83 |
| The Gateless Gate | 129 |
| Udana | 80 |
| Vimalakirti Nirdesa Sutra | 17 |
| Zen Koans Database | 98 |

### Occult / Esoteric

| Source | Rows |
| --- | ---: |
| Asclepius | 25 |
| The Corpus Hermeticum | 28 |
| The Key to Theosophy | 370 |

## Stale Documentation Found

These files still reference older counts such as 862 combined rows, 464 Buddhist
rows, or 398 esoteric rows and should be refreshed from live JSONL/dashboard data:

- `README.md`
- `CODE_EXPLAINED.md`
- `project_intake_document.md`
- `project_memory.md`
- `review_outputs/full_dialogue_dataset/README.md`

`review_outputs/full_dialogue_dataset/full_dialogue_dataset_splits.md` is closer
to current state and reports 1277 combined rows, 854 Buddhist rows, and 423
esoteric rows.

## Current Constraints

- Do not delete or move files without explicit user approval.
- Keep dashboard data generated from live JSONL counts.
- Keep `Obsidian/` as the project memory vault.
- Preserve existing `review_outputs/`, `source_texts/`, `Training Data/`, and
  `oritiginal text/` paths until compatibility wrappers and reference updates
  are in place.
