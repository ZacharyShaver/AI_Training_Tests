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
DEFAULT_SOURCE = (
    REPO_ROOT / "source_texts/occult/raw/theosophy_explained_pavri_djvu.txt"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_esoteric_sources"

BODY_START = 1749
BODY_END = 21800

ENQUIRER = "Enquirer"
PAVRI = "Pavri"

TURN_RE = re.compile(r"^(?P<label>Q|Ans?)\.\s+(?P<text>.*)$")
# Page headers: "THEOSOPHY EXPLAINED", chapter titles, page numbers
NOISE_RE = re.compile(
    r"^(THEOSOPHY|WHAT\s+THEOSOPHY|"
    r"THE\s+SOLAR\s+SYSTEM|EVOLUTION|KARMA|REINCARNATION|"
    r"[IVX]+\s*$|\d+\s*$|\|\s*\w)",
    re.IGNORECASE,
)
# All-caps short lines are section headers / page titles
_ALLCAPS_RE = re.compile(r"^[A-Z\s]{5,50}$")

# OCR artifact: two single-quotes used as opening double-quote
_OCR_DQUOTE_RE = re.compile(r"(?<!\w)''(?=\S)")


@dataclass
class Turn:
    speaker: str
    text: str
    start_line: int
    end_line: int

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


def _join_hyphenated(lines: list[str]) -> list[str]:
    """Join lines that end with a hyphen to the next line."""
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().endswith("-") and i + 1 < len(lines) and lines[i + 1].strip():
            result.append(line.rstrip("-").rstrip() + lines[i + 1].strip())
            i += 2
        else:
            result.append(line)
            i += 1
    return result


def parse_turns(path: Path) -> list[Turn]:
    raw_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    # Join hyphenated line breaks before parsing
    lines = _join_hyphenated(raw_lines)

    turns: list[Turn] = []
    current_speaker: str | None = None
    current_parts: list[str] = []
    current_start = 0
    current_end = 0

    def flush() -> None:
        if current_speaker and current_parts:
            text = clean_dataset_text(" ".join(current_parts))
            if text:
                turns.append(
                    Turn(
                        speaker=current_speaker,
                        text=text,
                        start_line=current_start,
                        end_line=current_end,
                    )
                )

    for line_no, raw in enumerate(lines, 1):
        if not (BODY_START <= line_no <= BODY_END):
            continue
        stripped = raw.strip()
        if not stripped:
            continue
        if NOISE_RE.match(stripped) or _ALLCAPS_RE.match(stripped):
            continue

        m = TURN_RE.match(stripped)
        if m:
            flush()
            current_parts = []
            label = m.group("label").upper()
            if label == "Q":
                current_speaker = ENQUIRER
            else:
                current_speaker = PAVRI
            current_start = line_no
            current_end = line_no
            text_part = m.group("text").strip()
            if text_part:
                current_parts.append(text_part)
        elif current_speaker and stripped:
            current_parts.append(stripped)
            current_end = line_no

    flush()
    return turns


def _alternating(seq: list[Turn]) -> bool:
    for i in range(1, len(seq)):
        if seq[i].speaker == seq[i - 1].speaker:
            return False
    return True


def history_is_usable(history: list[Turn], target: Turn) -> bool:
    speakers = {t.speaker for t in history + [target]}
    if speakers != {ENQUIRER, PAVRI}:
        return False
    if not _alternating(history + [target]):
        return False
    return all(3 <= t.word_count <= 400 for t in history)


def build_rows(
    turns: list[Turn],
    *,
    history_turns: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    rows: list[dict] = []
    source_name = DEFAULT_SOURCE.name

    for idx in range(history_turns, len(turns)):
        target = turns[idx]
        if target.speaker != PAVRI:
            continue
        if not (min_target_words <= target.word_count <= max_target_words):
            continue
        history = turns[idx - history_turns : idx]
        if not history_is_usable(history, target):
            continue

        def participant_label(speaker: str) -> str:
            return "Participant B" if speaker == PAVRI else "Participant A"

        history_tuples = [
            (f"{participant_label(t.speaker)} ({t.speaker})", t.text)
            for t in history
        ]

        target_text = _OCR_DQUOTE_RE.sub('"', target.text)
        if target_text.count('"') % 2 != 0:
            continue
        if target_text.rstrip().endswith((":", ";", ",")):
            continue

        rows.append(
            {
                "messages": build_messages(
                    system_prompt=SYSTEM_PROMPTS["theosophy"],
                    history=history_tuples,
                    target_participant="Participant B",
                    target_text=target_text,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind="theosophy_explained_next_reply",
                        source_lines=[history[0].start_line, target.end_line],
                        target_speaker=target.speaker,
                    ),
                    "kind": "theosophy_explained_next_reply",
                    "source": "Theosophy Explained in Questions and Answers",
                    "source_file": source_name,
                    "source_lines": [history[0].start_line, target.end_line],
                    "target_speaker": target.speaker,
                    "target_participant": "Participant B",
                    "target_words": count_dataset_words(target_text),
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
    parser = argparse.ArgumentParser(
        description="Parse Theosophy Explained Q&A dialogue rows."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="theosophy_explained_pavri_dialogue")
    parser.add_argument("--history-turns", type=int, default=2)
    parser.add_argument("--min-target-words", type=int, default=12)
    parser.add_argument("--max-target-words", type=int, default=500)
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
                "# Theosophy Explained Dialogue Review Sample",
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
