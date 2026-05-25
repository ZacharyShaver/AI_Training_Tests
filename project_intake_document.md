# Project Intake Document

## Project Summary

This project is a local AI dialogue system built around two philosophical agents
that converse with each other in a bounded session. The current repository now
centers on a direct-source dialogue dataset, with transcript conversion scripts,
a legacy data cleaning pipeline, and a Streamlit prototype that runs alternating
conversation turns through LM Studio.

The intended direction is to evolve from a prototype chat interface into a more complete website experience while keeping model quality and data quality as the primary technical priority.

## Current Repository State

- The current canonical training outputs live in
  `review_outputs/full_dialogue_dataset/`.
- Current generated full dataset counts:
  - Combined: `862` rows, `779` train, `83` eval
  - Buddhist: `464` rows, `420` train, `44` eval
  - Esoteric: `398` rows, `359` train, `39` eval
- Current included source corpora:
  - The Key to Theosophy
  - Corpus Hermeticum
  - Milinda Panha
  - Platform Sutra
  - The Gateless Gate
  - The Diamond Sutra
  - Udana
  - Sutta Nipata
- The repository includes:
  - Direct-source dialogue JSONL outputs
  - Markdown review samples
  - Transcript-based dual-chat examples
  - A legacy cleaning pipeline for older Q&A/transcript data
- Current interactive prototype:
  - Streamlit frontend
  - LM Studio OpenAI-compatible endpoint for inference

## Models & Training

### 1. Base Models Under Consideration

The project direction suggests small local instruction/chat-capable base models rather than very large models. The test transcript used `hermes_sage`, but the repository does not lock the system to one exact base. The practical range appears to be closer to `7B–8B` class models than `70B`.

### 2. Hardware Constraints

No explicit hardware profile is documented in the repository. The project memory recommends local LoRA/QLoRA on limited hardware, which implies a modest local setup rather than large multi-GPU full fine-tuning infrastructure.

### 3. Training Data Status

Training data is prepared at the dataset level, but the project has not yet
recorded completed fine-tuning runs or adapters. The active training-ready data
is the direct-source dialogue dataset under `review_outputs/full_dialogue_dataset/`.
The older Q&A cleaning pipeline remains in `scripts/data_prep/`, but its original
`Training Data/*_qa.jsonl` inputs are not currently present in the workspace.

### 4. Training Method

The intended method is local fine-tuning via `LoRA/QLoRA`, not full fine-tuning. This is explicitly consistent with the project notes and with the current scale of the dataset.

## The Two Personas

### 5. Persona Roles

The current design uses two distinct conversational roles:

- `Participant A`: reason carefully, respond directly, stay coherent
- `Participant B`: build on the prior point, challenge weak reasoning politely

This is not yet framed as a student/teacher pattern. It is closer to two interlocutors with different conversational tendencies.

### 6. Tradition Grounding

The project is currently grounded in a blend of traditions rather than one single lineage. The corpus spans Buddhist, Hermetic, and Theosophical texts.

- Buddhist:
  - Milinda Panha
  - Platform Sutra
  - The Gateless Gate
  - The Diamond Sutra
  - Udana
  - Sutta Nipata
- Hermetic / Theosophical:
  - Corpus Hermeticum
  - The Key to Theosophy

### 7. Names / Identities

At present the agents remain anonymous and are labeled as `Participant A` and `Participant B`. No named identities are currently defined in the repository.

## Conversation Flow

### 8. Triggering Conversations

The current application uses user-triggered sessions. Conversations do not run as an autonomous always-on stream.

### 9. Conversation Length

The current system uses bounded sessions controlled by duration and/or max-turn count. It is not set up for infinite back-and-forth.

### 10. Topic Seeding

The current conversation runner already supports a seeded topic. The best long-term design is likely both:

- free-form user topics
- curated themes drawn from the corpus

## Website / Product Direction

### 11. Frontend Stack

The current implementation uses `Streamlit`. There is no evidence in the repository of a separate React/Vue frontend yet.

### 12. Intended Audience

The repository reads as a prototype or research project rather than a production public deployment. The likely current audience is personal use or small-scale testing.

### 13. Visual Direction

