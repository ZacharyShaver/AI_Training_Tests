# Platform Sutra Extraction Notes

- Source file: `Platform Sutra .txt`
- Extraction style: explicit or strongly inferable quoted dialogue only
- Excluded material: front matter, appendix, glossary, bibliography, index
- Speaker normalization: common recurring roles normalized to stable labels such as `Huineng`, `Hongren`, and `Prefect Wei`
- Confidence policy: `high` for explicit named attributions on both sides; `medium` when one side is section/pronoun inferred; `low` retained only in the full file

- Parsed turns: 109
- Q&A pairs: 43
- High-confidence pairs: 40

## Section Counts

- Number Eight: Sudden and Gradual: 9
- Number Nine: Proclamations: 1
- Number One: Account of Origins: 3
- Number Seven: Encounters: 28
- Number Three: Questions: 2

## Caveats

- Section One contains nested autobiographical dialogue inside Huineng's long speech; some pronoun-based turns remain conservative or are dropped.
- Quoted material embedded inside doctrinal exposition can still create medium-confidence pairings that should be reviewed before training.
- The strict file is the safest starting point for finetuning or supervised dialogue extraction.
