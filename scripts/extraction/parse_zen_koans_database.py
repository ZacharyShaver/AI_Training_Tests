#!/usr/bin/env python3
"""Download and parse rows from the Cincinato Zen Koans Database."""

from __future__ import annotations

import argparse
import html
import json
import re
import urllib.parse
import urllib.request
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

from build_pilot_dialogue_dataset import (
    build_messages,
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    write_jsonl,
)
from preview_dialogue_examples import SYSTEM_PROMPTS, preview_text, select_spread


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIST = REPO_ROOT / "source_texts/buddhist/raw/zen_koans_database_list_en.html"
DEFAULT_RAW_DIR = REPO_ROOT / "source_texts/buddhist/raw/zen_koans_database_pages"
DEFAULT_CLEAN_JSON = REPO_ROOT / "source_texts/buddhist/clean/zen_koans_database.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"
BASE_URL = "https://cincinato.org/koans/"

WHITESPACE_RE = re.compile(r"\s+")
BOILERPLATE_RE = re.compile(r"English koan list|Random Koan", re.IGNORECASE)
QUOTE_RE = re.compile(r'"(?P<quote>[^"]+)"')
SPEECH_VERBS = (
    "called out|said|asked|replied|answered|responded|told|called|continued|"
    "remarked|hinted|observed|explained|concluded|inquired|exclaimed|"
    "complained|commented|added|cried|shouted|yelled|mused|protested|"
    "scolded|demanded|advised|insisted|suggested|declared|ordered|whispered"
)
PROPER_SPEAKER_PHRASE = (
    r"[A-Z][A-Za-z'-]+(?:\s+(?:no|of|the)\s+[A-Z][A-Za-z'-]+|"
    r"\s+[A-Z][A-Za-z'-]+){0,3}"
)
ROLE_SPEAKER_PHRASE = (
    r"(?:the|a|an|his|her)?\s*"
    r"(?:old|young|elder|younger|blind|rich|certain|other|wandering|university|"
    r"self-centered|boisterous)?\s*"
    r"(?:farmer|physician|doctor|friend|master|teacher|student|questioner|"
    r"priest|stranger|cook|carpenter|servant|customer|butcher|girl|pupil|"
    r"monk|nun|woman|man|thief|intruder|fellow|beggar|nephew|brother|"
    r"traveler|emperor|attendant|soldier|warrior|samurai|lord|merchant|"
    r"judge|policeman|police|people|disciple|disciples|professor|visitor|"
    r"geisha|artist|patron|child|boy|youth|listener|officer|wife|mother|"
    r"father|son|daughter|host|guest|preacher|swordsman|wrestler|adherent|"
    r"neighbor|other)"
)
SPEAKER_PHRASE = (
    rf"{PROPER_SPEAKER_PHRASE}|{ROLE_SPEAKER_PHRASE}|"
    r"first|second|third|fourth|he|she|one"
)
BEFORE_WHO_RE = re.compile(
    rf"(?<![A-Za-z])(?P<speaker>{PROPER_SPEAKER_PHRASE}),\s+"
    rf"who\s+(?:{SPEECH_VERBS})(?:\s+[^\".?!:]{{0,80}})?[:]\s*$"
)
BEFORE_SPEAKER_RE = re.compile(
    rf"(?<![A-Za-z])(?P<speaker>{SPEAKER_PHRASE})\s+"
    rf"(?:{SPEECH_VERBS})(?:\s+[^\".?!:]{{0,80}})?[:]\s*$"
)
BEFORE_ROLE_ACTION_SPEECH_RE = re.compile(
    rf"(?<![A-Za-z])(?P<speaker>{ROLE_SPEAKER_PHRASE})\s+"
    rf"(?:(?![\".?!:]).{{0,80}}\s+)?"
    rf"(?:{SPEECH_VERBS})(?:\s+[^\".?!:]{{0,80}})?[:]\s*$"
)
BEFORE_PRONOUN_ACTION_SPEECH_RE = re.compile(
    rf"(?<![A-Za-z])(?P<speaker>he|she)\s+"
    rf"(?:(?![\".?!:]).{{0,80}}\s+)?"
    rf"(?:{SPEECH_VERBS})(?:\s+[^\".?!:]{{0,80}})?[:]\s*$"
)
AFTER_VERB_SPEAKER_RE = re.compile(
    rf"^\s*,?\s*(?:{SPEECH_VERBS})\s+"
    rf"(?<![A-Za-z])(?P<speaker>{SPEAKER_PHRASE})"
    rf"(?:\s+[^\".?!]{{0,80}})?[.?!]?",
)
AFTER_SPEAKER_VERB_RE = re.compile(
    rf"^\s*,?\s*(?<![A-Za-z])(?P<speaker>{SPEAKER_PHRASE})\s+"
    rf"(?:{SPEECH_VERBS})(?:\s+[^\".?!]{{0,80}})?[.?!,]?"
)
BEFORE_SENTENCE_SPEAKER_RE = re.compile(
    rf"(?<![A-Za-z])(?P<speaker>{SPEAKER_PHRASE})\s+"
    rf"(?:{SPEECH_VERBS})(?:\s+[^\".?!:]{{0,80}})?[.?!]\s*$"
)
BEFORE_ACTION_SPEAKER_RE = re.compile(
    rf"(?<![A-Za-z])(?P<speaker>{PROPER_SPEAKER_PHRASE})\s+"
    r"(?:smiled|laughed|nodded|patted|bowed|mused|showed|wrote|sat|stood|"
    r"turned|opened|looked|produced)\b[^.?!]{0,120}[.?!]\s*$"
)
ATTRIBUTION_TAIL_RE = re.compile(
    rf"^\s*,?\s*(?:(?<![A-Za-z])(?:{SPEAKER_PHRASE})\s+(?:{SPEECH_VERBS})|"
    rf"(?:{SPEECH_VERBS})\s+(?<![A-Za-z])(?:{SPEAKER_PHRASE}))"
    rf"(?:\s+[^\".?!]{{0,80}})?[.?!,]?\s*"
)
NARRATIVE_CAPITAL_WORDS = {
    "A",
    "An",
    "And",
    "At",
    "Before",
    "But",
    "During",
    "Each",
    "Everything",
    "Every",
    "For",
    "Give",
    "In",
    "Look",
    "Now",
    "Once",
    "One",
    "So",
    "That",
    "The",
    "Then",
    "They",
    "This",
    "You",
    "When",
    "While",
    "With",
}
UNRELIABLE_DIALOGUE_SPEAKERS = {"Another", "Other"}
NON_PERSON_PROPER_SPEAKERS = {
    "Buddhahood",
    "Buddhism",
    "Mu",
    "No-Thing",
    "St",
    "Zen",
}
ROLE_ADJECTIVES_RE = re.compile(
    r"^(?:old|young|elder|younger|blind|rich|certain|other|wandering|"
    r"university|self-centered|boisterous)\s+",
    re.IGNORECASE,
)


