#!/usr/bin/env python3
"""Rebuild README.md and README.ru.md from topics/*.md and locales/ru/*.json."""

from __future__ import annotations

import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import locale_ru as ru

TOPICS = ROOT / "topics"
LOCALES = ROOT / "locales" / "ru"
README_EN = ROOT / "README.md"
README_RU = ROOT / "README.ru.md"

HEADING = re.compile(r"^## (.+?) \{#([^}]+)\}\s*$")
META = re.compile(r"^- (Level|Frequency|Kind): (.+)$")
SECTION = re.compile(r"^### (Answer|Example|Follow-ups|Prompt)\s*$")
LEVELS = ("Junior", "Mid", "Senior")

TOPIC_ORDER = [
    ("swift.md", "Swift", "swift"),
    ("memory.md", "Memory", "memory"),
    ("concurrency.md", "Concurrency", "concurrency"),
    ("architecture.md", "Architecture", "architecture"),
    ("uikit.md", "UIKit", "uikit"),
    ("swiftui.md", "SwiftUI", "swiftui"),
    ("combine.md", "Combine", "combine"),
    ("networking.md", "Networking", "networking"),
    ("persistence.md", "Persistence", "persistence"),
    ("performance.md", "Performance", "performance"),
    ("security.md", "Security", "security"),
    ("accessibility.md", "Accessibility", "accessibility"),
    ("frameworks.md", "Frameworks", "frameworks"),
    ("objc-runtime.md", "Objective-C runtime", "objc-runtime"),
    ("system-design.md", "System design", "system-design"),
    ("algorithms.md", "Algorithms", "algorithms"),
    ("behavioral.md", "Behavioral / process", "behavioral"),
]


def parse_cards() -> list[dict]:
    cards: list[dict] = []
    for path in sorted(TOPICS.glob("*.md")):
        if path.name.endswith(".ru.md"):
            continue
        current = None
        section: str | None = None
        buf: list[str] = []

        def flush_section() -> None:
            if current is None or section is None:
                return
            current[section.lower()] = "\n".join(buf).strip()

        for line in path.read_text(encoding="utf-8").splitlines():
            match = HEADING.match(line)
            if match:
                if current:
                    flush_section()
                    cards.append(current)
                current = {
                    "file": path.name,
                    "title": match.group(1),
                    "slug": match.group(2),
                    "level": None,
                    "freq": None,
                    "kind": "Spoken",
                    "answer": "",
                    "example": "",
                    "follow-ups": "",
                    "prompt": "",
                }
                section = None
                buf = []
                continue
            if current is None:
                continue
            meta = META.match(line)
            if meta:
                key, value = meta.group(1), meta.group(2).strip()
                if key == "Level":
                    current["level"] = value
                elif key == "Frequency":
                    current["freq"] = value
                elif key == "Kind":
                    current["kind"] = value
                continue
            sec = SECTION.match(line)
            if sec:
                flush_section()
                section = sec.group(1)
                buf = []
                continue
            if section:
                buf.append(line)
        if current:
            flush_section()
            cards.append(current)

    missing = [card for card in cards if not card["level"] or not card["freq"]]
    if missing:
        raise SystemExit(
            "cards missing Level or Frequency: "
            + ", ".join(f"{card['file']}#{card['slug']}" for card in missing)
        )
    return cards


def load_ru_cards() -> dict[str, dict]:
    merged: dict[str, dict] = {}
    if not LOCALES.is_dir():
        return merged
    for path in LOCALES.glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SystemExit(f"{path} must be a JSON object keyed by slug")
        merged.update(data)
    return merged


def localize_card(card: dict, locale: str, ru_cards: dict[str, dict]) -> dict:
    if locale != "ru":
        return card
    overlay = ru_cards.get(card["slug"], {})
    localized = dict(card)
    for key in ("title", "answer", "follow-ups", "prompt"):
        if overlay.get(key):
            localized[key] = overlay[key]
    return localized


def freq_key(card: dict) -> int:
    return {"High": 0, "Medium": 1, "Low": 2}.get(card["freq"], 9)


def topic_label(filename: str, locale: str) -> str:
    if locale == "ru":
        return ru.TOPICS.get(filename, filename.removesuffix(".md"))
    for name, label, _anchor in TOPIC_ORDER:
        if name == filename:
            return label
    return filename.removesuffix(".md")


def lang_switch(locale: str) -> str:
    if locale == "ru":
        en = '<a href="./README.md"><img src="https://img.shields.io/badge/English-8B9099?style=for-the-badge&labelColor=12141A" alt="English"></a>'
        ru_btn = '<a href="./README.ru.md"><img src="https://img.shields.io/badge/Русский-F05A28?style=for-the-badge&labelColor=12141A" alt="Русский"></a>'
    else:
        en = '<a href="./README.md"><img src="https://img.shields.io/badge/English-F05A28?style=for-the-badge&labelColor=12141A" alt="English"></a>'
        ru_btn = '<a href="./README.ru.md"><img src="https://img.shields.io/badge/Русский-8B9099?style=for-the-badge&labelColor=12141A" alt="Русский"></a>'
    return f'<p align="center">\n  {en}\n  {ru_btn}\n</p>'


