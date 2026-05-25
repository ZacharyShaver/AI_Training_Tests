# `parse_vimalakirti.py` Set 02 Run Summary

- Parser: `scripts/extraction/parse_vimalakirti.py`
- Source: `source_texts/buddhist/clean/vimalakirti_nirdesa_sutra.txt`
- Output JSONL: `vimalakirti_dialogue_set_02.jsonl`
- Review packet: `vimalakirti_dialogue_set_02_random_review.md`
- Rows written: `53`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling seed: `20260524`
- Sampling mode: `random sample without replacement`
- Human review status: `pending`

## Parser Changes In This Pass

- Added colon-style turn extraction such as `Vimalakirti: ...`.
- Switched from fixed history turns to adaptive local-exchange context windows.
- Expanded context only within the current two-speaker exchange around each target.
- Kept `Participant A (...)` / `Participant B (...)` review formatting.
- Preserved rejection of unusable speakers such as pronoun-only attributions.

## Current Interpretation

- This pass restores a meaningful candidate pool.
- It still needs human review for context quality and cryptic-sequence failure modes.
