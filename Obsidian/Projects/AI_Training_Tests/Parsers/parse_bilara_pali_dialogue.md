# parse_bilara_pali_dialogue.py

## Status

final

## Parser

- Code: `src/ai_training_tests/extraction/parsers/bilara_pali_dialogue.py`
- Wrapper: `scripts/extraction/parse_bilara_pali_dialogue.py`
- Reader: `tools/source_ingest/bilara_reader.py`
- Source: `source_texts/buddhist/raw/bilara-data/` (local GitHub clone, no network calls)
- Candidate output: `review_outputs/new_buddhist_sources/bilara_pali_dialogue.jsonl`
- Final dataset: `review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset.jsonl`
- Review pipeline: `review_outputs/parser_reviews/parse_bilara_pali_dialogue/`

## Approval

- Approved: 2026-05-31
- Passes required: 3 consecutive clean (set_09, set_10, set_11)
- Total sets run: 11
- Final row count: 352

## Collections

Default: `--collections dn sn1-11`

| Collection | Suttas | Notes |
|---|---|---|
| DN (cleaned) | 34 minus 11 excluded | Excluded: dn3, dn6, dn9, dn12, dn13, dn16, dn18, dn19, dn24, dn29, dn30 |
| SN1-11 (Sagāthāvagga) | 271 | Short verse dialogues, very clean 2-speaker structure |

## Key Design Decisions

- **Two-speaker model**: parser detects a questioner + The Buddha pair; uses alternation
  for unattributed speeches.
- **Speaker validity**: `_speaker_is_valid()` rejects pronouns, Pali place names,
  common English words.
- **Reversal detection**: `_has_attribution_reversal()` catches cases where a speaker's
  own turn contains address terms that only others use for them (e.g., King saying
  "great king", The Buddha saying "Holy One").
- **Automated pre-filter**: `auto_hard_failures()` from `review_policy.py` removes
  fragmentary, contaminated, or malformed rows before deduplication.
- **Deduplication**: exact duplicate target texts removed.

## Refresh

To regenerate from the same bilara-data clone:

```powershell
python scripts/extraction/parse_bilara_pali_dialogue.py --collections dn sn1-11
```

To refresh the bilara-data clone:

```powershell
cd source_texts/buddhist/raw/bilara-data
git pull
```

## Links

- [[Parser Hub]]
- [[../Sources/Buddhist Sources]]
