#!/usr/bin/env python3
"""Parse reviewed dialogue rows from the Vimalakirti Nirdesa Sutra."""

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
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/clean/vimalakirti_nirdesa_sutra.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

SPEAKER_TOKEN = (
    r"(?:[Tt]he\s+)?"
    r"(?:venerable\s+|elder\s+|crown prince\s+|young\s+Licchavi\s+|Licchavi\s+|bodhisattva\s+)?"
    r"[A-ZÁ][\wÁáÉéÍíÓóÚúñ-]*"
    r"(?:\s+[A-ZÁ][\wÁáÉéÍíÓóÚúñ-]*){0,4}"
)
LEADING_RE = re.compile(
    rf"(?P<speaker>{SPEAKER_TOKEN})\s+"
    r"(?P<verb>said|replied|declared|answered|asked|addressed|spoke|further addressed|thought to himself)"
    r"(?:\s+(?:to\s+)?(?P<addressee>(?:the|that|those|this)\s+[^,:]+|[^,:]+))?"
    r"[,:\s]+\s*\"(?P<quote>.+)\"$",
    re.IGNORECASE,
)
TRAILING_RE = re.compile(
    r'^"(?P<quote>.+)"\s*,?\s*'
    r"(?P<verb>replied|said|declared|answered|asked)\s+"
    r"(?P<speaker>.+?)"
    r"(?:\s+to\s+(?P<addressee>[^,.]+))?[.]?$",
    re.IGNORECASE,
)
COLON_RE = re.compile(rf"^(?P<speaker>{SPEAKER_TOKEN}):\s*(?P<quote>.+?)$", re.IGNORECASE)
NAME_CLEAN_RE = re.compile(
    r"^(?:the\s+venerable|venerable|the\s+young\s+Licchavi|the\s+Licchavi)\s+",
    re.IGNORECASE,
)
GROUP_MARKERS = (
    "young Licchavis",
    "living beings",
    "householders",
    "bhikkhus",
    "bodhisattvas",
    "crowd",
)
PRONOUN_SPEAKERS = {"they", "he", "she", "it", "we", "you", "i"}
ALLOWED_LOWER_TOKENS = {
    "the",
    "venerable",
    "elder",
    "crown",
    "prince",
    "young",
    "licchavi",
    "bodhisattva",
    "tathagata",
    "tathágata",
}


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
    paragraph_index: int

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


def iter_paragraphs(path: Path) -> list[Paragraph]:
    paragraphs: list[Paragraph] = []
    current_lines: list[str] = []
    start_line = 1

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


def canonical_speaker(name: str) -> str:
    name = clean_dataset_text(name)
    name = re.sub(r"^(?:Then,?\s+)", "", name, flags=re.IGNORECASE)
    name = re.sub(r"^(?:At that moment\s+)", "", name, flags=re.IGNORECASE)
    name = NAME_CLEAN_RE.sub("", name)
    name = re.sub(r"^the\s+", "The ", name)
    name = name.replace("The Lord Buddha", "The Buddha").replace("Lord Buddha", "The Buddha")
    name = name.replace("The Lord", "The Buddha")
    name = name.replace("The Buddha then", "The Buddha")
    name = name.replace("The Tathágata", "The Buddha")
    name = re.sub(r"^The Buddha has$", "The Buddha", name)
    name = re.sub(r"^The Buddha,?\s+knowing telepathically.*$", "The Buddha", name)
    name = re.sub(r"^The Buddha knew this thought.*$", "The Buddha", name)
    name = re.sub(r"^Licchavi ", "", name)
    name = re.sub(r"\s+and\s+the\s+five\s+hundred.+$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s*\(.*?\)\s*$", "", name)
    name = name.strip(" ,.;:-")
    return name


def extract_turn_from_paragraph(paragraph: str) -> tuple[str | None, str | None, str | None]:
    text = clean_dataset_text(paragraph).replace("“", '"').replace("”", '"')
    for pattern in (LEADING_RE, TRAILING_RE):
        match = pattern.search(text)
        if not match:
            continue
        speaker = canonical_speaker(match.group("speaker"))
        addressee = match.groupdict().get("addressee")
        if addressee:
            addressee = canonical_speaker(addressee)
        quote = clean_dataset_text(match.group("quote"))
        return speaker, addressee, quote
    colon_match = COLON_RE.match(text)
    if colon_match:
        speaker = canonical_speaker(colon_match.group("speaker"))
        quote = clean_dataset_text(colon_match.group("quote"))
        return speaker, None, quote
    return None, None, None


