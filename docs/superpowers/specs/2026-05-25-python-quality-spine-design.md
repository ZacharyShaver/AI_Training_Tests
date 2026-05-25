# Python Quality Spine Design

## Goal

Add a minimal but durable Python quality/tooling spine to the repository so parser and dataset work can be validated, linted, and run consistently.

## Scope

This design covers:

- a repo-level `pyproject.toml`
- initial `uv`-compatible project metadata
- `ruff` lint/format configuration
- `pytest` test configuration
- `pre-commit` hooks
- one GitHub Actions workflow for lint and tests
- one first-pass `Pydantic` schema for dialogue rows
- tests for valid and invalid dialogue-row validation

This design does not cover:

- broad parser refactors
- full property-based testing
- full type-checking rollout
- Obsidian Base dashboards

## Constraints

- keep the first pass small and low-friction
- do not force a repo restructure
- avoid speculative abstractions
- validate the current dialogue row shape instead of inventing a new dataset format

## Architecture

Use `pyproject.toml` as the single anchor for Python tooling. Keep the schema layer focused on one responsibility: validating the JSONL dialogue row structure already emitted by parser scripts.

The first schema should model:

- `messages`
- `metadata`
- required message roles
- required metadata fields
- basic invariants such as three-message rows and stable role order

## File Plan

- create `pyproject.toml`
- create `.pre-commit-config.yaml`
- create `.github/workflows/python-quality.yml`
- create `scripts/extraction/dialogue_schema.py`
- create `tests/test_dialogue_schema.py`

## Validation Strategy

Use test-first development for the schema module:

- valid row passes
- wrong message count fails
- wrong role order fails
- missing metadata field fails
- inconsistent `target_words` fails

## Success Criteria

- repo has one Python tool/config root
- linting and tests run locally in a standard way
- pre-commit can enforce basic hygiene
- CI can run the same checks
- at least one parser-output contract is explicit and tested
