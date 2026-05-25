# Repo Architecture

## Status

active

## Summary

The repository is in an incremental migration from script-only extraction code to
a package-backed architecture. Existing `scripts/extraction/` entrypoints remain
available for compatibility while shared modules and migrated parsers move into
`src/ai_training_tests/`.

## Current Shape

- `src/ai_training_tests/domain/`: dialogue schema and source manifest.
- `src/ai_training_tests/extraction/common/`: JSONL, text-cleaning, and review
  sample helpers.
- `src/ai_training_tests/extraction/review/`: shared review policy.
- `src/ai_training_tests/extraction/parsers/asclepius.py`: first migrated parser.
- `scripts/extraction/`: compatibility wrappers plus legacy parser entrypoints.
- `config/dataset_manifest.json`: dashboard and dataset metadata source.
- `dashboard/`: static local progress dashboard generated from live JSONL counts.
- `Obsidian/`: human-readable project memory.

## Constraints

- Do not delete or move generated data paths without explicit approval.
- Preserve `review_outputs/`, `source_texts/`, `Training Data/`, and
  `oritiginal text/` until compatibility references are updated.
- Keep old script paths working while package modules are introduced.

## Evidence

- `docs/architecture/current_repo_inventory.md`: repo inventory and stale-doc map.
- `docs/cleanup/delete_candidates.md`: cleanup candidates and approval status.
- `src/ai_training_tests/`: current package spine.
- `tests/test_package_architecture.py`: package and compatibility wrapper checks.
- `dashboard/project-progress-data.js`: live generated counts.

## Links

- [[../Datasets/Dataset Progress]]: current totals and targets.
- [[../Parsers/Parser Hub]]: parser status map.
- [[../Pipelines/New Parser Review Pipeline]]: parser review loop.

## Open Questions

- Whether to complete the parser migration family-by-family before moving any
  data directories.
- Which cleanup candidates should be approved after hash/reference evidence is
  reviewed.
