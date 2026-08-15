#!/usr/bin/env python3
"""Rebuild README.md catalogs from topics/*.md card metadata."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "topics"
README = ROOT / "README.md"

HEADING = re.compile(r"^## (.+?) \{#([^}]+)\}\s*$")
META = re.compile(r"^- (Level|Frequency|Kind): (.+)$")

TOPIC_ORDER = [
    ("swift.md", "Swift"),
    ("memory.md", "Memory"),
    ("concurrency.md", "Concurrency"),
    ("architecture.md", "Architecture"),
    ("uikit.md", "UIKit"),
    ("swiftui.md", "SwiftUI"),
    ("combine.md", "Combine"),
    ("networking.md", "Networking"),
    ("persistence.md", "Persistence"),
    ("performance.md", "Performance"),
    ("security.md", "Security"),
    ("accessibility.md", "Accessibility"),
    ("frameworks.md", "Frameworks"),
    ("objc-runtime.md", "Objective-C runtime"),
    ("system-design.md", "System design"),
    ("algorithms.md", "Algorithms"),
    ("behavioral.md", "Behavioral / process"),
]


def parse_cards() -> list[dict]:
    cards: list[dict] = []
    for path in sorted(TOPICS.glob("*.md")):
        current = None
        for line in path.read_text(encoding="utf-8").splitlines():
            match = HEADING.match(line)
            if match:
                if current:
                    cards.append(current)
                current = {
                    "file": path.name,
                    "title": match.group(1),
                    "slug": match.group(2),
                    "level": None,
                    "freq": None,
                    "kind": "Spoken",
                }
                continue
            if current:
                meta = META.match(line)
                if meta:
                    key, value = meta.group(1), meta.group(2).strip()
                    if key == "Level":
                        current["level"] = value
                    elif key == "Frequency":
                        current["freq"] = value
                    elif key == "Kind":
                        current["kind"] = value
        if current:
            cards.append(current)

    missing = [card for card in cards if not card["level"] or not card["freq"]]
    if missing:
        raise SystemExit(
            "cards missing Level or Frequency: "
            + ", ".join(f"{card['file']}#{card['slug']}" for card in missing)
        )
    return cards


def topic_label(filename: str) -> str:
    for name, label in TOPIC_ORDER:
        if name == filename:
            return label
    return filename.removesuffix(".md")


def link(card: dict) -> str:
    extra = " · Practice" if card["kind"] == "Practice" else ""
    return (
        f"- [{card['title']}](topics/{card['file']}#{card['slug']}) "
        f"— {card['level']}{extra}"
    )


def details_by_topic(cards: list[dict], extra: str | None = None) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        grouped[card["file"]].append(card)

    blocks = []
    for filename, label in TOPIC_ORDER:
        bucket = grouped.get(filename, [])
        if not bucket:
            continue
        lines = [link(card) for card in bucket]
        suffix = f" · {extra}" if extra else ""
        blocks.append(
            "\n".join(
                [
                    "<details>",
                    f"<summary><strong>{label}</strong> — {len(bucket)}{suffix}</summary>",
                    "",
                    *lines,
                    "",
                    "</details>",
                    "",
                ]
            )
        )
    return "\n".join(blocks).rstrip() + "\n"


def topics_table(cards: list[dict]) -> str:
    counts = defaultdict(int)
    for card in cards:
        counts[card["file"]] += 1
    rows = [
        "| Topic | File | Cards |",
        "| --- | --- | ---: |",
    ]
    for filename, label in TOPIC_ORDER:
        count = counts.get(filename, 0)
        if count == 0:
            continue
        rows.append(f"| {label} | [{filename}](topics/{filename}) | {count} |")
    return "\n".join(rows)


def render(cards: list[dict]) -> str:
    total = len(cards)
    practice = sum(1 for card in cards if card["kind"] == "Practice")
    spoken = total - practice
    high = [card for card in cards if card["freq"] == "High"]
    junior = [card for card in cards if card["level"] == "Junior"]
    mid = [card for card in cards if card["level"] == "Mid"]
    senior = [card for card in cards if card["level"] == "Senior"]

    return f"""# iOS Interview Questions

<p align="center">
  <img src="./assets/readme/hero.png" width="100%" alt="iOS Interview Questions: spoken-answer notes. A handwritten ARC card on paper, with counts for cards, practice prompts, and topics.">
</p>

<p align="center">
  <a href="#topics">Topics</a> ·
  <a href="#start-here">High frequency</a> ·
  <a href="#junior">Junior</a> ·
  <a href="#mid">Mid</a> ·
  <a href="#senior">Senior</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

Spoken-answer notes for iOS interviews. Each card is one question: a full answer in our own words, a short Swift example, and the follow-ups interviewers actually ask.

**{total}** cards · **{spoken}** with a written answer · **{practice}** practice prompts · **{len(TOPIC_ORDER)}** topics

English first. Russian twins come later, same files and `{{#slug}}` anchors. Answers are rewritten, not copied.

## How to study

1. Open **[Start here](#start-here)** — every `Frequency: High` card, grouped by topic.
2. Switch difficulty: **[Junior](#junior)** / **[Mid](#mid)** / **[Senior](#senior)**.
3. Or read one file in [`topics/`](topics) from top to bottom.
4. System-design, algorithm, and take-home **practice** cards are prompts only. Talk them through. Do not look for a pasted solution.

The lists below stay collapsed so you can jump. The answers live in the topic files.

## A card looks like this

From [ARC vs garbage collection](topics/memory.md#arc-vs-gc):

```markdown
## ARC vs garbage collection {{#arc-vs-gc}}

- Level: Mid
- Frequency: High

### Answer
Swift uses Automatic Reference Counting, not a tracing garbage collector.

### Example
weak var owner: Owner?

### Follow-ups
- Weak vs unowned — when is each the right choice?
```

Practice cards swap `Answer` / `Example` for a short `Prompt`.

## Topics

{topics_table(cards)}

## Start here

High-frequency cards — the ones that show up across sources. Open a topic, then a card.

{details_by_topic(high, "high")}
## Junior

{details_by_topic(junior, "Junior")}
## Mid

{details_by_topic(mid, "Mid")}
## Senior

{details_by_topic(senior, "Senior")}
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
    print(f"README.md ← {len(cards)} cards ({practice} practice)")


if __name__ == "__main__":
    main()
