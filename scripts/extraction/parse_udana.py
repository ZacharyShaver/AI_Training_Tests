#!/usr/bin/env python3
"""Parse Udana inspired-utterance rows from extracted PDF text."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from build_pilot_dialogue_dataset import (
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    write_jsonl,
)
from preview_dialogue_examples import SYSTEM_PROMPTS, preview_text, select_spread


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "source_texts/buddhist/clean/udana.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"

BODY_START_RE = re.compile(r"^\s*1\s:\sAwakening\s*$")
BOOK_END_RE = re.compile(r"^\s*Appendices\s*$")
SUTTA_RE = re.compile(
    r"^\s*(?P<section>[1-8]:(?:10|[1-9]))\s+(?P<title>.+?Sutta\))\s*$"
)
PAGE_NUMBER_RE = re.compile(r"^\s*\d+\s*$")
EXCLAMATION_RE = re.compile(
    r"(?:Then|On)\b.*?on that occasion\s+"
    r"(?:exclaimed|spoke these verses|spoke this verse):"
    r"|Then\s+(?:at that moment\s+)?the Blessed One exclaimed"
    r"(?: this exclamation)?[:,]?"
    r"|The Blessed One said further:",
    re.IGNORECASE | re.DOTALL,
)
TARGET_END_RE = re.compile(
    r"^\s*(?:N\s*O\s*T\s*E\s*S?\s*:|N\s*O\s*T\s*E\s*S?|NOTES|"
    r"See also:|Appendices|A PPEND|[1-8]\s*:\s+\S)",
    re.IGNORECASE | re.MULTILINE,
)
INLINE_NOTE_DIGIT_RE = re.compile(r"(?<=[A-Za-z.,;:!?'\"\]\)])\d{1,3}\b")
STANDALONE_NOTE_DIGIT_RE = re.compile(r"(^|(?<=[.!?'\"\)])\s+)\d{1,3}\s+(?=[A-Z])")

PDF_CHAR_MAP = str.maketrans(
    {
        "\u203a": "a",
        "\u0131": "i",
        "\u02da": "n",
        "\u02db": "t",
        "\u02dc": "d",
        "\u00ba": "n",
        "\u00aa": "m",
        "\u00d2": "u",
        "\u02d8": "l",
        "\u00f1": "n",
        "\u00fc": "u",
        "\u2265": "T",
        "\u00a7": "S",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": " - ",
        "\u2026": "...",
    }
)


@dataclass
class SourceBlock:
    section: str
    title: str
    start_line: int
    lines: list[tuple[int, str]]


@dataclass
class UdanaItem:
    section: str
    title: str
    start_line: int
    end_line: int
    narrative: str
    utterance: str
    dialogue_turns: list["DialogueTurn"]

    @property
    def target_words(self) -> int:
        return count_dataset_words(self.utterance)

    @property
    def narrative_words(self) -> int:
        return count_dataset_words(self.narrative)


@dataclass
class DialogueTurn:
    speaker: str
    start_offset: int
    end_offset: int
    start_line: int
    end_line: int
    text: str
    context: str

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


def normalize_pdf_line(line: str) -> str:
    return line.replace("\ufeff", "").replace("\x0c", "").translate(PDF_CHAR_MAP)


def text_with_line_map(lines: list[tuple[int, str]]) -> tuple[str, list[int]]:
    parts: list[str] = []
    line_map: list[int] = []
    for line_no, line in lines:
        if PAGE_NUMBER_RE.match(line):
            continue
        if parts:
            parts.append("\n")
            line_map.append(line_no)
        value = line.rstrip()
        parts.append(value)
        line_map.extend([line_no] * len(value))
    return "".join(parts), line_map


def line_for_offset(line_map: list[int], offset: int, fallback: int) -> int:
    if not line_map:
        return fallback
    if offset < 0:
        return line_map[0]
    if offset >= len(line_map):
        return line_map[-1]
    return line_map[offset]


def parse_blocks(path: Path) -> list[SourceBlock]:
    blocks: list[SourceBlock] = []
    current: SourceBlock | None = None
    in_body = False

    for line_no, raw in enumerate(
        path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1
    ):
        line = normalize_pdf_line(raw)
        if not in_body:
            if BODY_START_RE.match(line):
                in_body = True
            continue
        if BOOK_END_RE.match(line):
            break

        match = SUTTA_RE.match(line)
        if match:
            if current is not None:
                blocks.append(current)
            current = SourceBlock(
                section=match.group("section"),
                title=apply_udana_fixes(clean_dataset_text(match.group("title"))),
                start_line=line_no,
                lines=[],
            )
            continue

        if current is not None:
            current.lines.append((line_no, line))

    if current is not None:
        blocks.append(current)
    return blocks


def clean_narrative(text: str) -> str:
    text = INLINE_NOTE_DIGIT_RE.sub("", text)
    text = STANDALONE_NOTE_DIGIT_RE.sub(r"\1", text)
    text = clean_dataset_text(text)
    text = text.replace("clinging/ sustenance", "clinging/sustenance")
    text = apply_udana_fixes(text)
    return clean_dataset_text(text)


def apply_udana_fixes(text: str) -> str:
    replacements = {
        "Dhammatalk": "Dhamma-talk",
        "Dhamma talk": "Dhamma-talk",
        "wellestablished": "well-established",
        "welltaught": "well-taught",
        "wellpracticed": "well-practiced",
        "well practiced": "well-practiced",
        "selfawakened": "self-awakened",
        "Barkcloth": "Bark-cloth",
        "Koliyanson": "Koliyan-son",
        "dovefooted": "dove-footed",
        "Squirrels' refuge": "Squirrels' Sanctuary",
        "Now at on that occasion": "Now on that occasion",
        "wellundertaken": "well-undertaken",
        "wellexpounded": "well-expounded",
        "ManySon": "Many-Son",
        "once-returners": "once-returners",
        "oncereturners": "once-returners",
        "nonreturners": "non-returners",
        "non-return": "non-return",
        "finanda": "Ananda",
        "fiyusama": "Ayusama",
    }
    for bad, fixed in replacements.items():
        text = re.sub(rf"\b{re.escape(bad)}\b", fixed, text)
    return text


def clean_dialogue_text(text: str) -> str:
    text = INLINE_NOTE_DIGIT_RE.sub("", text)
    text = STANDALONE_NOTE_DIGIT_RE.sub(r"\1", text)
    text = clean_dataset_text(text)
    text = apply_udana_fixes(text)
    return clean_dataset_text(text)


def clean_utterance(text: str) -> str:
    lines: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or PAGE_NUMBER_RE.match(line):
            continue
        line = re.sub(r"^\d{1,2}\s+", "", line)
        line = INLINE_NOTE_DIGIT_RE.sub("", line)
        line = STANDALONE_NOTE_DIGIT_RE.sub(r"\1", line)
        line = clean_dataset_text(line)
        line = apply_udana_fixes(line)
        if line:
            lines.append(line)
    return "\n".join(lines)


def build_udana_messages(*, narrator_text: str, target_text: str) -> list[dict[str, str]]:
    narrator_text = clean_dataset_text(narrator_text)
    return [
        {"role": "system", "content": clean_dataset_text(SYSTEM_PROMPTS["buddhist"])},
        {
            "role": "user",
            "content": (
                "Conversation so far:\n"
                f"Participant A (Narrator): {narrator_text}\n\n"
                "Write Participant B's next reply."
            ),
        },
        {"role": "assistant", "content": target_text.strip()},
    ]


SPEAKER_ALIASES = {
    "blessed one": "Blessed One",
    "the blessed one": "Blessed One",
    "[the blessed one]": "Blessed One",
    "bahiya": "Bahiya",
    "bahiya of the bark-cloth": "Bahiya",
    "a certain devata": "Devata",
    "certain devata": "Devata",
    "devata": "Devata",
    "a devata": "Devata",
    "the devata": "Devata",
    "monks": "Monks",
    "the monks": "Monks",
    "a large number of monks": "Monks",
    "a certain monk": "Monk",
    "the monk": "Monk",
    "ven. meghiya": "Ven. Meghiya",
    "meghiya": "Ven. Meghiya",
    "ven. nanda": "Ven. Nanda",
    "nanda": "Ven. Nanda",
    "ven. ananda": "Ven. Ananda",
    "ven. finanda": "Ven. Ananda",
    "ananda": "Ven. Ananda",
    "finanda": "Ven. Ananda",
    "ven. yasoja": "Ven. Yasoja",
    "yasoja": "Ven. Yasoja",
    "ven. pilindavaccha": "Ven. Pilindavaccha",
    "pilindavaccha": "Ven. Pilindavaccha",
    "ven. sariputta": "Ven. Sariputta",
    "sariputta": "Ven. Sariputta",
    "ven. moggallana": "Ven. Maha Moggallana",
    "moggallana": "Ven. Maha Moggallana",
    "ven. maha moggallana": "Ven. Maha Moggallana",
    "maha moggallana": "Ven. Maha Moggallana",
    "ven. maha kaccayana": "Ven. Maha Kaccayana",
    "maha kaccayana": "Ven. Maha Kaccayana",
    "sona kotikanna": "Sona Kotikanna",
    "ven. nagasamala": "Ven. Nagasamala",
    "nagasamala": "Ven. Nagasamala",
    "ven. bhaddiya": "Ven. Bhaddiya",
    "bhaddiya": "Ven. Bhaddiya",
    "ven. dabba mallaputta": "Ven. Dabba Mallaputta",
    "dabba mallaputta": "Ven. Dabba Mallaputta",
    "suppavasa": "Suppavasa",
    "koliyan-son": "Koliyan-son",
    "the koliyan-son": "Koliyan-son",
    "young master": "Young Master",
    "the young master": "Young Master",
    "visakha": "Visakha",
    "queen mallika": "Queen Mallika",
    "mallika": "Queen Mallika",
    "king pasenadi": "King Pasenadi",
    "pasenadi": "King Pasenadi",
    "the lay follower": "Lay follower",
    "lay follower": "Lay follower",
    "wanderer": "Wanderer",
    "the wanderer": "Wanderer",
    "brahman": "Brahman",
    "the brahman": "Brahman",
    "the boys": "Boys",
    "boys": "Boys",
    "cunda": "Cunda",
    "cundaka": "Ven. Cundaka",
    "ven. cundaka": "Ven. Cundaka",
    "householders": "Householders",
    "the householders": "Householders",
    "mara": "Mara",
    "mara the evil one": "Mara",
    "the yakkha": "Yakkha",
    "the first yakkha": "Yakkha",
    "the second yakkha": "Yakkha",
}

NON_BLESSED_SPEAKER_PATTERN = (
    r"Ven\. (?:Meghiya|Nanda|Ananda|finanda|Yasoja|Pilindavaccha|"
    r"Maha Moggallana|Moggallana|Sariputta|Maha Kaccayana|Nagasamala|"
    r"Bhaddiya|Dabba Mallaputta)|"
    r"Bahiya(?: of the Bark-cloth)?|a devata|the devata|devata|"
    r"a large number of monks|the monks|a certain monk|the monk|monks|"
    r"Suppavasa|the Koliyan-son|Koliyan-son|the young master|young master|"
    r"Visakha|Queen Mallika|King Pasenadi|"
    r"the lay follower|lay follower|the wanderer|wanderer|the brahman|brahman|"
    r"the boys|boys|Cunda|Ven\. Cundaka|Cundaka|householders|the householders|"
    r"Mara(?: the Evil One)?|the first yakkha|the second yakkha|the yakkha|"
    r"Sona Kotikanna|Nagasamala|Ananda|finanda|Nanda|Meghiya"
)
SPEECH_VERB_RE = r"(?:said|responded|replied|addressed|asked|told|exclaimed)"
NON_BLESSED_PREFIX_RE = re.compile(
    rf"(?P<speaker>{NON_BLESSED_SPEAKER_PATTERN})[^\"\n]{{0,260}}?\b{SPEECH_VERB_RE}\b"
    r"[^\"\n]{0,140}?[:,]\s*$",
    re.IGNORECASE,
)
BLESSED_PREFIX_RE = re.compile(
    r"(?:"
    r"\[The Blessed One said:\]|"
    r"(?:the )?Blessed One\s+"
    r"(?:said|responded|replied|addressed|asked|told|exclaimed)\b[^\"\n]{0,160}?[:,]|"
    r"(?:Seated,\s*)?he addressed the monks:|"
    r"There he addressed the monks,|"
    r"the One Well-Gone, the Teacher, said further:"
    r")\s*$",
    re.IGNORECASE,
)
SUFFIX_SPEAKER_RE = re.compile(
    rf"^\s*,?\s*(?:When this was said,\s*)?(?P<speaker>{NON_BLESSED_SPEAKER_PATTERN})\s+{SPEECH_VERB_RE}\b",
    re.IGNORECASE,
)


def normalize_speaker_phrase(phrase: str) -> str | None:
    phrase = clean_dialogue_text(phrase).strip(" ,.:;[]()")
    phrase = re.sub(
        r"^(?:A second time|A third time|When this was said|Then|Now),?\s+",
        "",
        phrase,
        flags=re.IGNORECASE,
    )
    lowered = re.sub(r"\s+", " ", phrase.lower())
    for key, value in sorted(
        SPEAKER_ALIASES.items(), key=lambda item: len(item[0]), reverse=True
    ):
        if re.search(rf"(?<![a-z]){re.escape(key)}(?![a-z])", lowered):
            return value
    return None


def quote_spans(text: str, *, end_offset: int) -> list[tuple[int, int, str]]:
    spans: list[tuple[int, int, str]] = []
    start: int | None = None
    nested_depth = 0
    for idx, char in enumerate(text[:end_offset]):
        if char != '"':
            continue
        if start is None:
            start = idx
            nested_depth = 0
        elif is_continuation_quote(text, idx):
            continue
        elif is_nested_open_quote(text, idx):
            nested_depth += 1
            continue
        elif nested_depth:
            nested_depth -= 1
            continue
        else:
            quote = re.sub(r"\n\s*\"", "\n", text[start + 1 : idx]).strip()
            if quote:
                spans.append((start, idx, quote))
            start = None
            nested_depth = 0
    return spans


def is_continuation_quote(text: str, idx: int) -> bool:
    prefix = text[:idx]
    line_start = prefix.rfind("\n") + 1
    if prefix[line_start:idx].strip():
        return False
    next_char = text[idx + 1 : idx + 2]
    return bool(next_char and (next_char.isupper() or next_char == "["))


def is_nested_open_quote(text: str, idx: int) -> bool:
    prefix = text[:idx].rstrip()
    suffix = text[idx + 1 :].lstrip()
    if not prefix or not suffix:
        return False
    if re.match(
        r"^(?:Ven\.|the Blessed One|the monk|the monks|a certain monk|"
        r"a devata|the devata|Bahiya|Cunda|Suppavasa|Visakha|Queen|King|"
        r"Sakka|Mara|Responding\b|to\b)",
        suffix,
        re.IGNORECASE,
    ):
        return False
    return prefix[-1] in {",", ":", "(", "["} and (
        suffix[0].isupper() or suffix[0] in {"[", "("}
    )


def infer_blessed_pronoun_speaker(prefix: str) -> bool:
    tail = clean_dialogue_text(prefix[-700:])
    patterns = [
        r"\bBlessed One\s+(?:sat|stood|lay|went|drank|endured|adjusted|addressed|said|told|responded|replied)\b.{0,420}\b(?:Seated,\s*)?(?:Then\s+)?he\s+(?:said|addressed|told|asked)\s+(?:to\s+)?(?:Ven\.[^.?!\",]{0,80}|the monks|him|her|them)[^.?!\"]{0,120}[:,]\s*$",
        r"\bBlessed One,\s+(?:lying|seated|standing|having|after)\b.{0,420}\b(?:the Teacher|he)\s+(?:said|addressed|told|asked)\s+(?:to\s+)?(?:Ven\.[^.?!\",]{0,80}|the monks|him|her|them)[^.?!\"]{0,120}[:,]\s*$",
        r"\bBlessed One,\s+(?:going|having|after)\b.{0,420}\b(?:said|addressed|told|asked)\s+(?:to\s+)?(?:Ven\.[^.?!\",]{0,80}|the monks|him|her|them)[^.?!\"]{0,120}[:,]\s*$",
    ]
    return any(re.search(pattern, tail, re.IGNORECASE) for pattern in patterns)


def infer_non_blessed_pronoun_speaker(prefix: str) -> str | None:
    tail = clean_dialogue_text(prefix[-700:])
    pronoun_match = re.search(
        r"\b(?:he|she|they)\s+(?:said|told|replied|responded)\s+to\s+the Blessed One[:,]\s*$",
        tail,
        re.IGNORECASE,
    )
    if pronoun_match:
        speaker_candidates = [
            speaker
            for speaker_match in re.finditer(
                NON_BLESSED_SPEAKER_PATTERN,
                tail[: pronoun_match.start()],
                re.IGNORECASE,
            )
            if (speaker := normalize_speaker_phrase(speaker_match.group(0)))
        ]
        if speaker_candidates:
            return speaker_candidates[-1]
    return None


def infer_quote_speaker(
    text: str,
    *,
    start: int,
    end: int,
    active_pair: list[str],
    previous_turn: DialogueTurn | None,
) -> str | None:
    prefix = text[max(0, start - 700) : start]
    suffix = text[end + 1 : end + 220]

    if re.search(
        r"(?:thought occurred|knowledge arose|thinking|awareness):\s*$",
        prefix,
        re.IGNORECASE,
    ):
        return None

    if BLESSED_PREFIX_RE.search(prefix) or infer_blessed_pronoun_speaker(prefix):
        return "Blessed One"

    for match in NON_BLESSED_PREFIX_RE.finditer(prefix):
        before_match = prefix[max(0, match.start() - 12) : match.start()].lower()
        if re.search(r"\b(?:to|for|of)\s+$", before_match):
            continue
        if speaker := normalize_speaker_phrase(match.group("speaker")):
            return speaker

    match = SUFFIX_SPEAKER_RE.match(suffix)
    if match and (speaker := normalize_speaker_phrase(match.group("speaker"))):
        return speaker

    if speaker := infer_non_blessed_pronoun_speaker(prefix):
        return speaker

    if re.search(r"\b(?:he|she|they)\s+said to the Blessed One,\s*$", prefix, re.IGNORECASE):
        for speaker in reversed(active_pair):
            if speaker != "Blessed One":
                return speaker

    quote = text[start + 1 : end].strip()
    if previous_turn and previous_turn.speaker != "Blessed One" and "Blessed One" in active_pair:
        if re.match(
            r"(?:Then,|As you are talking|Monks,|Cunda,|Visakha,|Meghiya,|Nanda,|Bahiya,|"
            r"Relax,|Please,|This is not|Is it true|In the same way|It isn't)",
            quote,
        ):
            return "Blessed One"

    return None


def participant_for_udana_speaker(speaker: str) -> str:
    return "Participant B" if speaker == "Blessed One" else "Participant A"


def parse_dialogue_turns(text: str, line_map: list[int], *, end_offset: int) -> list[DialogueTurn]:
    turns: list[DialogueTurn] = []
    active_pair: list[str] = []
    previous_quote_end = 0

    for start, end, raw_quote in quote_spans(text, end_offset=end_offset):
        speaker = infer_quote_speaker(
            text,
            start=start,
            end=end,
            active_pair=active_pair,
            previous_turn=turns[-1] if turns else None,
        )
        if speaker is None:
            continue

        quote = clean_dialogue_text(raw_quote)
        if not quote:
            continue

        turn = DialogueTurn(
            speaker=speaker,
            start_offset=start,
            end_offset=end,
            start_line=line_for_offset(line_map, start, 0),
            end_line=line_for_offset(line_map, end, 0),
            text=quote,
            context=clean_narrative(text[previous_quote_end:start]),
        )
        turns.append(turn)
        previous_quote_end = end + 1

        if not active_pair or speaker not in active_pair:
            active_pair.append(speaker)
            active_pair = active_pair[-2:]

    return turns


def build_udana_messages_from_history(
    *,
    history: list[tuple[str, str]],
    target_text: str,
) -> list[dict[str, str]]:
    history_text = "\n".join(
        f"{speaker}: {clean_dialogue_text(text)}" for speaker, text in history
    )
    return [
        {"role": "system", "content": clean_dataset_text(SYSTEM_PROMPTS["buddhist"])},
        {
            "role": "user",
            "content": (
                f"Conversation so far:\n{history_text}\n\n"
                "Write Participant B's next reply."
            ),
        },
        {"role": "assistant", "content": clean_dialogue_text(target_text)},
    ]


def item_from_block(block: SourceBlock) -> UdanaItem | None:
    text, line_map = text_with_line_map(block.lines)
    formula_matches = list(EXCLAMATION_RE.finditer(text))
    if not formula_matches:
        return None

    formula = formula_matches[-1]
    target_start = formula.end()
    target_tail = text[target_start:]
    target_end_match = TARGET_END_RE.search(target_tail)
    target_end = (
        target_start + target_end_match.start()
        if target_end_match is not None
        else len(text)
    )
    while target_end > target_start and text[target_end - 1].isspace():
        target_end -= 1

    narrative = clean_narrative(text[:target_start])
    utterance = clean_utterance(text[target_start:target_end])
    dialogue_turns = parse_dialogue_turns(text, line_map, end_offset=target_start)
    if not narrative or not utterance:
        return None

    return UdanaItem(
        section=block.section,
        title=block.title,
        start_line=block.start_line,
        end_line=line_for_offset(line_map, target_end - 1, block.start_line),
        narrative=narrative,
        utterance=utterance,
        dialogue_turns=dialogue_turns,
    )


def parse_items(path: Path) -> list[UdanaItem]:
    return [item for block in parse_blocks(path) if (item := item_from_block(block))]


def item_to_row(
    item: UdanaItem,
    *,
    min_target_words: int,
    max_target_words: int,
    max_narrative_words: int,
) -> dict | None:
    if item.target_words < min_target_words or item.target_words > max_target_words:
        return None
    if item.narrative_words > max_narrative_words:
        return None

    source_name = "udana.txt"
    source_lines = [item.start_line, item.end_line]
    target_speaker = "Blessed One"
    target_participant = "Participant B"
    kind = "udana_blessed_one_exclamation"
    section_slug = item.section.replace(":", "-")
    narrator_text = item.narrative

    return {
        "messages": build_udana_messages(
            narrator_text=narrator_text,
            target_text=item.utterance,
        ),
        "metadata": {
            "record_id": make_record_id(
                source_name=source_name,
                kind=f"{kind}_{section_slug}",
                source_lines=source_lines,
                target_speaker=target_speaker,
            ),
            "kind": kind,
            "source": "Udana",
            "source_file": source_name,
            "source_lines": source_lines,
            "target_speaker": target_speaker,
            "target_participant": target_participant,
            "target_words": item.target_words,
            "narrative_words": item.narrative_words,
            "section": item.section,
            "title": item.title,
        },
    }


def turn_is_history_candidate(turn: DialogueTurn) -> bool:
    text = clean_dialogue_text(turn.text)
    if text.startswith(("As you say", "The Teacher calls you")):
        return False
    if turn.word_count < 6:
        return bool(
            turn.speaker != "Blessed One"
            and re.search(r"\b(?:yes|no),?\s+lord\b", text, re.IGNORECASE)
        )
    return True


def narrator_context_is_clean(text: str, *, max_context_words: int) -> bool:
    context_words = count_dataset_words(text)
    if not (8 <= context_words <= max_context_words):
        return False
    stripped = text.strip()
    if not stripped:
        return False
    if stripped[0].islower():
        return False
    return True


def direct_turn_to_row(
    item: UdanaItem,
    *,
    turn_index: int,
    history_turns: int,
    max_context_words: int,
    min_target_words: int,
    max_target_words: int,
) -> dict | None:
    target = item.dialogue_turns[turn_index]
    if target.speaker != "Blessed One":
        return None
    if target.word_count < min_target_words or target.word_count > max_target_words:
        return None

    prior_turns: list[DialogueTurn] = []
    seen_history: set[str] = set()
    for turn in item.dialogue_turns[max(0, turn_index - history_turns) : turn_index]:
        if not turn_is_history_candidate(turn):
            continue
        history_key = clean_dialogue_text(turn.text).lower()
        if history_key in seen_history:
            continue
        seen_history.add(history_key)
        prior_turns.append(turn)
    target_key = clean_dialogue_text(target.text).lower()
    if target_key in seen_history:
        return None
    has_non_blessed_history = any(turn.speaker != "Blessed One" for turn in prior_turns)

    history: list[tuple[str, str]] = []
    context_words = count_dataset_words(target.context)
    if target.context and narrator_context_is_clean(
        target.context, max_context_words=max_context_words
    ):
        history.append(("Participant A (Narrator)", target.context))

    for turn in prior_turns:
        participant = participant_for_udana_speaker(turn.speaker)
        history.append((f"{participant} ({turn.speaker})", turn.text))

    if not history:
        return None
    if not has_non_blessed_history and not any("Narrator" in speaker for speaker, _ in history):
        return None
    if not any("Narrator" in speaker for speaker, _ in history):
        non_blessed_history_words = sum(
            turn.word_count for turn in prior_turns if turn.speaker != "Blessed One"
        )
        if non_blessed_history_words < 8:
            return None

    source_name = "udana.txt"
    source_lines = [target.start_line, target.end_line]
    kind = "udana_blessed_one_direct_reply"
    section_slug = item.section.replace(":", "-")
    return {
        "messages": build_udana_messages_from_history(
            history=history,
            target_text=target.text,
        ),
        "metadata": {
            "record_id": make_record_id(
                source_name=source_name,
                kind=f"{kind}_{section_slug}_{turn_index}",
                source_lines=source_lines,
                target_speaker=target.speaker,
            ),
            "kind": kind,
            "source": "Udana",
            "source_file": source_name,
            "source_lines": source_lines,
            "target_speaker": target.speaker,
            "target_participant": "Participant B",
            "target_words": target.word_count,
            "context_words": context_words,
            "section": item.section,
            "title": item.title,
        },
    }


def build_direct_rows(
    items: list[UdanaItem],
    *,
    history_turns: int,
    max_context_words: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    rows: list[dict] = []
    seen_targets: set[str] = set()
    for item in items:
        for turn_index, turn in enumerate(item.dialogue_turns):
            row = direct_turn_to_row(
                item,
                turn_index=turn_index,
                history_turns=history_turns,
                max_context_words=max_context_words,
                min_target_words=min_target_words,
                max_target_words=max_target_words,
            )
            if row is None:
                continue

            target_key = clean_dialogue_text(turn.text).lower()
            if target_key in seen_targets:
                continue
            seen_targets.add(target_key)
            rows.append(row)
    return rows


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    detail_lines = [
        f"- Record ID: `{metadata['record_id']}`",
        f"- Kind: `{metadata['kind']}`",
        f"- Section: `{metadata['section']} {metadata['title']}`",
        f"- Lines: `{metadata['source_file']}:{metadata['source_lines'][0]}-{metadata['source_lines'][1]}`",
        f"- Target: `{metadata['target_participant']} ({metadata['target_speaker']})`",
        f"- Target words: `{metadata['target_words']}`",
    ]
    if "narrative_words" in metadata:
        detail_lines.append(f"- Narrative words: `{metadata['narrative_words']}`")
    if "context_words" in metadata:
        detail_lines.append(f"- Context words: `{metadata['context_words']}`")

    return "\n".join(
        [
            f"## Review Example {index}: {metadata['source']}",
            "",
            *detail_lines,
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
    parser = argparse.ArgumentParser(description="Parse Udana review rows.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="udana_dialogue")
    parser.add_argument("--min-target-words", type=int, default=12)
    parser.add_argument("--max-target-words", type=int, default=260)
    parser.add_argument("--max-narrative-words", type=int, default=2500)
    parser.add_argument("--final-only", action="store_true")
    parser.add_argument("--direct-history-turns", type=int, default=3)
    parser.add_argument("--direct-min-target-words", type=int, default=12)
    parser.add_argument("--direct-max-target-words", type=int, default=700)
    parser.add_argument("--direct-max-context-words", type=int, default=260)
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    args = parser.parse_args()

    items = parse_items(args.source.expanduser().resolve())
    exclamation_rows = [
        row
        for item in items
        if (
            row := item_to_row(
                item,
                min_target_words=args.min_target_words,
                max_target_words=args.max_target_words,
                max_narrative_words=args.max_narrative_words,
            )
        )
    ]
    direct_rows = (
        []
        if args.final_only
        else build_direct_rows(
            items,
            history_turns=args.direct_history_turns,
            max_context_words=args.direct_max_context_words,
            min_target_words=args.direct_min_target_words,
            max_target_words=args.direct_max_target_words,
        )
    )
    rows = [*exclamation_rows, *direct_rows]

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    direct_review_path = output_dir / f"{args.dataset_name}_direct_review_sample.md"
    write_jsonl(jsonl_path, rows)

    sample = select_spread(rows, args.sample_count)
    kind_counts = Counter(row["metadata"]["kind"] for row in rows)
    kind_count_lines = [
        f"- `{kind}`: `{count}`" for kind, count in sorted(kind_counts.items())
    ]
    review_path.write_text(
        "\n".join(
            [
                "# Udana Review Sample",
                "",
                f"Items parsed: `{len(items)}`",
                f"Rows parsed: `{len(rows)}`",
                "",
                "Rows by kind:",
                "",
                *kind_count_lines,
                "",
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
    direct_sample = select_spread(direct_rows, len(direct_rows))
    direct_review_path.write_text(
        "\n".join(
            [
                "# Udana Direct Reply Review Sample",
                "",
                f"Direct rows parsed: `{len(direct_rows)}`",
                "",
                *[
                    row_to_markdown(row, idx, preview_chars=args.preview_chars)
                    for idx, row in enumerate(direct_sample, 1)
                ],
            ]
        ),
        encoding="utf-8",
    )

    print(f"Items parsed: {len(items)}")
    print(f"Rows written: {len(rows)}")
    for kind, count in sorted(kind_counts.items()):
        print(f"{kind}: {count}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")
    print(f"Direct review: {direct_review_path}")


if __name__ == "__main__":
    main()
