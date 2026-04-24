# Project Memory

## Goal

Build clean training data from philosophical and spiritual source texts, then prepare it for local model training.

## Workspace Structure

- Original source texts are in `/Users/wewlad/GitHub/AI_Training_Tests/oritiginal text/`
- Most generated training data and helper scripts are in `/Users/wewlad/GitHub/AI_Training_Tests/Training Data/`

## Extracted Corpora

- `corpus_hermeticum_qa.jsonl` and strict subset exist
- `asclepius_qa.jsonl` and strict subset exist
- `milinda_panha_qa.jsonl` and strict subset exist
- `platform_sutra_qa.jsonl` and strict subset exist
- `key_to_theosophy_qa.jsonl` and strict subset exist

## Important Lessons

- Clean data matters more than raw volume.
- Footnotes, page headers, OCR bleed, and commentary contamination are common failure modes.
- `The Key to Theosophy` is structurally one of the cleanest dialogue corpora because it uses explicit speaker prefixes like `ENQUIRER.` and `THEOSOPHIST.`
- `Platform Sutra` required conservative extraction because of nested quotations and narrative framing.
- `Milinda Panha` is useful but still has some medium-confidence edge cases and commentary contamination in weaker records.

## Training Data Conventions

- Preferred core training format is clean `question -> answer` JSONL.
- Dialogue transcripts should be treated as `conversation so far -> next reply`, not as ordinary Q&A.
- Dual-chat transcripts are better as a secondary style dataset, not the main corpus.
- Recommended mix: mostly doctrinal/Q&A data, with a smaller amount of dialogue-continuation data.

## Scripts Added

- `Training Data/streamlit_lmstudio_dual_chat.py`
  Streamlit app for dual-model local conversations via LM Studio.
- `Training Data/convert_dual_chat_transcript.py`
  Converts LM Studio dual-chat transcript JSON into conversation-training JSONL.
- `extract_key_to_theosophy_qa.py`
  Extracts explicit `Enquirer/Theosophist` dialogue into training-ready JSONL.
- Other extractor scripts exist for Hermeticum, Asclepius, Milinda Panha, and Platform Sutra.

## Dual Chat Transcript Notes

- Transcript file: `Training Data/lmstudio_dual_chat_transcript.json`
- It contained 8 total messages, 4 from each participant, using model id `hermes_sage`
- Main theme: reasoning, self-awareness, detachment, intuition, and wisdom
- Transcript quality was only moderate; several turns looked truncated
- Converted conversation-training file exists:
  `Training Data/lmstudio_dual_chat_conversation_training.jsonl`

## Current Reusable Local Training Assets

- `Training Data/lmstudio_dual_chat_conversation_training.jsonl`
  Hand-shaped next-turn conversation training examples from current transcript
- `Training Data/convert_dual_chat_transcript.py`
  Reusable converter for future dual-chat transcripts

## Local Training Recommendation

- Prefer local LoRA/QLoRA over full fine-tuning for small datasets and limited hardware.
- Use Q&A corpora as the primary training set.
- Use dialogue-continuation data only as a supplemental style set.