def render_card(card: dict, locale: str, heading_id: bool = True) -> str:
    title = html.escape(card["title"])
    slug = card["slug"]
    heading = (
        f'<p id="card-{slug}" align="center"><strong>{title}</strong></p>'
        if heading_id
        else f'<p align="center"><strong>{title}</strong></p>'
    )
    freq = ru.FREQ.get(card["freq"], card["freq"]) if locale == "ru" else card["freq"]
    chips = f"<code>{html.escape(card['level'])}</code> · <code>{html.escape(freq)}</code>"
    if card["kind"] == "Practice":
        chips += " · <code>Practice</code>"
        summary = ru.SHOW_PROMPT if locale == "ru" else "Show prompt"
        if locale == "ru":
            body = card["prompt"] or ru.MISSING_PROMPT
        else:
            body = card["prompt"] or "_Prompt still to write._"
    else:
        summary = ru.SHOW_ANSWER if locale == "ru" else "Show answer and Swift"
        parts = []
        if card["answer"]:
            parts.append(card["answer"])
        if card["example"]:
            parts.extend(["", card["example"]])
        if parts:
            body = "\n\n".join(parts)
        elif locale == "ru":
            body = ru.MISSING_ANSWER.format(file=card["file"], slug=slug)
        else:
            body = f"See the full card in [topics/{card['file']}](topics/{card['file']}#{slug})."
    follow = ""
    if card["follow-ups"]:
        label = ru.THEN_ASK if locale == "ru" else "Then they usually ask"
        follow = f"\n\n**{label}**\n\n" + card["follow-ups"]
    source_label = ru.FULL_CARD if locale == "ru" else "Full card"
    source = f"[{source_label}](topics/{card['file']}#{slug})"
    return "\n".join(
        [
            "<table>",
            "<tr><td>",
            '<img src="./assets/readme/stretch.png" width="1200" height="1" alt="full width">',
            "</td></tr>",
            "<tr><td>",
            "",
            heading,
            "",
            f"{chips}<br>{source}",
            "",
            "<details>",
            f"<summary><strong>{summary}</strong></summary>",
            "",
            body,
            follow,
            "",
            "</details>",
            "",
            "</td></tr></table>",
            "",
        ]
    )


def render_topic_deck(
    filename: str,
    label: str,
    anchor: str,
    cards: list[dict],
    locale: str,
) -> str:
    high = sum(1 for card in cards if card["freq"] == "High")
    if locale == "ru":
        meta = f'<a href="topics/{filename}">{filename}</a> · {len(cards)} {ru.CARDS} · {high} {ru.OFTEN}'
        summary = f"<strong>{ru.OPEN} {html.escape(label)}</strong> · {ru.OPEN_HINT}"
    else:
        meta = f'<a href="topics/{filename}">{filename}</a> · {len(cards)} cards · {high} often asked'
        summary = f"<strong>Open {html.escape(label)}</strong> · read a question, then reveal the answer"
    blocks = [
        f'<h2 id="{anchor}">{html.escape(label)}</h2>',
        "",
        meta,
        "",
        "<details>",
        f"<summary>{summary}</summary>",
        "",
    ]
    by_level: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        by_level[card["level"]].append(card)
    for level in LEVELS:
        bucket = sorted(by_level.get(level, []), key=lambda card: (freq_key(card), card["title"]))
        if not bucket:
            continue
        blocks.append(f"### {html.escape(label)} · {level}")
        blocks.append("")
        for card in bucket:
            blocks.append(render_card(card, locale))
    blocks.extend(["</details>", ""])
    return "\n".join(blocks)


def render_high_deck(cards: list[dict], locale: str) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        if card["freq"] == "High":
            grouped[card["file"]].append(card)
    if locale == "ru":
        blocks = [
            f'<h2 id="start-here">{ru.HIGH_TITLE}</h2>',
            "",
            ru.HIGH_LEAD,
            "",
        ]
    else:
        blocks = [
            '<h2 id="start-here">High frequency</h2>',
            "",
            "The questions that show up across sources. Open a topic, say the answer, then reveal.",
            "",
        ]
    for filename, _en_label, _anchor in TOPIC_ORDER:
        bucket = sorted(
            grouped.get(filename, []),
            key=lambda card: (LEVELS.index(card["level"]) if card["level"] in LEVELS else 9, card["title"]),
        )
        if not bucket:
            continue
        label = topic_label(filename, locale)
        suffix = f"{len(bucket)} {ru.OFTEN}" if locale == "ru" else f"{len(bucket)} often asked"
        blocks.extend(
            [
                "<details>",
                f"<summary><strong>{html.escape(label)}</strong> · {suffix}</summary>",
                "",
            ]
        )
        for card in bucket:
            blocks.append(render_card(card, locale, heading_id=False))
        blocks.extend(["</details>", ""])
    return "\n".join(blocks)


