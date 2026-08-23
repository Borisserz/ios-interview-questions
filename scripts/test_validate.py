#!/usr/bin/env python3
"""Card schema, RU coverage, and generated-file freshness."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_readme as gen  # noqa: E402
import validate  # noqa: E402


def spoken(slug: str = "x", **overrides) -> dict:
    card = {
        "file": "swift.md",
        "title": "X",
        "slug": slug,
        "level": "Junior",
        "freq": "High",
        "kind": "Spoken",
        "answer": "a",
        "example": "",
        "follow-ups": "",
        "prompt": "",
    }
    card.update(overrides)
    return card


class SchemaTests(unittest.TestCase):
    def test_unknown_level_is_error(self) -> None:
        errors = validate.schema_errors([spoken(level="Staff")])
        self.assertTrue(any("level" in err.lower() or "Staff" in err for err in errors))

    def test_duplicate_slug_is_error(self) -> None:
        errors = validate.schema_errors([spoken("dup"), spoken("dup", file="memory.md")])
        self.assertTrue(any("dup" in err for err in errors))

    def test_missing_ru_overlay_is_error(self) -> None:
        errors = validate.locale_errors([spoken("no-ru")], {})
        self.assertTrue(any("no-ru" in err for err in errors))

    def test_valid_card_set_is_clean(self) -> None:
        card = spoken("ok")
        self.assertEqual(validate.schema_errors([card]), [])
        self.assertEqual(validate.locale_errors([card], {"ok": {"answer": "да"}}), [])


class RepoTests(unittest.TestCase):
    def test_current_repo_has_no_errors(self) -> None:
        self.assertEqual(validate.collect_errors(ROOT), [])

    def test_generated_outputs_match_check(self) -> None:
        self.assertEqual(gen.check_generated(ROOT), [])

    def test_path_files_exist(self) -> None:
        for name in ("junior-high-freq.md", "7-day-mid.md", "14-day-senior.md"):
            self.assertTrue((ROOT / "paths" / name).is_file(), name)


if __name__ == "__main__":
    unittest.main()
