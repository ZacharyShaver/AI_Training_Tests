from __future__ import annotations

import json
from pathlib import Path

from tools.review_pipeline.random_sample import create_random_sample, sample_rows


def make_row(index: int) -> dict:
    return {
        "messages": [
            {"role": "system", "content": "System"},
            {"role": "user", "content": f"Conversation so far:\nParticipant A: Prompt {index}"},
            {"role": "assistant", "content": f"Reply {index}"},
        ],
        "metadata": {
            "record_id": f"row-{index:02d}",
            "source": "Example Source",
            "source_file": "example.txt",
            "source_lines": [index, index + 1],
            "target_speaker": "Teacher",
            "target_participant": "Participant B",
            "target_words": 2,
        },
    }


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def record_ids(rows: list[dict]) -> list[str]:
    return [row["metadata"]["record_id"] for row in rows]


def test_sample_rows_is_deterministic_for_fixed_seed() -> None:
    rows = [make_row(index) for index in range(20)]

    first = sample_rows(rows, sample_size=5, seed=123)
    second = sample_rows(rows, sample_size=5, seed=123)
    different_seed = sample_rows(rows, sample_size=5, seed=124)

    assert record_ids(first) == record_ids(second)
    assert record_ids(first) != record_ids(different_seed)
    assert len(first) == 5


def test_create_random_sample_writes_jsonl_and_manifest(tmp_path: Path) -> None:
    source_path = tmp_path / "source.jsonl"
    sample_path = tmp_path / "set_01" / "source_set_01.jsonl"
    manifest_path = tmp_path / "set_01" / "sample_manifest.md"
    rows = [make_row(index) for index in range(3)]
    write_jsonl(source_path, rows)

    result = create_random_sample(
        source_path=source_path,
        output_jsonl_path=sample_path,
        manifest_path=manifest_path,
        sample_size=10,
        seed=20260525,
        generated_at="2026-05-25T12:00:00Z",
    )

    assert result.sampling_mode == "small population"
    assert record_ids(result.rows) == ["row-00", "row-01", "row-02"]
    assert sample_path.read_text(encoding="utf-8").count("\n") == 3

    manifest = manifest_path.read_text(encoding="utf-8")
    assert "Seed: `20260525`" in manifest
    assert "Source file: `source.jsonl`" in manifest
    assert "Row count: `3`" in manifest
    assert "Sampling mode: `small population`" in manifest
    assert "- `row-00`" in manifest

