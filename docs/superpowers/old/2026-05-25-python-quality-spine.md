# Python Quality Spine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a minimal Python tooling and validation spine for parser work in this repository.

**Architecture:** Use `pyproject.toml` as the tool configuration root, add lightweight lint/test automation, and introduce one focused `Pydantic` schema for dialogue rows with test-first validation.

**Tech Stack:** Python, uv-compatible `pyproject.toml`, Ruff, pytest, Pydantic, pre-commit, GitHub Actions

---

### Task 1: Add The First Failing Schema Tests

**Files:**
- Create: `tests/test_dialogue_schema.py`
- Test: `tests/test_dialogue_schema.py`

- [ ] **Step 1: Write the failing tests**

Add tests for:

```python
def test_valid_dialogue_row_passes_validation(): ...
def test_dialogue_row_requires_exactly_three_messages(): ...
def test_dialogue_row_requires_system_user_assistant_role_order(): ...
def test_dialogue_row_requires_target_words_to_match_assistant_text(): ...
def test_dialogue_row_requires_required_metadata_fields(): ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_dialogue_schema.py -q`
Expected: FAIL because `scripts.extraction.dialogue_schema` does not exist yet

### Task 2: Implement The Minimal Dialogue Row Schema

**Files:**
- Create: `scripts/extraction/dialogue_schema.py`
- Test: `tests/test_dialogue_schema.py`

- [ ] **Step 1: Write the minimal implementation**

Implement Pydantic models for:

```python
class DialogueMessage(BaseModel): ...
class DialogueMetadata(BaseModel): ...
class DialogueRow(BaseModel): ...
```

- [ ] **Step 2: Run test to verify it passes**

Run: `python -m pytest tests/test_dialogue_schema.py -q`
Expected: PASS

### Task 3: Add Repo Tooling Configuration

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Add minimal project and tool config**

Include:

```toml
[project]
name = "ai-training-tests"
version = "0.1.0"
requires-python = ">=3.11"

[dependency-groups]
dev = ["pydantic>=2", "pytest>=8", "ruff>=0.11", "pre-commit>=4"]
```

- [ ] **Step 2: Add Ruff and pytest config**

Configure `ruff` and `pytest` in the same file.

### Task 4: Add Pre-commit Hooks

**Files:**
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Add basic hygiene and Ruff hooks**

Include hooks for:

```yaml
- trailing-whitespace
- end-of-file-fixer
- check-yaml
- ruff-check
- ruff-format
```

### Task 5: Add CI

**Files:**
- Create: `.github/workflows/python-quality.yml`

- [ ] **Step 1: Add lint-and-test workflow**

Run:

```yaml
- checkout
- setup-python
- pip install .[dev]
- ruff check .
- python -m pytest tests
```

### Task 6: Verify The Tooling Spine

**Files:**
- Verify: `pyproject.toml`
- Verify: `.pre-commit-config.yaml`
- Verify: `.github/workflows/python-quality.yml`
- Verify: `tests/test_dialogue_schema.py`

- [ ] **Step 1: Run local verification**

Run:

```bash
python -m pytest tests/test_dialogue_schema.py -q
python -m ruff check scripts/extraction/dialogue_schema.py tests/test_dialogue_schema.py
```

Expected: PASS
