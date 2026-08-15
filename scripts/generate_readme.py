#!/usr/bin/env python3
"""Rebuild README.md study decks from topics/*.md cards."""

from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "topics"
README = ROOT / "README.md"

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


def topic_meta(filename: str) -> tuple[str, str]:
    for name, label, anchor in TOPIC_ORDER:
        if name == filename:
            return label, anchor
    return filename.removesuffix(".md"), filename.removesuffix(".md")


def freq_key(card: dict) -> int:
    return {"High": 0, "Medium": 1, "Low": 2}.get(card["freq"], 9)


def render_card(card: dict, heading_id: bool = True) -> str:
    title = html.escape(card["title"])
    slug = card["slug"]
    heading = (
        f'<h4 id="card-{slug}">{title}</h4>'
        if heading_id
        else f"<h4>{title}</h4>"
    )
    chips = f"<code>{html.escape(card['level'])}</code> · <code>{html.escape(card['freq'])}</code>"
    if card["kind"] == "Practice":
        chips += " · <code>Practice</code>"
        summary = "Show prompt"
        body = card["prompt"] or "_Prompt still to write._"
    else:
        summary = "Show answer and Swift"
        parts = []
        if card["answer"]:
            parts.append(card["answer"])
        if card["example"]:
            parts.extend(["", card["example"]])
        body = "\n\n".join(parts) if parts else f"See the full card in [topics/{card['file']}](topics/{card['file']}#{slug})."
    follow = ""
    if card["follow-ups"]:
        follow = "\n\n**Then they usually ask**\n\n" + card["follow-ups"]
    source = f"[Full card](topics/{card['file']}#{slug})"
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


def render_topic_deck(label: str, anchor: str, filename: str, cards: list[dict]) -> str:
    high = sum(1 for card in cards if card["freq"] == "High")
    blocks = [
        f'<h2 id="{anchor}">{html.escape(label)}</h2>',
        "",
        f"<a href=\"topics/{filename}\">{filename}</a> · {len(cards)} cards · {high} often asked",
        "",
        "<details>",
        f"<summary><strong>Open {html.escape(label)}</strong> · read a question, then reveal the answer</summary>",
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
            blocks.append(render_card(card))
    blocks.extend(["</details>", ""])
    return "\n".join(blocks)


def render_high_deck(cards: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        if card["freq"] == "High":
            grouped[card["file"]].append(card)
    blocks = [
        '<h2 id="start-here">High frequency</h2>',
        "",
        "The questions that show up across sources. Open a topic, say the answer, then reveal.",
        "",
    ]
    for filename, label, _anchor in TOPIC_ORDER:
        bucket = sorted(grouped.get(filename, []), key=lambda card: (LEVELS.index(card["level"]) if card["level"] in LEVELS else 9, card["title"]))
        if not bucket:
            continue
        blocks.extend(
            [
                "<details>",
                f"<summary><strong>{html.escape(label)}</strong> · {len(bucket)} often asked</summary>",
                "",
            ]
        )
        for card in bucket:
            blocks.append(render_card(card, heading_id=False))
        blocks.extend(["</details>", ""])
    return "\n".join(blocks)


def jump_row() -> str:
    links = " · ".join(
        f'<a href="#{anchor}">{html.escape(label)}</a>'
        for _filename, label, anchor in TOPIC_ORDER
    )
    return "\n".join(
        [
            "<p align=\"center\">",
            f'  <a href="#start-here">High frequency</a> · {links} · <a href="CONTRIBUTING.md">Contributing</a>',
            "</p>",
        ]
    )


def render(cards: list[dict]) -> str:
    total = len(cards)
    practice = sum(1 for card in cards if card["kind"] == "Practice")
    spoken = total - practice
    high = sum(1 for card in cards if card["freq"] == "High")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        grouped[card["file"]].append(card)

    decks = [render_high_deck(cards)]
    for filename, label, anchor in TOPIC_ORDER:
        decks.append(render_topic_deck(label, anchor, filename, grouped[filename]))

    return f"""# iOS Interview Questions

<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="iOS Interview Questions: spoken-answer notes. A handwritten ARC card on paper, with counts for cards, practice prompts, and topics.">
</p>

{jump_row()}

Spoken-answer notes for iOS interviews. Open a topic, read the question, then press **Show answer** for the spoken version and the Swift.

**{total}** cards · **{spoken}** with a written answer · **{practice}** practice prompts · **{high}** often asked · **{len(TOPIC_ORDER)}** topics

English first. Russian twins come later, same files and `{{#slug}}` anchors. Answers are rewritten, not copied.

## How to study

1. Start with **[High frequency](#start-here)** — open one topic, one question.
2. Or jump a subject in the row above and open that deck.
3. Inside a topic the cards sit by **Junior / Mid / Senior**.
4. Practice cards are prompts only. Talk them through. There is no pasted solution.

""" + "\n".join(decks) + """
## Contributing

New questions go through the ritual in [CONTRIBUTING.md](CONTRIBUTING.md): one source at a time, dedup by meaning, rewrite the answer, then regenerate this page with `python3 scripts/generate_readme.py`.

The local source log lives in `inbox/` and stays out of git.

## What this is not

- Not a dump of someone else's repo, course, or paid bank.
- Not tagged by company. A Sber or Flipkart recap can enrich a card; the card itself stays generic.
- Not a checklist with progress boxes.
- Practice prompts do not include third-party solutions.
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
    practice = sum(1 for card in cards if card["kind"] == "Practice")
    README.write_text(render(cards), encoding="utf-8")
    sync_hero_counts(len(cards), practice, len(TOPIC_ORDER))
    print(
        f"README.md ← {len(cards)} cards ({practice} practice), "
        f"{README.stat().st_size / 1024:.0f} KB"
    )


if __name__ == "__main__":
    main()
