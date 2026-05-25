# Occult Sources

## Status

active

## Summary

The occult / esoteric final dataset currently has 423 rows toward a 1,200-row
target. Current coverage is Hermetic and Theosophical, with Asclepius now present
in the final esoteric dataset.

## Final Coverage

| Source | Rows | Parser note |
| --- | ---: | --- |
| Asclepius | 25 | [[../Parsers/parse_asclepius]] |
| The Corpus Hermeticum | 28 | [[../Parsers/base_dialogue_dataset]] |
| The Key to Theosophy | 370 | [[../Parsers/base_dialogue_dataset]] |

## Candidate Sources

- Expanded Asclepius: current parser yields 25 final rows; additional clean
  dialogue may be extractable.
- Additional Hermetic texts: source and reuse status need verification before
  ingestion.
- Dialogue or catechism-style Theosophical texts: candidates should match the
  current `conversation so far -> next reply` format.

## Evidence

- `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`
- `review_outputs/new_esoteric_sources/asclepius_dialogue.jsonl`
- `dashboard/project-progress-data.js`
- `config/dataset_manifest.json`

## Links

- [[../Datasets/Dataset Progress]]
- [[../Parsers/Parser Hub]]
- [[../Pipelines/New Parser Review Pipeline]]
