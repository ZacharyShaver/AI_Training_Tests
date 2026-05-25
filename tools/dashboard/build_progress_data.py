#!/usr/bin/env python3
"""Build browser-readable progress data from live JSONL files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST_PATH = REPO_ROOT / "config/dataset_manifest.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "dashboard/project-progress-data.js"


def count_jsonl_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL in {path} at line {line_number}") from exc
    return rows


def repo_path(repo_root: Path, path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return repo_root / path


def source_counts_by_dataset(manifest: dict[str, Any], repo_root: Path) -> dict[str, Counter[str]]:
    dataset_paths = {
        source["final_dataset"]
        for source in manifest.get("sources", [])
        if source.get("final_dataset")
    }
    counts: dict[str, Counter[str]] = {}
    for dataset_path in dataset_paths:
        counter: Counter[str] = Counter()
        for row in read_jsonl(repo_path(repo_root, dataset_path)):
            source = row.get("metadata", {}).get("source")
            if source:
                counter[source] += 1
        counts[dataset_path] = counter
    return counts


def build_progress_data(
    *,
    manifest_path: Path = DEFAULT_MANIFEST_PATH,
    repo_root: Path = REPO_ROOT,
    generated_at: str | None = None,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    final_datasets = manifest["final_datasets"]
    totals = {
        f"{dataset['family']}_lines": count_jsonl_rows(repo_path(repo_root, dataset["path"]))
        for dataset in final_datasets.values()
    }

    source_groups: dict[str, dict[str, Any]] = {}
    for family, group in manifest.get("source_groups", {}).items():
        source_groups[family] = {
            **group,
            "family": family,
            "lines": totals.get(f"{family}_lines", 0),
        }

    counts_by_dataset = source_counts_by_dataset(manifest, repo_root)
    sources = []
    for source in manifest.get("sources", []):
        source_count = counts_by_dataset[source["final_dataset"]][source["source"]]
        sources.append({**source, "rows": source_count})

    return {
        "generated_at": generated_at or date.today().isoformat(),
        "goals": manifest["goals"],
        "totals": totals,
        "source_groups": source_groups,
        "sources": sources,
        "next_sources": manifest.get("next_sources", []),
        "stale_docs": manifest.get("stale_docs", []),
        "cleanup_notices": manifest.get("cleanup_notices", []),
    }


def write_project_progress_js(data: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    output_path.write_text(f"window.PROJECT_PROGRESS = {payload};\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build dashboard progress data.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    manifest_path = args.manifest.expanduser().resolve()
    output_path = args.output.expanduser().resolve()

    data = build_progress_data(manifest_path=manifest_path, repo_root=repo_root)
    write_project_progress_js(data, output_path)
    print(f"Wrote dashboard data: {output_path}")


if __name__ == "__main__":
    main()
