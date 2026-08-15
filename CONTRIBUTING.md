# How we add a question

One source at a time. Rewrite in our own words. Same meaning = one card.

## Ritual

1. Drop the source in chat (link, text, screenshot, PDF). Put a raw copy in `inbox/` only if we need it while extracting.
2. Pull out distinct questions. Normalize the English wording.
3. Dedup by meaning. If a card already exists, raise **Frequency** when the source confirms it is asked often. Do not create a second card.
4. Write a full English answer, a short Swift example, and follow-ups.
5. Place the card in the matching `topics/*.md` file. Create the topic file if this is the first question in that topic.
6. Update the topic table of contents and the tracks in [README.md](README.md).

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

## Rules

- **Level:** Junior / Mid / Senior — how deep the expected answer usually goes.
- **Frequency:** High / Medium / Low — how often it shows up across sources.
- Answers are rewritten. No verbatim dumps from courses, blogs, or other repos.
- Russian files come later, same paths and slugs (`swift.ru.md`, `{#arc-vs-gc}`).
- No progress checkboxes, company tags, or generators until we decide we need them.
