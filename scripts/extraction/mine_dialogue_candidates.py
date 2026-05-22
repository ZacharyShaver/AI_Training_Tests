#!/usr/bin/env python3
"""Report likely dialogue-rich regions in the original source texts.

This is intentionally a mining/report tool, not a dataset generator. It helps
decide where the extraction net should be widened before writing full training
data.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = REPO_ROOT / "oritiginal text"

SOURCE_FILES = [
    "the_key-to-theosophy.txt",
    "The Corpus Hermeticum.txt",
    "Milinda Panha.txt",
    "Platform Sutra .txt",
    "Asclepius.txt",
]

BODY_LINE_RANGES = {
    "the_key-to-theosophy.txt": (104, 3061),
    "The Corpus Hermeticum.txt": (70, 2446),
    "Milinda Panha.txt": (927, 8158),
    "Platform Sutra .txt": (532, 2838),
    "Asclepius.txt": (1230, 3285),
}

EXPLICIT_SPEAKER_PATTERNS = {
    "the_key-to-theosophy.txt": re.compile(
        r"(?P<label>ENQUIRER|INQUIRER|QUESTIONER|THEOSOPHIST|ANSWERER)\.\s*",
        re.IGNORECASE,
    ),
    "The Corpus Hermeticum.txt": re.compile(
        r"(?P<label>Hermes|Asclepius|Tat|Mind|Pimander|Workman|H|A|T):\s*"
    ),
}

SPEECH_CUE_RE = re.compile(
    r"\b(?P<speaker>"
    r"King Milinda|Venerable Nāgasena|Venerable Nagasena|Nāgasena|Nagasena|"
    r"The king|The Elder|the Elder|"
    r"Huineng|Hongren|The patriarch|the patriarch|The master|the master|"
    r"The monk|the monk|A monk|a monk|Someone|someone|The questioner|"
    r"Asclepius|Trismegistus|Hermes"
    r")\b.{0,120}?\b(?P<verb>asked|said|replied|answered|inquired|told|spoke)\b",
    re.IGNORECASE,
)

EDITORIAL_RE = re.compile(
    r"\b("
    r"table of contents|bibliography|index|translator|copyright|isbn|"
    r"contents|introduction|notes to|glossary|epilogue|printed in|published in"
    r")\b",
    re.IGNORECASE,
)

PAGE_NO_RE = re.compile(r"^\s*\d+\s*$")
SECTION_MARKER_RE = re.compile(r"^\d{1,3}\.\s*$")
ROMAN_HEADING_RE = re.compile(r"^[IVXLC]+\.\s+")
WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class Turn:
    source: str
    speaker: str
    start_line: int
    end_line: int
    text: str

    @property
    def word_count(self) -> int:
        return count_words(self.text)


@dataclass
class CueBlock:
    source: str
    cue: str
    start_line: int
    end_line: int
    text: str

    @property
    def word_count(self) -> int:
        return count_words(self.text)


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\x0c", " ")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("−", "-").replace("–", "-").replace("—", "-")
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def count_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def canonical_speaker(label: str, *, source_name: str) -> str:
    key = label.strip().upper()
    if key in {"ENQUIRER", "INQUIRER", "QUESTIONER", "Q"}:
        return "Enquirer"
    if key in {"THEOSOPHIST", "ANSWERER"}:
        return "Theosophist"
    if key == "H":
        return "Hermes"
    if key == "A" and source_name == "The Corpus Hermeticum.txt":
        return "Asclepius"
    if key == "A":
        return "Theosophist"
    if key == "T":
        return "Tat"
    return label.strip()


def is_noise_line(line: str) -> bool:
    stripped = normalize_text(line)
    if not stripped:
        return True
    if stripped.startswith("*"):
        return True
    if PAGE_NO_RE.match(stripped):
        return True
    if SECTION_MARKER_RE.match(stripped):
        return True
    if stripped in {"The Corpus Hermeticum", "The Corpus Hermetica"}:
        return True
    if ROMAN_HEADING_RE.match(stripped):
        return True
    if stripped.isupper() and 2 <= len(stripped.split()) <= 14:
        return True
    return bool(EDITORIAL_RE.search(stripped))


def in_body_range(source_name: str, line_no: int) -> bool:
    start, end = BODY_LINE_RANGES.get(source_name, (1, 10**9))
    return start <= line_no <= end


def split_explicit_segments(
    line: str, pattern: re.Pattern[str], *, source_name: str
) -> tuple[str, list[tuple[str, str]]]:
    matches = list(pattern.finditer(line))
    if not matches:
        return "", []

    segments: list[tuple[str, str]] = []
    prefix = normalize_text(line[: matches[0].start()])
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(line)
        label = canonical_speaker(match.group("label"), source_name=source_name)
        text = normalize_text(line[start:end])
        segments.append((label, text))
    return prefix, segments


def parse_explicit_turns(source: Path) -> list[Turn]:
    pattern = EXPLICIT_SPEAKER_PATTERNS.get(source.name)
    if not pattern:
        return []

    turns: list[Turn] = []
    current_speaker: str | None = None
    current_start = 0
    current_end = 0
    current_parts: list[str] = []

    def flush() -> None:
        nonlocal current_speaker, current_start, current_end, current_parts
        if current_speaker and current_parts:
            text = normalize_text(" ".join(current_parts))
            if text:
                turns.append(
                    Turn(
                        source=source.name,
                        speaker=current_speaker,
                        start_line=current_start,
                        end_line=current_end,
                        text=text,
                    )
                )
        current_speaker = None
        current_start = 0
        current_end = 0
        current_parts = []

    for line_no, raw in enumerate(source.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if not in_body_range(source.name, line_no):
            continue
        if is_noise_line(raw):
            continue

        prefix, segments = split_explicit_segments(raw, pattern, source_name=source.name)
        if segments:
            if current_speaker and prefix and not SECTION_MARKER_RE.match(prefix):
                current_parts.append(prefix)
                current_end = line_no
            for speaker, text in segments:
                flush()
                current_speaker = speaker
                current_start = line_no
                current_end = line_no
                if text:
                    current_parts.append(text)
            continue

        if current_speaker:
            cleaned = normalize_text(raw)
            if cleaned:
                current_parts.append(cleaned)
                current_end = line_no

    flush()
    return turns


def mine_speech_cue_blocks(source: Path, *, max_following_lines: int) -> list[CueBlock]:
    lines = source.read_text(encoding="utf-8", errors="ignore").splitlines()
    blocks: list[CueBlock] = []

    for idx, raw in enumerate(lines):
        if not in_body_range(source.name, idx + 1):
            continue
        line = normalize_text(raw)
        if is_noise_line(line):
            continue

        match = SPEECH_CUE_RE.search(line)
        if not match:
            continue

        parts = [line[match.start() :].strip()]
        end_idx = idx
        for next_idx in range(idx + 1, min(len(lines), idx + 1 + max_following_lines)):
            next_line = normalize_text(lines[next_idx])
            if not next_line:
                break
            if is_noise_line(next_line):
                break
            if SPEECH_CUE_RE.search(next_line) and next_idx != idx + 1:
                break
            parts.append(next_line)
            end_idx = next_idx

        text = normalize_text(" ".join(parts))
        if text:
            blocks.append(
                CueBlock(
                    source=source.name,
                    cue=f"{match.group('speaker')} {match.group('verb')}",
                    start_line=idx + 1,
                    end_line=end_idx + 1,
                    text=text,
                )
            )

    return blocks


def compact(text: str, *, limit: int) -> str:
    text = normalize_text(text)
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def print_turn_report(
    turns: list[Turn],
    *,
    top: int,
    preview_chars: int,
    min_target_words: int,
    max_target_words: int,
) -> None:
    print("EXPLICIT SPEAKER TURNS")
    print("======================")
    if not turns:
        print("No explicit turns found.")
        return

    by_source: dict[str, list[Turn]] = {}
    for turn in turns:
        by_source.setdefault(turn.source, []).append(turn)

    for source, source_turns in by_source.items():
        total_words = sum(turn.word_count for turn in source_turns)
        speakers = sorted({turn.speaker for turn in source_turns})
        usable_targets = sum(
            1
            for turn in source_turns[1:]
            if min_target_words <= turn.word_count <= max_target_words
        )
        print(
            f"{source}: turns={len(source_turns)} words={total_words} "
            f"usable_next_reply_targets={usable_targets} speakers={', '.join(speakers)}"
        )
        for speaker in speakers:
            speaker_turns = [turn for turn in source_turns if turn.speaker == speaker]
            speaker_words = sum(turn.word_count for turn in speaker_turns)
            print(f"  - {speaker}: turns={len(speaker_turns)} words={speaker_words}")

    print(f"\nTop {top} longest explicit turns:")
    for turn in sorted(turns, key=lambda item: item.word_count, reverse=True)[:top]:
        print(
            f"- {turn.source}:{turn.start_line}-{turn.end_line} "
            f"{turn.speaker} words={turn.word_count}"
        )
        print(f"  {compact(turn.text, limit=preview_chars)}")


def print_cue_report(blocks: list[CueBlock], *, top: int, preview_chars: int) -> None:
    print("\nSPEECH CUE BLOCKS")
    print("=================")
    if not blocks:
        print("No speech cue blocks found.")
        return

    by_source: dict[str, list[CueBlock]] = {}
    for block in blocks:
        by_source.setdefault(block.source, []).append(block)

    for source, source_blocks in by_source.items():
        total_words = sum(block.word_count for block in source_blocks)
        print(f"{source}: cue_blocks={len(source_blocks)} words={total_words}")

    print(f"\nTop {top} longest speech cue blocks:")
    for block in sorted(blocks, key=lambda item: item.word_count, reverse=True)[:top]:
        print(
            f"- {block.source}:{block.start_line}-{block.end_line} "
            f"{block.cue} words={block.word_count}"
        )
        print(f"  {compact(block.text, limit=preview_chars)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Mine source texts for dialogue-rich candidate regions."
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=SOURCE_DIR,
        help="Directory containing original .txt files.",
    )
    parser.add_argument("--top", type=int, default=12, help="Rows to show per report.")
    parser.add_argument(
        "--preview-chars",
        type=int,
        default=360,
        help="Characters to show for each preview.",
    )
    parser.add_argument(
        "--max-following-lines",
        type=int,
        default=18,
        help="Maximum lines to include after a speech cue.",
    )
    parser.add_argument(
        "--min-target-words",
        type=int,
        default=20,
        help="Minimum words for a candidate next-reply target.",
    )
    parser.add_argument(
        "--max-target-words",
        type=int,
        default=700,
        help="Maximum words for a candidate next-reply target.",
    )
    args = parser.parse_args()

    source_dir = args.source_dir.expanduser().resolve()
    paths = [source_dir / name for name in SOURCE_FILES if (source_dir / name).exists()]

    explicit_turns: list[Turn] = []
    cue_blocks: list[CueBlock] = []
    for path in paths:
        explicit_turns.extend(parse_explicit_turns(path))
        cue_blocks.extend(
            mine_speech_cue_blocks(path, max_following_lines=args.max_following_lines)
        )

    print_turn_report(
        explicit_turns,
        top=args.top,
        preview_chars=args.preview_chars,
        min_target_words=args.min_target_words,
        max_target_words=args.max_target_words,
    )
    print_cue_report(cue_blocks, top=args.top, preview_chars=args.preview_chars)


if __name__ == "__main__":
    main()
