# Code Explained

This file explains the project in plain English. It is meant to be readable even
if you are not deep into Python or machine-learning data pipelines.

## The Big Idea

The project is a dataset factory.

It starts with books and source texts. Then it uses Python scripts to find useful
dialogue or teaching passages. Then it turns those passages into JSONL training
examples that look like chat conversations.

The final output is not a trained model. The final output is training data.

## The Most Important Concept

Most generated records use this idea:

```text
Here is the conversation so far.
Now write the next reply from one speaker.
```

The model sees:

```text
Conversation so far:
Participant A (...): ...
Participant B (...): ...

Write Participant B's next reply.
```

The answer is the real next reply from the source text.

That means the code is not asking an AI to invent answers. The code is trying to
extract the real answer from the original text.

## The Main Data Shape

Most output rows are JSONL records. JSONL means "one JSON object per line."

A normal row looks like this:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are a Buddhist philosophical interlocutor..."
    },
    {
      "role": "user",
      "content": "Conversation so far:\n...\n\nWrite Participant B's next reply."
    },
    {
      "role": "assistant",
      "content": "The source-text reply goes here."
    }
  ],
  "metadata": {
    "record_id": "unique-id",
    "kind": "explicit_next_reply",
    "source": "The Key to Theosophy",
    "source_file": "the_key-to-theosophy.txt",
    "source_lines": [104, 107],
    "target_speaker": "Theosophist",
    "target_participant": "Participant B",
    "target_words": 68
  }
}
```

The `messages` field is what a training tool usually consumes.

The `metadata` field is for humans and debugging. It tells you where the row came
from and what kind of row it is.

## The Full Pipeline

The current full rebuild command is:

```bash
python scripts/extraction/build_full_dialogue_outputs.py
```

That script is the project's main "run everything" button.

It does this:

```text
source texts
  -> source-specific parsers
  -> JSONL dialogue rows
  -> combined dataset
  -> train/eval splits
  -> Markdown review samples
```

The current full output goes here:

```text
review_outputs/full_dialogue_dataset/
```

The current generated full output contains 1,277 combined rows: 1,156 train rows
and 121 eval rows. The Buddhist split has 854 rows, and the occult / esoteric
split has 423 rows.

## Step 1: Mine Or Parse Source Texts

Different source texts have different structures. The code uses different tricks
for each kind of source.

Some texts have explicit speaker labels:

```text
ENQUIRER. ...
THEOSOPHIST. ...
```

Those are easier to parse.

Some texts use normal prose:

```text
King Milinda said, "..."
Nagasena replied, "..."
```

Those need more careful regular expressions.

Some sources come from PDFs and have messy characters, page numbers, headers, and
footnotes. Those need cleanup before they become training data.

## Step 2: Build Training Rows

After a script finds turns in a source text, it chooses one turn as the answer.
The turns before it become the prompt.

Example:

```text
Turn 1: Participant A asks something.
Turn 2: Participant B answers.
Turn 3: Participant A asks another thing.
Turn 4: Participant B answers again.
```

The script can make a training row like:

```text
User prompt:
Conversation so far:
Turn 1
Turn 2
Turn 3

Write Participant B's next reply.

