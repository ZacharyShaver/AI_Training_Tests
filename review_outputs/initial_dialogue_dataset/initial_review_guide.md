# Initial Dialogue Dataset Review Guide

Use this guide while reviewing `initial_dialogue_dataset_review.md`.
Prefer citing the `Record ID` when you mark an item; example numbers can shift
after parser fixes.

## Mark Each Item

- `KEEP`: Correct speaker, readable context, complete target, useful doctrine or reasoning.
- `FIX`: Good source material, but needs cleanup, shorter context, better turn boundary, or different previous turns.
- `DROP`: Wrong target speaker, confusing context, broken extraction, weak training value, or unwanted tone.

## What Makes A Good Item

1. The assistant target is the voice we want to train.
2. The prompt gives enough prior dialogue to make the reply understandable.
3. The target is a complete answer, not a fragment or a clipped passage.
4. The row teaches useful reasoning, doctrine, metaphor, debate style, or vocabulary.
5. The text is mechanically clean: no page marks, footnote debris, broken line hyphens, or missing spaces.
6. The tone is worth teaching. Defensive or sectarian rows should be rare and intentional.
7. The set stays balanced across sources and topics.

## Suggested Review Notes

When an item needs work, write the problem in one short phrase:

- `wrong speaker`
- `not enough context`
- `target too long`
- `target too short`
- `narrative in prompt`
- `OCR cleanup`
- `bad tone`
- `too narrow`
- `strong but lower priority`
