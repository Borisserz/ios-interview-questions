#!/usr/bin/env python3
"""Rebuild storefront READMEs and docs/en + docs/ru decks from topics + locales."""

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
STARTER_SLUG = "identity-vs-equality"
SITE_URL = "https://borisserz.github.io/ios-interview-questions/"

# Overlap of 2025–2026 interview lists (gitGood top 50, LastRound, codinginterview,
# golinuxcloud). Not every Frequency: High card — that set is ~249.
FREQUENT_SLUGS = (
    "classes-vs-structs",
    "value-vs-reference",
    "copy-on-write",
    "optionals",
    "if-let-vs-guard-let",
    "closures",
    "escaping-closures",
    "protocols",
    "generics",
    "some-vs-any",
    "inout",
    "identity-vs-equality",
    "defer",
    "explain-arc",
    "arc-vs-gc",
    "retain-cycle",
    "weak-vs-unowned",
    "memory-leak",
    "gcd",
    "gcd-vs-async-await",
    "main-actor",
    "sendable",
    "actor-vs-serial-queue",
    "task-detached-taskgroup",
    "task-cancellation",
    "checked-continuation",
    "swift-6-concurrency",
    "thread-safe-state",
    "state",
    "binding",
    "stateobject-vs-observedobject",
    "observableobject-vs-observable",
    "swiftui-property-wrappers",
    "swiftui-rerender",
    "swiftui-vs-uikit",
    "mvvm",
    "delegates",
    "dependency-injection",
    "reuse-identifiers",
    "prepare-for-reuse",
    "viewcontroller-lifecycle",
    "auto-layout-anchors",
    "frame-vs-bounds",
    "urlsession",
    "network-request",
    "codable",
    "persist-options",
    "keychain",
    "instruments",
    "news-feed",
    "chat-app",
    "image-upload",
    "push-system",
)
FREQUENT_RANK = {slug: index for index, slug in enumerate(FREQUENT_SLUGS)}

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


def deck_href(filename: str, locale: str, slug: str | None = None) -> str:
    path = f"docs/{locale}/{filename}"
    return f"{path}#{slug}" if slug else path


def lang_switch(locale: str) -> str:
    if locale == "ru":
        en = '<a href="./README.md"><img src="https://img.shields.io/badge/English-8B9099?style=for-the-badge&labelColor=12141A" alt="English"></a>'
        ru_btn = '<a href="./README.ru.md"><img src="https://img.shields.io/badge/Русский-F05A28?style=for-the-badge&labelColor=12141A" alt="Русский"></a>'
    else:
        en = '<a href="./README.md"><img src="https://img.shields.io/badge/English-F05A28?style=for-the-badge&labelColor=12141A" alt="English"></a>'
        ru_btn = '<a href="./README.ru.md"><img src="https://img.shields.io/badge/Русский-8B9099?style=for-the-badge&labelColor=12141A" alt="Русский"></a>'
    return f'<p align="center">\n  {en}\n  {ru_btn}\n</p>'


def card_reveal(card: dict, locale: str) -> tuple[str, str]:
    slug = card["slug"]
    if card["kind"] == "Practice":
        summary = ru.SHOW_PROMPT if locale == "ru" else "Show prompt"
        if locale == "ru":
            body = card["prompt"] or ru.MISSING_PROMPT
        else:
            body = card["prompt"] or "_Prompt still to write._"
        return summary, body
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
    return summary, body


def card_follow(card: dict, locale: str) -> str:
    if not card["follow-ups"]:
        return ""
    label = ru.THEN_ASK if locale == "ru" else "Then they usually ask"
    return f"\n\n**{label}**\n\n" + card["follow-ups"]


def chips(card: dict, locale: str) -> str:
    freq = ru.FREQ.get(card["freq"], card["freq"]) if locale == "ru" else card["freq"]
    bits = f"<code>{html.escape(card['level'])}</code> · <code>{html.escape(freq)}</code>"
    if card["kind"] == "Practice":
        bits += " · <code>Practice</code>"
    return bits


def render_deck_card(card: dict, locale: str) -> str:
    title = html.escape(card["title"])
    slug = card["slug"]
    summary, body = card_reveal(card, locale)
    return "\n".join(
        [
            f'<h2 id="{html.escape(slug)}">{title}</h2>',
            "",
            chips(card, locale),
            "",
            "<details>",
            f"<summary><strong>{summary}</strong></summary>",
            "",
            body,
            card_follow(card, locale),
            "",
            "</details>",
            "",
        ]
    )


