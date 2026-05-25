#!/usr/bin/env python3
"""Download and parse Majjhima Nikaya dialogue rows from dhammatalks.org.

This parser follows the project's review-first style:
- keep the original translated wording as much as possible
- emit clean Participant A / Participant B conversation turns
- attach sutta/section information in metadata rather than in the prompt

Source note:
- dhammatalks.org currently provides complete translations of 104 Majjhima Nikaya
  suttas and excerpts from three more. This parser downloads the available HTML
  pages into a local raw-source cache, writes a clean consolidated text file for
  inspection, and mines dialogue rows from those cached HTML pages.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

from build_pilot_dialogue_dataset import (
    build_messages,
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    write_jsonl,
)
from preview_dialogue_examples import select_spread


REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = REPO_ROOT / "source_texts/buddhist/raw/majjhima_nikaya_dhammatalks"
PAGES_DIR = RAW_DIR / "pages"
CLEAN_TEXT = REPO_ROOT / "source_texts/buddhist/clean/majjhima_nikaya_dhammatalks_selected.txt"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"
INDEX_URL = "https://www.dhammatalks.org/suttas/MN/index_MN.html"
SOURCE_LABEL = "Majjhima Nikaya"
DATASET_NAME = "majjhima_nikaya_dialogue"

TITLE_RE = re.compile(r"MN\s*(?P<number>\d+)\b")
INDEX_LINK_RE = re.compile(r'href="(?P<href>/suttas/MN/MN\d+\.html)"')
DOUBLE_QUOTE_RE = re.compile(r'[“"]([^“”"]+)[”"]')
VERB_RE = re.compile(
    r"\b(said|asked|replied|responded|addressed|continued|declared|remarked|added|"
    r"told|answered|spoke|questioned)\b",
    re.IGNORECASE,
)
PURE_QUOTE_RE = re.compile(r'^[“"](?P<quote>.+)[”"]$')

UPPER = "A-ZĀĪŪṬḌṆḶṂÑṄ"
LETTER = "A-Za-zĀĪŪṬḌṆḶṂÑṄāīūṭḍṇḷṃñṅ"
WORD = rf"[{UPPER}][{LETTER}\-]*"
GENERIC_NAME_RE = re.compile(
    rf"(?:Master {WORD}|{WORD}(?: {WORD}){{0,3}}(?: the [A-Za-zĀĪŪṬḌṆḶṂÑṄāīūṭḍṇḷṃñṅ-]+)?)"
)
VEN_PATTERN = rf"Ven\. {WORD}(?: {WORD}){{0,4}}(?:[’']s)?"
KING_PATTERN = rf"King {WORD}(?: {WORD}){{0,4}}(?:[’']s)?"
QUEEN_PATTERN = rf"Queen {WORD}(?: {WORD}){{0,4}}(?:[’']s)?"
BRAHMAN_PATTERN = rf"[Bb]rahman {WORD}(?: {WORD}){{0,4}}(?:[’']s)?"
PRINCE_PATTERN = rf"Prince {WORD}(?: {WORD}){{0,4}}(?:[’']s)?"
HOUSEHOLDER_PATTERN = rf"Householder {WORD}(?: {WORD}){{0,4}}(?:[’']s)?"
NAME_RE = re.compile(
    "|".join(
        [
            r"(?:The Blessed One)",
            rf"(?:{VEN_PATTERN})",
            rf"(?:{KING_PATTERN})",
            rf"(?:{QUEEN_PATTERN})",
            rf"(?:{BRAHMAN_PATTERN})",
            rf"(?:{PRINCE_PATTERN})",
            rf"(?:{HOUSEHOLDER_PATTERN})",
            r"(?:the monks)",
            r"(?:the bhikkhus)",
            r"(?:the mendicants)",
            r"(?:the wanderers)",
            r"(?:the brahmans)",
        ]
    )
)
THEN_SUBJECT_RE = re.compile(rf"\bThen\s+({NAME_RE.pattern})\b")
LEADING_SUBJECT_RE = re.compile(rf"^({NAME_RE.pattern})\b")

GROUP_SPEAKERS = {"Monks", "Mendicants", "Wanderers", "The brahmans", "Householders", "Nigaṇṭhas"}
EXCLUDED_SPEAKERS = GROUP_SPEAKERS | {"The Buddha's statement"}
INVALID_SPEAKERS = {
    "friend",
    "friends",
    "lord",
    "sir",
    "i",
    "the",
    "similarly",
    "there",
    "is",
    "it",
    "this",
    "where",
    "just",
    "wait",
}
INVALID_SINGLE_WORD_SPEAKERS = INVALID_SPEAKERS | {
    "he",
    "she",
    "they",
    "we",
    "you",
    "for",
    "as",
    "one",
    "excellent",
    "why",
    "have",
    "tell",
    "responding",
    "saying",
    "now",
    "such",
    "my",
    "from",
    "whatever",
    "inconstant",
    "listen",
    "suppose",
    "dhamma",
    "are",
    "because",
    "river",
    "gotama",
    "come",
    "does",
    "has",
    "a",
    "t",
    "with",
    "discerning",
    "going",
    "good",
    "many",
    "modest",
    "right",
    "seated",
    "thus",
    "well",
    "wise",
    "worthless",
}
BARE_TITLE_SPEAKERS = {"Ven.", "King", "Queen", "Prince", "Householder", "Brahman", "brahman"}
KNOWN_SINGLE_SPEAKER_NAMES = {
    "anuruddha",
    "assalāyana",
    "bhaggava",
    "bhāradvāja",
    "māgaṇḍiya",
    "māluṅkyaputta",
    "pessa",
    "raṭṭhapāla",
    "rāhula",
    "rāma",
    "saccaka",
    "sunakkhatta",
    "sāti",
    "udāyin",
    "upāli",
}
NON_SPEAKER_NAMES = {
    "As",
    "Then",
    "And",
    "But",
    "So",
    "When",
    "What",
    "If",
    "In",
    "On",
    "At",
    "No",
    "Yes",
    "Ven",
    "Master",
    "Lord",
}
SYSTEM_PROMPT = (
    "You are a Buddhist philosophical interlocutor. Reply naturally, reason "
    "from the source tradition, and keep the exchange grounded rather than generic."
)


@dataclass
class Block:
    tag: str
    start_line: int
    end_line: int
    text: str


@dataclass
class SuttaPage:
    number: int
    title: str
    url: str
    source_file: str
    blocks: list[Block]


@dataclass
class Turn:
    speaker: str
    start_line: int
    end_line: int
    text: str
    section_title: str
    paragraph_index: int

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


class SuttaHTMLExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_sutta_depth = 0
        self.skip_depth = 0
        self.current_tag: str | None = None
        self.current_text: list[str] = []
        self.current_start_line = 0
        self.blocks: list[Block] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag == "div" and attr_map.get("id") == "sutta":
            self.in_sutta_depth = 1
            return
        if not self.in_sutta_depth:
            return

        if tag == "div":
            self.in_sutta_depth += 1

        classes = (attr_map.get("class") or "").split()
        if tag == "span" and (
            "fn" in classes
            or attr_map.get("epub_type") == "pagebreak"
            or attr_map.get("role") == "doc-pagebreak"
        ):
            self.skip_depth += 1
            return

        if self.skip_depth:
            self.skip_depth += 1
            return

        if tag in {"h1", "h2", "h3", "h4", "p"} and self.current_tag is None:
            self.current_tag = tag
            self.current_text = []
            self.current_start_line = self.getpos()[0]

    def handle_endtag(self, tag: str) -> None:
        if not self.in_sutta_depth:
            return

        if self.skip_depth:
            self.skip_depth -= 1
            return

        if self.current_tag == tag:
            text = re.sub(r"\s+", " ", "".join(self.current_text)).strip()
            if text:
                current_tag = self.current_tag or tag
                self.blocks.append(
                    Block(
                        tag=current_tag,
                        start_line=self.current_start_line,
                        end_line=self.getpos()[0],
                        text=text,
                    )
                )
            self.current_tag = None
            self.current_text = []

        if tag == "div":
            self.in_sutta_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_sutta_depth and self.current_tag and not self.skip_depth:
            self.current_text.append(data)


def slug_key(path: Path) -> int:
    match = re.search(r"MN(\d+)\.html$", path.name)
    return int(match.group(1)) if match else 9999


def canonical_speaker(name: str) -> str:
    name = name.replace("“", "").replace("”", "")
    name = re.sub(r"^(?:Then|And|But|So)\s+", "", name)
    name = name.split("—", 1)[0]
    name = name.split("(", 1)[0]
    name = re.sub(r"(?:[’']s)$", "", name)
    name = re.sub(r"\s+", " ", name).strip(" ,;:.-—")
    if not name.startswith("The ") and " the " in name:
        name = name.split(" the ", 1)[0]
    lowered = name.lower()
    if lowered.startswith("the blessed"):
        return "The Buddha"
    mapping = {
        "the blessed one": "The Buddha",
        "blessed one": "The Buddha",
        "master gotama": "The Buddha",
        "the teacher": "The Buddha",
        "sāriputta": "Ven. Sāriputta",
        "moggallāna": "Ven. Moggallāna",
        "ānanda": "Ven. Ānanda",
        "the monks": "Monks",
        "the bhikkhus": "Monks",
        "the mendicants": "Mendicants",
        "the wanderers": "Wanderers",
        "the brahmans": "The brahmans",
        "aggivessana": "Saccaka",
    }
    return mapping.get(lowered, name)


def extract_subject(paragraph: str) -> str | None:
    quote_positions = [pos for marker in ('“', '"') if (pos := paragraph.find(marker)) != -1]
    prefix = paragraph[: min(quote_positions)] if quote_positions else paragraph
    for pattern in (THEN_SUBJECT_RE, LEADING_SUBJECT_RE):
        match = pattern.search(prefix)
        if match:
            return canonical_speaker(match.group(1))
    generic_match = GENERIC_NAME_RE.search(prefix)
    if generic_match:
        return canonical_speaker(generic_match.group(0))
    return None


def find_name_candidates(text: str) -> list[str]:
    candidates: list[tuple[int, str]] = []
    for pattern in (NAME_RE, GENERIC_NAME_RE):
        for match in pattern.finditer(text):
            candidates.append((match.start(), match.group(0)))
    candidates.sort(key=lambda item: item[0])
    ordered: list[str] = []
    seen: set[str] = set()
    for _pos, raw in candidates:
        speaker = canonical_speaker(raw)
        if speaker in NON_SPEAKER_NAMES:
            continue
        if not speaker_is_usable(speaker):
            continue
        if speaker and speaker not in seen:
            ordered.append(speaker)
            seen.add(speaker)
    return ordered


def infer_addressee_from_quote(text: str) -> str | None:
    if re.search(r"\bMaster Gotama\b", text):
        return "The Buddha"
    if re.match(r"^Lord\b", text):
        return "Lord"
    candidates = find_name_candidates(text[:120])
    if candidates:
        return candidates[0]
    match = re.search(r"\b(lord|friend|master)\b", text[:80], re.IGNORECASE)
    if match:
        return canonical_speaker(match.group(1))
    return None


def resolve_pair_addressee(addressee: str | None, current_pair: tuple[str, str] | None) -> str | None:
    if not addressee or not current_pair:
        return addressee
    if addressee in current_pair:
        return addressee
    if addressee in {"Lord", "The Buddha"} and "The Buddha" in current_pair:
        return "The Buddha"
    return addressee


def strip_reporting_scaffolding(text: str) -> str:
    stripped = text.strip()
    stripped = re.sub(r"^(?:Then|So|Now)\s+", "", stripped)
    stripped = re.sub(
        r"^(?:Saying|Responding|Thinking|Knowing|Seeing)\b(?:\s+to\s+[^,]+)?\s*,\s*",
        "",
        stripped,
    )
    stripped = re.sub(r'^[“"][^”"]+[”"]\s*,?\s*', "", stripped)
    return stripped.strip()


def strip_embedded_quotes(text: str) -> str:
    return re.sub(r'[“"][^“”"]+[”"]', " ", text)


def infer_speaker_and_addressee(
    prefix: str,
    *,
    quote_matches: list[re.Match[str]],
    active_subject: str | None,
) -> tuple[str | None, str | None]:
    verbs = list(VERB_RE.finditer(prefix))
    if not verbs:
        return None, None

    verb_match = verbs[-1]
    clause_start = max(prefix.rfind(".", 0, verb_match.start()), prefix.rfind("!", 0, verb_match.start()))
    clause = prefix[clause_start + 1 :].strip() if clause_start >= 0 else prefix.strip()
    before = clause[: clause.lower().rfind(verb_match.group(0).lower())]
    after = prefix[verb_match.end() :]

    before_without_quotes = strip_embedded_quotes(before)
    local_before = strip_reporting_scaffolding(before_without_quotes.rsplit(".", 1)[-1])
    local_candidates = find_name_candidates(local_before)
    if local_candidates:
        speaker = local_candidates[0]
    else:
        names_before = find_name_candidates(before_without_quotes)
        speaker = names_before[-1] if names_before else None

    if speaker is None and re.search(r"\bhe\s+" + VERB_RE.pattern, clause, re.IGNORECASE):
        speaker = active_subject

    addressee = None
    to_match = re.search(r"\bto\s+([^,.;:]+)", after, re.IGNORECASE)
    if to_match:
        addressee_candidates = find_name_candidates(to_match.group(1))
        if addressee_candidates:
            addressee = addressee_candidates[0]
    return speaker, addressee


def parse_turn_from_paragraph(
    paragraph: str,
    *,
    active_subject: str | None,
    last_turn: Turn | None,
    current_pair: tuple[str, str] | None,
) -> tuple[str | None, str | None, str | None]:
    quote_matches = list(DOUBLE_QUOTE_RE.finditer(paragraph))
    pure_quote_match = PURE_QUOTE_RE.match(paragraph.strip()) if len(quote_matches) == 1 else None
    if pure_quote_match:
        quote = clean_dataset_text(pure_quote_match.group("quote").strip())
        addressee = resolve_pair_addressee(infer_addressee_from_quote(quote), current_pair)
        if current_pair and last_turn and last_turn.speaker in current_pair:
            speaker = current_pair[0] if current_pair[1] == last_turn.speaker else current_pair[1]
            return speaker, addressee, quote or None
        if current_pair and addressee in current_pair:
            speaker = current_pair[0] if current_pair[1] == addressee else current_pair[1]
            return speaker, addressee, quote or None
        return None, addressee, quote or None

    if not quote_matches:
        return None, None, None

    target_quote = quote_matches[-1]
    prefix = paragraph[: target_quote.start()].strip()
    speaker, addressee = infer_speaker_and_addressee(
        prefix,
        quote_matches=quote_matches,
        active_subject=active_subject,
    )

    if (
        speaker is None
        and paragraph.startswith(("“", '"'))
        and current_pair is not None
        and last_turn is not None
        and last_turn.speaker in current_pair
    ):
        speaker = current_pair[0] if current_pair[1] == last_turn.speaker else current_pair[1]

    quote = clean_dataset_text(target_quote.group(1).strip())
    addressee = addressee or infer_addressee_from_quote(quote)
    return speaker, addressee, quote or None


def speaker_is_usable(speaker: str | None) -> bool:
    if not speaker:
        return False
    if speaker in EXCLUDED_SPEAKERS:
        return False
    if speaker in BARE_TITLE_SPEAKERS:
        return False
    if speaker.endswith(" River"):
        return False
    if re.match(r"^(?:As|If|When|Then|For|Now|Am)\s+I\b", speaker):
        return False
    lowered = speaker.lower()
    if lowered in INVALID_SPEAKERS:
        return False
    if "," in speaker or speaker.startswith("Could "):
        return False
    tokens = re.findall(r"[A-Za-zĀĪŪṬḌṆḶṂÑṄāīūṭḍṇḷṃñṅ]+", speaker)
    if len(tokens) == 1 and lowered in INVALID_SINGLE_WORD_SPEAKERS:
        return False
    if len(tokens) == 1 and lowered not in KNOWN_SINGLE_SPEAKER_NAMES:
        return False
    allowed_lower = {"ven", "king", "queen", "prince", "householder", "brahman", "the"}
    for token in tokens:
        if token.lower() in allowed_lower:
            continue
        if token[0].islower():
            return False
    return True


def dialogue_text_is_usable(text: str) -> bool:
    if not text:
        return False
    if len(text) < 12:
        return False
    if text.endswith(":"):
        return False
    if text.endswith(("…", "...")):
        return False
    if text.count('"') % 2 == 1:
        return False
    if text.count("“") != text.count("”"):
        return False
    if any(marker in text for marker in ("Copyright", "dhammatalks.org", "Translator's note")):
        return False
    return True


def parse_page(path: Path) -> SuttaPage:
    html = path.read_text(encoding="utf-8", errors="ignore")
    parser = SuttaHTMLExtractor()
    parser.feed(html)

    title_block = next((block for block in parser.blocks if block.tag == "h1"), None)
    title = title_block.text if title_block else path.stem
    number_match = TITLE_RE.search(title)
    number = int(number_match.group("number")) if number_match else slug_key(path)
    url = f"https://www.dhammatalks.org/suttas/MN/MN{number}.html"
    return SuttaPage(
        number=number,
        title=clean_dataset_text(title),
        url=url,
        source_file=path.name,
        blocks=parser.blocks,
    )


def extract_turns(page: SuttaPage) -> list[Turn]:
    turns: list[Turn] = []
    active_subject: str | None = None
    last_turn: Turn | None = None
    current_pair: tuple[str, str] | None = None
    current_section = page.title

    for block in page.blocks:
        if block.tag in {"h2", "h3", "h4"}:
            current_section = clean_dataset_text(block.text)
            continue
        if block.tag != "p":
            continue

        subject = extract_subject(block.text)
        if subject:
            active_subject = subject

        speaker, addressee, quote = parse_turn_from_paragraph(
            block.text,
            active_subject=active_subject,
            last_turn=last_turn,
            current_pair=current_pair,
        )
        if speaker is None or not quote:
            continue
        if not speaker_is_usable(speaker) or not dialogue_text_is_usable(quote):
            continue

        turns.append(
            Turn(
                speaker=speaker,
                start_line=block.start_line,
                end_line=block.end_line,
                text=quote,
                section_title=current_section,
                paragraph_index=len(turns),
            )
        )
        if addressee and speaker != addressee:
            current_pair = (speaker, addressee)
        elif last_turn and last_turn.speaker != speaker:
            current_pair = (last_turn.speaker, speaker)
        last_turn = turns[-1]
        active_subject = speaker

    return turns


def history_is_usable(history: list[Turn], target: Turn) -> bool:
    all_turns = history + [target]
    unique_speakers = {turn.speaker for turn in all_turns}
    if len(unique_speakers) > 3:
        return False
    if len({turn.text for turn in all_turns}) != len(all_turns):
        return False
    for turn in history:
        if turn.word_count < 3 or turn.word_count > 260:
            return False
    return True


def speaker_reference_names(speaker: str) -> set[str]:
    cleaned = speaker
    cleaned = re.sub(r"^(?:Ven\.|King|Queen|Brahman|brahman|Prince|Householder)\s+", "", cleaned)
    cleaned = re.sub(r"^The\s+", "", cleaned)
    cleaned = cleaned.strip()
    parts = [part for part in re.split(r"\s+", cleaned) if part]
    names = {cleaned.lower()}
    if parts:
        names.add(parts[-1].lower())
    if len(parts) >= 2:
        names.add(" ".join(parts[-2:]).lower())
    if speaker == "The Buddha":
        names.update({"buddha", "blessed one"})
    return names


def leading_addressee(text: str) -> str | None:
    match = re.match(
        rf"^(?P<name>Monks|monks|bhikkhus|mendicants|wanderers|brahmans|{WORD}(?: {WORD}){{0,3}}),",
        text,
    )
    if not match:
        return None
    return match.group("name").strip().lower()


def pair_reference_names(history: list[Turn], target: Turn) -> set[str]:
    names: set[str] = set()
    for turn in history + [target]:
        names.update(speaker_reference_names(turn.speaker))
    return names


def row_is_clean(history: list[Turn], target: Turn) -> bool:
    address = leading_addressee(target.text)
    if not address:
        return True
    if address in {"friend", "friends", "lord", "master", "venerable"}:
        return True
    names = pair_reference_names(history, target)
    return address in names


def conversation_window_for_target(
    turns: list[Turn],
    target_index: int,
    *,
    max_history_turns: int,
    max_line_gap: int = 45,
    max_total_span: int = 90,
    max_history_words: int = 420,
) -> list[Turn] | None:
    if target_index <= 0:
        return None

    target = turns[target_index]
    partner = turns[target_index - 1]
    if target.start_line - partner.end_line > max_line_gap:
        return None

    history_reversed: list[Turn] = []
    total_words = 0
    newest = target

    for pos in range(target_index - 1, -1, -1):
        turn = turns[pos]
        if newest.start_line - turn.end_line > max_line_gap:
            break
        if target.end_line - turn.start_line > max_total_span:
            break
        if turn.word_count < 3 or turn.word_count > 260:
            break
        if total_words + turn.word_count > max_history_words and history_reversed:
            break
        history_reversed.append(turn)
        total_words += turn.word_count
        newest = turn
        if max_history_turns > 0 and len(history_reversed) >= max_history_turns:
            break

    history = list(reversed(history_reversed))
    if not history or not history_is_usable(history, target):
        return None
    if len(history) == 1 and history[0].speaker == target.speaker:
        return None
    if not row_is_clean(history, target):
        return None
    return history


def build_rows(
    pages: list[SuttaPage],
    *,
    history_turns: int,
    min_target_words: int,
    max_target_words: int,
) -> list[dict]:
    rows: list[dict] = []

    for page in pages:
        turns = extract_turns(page)
        for idx, target in enumerate(turns):
            if target.word_count < min_target_words or target.word_count > max_target_words:
                continue

            history = conversation_window_for_target(
                turns,
                idx,
                max_history_turns=history_turns,
            )
            if not history:
                continue

            mapped_history = [
                (
                    f"{'Participant B' if turn.speaker == target.speaker else 'Participant A'} ({turn.speaker})",
                    turn.text,
                )
                for turn in history
            ]
            source_lines = [history[0].start_line, target.end_line]
            kind = "majjhima_nikaya_next_reply"
            record_id = make_record_id(
                source_name=page.source_file,
                kind=f"{kind}_{page.number}_{idx}",
                source_lines=source_lines,
                target_speaker=target.speaker,
            )
            rows.append(
                {
                    "messages": build_messages(
                        system_prompt=SYSTEM_PROMPT,
                        history=mapped_history,
                        target_participant="Participant B",
                        target_text=target.text,
                    ),
                    "metadata": {
                        "record_id": record_id,
                        "kind": kind,
                        "source": SOURCE_LABEL,
                        "source_file": page.source_file,
                        "source_lines": source_lines,
                        "target_speaker": target.speaker,
                        "target_participant": "Participant B",
                        "target_words": target.word_count,
                        "sutta_number": page.number,
                        "sutta_title": page.title,
                        "section_title": target.section_title,
                        "source_url": page.url,
                    },
                }
            )

    return rows


def consolidated_text(pages: list[SuttaPage]) -> str:
    parts: list[str] = []
    for page in pages:
        parts.append(f"## MN {page.number}: {page.title}")
        parts.append("")
        for block in page.blocks:
            if block.tag == "p":
                parts.append(clean_dataset_text(block.text))
                parts.append("")
            elif block.tag in {"h2", "h3", "h4"}:
                parts.append(f"### {clean_dataset_text(block.text)}")
                parts.append("")
        parts.append("")
    return "\n".join(parts).strip() + "\n"


def download_html(url: str, path: Path, *, refresh: bool) -> None:
    if path.exists() and not refresh:
        return
    import requests

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    response.encoding = "utf-8"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(response.text, encoding="utf-8")


def download_corpus(*, raw_dir: Path, refresh: bool, limit: int | None) -> list[Path]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    pages_dir = raw_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    index_path = raw_dir / "index_MN.html"
    download_html(INDEX_URL, index_path, refresh=refresh)
    index_html = index_path.read_text(encoding="utf-8", errors="ignore")

    links: list[tuple[int, str]] = []
    seen: set[int] = set()
    for href in INDEX_LINK_RE.findall(index_html):
        number_match = re.search(r"MN(\d+)\.html$", href)
        if not number_match:
            continue
        number = int(number_match.group(1))
        if number in seen:
            continue
        seen.add(number)
        links.append((number, urljoin(INDEX_URL, href)))

    links.sort(key=lambda item: item[0])
    if limit is not None:
        links = links[:limit]

    page_paths: list[Path] = []
    for number, url in links:
        path = pages_dir / f"MN{number}.html"
        download_html(url, path, refresh=refresh)
        page_paths.append(path)
    return page_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse Majjhima Nikaya dialogue rows.")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--clean-text", type=Path, default=CLEAN_TEXT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default=DATASET_NAME)
    parser.add_argument("--history-turns", type=int, default=8)
    parser.add_argument("--min-target-words", type=int, default=20)
    parser.add_argument("--max-target-words", type=int, default=260)
    parser.add_argument("--sample-count", type=int, default=12)
    parser.add_argument("--preview-chars", type=int, default=1400)
    parser.add_argument("--limit", type=int, help="Optional limit on downloaded/parsed MN pages.")
    parser.add_argument(
        "--refresh-downloads",
        action="store_true",
        help="Re-download the index and cached HTML pages.",
    )
    args = parser.parse_args()

    page_paths = download_corpus(
        raw_dir=args.raw_dir.expanduser().resolve(),
        refresh=args.refresh_downloads,
        limit=args.limit,
    )
    pages = [parse_page(path) for path in sorted(page_paths, key=slug_key)]

    clean_text_path = args.clean_text.expanduser().resolve()
    clean_text_path.parent.mkdir(parents=True, exist_ok=True)
    clean_text_path.write_text(consolidated_text(pages), encoding="utf-8")

    rows = build_rows(
        pages,
        history_turns=args.history_turns,
        min_target_words=args.min_target_words,
        max_target_words=args.max_target_words,
    )
    rows.sort(
        key=lambda row: (
            row["metadata"]["sutta_number"],
            row["metadata"]["source_lines"][0],
            row["metadata"]["source_lines"][1],
        )
    )

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = output_dir / f"{args.dataset_name}.jsonl"
    write_jsonl(dataset_path, rows)

    review_rows = select_spread(rows, args.sample_count)
    review_path = output_dir / f"{args.dataset_name}_review_sample.json"
    review_path.write_text(
        __import__("json").dumps(review_rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    per_sutta = Counter(row["metadata"]["sutta_number"] for row in rows)
    per_speaker = Counter(row["metadata"]["target_speaker"] for row in rows)
    print(f"Downloaded pages: {len(page_paths)}")
    print(f"Consolidated text: {clean_text_path}")
    print(f"Rows written: {len(rows)}")
    print(f"Dataset: {dataset_path}")
    print(f"Review JSON: {review_path}")
    print(f"Suttas contributing rows: {len(per_sutta)}")
    print("Top target speakers:")
    for speaker, count in per_speaker.most_common(10):
        print(f"- {speaker}: {count}")


if __name__ == "__main__":
    main()
