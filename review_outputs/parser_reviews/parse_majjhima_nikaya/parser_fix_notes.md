# `parse_majjhima_nikaya.py` Aggregate Parser Fix Notes

- Added Majjhima-specific speaker normalization and quote-handling for local exchanges such as `Saccaka` / `Aggivessana` and `The Blessed One`.
- Tightened quote-only turn inference so replies can flip speakers after local questions or short answers instead of inheriting stale speaker pairs.
- Added a local conversation-window gate with line-gap limits so monologue spillover and time-jump rows no longer survive into the dataset.
- Hardened malformed-speaker rejection so rows with labels such as `friend`, `The`, `Similarly`, and similar extraction debris are dropped instead of entering the review pool.
- Current blocker: after those fixes, the parser yields only `1` surviving row, which means the extraction strategy is now too brittle to sustain a meaningful Majjhima review population.
- Re-audit result under the loosened review policy: the surviving row now passes as `Approve with warning` instead of failing for thin context, but the parser remains blocked because the candidate pool is still degenerate.
- Current rewrite direction: Majjhima row assembly now uses broader local exchange windows, narration-focused speaker attribution, explicit single-name speaker validation, and fragment rejection for dangling ellipses or unmatched quotes.
- Current state: the rewritten parser rebuilds a meaningful pool of `190` rows, clears the current review policy at dataset level, and has now passed `3` consecutive seeded machine-review sets.
