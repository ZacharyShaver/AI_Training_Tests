from __future__ import annotations

import json
from pathlib import Path


def test_domain_modules_are_available_from_package_and_legacy_paths() -> None:
    from ai_training_tests.domain.dialogue_schema import DialogueRow as PackageDialogueRow
    from ai_training_tests.domain.source_manifest import approved_source_labels
    from scripts.extraction.dialogue_schema import DialogueRow as LegacyDialogueRow
    from scripts.extraction.dialogue_source_manifest import (
        approved_source_labels as legacy_approved_source_labels,
    )

    assert PackageDialogueRow is LegacyDialogueRow
    assert "Asclepius" in approved_source_labels()
    assert approved_source_labels() == legacy_approved_source_labels()


def test_extraction_common_jsonl_helpers_round_trip_rows(tmp_path: Path) -> None:
    from ai_training_tests.extraction.common.jsonl_io import read_jsonl, write_jsonl

    path = tmp_path / "rows.jsonl"
    rows = [{"metadata": {"record_id": "one"}}, {"metadata": {"record_id": "two"}}]

    write_jsonl(path, rows)

    assert path.read_text(encoding="utf-8").endswith("\n")
    assert [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] == rows
    assert read_jsonl(path) == rows


def test_review_policy_is_available_from_package_and_legacy_paths() -> None:
    from ai_training_tests.extraction.review.review_policy import assess_row as package_assess_row
    from scripts.extraction.review_policy import assess_row as legacy_assess_row

    assert package_assess_row is legacy_assess_row


def test_asclepius_parser_is_available_from_package_and_legacy_paths() -> None:
    from ai_training_tests.extraction.parsers.asclepius import infer_speaker as package_infer
    from scripts.extraction.parse_asclepius import infer_speaker as legacy_infer

    quote = "Why was it necessary, O Trismegistus, that Man be placed in the world?"

    assert package_infer(quote, previous_speaker="Hermes") == "Asclepius"
    assert legacy_infer is package_infer
