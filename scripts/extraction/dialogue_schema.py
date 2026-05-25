from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, model_validator

WORD_RE = re.compile(r"\b[\w'-]+\b")
EXPECTED_ROLE_ORDER = ("system", "user", "assistant")


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


class DialogueMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class DialogueMetadata(BaseModel):
    record_id: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    source: str = Field(min_length=1)
    source_file: str = Field(min_length=1)
    source_lines: list[int]
    target_speaker: str = Field(min_length=1)
    target_participant: str = Field(min_length=1)
    target_words: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_source_lines(self) -> "DialogueMetadata":
        if len(self.source_lines) != 2:
            raise ValueError("source_lines must contain exactly two integers")
        if self.source_lines[0] > self.source_lines[1]:
            raise ValueError("source_lines must be in ascending order")
        return self


class DialogueRow(BaseModel):
    messages: list[DialogueMessage]
    metadata: DialogueMetadata

    @model_validator(mode="after")
    def validate_row(self) -> "DialogueRow":
        if len(self.messages) != 3:
            raise ValueError("dialogue rows must contain exactly three messages")

        role_order = tuple(message.role for message in self.messages)
        if role_order != EXPECTED_ROLE_ORDER:
            raise ValueError("dialogue rows must use system, user, assistant role order")

        assistant_words = count_words(self.messages[2].content)
        if assistant_words != self.metadata.target_words:
            raise ValueError(
                f"target_words must match assistant text word count (expected {assistant_words})"
            )

        return self
