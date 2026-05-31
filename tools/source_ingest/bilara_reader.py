"""Read bilara-data segment files from a local clone of github.com/suttacentral/bilara-data.

No network calls. All reads come from the locally cloned repo at
source_texts/buddhist/raw/bilara-data/.

To refresh the clone:
  cd source_texts/buddhist/raw
  git clone --depth 1 --filter=blob:none --sparse https://github.com/suttacentral/bilara-data bilara-data
  cd bilara-data && git sparse-checkout set translation/en/sujato
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BILARA_ROOT = REPO_ROOT / "source_texts/buddhist/raw/bilara-data/translation/en/sujato/sutta"

_UID_INDEX: dict[str, Path] | None = None


def _build_uid_index(bilara_root: Path) -> dict[str, Path]:
    """Walk bilara_root once and build a uid→path map for all JSON files."""
    index: dict[str, Path] = {}
    for p in bilara_root.rglob("*_translation-en-sujato.json"):
        uid = p.stem.replace("_translation-en-sujato", "")
        index[uid] = p
    return index


def _get_uid_index(bilara_root: Path = BILARA_ROOT) -> dict[str, Path]:
    global _UID_INDEX
    if _UID_INDEX is None:
        _UID_INDEX = _build_uid_index(bilara_root)
    return _UID_INDEX


def find_json(uid: str, bilara_root: Path = BILARA_ROOT) -> Path | None:
    """Return the Path for a sutta UID, or None if not found."""
    return _get_uid_index(bilara_root).get(uid)


def _segment_sort_key(item: tuple[str, str]) -> tuple[str, ...]:
    """Numeric sort for keys like 'dn2:5.7.0'. Zero-pads ints for correct ordering."""
    key = item[0]
    _, _, key_part = key.partition(":")
    parts: list[str] = []
    for chunk in key_part.split("."):
        parts.append(chunk.zfill(8) if chunk.isdigit() else chunk)
    return tuple(parts)


def load_segments(uid: str, bilara_root: Path = BILARA_ROOT) -> list[tuple[str, str]]:
    """Return sorted (key, text) pairs for a sutta UID.

    Raises FileNotFoundError if the UID is not in the local clone.
    """
    path = find_json(uid, bilara_root)
    if path is None:
        raise FileNotFoundError(
            f"No bilara JSON for uid={uid!r}. "
            f"Is the bilara-data sparse checkout populated at {bilara_root}?"
        )
    with open(path, encoding="utf-8") as f:
        data: dict[str, str] = json.load(f)
    return sorted(data.items(), key=_segment_sort_key)


def iter_uids(collection: str, bilara_root: Path = BILARA_ROOT) -> list[str]:
    """Return all UIDs in a collection.

    collection examples:
      'dn'        → all 34 DN suttas
      'mn'        → all 152 MN suttas
      'sn1'       → all suttas in SN samyutta 1 (81 suttas)
      'sn1-11'    → all sagāthāvagga suttas (SN1 through SN11)
      'sn'        → all 1819 SN suttas
      'an'        → all AN suttas
      'iti'       → Itivuttaka
      'ud'        → Udana
    """
    index = _get_uid_index(bilara_root)

    # Range shorthand: 'sn1-11' → collect sn1 through sn11
    if "-" in collection and not collection.startswith("an"):
        prefix, _, rest = collection.partition("-")
        # e.g. 'sn1-11' → prefix='sn1', rest='11'
        coll_match = _parse_range(collection)
        if coll_match:
            uids: list[str] = []
            for uid in sorted(index):
                if _uid_in_range(uid, coll_match):
                    uids.append(uid)
            return sorted(uids, key=_segment_sort_key_for_uid)

    results: list[str] = []
    for uid in index:
        if _uid_in_collection(uid, collection):
            results.append(uid)
    return sorted(results, key=_segment_sort_key_for_uid)


def _parse_range(spec: str) -> tuple[str, int, int] | None:
    """Parse 'sn1-11' into ('sn', 1, 11), or None if not a valid range."""
    import re
    m = re.match(r"^([a-z]+)(\d+)-(\d+)$", spec)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3))
    return None


def _uid_in_range(uid: str, range_spec: tuple[str, int, int]) -> bool:
    """Return True if uid like 'sn3.4' falls in range ('sn', 1, 11)."""
    import re
    prefix, lo, hi = range_spec
    m = re.match(rf"^{re.escape(prefix)}(\d+)", uid)
    if not m:
        return False
    n = int(m.group(1))
    return lo <= n <= hi


def _uid_in_collection(uid: str, collection: str) -> bool:
    """Return True if uid belongs to the given collection string."""
    import re
    # Exact nikaya: 'dn', 'mn', 'sn', 'an'
    if collection in ("dn", "mn", "sn", "an"):
        return bool(re.match(rf"^{collection}\d", uid))
    # Specific samyutta/nipata: 'sn1', 'an4', etc.
    if re.match(r"^(sn|an)\d+$", collection):
        coll_prefix = re.match(r"^([a-z]+)(\d+)$", collection)
        if coll_prefix:
            prefix, num = coll_prefix.group(1), coll_prefix.group(2)
            return bool(re.match(rf"^{prefix}{num}\.", uid))
    # KN sub-collection: 'iti', 'ud', 'snp', 'thag', 'thig', etc.
    kn_colls = ("iti", "ud", "snp", "thag", "thig", "dhp", "ja", "kp", "cp")
    if collection in kn_colls:
        return uid.startswith(collection)
    return False


def _segment_sort_key_for_uid(uid: str) -> tuple[object, ...]:
    """Sort UIDs like 'sn1.3' numerically."""
    import re
    parts: list[object] = []
    for chunk in re.split(r"(\d+)", uid):
        if chunk.isdigit():
            parts.append(int(chunk))
        elif chunk:
            parts.append(chunk)
    return tuple(parts)
