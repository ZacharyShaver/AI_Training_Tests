# `parse_bilara_pali_dialogue.py` Pass History

Current consecutive fully approved sets: `3` (set_09, set_10, set_11) — **APPROVED**

## Context

This parser reads from the local bilara-data GitHub clone at
`source_texts/buddhist/raw/bilara-data/` (sparse checkout, no network calls).
Default collections: all 34 DN suttas + SN1-11 (Sagāthāvagga, 271 suttas).

Replaces the deprecated SuttaCentral web-request fetcher
(`tools/source_ingest/fetch_milinda_suttacentral.py`).

Key components:
- Reader: `tools/source_ingest/bilara_reader.py`
- Parser: `src/ai_training_tests/extraction/parsers/bilara_pali_dialogue.py`
- Wrapper: `scripts/extraction/parse_bilara_pali_dialogue.py`

## Set Log

### Set 01

- Status: `fail`
- Parser version: initial implementation
- Output rows: `627`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `385213891`
- Review packet: `set_01/bilara_pali_dialogue_set_01_random_review.md`
- Pass/fail: `4/10 pass`
- Issues found:
  - `dn11`: Multi-speaker sutta — both non-target speakers collapsed to `Participant A`,
    making the prompt ambiguous (two different people sharing the same label).
  - `sn2.6`: `<j>` bilara HTML markup tag appeared inside the assistant target text.
  - `dn30`: Speaker labeled `"There the Buddha"` — locative word "There" from narrative
    captured as part of speaker name.
  - `dn16`: Speaker labeled `"Vesālī"` (city name) and `"they"` (pronoun) — place name
    and pronoun captured as speakers. Multiple DN16 rows failed due to the sutta's
    complex cast of characters across many scenes.
- Fixes applied before set_02:
  - Added `_strip_bilara_tags()` to remove `<j>` and similar markup.
  - Added "There", "Here", "Well", "Good", "Now", "Once", "Just" to `_SKIP_WORDS`.
  - Added `_speaker_is_valid()` check: rejects pronouns and known Pali place names.
  - Added multi-speaker history filter in `build_rows`: rejects rows where history
    has more than one distinct non-target speaker (prevents ambiguous `Participant A`).

### Set 02

