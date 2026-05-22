#!/usr/bin/env python3
"""Create small human-review previews for dialogue training examples.

The output is deliberately small and readable. It is meant for review before any
full dataset is generated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

from mine_dialogue_candidates import (
    BODY_LINE_RANGES,
    SOURCE_DIR,
    Turn,
    count_words,
    mine_speech_cue_blocks,
    normalize_text,
    parse_explicit_turns,
)


EXPLICIT_SOURCES = [
    "the_key-to-theosophy.txt",
    "The Corpus Hermeticum.txt",
]

CUE_SOURCES = [
    "Milinda Panha.txt",
    "Platform Sutra .txt",
    "Asclepius.txt",
]

SOURCE_LABELS = {
    "the_key-to-theosophy.txt": "The Key to Theosophy",
    "The Corpus Hermeticum.txt": "The Corpus Hermeticum",
    "Milinda Panha.txt": "Milinda Panha",
    "Platform Sutra .txt": "Platform Sutra",
    "Asclepius.txt": "Asclepius",
}

SYSTEM_PROMPTS = {
    "hermetic": (
        "You are a Hermetic philosophical interlocutor. Reply naturally, reason "
        "from the source tradition, and keep the exchange grounded rather than "
        "generic."
    ),
    "theosophy": (
        "You are a Theosophical philosophical interlocutor. Reply naturally, "
        "reason from the source tradition, and keep the exchange grounded rather "
        "than generic."
    ),
    "buddhist": (
        "You are a Buddhist philosophical interlocutor. Reply naturally, reason "
        "from the source tradition, and keep the exchange grounded rather than "
        "generic."
    ),
}

TARGET_SPEAKERS = {
    "the_key-to-theosophy.txt": {"Theosophist"},
    "The Corpus Hermeticum.txt": {"Hermes", "Mind"},
}

CONTAMINATION_MARKERS = [
    "The Corpus Hermeticum",
    "The Corpus Hermetica",
    "Table of Contents",
    "GLOSSARY",
    "FINIS",
    "Bibliography",
    "Index",
    "Epilogue",
]


def model_family_for_source(source_name: str) -> str:
    if source_name == "the_key-to-theosophy.txt":
        return "theosophy"
    if source_name == "The Corpus Hermeticum.txt":
        return "hermetic"
    return "buddhist"


def participant_for_speaker(source_name: str, speaker: str) -> str:
    if source_name == "the_key-to-theosophy.txt":
        return "Participant A" if speaker == "Enquirer" else "Participant B"
    if source_name == "The Corpus Hermeticum.txt":
        if speaker in {"Hermes", "Mind"}:
            return "Participant B"
        return "Participant A"
    return speaker


def target_is_usable(turn: Turn, *, min_words: int, max_words: int) -> bool:
    words = turn.word_count
    if words < min_words or words > max_words:
        return False
    text = turn.text.strip()
    if not text:
        return False
    if any(marker in text for marker in CONTAMINATION_MARKERS):
        return False
    return text[-1] in ".!?'\""


def history_is_usable(history: list[Turn]) -> bool:
    for turn in history:
        if any(marker in turn.text for marker in CONTAMINATION_MARKERS):
            return False
        if turn.word_count < 3:
            return False
        if turn.word_count > 260:
            return False
    return True


def preview_text(text: str, *, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_explicit_examples(
    turns: list[Turn],
    *,
    per_source: int,
    min_words: int,
    max_words: int,
    history_turns: int,
) -> list[dict]:
    by_source: dict[str, list[Turn]] = {}
    for turn in turns:
        by_source.setdefault(turn.source, []).append(turn)

    examples: list[dict] = []
    for source_name, source_turns in by_source.items():
        source_examples: list[dict] = []
        for idx in range(history_turns, len(source_turns)):
            target = source_turns[idx]
            if target.speaker not in TARGET_SPEAKERS.get(source_name, set()):
                continue
            if not target_is_usable(target, min_words=min_words, max_words=max_words):
                continue
            history = source_turns[idx - history_turns : idx]
            if any(item.source != target.source for item in history):
                continue
            if not history_is_usable(history):
                continue

            family = model_family_for_source(source_name)
            history_text = "\n".join(
                f"{participant_for_speaker(source_name, item.speaker)} "
                f"({item.speaker}): {item.text}"
                for item in history
            )
            participant = participant_for_speaker(source_name, target.speaker)
            source_examples.append(
                {
                    "kind": "explicit_next_reply",
                    "source": SOURCE_LABELS[source_name],
                    "source_file": source_name,
                    "source_lines": [history[0].start_line, target.end_line],
                    "target_speaker": target.speaker,
                    "target_participant": participant,
                    "target_words": target.word_count,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPTS[family]},
                        {
                            "role": "user",
                            "content": (
                                f"Conversation so far:\n{history_text}\n\n"
                                f"Write {participant}'s next reply."
                            ),
                        },
                        {"role": "assistant", "content": target.text},
                    ],
                }
            )

        examples.extend(select_spread(source_examples, per_source))

    return examples


def select_spread(rows: list[dict], count: int) -> list[dict]:
    if len(rows) <= count:
        return rows
    if count <= 1:
        return [rows[0]]

    step = (len(rows) - 1) / (count - 1)
    selected = []
    used_indexes = set()
    for slot in range(count):
        idx = round(slot * step)
        if idx not in used_indexes:
            selected.append(rows[idx])
            used_indexes.add(idx)
    return selected


def block_has_dialogue_signal(text: str) -> bool:
    signals = ["\"", "'", "asked", "said", "replied", "answered", "sire", "revered"]
    lowered = text.lower()
    return sum(1 for signal in signals if signal in lowered) >= 2


def cue_block_is_usable(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False
    if any(marker in stripped for marker in CONTAMINATION_MARKERS):
        return False
    if stripped[0].islower():
        return False
    if stripped[-1] not in ".!?'\"":
        return False
    return block_has_dialogue_signal(stripped)


def build_cue_candidates(
    source_dir: Path,
    *,
    per_source: int,
    max_following_lines: int,
    min_words: int,
    max_words: int,
) -> list[dict]:
    candidates: list[dict] = []
    for source_name in CUE_SOURCES:
        path = source_dir / source_name
        if not path.exists():
            continue
        blocks = mine_speech_cue_blocks(path, max_following_lines=max_following_lines)
        filtered = [
            block
            for block in blocks
            if min_words <= block.word_count <= max_words
            and cue_block_is_usable(block.text)
        ]
        for block in select_spread(filtered, per_source):
            candidates.append(
                {
                    "kind": "speech_cue_candidate",
                    "source": SOURCE_LABELS[source_name],
                    "source_file": source_name,
                    "source_lines": [block.start_line, block.end_line],
                    "cue": block.cue,
                    "words": block.word_count,
                    "text": block.text,
                }
            )
    return candidates


def example_to_markdown(example: dict, index: int, *, preview_chars: int) -> str:
    lines = [
        f"## Example {index}: {example['source']}",
        "",
        f"- Kind: `{example['kind']}`",
        f"- Lines: `{example['source_file']}:{example['source_lines'][0]}-{example['source_lines'][1]}`",
    ]

    if example["kind"] == "explicit_next_reply":
        lines.extend(
            [
                f"- Target: `{example['target_participant']} ({example['target_speaker']})`",
                f"- Target words: `{example['target_words']}`",
                "",
                "### User Prompt",
                "",
                "```text",
                preview_text(example["messages"][1]["content"], limit=preview_chars),
                "```",
                "",
                "### Assistant Target",
                "",
                "```text",
                preview_text(example["messages"][2]["content"], limit=preview_chars),
                "```",
            ]
        )
    else:
        lines.extend(
            [
                f"- Cue: `{example['cue']}`",
                f"- Words: `{example['words']}`",
                "",
                "### Candidate Block",
                "",
                "```text",
                preview_text(example["text"], limit=preview_chars),
                "```",
            ]
        )
    return "\n".join(lines)


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate small readable dialogue extraction previews."
    )
    parser.add_argument("--source-dir", type=Path, default=SOURCE_DIR)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("review_outputs/dialogue_previews"),
        help="Directory for markdown and JSONL preview files.",
    )
    parser.add_argument("--per-source", type=int, default=5)
    parser.add_argument("--history-turns", type=int, default=3)
    parser.add_argument("--min-target-words", type=int, default=25)
    parser.add_argument("--max-target-words", type=int, default=220)
    parser.add_argument("--max-following-lines", type=int, default=18)
    parser.add_argument("--preview-chars", type=int, default=900)
    args = parser.parse_args()

    source_dir = args.source_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    explicit_turns: list[Turn] = []
    for source_name in EXPLICIT_SOURCES:
        path = source_dir / source_name
        if path.exists():
            explicit_turns.extend(parse_explicit_turns(path))

    explicit_examples = build_explicit_examples(
        explicit_turns,
        per_source=args.per_source,
        min_words=args.min_target_words,
        max_words=args.max_target_words,
        history_turns=args.history_turns,
    )
    cue_candidates = build_cue_candidates(
        source_dir,
        per_source=args.per_source,
        max_following_lines=args.max_following_lines,
        min_words=args.min_target_words,
        max_words=args.max_target_words * 2,
    )

    all_rows = explicit_examples + cue_candidates
    markdown_parts = [
        "# Dialogue Extraction Preview",
        "",
        "This is a small review sample. Explicit examples are close to training",
        "records. Speech-cue candidates still need parser review before they are",
        "trusted as training examples.",
        "",
        "## Body Line Ranges",
        "",
    ]
    for source_name, line_range in BODY_LINE_RANGES.items():
        markdown_parts.append(f"- `{source_name}`: `{line_range[0]}-{line_range[1]}`")
    markdown_parts.append("")

    for idx, row in enumerate(all_rows, 1):
        markdown_parts.append(example_to_markdown(row, idx, preview_chars=args.preview_chars))
        markdown_parts.append("")

    markdown_path = output_dir / "dialogue_candidate_preview.md"
    jsonl_path = output_dir / "dialogue_candidate_preview.jsonl"
    markdown_path.write_text("\n".join(markdown_parts), encoding="utf-8")
    write_jsonl(jsonl_path, all_rows)

    print(f"Explicit next-reply examples: {len(explicit_examples)}")
    print(f"Speech-cue candidates: {len(cue_candidates)}")
    print(f"Markdown preview: {markdown_path}")
    print(f"JSONL preview: {jsonl_path}")


if __name__ == "__main__":
    main()
