#!/usr/bin/env python3
"""Rebuild all reviewed direct-source dialogue dataset outputs."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from dialogue_source_manifest import (
    APPROVED_SOURCE_SPECS,
    output_path_for_spec,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/full_dialogue_dataset"
DEFAULT_NEW_BUDDHIST_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"
DEFAULT_NEW_ESOTERIC_DIR = REPO_ROOT / "review_outputs/new_esoteric_sources"


def run_script(script_name: str, *args: str) -> None:
    command = [sys.executable, str(SCRIPT_DIR / script_name), *args]
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build full dialogue datasets and splits.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--new-buddhist-dir", type=Path, default=DEFAULT_NEW_BUDDHIST_DIR)
    parser.add_argument("--new-esoteric-dir", type=Path, default=DEFAULT_NEW_ESOTERIC_DIR)
    parser.add_argument("--eval-ratio", type=float, default=0.1)
    parser.add_argument("--combined-sample-count", type=int, default=12)
    parser.add_argument("--buddhist-sample-count", type=int, default=10)
    parser.add_argument(
        "--skip-review-samples",
        action="store_true",
        help="Rebuild JSONL outputs and split reports without overwriting review Markdown samples.",
    )
    args = parser.parse_args()

    output_dir = args.output_dir.expanduser().resolve()
    new_buddhist_dir = args.new_buddhist_dir.expanduser().resolve()
    new_esoteric_dir = args.new_esoteric_dir.expanduser().resolve()
    base_jsonl = output_dir / "full_dialogue_dataset.jsonl"

    run_script(
        "build_pilot_dialogue_dataset.py",
        "--dataset-name",
        "full_dialogue_dataset",
        "--output-dir",
        str(output_dir),
        "--per-explicit-source",
        "500",
        "--per-buddhist-source",
        "250",
        "--per-platform-source",
        "200",
        "--history-turns",
        "3",
        "--cue-history-turns",
        "6",
        "--platform-context-gap-lines",
        "20",
        "--min-target-words",
        "20",
        "--explicit-min-target-words",
        "20",
        "--buddhist-min-target-words",
        "20",
        "--platform-min-target-words",
        "20",
        "--max-target-words",
        "700",
        "--max-following-lines",
        "30",
        "--preview-chars",
        "1000",
    )
    for spec in APPROVED_SOURCE_SPECS:
        if spec.parser_script is None:
            continue
        if spec.output_group == "new_buddhist":
            target_output_dir = new_buddhist_dir
        elif spec.output_group == "new_esoteric":
            target_output_dir = new_esoteric_dir
        else:
            continue
        run_script(
            spec.parser_script,
            "--output-dir",
            str(target_output_dir),
            "--dataset-name",
            spec.dataset_name,
            *spec.parser_args,
            "--sample-count",
            str(args.buddhist_sample_count),
            "--preview-chars",
            "1400",
        )
    combine_inputs: list[str] = []
    seen_inputs: set[str] = set()
    for spec in APPROVED_SOURCE_SPECS:
        input_path = str(
            output_path_for_spec(
                spec,
                output_dir=output_dir,
                new_buddhist_dir=new_buddhist_dir,
                new_esoteric_dir=new_esoteric_dir,
            )
        )
        if input_path in seen_inputs:
            continue
        seen_inputs.add(input_path)
        combine_inputs.append(input_path)
    run_script(
        "combine_dialogue_datasets.py",
        *combine_inputs,
        "--output",
        str(base_jsonl),
    )
    run_script(
        "split_dialogue_dataset.py",
        str(base_jsonl),
        "--output-dir",
        str(output_dir),
        "--eval-ratio",
        str(args.eval_ratio),
    )
    if not args.skip_review_samples:
        run_script(
            "make_review_sample.py",
            str(output_dir / "full_buddhist_dialogue_dataset.jsonl"),
            "--output-md",
            str(output_dir / "full_buddhist_dialogue_dataset_review_sample.md"),
            "--count",
            str(args.buddhist_sample_count),
            "--preview-chars",
            "1400",
            "--title",
            "Full Buddhist Dialogue Dataset Review Sample",
        )
        run_script(
            "make_review_sample.py",
            str(output_dir / "full_combined_dialogue_dataset.jsonl"),
            "--output-md",
            str(output_dir / "full_combined_dialogue_dataset_review_sample.md"),
            "--count",
            str(args.combined_sample_count),
            "--preview-chars",
            "1200",
            "--title",
            "Full Combined Dialogue Dataset Review Sample",
        )

    print(f"Full outputs rebuilt in: {output_dir}")


if __name__ == "__main__":
    main()
