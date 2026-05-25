# Dataset Progress

## Status

active

## Summary

Current progress is generated from live JSONL counts, not from stale README or
legacy project-memory counts.

## Live Totals

| Dataset | Current rows | Target rows | Progress |
| --- | ---: | ---: | ---: |
| Buddhist final dataset | 854 | 1,200 | 71.2% |
| Occult / esoteric final dataset | 423 | 1,200 | 35.3% |
| Combined final dataset | 1,277 | 2,400 | 53.2% |

## Current Final Outputs

- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`
- `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`
- `review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset.jsonl`

## Dashboard

- Static dashboard: `dashboard/index.html`
- Generated dashboard data: `dashboard/project-progress-data.js`
- Generator: `tools/dashboard/build_progress_data.py`
- Manifest: `config/dataset_manifest.json`

Regenerate dashboard data after any final dataset promotion:

```powershell
python tools/dashboard/build_progress_data.py
```

## Source Counts

Source counts are tracked in `dashboard/project-progress-data.js` and
`review_outputs/full_dialogue_dataset/full_dialogue_dataset_splits.md`.

Key current source counts:

- Buddhist: Itivuttaka 107, Majjhima Nikaya 168, Milinda Panha 73, Platform
  Sutra 19, Sutta Nipata 80, Diamond Sutra 83, Gateless Gate 129, Udana 80,
  Vimalakirti Nirdesa Sutra 17, Zen Koans Database 98.
- Occult / esoteric: Asclepius 25, Corpus Hermeticum 28, Key to Theosophy 370.

## Links

- [[Projects/AI_Training_Tests]]
- [[Projects/AI_Training_Tests/Datasets/Training Data Style Guide]]
- [[Projects/AI_Training_Tests/Datasets/Approved Examples]]
- [[Projects/AI_Training_Tests/Parsers/Parser Hub]]

## Open Questions

- Should the final Buddhist dataset be refreshed with the 190-row approved
  Majjhima candidate output?
- Which candidate source should move through the new review pipeline first:
  Blue Cliff Record, Dhammapada Commentary, Udana direct dialogue, or expanded
  Asclepius?

