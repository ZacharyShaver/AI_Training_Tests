# `parse_majjhima_nikaya.py` Set 01 Random Review

- Seed: `20260525`
- Rows available: `1`
- Sampled rows: `1`

## Review Example 1: Majjhima Nikaya

- Record ID: `mn126-html:majjhima_nikaya_next_reply_126_2:203-206:ven-bh-mija`
- Kind: `majjhima_nikaya_next_reply`
- Lines: `MN126.html:203-206`
- Target: `Participant B (Ven. Bhūmija)`
- Target words: `44`
- Reviewer status: `Approve`

### User Prompt

```text
Conversation so far:
Participant A (Master Bhūmija): I haven't heard this face to face with the Blessed One, prince, I haven't received this face to face with the Blessed One, but there is the possibility that the Blessed One would answer in this way: 'If one follows the holy life inappropriately, even when having made a wish (for results), one is incapable of obtaining results. If one follows the holy life inappropriately, even when having made no wish… both having made a wish and having made no wish… neither having made a wish nor having made no wish, one is incapable of obtaining results. (But) if one follows the holy life appropriately, even when having made a wish, one is capable of obtaining results. If one follows the holy life appropriately, even when having made no wish… both having made a wish and having made no wish… neither having made a wish nor having made no wish, one is capable of obtaining results.' I haven't heard this face to face with the Blessed One, I haven't received this face to face with the Blessed One, but there is the possibility that the Blessed One would answer in this way.

Write Participant B's next reply.
```

### Assistant Target

```text
If one follows the holy life even when having made a wish (for results)… having made no wish… both having made a wish and having made no wish… neither having made a wish nor having made no wish, one is incapable of obtaining results.
```

### Machine Review Notes

- Decision: `Approve`
- Reason: The surviving row is locally coherent and does not show the wrong-speaker or scene-jump failures that appeared in the earlier Majjhima output.

## Parser-Level Outcome

- Overall parser status: `machine-blocked`
- Blocking reason: a single approved row is not a meaningful review population, and the current parser revision collapses from `168` rows to `1`.
- Required next step for future work: redesign Majjhima extraction so local two-speaker continuity is preserved without collapsing the dataset.
