# Approved Examples

## Status

active

## Purpose

Use these as compact pointers to good current training rows. Keep full row text
in JSONL artifacts and review packets; this note records `record_id`, source,
family, parser, and why the row is a useful style reference.

## Examples

| record_id | Source | Family | Parser | Why it is useful | Artifact |
| --- | --- | --- | --- | --- | --- |
| `milinda-panha-txt:quoted_buddhist_next_reply_1:1618-1633:venerable-nagasena` | Milinda Panha | Buddhist | [[Projects/AI_Training_Tests/Parsers/base_dialogue_dataset]] | Clean named-speaker exchange with a direct next reply target. | `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl` |
| `the-key-to-theosophy-txt:explicit_next_reply:104-107:theosophist` | The Key to Theosophy | Occult / esoteric | [[Projects/AI_Training_Tests/Parsers/base_dialogue_dataset]] | Strong catechism-style source with explicit speaker prefixes. | `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl` |
| `mn5-html:majjhima_nikaya_next_reply_5_4:207-248:ven-moggall-na` | Majjhima Nikaya | Buddhist | [[Projects/AI_Training_Tests/Parsers/parse_majjhima_nikaya]] | Represents the approved parser redesign and local exchange-window approach. | `review_outputs/new_buddhist_sources/majjhima_nikaya_dialogue.jsonl` |
| `vimalakirti-nirdesa-sutra-txt:vimalakirti_next_reply:540-545:shariputra` | Vimalakirti Nirdesa Sutra | Buddhist | [[Projects/AI_Training_Tests/Parsers/parse_vimalakirti]] | Compact named-speaker sutra dialogue from a small approved pool. | `review_outputs/new_buddhist_sources/vimalakirti_dialogue.jsonl` |

## Compact Style Notes

- Milinda Panha rows are useful for source-grounded debate because the target is
  a named respondent and the prompt keeps the preceding turn visible.
- The Key to Theosophy rows are useful for clean explicit dialogue because the
  source already has stable questioner/respondent labels.
- Majjhima and Vimalakirti review packets are useful examples of the approval
  gate, not standalone proof that future parser edits are safe.

## Evidence Links

- `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`
- `review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset.jsonl`
- `review_outputs/parser_reviews/parse_majjhima_nikaya/pass_history.md`
- `review_outputs/parser_reviews/parse_vimalakirti/pass_history.md`
