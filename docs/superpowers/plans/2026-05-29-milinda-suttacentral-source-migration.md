# Milinda SuttaCentral Source Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current OCR-heavy Milinda source with a locally exported SuttaCentral-based corpus, cut Milinda over to a dedicated parser, and leave the repo ready for focused parser improvement work on the new source.

**Architecture:** Do this in two phases. First add a deterministic SuttaCentral ingestion/export tool that downloads or reuses cached Milinda pages and writes one canonical local text file plus raw cached artifacts. Second add a dedicated `parse_milinda_panha.py` parser and switch the build off the legacy base builder for Milinda in the same cutover commit that replaces `oritiginal text/Milinda Panha.txt`, so source migration does not silently change the live dataset before the dedicated parser exists.

**Tech Stack:** Python 3.11, stdlib `urllib.request`, `html.parser`, `json`, `argparse`, pytest, JSONL, Markdown review artifacts, existing review pipeline under `tools/review_pipeline/`.

---

## Current Constraints

- `scripts/extraction/build_pilot_dialogue_dataset.py` currently reads `oritiginal text/Milinda Panha.txt` directly and contributes Milinda rows into `full_dialogue_dataset.jsonl`.
- `config/dataset_manifest.json` and `src/ai_training_tests/domain/source_manifest.py` still treat Milinda as part of the legacy base builder.
- The user wants the SuttaCentral source exported locally and consolidated into a file that replaces the current OCR text, but replacing that file too early would change the production dataset without a dedicated parser review gate.
- Therefore, the source replacement must happen only after the dedicated Milinda parser is added and the legacy builder no longer consumes Milinda.

## Target File Layout

### New Source-Ingest Files

- Create: `tools/source_ingest/__init__.py`
- Create: `tools/source_ingest/fetch_milinda_suttacentral.py`
- Create: `tests/test_fetch_milinda_suttacentral.py`
- Create: `tests/fixtures/milinda_suttacentral/index.html`
- Create: `tests/fixtures/milinda_suttacentral/mil3.1.1.html`
- Create: `tests/fixtures/milinda_suttacentral/mil3.2.1.html`

### New Local Source Artifacts

- Create: `source_texts/buddhist/raw/milindapanha_suttacentral/index.html`
- Create: `source_texts/buddhist/raw/milindapanha_suttacentral/pages/`
- Create: `source_texts/buddhist/raw/milindapanha_suttacentral/export_manifest.json`
- Create: `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- Modify later in the cutover task: `oritiginal text/Milinda Panha.txt`

### New Parser Files

- Create: `src/ai_training_tests/extraction/parsers/milinda_panha.py`
- Create: `scripts/extraction/parse_milinda_panha.py`
- Create: `tests/test_parse_milinda_panha_outputs.py`

### Existing Files To Modify During Cutover

- Modify: `scripts/extraction/build_pilot_dialogue_dataset.py`
- Modify: `scripts/extraction/build_full_dialogue_outputs.py`
- Modify: `src/ai_training_tests/domain/source_manifest.py`
- Modify: `scripts/extraction/dialogue_source_manifest.py`
- Modify: `config/dataset_manifest.json`
- Modify: `source_texts/buddhist/SOURCES.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Parsers/base_dialogue_dataset.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Parsers/parse_milinda_panha.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Sources/Buddhist Sources.md`

---

### Task 1: Add Source-Ingest Fixtures And Tests

**Files:**
- Create: `tests/test_fetch_milinda_suttacentral.py`
- Create: `tests/fixtures/milinda_suttacentral/index.html`
- Create: `tests/fixtures/milinda_suttacentral/mil3.1.1.html`
- Create: `tests/fixtures/milinda_suttacentral/mil3.2.1.html`

- [ ] **Step 1: Write a failing test for section discovery from a cached SuttaCentral index**

```python
from pathlib import Path

from tools.source_ingest.fetch_milinda_suttacentral import discover_section_refs


def test_discover_section_refs_reads_mil_ids_from_index_fixture() -> None:
    fixture = Path("tests/fixtures/milinda_suttacentral/index.html")
    refs = discover_section_refs(fixture.read_text(encoding="utf-8"))

    assert "mil3.1.1" in refs
    assert "mil3.2.1" in refs
    assert refs == sorted(set(refs))
```

- [ ] **Step 2: Write a failing test for consolidated export rendering**

```python
from pathlib import Path

from tools.source_ingest.fetch_milinda_suttacentral import parse_suttacentral_page, render_consolidated_text


