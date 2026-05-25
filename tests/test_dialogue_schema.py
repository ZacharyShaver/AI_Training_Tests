from __future__ import annotations

import pytest

from scripts.extraction.dialogue_schema import DialogueRow


def make_valid_row() -> dict:
    assistant_text = "This is the assistant reply."
    return {
        "messages": [
            {"role": "system", "content": "You are a helpful philosophical interlocutor."},
            {
                "role": "user",
                "content": (
                    "Conversation so far:\nParticipant A: Hello\n\n"
                    "Write Participant B's next reply."
                ),
            },
            {"role": "assistant", "content": assistant_text},
        ],
        "metadata": {
            "record_id": "example-source:next_reply:10-12:teacher",
            "kind": "example_next_reply",
            "source": "Example Source",
            "source_file": "example.txt",
            "source_lines": [10, 12],
            "target_speaker": "Teacher",
            "target_participant": "Participant B",
            "target_words": 5,
        },
    }


def test_valid_dialogue_row_passes_validation() -> None:
    row = DialogueRow.model_validate(make_valid_row())

    assert row.messages[0].role == "system"
    assert row.messages[1].role == "user"
    assert row.messages[2].role == "assistant"
    assert row.metadata.target_words == 5


def test_dialogue_row_requires_exactly_three_messages() -> None:
    row = make_valid_row()
    row["messages"].append({"role": "assistant", "content": "Extra reply"})

    with pytest.raises(ValueError, match="exactly three messages"):
        DialogueRow.model_validate(row)


def test_dialogue_row_requires_system_user_assistant_role_order() -> None:
    row = make_valid_row()
    row["messages"][0]["role"] = "user"

    with pytest.raises(ValueError, match="system, user, assistant"):
        DialogueRow.model_validate(row)


def test_dialogue_row_requires_target_words_to_match_assistant_text() -> None:
    row = make_valid_row()
    row["metadata"]["target_words"] = 99

    with pytest.raises(ValueError, match="target_words"):
        DialogueRow.model_validate(row)


def test_dialogue_row_requires_required_metadata_fields() -> None:
    row = make_valid_row()
    del row["metadata"]["record_id"]

    with pytest.raises(Exception):
        DialogueRow.model_validate(row)
