from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path

from tools.review_pipeline.random_sample import create_random_sample
from tools.review_pipeline.render_review_packet import write_review_packet


def run_parser_command(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(command, cwd=cwd, check=True, text=True, capture_output=True)


def run_new_parser_pass(
    *,
    parser_command: list[str] | None,
    source_jsonl_path: Path,
    output_dir: Path,
    dataset_stem: str,
    sample_size: int = 10,
    seed: int | None = None,
    cwd: Path | None = None,
) -> dict[str, Path | int]:
    if parser_command:
        run_parser_command(parser_command, cwd=cwd)

    sample_jsonl_path = output_dir / f"{dataset_stem}.jsonl"
    manifest_path = output_dir / "sample_manifest.md"
    packet_path = output_dir / f"{dataset_stem}_random_review.md"
    result = create_random_sample(
        source_path=source_jsonl_path,
        output_jsonl_path=sample_jsonl_path,
        manifest_path=manifest_path,
        sample_size=sample_size,
        seed=seed,
    )
    write_review_packet(source_jsonl_path=sample_jsonl_path, output_path=packet_path)

    run_summary_path = output_dir / "run_summary.md"
    run_summary_path.write_text(
        "# Parser Pass Run Summary\n\n"
        f"- Source JSONL: `{source_jsonl_path.as_posix()}`\n"
        f"- Sample JSONL: `{sample_jsonl_path.as_posix()}`\n"
        f"- Review packet: `{packet_path.as_posix()}`\n"
        f"- Seed: `{result.seed}`\n"
        f"- Row count: `{result.row_count}`\n"
        f"- Sampled rows: `{len(result.rows)}`\n",
        encoding="utf-8",
    )
    return {
        "seed": result.seed,
        "sample_jsonl_path": sample_jsonl_path,
        "manifest_path": manifest_path,
        "packet_path": packet_path,
        "run_summary_path": run_summary_path,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a parser pass, sample output, and render a packet.")
    parser.add_argument("--source-jsonl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset-stem", required=True)
    parser.add_argument("--sample-size", type=int, default=10)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--parser-command", help="Optional parser command to run before sampling.")
    args = parser.parse_args()

    parser_command = shlex.split(args.parser_command) if args.parser_command else None
    outputs = run_new_parser_pass(
        parser_command=parser_command,
        source_jsonl_path=args.source_jsonl,
        output_dir=args.output_dir,
        dataset_stem=args.dataset_stem,
        sample_size=args.sample_size,
        seed=args.seed,
    )
    print(f"Wrote review packet to {outputs['packet_path']}")


if __name__ == "__main__":
    main()

