# Conversation + Memory Harness Design

## Goal

Stand up a harness that lets the project's fine-tuned models hold a
*continuously running conversation* with durable memory, instead of being
limited to one-shot replies in the LM Studio chat UI.

Concretely:

- two separate persona models (Buddhist, Occult) carry on a conversation,
  either with a human or with each other
- the conversation is watched live in a dedicated web chat UI, ticking back
  and forth, **not** in the LM Studio UI
- the conversation survives past the model's effective context window via
  compaction
- the system retrieves relevant source passages and prior learnings and
  injects them into context before each reply
- learnings are written to a human-readable, auditable memory store
- the design degrades gracefully on the current 3B models and upgrades
  cleanly to a larger tool-capable model later

The **first deliverable (phase 1 MVP)** is narrow and concrete: the web chat
UI, with the orchestrator behind it, showing the two persona models going back
and forth live. That milestone is a decision point — watch the exchange, make
further fine-tuning decisions, or proceed to the next phase. Everything beyond
phase 1 (compaction, RAG, memory, tools) follows only after the web chat is
visibly working.

**Status as of 2026-05-31:** phase 1 is built. The web chat UI was found in
the repo at `scripts/apps/streamlit_lmstudio_dual_chat.py` (a Streamlit
dual-model app that was already there — no rebuild needed). Changes made:
`streamlit` added as an `app` extra in `pyproject.toml`; default base URL
updated to `http://192.168.21.1:45`; token streaming added (replies tick in
live with a "typing…" cursor). Served at `http://localhost:8501`. LM Studio
server at `http://192.168.21.1:45` has `buddhist-llama3b` on the shelf;
`text-embedding-nomic-embed-text-v1.5` and several large models (Qwen,
Hermes-4-70B) are available for later phases. The occult persona was still
training as of this date and is not yet exported to GGUF. Phases 2–5 remain
design-only and are deferred until the phase-1 decision point is passed.

## Background And Current State

Today the project produces three-message dialogue training rows and LoRA
fine-tunes `meta-llama/Llama-3.2-3B-Instruct`, exporting GGUF for LM Studio.
There are two persona adapters in active use:

- `models/lora_adapters/buddhist_llama3b`
- `models/lora_adapters/occult_llama3b`

The fine-tunes shape *voice and content* of a single reply. They do not add
memory, persistence, long-conversation tracking, or tool use. Those are
properties of the harness around the model, not of the weights. The LM Studio
chat UI offers no control over context assembly and silently truncates old
turns, so long conversations lose their early state. For that reason LM Studio
is used here **only as a headless backend** (server mode), never as the
viewing surface.

A small dedicated web chat UI for watching these models converse was built in
a previous effort. It lives outside this repo and may no longer be locatable.
It is simple enough to recreate if it cannot be found, and recreating or
restoring it is the core of phase 1. The intent is to see the conversation
tick back and forth in that web UI, with the orchestration working behind it.

## Design Principles

- The model is a stateless reply generator. All state lives in the harness.
- The orchestrator is code, not a model. It routes text, counts tokens, and
  calls models; it does not "think."
- Separate jobs from weights. Three model *roles* exist; they may or may not
  share weights.
- Spend the context window deliberately. On a 3B model, coherence degrades
  long before the nominal limit, so a tight, prioritized token budget matters
  more than raw window size.
- Keep canon and invented memory in separate stores so hallucinated notes can
  never be confused with source text.
- The memory store is human-readable and auditable; the vector index is a
  derived artifact that can be rebuilt from it at any time.
- Memory writes are narrow, structured, and validated. Memory poisoning is the
  primary long-term failure mode and is designed against from the start.
- The two persona models stay separate. The Buddhist-vs-occultist contrast is
  the point; a combined model would blur the voices.

## Model Roles

The harness involves three distinct model *roles*. Only the persona role is
ever seen by the user.

| Role | Job | Needs to be smart? | Mapping |
|---|---|---|---|
| Persona / chat | Generate in-voice replies | No — 3B + LoRA is sufficient | Buddhist adapter, Occult adapter (two separate instances) |
| Embedding | Turn text into vectors for retrieval; never converses | No — small specialist | e.g. `nomic-embed-text` / `bge-small-en` |
| Utility / librarian | Summarize scrolled-off turns (compaction); extract and validate memory notes; judge relevance | Yes — this is where 3B is weakest | 3B reused at first; a stronger 8–14B model is the highest-leverage upgrade |

Key insight: the highest-value upgrade is **not** making the chatting models
smarter. It is giving the *librarian* role a stronger model while keeping the
cheap 3B fine-tunes as the characters. Characterful-but-limited voices, one
capable librarian behind them.

## Architecture Overview

