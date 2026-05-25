# `parse_vimalakirti.py` Set 04 Run Summary

- Parser: `scripts/extraction/parse_vimalakirti.py`
- Source: `source_texts/buddhist/clean/vimalakirti_nirdesa_sutra.txt`
- Output JSONL: `vimalakirti_dialogue_set_04.jsonl`
- Review packet: `vimalakirti_dialogue_set_04_random_review.md`
- Rows written: `17`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling seed: `20260526`
- Sampling mode: `random sample without replacement`
- Machine review status: `machine-pass-set-2`

## Parser Changes In This Pass

- Restricted leading-speaker extraction to name-like speaker tokens and added support for narrated speech verbs such as `asked`, `addressed`, and `spoke`.
- Rejected malformed narrative speaker labels with lowercase action fragments or embedded narration.
- Added paragraph-gap continuity checks so scene jumps no longer survive as adjacent-turn rows.
- Rejected one-turn reply rows unless the visible setup is a direct question.
- Dropped incomplete quote fragments that end mid-sentence, such as rows truncated at commas or semicolons.

## Current Interpretation

- This parser revision removed the concrete Set 02 failure modes and preserved a still-meaningful candidate pool.
- The sampled rows in this set passed machine review at 100 percent.