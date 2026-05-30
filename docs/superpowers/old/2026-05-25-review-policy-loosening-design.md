# Review Policy Loosening Design

## Goal

Relax the dialogue review pipeline so it remains strict on structural integrity while becoming more permissive about thin context and slight local looseness.

This change applies to review and machine-review policy only. It does not relax source-parser extraction safeguards.

## Problem

The current pipeline mixes two distinct concerns:

1. extraction correctness
2. review strictness

In practice, this causes machine-review to reject rows for being thin, locally compressed, or slightly out of context even when:

- the `Participant A` / `Participant B` structure is intact
- the target speaker is correct
- the target text is a coherent local next reply

The Majjhima Nikaya review loop made this visible. Parser fixes removed real extraction failures, but the review posture then became so strict that only one row survived. That indicates the review standard is over-penalizing acceptable rows once structural failures are removed.

## Desired Outcome

The pipeline should:

- stay strict about who is speaking and whether the row is structurally valid
- tolerate one-turn prompts when the reply is locally coherent
- tolerate slight scene looseness when the reply still clearly belongs to the correct participant
- continue rejecting rows that would train the model on incorrect speaker behavior, broken formatting, or contaminated content

## Non-Goals

- Do not relax parser extraction logic to allow wrong-speaker or obviously cross-scene rows
- Do not change the chat format or metadata schema
- Do not promote provisional parser outputs to canon automatically
- Do not lower standards around narration, commentary contamination, or malformed target text

## Policy Split

### 1. Extraction Gate

Parser-level safeguards remain strict.

Rows must still fail extraction or be rejected during parser review if they show:

- wrong speaker attribution
- broken `Participant A` / `Participant B` mapping
- obvious scene jump
- malformed or fragmentary target text
- narration or commentary contamination

These remain hard failures.

### 2. Review Gate

Review becomes more permissive on context depth and local compression.

Rows may now pass review if:

- the participant mapping is correct
- the target reply is coherent as the next utterance by the labeled participant
- the local exchange is understandable even with only one prior turn
- the row shows slight contextual looseness but not a clear speaker or scene break

Thin context by itself is not failure.

Slight looseness by itself is not failure.

## New Review Categories

The review pipeline should evaluate rows using three categories:

### Hard Failures

These always reject a row:

- wrong speaker attribution
- broken `Participant A` / `Participant B` mapping
- obvious scene jump
- malformed or fragmentary target text
- narration/commentary contamination

### Soft Warnings

These do not reject a row on their own:

- only one prior turn of context
- compressed setup that omits some intermediate narrative or framing
- slight local scene looseness where the target still clearly reads as the correct next reply
- minimal but still meaningful context

### Clear Passes

Rows with clean participant structure and coherent next-reply behavior pass regardless of whether they have one prior turn or several.

## Review Decision Rule

A row passes if:

- it has no hard failures
- its participant structure is intact
- its target reads as a plausible next reply from the labeled participant

A row fails if:

- any hard failure is present

A row with only soft warnings passes, but the warning should still be recorded in the review artifact so later policy tuning remains possible.

## Machine Review Behavior

Machine-review should stop treating all context-thin rows as failures.

Instead:

- sampled rows should be labeled with `Approve`, `Approve with warning`, or `Reject`
- only `Reject` should count against a set’s pass rate
- warnings should be aggregated in run summaries so humans can see when a parser passes mostly on thin-context rows

This preserves auditability without punishing rows that are structurally sound.

## Candidate Pool Interpretation

Low row count alone should not automatically mean failure.

However, a parser should still be treated as blocked if:

- the surviving pool is so small that the review set is not meaningful, or
- the pool survives only because almost everything else is structurally broken

The distinction is:

- small but still meaningful pool: acceptable
- collapsed or degenerate pool: blocked

This judgment should be based on review notes, not just a fixed numeric threshold.

## Implementation Shape

Add a centralized review policy module under `scripts/extraction/`.

It should define:

- hard failure conditions
- soft warning conditions
- pass decision rules
- helper text for review packet generation

Machine-review code and review artifact generation should consume this policy instead of embedding implicit standards in ad hoc notes.

Source parsers should not import loosened review behavior into extraction rules. Parser code remains focused on source interpretation and structural correctness.

## Artifact Changes

Review artifacts should explicitly distinguish:

- hard failure
- warning
- pass

Run summaries should include:

- rejected rows count
- warning-only rows count
- pass count
- whether the set passed with clean approvals only or with mixed warnings

Pass history should note whether a parser is:

- structurally clean and approved
- structurally clean but warning-heavy
- blocked due to real hard-failure prevalence
- blocked due to degenerate population collapse

## Testing

Add tests covering:

- one-turn prompt rows that should now pass review
- slight local looseness rows that should now pass with warning
- wrong-speaker rows that must still fail
- broken participant-mapping rows that must still fail
- malformed target rows that must still fail
- contaminated narration rows that must still fail

Tests should focus on policy decisions rather than parser-specific extraction heuristics.

## Risks

### Risk: Review becomes too permissive

Mitigation:

- keep structural failures as hard rejects
- record warnings explicitly
- preserve human review before canon promotion

### Risk: Standards become inconsistent across parsers

Mitigation:

- use one centralized review policy
- keep parser-specific exceptions out of the shared standard unless explicitly justified

### Risk: Machine-approved starts to imply canon-ready

Mitigation:

- keep the existing rule that machine approval is never canon approval
- keep review artifacts in `review_outputs/` until a human promotes them

## Rollout

1. Add the shared review policy module.
2. Update machine-review scoring to use hard failures versus soft warnings.
3. Update review packet generation to surface warnings explicitly.
4. Re-run the Majjhima Nikaya machine review under the loosened review policy without relaxing extraction safeguards.
5. Reassess whether the parser is still blocked once review is no longer over-penalizing thin-context rows.

## Success Criteria

The change is successful when:

- structurally sound one-turn prompt rows are no longer rejected just for being thin
- slight local looseness is recorded as warning instead of failure
- wrong-speaker and obvious scene-jump rows still fail
- machine-review artifacts clearly explain why a row passed, warned, or failed
- Majjhima-style parser reviews no longer collapse solely because review policy is stricter than intended
