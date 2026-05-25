import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dialogue_source_manifest import (
    approved_source_labels,
    source_labels_for_family,
)
from parse_asclepius import infer_speaker as infer_asclepius_speaker
from parse_dhammapada_commentary import extract_turns_from_paragraph
from parse_majjhima_nikaya import build_rows, extract_turns, parse_page
from parse_vimalakirti import (
    Turn as VimalakirtiTurn,
    conversation_window_for_target,
    extract_turn_from_paragraph,
)


class DialogueSourceManifestTest(unittest.TestCase):
    def test_manifest_lists_new_buddhist_and_esoteric_sources(self) -> None:
        buddhist = source_labels_for_family("buddhist")
        esoteric = source_labels_for_family("esoteric")

        self.assertIn("Majjhima Nikaya", buddhist)
        self.assertIn("Itivuttaka", buddhist)
        self.assertIn("Zen Koans Database", buddhist)
        self.assertIn("Vimalakirti Nirdesa Sutra", buddhist)
        self.assertIn("Asclepius", esoteric)

        approved = approved_source_labels()
        self.assertIn("The Key to Theosophy", approved)
        self.assertIn("The Corpus Hermeticum", approved)
        self.assertIn("Asclepius", approved)


class VimalakirtiParserTest(unittest.TestCase):
    def test_extracts_leading_speaker_quote(self) -> None:
        speaker, addressee, quote = extract_turn_from_paragraph(
            'The Buddha said, "Noble sons, a Buddha-field of bodhisattvas is a field of living beings."'
        )

        self.assertEqual(speaker, "The Buddha")
        self.assertIsNone(addressee)
        self.assertEqual(
            quote,
            "Noble sons, a Buddha-field of bodhisattvas is a field of living beings.",
        )

    def test_extracts_trailing_attribution_quote(self) -> None:
        speaker, addressee, quote = extract_turn_from_paragraph(
            '"Very good, Lord," replied Ratnakara and the five hundred young Licchavis.'
        )

        self.assertEqual(speaker, "Ratnakara")
        self.assertIsNone(addressee)
        self.assertEqual(quote, "Very good, Lord,")

    def test_extracts_colon_delimited_speaker_turn(self) -> None:
        speaker, addressee, quote = extract_turn_from_paragraph(
            "Vimalakirti: Until is it digested."
        )

        self.assertEqual(speaker, "Vimalakirti")
        self.assertIsNone(addressee)
        self.assertEqual(quote, "Until is it digested.")

    def test_conversation_window_stays_with_local_exchange(self) -> None:
        turns = [
            VimalakirtiTurn("Ratnakara", "Very good, Lord,", 376, 377, 0),
            VimalakirtiTurn(
                "The Buddha",
                "What do you think, Shariputra? Is it because the sun and moon are impure that those blind from birth do not see them?",
                500,
                502,
                1,
            ),
            VimalakirtiTurn(
                "Shariputra",
                "No, Lord. It is not so. The fault lies with those blind from birth, and not with the sun and moon.",
                505,
                506,
                2,
            ),
            VimalakirtiTurn(
                "The Buddha",
                "In the same way, Shariputra, the fact that some living beings do not behold the splendid display of virtues of the Buddha-field of the Tathágata is due to their own ignorance.",
                509,
                512,
                3,
            ),
        ]

        history = conversation_window_for_target(turns, 3)

        self.assertIsNotNone(history)
        self.assertEqual([turn.speaker for turn in history], ["The Buddha", "Shariputra"])


class AsclepiusParserTest(unittest.TestCase):
    def test_infers_asclepius_when_addressing_trismegistus(self) -> None:
        quote = "Why was it necessary, O Trismegistus, that Man be placed in the world?"
        self.assertEqual(
            infer_asclepius_speaker(quote, previous_speaker="Hermes"),
            "Asclepius",
        )

    def test_infers_hermes_when_addressing_asclepius(self) -> None:
        quote = "Yes, statues, Asclepius. Do you see how you lack faith?"
        self.assertEqual(
            infer_asclepius_speaker(quote, previous_speaker="Asclepius"),
            "Hermes",
        )


