#!/usr/bin/env python3
"""Parse Diamond Sutra attributed dialogue into Buddhist dialogue rows."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from build_pilot_dialogue_dataset import (
    build_messages,
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    write_jsonl,
)
from preview_dialogue_examples import SYSTEM_PROMPTS, preview_text, select_spread


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/diamond_sutra_gutenberg.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

ATTRIBUTED_QUOTE_RE = re.compile(
    r"(?P<prefix>"
    r"(?:The Lord Buddha|Subhuti|the venerable Subhuti|venerable Subhuti)"
    r"[^\"\n]{0,260}?"
    r"(?:replied|addressed|enquired|interrogated|declared|said|assenting|continuing|endorsed|rejoined|discoursed)"
    r"[^\"\n]{0,120}?"
    r"(?:saying|said)?"
    r")\s*(?:[:;,]\s*(?:\[\d+\]\s*)?|,\s*)\"(?P<quote>.*?)\"",
    re.IGNORECASE | re.DOTALL,
)
QUOTE_SPAN_RE = re.compile(r"\"(?P<quote>[^\"\n](?:.*?[^\"\n])?)\"", re.DOTALL)
CHAPTER_RE = re.compile(r"^\[Chapter (?P<chapter>[^\]]+)\]$")
GUTENBERG_END_RE = re.compile(r"\*\*\* END OF THE PROJECT GUTENBERG", re.IGNORECASE)


@dataclass
class Turn:
    speaker: str
    start_line: int
    end_line: int
    text: str


def main_body_with_line_map(path: Path) -> tuple[str, list[int]]:
    parts: list[str] = []
    line_map: list[int] = []
    in_body = False

    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if GUTENBERG_END_RE.search(raw):
            break
        if raw.strip() == "[Chapter 1]":
            in_body = True
        if not in_body:
            continue
        if raw.startswith("  "):
            continue
        stripped = raw.strip()
        if not stripped:
            if parts and parts[-1] != "\n":
                parts.append("\n")
                line_map.append(line_no)
            continue
        if CHAPTER_RE.match(stripped):
            parts.append(f"\n{stripped}\n")
            line_map.extend([line_no] * (len(stripped) + 2))
            continue
        if parts and parts[-1] not in {" ", "\n"}:
            parts.append(" ")
            line_map.append(line_no)
        parts.append(stripped)
        line_map.extend([line_no] * len(stripped))

    text = "".join(parts).replace("“", '"').replace("”", '"')
    return text, line_map


def speaker_from_prefix(prefix: str) -> str:
    lowered = prefix.lower()
    if lowered.startswith("the lord buddha"):
        return "Lord Buddha"
    return "Subhuti"


def infer_unattributed_speaker(quote: str) -> str | None:
    if quote.startswith(("Honoured of the Worlds!", "Thou art of transcendent wisdom")):
        return "Subhuti"
    buddha_starts = (
        "By this wisdom",
        "Moreover, Subhuti,",
        "Subhuti,",
        "Furthermore, Subhuti,",
        "Again, Subhuti,",
        "In what attitude",
        "If a disciple affirmed",
    )
    if quote.startswith(buddha_starts):
        return "Lord Buddha"
    return None


def parse_turns(path: Path) -> list[Turn]:
    text, line_map = main_body_with_line_map(path)
    turns: list[Turn] = []
    attributed_spans: list[tuple[int, int]] = []
    for match in ATTRIBUTED_QUOTE_RE.finditer(text):
        prefix = match.group("prefix")
        if re.match(r"(?i)^subhuti,?\s+saying\b", prefix.strip()):
            continue
        quote = clean_dataset_text(match.group("quote"))
        if not quote:
            continue
        attributed_spans.append((match.start("quote"), match.end("quote")))
        start = line_map[match.start()] if match.start() < len(line_map) else 0
        end_pos = max(match.start(), match.end() - 1)
        end = line_map[end_pos] if end_pos < len(line_map) else start
        turns.append(
            Turn(
                speaker=speaker_from_prefix(match.group("prefix")),
                start_line=start,
                end_line=end,
                text=quote,
            )
        )

    for match in QUOTE_SPAN_RE.finditer(text):
        quote_start = match.start("quote")
        quote_end = match.end("quote")
        if any(start <= quote_start and quote_end <= end for start, end in attributed_spans):
            continue

        quote = clean_dataset_text(match.group("quote"))
        speaker = infer_unattributed_speaker(quote)
        if not quote or speaker is None:
            continue
        start = line_map[match.start()] if match.start() < len(line_map) else 0
        end_pos = max(match.start(), match.end() - 1)
        end = line_map[end_pos] if end_pos < len(line_map) else start
        turns.append(Turn(speaker=speaker, start_line=start, end_line=end, text=quote))

    turns.sort(key=lambda turn: (turn.start_line, turn.end_line, turn.text))
    return turns


def build_rows(
    turns: list[Turn],
    *,
    min_words: int,
    max_words: int,
    history_turns: int,
    target_speakers: set[str],
) -> list[dict]:
    rows: list[dict] = []
    source_name = "diamond_sutra_gutenberg.txt"
    for idx, target in enumerate(turns):
        if target.speaker not in target_speakers:
            continue
        target_words = count_dataset_words(target.text)
        if target_words < min_words or target_words > max_words:
            continue
        history = turns[max(0, idx - history_turns) : idx]
        if not history or not any(item.speaker != target.speaker for item in history):
            continue

        source_lines = [history[0].start_line, target.end_line]
        target_participant = "Participant B" if target.speaker == "Lord Buddha" else "Participant A"
        kind = (
            "diamond_sutra_buddha_next_reply"
            if target.speaker == "Lord Buddha"
            else "diamond_sutra_subhuti_next_reply"
        )
        mapped_history = [
            (
                ("Participant B" if item.speaker == "Lord Buddha" else "Participant A")
                + f" ({item.speaker})",
                item.text,
            )
            for item in history
        ]
        rows.append(
            {
                "messages": build_messages(
                    system_prompt=SYSTEM_PROMPTS["buddhist"],
                    history=mapped_history,
                    target_participant=target_participant,
                    target_text=target.text,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind=f"{kind}_{idx}",
                        source_lines=source_lines,
                        target_speaker=target.speaker,
                    ),
                    "kind": kind,
                    "source": "The Diamond Sutra",
                    "source_file": source_name,
                    "source_lines": source_lines,
                    "target_speaker": target.speaker,
                    "target_participant": target_participant,
                    "target_words": target_words,
                },
            }
        )
    return rows


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    return "\n".join(
        [
            f"## Review Example {index}: {metadata['source']}",
            "",
            f"- Record ID: `{metadata['record_id']}`",
            f"- Kind: `{metadata['kind']}`",
            f"- Lines: `{metadata['source_file']}:{metadata['source_lines'][0]}-{metadata['source_lines'][1]}`",
            f"- Target: `{metadata['target_participant']} ({metadata['target_speaker']})`",
            f"- Target words: `{metadata['target_words']}`",
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
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Diamond Sutra dialogue rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="diamond_sutra_dialogue")
    parser.add_argument("--history-turns", type=int, default=4)
    parser.add_argument("--min-target-words", type=int, default=20)
    parser.add_argument("--max-target-words", type=int, default=500)
    parser.add_argument(
        "--target-speaker",
        action="append",
        choices=["Lord Buddha", "Subhuti"],
        dest="target_speakers",
        help="Speaker to use as an assistant target. Repeat to include both.",
    )
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    args = parser.parse_args()

    turns = parse_turns(args.source.expanduser().resolve())
    rows = build_rows(
        turns,
        min_words=args.min_target_words,
        max_words=args.max_target_words,
        history_turns=args.history_turns,
        target_speakers=set(args.target_speakers or ["Lord Buddha", "Subhuti"]),
    )

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    write_jsonl(jsonl_path, rows)

    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(
            [
                "# Diamond Sutra Review Sample",
                "",
                f"Turns parsed: `{len(turns)}`",
                f"Rows parsed: `{len(rows)}`",
                f"Sampled rows: `{len(sample)}`",
                "",
                *[
                    row_to_markdown(row, idx, preview_chars=args.preview_chars)
                    for idx, row in enumerate(sample, 1)
                ],
            ]
        ),
        encoding="utf-8",
    )

    print(f"Turns parsed: {len(turns)}")
    print(f"Rows written: {len(rows)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
