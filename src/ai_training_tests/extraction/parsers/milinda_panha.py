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
    normalize_text,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/clean/milindapanha_suttacentral.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"
DEFAULT_MIN_TARGET_WORDS = 5
KING_MILINDA = "King Milinda"
VEN_NAGASENA = "Venerable N\u0101gasena"
SECTION_RE = re.compile(r"^## (?P<section>mil[\d.]+)$", re.IGNORECASE)
SPEAKER_CUE_RE = re.compile(
    "^(?:Then,?\\s+)?(?P<speaker>King Milinda|Venerable (?:N\u0101gasena|Nagasena))\\s+"
    "(?:said|asked|replied|answered|declared)\\b.*$",
    re.IGNORECASE,
)
SPEAKER_CUE_FRAGMENT_RE = re.compile(
    "(?P<speaker>King Milinda|Venerable (?:N\u0101gasena|Nagasena))\\s+"
    "(?:said(?:\\s+this)?|asked|replied|answered|declared)\\b",
    re.IGNORECASE,
)


@dataclass
class Line:
    line_no: int
    text: str
    section_ref: str


@dataclass
class Turn:
    speaker: str
    text: str
    start_line: int
    end_line: int
    section_ref: str

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


def canonical_speaker(raw: str) -> str | None:
    lowered = clean_dataset_text(raw).lower()
    if lowered == KING_MILINDA.lower():
        return KING_MILINDA
    if lowered in {VEN_NAGASENA.lower(), "venerable nagasena"}:
        return VEN_NAGASENA
    return None


def iter_lines(path: Path) -> list[Line]:
    lines: list[Line] = []
    section_ref = ""
    for line_no, raw in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        normalized = normalize_text(raw)
        if not normalized:
            continue
        if section_match := SECTION_RE.match(normalized):
            section_ref = section_match.group("section")
            lines.append(Line(line_no=line_no, text=normalized, section_ref=section_ref))
            continue
        text = clean_dataset_text(raw)
        if not text:
            continue
        lines.append(Line(line_no=line_no, text=text, section_ref=section_ref))
    return lines


def extract_quote_text(text: str) -> str | None:
    first_quote = text.find('"')
    last_quote = text.rfind('"')
    if first_quote == -1 or last_quote <= first_quote:
        return None
    quote = clean_dataset_text(text[first_quote + 1 : last_quote])
    return quote or None


def quote_is_complete(parts: list[str]) -> bool:
    joined = " ".join(parts)
    return joined.count('"') >= 2 and joined.find('"') != joined.rfind('"')


def alternate_speaker(speaker: str) -> str | None:
    if speaker == KING_MILINDA:
        return VEN_NAGASENA
    if speaker == VEN_NAGASENA:
        return KING_MILINDA
    return None


def infer_speaker(pending_speaker: str | None, previous_turn: Turn | None, section_ref: str) -> str | None:
    if pending_speaker:
        return pending_speaker
    if previous_turn is None or previous_turn.section_ref != section_ref:
        return None
    return alternate_speaker(previous_turn.speaker)


def speaker_from_fragment(text: str) -> str | None:
    matches = list(SPEAKER_CUE_FRAGMENT_RE.finditer(text))
    if not matches:
        return None
    return canonical_speaker(matches[-1].group("speaker"))


def iter_inline_quotes(text: str) -> list[tuple[str, str]]:
    quotes: list[tuple[str, str]] = []
    cursor = 0
    while True:
        start = text.find('"', cursor)
        if start == -1:
            break
        end = text.find('"', start + 1)
        if end == -1:
            break
        quote = clean_dataset_text(text[start + 1 : end])
        if quote:
            quotes.append((text[cursor:start], quote))
        cursor = end + 1
    return quotes


def extract_inline_turns(line: Line, speaker: str) -> list[Turn]:
    turns: list[Turn] = []
    current_speaker: str | None = speaker
    for prefix, quote in iter_inline_quotes(line.text):
        explicit_speaker = speaker_from_fragment(prefix)
        if explicit_speaker is not None:
            current_speaker = explicit_speaker
        if current_speaker is None:
            break
        if turns and turns[-1].speaker == current_speaker:
            turns[-1].text = clean_dataset_text(f"{turns[-1].text} {quote}")
            turns[-1].end_line = line.line_no
        else:
            turns.append(
                Turn(
                    speaker=current_speaker,
                    text=quote,
                    start_line=line.line_no,
                    end_line=line.line_no,
                    section_ref=line.section_ref,
                )
            )
        current_speaker = alternate_speaker(current_speaker)
    return turns


