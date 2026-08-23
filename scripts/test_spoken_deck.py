#!/usr/bin/env python3
"""Spoken-deck v1: storefront stays small, decks hide answers, RU lives in docs/ru."""

from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
