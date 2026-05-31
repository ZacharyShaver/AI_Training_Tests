from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from ai_training_tests.extraction.parsers.milinda_panha import build_rows, parse_turns


REPO_ROOT = Path(__file__).resolve().parents[1]
PARSE_MILINDA = REPO_ROOT / "scripts/extraction/parse_milinda_panha.py"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_parse_turns_handles_same_paragraph_dialogue_and_preserves_section_refs() -> None:
    source_dir = REPO_ROOT / "review_outputs" / f"milinda-parse-unit-{os.getpid()}"
    source_dir.mkdir(parents=True, exist_ok=True)
    source = source_dir / "milinda_sample.txt"
    source.write_text(
        "\n".join(
            [
                "## mil3.1.1",
                "",
                (
                    "Then, King Milinda said to Venerable NÄgasena, "
                    "â€œHow is the reverend one known, what is your name, venerable sir?â€ "
                    "â€œI am called NÄgasena, your majesty.â€"
                ),
                "",
                (
                    "Then, Venerable NÄgasena said this to King Milinda, "
                    "â€œDid you come on foot or rather in a vehicle?â€ "
                    "â€œI did not come on foot, venerable sir, I came in a chariot.â€"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )

    turns = parse_turns(source)

    assert [(turn.section_ref, turn.speaker) for turn in turns] == [
        ("mil3.1.1", "King Milinda"),
        ("mil3.1.1", "Venerable Nāgasena"),
        ("mil3.1.1", "Venerable Nāgasena"),
        ("mil3.1.1", "King Milinda"),
    ]
    assert turns[0].text == "How is the reverend one known, what is your name, venerable sir?"
    assert turns[1].text == "I am called Nāgasena, your majesty."
    assert turns[2].text == "Did you come on foot or rather in a vehicle?"
    assert turns[3].text == "I did not come on foot, venerable sir, I came in a chariot."


def test_parse_turns_merges_repeated_same_speaker_inline_quotes_before_reply() -> None:
    source_dir = REPO_ROOT / "review_outputs" / f"milinda-parse-unit-{os.getpid()}-same-speaker"
    source_dir.mkdir(parents=True, exist_ok=True)
    source = source_dir / "milinda_same_speaker_sample.txt"
    source.write_text(
        "\n".join(
            [
                "## mil3.1.1",
                "",
                (
                    "Then, King Milinda said this, "
                    "“May the assembly hear me.” "
                    "Then, King Milinda said this to Venerable Nāgasena, "
                    "“If there is no person here, who receives the offerings?” "
                    "“It is only a designation, your majesty.”"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )

    turns = parse_turns(source)

    assert [(turn.section_ref, turn.speaker) for turn in turns] == [
        ("mil3.1.1", "King Milinda"),
        ("mil3.1.1", "Venerable Nāgasena"),
    ]
    assert turns[0].text == "May the assembly hear me. If there is no person here, who receives the offerings?"
    assert turns[1].text == "It is only a designation, your majesty."


def test_build_rows_uses_bounded_alternating_exchange_after_same_speaker_merge() -> None:
    source_dir = REPO_ROOT / "review_outputs" / f"milinda-parse-unit-{os.getpid()}-rows"
    source_dir.mkdir(parents=True, exist_ok=True)
    source = source_dir / "milinda_row_sample.txt"
    source.write_text(
        "\n".join(
            [
                "## mil3.1.1",
                "",
                (
                    "Then, King Milinda said this, "
                    "“May the assembly hear me.” "
                    "Then, King Milinda said this to Venerable Nāgasena, "
                    "“If there is no person here, who receives the offerings?” "
                    "“It is only a designation, your majesty.”"
                ),
                "",
            ]
        ),
        encoding="utf-8",
    )

    rows = build_rows(
        parse_turns(source),
        max_history_turns=6,
        min_target_words=3,
        max_target_words=260,
    )

    assert len(rows) == 1
    assert rows[0]["messages"][1]["content"] == (
        "Conversation so far:\n"
        "Participant A (King Milinda): May the assembly hear me. "
        "If there is no person here, who receives the offerings?\n\n"
        "Write Participant B's next reply."
    )
    assert rows[0]["messages"][2]["content"] == "It is only a designation, your majesty."


def test_milinda_parser_writes_dataset_and_review_sample() -> None:
    output_dir = (
        REPO_ROOT / "review_outputs" / f"milinda-parser-test-{os.getpid()}-{os.getppid()}"
    )
    subprocess.run(
        [
            sys.executable,
            str(PARSE_MILINDA),
            "--output-dir",
            str(output_dir),
            "--sample-count",
            "3",
        ],
        cwd=REPO_ROOT,
        check=True,
    )

    dataset_path = output_dir / "milinda_panha_dialogue.jsonl"
    sample_path = output_dir / "milinda_panha_dialogue_review_sample.md"
    rows = read_jsonl(dataset_path)

    assert dataset_path.exists()
    assert sample_path.exists()
    assert any(row["metadata"]["source"] == "Milinda Panha" for row in rows)
    assert all(row["messages"][2]["content"] != "Certainly not, your majesty." for row in rows)
