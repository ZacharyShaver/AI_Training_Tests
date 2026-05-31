# Digha Nikaya Selected SuttaCentral Dialogues Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new Buddhist candidate dataset from a bounded set of dialogue-heavy Digha Nikaya discourses on SuttaCentral, generate review artifacts, and leave the source clearly positioned as the next promotion candidate without touching the final dataset yet.

**Architecture:** Keep the scope narrow and reuse what already works. Fetch only `DN 2`, `DN 13`, `DN 21`, and `DN 23` from SuttaCentral's Bilara API using Bhikkhu Sujato's English translation, cache the raw JSON payloads locally, render one canonical clean text file, and then parse only conservative attributed exchanges into a candidate JSONL plus review packet. Do not generalize all SuttaCentral ingestion in this pass, and do not promote rows into the final Buddhist dataset.

**Tech Stack:** Python 3.11, stdlib `urllib.request`, `json`, `argparse`, existing SuttaCentral rendering helpers in `tools/source_ingest/fetch_milinda_suttacentral.py`, pytest via `_pytest.config.console_main()`, JSONL, Markdown review artifacts, `tools/review_pipeline/run_new_parser_pass.py`.

---

## Current Constraints

- Milinda's SuttaCentral candidate path was refreshed on 2026-05-30 and reduced to `14` rows, so it is parked rather than extended.
- The next SuttaCentral source needs materially better yield than Milinda while staying bounded enough to review quickly.
- SuttaCentral HTML pages are JavaScript-heavy in generic fetch contexts, so this plan should use API payloads and local raw caches rather than browser-page scraping.
- This pass must stop at candidate outputs and review packets. No final-dataset promotion, no dashboard count update, and no compatibility-builder cutover belong here.
- The current repo already has working helpers for Bilara JSON rendering in `tools/source_ingest/fetch_milinda_suttacentral.py`; reuse them instead of inventing a second rendering path.

## Selected Discourses

- `dn2` - `Samannaphalasutta`
- `dn13` - `Tevijjasutta`
- `dn21` - `Sakkapanhasutta`
- `dn23` - `Payasisutta`

These four are the initial pilot because they are bounded, clearly identifiable, and dialogue-heavy. If the pilot yields strong reviewable rows, later expansion can consider `DN 3` or `DN 5`, but that expansion is explicitly out of scope for this plan.

## Target File Layout

### New Source-Ingest Files

- Create: `tools/source_ingest/fetch_digha_selected_suttacentral.py`
- Create: `tests/test_fetch_digha_selected_suttacentral.py`
- Create: `tests/fixtures/digha_selected_suttacentral/dn2.json`
- Create: `tests/fixtures/digha_selected_suttacentral/dn13.json`
- Create: `tests/fixtures/digha_selected_suttacentral/dn21.json`
- Create: `tests/fixtures/digha_selected_suttacentral/dn23.json`

### New Local Source Artifacts

- Create: `source_texts/buddhist/raw/digha_nikaya_selected_suttacentral/payloads/`
- Create: `source_texts/buddhist/raw/digha_nikaya_selected_suttacentral/export_manifest.json`
- Create: `source_texts/buddhist/clean/digha_nikaya_selected_suttacentral.txt`

### New Parser Files

- Create: `src/ai_training_tests/extraction/parsers/digha_nikaya_selected.py`
- Create: `scripts/extraction/parse_digha_nikaya_selected.py`
- Create: `tests/test_parse_digha_nikaya_selected_outputs.py`

### New Candidate And Review Artifacts

- Generate: `review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue.jsonl`
- Generate: `review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue_review_sample.md`
- Generate: `review_outputs/parser_reviews/parse_digha_nikaya_selected/set_01/`

### Existing Files To Modify

- Modify: `config/dataset_manifest.json`
- Modify: `source_texts/buddhist/SOURCES.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Sources/Buddhist Sources.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- Create: `Obsidian/Projects/AI_Training_Tests/Parsers/parse_digha_nikaya_selected.md`

---

### Task 1: Add Fixture-Backed Tests For The Selected Digha SuttaCentral Fetcher

**Files:**
- Create: `tests/test_fetch_digha_selected_suttacentral.py`
- Create: `tests/fixtures/digha_selected_suttacentral/dn2.json`
- Create: `tests/fixtures/digha_selected_suttacentral/dn13.json`
- Create: `tests/fixtures/digha_selected_suttacentral/dn21.json`
- Create: `tests/fixtures/digha_selected_suttacentral/dn23.json`

- [ ] **Step 1: Write a failing test for the selected UID list and cache naming**

```python
from pathlib import Path

