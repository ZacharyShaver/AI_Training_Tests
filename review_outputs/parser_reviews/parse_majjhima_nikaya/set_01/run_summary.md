# `parse_majjhima_nikaya.py` Set 01 Run Summary

- Parser: `scripts/extraction/parse_majjhima_nikaya.py`
- Source: `source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages`
- Output JSONL: `majjhima_nikaya_dialogue_set_01.jsonl`
- Review packet: `majjhima_nikaya_dialogue_set_01_random_review.md`
- Rows written: `1`
- Requested sample size: `10`
- Actual sample size: `1`
- Sampling seed: `20260525`
- Sampling mode: `full population`
- Machine review status: `machine-blocked`

## Parser Changes In This Pass

- Added Majjhima-specific speaker normalization for local dialogue names and titles.
- Tightened quote-only exchange inference to avoid stale speaker carryover.
- Added line-gap continuity gating so long monologue jumps no longer produce reply rows.
- Rejected malformed generic speaker labels that appeared after the first tightening pass.

## Current Interpretation

- This revision successfully removed the concrete wrong-speaker and cross-scene failure modes seen in the pre-review Majjhima output.
- The candidate pool then collapsed to a single surviving row, which means the parser no longer has a substantive conversational population.
- Under the machine-review rule, this is a `machine-blocked` state rather than a pass.
