#!/usr/bin/env python3
"""Build clean speaker-specific chat training datasets from a transcript JSON export.

Input format:
    A JSON array of message objects like:
    {
      "speaker": "Participant A",
      "model_id": "hermes_sage",
      "role": "assistant",
      "content": "..."
    }

Outputs:
    - combined JSONL with next-turn examples for all speakers
    - participant_a JSONL with only Participant A targets
    - participant_b JSONL with only Participant B targets

Each JSONL record uses chat/messages format:
    {
      "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "Conversation so far:\n..."},
        {"role": "assistant", "content": "..."}
      ]
    }
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DEFAULT_SYSTEM_PROMPTS = {
    "Participant A": (
        "You are Participant A in a philosophical dialogue. Respond directly to "
        "Participant B, stay coherent with the prior discussion, and keep the reply "
        "natural and concise."
    ),
    "Participant B": (
        "You are Participant B in a philosophical dialogue. Respond directly to "
        "Participant A, challenge weak reasoning politely, and keep the reply natural "
        "and concise."
    ),
}

SPEAKER_PREFIX_RE = re.compile(r"^(Participant [A-Z]|[A-Z]):\s*")
INLINE_SPEAKER_RE = re.compile(r"\bParticipant [A-Z]:")


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = text.replace("\x0c", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def strip_leading_speaker_prefix(text: str) -> str:
    return SPEAKER_PREFIX_RE.sub("", text.strip()).strip()


def looks_truncated(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.endswith((",", ";", ":", "-", "—")):
        return True
    if len(stripped) < 40:
        return True
    return stripped[-1] not in ".!?\"'”’"


def has_role_bleed(text: str, expected_speaker: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    matches = list(INLINE_SPEAKER_RE.finditer(stripped))
    if not matches:
        return False

    # A leading self-label is usually formatting noise; inline labels are bleed.
    if matches[0].start() == 0 and matches[0].group(0).startswith(expected_speaker):
        matches = matches[1:]

    return bool(matches)


def load_transcript(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Transcript JSON must be a list of messages.")

    messages = []
    for item in payload:
        if not isinstance(item, dict):
            continue

        speaker = str(item.get("speaker", "")).strip()
        content = strip_leading_speaker_prefix(
            normalize_text(str(item.get("content", "")))
        )
        if not speaker or not content:
            continue

        messages.append(
            {
                "speaker": speaker,
                "model_id": str(item.get("model_id", "")).strip(),
                "role": str(item.get("role", "")).strip(),
                "content": content,
            }
        )

    return messages


def build_system_prompt(speaker: str) -> str:
    if speaker in DEFAULT_SYSTEM_PROMPTS:
        return DEFAULT_SYSTEM_PROMPTS[speaker]

    partner = "the other participant"
    return (
        f"You are {speaker} in a dialogue. Respond directly to {partner}, remain "
        "consistent with the prior conversation, and keep the reply natural and concise."
    )


def build_example(history: list[dict], target: dict) -> dict:
    speaker = target["speaker"]
    transcript = "\n".join(f"{msg['speaker']}: {msg['content']}" for msg in history)
    user_prompt = f"Conversation so far:\n{transcript}\n\nWrite {speaker}'s next reply."
    return {
        "messages": [
            {"role": "system", "content": build_system_prompt(speaker)},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": target["content"]},
        ]
    }


def convert_messages(
    messages: list[dict],
    *,
    min_history: int,
    drop_truncated_targets: bool,
    drop_role_bleed_targets: bool,
) -> tuple[list[dict], dict[str, list[dict]], dict[str, int]]:
    combined: list[dict] = []
    by_speaker: dict[str, list[dict]] = {}
    stats = {
        "input_messages": len(messages),
        "combined_examples": 0,
        "skipped_truncated": 0,
        "skipped_role_bleed": 0,
    }

    for idx in range(max(min_history, 1), len(messages)):
        history = messages[:idx]
        target = messages[idx]
        content = target["content"]

        if drop_truncated_targets and looks_truncated(content):
            stats["skipped_truncated"] += 1
            continue
        if drop_role_bleed_targets and has_role_bleed(content, target["speaker"]):
            stats["skipped_role_bleed"] += 1
            continue

        example = build_example(history, target)
        combined.append(example)
        by_speaker.setdefault(target["speaker"], []).append(example)

    stats["combined_examples"] = len(combined)
    for speaker, rows in by_speaker.items():
        stats[f"{speaker.lower().replace(' ', '_')}_examples"] = len(rows)

    return combined, by_speaker, stats


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create clean combined and speaker-specific chat datasets from a transcript."
    )
    parser.add_argument("input", type=Path, help="Path to transcript JSON file")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory for JSONL outputs. Defaults to the input file's directory.",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Filename prefix for outputs. Defaults to the input filename stem.",
    )
    parser.add_argument(
        "--min-history",
        type=int,
        default=1,
        help="Minimum number of prior messages required before creating an example.",
    )
    parser.add_argument(
        "--keep-truncated",
        action="store_true",
        help="Keep targets that appear truncated or incomplete.",
    )
    parser.add_argument(
        "--keep-role-bleed",
        action="store_true",
        help="Keep targets that appear to contain another speaker label inline.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir
        else input_path.parent.resolve()
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    prefix = args.prefix or input_path.stem
    messages = load_transcript(input_path)
    combined, by_speaker, stats = convert_messages(
        messages,
        min_history=args.min_history,
        drop_truncated_targets=not args.keep_truncated,
        drop_role_bleed_targets=not args.keep_role_bleed,
    )

    combined_path = output_dir / f"{prefix}_combined.jsonl"
    write_jsonl(combined_path, combined)

    output_paths = {"combined_path": str(combined_path)}
    for speaker, rows in by_speaker.items():
        slug = speaker.lower().replace(" ", "_")
        speaker_path = output_dir / f"{prefix}_{slug}.jsonl"
        write_jsonl(speaker_path, rows)
        output_paths[f"{slug}_path"] = str(speaker_path)

    print(json.dumps(stats | output_paths, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