class DhammapadaCommentaryParserTest(unittest.TestCase):
    def test_extracts_dash_delimited_dialogue_sequence(self) -> None:
        paragraph = (
            'The Teacher asked him: "Have you no kinsman of whom it is proper that you '
            'should ask leave?" – "Why yes, venerable Sir, I have a younger brother." – '
            '"Well then, ask him." To this Mahā Pāla agreed, and said: "Very well."'
        )

        turns = extract_turns_from_paragraph(paragraph)

        self.assertEqual(
            turns,
            [
                ("The Buddha", "Have you no kinsman of whom it is proper that you should ask leave?"),
                ("Mahā Pāla", "Why yes, venerable Sir, I have a younger brother."),
                ("The Buddha", "Well then, ask him."),
                ("Mahā Pāla", "Very well."),
            ],
        )


class MajjhimaNikayaParserTest(unittest.TestCase):
    def test_quote_only_exchange_uses_local_saccaka_pair(self) -> None:
        page = parse_page(
            Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN35.html")
        )

        turns = {
            turn.start_line: turn
            for turn in extract_turns(page)
            if turn.start_line in {230, 231, 232, 237, 238, 239, 240, 241}
        }

        self.assertEqual(turns[230].speaker, "Saccaka")
        self.assertEqual(turns[231].speaker, "The Buddha")
        self.assertEqual(turns[232].speaker, "Saccaka")
        self.assertEqual(turns[237].speaker, "The Buddha")
        self.assertEqual(turns[238].speaker, "Saccaka")
        self.assertEqual(turns[239].speaker, "The Buddha")
        self.assertEqual(turns[240].speaker, "Saccaka")
        self.assertEqual(turns[241].speaker, "The Buddha")

    def test_explicit_blessed_one_quote_stays_with_buddha(self) -> None:
        page = parse_page(
            Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN67.html")
        )

        turns = {turn.start_line: turn for turn in extract_turns(page) if 220 <= turn.start_line <= 224}

        self.assertEqual(turns[221].speaker, "The Buddha")
        self.assertEqual(turns[222].speaker, "Ven. Sāriputta")
        self.assertEqual(turns[223].speaker, "The Buddha")
        self.assertEqual(turns[224].speaker, "Ven. Moggallāna")

    def test_build_rows_drops_known_scene_jump_rows(self) -> None:
        pages = [
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN12.html")
            ),
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN36.html")
            ),
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN97.html")
            ),
        ]

        rows = build_rows(
            pages,
            history_turns=8,
            min_target_words=20,
            max_target_words=260,
        )
        record_ids = {row["metadata"]["record_id"] for row in rows}

        self.assertNotIn(
            "mn12-html:majjhima_nikaya_next_reply_12_2:204-271:ven-s-riputta",
            record_ids,
        )
        self.assertNotIn(
            "mn36-html:majjhima_nikaya_next_reply_36_20:242-263:ven-nanda",
            record_ids,
        )
        self.assertNotIn(
            "mn97-html:majjhima_nikaya_next_reply_97_9:230-259:the-buddha",
            record_ids,
        )

    def test_build_rows_recovers_known_good_dialogue_families(self) -> None:
        pages = [
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN31.html")
            ),
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN43.html")
            ),
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN64.html")
            ),
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN95.html")
            ),
        ]

        rows = build_rows(
            pages,
            history_turns=8,
            min_target_words=20,
            max_target_words=260,
        )
        by_page = {}
        for row in rows:
            by_page.setdefault(row["metadata"]["source_file"], []).append(row)

        self.assertGreaterEqual(len(by_page), 3)
        self.assertIn("MN64.html", by_page)
        self.assertIn("MN95.html", by_page)

        self.assertTrue(
            any(row["metadata"]["target_speaker"] in {"Māluṅkyaputta", "Ven. Māluṅkyaputta", "Ven. Ānanda"} for row in by_page["MN64.html"])
        )
        self.assertTrue(
            any(row["metadata"]["target_speaker"] in {"The Buddha", "Bhāradvāja", "brahman Caṅkī"} for row in by_page["MN95.html"])
        )

    def test_extract_turns_rejects_generic_clause_openers_as_speakers(self) -> None:
        pages = [
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN44.html")
            ),
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN109.html")
            ),
            parse_page(
                Path("source_texts/buddhist/raw/majjhima_nikaya_dhammatalks/pages/MN119.html")
            ),
        ]

        leaked = {
            turn.speaker
            for page in pages
            for turn in extract_turns(page)
            if turn.speaker
            in {
                "As",
                "Are",
                "Dhamma",
                "For",
                "From",
                "He",
                "Inconstant",
                "Listen",
                "Responding",
                "Saying",
                "Suppose",
                "Whatever",
            }
        }

        self.assertEqual(leaked, set())


if __name__ == "__main__":
    unittest.main()