def render_deck(filename: str, label: str, cards: list[dict], locale: str) -> str:
    high = sum(1 for card in cards if card["freq"] == "High")
    source = f"../../topics/{filename}"
    if locale == "ru":
        meta = f"{len(cards)} {ru.CARDS} · {high} {ru.OFTEN} · [{filename}]({source})"
    else:
        meta = f"{len(cards)} cards · {high} often asked · source [{filename}]({source})"
    blocks = [f"# {label}", "", meta, ""]
    by_level: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        by_level[card["level"]].append(card)
    for level in LEVELS:
        bucket = sorted(by_level.get(level, []), key=lambda card: (freq_key(card), card["title"]))
        if not bucket:
            continue
        blocks.append(f"### {level}")
        blocks.append("")
        for card in bucket:
            blocks.append(render_deck_card(card, locale))
    return "\n".join(blocks).rstrip() + "\n"


def write_decks(cards: list[dict], ru_cards: dict[str, dict], root: Path) -> list[Path]:
    written: list[Path] = []
    for locale in ("en", "ru"):
        dest = root / "docs" / locale
        dest.mkdir(parents=True, exist_ok=True)
        for old in dest.glob("*.md"):
            old.unlink()
        view = [localize_card(card, locale, ru_cards) for card in cards]
        grouped: dict[str, list[dict]] = defaultdict(list)
        for card in view:
            grouped[card["file"]].append(card)
        for filename, en_label, _anchor in TOPIC_ORDER:
            label = topic_label(filename, locale)
            path = dest / filename
            path.write_text(render_deck(filename, label, grouped[filename], locale), encoding="utf-8")
            written.append(path)
    return written


def render_starter(cards: list[dict], locale: str) -> str:
    card = next((item for item in cards if item["slug"] == STARTER_SLUG), None)
    if card is None:
        return ""
    title = html.escape(card["title"])
    summary, body = card_reveal(card, locale)
    deck = deck_href(card["file"], locale, card["slug"])
    more = ru.FULL_CARD if locale == "ru" else "Open in the Swift deck"
    heading = ru.STARTER_TITLE if locale == "ru" else "Try one card"
    lead = ru.STARTER_LEAD if locale == "ru" else (
        "Say the answer out loud, then reveal. About 60 seconds."
    )
    return "\n".join(
        [
            f"## {heading}",
            "",
            lead,
            "",
            f'<h2 id="{html.escape(card["slug"])}">{title}</h2>',
            "",
            f"{chips(card, locale)}<br>[{more}]({deck})",
            "",
            "<details>",
            f"<summary><strong>{summary}</strong></summary>",
            "",
            body,
            card_follow(card, locale),
            "",
            "</details>",
            "",
        ]
    )


