from __future__ import annotations

from ai_training_tests.extraction.common.text_cleaning import clean_dataset_text

SYSTEM_PROMPTS = {
    "hermetic": (
        "You are a Hermetic philosophical interlocutor. Reply naturally, reason "
        "from the source tradition, and keep the exchange grounded rather than "
        "generic."
    ),
    "theosophy": (
        "You are a Theosophical philosophical interlocutor. Reply naturally, "
        "reason from the source tradition, and keep the exchange grounded rather "
        "than generic."
    ),
    "buddhist": (
        "You are a Buddhist philosophical interlocutor. Reply naturally, reason "
        "from the source tradition, and keep the exchange grounded rather than "
        "generic."
    ),
}


def build_messages(
    *,
    system_prompt: str,
    history: list[tuple[str, str]],
    target_participant: str,
    target_text: str,
) -> list[dict[str, str]]:
    history_text = "\n".join(
        f"{speaker}: {clean_dataset_text(text)}" for speaker, text in history
    )
    return [
        {"role": "system", "content": clean_dataset_text(system_prompt)},
        {
            "role": "user",
            "content": (
                f"Conversation so far:\n{history_text}\n\n"
                f"Write {target_participant}'s next reply."
            ),
        },
        {"role": "assistant", "content": clean_dataset_text(target_text)},
    ]


def preview_text(text: str, *, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def select_spread(rows: list[dict], count: int) -> list[dict]:
    if len(rows) <= count:
        return rows
    if count <= 1:
        return [rows[0]]

    step = (len(rows) - 1) / (count - 1)
    selected = []
    used_indexes = set()
    for slot in range(count):
        idx = round(slot * step)
        if idx not in used_indexes:
            selected.append(rows[idx])
            used_indexes.add(idx)
    return selected

