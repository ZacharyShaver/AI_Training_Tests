# Full Dialogue Dataset Outputs

This folder contains the current direct-source dialogue training pass. The rows
are extracted from source texts; they are not AI-regenerated.

## Training files

- `full_combined_dialogue_dataset_train.jsonl` / `full_combined_dialogue_dataset_eval.jsonl`
  - Combined set for one model trained across both esoteric and Buddhist voices.
- `full_esoteric_dialogue_dataset_train.jsonl` / `full_esoteric_dialogue_dataset_eval.jsonl`
  - Esoteric-only split.
- `full_buddhist_dialogue_dataset_train.jsonl` / `full_buddhist_dialogue_dataset_eval.jsonl`
  - Buddhist-only split.

Each row uses chat messages:

```json
{"messages":[{"role":"system","content":"..."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}],"metadata":{...}}
```

## Review files

- `full_dialogue_dataset_splits.md` gives counts by source, kind, and target speaker.
- `full_buddhist_dialogue_dataset_review_sample.md` is the current 10-row Buddhist review sample.
- `full_combined_dialogue_dataset_review_sample.md` is a 12-row mixed review sample.
- `full_dialogue_dataset_review.md` is the larger review output from the original source pass.

## Current counts

- Combined: 671 rows, 607 train, 64 eval.
- Esoteric: 398 rows, 359 train, 39 eval.
- Buddhist: 273 rows, 248 train, 25 eval.

## Rebuild command

From the repository root:

```bash
PYTHONPATH=scripts/extraction python3 scripts/extraction/build_full_dialogue_outputs.py
```

That command rebuilds the original-source dialogue rows, parses the added
Gateless Gate and Diamond Sutra sources, combines everything, regenerates
train/eval splits, and refreshes review samples.
