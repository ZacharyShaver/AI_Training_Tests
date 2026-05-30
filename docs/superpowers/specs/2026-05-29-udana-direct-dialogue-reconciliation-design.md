# Udana Direct Dialogue Reconciliation Design

## Status

implemented 2026-05-29

## Outcome

- `parse_udana.py` now writes exclamation and direct-dialogue row families to
  separate artifacts by default.
- The regenerated exclamation artifact contains 80
  `udana_blessed_one_exclamation` rows.
- The regenerated direct-dialogue artifact contains 27
  `udana_blessed_one_direct_reply` rows.
- The older `udana_dialogue.jsonl` artifact is confirmed as a mixed 107-row
  legacy artifact and is no longer the manifest or vault target for direct
  candidate review.

## Problem

The current Udana parser output and project documentation disagree about what
`review_outputs/new_buddhist_sources/udana_dialogue.jsonl` contains.

The checked-in parser currently writes:

- `80` `udana_blessed_one_exclamation` rows
- `27` `udana_blessed_one_direct_reply` rows

into the same `udana_dialogue.jsonl` file.

However, the vault and manifest describe that file as if it were a separate
direct-dialogue candidate artifact with `107` direct rows. That mismatch makes
review unclear and weakens confidence in downstream dataset selection.

## Goals

- Separate Udana exclamation rows from Udana direct-dialogue candidate rows at
  the artifact level.
- Make parser output names reflect actual row families.
- Reconcile the manifest and vault notes with the generated artifacts.
- Inspect the direct-dialogue extraction path and intentionally tune its gates
  only if doing so improves source-grounded training quality.
- Regenerate review artifacts so the direct-dialogue candidate set can move into
  the newer parser-review workflow later.

## Non-Goals

- Promoting Udana direct-dialogue rows into the final dataset.
- Changing other parser families.
- Loosening filters merely to recover an old row count target.
- Rebuilding the full Buddhist dataset in this pass.

## Current State

### Source Of Truth In Code

`scripts/extraction/parse_udana.py` currently:

- builds `exclamation_rows` from `item_to_row(...)`
- builds `direct_rows` from `build_direct_rows(...)`
- concatenates them into one `rows` list
- writes that combined list to `--dataset-name`, whose default is
  `udana_dialogue`

As a result, the default checked-in `udana_dialogue.jsonl` is a mixed output.

### Source Of Truth In Artifacts

Current checked-in artifacts:

- `review_outputs/new_buddhist_sources/udana_exclamation_dialogue.jsonl`
- `review_outputs/new_buddhist_sources/udana_dialogue.jsonl`
- `review_outputs/new_buddhist_sources/udana_exclamation_dialogue_review_sample.md`

Observed row mix inside `udana_dialogue.jsonl`:

- `80` exclamation rows
- `27` direct-reply rows

### Drift In Documentation

The following project memory currently describe `udana_dialogue.jsonl` as if it
were direct-only:

- `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- `Obsidian/Projects/AI_Training_Tests/Parsers/parse_udana.md`
- `config/dataset_manifest.json`

## Proposed Design

### 1. Split Output Families

The parser should write separate artifacts for the two Udana row families:

- `udana_exclamation_dialogue.jsonl`
- `udana_direct_dialogue.jsonl`

And separate review samples:

- `udana_exclamation_dialogue_review_sample.md`
- `udana_direct_dialogue_review_sample.md`

The mixed `udana_dialogue.jsonl` artifact should stop being the primary output
for normal parser runs.

### 2. Make The CLI Reflect The Output Shape

`parse_udana.py` should stop coupling one default dataset name to both row
families.

Preferred shape:

- always build exclamation rows
- build direct rows unless a flag disables them
- write each row family to its own named output file
- print counts for each family independently

This keeps the parser behavior explicit and makes later review automation much
cleaner.

### 3. Audit Direct-Dialogue Quality Before Chasing Counts

The direct-dialogue candidate pool should be treated as quality-sensitive, not
count-sensitive.

The direct-row audit will inspect:

- target speaker filtering
- duplicate target suppression
- minimal history requirements
- narrator-context acceptance
- direct target word thresholds
- whether valid Blessed One replies are being discarded for avoidable reasons

The decision rule is:

- keep current gates when they are removing weak or ambiguous rows
- relax or adjust a gate only when the rejected row is clearly source-grounded,
  coherent, and useful training data in the three-message format

The work will favor a smaller clean direct pool over a larger noisy one.

### 4. Reconcile Durable Project Memory

After the parser output shape is corrected, update:

- `config/dataset_manifest.json`
- `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- `Obsidian/Projects/AI_Training_Tests/Parsers/parse_udana.md`

These updates should describe:

- the final exclamation artifact as the current final Udana source output
- the direct-dialogue artifact as a separate candidate family
- the real candidate row count from the regenerated direct-only artifact

### 5. Keep Promotion Out Of Scope

Even if the direct-only output improves, it remains candidate-only until it goes
through explicit sample review under the newer parser-review workflow.

This pass ends at:

- clean artifact separation
- regenerated candidate outputs
- corrected durable notes

It does not end at final dataset promotion.

## Implementation Outline

1. Refactor `parse_udana.py` output writing so exclamation and direct rows are
   written to separate JSONL and markdown files.
2. Regenerate Udana artifacts and inspect the resulting direct-only row count.
3. If the direct-only count is unexpectedly low, inspect rejected or filtered
   cases and make narrowly justified quality improvements.
4. Regenerate artifacts again after any parser adjustment.
5. Update the manifest and vault notes to match the corrected artifact layout
   and counts.

## Verification

The work will be considered complete for this pass when all of the following
are true:

- the parser writes separate exclamation and direct JSONL files
- the direct artifact contains only `udana_blessed_one_direct_reply` rows
- the exclamation artifact contains only `udana_blessed_one_exclamation` rows
- the review sample files match the separated row families
- the manifest and vault note text match the generated artifacts

Useful verification commands:

```text
python scripts/extraction/parse_udana.py
python -m pytest tests
```

And targeted content checks:

```text
group generated rows by metadata.kind
confirm file names and counts
inspect first and last rows of each artifact
```

## Risks

- The historical `107` figure may have been inferred from a mixed artifact
  rather than a real direct-only pool, so the regenerated direct count may stay
  small.
- Some direct-dialogue rows may look attractive but still be weak training data
  because they lack enough context or blur narration with reply turns.
- Any parser loosening that is not reviewed carefully could trade count for
  quality in a way the project has already tried to avoid.

## Recommendation

Proceed with artifact separation first, then treat direct-row count as an
empirical outcome of quality review rather than a target to recover.
