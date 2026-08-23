# Contributing

One source at a time. Rewrite in our own words. Same meaning = one card.

To suggest a question or a source from the website: **Issues → New issue → Propose a question or source**, or open [this form](https://github.com/Borisserz/ios-interview-questions/issues/new?template=propose-question.yml). Interview recaps without a URL go to [Discussions](https://github.com/Borisserz/ios-interview-questions/discussions/new?category=q-a).

## Ritual

1. Check the local `inbox/sources.md` log (not in git) so the same source is not processed twice. Drop the source in chat. Put a raw copy in `inbox/` only if you need it while extracting. After processing, append the source to that log.
2. Pull out distinct questions. Normalize the English wording.
3. Dedup by meaning. Same question = one card. If the card already exists, **enrich it**: add a missing fact, a sharper example, or a follow-up the new source actually uses. Raise **Frequency** when the source treats it as common. Do not open a second card.
4. Write a full English answer, a short Swift example, and follow-ups. **Exception:** a system-design / algorithm / take-home **practice** prompt may skip Answer and Example — use `Kind: Practice` and a short Prompt plus follow-ups.
5. Place the card in the matching `topics/*.md` file. Create the topic file if this is the first question in that topic.
6. Update that file’s table of contents.
7. Add the Russian overlay for that `{#slug}` in `locales/ru/*.json` (`title`, `answer` or `prompt`, `follow-ups`). CI fails if the slug is missing.
8. Regenerate the storefronts and the study decks:

```bash
python3 scripts/generate_readme.py
python3 scripts/validate.py
```

That writes `README.md`, `README.ru.md`, `docs/en/*.md`, `docs/ru/*.md`, and `docs/data/cards.json` (the GitHub Pages study app). Do not edit those generated files by hand. Learners study from the decks (answer hidden) and from `paths/`. Progress checkboxes belong only on a path file or a local `STUDY.local.md` (see `STUDY.local.md.example`).

## Card template

Use a stable `{#slug}` so a Russian twin can share the same anchor later.

````markdown
## Short question title {#short-question-title}

- Level: Junior | Mid | Senior
- Frequency: High | Medium | Low

### Answer

Full answer in your own words: what it is, when interviewers ask it, common mistakes.

### Example

```swift
// Short compiling example
```

### Follow-ups

- Typical next question?
````

Practice prompt (no spoken answer yet):

````markdown
## Design a chat app {#chat-app}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

What to design and a tight default scope. Do not paste a third-party solution.

### Follow-ups

- Typical interviewer poke?
````

## Rules

- **Level:** Junior / Mid / Senior — how deep the expected answer usually goes.
- **Frequency:** High / Medium / Low — how often it shows up across sources.
- Answers are rewritten. No verbatim dumps from courses, blogs, or other repos.
- **Practice** cards (`Kind: Practice`) are prompts for speaking out loud. Short Prompt + follow-ups. No pasted third-party solutions.
- Russian card text lives in `locales/ru/*.json`, keyed by the same `{#slug}`. Generated decks are `docs/ru/<topic>.md`.
- No progress checkboxes and no company tags on cards. A company recap can enrich a generic card; the card itself stays untagged. Checkboxes go on `paths/*.md` or `STUDY.local.md` only.
- `inbox/sources.md` stays local. Do not commit raw third-party dumps.

## Where a card goes

| If the question is about… | File |
| --- | --- |
| Language, types, generics, errors | [topics/swift.md](topics/swift.md) |
| ARC, leaks, copies | [topics/memory.md](topics/memory.md) |
| Threads, actors, async | [topics/concurrency.md](topics/concurrency.md) |
| VIPER, modularization, testing shape | [topics/architecture.md](topics/architecture.md) |
| UIKit, UIKit+SwiftUI | [topics/uikit.md](topics/uikit.md) |
| SwiftUI, Observation, StoreKit UI | [topics/swiftui.md](topics/swiftui.md) |
| Combine | [topics/combine.md](topics/combine.md) |
| URLSession, HTTP, auth | [topics/networking.md](topics/networking.md) |
| Core Data, SwiftData, files | [topics/persistence.md](topics/persistence.md) |
| Instruments, hitching, launch | [topics/performance.md](topics/performance.md) |
| Keychain, ATS, privacy | [topics/security.md](topics/security.md) |
| VoiceOver, Dynamic Type | [topics/accessibility.md](topics/accessibility.md) |
| Apple frameworks that are not the above | [topics/frameworks.md](topics/frameworks.md) |
| Runtime, ObjC, swizzling | [topics/objc-runtime.md](topics/objc-runtime.md) |
| App / feature design prompts | [topics/system-design.md](topics/system-design.md) |
| Algorithms to talk through | [topics/algorithms.md](topics/algorithms.md) |
| Behavioral, process, take-home habits | [topics/behavioral.md](topics/behavioral.md) |

## Fresh questions

Communities are **watch sources**, not banks to scrape.

- Reddit: r/iOSProgramming, r/swift, r/cscareerquestions — public recaps only. Do not dump a thread.
- Glassdoor / Blind — public snippets only. No login scrape, no company tags on cards.

When a recap lands: same ritual (dedup, enrich, raise Frequency if the theme repeats). Date the harvest in `inbox/sources.md`.
