from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PARSE_UDANA = REPO_ROOT / "scripts/extraction/parse_udana.py"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_default_udana_parser_writes_separate_row_family_artifacts(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            str(PARSE_UDANA),
            "--output-dir",
            str(tmp_path),
            "--sample-count",
            "3",
            "--preview-chars",
            "300",
        ],
        cwd=REPO_ROOT,
        check=True,
    )

    exclamation_path = tmp_path / "udana_exclamation_dialogue.jsonl"
    direct_path = tmp_path / "udana_direct_dialogue.jsonl"
    legacy_mixed_path = tmp_path / "udana_dialogue.jsonl"

    assert exclamation_path.exists()
    assert direct_path.exists()
    assert not legacy_mixed_path.exists()
    assert (tmp_path / "udana_exclamation_dialogue_review_sample.md").exists()
    assert (tmp_path / "udana_direct_dialogue_review_sample.md").exists()

    exclamation_kinds = {
        row["metadata"]["kind"] for row in read_jsonl(exclamation_path)
    }
    direct_kinds = {row["metadata"]["kind"] for row in read_jsonl(direct_path)}

    assert exclamation_kinds == {"udana_blessed_one_exclamation"}
    assert direct_kinds == {"udana_blessed_one_direct_reply"}
