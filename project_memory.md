# Project Memory

## Goal

Build clean training data from philosophical and spiritual source texts, then prepare it for local model training.

## Workspace Structure

- Original source texts are in `/Users/wewlad/GitHub/AI_Training_Tests/oritiginal text/`
- Current canonical generated datasets are in `/Users/wewlad/GitHub/AI_Training_Tests/review_outputs/full_dialogue_dataset/`
- Older transcript and legacy cleaning artifacts are in `/Users/wewlad/GitHub/AI_Training_Tests/Training Data/`

## Current Dataset State

- Active training format is direct-source dialogue: `conversation so far -> next reply`.
- Current full combined dataset has 862 rows: 779 train and 83 eval.
- Current Buddhist split has 464 rows.
- Current esoteric split has 398 rows.
- The full dataset currently includes The Key to Theosophy, The Corpus Hermeticum, Milinda Panha, Platform Sutra, The Gateless Gate, The Diamond Sutra, Udana, and Sutta Nipata.
- The main rebuild script regenerates the included source outputs before combining datasets.

## Historical Q&A Corpora

Earlier project notes referred to Q&A files such as:

- `corpus_hermeticum_qa.jsonl`
- `asclepius_qa.jsonl`
- `milinda_panha_qa.jsonl`
- `platform_sutra_qa.jsonl`
- `key_to_theosophy_qa.jsonl`

Those files are not currently present as active `Training Data/*_qa.jsonl`
inputs in the workspace. The older Q&A pipeline remains useful if those files
are restored, but the current canonical outputs are the direct-source dialogue
splits in `review_outputs/full_dialogue_dataset/`.

## Important Lessons

- Clean data matters more than raw volume.
- Footnotes, page headers, OCR bleed, and commentary contamination are common failure modes.
- `The Key to Theosophy` is structurally one of the cleanest dialogue corpora because it uses explicit speaker prefixes like `ENQUIRER.` and `THEOSOPHIST.`
- `Platform Sutra` required conservative extraction because of nested quotations and narrative framing.
- `Milinda Panha` is useful but still has some medium-confidence edge cases and commentary contamination in weaker records.

## Training Data Conventions

- Preferred current core training format is direct-source `conversation so far -> next reply` JSONL.
- Clean `question -> answer` JSONL remains useful if the older Q&A corpora are restored.
- Dialogue transcripts should be treated as `conversation so far -> next reply`, not as ordinary Q&A.
- Dual-chat transcripts are better as a secondary style dataset, not the main corpus.
- Recommended near-term path: validate and train against the direct-source dialogue splits first, then decide whether restored Q&A data should be mixed in.

## Scripts Added

- `scripts/apps/streamlit_lmstudio_dual_chat.py`
  Streamlit app for dual-model local conversations via LM Studio.
- `scripts/data_prep/convert_dual_chat_transcript.py`
  Converts LM Studio dual-chat transcript JSON into conversation-training JSONL.
- `scripts/extraction/build_full_dialogue_outputs.py`
  Main current rebuild command for the full direct-source dialogue dataset.
- Source-specific parsers live under `scripts/extraction/`.

## Dual Chat Transcript Notes

- Transcript file: `Training Data/Test Conversations/lmstudio_dual_chat_transcript.json`
- It contained 8 total messages, 4 from each participant, using model id `hermes_sage`
- Main theme: reasoning, self-awareness, detachment, intuition, and wisdom
- Transcript quality was only moderate; several turns looked truncated
- Converted conversation-training file exists:
  `Training Data/Test Conversations/lmstudio_dual_chat_conversation_training_generated.jsonl`

## Current Reusable Local Training Assets

- `Training Data/cleaned_pipeline/cleaned_dialogue/combined_messages.jsonl`
  Small transcript-derived next-turn conversation examples
- `scripts/data_prep/convert_dual_chat_transcript.py`
  Reusable converter for future dual-chat transcripts

## Local Training Recommendation

- Prefer local LoRA/QLoRA over full fine-tuning for small datasets and limited hardware.
- Use the direct-source combined, Buddhist-only, and esoteric-only splits as the first training candidates.
- Use transcript-derived dual-chat data only as a supplemental style set.
