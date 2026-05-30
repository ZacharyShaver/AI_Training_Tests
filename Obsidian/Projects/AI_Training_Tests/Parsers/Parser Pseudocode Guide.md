# Parser Pseudocode Guide

## Status

active

## Purpose

This note explains the parser family in plain language. It is not executable
code. Use it as a beginner-friendly map before reading `scripts/extraction/` or
the parser-specific notes.

## The Basic Parser Recipe

Most parsers in this repo do the same job:

```text
open one source text
remove obvious junk like headers, footnotes, page noise, or web boilerplate
split the source into sensible chunks
find speaker turns, teaching blocks, cases, verses, or quoted replies
choose one turn as the assistant's target reply
put earlier source material into "Conversation so far"
save the row as a three-message chat record
write metadata so reviewers can trace the row back to the source
write JSONL output and usually a small markdown review sample
```

The final row shape comes from the training data style guide:

```text
system message: short instruction for the model
user message: conversation so far, with Participant A / Participant B labels
assistant message: the next source-grounded reply only
metadata: source, source file, source lines, target speaker, target words
```

## Common Helpers In Plain English

```text
clean_text(text):
  fix spacing
  remove repeated page headers or OCR junk
  remove footnote markers when they are not part of the dialogue
  return readable source text
```

```text
parse_turns(source):
  scan the source for places where someone speaks
  normalize speaker names
  ignore speakers that are too vague or obviously wrong
  keep the spoken words and source location
  return a list of turns
```

```text
build_rows(turns):
  walk through the turns in order
  pick a later turn as the answer
  use nearby earlier turns as context
  convert speaker names into Participant A / Participant B labels
  create the system, user, and assistant messages
  add source metadata
  skip rows that are too short, too messy, or not clearly connected
```

```text
write_outputs(rows):
  save every row to a JSONL file
  save a small markdown preview for human review
  print row counts so the operator can tell what happened
```

## Parser By Parser

### [[base_dialogue_dataset]]

Code: `scripts/extraction/build_pilot_dialogue_dataset.py`

This is the older multi-source builder for Milinda Panha, Platform Sutra, The
Corpus Hermeticum, and The Key to Theosophy.

```text
load the legacy source files from "oritiginal text"
for sources with obvious speaker labels:
  split the text at speaker labels
  keep each speaker's words as a turn
for sources with less obvious dialogue:
  look for quoted speech and nearby cue words
  decide who is probably speaking
for each usable exchange:
  build "Conversation so far" from earlier turns
  make the next turn the assistant answer
  attach source and line metadata
save the combined rows into the full dialogue dataset
```

### Platform Sutra Helper

Code: `scripts/extraction/platform_sutra_dialogue.py`

```text
read the Platform Sutra source
ignore lines outside the known body range
look for quoted speech
look near each quote for speaker labels like Master or Prefect
normalize the speaker names
merge adjacent turns from the same speaker
print or return the cleaner turn list
```

### [[parse_itivuttaka]]

Code: `scripts/extraction/parse_itivuttaka.py`

```text
load the cleaned Itivuttaka text
split it into numbered teaching items
for each item:
  separate the prose setup from the verse response
  clean both parts
  skip items where the target verse is too short or too long
  make the prose the conversation context
  make the verse the assistant's next reply
  save source lines covering the full item
write JSONL rows and a review sample
```

### [[parse_majjhima_nikaya]]

Code: `scripts/extraction/parse_majjhima_nikaya.py`

```text
read selected Majjhima Nikaya pages or cached HTML
turn the HTML into clean text blocks
scan each block for reporting patterns like "X said to Y"
normalize speaker names
reject fake speakers, group speakers, and broken labels
build local exchange windows around real speaker turns
for each usable target turn:
  include enough nearby context so the reply makes sense
  avoid cross-scene jumps
  create a three-message chat row
save candidate rows and review artifacts
```

### [[parse_sutta_nipata]]

Code: `scripts/extraction/parse_sutta_nipata.py`

```text
load the cleaned Sutta Nipata text
start at the real body of the book and stop before glossary/table material
split the text into sections
inside each section:
  detect speaker labels and quoted teaching passages
  clean verse and prose lines
  map source speakers to Participant A / Participant B
  target the Buddha or Buddha Kassapa replies
  skip rows without enough non-target context
write final dialogue rows and a review sample
```

### [[parse_diamond_sutra]]

Code: `scripts/extraction/parse_diamond_sutra.py`

