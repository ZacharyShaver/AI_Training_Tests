#!/usr/bin/env python3

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "The Corpus Hermeticum" / "The Corpus Hermeticum.txt"
OUTPUT_DIR = REPO_ROOT / "Training Data"
OUT_JSONL = OUTPUT_DIR / "corpus_hermeticum_qa.jsonl"
OUT_STRICT_JSONL = OUTPUT_DIR / "corpus_hermeticum_qa_high_confidence.jsonl"
OUT_NOTES = OUTPUT_DIR / "corpus_hermeticum_extraction_notes.md"
VALID_SPEAKERS = {"Hermes", "Asclepius", "Tat", "Mind", "Poemandres"}


ROMAN_BOOK_RE = re.compile(r"^(?P<title>[IVXLCDM]+\.\s+.+)$")
NAMED_BOOK_RE = re.compile(r"^The\s+[A-Za-z]+\s+Book\.\s+.+")
SPEAKER_RE = re.compile(
    r"^(?:(?P<num>\d+)\.\s+)?(?P<speaker>\[?[A-Za-z][A-Za-z .'\-\[\]]*[A-Za-z\]])(?::|\.)\s+(?P<text>.+)$"
)

SKIP_PATTERNS = [
    re.compile(r"^\s*$"),
    re.compile(r"^The Corpus Hermeticum\s*$"),
    re.compile(r"^The Corpus Hermetica\s*$"),
    re.compile(r"^translated by "),
    re.compile(r"^Table of Contents$"),
    re.compile(r"^http://"),
    re.compile(r"^[ivxlcdm]+\s*$", re.IGNORECASE),
    re.compile(r"^\d+\s*$"),
    re.compile(r"^[•*]\s"),
]


def normalize_line(line: str) -> str:
    line = line.replace("\ufeff", "")
    line = line.replace("\x0c", "")
    line = line.replace("−", "-")
    line = line.replace("—", "-")
    line = re.sub(r"\s+", " ", line.strip())
    return line


def canonical_speaker(raw: str) -> str:
    cleaned = raw.strip("[] ").rstrip(".").strip()
    key = cleaned.lower()
    aliases = {
        "h": "Hermes",
        "hermes": "Hermes",
        "trismegistus": "Hermes",
        "a": "Asclepius",
        "asclepius": "Asclepius",
        "tat": "Tat",
        "mind": "Mind",
        "pimander": "Poemandres",
        "poemandres": "Poemandres",
    }
    return aliases.get(key, cleaned)


def clean_book_title(line: str) -> str:
    line = re.sub(r"\s+\d+\s*$", "", line).strip()
    return line.rstrip(".") if line.startswith("The ") else line


def is_skip_line(line: str) -> bool:
    if any(pattern.match(line) for pattern in SKIP_PATTERNS):
        return True
    if "copyright" in line.lower():
        return True
    if re.match(r"^The (First|Second|Third|Fourth|Fifth|Sixth|Seventh|Eighth|Ninth|Tenth|Eleventh|Twelfth|Thirteenth|Fourteenth|Fifteenth|Sixteenth|Seventeenth) Book", line):
        return False
    if re.match(r"^[IVXLCDM]+\.\s", line):
        return False
    if re.match(r"^[A-Z][A-Za-z ]+\.$", line):
        return False
    if re.search(r"\.{5,}", line):
        return True
    if re.search(r"\bTo Hi$", line):
        return True
    return False


def load_dialogue_turns():
    turns = []
    current_book = None
    current_translation = "mead"
    pending = None

    for lineno, raw in enumerate(SOURCE.read_text(encoding="utf-8", errors="ignore").splitlines(), start=1):
        line = normalize_line(raw)
        if not line or is_skip_line(line):
            continue

        if ROMAN_BOOK_RE.match(line):
            current_book = clean_book_title(line)
            current_translation = "mead"
            pending = None
            continue

        if NAMED_BOOK_RE.match(line):
            current_book = clean_book_title(line)
            current_translation = "everard"
            pending = None
            continue

        speaker_match = SPEAKER_RE.match(line)
        if speaker_match:
            speaker = canonical_speaker(speaker_match.group("speaker"))
            if speaker not in VALID_SPEAKERS:
                if pending:
                    pending["text_parts"].append(line)
                    pending["end_line"] = lineno
                continue
            text = speaker_match.group("text").strip()

            if pending:
                turns.append(pending)

            pending = {
                "book": current_book,
                "translation": current_translation,
                "speaker": speaker,
                "text_parts": [text],
                "start_line": lineno,
                "end_line": lineno,
            }
            continue

        if pending:
            pending["text_parts"].append(line)
            pending["end_line"] = lineno

    if pending:
        turns.append(pending)

    for turn in turns:
        turn["text"] = " ".join(turn.pop("text_parts"))
        turn["text"] = re.sub(r"\s+", " ", turn["text"]).strip()

    return turns