def jump_row(locale: str) -> str:
    links = " · ".join(
        f'<a href="#{anchor}">{html.escape(topic_label(filename, locale))}</a>'
        for filename, _label, anchor in TOPIC_ORDER
    )
    high = ru.NAV_HIGH if locale == "ru" else "High frequency"
    contrib = ru.NAV_CONTRIB
    return "\n".join(
        [
            "<p align=\"center\">",
            f'  <a href="#start-here">{high}</a> · {links} · <a href="CONTRIBUTING.md">{contrib}</a>',
            "</p>",
        ]
    )


def render(cards: list[dict], locale: str, ru_cards: dict[str, dict]) -> str:
    view = [localize_card(card, locale, ru_cards) for card in cards]
    total = len(view)
    practice = sum(1 for card in view if card["kind"] == "Practice")
    spoken = total - practice
    high = sum(1 for card in view if card["freq"] == "High")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for card in view:
        grouped[card["file"]].append(card)

    decks = [render_high_deck(view, locale)]
    for filename, en_label, anchor in TOPIC_ORDER:
        label = topic_label(filename, locale)
        decks.append(render_topic_deck(filename, label, anchor, grouped[filename], locale))

    hero_alt = ru.HERO_ALT if locale == "ru" else (
        "iOS Interview Questions: spoken-answer notes. A handwritten ARC card on paper, "
        "with counts for cards, practice prompts, and topics."
    )
    if locale == "ru":
        intro = ru.INTRO
        stats = ru.STATS.format(
            total=total, spoken=spoken, practice=practice, high=high, topics=len(TOPIC_ORDER)
        )
        lead = ru.LEAD
        how_title = ru.HOW_TITLE
        how = ru.HOW
        contrib_title = ru.CONTRIB_TITLE
        contrib = ru.CONTRIB
        inbox = ru.INBOX
        not_title = ru.NOT_TITLE
        not_this = ru.NOT_THIS
    else:
        intro = (
            "Spoken-answer notes for iOS interviews. Open a topic, read the question, "
            "then press **Show answer** for the spoken version and the Swift."
        )
        stats = (
            f"**{total}** cards · **{spoken}** with a written answer · **{practice}** practice prompts · "
            f"**{high}** often asked · **{len(TOPIC_ORDER)}** topics"
        )
        lead = "Answers are rewritten, not copied. API names stay in Swift."
        how_title = "How to study"
        how = """1. Start with **[High frequency](#start-here)** — open one topic, one question.
2. Or jump a subject in the row above and open that deck.
3. Inside a topic the cards sit by **Junior / Mid / Senior**.
4. Practice cards are prompts only. Talk them through. There is no pasted solution."""
        contrib_title = "Contributing"
        contrib = (
            "New questions go through the ritual in [CONTRIBUTING.md](CONTRIBUTING.md): "
            "one source at a time, dedup by meaning, rewrite the answer, then regenerate "
            "this page with `python3 scripts/generate_readme.py`."
        )
        inbox = "The local source log lives in `inbox/` and stays out of git."
        not_title = "What this is not"
        not_this = """- Not a dump of someone else's repo, course, or paid bank.
- Not tagged by company. A Sber or Flipkart recap can enrich a card; the card itself stays generic.
- Not a checklist with progress boxes.
- Practice prompts do not include third-party solutions."""

    return f"""# iOS Interview Questions

{lang_switch(locale)}

<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="{hero_alt}">
</p>

{jump_row(locale)}

{intro}

{stats}

{lead}

## {how_title}

{how}

""" + "\n".join(decks) + f"""
## {contrib_title}

{contrib}

{inbox}

## {not_title}

{not_this}
"""


def sync_hero_counts(total: int, practice: int, topic_count: int) -> None:
    replacements = {
        "stat-cards": str(total),
        "stat-practice": str(practice),
        "stat-topics": str(topic_count),
    }
    for svg_path in (
        ROOT / "assets/readme/hero.svg",
        ROOT / "assets/readme/hero-left.svg",
    ):
        if not svg_path.is_file():
            continue
        text = svg_path.read_text(encoding="utf-8")
        for element_id, value in replacements.items():
            text = re.sub(
                rf'(id="{element_id}"[^>]*>)[^<]+',
                rf"\g<1>{value}",
                text,
                count=1,
            )
        svg_path.write_text(text, encoding="utf-8")


def main() -> None:
    cards = parse_cards()
    ru_cards = load_ru_cards()
    practice = sum(1 for card in cards if card["kind"] == "Practice")
    README_EN.write_text(render(cards, "en", ru_cards), encoding="utf-8")
    README_RU.write_text(render(cards, "ru", ru_cards), encoding="utf-8")
    sync_hero_counts(len(cards), practice, len(TOPIC_ORDER))
    missing = [card["slug"] for card in cards if card["slug"] not in ru_cards]
    print(
        f"README.md + README.ru.md ← {len(cards)} cards "
        f"({practice} practice), ru overlays {len(ru_cards)}, missing {len(missing)}"
    )


if __name__ == "__main__":
    main()
