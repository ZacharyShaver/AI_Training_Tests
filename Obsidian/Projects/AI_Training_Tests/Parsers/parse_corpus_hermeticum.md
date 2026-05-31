# parse_corpus_hermeticum

## Status

final — **APPROVED 2026-05-31**

## Source

The Corpus Hermeticum (GRS Mead translation). 13 tractates: Poemandres,
To Asclepius, The Sacred Sermon, The Cup or Monad, etc.
Source file already on disk from original pilot dataset.

- Source file: `oritiginal text/The Corpus Hermeticum.txt`
- Parser: `src/ai_training_tests/extraction/parsers/corpus_hermeticum.py`
- Wrapper: `scripts/extraction/parse_corpus_hermeticum.py`
- Pass history: `review_outputs/parser_reviews/parse_corpus_hermeticum_v2/pass_history.md`

## Format

H:/Hermes:, A:/Asclepius:, T:/Tat:, Mind:, Pimander: at line-start.
118 speaker turns (66 Hermes). Body: lines 400–2900.
Target: Hermes or Mind (the teacher). Participant B.

## Rows

44 rows. Supplements original 28 rows from build_pilot_dialogue_dataset.py.
