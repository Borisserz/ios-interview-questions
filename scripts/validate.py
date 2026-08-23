#!/usr/bin/env python3
"""Fail the build if cards, RU overlays, or generated files drift."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_readme as gen

LEVELS = set(gen.LEVELS)
FREQS = {"High", "Medium", "Low"}
KINDS = {"Spoken", "Practice"}
H2 = re.compile(r"^## ")
HEADING = gen.HEADING


def schema_errors(cards: list[dict]) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    for card in cards:
        slug = card["slug"]
        loc = f"{card['file']}#{slug}"
        if card["level"] not in LEVELS:
            errors.append(f"{loc}: bad Level {card['level']!r}")
        if card["freq"] not in FREQS:
            errors.append(f"{loc}: bad Frequency {card['freq']!r}")
        if card["kind"] not in KINDS:
            errors.append(f"{loc}: bad Kind {card['kind']!r}")
        if slug in seen:
            errors.append(f"duplicate slug {slug!r} in {seen[slug]} and {loc}")
        else:
            seen[slug] = loc
    return errors


def locale_errors(cards: list[dict], ru_cards: dict[str, dict]) -> list[str]:
    errors: list[str] = []
    slugs = {card["slug"] for card in cards}
    for card in cards:
        if card["slug"] not in ru_cards:
            errors.append(f"missing RU overlay for {card['file']}#{card['slug']}")
    extra = sorted(set(ru_cards) - slugs)
    for slug in extra:
        errors.append(f"extra RU overlay with no English card: {slug}")
    return errors


def source_heading_errors(root: Path) -> list[str]:
    errors: list[str] = []
    known = {name for name, _label, _anchor in gen.TOPIC_ORDER}
    topics = root / "topics"
    for path in sorted(topics.glob("*.md")):
        if path.name.endswith(".ru.md"):
            continue
        if path.name not in known:
            errors.append(f"{path.relative_to(root)} is not in TOPIC_ORDER")
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if H2.match(line) and not HEADING.match(line):
                errors.append(f"{path.name}:{lineno}: H2 missing {{#slug}}: {line}")
    return errors


def ru_json_errors(root: Path) -> list[str]:
    errors: list[str] = []
    seen: dict[str, str] = {}
    locales = root / "locales" / "ru"
    if not locales.is_dir():
        return ["locales/ru is missing"]
    for path in sorted(locales.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            errors.append(f"{path.name} must be a JSON object keyed by slug")
            continue
        for slug in data:
            if slug in seen:
                errors.append(f"RU slug {slug!r} in both {seen[slug]} and {path.name}")
            else:
                seen[slug] = path.name
    return errors


def collect_errors(root: Path = ROOT) -> list[str]:
    cards = gen.parse_cards()
    ru_cards = gen.load_ru_cards()
    return [
        *schema_errors(cards),
        *locale_errors(cards, ru_cards),
        *source_heading_errors(root),
        *ru_json_errors(root),
        *gen.check_generated(root),
    ]


def main() -> None:
    errors = collect_errors(ROOT)
    if errors:
        print("validate failed:", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        raise SystemExit(1)
    print("validate ok")


if __name__ == "__main__":
    main()
