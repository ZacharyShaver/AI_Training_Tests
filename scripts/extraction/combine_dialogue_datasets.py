#!/usr/bin/env python3
"""Combine direct-source dialogue JSONL files with record-id de-duplication."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def combine_rows(paths: list[Path]) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    seen: set[str] = set()
    duplicates: list[str] = []

    for path in paths:
        for row in read_jsonl(path):
            record_id = row["metadata"]["record_id"]
            if record_id in seen:
                duplicates.append(record_id)
                continue
            seen.add(record_id)
            rows.append(row)

    return rows, duplicates


def main() -> None:
    parser = argparse.ArgumentParser(description="Combine dialogue JSONL datasets.")
    parser.add_argument("inputs", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    input_paths = [path.expanduser().resolve() for path in args.inputs]
    rows, duplicates = combine_rows(input_paths)
    output = args.output.expanduser().resolve()
    write_jsonl(output, rows)

    source_counts = Counter(row["metadata"]["source"] for row in rows)
    print(f"Inputs: {len(input_paths)}")
    print(f"Rows written: {len(rows)}")
    print(f"Duplicate record ids skipped: {len(duplicates)}")
    for source, count in sorted(source_counts.items()):
        print(f"{source}: {count}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
