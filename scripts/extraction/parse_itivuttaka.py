#!/usr/bin/env python3
"""Parse Itivuttaka prose-to-verse teaching rows from extracted PDF text."""

from __future__ import annotations

import argparse
import re
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
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/clean/itivuttaka_thanissaro.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

SECTION_RE = re.compile(r"^§+(?P<number>\d+(?:[–—-]\d+)?)\.\s*", re.MULTILINE)
PAGE_NUMBER_RE = re.compile(r"^\s*\d+\s*$")
NOTE_LINE_RE = re.compile(r"^\s*\d+\.\s+")
SPACED_NOTE_RE = re.compile(r"^N\s*O\s*T\s*E\s*:", re.IGNORECASE)
SO_SAID_RE = re.compile(r"\bso I have heard\.?\s*\d*\s*$", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"[ \t]+")
FOOTNOTE_NUMBER_RE = re.compile(r"\b\d{1,3}\b")


@dataclass
class ItivuttakaItem:
    number: str
    start_line: int
    end_line: int
    prose: str
    verse: str

    @property
    def verse_words(self) -> int:
        return count_dataset_words(self.verse)


def line_for_offset(line_starts: list[int], offset: int) -> int:
    line_no = 1
    for idx, start in enumerate(line_starts, 1):
        if start > offset:
            break
        line_no = idx
    return line_no


def normalize_pdf_text(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\x0c", "\n")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("’", "'").replace("‘", "'")
    text = text.replace("—", "-").replace("–", "-")
    text = text.replace("≥h›nissaro", "Thanissaro")
    text = text.translate(
        str.maketrans(
            {
                "›": "a",
                "ª": "m",
                "º": "n",
                "˚": "n",
                "˜": "n",
                "˛": "t",
                "Ò": "u",
                "�": "",
            }
        )
    )
    return text


def clean_prose(text: str) -> str:
    text = FOOTNOTE_NUMBER_RE.sub("", text)
    text = clean_dataset_text(text)
    text = text.replace("wrong viewsat", "wrong views-at")
    text = text.replace("unfeverishand", "unfeverish-and")
    text = text.replace("nonreturn", "non-return")
    text = re.sub(r"\bThis is the meaning of what the Blessed One said.*$", "", text)
    text = re.sub(r"\bSo with regard to this it was said:?\s*$", "", text)
    text = SO_SAID_RE.sub("", text)
    return clean_dataset_text(text)


def clean_verse_lines(text: str) -> str:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if PAGE_NUMBER_RE.match(line):
            continue
        if line == "NOTES" or NOTE_LINE_RE.match(line):
            break
        if SPACED_NOTE_RE.match(line) or line.startswith("See also:"):
            break
        if line.startswith("This, too, was the meaning"):
            break
        line = re.sub(r"^\d+\s+", "", line)
        if line.startswith("This is the meaning"):
            continue
        if line.startswith("So with regard to this it was said"):
            continue
        line = FOOTNOTE_NUMBER_RE.sub("", line)
        line = clean_dataset_text(WHITESPACE_RE.sub(" ", line))
        line = line.replace("wanderingon", "wandering-on")
        line = line.replace("wrong viewsat", "wrong views-at")
        line = line.replace("unfeverishand", "unfeverish-and")
        line = line.replace("nonreturn", "non-return")
        if line:
            lines.append(line)
    return "\n".join(lines)


def split_prose_and_verse(block: str) -> tuple[str, str]:
    quote_start = block.find('"')
    if quote_start < 0:
        return "", ""

    before_quote = block[:quote_start]
    prefix_lines = before_quote.count("\n")
    tail = block[quote_start + 1 :]
    lines = tail.splitlines()
    prose_lines: list[str] = []
    verse_start_idx: int | None = None

    for idx, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped:
            if prose_lines:
                prose_lines.append("")
            continue
        if stripped == "NOTES" or SPACED_NOTE_RE.match(stripped):
            verse_start_idx = idx
            break
        if stripped.startswith(("This is the meaning", "So with regard to this it was said")):
            verse_start_idx = idx
            break
        if re.match(r"^\s{8,}\S", raw) and not PAGE_NUMBER_RE.match(stripped):
            verse_start_idx = idx
            break
        if '"' in raw:
            before, after = raw.split('"', 1)
            normalized_after = re.sub(r"^\d+\s+", "", after.strip())
            if normalized_after.startswith(("This is the meaning", "So with regard")):
                prose_lines.append(before)
                verse_start_idx = idx + 1
                break
        prose_lines.append(raw.replace('"', ""))

    if verse_start_idx is None:
        return "", ""

    prose = clean_prose("\n".join(prose_lines))
    verse = clean_verse_lines("\n".join(lines[verse_start_idx:]))
    return prose, verse


def parse_items(path: Path) -> list[ItivuttakaItem]:
    raw_text = normalize_pdf_text(path.read_text(encoding="utf-8", errors="ignore"))
    line_starts = [match.start() for match in re.finditer(r"^", raw_text, re.MULTILINE)]
    matches = list(SECTION_RE.finditer(raw_text))
    items: list[ItivuttakaItem] = []

    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_text)
        block = raw_text[start:end]
        if "\nGlossary" in block or "\nAbbreviations" in block:
            block = block.split("\nGlossary", 1)[0].split("\nAbbreviations", 1)[0]

        prose, verse = split_prose_and_verse(block)
        if not prose or not verse:
            continue

        items.append(
            ItivuttakaItem(
                number=match.group("number"),
                start_line=line_for_offset(line_starts, start),
                end_line=line_for_offset(line_starts, end),
                prose=prose,
                verse=verse,
            )
        )

    return items


