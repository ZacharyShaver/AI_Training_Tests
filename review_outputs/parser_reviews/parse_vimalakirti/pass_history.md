# `parse_vimalakirti.py` Pass History

Current consecutive fully approved sets: `3`

## Set Log

### Set 01

- Status: `superseded by parser redesign`
- Output rows after parser tightening: `2`
- Requested sample size: `10`
- Actual sample size: `2`
- Sampling mode: `full population` because fewer than `10` rows survived
- Review packet: `set_01/vimalakirti_dialogue_set_01_review_sample.md`
- Notes:
  - Parser no longer emitted the earlier one-turn, pronoun-speaker, and long scene-jump rows.
  - Surviving row count was too low, which suggested the source needed a redesigned extraction strategy.

### Set 02

- Status: `machine-failed`
- Output rows after adaptive-context redesign: `53`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `20260524`
- Review packet: `set_02/vimalakirti_dialogue_set_02_random_review.md`
- Notes:
  - Machine review found cross-scene continuity failures, declaration-sequence pseudo-replies, malformed speaker extraction, and incomplete quote fragments.
  - This set was retired after parser fixes and does not count toward approval streaks.

### Set 03

- Status: `machine-pass-set-1`
- Output rows after extraction and continuity fixes: `17`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `20260525`
- Review packet: `set_03/vimalakirti_dialogue_set_03_random_review.md`
- Notes:
  - All sampled rows passed machine review.
  - Candidate pool remained small but still substantive rather than collapsing to a trivial handful of examples.

### Set 04

- Status: `machine-pass-set-2`
- Output rows after extraction and continuity fixes: `17`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `20260526`
- Review packet: `set_04/vimalakirti_dialogue_set_04_random_review.md`
- Notes:
  - A second independent random sample passed at 100 percent.

### Set 05

- Status: `machine-approved`
- Output rows after extraction and continuity fixes: `17`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `20260527`
- Review packet: `set_05/vimalakirti_dialogue_set_05_random_review.md`
- Notes:
  - A third consecutive independent random sample passed at 100 percent.
  - `parse_vimalakirti.py` is now `machine-approved`.

Approval rule reminder: `3` consecutive random sets must pass at `100%` before parser approval.