```text
load the Project Gutenberg source
throw away Gutenberg header and footer material
scan the main body for quoted speech
infer whether the speaker is the Buddha, Subhuti, or another attributed voice
keep turns that look like real direct discourse
for each target reply:
  use earlier nearby turns as the prompt context
  keep the target reply as the assistant message
  record source lines
write JSONL rows and a review sample
```

### [[parse_gateless_gate]]

Code: `scripts/extraction/parse_gateless_gate.py`

```text
load the raw Wikisource JSON
clean wiki markup and repeated lines
split the source into koan cases
for each case:
  keep the case number and title
  separate the case, comment, and verse parts
  create main rows from case material into comment or verse responses
  optionally extract internal quoted dialogue as separate candidate rows
write final rows separately from internal-dialogue candidates
```

### [[parse_udana]]

Code: `scripts/extraction/parse_udana.py`

The final output uses inspired utterance rows. The direct-dialogue output is a
separate candidate family.

```text
load the cleaned Udana text
split it into source blocks
for final exclamation rows:
  find the narrative setup
  find the inspired utterance target
  clean both pieces
  make the narrative the prompt context
  make the utterance the assistant reply
for candidate direct-dialogue rows:
  find quoted speech inside the block
  infer each quote's speaker from nearby narration
  build local dialogue history
  skip rows with unclear speakers or dirty context
write exclamation rows and direct-dialogue rows as separate outputs
```

### [[parse_vimalakirti]]

Code: `scripts/extraction/parse_vimalakirti.py`

```text
load the cleaned Vimalakirti text
split it into paragraphs
look for paragraphs that contain attributed speech
normalize speaker names
reject pronouns, incomplete fragments, and vague speakers
walk through the turn list
for each possible target reply:
  build an adaptive nearby context window
  check that the history and target belong together
  skip rows that jump scenes or contain broken quotes
write the small approved row pool and review artifacts
```

### [[parse_zen_koans_database]]

Code: `scripts/extraction/parse_zen_koans_database.py`

```text
read the Zen Koans list page
for each story link:
  use the cached page if it exists
  otherwise download and cache the page
  parse the story title and paragraphs
  save a clean JSON version for reproducibility
for each story:
  find quoted speech and named speakers
  infer simple pronoun references when safe
  reject unreliable speakers like "Another" or "Other"
  create one-row story summaries and named-dialogue rows
clean the row list
write the canonical clean dialogue JSONL
```

### [[parse_asclepius]]

Code: `src/ai_training_tests/extraction/parsers/asclepius.py`
Wrapper: `scripts/extraction/parse_asclepius.py`

```text
load the Asclepius text
split the text into paragraphs with line numbers
find attributed turns between Hermes and Asclepius
infer the speaker when the text gives enough evidence
walk through the turns
for each target turn:
  use the recent previous turns as conversation history
  require history that makes the target reply understandable
  write the row with source line metadata
save JSONL and markdown preview files
```

### [[parse_blue_cliff_record]]

Code: `scripts/extraction/parse_blue_cliff_record.py`

This parser is candidate-only and produces more than one row family.

```text
load the Blue Cliff Record HTML
convert HTML into plain text
split the text into numbered cases
for each case:
  keep case number and title
  separate case text, commentary-style material, and verse/ode material
  build dialogue rows from clear exchanges
  build ode rows from case-to-ode relationships
  build internal-dialogue candidate rows from quoted speech inside the case
write each row family to its own output file
keep all Blue Cliff outputs out of final data until reviewed
```

### [[parse_dhammapada_commentary]]

Code: `scripts/extraction/parse_dhammapada_commentary.py`

```text
load the cleaned commentary text
split it into paragraphs with source line numbers
start only after the real story section begins
inside each paragraph:
  look for speaker phrases before or after quoted speech
  normalize common speaker names
  reject unusable speakers and weak dialogue
build rows from local turn history into the next reply
write candidate output and review samples
do not treat the existing sample as final approval
```

## How To Read A Parser File

When a parser feels complicated, read it in this order:

```text
1. find DEFAULT_SOURCE and DEFAULT_OUTPUT_DIR
2. find the small data classes near the top
3. read the clean_* functions
4. read parse_* functions to see how source material becomes turns/items/cases
5. read build_* or *_to_row functions to see how rows are made
6. read main() last to see what files get written
```

## Review Reminder

```text
generated rows are candidates until reviewed
a clean sample is not the same as final approval
candidate outputs should not be promoted without manifest, dashboard, and vault updates
```

## Links

- [[Parser Hub]]
- [[../Datasets/Training Data Style Guide]]
- [[../Pipelines/New Parser Review Pipeline]]
