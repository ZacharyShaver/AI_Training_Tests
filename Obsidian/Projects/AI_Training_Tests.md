# AI_Training_Tests

`AI_Training_Tests` builds clean philosophical and spiritual training data from
source texts, with the current focus on direct-source dialogue records in the
`conversation so far -> next reply` format.

## Current Status

- Current live dashboard: `dashboard/index.html`
- Current manifest: `config/dataset_manifest.json`
- Buddhist final dataset: 854 / 1,200 rows
- Occult / esoteric final dataset: 423 / 1,200 rows
- Combined final dataset: 1,277 / 2,400 rows

The dashboard data is generated from live JSONL counts by
`tools/dashboard/build_progress_data.py`.

## Architecture

- Repo inventory: `docs/architecture/current_repo_inventory.md`
- Cleanup proposal: `docs/cleanup/delete_candidates.md`
- Architecture note: [[Projects/AI_Training_Tests/Architecture/Repo Architecture]]

Current constraints:

- Do not delete or move files without explicit user approval.
- Keep dashboard data generated from live JSONL counts.
- Preserve legacy `review_outputs/`, `source_texts/`, `Training Data/`, and
  `oritiginal text/` paths until compatibility wrappers and reference updates
  are in place.

## Datasets

- Dataset progress: [[Projects/AI_Training_Tests/Datasets/Dataset Progress]]
- Training data style guide: [[Projects/AI_Training_Tests/Datasets/Training Data Style Guide]]
- Approved examples: [[Projects/AI_Training_Tests/Datasets/Approved Examples]]
- Final outputs: `review_outputs/full_dialogue_dataset/`

Current final datasets:

- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`
- `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`
- `review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset.jsonl`

## Parsers

- Parser Hub: [[Projects/AI_Training_Tests/Parsers/Parser Hub]]
- Parser code: `scripts/extraction/`
- Parser review outputs: `review_outputs/parser_reviews/`

Active final parser/source coverage currently includes Itivuttaka, Majjhima
Nikaya, Milinda Panha, Platform Sutra, Sutta Nipata, The Diamond Sutra, The
Gateless Gate, Udana, Vimalakirti Nirdesa Sutra, Zen Koans Database, Asclepius,
The Corpus Hermeticum, and The Key to Theosophy.

## Sources

- Buddhist sources: [[Projects/AI_Training_Tests/Sources/Buddhist Sources]]
- Occult sources: [[Projects/AI_Training_Tests/Sources/Occult Sources]]
- Candidate next sources are tracked in `config/dataset_manifest.json`.

## Pipelines

- New parser review pipeline: [[Projects/AI_Training_Tests/Pipelines/New Parser Review Pipeline]]
- Parser writer agent note: [[Projects/AI_Training_Tests/Pipelines/Agents/parser-writer]]
- Sample reviewer agent note: [[Projects/AI_Training_Tests/Pipelines/Agents/sample-reviewer]]
- Implementation plan: `docs/superpowers/plans/2026-05-25-repo-architecture-dashboard-vault-review-pipeline.md`

## Related Vault Notes

- [[Hermes_Memory_Protocol]]
- [[Projects/Codex_Obsidian_Best_Practices]]
