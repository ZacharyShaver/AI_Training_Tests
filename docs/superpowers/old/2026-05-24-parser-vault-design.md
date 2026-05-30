# Parser Vault Design

## Goal

Store parser knowledge in the Obsidian vault in a parser-centric structure that stays durable over time, surfaces cross-parser reuse clearly, and avoids turning the vault into a duplicate of `review_outputs/`.

## Design Priorities

This design is optimized for:

- durable extraction knowledge over session chatter
- explicit separation of approved, provisional, rejected, and unknown parser states
- concise summaries that link to evidence rather than copying large artifacts
- cross-parser comparisons that make reuse and failure clustering obvious

## Scope

This design covers:

- one note per active source parser in `scripts/extraction/parse_*.py`
- one parser hub note for cross-parser pattern tracking
- one update to the existing project note so the parser area is discoverable
- a controlled vocabulary for parser status, evidence, and pattern headings

This design does not cover:

- changing parser code
- approving sources for canonical promotion
- storing raw JSONL outputs or full review packets inside the vault

## Risk Controls

The earlier draft identified three risks. This design addresses them directly:

### 1. Transient Observations Polluting Durable Notes

Control:

- every parser note will separate `Durable Patterns` from `Current Review Snapshot`
- only repeatable extraction lessons belong in pattern sections
- one-off run details stay out unless they changed the parser strategy or review decision

Rule:

- if an observation matters only to a single run, do not store it as a pattern

### 2. Vault Duplication Of Large Review Artifacts

Control:

- parser notes will never embed large review packets or bulk sample text
- notes will store short evidence summaries plus path references to `review_outputs/` or vault archive material

Rule:

- summarize, link, and classify; do not copy review packet bodies into parser notes

### 3. Approved And Provisional States Getting Mixed

Control:

- every parser note must declare one status using a fixed vocabulary
- the hub note will group parsers by status instead of mixing them in one flat list

Required status vocabulary:

- `Approved`
- `Provisional`
- `Rejected`
- `In Review`
- `Unknown`

Rule:

- if evidence does not support a stronger claim, use `Unknown`

## Storage Model

Primary structure:

- one parser hub note
- one note per parser
- links from the existing project note into the parser hub

Vault location:

- `hermes_memory_vault/Projects/AI_Training_Tests/Parsers/`

Files:

- `hermes_memory_vault/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- `hermes_memory_vault/Projects/AI_Training_Tests/Parsers/<parser note>.md`

The existing `hermes_memory_vault/Projects/AI_Training_Tests.md` remains the project entry point.

## Parser Note Model

Each parser note should use the same sections, in the same order:

1. `Parser`
2. `Status`
3. `Source And Outputs`
4. `Extraction Strategy`
5. `Durable Patterns That Worked`
6. `Durable Patterns That Failed`
7. `Current Review Snapshot`
8. `Evidence`
9. `Related Parsers`
10. `Open Questions`
11. `Next Likely Improvements`

### Field Rules

`Status`

- must use the fixed vocabulary exactly

`Durable Patterns That Worked`

- only include techniques that appear intentionally designed or repeatedly useful

`Durable Patterns That Failed`

- only include failure modes that reflect parser logic, source structure mismatch, or review-standard mismatch

`Current Review Snapshot`

- short, date-aware summary of where the parser stands now
- may mention specific review artifacts, but should not become a run log

`Evidence`

- list concise bullets with file paths and one-line significance

`Related Parsers`

- each link should include the relationship reason, such as shared source shape or shared failure mode

## Hub Note Model

The hub note should contain:

- parser inventory grouped by status
- recurring patterns that worked across multiple parsers
- recurring patterns that failed across multiple parsers
- relationship map between parsers
- open questions for future parser development

The hub note should summarize patterns only after they appear in one or more parser notes. It is not the place for isolated speculation.

## Controlled Vocabulary

Use these exact section names in parser notes:

- `Durable Patterns That Worked`
- `Durable Patterns That Failed`
- `Current Review Snapshot`
- `Evidence`
- `Related Parsers`
- `Open Questions`

Use these relationship phrases when possible:

- `Shares extraction shape with`
- `Shares failure mode with`
- `Can borrow logic from`
- `Useful contrast with`

This keeps cross-parser links consistent and searchable.

## Linking Rules

Use Obsidian wikilinks for internal note relationships.

Required links:

- project note -> parser hub
- parser hub -> every parser note
- parser note -> parser hub
- parser note -> related parser notes

Evidence references:

- use code-formatted repo paths for files outside the vault
- do not mirror artifact contents unless the summary itself is the durable knowledge

## Data Sources

Populate parser notes from:

- `scripts/extraction/parse_*.py`
- `review_outputs/`
- `hermes_memory_vault/References/Review_Archive/`
- `hermes_memory_vault/Projects/AI_Training_Tests.md`

When the evidence is thin, prefer `Unknown` status and a narrow summary over confident invention.

## Initial Coverage

Create notes for:

- `parse_asclepius.py`
- `parse_blue_cliff_record.py`
- `parse_dhammapada_commentary.py`
- `parse_diamond_sutra.py`
- `parse_gateless_gate.py`
- `parse_itivuttaka.py`
- `parse_majjhima_nikaya.py`
- `parse_sutta_nipata.py`
- `parse_udana.py`
- `parse_vimalakirti.py`
- `parse_zen_koans_database.py`

## Quality Gate For Note Writing

Before a parser note is considered complete, verify:

- status is explicit and uses the fixed vocabulary
- evidence bullets point to real files
- pattern sections contain durable lessons, not run chatter
- no large review packet text was copied in
- related parser links have reasons, not just names

## Implementation Plan

1. Create the parser note directory and parser hub.
2. Add a standardized parser note template using the required sections.
3. Read parser scripts and review evidence to populate each parser note conservatively.
4. Add cross-links only when the relationship is defensible from code or review evidence.
5. Update the project note to link into the parser hub.

## Success Criteria

- every active parser has a dedicated note
- parser statuses are unambiguous
- the hub makes cross-parser patterns visible without duplicating review packets
- durable patterns are easy to scan across notes
- the vault remains a knowledge layer, not a second copy of generated outputs
