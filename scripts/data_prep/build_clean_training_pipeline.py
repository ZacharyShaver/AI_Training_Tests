#!/usr/bin/env python3
"""Build cleaned QA and dual-model dialogue training datasets.

This pipeline:
1. Cleans QA corpora with corpus-specific confidence thresholds and heuristics.
2. Converts cleaned QA into chat/messages format.
3. Converts transcript JSON exports into combined and speaker-specific dialogue data.
4. Builds ready-to-train model_a/model_b train/valid splits with dialogue oversampling.
5. Writes a summary report with kept/dropped counts by corpus and transcript.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path
from typing import Any


CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}
DEFAULT_MIN_CONFIDENCE_BY_CORPUS = {
    "key_to_theosophy": "high",
    "corpus_hermeticum": "high",
    "asclepius": "medium",
    "milinda_panha": "high",
    "platform_sutra": "high",
}
DEFAULT_DIALOGUE_SYSTEM_PROMPTS = {
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
QA_SYSTEM_PROMPT = (
    "You are participating in a philosophical conversation. Answer directly, remain "
    "faithful to the source material provided in the prompt, and keep the response "
    "clear and natural."
)
SPEAKER_PREFIX_RE = re.compile(r"^(Participant [A-Z]|[A-Z]):\s*")
INLINE_PARTICIPANT_RE = re.compile(r"\bParticipant [A-Z]:")
INLINE_ROLE_LABEL_RE = re.compile(
    r"(?:^|\n)\s*(?:Enquirer|Theosophist|Questioner|Answerer|Participant [A-Z]):"
)
SUSPICIOUS_EDITORIAL_RE = re.compile(
    r"(?:\bTranslation\b|\bglossary\b|\btable of contents\b)", re.IGNORECASE
)


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = text.replace("\x0c", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def slug_from_filename(path: Path) -> str:
    name = path.stem
    if name.endswith("_qa"):
        return name[:-3]
    return name


def confidence_at_least(value: str, minimum: str) -> bool:
    return CONFIDENCE_RANK.get(value.lower(), -1) >= CONFIDENCE_RANK.get(
        minimum.lower(), 0
    )


def looks_truncated(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if stripped.endswith((",", ";", ":", "-", "—")):
        return True
    if len(stripped) < 8:
        return stripped[-1] not in ".!?\"'”’"
    return stripped[-1] not in ".!?\"'”’"


def contains_role_bleed(text: str) -> bool:
    return bool(INLINE_ROLE_LABEL_RE.search(text))


def looks_editorial(text: str) -> bool:
    return bool(SUSPICIOUS_EDITORIAL_RE.search(text))


def build_qa_user_prompt(record: dict[str, Any]) -> str:
    lines: list[str] = []

    source_text = record.get("source_text")
    if source_text:
        lines.append(f"Source: {source_text}")

    part = record.get("part")
    if part:
        lines.append(f"Part: {part}")

    section_num = record.get("section_num")
    section_title = record.get("section_title")
    section = record.get("section")
    if section_num and section_title:
        lines.append(f"Section {section_num}: {section_title}")
    elif section_title:
        lines.append(f"Section: {section_title}")
    elif section:
        lines.append(f"Section: {section}")

    chapter = record.get("chapter")
    if chapter:
        lines.append(f"Chapter: {chapter}")

    book = record.get("book")
    if book:
        lines.append(f"Book: {book}")

    translation = record.get("translation")
    if translation:
        lines.append(f"Translation: {translation}")

    questioner = record.get("questioner")
    if questioner:
        lines.append(f"Questioner: {questioner}")

    answerer = record.get("answerer")
    if answerer:
        lines.append(f"Answerer: {answerer}")

    lines.append("")
    lines.append(f"Question: {record['question']}")
    lines.append("")
    lines.append("Reply with the source-faithful answer only.")
    return "\n".join(lines)


def qa_record_to_messages(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "messages": [
            {"role": "system", "content": QA_SYSTEM_PROMPT},
            {"role": "user", "content": build_qa_user_prompt(record)},
            {"role": "assistant", "content": record["answer"]},
        ]
    }


def clean_qa_record(
    record: dict[str, Any], *, min_confidence: str
) -> tuple[dict[str, Any] | None, str | None]:
    cleaned = dict(record)
    cleaned["question"] = normalize_text(str(record.get("question", "")))
    cleaned["answer"] = normalize_text(str(record.get("answer", "")))
    confidence = str(record.get("confidence", "medium")).strip().lower() or "medium"
    cleaned["confidence"] = confidence

    if not cleaned["question"]:
        return None, "empty_question"
    if not cleaned["answer"]:
        return None, "empty_answer"
    if not confidence_at_least(confidence, min_confidence):
        return None, "low_confidence"
    if looks_truncated(cleaned["answer"]):
        return None, "truncated_answer"
    if contains_role_bleed(cleaned["answer"]):
        return None, "role_bleed"
    if looks_editorial(cleaned["answer"]):
        return None, "editorial_contamination"

    return cleaned, None


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def strip_leading_speaker_prefix(text: str) -> str:
    return SPEAKER_PREFIX_RE.sub("", text.strip()).strip()


def load_transcript(path: Path) -> list[dict[str, str]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"{path} must contain a JSON list.")

    rows: list[dict[str, str]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        speaker = str(item.get("speaker", "")).strip()
        content = strip_leading_speaker_prefix(
            normalize_text(str(item.get("content", "")))
        )
        if not speaker or not content:
            continue
        rows.append(
            {
                "speaker": speaker,
                "model_id": str(item.get("model_id", "")).strip(),
                "role": str(item.get("role", "")).strip(),
                "content": content,
            }
        )
    return rows


def has_participant_role_bleed(text: str, expected_speaker: str) -> bool:
    matches = list(INLINE_PARTICIPANT_RE.finditer(text))
    if not matches:
        return False
    if matches[0].start() == 0 and matches[0].group(0).startswith(expected_speaker):
        matches = matches[1:]
    return bool(matches)


def build_dialogue_example(history: list[dict[str, str]], target: dict[str, str]) -> dict:
    transcript = "\n".join(f"{row['speaker']}: {row['content']}" for row in history)
    return {
        "messages": [
            {
                "role": "system",
                "content": DEFAULT_DIALOGUE_SYSTEM_PROMPTS.get(
                    target["speaker"],
                    "You are participating in a dialogue. Stay coherent with the "
                    "prior conversation and reply naturally.",
                ),
            },
            {
                "role": "user",
                "content": f"Conversation so far:\n{transcript}\n\nWrite {target['speaker']}'s next reply.",
            },
            {"role": "assistant", "content": target["content"]},
        ]
    }


def convert_transcript(
    messages: list[dict[str, str]], *, min_history: int
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

        if looks_truncated(content):
            stats["skipped_truncated"] += 1
            continue
        if has_participant_role_bleed(content, target["speaker"]):
            stats["skipped_role_bleed"] += 1
            continue

        row = build_dialogue_example(history, target)
        combined.append(row)
        by_speaker.setdefault(target["speaker"], []).append(row)

    stats["combined_examples"] = len(combined)
    for speaker, rows in by_speaker.items():
        stats[f"{speaker.lower().replace(' ', '_')}_examples"] = len(rows)
    return combined, by_speaker, stats


def split_rows(
    rows: list[dict[str, Any]], *, valid_ratio: float, seed: int
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not rows:
        return [], []

    shuffled = rows[:]
    random.Random(seed).shuffle(shuffled)

    valid_count = int(len(shuffled) * valid_ratio)
    if valid_ratio > 0 and valid_count == 0 and len(shuffled) > 1:
        valid_count = 1
    if valid_count >= len(shuffled):
        valid_count = max(1, len(shuffled) - 1)

    return shuffled[valid_count:], shuffled[:valid_count]


def repeat_rows(rows: list[dict[str, Any]], times: int) -> list[dict[str, Any]]:
    if times <= 1:
        return rows[:]
    repeated: list[dict[str, Any]] = []
    for _ in range(times):
        repeated.extend(rows)
    return repeated


def find_qa_inputs(training_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in training_dir.glob("*_qa.jsonl")
        if not path.name.endswith("_alpaca.jsonl")
    )


def find_transcripts(training_dir: Path) -> list[Path]:
    return sorted((training_dir / "Test Conversations").glob("*.json"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build cleaned QA and dual-model dialogue datasets."
    )
    parser.add_argument(
        "--training-dir",
        type=Path,
        default=Path("Training Data"),
        help="Directory containing source QA files and Test Conversations.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("Training Data/cleaned_pipeline"),
        help="Directory where cleaned outputs will be written.",
    )
    parser.add_argument(
        "--valid-ratio",
        type=float,
        default=0.1,
        help="Fraction of examples to place in valid splits.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for train/valid splitting.",
    )
    parser.add_argument(
        "--dialogue-weight",
        type=int,
        default=8,
        help="How many times to repeat dialogue examples in model-specific train splits.",
    )
    parser.add_argument(
        "--min-history",
        type=int,
        default=1,
        help="Minimum prior messages required before creating a dialogue example.",
    )
    args = parser.parse_args()

    if not 0 <= args.valid_ratio < 1:
        raise SystemExit("--valid-ratio must be in the range [0, 1).")
    if args.dialogue_weight < 1:
        raise SystemExit("--dialogue-weight must be at least 1.")

    training_dir = args.training_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    cleaned_qa_dir = output_dir / "cleaned_qa"
    dialogue_dir = output_dir / "cleaned_dialogue"
    model_a_dir = output_dir / "model_a"
    model_b_dir = output_dir / "model_b"
    for path in (cleaned_qa_dir, dialogue_dir, model_a_dir, model_b_dir):
        path.mkdir(parents=True, exist_ok=True)

    summary: dict[str, Any] = {
        "training_dir": str(training_dir),
        "output_dir": str(output_dir),
        "dialogue_weight": args.dialogue_weight,
        "valid_ratio": args.valid_ratio,
        "seed": args.seed,
        "qa": {},
        "dialogue": {},
    }

    combined_qa_records: list[dict[str, Any]] = []
    combined_qa_messages: list[dict[str, Any]] = []

    for path in find_qa_inputs(training_dir):
        slug = slug_from_filename(path)
        min_confidence = DEFAULT_MIN_CONFIDENCE_BY_CORPUS.get(slug, "medium")
        records = load_jsonl(path)
        cleaned_rows: list[dict[str, Any]] = []
        dropped: dict[str, int] = {}

        for record in records:
            cleaned, reason = clean_qa_record(record, min_confidence=min_confidence)
            if cleaned is None:
                dropped[reason or "unknown"] = dropped.get(reason or "unknown", 0) + 1
                continue
            cleaned_rows.append(cleaned)

        qa_messages = [qa_record_to_messages(row) for row in cleaned_rows]
        combined_qa_records.extend(cleaned_rows)
        combined_qa_messages.extend(qa_messages)

        write_jsonl(cleaned_qa_dir / f"{slug}_cleaned.jsonl", cleaned_rows)
        write_jsonl(cleaned_qa_dir / f"{slug}_messages.jsonl", qa_messages)

        summary["qa"][slug] = {
            "input_records": len(records),
            "kept_records": len(cleaned_rows),
            "dropped_records": len(records) - len(cleaned_rows),
            "min_confidence": min_confidence,
            "drop_reasons": dropped,
        }

    write_jsonl(cleaned_qa_dir / "combined_cleaned.jsonl", combined_qa_records)
    write_jsonl(cleaned_qa_dir / "combined_messages.jsonl", combined_qa_messages)

    combined_dialogue: list[dict[str, Any]] = []
    dialogue_a: list[dict[str, Any]] = []
    dialogue_b: list[dict[str, Any]] = []

    for path in find_transcripts(training_dir):
        messages = load_transcript(path)
        combined_rows, by_speaker, stats = convert_transcript(
            messages, min_history=args.min_history
        )
        combined_dialogue.extend(combined_rows)
        dialogue_a.extend(by_speaker.get("Participant A", []))
        dialogue_b.extend(by_speaker.get("Participant B", []))
        summary["dialogue"][path.name] = stats

    write_jsonl(dialogue_dir / "combined_messages.jsonl", combined_dialogue)
    write_jsonl(dialogue_dir / "participant_a_messages.jsonl", dialogue_a)
    write_jsonl(dialogue_dir / "participant_b_messages.jsonl", dialogue_b)

    qa_train, qa_valid = split_rows(
        combined_qa_messages, valid_ratio=args.valid_ratio, seed=args.seed
    )
    dialogue_a_train, dialogue_a_valid = split_rows(
        dialogue_a, valid_ratio=args.valid_ratio, seed=args.seed + 1
    )
    dialogue_b_train, dialogue_b_valid = split_rows(
        dialogue_b, valid_ratio=args.valid_ratio, seed=args.seed + 2
    )

    model_a_train = qa_train + repeat_rows(dialogue_a_train, args.dialogue_weight)
    model_a_valid = qa_valid + dialogue_a_valid
    model_b_train = qa_train + repeat_rows(dialogue_b_train, args.dialogue_weight)
    model_b_valid = qa_valid + dialogue_b_valid

    write_jsonl(model_a_dir / "train.jsonl", model_a_train)
    write_jsonl(model_a_dir / "valid.jsonl", model_a_valid)
    write_jsonl(model_b_dir / "train.jsonl", model_b_train)
    write_jsonl(model_b_dir / "valid.jsonl", model_b_valid)

    summary["merged"] = {
        "qa_messages": len(combined_qa_messages),
        "dialogue_messages": len(combined_dialogue),
        "participant_a_messages": len(dialogue_a),
        "participant_b_messages": len(dialogue_b),
        "model_a_train": len(model_a_train),
        "model_a_valid": len(model_a_valid),
        "model_b_train": len(model_b_train),
        "model_b_valid": len(model_b_valid),
    }
    summary["output_files"] = {
        "qa_messages": str(cleaned_qa_dir / "combined_messages.jsonl"),
        "dialogue_a": str(dialogue_dir / "participant_a_messages.jsonl"),
        "dialogue_b": str(dialogue_dir / "participant_b_messages.jsonl"),
        "model_a_train": str(model_a_dir / "train.jsonl"),
        "model_b_train": str(model_b_dir / "train.jsonl"),
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
