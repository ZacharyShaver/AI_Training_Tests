import unittest

from review_policy import (
    HARD_FAILURE_BROKEN_MAPPING,
    HARD_FAILURE_CONTAMINATION,
    HARD_FAILURE_MALFORMED_TARGET,
    WARNING_ONE_TURN,
    WARNING_SCENE_LOOSENESS,
    assess_row,
)


def make_row(
    *,
    prompt_lines: list[str],
    assistant: str,
    source_lines: list[int] | None = None,
    target_participant: str = "Participant B",
) -> dict:
    prompt = "Conversation so far:\n" + "\n".join(prompt_lines) + f"\n\nWrite {target_participant}'s next reply."
    return {
        "messages": [
            {"role": "system", "content": "system"},
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": assistant},
        ],
        "metadata": {
            "record_id": "test:kind:1-2:speaker",
            "kind": "kind",
            "source": "Source",
            "source_file": "source.txt",
            "source_lines": source_lines or [10, 12],
            "target_speaker": "Speaker",
            "target_participant": target_participant,
            "target_words": len(assistant.split()),
        },
    }


class ReviewPolicyTest(unittest.TestCase):
    def test_one_turn_prompt_passes_with_warning(self) -> None:
        row = make_row(
            prompt_lines=["Participant A (Teacher): What is the path?"],
            assistant="Steady attention is the path.",
        )

        assessment = assess_row(row)

        self.assertEqual(assessment.label, "Approve with warning")
        self.assertEqual(assessment.hard_failures, [])
        self.assertIn(WARNING_ONE_TURN, assessment.warnings)

    def test_slight_scene_looseness_passes_with_warning(self) -> None:
        row = make_row(
            prompt_lines=[
                "Participant A (Teacher): What is the path?",
                "Participant B (Student): Steady attention.",
                "Participant A (Teacher): What follows from that?",
            ],
            assistant="Release follows from that.",
            source_lines=[200, 255],
        )

        assessment = assess_row(row)

        self.assertEqual(assessment.label, "Approve with warning")
        self.assertIn(WARNING_SCENE_LOOSENESS, assessment.warnings)

    def test_clean_multi_turn_row_is_approved(self) -> None:
        row = make_row(
            prompt_lines=[
                "Participant A (Teacher): What is the path?",
                "Participant B (Student): Steady attention is the path.",
                "Participant A (Teacher): And what follows from that?",
            ],
            assistant="Release follows from that.",
            source_lines=[20, 24],
        )

        assessment = assess_row(row)

        self.assertEqual(assessment.label, "Approve")
        self.assertEqual(assessment.hard_failures, [])
        self.assertEqual(assessment.warnings, [])

    def test_broken_participant_mapping_rejects(self) -> None:
        row = make_row(
            prompt_lines=["Narrator: What is the path?"],
            assistant="Steady attention is the path.",
        )

        assessment = assess_row(row)

        self.assertEqual(assessment.label, "Reject")
        self.assertIn(HARD_FAILURE_BROKEN_MAPPING, assessment.hard_failures)

    def test_fragmentary_target_rejects(self) -> None:
        row = make_row(
            prompt_lines=["Participant A (Teacher): What is the path?"],
            assistant="Steady attention:",
        )

        assessment = assess_row(row)

        self.assertEqual(assessment.label, "Reject")
        self.assertIn(HARD_FAILURE_MALFORMED_TARGET, assessment.hard_failures)

    def test_contamination_rejects(self) -> None:
        row = make_row(
            prompt_lines=["Participant A (Teacher): Translator's note: what is the path?"],
            assistant="Steady attention is the path.",
        )

        assessment = assess_row(row)

        self.assertEqual(assessment.label, "Reject")
        self.assertIn(HARD_FAILURE_CONTAMINATION, assessment.hard_failures)


if __name__ == "__main__":
    unittest.main()
