from __future__ import annotations

import re

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


def normalize_text(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\x0c", " ")
    text = text.replace("\u00e2\u20ac\u0153", '"').replace("\u00e2\u20ac\u009d", '"')
    text = text.replace("\u00e2\u20ac\u2122", "'").replace("\u00e2\u20ac\u02dc", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u00e2\u02c6\u2019", "-").replace("\u00e2\u20ac\u201c", "-")
    text = text.replace("\u00e2\u20ac\u201d", "-")
    text = text.replace("\u2013", "-").replace("\u2014", "-")
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
