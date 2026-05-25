#!/usr/bin/env python3
"""Validate direct-source dialogue JSONL datasets."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

from build_pilot_dialogue_dataset import count_dataset_words


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATASET_DIR = REPO_ROOT / "review_outputs/full_dialogue_dataset"

EXPECTED_ROLES = ("system", "user", "assistant")
REQUIRED_METADATA_FIELDS = (
    "record_id",
    "kind",
    "source",
    "source_file",
    "source_lines",
    "target_speaker",
    "target_participant",
    "target_words",
)
TARGET_WORD_BUCKETS = (
    (0, 19, "0-19"),
    (20, 49, "20-49"),
    (50, 99, "50-99"),
    (100, 199, "100-199"),
    (200, 399, "200-399"),
    (400, 699, "400-699"),
    (700, None, "700+"),
)


@dataclass
class DatasetValidation:
    name: str
    path: Path
    rows: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duplicate_record_ids: list[str] = field(default_factory=list)


def count_words(text: str) -> int:
    return count_dataset_words(text)


def bucket_target_words(word_count: int) -> str:
    for low, high, label in TARGET_WORD_BUCKETS:
        if word_count >= low and (high is None or word_count <= high):
            return label
    return "unknown"


def read_jsonl(path: Path, name: str) -> DatasetValidation:
    result = DatasetValidation(name=name, path=path)
    if not path.exists():
        result.errors.append(f"{path}: file does not exist")
        return result

    seen: set[str] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            result.errors.append(f"{path}:{line_number}: blank JSONL line")
            continue

        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            result.errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue

        if not isinstance(row, dict):
            result.errors.append(f"{path}:{line_number}: row is not a JSON object")
            continue

        metadata = row.get("metadata")
        record_id = metadata.get("record_id") if isinstance(metadata, dict) else None
        if isinstance(record_id, str):
            if record_id in seen:
                result.duplicate_record_ids.append(record_id)
            seen.add(record_id)

        validate_row_shape(row, result, line_number)
        result.rows.append(row)

    if result.duplicate_record_ids:
        result.errors.append(
            f"{path}: duplicate record_id values: {len(result.duplicate_record_ids)}"
        )

    return result


def validate_row_shape(row: dict, result: DatasetValidation, line_number: int) -> None:
    path = result.path
    messages = row.get("messages")
    metadata = row.get("metadata")

    if not isinstance(messages, list):
        result.errors.append(f"{path}:{line_number}: messages is not a list")
    elif len(messages) != len(EXPECTED_ROLES):
        result.errors.append(
            f"{path}:{line_number}: messages has {len(messages)} entries, expected 3"
        )
    else:
        roles = tuple(
            message.get("role") if isinstance(message, dict) else None
            for message in messages
        )
        if roles != EXPECTED_ROLES:
            result.errors.append(
                f"{path}:{line_number}: message roles are {roles}, expected {EXPECTED_ROLES}"
            )
        for idx, message in enumerate(messages):
            if not isinstance(message, dict):
                result.errors.append(
                    f"{path}:{line_number}: messages[{idx}] is not an object"
                )
                continue
            content = message.get("content")
            if not isinstance(content, str) or not content.strip():
                result.errors.append(
                    f"{path}:{line_number}: messages[{idx}].content is empty or not a string"
                )

    if not isinstance(metadata, dict):
        result.errors.append(f"{path}:{line_number}: metadata is not an object")
        return

    missing = [field for field in REQUIRED_METADATA_FIELDS if field not in metadata]
    if missing:
        result.errors.append(f"{path}:{line_number}: missing metadata fields: {missing}")
        return

    if not isinstance(metadata["record_id"], str) or not metadata["record_id"].strip():
        result.errors.append(f"{path}:{line_number}: metadata.record_id is invalid")
    if not isinstance(metadata["source"], str) or not metadata["source"].strip():
        result.errors.append(f"{path}:{line_number}: metadata.source is invalid")
    if not isinstance(metadata["kind"], str) or not metadata["kind"].strip():
        result.errors.append(f"{path}:{line_number}: metadata.kind is invalid")

    source_lines = metadata["source_lines"]
    if (
        not isinstance(source_lines, list)
        or len(source_lines) != 2
        or not all(isinstance(value, int) for value in source_lines)
    ):
        result.errors.append(
            f"{path}:{line_number}: metadata.source_lines must be a two-item integer list"
        )

    target_words = metadata["target_words"]
    if not isinstance(target_words, int) or target_words < 1:
        result.errors.append(f"{path}:{line_number}: metadata.target_words is invalid")
        return

    if isinstance(messages, list) and len(messages) == len(EXPECTED_ROLES):
        assistant_content = (
            messages[2].get("content", "") if isinstance(messages[2], dict) else ""
        )
        actual_words = (
            count_words(assistant_content) if isinstance(assistant_content, str) else 0
        )
        if actual_words and abs(actual_words - target_words) > 3:
            result.warnings.append(
                f"{path}:{line_number}: target_words={target_words}, counted={actual_words}"
            )


def record_ids(rows: Iterable[dict]) -> set[str]:
    ids: set[str] = set()
    for row in rows:
        metadata = row.get("metadata")
        if isinstance(metadata, dict) and isinstance(metadata.get("record_id"), str):
            ids.add(metadata["record_id"])
    return ids


def source_counts(rows: list[dict]) -> Counter:
    return Counter(
        row["metadata"]["source"]
        for row in rows
        if isinstance(row.get("metadata"), dict)
        and isinstance(row["metadata"].get("source"), str)
    )


def target_word_counts(rows: list[dict]) -> Counter:
    counts: Counter = Counter()
    for row in rows:
        metadata = row.get("metadata")
        if not isinstance(metadata, dict):
            continue
        target_words = metadata.get("target_words")
        if isinstance(target_words, int):
            counts[bucket_target_words(target_words)] += 1
    return counts


def validate_split(
    full: DatasetValidation,
    train: DatasetValidation,
    eval_rows: DatasetValidation,
) -> list[str]:
    errors: list[str] = []
    full_ids = record_ids(full.rows)
    train_ids = record_ids(train.rows)
    eval_ids = record_ids(eval_rows.rows)

    overlap = train_ids & eval_ids
    if overlap:
        errors.append(
            f"{train.path} and {eval_rows.path}: train/eval overlap: {len(overlap)} record ids"
        )

    missing_from_full = (train_ids | eval_ids) - full_ids
    if missing_from_full:
        errors.append(
            f"{full.path}: train/eval ids missing from full dataset: {len(missing_from_full)}"
        )

    unsplit_full_ids = full_ids - (train_ids | eval_ids)
    if unsplit_full_ids:
        errors.append(
            f"{full.path}: full rows absent from train/eval split: {len(unsplit_full_ids)}"
        )

    return errors


def default_dataset_groups(dataset_dir: Path) -> list[tuple[str, Path, Path, Path]]:
    return [
        (
            "Combined",
            dataset_dir / "full_combined_dialogue_dataset.jsonl",
            dataset_dir / "full_combined_dialogue_dataset_train.jsonl",
            dataset_dir / "full_combined_dialogue_dataset_eval.jsonl",
        ),
        (
            "Buddhist",
            dataset_dir / "full_buddhist_dialogue_dataset.jsonl",
            dataset_dir / "full_buddhist_dialogue_dataset_train.jsonl",
            dataset_dir / "full_buddhist_dialogue_dataset_eval.jsonl",
        ),
        (
            "Esoteric",
            dataset_dir / "full_esoteric_dialogue_dataset.jsonl",
            dataset_dir / "full_esoteric_dialogue_dataset_train.jsonl",
            dataset_dir / "full_esoteric_dialogue_dataset_eval.jsonl",
        ),
    ]


def render_counter(counter: Counter, preferred_order: Iterable[str] | None = None) -> list[str]:
    if preferred_order is None:
        items = sorted(counter.items())
    else:
        items = [(label, counter[label]) for label in preferred_order if counter[label]]
    return [f"- `{label}`: `{count}`" for label, count in items]


def render_dataset_report(result: DatasetValidation) -> str:
    lines = [
        f"### {result.name}",
        "",
        f"- File: `{result.path}`",
        f"- Rows: `{len(result.rows)}`",
        f"- Errors: `{len(result.errors)}`",
        f"- Warnings: `{len(result.warnings)}`",
        "",
        "#### Sources",
        "",
        *render_counter(source_counts(result.rows)),
        "",
        "#### Target Word Buckets",
        "",
        *render_counter(
            target_word_counts(result.rows),
            [label for _, _, label in TARGET_WORD_BUCKETS],
        ),
    ]

    if result.duplicate_record_ids:
        lines.extend(
            [
                "",
                "#### Duplicate Record IDs",
                "",
                *[f"- `{record_id}`" for record_id in result.duplicate_record_ids[:20]],
            ]
        )
        if len(result.duplicate_record_ids) > 20:
            lines.append(f"- ... {len(result.duplicate_record_ids) - 20} more")

    return "\n".join(lines)


def render_issue_section(title: str, issues: list[str]) -> str:
    if not issues:
        return "\n".join([f"## {title}", "", "None."])

    lines = [f"## {title}", ""]
    lines.extend(f"- {issue}" for issue in issues[:100])
    if len(issues) > 100:
        lines.append(f"- ... {len(issues) - 100} more")
    return "\n".join(lines)


def validate_dataset_groups(
    groups: list[tuple[str, Path, Path, Path]],
) -> tuple[list[DatasetValidation], list[str]]:
    results: list[DatasetValidation] = []
    split_errors: list[str] = []

    for name, full_path, train_path, eval_path in groups:
        full = read_jsonl(full_path, f"{name} Full")
        train = read_jsonl(train_path, f"{name} Train")
        eval_rows = read_jsonl(eval_path, f"{name} Eval")
        results.extend([full, train, eval_rows])

        if not full.errors and not train.errors and not eval_rows.errors:
            split_errors.extend(validate_split(full, train, eval_rows))

    return results, split_errors


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate dialogue dataset JSONL outputs.")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        help="Folder containing full_*_dialogue_dataset JSONL outputs.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="Optional path for a Markdown validation report.",
    )
    args = parser.parse_args()

    dataset_dir = args.dataset_dir.expanduser().resolve()
    results, split_errors = validate_dataset_groups(default_dataset_groups(dataset_dir))

    all_errors = [error for result in results for error in result.errors]
    all_warnings = [warning for result in results for warning in result.warnings]
    all_errors.extend(split_errors)

    report = "\n\n".join(
        [
            "# Dialogue Dataset Validation",
            f"Dataset directory: `{dataset_dir}`",
            f"Validated files: `{len(results)}`",
            f"Total errors: `{len(all_errors)}`",
            f"Total warnings: `{len(all_warnings)}`",
            *[render_dataset_report(result) for result in results],
            render_issue_section("Errors", all_errors),
            render_issue_section("Warnings", all_warnings),
        ]
    )

    print(report)
    if args.output_md:
        output_md = args.output_md.expanduser().resolve()
        write_report(output_md, report)
        print(f"\nReport written: {output_md}")

    if all_errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
