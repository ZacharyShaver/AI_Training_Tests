#!/usr/bin/env python3
"""Convert an LM Studio dual-chat transcript export into conversation-training JSONL.

Input format:
    A JSON array of objects like:
    {
      "speaker": "Participant A",
      "model_id": "hermes_sage",
      "role": "assistant",
      "content": "..."
    }

Output format:
    One JSONL line per next-turn training example:
    {
      "messages": [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "Conversation so far: ..."},
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
        "You are Participant A in a philosophical dialogue. Reason carefully, "
        "respond directly to Participant B, and keep the reply concise and natural."
    ),
    "Participant B": (
        "You are Participant B in a philosophical dialogue. Respond directly to "
        "Participant A, build on the prior point, challenge weak reasoning politely, "
        "and keep the reply concise and natural."
    ),
}


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = text.replace("\x0c", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def looks_truncated(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.endswith((",", ";", ":", "-", "—")):
        return True
    if len(stripped) < 40:
        return True
    last_char = stripped[-1]
    if last_char not in ".!?\"'”’":
        return True
    return False


def load_transcript(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Transcript JSON must be a list of messages.")
    messages = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        speaker = str(item.get("speaker", "")).strip()
        content = normalize_text(str(item.get("content", "")))
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


def build_example(history: list[dict], target: dict) -> dict:
    speaker = target["speaker"]
    partner = "Participant B" if speaker == "Participant A" else "Participant A"
    system_prompt = DEFAULT_SYSTEM_PROMPTS.get(
        speaker,
        (
            f"You are {speaker} in a dialogue. Respond directly to {partner}, "
            "stay coherent with the prior conversation, and keep the reply natural."
        ),
    )
    transcript = "\n".join(f"{msg['speaker']}: {msg['content']}" for msg in history)
    user_prompt = f"Conversation so far:\n{transcript}\n\nWrite {speaker}'s next reply."
    return {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": target["content"]},
        ]
    }


def convert_messages(
    messages: list[dict], *, drop_truncated_targets: bool = True, min_history: int = 1
) -> list[dict]:
    examples = []
    for idx in range(min_history, len(messages)):
        history = messages[:idx]
        target = messages[idx]
        if drop_truncated_targets and looks_truncated(target["content"]):
            continue
        examples.append(build_example(history, target))
    return examples


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a dual-chat transcript JSON export into training JSONL."
    )
    parser.add_argument("input", type=Path, help="Path to transcript JSON file")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Path to output JSONL file. Defaults next to input with _conversation_training suffix.",
    )
    parser.add_argument(
        "--keep-truncated",
        action="store_true",
        help="Keep target turns that appear truncated or incomplete.",
    )
    parser.add_argument(
        "--min-history",
        type=int,
        default=1,
        help="Minimum number of prior messages required before creating an example.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input
    output_path = args.output or input_path.with_name(
        f"{input_path.stem}_conversation_training.jsonl"
    )

    messages = load_transcript(input_path)
    examples = convert_messages(
        messages,
        drop_truncated_targets=not args.keep_truncated,
        min_history=max(args.min_history, 1),
    )

    with output_path.open("w", encoding="utf-8") as fh:
        for example in examples:
            fh.write(json.dumps(example, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "input_messages": len(messages),
                "output_examples": len(examples),
                "output_path": str(output_path),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