def test_render_consolidated_text_keeps_headings_and_dialogue() -> None:
    page_one = parse_suttacentral_page(
        "mil3.1.1",
        Path("tests/fixtures/milinda_suttacentral/mil3.1.1.html").read_text(encoding="utf-8"),
    )
    page_two = parse_suttacentral_page(
        "mil3.2.1",
        Path("tests/fixtures/milinda_suttacentral/mil3.2.1.html").read_text(encoding="utf-8"),
    )

    text = render_consolidated_text([page_one, page_two])

    assert "## mil3.1.1" in text
    assert "King Milinda" in text
    assert "Nāgasena" in text
    assert "unsupported browser" not in text.lower()
```

- [ ] **Step 3: Run the new tests to verify they fail**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_fetch_milinda_suttacentral.py -q`  
Expected: FAIL with import errors because `tools.source_ingest.fetch_milinda_suttacentral` does not exist yet.

### Task 2: Implement The SuttaCentral Ingestion And Local Export Tool

**Files:**
- Create: `tools/source_ingest/__init__.py`
- Create: `tools/source_ingest/fetch_milinda_suttacentral.py`

- [ ] **Step 1: Add the source-ingest package marker**

```python
"""Source acquisition helpers for local corpus exports."""
```

- [ ] **Step 2: Implement section discovery, page parsing, and export rendering**

Use stdlib networking so the tool does not add a new dependency. The module should expose:

```python
def discover_section_refs(index_html: str) -> list[str]: ...
def fetch_html(url: str, *, timeout: int = 60) -> str: ...
def parse_suttacentral_page(section_ref: str, html: str) -> SuttaCentralPage: ...
def render_consolidated_text(pages: list[SuttaCentralPage]) -> str: ...
def write_export_manifest(path: Path, *, source: str, base_url: str, refs: list[str], output_path: Path) -> None: ...
```

Core design rules:

- Fetch only SuttaCentral Milinda section pages such as `mil3.1.1/en/kelly` or the selected translation path.
- Strip navigation, browser-warning, and site-chrome text.
- Preserve Unicode speaker names and diacritics.
- Write one canonical text file in reading order with stable section headings.
- Cache raw HTML locally under `source_texts/buddhist/raw/milindapanha_suttacentral/pages/`.

- [ ] **Step 3: Add the CLI entrypoint**

The script should accept:

```python
parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
parser.add_argument("--clean-text", type=Path, default=CLEAN_TEXT)
parser.add_argument("--translation", choices=["kelly", "tw_rhysdavids"], default="kelly")
parser.add_argument("--limit", type=int)
parser.add_argument("--refresh-downloads", action="store_true")
parser.add_argument("--write-legacy-mirror", action="store_true")
parser.add_argument("--legacy-output", type=Path, default=LEGACY_OUTPUT)
```