Assistant target:
Turn 4
```

This teaches a model how a certain speaker responds in context.

## Step 3: Clean The Text

Many source files have problems that would hurt training quality.

The cleanup code removes or repairs things like:

- page numbers
- footnote markers
- weird PDF characters
- broken words from line wrapping
- extra whitespace
- table-of-contents text
- obvious editorial notes

The important rule is that cleanup should fix extraction artifacts, not rewrite
the source's meaning.

## Step 4: Combine Outputs

`combine_dialogue_datasets.py` reads multiple JSONL files and writes one combined
file.

It also checks `metadata.record_id`. If two rows have the same record ID, only
the first one is kept.

This prevents accidental duplicate training rows.

## Step 5: Split Into Train And Eval

`split_dialogue_dataset.py` creates:

- one combined dataset
- one Buddhist-only dataset
- one esoteric-only dataset
- train/eval splits for each

Train rows are used for learning.

Eval rows are held back so you can test whether training is working.

The split is deterministic. It does not randomly shuffle. It keeps a regular
slice from each source so the eval set has examples from multiple sources.

## Step 6: Make Review Samples

`make_review_sample.py` creates small Markdown review files.

These are easier to read than JSONL. They show:

- source
- record ID
- line numbers
- target speaker
- user prompt
- assistant target

You should inspect these before training.

## Important Extraction Scripts

### `scripts/extraction/build_full_dialogue_outputs.py`

This is the main rebuild script.

It does not contain much parsing logic itself. Instead, it calls other scripts in
the correct order.

It currently includes:

- older original-source rows from `build_pilot_dialogue_dataset.py`
- Gateless Gate rows
- Diamond Sutra rows
- Udana exclamation rows
- Sutta Nipata rows

The script regenerates those included source outputs before combining them.
Itivuttaka, Majjhima Nikaya, Vimalakirti Nirdesa Sutra, Zen Koans Database, and
Asclepius are also represented in the current final family datasets. Blue Cliff
Record, Dhammapada Commentary, and Udana direct-dialogue rows remain candidates.

### `scripts/extraction/mine_dialogue_candidates.py`

This is a helper script for finding useful dialogue regions.

It defines two important small data objects:

- `Turn`: one speaker's explicit turn
- `CueBlock`: a block of text near a phrase like "said", "asked", or "replied"

It also stores source-specific body line ranges. Those ranges help the scripts
ignore front matter, tables of contents, indexes, and other non-body text.

Use this script when you want to explore where dialogue might exist before
building final training rows.

### `scripts/extraction/preview_dialogue_examples.py`

This creates small preview files before building larger datasets.

It also contains shared rules used by other scripts:

- source labels
- system prompts
- target speakers
- participant mapping
- contamination markers
- helper functions like `select_spread`

`select_spread` chooses examples from across a list instead of only taking the
first examples. That makes review samples more representative.

### `scripts/extraction/build_pilot_dialogue_dataset.py`

Despite the word `pilot`, this script is part of the current full rebuild.

It builds rows from these older source files:

- `the_key-to-theosophy.txt`
- `The Corpus Hermeticum.txt`
- `Milinda Panha.txt`
- `Platform Sutra .txt`

It has three main row builders:

- `build_explicit_rows`
  Handles sources with clear speaker labels, like The Key to Theosophy and The
  Corpus Hermeticum.

- `build_buddhist_rows`
  Handles Milinda Panha dialogue found through speech-cue blocks.

- `build_platform_rows`
  Handles Platform Sutra dialogue using the dedicated Platform Sutra parser.

It also has shared cleanup functions like `clean_dataset_text` and
`count_dataset_words`.

### `scripts/extraction/platform_sutra_dialogue.py`

This is a custom parser for the Platform Sutra.

It looks for phrases like:

```text
The master said "..."
A monk asked "..."
```

Then it turns each quote into a `Turn` with:

- speaker
- start line
- end line
- text

The main dataset builder then uses those turns to create next-reply examples.

### `scripts/extraction/parse_gateless_gate.py`

This parser reads:

```text
source_texts/buddhist/gateless_gate_wikisource_raw.json
```

It extracts:

- the koan case
- Mumon's or Amban's comment
- the attached verse, when present

It creates two kinds of rows:

- `gateless_gate_koan_commentary`
- `gateless_gate_commentary_verse`

These rows are slightly different from normal conversation rows. The prompt asks
the model to write a comment or verse for a koan case.

### `scripts/extraction/parse_diamond_sutra.py`

This parser reads:

```text
source_texts/buddhist/diamond_sutra_gutenberg.txt
```

It finds attributed quotes from:

- Lord Buddha
- Subhuti

Then it builds next-reply rows where either speaker can be the target.

It creates rows with kinds like:

- `diamond_sutra_buddha_next_reply`
- `diamond_sutra_subhuti_next_reply`

### `scripts/extraction/parse_udana.py`

This parser reads:

```text
source_texts/buddhist/clean/udana.txt
```

It can build two kinds of rows:

- final inspired utterance rows
- direct reply rows from dialogue inside a section

It has more cleanup code than many other scripts because the PDF text contains
many extraction artifacts and speaker names.

The generated Udana files currently live in:

```text
review_outputs/new_buddhist_sources/
```

The full rebuild script reruns this parser for the
`udana_exclamation_dialogue.jsonl` output before combining the full dataset.

### `scripts/extraction/parse_itivuttaka.py`

This parser reads:

```text
source_texts/buddhist/clean/itivuttaka_thanissaro.txt
```

It extracts prose teaching sections and their attached verse summaries.

Its row kind is:

```text
itivuttaka_prose_to_verse
```

This is useful, but it is not the same as a normal back-and-forth conversation.
Itivuttaka rows are included in the current Buddhist final dataset.

### `src/ai_training_tests/`

This package is the new architecture spine. Shared modules are moving here while
old script paths stay available:

- `domain/dialogue_schema.py`: validates the three-message chat row schema.
- `domain/source_manifest.py`: tracks approved source families and output groups.
- `extraction/common/jsonl_io.py`: shared JSONL read/write helpers.
- `extraction/common/text_cleaning.py`: shared source-text cleanup helpers.
- `extraction/review/review_policy.py`: machine-review policy helpers.
- `extraction/parsers/asclepius.py`: first migrated source parser.

### `scripts/extraction/combine_dialogue_datasets.py`

This script joins JSONL files together.

It skips rows with duplicate `metadata.record_id` values.

### `scripts/extraction/split_dialogue_dataset.py`

This script writes the final training/evaluation files.

It knows which sources count as Buddhist and which count as esoteric.

Current Buddhist source names:

- `Milinda Panha`
- `Platform Sutra`
- `Itivuttaka`
- `Majjhima Nikaya`
- `The Gateless Gate`
- `The Diamond Sutra`
- `Udana`
- `Sutta Nipata`
- `Vimalakirti Nirdesa Sutra`
- `Zen Koans Database`

Current esoteric source names:

- `The Key to Theosophy`
- `The Corpus Hermeticum`
- `Asclepius`

`Asclepius` is included in the current occult / esoteric final dataset.

### `scripts/extraction/make_review_sample.py`

This creates small Markdown review files from a JSONL dataset.

It is for human checking, not model training.

## Data Prep Scripts

The scripts in `scripts/data_prep/` are supporting tools. They are mainly useful
for older Q&A datasets and LM Studio transcript datasets.

### `convert_dual_chat_transcript.py`

Takes a transcript JSON file from the Streamlit dual-chat app and turns it into
conversation-training JSONL.

It creates one row per target reply.

### `build_dual_model_chat_datasets.py`

Also converts a transcript, but writes:

- combined rows
- Participant A target rows
- Participant B target rows

It also filters out replies that look truncated or contain speaker-label bleed.

### `convert_jsonl_to_alpaca.py`

Converts old Q&A-style JSONL records into Alpaca format:

```json
{
  "instruction": "...",
  "input": "...",
  "output": "..."
}
```

This expects each input row to have `question` and `answer` fields.

### `build_mlx_dataset.py`

Converts Alpaca files into MLX-style prompt/completion files:

```json
{
  "prompt": "...",
  "completion": "..."
}
```

It also creates `train.jsonl` and `valid.jsonl`.

### `build_clean_training_pipeline.py`

This is an older combined cleaning pipeline.

It can:

- clean Q&A datasets
- convert Q&A records into chat messages
- convert transcript JSON files into dialogue examples
- build model-specific train/valid splits

Some old Q&A files that this script expects are not currently present in the
working tree, so treat this as a supporting or legacy path unless those inputs
are restored.

## Streamlit App

The app file is:

```text
scripts/apps/streamlit_lmstudio_dual_chat.py
```

It creates a browser UI for running two local LM Studio models in a timed
conversation.

The app does this:

1. Connects to LM Studio at `http://localhost:8000` by default.
2. Fetches the available local models.
3. Lets you choose a model and system prompt for Participant A.
4. Lets you choose a model and system prompt for Participant B.
5. Alternates turns between the two participants.
6. Displays the transcript.
7. Lets you download the transcript JSON.