def render_high_index(cards: list[dict], locale: str) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        if card["freq"] == "High":
            grouped[card["file"]].append(card)
    if locale == "ru":
        blocks = [f'<h2 id="start-here">{ru.HIGH_TITLE}</h2>', "", ru.HIGH_LEAD, ""]
    else:
        blocks = [
            '<h2 id="start-here">High frequency</h2>',
            "",
            "Titles only. Open a card, say the answer, then reveal.",
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
        blocks.append(f"### {label} · {suffix}")
        blocks.append("")
        for card in bucket:
            href = deck_href(filename, locale, card["slug"])
            blocks.append(f"- [{card['title']}]({href}) · {card['level']}")
        blocks.append("")
    return "\n".join(blocks)


def render_topic_index(cards: list[dict], locale: str) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for card in cards:
        grouped[card["file"]].append(card)
    title = ru.TOPICS_TITLE if locale == "ru" else "Topics"
    blocks = [f"## {title}", ""]
    for filename, _en_label, _anchor in TOPIC_ORDER:
        bucket = grouped.get(filename, [])
        high = sum(1 for card in bucket if card["freq"] == "High")
        label = topic_label(filename, locale)
        href = deck_href(filename, locale)
        if locale == "ru":
            blocks.append(f"- [{label}]({href}) — {len(bucket)} {ru.CARDS} · {high} {ru.OFTEN}")
        else:
            blocks.append(f"- [{label}]({href}) — {len(bucket)} cards · {high} often asked")
    blocks.append("")
    return "\n".join(blocks)


def render_paths(locale: str) -> str:
    if locale == "ru":
        return "\n".join(
            [
                f'<h2 id="study-paths">{ru.PATHS_TITLE}</h2>',
                "",
                ru.PATHS_LEAD,
                "",
                ru.PATHS_LIST,
                "",
            ]
        )
    return """<h2 id="study-paths">Study paths</h2>

Finite lists. Checkboxes live only here — not on the cards. About 20 minutes a session.

- [Junior high-frequency](paths/junior-high-freq.md) — 6 sessions
- [7-day mid](paths/7-day-mid.md) — 8–12 cards a day
- [14-day senior](paths/14-day-senior.md) — plus system design and behavioral

"""


def jump_row(locale: str) -> str:
    links = " · ".join(
        f'<a href="{deck_href(filename, locale)}">{html.escape(topic_label(filename, locale))}</a>'
        for filename, _label, _anchor in TOPIC_ORDER
    )
    site = ru.NAV_SITE if locale == "ru" else "Study site"
    high = ru.NAV_HIGH if locale == "ru" else "High frequency"
    paths = ru.NAV_PATHS if locale == "ru" else "Study paths"
    contrib = ru.NAV_CONTRIB
    return "\n".join(
        [
            "<p align=\"center\">",
            f'  <a href="{SITE_URL}">{html.escape(site)}</a> · <a href="#start-here">{high}</a> · <a href="#study-paths">{paths}</a> · {links} · <a href="CONTRIBUTING.md">{contrib}</a>',
            "</p>",
        ]
    )


def render_site_cta(locale: str) -> str:
    if locale == "ru":
        title = ru.SITE_TITLE
        alt = ru.SITE_ALT
        lead = ru.SITE_LEAD
        open_label = ru.SITE_OPEN
        banner = "./assets/readme/site-banner.ru.svg"
        badge = "https://img.shields.io/badge/Открыть_сайт-F05A28?style=for-the-badge&labelColor=12141A"
    else:
        title = "Study site"
        alt = "Open the English study site: pick a topic, speak the answer, then reveal."
        lead = "English card deck in the browser. Pick a topic and level. Speak. Reveal."
        open_label = "Open the study site"
        banner = "./assets/readme/site-banner.svg"
        badge = "https://img.shields.io/badge/Open_the_study_site-F05A28?style=for-the-badge&labelColor=12141A"
    return "\n".join(
        [
            f'<h2 id="study-site">{title}</h2>',
            "",
            '<p align="center">',
            f'  <a href="{SITE_URL}">',
            f'    <img src="{badge}" alt="{html.escape(open_label)}">',
            "  </a>",
            "</p>",
            "",
            '<p align="center">',
            f'  <a href="{SITE_URL}">',
            f'    <img src="{banner}" width="100%" alt="{html.escape(alt)}">',
            "  </a>",
            "</p>",
            "",
            f'<p align="center"><code>{SITE_URL}</code></p>',
            "",
            lead,
            "",
        ]
    )


def render(cards: list[dict], locale: str, ru_cards: dict[str, dict]) -> str:
    view = [localize_card(card, locale, ru_cards) for card in cards]
    total = len(view)
    practice = sum(1 for card in view if card["kind"] == "Practice")
    spoken = total - practice
    high = sum(1 for card in view if card["freq"] == "High")

    hero_alt = ru.HERO_ALT if locale == "ru" else (
        "iOS Interview Questions: spoken-answer notes, with counts for cards, "
        "practice prompts, and topics."
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
        how = """1. Try **[one card](#identity-vs-equality)** below, or follow a **[study path](#study-paths)** (~20 min).
2. Topic decks live in `docs/en/` (Russian twins in `docs/ru/`). Cards sit by **Junior / Mid / Senior**.
3. Practice cards are prompts only. Talk them through. There is no pasted solution."""
        contrib_title = "Contributing"
        contrib = (
            "New questions go through the ritual in [CONTRIBUTING.md](CONTRIBUTING.md): "
            "one source at a time, dedup by meaning, rewrite the answer, then regenerate "
            "with `python3 scripts/generate_readme.py`."
        )
        inbox = "The local source log lives in `inbox/` and stays out of git."
        not_title = "What this is not"
        not_this = """- Not a dump of someone else's repo, course, or paid bank.
- Not tagged by company. A Sber or Flipkart recap can enrich a card; the card itself stays generic.
- Not a checklist with progress boxes on the cards. Track a path or a local `STUDY.local.md`.
- Practice prompts do not include third-party solutions."""

    return f"""# iOS Interview Questions

{lang_switch(locale)}

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="{hero_alt}">
</p>

{render_site_cta(locale)}

{jump_row(locale)}

{intro}

{stats}

{lead}

## {how_title}

{how}

{render_starter(view, locale)}
{render_paths(locale)}
{render_high_index(view, locale)}
{render_topic_index(view, locale)}
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


def site_card(card: dict) -> dict:
    topic = card["file"].removesuffix(".md")
    topic_id = topic
    for filename, label, anchor in TOPIC_ORDER:
        if filename == card["file"]:
            topic = label
            topic_id = anchor
            break
    slug = card["slug"]
    return {
        "slug": slug,
        "title": card["title"],
        "file": card["file"],
        "topic": topic,
        "topicId": topic_id,
        "level": card["level"],
        "freq": card["freq"],
        "kind": card["kind"],
        "frequent": slug in FREQUENT_RANK,
        "frequentRank": FREQUENT_RANK.get(slug),
        "answer": card["answer"],
        "example": card["example"],
        "follow-ups": card["follow-ups"],
        "prompt": card["prompt"],
    }


def render_site_cards(cards: list[dict]) -> str:
    payload = {
        "topics": [
            {"id": "frequent", "file": "", "label": "Most frequent"},
        ]
        + [
            {"id": anchor, "file": filename, "label": label}
            for filename, label, anchor in TOPIC_ORDER
        ],
        "cards": [site_card(card) for card in cards],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def generated_texts(cards: list[dict], ru_cards: dict[str, dict]) -> dict[str, str]:
    texts = {
        "README.md": render(cards, "en", ru_cards),
        "README.ru.md": render(cards, "ru", ru_cards),
        "docs/data/cards.json": render_site_cards(cards),
    }
    for locale in ("en", "ru"):
        view = [localize_card(card, locale, ru_cards) for card in cards]
        grouped: dict[str, list[dict]] = defaultdict(list)
        for card in view:
            grouped[card["file"]].append(card)
        for filename, en_label, _anchor in TOPIC_ORDER:
            label = topic_label(filename, locale)
            texts[f"docs/{locale}/{filename}"] = render_deck(
                filename, label, grouped[filename], locale
            )
    return texts


def check_generated(root: Path) -> list[str]:
    cards = parse_cards()
    ru_cards = load_ru_cards()
    errors: list[str] = []
    for rel, expected in generated_texts(cards, ru_cards).items():
        path = root / rel
        if not path.is_file():
            errors.append(f"{rel} is missing; run python3 scripts/generate_readme.py")
            continue
        if path.read_text(encoding="utf-8") != expected:
            errors.append(f"{rel} is stale; run python3 scripts/generate_readme.py")
    return errors


def write_outputs(root: Path | None = None) -> None:
    dest = root or ROOT
    cards = parse_cards()
    ru_cards = load_ru_cards()
    practice = sum(1 for card in cards if card["kind"] == "Practice")
    (dest / "README.md").write_text(render(cards, "en", ru_cards), encoding="utf-8")
    (dest / "README.ru.md").write_text(render(cards, "ru", ru_cards), encoding="utf-8")
    written = write_decks(cards, ru_cards, dest)
    data_dir = dest / "docs" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "cards.json").write_text(render_site_cards(cards), encoding="utf-8")
    if dest == ROOT:
        sync_hero_counts(len(cards), practice, len(TOPIC_ORDER))
    missing = [card["slug"] for card in cards if card["slug"] not in ru_cards]
    print(
        f"README.md + README.ru.md + {len(written)} decks + cards.json ← {len(cards)} cards "
        f"({practice} practice), ru overlays {len(ru_cards)}, missing {len(missing)}"
    )


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in {"--check", "check"}:
        errors = check_generated(ROOT)
        if errors:
            print("generate --check failed:", file=sys.stderr)
            for err in errors:
                print(f"  {err}", file=sys.stderr)
            raise SystemExit(1)
        print("generate --check ok")
        return
    write_outputs(ROOT)


if __name__ == "__main__":
    main()
