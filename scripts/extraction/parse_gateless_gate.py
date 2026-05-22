#!/usr/bin/env python3
"""Parse The Gateless Gate into koan-to-commentary dialogue rows."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from build_pilot_dialogue_dataset import (
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    write_jsonl,
)
from preview_dialogue_examples import SYSTEM_PROMPTS, preview_text, select_spread


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/gateless_gate_wikisource_raw.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

CASE_RE = re.compile(r"section\s*=\s*'{0,3}(?P<number>\d+)\.\s*(?P<title>.*?)'{0,3}\s*$", re.MULTILINE)
COMMENT_RE = re.compile(
    r":\s*'''(?P<speaker>Mumon|Amban)['’]s comment:?'''(?P<comment>.*?)(?=\n::|\n<br\s*/?>|\n\{\{rule\}\}|\Z)",
    re.DOTALL,
)
VERSE_LINE_RE = re.compile(r"^::\s*''(?P<line>.*?)''\s*$", re.MULTILINE)
HEADER_RE = re.compile(r"\{\{header.*?\}\}\s*", re.DOTALL)
TEMPLATE_RE = re.compile(r"\{\{[^{}]*\}\}")
LINK_RE = re.compile(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]")
ITALIC_RE = re.compile(r"'{2,5}")
HTML_TAG_RE = re.compile(r"<[^>]+>")
QUOTE_RE = re.compile(r'"(?P<quote>[^"]+)"')
ATTRIBUTED_BEFORE_RE = re.compile(
    r"(?P<speaker>"
    r"(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,2})|"
    r"(?:A|The|the|an|An)\s+(?:monk|student|pupil|teacher|attendant|successor|old man|boy)|"
    r"(?:he|He|she|She)"
    r")\s+"
    r"(?P<verb>asked|said|replied|answered|responded|called|told|cried|complained|added|continued|repeated|asked of)"
    r"(?:\s+[^:\".?!]{0,80})?:\s*$",
    re.IGNORECASE,
)
INTERNAL_DIALOGUE_SKIP_CASES = {2, 17, 23, 28}
INTERNAL_DIALOGUE_SKIP_TARGETS = {"Someone"}
ATTRIBUTED_AFTER_RE = re.compile(
    r"^\s*,?\s*"
    r"(?:(?P<verb>asked|said|replied|answered|responded|called|told|cried|complained|added|continued|repeated)\s+"
    r"(?P<speaker>"
    r"(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,2})|"
    r"(?:the|a|an)\s+(?:monk|student|pupil|teacher|attendant|successor|old man|boy)|"
    r"(?:he|she)"
    r")|"
    r"(?P<speaker_first>"
    r"(?:[A-Z][A-Za-z-]+(?:\s+[A-Z][A-Za-z-]+){0,2})|"
    r"(?:The|A|An|the|a|an)\s+(?:monk|student|pupil|teacher|attendant|successor|old man|boy)|"
    r"(?:he|she)"
    r")\s+"
    r"(?P<verb_after>asked|said|replied|answered|responded|called|told|cried|complained|added|continued|repeated))\b",
    re.IGNORECASE,
)


def clean_wiki_text(text: str) -> str:
    text = TEMPLATE_RE.sub("", text)
    text = LINK_RE.sub(r"\1", text)
    text = ITALIC_RE.sub("", text)
    text = HTML_TAG_RE.sub("", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("&#160;", " ")
    text = re.sub(r"^:+\s*", "", text, flags=re.MULTILINE)
    return clean_dataset_text(text)


def clean_wiki_lines(lines: list[str]) -> str:
    cleaned = [clean_wiki_text(line) for line in lines]
    return "\n".join(line for line in cleaned if line)


def extract_case(page: dict) -> dict | None:
    title = page["title"].split("/", 1)[-1]
    raw = page["revisions"][0]["slots"]["main"]["*"]
    case_match = CASE_RE.search(raw)
    if not case_match:
        return None

    case_number = int(case_match.group("number"))
    case_title = clean_wiki_text(case_match.group("title"))
    body = HEADER_RE.sub("", raw, count=1)
    comment_match = COMMENT_RE.search(body)
    if not comment_match:
        return None

    koan_text = clean_wiki_text(body[: comment_match.start()])
    comment_text = clean_wiki_text(comment_match.group("comment"))
    verse_text = clean_wiki_lines(VERSE_LINE_RE.findall(body))
    if not koan_text or not comment_text:
        return None

    return {
        "case_number": case_number,
        "title": case_title or title,
        "koan": koan_text,
        "comment": comment_text,
        "comment_speaker": comment_match.group("speaker"),
        "verse": verse_text,
    }


def parse_cases(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    pages = payload["query"]["pages"].values()
    cases = [case for page in pages if (case := extract_case(page))]
    return sorted(cases, key=lambda item: item["case_number"])


def case_context_label(case: dict) -> str:
    return f"Participant A (Koan case {case['case_number']}: {case['title']})"


def build_gateless_messages(
    *,
    history: list[tuple[str, str]],
    target_speaker: str,
    target_text: str,
) -> list[dict[str, str]]:
    history_text = "\n".join(
        f"{speaker}: {clean_dataset_text(text)}" for speaker, text in history
    )
    return [
        {"role": "system", "content": clean_dataset_text(SYSTEM_PROMPTS["buddhist"])},
        {
            "role": "user",
            "content": (
                f"Conversation so far:\n{history_text}\n\n"
                f"Write Participant B ({target_speaker})'s next reply."
            ),
        },
        {"role": "assistant", "content": clean_dataset_text(target_text)},
    ]


def canonical_internal_speaker(speaker: str, previous_speaker: str | None) -> str | None:
    speaker = clean_dataset_text(speaker).strip(" ,.;:")
    lowered = speaker.lower()
    narrative_starts = (
        "after ",
        "again ",
        "and ",
        "for ",
        "next ",
        "then ",
        "to ",
    )
    narrative_fragments = {
        "the cat and",
        "the phrase ummon",
        "hyakujo smiled and",
        "and he also",
    }
    if lowered.startswith(narrative_starts) or lowered in narrative_fragments:
        return None
    if " and " in lowered or lowered.endswith(" and"):
        return None
    if lowered in {"the other"}:
        return None
    if lowered in {"he", "she"}:
        return previous_speaker
    if lowered in {"a monk", "the monk", "an monk"}:
        return "Monk"
    if lowered in {"a student", "the student", "an student"}:
        return "Student"
    if lowered in {"a pupil", "the pupil", "an pupil"}:
        return "Pupil"
    if lowered in {"a teacher", "the teacher", "an teacher"}:
        return "Teacher"
    if lowered in {"a boy", "the boy", "an boy"}:
        return "Boy"
    if lowered in {"a attendant", "the attendant", "an attendant"}:
        return "Attendant"
    if lowered in {"a successor", "the successor", "an successor"}:
        return "Successor"
    if lowered in {"a old man", "an old man", "the old man"}:
        return "Old Man"
    if len(speaker.split()) > 4:
        return None
    return speaker[:1].upper() + speaker[1:]


def speaker_before_quote(text: str, quote_start: int) -> str | None:
    prefix = text[max(0, quote_start - 180) : quote_start]
    matches = list(ATTRIBUTED_BEFORE_RE.finditer(prefix))
    if not matches:
        return None
    match = matches[-1]
    return match.group("speaker")


def speaker_after_quote(text: str, quote_end: int) -> str | None:
    suffix = text[quote_end : quote_end + 120]
    match = ATTRIBUTED_AFTER_RE.search(suffix)
    if not match:
        return None
    return match.group("speaker") or match.group("speaker_first")


def extract_internal_quote_turns(case: dict) -> list[dict[str, object]]:
    turns: list[dict[str, object]] = []
    previous_speaker: str | None = None

    for match in QUOTE_RE.finditer(case["koan"]):
        quote = clean_dataset_text(match.group("quote"))
        if not quote:
            continue
        if quote.endswith(","):
            continue

        raw_speaker = speaker_before_quote(case["koan"], match.start())
        if raw_speaker is None:
            raw_speaker = speaker_after_quote(case["koan"], match.end())
        speaker = canonical_internal_speaker(raw_speaker, previous_speaker) if raw_speaker else None
        if speaker is None:
            continue

        turns.append(
            {
                "speaker": speaker,
                "text": quote,
                "quote_start": match.start(),
                "quote_end": match.end(),
            }
        )
        previous_speaker = speaker

    return turns


def internal_turns_to_rows(
    case: dict,
    *,
    history_quotes: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    source_name = "gateless_gate_wikisource_raw.json"
    kind = "gateless_gate_internal_dialogue"
    rows: list[dict] = []
    if case["case_number"] in INTERNAL_DIALOGUE_SKIP_CASES:
        return rows

    turns = extract_internal_quote_turns(case)

    for idx, target in enumerate(turns):
        target_words = count_dataset_words(str(target["text"]))
        if target_words < min_target_words or target_words > max_target_words:
            continue

        history = turns[max(0, idx - history_quotes) : idx]
        if not history or not any(item["speaker"] != target["speaker"] for item in history):
            continue

        target_speaker = str(target["speaker"])
        if target_speaker in INTERNAL_DIALOGUE_SKIP_TARGETS:
            continue
        mapped_history = [
            (
                (
                    "Participant B"
                    if item["speaker"] == target_speaker
                    else "Participant A"
                )
                + f" ({item['speaker']})",
                str(item["text"]),
            )
            for item in history
        ]
        rows.append(
            {
                "messages": build_gateless_messages(
                    history=mapped_history,
                    target_speaker=target_speaker,
                    target_text=str(target["text"]),
                ),
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind=f"{kind}_{case['case_number']}_{idx}",
                        source_lines=[case["case_number"], case["case_number"]],
                        target_speaker=target_speaker,
                    ),
                    "kind": kind,
                    "source": "The Gateless Gate",
                    "source_file": source_name,
                    "source_lines": [case["case_number"], case["case_number"]],
                    "target_speaker": target_speaker,
                    "target_participant": "Participant B",
                    "target_words": target_words,
                    "case_title": case["title"],
                },
            }
        )

    return rows


def case_to_row(case: dict) -> dict:
    source_name = "gateless_gate_wikisource_raw.json"
    source_lines = [case["case_number"], case["case_number"]]
    kind = "gateless_gate_koan_commentary"
    target_speaker = case["comment_speaker"]
    return {
        "messages": build_gateless_messages(
            history=[(case_context_label(case), case["koan"])],
            target_speaker=target_speaker,
            target_text=case["comment"],
        ),
        "metadata": {
            "record_id": make_record_id(
                source_name=source_name,
                kind=f"{kind}_{case['case_number']}",
                source_lines=source_lines,
                target_speaker=target_speaker,
            ),
            "kind": kind,
            "source": "The Gateless Gate",
            "source_file": source_name,
            "source_lines": source_lines,
            "target_speaker": target_speaker,
            "target_participant": "Participant B",
            "target_words": count_dataset_words(case["comment"]),
            "case_title": case["title"],
        },
    }


def case_to_verse_row(case: dict) -> dict | None:
    if not case.get("verse"):
        return None

    source_name = "gateless_gate_wikisource_raw.json"
    source_lines = [case["case_number"], case["case_number"]]
    kind = "gateless_gate_commentary_verse"
    target_speaker = case["comment_speaker"]
    return {
        "messages": build_gateless_messages(
            history=[
                (case_context_label(case), case["koan"]),
                (f"Participant B ({target_speaker})", case["comment"]),
            ],
            target_speaker=target_speaker,
            target_text=case["verse"],
        ),
        "metadata": {
            "record_id": make_record_id(
                source_name=source_name,
                kind=f"{kind}_{case['case_number']}",
                source_lines=source_lines,
                target_speaker=target_speaker,
            ),
            "kind": kind,
            "source": "The Gateless Gate",
            "source_file": source_name,
            "source_lines": source_lines,
            "target_speaker": target_speaker,
            "target_participant": "Participant B",
            "target_words": count_dataset_words(case["verse"]),
            "case_title": case["title"],
        },
    }


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    return "\n".join(
        [
            f"## Review Example {index}: {metadata['source']}",
            "",
            f"- Record ID: `{metadata['record_id']}`",
            f"- Kind: `{metadata['kind']}`",
            f"- Case: `{metadata['source_lines'][0]}. {metadata['case_title']}`",
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
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Gateless Gate koan rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="gateless_gate_dialogue")
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    parser.add_argument(
        "--include-internal-dialogue",
        action="store_true",
        help="Also mine clear quoted dialogue turns inside the koan cases.",
    )
    parser.add_argument(
        "--only-internal-dialogue",
        action="store_true",
        help="Write only mined quoted dialogue turns inside the koan cases.",
    )
    parser.add_argument(
        "--internal-history-quotes",
        type=int,
        default=3,
        help="Quoted turns to include before an internal-dialogue target.",
    )
    parser.add_argument(
        "--internal-min-target-words",
        type=int,
        default=1,
        help="Minimum words for internal quoted dialogue targets.",
    )
    parser.add_argument(
        "--internal-max-target-words",
        type=int,
        default=120,
        help="Maximum words for internal quoted dialogue targets.",
    )
    args = parser.parse_args()

    cases = parse_cases(args.source.expanduser().resolve())
    internal_rows = [
        row
        for case in cases
        for row in internal_turns_to_rows(
            case,
            history_quotes=args.internal_history_quotes,
            min_target_words=args.internal_min_target_words,
            max_target_words=args.internal_max_target_words,
        )
    ]
    rows = [] if args.only_internal_dialogue else [case_to_row(case) for case in cases]
    if not args.only_internal_dialogue:
        rows.extend(row for case in cases if (row := case_to_verse_row(case)))
    if args.include_internal_dialogue or args.only_internal_dialogue:
        rows.extend(internal_rows)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    write_jsonl(jsonl_path, rows)

    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(
            [
                "# Gateless Gate Review Sample",
                "",
                f"Rows parsed: `{len(rows)}`",
                f"Sampled rows: `{len(sample)}`",
                "",
                *[
                    row_to_markdown(row, idx, preview_chars=args.preview_chars)
                    for idx, row in enumerate(sample, 1)
                ],
            ]
        ),
        encoding="utf-8",
    )

    print(f"Cases parsed: {len(cases)}")
    print(f"Internal dialogue rows mined: {len(internal_rows)}")
    print(f"Rows written: {len(rows)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
