# Combine

- [Combine and reactive programming](#combine)
- [Subjects in Combine](#combine-subjects)
- [Combining publishers](#combine-operators)

## Combine and reactive programming {#combine}

- Level: Mid
- Frequency: High

### Answer

Reactive code models values **over time**: a publisher emits events, an operator transforms them, a subscriber does the work. **Combine** is Apple’s version; RxSwift is the older cross-platform one. You use it for search-as-you-type, pairing two network calls, and binding a view model to UIKit. The win is composition and cancellation (`AnyCancellable` / `store(in:)`). The cost is a call stack nobody can read when it goes wrong, and you must know threads (`receive(on:)`). Swift concurrency covers a lot of new work; Combine still shows up in existing apps and interviews. Typical mistakes: leaking a subscription, and doing UI work on the publisher’s thread.

### Example

```swift
cancellable = NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
    .receive(on: RunLoop.main)
    .sink { _ in refresh() }
```

### Follow-ups

- `Future` / Promise vs a long-lived `Publisher`?
- Publisher vs Subject vs `@Published`?
- How do you cancel, and what happens if you forget?
- When do you pick `async`/`await` over Combine?
- `debounce` vs `throttle` on a search box?
- Why `[weak self]` in `sink`, and what does `receive(on:)` change?

## Subjects in Combine {#combine-subjects}

- Level: Mid
- Frequency: Medium

### Answer

A **Subject** is a publisher you can also send into. **`PassthroughSubject`** has no current value — late subscribers miss past events (taps, one-shot events). **`CurrentValueSubject`** always has a latest value and replays it (a screen’s `isLoggedIn`). `@Published` is a `CurrentValueSubject` with SwiftUI/Combine wiring. You erase to `AnyPublisher` at the API boundary. Typical miss: a `Passthrough` for state the view needs on appear.

### Example

```swift
let taps = PassthroughSubject<Void, Never>()
let name = CurrentValueSubject<String, Never>("")
taps.send(())
name.send("Ada")
```

### Follow-ups

- Subject vs `@Published` vs `AsyncStream`?
- Why erase to `AnyPublisher`?
- What does `share()` change about a cold publisher?

## Combining publishers {#combine-operators}

- Level: Mid
- Frequency: High

### Answer

**`combineLatest`** emits when *any* input fires, with the latest value from each — a form that needs email *and* password. **`zip`** pairs events 1-to-1 and waits for the slower side. **`merge`** interleaves the same `Output` type into one stream. **`switchToLatest`** (often after `map` + search) cancels the previous inner publisher so only the latest request wins. `flatMap` starts inners and lets them overlap. Typical miss: `zip` on two `@Published` fields and wondering why the button never enables after the first pair.

### Example

```swift
let canSubmit = email.combineLatest(password)
    .map { !$0.isEmpty && $1.count >= 8 }

query
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .map { api.search($0) }
    .switchToLatest()
```

### Follow-ups

- `combineLatest` vs `zip` vs `merge` — one sentence each?
- When is `flatMap` the wrong choice vs `switchToLatest`?
- Where do you put `receive(on: DispatchQueue.main)`?
- Write `debounce` (or `throttle`) without Combine — what timer do you cancel?