@dataclass
class KoanLink:
    slug: str
    title: str
    href: str


@dataclass
class KoanStory:
    slug: str
    title: str
    paragraphs: list[str]
    source_file: str


@dataclass
class RenderedTurn:
    speaker: str
    text: str


class KoanListParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[KoanLink] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attrs_dict = dict(attrs)
        href = attrs_dict.get("href") or ""
        if href.startswith("showone_en.php?koan="):
            self._current_href = href
            self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._current_href:
            return
        title = clean_text(" ".join(self._current_text))
        parsed = urllib.parse.urlparse(self._current_href)
        params = urllib.parse.parse_qs(parsed.query)
        slug = params.get("koan", [""])[0]
        if slug and title:
            self.links.append(KoanLink(slug=slug, title=title, href=self._current_href))
        self._current_href = None
        self._current_text = []


class KoanPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_content = False
        self.in_sidebar = False
        self.in_h2 = False
        self.in_p = False
        self.title_parts: list[str] = []
        self.current_p: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag.lower() == "div" and attrs_dict.get("class") == "content":
            self.in_content = True
        if tag.lower() == "div" and attrs_dict.get("id") == "sidebar":
            self.in_sidebar = True
            self.in_content = False
        if not self.in_content or self.in_sidebar:
            return
        if tag.lower() == "h2":
            self.in_h2 = True
        elif tag.lower() == "p":
            self.in_p = True
            self.current_p = []

    def handle_data(self, data: str) -> None:
        if not self.in_content or self.in_sidebar:
            return
        if self.in_h2:
            self.title_parts.append(data)
        elif self.in_p:
            self.current_p.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "h2":
            self.in_h2 = False
        elif tag == "p" and self.in_p:
            text = clean_text(" ".join(self.current_p))
            if text and not BOILERPLATE_RE.search(text) and text != "&nbsp;":
                self.paragraphs.append(text)
            self.current_p = []
            self.in_p = False
        elif tag == "div" and self.in_content:
            self.in_content = False

    @property
    def title(self) -> str:
        return clean_text(" ".join(self.title_parts))


class FragmentTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    @property
    def text(self) -> str:
        return clean_text(" ".join(self.parts))


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2013", "-").replace("\u2014", " - ")
    text = WHITESPACE_RE.sub(" ", text)
    text = clean_dataset_text(text.strip())
    replacements = {
        "begining": "beginning",
        "phsisician": "physician",
        "Liek": "Like",
        "th first": "the first",
        "Uzemu": "Umezu",
    }
    for bad, fixed in replacements.items():
        text = re.sub(rf"\b{re.escape(bad)}\b", fixed, text)
    text = text.replace('Why should I?"', '"Why should I?"')
    text = text.replace('""Why should I?"', '"Why should I?"')
    return text


def read_list_links(path: Path) -> list[KoanLink]:
    parser = KoanListParser()
    parser.feed(path.read_text(encoding="iso-8859-1", errors="ignore"))
    seen: set[str] = set()
    links: list[KoanLink] = []
    for link in parser.links:
        if link.slug in seen:
            continue
        seen.add(link.slug)
        links.append(link)
    return links


def download_page(link: KoanLink, raw_dir: Path, *, refresh: bool) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{Path(link.slug).stem}.html"
    if path.exists() and not refresh:
        return path
    url = urllib.parse.urljoin(BASE_URL, link.href)
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        content = response.read()
    path.write_bytes(content)
    return path


def cached_page_path(link: KoanLink, raw_dir: Path) -> Path:
    return raw_dir / f"{Path(link.slug).stem}.html"


def parse_page(path: Path, link: KoanLink) -> KoanStory | None:
    text = path.read_text(encoding="iso-8859-1", errors="ignore")
    content_match = re.search(
        r'<div class="content">\s*(?P<body>.*?)\s*</div>\s*</div>\s*<div id="sidebar"',
        text,
        re.IGNORECASE | re.DOTALL,
    )
    content = content_match.group("body") if content_match else text

    title_match = re.search(r"<h2>(?P<title>.*?)</h2>", content, re.IGNORECASE | re.DOTALL)
    title = clean_text(title_match.group("title")) if title_match else link.title

    content = re.sub(r"<h2>.*?</h2>", "", content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r"<center>.*?</center>", "", content, flags=re.IGNORECASE | re.DOTALL)
    raw_parts = re.split(r"<p[^>]*>", content, flags=re.IGNORECASE)
    paragraphs: list[str] = []
    for raw_part in raw_parts:
        fragment_parser = FragmentTextParser()
        fragment_parser.feed(raw_part)
        paragraph = fragment_parser.text
        if paragraph and paragraph != "&nbsp;" and not BOILERPLATE_RE.search(paragraph):
            paragraphs.append(paragraph)

    paragraphs = [p for p in paragraphs if p and p != title]
    if len(paragraphs) < 2:
        return None
    return KoanStory(
        slug=link.slug,
        title=title,
        paragraphs=paragraphs,
        source_file=path.name,
    )


def normalize_speaker(speaker: str | None, *, previous_named: str | None = None) -> str:
    if not speaker:
        return "Quoted speaker"
    speaker = clean_text(speaker).strip(" ,.:;\"'")
    original_lower = speaker.lower()
    possessive_role = original_lower.startswith(("his ", "her "))
    speaker = re.sub(r"^(?:the|a|an|his|her)\s+", "", speaker, flags=re.IGNORECASE)
    speaker = ROLE_ADJECTIVES_RE.sub("", speaker)
    speaker = re.sub(r"\s+", " ", speaker)
    lower = speaker.lower()
    ordinal_map = {
        "first": "First pupil",
        "second": "Second pupil",
        "third": "Third pupil",
        "fourth": "Fourth pupil",
    }
    if lower in ordinal_map:
        return ordinal_map[lower]
    if lower in {"he", "she"} and previous_named:
        return previous_named
    if lower in {"he", "she", "one", "who"}:
        return "Quoted speaker"
    if speaker.split()[0] in NARRATIVE_CAPITAL_WORDS:
        return "Quoted speaker"
    if lower == "master":
        if possessive_role and previous_named:
            return previous_named
        return "Master"
    if lower == "teacher":
        if possessive_role and previous_named:
            return previous_named
        return "Teacher"
    return speaker[:1].upper() + speaker[1:]


