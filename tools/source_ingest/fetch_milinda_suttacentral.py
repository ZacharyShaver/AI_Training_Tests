#!/usr/bin/env python3
"""Fetch and consolidate Milinda Panha pages from SuttaCentral.

DEPRECATED FOR NEW WORK: The Milindapañha is extra-canonical and is NOT
present in the bilara-data GitHub repo. For all canonical Pali suttas
(DN, MN, SN, AN, KN) use tools/source_ingest/bilara_reader.py instead,
which reads from the local bilara-data clone with zero network calls.

This script exists only if the Milinda clean-text cache needs refreshing.
The cached output is at source_texts/buddhist/clean/milindapanha_suttacentral.txt
and does not need to be re-fetched unless the source translation changes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from ai_training_tests.extraction.common.text_cleaning import normalize_text

BASE_URL = "https://suttacentral.net/"
INDEX_URL = urljoin(BASE_URL, "api/suttaplex/mil")
INDEX_FALLBACK_URL = urljoin(BASE_URL, "api/range_suttaplex/mil")
BILARA_SUTTA_API_BASE_URL = urljoin(BASE_URL, "api/bilarasuttas/")
RAW_DIR = REPO_ROOT / "source_texts/buddhist/raw/milindapanha_suttacentral"
PAGES_DIR = RAW_DIR / "pages"
INDEX_PATH = RAW_DIR / "index.html"
MANIFEST_PATH = RAW_DIR / "export_manifest.json"
CLEAN_TEXT = REPO_ROOT / "source_texts/buddhist/clean/milindapanha_suttacentral.txt"
LEGACY_OUTPUT = REPO_ROOT / "oritiginal text/Milinda Panha.txt"
PAGE_REF_RE = re.compile(r"/(?P<ref>mil[\d.]+)/en/(?P<translation>[a-z_]+)")
SECTION_REF_RE = re.compile(r"^mil\d+(?:\.\d+){2,}$")
WHITESPACE_RE = re.compile(r"\s+")
TRANSLATION_FALLBACKS = {
    "kelly": ("kelly", "tw_rhysdavids"),
    "tw_rhysdavids": ("tw_rhysdavids", "kelly"),
}
CHROME_SNIPPETS = (
    "unsupported browser",
    "your browser is unsupported",
    "javascript",
    "cookie",
)
BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "li"}
CONTENT_ROOT_TAGS = {"main", "article"}
SKIP_TAGS = {"script", "style", "nav", "footer", "aside"}


@dataclass(slots=True)
class SuttaCentralPage:
    section_ref: str
    title: str = ""
    headings: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)


class SectionRefParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        href = dict(attrs).get("href") or ""
        if match := PAGE_REF_RE.search(href):
            self.refs.add(match.group("ref"))


class SuttaCentralPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._content_depth = 0
        self._current_tag: str | None = None
        self._current_parts: list[str] = []
        self._title = ""
        self.headings: list[str] = []
        self.paragraphs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        classes = set((attrs_dict.get("class") or "").split())
        if tag in SKIP_TAGS or "browser-warning" in classes:
            self._skip_depth += 1
            return

        if tag == "a" and "ref" in classes:
            self._skip_depth += 1
            return

        if tag in CONTENT_ROOT_TAGS:
            self._content_depth += 1
        elif self._content_depth and tag in {"section", "div"}:
            self._content_depth += 1

        if not self._content_depth or self._skip_depth:
            return

        if tag in BLOCK_TAGS and self._current_tag is None:
            self._current_tag = tag
            self._current_parts = []

    def handle_endtag(self, tag: str) -> None:
        if self._skip_depth:
            self._skip_depth -= 1
            return

        if self._current_tag == tag:
            text = clean_text(" ".join(self._current_parts))
            if text and not is_site_chrome(text):
                if tag == "h1":
                    self._title = text
                elif tag in {"h2", "h3", "h4", "li"}:
                    self.headings.append(text)
                else:
                    self.paragraphs.append(text)
            self._current_tag = None
            self._current_parts = []

        if self._content_depth and tag in CONTENT_ROOT_TAGS | {"section", "div"}:
            self._content_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._content_depth and self._current_tag and not self._skip_depth:
            self._current_parts.append(data)

    @property
    def title(self) -> str:
        return self._title


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = WHITESPACE_RE.sub(" ", text)
    return normalize_text(text)


def is_site_chrome(text: str) -> bool:
    lowered = text.lower()
    return any(snippet in lowered for snippet in CHROME_SNIPPETS)


def discover_section_refs(index_html: str) -> list[str]:
    json_refs = discover_section_refs_from_json(index_html)
    if json_refs:
        return json_refs

    parser = SectionRefParser()
    parser.feed(index_html)
    return sorted(parser.refs)


def discover_section_refs_from_json(payload: str) -> list[str]:
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return []

    refs: set[str] = set()

    def visit(node: object) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "uid" and isinstance(value, str) and SECTION_REF_RE.match(value):
                    refs.add(value)
                else:
                    visit(value)
            return
        if isinstance(node, list):
            for item in node:
                visit(item)
            return
        if isinstance(node, str):
            if SECTION_REF_RE.match(node):
                refs.add(node)
            elif match := PAGE_REF_RE.search(node):
                candidate = match.group("ref")
                if SECTION_REF_RE.match(candidate):
                    refs.add(candidate)

    visit(data)
    return sorted(refs)


def load_json_object(payload: str) -> object | None:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return None


def fetch_html(url: str, *, timeout: int = 60) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_sutta_json_page(section_ref: str, payload: str) -> SuttaCentralPage | None:
    data = load_json_object(payload)
    if data is None:
        return None

    if not isinstance(data, dict):
        return None

    if is_bilara_translation_payload(data):
        title = ""
        meta = data.get("_meta")
        if isinstance(meta, dict):
            title = clean_text(str(meta.get("title") or meta.get("translated_title") or ""))

        paragraphs: list[str] = []
        for key in sorted(data, key=bilara_segment_sort_key):
            if key.startswith("_"):
                continue
            value = data[key]
            if not isinstance(value, str):
                continue
            text = clean_text(value)
            if text and not is_site_chrome(text):
                paragraphs.append(text)

        headings = [title] if title else []
        return SuttaCentralPage(
            section_ref=section_ref,
            title=title or section_ref,
            headings=headings,
            paragraphs=paragraphs,
        )

    suttaplex = data.get("suttaplex")
    translation = data.get("translation")
    if not isinstance(suttaplex, dict) or not isinstance(translation, dict):
        return None

    translated_title = clean_text(str(suttaplex.get("translated_title") or ""))
    root_title = clean_text(str(suttaplex.get("root_title") or ""))
    title = translated_title or root_title

    text_map = translation.get("text")
    if isinstance(text_map, str):
        page_title = clean_text(str(translation.get("title") or title or section_ref))
        return parse_html_page(
            section_ref,
            text_map,
            fallback_title=page_title,
        )
    if not isinstance(text_map, dict):
        return None

    paragraphs: list[str] = []
    for key in sorted(text_map):
        value = text_map[key]
        if not isinstance(value, str):
            continue
        text = clean_text(value)
        if text and not is_site_chrome(text):
            paragraphs.append(text)

    headings = [title] if title else []
    page_title = clean_text(str(suttaplex.get("acronym") or title or section_ref))
    return SuttaCentralPage(
        section_ref=section_ref,
        title=page_title,
        headings=headings,
        paragraphs=paragraphs,
    )


def is_bilara_translation_payload(data: dict[object, object]) -> bool:
    if "translation" in data or "suttaplex" in data:
        return False
    return any(isinstance(key, str) and key.startswith("mil") for key in data)


def bilara_segment_sort_key(key: str) -> tuple[object, ...]:
    prefix, _, suffix = key.partition(":")
    if not suffix:
        return (prefix,)
    parts: list[object] = [prefix]
    for chunk in suffix.split("."):
        parts.append(int(chunk) if chunk.isdigit() else chunk)
    return tuple(parts)


def parse_html_page(
    section_ref: str,
    html: str,
    *,
    fallback_title: str = "",
) -> SuttaCentralPage:
    parser = SuttaCentralPageParser()
    parser.feed(html)
    return SuttaCentralPage(
        section_ref=section_ref,
        title=parser.title or fallback_title,
        headings=parser.headings,
        paragraphs=parser.paragraphs,
    )


def parse_suttacentral_page(section_ref: str, html: str) -> SuttaCentralPage:
    if json_page := parse_sutta_json_page(section_ref, html):
        return json_page

    return parse_html_page(section_ref, html)


def render_consolidated_text(pages: list[SuttaCentralPage]) -> str:
    parts: list[str] = []
    for page in pages:
        parts.append(f"## {page.section_ref}")
        parts.append("")
        if page.title:
            parts.append(page.title)
            parts.append("")
        for heading in page.headings:
            parts.append(f"### {heading}")
            parts.append("")
        for paragraph in page.paragraphs:
            parts.append(paragraph)
            parts.append("")
    return "\n".join(parts).strip() + "\n"


def write_export_manifest(
    path: Path,
    *,
    source: str,
    base_url: str,
    index_url: str | None = None,
    refs: list[str],
    output_path: Path,
    section_translations: list[dict[str, str]] | None = None,
) -> None:
    manifest = {
        "source": source,
        "base_url": base_url,
        "refs": refs,
        "output_path": str(output_path),
    }
    if index_url:
        manifest["index_url"] = index_url
    if section_translations:
        manifest["section_translations"] = section_translations
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def bilarasutta_api_url(section_ref: str, translation_entry: dict[str, object]) -> str:
    author_uid = str(translation_entry["author_uid"])
    lang = str(translation_entry["lang"])
    return urljoin(
        BILARA_SUTTA_API_BASE_URL,
        f"{section_ref}/{author_uid}?lang={lang}",
    )


def sutta_api_url(section_ref: str, translation: str) -> str:
    return urljoin(BASE_URL, f"api/suttas/{section_ref}/{translation}")


def translation_payload_url(
    section_ref: str,
    translation_entry: dict[str, object],
) -> str:
    if translation_entry.get("segmented") is False:
        return sutta_api_url(section_ref, str(translation_entry["author_uid"]))
    return bilarasutta_api_url(section_ref, translation_entry)


def extract_html_from_sutta_payload(payload: str) -> str | None:
    data = load_json_object(payload)
    if not isinstance(data, dict):
        return None

    translation = data.get("translation")
    if isinstance(translation, dict):
        text = translation.get("text")
        if isinstance(text, str):
            return text

    root_text = data.get("root_text")
    if isinstance(root_text, dict):
        text = root_text.get("text")
        if isinstance(text, str):
            return text

    return None


def extract_html_from_bilarasutta_payload(payload: str) -> str | None:
    data = load_json_object(payload)
    if not isinstance(data, dict):
        return None

    html_text = data.get("html_text")
    translation_text = data.get("translation_text")
    keys_order = data.get("keys_order")
    if (
        not isinstance(html_text, dict)
        or not isinstance(translation_text, dict)
        or not isinstance(keys_order, list)
    ):
        return None

    html_parts: list[str] = []
    for key in keys_order:
        if not isinstance(key, str):
            continue
        html_chunk = html_text.get(key)
        if not isinstance(html_chunk, str):
            continue
        if key == "~":
            html_parts.append(html_chunk)
            continue
        translation_chunk = translation_text.get(key, "")
        if not isinstance(translation_chunk, str):
            translation_chunk = ""
        if "{}" in html_chunk:
            html_parts.append(html_chunk.replace("{}", translation_chunk))
        else:
            html_parts.append(f"{html_chunk}{translation_chunk}")

    return "".join(html_parts).replace("{}", "")


def find_translation_entry(
    index_payload: str,
    *,
    section_ref: str,
    translation: str,
) -> dict[str, object]:
    data = load_json_object(index_payload)
    if data is None:
        raise RuntimeError("Milinda index payload is not valid JSON.")

    preferred_authors = TRANSLATION_FALLBACKS.get(translation, (translation,))

    def visit(node: object) -> dict[str, object] | None:
        if isinstance(node, dict):
            if node.get("uid") == section_ref:
                translations = node.get("translations")
                if isinstance(translations, list):
                    for author_uid in preferred_authors:
                        for entry in translations:
                            if (
                                isinstance(entry, dict)
                                and entry.get("author_uid") == author_uid
                                and isinstance(entry.get("id"), str)
                                and isinstance(entry.get("lang"), str)
                            ):
                                return {
                                    "author_uid": entry["author_uid"],
                                    "id": entry["id"],
                                    "lang": entry["lang"],
                                    "segmented": bool(entry.get("segmented")),
                                }
            for value in node.values():
                if found := visit(value):
                    return found
            return None
        if isinstance(node, list):
            for item in node:
                if found := visit(item):
                    return found
        return None

    if found := visit(data):
        return found
    raise RuntimeError(
        "Could not find translation metadata for "
        f"{section_ref} / {translation} in SuttaCentral index payload."
    )


def cached_page_path(raw_dir: Path, section_ref: str, translation: str) -> Path:
    return raw_dir / "pages" / translation / f"{section_ref}.html"


def cache_page(
    section_ref: str,
    *,
    raw_dir: Path,
    translation: str,
    index_payload: str,
    refresh: bool,
) -> tuple[str, dict[str, object]]:
    page_path = cached_page_path(raw_dir, section_ref, translation)
    page_path.parent.mkdir(parents=True, exist_ok=True)
    translation_entry = find_translation_entry(
        index_payload,
        section_ref=section_ref,
        translation=translation,
    )
    if page_path.exists() and not refresh:
        return page_path.read_text(encoding="utf-8"), translation_entry
    payload = fetch_html(translation_payload_url(section_ref, translation_entry))
    if translation_entry.get("segmented") is False:
        html = extract_html_from_sutta_payload(payload)
    else:
        html = extract_html_from_bilarasutta_payload(payload)
    if not html:
        raise RuntimeError(
            f"Could not render HTML for {section_ref} / {translation_entry['author_uid']}."
        )
    page_path.write_text(html, encoding="utf-8")
    return html, translation_entry


def download_index(*, raw_dir: Path, refresh: bool) -> str:
    raw_dir.mkdir(parents=True, exist_ok=True)
    index_path = raw_dir / "index.html"
    if index_path.exists() and not refresh:
        return index_path.read_text(encoding="utf-8")
    last_error: Exception | None = None
    for url in (INDEX_URL, INDEX_FALLBACK_URL):
        try:
            payload = fetch_html(url)
            if discover_section_refs(payload):
                index_path.write_text(payload, encoding="utf-8")
                return payload
        except Exception as exc:  # pragma: no cover - network fallback path
            last_error = exc
    if last_error is not None:
        raise last_error
    raise RuntimeError("Failed to discover Milinda section refs from SuttaCentral APIs.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch and consolidate Milinda Panha pages from SuttaCentral."
    )
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--clean-text", type=Path, default=CLEAN_TEXT)
    parser.add_argument(
        "--translation",
        choices=["kelly", "tw_rhysdavids"],
        default="kelly",
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--refresh-downloads", action="store_true")
    parser.add_argument("--write-legacy-mirror", action="store_true")
    parser.add_argument("--legacy-output", type=Path, default=LEGACY_OUTPUT)
    args = parser.parse_args()

    raw_dir = args.raw_dir.expanduser().resolve()
    index_html = download_index(raw_dir=raw_dir, refresh=args.refresh_downloads)
    refs = discover_section_refs(index_html)
    if args.limit is not None:
        refs = refs[: args.limit]

    pages: list[SuttaCentralPage] = []
    section_translations: list[dict[str, str]] = []
    for section_ref in refs:
        payload, translation_entry = cache_page(
            section_ref,
            raw_dir=raw_dir,
            translation=args.translation,
            index_payload=index_html,
            refresh=args.refresh_downloads,
        )
        pages.append(parse_suttacentral_page(section_ref, payload))
        section_translations.append(
            {
                "section_ref": section_ref,
                "author_uid": str(translation_entry["author_uid"]),
                "translation_id": str(translation_entry["id"]),
            }
        )

    clean_text = render_consolidated_text(pages)
    clean_text_path = args.clean_text.expanduser().resolve()
    clean_text_path.parent.mkdir(parents=True, exist_ok=True)
    clean_text_path.write_text(clean_text, encoding="utf-8")

    write_export_manifest(
        raw_dir / "export_manifest.json",
        source="SuttaCentral Milindapañha",
        base_url=BASE_URL,
        index_url=INDEX_URL,
        refs=refs,
        output_path=clean_text_path,
        section_translations=section_translations,
    )

    if args.write_legacy_mirror:
        legacy_output = args.legacy_output.expanduser().resolve()
        legacy_output.parent.mkdir(parents=True, exist_ok=True)
        legacy_output.write_text(clean_text, encoding="utf-8")

    print(f"Sections exported: {len(refs)}")
    print(f"Clean text: {clean_text_path}")
    print(f"Manifest: {raw_dir / 'export_manifest.json'}")


if __name__ == "__main__":
    main()
