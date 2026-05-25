# `parse_vimalakirti.py` Aggregate Parser Fix Notes

- Removed stale failure modes from Set 02, including cross-scene Buddha replies, declaration-sequence pseudo-replies, pronoun/group contamination, and incomplete quote fragments.
- Recovered narrated question turns such as `Ananda asked the Buddha ...` so valid question-answer rows survive while scene-jump rows fail.
- Current candidate pool is smaller (`17` rows) but still spans multiple independent exchanges and no longer passes by collapsing to only one or two rows.
