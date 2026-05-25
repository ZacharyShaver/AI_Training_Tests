from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SampleResult:
    rows: list[dict]
    seed: int
    source_path: Path
    row_count: int
    requested_sample_size: int
    sampling_mode: str
    generated_at: str

    @property
    def selected_record_ids(self) -> list[str]:
        return [record_id_for(row) for row in self.rows]


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_number}") from exc
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )


def record_id_for(row: dict) -> str:
    metadata = row.get("metadata") or {}
    record_id = metadata.get("record_id")
    if not record_id:
        raise ValueError("Every sampled row must include metadata.record_id")
    return str(record_id)


def sample_rows(rows: list[dict], *, sample_size: int = 10, seed: int) -> list[dict]:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if len(rows) <= sample_size:
        return list(rows)
    indexes = random.Random(seed).sample(range(len(rows)), sample_size)
    return [rows[index] for index in indexes]


def render_sample_manifest(result: SampleResult) -> str:
    ids = "\n".join(f"- `{record_id}`" for record_id in result.selected_record_ids)
    return (
        "# Sample Manifest\n\n"
        f"- Generated at: `{result.generated_at}`\n"
        f"- Seed: `{result.seed}`\n"
        f"- Source file: `{result.source_path.name}`\n"
        f"- Row count: `{result.row_count}`\n"
        f"- Requested sample size: `{result.requested_sample_size}`\n"
        f"- Actual sample size: `{len(result.rows)}`\n"
        f"- Sampling mode: `{result.sampling_mode}`\n\n"
        "## Selected Record IDs\n\n"
        f"{ids}\n"
    )


def create_random_sample(
    *,
    source_path: Path,
    output_jsonl_path: Path,
    manifest_path: Path,
    sample_size: int = 10,
    seed: int | None = None,
    generated_at: str | None = None,
) -> SampleResult:
    rows = load_jsonl(source_path)
    seed = seed if seed is not None else random.SystemRandom().randrange(1, 2**31)
    generated_at = generated_at or datetime.now(UTC).isoformat(timespec="seconds")
    sampled_rows = sample_rows(rows, sample_size=sample_size, seed=seed)
    sampling_mode = "small population" if len(rows) <= sample_size else "random sample without replacement"
    result = SampleResult(
        rows=sampled_rows,
        seed=seed,
        source_path=source_path,
        row_count=len(rows),
        requested_sample_size=sample_size,
        sampling_mode=sampling_mode,
        generated_at=generated_at,
    )
    write_jsonl(output_jsonl_path, sampled_rows)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(render_sample_manifest(result), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a seeded random JSONL review sample.")
    parser.add_argument("source_path", type=Path)
    parser.add_argument("output_jsonl_path", type=Path)
    parser.add_argument("manifest_path", type=Path)
    parser.add_argument("--sample-size", type=int, default=10)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()

    result = create_random_sample(
        source_path=args.source_path,
        output_jsonl_path=args.output_jsonl_path,
        manifest_path=args.manifest_path,
        sample_size=args.sample_size,
        seed=args.seed,
    )
    print(f"Wrote {len(result.rows)} sample rows to {args.output_jsonl_path}")
    print(f"Seed: {result.seed}")


if __name__ == "__main__":
    main()
