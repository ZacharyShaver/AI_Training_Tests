# `parse_milinda_panha.py` Pass History

Current consecutive fully approved sets: `0`

## Set Log

### Set 01

- Status: `candidate-baseline`
- Output rows after parser baseline fixes: `25`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1226856497`
- Review packet: `set_01/milinda_panha_dialogue_set_01_random_review.md`
- Notes:
  - This is the first review packet after moving Milinda onto the cached
    SuttaCentral export and fixing section-header plus same-paragraph cue parsing.
  - Parser promotion is still blocked pending review of speaker continuity and
    lingering mojibake in the exported text.

### Set 02

- Status: `candidate-refresh`
- Output rows after source-boundary cleanup and target-quality tightening: `14`
- Requested sample size: `10`
- Actual sample size: `10`
- Sampling mode: `random sample without replacement`
- Sampling seed: `1389503769`
- Review packet: `set_02/milinda_panha_dialogue_set_02_random_review.md`
- Notes:
  - The canonical SuttaCentral clean export was regenerated after fixing common
    mojibake at the source boundary, including broken diacritics and punctuation.
  - Inline quote parsing now honors repeated same-speaker cues inside long
    same-line exchanges instead of blindly alternating speakers.
  - The default Milinda candidate floor now excludes ultra-short stock targets
    such as `Certainly not, your majesty.` to keep the candidate pool focused on
    stronger prompt/target pairs.

Approval rule reminder: `3` consecutive random sets must pass at `100%` before parser approval.