```
        ┌────────────────────────────────────────────┐
        │  WEB CHAT UI (browser)                       │
        │  live view of the two personas going back    │
        │  and forth; this is the viewing surface,     │
        │  NOT the LM Studio UI                         │
        └───────────────────┬──────────────────────────┘
                            │ HTTP / WebSocket (stream)
   ┌────────────────────────▼─────────────────────────────────┐
   │                ORCHESTRATOR (code, no model)               │
   │   serves the web UI; owns the turn loop and context        │
   │                                                            │
   │   Persona A: Buddhist 3B+LoRA  ─┐                          │
   │   Persona B: Occult 3B+LoRA   ──┘  ← these two converse    │
   │                                     (with user or together)│
   │                                                            │
   │   Embedding model (tiny)   ← finds relevant notes/passages │
   │   Utility model            ← compaction + memory writing   │
   └───────────────┬───────────────────────────┬───────────────┘
                   │ /v1 (server mode)          │
        ┌──────────▼───────────┐     ┌──────────▼───────────┐
        │ LM Studio (headless)  │    │ Obsidian vault (md)  │
        │  serves the GGUF +    │    │  /canon  (read-only) │
        │  LoRA adapters        │    │  /memory (episodic)  │
        └───────────────────────┘    └──────────┬───────────┘
                                                 │ (re)index
                                      ┌──────────▼───────────┐
                                      │ Vector index         │
                                      │  (sqlite-vec)        │
                                      │  derived, rebuildable│
                                      └──────────────────────┘
```

The web chat UI is the only surface a person watches. The orchestrator serves
it and streams each persona's reply to it token by token, so the exchange is
visible ticking back and forth. LM Studio runs headless in server mode behind
the orchestrator. `/canon` is chunked from `source_texts/` and is read-only
grounding; `/memory` holds episodic notes the harness writes during
conversation.

## Turn Lifecycle

Each conversational turn proceeds through the orchestrator as follows:

1. **Retrieve.** Embed the last user message (plus the previous assistant turn
   for context). Cosine-search the index for the top-k `/memory` notes and
   top-k `/canon` passages.
2. **Assemble.** Fill a fixed token budget, highest priority first (see
   below). Persona and current message are never dropped; everything else
   degrades gracefully.
3. **Generate.** POST the assembled context to the active persona model's
   `/v1/chat/completions` endpoint and stream the reply to the user.
4. **Append.** Add the user+assistant pair to the in-memory transcript and an
   append-only `session.jsonl` log.
5. **Write memory (async).** The utility model extracts durable, structured
   notes, validates them, and writes survivors to `/memory`. Reindex.
6. **Compact (async).** If verbatim recent-turn tokens exceed a threshold, the
   utility model folds the oldest turns into the running summary.

Steps 5 and 6 run after the reply is streamed so they add no perceived
latency.

## Context Budget

Target a tight working window (~6–8K tokens) even though the base model's
nominal window is larger, because a 3B model's coherence fades well before its
hard limit. Each turn the assembler fills the budget in priority order and
truncates the remainder.

| Slot | Approx budget | Source | Notes |
|---|---|---|---|
| System / persona | ~600 | static | Pinned; always present. The voice contract. |
| Long-term memory | ~800 | `/memory` retrieval | Top 3–5 episodic notes. |
| Source grounding | ~1000 | `/canon` retrieval | Top 2–3 passages. Optional if persona alone suffices. |
| Conversation summary | ~500 | compaction | Running synopsis of scrolled-off turns. |
| Recent turns (verbatim) | ~3000 | transcript | Rolling window of the most recent exchanges. |
| Current user message | variable | — | Never dropped. |
| Response headroom | ~2000 | — | Reserved for the reply. |

Rule: persona and current message are guaranteed; memory, grounding, and
summary shrink first under pressure.

## Memory Model

Two stores, one format.

- **Vault is the source of truth** (markdown, Obsidian). The **vector index is
  derived** and rebuildable from the vault. They are never allowed to
  disagree; the index is refreshed on every write.
- **`/canon`** is chunked and embedded once from `source_texts/`. Read-only.
  This keeps source grounding strictly separate from invented memory.
- **`/memory`** holds episodic notes the harness writes. One fact per note,
  structured frontmatter, mirroring the discipline of the project's existing
  memory conventions:

```markdown
---
id: 2026-05-31-user-prefers-terse
type: preference | fact | event
session: <session id>
created: 2026-05-31
confidence: high | medium | low
source: <turn ref or canon ref>
---
User prefers short, direct answers over long explanations.
```

## Memory Poisoning Guardrails

Non-negotiable on small models. Without these, invented notes are retrieved as
authoritative context and compound errors over time.

- **Structured and narrow writes only** — one fact, with `confidence` and
  `source`. No free-form essays.
- **Validate before write** — reject notes that contradict `/canon`, are
  near-duplicates (cosine > 0.9 of an existing note → merge or skip), or fall
  below a confidence threshold.
- **The conversing/utility model writes, not a separate weaker model** — it
  has full context and removes a failure point. A separate small writer is the
  more dangerous option and is explicitly rejected.
- **Retention and decay** — timestamp everything; let stale, low-confidence
  notes age out so the vault does not bloat and degrade retrieval.