def plausible_proper_speaker(candidate: str) -> str | None:
    candidate = clean_text(candidate).strip(" ,.:;\"'")
    if not candidate:
        return None
    if candidate in NON_PERSON_PROPER_SPEAKERS:
        return None
    first = candidate.split()[0]
    if first in NARRATIVE_CAPITAL_WORDS:
        return None
    return candidate


def infer_pronoun_antecedent(before: str) -> str | None:
    fragments = [part.strip() for part in re.split(r"[.?!]", before) if part.strip()]
    if not fragments:
        return None

    current_fragment = fragments[-1]
    when_match = re.search(
        rf"\bWhen\s+(?P<speaker>{PROPER_SPEAKER_PHRASE})\b"
        rf"(?:(?![.?!]).){{0,100}}\b(?:he|she)\s+(?:{SPEECH_VERBS})\b",
        current_fragment,
    )
    if when_match:
        return plausible_proper_speaker(when_match.group("speaker"))

    for fragment in reversed(fragments):
        matches = [
            candidate
            for match in re.finditer(PROPER_SPEAKER_PHRASE, fragment)
            if (candidate := plausible_proper_speaker(match.group(0)))
        ]
        if matches:
            return matches[-1]
    return None


def normalize_inferred_speaker(
    speaker: str | None,
    *,
    before: str,
    previous_named: str | None,
) -> str:
    if speaker and clean_text(speaker).strip(" ,.:;\"'").lower() in {"he", "she"}:
        if antecedent := infer_pronoun_antecedent(before):
            return normalize_speaker(antecedent, previous_named=previous_named)
    return normalize_speaker(speaker, previous_named=previous_named)


def infer_quote_speaker(
    paragraph: str,
    *,
    quote_start: int,
    quote_end: int,
    previous_named: str | None,
) -> str:
    before = paragraph[max(0, quote_start - 180) : quote_start]
    after = paragraph[quote_end : quote_end + 180]
    if who_match := BEFORE_WHO_RE.search(before):
        return normalize_inferred_speaker(
            who_match.group("speaker"), before=before, previous_named=previous_named
        )
    if before_match := BEFORE_ROLE_ACTION_SPEECH_RE.search(before):
        return normalize_inferred_speaker(
            before_match.group("speaker"), before=before, previous_named=previous_named
        )
    if before_match := BEFORE_SPEAKER_RE.search(before):
        return normalize_inferred_speaker(
            before_match.group("speaker"), before=before, previous_named=previous_named
        )
    if before_match := BEFORE_PRONOUN_ACTION_SPEECH_RE.search(before):
        return normalize_inferred_speaker(
            before_match.group("speaker"), before=before, previous_named=previous_named
        )
    if before_match := BEFORE_SENTENCE_SPEAKER_RE.search(before):
        return normalize_inferred_speaker(
            before_match.group("speaker"), before=before, previous_named=previous_named
        )
    if before_match := BEFORE_ACTION_SPEAKER_RE.search(before):
        return normalize_inferred_speaker(
            before_match.group("speaker"), before=before, previous_named=previous_named
        )
    if after_match := AFTER_SPEAKER_VERB_RE.search(after):
        return normalize_speaker(after_match.group("speaker"), previous_named=previous_named)
    if after_match := AFTER_VERB_SPEAKER_RE.search(after):
        return normalize_speaker(after_match.group("speaker"), previous_named=previous_named)
    return "Quoted speaker"


def strip_trailing_speech_intro(text: str) -> str:
    for pattern in (
        BEFORE_WHO_RE,
        BEFORE_ROLE_ACTION_SPEECH_RE,
        BEFORE_SPEAKER_RE,
        BEFORE_PRONOUN_ACTION_SPEECH_RE,
        BEFORE_SENTENCE_SPEAKER_RE,
        BEFORE_ACTION_SPEAKER_RE,
    ):
        match = pattern.search(text)
        if match:
            return text[: match.start()]
    return text


