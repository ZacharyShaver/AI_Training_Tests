#!/usr/bin/env python3
"""Create a compact Markdown review sample from a JSONL dialogue dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from preview_dialogue_examples import preview_text, select_spread
from review_policy import assess_row, assessment_summary_text


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    assessment = assess_row(row)
    lines = [
        f"## Review Example {index}: {metadata['source']}",
        "",
        f"- Record ID: `{metadata['record_id']}`",
        f"- Kind: `{metadata['kind']}`",
        f"- Lines: `{metadata['source_file']}:{metadata['source_lines'][0]}-{metadata['source_lines'][1]}`",
        f"- Target: `{metadata['target_participant']} ({metadata['target_speaker']})`",
        f"- Target words: `{metadata['target_words']}`",
        f"- Reviewer status: `{assessment.label}`",
        "",
        "### User Prompt",
        "",
        "```text",
        preview_text(row["messages"][1]["content"], limit=preview_chars),
        "```",
        "",
        "### Assistant Target",
        "",
        "```text",
        preview_text(row["messages"][2]["content"], limit=preview_chars),
        "```",
        "",
        "### Review Notes",
        "",
        f"- Summary: `{assessment_summary_text(assessment)}`",
    ]
    if assessment.hard_failures:
        lines.extend(
            [
                "- Hard failures:",
                *[f"  - {item}" for item in assessment.hard_failures],
            ]
        )
    if assessment.warnings:
        lines.extend(
            [
                "- Warnings:",
                *[f"  - {item}" for item in assessment.warnings],
            ]
        )
    lines.extend(
        [
            "",
        ]
    )
    return "\n".join(lines)


def sample_status_summary(rows: list[dict]) -> dict[str, int]:
    counts = {"Approve": 0, "Approve with warning": 0, "Reject": 0}
    for row in rows:
        counts[assess_row(row).label] += 1
    return counts


def render_status_summary(rows: list[dict]) -> list[str]:
    counts = sample_status_summary(rows)
    return [
        "## Review Policy Summary",
        "",
        f"- Approve: `{counts['Approve']}`",
        f"- Approve with warning: `{counts['Approve with warning']}`",
        f"- Reject: `{counts['Reject']}`",
        "",
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a compact dataset review sample.")
    parser.add_argument("input_jsonl", type=Path)
    parser.add_argument("--output-md", type=Path, required=True)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    parser.add_argument(
        "--title",
        default="Dialogue Dataset Review Sample",
        help="Markdown title.",
    )
    args = parser.parse_args()

    rows = [
        json.loads(line)
        for line in args.input_jsonl.expanduser().resolve().read_text(encoding="utf-8").splitlines()
    ]
    selected = select_spread(rows, args.count)

    output = args.output_md.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(
            [
                f"# {args.title}",
                "",
                f"Sampled rows: `{len(selected)}`",
                f"Source dataset: `{args.input_jsonl}`",
                "",
                *render_status_summary(selected),
                *[
                    row_to_markdown(row, idx, preview_chars=args.preview_chars)
                    for idx, row in enumerate(selected, 1)
                ],
            ]
        ),
        encoding="utf-8",
    )
    print(f"Rows sampled: {len(selected)}")
    print(f"Markdown: {output}")


if __name__ == "__main__":
    main()