def item_to_row(item: ItivuttakaItem, *, min_target_words: int, max_target_words: int) -> dict | None:
    if item.verse_words < min_target_words or item.verse_words > max_target_words:
        return None

    source_name = "itivuttaka_thanissaro.txt"
    source_lines = [item.start_line, item.end_line]
    target_speaker = "Blessed One"
    prompt = (
        f"Itivuttaka section {item.number}\n\n"
        f"Prose teaching:\n{item.prose}\n\n"
        "Write the verse summary attached to this teaching."
    )
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPTS["buddhist"]},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": item.verse},
        ],
        "metadata": {
            "record_id": make_record_id(
                source_name=source_name,
                kind=f"itivuttaka_prose_to_verse_{item.number}",
                source_lines=source_lines,
                target_speaker=target_speaker,
            ),
            "kind": "itivuttaka_prose_to_verse",
            "source": "Itivuttaka",
            "source_file": source_name,
            "source_lines": source_lines,
            "target_speaker": target_speaker,
            "target_participant": "Participant B",
            "target_words": item.verse_words,
            "section": item.number,
        },
    }


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    return "\n".join(
        [
            f"## Review Example {index}: {metadata['source']}",
            "",
            f"- Record ID: `{metadata['record_id']}`",
            f"- Kind: `{metadata['kind']}`",
            f"- Section: `{metadata['section']}`",
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
    parser = argparse.ArgumentParser(description="Parse Itivuttaka review rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="itivuttaka_dialogue")
    parser.add_argument("--min-target-words", type=int, default=18)
    parser.add_argument("--max-target-words", type=int, default=220)
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    args = parser.parse_args()

    items = parse_items(args.source.expanduser().resolve())
    rows = [
        row
        for item in items
        if (
            row := item_to_row(
                item,
                min_target_words=args.min_target_words,
                max_target_words=args.max_target_words,
            )
        )
    ]

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    write_jsonl(jsonl_path, rows)

    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(
            [
                "# Itivuttaka Review Sample",
                "",
                f"Items parsed: `{len(items)}`",
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

    print(f"Items parsed: {len(items)}")
    print(f"Rows written: {len(rows)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
