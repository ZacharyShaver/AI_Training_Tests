# Buddhist Sources

## Status

active

## Summary

The Buddhist final dataset currently has 854 rows toward a 1,200-row target.
Rows are tracked through `config/dataset_manifest.json` and generated dashboard
data.

## Final Coverage

| Source | Rows | Parser note |
| --- | ---: | --- |
| Itivuttaka | 107 | [[../Parsers/parse_itivuttaka]] |
| Majjhima Nikaya | 168 | [[../Parsers/parse_majjhima_nikaya]] |
| Milinda Panha | 73 | [[../Parsers/base_dialogue_dataset]] |
| Platform Sutra | 19 | [[../Parsers/base_dialogue_dataset]] |
| Sutta Nipata | 80 | [[../Parsers/parse_sutta_nipata]] |
| The Diamond Sutra | 83 | [[../Parsers/parse_diamond_sutra]] |
| The Gateless Gate | 129 | [[../Parsers/parse_gateless_gate]] |
| Udana | 80 | [[../Parsers/parse_udana]] |
| Vimalakirti Nirdesa Sutra | 17 | [[../Parsers/parse_vimalakirti]] |
| Zen Koans Database | 98 | [[../Parsers/parse_zen_koans_database]] |

## Candidate Sources

- Blue Cliff Record: candidate outputs exist and need parser/sample review.
- Dhammapada Commentary: candidate review sample exists.
- Udana direct dialogue rows: separate from the final exclamation-row output.
- Additional Majjhima Nikaya pass: possible if the 190-row candidate is promoted.

## Evidence

- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`
- `dashboard/project-progress-data.js`
- `config/dataset_manifest.json`

## Links

- [[../Datasets/Dataset Progress]]
- [[../Parsers/Parser Hub]]
- [[../Pipelines/New Parser Review Pipeline]]