The current interface uses alternating chat bubbles and a warm parchment-like aesthetic. No fully developed visual system exists yet, but the current direction is calm, contemplative, and minimal rather than flashy.

## Evolving Beyond Streamlit

### 14. Streamlit vs Proper Web App

The repo currently uses Streamlit effectively as a prototype, but the language around building a “website” suggests a proper web app is the likely long-term destination.

Streamlit remains acceptable for experimentation and internal testing, but it is probably not the final product direction if polish and public accessibility matter.

### 15. Backend Preference

No explicit backend preference is documented. Because the current tooling is already Python-based, `FastAPI` would be the most natural backend if the project moves to a standard web stack.

### 16. Hosting Direction

No explicit hosting plan is documented. The current setup implies local or same-machine hosting during development, with inference running through local model infrastructure.

## Model Strategy

### 17. One Shared Model or Two Fine-Tuned Models

The project has already moved toward `two separate fine-tuned models`, not one single shared model with different prompts. This is reflected in the cleaned pipeline, which emits separate `model_a` and `model_b` datasets.

### 18. Training Run Status

There is no evidence in the repository of completed fine-tuning runs or saved adapters/checkpoints. The present state is:

- data prepared
- data cleaned
- train/valid splits built
- training not yet evidenced in-repo

### 19. Current Inference Stack

Current inference is run through `LM Studio` using its OpenAI-compatible API endpoint.

## Conversation Design Evolution

### 20. Persona Differentiation

The current roles are only lightly differentiated. A stronger next step would be to evolve them into more distinct archetypes, for example:

- one agent more grounded in Buddhist dialogue texts
- one agent more grounded in Hermetic / Theosophical texts

That would create a more distinct cross-tradition dialogue and reduce role collapse.

### 21. Topic Input Design

The best fit is likely:

- free-form topic entry
- curated themes such as impermanence, mind, selfhood, wisdom, intuition, karma, the One, or awakening

### 22. Session Length Control

User-controlled bounded sessions are the best fit for the current architecture, with a reasonable default turn limit.

## Look and Feel

### 23. Message Presentation

The current design is closest to a messaging interface:

- left/right aligned bubbles
- alternating speakers
- not a forum or transcript-heavy layout

### 24. Aesthetic Direction

The current parchment/warm contemplative look should be treated as the active visual baseline unless deliberately changed.

### 25. Ambient Elements

No ambient sound or immersive effects are present. The current direction is subtle background atmosphere with an otherwise clean interface.

## Scope and Priority

### 26. Primary Priority

Based on the repository, the dominant priority is model and data quality rather than frontend polish. Most of the substantial work so far has gone into:

- extraction
- cleaning
- formatting
- transcript conversion
- role-separated dataset preparation

### 27. Project Pace

This appears to be a longer-term incremental build rather than a one-week launch project. The training side is still in the preparation/prototyping stage.

## Recommended Immediate Next Steps

1. Run the full dialogue rebuild and validation pass before training.
2. Keep the lightweight validation command focused on JSONL shape, duplicate record IDs,
   source counts, target length buckets, and train/eval overlap.
3. Review short-target records and license-sensitive sources before training.
4. Run small LoRA/QLoRA experiments against combined, Buddhist-only, and
   esoteric-only splits.
5. Keep Streamlit for short-term testing, but plan a later migration to a proper
   web frontend plus Python backend if public deployment is the goal.

## Key Project Artifacts

- Intake source notes: [project_memory.md](/Users/wewlad/GitHub/AI_Training_Tests/project_memory.md)
- Streamlit prototype: [streamlit_lmstudio_dual_chat.py](/Users/wewlad/GitHub/AI_Training_Tests/scripts/apps/streamlit_lmstudio_dual_chat.py)
- Dual-model transcript converter: [build_dual_model_chat_datasets.py](/Users/wewlad/GitHub/AI_Training_Tests/scripts/data_prep/build_dual_model_chat_datasets.py)
- Full cleaning pipeline: [build_clean_training_pipeline.py](/Users/wewlad/GitHub/AI_Training_Tests/scripts/data_prep/build_clean_training_pipeline.py)
- Cleaned output summary: [summary.json](/Users/wewlad/GitHub/AI_Training_Tests/Training%20Data/cleaned_pipeline/summary.json)
