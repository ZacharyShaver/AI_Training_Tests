#!/usr/bin/env python3
"""Parse attributed dialogue turns from Platform Sutra source text."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict
from pathlib import Path

from mine_dialogue_candidates import BODY_LINE_RANGES, SOURCE_DIR, Turn, normalize_text


SOURCE_NAME = "Platform Sutra .txt"

ATTRIBUTION_RE = re.compile(
    r"(?P<speaker>"
    r"The Great Master|the Great Master|The master|the master|"
    r"The patriarch|the patriarch|The Fifth Patriarch|the Fifth Patriarch|"
    r"Fifth Patriarch|Hongren|Huineng|I|"
    r"Lord Wei|Prefect Wei|Prefect \[Wei\]|\[Wei\]|Wei|"
    r"Fahai|\[Fahai\]|Fada|\[Fada\]|Zhidao|\[Zhidao\]|"
    r"Xingsi|\[Xingsi\]|Huairang|\[Huairang\]|Xuanjue|\[Xuanjue\]|"
    r"Xuance|\[Xuance\]|Zhihuang|\[Zhihuang\]|"
    r"Xingchang|\[Xingchang\]|Shenhui|\[Shenhui\]|Huiming|\[Huiming\]|"
    r"Yinzong|\[Yinzong\]|"
    r"Fangbian|\[The monk\]|The monk|the monk|A monk|a monk|"
    r"The nun|the nun|The assembly|the assembly|Those in the assembly"
    r")\s+"
    r"(?P<verb>"
    r"asked(?: further)?|said(?: further| again)?|replied|answered|told|"
    r"rebuked|announced|informed|questioned|addressed|called"
    r")"
    r"(?P<between>.{0,120}?)(?P<quote>[\"'])",
    re.IGNORECASE,
)

PAGE_MARK_RE = re.compile(r"^\d+[a-z]$", re.IGNORECASE)
FOOTNOTE_MARK_RE = re.compile(r"^\d+$")


def canonical_speaker(raw: str) -> str:
    value = raw.strip("[] ")
    lowered = value.lower()
    if lowered in {"the great master", "the master", "huineng", "i"}:
        return "Huineng"
    if lowered in {"the patriarch", "the fifth patriarch", "fifth patriarch", "hongren"}:
        return "Fifth Patriarch"
    if "wei" in lowered:
        return "Prefect Wei"
    if lowered in {"the monk", "a monk"}:
        return "Monk"
    if lowered == "the nun":
        return "Nun"
    if "assembly" in lowered:
        return "Assembly"
    return value


def is_body_line(line_no: int) -> bool:
    start, end = BODY_LINE_RANGES[SOURCE_NAME]
    return start <= line_no <= end


def is_noise_line(raw: str) -> bool:
    stripped = normalize_text(raw)
    if not stripped:
        return True
    if PAGE_MARK_RE.match(stripped) or FOOTNOTE_MARK_RE.match(stripped):
        return True
    return False


def source_text_with_line_map(path: Path) -> tuple[str, list[int]]:
    parts: list[str] = []
    line_map: list[int] = []

    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if not is_body_line(line_no) or is_noise_line(raw):
            continue
        cleaned = normalize_text(raw)
        if not cleaned:
            continue
        if parts:
            parts.append(" ")
            line_map.append(line_no)
        parts.append(cleaned)
        line_map.extend([line_no] * len(cleaned))

    return "".join(parts), line_map


def find_closing_quote(text: str, start: int, quote_char: str) -> int:
    idx = start
    while idx < len(text):
        if text[idx] != quote_char:
            idx += 1
            continue

        before = text[idx - 1] if idx > 0 else ""
        after = text[idx + 1] if idx + 1 < len(text) else ""

        # Apostrophes inside words are not quote terminators.
        if quote_char == "'" and before.isalpha() and after.isalpha():
            idx += 1
            continue

        return idx
    return -1


def clean_turn_text(text: str) -> str:
    text = normalize_text(text)
    text = re.sub(r"\b\d{2,3}\b", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return normalize_text(text)


def parse_platform_turns(path: Path) -> list[Turn]:
    text, line_map = source_text_with_line_map(path)
    turns: list[Turn] = []
    pos = 0

    while True:
        match = ATTRIBUTION_RE.search(text, pos)
        if not match:
            break

        quote_start = match.end()
        quote_end = find_closing_quote(text, quote_start, match.group("quote"))
        if quote_end == -1:
            pos = match.end()
            continue

        content = clean_turn_text(text[quote_start:quote_end])
        speaker = canonical_speaker(match.group("speaker"))
        if content and len(content.split()) >= 3:
            start_line = line_map[match.start()] if match.start() < len(line_map) else 0
            end_line = line_map[quote_end - 1] if quote_end - 1 < len(line_map) else start_line
            turns.append(
                Turn(
                    source=SOURCE_NAME,
                    speaker=speaker,
                    start_line=start_line,
                    end_line=end_line,
                    text=content,
                )
            )

        pos = quote_end + 1

    return turns


def merge_adjacent_same_speaker(turns: list[Turn]) -> list[Turn]:
    merged: list[Turn] = []
    for turn in turns:
        if (
            merged
            and merged[-1].speaker == turn.speaker
            and turn.start_line - merged[-1].end_line <= 2
        ):
            merged[-1] = Turn(
                source=turn.source,
                speaker=turn.speaker,
                start_line=merged[-1].start_line,
                end_line=turn.end_line,
                text=normalize_text(f"{merged[-1].text} {turn.text}"),
            )
        else:
            merged.append(turn)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Preview parsed Platform Sutra dialogue turns."
    )
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    parser.add_argument("--top", type=int, default=40)
    args = parser.parse_args()

    turns = parse_platform_turns(args.source_dir / SOURCE_NAME)
    if args.json:
        print(json.dumps([asdict(turn) for turn in turns[: args.top]], ensure_ascii=False, indent=2))
        return

    print(f"turns={len(turns)}")
    by_speaker: dict[str, int] = {}
    for turn in turns:
        by_speaker[turn.speaker] = by_speaker.get(turn.speaker, 0) + 1
    for speaker, count in sorted(by_speaker.items()):
        print(f"{speaker}: {count}")
    print()
    for turn in turns[: args.top]:
        print(f"{turn.start_line}-{turn.end_line} {turn.speaker} words={turn.word_count}")
        print(f"  {turn.text[:240]}")


if __name__ == "__main__":
    main()