- Status: `fail`
- Parser version: with tag-stripping and validity checks
- Output rows: `476`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: (from set_02 manifest)
- Review packet: `set_02/bilara_pali_dialogue_set_02_random_review.md`
- Pass/fail: `6/10 pass`
- Issues found:
  - `sn3.16`: Attendant misattributed as King Pasenadi — pre-scan registered King
    Pasenadi as the questioner for the whole sutta, causing an attendant's speech
    to be incorrectly labeled as King Pasenadi.
  - `dn16`: Pukkusa the Malla labeled as King Ajātasattu — DN16's large cast caused
    the pre-scanned speaker pair (Ajātasattu/Buddha from the sutta's opening) to
    bleed into unrelated later sections.
  - `dn16`: Speaker `"Vesālī"` (city) and `"they"` (pronoun) still appearing despite
    the validity check (some edge cases not yet covered).
  - `dn27`: Speaker `"they"` — pronoun slipping through.
- Fixes applied before set_03:
  - Expanded `_PRONOUN_LOWER` to cover "we", "you", "him", "her", "them", "his", "their".
  - Added `_PALI_PLACES` set of known place names excluded from speaker detection.
  - Added known-pair reset logic: when a new explicit speaker not in the current pair
    appears, `known_speakers` is cleared so alternation uses the new pair.
  - Added `_speaker_is_valid()` check applied at commit time and pre-scan time.

### Set 03

- Status: `fail`
- Parser version: with pronoun expansion, place-name exclusion, pair-reset
- Output rows: `730`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: (from set_03 manifest)
- Review packet: `set_03/bilara_pali_dialogue_set_03_random_review.md`
- Pass/fail: `6/10 pass`
- Issues found:
  - `dn3`: Speaker `"Though"` — the word "Though" in narrative "Though the student
    Ambaṭṭha sees..." being captured as a speaker name.
  - `dn16`: Ānanda/Buddha labels reversed in one row — `"Yes, worthy sir"` attributed
    to The Buddha; Vassakāra the minister labeled as King Ajātasattu. DN16 is too
    structurally complex (80+ pages, dozens of characters) for the two-speaker model.
  - `dn30`: DN30 (Marks discourse) has a highly repetitive alternating prose/verse
    structure that generates many rows with the same formulaic content.
  - `sn2.29`: Ānanda/Buddha labels reversed — the questioner (Buddha addressing
    Ānanda) and respondent (Ānanda) were swapped.
- Fixes applied before set_04:
  - Added "Though", "Thus", "Such", "Both", "All", "Not", "No", "Yes" to `_SKIP_WORDS`.
  - Added `_EXCLUDED_UIDS` set: `dn16`, `dn19`, `dn30` excluded by default. These are
    structurally too complex for the two-speaker model to handle reliably.

### Set 04

- Status: `fail`
- Parser version: with "Though" fix and complex-sutta exclusions
- Output rows: `594`
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `268724992`
- Review packet: `set_04/bilara_pali_dialogue_set_04_random_review.md`
- Pass/fail: `5/10 pass`
- Issues found:
  - `dn24`, `dn9` (later sections): Speaker labels reversed in 3-party conversation
    sections. DN24 (About Pāṭikaputta) and later sections of DN9 (Poṭṭhapāda)
    have more than 2 active speakers, causing speaker reversal.
  - `dn2` (one section): Last history turn misattributed — King Ajātasattu's speech
    labeled as The Buddha in the sliding context window.
  - `dn4` (Row 1): Very short 6-word target ("Yes, gentlemen, it is true.") — not a
    clear training example, minimal context.
  - `dn2` (Row 8): Speaker `"Neither"` captured from narrative "Neither can I..." text.
- Pattern observed across all sets:
  - SN1-11 (Sagāthāvagga) rows pass at ~90% — short verse dialogues with clean
    2-speaker structure and explicit reporting clauses.
  - DN rows pass at ~40-50% — complex narrative suttas have multi-party sections
    that exceed the two-speaker model's handling capacity.
- Next planned action:
  - Option A: Promote SN1-11 rows only (296 deduplicated rows) as a clean candidate
    subset while DN parser work continues.
  - Option B: Add DN9 and DN24 to `_EXCLUDED_UIDS`; add "Neither" and "Clearly" to
    `_SKIP_WORDS`; restrict DN to known clean 2-speaker suttas (DN2, DN21, DN23,
    DN25) for a tighter fifth pass.

### Set 05

- Status: `fail`
- Parser version: DN-focused pass — 6 additional DN exclusions + interrogative/conjunction SKIP_WORDS
- Excluded UIDs (cumulative): dn3, dn9, dn13, dn16, dn18, dn19, dn24, dn29, dn30
- Output rows: `463` (DN: 161, SN: 302)
- Requested sample size: `10` / Actual: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `2074180061`
- Review packet: `set_05/bilara_pali_dialogue_set_05_random_review.md`
- Pass/fail: `7/10 pass` (best result so far; rows 9 and 10 borderline)
- Passes by the pipeline lenient standard (mild thinness acceptable): `7-9/10`
- Issues found:
  - `dn2` (Row 5): Speaker labels reversed — "What do you think, great king?" labeled
    as King Ajātasattu (B) instead of The Buddha. Root cause: in long suttas the Buddha
    sometimes ASKS questions of the human, breaking the fixed questioner/respondent
    alternation. The parser's alternation has no way to detect when the Buddha initiates.
  - `dn21` (Row 7): Pañcasikha's devotional hymn ("Homage to him, the blessed one...")
    labeled as The Buddha — a third character's speech bleeding in.
  - `dn5` (Row 8): Target text addressed TO the Buddha labeled as The Buddha speaking —
    multi-speaker section in DN5 where a brahmin questioner speaks but is attributed to
    the wrong position in the pair.
  - `dn11` (Row 9, borderline): Target identical to an earlier history turn — Kevaḍḍha
    repeats his request verbatim. Accurate to source; passes "mild thinness" criterion.
  - `dn25` (Row 10, borderline): Same affirmation formula in both history and target.
- Pipeline constraint notes (from this review):
  - `review_policy.py` auto-checks are NOT called by the pipeline runner — pipeline is
    entirely human review of 10 rows. No automated pre-filtering of hard failures.
  - `scene_looseness` warning never fires — `source_lines` are segment key strings, not
    integers, so the integer comparison always returns False (unreported gap in policy).
  - Pipeline criteria are NOT overly strict — "mild thinness acceptable" means rows 9/10
    would pass strict pipeline review.
- Next planned action:
  - The remaining DN failures all trace to bidirectional Q&A (the Buddha initiates
    questions) breaking the fixed alternation model. Options:
    A: Accept the current 7/10 rate and promote SN-only (302 rows) as a clean first pass.
    B: Add a check in `build_rows` that rejects rows where the first history turn
       (oldest) has a speaker name mismatch with the reported questioner — filtering
       alternation-reversal rows without excluding whole suttas.
    C: Move to SN-only promotion now; park DN improvements for a future parser version.

### Set 06

- Status: `fail`
- Output rows: `429`
- Seed: (set_06 manifest)
- Pass/fail: `8/10 pass`
- Issues: Row 1 (SN3.19): King Pasenadi A-turn contained "great king" — a reverse
  where the Buddha's speech bled into the King's label. A-turn reversal check
  was not yet covering this case. Row 9 (DN12): Rosika (3rd character) speech
  attributed to The Buddha through alternation.
- Fixes: Added A-labeled turn to `_has_attribution_reversal` checks. Added `dn12` to
  `_EXCLUDED_UIDS`.

### Set 07

- Status: `fail`
- Output rows: `389`
- Seed: (set_07 manifest)
- Pass/fail: `9/10 pass`
- Issues: Row 10 (SN2.23): Target text cut off mid-sentence ending with `,` —
  fragmentary target from a mid-segment quote boundary error. The `auto_hard_failures`
  policy check was not applied before sampling.
- Fixes: Wired `auto_hard_failures` from `review_policy.py` as a post-build filter
  in `build_rows`. Added `dn6` to `_EXCLUDED_UIDS` (Mahāli/Oṭṭhaddha 3-party issue).

### Set 08

- Status: `fail`
- Output rows: `376`
- Seed: (set_08 manifest)
- Pass/fail: `8/10 pass`
- Issues: Row 7 (SN3.12 Vaṅgīsa): `Participant B (The Buddha)` says "I feel inspired to
  speak, Blessed One! I feel inspired to speak, Holy One!" — devotee's speech attributed
  to the Buddha. "Blessed One" and "Holy One" were not in the Buddha address_re pattern.
  Row 9 (DN6): Oṭṭhaddha/Mahāli speaker reversal with 3-party complexity not caught.
- Fixes: Added `\bblessed one\b|\bholy one\b` to the Buddha address_re in
  `_B_SELF_ADDRESS_CHECKS`. Added `dn6` to `_EXCLUDED_UIDS`.

### Set 09 ✓ CLEAN

- Status: `pass`
- Output rows: `352`
- Seed: (set_09 manifest)
- Pass/fail: `10/10` — first fully clean pass
- Notes: All rows correctly attributed. SN sagāthāvagga and tighter DN set now
  producing consistently clean output. Consecutive clean count: 1.

### Set 10 ✓ CLEAN

- Status: `pass`
- Output rows: `352`
- Seed: (set_10 manifest)
- Pass/fail: `10/10`
- Notes: Consecutive clean count: 2.

### Set 11 ✓ CLEAN — PARSER APPROVED

- Status: `pass — APPROVED`
- Output rows: `352`
- Seed: (set_11 manifest)
- Pass/fail: `10/10`
- Notes: Three consecutive clean passes achieved. Parser meets the approval gate.
  Consecutive clean count: 3.
- Approval date: 2026-05-31
- Next step: Promote `review_outputs/new_buddhist_sources/bilara_pali_dialogue.jsonl`
  to the Buddhist final dataset after updating `config/dataset_manifest.json`,
  `dashboard/project-progress-data.js`, and the relevant Obsidian notes.

---

## Final Parser State (approved)

- Output file: `review_outputs/new_buddhist_sources/bilara_pali_dialogue.jsonl`
- Row count: `352` (deduplicated, auto-hard-failure filtered)
- Collections: DN (cleaned set) + SN1-11 (Sagāthāvagga)
- Excluded DN suttas: dn3, dn6, dn9, dn12, dn13, dn16, dn18, dn19, dn24, dn29, dn30
- Key filters applied:
  - `_EXCLUDED_UIDS`: 11 structurally complex suttas excluded
  - `_SKIP_WORDS`: 40+ common non-speaker words that appear capitalized in narrative
  - `_has_attribution_reversal()`: speaker-content cross-check for label swaps
  - `_PALI_PLACES`: known place names excluded from speaker detection
  - `auto_hard_failures()`: fragmentary/contaminated rows filtered before dedup
  - Target deduplication: exact duplicate targets removed

## Approval rule reminder

`3` consecutive random sets must pass at `100%` before parser approval.
