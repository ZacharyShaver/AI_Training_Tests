# `parse_majjhima_nikaya.py` Set 01 Parser Fix Notes

- Replaced stale-pair quote carryover with local-pair inference so question/answer runs no longer inherit speakers from earlier scenes.
- Added line-gap continuity checks to reject rows that splice later narrative or separate scenes onto an earlier prompt.
- Tightened speaker validation after the first rerun exposed malformed labels and an unnaturally collapsed pool.
- Result: the obvious bad rows were removed, but only one candidate survived, so this revision is blocked rather than approved.
