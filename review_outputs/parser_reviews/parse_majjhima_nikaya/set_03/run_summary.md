# `parse_majjhima_nikaya.py` Set 03 Run Summary

- Parser: `scripts/extraction/parse_majjhima_nikaya.py`
- Source: `source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages`
- Output JSONL: `majjhima_nikaya_dialogue_set_03.jsonl`
- Review packet: `majjhima_nikaya_dialogue_set_03_random_review.md`
- Rows written: `190`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling seed: `20260527`
- Sampling mode: `random sample without replacement`
- Machine review status: `machine-pass-set-1`
- Review-policy summary:
  - Approve: `8`
  - Approve with warning: `2`
  - Reject: `0`

## Parser Changes In This Pass

- Rebuilt local conversation windows so Majjhima can keep more than one or two prior turns when the scene remains nearby and coherent.
- Replaced brittle subject carryover with narration-focused speaker attribution and stronger quote-only alternation.
- Added speaker sanitation for malformed English clause-openers and fragmentary pseudo-speakers.
- Dropped malformed target fragments with dangling ellipses or unmatched quotes.

## Current Interpretation

- This rewritten parser no longer exhibits the one-row collapse that caused the earlier blocked states.
- The rebuilt dataset now contains a meaningful review population and the sampled Set 03 rows pass under the current review policy.
- This is the first consecutive clean set after the parser rewrite, so the parser advances to `machine-pass-set-1` rather than full approval.
