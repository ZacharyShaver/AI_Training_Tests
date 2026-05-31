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
DEFAULT_SOURCE = REPO_ROOT / "source_texts/occult/raw/plato_philebus_jowett.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_esoteric_sources"

BODY_START = 1
BODY_END = 9999

SOCRATES = "Socrates"
INTERLOCUTORS = {"Protarchus", "Philebus"}

SPEAKER_RE = re.compile(
    r"^(?P<label>SOCRATES|PROTARCHUS|PHILEBUS)"
    r"[.:\s]?\s*(?P<text>.*)$"
)
NOISE_RE = re.compile(
    r"^(introduction|INTRODUCTION|[IVX]+\.\s|THE\s+ARGUMENT|SCENE:)",
    re.IGNORECASE,
)

SYSTEM_PROMPT = (
    "You are a Socratic philosophical interlocutor in the tradition of Plato. "
    "Reply naturally, reason from the source tradition, and keep the exchange grounded rather than generic."
)


def canonical_speaker(label: str) -> str:
    mapping = {
        "SOCRATES": SOCRATES,
        "PROTARCHUS": "Protarchus",
        "PHILEBUS": "Philebus",
    }
    return mapping.get(label.strip().upper(), label.strip())


@dataclass
class Turn:
    speaker: str
    text: str
    start_line: int
    end_line: int

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


def parse_turns(path: Path) -> list[Turn]:
    source_lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    turns: list[Turn] = []
    current_speaker: str | None = None
    current_parts: list[str] = []
    current_start = 0
    current_end = 0

    def flush() -> None:
        if current_speaker and current_parts:
            text = clean_dataset_text(" ".join(current_parts))
            if text and count_dataset_words(text) >= 2:
                turns.append(Turn(speaker=current_speaker, text=text, start_line=current_start, end_line=current_end))

    for line_no, raw in enumerate(source_lines, 1):
        if not (BODY_START <= line_no <= BODY_END):
            continue
        stripped = raw.strip()
        if not stripped:
            continue
        if NOISE_RE.match(stripped):
            continue
        m = SPEAKER_RE.match(stripped)
        if m:
            flush()
            current_speaker = canonical_speaker(m.group("label"))
            current_start = line_no
            current_end = line_no
            current_parts = []
            text_part = m.group("text").strip()
            if text_part:
                current_parts.append(text_part)
        elif current_speaker:
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
    all_turns = history + [target]
    speakers = {t.speaker for t in all_turns}
    if SOCRATES not in speakers:
        return False
    if not any(t.speaker != SOCRATES for t in all_turns):
        return False
    if not _alternating(all_turns):
        return False
    return all(2 <= t.word_count <= 500 for t in history)


def build_rows(turns: list[Turn], *, history_turns: int, min_target_words: int, max_target_words: int) -> list[dict]:
    rows: list[dict] = []
    source_name = DEFAULT_SOURCE.name
    for idx in range(history_turns, len(turns)):
        target = turns[idx]
        if target.speaker != SOCRATES:
            continue
        if not (min_target_words <= target.word_count <= max_target_words):
            continue
        history = turns[idx - history_turns : idx]
        if not history_is_usable(history, target):
            continue
        target_text = target.text
        if target_text.rstrip().endswith((":", ";", ",")):
            continue
        if target_text.count('"') % 2 != 0:
            continue
        def participant_label(speaker: str) -> str:
            return "Participant B" if speaker == SOCRATES else "Participant A"
        history_tuples = [(f"{participant_label(t.speaker)} ({t.speaker})", t.text) for t in history]
        rows.append({
            "messages": build_messages(
                system_prompt=SYSTEM_PROMPT,
                history=history_tuples,
                target_participant="Participant B",
                target_text=target_text,
            ),
            "metadata": {
                "record_id": make_record_id(source_name=source_name, kind="philebus_next_reply", source_lines=[history[0].start_line, target.end_line], target_speaker=target.speaker),
                "kind": "philebus_next_reply",
                "source": "Plato's Philebus",
                "source_file": source_name,
                "source_lines": [history[0].start_line, target.end_line],
                "target_speaker": target.speaker,
                "target_participant": "Participant B",
                "target_words": count_dataset_words(target_text),
            },
        })
    return rows


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    return "\n".join([
        f"## Review Example {index}: {metadata['source']}",
        "",
        f"- Record ID: `{metadata['record_id']}`",
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
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Plato Philebus dialogue rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="plato_philebus_dialogue")
    parser.add_argument("--history-turns", type=int, default=2)
    parser.add_argument("--min-target-words", type=int, default=12)
    parser.add_argument("--max-target-words", type=int, default=500)
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    args = parser.parse_args()

    turns = parse_turns(args.source.expanduser().resolve())
    rows = build_rows(turns, history_turns=args.history_turns, min_target_words=args.min_target_words, max_target_words=args.max_target_words)

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    write_jsonl(jsonl_path, rows)

    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(["# Plato Philebus Dialogue Review Sample", "", f"Turns parsed: `{len(turns)}`", f"Rows parsed: `{len(rows)}`", f"Sampled rows: `{len(sample)}`", "", *[row_to_markdown(row, idx, preview_chars=args.preview_chars) for idx, row in enumerate(sample, 1)]]) + "\n",
        encoding="utf-8",
    )

    print(f"Turns parsed: {len(turns)}")
    print(f"Rows written: {len(rows)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