def speaker_is_usable(speaker: str | None) -> bool:
    if not speaker:
        return False
    lowered = speaker.lower()
    if lowered in PRONOUN_SPEAKERS:
        return False
    if any(marker.lower() in lowered for marker in GROUP_MARKERS):
        return False
    if speaker in {"Lord", "Friends"}:
        return False
    if "," in speaker or " has" in lowered:
        return False
    if any(
        phrase in lowered
        for phrase in (
            " thought",
            " addressed ",
            " applauded ",
            " exclaimed ",
            " asked ",
            " replied ",
            " said ",
            " declared ",
        )
    ):
        return False
    for token in re.findall(r"[A-Za-zÁáÉéÍíÓóÚúñÑ-]+", speaker):
        if token.lower() in ALLOWED_LOWER_TOKENS:
            continue
        if token[0].islower():
            return False
    return True


def turn_text_is_complete(text: str | None) -> bool:
    if not text:
        return False
    return bool(re.search(r'[.!?"]$', text.strip()))


def participant_label(*, target_speaker: str, speaker: str) -> str:
    participant = "Participant B" if speaker == target_speaker else "Participant A"
    return f"{participant} ({speaker})"


def parse_turns(path: Path) -> list[Turn]:
    rows = iter_paragraphs(path)
    started = False
    turns: list[Turn] = []
    for paragraph_index, paragraph in enumerate(rows):
        if not started and "Thus have I heard:" in paragraph.text:
            started = True
        if not started:
            continue
        speaker, _addressee, quote = extract_turn_from_paragraph(paragraph.text)
        if not speaker_is_usable(speaker) or not turn_text_is_complete(quote):
            continue
        turns.append(
            Turn(
                speaker=speaker or "",
                text=quote,
                start_line=paragraph.start_line,
                end_line=paragraph.end_line,
                paragraph_index=paragraph_index,
            )
        )
    return turns


def history_is_usable(history: list[Turn], target: Turn) -> bool:
    if not history:
        return False
    if history[-1].speaker == target.speaker:
        return False
    if any(not 5 <= turn.word_count <= 260 for turn in history):
        return False
    history_words = sum(turn.word_count for turn in history)
    if len(history) == 1 and not history[-1].text.rstrip().endswith("?"):
        return False
    if history_words >= 24:
        return True
    return history[-1].word_count >= 12 and history[-1].text.rstrip().endswith("?")


def conversation_window_for_target(
    turns: list[Turn],
    target_index: int,
    *,
    max_history_turns: int = 8,
    max_line_gap: int = 60,
    max_paragraph_gap: int = 1,
) -> list[Turn] | None:
    if target_index <= 0:
        return None

    target = turns[target_index]
    partner = turns[target_index - 1]
    if partner.speaker == target.speaker:
        return None
    if target.paragraph_index - partner.paragraph_index > max_paragraph_gap:
        return None

    allowed_speakers = {target.speaker, partner.speaker}
    history_reversed: list[Turn] = []

    for pos in range(target_index - 1, -1, -1):
        turn = turns[pos]
        if turn.speaker not in allowed_speakers:
            break
        if history_reversed:
            newer = history_reversed[-1]
            if newer.start_line - turn.end_line > max_line_gap:
                break
            if newer.paragraph_index - turn.paragraph_index > max_paragraph_gap:
                break
        history_reversed.append(turn)
        if len(history_reversed) >= max_history_turns:
            break

    history = list(reversed(history_reversed))
    if not history:
        return None
    if target.start_line - history[-1].end_line > max_line_gap:
        return None
    if {turn.speaker for turn in history + [target]} != allowed_speakers:
        return None
    if any(turn.speaker == next_turn.speaker for turn, next_turn in zip(history, history[1:])):
        return None
    if not history_is_usable(history, target):
        return None
    return history


def build_rows(
    turns: list[Turn], *, max_history_turns: int, min_target_words: int, max_target_words: int
) -> list[dict]:
    rows: list[dict] = []
    source_name = DEFAULT_SOURCE.name
    for idx in range(1, len(turns)):
        target = turns[idx]
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
                            participant_label(target_speaker=target.speaker, speaker=turn.speaker),
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
                        kind="vimalakirti_next_reply",
                        source_lines=[history[0].start_line, target.end_line],
                        target_speaker=target.speaker,
                    ),
                    "kind": "vimalakirti_next_reply",
                    "source": "Vimalakirti Nirdesa Sutra",
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
    parser = argparse.ArgumentParser(description="Parse Vimalakirti dialogue rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="vimalakirti_dialogue")
    parser.add_argument("--max-history-turns", type=int, default=8)
    parser.add_argument("--min-target-words", type=int, default=18)
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
                "# Vimalakirti Dialogue Review Sample",
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
