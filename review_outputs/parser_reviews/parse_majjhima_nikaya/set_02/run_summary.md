# `parse_majjhima_nikaya.py` Set 02 Run Summary

- Parser: `scripts/extraction/parse_majjhima_nikaya.py`
- Source: `source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages`
- Output JSONL: `majjhima_nikaya_dialogue_set_02.jsonl`
- Review packet: `majjhima_nikaya_dialogue_set_02_random_review.md`
- Rows written: `1`
- Requested sample size: `10`
- Actual sample size: `1`
- Sampling seed: `20260526`
- Sampling mode: `full population`
- Machine review status: `machine-blocked`
- Review-policy summary:
  - Approve: `0`
  - Approve with warning: `1`
  - Reject: `0`

## Parser Changes In This Pass

- No parser changes were applied in this pass.
- This set re-audits the existing Majjhima output under the loosened review policy that distinguishes hard failures from soft warnings.

## Current Interpretation

- The surviving row is now acceptable under review policy and no longer fails purely for thin context.
- The row still carries the warning `one prior turn of context`.
- The parser remains `machine-blocked` because a one-row dataset is too small to count as a meaningful random-review population.