def build_qa_records(turns):
    records = []
    question_words = (
        "what",
        "why",
        "how",
        "who",
        "where",
        "when",
        "which",
        "whence",
        "dost",
        "didst",
        "is",
        "are",
        "can",
        "must",
        "shall",
        "will",
    )

    i = 0
    while i < len(turns) - 1:
        turn = turns[i]
        next_turn = turns[i + 1]

        same_book = turn["book"] == next_turn["book"]
        different_speaker = turn["speaker"] != next_turn["speaker"]
        text_lower = turn["text"].lower()
        looks_like_question = "?" in turn["text"] or text_lower.startswith(question_words)

        if same_book and different_speaker and looks_like_question:
            answer_parts = [next_turn["text"]]
            end_line = next_turn["end_line"]
            j = i + 2

            while j < len(turns):
                candidate = turns[j]
                if candidate["book"] != turn["book"] or candidate["speaker"] == turn["speaker"]:
                    break
                if "?" in candidate["text"]:
                    break
                answer_parts.append(candidate["text"])
                end_line = candidate["end_line"]
                j += 1

            question_text = re.sub(r"\s+", " ", turn["text"]).strip()
            answer_text = re.sub(r"\s+", " ", " ".join(answer_parts)).strip()
            confidence = "high" if question_text.endswith("?") else "medium"

            records.append(
                {
                    "id": f"ch-{len(records)+1:04d}",
                    "translation": turn["translation"],
                    "book": turn["book"],
                    "questioner": turn["speaker"],
                    "answerer": next_turn["speaker"],
                    "question": question_text,
                    "answer": answer_text,
                    "source_lines": [turn["start_line"], end_line],
                    "confidence": confidence,
                }
            )
            i += 1
        i += 1

    return records


def write_outputs(records):
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

    strict_records = [record for record in records if record["confidence"] == "high"]
    with OUT_STRICT_JSONL.open("w", encoding="utf-8") as fh:
        for record in strict_records:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

    translation_counts = {}
    book_counts = {}
    for record in records:
        translation_counts[record["translation"]] = translation_counts.get(record["translation"], 0) + 1
        book_counts[record["book"]] = book_counts.get(record["book"], 0) + 1

    top_books = sorted(book_counts.items(), key=lambda item: (-item[1], item[0]))
    top_books_text = "\n".join(f"- `{book}`: {count} pairs" for book, count in top_books[:12])

    notes = f"""# Corpus Hermeticum Q&A Extraction

This dataset was extracted from `The Corpus Hermeticum.txt` into [corpus_hermeticum_qa.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/corpus_hermeticum_qa.jsonl).
The stricter subset is available at [corpus_hermeticum_qa_high_confidence.jsonl](/Users/wewlad/GitHub/AI_Training_Tests/corpus_hermeticum_qa_high_confidence.jsonl).

## What was extracted

- Explicit dialogue turns only.
- Speaker labels were normalized, including `H` -> `Hermes`, `A` -> `Asclepius`, and `Trismegistus` -> `Hermes`.
- Each JSONL record contains `book`, `translation`, `questioner`, `answerer`, `question`, `answer`, `source_lines`, and a heuristic `confidence`.
- `high` confidence means the question turn ends with an explicit question mark and the following turn is a different named speaker in the same book.
- `medium` confidence means the pairing still looked plausible, but the local turn boundary was less explicit.

## Important caveats

- The source file contains at least two translation families: Mead-style Roman numeral books and Everard-style `The Ninth Book...` headings.
- Those translations overlap in content, so they were tagged separately instead of merged. This helps prevent accidental duplicate training examples.
- Narrative-only stretches were intentionally excluded. They should be handled as a second dataset, such as `instruction -> exposition` or `topic -> passage summary`, rather than forced into fake Q&A.

## Recommended training strategy

- Use the JSONL file as a clean `question -> answer` subset.
- Prefer the high-confidence JSONL for first-pass training.
- Deduplicate across translations before fine-tuning if you want a single canonical answer set.
- Keep `translation` as metadata if stylistic variation is useful.
- For the non-dialogue material, create a separate corpus with fields like `book`, `theme`, `passage`, and `summary` rather than mixing it with direct Q&A.

## Pair counts

- Total pairs: `{len(records)}`
- High-confidence pairs: `{len(strict_records)}`
- Mead pairs: `{translation_counts.get("mead", 0)}`
- Everard pairs: `{translation_counts.get("everard", 0)}`

## Most dialogue-heavy sections

{top_books_text}
"""

    OUT_NOTES.write_text(notes, encoding="utf-8")


def main():
    turns = load_dialogue_turns()
    records = build_qa_records(turns)
    write_outputs(records)
    print(json.dumps({"turns": len(turns), "qa_pairs": len(records), "jsonl": str(OUT_JSONL)}))


if __name__ == "__main__":
    main()
