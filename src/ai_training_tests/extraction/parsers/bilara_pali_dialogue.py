"""Parse dialogue training rows from bilara-data Pali Canon segments.

Sources: any sutta in the local bilara-data clone. Default targets are
DN (all 34 suttas) and SN1-11 (Sagāthāvagga, 271 suttas).

Speaker detection handles:
  - Named speakers from explicit reporting clauses
  - Anonymous speakers ("a deity said to the Buddha:")
  - Two-speaker alternation after initial attribution
  - Multi-segment quoted speeches (verse and prose)

Wider net vs milinda_panha.py:
  - Both speakers can be training targets, not just one side
  - Verse exchanges included, not just prose Q&A
  - Works across entire nikayas, not a single text
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
TOOLS_ROOT = REPO_ROOT / "tools"
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from source_ingest.bilara_reader import BILARA_ROOT, iter_uids, load_segments

from ai_training_tests.extraction.common.jsonl_io import write_jsonl
from ai_training_tests.extraction.common.review_samples import (
    SYSTEM_PROMPTS,
    build_messages,
    preview_text,
    select_spread,
)
from ai_training_tests.extraction.common.text_cleaning import (
    clean_dataset_text,
    count_dataset_words,
    make_record_id,
    normalize_text,
)

DEFAULT_OUTPUT_DIR = REPO_ROOT / "review_outputs/new_buddhist_sources"
DEFAULT_COLLECTIONS = ("dn", "sn1-11")

# Names that map to "The Buddha"
_BUDDHA_LOWER = frozenset(
    {
        "the buddha",
        "buddha",
        "the blessed one",
        "blessed one",
        "the awakened one",
        "the tathagata",
        "tathagata",
        "the teacher",
        "the world-honored one",
        "gotama",
        "master gotama",
        "worthy gotama",
        "the worthy gotama",
    }
)

# Speech verb pattern — any of these signals a reporting clause
_SPEECH_VERB_RE = re.compile(
    r"\b(?:said|asked|replied|answered|addressed|told|responded|recited|spoke)\b",
    re.IGNORECASE,
)

# Strip leading connectives before extracting subject
_CONNECTIVE_START_RE = re.compile(
    r"^(?:And\s+then|Then[,]?\s*|So[,]?\s*|At\s+that\s+(?:time|point)[,]?\s*"
    r"|Now[,]?\s*|Well[,]?\s*)\s*",
    re.IGNORECASE,
)

# Proper-noun sequence (capitalized, possibly multi-word)
_PROPER_NAME_RE = re.compile(
    r"(?P<name>[A-ZĀ-ſ][A-Za-zāīūĀĪŪṃṭḍṇḷṅñ\-\']{1,22}"
    r"(?:\s+(?:the\s+)?[A-ZĀ-ſ][A-Za-zāīūĀĪŪṃṭḍṇḷṅñ\-\']{1,22}){0,3})",
    re.UNICODE,
)

# Anonymous / generic entity description before a speech verb
_ANON_SUBJECT_RE = re.compile(
    r"\b(?:[Aa]n?\s+)?(?:glorious\s+|wicked\s+|evil\s+|certain\s+|young\s+)?"
    r"(?P<type>deity|brahmin|deva|yakkha|spirit|being|nāga|wanderer|ascetic|mendicant)",
    re.IGNORECASE,
)

# Words that look capitalized but are NOT speaker names
_SKIP_WORDS = frozenset(
    {
        "The",
        "A",
        "An",
        "This",
        "That",
        "These",
        "Those",
        "Some",
        "One",
        "He",
        "She",
        "They",
        "It",
        "His",
        "Her",
        "Their",
        "Its",
        "Now",
        "Then",
        "And",
        "But",
        "So",
        "Yet",
        "Also",
        "At",
        "In",
        "On",
        "Of",
        "To",
        "For",
        "With",
        "As",
        "From",
        "When",
        "While",
        "After",
        "Before",
        "Although",
        "Since",
        "Until",
        "Late",
        "Early",
        "Good",
        "Well",
        "There",
        "Here",
        "Once",
        "Just",
        "Though",
        "Thus",
        "Such",
        "Both",
        "All",
        "Not",
        "No",
        "Yes",
        "Another",
        "Neither",
        "Other",
        "Others",
        "If",
        "Whether",
        "Next",
        "First",
        "Second",
        "Third",
        "How",
        "What",
        "When",
        "Where",
        "Which",
        "Who",
        "Why",
        "Whoever",
        "Whatever",
        "Wherever",
    }
)


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Segment:
    key: str
    text: str  # normalized

    @property
    def is_header(self) -> bool:
        last = self.key.split(":")[-1].split(".")[-1]
        return last == "0"

    @property
    def opens_speech(self) -> bool:
        return self.text.lstrip().startswith('"')

    @property
    def closes_speech(self) -> bool:
        return self.text.rstrip().endswith('"')


@dataclass
class Turn:
    speaker: str
    text: str
    uid: str
    start_key: str
    end_key: str

    @property
    def word_count(self) -> int:
        return count_dataset_words(self.text)


# ---------------------------------------------------------------------------
# Speaker normalization
# ---------------------------------------------------------------------------


# Strip bilara HTML-like markup tags (<j>, <span class="..."> etc.) from segment text
_BILARA_TAG_RE = re.compile(r"<[^>]{1,40}>", re.ASCII)


def _strip_bilara_tags(text: str) -> str:
    return _BILARA_TAG_RE.sub("", text).strip()


# Known Pali place names that can appear before speech verbs but are NOT speakers.
# Pattern: "near Vesālī, the Buddha said..." → "Vesālī" incorrectly captured.
_PALI_PLACES = frozenset({
    "vesālī", "sāvatthī", "rājagaha", "uruvelā", "kosala", "magadha",
    "kapilavatthu", "campā", "ātumā", "setavyā", "varanasi", "sāketa",
    "kosambī", "bārāṇasī", "pāṭaliputta", "nāḷandā", "mithilā", "videha",
})


def _canonicalize_speaker(raw: str) -> str:
    """Map raw speaker string to a clean, stable label."""
    cleaned = clean_dataset_text(raw).strip().rstrip(",")
    cleaned = re.sub(r"\s+", " ", cleaned)
    # Strip leading connectives / locatives that occasionally get captured
    cleaned = re.sub(r"^(?:Then|And|So|Now|Well|There)\s+", "", cleaned).strip()
    if cleaned.lower() in _BUDDHA_LOWER:
        return "The Buddha"
    return cleaned


def _speaker_is_valid(speaker: str) -> bool:
    """Return False for pronouns, place names, or implausible speaker strings."""
    low = speaker.strip().lower()
    if low in _PRONOUN_LOWER:
        return False
    if low in _PALI_PLACES:
        return False
    # Reject single very-short tokens (likely pronouns or articles)
    if len(speaker.strip()) <= 2:
        return False
    return True


def _extract_speaker(text: str) -> str | None:
    """Extract speaker from a reporting clause using a two-step approach.

    Only call this on non-speech segments (segments that do NOT open with a
    quotation mark). For segments that start with speech, the caller should
    use pending_speaker or alternation instead.

    Step 1: verify the segment contains a speech verb.
    Step 2: extract the grammatical subject from text before the verb.
    """
    # Segments starting with a quote are speech-first (inverted) — the named
    # entity after the verb is the speaker, but these are usually minor
    # characters. Skip to avoid false attributions.
    if text.lstrip().startswith("\x22"):
        return None

    verb_m = _SPEECH_VERB_RE.search(text)
    if not verb_m:
        return None

    # Work with text before the first speech verb
    before = text[: verb_m.start()]
    # Strip leading connectives
    before = _CONNECTIVE_START_RE.sub("", before).strip()

    # Try anonymous / generic entity first (often "a glorious deity ...")
    early = before[:100]
    anon_m = _ANON_SUBJECT_RE.search(early)
    if anon_m:
        return f"a {anon_m.group('type').lower()}"

    # Try named speaker: scan for first proper-noun sequence
    for m in _PROPER_NAME_RE.finditer(before):
        if m.start() > 100:
            break
        name = m.group("name").strip().rstrip(",")
        first_word = name.split()[0]
        if first_word in _SKIP_WORDS:
            continue
        # Skip gerunds / past participles (narrative phrase starters)
        if first_word.endswith(("ing", "ed")) and len(first_word) > 4:
            continue
        # Skip possessives: "Jeta's Grove"
        after = before[m.end() :]
        if after.lstrip().startswith(("'s", "'s")):
            continue
        if len(name) < 2:
            continue
        return _canonicalize_speaker(name)

    return None


# Extract the addressee from a reporting clause ("X said to Y") so we can
# pre-register Y as the second speaker for alternation.
_ADDRESSEE_RE = re.compile(
    r"\b(?:said|asked|replied|answered|addressed|told)\s+to\s+"
    r"(?:(?:Venerable|Master|King|Queen|Prince|Chieftain|the\s+Buddha)\s*)?"
    r"(?P<addressee>[A-ZĀ-ſ][A-Za-zāīūĀĪŪṃṭḍṇḷṅñ\-\']{1,22}"
    r"(?:\s+(?:the\s+)?[A-ZĀ-ſ][A-Za-zāīūĀĪŪṃṭḍṇḷṅñ\-\']{1,22}){0,2})",
    re.UNICODE,
)


def _extract_addressee(text: str) -> str | None:
    """Extract the person being spoken TO from a reporting clause."""
    m = _ADDRESSEE_RE.search(text)
    if not m:
        return None
    raw = m.group("addressee").strip()
    # Skip simple pronouns
    if raw.lower() in {"him", "her", "them", "it", "the"}:
        return None
    return _canonicalize_speaker(raw)


def _segment_sort_key(seg: Segment) -> tuple[object, ...]:
    _, _, key_part = seg.key.partition(":")
    parts: list[object] = []
    for chunk in key_part.split("."):
        parts.append(int(chunk) if chunk.isdigit() else chunk)
    return tuple(parts)


# ---------------------------------------------------------------------------
# Turn extraction
# ---------------------------------------------------------------------------


def _sutta_title(segments: list[Segment]) -> str:
    """Extract a human-readable title from the first header segments."""
    titles: list[str] = []
    for seg in segments[:10]:
        if seg.is_header or seg.key.split(":")[-1].startswith("0."):
            t = seg.text.strip()
            if t:
                titles.append(t)
        if len(titles) >= 2:
            break
    return " / ".join(titles) if titles else ""


# Pre-scan pattern: "X went up to/approached the Buddha" identifies the questioner.
_APPROACHED_BUDDHA_RE = re.compile(
    r"(?P<questioner>[A-ZĀ-ſ][A-Za-zāīūĀĪŪṃṭḍṇḷṅñ\-\'\s]{2,45}?)\s+"
    r"(?:went up to|approached|went to|came to)\s+"
    r"(?:the\s+)?(?:Buddha|Blessed\s+One)",
    re.UNICODE,
)

_PRONOUN_LOWER = frozenset(
    {"he", "she", "they", "it", "that", "this", "who", "one", "we", "you",
     "him", "her", "them", "his", "their"}
)


def _prescan_questioner(segments: list[Segment]) -> str | None:
    """Scan early narrative to find who approached the Buddha (the questioner)."""
    for seg in segments[:25]:
        if seg.opens_speech:
            continue
        m = _APPROACHED_BUDDHA_RE.search(seg.text)
        if m:
            raw = m.group("questioner").strip().rstrip(",")
            if raw.lower() not in _PRONOUN_LOWER and len(raw) > 1:
                cleaned = _canonicalize_speaker(raw)
                if cleaned != "The Buddha":
                    return cleaned
    return None


def parse_turns(uid: str, bilara_root: Path = BILARA_ROOT) -> list[Turn]:
    """
    Extract dialogue turns from a bilara sutta.

    Returns turns with speaker attribution. May return an empty list for
    suttas without extractable attributed dialogue.
    """
    raw_segs = load_segments(uid, bilara_root)
    segments = []
    for key, text in raw_segs:
        norm = normalize_text(_strip_bilara_tags(text))
        if norm:
            segments.append(Segment(key=key, text=norm))

    turns: list[Turn] = []
    pending_speaker: str | None = None  # set by reporting clause
    in_speech = False
    speech_parts: list[str] = []
    speech_start_key: str = ""
    speech_speaker: str | None = None
    # For two-speaker alternation. Pre-populate from narrative pre-scan.
    known_speakers: list[str] = []

    # Pre-scan: find the questioner from narrative ("X went up to the Buddha")
    questioner = _prescan_questioner(segments)
    if questioner and _speaker_is_valid(questioner):
        known_speakers.append(questioner)
        known_speakers.append("The Buddha")

    def commit_turn(end_key: str) -> None:
        nonlocal speech_speaker, speech_parts, in_speech, speech_start_key
        if not speech_speaker or not speech_parts:
            return
        raw_text = " ".join(p for p in speech_parts if p)
        raw_text = raw_text.strip().strip('"')
        text = clean_dataset_text(raw_text)
        if not text:
            return
        speaker = _canonicalize_speaker(speech_speaker)
        if not _speaker_is_valid(speaker):
            return
        turns.append(
            Turn(
                speaker=speaker,
                text=text,
                uid=uid,
                start_key=speech_start_key,
                end_key=end_key,
            )
        )
        # Track unique speakers for alternation
        if speaker not in known_speakers:
            known_speakers.append(speaker)

    for seg in segments:
        if seg.is_header:
            # Commit any open speech at section boundary, but keep pending_speaker
            # so attribution can carry across section headers.
            if in_speech:
                commit_turn(seg.key)
                in_speech = False
                speech_parts = []
                speech_speaker = None
            continue

        text = seg.text

        if not in_speech:
            # Look for reporting clause only on non-speech segments
            if not seg.opens_speech:
                found_speaker = _extract_speaker(text)
                if found_speaker and _speaker_is_valid(found_speaker):
                    # If a new named speaker appears who is not in the current pair,
                    # reset known_speakers so alternation uses the new pair rather than
                    # bleeding old attribution (common in long suttas like DN16).
                    if known_speakers and found_speaker not in known_speakers:
                        known_speakers.clear()
                    pending_speaker = found_speaker
                    # Pre-register the addressee as second known speaker so
                    # alternation works without needing explicit "Y said..." later.
                    addressee = _extract_addressee(text)
                    if (
                        addressee
                        and _speaker_is_valid(addressee)
                        and addressee != found_speaker
                        and len(known_speakers) < 2
                        and addressee not in known_speakers
                    ):
                        known_speakers.append(addressee)
                    continue

            if seg.opens_speech:
                # Determine speaker attribution
                attributed_speaker = pending_speaker
                if attributed_speaker is None:
                    last_speaker = turns[-1].speaker if turns else None
                    if len(known_speakers) >= 2:
                        # Standard two-speaker alternation
                        if last_speaker == known_speakers[0]:
                            attributed_speaker = known_speakers[1]
                        elif last_speaker == known_speakers[1]:
                            attributed_speaker = known_speakers[0]
                        elif last_speaker is None:
                            # First speech: questioner (non-Buddha) goes first
                            non_buddha = [s for s in known_speakers if s != "The Buddha"]
                            if non_buddha:
                                attributed_speaker = non_buddha[0]
                    elif len(known_speakers) == 1 and known_speakers[0] != "The Buddha":
                        # One known speaker (non-Buddha questioner): Buddha is the implied responder
                        attributed_speaker = "The Buddha"
                        known_speakers.append("The Buddha")

                if attributed_speaker is None:
                    # Can't attribute — skip
                    pending_speaker = None
                    continue

                speech_speaker = attributed_speaker
                speech_start_key = seg.key
                pending_speaker = None

                # Strip the opening " from the text when starting collection.
                # Look for a closing " in the SAME segment (single-segment speech
                # or inverted-reporting like '"Yes, sir," replied X.').
                inner = text[1:] if text.startswith('"') else text
                close_pos = inner.find('"')
                if close_pos != -1:
                    # Speech closes within this segment
                    speech_parts = [inner[:close_pos]]
                    commit_turn(seg.key)
                    speech_parts = []
                    speech_speaker = None
                else:
                    speech_parts = [inner]
                    in_speech = True

        else:  # in_speech
            # Look for a closing " anywhere in the segment.
            close_pos = text.find('"')
            if close_pos != -1:
                speech_parts.append(text[:close_pos])
                commit_turn(seg.key)
                in_speech = False
                speech_parts = []
                speech_speaker = None
            else:
                speech_parts.append(text)

    # Commit any unclosed speech at end of sutta
    if in_speech and speech_parts and segments:
        commit_turn(segments[-1].key)

    return turns


# ---------------------------------------------------------------------------
# Row construction
# ---------------------------------------------------------------------------


# Speaker-content reversal checks: (speaker_keyword, address_in_own_speech).
# If speaker X has a turn containing an address term that only others use FOR X,
# it means X's label is wrong (someone else's speech is attributed to X).
_B_SELF_ADDRESS_CHECKS: list[tuple[re.Pattern[str], re.Pattern[str]]] = [
    # King addressing himself as "great king" → the Buddha's speech, not the king's
    (re.compile(r"\bking\b|\bajātasattu\b|\bpasenadi\b|\baj-tasattu\b", re.I),
     re.compile(r"\bgreat king\b", re.I)),
    # Pāyāsi addressing himself as "chieftain" → Kassapa's speech
    (re.compile(r"\bpāyāsi\b|\bpayasi\b", re.I),
     re.compile(r"\bchieftain\b", re.I)),
    # The Buddha addressing himself with devotee epithets → someone else's speech.
    # The Buddha never refers to themselves as "Blessed One", "Holy One", "worthy Gotama" etc.
    (re.compile(r"\bbuddha\b|\bblessed one\b", re.I),
     re.compile(
         r"\bmister gotama\b|\bworthy gotama\b|\bascetic gotama\b"
         r"|\bblessed one\b|\bholy one\b",
         re.I,
     )),
]

# Turns labeled as "The Buddha" that contain devotional praise formulas the
# Buddha would never say about themselves — signals another speaker's words.
_BUDDHA_DEVOTIONAL_RE = re.compile(r"\bhomage to him\b|\bhomage to the buddha\b", re.I)


def _has_attribution_reversal(history: list[Turn], target: Turn) -> bool:
    """Return True if any turn shows clear evidence of speaker-label reversal.

    Catches cases like:
    - King Ajātasattu (B) turn containing "great king" (the Buddha's address for him)
    - The Buddha (B or A) turn containing "Homage to him" (devotional formula)
    - The Buddha (B) turn containing "worthy Gotama" (questioner's address for the Buddha)
    """
    target_speaker = target.speaker
    # Check B-labeled turns (history B turns + the target itself)
    b_turns = [t for t in history if t.speaker == target_speaker] + [target]
    for turn in b_turns:
        text_low = turn.text.lower()
        speaker_low = turn.speaker.lower()
        for speaker_re, address_re in _B_SELF_ADDRESS_CHECKS:
            if speaker_re.search(speaker_low) and address_re.search(text_low):
                return True

    # Check any Buddha-labeled history turn for devotional formulas
    for turn in history:
        if re.search(r"\bbuddha\b|\bblessed one\b", turn.speaker, re.I):
            if _BUDDHA_DEVOTIONAL_RE.search(turn.text):
                return True

    # Also check A-labeled (non-target) turns — reversal can appear there too.
    # E.g. King Pasenadi (A) saying "great king" means the Buddha's speech
    # has leaked into the King's label.
    for turn in history:
        if turn.speaker == target.speaker:
            continue  # already checked above
        text_low = turn.text.lower()
        speaker_low = turn.speaker.lower()
        for speaker_re, address_re in _B_SELF_ADDRESS_CHECKS:
            if speaker_re.search(speaker_low) and address_re.search(text_low):
                return True

    return False


def _history_is_usable(history: list[Turn], target: Turn) -> bool:
    """Conservative quality gate on the conversation window."""
    if not history:
        return False
    # All turns must be from the same sutta
    if any(t.uid != target.uid for t in history):
        return False
    # No consecutive same-speaker turns
    all_turns = history + [target]
    if any(
        all_turns[i].speaker == all_turns[i + 1].speaker
        for i in range(len(all_turns) - 1)
    ):
        return False
    # History turns must have usable length
    if any(not (3 <= t.word_count <= 350) for t in history):
        return False
    # Reject rows with clear speaker-label reversal evidence
    if _has_attribution_reversal(history, target):
        return False
    return True


def build_rows(
    turns: list[Turn],
    sutta_title: str = "",
    *,
    max_history_turns: int = 4,
    min_target_words: int = 5,
    max_target_words: int = 300,
    source_label: str = "Pali Canon (bilara)",
) -> list[dict]:
    """Build three-message training rows from extracted turns."""
    rows: list[dict] = []

    for idx in range(1, len(turns)):
        target = turns[idx]
        if not (min_target_words <= target.word_count <= max_target_words):
            continue

        # Build history window
        history_reversed: list[Turn] = []
        for pos in range(idx - 1, -1, -1):
            t = turns[pos]
            if t.uid != target.uid:
                break
            # Stop on consecutive same-speaker
            if history_reversed and history_reversed[-1].speaker == t.speaker:
                break
            history_reversed.append(t)
            if len(history_reversed) >= max_history_turns:
                break

        history = list(reversed(history_reversed))
        if not _history_is_usable(history, target):
            continue

        # Map speakers to Participant A / B labels.
        # Target speaker = Participant B. Everyone else = Participant A.
        # Reject rows where history has more than one distinct non-target speaker —
        # that would force two different people to share the "Participant A" label,
        # creating ambiguous training data.
        target_speaker = target.speaker
        non_target_speakers = list(
            dict.fromkeys(t.speaker for t in history if t.speaker != target_speaker)
        )
        if len(non_target_speakers) > 1:
            continue

        def participant_label(speaker: str) -> str:
            if speaker == target_speaker:
                return f"Participant B ({speaker})"
            return f"Participant A ({speaker})"

        history_formatted = [
            (participant_label(t.speaker), t.text) for t in history
        ]

        kind = "bilara_dialogue"
        source_file = f"bilara:{target.uid}"
        row = {
            "messages": build_messages(
                system_prompt=SYSTEM_PROMPTS["buddhist"],
                history=history_formatted,
                target_participant="Participant B",
                target_text=target.text,
            ),
            "metadata": {
                "record_id": make_record_id(
                    source_name=target.uid,
                    kind=f"{kind}_{idx}",
                    source_lines=[0, 0],
                    target_speaker=target_speaker,
                ),
                "kind": kind,
                "source": source_label,
                "source_file": source_file,
                "source_lines": [target.start_key, target.end_key],
                "target_speaker": target_speaker,
                "target_participant": "Participant B",
                "target_words": target.word_count,
                "uid": target.uid,
                "sutta_title": sutta_title,
                "speakers": list(
                    dict.fromkeys(t.speaker for t in history + [target])
                ),
            },
        }
        rows.append(row)

    # Apply automated hard-failure checks from review_policy to the full row pool.
    # This catches fragmentary targets (mid-sentence cutoffs ending with comma/colon),
    # broken participant mapping, and contamination before sampling.
    from ai_training_tests.extraction.review.review_policy import auto_hard_failures

    return [r for r in rows if not auto_hard_failures(r)]


# ---------------------------------------------------------------------------
# Collection-level processing
# ---------------------------------------------------------------------------

# Suttas excluded from the two-speaker model: either too many active speakers,
# or structural complexity that causes systematic mis-attribution.
_EXCLUDED_UIDS = frozenset({
    "dn3",    # Ambaṭṭha — 3-speaker: Ambaṭṭha + Pokkharasāti + Buddha
    "dn9",    # Poṭṭhapāda — 3-speaker: Poṭṭhapāda + Citta Hatthisāriputta + Buddha
    "dn13",   # Tevijja — 2 brahmins debating; Buddha not detected as main speaker
    "dn16",   # Mahāparinibbāna — 80+ pages, dozens of characters
    "dn18",   # "Magadhan" and "Next" appear as bad speaker names; complex cast
    "dn19",   # Mahāgovinda — complex multi-party narrative
    "dn24",   # Pāṭikaputta — 3-speaker: Sunakkhatta + Bhaggava + Buddha
    "dn6",    # Mahāli Sutta — 3-party: Oṭṭhaddha/Mahāli identity confusion + brahmin
    "dn12",   # Lohicca Sutta — 3-party: Lohicca + Rosika (student) + Buddha
    "dn29",   # Pāsādika — "Ānanda and Cunda" as composite speaker name
    "dn30",   # Lakkhaṇa — alternating prose/verse repetitive marks structure
})


_COLLECTION_LABELS: dict[str, str] = {
    "dn": "Digha Nikaya",
    "mn": "Majjhima Nikaya",
    "sn": "Samyutta Nikaya",
    "an": "Anguttara Nikaya",
}


def _source_label_for_uid(uid: str) -> str:
    import re as _re
    m = _re.match(r"^([a-z]+)", uid)
    prefix = m.group(1) if m else uid
    # SN sagāthāvagga
    sn_m = _re.match(r"^sn(\d+)\.", uid)
    if sn_m and 1 <= int(sn_m.group(1)) <= 11:
        return "Samyutta Nikaya Sagathavagga"
    return _COLLECTION_LABELS.get(prefix, prefix.upper())


def process_uid(
    uid: str,
    bilara_root: Path = BILARA_ROOT,
    *,
    max_history_turns: int = 4,
    min_target_words: int = 5,
    max_target_words: int = 300,
) -> list[dict]:
    """Parse one sutta and return its rows."""
    if uid in _EXCLUDED_UIDS:
        return []
    try:
        turns = parse_turns(uid, bilara_root)
    except Exception:
        return []

    if len(turns) < 2:
        return []

    # Use only the first two distinct speakers; skip if more than 2 complicate rows
    all_speakers = list(dict.fromkeys(t.speaker for t in turns))
    if len(all_speakers) < 2:
        return []

    # Get title from segments
    raw_segs = load_segments(uid, bilara_root)
    title_segs = [
        normalize_text(v)
        for k, v in raw_segs
        if k.split(":")[-1].startswith("0.") and normalize_text(v)
    ]
    title = " / ".join(title_segs[:2]) if title_segs else uid

    return build_rows(
        turns,
        sutta_title=title,
        max_history_turns=max_history_turns,
        min_target_words=min_target_words,
        max_target_words=max_target_words,
        source_label=_source_label_for_uid(uid),
    )


def process_collections(
    collections: list[str],
    bilara_root: Path = BILARA_ROOT,
    *,
    max_history_turns: int = 4,
    min_target_words: int = 5,
    max_target_words: int = 300,
    verbose: bool = False,
) -> list[dict]:
    """Process all suttas in a list of collection specs and return combined rows."""
    all_uids: list[str] = []
    for coll in collections:
        uids = iter_uids(coll, bilara_root)
        all_uids.extend(uids)

    all_rows: list[dict] = []
    seen_uids: set[str] = set()
    for uid in all_uids:
        if uid in seen_uids:
            continue
        seen_uids.add(uid)
        rows = process_uid(
            uid,
            bilara_root,
            max_history_turns=max_history_turns,
            min_target_words=min_target_words,
            max_target_words=max_target_words,
        )
        if verbose and rows:
            print(f"  {uid}: {len(rows)} rows")
        all_rows.extend(rows)

    # Deduplicate by exact target text — keeps the first occurrence of each
    # unique assistant reply so repetitive formulaic responses don't dominate.
    seen_targets: set[str] = set()
    deduped: list[dict] = []
    for row in all_rows:
        target_key = row["messages"][2]["content"].strip()
        if target_key not in seen_targets:
            seen_targets.add(target_key)
            deduped.append(row)
    return deduped


# ---------------------------------------------------------------------------
# Review sample renderer
# ---------------------------------------------------------------------------


def row_to_markdown(row: dict, index: int, *, preview_chars: int = 1400) -> str:
    meta = row["metadata"]
    speakers_str = ", ".join(meta.get("speakers", []))
    return "\n".join(
        [
            f"## Review Example {index}: {meta['source']}",
            "",
            f"- Record ID: `{meta['record_id']}`",
            f"- Kind: `{meta['kind']}`",
            f"- UID: `{meta['uid']}`",
            f"- Title: {meta.get('sutta_title', '')}",
            f"- Speakers: {speakers_str}",
            f"- Target: `{meta['target_participant']} ({meta['target_speaker']})`",
            f"- Target words: `{meta['target_words']}`",
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


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse bilara Pali Canon dialogue rows from local bilara-data clone."
    )
    parser.add_argument(
        "--collections",
        nargs="+",
        default=list(DEFAULT_COLLECTIONS),
        help="Collections to process. Examples: dn sn1-11 mn sn3",
    )
    parser.add_argument(
        "--uids",
        nargs="*",
        default=[],
        help="Process specific UIDs instead of full collections (e.g. dn23 sn3.1).",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dataset-name", default="bilara_pali_dialogue")
    parser.add_argument("--max-history-turns", type=int, default=4)
    parser.add_argument("--min-target-words", type=int, default=5)
    parser.add_argument("--max-target-words", type=int, default=300)
    parser.add_argument("--sample-count", type=int, default=10)
    parser.add_argument("--preview-chars", type=int, default=1400)
    parser.add_argument("--bilara-root", type=Path, default=BILARA_ROOT)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    bilara_root = args.bilara_root.expanduser().resolve()

    if args.uids:
        rows: list[dict] = []
        for uid in args.uids:
            uid_rows = process_uid(
                uid,
                bilara_root,
                max_history_turns=args.max_history_turns,
                min_target_words=args.min_target_words,
                max_target_words=args.max_target_words,
            )
            rows.extend(uid_rows)
            if args.verbose:
                print(f"  {uid}: {len(uid_rows)} rows")
    else:
        print(f"Collections: {args.collections}")
        rows = process_collections(
            args.collections,
            bilara_root,
            max_history_turns=args.max_history_turns,
            min_target_words=args.min_target_words,
            max_target_words=args.max_target_words,
            verbose=args.verbose,
        )

    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / f"{args.dataset_name}.jsonl"
    review_path = output_dir / f"{args.dataset_name}_review_sample.md"

    write_jsonl(jsonl_path, rows)

    sample = select_spread(rows, args.sample_count)
    review_path.write_text(
        "\n".join(
            [
                "# Bilara Pali Dialogue Review Sample",
                "",
                f"Collections: `{args.collections}`",
                f"Total rows: `{len(rows)}`",
                f"Sampled rows: `{len(sample)}`",
                "",
                *[
                    row_to_markdown(row, idx, preview_chars=args.preview_chars)
                    for idx, row in enumerate(sample, 1)
                ],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Rows written: {len(rows)}")
    print(f"JSONL: {jsonl_path}")
    print(f"Review sample: {review_path}")


if __name__ == "__main__":
    main()
