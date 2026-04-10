#!/usr/bin/env python3

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "oritiginal text" / "the_key-to-theosophy.txt"
OUTPUT_DIR = REPO_ROOT / "Training Data"
OUT_JSONL = OUTPUT_DIR / "key_to_theosophy_qa.jsonl"
OUT_STRICT_JSONL = OUTPUT_DIR / "key_to_theosophy_qa_high_confidence.jsonl"
OUT_NOTES = OUTPUT_DIR / "key_to_theosophy_extraction_notes.md"


START_RE = re.compile(r"^SECTION 1: THEOSOPHY AND THE THEOSOPHICAL SOCIETY$")
END_RE = re.compile(r"^GLOSSARY$")
SECTION_RE = re.compile(r"^SECTION\s+(\d+):\s+(.+)$")
FOOTNOTE_START_RE = re.compile(r"^\d+\s+")
SPEAKER_RE = re.compile(
    r"^(?P<label>ENQUIRER|INQUIRER|ENQUIRER \(continued\)|QUESTIONER|THEOSOPHIST|ANSWERER|Q|A)\.\s*(?P<text>.*)$",
    re.IGNORECASE,
)
INLINE_SPEAKER_SPLIT_RE = re.compile(
    r"\s+(?=(?:ENQUIRER|INQUIRER|QUESTIONER|THEOSOPHIST|ANSWERER|Q|A)\.\s)",
    re.IGNORECASE,
)


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


def normalize_speaker(label: str) -> str:
    key = label.upper()
    if key in {"ENQUIRER", "INQUIRER", "ENQUIRER (CONTINUED)", "QUESTIONER", "Q"}:
        return "Enquirer"
    if key in {"THEOSOPHIST", "ANSWERER", "A"}:
        return "Theosophist"
    return label.title()


def is_heading(line: str) -> bool:
    if not line:
        return False
    if SECTION_RE.match(line):
        return True
    if line == "PREFACE":
        return True
    if line.isupper() and len(line) > 4 and len(line.split()) <= 12:
        return True
    return False


def clean_text(text: str) -> str:
    text = re.sub(r"\(\d+\)", "", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def expand_line(line: str) -> list[str]:
    parts = INLINE_SPEAKER_SPLIT_RE.split(line)
    return [part.strip() for part in parts if part.strip()]


def parse_turns():
    lines = SOURCE.read_text(encoding="utf-8", errors="ignore").splitlines()
    in_body = False
    section = None
    subsection = None
    turns = []
    pending = None
    in_footnote = False

    for lineno, raw in enumerate(lines, start=1):
        normalized = normalize_line(raw)
        if not normalized:
            continue

        for line in expand_line(normalized):
            if not in_body:
                if START_RE.match(line):
                    in_body = True
                    section = line
                continue

            if END_RE.match(line):
                in_body = False
                break

            section_match = SECTION_RE.match(line)
            if section_match:
                in_footnote = False
                section = f"SECTION {section_match.group(1)}: {section_match.group(2)}"
                subsection = None
                continue

            speaker_match = SPEAKER_RE.match(line)
            if speaker_match:
                in_footnote = False
                if pending:
                    pending["text"] = clean_text(pending["text"])
                    if pending["text"]:
                        turns.append(pending)
                pending = {
                    "section": section,
                    "subsection": subsection,
                    "speaker": normalize_speaker(speaker_match.group("label")),
                    "speaker_source": "explicit_prefix",
                    "speaker_confidence": 0.99,
                    "text": speaker_match.group("text").strip(),
                    "line": lineno,
                }
                continue

            if FOOTNOTE_START_RE.match(line):
                in_footnote = True
                continue

            if in_footnote:
                continue

            if is_heading(line):
                subsection = line
                continue

            if pending:
                pending["text"] += " " + line

    if pending:
        pending["text"] = clean_text(pending["text"])
        if pending["text"]:
            turns.append(pending)

    return turns


def build_records(turns: list[dict]):
    records = []
    for idx, turn in enumerate(turns[:-1]):
        if turn["speaker"] != "Enquirer":
            continue
        if "?" not in turn["text"]:
            continue

        nxt = turns[idx + 1]
        if nxt["speaker"] != "Theosophist":
            continue
        if turn["section"] != nxt["section"]:
            continue

        confidence = "high"
        if turn["subsection"] != nxt["subsection"]:
            confidence = "medium"

        records.append(
            {
                "id": f"key-{len(records)+1:04d}",
                "source_text": "The Key to Theosophy",
                "section": turn["section"],
                "subsection": turn["subsection"],
                "questioner": turn["speaker"],
                "answerer": nxt["speaker"],
                "question": turn["text"],
                "answer": nxt["text"],
                "source_lines": [turn["line"], nxt["line"]],
                "confidence": confidence,
            }
        )
    return records


def write_outputs(records: list[dict], turns: list[dict]):
    with OUT_JSONL.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

    strict_records = [r for r in records if r["confidence"] == "high"]
    with OUT_STRICT_JSONL.open("w", encoding="utf-8") as fh:
        for record in strict_records:
            fh.write(json.dumps(record, ensure_ascii=True) + "\n")

    section_counts: dict[str, int] = {}
    subsection_counts: dict[str, int] = {}
    for record in records:
        section_counts[record["section"]] = section_counts.get(record["section"], 0) + 1
        key = record["subsection"] or "unknown"
        subsection_counts[key] = subsection_counts.get(key, 0) + 1

    top_subsections = sorted(subsection_counts.items(), key=lambda item: (-item[1], item[0]))[:12]

    notes = [
        "# Key To Theosophy Extraction Notes",
        "",
        f"- Source file: `{SOURCE.name}`",
        "- Extraction style: explicit dialogue-prefix extraction using speaker labels such as `ENQUIRER.` and `THEOSOPHIST.`",
        "- Excluded material: title matter, table of contents, preface, glossary",
        "- Speaker cue expansion supported in extractor: `ENQUIRER`, `INQUIRER`, `QUESTIONER`, `Q`, `THEOSOPHIST`, `ANSWERER`, `A`",
        "- Confidence policy: `high` when an `Enquirer` turn is immediately followed by a `Theosophist` reply in the same section and subsection; `medium` when the reply crosses subsection boundaries",
        "",
        f"- Parsed turns: {len(turns)}",
        f"- Q&A pairs: {len(records)}",
        f"- High-confidence pairs: {len(strict_records)}",
        "",
        "## Section Counts",
        "",
    ]

    for key, count in sorted(section_counts.items()):
        notes.append(f"- {key}: {count}")

    notes.extend(
        [
            "",
            "## Top Subsections",
            "",
        ]
    )
    for key, count in top_subsections:
        notes.append(f"- {key}: {count}")

    notes.extend(
        [
            "",
            "## Caveats",
            "",
            "- This text is unusually clean for extraction because most exchanges are explicitly prefixed with named speakers.",
            "- Standalone numbered footnote blocks are stripped during parsing so they do not bleed into answer text.",
            "- A few answers span multiple paragraphs or include quoted material inside the answer; these are preserved as single answer blocks for training usefulness.",
            "- The extractor was written with broader prefix support so the same pattern family can be reused on similar dialogue texts with `Q.` / `A.` or `Questioner.` / `Answerer.` labels.",
        ]
    )

    OUT_NOTES.write_text("\n".join(notes) + "\n", encoding="utf-8")


def main():
    turns = parse_turns()
    records = build_records(turns)
    write_outputs(records, turns)
    print(
        json.dumps(
            {
                "turns": len(turns),
                "qa_pairs": len(records),
                "high_confidence": sum(1 for r in records if r["confidence"] == "high"),
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
