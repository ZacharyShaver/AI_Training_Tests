#!/usr/bin/env python3
"""Convert QA-style JSONL datasets into Alpaca-format JSONL files.

Each input record is expected to contain at least:
  - question
  - answer

The script scans a directory for .jsonl files and writes matching
*_alpaca.jsonl files into an output directory.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def build_instruction(record: dict[str, Any]) -> str:
    lines: list[str] = []

    source_text = record.get("source_text")
    if source_text:
        lines.append(f"Answer the question from {source_text}.")
    else:
        lines.append("Answer the question.")

    part = record.get("part")
    if part:
        lines.append(f"Part: {part}")

    section_num = record.get("section_num")
    section_title = record.get("section_title")
    section = record.get("section")
    if section_num and section_title:
        lines.append(f"Section {section_num}: {section_title}")
    elif section_title:
        lines.append(f"Section: {section_title}")
    elif section:
        lines.append(f"Section: {section}")

    chapter = record.get("chapter")
    if chapter:
        lines.append(f"Chapter: {chapter}")

    questioner = record.get("questioner")
    if questioner:
        lines.append(f"Questioner: {questioner}")

    answerer = record.get("answerer")
    if answerer:
        lines.append(f"Answerer: {answerer}")

    return "\n".join(lines)


def convert_record(record: dict[str, Any]) -> dict[str, str]:
    question = str(record.get("question", "")).strip()
    answer = str(record.get("answer", "")).strip()

    if not question or not answer:
        raise ValueError("Record is missing a non-empty question or answer field.")

    return {
        "instruction": build_instruction(record),
        "input": question,
        "output": answer,
    }


def convert_file(input_path: Path, output_path: Path) -> tuple[int, int]:
    converted = 0
    skipped = 0

    with input_path.open("r", encoding="utf-8") as infile, output_path.open(
        "w", encoding="utf-8"
    ) as outfile:
        for line_number, line in enumerate(infile, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
                alpaca_record = convert_record(record)
            except Exception as exc:
                skipped += 1
                print(f"[skip] {input_path.name}:{line_number} -> {exc}")
                continue

            outfile.write(json.dumps(alpaca_record, ensure_ascii=False) + "\n")
            converted += 1

    return converted, skipped


def iter_input_files(input_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in input_dir.glob("*.jsonl")
        if not path.name.endswith("_alpaca.jsonl")
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert JSONL QA files into Alpaca-format JSONL files."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=".",
        help="Directory containing source .jsonl files. Defaults to current directory.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for converted files. Defaults to the input directory.",
    )
    args = parser.parse_args()

    input_dir = Path(args.input_dir).expanduser().resolve()
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else input_dir
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    input_files = iter_input_files(input_dir)
    if not input_files:
        print(f"No source .jsonl files found in {input_dir}")
        return

    total_converted = 0
    total_skipped = 0

    for input_path in input_files:
        output_path = output_dir / f"{input_path.stem}_alpaca.jsonl"
        converted, skipped = convert_file(input_path, output_path)
        total_converted += converted
        total_skipped += skipped
        print(
            f"[done] {input_path.name} -> {output_path.name} "
            f"(converted={converted}, skipped={skipped})"
        )

    print(
        f"Finished. Converted {total_converted} records; skipped {total_skipped} records."
    )


if __name__ == "__main__":
    main()
