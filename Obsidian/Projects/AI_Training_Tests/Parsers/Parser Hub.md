# Parser Hub

## Status

active

## Purpose

This hub maps the current parser surface for `AI_Training_Tests`. Use it before
editing parser code or promoting candidate source outputs into the final dataset.

Companion guide: [[Parser Pseudocode Guide]] explains the parser family in
plain-language pseudocode for easier onboarding.

## Final Parsers And Sources

| Parser note | Source | Current rows | Evidence |
| --- | --- | ---: | --- |
| [[parse_itivuttaka]] | Itivuttaka | 107 | `review_outputs/new_buddhist_sources/itivuttaka_dialogue.jsonl` |
| [[parse_majjhima_nikaya]] | Majjhima Nikaya | 168 final, 190 candidate | `review_outputs/parser_reviews/parse_majjhima_nikaya/status_marker.txt` |
| [[base_dialogue_dataset]] | Milinda Panha | 73 | `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl` |
| [[base_dialogue_dataset]] | Platform Sutra | 19 | `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl` |
| [[parse_sutta_nipata]] | Sutta Nipata | 80 | `review_outputs/new_buddhist_sources/sutta_nipata_dialogue.jsonl` |
| [[parse_diamond_sutra]] | The Diamond Sutra | 83 | `review_outputs/new_buddhist_sources/diamond_sutra_dialogue.jsonl` |
| [[parse_gateless_gate]] | The Gateless Gate | 129 | `review_outputs/new_buddhist_sources/gateless_gate_dialogue.jsonl` |
| [[parse_udana]] | Udana exclamation rows | 80 | `review_outputs/new_buddhist_sources/udana_exclamation_dialogue.jsonl` |
| [[parse_vimalakirti]] | Vimalakirti Nirdesa Sutra | 17 | `review_outputs/parser_reviews/parse_vimalakirti/status_marker.txt` |
| [[parse_zen_koans_database]] | Zen Koans Database | 98 | `review_outputs/new_buddhist_sources/zen_koans_database_clean_dialogue.jsonl` |
| [[parse_asclepius]] | Asclepius | 25 | `review_outputs/new_esoteric_sources/asclepius_dialogue.jsonl` |
| [[base_dialogue_dataset]] | The Corpus Hermeticum | 28 | `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl` |
| [[parse_corpus_hermeticum]] | Corpus Hermeticum (v2 standalone) | 44 | `review_outputs/new_esoteric_sources/corpus_hermeticum_v2_dialogue.jsonl` |
| [[base_dialogue_dataset]] | The Key to Theosophy | 370 | `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl` |
| [[parse_transactions_blavatsky_lodge]] | Transactions of the Blavatsky Lodge | 288 | `review_outputs/new_esoteric_sources/transactions_blavatsky_lodge_dialogue.jsonl` |
| [[parse_theosophy_explained_pavri]] | Theosophy Explained in Q&A (Pavri) | 97 | `review_outputs/new_esoteric_sources/theosophy_explained_pavri_dialogue.jsonl` |
| [[parse_plato_gorgias]] | Plato's Gorgias (Jowett) | 262 | `review_outputs/new_esoteric_sources/plato_gorgias_dialogue.jsonl` |
| [[parse_plato_philebus]] | Plato's Philebus (Jowett) | 283 | `review_outputs/new_esoteric_sources/plato_philebus_dialogue.jsonl` |

## Candidate Or In Review Parsers

| Parser note                     | Source                     |                                 Current rows | Status                                         |
| ------------------------------- | -------------------------- | -------------------------------------------: | ---------------------------------------------- |
| [[parse_bilara_pali_dialogue]]  | Bilara Pali Canon (DN + SN1-11) |                                      352 | **APPROVED** — 3 clean passes (set_09-11); 2026-05-31                 |
| [[parse_blue_cliff_record]]     | Blue Cliff Record          | 10 dialogue, 31 ode, 227 internal candidates | candidate                                      |
| [[parse_dhammapada_commentary]] | Dhammapada Commentary      |                                sample exists | candidate                                      |
| [[parse_milinda_panha]]         | Milinda Panha (SuttaCentral export) |                                    14 | parked after low-yield refresh; keep as non-final reference |
| [[parse_udana]]                 | Udana direct dialogue rows |                                           27 | candidate separate from final exclamation rows |

## Next Planned Candidate

- Occult target (1200 rows) REACHED: 1397 rows total as of 2026-05-31.
  Sources added this session: Transactions of the Blavatsky Lodge (288 rows),
  Corpus Hermeticum v2 (44 rows), Theosophy Explained Pavri (97 rows),
  Plato's Gorgias (262 rows), Plato's Philebus (283 rows).
- Bilara Pali Canon: **APPROVED 2026-05-31** — ready for promotion. 352 rows from
  DN (cleaned set, 11 complex suttas excluded) + SN1-11 (Sagāthāvagga). Ready to
  promote to `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`
  after updating manifest and dashboard.

## Review Rules

- A parser is not final merely because a sample is clean.
- The current machine-review approval pattern requires three consecutive clean
  random samples for parser approval.
- Do not reject coherent rows for mild thinness when they preserve source
  wording and the target reply follows the prompt context.
- Do not promote candidate outputs without updating `config/dataset_manifest.json`,
  `dashboard/project-progress-data.js`, and the relevant dataset notes.

## Evidence

- `config/dataset_manifest.json`: source, parser, final dataset, and vault note map.
- `dashboard/project-progress-data.js`: live final-row counts grouped by source.
- `review_outputs/parser_reviews/parse_majjhima_nikaya/pass_history.md`: example
  of failed collapsed-pool passes followed by machine approval.
- `review_outputs/parser_reviews/parse_vimalakirti/pass_history.md`: example of
  parser redesign and approval after three passing random sets.

## Open Questions

- Should `review_outputs/full_dialogue_dataset/full_dialogue_dataset.jsonl` remain
  as a compatibility output or be replaced after hash and reference checks?
- Should candidate Blue Cliff, Dhammapada Commentary, and Udana direct rows move
  through the new random-sample review pipeline before any final promotion?
