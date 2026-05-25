# `parse_majjhima_nikaya.py` Pass History

Current consecutive fully approved sets: `3`

## Set Log

### Set 01

- Status: `machine-blocked`
- Output rows after parser tightening: `1`
- Requested sample size: `10`
- Actual sample size: `1`
- Sampling mode: `full population` because fewer than `10` rows survived
- Sampling seed: `20260525`
- Review packet: `set_01/majjhima_nikaya_dialogue_set_01_random_review.md`
- Notes:
  - Parser fixes removed the previously observed wrong-speaker rows and long scene-jump rows from the Majjhima output.
  - The surviving candidate pool collapsed from `168` rows to `1`, which is not a meaningful conversational population and cannot count as a passing machine-review state.
  - Per project policy, a parser that begins to pass only because the candidate pool has collapsed unnaturally must be treated as failure, not success.

Approval rule reminder: `3` consecutive random sets must pass at `100%` before parser approval. A collapsed candidate pool is `machine-blocked`, not a pass.

### Set 02

- Status: `machine-blocked`
- Output rows after re-audit under loosened review policy: `1`
- Requested sample size: `10`
- Actual sample size: `1`
- Sampling mode: `full population` because fewer than `10` rows survived
- Sampling seed: `20260526`
- Review packet: `set_02/majjhima_nikaya_dialogue_set_02_random_review.md`
- Notes:
  - Under the loosened review policy, the surviving Majjhima row is no longer rejected for thin context and now scores `Approve with warning`.
  - The warning is `one prior turn of context`, which is now acceptable at review time.
  - The parser remains `machine-blocked` because a one-row population is still too small to count as a meaningful review pool.

### Set 03

- Status: `machine-pass-set-1`
- Output rows after parser rewrite: `190`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `20260527`
- Review packet: `set_03/majjhima_nikaya_dialogue_set_03_random_review.md`
- Notes:
  - The parser was rewritten around broader local exchange windows instead of the earlier continuity gate that collapsed the dataset.
  - Speaker attribution now searches narration around reporting verbs, strips embedded quote content from that search, and rejects malformed speaker labels before row construction.
  - The rebuilt dataset now forms a meaningful review population and the sampled Set 03 rows pass under the current review policy.

### Set 04

- Status: `machine-pass-set-2`
- Output rows after parser rewrite: `190`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `20260528`
- Review packet: `set_04/majjhima_nikaya_dialogue_set_04_random_review.md`
- Notes:
  - No parser changes were required in this pass.
  - A fresh seeded sample from the rewritten dataset passed under the current review policy.
  - Majjhima advanced to `machine-pass-set-2`.

### Set 05

- Status: `machine-approved`
- Output rows after parser rewrite: `190`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `20260529`
- Review packet: `set_05/majjhima_nikaya_dialogue_set_05_random_review.md`
- Notes:
  - No parser changes were required in this pass.
  - A third consecutive seeded sample passed under the current review policy.
  - Majjhima now satisfies the `3` consecutive passing-set rule and is `machine-approved`.
