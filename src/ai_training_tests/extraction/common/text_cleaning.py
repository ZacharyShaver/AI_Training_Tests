from __future__ import annotations

import re
import unicodedata

WHITESPACE_RE = re.compile(r"\s+")
BROKEN_LINE_HYPHEN_RE = re.compile(r"(?u)\b([^\W\d_]{2,})-\s+([^\W\d_]{2,})\b")
MISSING_SENTENCE_SPACE_RE = re.compile(r"([.!?])(?=[A-Z])")
SECTION_NUMBER_RE = re.compile(r"(^|\s)\d{1,3}\.\s+(?=[A-Z\"'])")
TRAILING_SECTION_NUMBER_RE = re.compile(r"\s+\d{1,3}\.\s*$")
INLINE_FOOTNOTE_RE = re.compile(r"\*\s*\*[^.]*\.", re.DOTALL)
FOOTNOTE_MARKER_RE = re.compile(r"(?<=[A-Za-z0-9),.?!;:'\"\]])\*+")
INLINE_NOTE_NUMBER_RE = re.compile(r"(?<=[A-Za-z\]\)'\"])\d{1,3}\b|(?<=[,;:.?!])\d{1,3}(?=\s+)")
BRACKET_NOTE_NUMBER_RE = re.compile(r"\[\d{1,3}\]")
WORD_RE = re.compile(r"\b[\w'-]+\b")
MOJIBAKE_TOKEN_RE = re.compile(r"\S*[\u00c2-\u00c5\u00e1\u00e2\u00f0\u0080-\u009f]\S*")

MOJIBAKE_MARKERS = (
    "Ã",
    "Â",
    "â",
    "Ä",
    "Å",
    "á",
    "ð",
    "\x80",
    "\x81",
    "\x8d",
    "\x8f",
    "\x90",
    "\x9d",
)
UNICODE_PUNCTUATION_REPLACEMENTS = {
    "\u00e2\u20ac\u0153": '"',
    "\u00e2\u20ac\u009d": '"',
    "\u00e2\u20ac\u2122": "'",
    "\u00e2\u20ac\u02dc": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2018": "'",
    "\u2019": "'",
    "\u00e2\u02c6\u2019": "-",
    "\u00e2\u20ac\u201c": "-",
    "\u00e2\u20ac\u201d": "-",
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
}

KNOWN_COMPOUND_FIXES = {
    "mindand-matter": "mind-and-matter",
    "mind-andmatter": "mind-and-matter",
    "notself": "not-self",
    "buddhanature": "buddha-nature",
    "buddhanatures": "buddha-natures",
    "superknowledge": "super-knowledge",
    "things-even": "things - even",
    "training-how": "training - how",
    "wisdomreligion": "Wisdom-Religion",
    "fellowbrothers": "fellow-brothers",
    "wellregulated": "well-regulated",
    "deeprooted": "deep-rooted",
}


def mojibake_score(text: str) -> int:
    return sum(text.count(marker) for marker in MOJIBAKE_MARKERS)


def to_possible_utf8_bytes(text: str) -> bytes | None:
    raw_bytes = bytearray()
    for char in text:
        codepoint = ord(char)
        if codepoint <= 0xFF:
            raw_bytes.append(codepoint)
            continue
        try:
            raw_bytes.extend(char.encode("cp1252"))
        except UnicodeEncodeError:
            return None
    return bytes(raw_bytes)


def repair_mojibake(text: str) -> str:
    repaired = text
    for _ in range(3):
        best = repaired
        best_score = mojibake_score(repaired)
        candidate_bytes = to_possible_utf8_bytes(repaired)
        if candidate_bytes is not None:
            try:
                candidate = candidate_bytes.decode("utf-8")
            except UnicodeDecodeError:
                candidate = None
            if candidate is not None:
                candidate = unicodedata.normalize("NFC", candidate)
                candidate_score = mojibake_score(candidate)
                if candidate_score < best_score:
                    best = candidate
                    best_score = candidate_score
        if best == repaired:
            break
        repaired = best
    return repaired


def repair_mojibake_tokens(text: str) -> str:
    return MOJIBAKE_TOKEN_RE.sub(lambda match: repair_mojibake(match.group(0)), text)


def strip_control_chars(text: str) -> str:
    return "".join(
        " " if unicodedata.category(char).startswith("C") and char not in "\t\n\r" else char
        for char in text
    )


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\x0c", " ").replace("\xa0", " ")
    text = repair_mojibake(text)
    text = repair_mojibake_tokens(text)
    text = unicodedata.normalize("NFC", text)
    for bad, fixed in UNICODE_PUNCTUATION_REPLACEMENTS.items():
        text = text.replace(bad, fixed)
    text = strip_control_chars(text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def repair_broken_hyphen(match: re.Match[str]) -> str:
    left, right = match.group(1), match.group(2)
    if right[:1].isupper():
        return f"{left}-{right}"
    return f"{left}{right}"


def clean_dataset_text(text: str) -> str:
    text = normalize_text(text)
    text = INLINE_FOOTNOTE_RE.sub("", text)
    text = FOOTNOTE_MARKER_RE.sub("", text)
    text = BRACKET_NOTE_NUMBER_RE.sub("", text)
    text = INLINE_NOTE_NUMBER_RE.sub("", text)
    text = text.replace("_", "")
    text = BROKEN_LINE_HYPHEN_RE.sub(repair_broken_hyphen, text)
    text = SECTION_NUMBER_RE.sub(r"\1", text)
    text = TRAILING_SECTION_NUMBER_RE.sub("", text)
    text = MISSING_SENTENCE_SPACE_RE.sub(r"\1 ", text)
    text = re.sub(r"\ba(pernicious)\b", r"a \1", text)
    for bad, fixed in KNOWN_COMPOUND_FIXES.items():
        text = re.sub(rf"\b{re.escape(bad)}\b", fixed, text, flags=re.IGNORECASE)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    return normalize_text(text)


def count_dataset_words(text: str) -> int:
    return len(WORD_RE.findall(clean_dataset_text(text)))


def make_record_id(
    *,
    source_name: str,
    kind: str,
    source_lines: list[int],
    target_speaker: str,
) -> str:
    source_slug = re.sub(r"[^a-z0-9]+", "-", source_name.lower()).strip("-")
    speaker_slug = re.sub(r"[^a-z0-9]+", "-", target_speaker.lower()).strip("-")
    return f"{source_slug}:{kind}:{source_lines[0]}-{source_lines[1]}:{speaker_slug}"