from tools.source_ingest.fetch_digha_selected_suttacentral import (
    SELECTED_UIDS,
    payload_path,
)


def test_selected_uids_and_payload_paths_are_stable() -> None:
    raw_dir = Path("tests/fixtures/digha_selected_suttacentral")

    assert SELECTED_UIDS == ("dn2", "dn13", "dn21", "dn23")
    assert payload_path(raw_dir, "dn21") == raw_dir / "payloads" / "dn21.json"
```

- [ ] **Step 2: Write a failing test for consolidated text rendering from Bilara payloads**

```python
from pathlib import Path

from tools.source_ingest.fetch_digha_selected_suttacentral import render_selected_text


def test_render_selected_text_keeps_discourse_boundaries_and_titles() -> None:
    fixture_dir = Path("tests/fixtures/digha_selected_suttacentral")
    payloads = {
        "dn2": (fixture_dir / "dn2.json").read_text(encoding="utf-8"),
        "dn23": (fixture_dir / "dn23.json").read_text(encoding="utf-8"),
    }

    text = render_selected_text(payloads)

    assert "## dn2" in text
    assert "## dn23" in text
    assert "### The Fruits of the Ascetic Life" in text
    assert "### With Payasi" in text
    assert "unsupported browser" not in text.lower()
```

- [ ] **Step 3: Run the new fetcher tests to verify they fail**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_fetch_digha_selected_suttacentral.py -q`  
Expected: FAIL with import errors because `tools.source_ingest.fetch_digha_selected_suttacentral` does not exist yet.

### Task 2: Implement The Selected Digha SuttaCentral Fetcher

**Files:**
- Create: `tools/source_ingest/fetch_digha_selected_suttacentral.py`

- [ ] **Step 1: Add the selected-discourse fetcher with explicit constants and path helpers**

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urljoin

from tools.source_ingest.fetch_milinda_suttacentral import (
    BASE_URL,
    fetch_html,
    parse_sutta_json_page,
    render_consolidated_text,
    write_export_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "source_texts/buddhist/raw/digha_nikaya_selected_suttacentral"
CLEAN_TEXT = REPO_ROOT / "source_texts/buddhist/clean/digha_nikaya_selected_suttacentral.txt"
SELECTED_UIDS = ("dn2", "dn13", "dn21", "dn23")
TRANSLATION_AUTHOR = "sujato"


def payload_path(raw_dir: Path, uid: str) -> Path:
    return raw_dir / "payloads" / f"{uid}.json"


def payload_url(uid: str) -> str:
    return urljoin(BASE_URL, f"api/bilarasuttas/{uid}/{TRANSLATION_AUTHOR}?lang=en")
```

- [ ] **Step 2: Implement cache loading and consolidated text rendering on top of the existing Milinda helpers**

```python
def cache_payload(uid: str, *, raw_dir: Path, refresh: bool) -> str:
    path = payload_path(raw_dir, uid)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not refresh:
        return path.read_text(encoding="utf-8")
    payload = fetch_html(payload_url(uid))
    path.write_text(payload, encoding="utf-8")
    return payload


def render_selected_text(payloads: dict[str, str]) -> str:
    pages = [parse_sutta_json_page(uid, payloads[uid]) for uid in SELECTED_UIDS]
    return render_consolidated_text([page for page in pages if page is not None])
```

- [ ] **Step 3: Add the CLI entrypoint**

```python
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch selected Digha Nikaya discourses from SuttaCentral."
    )
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--clean-text", type=Path, default=CLEAN_TEXT)
    parser.add_argument("--refresh-downloads", action="store_true")
    args = parser.parse_args()

    raw_dir = args.raw_dir.expanduser().resolve()
    payloads = {
        uid: cache_payload(uid, raw_dir=raw_dir, refresh=args.refresh_downloads)
        for uid in SELECTED_UIDS
    }
    clean_text = render_selected_text(payloads)
    clean_path = args.clean_text.expanduser().resolve()
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    clean_path.write_text(clean_text, encoding="utf-8")
    write_export_manifest(
        raw_dir / "export_manifest.json",
        source="SuttaCentral Digha Nikaya selected dialogues",
        base_url=BASE_URL,
        refs=list(SELECTED_UIDS),
        output_path=clean_path,
        section_translations=[
            {"section_ref": uid, "author_uid": TRANSLATION_AUTHOR, "translation_id": f"{uid}_translation-en-sujato"}
            for uid in SELECTED_UIDS
        ],
    )
