from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from ai_training_tests.extraction.common.jsonl_io import write_jsonl
from ai_training_tests.extraction.common.review_samples import (
    SYSTEM_PROMPTS,
    build_messages,
    preview_text,
    select_spread,
)
from ai_training_tests.extraction.common.text_cleaning import (
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SOURCE = REPO_ROOT / "oritiginal text/Asclepius.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_esoteric_sources"
BODY_START_RE = re.compile(r"^\[1\]|\bdivine love began to speak\b", re.IGNORECASE)
BODY_END_RE = re.compile(r"^\s*Notes\b|^\s*Bibliography\b", re.IGNORECASE)
QUOTE_RE = re.compile(r"[\"'\u00e2\u20ac\u02dc](?P<quote>.+?)[\"'\u00e2\u20ac\u2122]")


@dataclass
class Paragraph:
    start_line: int
    end_line: int
    text: str


@dataclass
class Turn:
    speaker: str
    text: str
    start_line: int
    end_line: int

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


def iter_paragraphs(path: Path) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    current_lines: list[str] = []
    start_line = 1
    line_no = 0
    source_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line_no, raw in enumerate(source_lines, 1):
        stripped = raw.strip()
        if not stripped:
            if current_lines:
                paragraphs.append(
                    Paragraph(
                        start_line=start_line,
                        end_line=line_no - 1,
                        text=clean_dataset_text(" ".join(current_lines)),
                    )
                )
                current_lines = []
            continue
        if not current_lines:
            start_line = line_no
        current_lines.append(stripped)
    if current_lines:
        paragraphs.append(
            Paragraph(
                start_line=start_line,
                end_line=line_no,
                text=clean_dataset_text(" ".join(current_lines)),
            )
        )
    return paragraphs


def infer_speaker(quote: str, previous_speaker: str | None) -> str | None:
    quote = clean_dataset_text(quote)
    lowered = quote.lower()
    if "o trismegistus" in lowered or "o hermes" in lowered:
        return "Asclepius"
    if "o asclepius" in lowered or "my son" in lowered:
        return "Hermes"
    if previous_speaker == "Hermes":
        return "Asclepius"
    if previous_speaker == "Asclepius":
        return "Hermes"
    return "Hermes"


def parse_turns(path: Path) -> list[Turn]:
    paragraphs = iter_paragraphs(path)
    turns: list[Turn] = []
    started = False
    previous_speaker: str | None = None

    for paragraph in paragraphs:
        if started and BODY_END_RE.search(paragraph.text):
            break
        if not started and paragraph.start_line >= 1500 and BODY_START_RE.search(paragraph.text):
            started = True
        if not started:
            continue

        quotes = [
            clean_dataset_text(match.group("quote"))
            for match in QUOTE_RE.finditer(paragraph.text)
        ]
        if not quotes:
            continue
        for quote in quotes:
            if count_dataset_words(quote) < 4:
                continue
            speaker = infer_speaker(quote, previous_speaker=previous_speaker)
            if speaker is None:
                continue
            turns.append(
                Turn(
                    speaker=speaker,
                    text=quote,
                    start_line=paragraph.start_line,
                    end_line=paragraph.end_line,
                )
            )
            previous_speaker = speaker
    return turns


def history_is_usable(history: list[Turn], target: Turn) -> bool:
    unique_speakers = {turn.speaker for turn in history + [target]}
    if unique_speakers != {"Hermes", "Asclepius"}:
        return False
    if not any(turn.speaker != target.speaker for turn in history):
        return False
    return all(3 <= turn.word_count <= 180 for turn in history)


def build_rows(
    turns: list[Turn], *, history_turns: int, min_target_words: int, max_target_words: int
) -> list[dict]:
    rows: list[dict] = []
    source_name = DEFAULT_SOURCE.name
    for idx in range(history_turns, len(turns)):
        target = turns[idx]
        if target.speaker != "Hermes":
            continue
        if target.word_count < min_target_words or target.word_count > max_target_words:
            continue
        history = turns[idx - history_turns : idx]
        if not history_is_usable(history, target):
            continue
        rows.append(
            {
                "messages": build_messages(
                    system_prompt=SYSTEM_PROMPTS["hermetic"],
                    history=[(turn.speaker, turn.text) for turn in history],
                    target_participant="Participant B",
                    target_text=target.text,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind="asclepius_next_reply",
                        source_lines=[history[0].start_line, target.end_line],
                        target_speaker=target.speaker,
                    ),
                    "kind": "asclepius_next_reply",
                    "source": "Asclepius",
                    "source_file": source_name,
                    "source_lines": [history[0].start_line, target.end_line],
                    "target_speaker": target.speaker,
                    "target_participant": "Participant B",
                    "target_words": target.word_count,
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
            (
                f"- Lines: `{metadata['source_file']}:"
                f"{metadata['source_lines'][0]}-{metadata['source_lines'][1]}`"
            ),
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
    parser = argparse.ArgumentParser(description="Parse Asclepius dialogue rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="asclepius_dialogue")
    parser.add_argument("--history-turns", type=int, default=2)
    parser.add_argument("--min-target-words", type=int, default=18)
    parser.add_argument("--max-target-words", type=int, default=180)
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    args = parser.parse_args()

    turns = parse_turns(args.source.expanduser().resolve())
    rows = build_rows(
        turns,
        history_turns=args.history_turns,
        min_target_words=args.min_target_words,
        max_target_words=args.max_target_words,
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
                "# Asclepius Dialogue Review Sample",
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
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Turns parsed: {len(turns)}")
    print(f"Rows written: {len(rows)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
