# Delete And Cleanup Candidates

Updated: 2026-05-25

Candidates 1–5 in this document are approved for deletion/untracking. Other candidates require the listed verification and explicit user approval before any cleanup command is run.

## High-Confidence Delete Or Untrack Candidates

| Candidate path | Reason | Required verification | Approval status |
| --- | --- | --- | --- |
| `ai_training_tests.egg-info/` | Generated package metadata should not be tracked. The ignore rule now covers `*.egg-info/`. | Confirm package imports and tests work without tracked metadata, then untrack with user approval. | Approved |
| `.codegraph/codegraph.db` | Generated local CodeGraph index state. | Confirm `.codegraph/.gitignore` or root `.gitignore` keeps the DB untracked. | Not approved |
| `Obsidian/.obsidian/workspace.json` | Obsidian local UI workspace state is noisy in shared repo history. | Confirm shared vault settings do not require committing workspace state. | Not approved |
| `review_outputs/full_dialogue_dataset/full_dialogue_dataset.jsonl` | Appears to overlap with `review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset.jsonl`. | Compare file hashes and check references before deleting or replacing with a docs pointer. | Approved |
| `review_outputs/new_buddhist_sources/zen_koans_database_dialogue.jsonl` | Appears to overlap with `review_outputs/new_buddhist_sources/zen_koans_database_clean_dialogue.jsonl`. | Compare file hashes and check parser/docs references. | Approved |

## Archive Or Delete After Review

| Candidate path | Reason | Required verification | Approval status |
| --- | --- | --- | --- |
| `review_outputs/initial_dialogue_dataset/` | Older snapshot appears superseded by the full dataset. | Confirm no unique records are absent from final outputs. | Not approved |
| `review_outputs/pilot_dialogue_dataset/` | Older pilot snapshot appears superseded by the full dataset. | Confirm current full rebuild can regenerate any still-needed base rows. | Not approved |
| `Training Data/Test Conversations/dual_model_demo_*.jsonl` | These appear duplicated by `Training Data/cleaned_pipeline/cleaned_dialogue/`. | Compare hashes and decide the canonical transcript-derived folder. | Approved |
| `review_outputs/new_buddhist_sources/*_direct_review_sample.md` | Some direct review sample files may be empty or failed sample artifacts. | Open each file and confirm whether durable review content exists. | Not approved |
| `.claude/CLAUDE.md` | Tool-specific guidance may overlap `AGENTS.md` and general CodeGraph docs. | Preserve as Claude-only guidance, or move general guidance into `docs/tooling/codegraph.md` after review. | Not approved |

## Rename Or Move Candidates

| Candidate path | Issue | Proposed destination | Required verification | Approval status |
| --- | --- | --- | --- | --- |
| `oritiginal text/` | Misspelled legacy folder name, still referenced by scripts. | `data/legacy/original_text/` | Add compatibility path handling and update script/docs references first. | Not approved |
| `Training Data/` | Space in path and mixed concerns. | `data/legacy/training_data/` | Add compatibility path handling and update script/docs references first. | Not approved |

## Cleanup Gate

Before any cleanup happens:

1. Collect hash, import, or reference evidence for the specific path.
2. Present the evidence to the user.
3. Wait for explicit approval for the specific path.
4. Use `git rm` or `git mv` only for approved tracked paths.
5. Re-run tests and reference searches after the cleanup.

## Verification Evidence Captured 2026-05-25

No cleanup has been approved or performed.

### Strong Cleanup Candidates

| Candidate path | Evidence | Suggested action if approved |
| --- | --- | --- |
| `ai_training_tests.egg-info/` | Tracked files: `PKG-INFO`, `SOURCES.txt`, `dependency_links.txt`, `requires.txt`, `top_level.txt`. Root `.gitignore` now ignores `*.egg-info/`, and `git check-ignore --no-index ai_training_tests.egg-info/PKG-INFO` confirms future generated metadata is ignored. Package imports and tests pass from `src/ai_training_tests/`. | `git rm -r ai_training_tests.egg-info/` |
| `.codegraph/codegraph.db` | Exists locally at 2,424,832 bytes. `.codegraph/.gitignore` ignores `*.db`, `*.db-wal`, `*.db-shm`, cache, logs, and hook markers. Root `.gitignore` also ignores `.codegraph/codegraph.db`; `git check-ignore .codegraph/codegraph.db` confirms ignore coverage. | Leave untracked and do not commit. |
| `Obsidian/.obsidian/workspace.json` | Exists locally at 6,747 bytes. Root `.gitignore` ignores it; `git check-ignore Obsidian/.obsidian/workspace.json` confirms ignore coverage. | Leave untracked and do not commit. |
| `review_outputs/full_dialogue_dataset/full_dialogue_dataset.jsonl` | SHA256 matches `review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset.jsonl`: `AD7C0B58A32BF9E78508A7694702B886A7E01540DEE560E1708DF5BC80F56C49`. The rebuild script still writes this compatibility file. | Keep for now, or approve a later compatibility change before deletion. |
| `review_outputs/new_buddhist_sources/zen_koans_database_dialogue.jsonl` | SHA256 matches `review_outputs/new_buddhist_sources/zen_koans_database_clean_dialogue.jsonl`: `208772DCB2B8EC188239E661C2EFBDAD790DD1CFF149E4EF0F487908BC6E127B`. Parser/vault notes still mention it as a duplicate candidate. | Keep for now, or approve deletion after reference update. |
| `Training Data/Test Conversations/dual_model_demo_*.jsonl` | Hashes exactly match `Training Data/cleaned_pipeline/cleaned_dialogue/combined_messages.jsonl`, `participant_a_messages.jsonl`, and `participant_b_messages.jsonl`. | Candidate for deletion after approval if cleaned pipeline outputs are canonical. |
| `review_outputs/new_buddhist_sources/udana_exclamation_dialogue_direct_review_sample.md` | 63-byte file containing only title plus `Direct rows parsed: 0`. | Candidate for deletion after approval. |

### Candidates Requiring More Review

| Candidate path | Evidence | Current recommendation |
| --- | --- | --- |
| `review_outputs/initial_dialogue_dataset/` | Tracked. `initial_dialogue_dataset.jsonl` has 78 rows, with 21 record IDs not found in the current final combined dataset by exact `metadata.record_id`. `pilot_dialogue_dataset.jsonl` lacks `metadata.record_id` values, so exact ID comparison is inconclusive. | Do not delete yet. Review whether the missing rows or no-ID rows have historical value. |
| `review_outputs/pilot_dialogue_dataset/` | Tracked. `pilot_dialogue_dataset.jsonl` has 26 rows and lacks `metadata.record_id` values, so exact ID comparison is inconclusive. | Do not delete yet. Review historical value first. |
| `oritiginal text/` | Still referenced by manifest, dashboard data, parser notes, docs, and scripts. | Do not move until compatibility path handling exists. |
| `Training Data/` | Still referenced by docs and data prep defaults. | Do not move until compatibility path handling exists. |
| `.claude/CLAUDE.md` | Untracked local/tool-specific guidance. | Preserve as tool-specific guidance unless the user wants it consolidated. |
