#!/usr/bin/env python3
"""Build MLX-ready train/valid JSONL files from Alpaca-format JSONL files."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


def iter_alpaca_files(input_dir: Path) -> list[Path]:
    return sorted(input_dir.glob("*_alpaca.jsonl"))


def build_prompt(record: dict[str, Any]) -> str:
    instruction = str(record.get("instruction", "")).strip()
    input_text = str(record.get("input", "")).strip()

    if instruction and input_text:
        return f"{instruction}\n\n{input_text}"
    if instruction:
        return instruction
    if input_text:
        return input_text
    raise ValueError("Record is missing both instruction and input.")


def convert_record(record: dict[str, Any]) -> dict[str, str]:
    prompt = build_prompt(record)
    completion = str(record.get("output", "")).strip()
    if not completion:
        raise ValueError("Record is missing a non-empty output field.")
    return {"prompt": prompt, "completion": completion}


def load_examples(input_files: list[Path]) -> tuple[list[dict[str, str]], int]:
    examples: list[dict[str, str]] = []
    skipped = 0

    for path in input_files:
        with path.open("r", encoding="utf-8") as infile:
            for line_number, line in enumerate(infile, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    examples.append(convert_record(record))
                except Exception as exc:
                    skipped += 1
                    print(f"[skip] {path.name}:{line_number} -> {exc}")

    return examples, skipped


def write_jsonl(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as outfile:
        for row in rows:
            outfile.write(json.dumps(row, ensure_ascii=False) + "\n")


def split_examples(
    examples: list[dict[str, str]], valid_ratio: float, seed: int
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    shuffled = examples[:]
    random.Random(seed).shuffle(shuffled)

    if not shuffled:
        return [], []

    valid_count = int(len(shuffled) * valid_ratio)
    if valid_ratio > 0 and valid_count == 0 and len(shuffled) > 1:
        valid_count = 1
    if valid_count >= len(shuffled):
        valid_count = max(1, len(shuffled) - 1)

    valid_rows = shuffled[:valid_count]
    train_rows = shuffled[valid_count:]
    return train_rows, valid_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge Alpaca JSONL files into MLX train/valid completions datasets."
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=".",
        help="Directory containing *_alpaca.jsonl files. Defaults to current directory.",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory where train.jsonl and valid.jsonl will be written.",
    )
    parser.add_argument(
        "--valid-ratio",
        type=float,
        default=0.1,
        help="Fraction of examples to place in valid.jsonl. Default: 0.1",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for shuffling before the split. Default: 42",
    )
    args = parser.parse_args()

    if not 0 <= args.valid_ratio < 1:
        raise SystemExit("--valid-ratio must be in the range [0, 1).")

    input_dir = Path(args.input_dir).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    input_files = iter_alpaca_files(input_dir)
    if not input_files:
        print(f"No *_alpaca.jsonl files found in {input_dir}")
        return

    examples, skipped = load_examples(input_files)
    if not examples:
        print("No valid Alpaca examples were found.")
        return

    train_rows, valid_rows = split_examples(examples, args.valid_ratio, args.seed)
    train_path = output_dir / "train.jsonl"
    valid_path = output_dir / "valid.jsonl"

    write_jsonl(train_path, train_rows)
    write_jsonl(valid_path, valid_rows)

    print(f"Input files: {len(input_files)}")
    print(f"Examples loaded: {len(examples)}")
    print(f"Examples skipped: {skipped}")
    print(f"Train examples: {len(train_rows)} -> {train_path}")
    print(f"Valid examples: {len(valid_rows)} -> {valid_path}")


if __name__ == "__main__":
    main()
