#!/usr/bin/env python3
"""Split a dialogue JSONL dataset into practical training outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


ESOTERIC_SOURCES = {"The Key to Theosophy", "The Corpus Hermeticum", "Asclepius"}
BUDDHIST_SOURCES = {
    "Milinda Panha",
    "Platform Sutra",
    "The Gateless Gate",
    "The Diamond Sutra",
    "Udana",
    "Sutta Nipata",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def split_group_train_eval(
    rows: list[dict], *, eval_ratio: float
) -> tuple[list[dict], list[dict]]:
    if not rows:
        return [], []

    eval_every = round(1 / eval_ratio) if eval_ratio > 0 else 0
    if eval_every < 2:
        return rows, []

    train: list[dict] = []
    eval_rows: list[dict] = []
    for idx, row in enumerate(rows, 1):
        target = eval_rows if idx % eval_every == 0 else train
        target.append(row)

    if not eval_rows and len(rows) > 1:
        eval_rows.append(train.pop())
    return train, eval_rows


def split_train_eval(rows: list[dict], *, eval_ratio: float) -> tuple[list[dict], list[dict]]:
    """Create a deterministic source-stratified train/eval split."""
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["metadata"]["source"], []).append(row)

    train: list[dict] = []
    eval_rows: list[dict] = []
    for source in sorted(grouped):
        source_train, source_eval = split_group_train_eval(
            grouped[source], eval_ratio=eval_ratio
        )
        train.extend(source_train)
        eval_rows.extend(source_eval)

    return train, eval_rows


def dataset_stats(rows: list[dict]) -> dict[str, Counter]:
    return {
        "sources": Counter(row["metadata"]["source"] for row in rows),
        "kinds": Counter(row["metadata"]["kind"] for row in rows),
        "speakers": Counter(row["metadata"]["target_speaker"] for row in rows),
    }


def stats_markdown(name: str, rows: list[dict], train: list[dict], eval_rows: list[dict]) -> str:
    stats = dataset_stats(rows)
    lines = [
        f"## {name}",
        "",
        f"- Total rows: `{len(rows)}`",
        f"- Train rows: `{len(train)}`",
        f"- Eval rows: `{len(eval_rows)}`",
        "",
        "### Sources",
        "",
    ]
    for source, count in sorted(stats["sources"].items()):
        lines.append(f"- `{source}`: `{count}`")

    lines.extend(["", "### Kinds", ""])
    for kind, count in sorted(stats["kinds"].items()):
        lines.append(f"- `{kind}`: `{count}`")

    lines.extend(["", "### Target Speakers", ""])
    for speaker, count in sorted(stats["speakers"].items()):
        lines.append(f"- `{speaker}`: `{count}`")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Split full dialogue dataset outputs.")
    parser.add_argument("input_jsonl", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--eval-ratio", type=float, default=0.1)
    args = parser.parse_args()

    rows = read_jsonl(args.input_jsonl.expanduser().resolve())
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    datasets = {
        "full_combined_dialogue_dataset": rows,
        "full_esoteric_dialogue_dataset": [
            row for row in rows if row["metadata"]["source"] in ESOTERIC_SOURCES
        ],
        "full_buddhist_dialogue_dataset": [
            row for row in rows if row["metadata"]["source"] in BUDDHIST_SOURCES
        ],
    }

    report_parts = [
        "# Full Dialogue Dataset Splits",
        "",
        "These files use the reviewed direct-source conversation format.",
    ]

    for name, dataset_rows in datasets.items():
        train, eval_rows = split_train_eval(dataset_rows, eval_ratio=args.eval_ratio)
        write_jsonl(output_dir / f"{name}.jsonl", dataset_rows)
        write_jsonl(output_dir / f"{name}_train.jsonl", train)
        write_jsonl(output_dir / f"{name}_eval.jsonl", eval_rows)
        report_parts.extend(["", stats_markdown(name, dataset_rows, train, eval_rows)])

    report_path = output_dir / "full_dialogue_dataset_splits.md"
    report_path.write_text("\n".join(report_parts) + "\n", encoding="utf-8")
    print(f"Input rows: {len(rows)}")
    for name, dataset_rows in datasets.items():
        train, eval_rows = split_train_eval(dataset_rows, eval_ratio=args.eval_ratio)
        print(f"{name}: total={len(dataset_rows)} train={len(train)} eval={len(eval_rows)}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