The transcript JSON can later be converted into training examples with the
transcript conversion scripts.

## Source Folders

### `oritiginal text/`

This contains older source files used by the original extraction scripts.

The folder name is misspelled, but the scripts expect that exact spelling.

### `source_texts/buddhist/raw/`

This contains raw Buddhist PDFs.

### `source_texts/buddhist/clean/`

This contains text extracted from those PDFs.

The PDF-derived text is easier for Python to parse than PDF files directly.

### `source_texts/buddhist/SOURCES.md`

This explains where the Buddhist sources came from and includes license/status
notes.

## Output Folders

### `review_outputs/full_dialogue_dataset/`

This is the main output folder.

Important files:

```text
full_combined_dialogue_dataset_train.jsonl
full_combined_dialogue_dataset_eval.jsonl
full_buddhist_dialogue_dataset_train.jsonl
full_buddhist_dialogue_dataset_eval.jsonl
full_esoteric_dialogue_dataset_train.jsonl
full_esoteric_dialogue_dataset_eval.jsonl
```

### `review_outputs/new_buddhist_sources/`

This contains generated files for newer Buddhist parsers:

- Diamond Sutra
- Gateless Gate
- Udana
- Sutta Nipata
- Itivuttaka
- Blue Cliff Record
- Zen Koans Database

