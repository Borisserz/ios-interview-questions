#!/usr/bin/env python3
"""Spoken-deck v1: storefront stays small, decks hide answers, RU lives in docs/ru."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_readme as gen  # noqa: E402


STARTER = "identity-vs-equality"


class StorefrontTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cards = gen.parse_cards()
        cls.ru = gen.load_ru_cards()
        cls.en = gen.render(cls.cards, "en", cls.ru)
        cls.ru_page = gen.render(cls.cards, "ru", cls.ru)

    def test_storefront_has_no_stretch_png(self) -> None:
        self.assertNotIn("stretch.png", self.en)
        self.assertNotIn("stretch.png", self.ru_page)

    def test_storefront_under_80kb(self) -> None:
        self.assertLess(len(self.en.encode()), 80_000)
        self.assertLess(len(self.ru_page.encode()), 80_000)

    def test_storefront_features_study_site(self) -> None:
        site = "https://borisserz.github.io/ios-interview-questions/"
        self.assertIn(site, self.en)
        self.assertIn(site, self.ru_page)
        self.assertIn("assets/readme/site-banner.svg", self.en)
        self.assertIn("assets/readme/site-banner.ru.svg", self.ru_page)
        self.assertIn('id="study-site"', self.en)
        self.assertIn('id="study-site"', self.ru_page)
        self.assertLess(self.en.find(site), self.en.find("## How to study"))
        self.assertLess(self.ru_page.find(site), self.ru_page.find(f"## {gen.ru.HOW_TITLE}"))
        self.assertTrue((ROOT / "assets/readme/site-banner.svg").is_file())
        self.assertTrue((ROOT / "assets/readme/site-banner.ru.svg").is_file())
        self.assertIn(f"<code>{site}</code>", self.en)
        self.assertIn(f"<code>{site}</code>", self.ru_page)

    def test_storefront_links_to_locale_decks(self) -> None:
        self.assertIn("docs/en/swift.md", self.en)
        self.assertIn("docs/ru/swift.md", self.ru_page)

    def test_high_frequency_is_index_not_second_deck(self) -> None:
        self.assertLessEqual(self.en.count("Show answer and Swift"), 1)
        self.assertLessEqual(self.ru_page.count("Показать ответ и Swift"), 1)
        self.assertIn(f"docs/en/swift.md#{STARTER}", self.en)
        self.assertIn(f"docs/ru/swift.md#{STARTER}", self.ru_page)

    def test_starter_card_is_visible_with_details(self) -> None:
        self.assertIn(f'id="{STARTER}"', self.en)
        self.assertIn("<details>", self.en)
        self.assertIn("== vs ===", self.en)

    def test_paths_are_linked(self) -> None:
        self.assertIn("paths/7-day-mid.md", self.en)
        self.assertIn("paths/junior-high-freq.md", self.en)
        self.assertIn("paths/14-day-senior.md", self.en)


class DeckCardTests(unittest.TestCase):
    def test_deck_card_uses_html_heading_and_details(self) -> None:
        card = {
            "file": "swift.md",
            "title": "== vs ===",
            "slug": STARTER,
            "level": "Junior",
            "freq": "High",
            "kind": "Spoken",
            "answer": "Equal values vs same instance.",
            "example": "```swift\n1 == 1\n```",
            "follow-ups": "- Why?",
            "prompt": "",
        }
        html = gen.render_deck_card(card, "en")
        self.assertIn(f'<h2 id="{STARTER}">', html)
        self.assertIn("<details>", html)
        self.assertIn("Show answer and Swift", html)
        self.assertNotIn("stretch.png", html)
        self.assertIn("Equal values vs same instance.", html)

    def test_deck_groups_by_level_and_hides_answers(self) -> None:
        cards = [
            {
                "file": "swift.md",
                "title": "A",
                "slug": "a",
                "level": "Senior",
                "freq": "Low",
                "kind": "Spoken",
                "answer": "senior-secret",
                "example": "",
                "follow-ups": "",
                "prompt": "",
            },
            {
                "file": "swift.md",
                "title": "B",
                "slug": "b",
                "level": "Junior",
                "freq": "High",
                "kind": "Spoken",
                "answer": "junior-secret",
                "example": "",
                "follow-ups": "",
                "prompt": "",
            },
        ]
        text = gen.render_deck("swift.md", "Swift", cards, "en")
        self.assertLess(text.index("### Junior"), text.index("### Senior"))
        self.assertIn('<h2 id="a">', text)
        self.assertIn('<h2 id="b">', text)
        self.assertGreater(text.count("<details>"), 1)

    def test_ru_deck_uses_overlay_answer(self) -> None:
        card = {
            "file": "swift.md",
            "title": "== vs ===",
            "slug": STARTER,
            "level": "Junior",
            "freq": "High",
            "kind": "Spoken",
            "answer": "English body",
            "example": "",
            "follow-ups": "",
            "prompt": "",
        }
        localized = gen.localize_card(
            card, "ru", {STARTER: {"title": "Равенство", "answer": "Русский ответ"}}
        )
        html = gen.render_deck_card(localized, "ru")
        self.assertIn("Русский ответ", html)
        self.assertIn("Показать ответ и Swift", html)
        self.assertNotIn("English body", html)


class WriteDecksTests(unittest.TestCase):
    def test_write_decks_emits_en_and_ru_files(self) -> None:
        cards = gen.parse_cards()
        ru = gen.load_ru_cards()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            written = gen.write_decks(cards, ru, root)
            swift_en = root / "docs" / "en" / "swift.md"
            swift_ru = root / "docs" / "ru" / "swift.md"
            self.assertTrue(swift_en.is_file())
            self.assertTrue(swift_ru.is_file())
            en_text = swift_en.read_text(encoding="utf-8")
            ru_text = swift_ru.read_text(encoding="utf-8")
            self.assertIn(f'<h2 id="{STARTER}">', en_text)
            self.assertIn("<details>", en_text)
            self.assertIn("<details>", ru_text)
            self.assertGreaterEqual(len(written), 2 * len(gen.TOPIC_ORDER))


class SiteAppTests(unittest.TestCase):
    def test_pages_shell_points_at_generated_json(self) -> None:
        html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        self.assertIn("./data/cards.json", js)
        self.assertIn("./app.js?", html)
        self.assertIn("./app.css?", html)
        self.assertIn("./tokens.css?", html)
        self.assertIn('class="back"', js)
        self.assertIn("topic-block", js)
        self.assertIn("matchesTopic", js)
        self.assertIn("card.frequent", js)
        css = (ROOT / "docs" / "app.css").read_text(encoding="utf-8")
        self.assertIn("margin: 0 auto", css)
        self.assertIn("max-width: var(--page)", css)
        self.assertIn("toolbar-controls", js)
        self.assertIn("saveGrade", js)
        self.assertIn("splitGist", js)
        self.assertIn("DATA.paths", js)
        self.assertIn('=== "practice"', js)
        self.assertIn(".grades", css)
        self.assertIn(".gist", css)
        self.assertIn(".timer", css)
        self.assertTrue((ROOT / "docs" / ".nojekyll").exists())

    def test_session_size_is_user_chosen(self) -> None:
        js = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        self.assertIn("function parseCap", js)
        self.assertIn('name="cap"', js)
        self.assertNotIn('filters.cap === "12"', js)
        self.assertIn("session-size", js)

    def test_all_includes_practice_named_topics_do_not(self) -> None:
        js = (ROOT / "docs" / "app.js").read_text(encoding="utf-8")
        all_idx = js.index('if (topicId === "all") return true;')
        skip_idx = js.index("if (isPractice(card)) return false;")
        self.assertLess(all_idx, skip_idx)


class SiteCardsTests(unittest.TestCase):
    def test_frequent_slugs_exist_and_are_flagged(self) -> None:
        cards = gen.parse_cards()
        slugs = {card["slug"] for card in cards}
        missing = sorted(set(gen.FREQUENT_SLUGS) - slugs)
        self.assertEqual(missing, [])
        payload = json.loads(gen.render_site_cards(cards))
        self.assertEqual(payload["topics"][0]["id"], "frequent")
        self.assertEqual(payload["topics"][1]["id"], "practice")
        flagged = {card["slug"] for card in payload["cards"] if card.get("frequent")}
        self.assertEqual(flagged, set(gen.FREQUENT_SLUGS))
        self.assertIn(STARTER, flagged)

    def test_practice_topic_and_paths_are_in_site_json(self) -> None:
        cards = gen.parse_cards()
        payload = json.loads(gen.render_site_cards(cards))
        ids = [topic["id"] for topic in payload["topics"]]
        self.assertEqual(ids[:2], ["frequent", "practice"])
        practice = [card for card in payload["cards"] if card.get("practice")]
        self.assertEqual(len(practice), sum(1 for card in cards if card["kind"] == "Practice"))
        self.assertTrue(all(card["kind"] == "Practice" for card in practice))
        self.assertIn("chat-app", {card["slug"] for card in practice})
        path_ids = [path["id"] for path in payload["paths"]]
        self.assertEqual(path_ids, ["junior-high-freq", "7-day-mid", "14-day-senior"])
        junior = next(path for path in payload["paths"] if path["id"] == "junior-high-freq")
        self.assertGreaterEqual(len(junior["sessions"]), 6)
        self.assertIn(STARTER, junior["sessions"][0]["slugs"])

    def test_site_cards_json_has_starter_and_all_cards(self) -> None:
        cards = gen.parse_cards()
        payload = json.loads(gen.render_site_cards(cards))
        self.assertEqual(len(payload["cards"]), len(cards))
        by_slug = {card["slug"]: card for card in payload["cards"]}
        self.assertIn(STARTER, by_slug)
        starter = by_slug[STARTER]
        self.assertEqual(starter["topicId"], "swift")
        self.assertEqual(starter["topic"], "Swift")
        self.assertIn("==", starter["title"])
        self.assertTrue(starter["answer"])
        self.assertIn("level", starter)
        self.assertIn("kind", starter)

    def test_generated_texts_includes_cards_json(self) -> None:
        cards = gen.parse_cards()
        ru = gen.load_ru_cards()
        texts = gen.generated_texts(cards, ru)
        self.assertIn("docs/data/cards.json", texts)
        payload = json.loads(texts["docs/data/cards.json"])
        self.assertEqual(len(payload["cards"]), 458)

    def test_write_decks_does_not_delete_site_data(self) -> None:
        cards = gen.parse_cards()
        ru = gen.load_ru_cards()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            data = root / "docs" / "data"
            data.mkdir(parents=True)
            keep = data / "cards.json"
            keep.write_text("keep-me", encoding="utf-8")
            gen.write_decks(cards, ru, root)
            self.assertEqual(keep.read_text(encoding="utf-8"), "keep-me")


if __name__ == "__main__":
    unittest.main()
