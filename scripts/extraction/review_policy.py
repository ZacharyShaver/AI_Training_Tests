#!/usr/bin/env python3
"""Shared review policy for dialogue row review and machine-review packets."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable

from build_pilot_dialogue_dataset import count_dataset_words


TURN_RE = re.compile(r"^(Participant [AB]) \((.+)\):\s*(.+)$")
WRITE_RE = re.compile(r"^Write (?P<participant>Participant [AB](?: \([^)]+\))?)'s next reply\.$")

HARD_FAILURE_BROKEN_MAPPING = "broken participant mapping"
HARD_FAILURE_SCENE_JUMP = "obvious scene jump"
HARD_FAILURE_WRONG_SPEAKER = "wrong speaker attribution"
HARD_FAILURE_MALFORMED_TARGET = "malformed or fragmentary target text"
HARD_FAILURE_CONTAMINATION = "narration or commentary contamination"

WARNING_ONE_TURN = "one prior turn of context"
WARNING_MINIMAL_CONTEXT = "minimal context"
WARNING_SCENE_LOOSENESS = "slight local scene looseness"

CONTAMINATION_MARKERS = (
    "Translator's note",
    "Copyright",
    "Table of Contents",
    "Bibliography",
    "Index",
    "GLOSSARY",
)


@dataclass
class ParsedPrompt:
    turns: list[tuple[str, str, str]]
    instruction_participant: str | None


@dataclass
class ReviewAssessment:
    label: str
    hard_failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_prompt(user_content: str) -> ParsedPrompt:
    lines = [line.rstrip() for line in user_content.splitlines()]
    turns: list[tuple[str, str, str]] = []
    instruction_participant: str | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line == "Conversation so far:":
            continue
        turn_match = TURN_RE.match(line)
        if turn_match:
            turns.append(
                (
                    turn_match.group(1),
                    turn_match.group(2),
                    turn_match.group(3),
                )
            )
            continue
        write_match = WRITE_RE.match(line)
        if write_match:
            instruction_participant = write_match.group("participant")

    return ParsedPrompt(turns=turns, instruction_participant=instruction_participant)


def contains_contamination(text: str) -> bool:
    return any(marker in text for marker in CONTAMINATION_MARKERS)


def target_is_fragmentary(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if count_dataset_words(stripped) < 2:
        return True
    if stripped.endswith((":", ";", ",")):
        return True
    if stripped.endswith("...") or stripped.endswith(".…") or stripped.endswith(".."):
        return True
    if stripped.count('"') % 2 == 1:
        return True
    if stripped.count("“") != stripped.count("”"):
        return True
    return False


def auto_hard_failures(row: dict) -> list[str]:
    failures: list[str] = []
    messages = row.get("messages") or []
    metadata = row.get("metadata") or {}
    if len(messages) != 3:
        return [HARD_FAILURE_BROKEN_MAPPING]

    user_content = messages[1].get("content", "")
    target_text = messages[2].get("content", "")
    target_participant = metadata.get("target_participant", "")

    parsed = parse_prompt(user_content)
    if not parsed.turns or parsed.instruction_participant is None:
        failures.append(HARD_FAILURE_BROKEN_MAPPING)
    if not isinstance(target_participant, str) or not target_participant.startswith("Participant B"):
        failures.append(HARD_FAILURE_BROKEN_MAPPING)
    if parsed.instruction_participant and not parsed.instruction_participant.startswith("Participant B"):
        failures.append(HARD_FAILURE_BROKEN_MAPPING)
    if contains_contamination(user_content) or contains_contamination(target_text):
        failures.append(HARD_FAILURE_CONTAMINATION)
    if target_is_fragmentary(target_text):
        failures.append(HARD_FAILURE_MALFORMED_TARGET)

    return dedupe(failures)


def auto_warnings(row: dict) -> list[str]:
    warnings: list[str] = []
    messages = row.get("messages") or []
    metadata = row.get("metadata") or {}
    if len(messages) != 3:
        return warnings

    parsed = parse_prompt(messages[1].get("content", ""))
    turn_count = len(parsed.turns)
    if turn_count == 1:
        warnings.append(WARNING_ONE_TURN)
    elif turn_count == 2:
        warnings.append(WARNING_MINIMAL_CONTEXT)

    source_lines = metadata.get("source_lines")
    if (
        isinstance(source_lines, list)
        and len(source_lines) == 2
        and all(isinstance(value, int) for value in source_lines)
        and source_lines[1] - source_lines[0] > 40
    ):
        warnings.append(WARNING_SCENE_LOOSENESS)

    return dedupe(warnings)


def assess_row(
    row: dict,
    *,
    manual_hard_failures: Iterable[str] = (),
    manual_warnings: Iterable[str] = (),
) -> ReviewAssessment:
    hard_failures = dedupe([*auto_hard_failures(row), *manual_hard_failures])
    warnings = dedupe([*auto_warnings(row), *manual_warnings])
    if hard_failures:
        return ReviewAssessment(label="Reject", hard_failures=hard_failures, warnings=warnings)
    if warnings:
        return ReviewAssessment(
            label="Approve with warning",
            hard_failures=[],
            warnings=warnings,
        )
    return ReviewAssessment(label="Approve")


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def assessment_summary_text(assessment: ReviewAssessment) -> str:
    if assessment.label == "Reject":
        return "; ".join(assessment.hard_failures)
    if assessment.warnings:
        return "; ".join(assessment.warnings)
    return "clean structural pass"
