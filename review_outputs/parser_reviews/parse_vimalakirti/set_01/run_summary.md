# `parse_vimalakirti.py` Set 01 Run Summary

- Parser: `scripts/extraction/parse_vimalakirti.py`
- Source: `source_texts/buddhist/clean/vimalakirti_nirdesa_sutra.txt`
- Output JSONL: `vimalakirti_dialogue_set_01.jsonl`
- Review packet: `vimalakirti_dialogue_set_01_review_sample.md`
- Turns parsed: `92`
- Rows written: `2`
- Requested sample size: `10`
- Actual sample size: `2`
- Sampling mode: `full population`
- Human review status: `pending`

## Parser Changes In This Pass

- Raised the default history window from `1` turn to `2` turns.
- Enforced exactly two active speakers across each review window.
- Required clean alternation into the target turn.
- Rejected pronoun-only speakers such as `They`.
- Rejected windows with large narrative gaps or long line-range jumps.
- Rendered prompt history in `Participant A (...)` / `Participant B (...)` form.
- Restored the old prompt ending: `Write Participant B's next reply.`

## Expected Effect

These changes were intended to eliminate:

- one-line, out-of-context prompts
- speaker-attribution failures
- cross-scene continuations
- review packets that do not match the older approved format

## Current Interpretation

This pass looks directionally correct for quality, but it may also show that the source does not yield enough strong direct-source next-reply rows once stricter review rules are applied.
