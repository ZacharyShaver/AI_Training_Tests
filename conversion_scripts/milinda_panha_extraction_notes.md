# Milinda Panha Q&A Extraction

This dataset was extracted from [Milinda Panha.txt](/Users/wewlad/GitHub/AI_Training_Tests/Milinda%20Panha.txt) into [milinda_panha_qa.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/milinda_panha_qa.jsonl).
The stricter subset is available at [milinda_panha_qa_high_confidence.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/milinda_panha_qa_high_confidence.jsonl).

## What was extracted

- Extraction starts at `PART I: PAST HISTORY` and stops before the index.
- Dialogue turns were parsed from quoted speech blocks.
- Speakers were taken from explicit narration where possible, such as `King Milinda said` and `Venerable Nāgasena replied`.
- In the question sections, local Milinda-Nagasena alternation was used only when the surrounding context clearly stayed inside that exchange.

## Caveats

- High-confidence pairs use explicit speaker attribution on both sides.
- Medium-confidence pairs use one or more local alternation inferences inside a clearly established section dialogue.
- The file is an abridged edition with editorial front matter and notes, so only the main body was parsed.
- Some longer answers contain nested rhetorical questions; those were kept as part of the answer text rather than split further.

## Pair counts

- Total pairs: `298`
- High-confidence pairs: `44`

## Part counts

- `PART II: Questions on Distinguishing Marks`: 110 pairs
- `PART III: Questions for the Cutting Off of Perplexity`: 169 pairs
- `PART V: A Question Solved by Inference`: 19 pairs

## Most dialogue-heavy sections

- `34. Is There This Element of Nibbāna?`: 23 pairs
- `25. Seeing and Thinking`: 17 pairs
- `1. No Person is Found`: 14 pairs
- `20. What Are You Striving For?`: 13 pairs
- `22. Why Only One Buddha at a Time?`: 10 pairs
- `30. The Transference of Merit`: 9 pairs
- `29. What Is Not Born of a Cause?`: 8 pairs
- `15. Knowledge and Wisdom`: 7 pairs
- `24. No Experiencer is Found`: 7 pairs
- `2. The Speech of the Learned`: 6 pairs
- `25. Arahats and the Body`: 6 pairs
- `26. If a Householder Attains Arahatship`: 6 pairs
- `32. Nibbāna is Entirely Blissful`: 6 pairs
- `13. Is the Body Dear to Monks?`: 5 pairs
- `17. The Quality of Feelings`: 5 pairs
- `18. Memory`: 5 pairs
- `18. Who Takes Rebirth?`: 5 pairs
- `21. The Speed of Rebirth`: 5 pairs
- `22. Distance Makes No Difference`: 5 pairs
- `9. Transmigration and Rebirth`: 5 pairs
