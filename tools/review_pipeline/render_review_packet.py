from __future__ import annotations

import argparse
from pathlib import Path

from tools.review_pipeline.random_sample import load_jsonl


DEFAULT_CRITERIA = [
    "Prompt and reply preserve source continuity.",
    "Speaker labels are coherent and not malformed.",
    "Assistant target is the next reply only.",
    "No page headers, footnotes, OCR bleed, or commentary contamination.",
]


def render_review_packet(
    *,
    rows: list[dict],
    source_jsonl_path: Path,
    criteria: list[str] | None = None,
) -> str:
    criteria = criteria or DEFAULT_CRITERIA
    lines = [
        "# Random Sample Review Packet",
        "",
        f"Source JSONL: `{source_jsonl_path.as_posix()}`",
        f"Rows: `{len(rows)}`",
        "",
        "## Reviewer Criteria",
        "",
    ]
    lines.extend(f"- {item}" for item in criteria)
    lines.extend(["", "## Rows", ""])

    for index, row in enumerate(rows, start=1):
        metadata = row.get("metadata") or {}
        messages = row.get("messages") or []
        user_message = messages[1]["content"] if len(messages) > 1 else ""
        assistant_message = messages[2]["content"] if len(messages) > 2 else ""
        target = f"{metadata.get('target_participant')} ({metadata.get('target_speaker')})"

        lines.extend(
            [
                f"### Row {index}",
                "",
                f"- Record ID: `{metadata.get('record_id')}`",
                f"- Source: `{metadata.get('source')}`",
                f"- Source file: `{metadata.get('source_file')}`",
                f"- Source lines: `{metadata.get('source_lines')}`",
                f"- Assistant target: `{target}`",
                "",
                "#### Prompt",
                "",
                "```text",
                user_message,
                "```",
                "",
                "#### Assistant Target",
                "",
                "```text",
                assistant_message,
                "```",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def write_review_packet(
    *,
    source_jsonl_path: Path,
    output_path: Path,
    criteria: list[str] | None = None,
) -> str:
    rows = load_jsonl(source_jsonl_path)
    packet = render_review_packet(
        rows=rows,
        source_jsonl_path=source_jsonl_path,
        criteria=criteria,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(packet, encoding="utf-8")
    return packet


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a Markdown review packet from JSONL rows.")
    parser.add_argument("source_jsonl_path", type=Path)
    parser.add_argument("output_path", type=Path)
    args = parser.parse_args()

    write_review_packet(source_jsonl_path=args.source_jsonl_path, output_path=args.output_path)
    print(f"Wrote review packet to {args.output_path}")


if __name__ == "__main__":
    main()