- **Provenance** — every retrieved memory carries its source so any reply can
  be audited back to its origin.

## Optional Tool Layer

The current 3B personas cannot drive tools reliably, but the harness is built
ready for them. Between generate (step 3) and append (step 4): if a reply
contains a tool call, the orchestrator dispatches it, appends the result to
the transcript, and loops back to generate. Candidate tools:

- `search_canon(query)`
- `recall(query)`
- `save_memory(note)`

When the persona endpoint is later swapped to a tool-capable model
(Qwen 14B / Command-R), this layer activates with no other redesign. This is
why tool use belongs in the harness, not in the LoRA fine-tune.

## Build Phases

Do not build it all at once. Each phase is independently useful.

1. **Web chat MVP** — the dedicated web chat UI (restored or recreated) served
   by the orchestrator, with LM Studio headless behind it, showing the two
   persona models going back and forth live with a rolling-window transcript.
   No memory, no RAG, no compaction yet. This is the gating milestone: once the
   conversation is visibly ticking in the browser, the work pauses for a
   decision — keep watching to inform fine-tuning, or proceed to phase 2.
2. **Compaction** — running summary so long sessions stop hitting amnesia.
3. **Canon RAG** — chunk/embed `source_texts/`, retrieve grounding. Biggest
   single quality jump for a small model.
4. **Episodic memory** — vault writes, retrieval, and the poisoning
   guardrails.
5. **Tools** — only after moving to a tool-capable persona model.

Phase 1 is the immediate priority and the only phase that must precede the
others. Everything from phase 2 on is explicitly deferred until the web chat
is working and the decision point above has been reached.

## File-Level Intent

When this design is later implemented, the expected layout, consistent with
the package conventions, is:

```
src/ai_training_tests/chat/
  server.py            # serves the web UI; HTTP/WebSocket endpoints
  orchestrator.py      # turn lifecycle
  context_budget.py    # the budget table above
  retrieval.py         # embeddings + vector search
  memory_writer.py     # validated extraction → vault
  compaction.py        # rolling summary
  llm_client.py        # LM Studio /v1 wrapper
web/                   # the web chat UI (restored or recreated in phase 1)
scripts/chat/run_chat.py
```

The `web/` UI and `server.py` are the phase-1 surface. If the previous web
chat cannot be located, recreate a minimal version: a two-pane (or
single-stream) chat view that connects to the orchestrator over a WebSocket
and renders each persona's streamed tokens as they arrive, with a visible
speaker label per turn.

Expected new artifacts:

- an Obsidian vault tree with `/canon` and `/memory`
- a `sqlite-vec` index derived from the vault
- per-session `session.jsonl` transcripts

## Verification Plan

Because this is design-only, verification here means agreeing the design is
sound. When implemented, each phase verifies independently:

1. Web chat MVP — the web chat UI loads in a browser and shows a multi-turn
   conversation between the two persona adapters streaming live, served by the
   orchestrator with LM Studio headless behind it. Success is literally being
   able to watch the two models go back and forth in the browser.
2. Compaction — a conversation exceeding the recent-turn budget retains early
   facts via the running summary.
3. Canon RAG — replies cite or reflect retrieved `source_texts/` passages;
   retrieval returns relevant chunks for representative queries.
4. Episodic memory — facts written in one session are retrieved in a later
   session; the guardrails reject contradictory, duplicate, and low-confidence
   writes.

## Success Criteria

The design is successful if:

- the three model roles are clearly separated and mappable to concrete models
- context assembly is bounded by an explicit, prioritized token budget
- canon and episodic memory are stored separately, with the vault as source of
  truth and the index as a rebuildable derivative
- memory poisoning guardrails are specified before any memory write path
- the persona endpoint is swappable so a tool-capable model can be adopted
  without redesigning the harness
- the build is staged so each phase delivers standalone value

## Risks

- A 3B persona's long-conversation coherence is inherently limited; the
  harness mitigates but cannot eliminate drift and repetition.
- An under-validated memory writer poisons the vault; the guardrails are the
  mitigation and must not be deferred past phase 4.
- Letting the index and vault drift apart corrupts retrieval; always reindex on
  write and treat the vault as authoritative.
- Over-large context on a 3B degrades quality; resist widening the budget
  instead of improving retrieval and compaction.
- Combining the two personas into one model to "simplify" would blur the
  voices and defeat the project's contrast; keep them separate.

## Recommendation

Implement in phase order, and treat phase 1 — the web chat UI with the two
personas visibly conversing — as the immediate and gating deliverable. Restore
the previous web chat if it can be found; otherwise recreate a minimal
streaming view. Only after the conversation is watchable in the browser, and
the resulting fine-tuning decision is made, proceed to compaction, RAG, and
memory. Keep the two 3B persona fine-tunes as the characters and invest the
single available upgrade in the librarian (utility) role rather than the chat
models. Defer the tool layer until a tool-capable persona model is adopted, at
which point the harness should accept it as an endpoint swap.
