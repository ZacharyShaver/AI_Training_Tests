#!/usr/bin/env python3
"""Parse a personal-use English Blue Cliff Record source into review rows."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

from build_pilot_dialogue_dataset import (
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    write_jsonl,
)
from preview_dialogue_examples import SYSTEM_PROMPTS, preview_text, select_spread


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = (
    REPO_ROOT / "source_texts/buddhist/raw/blue_cliff_record_wonderwheel_wayback.html"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

CASE_MARKER_RE = re.compile(r"@@CASE(?P<number>\d+)@@")
CASE_HEADING_RE = re.compile(r"^(?P<number>\d+)\.?\s*(?P<title>.*)$")
ODE_RE = re.compile(
    r"(?:\[Xuedou's(?:\s+Second)?\]\s+Ode|Xuedou's\s+ode)\s+says:\s*",
    re.IGNORECASE,
)
QUOTE_RE = re.compile(r'"(?P<quote>[^"]+)"')
SPEAKER_BEFORE_RE = re.compile(
    r"(?P<speaker>"
    r"(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,3})|"
    r"(?:A|The|the)\s+(?:monk|student|teacher|emperor|assembly|official|master|monks)"
    r")\s+"
    r"(?P<verb>asked|said|stated|replied|answered|shouted|called|taught|instructed|"
    r"substituted himself and said|handed down words and said)"
    r"(?:\s+[^:\".?!]{0,80})?[,:.]?\s*$",
    re.IGNORECASE,
)
SPEAKER_AFTER_RE = re.compile(
    r"^\s*,?\s*"
    r"(?:(?P<verb>asked|said|stated|replied|answered|shouted|called|taught|instructed)\s+"
    r"(?P<speaker>"
    r"(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,3})|"
    r"(?:the|a)\s+(?:monk|student|teacher|emperor|assembly|official|master|monks)"
    r")|"
    r"(?P<speaker_first>"
    r"(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,3})|"
    r"(?:The|A|the|a)\s+(?:monk|student|teacher|emperor|assembly|official|master|monks)"
    r")\s+"
    r"(?P<verb_after>asked|said|stated|replied|answered|shouted|called|taught|instructed))\b",
    re.IGNORECASE,
)


@dataclass
class BlueCliffCase:
    number: int
    title: str
    raised: str
    odes: list[str]


@dataclass
class DialogueTurn:
    speaker: str
    text: str


class CaseTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"p", "div", "br", "pre", "h1", "h2", "h3"}:
            self.parts.append("\n")
        for key, value in attrs:
            if key == "name" and value and re.fullmatch(r"case\d+", value):
                self.parts.append(f"\n@@{value.upper()}@@\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self.parts.append(unescape(f"&#{name};"))


def html_to_text(path: Path) -> str:
    raw = path.read_text(encoding="windows-1252", errors="ignore")
    parser = CaseTextExtractor()
    parser.feed(raw)
    text = "".join(parser.parts)
    text = text.replace("\r", "\n")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\ufffd", " ")
    text = re.sub(r"[ \t\xa0]+", " ", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_blue_text(text: str) -> str:
    text = re.sub(r"\[\s*fn\d+\s*\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\(alt\.?:.*?\)", "", text, flags=re.IGNORECASE)
    text = text.replace("<TOC>", "").replace("^TOC^", "")
    return clean_dataset_text(text)


def parse_heading(block: str, number: int) -> tuple[str, str]:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if not lines:
        return f"Case {number}", ""

    first = lines[0]
    match = CASE_HEADING_RE.match(first)
    title_parts: list[str] = []
    if match:
        if match.group("title"):
            title_parts.append(match.group("title"))
        lines = lines[1:]
    else:
        lines = lines[1:]

    while lines and lines[0] != "Raised:" and "pointer says:" not in lines[0].lower():
        title_parts.append(lines.pop(0))

    title = clean_blue_text(" ".join(title_parts)) or f"Case {number}"
    return title, "\n".join(lines)


def parse_case_block(number: int, block: str) -> BlueCliffCase | None:
    block = block.split("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", 1)[0]
    title, remainder = parse_heading(block, number)
    if "Raised:" not in remainder:
        return None

    remainder = remainder.split("Raised:", 1)[1]
    remainder = remainder.split("^TOC^", 1)[0].split("<TOC>", 1)[0]
    ode_matches = list(ODE_RE.finditer(remainder))
    if ode_matches:
        raised = remainder[: ode_matches[0].start()]
        odes: list[str] = []
        for idx, match in enumerate(ode_matches):
            start = match.end()
            end = ode_matches[idx + 1].start() if idx + 1 < len(ode_matches) else len(remainder)
            ode = clean_blue_text(remainder[start:end])
            if ode:
                odes.append(ode)
    else:
        raised = remainder
        odes = []

    raised = clean_blue_text(raised)
    if not raised:
        return None
    return BlueCliffCase(number=number, title=title, raised=raised, odes=odes)


def parse_cases(path: Path) -> list[BlueCliffCase]:
    text = html_to_text(path)
    markers = list(CASE_MARKER_RE.finditer(text))
    cases: list[BlueCliffCase] = []
    for idx, marker in enumerate(markers):
        number = int(marker.group("number"))
        start = marker.end()
        end = markers[idx + 1].start() if idx + 1 < len(markers) else len(text)
        if case := parse_case_block(number, text[start:end]):
            cases.append(case)
    return cases


def build_messages(
    *,
    history: list[tuple[str, str]],
    target_speaker: str,
    target_text: str,
) -> list[dict[str, str]]:
    history_text = "\n".join(
        f"{speaker}: {clean_blue_text(text)}" for speaker, text in history
    )
    return [
        {"role": "system", "content": clean_dataset_text(SYSTEM_PROMPTS["buddhist"])},
        {
            "role": "user",
            "content": (
                f"Conversation so far:\n{history_text}\n\n"
                f"Write Participant B ({target_speaker})'s next reply."
            ),
        },
        {"role": "assistant", "content": clean_blue_text(target_text)},
    ]


def case_dialogue_history(case: BlueCliffCase) -> list[tuple[str, str]] | None:
    turns = extract_case_dialogue_turns(case)
    has_quote_marks = '"' in case.raised
    quote_count = len(
        [
            match
            for match in QUOTE_RE.finditer(case.raised)
            if clean_blue_text(match.group("quote"))
            and not clean_blue_text(match.group("quote")).endswith(",")
        ]
    )

    if quote_count == 0:
        if has_quote_marks:
            return None
        return [(f"Participant A (Blue Cliff case {case.number}: {case.title})", case.raised)]
    if len(turns) != quote_count or len(turns) < 2:
        return None
    if any(
        previous.speaker == current.speaker
        for previous, current in zip(turns, turns[1:])
    ):
        return None

    first_speaker = turns[0].speaker
    second_speaker = next(
        (turn.speaker for turn in turns if turn.speaker != first_speaker), None
    )
    if second_speaker is None:
        return None
    distinct_speakers = {turn.speaker for turn in turns}
    if len(distinct_speakers) > 2:
        return None
    if "Xuedou" in distinct_speakers:
        return None

    history: list[tuple[str, str]] = []
    for turn in turns:
        participant = "Participant A" if turn.speaker == first_speaker else "Participant B"
        history.append((f"{participant} ({turn.speaker})", turn.text))
    return history


def case_to_ode_rows(case: BlueCliffCase) -> list[dict]:
    rows: list[dict] = []
    source_name = "blue_cliff_record_wonderwheel_wayback.html"
    history = case_dialogue_history(case)
    if history is None:
        return rows

    for idx, ode in enumerate(case.odes, 1):
        target_speaker = "Xuedou"
        kind = "blue_cliff_case_ode" if idx == 1 else "blue_cliff_case_second_ode"
        rows.append(
            {
                "messages": build_messages(
                    history=history,
                    target_speaker=target_speaker,
                    target_text=ode,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind=f"{kind}_{case.number}_{idx}",
                        source_lines=[case.number, case.number],
                        target_speaker=target_speaker,
                    ),
                    "kind": kind,
                    "source": "The Blue Cliff Record",
                    "source_file": source_name,
                    "source_lines": [case.number, case.number],
                    "target_speaker": target_speaker,
                    "target_participant": "Participant B",
                    "target_words": count_dataset_words(ode),
                    "case_title": case.title,
                    "source_scope": "personal_local_only_translation",
                },
            }
        )
    return rows


def canonical_speaker(raw: str | None) -> str | None:
    if not raw:
        return None
    speaker = clean_blue_text(raw).strip(" ,.;:")
    lowered = speaker.lower()
    narrative_starts = (
        "again ",
        "and ",
        "as ",
        "at ",
        "he ",
        "later ",
        "next ",
        "personally ",
        "picked ",
        "then ",
        "therefore ",
        "who ",
    )
    narrative_fragments = (
        " and",
        " who",
        " one day",
        " at that time",
        " as ",
    )
    if lowered.startswith(narrative_starts) or any(
        fragment in lowered for fragment in narrative_fragments
    ):
        return None
    if lowered in {"he", "she", "they"}:
        return None
    if lowered in {"a monk", "the monk"}:
        return "Monk"
    if lowered in {"the emperor", "emperor"}:
        return "Emperor"
    if lowered in {"the official", "official"}:
        return "Official"
    if lowered in {"the monks"}:
        return "Monks"
    if lowered in {"xuedou's attached words", "attached words"}:
        return None
    narrative_terms = [
        " again",
        " also",
        " separately",
        " thereupon",
        " then",
        " at ",
        " with ",
    ]
    if any(term in lowered for term in narrative_terms):
        return None
    if len(speaker.split()) > 4:
        return None
    return speaker[:1].upper() + speaker[1:]


def speaker_before(text: str, quote_start: int) -> str | None:
    prefix = text[max(0, quote_start - 180) : quote_start]
    matches = list(SPEAKER_BEFORE_RE.finditer(prefix))
    return matches[-1].group("speaker") if matches else None


def speaker_after(text: str, quote_end: int) -> str | None:
    suffix = text[quote_end : quote_end + 120]
    match = SPEAKER_AFTER_RE.search(suffix)
    if not match:
        return None
    return match.group("speaker") or match.group("speaker_first")


def extract_case_dialogue_turns(case: BlueCliffCase) -> list[DialogueTurn]:
    turns: list[DialogueTurn] = []
    for match in QUOTE_RE.finditer(case.raised):
        quote = clean_blue_text(match.group("quote"))
        if not quote or quote.endswith(","):
            continue
        speaker = canonical_speaker(speaker_before(case.raised, match.start()))
        if speaker is None:
            speaker = canonical_speaker(speaker_after(case.raised, match.end()))
        if speaker is None:
            continue
        turns.append(DialogueTurn(speaker=speaker, text=quote))
    return turns


def internal_dialogue_rows(case: BlueCliffCase, *, history_quotes: int) -> list[dict]:
    source_name = "blue_cliff_record_wonderwheel_wayback.html"
    turns = extract_case_dialogue_turns(case)

    rows: list[dict] = []
    for idx, target in enumerate(turns):
        if idx == 0:
            continue
        target_speaker = target.speaker
        target_text = target.text
        history = turns[max(0, idx - history_quotes) : idx]
        if not any(turn.speaker != target_speaker for turn in history):
            continue
        mapped_history = [
            (
                (
                    "Participant B"
                    if turn.speaker == target_speaker
                    else "Participant A"
                )
                + f" ({turn.speaker})",
                turn.text,
            )
            for turn in history
        ]
        rows.append(
            {
                "messages": build_messages(
                    history=mapped_history,
                    target_speaker=target_speaker,
                    target_text=target_text,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind=f"blue_cliff_internal_dialogue_{case.number}_{idx}",
                        source_lines=[case.number, case.number],
                        target_speaker=target_speaker,
                    ),
                    "kind": "blue_cliff_internal_dialogue",
                    "source": "The Blue Cliff Record",
                    "source_file": source_name,
                    "source_lines": [case.number, case.number],
                    "target_speaker": target_speaker,
                    "target_participant": "Participant B",
                    "target_words": count_dataset_words(target_text),
                    "case_title": case.title,
                    "source_scope": "personal_local_only_translation",
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
            f"- Case: `{metadata['source_lines'][0]}. {metadata['case_title']}`",
            f"- Target: `{metadata['target_participant']} ({metadata['target_speaker']})`",
            f"- Target words: `{metadata['target_words']}`",
            f"- Scope: `{metadata['source_scope']}`",
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
    parser = argparse.ArgumentParser(description="Parse Blue Cliff Record review rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="blue_cliff_record_dialogue")
    parser.add_argument("--sample-count", type=int, default=12)
    parser.add_argument("--preview-chars", type=int, default=1400)
    parser.add_argument("--include-internal-dialogue", action="store_true")
    parser.add_argument("--only-internal-dialogue", action="store_true")
    parser.add_argument("--history-quotes", type=int, default=3)
    args = parser.parse_args()

    cases = parse_cases(args.source.expanduser().resolve())
    ode_rows = [] if args.only_internal_dialogue else [
        row for case in cases for row in case_to_ode_rows(case)
    ]
    internal_rows = [
        row for case in cases for row in internal_dialogue_rows(case, history_quotes=args.history_quotes)
    ]
    rows = list(ode_rows)
    if args.include_internal_dialogue or args.only_internal_dialogue:
        rows.extend(internal_rows)

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    write_jsonl(jsonl_path, rows)

    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(
            [
                "# Blue Cliff Record Review Sample",
                "",
                "Source scope: `personal_local_only_translation`",
                f"Cases parsed: `{len(cases)}`",
                f"Ode rows parsed: `{len(ode_rows)}`",
                f"Internal dialogue rows mined: `{len(internal_rows)}`",
                f"Rows written: `{len(rows)}`",
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

    print(f"Cases parsed: {len(cases)}")
    print(f"Ode rows parsed: {len(ode_rows)}")
    print(f"Internal dialogue rows mined: {len(internal_rows)}")
    print(f"Rows written: {len(rows)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
