# Asclepius Q&A Extraction

This dataset was extracted from [Asclepius.txt](/Users/wewlad/GitHub/AI_Training_Tests/Asclepius.txt) into [asclepius_qa.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/asclepius_qa.jsonl).
The stricter subset is available at [asclepius_qa_high_confidence.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/asclepius_qa_high_confidence.jsonl).

## What was extracted

- Only the translation section was parsed; introduction, notes, bibliography, and index were excluded.
- Dialogue turns were extracted from quoted speech.
- Speakers were inferred conservatively from local cues such as `O Trismegistus`, `O Asclepius`, and nearby narration like `Trismegistus said`.
- Each record contains `section`, `questioner`, `answerer`, `question`, `answer`, `source_lines`, and a heuristic `confidence`.

## Caveats

- This text uses fewer explicit speaker labels than the Corpus file, so speaker attribution is partly inferred.
- High-confidence pairs are those where both speaker assignments came from strong local cues.
- Medium-confidence pairs are still plausible, but they rely more on alternation and discourse context.
- Narrative exposition between exchanges was not converted into synthetic Q&A.

## Pair counts

- Total pairs: `21`
- High-confidence pairs: `4`

## Section counts

- Section `2`: 2 pairs
- Section `7`: 2 pairs
- Section `16`: 1 pairs
- Section `18`: 1 pairs
- Section `19`: 1 pairs
- Section `20`: 1 pairs
- Section `21`: 1 pairs
- Section `24`: 2 pairs
- Section `25`: 1 pairs
- Section `26`: 1 pairs
- Section `27`: 2 pairs
- Section `28`: 1 pairs
- Section `29`: 1 pairs
- Section `36`: 1 pairs
- Section `38`: 1 pairs
- Section `39`: 1 pairs
- Section `41`: 1 pairs
