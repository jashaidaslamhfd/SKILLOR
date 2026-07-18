"""Fast, offline regression tests for the production-critical content rules."""
import unittest

from script_generator import _normalize_scenes, validate_script
from seo_generator import generate_seo_package
from shorts_enhancer import score_hook
from trend_fetcher import _deduplicate, _is_relevant


class ScriptPolicyTests(unittest.TestCase):
    def setUp(self):
        self.script = _normalize_scenes({
            "title": "Why Sleep Helps Your Brain",
            "thumbnail_text": "Memory Reset",
            "hook": "Your brain saves memories while sleeping.",
            "cta": "Follow for more science made simple.",
            "description": "Sleep helps your brain strengthen important memories.",
            "scenes": [
                {"visual": "glowing brain during deep sleep", "caption": "Your brain saves important memories while sleeping."},
                {"visual": "memory signals moving through neurons", "caption": "But how does your brain decide what to keep overnight?"},
                {"visual": "student studying in a quiet room", "caption": "Without restful sleep, new information is harder to organize and recall."},
                {"visual": "brain pathways strengthening overnight", "caption": "During deep sleep, important neural connections become stronger and more stable."},
                {"visual": "calm sleeper with brain overlay", "caption": "That process helps turn today's learning into tomorrow's useful long-term memory."},
                {"visual": "morning light over focused person", "caption": "So sleep is when your brain saves what matters most."},
            ],
        })

    def test_script_matches_the_unified_short_policy(self):
        valid, issues = validate_script(self.script)
        self.assertTrue(valid, issues)
        words = len(self.script["voiceover"].split())
        self.assertGreaterEqual(words, 60)
        self.assertLessEqual(words, 78)
        self.assertEqual(len(self.script["scenes"]), 6)

    def test_hook_passes_natural_hook_gate(self):
        self.assertGreaterEqual(score_hook(self.script)["score"], 70)


class SeoPolicyTests(unittest.TestCase):
    def test_titles_tags_and_thumbnail_are_topic_specific(self):
        script = {
            "title": "Why Sleep Helps Your Brain",
            "thumbnail_text": "Memory Reset",
            "hook": "Your brain saves memories while sleeping.",
            "cta": "Follow for more science made simple.",
            "description": "Sleep helps your brain strengthen important memories.",
            "summary": "Sleep helps your brain strengthen important memories.",
        }
        package = generate_seo_package("How sleep helps your brain make memories", script)
        self.assertTrue(all(len(title.split()) <= 5 for title in package["title_options"]))
        self.assertEqual(package["thumbnail_text"], "MEMORY RESET")
        self.assertNotIn("helps", [tag.lower() for tag in package["tags"]])
        self.assertEqual(
            [tag.lower() for tag in package["hashtags"]],
            ["#sleepscience", "#sleepandmemory", "#memoryformation"],
        )


class TrendSafetyTests(unittest.TestCase):
    def test_irrelevant_football_hearts_title_is_not_body_science(self):
        self.assertFalse(_is_relevant("Hearts - Rayo Vallecano"))
        self.assertTrue(_is_relevant("NASA releases a new space image"))

    def test_topic_deduplication_ignores_case_and_punctuation(self):
        records = _deduplicate([
            {"topic": "Brain Science"},
            {"topic": "brain-science"},
        ])
        self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