def add_turn(turns: list[RenderedTurn], speaker: str, text: str) -> None:
    text = clean_text(text)
    if not text:
        return
    if turns and turns[-1].speaker == speaker:
        turns[-1].text = clean_text(f"{turns[-1].text} {text}")
    else:
        turns.append(RenderedTurn(speaker=speaker, text=text))


def paragraph_to_turns(paragraph: str, *, previous_named: str | None) -> tuple[list[RenderedTurn], str | None]:
    turns: list[RenderedTurn] = []
    pos = 0
    last_named = previous_named
    continuation_speaker: str | None = None
    for match in QUOTE_RE.finditer(paragraph):
        prefix = paragraph[pos : match.start()]
        prefix_clean = strip_trailing_speech_intro(prefix)
        prefix_clean = ATTRIBUTION_TAIL_RE.sub("", prefix_clean).strip(" :")
        add_turn(turns, "Narrator", prefix_clean)

        speaker = infer_quote_speaker(
            paragraph,
            quote_start=match.start(),
            quote_end=match.end(),
            previous_named=last_named,
        )
        if speaker == "Quoted speaker" and continuation_speaker:
            speaker = continuation_speaker
        add_turn(turns, speaker, match.group("quote"))
        if speaker != "Quoted speaker":
            last_named = speaker

        tail = paragraph[match.end() :]
        tail_match = ATTRIBUTION_TAIL_RE.match(tail)
        if tail_match:
            pos = match.end() + tail_match.end()
            continuation_speaker = speaker if speaker != "Quoted speaker" else None
        else:
            pos = match.end()
            continuation_speaker = None

    add_turn(turns, "Narrator", paragraph[pos:])
    return turns, last_named


def story_history_turns(paragraphs: list[str]) -> list[RenderedTurn]:
    turns: list[RenderedTurn] = []
    previous_named: str | None = None
    for paragraph in paragraphs:
        paragraph_turns, previous_named = paragraph_to_turns(
            paragraph, previous_named=previous_named
        )
        for turn in paragraph_turns:
            add_turn(turns, turn.speaker, turn.text)
    return turns


def infer_target_speaker(target_text: str, *, previous_turns: list[RenderedTurn]) -> str:
    previous_named = next(
        (turn.speaker for turn in reversed(previous_turns) if turn.speaker != "Narrator"),
        None,
    )
    target_turns, _ = paragraph_to_turns(target_text, previous_named=previous_named)
    non_narrator = [turn.speaker for turn in target_turns if turn.speaker != "Narrator"]
    if non_narrator:
        return non_narrator[0]
    return "Koan closing line"


def participant_for_speaker(speaker: str, target_speaker: str) -> str:
    return "Participant B" if speaker == target_speaker else "Participant A"


def is_usable_dialogue_speaker(speaker: str) -> bool:
    if speaker in {"Narrator", "Quoted speaker"}:
        return False
    if speaker in UNRELIABLE_DIALOGUE_SPEAKERS:
        return False
    if speaker.split()[0] in NARRATIVE_CAPITAL_WORDS:
        return False
    return True


def render_history(turns: list[RenderedTurn], *, target_speaker: str) -> str:
    return "\n".join(
        f"{participant_for_speaker(turn.speaker, target_speaker)} ({turn.speaker}): {turn.text}"
        for turn in turns
    )


def story_to_row(
    story: KoanStory,
    *,
    min_prompt_words: int,
    max_prompt_words: int,
    min_target_words: int,
    max_target_words: int,
) -> dict | None:
    history_turns = story_history_turns(story.paragraphs[:-1])
    target_text = clean_text(story.paragraphs[-1])
    target_speaker = infer_target_speaker(target_text, previous_turns=history_turns)
    history_text = render_history(history_turns, target_speaker=target_speaker)
    prompt_words = count_dataset_words(history_text)
    target_words = count_dataset_words(target_text)
    if not history_text:
        return None
    if not (min_prompt_words <= prompt_words <= max_prompt_words):
        return None
    if not (min_target_words <= target_words <= max_target_words):
        return None

    source_name = "zen_koans_database"
    kind = "zen_koans_database_story_completion"
    return {
        "messages": [
            {"role": "system", "content": clean_dataset_text(SYSTEM_PROMPTS["buddhist"])},
            {
                "role": "user",
                "content": (
                    "Conversation so far:\n"
                    f"{history_text}\n\n"
                    "Write Participant B's next reply."
                ),
            },
            {"role": "assistant", "content": target_text},
        ],
        "metadata": {
            "record_id": make_record_id(
                source_name=source_name,
                kind=f"{kind}_{Path(story.slug).stem}",
                source_lines=[1, len(story.paragraphs)],
                target_speaker=target_speaker,
            ),
            "kind": kind,
            "source": "Zen Koans Database",
            "source_file": story.source_file,
            "source_lines": [1, len(story.paragraphs)],
            "target_speaker": target_speaker,
            "target_participant": "Participant B",
            "target_words": target_words,
            "prompt_words": prompt_words,
            "title": story.title,
            "slug": story.slug,
        },
    }


