# Corpus Hermeticum Q&A Extraction

This dataset was extracted from `The Corpus Hermeticum.txt` into [corpus_hermeticum_qa.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/corpus_hermeticum_qa.jsonl).
The stricter subset is available at [corpus_hermeticum_qa_high_confidence.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/corpus_hermeticum_qa_high_confidence.jsonl).

## What was extracted

- Explicit dialogue turns only.
- Speaker labels were normalized, including `H` -> `Hermes`, `A` -> `Asclepius`, and `Trismegistus` -> `Hermes`.
- Each JSONL record contains `book`, `translation`, `questioner`, `answerer`, `question`, `answer`, `source_lines`, and a heuristic `confidence`.
- `high` confidence means the question turn ends with an explicit question mark and the following turn is a different named speaker in the same book.
- `medium` confidence means the pairing still looked plausible, but the local turn boundary was less explicit.

## Important caveats

- The source file contains at least two translation families: Mead-style Roman numeral books and Everard-style `The Ninth Book...` headings.
- Those translations overlap in content, so they were tagged separately instead of merged. This helps prevent accidental duplicate training examples.
- Narrative-only stretches were intentionally excluded. They should be handled as a second dataset, such as `instruction -> exposition` or `topic -> passage summary`, rather than forced into fake Q&A.

## Recommended training strategy

- Use the JSONL file as a clean `question -> answer` subset.
- Prefer the high-confidence JSONL for first-pass training.
- Deduplicate across translations before fine-tuning if you want a single canonical answer set.
- Keep `translation` as metadata if stylistic variation is useful.
- For the non-dialogue material, create a separate corpus with fields like `book`, `theme`, `passage`, and `summary` rather than mixing it with direct Q&A.

## Pair counts

- Total pairs: `51`
- High-confidence pairs: `42`
- Mead pairs: `17`
- Everard pairs: `34`

## Most dialogue-heavy sections

- `The Ninth Book. A Universal Sermon To Asclepius`: 12 pairs
- `XIII. The Secret Sermon on the Mountain`: 8 pairs
- `The Seventh Book. His Secret Sermon in the Mount Of Regeneration, and the Profession of Silence`: 6 pairs
- `The Fifteenth Book. Of Truth to His Son Tat`: 5 pairs
- `X. The Key`: 4 pairs
- `XII. About The Common Mind`: 4 pairs
- `The Eleventh Book. Of the Common Mind to Tat`: 3 pairs
- `The Third Book. Called "The Holy Sermon."`: 3 pairs
- `The Fourteenth Book. Of Operation and Sense`: 2 pairs
- `The Second Book. Called "Poemander."`: 2 pairs
- `The Twelfth Book. His Crater or Monas`: 1 pairs
- `XI. Mind Unto Hermes`: 1 pairs
