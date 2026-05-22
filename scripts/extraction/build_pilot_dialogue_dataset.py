#!/usr/bin/env python3
"""Build a small review-sized dialogue dataset from direct source text.

This is not the full generation step. It creates a pilot JSONL and Markdown
review file from high-confidence explicit turns plus conservative quoted
dialogue recovered from Buddhist speech-cue blocks.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

from mine_dialogue_candidates import (
    SOURCE_DIR,
    Turn,
    mine_speech_cue_blocks,
    normalize_text,
    parse_explicit_turns,
)
from preview_dialogue_examples import (
    SOURCE_LABELS,
    SYSTEM_PROMPTS,
    TARGET_SPEAKERS,
    history_is_usable,
    model_family_for_source,
    participant_for_speaker,
    preview_text,
    select_spread,
    target_is_usable,
)
from platform_sutra_dialogue import SOURCE_NAME as PLATFORM_SOURCE_NAME
from platform_sutra_dialogue import parse_platform_turns


EXPLICIT_SOURCES = [
    "the_key-to-theosophy.txt",
    "The Corpus Hermeticum.txt",
]

BUDDHIST_CUE_SOURCES = [
    "Milinda Panha.txt",
]

QUOTE_RE = re.compile(r'"([^"]+)"|\'([^\']+)\'')
DOUBLE_QUOTE_RE = re.compile(r'"([^"]+)"')
MILINDA_START_RE = re.compile(r"^King Milinda said:", re.IGNORECASE)
BROKEN_LINE_HYPHEN_RE = re.compile(r"(?u)\b([^\W\d_]{2,})-\s+([^\W\d_]{2,})\b")
MISSING_SENTENCE_SPACE_RE = re.compile(r"([.!?])(?=[A-Z])")
SECTION_NUMBER_RE = re.compile(r"(^|\s)\d{1,3}\.\s+(?=[A-Z\"'])")
TRAILING_SECTION_NUMBER_RE = re.compile(r"\s+\d{1,3}\.\s*$")
INLINE_FOOTNOTE_RE = re.compile(r"\*\s*\*[^.]*\.", re.DOTALL)
FOOTNOTE_MARKER_RE = re.compile(r"(?<=[A-Za-z0-9),.?!;:'\"\]])\*+")
INLINE_NOTE_NUMBER_RE = re.compile(
    r"(?<=[A-Za-z\]\)'\"])\d{1,3}\b|(?<=[,;:.?!])\d{1,3}(?=\s+)"
)
BRACKET_NOTE_NUMBER_RE = re.compile(r"\[\d{1,3}\]")
KNOWN_COMPOUND_FIXES = {
    "mindand-matter": "mind-and-matter",
    "mind-andmatter": "mind-and-matter",
    "notself": "not-self",
    "buddhanature": "buddha-nature",
    "buddhanatures": "buddha-natures",
    "superknowledge": "super-knowledge",
    "things-even": "things - even",
    "training-how": "training - how",
    "wisdomreligion": "Wisdom-Religion",
    "fellowbrothers": "fellow-brothers",
    "wellregulated": "well-regulated",
    "deeprooted": "deep-rooted",
}
PLATFORM_SPEAKER_RE = re.compile(
    r"(The patriarch|the patriarch|The master|the master|A monk|The monk|"
    r"the monk|I|Fada|Xingchang|Xuanjue|The nun|the nun)\s+"
    r"(?:asked|said|replied|answered|told)",
    re.IGNORECASE,
)


def repair_broken_hyphen(match: re.Match[str]) -> str:
    left, right = match.group(1), match.group(2)
    if right[:1].isupper():
        return f"{left}-{right}"
    return f"{left}{right}"


def clean_dataset_text(text: str) -> str:
    """Normalize extraction artifacts while preserving source wording."""
    text = normalize_text(text)
    text = INLINE_FOOTNOTE_RE.sub("", text)
    text = FOOTNOTE_MARKER_RE.sub("", text)
    text = BRACKET_NOTE_NUMBER_RE.sub("", text)
    text = INLINE_NOTE_NUMBER_RE.sub("", text)
    text = text.replace("_", "")
    text = BROKEN_LINE_HYPHEN_RE.sub(repair_broken_hyphen, text)
    text = SECTION_NUMBER_RE.sub(r"\1", text)
    text = TRAILING_SECTION_NUMBER_RE.sub("", text)
    text = MISSING_SENTENCE_SPACE_RE.sub(r"\1 ", text)
    text = re.sub(r"\ba(pernicious)\b", r"a \1", text)
    for bad, fixed in KNOWN_COMPOUND_FIXES.items():
        text = re.sub(rf"\b{re.escape(bad)}\b", fixed, text, flags=re.IGNORECASE)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return normalize_text(text)


def count_dataset_words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", clean_dataset_text(text)))


def make_record_id(
    *,
    source_name: str,
    kind: str,
    source_lines: list[int],
    target_speaker: str,
) -> str:
    source_slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")
    speaker_slug = re.sub(r"[^a-z0-9]+", "-", target_speaker.lower()).strip("-")
    return f"{source_slug}:{kind}:{source_lines[0]}-{source_lines[1]}:{speaker_slug}"


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_messages(
    *,
    system_prompt: str,
    history: list[tuple[str, str]],
    target_participant: str,
    target_text: str,
) -> list[dict[str, str]]:
    history_text = "\n".join(
        f"{speaker}: {clean_dataset_text(text)}" for speaker, text in history
    )
    return [
        {"role": "system", "content": clean_dataset_text(system_prompt)},
        {
            "role": "user",
            "content": (
                f"Conversation so far:\n{history_text}\n\n"
                f"Write {target_participant}'s next reply."
            ),
        },
        {"role": "assistant", "content": clean_dataset_text(target_text)},
    ]


def build_explicit_rows(
    source_dir: Path,
    *,
    per_source: int,
    history_turns: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    if per_source <= 0:
        return []

    rows: list[dict] = []

    for source_name in EXPLICIT_SOURCES:
        path = source_dir / source_name
        if not path.exists():
            continue
        turns = parse_explicit_turns(path)
        source_rows: list[dict] = []

        for idx in range(history_turns, len(turns)):
            target = turns[idx]
            if target.speaker not in TARGET_SPEAKERS.get(source_name, set()):
                continue
            if not target_is_usable(
                target, min_words=min_target_words, max_words=max_target_words
            ):
                continue
            history_turn_list = turns[idx - history_turns : idx]
            if not history_is_usable(history_turn_list):
                continue

            family = model_family_for_source(source_name)
            target_participant = participant_for_speaker(source_name, target.speaker)
            source_lines = [history_turn_list[0].start_line, target.end_line]
            history = [
                (
                    f"{participant_for_speaker(source_name, item.speaker)} ({item.speaker})",
                    item.text,
                )
                for item in history_turn_list
            ]
            source_rows.append(
                {
                    "messages": build_messages(
                        system_prompt=SYSTEM_PROMPTS[family],
                        history=history,
                        target_participant=target_participant,
                        target_text=target.text,
                    ),
                    "metadata": {
                        "record_id": make_record_id(
                            source_name=source_name,
                            kind="explicit_next_reply",
                            source_lines=source_lines,
                            target_speaker=target.speaker,
                        ),
                        "kind": "explicit_next_reply",
                        "source": SOURCE_LABELS[source_name],
                        "source_file": source_name,
                        "source_lines": source_lines,
                        "target_speaker": target.speaker,
                        "target_participant": target_participant,
                        "target_words": count_dataset_words(target.text),
                    },
                }
            )

        rows.extend(select_spread(source_rows, per_source))

    return rows


def quoted_strings(text: str) -> list[str]:
    quotes: list[str] = []
    for match in QUOTE_RE.finditer(text):
        quote = match.group(1) if match.group(1) is not None else match.group(2)
        quote = normalize_text(quote)
        if quote:
            quotes.append(quote)
    return quotes


def double_quoted_strings(text: str) -> list[str]:
    quotes: list[str] = []
    for match in DOUBLE_QUOTE_RE.finditer(text):
        quote = normalize_text(match.group(1))
        if quote:
            quotes.append(quote)
    return quotes


def enough_dialogue(quotes: list[str]) -> bool:
    if len(quotes) < 4:
        return False
    return sum(1 for quote in quotes if len(quote.split()) >= 4) >= 3


def parse_milinda_block(text: str) -> list[tuple[str, str]]:
    if not MILINDA_START_RE.match(text):
        return []
    quotes = double_quoted_strings(text)
    if len(quotes) < 2:
        return []

    turns: list[tuple[str, str]] = []
    for idx, quote in enumerate(quotes):
        speaker = "King Milinda" if idx % 2 == 0 else "Venerable Nagasena"
        turns.append((speaker, quote))
    return turns


def normalize_platform_speaker(raw: str) -> str:
    lowered = raw.lower()
    if "patriarch" in lowered:
        return "Fifth Patriarch"
    if "master" in lowered:
        return "Huineng"
    if lowered == "i":
        return "Huineng"
    if "monk" in lowered:
        return "Monk"
    if "nun" in lowered:
        return "Nun"
    return raw


def parse_platform_block(text: str) -> list[tuple[str, str]]:
    turns: list[tuple[str, str]] = []
    for quote_match in QUOTE_RE.finditer(text):
        prefix = text[max(0, quote_match.start() - 90) : quote_match.start()]
        speaker_matches = list(PLATFORM_SPEAKER_RE.finditer(prefix))
        if not speaker_matches:
            continue
        speaker = normalize_platform_speaker(speaker_matches[-1].group(1))
        quote = quote_match.group(1) if quote_match.group(1) is not None else quote_match.group(2)
        quote = normalize_text(quote)
        if quote:
            turns.append((speaker, quote))

    deduped: list[tuple[str, str]] = []
    for speaker, quote in turns:
        if not deduped or deduped[-1] != (speaker, quote):
            deduped.append((speaker, quote))
    return deduped if enough_dialogue([quote for _, quote in deduped]) else []


def cue_turns_to_row(
    *,
    source_name: str,
    source_lines: list[int],
    turns: list[tuple[str, str]],
    min_target_words: int,
    max_target_words: int,
    max_history_turns: int,
    target_index: int | None = None,
) -> dict | None:
    if len(turns) < 2:
        return None

    if target_index is None:
        target_index = len(turns) - 1
    if target_index <= 0 or target_index >= len(turns):
        return None

    history_start = max(0, target_index - max_history_turns)
    history = [
        (speaker, cleaned)
        for speaker, text in turns[history_start:target_index]
        if (cleaned := clean_dataset_text(text))
    ]
    target_speaker, raw_target_text = turns[target_index]
    target_text = clean_dataset_text(raw_target_text)
    if target_speaker not in {"Venerable Nagasena", "Huineng"}:
        return None
    if not history or not target_text:
        return None
    if history[-1][1].rstrip().endswith(":"):
        return None
    target_words = count_dataset_words(target_text)
    if target_words < min_target_words or target_words > max_target_words:
        return None

    family = "buddhist"
    kind = "quoted_buddhist_next_reply"
    target_participant = "Participant B"
    mapped_history = [
        (("Participant B" if speaker in {"Venerable Nagasena", "Huineng"} else "Participant A") + f" ({speaker})", text)
        for speaker, text in history
    ]

    return {
        "messages": build_messages(
            system_prompt=SYSTEM_PROMPTS[family],
            history=mapped_history,
            target_participant=target_participant,
            target_text=target_text,
        ),
        "metadata": {
            "record_id": make_record_id(
                source_name=source_name,
                kind=f"{kind}_{target_index}",
                source_lines=source_lines,
                target_speaker=target_speaker,
            ),
            "kind": kind,
            "source": SOURCE_LABELS[source_name],
            "source_file": source_name,
            "source_lines": source_lines,
            "target_speaker": target_speaker,
            "target_participant": target_participant,
            "target_words": target_words,
            "turn_count": len(turns),
        },
    }


def build_buddhist_rows(
    source_dir: Path,
    *,
    per_source: int,
    max_following_lines: int,
    cue_history_turns: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    if per_source <= 0:
        return []

    rows: list[dict] = []
    for source_name in BUDDHIST_CUE_SOURCES:
        path = source_dir / source_name
        if not path.exists():
            continue

        source_rows: list[dict] = []
        for block in mine_speech_cue_blocks(path, max_following_lines=max_following_lines):
            if source_name == "Milinda Panha.txt":
                turns = parse_milinda_block(block.text)
            else:
                turns = parse_platform_block(block.text)
            if not turns:
                continue
            for target_index, (speaker, _) in enumerate(turns):
                if speaker != "Venerable Nagasena":
                    continue
                row = cue_turns_to_row(
                    source_name=source_name,
                    source_lines=[block.start_line, block.end_line],
                    turns=turns,
                    min_target_words=min_target_words,
                    max_target_words=max_target_words,
                    max_history_turns=cue_history_turns,
                    target_index=target_index,
                )
                if row:
                    source_rows.append(row)

        rows.extend(select_spread(source_rows, per_source))
    return rows


def build_platform_rows(
    source_dir: Path,
    *,
    per_source: int,
    history_turns: int,
    context_gap_lines: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    if per_source <= 0:
        return []

    path = source_dir / PLATFORM_SOURCE_NAME
    if not path.exists():
        return []

    turns = parse_platform_turns(path)
    max_platform_history_turns = max(1, history_turns)
    source_rows: list[dict] = []
    for idx in range(1, len(turns)):
        target = turns[idx]
        if target.speaker != "Huineng":
            continue
        if turns[idx - 1].speaker == "Huineng":
            continue
        if not target_is_usable(
            target, min_words=min_target_words, max_words=max_target_words
        ):
            continue

        history_turn_list: list[Turn] = []
        cursor_start = target.start_line
        for prior_idx in range(idx - 1, -1, -1):
            candidate = turns[prior_idx]
            if cursor_start - candidate.end_line > context_gap_lines:
                break
            history_turn_list.insert(0, candidate)
            cursor_start = candidate.start_line
            if len(history_turn_list) >= max_platform_history_turns:
                break

        if not history_turn_list:
            continue
        if not history_is_usable(history_turn_list):
            continue
        if not any(item.speaker != "Huineng" for item in history_turn_list):
            continue

        kind = "platform_sutra_next_reply"
        source_lines = [history_turn_list[0].start_line, target.end_line]
        history = [
            (
                ("Participant B" if item.speaker == "Huineng" else "Participant A")
                + f" ({item.speaker})",
                item.text,
            )
            for item in history_turn_list
        ]
        source_rows.append(
            {
                "messages": build_messages(
                    system_prompt=SYSTEM_PROMPTS["buddhist"],
                    history=history,
                    target_participant="Participant B",
                    target_text=target.text,
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=PLATFORM_SOURCE_NAME,
                        kind=f"{kind}_{idx}",
                        source_lines=source_lines,
                        target_speaker=target.speaker,
                    ),
                    "kind": kind,
                    "source": SOURCE_LABELS[PLATFORM_SOURCE_NAME],
                    "source_file": PLATFORM_SOURCE_NAME,
                    "source_lines": source_lines,
                    "target_speaker": target.speaker,
                    "target_participant": "Participant B",
                    "target_words": count_dataset_words(target.text),
                },
            }
        )

    return select_spread(source_rows, per_source)


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    lines = [
        f"## Pilot Example {index}: {metadata['source']}",
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
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a small pilot dialogue dataset for review."
    )
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument(
        "--dataset-name",
        default="pilot_dialogue_dataset",
        help="Base filename and review title slug for generated outputs.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("review_outputs/pilot_dialogue_dataset"),
    )
    parser.add_argument("--per-explicit-source", type=int, default=8)
    parser.add_argument("--per-buddhist-source", type=int, default=5)
    parser.add_argument("--per-platform-source", type=int, default=5)
    parser.add_argument("--history-turns", type=int, default=3)
    parser.add_argument(
        "--cue-history-turns",
        type=int,
        default=6,
        help="Maximum prior cue-parsed turns to include before each target reply.",
    )
    parser.add_argument(
        "--platform-context-gap-lines",
        type=int,
        default=5,
        help="Maximum line gap allowed between adjacent Platform Sutra turns.",
    )
    parser.add_argument("--min-target-words", type=int, default=25)
    parser.add_argument(
        "--explicit-min-target-words",
        type=int,
        default=None,
        help="Override minimum target words for explicit esoteric sources.",
    )
    parser.add_argument(
        "--buddhist-min-target-words",
        type=int,
        default=None,
        help="Override minimum target words for Milinda Panha cue dialogue.",
    )
    parser.add_argument(
        "--platform-min-target-words",
        type=int,
        default=None,
        help="Override minimum target words for Platform Sutra dialogue.",
    )
    parser.add_argument("--max-target-words", type=int, default=220)
    parser.add_argument("--max-following-lines", type=int, default=18)
    parser.add_argument("--preview-chars", type=int, default=1000)
    args = parser.parse_args()

    source_dir = args.source_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    explicit_min_target_words = (
        args.explicit_min_target_words
        if args.explicit_min_target_words is not None
        else args.min_target_words
    )
    buddhist_min_target_words = (
        args.buddhist_min_target_words
        if args.buddhist_min_target_words is not None
        else args.min_target_words
    )
    platform_min_target_words = (
        args.platform_min_target_words
        if args.platform_min_target_words is not None
        else args.min_target_words
    )

    explicit_rows = build_explicit_rows(
        source_dir,
        per_source=args.per_explicit_source,
        history_turns=args.history_turns,
        min_target_words=explicit_min_target_words,
        max_target_words=args.max_target_words,
    )
    buddhist_rows = build_buddhist_rows(
        source_dir,
        per_source=args.per_buddhist_source,
        max_following_lines=args.max_following_lines,
        cue_history_turns=args.cue_history_turns,
        min_target_words=buddhist_min_target_words,
        max_target_words=args.max_target_words,
    )
    platform_rows = build_platform_rows(
        source_dir,
        per_source=args.per_platform_source,
        history_turns=args.history_turns,
        context_gap_lines=args.platform_context_gap_lines,
        min_target_words=platform_min_target_words,
        max_target_words=args.max_target_words,
    )
    rows = explicit_rows + buddhist_rows + platform_rows

    dataset_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", args.dataset_name).strip("_")
    if not dataset_name:
        dataset_name = "dialogue_dataset"
    review_title = dataset_name.replace("_", " ").replace("-", " ").title()

    jsonl_path = output_dir / f"{dataset_name}.jsonl"
    md_path = output_dir / f"{dataset_name}_review.md"
    write_jsonl(jsonl_path, rows)
    md_path.write_text(
        "\n".join(
            [
                f"# {review_title} Review",
                "",
                "This is a direct-source dialogue dataset. Nothing here has been",
                "AI-regenerated; records are extracted from the original texts.",
                "",
                *[
                    row_to_markdown(row, idx, preview_chars=args.preview_chars)
                    for idx, row in enumerate(rows, 1)
                ],
            ]
        ),
        encoding="utf-8",
    )

    counts: dict[str, int] = {}
    for row in rows:
        source = row["metadata"]["source"]
        counts[source] = counts.get(source, 0) + 1

    print(f"Rows written: {len(rows)}")
    for source, count in sorted(counts.items()):
        print(f"{source}: {count}")
    print(f"JSONL: {jsonl_path}")
    print(f"Markdown: {md_path}")


if __name__ == "__main__":
    main()
