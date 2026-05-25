from __future__ import annotations

import json
from pathlib import Path

from tools.dashboard.build_progress_data import (
    build_progress_data,
    count_jsonl_rows,
    write_project_progress_js,
)


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def make_row(record_id: str, source: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "Conversation so far:\nParticipant A: Test"},
            {"role": "assistant", "content": "Reply"},
        ],
        "metadata": {
            "record_id": record_id,
            "source": source,
        },
    }


def test_count_jsonl_rows_counts_non_empty_lines(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "rows.jsonl"
    jsonl_path.write_text('{"a": 1}\n\n{"a": 2}\n', encoding="utf-8")

    assert count_jsonl_rows(jsonl_path) == 2


def test_build_progress_data_counts_totals_and_sources_by_family(tmp_path: Path) -> None:
    buddhist_path = tmp_path / "buddhist.jsonl"
    occult_path = tmp_path / "occult.jsonl"
    combined_path = tmp_path / "combined.jsonl"
    write_jsonl(
        buddhist_path,
        [
            make_row("b1", "Source A"),
            make_row("b2", "Source A"),
            make_row("b3", "Source B"),
        ],
    )
    write_jsonl(occult_path, [make_row("o1", "Source C")])
    write_jsonl(
        combined_path,
        [
            make_row("b1", "Source A"),
            make_row("b2", "Source A"),
            make_row("b3", "Source B"),
            make_row("o1", "Source C"),
        ],
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "goals": {"buddhist_lines": 5, "occult_lines": 5},
                "source_groups": {
                    "buddhist": {"label": "Buddhist", "target_lines": 5},
                    "occult": {"label": "Occult", "target_lines": 5},
                },
                "final_datasets": {
                    "buddhist": {
                        "family": "buddhist",
                        "label": "Buddhist",
                        "path": str(buddhist_path.relative_to(tmp_path)),
                    },
                    "occult": {
                        "family": "occult",
                        "label": "Occult",
                        "path": str(occult_path.relative_to(tmp_path)),
                    },
                    "combined": {
                        "family": "combined",
                        "label": "Combined",
                        "path": str(combined_path.relative_to(tmp_path)),
                    },
                },
                "sources": [
                    {
                        "family": "buddhist",
                        "source": "Source A",
                        "final_dataset": str(buddhist_path.relative_to(tmp_path)),
                        "parser": "scripts/extraction/parse_a.py",
                        "vault_note": "Obsidian/Projects/AI_Training_Tests/Parsers/parse_a.md",
                        "status": "final",
                    },
                    {
                        "family": "buddhist",
                        "source": "Source B",
                        "final_dataset": str(buddhist_path.relative_to(tmp_path)),
                        "parser": "scripts/extraction/parse_b.py",
                        "vault_note": "Obsidian/Projects/AI_Training_Tests/Parsers/parse_b.md",
                        "status": "final",
                    },
                    {
                        "family": "occult",
                        "source": "Source C",
                        "final_dataset": str(occult_path.relative_to(tmp_path)),
                        "parser": "scripts/extraction/parse_c.py",
                        "vault_note": "Obsidian/Projects/AI_Training_Tests/Parsers/parse_c.md",
                        "status": "final",
                    },
                ],
                "next_sources": [],
                "stale_docs": [],
                "cleanup_notices": [],
            }
        ),
        encoding="utf-8",
    )

    progress = build_progress_data(
        manifest_path=manifest_path,
        repo_root=tmp_path,
        generated_at="2026-05-25",
    )

    assert progress["totals"] == {
        "buddhist_lines": 3,
        "occult_lines": 1,
        "combined_lines": 4,
    }
    assert progress["source_groups"]["buddhist"]["lines"] == 3
    assert progress["source_groups"]["occult"]["lines"] == 1
    assert {
        (source["family"], source["source"], source["rows"])
        for source in progress["sources"]
    } == {
        ("buddhist", "Source A", 2),
        ("buddhist", "Source B", 1),
        ("occult", "Source C", 1),
    }


def test_write_project_progress_js_writes_browser_global(tmp_path: Path) -> None:
    output_path = tmp_path / "project-progress-data.js"

    write_project_progress_js({"totals": {"combined_lines": 4}}, output_path)

    output = output_path.read_text(encoding="utf-8")
    assert output.startswith("window.PROJECT_PROGRESS = ")
    assert '"combined_lines": 4' in output
