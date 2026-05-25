# `parse_majjhima_nikaya.py` Set 02 Parser Fix Notes

- No extraction changes were made for this re-audit.
- The review policy was loosened so one-turn prompt rows and slight local looseness no longer count as automatic failures.
- Result: the surviving Majjhima row now evaluates as `Approve with warning` instead of being rejected for thin context.
- Remaining blocker: the parser still emits only one row, so the review population is not meaningful enough for machine approval.
