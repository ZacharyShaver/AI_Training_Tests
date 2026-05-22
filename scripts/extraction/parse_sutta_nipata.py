#!/usr/bin/env python3
"""Parse dialogue rows from the Sutta Nipata clean text.

This is a review-first miner. It targets explicit verse dialogue labels such
as "Dhaniya:" and "The Buddha:" and keeps section/title labels in metadata,
not in the training prompt.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from build_pilot_dialogue_dataset import (
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    write_jsonl,
)
from preview_dialogue_examples import SYSTEM_PROMPTS, preview_text, select_spread


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/clean/sutta_nipata.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

BODY_START_RE = re.compile(r"^\s*1:1\s+The Snake\s*$")
BODY_END_RE = re.compile(r"^\s*Glossary\s*$|^\s*Table of Contents\s*$")
SECTION_RE = re.compile(
    r"^\s*(?P<section>[1-5]:(?:1[0-6]|[1-9]))\s+(?P<title>.+?)\s*$"
)
PAGE_NUMBER_RE = re.compile(r"^\s*\d+\s*$")
NOTES_RE = re.compile(r"^\s*Notes?\s*$|^\s*See also:")
VERSE_RANGE_RE = re.compile(r"^\s*(?:vv?\.|v\.)\s*\d+")
SPEAKER_LABEL_RE = re.compile(
    r"^\s*(?P<label>[A-ZĀĪŪṬḌṆḶṂÑṄa-zāīūṭḍṇḷṃñṅ][A-ZĀĪŪṬḌṆḶṂÑṄa-zāīūṭḍṇḷṃñṅ .’'()-]{1,56}):\s*(?:\d+)?\s*$"
)
INLINE_NOTE_DIGIT_RE = re.compile(r"(?<=[A-Za-z.,;:!?'\"\]\)])\d{1,3}\b")
STANDALONE_NOTE_DIGIT_RE = re.compile(r"(^|(?<=[.!?'\"\)])\s+)\d{1,3}\s+(?=[A-Z])")
WHITESPACE_RE = re.compile(r"[ \t]+")

PDF_CHAR_MAP = str.maketrans(
    {
        "\ufeff": "",
        "\x0c": "",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": " - ",
        "\u2026": "...",
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\ufb03": "ffi",
        "\ufb04": "ffl",
    }
)

SPEAKER_ALIASES = {
    "the buddha": "The Buddha",
    "buddha": "The Buddha",
    "the blessed one said": "The Buddha",
    "the blessed one": "The Buddha",
    "the buddha kassapa": "The Buddha Kassapa",
    "buddha kassapa": "The Buddha Kassapa",
    "dhaniya": "Dhaniya",
    "dhaniya said": "Dhaniya",
    "dhaniya the cattleman": "Dhaniya",
    "cunda": "Cunda",
    "cunda the smith": "Cunda",
    "the deva": "The deva",
    "sātāgira the yakkha": "Sātāgira the yakkha",
    "hemavata the yakkha": "Hemavata the yakkha",
    "ā avaka": "Āḷavaka",
    "āḷavaka": "Āḷavaka",
    "tissa": "Tissa",
    "sundarika": "Sundarika",
    "māgha": "Māgha",
    "sabhiya": "Sabhiya",
    "sela": "Sela",
    "vāseṭṭha": "Vāseṭṭha",
    "tissa-metteyya": "Tissa-metteyya",
    "māgandiya": "Māgandiya",
    "sāriputta": "Sāriputta",
    "ajita": "Ajita",
    "pu ṇṇaka": "Puṇṇaka",
    "puṇṇaka": "Puṇṇaka",
    "mettagū": "Mettagū",
    "dhotaka": "Dhotaka",
    "upasīva": "Upasīva",
    "nanda": "Nanda",
    "hemaka": "Hemaka",
    "todeyya": "Todeyya",
    "kappa": "Kappa",
    "jatuka ṇṇin": "Jatukaṇṇin",
    "jatukaṇṇin": "Jatukaṇṇin",
    "bhadrāvudha": "Bhadrāvudha",
    "udaya": "Udaya",
    "posāla": "Posāla",
    "mogharāja": "Mogharāja",
    "pi ṅgiya": "Piṅgiya",
    "piṅgiya": "Piṅgiya",
}
TARGET_SPEAKERS = {"The Buddha", "The Buddha Kassapa"}


@dataclass
class Turn:
    speaker: str
    start_line: int
    end_line: int
    text: str

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


@dataclass
class Section:
    section: str
    title: str
    start_line: int
    end_line: int
    narrator: str
    turns: list[Turn]


def normalize_line(line: str) -> str:
    return line.translate(PDF_CHAR_MAP).rstrip()


def clean_text(text: str) -> str:
    text = text.translate(PDF_CHAR_MAP)
    text = re.sub(r"(?:^|\s)\*\s+\*\s+\*(?:\s|$)", " ", text)
    text = INLINE_NOTE_DIGIT_RE.sub("", text)
    text = STANDALONE_NOTE_DIGIT_RE.sub(r"\1", text)
    text = re.sub(r"\s+\d{1,3}\s+(?=(?:\"|'|$))", " ", text)
    text = re.sub(r"\s+vv?\.\s*\d+(?:[-–]\d+)?\s*$", "", text, flags=re.IGNORECASE)
    text = WHITESPACE_RE.sub(" ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return clean_dataset_text(text.strip())


def clean_turn_text(lines: list[str]) -> str:
    cleaned: list[str] = []
    for raw in lines:
        line = normalize_line(raw).strip()
        if not line or PAGE_NUMBER_RE.match(line):
            continue
        if re.fullmatch(r"\*+\s*(?:\*+\s*)*", line):
            continue
        line = re.sub(r"(?:^|\s)\*\s+\*\s+\*(?:\s|$)", " ", line)
        if VERSE_RANGE_RE.match(line):
            continue
        line = re.sub(r"^\d{1,3}\s+", "", line)
        line = re.sub(r"\s+\d{1,3}\s*$", "", line)
        line = INLINE_NOTE_DIGIT_RE.sub("", line)
        line = STANDALONE_NOTE_DIGIT_RE.sub(r"\1", line)
        line = WHITESPACE_RE.sub(" ", line)
        if line:
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def canonical_speaker(label: str) -> str | None:
    label = clean_text(label).strip(" :")
    lowered = label.lower()
    return SPEAKER_ALIASES.get(lowered)


def line_is_noise(line: str) -> bool:
    stripped = normalize_line(line).strip()
    if not stripped:
        return False
    if PAGE_NUMBER_RE.match(stripped):
        return True
    if NOTES_RE.match(stripped):
        return True
    if stripped in {"Sutta Nipāta", "The Discourse Group"}:
        return True
    return False


def starts_new_unlabeled_quote(line: str, current_lines: list[str]) -> bool:
    stripped = normalize_line(line).strip()
    if not stripped.startswith(('"', "“")):
        return False
    previous_nonempty = next(
        (normalize_line(value).strip() for value in reversed(current_lines) if value.strip()),
        "",
    )
    return previous_nonempty.endswith(('"', "”"))


def parse_sections(path: Path) -> list[Section]:
    sections: list[Section] = []
    current_meta: tuple[str, str, int] | None = None
    current_narrator_lines: list[str] = []
    current_turns: list[Turn] = []
    current_speaker: str | None = None
    current_turn_start = 0
    current_turn_lines: list[str] = []
    in_body = False
    in_notes = False

    def flush_turn(end_line: int) -> None:
        nonlocal current_speaker, current_turn_start, current_turn_lines
        if current_speaker and current_turn_lines:
            text = clean_turn_text(current_turn_lines)
            if text:
                current_turns.append(
                    Turn(
                        speaker=current_speaker,
                        start_line=current_turn_start,
                        end_line=end_line,
                        text=text,
                    )
                )
        current_speaker = None
        current_turn_start = 0
        current_turn_lines = []

    def flush_section(end_line: int) -> None:
        nonlocal current_meta, current_narrator_lines, current_turns
        if current_meta:
            section, title, start_line = current_meta
            sections.append(
                Section(
                    section=section,
                    title=title,
                    start_line=start_line,
                    end_line=end_line,
                    narrator=clean_text(" ".join(current_narrator_lines)),
                    turns=current_turns,
                )
            )
        current_meta = None
        current_narrator_lines = []
        current_turns = []

    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    for line_no, raw in enumerate(lines, 1):
        line = normalize_line(raw)
        if not in_body:
            if BODY_START_RE.match(line):
                in_body = True
            else:
                continue
        if BODY_END_RE.match(line):
            flush_turn(line_no - 1)
            flush_section(line_no - 1)
            break

        section_match = SECTION_RE.match(line)
        if section_match:
            flush_turn(line_no - 1)
            flush_section(line_no - 1)
            current_meta = (
                section_match.group("section"),
                clean_text(section_match.group("title")),
                line_no,
            )
            in_notes = False
            continue

        if current_meta is None:
            continue
        if NOTES_RE.match(line):
            flush_turn(line_no - 1)
            in_notes = True
            continue
        if in_notes:
            continue
        if PAGE_NUMBER_RE.match(line.strip()):
            continue

        speaker_match = SPEAKER_LABEL_RE.match(line)
        if speaker_match:
            speaker = canonical_speaker(speaker_match.group("label"))
            if speaker:
                flush_turn(line_no - 1)
                current_speaker = speaker
                current_turn_start = line_no
                current_turn_lines = []
                continue

        if current_speaker:
            if starts_new_unlabeled_quote(line, current_turn_lines):
                flush_turn(line_no - 1)
                continue
            current_turn_lines.append(line)
        elif not current_turns and not line_is_noise(line):
            current_narrator_lines.append(line)

    return sections


def participant_for_speaker(speaker: str) -> str:
    return "Participant B" if speaker in TARGET_SPEAKERS else "Participant A"


def build_messages(history: list[tuple[str, str]], target_text: str) -> list[dict[str, str]]:
    history_text = "\n".join(f"{speaker}: {clean_text(text)}" for speaker, text in history)
    return [
        {"role": "system", "content": clean_dataset_text(SYSTEM_PROMPTS["buddhist"])},
        {
            "role": "user",
            "content": (
                f"Conversation so far:\n{history_text}\n\n"
                "Write Participant B's next reply."
            ),
        },
        {"role": "assistant", "content": clean_turn_text(target_text.splitlines())},
    ]


def section_to_rows(
    item: Section,
    *,
    history_turns: int,
    max_context_words: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    rows: list[dict] = []
    for idx, target in enumerate(item.turns):
        if target.speaker not in TARGET_SPEAKERS:
            continue
        if not (min_target_words <= target.word_count <= max_target_words):
            continue

        prior_turns = item.turns[max(0, idx - history_turns) : idx]
        has_non_target_history = any(turn.speaker not in TARGET_SPEAKERS for turn in prior_turns)
        history: list[tuple[str, str]] = []
        context_words = count_dataset_words(item.narrator)
        if idx == 0 and item.narrator and 8 <= context_words <= max_context_words:
            history.append(("Participant A (Narrator)", item.narrator))
        for turn in prior_turns:
            participant = participant_for_speaker(turn.speaker)
            history.append((f"{participant} ({turn.speaker})", turn.text))

        if not history:
            continue
        if not has_non_target_history and not any("Narrator" in speaker for speaker, _ in history):
            continue

        source_name = "sutta_nipata.txt"
        source_lines = [target.start_line, target.end_line]
        kind = "sutta_nipata_buddha_next_reply"
        if target.speaker == "The Buddha Kassapa":
            kind = "sutta_nipata_buddha_kassapa_next_reply"
        rows.append(
            {
                "messages": build_messages(history, target.text),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind=f"{kind}_{item.section.replace(':', '-')}_{idx}",
                        source_lines=source_lines,
                        target_speaker=target.speaker,
                    ),
                    "kind": kind,
                    "source": "Sutta Nipata",
                    "source_file": source_name,
                    "source_lines": source_lines,
                    "target_speaker": target.speaker,
                    "target_participant": "Participant B",
                    "target_words": target.word_count,
                    "context_words": context_words if idx == 0 else 0,
                    "section": item.section,
                    "title": item.title,
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
            f"- Section: `{metadata['section']} {metadata['title']}`",
            f"- Lines: `{metadata['source_file']}:{metadata['source_lines'][0]}-{metadata['source_lines'][1]}`",
            f"- Target: `{metadata['target_participant']} ({metadata['target_speaker']})`",
            f"- Target words: `{metadata['target_words']}`",
            f"- Context words: `{metadata['context_words']}`",
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
    parser = argparse.ArgumentParser(description="Parse Sutta Nipata dialogue rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="sutta_nipata_dialogue")
    parser.add_argument("--history-turns", type=int, default=4)
    parser.add_argument("--max-context-words", type=int, default=220)
    parser.add_argument("--min-target-words", type=int, default=8)
    parser.add_argument("--max-target-words", type=int, default=420)
    parser.add_argument("--sample-count", type=int, default=12)
    parser.add_argument("--preview-chars", type=int, default=1400)
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    sections = parse_sections(source)
    rows: list[dict] = []
    for section in sections:
        rows.extend(
            section_to_rows(
                section,
                history_turns=args.history_turns,
                max_context_words=args.max_context_words,
                min_target_words=args.min_target_words,
                max_target_words=args.max_target_words,
            )
        )

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    write_jsonl(jsonl_path, rows)

    kind_counts = Counter(row["metadata"]["kind"] for row in rows)
    speaker_counts = Counter(row["metadata"]["target_speaker"] for row in rows)
    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(
            [
                "# Sutta Nipata Dialogue Review Sample",
                "",
                f"Sections parsed: `{len(sections)}`",
                f"Rows parsed: `{len(rows)}`",
                "",
                "Rows by kind:",
                "",
                *[f"- `{kind}`: `{count}`" for kind, count in sorted(kind_counts.items())],
                "",
                "Target speakers:",
                "",
                *[
                    f"- `{speaker}`: `{count}`"
                    for speaker, count in sorted(speaker_counts.items())
                ],
                "",
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

    print(f"Sections parsed: {len(sections)}")
    print(f"Rows written: {len(rows)}")
    for kind, count in sorted(kind_counts.items()):
        print(f"{kind}: {count}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
