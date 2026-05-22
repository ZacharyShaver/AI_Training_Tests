import unittest

from parse_zen_koans_database import KoanStory, story_history_turns, story_to_dialogue_rows


class ZenKoansDatabaseParserTest(unittest.TestCase):
    def test_split_quote_attribution_is_merged_without_narration(self) -> None:
        story = KoanStory(
            slug="reciting_sutras.txt",
            title="Reciting Sutras",
            source_file="reciting_sutras.html",
            paragraphs=[
                (
                    "A farmer requested a Tendai priest to recite sutras for his wife, who "
                    'had died. After the recitation was over the farmer asked: "Do you think '
                    'my wife will gain merit from this?"'
                ),
                (
                    '"Not only your wife, but all sentient beings will benefit from the '
                    'recitation of sutras," answered the priest.'
                ),
                (
                    '"If you say all sentient beings will benefit," said the farmer, "my '
                    "wife may be very weak and others will take advantage of her, getting "
                    'the benefit she should have. So please recite sutras just for her."'
                ),
            ],
        )

        rows = story_to_dialogue_rows(
            story,
            history_turns=3,
            min_target_words=2,
            max_target_words=120,
        )
        farmer_rows = [
            row
            for row in rows
            if row["metadata"]["target_speaker"] == "Farmer"
            and row["messages"][2]["content"].startswith("If you say")
        ]

        self.assertEqual(len(farmer_rows), 1)
        self.assertIn(
            "So please recite sutras just for her.",
            farmer_rows[0]["messages"][2]["content"],
        )
        self.assertNotIn("Narrator", farmer_rows[0]["messages"][1]["content"])
        self.assertNotIn("Quoted speaker", farmer_rows[0]["messages"][1]["content"])

    def test_named_monologue_story_does_not_become_dialogue_rows(self) -> None:
        story = KoanStory(
            slug="the_thief_who_became_a_disciple.txt",
            title="The Thief Who Became A Disciple",
            source_file="the_thief_who_became_a_disciple.html",
            paragraphs=[
                (
                    "One evening as Shichiri Kojun was reciting sutras a thief with a sharp "
                    "sword entered, demanding wither his money or his life."
                ),
                (
                    'Shichiri told him: "Do not disturb me. You can find the money in that '
                    'drawer." Then he resumed his recitation.'
                ),
                (
                    'A little while afterwards he stopped and called: "Don\'t take it all. '
                    'I need some to pay taxes with tomorrow."'
                ),
                (
                    'The intruder gathered up most of the money and started to leave. "Thank '
                    'a person when you receive a gift," Shichiri added. The man thanked him '
                    "and made off."
                ),
                (
                    "A few days afterwards the fellow was caught and confessed, among others, "
                    'the offense against Shichiri. When Shichiri was called as a witness he said: '
                    '"This man is no thief, at least as far as I am concerned. I gave him the '
                    'money and he thanked me for it."'
                ),
            ],
        )

        turns = story_history_turns(story.paragraphs)
        quoted_turns = [turn for turn in turns if turn.speaker != "Narrator"]
        self.assertTrue(quoted_turns)
        self.assertEqual({turn.speaker for turn in quoted_turns}, {"Shichiri"})

        rows = story_to_dialogue_rows(
            story,
            history_turns=3,
            min_target_words=2,
            max_target_words=120,
        )
        self.assertEqual(rows, [])


if __name__ == "__main__":
    unittest.main()
