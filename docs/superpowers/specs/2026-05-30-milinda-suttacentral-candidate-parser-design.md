# Milinda SuttaCentral Candidate Parser Improvement Design

## Goal

Improve the Milinda SuttaCentral candidate path in a balanced way:

- fix source-boundary mojibake and broken punctuation in the canonical export
- improve candidate-row coherence in the dedicated Milinda parser
- preserve the current candidate workflow and review gate
- avoid forcing an immediate final-dataset cutover

## Current Problem

The current Milinda SuttaCentral candidate path is materially better than the
older OCR/PDF path, but it still has two quality problems:

1. The canonical clean source still contains mojibake such as `NÄgasena`,
   `â€œ`, `â€`, and `â€¦`.
2. The dedicated parser can recover coherent short exchanges, but long
   same-line quote runs still risk generating awkward or weak `next reply` rows.

This makes the SuttaCentral path promising but not yet ready for promotion over
the current legacy Milinda final rows.

## Design Principles

- Source cleanup belongs at the source boundary, not in downstream row logic.
- Parser logic should reason about dialogue structure, not text-decoding repair.
- Review gates remain mandatory; cleaner source alone is not enough to promote
  Milinda into the final dataset.
- This pass should improve quality without turning into a full coverage redesign.

## Scope

### In Scope

- improve normalization for SuttaCentral-derived Milinda text
- regenerate the canonical Milinda SuttaCentral clean export if needed
- tighten Milinda parser row selection for bounded alternating exchanges
- add or update focused tests for normalization and parser behavior
- regenerate the Milinda candidate output and a fresh review packet

### Out Of Scope

- replacing the live final Milinda rows in the main build
- broad redesign of all SuttaCentral ingest tooling
- maximizing Milinda row count at the expense of coherence
- touching unrelated Buddhist parsers

## Recommended Approach

### 1. Fix Text Sanitation At The Source Boundary

The ingest or shared normalization layer should emit cleaner canonical text for
Milinda before the parser sees it.

Expected outcome:

- curly quotes become standard quotes
- mojibake ellipses become `...` or a normalized ellipsis form already accepted
  by repo conventions
- common mojibake name fragments normalize to intended Unicode or stable ASCII
  text
- section headings and stable structural markers remain unchanged

The key boundary is the canonical source file:

- `source_texts/buddhist/clean/milindapanha_suttacentral.txt`

This file should be treated as the parser input contract. If the file is
corrupted, every downstream parser refinement becomes brittle.

### 2. Tighten Milinda Parser Extraction

The dedicated Milinda parser should emit rows only from bounded alternating
dialogue exchanges.

Expected behavior:

- keep coherent short and medium alternating Q/A runs
- preserve the strong chariot and identity sequences already visible in the
  candidate packet
- reject tails that behave like collapsed monologues or mixed narration blocks
- avoid producing prompts where `Participant B` appears twice in sequence
  without an intervening `Participant A`

Practical parser changes may include:

- segmenting long inline quote chains into local windows
- enforcing speaker alternation at the row-construction boundary
- rejecting windows contaminated by applause lines, narration, or post-exchange
  commentary
- keeping history windows local to one section and one exchange run

### 3. Re-run Candidate Review, Not Final Promotion

This pass ends with a refreshed candidate JSONL and a new review packet for
`parse_milinda_panha`.

It does not end with final promotion.

Promotion remains blocked until:

- the refreshed candidate output is cleaner
- review packets show coherent speaker continuity
- output quality is good enough to justify a later cutover conversation

## File-Level Intent

### Likely Files To Change

- `tools/source_ingest/fetch_milinda_suttacentral.py`
- `src/ai_training_tests/extraction/common/text_cleaning.py`
- `src/ai_training_tests/extraction/parsers/milinda_panha.py`
- `tests/test_fetch_milinda_suttacentral.py`
- `tests/test_parse_milinda_panha_outputs.py`

### Expected Artifacts To Refresh

- `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- `review_outputs/new_buddhist_sources/milinda_panha_dialogue.jsonl`
- `review_outputs/new_buddhist_sources/milinda_panha_dialogue_review_sample.md`
- `review_outputs/parser_reviews/parse_milinda_panha/set_02/` or the next
  available review set
- `review_outputs/parser_reviews/parse_milinda_panha/pass_history.md`

## Test Strategy

### Source Normalization Tests

Add or extend tests that prove SuttaCentral-derived text normalizes correctly.

Examples:

- HTML or JSON payload text containing `â€œ`, `â€`, `â€¦`, and `NÄgasena`
  should normalize into stable clean text
- canonical section markers such as `## mil3.1.1` must survive normalization

### Parser Behavior Tests

Add or extend tests that prove the Milinda parser prefers bounded alternating
dialogue.

Examples:

- same-line quote chains still parse when they represent a clean local exchange
- prompts do not contain `Participant B` twice in sequence
- narration or applause lines do not become assistant targets
- long inline sequences are segmented or filtered rather than blindly converted
  into rows

## Verification Plan

Run Milinda-focused verification only.

Primary checks:

1. targeted ingest/normalization tests
2. targeted Milinda parser tests
3. a Milinda parser smoke run that rewrites candidate outputs
4. a fresh parser review packet
5. manual inspection of the review sample for:
   - clean names and punctuation
   - coherent speaker continuity
   - no obvious narration contamination

## Success Criteria

This pass is successful if all of the following are true:

- the canonical Milinda SuttaCentral clean source no longer contains the main
  mojibake patterns currently visible in review artifacts
- the Milinda candidate parser still produces a viable candidate pool
- the refreshed review packet shows stronger prompt/target continuity than the
  current baseline
- no final-build cutover is performed in this pass

## Risks

- fixing normalization too narrowly in the parser would hide a source problem
  instead of solving it
- over-tightening parser gates could collapse the candidate pool too far
- aggressive cleanup could accidentally damage section markers or quote
  boundaries

## Recommendation

Implement this as one balanced refinement pass:

- source cleanup first
- parser gating second
- Milinda-only verification third

If the resulting candidate set is cleaner but still too small, treat that as
evidence for a later coverage redesign rather than over-expanding scope now.