- [ ] **Step 4: Run the ingest tests**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_fetch_milinda_suttacentral.py -q`  
Expected: PASS.

### Task 3: Export The Canonical Local Milinda Source Without Touching The Live Legacy File Yet

**Files:**
- Generate: `source_texts/buddhist/raw/milindapanha_suttacentral/index.html`
- Generate: `source_texts/buddhist/raw/milindapanha_suttacentral/pages/*.html`
- Generate: `source_texts/buddhist/raw/milindapanha_suttacentral/export_manifest.json`
- Generate: `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- Modify: `source_texts/buddhist/SOURCES.md`

- [ ] **Step 1: Run the export tool against the full Milinda corpus**

Run: `.venv\Scripts\python tools\source_ingest\fetch_milinda_suttacentral.py --translation kelly --refresh-downloads`  
Expected: raw cache files plus `source_texts/buddhist/clean/milindapanha_suttacentral.txt`.

- [ ] **Step 2: Add provenance to the Buddhist sources note**

Add a source block like:

```md
## Milindapañha / SuttaCentral

- Source: SuttaCentral Milinda section pages, locally cached and consolidated.
- Base URL: `https://suttacentral.net/`
- Translation: John Kelly (primary export), with Rhys Davids as fallback comparison source.
- Local raw cache: `source_texts/buddhist/raw/milindapanha_suttacentral/`
- Local clean export: `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- License/status note: verify SuttaCentral page/public-domain reuse note before final redistribution decisions.
```

- [ ] **Step 3: Verify the export manifest and clean file exist**

Run: `Get-ChildItem source_texts\buddhist\raw\milindapanha_suttacentral -Recurse`  
Expected: index, pages directory, and export manifest present.

### Task 4: Add A Dedicated Milinda Parser On The New Canonical Source

**Files:**
- Create: `src/ai_training_tests/extraction/parsers/milinda_panha.py`
- Create: `scripts/extraction/parse_milinda_panha.py`
- Create: `tests/test_parse_milinda_panha_outputs.py`
- Modify: `tests/test_package_architecture.py`

- [ ] **Step 1: Write a failing parser output smoke test**

```python
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PARSE_MILINDA = REPO_ROOT / "scripts/extraction/parse_milinda_panha.py"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_milinda_parser_writes_dataset_and_review_sample(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(PARSE_MILINDA),
            "--output-dir",
            str(tmp_path),
            "--sample-count",
            "3",
        ],
        cwd=REPO_ROOT,
        check=True,
    )

    dataset_path = tmp_path / "milinda_panha_dialogue.jsonl"
    sample_path = tmp_path / "milinda_panha_dialogue_review_sample.md"

    assert dataset_path.exists()
    assert sample_path.exists()
    assert any(row["metadata"]["source"] == "Milinda Panha" for row in read_jsonl(dataset_path))
```

- [ ] **Step 2: Implement the package parser**

The parser should:

- read `source_texts/buddhist/clean/milindapanha_suttacentral.txt`
- split on stable section headings emitted by the exporter
- extract quoted exchanges with explicit speaker attribution from the cleaner SuttaCentral text
- build `quoted_buddhist_next_reply` rows in the same three-message format already used for Milinda
- write `milinda_panha_dialogue.jsonl` and `milinda_panha_dialogue_review_sample.md`

Expose a package `main()` and a thin wrapper at `scripts/extraction/parse_milinda_panha.py`, following the Asclepius pattern.

- [ ] **Step 3: Extend the package-architecture test for the new wrapper**

Add an assertion block like:

```python
def test_milinda_parser_is_available_from_package_and_legacy_paths() -> None:
    from ai_training_tests.extraction.parsers.milinda_panha import main as package_main
    from scripts.extraction.parse_milinda_panha import main as legacy_main

    assert legacy_main is package_main
```

- [ ] **Step 4: Run the parser smoke test**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_parse_milinda_panha_outputs.py -q`  
Expected: PASS.

### Task 5: Cut Milinda Over From The Base Builder To The Dedicated Parser

**Files:**
- Modify: `scripts/extraction/build_pilot_dialogue_dataset.py`
- Modify: `scripts/extraction/build_full_dialogue_outputs.py`
- Modify: `src/ai_training_tests/domain/source_manifest.py`
- Modify: `scripts/extraction/dialogue_source_manifest.py`
- Modify: `config/dataset_manifest.json`

- [ ] **Step 1: Remove Milinda from the legacy base-builder source list**

Change the base builder so it no longer treats Milinda as part of `BUDDHIST_CUE_SOURCES`.

Expected direction:

```python
BUDDHIST_CUE_SOURCES = []
```

or, if Platform still needs a cue source list, make the list Milinda-free and leave Platform-specific logic intact.

- [ ] **Step 2: Add Milinda as an approved dedicated parser source**

Update `src/ai_training_tests/domain/source_manifest.py` so Milinda changes from:

```python
SourceBuildSpec(
    family="buddhist",
    source_label="Milinda Panha",
    dataset_name="full_dialogue_dataset",
    parser_script=None,
    output_group="base",
)
```

to a dedicated parser spec:

```python
SourceBuildSpec(
    family="buddhist",
    source_label="Milinda Panha",
    dataset_name="milinda_panha_dialogue",
    parser_script="parse_milinda_panha.py",
    output_group="new_buddhist",
)
```

- [ ] **Step 3: Update the dataset manifest to point to the new canonical clean source**

Set:

```json
{
  "source": "Milinda Panha",
  "source_file": "source_texts/buddhist/clean/milindapanha_suttacentral.txt",
  "parser": "scripts/extraction/parse_milinda_panha.py"
}
```

- [ ] **Step 4: Run a full-output smoke build before touching the legacy mirror**

Run: `.venv\Scripts\python scripts\extraction\build_full_dialogue_outputs.py --skip-review-samples`  
Expected: full build completes with Milinda now coming from `milinda_panha_dialogue.jsonl`, not from the base builder.

### Task 6: Replace The Legacy `oritiginal text` Milinda File As A Generated Compatibility Mirror

**Files:**
- Modify: `oritiginal text/Milinda Panha.txt`
- Modify: `tools/source_ingest/fetch_milinda_suttacentral.py`

- [ ] **Step 1: Enable the exporter’s legacy mirror mode**

The exporter should support:

```python
if args.write_legacy_mirror:
    args.legacy_output.write_text(render_consolidated_text(pages), encoding="utf-8")
```

- [ ] **Step 2: Write the legacy mirror only after Task 5 passes**

Run: `.venv\Scripts\python tools\source_ingest\fetch_milinda_suttacentral.py --translation kelly --write-legacy-mirror`  
Expected: `oritiginal text/Milinda Panha.txt` is replaced by the consolidated SuttaCentral export.

- [ ] **Step 3: Verify the legacy file now matches the canonical clean export**

Run:

```powershell
Get-FileHash source_texts\buddhist\clean\milindapanha_suttacentral.txt
Get-FileHash 'oritiginal text\Milinda Panha.txt'
```

Expected: matching hashes.

### Task 7: Wire Review Artifacts And Vault Notes To The New Parser

**Files:**
- Create: `Obsidian/Projects/AI_Training_Tests/Parsers/parse_milinda_panha.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Parsers/base_dialogue_dataset.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Sources/Buddhist Sources.md`

- [ ] **Step 1: Add a dedicated Milinda parser note**

Document:

- code path
- canonical source path
- output path
- SuttaCentral export dependency
- known current limitations

- [ ] **Step 2: Update the parser hub and Buddhist source tables**

Move Milinda from `[[base_dialogue_dataset]]` to `[[parse_milinda_panha]]`.

- [ ] **Step 3: Leave a short note in the base parser page**

Add a migration note such as:

```md
- Milinda Panha no longer belongs to this legacy builder after the SuttaCentral migration.
```

### Task 8: Run Review-Pipeline And Verification Gates

**Files:**
- Generate: `review_outputs/parser_reviews/parse_milinda_panha/`

- [ ] **Step 1: Run the dedicated parser**

Run: `.venv\Scripts\python scripts\extraction\parse_milinda_panha.py --output-dir review_outputs\new_buddhist_sources --sample-count 10`

- [ ] **Step 2: Create the first parser review pass**

Run:

```powershell
.venv\Scripts\python tools\review_pipeline\run_new_parser_pass.py `
  --parser-command ".venv\Scripts\python scripts\extraction\parse_milinda_panha.py --output-dir review_outputs\new_buddhist_sources --sample-count 10" `
  --dataset-path review_outputs\new_buddhist_sources\milinda_panha_dialogue.jsonl `
  --parser-name parse_milinda_panha
```

Expected: `review_outputs/parser_reviews/parse_milinda_panha/set_01/` exists with manifest and review packet.

- [ ] **Step 3: Run focused verification**

Run:

```powershell
.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_fetch_milinda_suttacentral.py tests\test_parse_milinda_panha_outputs.py tests\test_package_architecture.py -q
.venv\Scripts\python scripts\extraction\build_full_dialogue_outputs.py --skip-review-samples
rg -n "Milinda Panha" config\dataset_manifest.json src\ai_training_tests\domain\source_manifest.py Obsidian\Projects\AI_Training_Tests
```

Expected:

- tests pass
- full build completes
- Milinda references now point at the dedicated parser and canonical SuttaCentral clean source

---

## Review Gates

1. Do not overwrite `oritiginal text/Milinda Panha.txt` before the dedicated parser is live in the build.
2. Do not promote new Milinda rows as final solely because the source migration is cleaner.
3. Keep the canonical source at `source_texts/buddhist/clean/milindapanha_suttacentral.txt`; treat the legacy `oritiginal text` file as a generated mirror only.
4. Use the review pipeline after cutover so parser-quality changes are evaluated separately from source-ingest changes.

## Known Risks

- SuttaCentral page structure may shift, so the exporter must be cache-first and test-backed with fixtures.
- Mixing source replacement and parser redesign in one commit would make regressions hard to localize.
- Overwriting the legacy source before removing Milinda from the base builder would mutate the live final dataset without a review gate.
- The SuttaCentral HTML pages may contain navigation or JS/browser-warning text that must be stripped deterministically.

## Success Criteria

- Milinda has a reproducible local raw cache and canonical clean export under `source_texts/buddhist/`.
- `oritiginal text/Milinda Panha.txt` is no longer an OCR artifact; it is a generated mirror of the canonical clean export.
- Milinda is parsed by `scripts/extraction/parse_milinda_panha.py`, not by the legacy base builder.
- The full build still runs successfully after cutover.
- A parser review pass exists for the new Milinda parser, ready for the next improvement cycle.