The full combined dataset currently includes Diamond Sutra, Gateless Gate, Udana
exclamation rows, and Sutta Nipata rows. Those included Buddhist outputs are
regenerated by the full rebuild script before combining.

### `Training Data/cleaned_pipeline/cleaned_dialogue/`

This contains small transcript-derived dialogue examples.

Current files:

```text
combined_messages.jsonl
participant_a_messages.jsonl
participant_b_messages.jsonl
```

## How To Add A New Source

A simple path for adding a new source is:

1. Put the raw source file somewhere under `source_texts/`.
2. If it is a PDF, extract it to plain text first.
3. Write a parser in `scripts/extraction/`.
4. Make the parser output JSONL rows with `messages` and `metadata`.
5. Make the parser also output a Markdown review sample.
6. Review the sample by hand.
7. If the rows look good, update `build_full_dialogue_outputs.py` so the new
   JSONL file is included in the combined dataset.
8. Update `split_dialogue_dataset.py` if the new source belongs in the Buddhist
   or esoteric split.

## How To Change Dataset Size Or Filters

Most extraction scripts expose command-line options.

Common options:

- `--min-target-words`
- `--max-target-words`
- `--history-turns`
- `--sample-count`
- `--preview-chars`

For example:

```bash
python scripts/extraction/parse_diamond_sutra.py --max-target-words 700
```

## What To Watch Out For

- Regular expressions are useful but imperfect. Always review samples.
- PDF text extraction can create broken words and strange characters.
- Some source files have copyright or reuse restrictions. Check
  `source_texts/buddhist/SOURCES.md` before using a source broadly.
- Paths like `Training Data/` and `oritiginal text/` need quotes in shell
  commands because they contain spaces.
- Generated JSONL files can be large and hard to read directly. Use the Markdown
  review files first.

## Quick Troubleshooting

If imports fail when running extraction scripts, run from the repository root and
use the compatibility entrypoint:

```bash
python scripts/extraction/build_full_dialogue_outputs.py
```

If the Streamlit app cannot find models, make sure LM Studio is running its local
server and that at least one chat model is loaded.

If a generated dataset has strange text, inspect the matching review sample and
then adjust the cleanup rules in the source-specific parser.
