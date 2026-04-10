#!/usr/bin/env python3

import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = REPO_ROOT / "oritiginal text" / "Platform Sutra .txt"
OUTPUT_DIR = REPO_ROOT / "Training Data"
OUT_JSONL = OUTPUT_DIR / "platform_sutra_qa.jsonl"
OUT_STRICT_JSONL = OUTPUT_DIR / "platform_sutra_qa_high_confidence.jsonl"
OUT_NOTES = OUTPUT_DIR / "platform_sutra_extraction_notes.md"


BODY_START_RE = re.compile(r"^Number One: Account of Origins$")
BODY_END_RE = re.compile(r"^End of The Platform Sutra\b")
QUOTE_RE = re.compile(r'(?P<quote>["\'])(?P<text>.+?)(?P=quote)')
SECTION_LINES = [
    "Number One: Account of Origins",
    "Number Two: Prajna",
    "Number Three: Questions",
    "Number Four: Meditation and Wisdom",
    "Number Five: Seated Meditation",
    "Number Six: Repentance",
    "Number Seven: Encounters",
    "Number Eight: Sudden and Gradual",
    "Number Nine: Proclamations",
    "Number Ten: Transmission",
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
    line = line.replace("�", "")
    line = re.sub(r"\s+", " ", line.strip())
    return line


def should_skip_line(line: str) -> bool:
    if not line:
        return True
    if re.fullmatch(r"\d+[a-z]?", line):
        return True
    if re.fullmatch(r"\[?\d+\]?", line):
        return True
    if re.fullmatch(r"[A-Z][a-z]+ \d+", line):
        return True
    return False


def read_body():
    lines = SOURCE.read_text(encoding="utf-8", errors="ignore").splitlines()
    body = []
    in_body = False

    for raw in lines:
        line = normalize_line(raw)
        if not in_body:
            if BODY_START_RE.match(line):
                in_body = True
                body.append(line)
            continue
        if BODY_END_RE.match(line):
            break
        body.append(line)
    return body


def build_paragraphs(lines: list[str]):
    paragraphs = []
    chunk = []
    for line in lines:
        if line.startswith("Number "):
            if chunk:
                paragraphs.append(" ".join(chunk).strip())
                chunk = []
            paragraphs.append(line)
            continue
        if should_skip_line(line):
            if chunk:
                paragraphs.append(" ".join(chunk).strip())
                chunk = []
            continue
        chunk.append(line)
    if chunk:
        paragraphs.append(" ".join(chunk).strip())
    return paragraphs


def normalize_speaker(raw: str, section: str | None, previous_speaker: str | None):
    text = raw.strip(" [](),.:-")
    lower = text.lower()

    if not text:
        return None, "unknown", 0.0

    direct_map = [
        ("the great master", "Huineng"),
        ("the master", "Huineng"),
        ("master", "Huineng"),
        ("prefect wei", "Prefect Wei"),
        ("lord wei", "Prefect Wei"),
        ("wei", "Prefect Wei"),
        ("the patriarch", "Hongren" if section == "Number One: Account of Origins" else "Huineng"),
        ("the fifth patriarch", "Hongren"),
        ("hongren", "Hongren"),
        ("yinzong", "Yinzong"),
        ("huiming", "Huiming"),
        ("fahai", "Fahai"),
        ("fada", "Fada"),
        ("zhitong", "Zhitong"),
        ("zhichang", "Zhichang"),
        ("zhidao", "Zhidao"),
        ("xingsi", "Xingsi"),
        ("huairang", "Huairang"),
        ("xuance", "Xuance"),
        ("xuanjue", "Yongjia Xuanjue"),
        ("zhihuang", "Zhihuang"),
        ("shenhui", "Shenhui"),
        ("the assembly", "Assembly"),
        ("those in the assembly", "Assembly"),
        ("the members of the congregation", "Assembly"),
        ("the government staff, scholars, and commoners respectfully bowed once again and", "Assembly"),
        ("the government staff, scholars, and commoners", "Assembly"),
        ("those in the great assembly", "Assembly"),
        ("everyone listening was amazed. yinzong had me brought up to the dais, where he examined me on the import of what i had said. hearing me say that the discrimination of the truth did not depend on written words, yinzong", "Yinzong"),
    ]
    for needle, normalized in direct_map:
        if lower.endswith(needle) or lower == needle:
            return normalized, "explicit", 0.98

    if lower in {"i", "i also", "i then", "i addressed him", "i replied"}:
        if section == "Number One: Account of Origins":
            return "Huineng", "section_inference", 0.75
        return previous_speaker, "pronoun_inference", 0.35

    if lower in {"he", "they"}:
        label = "Unidentified interlocutor" if lower == "he" else "Assembly"
        return label, "pronoun_inference", 0.35

    named_match = re.search(r"([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)$", text)
    if named_match:
        return named_match.group(1), "explicit", 0.94

    return None, "unknown", 0.0


def extract_speaker(context: str, section: str | None, previous_speaker: str | None):
    context = context.strip()
    if not context:
        return None, "unknown", 0.0

    patterns = [
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+asked(?:\s+further)?[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+said(?:\s+further| again)?[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+replied[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+answered[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+questioned(?:\s+me|\s+further)?[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+told(?:\s+the assembly|\s+me)?[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+addressed(?:\s+the assembly)?[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+rebuked him[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+announced[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+cried out[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+bowed(?:\s+to me)? and said[,: ]*$",
        r"([A-Za-z][A-Za-z .\[\]'-]{0,100}?)\s+called to me, saying[,: ]*$",
    ]

    search_window = context[-180:]
    for pattern in patterns:
        match = re.search(pattern, search_window, flags=re.IGNORECASE)
        if match:
            return normalize_speaker(match.group(1), section, previous_speaker)

    pronoun_patterns = [
        r"\b(I|He|he|They|they)\s+asked(?:\s+further)?[,: ]*$",
        r"\b(I|He|he|They|they)\s+said(?:\s+further| again)?[,: ]*$",
        r"\b(I|He|he|They|they)\s+replied[,: ]*$",
        r"\b(I|He|he|They|they)\s+answered[,: ]*$",
        r"\b(I|He|he|They|they)\s+addressed him[,: ]*$",
    ]
    for pattern in pronoun_patterns:
        match = re.search(pattern, search_window, flags=re.IGNORECASE)
        if match:
            return normalize_speaker(match.group(1), section, previous_speaker)

    return None, "unknown", 0.0


def clean_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_turns():
    paragraphs = build_paragraphs(read_body())
    turns = []
    current_section = None
    previous_speaker = None

    for idx, paragraph in enumerate(paragraphs, start=1):
        for section_line in SECTION_LINES:
            if paragraph.startswith(section_line):
                current_section = section_line
                paragraph = paragraph[len(section_line) :].strip()
                break
        if not paragraph:
            continue

        for quote_match in QUOTE_RE.finditer(paragraph):
            text = clean_text(quote_match.group("text"))
            if not text:
                continue
            context = paragraph[: quote_match.start()]
            speaker, source, confidence = extract_speaker(context, current_section, previous_speaker)
            if not speaker:
                continue

            turns.append(
                {
                    "section": current_section,
                    "speaker": speaker,
                    "speaker_source": source,
                    "speaker_confidence": confidence,
                    "text": text,
                    "paragraph_index": idx,
                }
            )
            previous_speaker = speaker
    return turns


def build_records(turns: list[dict]):
    records = []
    for idx, turn in enumerate(turns):
        if "?" not in turn["text"]:
            continue

        answer_turn = None
        for nxt in turns[idx + 1 : idx + 5]:
            if nxt["section"] != turn["section"]:
                break
            if nxt["speaker"] != turn["speaker"]:
                answer_turn = nxt
                break
        if not answer_turn:
            continue

        confidence = "high"
        if min(turn["speaker_confidence"], answer_turn["speaker_confidence"]) < 0.9:
            confidence = "medium"
        if min(turn["speaker_confidence"], answer_turn["speaker_confidence"]) < 0.5:
            confidence = "low"

        records.append(
            {
                "id": f"platform-{len(records)+1:04d}",
                "source_text": "Platform Sutra",
                "section": turn["section"],
                "questioner": turn["speaker"],
                "answerer": answer_turn["speaker"],
                "question": turn["text"],
                "answer": answer_turn["text"],
                "source_paragraphs": [turn["paragraph_index"], answer_turn["paragraph_index"]],
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
    for record in records:
        key = record["section"] or "unknown"
        section_counts[key] = section_counts.get(key, 0) + 1

    notes = [
        "# Platform Sutra Extraction Notes",
        "",
        f"- Source file: `{SOURCE.name}`",
        "- Extraction style: explicit or strongly inferable quoted dialogue only",
        "- Excluded material: front matter, appendix, glossary, bibliography, index",
        "- Speaker normalization: common recurring roles normalized to stable labels such as `Huineng`, `Hongren`, and `Prefect Wei`",
        "- Confidence policy: `high` for explicit named attributions on both sides; `medium` when one side is section/pronoun inferred; `low` retained only in the full file",
        "",
        f"- Parsed turns: {len(turns)}",
        f"- Q&A pairs: {len(records)}",
        f"- High-confidence pairs: {len(strict_records)}",
        "",
        "## Section Counts",
        "",
    ]
    for section, count in sorted(section_counts.items()):
        notes.append(f"- {section}: {count}")

    notes.extend(
        [
            "",
            "## Caveats",
            "",
            "- Section One contains nested autobiographical dialogue inside Huineng's long speech; some pronoun-based turns remain conservative or are dropped.",
            "- Quoted material embedded inside doctrinal exposition can still create medium-confidence pairings that should be reviewed before training.",
            "- The strict file is the safest starting point for finetuning or supervised dialogue extraction.",
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
