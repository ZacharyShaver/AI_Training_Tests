#!/usr/bin/env python3

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "oritiginal text" / "Milinda Panha.txt"
OUTPUT_DIR = REPO_ROOT / "Training Data"
OUT_JSONL = OUTPUT_DIR / "milinda_panha_qa.jsonl"
OUT_STRICT_JSONL = OUTPUT_DIR / "milinda_panha_qa_high_confidence.jsonl"
OUT_NOTES = OUTPUT_DIR / "milinda_panha_extraction_notes.md"


PART_ONLY_RE = re.compile(r"^PART\s+(?P<num>[IVX]+)$")
SECTION_RE = re.compile(r"^(?P<num>\d+)\.\s+(?P<title>.+?)\s+\((?P<ref>[^)]+)\)$")
START_RE = re.compile(r"^PART I$")
END_RE = re.compile(r"^INDEX\b")

SPEAKER_PATTERNS = [
    (re.compile(r"\b(King Milinda)\s+(?:then\s+)?(?:said|asked|spoke thus|addressed [^:]+|told [^:]+):"), "King Milinda"),
    (re.compile(r"\b(Venerable Nāgasena)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Venerable Nāgasena"),
    (re.compile(r"\b(Venerable Rohaṇa)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Venerable Rohaṇa"),
    (re.compile(r"\b(Venerable Assagutta)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Venerable Assagutta"),
    (re.compile(r"\b(Venerable Āyupāla)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Venerable Āyupāla"),
    (re.compile(r"\b(Venerable Dhammarakkhita)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Venerable Dhammarakkhita"),
    (re.compile(r"\b(Devamantiya)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Devamantiya"),
    (re.compile(r"\b(Soṇuttara)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Soṇuttara"),
    (re.compile(r"\b(Mahāsena)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "Mahāsena"),
    (re.compile(r"\b(The Bactrians)\s+(?:then\s+)?(?:said|asked|replied|spoke thus|told [^:]+):"), "The Bactrians"),
]


def normalize_line(line: str) -> str:
    line = line.replace("\ufeff", "")
    line = line.replace("\x0c", "")
    line = line.replace("“", '"')
    line = line.replace("”", '"')
    line = line.replace("’", "'")
    line = line.replace("‘", "'")
    line = line.replace("—", "-")
    line = line.replace("–", "-")
    return re.sub(r"\s+", " ", line.strip())


def extract_explicit_speaker(line: str):
    for pattern, speaker in SPEAKER_PATTERNS:
        if pattern.search(line):
            return speaker
    return None


def infer_qa_speaker(content: str, previous_turn_speaker: str | None):
    text = content.strip()
    lower = text.lower()

    king_markers = [
        "revered nāgasena",
        "revered sir",
        "you are dexterous, revered nāgasena",
        "it is wonderful, revered nāgasena",
        "it is good, revered nāgasena",
    ]
    if any(lower.startswith(marker) for marker in king_markers):
        return "King Milinda", "qa_heuristic"
    if lower.startswith("i, revered sir"):
        return "King Milinda", "qa_heuristic"
    if "revered nāgasena" in lower and "sire" not in lower[:20]:
        return "King Milinda", "qa_heuristic"

    nagasena_markers = [
        "sire,",
        "no, sire",
        "yes, sire",
        "it is good, sire",
        "even so, sire",
        "ask it, sire",
        "that has been answered, sire",
        "but what was asked by you, sire",
        "why, sire",
    ]
    if any(lower.startswith(marker) for marker in nagasena_markers):
        return "Venerable Nāgasena", "qa_heuristic"
    if re.search(r"\bsire[?.!]?$", lower):
        return "Venerable Nāgasena", "qa_heuristic"

    if previous_turn_speaker == "King Milinda":
        return "Venerable Nāgasena", "qa_alternation"
    if previous_turn_speaker == "Venerable Nāgasena":
        return "King Milinda", "qa_alternation"
    return None, "unknown"


def clean_content(text: str) -> str:
    text = re.sub(r"\b\d+\s+The Questions of King Milinda\b", "", text)
    text = re.sub(r"\bQuestions on Distinguishing Marks\s+\d+\b", "", text)
    text = re.sub(r"\bPast History\s+\d+\b", "", text)
    text = re.sub(r"\bThe Dilemmas\s+\d+\b", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_turns():
    lines = SOURCE.read_text(encoding="utf-8", errors="ignore").splitlines()
    in_body = False
    part = None
    awaiting_part_title = False
    section_num = None
    section_title = None
    turns = []
    pending_speaker = None
    previous_turn_speaker = None
    current_qa_mode = False
    turns_in_section = 0
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = normalize_line(raw)
        lineno = i + 1

        if not line:
            i += 1
            continue

        if not in_body:
            if START_RE.match(line):
                in_body = True
                part = "PART I: Past History"
                awaiting_part_title = True
            i += 1
            continue

        if END_RE.match(line):
            break

        part_match = PART_ONLY_RE.match(line)
        if part_match:
            roman = part_match.group("num")
            part = f"PART {roman}"
            awaiting_part_title = True
            i += 1
            continue

        if awaiting_part_title and not SECTION_RE.match(line):
            if line.isupper() or re.match(r"^[A-Z][A-Za-z .'\-]+$", line):
                if ":" in part:
                    part = f"{part.split(':')[0]}: {line}"
                else:
                    part = f"{part}: {line}"
                awaiting_part_title = False
                i += 1
                continue

        section_match = SECTION_RE.match(line)
        if section_match:
            section_num = section_match.group("num")
            section_title = section_match.group("title")
            current_qa_mode = False
            pending_speaker = None
            awaiting_part_title = False
            turns_in_section = 0
            i += 1
            continue

        explicit_speaker = extract_explicit_speaker(line)
        if explicit_speaker:
            pending_speaker = explicit_speaker
            if explicit_speaker in {"King Milinda", "Venerable Nāgasena"} and section_num is not None:
                current_qa_mode = True

        quote_start = line.find('"')
        if quote_start == -1:
            i += 1
            continue

        before_quote = line[:quote_start]
        explicit_before_quote = extract_explicit_speaker(before_quote)
        if explicit_before_quote:
            pending_speaker = explicit_before_quote

        content_parts = [line[quote_start + 1 :]]
        j = i
        while True:
            current = content_parts[-1]
            if '"' in current:
                idx = current.find('"')
                content_parts[-1] = current[:idx]
                break
            j += 1
            if j >= len(lines):
                break
            next_line = normalize_line(lines[j])
            if not next_line:
                continue
            if re.match(r"^\d+\.\s", next_line):
                j += 1
                continue
            if "The Questions of King Milinda" in next_line:
                j += 1
                continue
            if re.match(r"^[A-Z][A-Za-z ]+\s+\d+$", next_line):
                j += 1
                continue
            content_parts.append(next_line)

        content = " ".join(part for part in content_parts if part).strip()
        content = re.sub(r"\s+", " ", content).strip()
        content = clean_content(content)
        if not content:
            i = max(j + 1, i + 1)
            continue

        speaker = pending_speaker
        speaker_source = "explicit" if speaker else "inferred"

        if current_qa_mode:
            inferred_speaker, inferred_source = infer_qa_speaker(content, previous_turn_speaker)
            if inferred_speaker:
                speaker = inferred_speaker
                speaker_source = inferred_source
            elif turns_in_section == 0:
                if "?" in content:
                    speaker = "King Milinda"
                    speaker_source = "section_default"
                else:
                    speaker = "Venerable Nāgasena"
                    speaker_source = "section_default"
            elif not speaker and previous_turn_speaker in {"King Milinda", "Venerable Nāgasena"}:
                speaker = "Venerable Nāgasena" if previous_turn_speaker == "King Milinda" else "King Milinda"
                speaker_source = "qa_alternation"

        if not speaker:
            speaker = "Unknown"
            speaker_source = "unknown"

        turns.append(
            {
                "part": part,
                "section_num": section_num,
                "section_title": section_title,
                "speaker": speaker,
                "speaker_source": speaker_source,
                "text": content,
                "line": lineno,
            }
        )

        previous_turn_speaker = speaker if speaker != "Unknown" else previous_turn_speaker
        turns_in_section += 1

        pending_speaker = None

        i = max(j + 1, i + 1)

    return turns


def build_records(turns):
    records = []
    for idx in range(len(turns) - 1):
        turn = turns[idx]
        nxt = turns[idx + 1]

        if turn["section_num"] != nxt["section_num"]:
            continue
        if turn["speaker"] == nxt["speaker"]:
            continue
        if turn["speaker"] == "Unknown" or nxt["speaker"] == "Unknown":
            continue
        if "?" not in turn["text"]:
            continue

        confidence = "high"
        if "unknown" in {turn["speaker_source"], nxt["speaker_source"]}:
            continue
        if "qa_alternation" in {turn["speaker_source"], nxt["speaker_source"]}:
            confidence = "medium"

        records.append(
            {
                "id": f"mil-{len(records)+1:04d}",
                "source_text": "Milinda Panha",
                "part": turn["part"],
                "section_num": turn["section_num"],
                "section_title": turn["section_title"],
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

    strict_records = [record for record in records if record["confidence"] == "high"]
    with OUT_STRICT_JSONL.open("w", encoding="utf-8") as fh:
        for record in strict_records:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

    part_counts = {}
    section_counts = {}
    for record in records:
        part_counts[record["part"]] = part_counts.get(record["part"], 0) + 1
        key = f'{record["section_num"]}. {record["section_title"]}'
        section_counts[key] = section_counts.get(key, 0) + 1

    part_summary = "\n".join(
        f"- `{part}`: {count} pairs"
        for part, count in sorted(part_counts.items(), key=lambda item: item[0])
    )
    section_summary = "\n".join(
        f"- `{section}`: {count} pairs"
        for section, count in sorted(section_counts.items(), key=lambda item: (-item[1], item[0]))[:20]
    )

    notes = f"""# Milinda Panha Q&A Extraction

This dataset was extracted from [Milinda Panha.txt](/Users/wewlad/GitHub/AI_Training_Tests/Milinda%20Panha.txt) into [milinda_panha_qa.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/milinda_panha_qa.jsonl).
The stricter subset is available at [milinda_panha_qa_high_confidence.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/milinda_panha_qa_high_confidence.jsonl).

## What was extracted

- Extraction starts at `PART I: PAST HISTORY` and stops before the index.
- Dialogue turns were parsed from quoted speech blocks.
- Speakers were taken from explicit narration where possible, such as `King Milinda said` and `Venerable Nāgasena replied`.
- In the question sections, local Milinda-Nagasena alternation was used only when the surrounding context clearly stayed inside that exchange.

## Caveats

- High-confidence pairs use explicit speaker attribution on both sides.
- Medium-confidence pairs use one or more local alternation inferences inside a clearly established section dialogue.
- The file is an abridged edition with editorial front matter and notes, so only the main body was parsed.
- Some longer answers contain nested rhetorical questions; those were kept as part of the answer text rather than split further.

## Pair counts

- Total pairs: `{len(records)}`
- High-confidence pairs: `{len(strict_records)}`

## Part counts

{part_summary}

## Most dialogue-heavy sections

{section_summary}
"""

    OUT_NOTES.write_text(notes, encoding="utf-8")


def main():
    turns = parse_turns()
    records = build_records(turns)
    write_outputs(records)
    print(json.dumps({"turns": len(turns), "qa_pairs": len(records), "high_confidence": len([r for r in records if r["confidence"] == "high"])}))


if __name__ == "__main__":
    main()
