from pathlib import Path

from tools.source_ingest.fetch_milinda_suttacentral import (
    cached_page_path,
    discover_section_refs,
    extract_html_from_bilarasutta_payload,
    find_translation_entry,
    parse_suttacentral_page,
    render_consolidated_text,
    translation_payload_url,
)


def test_discover_section_refs_reads_mil_ids_from_index_fixture() -> None:
    fixture = Path("tests/fixtures/milinda_suttacentral/index.html")
    refs = discover_section_refs(fixture.read_text(encoding="utf-8"))

    assert "mil3.1.1" in refs
    assert "mil3.2.1" in refs
    assert refs == sorted(set(refs))


def test_discover_section_refs_reads_mil_ids_from_suttaplex_json() -> None:
    payload = """
    [
      {"uid": "mil"},
      {"uid": "mil3"},
      {"uid": "mil3.2.1"},
      {"uid": "dn1"},
      {"uid": "mil3.1.1"}
    ]
    """

    refs = discover_section_refs(payload)

    assert refs == ["mil3.1.1", "mil3.2.1"]


def test_render_consolidated_text_keeps_headings_and_dialogue() -> None:
    page_one = parse_suttacentral_page(
        "mil3.1.1",
        Path("tests/fixtures/milinda_suttacentral/mil3.1.1.html").read_text(
            encoding="utf-8"
        ),
    )
    page_two = parse_suttacentral_page(
        "mil3.2.1",
        Path("tests/fixtures/milinda_suttacentral/mil3.2.1.html").read_text(
            encoding="utf-8"
        ),
    )

    text = render_consolidated_text([page_one, page_two])

    assert "## mil3.1.1" in text
    assert "King Milinda" in text
    assert "unsupported browser" not in text.lower()
    assert 'Nāgasena replied, "People know me as Nāgasena, great king."' in text
    assert 'King Milinda asked, "Is Nāgasena your permanent self?"' in text
    assert "NÄ" not in text
    assert "â€" not in text


def test_parse_suttacentral_page_reads_translation_text_from_sutta_json() -> None:
    payload = """
    {
      "mil3.1.1:0.1": "King Milinda said, \\"Who are you, venerable sir?\\"",
      "mil3.1.1:0.2": "NÄgasena replied, \\"People know me as NÄgasena, great king.\\""
    }
    """

    page = parse_suttacentral_page("mil3.1.1", payload)
    text = render_consolidated_text([page])

    assert "## mil3.1.1" in text
    assert 'King Milinda said, "Who are you, venerable sir?"' in text
    assert 'Nāgasena replied, "People know me as Nāgasena, great king."' in text


def test_parse_suttacentral_page_reads_title_and_text_from_bilara_payload() -> None:
    payload = """
    {
      "_meta": {
        "title": "The Opening Question"
      }
    ,
      "mil3.1.1:0.1": "Then, King Milinda approached NÄgasena.",
      "mil3.1.1:0.2": "How is the reverend one known?"
    }
    """

    page = parse_suttacentral_page("mil3.1.1", payload)
    text = render_consolidated_text([page])

    assert "## mil3.1.1" in text
    assert "### The Opening Question" in text
    assert "Then, King Milinda approached Nāgasena." in text
    assert "How is the reverend one known?" in text


def test_parse_suttacentral_page_reads_html_from_api_payload() -> None:
    payload = """
    {
      "suttaplex": {
        "uid": "mil3.1.1",
        "translated_title": "The Question on Conventional Names"
      },
      "translation": {
        "title": "Individuality and name; the chariot simile",
        "text": "<!DOCTYPE html><html><body><article id='mil3.1.1'><header><ul><li class='division'>The Questions of King Milinda</li></ul><h1>3.1.1. Individuality and name; the chariot simile</h1></header><p><a class='ref pts-vp-en' href='#pts-vp-en40'>PTS vp En 40</a>Now Milinda the king went up to where the venerable NÃ„Âgasena was.</p><p>And Milinda began by asking, â€˜How is your Reverence known?â€™</p><footer><p>This text is in the public domain.</p></footer></article></body></html>"
      }
    }
    """

    page = parse_suttacentral_page("mil3.1.1", payload)

    assert page.headings == ["The Questions of King Milinda"]
    assert page.title == "3.1.1. Individuality and name; the chariot simile"
    assert page.paragraphs == [
        "Now Milinda the king went up to where the venerable Nāgasena was.",
        "And Milinda began by asking, 'How is your Reverence known?'",
    ]