def parse_turns(path: Path) -> list[Turn]:
    turns: list[Turn] = []
    pending_speaker: str | None = None
    current_speaker: str | None = None
    current_parts: list[str] = []
    current_start_line = 0
    current_section_ref = ""

    for line in iter_lines(path):
        if SECTION_RE.match(line.text):
            pending_speaker = None
            current_speaker = None
            current_parts = []
            current_start_line = 0
            current_section_ref = line.section_ref
            continue

        if speaker_match := SPEAKER_CUE_RE.match(line.text):
            pending_speaker = canonical_speaker(speaker_match.group("speaker"))
            if pending_speaker and '"' in line.text:
                turns.extend(extract_inline_turns(line, pending_speaker))
                pending_speaker = None
            continue

        if current_parts:
            current_parts.append(line.text)
            if quote_is_complete(current_parts):
                quote = extract_quote_text(" ".join(current_parts))
                if quote and current_speaker:
                    turns.append(
                        Turn(
                            speaker=current_speaker,
                            text=quote,
                            start_line=current_start_line,
                            end_line=line.line_no,
                            section_ref=current_section_ref,
                        )
                    )
                current_speaker = None
                current_parts = []
                current_start_line = 0
                pending_speaker = None
            continue

        if '"' not in line.text:
            pending_speaker = None
            continue

        speaker = infer_speaker(pending_speaker, turns[-1] if turns else None, line.section_ref)
        if speaker is None:
            pending_speaker = None
            continue

        current_speaker = speaker
        current_parts = [line.text]
        current_start_line = line.line_no
        current_section_ref = line.section_ref
        if quote_is_complete(current_parts):
            quote = extract_quote_text(current_parts[0])
            if quote:
                turns.append(
                    Turn(
                        speaker=current_speaker,
                        text=quote,
                        start_line=current_start_line,
                        end_line=line.line_no,
                        section_ref=line.section_ref,
                    )
                )
            current_speaker = None
            current_parts = []
            current_start_line = 0
            pending_speaker = None

    return turns


def history_is_usable(history: list[Turn], target: Turn) -> bool:
    if not history:
        return False
    if history[-1].speaker != KING_MILINDA:
        return False
    if any(turn.section_ref != target.section_ref for turn in history):
        return False
    if any(turn.speaker == next_turn.speaker for turn, next_turn in zip(history, history[1:])):
        return False
    if any(not 3 <= turn.word_count <= 260 for turn in history):
        return False
    if len(history) == 1:
        return history[0].text.rstrip().endswith("?")
    return True


def conversation_window_for_target(
    turns: list[Turn], target_index: int, *, max_history_turns: int
) -> list[Turn] | None:
    if target_index <= 0:
        return None
    target = turns[target_index]
    history_reversed: list[Turn] = []
    for pos in range(target_index - 1, -1, -1):
        turn = turns[pos]
        if turn.section_ref != target.section_ref:
            break
        if history_reversed and history_reversed[-1].speaker == turn.speaker:
            break
        history_reversed.append(turn)
        if len(history_reversed) >= max_history_turns:
            break
    history = list(reversed(history_reversed))
    if not history_is_usable(history, target):
        return None
    return history


def build_rows(
    turns: list[Turn], *, max_history_turns: int, min_target_words: int, max_target_words: int
) -> list[dict]:
    rows: list[dict] = []
    source_name = DEFAULT_SOURCE.name
    kind = "quoted_buddhist_next_reply"
    for idx in range(1, len(turns)):
        target = turns[idx]
        if target.speaker != VEN_NAGASENA:
            continue
        if target.word_count < min_target_words or target.word_count > max_target_words:
            continue
        history = conversation_window_for_target(
            turns,
            idx,
            max_history_turns=max_history_turns,
        )
        if not history:
            continue
        rows.append(
            {
                "messages": build_messages(
                    system_prompt=SYSTEM_PROMPTS["buddhist"],
                    history=[
                        (
                            ("Participant B" if turn.speaker == target.speaker else "Participant A")
                            + f" ({turn.speaker})",
                            turn.text,
                        )
                        for turn in history
                    ],
                    target_participant="Participant B",
                    target_text=target.text,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind=f"{kind}_{idx}",
                        source_lines=[history[0].start_line, target.end_line],
                        target_speaker=target.speaker,
                    ),
                    "kind": kind,
                    "source": "Milinda Panha",
                    "source_file": source_name,
                    "source_lines": [history[0].start_line, target.end_line],
                    "target_speaker": target.speaker,
                    "target_participant": "Participant B",
                    "target_words": target.word_count,
                    "section_ref": target.section_ref,
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
            f"- Section: `{metadata['section_ref']}`",
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
    parser = argparse.ArgumentParser(description="Parse Milinda Panha dialogue rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="milinda_panha_dialogue")
    parser.add_argument("--max-history-turns", type=int, default=6)
    parser.add_argument("--min-target-words", type=int, default=DEFAULT_MIN_TARGET_WORDS)
    parser.add_argument("--max-target-words", type=int, default=260)
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    args = parser.parse_args()

    turns = parse_turns(args.source.expanduser().resolve())
    rows = build_rows(
        turns,
        max_history_turns=args.max_history_turns,
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
                "# Milinda Panha Dialogue Review Sample",
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
