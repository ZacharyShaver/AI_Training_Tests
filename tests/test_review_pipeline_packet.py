from __future__ import annotations

from pathlib import Path

from tools.review_pipeline.render_review_packet import render_review_packet


def make_review_row() -> dict:
    return {
        "messages": [
            {"role": "system", "content": "System"},
            {
                "role": "user",
                "content": "Conversation so far:\nParticipant A: What is wisdom?",
            },
            {"role": "assistant", "content": "Wisdom is tested in conduct."},
        ],
        "metadata": {
            "record_id": "example:next_reply:1-2:teacher",
            "source": "Example Source",
            "source_file": "example.txt",
            "source_lines": [1, 2],
            "target_speaker": "Teacher",
            "target_participant": "Participant B",
            "target_words": 5,
        },
    }


def test_render_review_packet_includes_row_context_and_criteria() -> None:
    packet = render_review_packet(
        rows=[make_review_row()],
        source_jsonl_path=Path("review_outputs/parser_reviews/example/set_01/example.jsonl"),
        criteria=["Prompt and reply preserve source continuity.", "No malformed speaker labels."],
    )

    assert "# Random Sample Review Packet" in packet
    assert "Source JSONL: `review_outputs/parser_reviews/example/set_01/example.jsonl`" in packet
    assert "Record ID: `example:next_reply:1-2:teacher`" in packet
    assert "Source: `Example Source`" in packet
    assert "Assistant target: `Participant B (Teacher)`" in packet
    assert "Conversation so far:" in packet
    assert "Wisdom is tested in conduct." in packet
    assert "- Prompt and reply preserve source continuity." in packet
    assert "- No malformed speaker labels." in packet

