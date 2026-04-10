#!/usr/bin/env python3

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "oritiginal text" / "Asclepius.txt"
OUTPUT_DIR = REPO_ROOT / "Training Data"
OUT_JSONL = OUTPUT_DIR / "asclepius_qa.jsonl"
OUT_STRICT_JSONL = OUTPUT_DIR / "asclepius_qa_high_confidence.jsonl"
OUT_NOTES = OUTPUT_DIR / "asclepius_extraction_notes.md"


VALID_SPEAKERS = {"Hermes", "Asclepius", "Tat", "Hammon"}
TRANSLATION_START_RE = re.compile(r"^Translation$")
SECTION_RE = re.compile(r"^\[(\d+)\]")
QUOTE_START_RE = re.compile(r"^[‘'](.*)")


def normalize_line(line: str) -> str:
    line = line.replace("\ufeff", "")
    line = line.replace("\x0c", "")
    line = line.replace("’", "'")
    line = line.replace("‘", "'")
    line = line.replace("“", '"')
    line = line.replace("”", '"')
    line = line.replace("—", "-")
    line = line.replace("–", "-")
    line = line.replace("\u0002", " ")
    return re.sub(r"\s+", " ", line.strip())


def infer_speaker(text: str, previous_speaker: str | None, pending_hint: str | None):
    lower = text.lower()

    if pending_hint in VALID_SPEAKERS:
        return pending_hint, 0.95

    if "o trismegistus" in lower:
        if "asclepius" in lower:
            return "Asclepius", 0.9
        return "Asclepius", 0.75

    if "o asclepius" in lower:
        return "Hermes", 0.9

    if "o tat" in lower:
        return "Hermes", 0.9

    if "o hammon" in lower:
        return "Hermes", 0.9

    if previous_speaker == "Hermes":
        return "Asclepius", 0.45
    if previous_speaker == "Asclepius":
        return "Hermes", 0.45
    if previous_speaker == "Tat":
        return "Hermes", 0.45
    if previous_speaker == "Hammon":
        return "Hermes", 0.45

    return "Hermes", 0.25


def parse_dialogue():
    text_lines = SOURCE.read_text(encoding="utf-8", errors="ignore").splitlines()
    in_translation = False
    current_section = None
    current_book = "Asclepius"
    turns = []
    previous_speaker = None
    pending_hint = None
    pending_expected_reply = None
    i = 0

    while i < len(text_lines):
        lineno = i + 1
        line = normalize_line(text_lines[i])
        if not line:
            i += 1
            continue

        if not in_translation:
            if TRANSLATION_START_RE.match(line):
                in_translation = True
            i += 1
            continue

        if line.startswith("Bibliography") or line.startswith("Index"):
            break

        section_match = SECTION_RE.match(line)
        if section_match:
            current_section = section_match.group(1)
            line = SECTION_RE.sub("", line, count=1).strip()
            if not line:
                i += 1
                continue

        hint_match = re.search(r"(Trismegistus|Asclepius|Tat|Hammon) said", line)
        if hint_match:
            name = hint_match.group(1)
            pending_hint = "Hermes" if name == "Trismegistus" else name

        entry_match = QUOTE_START_RE.match(line)
        if not entry_match:
            i += 1
            continue

        block_lines = [entry_match.group(1).strip()]
        j = i + 1
        while j < len(text_lines):
            next_line = normalize_line(text_lines[j])
            if not next_line:
                j += 1
                continue
            if next_line.startswith("Bibliography") or next_line.startswith("Index"):
                break
            if SECTION_RE.match(next_line):
                break
            if QUOTE_START_RE.match(next_line):
                break
            if next_line == "Asclepius" or next_line.isdigit():
                j += 1
                continue
            if next_line.startswith("* See Translator's Note"):
                j += 1
                continue
            if re.match(r"^[A-Z][A-Za-z .'-]+:$", next_line):
                break
            block_lines.append(next_line)
            j += 1

        content = " ".join(block_lines).strip().rstrip("'").strip()
        if not content:
            i = j
            continue

        hint = pending_hint or pending_expected_reply
        speaker, speaker_conf = infer_speaker(content, previous_speaker, hint)
        turns.append(
            {
                "book": current_book,
                "section": current_section,
                "speaker": speaker,
                "speaker_confidence": speaker_conf,
                "text": content,
                "line": lineno,
            }
        )
        previous_speaker = speaker
        pending_hint = None
        pending_expected_reply = None

        if "?" in content:
            lower = content.lower()
            if "o trismegistus" in lower:
                pending_expected_reply = "Hermes"
            elif "o asclepius" in lower:
                pending_expected_reply = "Asclepius"
            elif "o tat" in lower:
                pending_expected_reply = "Tat"
            elif "o hammon" in lower:
                pending_expected_reply = "Hammon"

        i = j

    return turns


