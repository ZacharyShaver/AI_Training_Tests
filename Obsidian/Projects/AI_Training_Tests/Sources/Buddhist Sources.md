# Buddhist Sources

## Status

active

## Summary

The Buddhist final dataset has **1,206 rows** — exceeds the 1,200-row target.
Rows are tracked through `config/dataset_manifest.json` and generated dashboard
data.

## Final Coverage

| Source | Rows | Parser note |
| --- | ---: | --- |
| Bilara Pali Canon (DN + SN Sagāthāvagga) | 352 | [[../Parsers/parse_bilara_pali_dialogue]] |
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

- Selected Digha Nikaya dialogues (SuttaCentral): next recommended Buddhist
  source. Start with `DN 2`, `DN 13`, `DN 21`, and `DN 23` as a bounded
  long-discourse pilot; execution plan saved at
  `docs/superpowers/plans/2026-05-30-digha-nikaya-selected-suttacentral-dialogues.md`.
- Blue Cliff Record: candidate outputs exist and need parser/sample review.
- Dhammapada Commentary: candidate review sample exists.
- Milinda Panha (SuttaCentral export): parked after the second refresh reduced
  the candidate pool to `14` stronger rows; the legacy builder still supplies
  the live final Milinda rows and no further Milinda expansion is planned right
  now.
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
