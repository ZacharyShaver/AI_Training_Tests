# AI Training Tests

This project builds local AI training data from philosophical and spiritual source
texts. The current main focus is direct-source dialogue data: the scripts pull
real passages from source texts and turn them into chat-style JSONL records.

The project does not train a model by itself. It prepares datasets that can be
used later for local fine-tuning.

## What This Project Does

In simple terms:

1. Source texts live in folders like `oritiginal text/` and `source_texts/`.
2. Python extraction scripts find usable conversations or teaching passages.
3. The scripts convert those passages into chat records with this shape:

   ```json
   {
     "messages": [
       {"role": "system", "content": "..."},
       {"role": "user", "content": "Conversation so far: ..."},
       {"role": "assistant", "content": "..."}
     ],
     "metadata": {
       "source": "...",
       "source_lines": [1, 2],
       "target_speaker": "..."
     }
   }
   ```

4. Generated datasets and review samples are written to `review_outputs/`.
5. A Streamlit prototype can run two local LM Studio models in conversation.

## Main Workflow

The main rebuild command is:

```bash
python scripts/extraction/build_full_dialogue_outputs.py
```

That script rebuilds the current full dialogue dataset by running several smaller
scripts in order:

1. `build_pilot_dialogue_dataset.py`
   Extracts dialogue rows from the older text files in `oritiginal text/`.

2. `parse_gateless_gate.py`
   Extracts koan/commentary rows from The Gateless Gate.

3. `parse_diamond_sutra.py`
   Extracts attributed dialogue rows from The Diamond Sutra.

4. `parse_udana.py`
   Regenerates the Udana exclamation rows used in the full dataset.

5. `parse_sutta_nipata.py`
   Regenerates the Sutta Nipata rows used in the full dataset.

6. `combine_dialogue_datasets.py`
   Combines the base output with Gateless Gate, Diamond Sutra, Udana
   exclamation, and Sutta Nipata JSONL files, then skips duplicate record IDs.

7. `split_dialogue_dataset.py`
   Creates combined, Buddhist-only, and esoteric-only train/eval splits.

8. `make_review_sample.py`
   Creates smaller Markdown files that are easier to inspect by hand.

Current full output folder:

```text
review_outputs/full_dialogue_dataset/
```

Current generated full dataset counts:

```text
Combined: 1,277 rows, 1,156 train, 121 eval
Buddhist: 854 rows, 774 train, 80 eval
Occult / esoteric: 423 rows, 382 train, 41 eval
```

Current combined sources:

```text
The Key to Theosophy: 370 rows
The Corpus Hermeticum: 28 rows
Asclepius: 25 rows
Milinda Panha: 73 rows
Platform Sutra: 19 rows
Itivuttaka: 107 rows
Majjhima Nikaya: 168 rows
The Gateless Gate: 129 rows
The Diamond Sutra: 83 rows
Udana: 80 rows
Sutta Nipata: 80 rows
Vimalakirti Nirdesa Sutra: 17 rows
Zen Koans Database: 98 rows
```

The main rebuild command now regenerates every source currently included in the
full combined dataset before writing splits and review samples.

## Important Folders

### `scripts/extraction/`

Compatibility entrypoints for the extraction code. Shared domain modules, review
policy, JSONL helpers, and the first migrated parser now live under
`src/ai_training_tests/`; the old script paths remain as wrappers while the
package migration continues.

Most important files:

- `build_full_dialogue_outputs.py`
  Runs the full current rebuild.
- `build_pilot_dialogue_dataset.py`
  Builds the base direct-source dialogue rows from the older text sources.
- `parse_gateless_gate.py`
  Builds The Gateless Gate rows.
- `parse_diamond_sutra.py`
  Builds The Diamond Sutra rows.
- `parse_udana.py`
  Builds Udana rows. The full dataset currently uses the regenerated
  `udana_exclamation_dialogue.jsonl` output.
- `parse_sutta_nipata.py`
  Builds Sutta Nipata rows. The full rebuild command regenerates this output
  before combining datasets.
- `parse_itivuttaka.py`
  Builds Itivuttaka rows included in the current Buddhist dataset.
- `parse_majjhima_nikaya.py`
  Builds Majjhima Nikaya rows included in the current Buddhist dataset.