def story_to_dialogue_rows(
    story: KoanStory,
    *,
    history_turns: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    source_name = "zen_koans_database"
    kind = "zen_koans_database_clean_dialogue"
    turns = [
        turn
        for turn in story_history_turns(story.paragraphs)
        if is_usable_dialogue_speaker(turn.speaker)
    ]
    rows: list[dict] = []

    for idx, target in enumerate(turns):
        target_words = count_dataset_words(target.text)
        if target_words < min_target_words or target_words > max_target_words:
            continue

        history = turns[max(0, idx - history_turns) : idx]
        if not history or not any(turn.speaker != target.speaker for turn in history):
            continue

        mapped_history = [
            (
                (
                    "Participant B"
                    if turn.speaker == target.speaker
                    else "Participant A"
                )
                + f" ({turn.speaker})",
                turn.text,
            )
            for turn in history
        ]
        messages = build_messages(
            system_prompt=SYSTEM_PROMPTS["buddhist"],
            history=mapped_history,
            target_participant=f"Participant B ({target.speaker})",
            target_text=target.text,
        )
        rows.append(
            {
                "messages": messages,
                "metadata": {
                    "record_id": make_record_id(
                        source_name=source_name,
                        kind=f"{kind}_{Path(story.slug).stem}_{idx}",
                        source_lines=[1, len(story.paragraphs)],
                        target_speaker=target.speaker,
                    ),
                    "kind": kind,
                    "source": "Zen Koans Database",
                    "source_file": story.source_file,
                    "source_lines": [1, len(story.paragraphs)],
                    "target_speaker": target.speaker,
                    "target_participant": "Participant B",
                    "target_words": target_words,
                    "prompt_words": count_dataset_words(messages[1]["content"]),
                    "title": story.title,
                    "slug": story.slug,
                    "turn_index": idx,
                },
            }
        )

    return rows


def clean_dialogue_candidate(row: dict) -> bool:
    prompt = row["messages"][1]["content"]
    target = row["messages"][2]["content"]
    target_speaker = row["metadata"]["target_speaker"]
    if "Quoted speaker" in prompt or target_speaker == "Quoted speaker":
        return False
    if target_speaker == "Koan closing line":
        # Keep action punchlines only when the prompt ends in an explicit question.
        history = prompt.split("\n\nWrite Participant B's next reply.", 1)[0]
        last_turn = history.strip().splitlines()[-1] if history.strip() else ""
        if "?" not in last_turn:
            return False
    if "Participant B" not in prompt and target_speaker != "Koan closing line":
        return False
    if re.search(r"Participant A \((?:He|She|One)\):", prompt):
        return False
    if re.search(r"Participant A \(Narrator\):\s*(?:asked|said|replied|told)\b", prompt):
        return False
    if count_dataset_words(target) > 120:
        return False
    return True


def clean_rows(rows: list[dict]) -> list[dict]:
    clean: list[dict] = []
    for row in rows:
        if not clean_dialogue_candidate(row):
            continue
        row = dict(row)
        metadata = dict(row["metadata"])
        metadata["kind"] = "zen_koans_database_clean_dialogue"
        metadata["record_id"] = make_record_id(
            source_name="zen_koans_database",
            kind=f"{metadata['kind']}_{Path(metadata['slug']).stem}",
            source_lines=metadata["source_lines"],
            target_speaker=metadata["target_speaker"],
        )
        row["metadata"] = metadata
        clean.append(row)
    return clean


def row_to_markdown(row: dict, index: int, *, preview_chars: int) -> str:
    metadata = row["metadata"]
    return "\n".join(
        [
            f"## Review Example {index}: {metadata['source']}",
            "",
            f"- Record ID: `{metadata['record_id']}`",
            f"- Kind: `{metadata['kind']}`",
            f"- Title: `{metadata['title']}`",
            f"- Source file: `{metadata['source_file']}`",
            f"- Target: `{metadata['target_participant']} ({metadata['target_speaker']})`",
            f"- Prompt words: `{metadata['prompt_words']}`",
            f"- Target words: `{metadata['target_words']}`",
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
    parser = argparse.ArgumentParser(description="Parse the Zen Koans Database.")
    parser.add_argument("--list-html", type=Path, default=DEFAULT_LIST)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--clean-json", type=Path, default=DEFAULT_CLEAN_JSON)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="zen_koans_database_dialogue")
    parser.add_argument(
        "--clean-only",
        action="store_true",
        help="Deprecated alias for the default named-dialogue-only output.",
    )
    parser.add_argument(
        "--include-story-completions",
        action="store_true",
        help="Also write legacy whole-story completion rows, including narrator context.",
    )
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument(
        "--cache-only",
        action="store_true",
        help="Parse already downloaded page cache without fetching missing pages.",
    )
    parser.add_argument(
        "--history-turns",
        type=int,
        default=3,
        help="Named quoted turns to include before each dialogue target.",
    )
    parser.add_argument("--min-prompt-words", type=int, default=12)
    parser.add_argument("--max-prompt-words", type=int, default=500)
    parser.add_argument("--min-target-words", type=int, default=2)
    parser.add_argument("--max-target-words", type=int, default=120)
    parser.add_argument("--sample-count", type=int, default=12)
    parser.add_argument("--preview-chars", type=int, default=1200)
    args = parser.parse_args()

    links = read_list_links(args.list_html.expanduser().resolve())
    raw_dir = args.raw_dir.expanduser().resolve()
    stories: list[KoanStory] = []
    missing: list[str] = []
    for link in links:
        if args.cache_only:
            page_path = cached_page_path(link, raw_dir)
            if not page_path.exists():
                missing.append(link.slug)
                continue
        else:
            page_path = download_page(link, raw_dir, refresh=args.refresh)
        if story := parse_page(page_path, link):
            stories.append(story)

    clean_json = args.clean_json.expanduser().resolve()
    clean_json.parent.mkdir(parents=True, exist_ok=True)
    clean_json.write_text(
        json.dumps([story.__dict__ for story in stories], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    story_completion_rows = [
        row
        for story in stories
        if (
            row := story_to_row(
                story,
                min_prompt_words=args.min_prompt_words,
                max_prompt_words=args.max_prompt_words,
                min_target_words=args.min_target_words,
                max_target_words=args.max_target_words,
            )
        )
    ]
    dialogue_rows = [
        row
        for story in stories
        for row in story_to_dialogue_rows(
            story,
            history_turns=args.history_turns,
            min_target_words=args.min_target_words,
            max_target_words=args.max_target_words,
        )
    ]
    rows = list(dialogue_rows)
    if args.include_story_completions and not args.clean_only:
        rows.extend(story_completion_rows)

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"
    write_jsonl(jsonl_path, rows)

    kind_counts = Counter(row["metadata"]["kind"] for row in rows)
    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(
            [
                "# Zen Koans Database Review Sample",
                "",
                f"Links found: `{len(links)}`",
                f"Stories parsed: `{len(stories)}`",
                f"Rows parsed: `{len(rows)}`",
                f"Named dialogue rows: `{len(dialogue_rows)}`",
                f"Legacy story completion candidates: `{len(story_completion_rows)}`",
                f"Story completions included: `{bool(args.include_story_completions and not args.clean_only)}`",
                "",
                "Rows by kind:",
                "",
                *[f"- `{kind}`: `{count}`" for kind, count in sorted(kind_counts.items())],
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

    print(f"Links found: {len(links)}")
    print(f"Stories parsed: {len(stories)}")
    print(f"Missing cached pages: {len(missing)}")
    print(f"Named dialogue rows: {len(dialogue_rows)}")
    print(f"Legacy story completion candidates: {len(story_completion_rows)}")
    print(f"Rows written: {len(rows)}")
    for kind, count in sorted(kind_counts.items()):
        print(f"{kind}: {count}")
    print(f"Clean JSON: {clean_json}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review: {review_path}")


if __name__ == "__main__":
    main()