def build_records(turns):
    records = []
    for idx in range(len(turns) - 1):
        turn = turns[idx]
        nxt = turns[idx + 1]
        if turn["section"] != nxt["section"]:
            continue
        if turn["speaker"] == nxt["speaker"]:
            continue
        if "?" not in turn["text"]:
            continue

        confidence = "high"
        if turn["speaker_confidence"] < 0.8 or nxt["speaker_confidence"] < 0.8:
            confidence = "medium"

        records.append(
            {
                "id": f"asc-{len(records)+1:04d}",
                "source_text": "Asclepius",
                "book": turn["book"],
                "section": turn["section"],
                "questioner": turn["speaker"],
                "answerer": nxt["speaker"],
                "question": turn["text"],
                "answer": nxt["text"],
                "source_lines": [turn["line"], nxt["line"]],
                "confidence": confidence,
            }
        )
    return records


def write_outputs(records):
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

    strict_records = [r for r in records if r["confidence"] == "high"]
    with OUT_STRICT_JSONL.open("w", encoding="utf-8") as fh:
        for record in strict_records:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

    section_counts = {}
    for record in records:
        key = record["section"] or "unknown"
        section_counts[key] = section_counts.get(key, 0) + 1

    section_summary = "\n".join(
        f"- Section `{section}`: {count} pairs"
        for section, count in sorted(section_counts.items(), key=lambda item: (int(item[0]) if item[0].isdigit() else 9999, item[0]))
    )

    notes = f"""# Asclepius Q&A Extraction

This dataset was extracted from [Asclepius.txt](/Users/wewlad/GitHub/AI_Training_Tests/Asclepius.txt) into [asclepius_qa.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/asclepius_qa.jsonl).
The stricter subset is available at [asclepius_qa_high_confidence.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/asclepius_qa_high_confidence.jsonl).

## What was extracted

- Only the translation section was parsed; introduction, notes, bibliography, and index were excluded.
- Dialogue turns were extracted from quoted speech.
- Speakers were inferred conservatively from local cues such as `O Trismegistus`, `O Asclepius`, and nearby narration like `Trismegistus said`.
- Each record contains `section`, `questioner`, `answerer`, `question`, `answer`, `source_lines`, and a heuristic `confidence`.

## Caveats

- This text uses fewer explicit speaker labels than the Corpus file, so speaker attribution is partly inferred.
- High-confidence pairs are those where both speaker assignments came from strong local cues.
- Medium-confidence pairs are still plausible, but they rely more on alternation and discourse context.
- Narrative exposition between exchanges was not converted into synthetic Q&A.

## Pair counts

- Total pairs: `{len(records)}`
- High-confidence pairs: `{len(strict_records)}`

## Section counts

{section_summary}
"""

    OUT_NOTES.write_text(notes, encoding="utf-8")


def main():
    turns = parse_dialogue()
    records = build_records(turns)
    write_outputs(records)
    print(json.dumps({"turns": len(turns), "qa_pairs": len(records), "high_confidence": sum(r["confidence"] == "high" for r in records)}))


if __name__ == "__main__":
    main()