- `parse_asclepius.py`
  Compatibility wrapper for `ai_training_tests.extraction.parsers.asclepius`.
- `split_dialogue_dataset.py`
  Writes train/eval splits.
- `make_review_sample.py`
  Writes readable Markdown review samples.

### `src/ai_training_tests/`

Packaged Python code introduced for the architecture migration:

- `domain/dialogue_schema.py`
  Pydantic validation for the three-message dialogue row format.
- `domain/source_manifest.py`
  Approved source manifest used by rebuild and split logic.
- `extraction/common/`
  Shared JSONL, text-cleaning, and review-sample helpers.
- `extraction/review/review_policy.py`
  Structural review policy used by machine-review packets.
- `extraction/parsers/asclepius.py`
  First migrated source parser.

Existing `scripts/extraction/*.py` paths are preserved for compatibility.

### `review_outputs/`

Generated output files for review and training.

Most important folder:

```text
review_outputs/full_dialogue_dataset/
```

Most important training files:

```text
review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset_train.jsonl
review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset_eval.jsonl
review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset_train.jsonl
review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset_eval.jsonl
review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset_train.jsonl
review_outputs/full_dialogue_dataset/full_esoteric_dialogue_dataset_eval.jsonl
```

### `oritiginal text/`

Original text files used by the older extraction scripts. The folder name is
misspelled in the repository, so scripts use that exact spelling.

Do not rename this folder unless you also update the script paths.

### `source_texts/`

Newer source-text storage, especially Buddhist sources.

Important files:

- `source_texts/buddhist/SOURCES.md`
  Notes where the Buddhist source texts came from.
- `source_texts/buddhist/raw/`
  User-supplied PDFs.
- `source_texts/buddhist/clean/`
  Text extracted from those PDFs.
- `source_texts/buddhist/diamond_sutra_gutenberg.txt`
  Diamond Sutra source used by `parse_diamond_sutra.py`.
- `source_texts/buddhist/gateless_gate_wikisource_raw.json`
  Gateless Gate source used by `parse_gateless_gate.py`.

### `scripts/data_prep/`

Supporting and older data-prep scripts. These are useful if you are working with
dual-chat transcripts or old Q&A-style datasets, but they are not the current
main direct-source extraction path.

### `scripts/apps/`

Contains the Streamlit LM Studio prototype:

```text
scripts/apps/streamlit_lmstudio_dual_chat.py
```

## Running The Streamlit Prototype

The app expects LM Studio's local OpenAI-compatible server to be running.

Install the app dependencies:

```bash
python3 -m pip install -r "Training Data/requirements_streamlit_lmstudio.txt"
```

Run the app:

```bash
streamlit run scripts/apps/streamlit_lmstudio_dual_chat.py
```

By default, the app tries to connect to:

```text
http://localhost:8000
```

## Output Files To Review

Before using a generated dataset for training, inspect the Markdown review files:

```text
review_outputs/full_dialogue_dataset/full_combined_dialogue_dataset_review_sample.md
review_outputs/full_dialogue_dataset/full_buddhist_dialogue_dataset_review_sample.md
review_outputs/full_dialogue_dataset/full_dialogue_dataset_review.md
```

These files show the prompt and target answer in a human-readable way.

## Quick Checks

Run the currently available parser unittest from the repository root:

```bash
python -m pytest tests -q
```

Regenerate the dataset validation report:

```bash
python -B scripts/extraction/validate_dialogue_dataset.py --output-md review_outputs/full_dialogue_dataset/dialogue_dataset_validation_report.md
```

For dataset health, check `full_dialogue_dataset_splits.md` after each rebuild
and verify row counts, source coverage, and train/eval sizes before training.

## Notes

- The extraction code uses regular expressions and source-specific rules. It is
  practical, but human review is still important.
- The scripts try to preserve original source wording while cleaning extraction
  artifacts like footnote markers, bad PDF characters, broken hyphenation, and
  page noise.
- Some source folders and file names contain spaces. Quote those paths in shell
  commands.
- The repository now has a lightweight pytest suite and a package spine under
  `src/ai_training_tests/`, while most parser entrypoints can still be run
  directly through `scripts/extraction/`.

For a slower, more detailed explanation of how the code works, read
`CODE_EXPLAINED.md`.
