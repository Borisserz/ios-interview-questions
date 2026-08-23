"""Russian UI copy for README.ru.md. Card bodies live in locales/ru/*.json."""

from __future__ import annotations

# Topic file → label in the Russian deck. Keep framework names in English.
TOPICS = {
    "swift.md": "Swift",
    "memory.md": "Память",
    "concurrency.md": "Concurrency",
    "architecture.md": "Архитектура",
    "uikit.md": "UIKit",
    "swiftui.md": "SwiftUI",
    "combine.md": "Combine",
    "networking.md": "Сеть",
    "persistence.md": "Хранение",
    "performance.md": "Performance",
    "security.md": "Безопасность",
    "accessibility.md": "Accessibility",
    "frameworks.md": "Фреймворки",
    "objc-runtime.md": "Objective-C runtime",
    "system-design.md": "System design",
    "algorithms.md": "Алгоритмы",
    "behavioral.md": "Поведение и процесс",
}

FREQ = {"High": "Часто", "Medium": "Средне", "Low": "Редко"}

SHOW_ANSWER = "Показать ответ и Swift"
SHOW_PROMPT = "Показать формулировку"
FULL_CARD = "Полная карточка"
THEN_ASK = "Потом обычно спрашивают"
OFTEN = "часто спрашивают"
CARDS = "карточек"
OPEN = "Открыть"
OPEN_HINT = "прочитай вопрос, потом ответ"
HIGH_TITLE = "Часто спрашивают"
HIGH_LEAD = "Только названия. Открой карточку, скажи ответ, потом раскрой."
HOW_TITLE = "Как учить"
CONTRIB_TITLE = "Как добавлять вопросы"
NOT_TITLE = "Чего здесь нет"
NAV_HIGH = "Часто спрашивают"
NAV_PATHS = "Маршруты"
NAV_CONTRIB = "Contributing"
STARTER_TITLE = "Одна карточка"
STARTER_LEAD = "Скажи ответ вслух, потом раскрой. Около 60 секунд."
PATHS_TITLE = "Маршруты"
PATHS_LEAD = "Конечные списки. Галочки только здесь — не на карточках. Сессия около 20 минут."
PATHS_LIST = """- [Junior, часто спрашивают](paths/junior-high-freq.md) — ~5 сессий
- [7 дней, Mid](paths/7-day-mid.md) — 8–12 карточек в день
- [14 дней, Senior](paths/14-day-senior.md) — плюс system design и behavioral"""
TOPICS_TITLE = "Темы"
HERO_ALT = "iOS Interview Questions: устные ответы. Счётчики карточек, practice и тем."

INTRO = (
    "Конспекты устных ответов на iOS-собеседования. Открой тему, прочитай вопрос, "
    "нажми **Показать ответ** — там текст, как его говорят, и Swift."
)

STATS = (
    "**{total}** карточек · **{spoken}** с ответом · **{practice}** practice · "
    "**{high}** часто спрашивают · **{topics}** тем"
)

LEAD = "Ответы своими словами, не копипаст. Код и имена API — как в Swift, без перевода."

HOW = """1. Попробуй **[одну карточку](#identity-vs-equality)** ниже — скажи ответ, потом раскрой.
2. Возьми **[маршрут](#study-paths)** (~20 мин). Или начни с [Часто спрашивают](#start-here).
3. Колоды в `docs/ru/` (английские близнецы в `docs/en/`). Карточки лежат по **Junior / Mid / Senior**.
4. Practice — только формулировка. Проговори вслух. Готового решения в карточке нет."""

CONTRIB = """Новые вопросы — по ритуалу в [CONTRIBUTING.md](CONTRIBUTING.md): один источник за раз, один смысл — одна карточка, ответ своими словами, потом `python3 scripts/generate_readme.py`."""

INBOX = "Лог источников лежит в `inbox/` и в git не попадает."

NOT_THIS = """- Не дамп чужого репо, курса или платного банка.
- Без тегов компаний. Рекап из Сбера или Flipkart может дополнить карточку — на самой карточке компании нет.
- Не чеклист с галочками на карточках. Прогресс — в маршруте или в локальном `STUDY.local.md`.
- В practice нет чужих решений."""

MISSING_ANSWER = "См. полную карточку в [topics/{file}](topics/{file}#{slug})."
MISSING_PROMPT = "_Формулировки пока нет._"
