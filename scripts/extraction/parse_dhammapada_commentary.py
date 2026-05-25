#!/usr/bin/env python3
"""Parse reviewed dialogue rows from the Dhammapada commentary corpus."""

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
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/clean/dhamma_verses_commentary.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

QUOTE_RE = re.compile(r'"([^"]+)"')
SPEAKER_PHRASE = (
    r"(?:The Teacher|Teacher|Realised One|Fortunate One|Buddha|"
    r"[A-ZĀĪŪṬḌṆṂÑ][\wĀĪŪṬḌṆṂÑāīūṭḍṇṃñ'-]*(?:\s+[A-ZĀĪŪṬḌṆṂÑ][\wĀĪŪṬḌṆṂÑāīūṭḍṇṃñ'-]*){0,3}|"
    r"(?:the|The)\s+[A-Za-z-]+(?:\s+[A-Za-z-]+){0,3})"
)
LEADING_SPEAKER_RE = re.compile(
    rf"(?P<speaker>{SPEAKER_PHRASE})\s+"
    r"(?:asked|said|replied|answered|enquired|declared|pronounced|told)"
    r"(?:\s+(?:him|her|them|to\s+him|to\s+her|to\s+them))?\s*:\s*$",
    re.IGNORECASE,
)
TRAILING_SPEAKER_RE = re.compile(
    rf"(?P<speaker>{SPEAKER_PHRASE})\s+"
    r"(?:said|replied|answered|asked|declared|pronounced)\s*:\s*$",
    re.IGNORECASE,
)
SPEAKER_NORMALIZATIONS = {
    "The Teacher": "The Buddha",
    "Teacher": "The Buddha",
    "Realised One": "The Buddha",
    "Fortunate One": "The Buddha",
}
SKIP_LINE_RE = re.compile(
    r"^(?:AJ:|Dhp\s+\d+|Burlingame:|Compare:|\d+\s*$|The Chapter about)",
    re.IGNORECASE,
)
SECTION_START_RE = re.compile(r"\bThe Story about\b", re.IGNORECASE)


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


def canonical_speaker(name: str) -> str:
    name = clean_dataset_text(name).strip(" ,.;:-")
    name = re.sub(r"^(?:the\s+)?elder\b", "Elder", name, flags=re.IGNORECASE)
    name = re.sub(r"^(?:the\s+)?physician\b", "Physician", name, flags=re.IGNORECASE)
    name = re.sub(r"^(?:the\s+)?Brahmin\b", "Brahmin", name, flags=re.IGNORECASE)
    return SPEAKER_NORMALIZATIONS.get(name, name)


def iter_paragraphs(path: Path) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    current_lines: list[str] = []
    start_line = 1
    line_no = 0

    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
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
        if SKIP_LINE_RE.match(stripped):
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


def infer_first_speaker(prefix: str) -> str | None:
    prefix = clean_dataset_text(prefix)
    match = LEADING_SPEAKER_RE.search(prefix)
    if match:
        return canonical_speaker(match.group("speaker"))
    return None


def infer_last_speaker(prefix: str) -> str | None:
    prefix = clean_dataset_text(prefix)
    explicit = re.search(r"To this (?P<speaker>.+?) agreed, and said:\s*$", prefix)
    if explicit:
        return canonical_speaker(explicit.group("speaker"))
    match = TRAILING_SPEAKER_RE.search(prefix)
    if match:
        return canonical_speaker(match.group("speaker"))
    return None


def extract_turns_from_paragraph(paragraph: str) -> list[tuple[str, str]]:
    text = (
        clean_dataset_text(paragraph)
        .replace("“", '"')
        .replace("”", '"')
        .replace("‖", "'")
        .replace("–", " - ")
    )
    quotes = [clean_dataset_text(match.group(1)) for match in QUOTE_RE.finditer(text)]
    if not quotes:
        return []

    first_quote = next(QUOTE_RE.finditer(text))
    first_speaker = infer_first_speaker(text[: first_quote.start()])

    last_match = None
    for last_match in QUOTE_RE.finditer(text):
        pass
    last_speaker = infer_last_speaker(text[: last_match.start()]) if last_match else None

    if first_speaker and last_speaker and len(quotes) >= 2:
        other_speaker = last_speaker if last_speaker != first_speaker else None
        if other_speaker:
            turns: list[tuple[str, str]] = []
            for idx, quote in enumerate(quotes):
                speaker = first_speaker if idx % 2 == 0 else other_speaker
                turns.append((speaker, quote))
            return turns

    if first_speaker and len(quotes) == 1:
        return [(first_speaker, quotes[0])]

    if last_speaker and len(quotes) == 1:
        return [(last_speaker, quotes[0])]

    return []


def speaker_is_usable(speaker: str) -> bool:
    if speaker in {"Lay friends", "Friends", "People", "he", "she", "they", "and"}:
        return False
    if speaker.lower() in {"he", "she", "they", "and"}:
        return False
    if " and" in speaker.lower():
        return False
    if not speaker:
        return False
    return len(speaker) <= 60 and (speaker[0].isupper() or speaker.startswith("the "))


def parse_turns(path: Path) -> list[Turn]:
    paragraphs = iter_paragraphs(path)
    turns: list[Turn] = []
    started = False
    for paragraph in paragraphs:
        if not started and paragraph.start_line >= 298 and SECTION_START_RE.search(paragraph.text):
            started = True
        if not started:
            continue
        extracted = extract_turns_from_paragraph(paragraph.text)
        if not extracted:
            continue
        for speaker, quote in extracted:
            if not speaker_is_usable(speaker):
                continue
            turns.append(
                Turn(
                    speaker=speaker,
                    text=quote,
                    start_line=paragraph.start_line,
                    end_line=paragraph.end_line,
                )
            )
    return turns


def history_is_usable(history: list[Turn], target: Turn) -> bool:
    unique_speakers = {turn.speaker for turn in history + [target]}
    if len(unique_speakers) > 2:
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
        if target.word_count < min_target_words or target.word_count > max_target_words:
            continue
        history = turns[idx - history_turns : idx]
        if not history_is_usable(history, target):
            continue
        rows.append(
            {
                "messages": build_messages(
                    system_prompt=SYSTEM_PROMPTS["buddhist"],
                    history=[(turn.speaker, turn.text) for turn in history],
                    target_participant="Participant B",
                    target_text=target.text,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind="dhammapada_commentary_next_reply",
                        source_lines=[history[0].start_line, target.end_line],
                        target_speaker=target.speaker,
                    ),
                    "kind": "dhammapada_commentary_next_reply",
                    "source": "Dhammapada Commentary",
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
    parser = argparse.ArgumentParser(description="Parse Dhammapada commentary dialogue rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="dhammapada_commentary_dialogue")
    parser.add_argument("--history-turns", type=int, default=1)
    parser.add_argument("--min-target-words", type=int, default=10)
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
                "# Dhammapada Commentary Review Sample",
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