```

- [ ] **Step 4: Run the fetcher tests**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_fetch_digha_selected_suttacentral.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit the ingest milestone**

```bash
git add tools/source_ingest/fetch_digha_selected_suttacentral.py tests/test_fetch_digha_selected_suttacentral.py tests/fixtures/digha_selected_suttacentral
git commit -m "feat: add selected digha suttacentral fetcher"
```

### Task 3: Export The Canonical Selected Digha Source And Record Provenance

**Files:**
- Generate: `source_texts/buddhist/raw/digha_nikaya_selected_suttacentral/payloads/*.json`
- Generate: `source_texts/buddhist/raw/digha_nikaya_selected_suttacentral/export_manifest.json`
- Generate: `source_texts/buddhist/clean/digha_nikaya_selected_suttacentral.txt`
- Modify: `source_texts/buddhist/SOURCES.md`

- [ ] **Step 1: Run the fetcher against the selected discourse set**

Run: `.venv\Scripts\python tools\source_ingest\fetch_digha_selected_suttacentral.py --refresh-downloads`  
Expected: four cached JSON payloads plus `source_texts/buddhist/clean/digha_nikaya_selected_suttacentral.txt`.

- [ ] **Step 2: Add a provenance block to `source_texts/buddhist/SOURCES.md`**

```md
## Digha Nikaya Selected Dialogues / SuttaCentral

- Source: SuttaCentral Bilara API payloads for selected Digha Nikaya discourses.
- Selection: `dn2`, `dn13`, `dn21`, `dn23`.
- Translation: Bhikkhu Sujato.
- Local raw cache: `raw/digha_nikaya_selected_suttacentral/`
- Canonical clean export: `clean/digha_nikaya_selected_suttacentral.txt`
- License/status note: the SuttaCentral Digha edition page marks Sujato's translation CC0; keep the export manifest with the exact cached URLs.
```

- [ ] **Step 3: Verify the export manifest and clean text exist**

Run: `Get-ChildItem source_texts\buddhist\raw\digha_nikaya_selected_suttacentral -Recurse`  
Expected: `payloads\`, `export_manifest.json`, and the four discourse payloads are present.

### Task 4: Add Failing Parser Tests For Conservative Dialogue Extraction

**Files:**
- Create: `tests/test_parse_digha_nikaya_selected_outputs.py`

- [ ] **Step 1: Write a failing unit test for turn extraction from the clean selected-DN source format**

```python
from pathlib import Path

from ai_training_tests.extraction.parsers.digha_nikaya_selected import parse_turns


def test_parse_turns_extracts_named_question_answer_pairs(tmp_path: Path) -> None:
    source = tmp_path / "digha_selected_sample.txt"
    source.write_text(
        "\n".join(
            [
                "## dn23",
                "### With Payasi",
                'Then Payasi said, "There is no afterlife."',
                'Kassapa the Prince said, "Can you prove it?"',
                'Payasi said, "I have not seen any being return."',
                'Kassapa the Prince said, "Not seeing is not proof."',
            ]
        ),
        encoding="utf-8",
    )

    turns = parse_turns(source)

    assert [(turn.section_ref, turn.speaker, turn.text) for turn in turns] == [
        ("dn23", "Payasi", "There is no afterlife."),
        ("dn23", "Kassapa the Prince", "Can you prove it?"),
        ("dn23", "Payasi", "I have not seen any being return."),
        ("dn23", "Kassapa the Prince", "Not seeing is not proof."),
    ]
```

- [ ] **Step 2: Write a failing parser smoke test for JSONL and review-sample generation**

```python
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PARSE_DN = REPO_ROOT / "scripts/extraction/parse_digha_nikaya_selected.py"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_selected_digha_parser_writes_dataset_and_review_sample(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(PARSE_DN),
            "--output-dir",
            str(tmp_path),
            "--sample-count",
            "4",
        ],
        cwd=REPO_ROOT,
        check=True,
    )

    dataset_path = tmp_path / "digha_nikaya_selected_dialogue.jsonl"
    sample_path = tmp_path / "digha_nikaya_selected_dialogue_review_sample.md"
    rows = read_jsonl(dataset_path)

    assert dataset_path.exists()
    assert sample_path.exists()
    assert rows
    assert all(row["metadata"]["source"] == "Digha Nikaya selected dialogues" for row in rows)
```

- [ ] **Step 3: Run the new parser tests to verify they fail**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_parse_digha_nikaya_selected_outputs.py -q`  
Expected: FAIL because the parser module and wrapper do not exist yet.

### Task 5: Implement The Selected Digha Dialogue Parser

**Files:**
- Create: `src/ai_training_tests/extraction/parsers/digha_nikaya_selected.py`
- Create: `scripts/extraction/parse_digha_nikaya_selected.py`
- Modify: `tests/test_package_architecture.py`

- [ ] **Step 1: Add the package parser with section parsing, speaker normalization, and turn extraction**

```python
SECTION_RE = re.compile(r"^## (?P<section>dn(?:2|13|21|23))$", re.IGNORECASE)
QUOTE_RE = re.compile(r'"(?P<quote>[^"]+)"')
CANONICAL_SPEAKERS = {
    "the buddha": "The Buddha",
    "the blessed one": "The Buddha",
    "master gotama": "The Buddha",
    "worthy gotama": "The Buddha",
    "king ajatasattu": "King Ajatasattu",
    "ajatasattu": "King Ajatasattu",
    "vasettha": "Vasettha",
    "bharadvaja": "Bharadvaja",
    "sakka": "Sakka",
    "pancasikha": "Pancasikha",
    "payasi": "Payasi",
    "kassapa the prince": "Kassapa the Prince",
}
```

The parser should:

- read `source_texts/buddhist/clean/digha_nikaya_selected_suttacentral.txt`
- split on `## dn...` headings
- recover only explicitly quoted, speaker-attributed turns
- preserve `section_ref` and nearby subheading metadata
- reject narration-only paragraphs and unbounded sermon blocks

- [ ] **Step 2: Implement row construction with conservative history gating**

```python
rows = build_rows(
    turns,
    max_history_turns=6,
    min_target_words=5,
    max_target_words=260,
)
```

Keep the gating rules strict:

- require at least one prior turn
- require the target speaker to differ from the immediately preceding speaker
- require all history turns to come from the same `section_ref`
- reject target replies shorter than 5 words
- keep source-specific metadata such as `section_ref`, `section_title`, and `speakers`

- [ ] **Step 3: Add the thin script wrapper**

```python
#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_training_tests.extraction.parsers.digha_nikaya_selected import main


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the focused parser tests**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_parse_digha_nikaya_selected_outputs.py -q`  
Expected: PASS.

- [ ] **Step 5: Commit the parser milestone**

```bash
git add src/ai_training_tests/extraction/parsers/digha_nikaya_selected.py scripts/extraction/parse_digha_nikaya_selected.py tests/test_parse_digha_nikaya_selected_outputs.py
git commit -m "feat: add selected digha dialogue parser"
```

### Task 6: Generate Candidate Artifacts, First Review Packet, And Candidate Tracking Notes

**Files:**
- Generate: `review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue.jsonl`
- Generate: `review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue_review_sample.md`
- Generate: `review_outputs/parser_reviews/parse_digha_nikaya_selected/set_01/*`
- Modify: `config/dataset_manifest.json`
- Create: `Obsidian/Projects/AI_Training_Tests/Parsers/parse_digha_nikaya_selected.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md`
- Modify: `Obsidian/Projects/AI_Training_Tests/Sources/Buddhist Sources.md`

- [ ] **Step 1: Run the selected Digha parser and generate the candidate JSONL**

Run: `.venv\Scripts\python scripts\extraction\parse_digha_nikaya_selected.py --sample-count 10`  
Expected: `review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue.jsonl` and `review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue_review_sample.md`.

- [ ] **Step 2: Generate the first parser-review packet**

Run: `.venv\Scripts\python tools\review_pipeline\run_new_parser_pass.py --source-jsonl review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue.jsonl --output-dir review_outputs/parser_reviews/parse_digha_nikaya_selected/set_01 --dataset-stem digha_nikaya_selected_dialogue_set_01 --sample-size 10`  
Expected: `sample_manifest.md`, `run_summary.md`, sampled JSONL, and `digha_nikaya_selected_dialogue_set_01_random_review.md`.

- [ ] **Step 3: Update `config/dataset_manifest.json` and the parser/source notes**

Add this `next_sources` entry:

```json
{
  "family": "buddhist",
  "source": "Digha Nikaya selected dialogues (SuttaCentral)",
  "reason": "Bounded pilot on DN 2, DN 13, DN 21, and DN 23; first parser-review packet exists.",
  "current_artifact": "review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue.jsonl"
}
```

Create `Obsidian/Projects/AI_Training_Tests/Parsers/parse_digha_nikaya_selected.md` with:

```md
# parse_digha_nikaya_selected.py

## Parser

- Code: `src/ai_training_tests/extraction/parsers/digha_nikaya_selected.py`
- Wrapper: `scripts/extraction/parse_digha_nikaya_selected.py`
- Canonical source: `source_texts/buddhist/clean/digha_nikaya_selected_suttacentral.txt`
- Candidate outputs: `review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue.jsonl`
- Review pipeline: `review_outputs/parser_reviews/parse_digha_nikaya_selected/`

## Status

candidate
```

- [ ] **Step 4: Update the Buddhist source and parser hub notes**

Record:

- this source is now the next planned Buddhist promotion candidate
- the bounded selection is `DN 2`, `DN 13`, `DN 21`, and `DN 23`
- Milinda remains parked at `14` candidate rows
- no final-dataset promotion has happened yet

- [ ] **Step 5: Run focused verification for the whole pass**

Run: `.venv\Scripts\python -c "from _pytest.config import console_main; raise SystemExit(console_main())" tests\test_fetch_digha_selected_suttacentral.py tests\test_parse_digha_nikaya_selected_outputs.py tests\test_review_pipeline_packet.py -q`  
Expected: PASS.

- [ ] **Step 6: Commit the candidate-artifact and docs milestone**

```bash
git add review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue.jsonl review_outputs/new_buddhist_sources/digha_nikaya_selected_dialogue_review_sample.md review_outputs/parser_reviews/parse_digha_nikaya_selected config/dataset_manifest.json Obsidian/Projects/AI_Training_Tests/Parsers/parse_digha_nikaya_selected.md Obsidian/Projects/AI_Training_Tests/Parsers/Parser Hub.md Obsidian/Projects/AI_Training_Tests/Sources/Buddhist Sources.md source_texts/buddhist/SOURCES.md
git commit -m "feat: add selected digha suttacentral candidate dataset"
```

## Risks And Guardrails

- SuttaCentral may change API payload details; keep fixture-backed tests and raw JSON caches so parser iteration does not depend on the live site.
- These discourses contain long doctrinal stretches; the parser must prefer conservative under-capture over inventing dialogue.
- The selected set may still produce fewer rows than expected. If so, stop after `set_01`, review the failure mode, and decide whether to expand to `DN 3` or `DN 5` rather than weakening parser quality gates.
- Do not update `dashboard/project-progress-data.js` or any final dataset counts in this pass.

## Definition Of Done

- A deterministic local SuttaCentral cache exists for `DN 2`, `DN 13`, `DN 21`, and `DN 23`.
- `source_texts/buddhist/clean/digha_nikaya_selected_suttacentral.txt` is generated and documented.
- `parse_digha_nikaya_selected.py` writes a candidate JSONL and review sample.
- `review_outputs/parser_reviews/parse_digha_nikaya_selected/set_01/` exists with manifest, sampled JSONL, packet, and run summary.
- `config/dataset_manifest.json` and the relevant Obsidian notes point at the new candidate.
- No final dataset promotion or dashboard refresh has been performed.