def test_translation_payload_url_uses_bilarasutta_api_for_segmented_text() -> None:
    url = translation_payload_url(
        "mil3.1.1",
        {
            "lang": "en",
            "author_uid": "kelly",
            "id": "mil3.1.1_translation-en-kelly",
            "segmented": True,
        },
    )

    assert url.endswith("/api/bilarasuttas/mil3.1.1/kelly?lang=en")


def test_translation_payload_url_uses_sutta_api_for_legacy_text() -> None:
    url = translation_payload_url(
        "mil3.1.1",
        {
            "lang": "en",
            "author_uid": "tw_rhysdavids",
            "id": "en_mil3.1.1_tw_rhysdavids",
            "segmented": False,
        },
    )

    assert url.endswith("/api/suttas/mil3.1.1/tw_rhysdavids")


def test_extract_html_from_bilarasutta_payload_reconstructs_page_html() -> None:
    payload = """
    {
      "html_text": {
        "mil3.1.1:0.1": "<article><header><ul><li class='division'>{}</li>",
        "mil3.1.1:0.2": "<li>{}</li></ul><h1>{}</h1></header>",
        "mil3.1.1:1.1": "<p>{}</p></article>"
      },
      "translation_text": {
        "mil3.1.1:0.1": "Milindaâ€™s Questions",
        "mil3.1.1:0.2": "Great Chapter",
        "mil3.1.1:1.1": "King Milinda spoke."
      },
      "keys_order": [
        "mil3.1.1:0.1",
        "mil3.1.1:0.2",
        "mil3.1.1:1.1"
      ]
    }
    """

    html = extract_html_from_bilarasutta_payload(payload)

    assert "<li class='division'>Milindaâ€™s Questions</li>" in html
    assert "<li>Great Chapter</li>" in html
    assert "<p>King Milinda spoke.</p>" in html


def test_parse_suttacentral_page_keeps_bilara_segment_order() -> None:
    payload = """
    {
      "_meta": {
        "title": "Ordered Sections"
      },
      "mil3.1.1:0.1": "Opening line",
      "mil3.1.1:10.1": "Tenth line",
      "mil3.1.1:2.1": "Second line"
    }
    """

    page = parse_suttacentral_page("mil3.1.1", payload)

    assert page.paragraphs == ["Opening line", "Second line", "Tenth line"]


def test_find_translation_entry_falls_back_when_kelly_is_missing() -> None:
    payload = """
    [
      {
        "uid": "mil5.1.10",
        "translations": [
          {
            "author_uid": "tw_rhysdavids",
            "id": "en_mil5.1.10_tw_rhysdavids",
            "lang": "en",
            "segmented": false
          }
        ]
      }
    ]
    """

    entry = find_translation_entry(
        payload,
        section_ref="mil5.1.10",
        translation="kelly",
    )

    assert entry["author_uid"] == "tw_rhysdavids"
    assert entry["id"] == "en_mil5.1.10_tw_rhysdavids"
    assert entry["segmented"] is False


def test_cached_page_path_is_translation_stable() -> None:
    raw_dir = Path("tests/fixtures/milinda_suttacentral")
    kelly_path = cached_page_path(raw_dir, "mil3.1.1", "kelly")
    rhysdavids_path = cached_page_path(raw_dir, "mil3.1.1", "tw_rhysdavids")

    assert kelly_path != rhysdavids_path
    assert kelly_path.name == "mil3.1.1.html"
    assert rhysdavids_path.name == "mil3.1.1.html"
    assert kelly_path.parent.name == "kelly"
    assert rhysdavids_path.parent.name == "tw_rhysdavids"
