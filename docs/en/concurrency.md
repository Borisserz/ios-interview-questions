# Concurrency

27 cards · 23 often asked · source [concurrency.md](../../topics/concurrency.md)

### Junior

<h2 id="concurrency-vs-parallelism">Concurrency vs parallelism</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Concurrency** is interleaving: many tasks make progress, not necessarily at the same instant. An iOS app is concurrent when the user scrolls, a download finishes, and a tap is handled — one core can still do that by switching. **Parallelism** is the same instant on two cores: two image filters, a video encode. Interviewers want “responsiveness vs throughput.” GCD concurrent queues and `async let` *may* run in parallel; they always give you concurrency. Typical miss: “async means two CPUs” or calling every background queue “parallel.”



```swift
// Concurrent: main keeps scrolling while this suspends.
let data = try await URLSession.shared.data(from: url).0

// Parallel *if* the pool has two cores free:
async let a = decode(left)
async let b = decode(right)
let (l, r) = await (a, b)
```


**Then they usually ask**

- Can you have concurrency on a single core?
- When do you actually need parallelism on iPhone?
- Sync vs async — is that the same axis as serial vs concurrent?

</details>

### Mid

<h2 id="main-actor">@MainActor</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`@MainActor` is a global actor: everything annotated with it runs on the main thread/queue. UIKit and SwiftUI views are main-actor isolated. **`DispatchQueue.main.async` is a hop onto that queue; `@MainActor` is isolation the compiler understands.** `main.async` does not make the next line `Sendable`-safe or stop you from touching UI from a detached task later. `MainActor.run` / `await` on a main-actor method *is* a hop, and it can skip the enqueue if you are already isolated (`assumeIsolated`). **Why the main thread:** UIKit is not thread-safe. The render server and `UIWindow` expect mutations on the main run loop; off-main UI work is undefined (tearing, lost touches, crashes). Isolating a whole class means all methods need the main actor unless you mark `nonisolated`. Typical mistakes: treating `DispatchQueue.main.async` as the Swift 6 answer, `Task.detached` then touching `@State`, or `@MainActor` on a heavy parser so you hitch the UI. Prefer isolating the UI type, not the networking layer.



```swift
@MainActor
final class ProfileScreen {
    var name = ""

    func show(_ user: User) {
        name = user.name // main, safe for UI
    }
}

func fetch() async {
    let user = await api.user()
    await ProfileScreen().show(user)
}
```


**Then they usually ask**

- `@MainActor` on a function vs on a type — what inherits?
- When do you use `MainActor.assumeIsolated`?
- How does this replace `DispatchQueue.main.async`?
- You are already on the main queue — does `MainActor.run` still hop?
- Why must UIKit updates happen on the main thread?
- When is `nonisolated` legal on a `@MainActor` type?
- Does `Task { }` inside a `@MainActor` method hop off main?
- Does `@MainActor` block the main thread while you `await` a network call?

</details>

<h2 id="actor-vs-serial-queue">Actor vs serial DispatchQueue</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **serial queue** is a convention: you promise to touch the state only on that queue. The compiler does not help. An **`actor`** is language isolation — crossing the boundary is `await`, and Swift 6 will refuse unsynchronized access. Actors reenter at `await`; a serial queue does not yield in the middle of a block unless you schedule more work. Actors compose with `async` functions and cancellation; queues compose with GCD and callbacks. Keep a serial queue when you must call a synchronous API from many threads today (a C library, a lock-free cache read). For new model objects, start with an actor. Typical mistake: wrapping every function in `queue.async` and then `sync`ing out a return value from the same queue.



```swift
actor SessionStore {
    private var token: String?

    func setToken(_ token: String) { self.token = token }

    func currentToken() -> String? { token }
}

// Older equivalent: private let queue = DispatchQueue(label: "session")
```


**Then they usually ask**

- How do you expose a synchronous read from an actor?
- What is actor reentrancy, and does a serial queue have it?
- When would you use `nonisolated` on an actor method?
- Image cache: two `load` calls hit the same miss — how do you coalesce after `await`?

</details>

<h2 id="async-sequence">AsyncSequence</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`AsyncSequence` is `Sequence` for values that **arrive over time**: `for await x in stream`. `URLSession.bytes`, `NotificationCenter.notifications`, and `AsyncStream` are the usual sources. Back-pressure and cancellation come from the `for await` loop ending. Typical miss: buffering an unbounded `AsyncStream` continuation, or blocking inside `next()`.



```swift
for await note in NotificationCenter.default.notifications(named: .NSSystemTimeZoneDidChange) {
    refreshClocks()
}
```


**Then they usually ask**

- `AsyncStream` vs Combine publisher?
- What happens to the loop when the `Task` is cancelled?
- When is `AsyncSequence` the wrong tool vs one `await`?

</details>

<h2 id="checked-continuation">Checked continuations</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`withCheckedContinuation` / `withCheckedThrowingContinuation` bridges a callback API into `async`. You resume **exactly once**. Resume twice and the checked variant traps in debug; the unsafe variant is undefined. Never leak the continuation — if the callback can fail to fire, resume with an error on timeout or `onCancel`. This is how you wrap `URLSession.dataTask` or a delegate that has no async overload. Prefer the real async API when it exists (`data(from:)`). Typical mistake: capturing `self` strongly in the callback and never resuming on the error path.



```swift
func token() async throws -> String {
    try await withCheckedThrowingContinuation { cont in
        auth.renew { result in
            switch result {
            case .success(let value): cont.resume(returning: value)
            case .failure(let error): cont.resume(throwing: error)
            }
        }
    }
}
```


**Then they usually ask**

- Checked vs unsafe continuation — when is unsafe justified?
- How do you hook `onCancel` to stop the underlying work?
- Why not wrap every Combine publisher this way?

</details>

<h2 id="concurrency-problems">Concurrency problems</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Name the failure, then the fix. A **data race** is unsynchronized read/write of the same memory — Swift 6 treats that as a compile error under complete checking. A **race condition** is a logic bug: two orders of events are both “valid” but one is wrong (check-then-act). **Deadlock** is two waiters holding what the other needs; the classic iOS case is `DispatchQueue.main.sync` from the main thread. **Priority inversion** is a low-priority holder blocking a high-priority waiter; QoS inheritance and actors reduce it. **Actor reentrancy** is not a race: `await` inside an actor lets other tasks enter, so your invariants can change across the suspension. Interviewers want you to pick the right word, not say “threading bug.”



```swift
actor Counter {
    private var value = 0

    func bumpIfPositive() async {
        guard value > 0 else { return }
        await Task.yield() // other tasks can enter here
        value += 1         // value may no longer be > 0
    }
}
```


**Then they usually ask**

- Data race vs race condition — one sentence each?
- How does Swift 6 complete concurrency checking change the interview answer?
- What is a practical fix for actor reentrancy — check again after `await`?
- Deadlock vs livelock — one sentence each?
- How do you catch a data race in Xcode (Thread Sanitizer)?
- GCD “queue reentrancy” (`sync` on the same serial queue) vs actor reentrancy — which one deadlocks?
- They hand you a hanging Xcode project — first step to tell deadlock from a data race?

</details>

<h2 id="dispatch-group">DispatchGroup</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A `DispatchGroup` is a **counter** for “these N async jobs are done.” `enter` before the work, `leave` on every path (including errors), then `notify` or `wait`. Use it to join several GCD / completion-handler calls when you cannot rewrite them as `async let`. `wait` on the main queue is a hang. You cannot cancel remaining members the way a throwing task group can. Typical miss: `enter` without `leave` on the failure path, so `notify` never fires.



```swift
let group = DispatchGroup()
for url in urls {
    group.enter()
    session.dataTask(with: url) { _, _, _ in
        defer { group.leave() }
        // handle data / error
    }.resume()
}
group.notify(queue: .main) { table.reloadData() }
```


**Then they usually ask**

- `notify` vs `wait` — which one is legal on main?
- How do you abort the rest if one download fails?
- What replaces this in Swift concurrency?

</details>

<h2 id="dispatch-semaphore">DispatchSemaphore</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A `DispatchSemaphore` is a **permit count**. `wait` decrements (blocks at 0); `signal` increments. Use it to cap concurrent *blocking* work — two file handles, a legacy SDK. It is not a mutex (no owner, easy to over-signal) and it is a trap in Swift concurrency: `wait` on a task thread starves the cooperative pool. Prefer a task group with a sliding window, or `AsyncStream` + a counter. Typical miss: `wait` on main, or using a semaphore of 1 as your only “thread safety” while still hopping queues inside the critical section.



```swift
final class Gate {
    private let sem = DispatchSemaphore(value: 2)

    func limited(_ work: () -> Void) {
        sem.wait()
        defer { sem.signal() }
        work()
    }
}
```


**Then they usually ask**

- Semaphore vs serial queue vs actor — which problem does each solve?
- Why is `wait` inside `Task { }` a thread-explosion risk?
- How do you rate-limit `URLSession` without a semaphore?

</details>

<h2 id="gcd">GCD</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Grand Central Dispatch is the queue runtime behind `DispatchQueue`. Queues are **serial** (one block at a time) or **concurrent** (many). `async` schedules work and returns; `sync` blocks the caller until that work finishes — `sync` on the serial queue you are already on deadlocks. `DispatchQueue.main` is for UI. `DispatchQueue.global(qos:)` is for fire-and-forget work. A private serial queue is the usual way to protect mutable state. A **`DispatchGroup`** lets you wait for several async jobs (`enter` / `leave` / `notify`). A **barrier** on a concurrent queue waits for in-flight reads, then runs exclusive writes — the classic reader-writer cache. Quality of Service is a scheduling hint, not a priority lock. GCD work items do not cancel the way a `Task` does. New code should default to `async`/`await` and actors. Interviewers still want sync versus async, serial vs concurrent, the main-thread rule, and the deadlock example.



```swift
let lockQueue = DispatchQueue(label: "com.app.state")

func updateTitle(_ text: String) {
    lockQueue.async {
        DispatchQueue.main.async {
            self.label.text = text
        }
    }
}

// Deadlock if this runs on the main queue:
// DispatchQueue.main.sync { print("never") }
```


**Then they usually ask**

- Serial vs concurrent queue — where do you put a barrier?
- How does GCD QoS interact with `Task` priority?
- Reader-writer: many `async` reads, one `async(flags: .barrier)` write?
- `OperationQueue` vs GCD — when do you want dependencies and cancellation?
- What replaces a private serial queue in Swift concurrency?
- How do you wait for N image downloads with a `DispatchGroup`?
- Why is setting `label.text` on a global queue a bug — how do you fix it?
- `concurrentPerform` vs a `for` on a concurrent queue?
- Is `asyncAfter` an exact delay?

</details>

<h2 id="gcd-vs-operationqueue">GCD vs OperationQueue</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**GCD** schedules closures on queues. It is the right default for “run this off the main thread” and for a private serial lock. **`OperationQueue`** wraps work as `Operation` objects: dependencies (`addDependency`), cancellation that you can check, max concurrent operation count, and KVO on `isFinished`. Set `maxConcurrentOperationCount = 1` when they ask how to run API calls **serially** on an operation queue — same idea as a private serial `DispatchQueue`. Use operations when a pipeline has “decode then upload, cancel the upload if the user leaves.” GCD groups can wait for a batch, but they do not model a DAG of named steps as cleanly. New Swift concurrency (`Task`, `TaskGroup`) covers a lot of what operations used to do. Typical mistake: building a custom operation just to call `async` once.



```swift
let decode = BlockOperation { decodeOnDisk() }
let upload = BlockOperation { uploadFile() }
upload.addDependency(decode)
upload.completionBlock = { print("done or cancelled") }

let queue = OperationQueue()
queue.maxConcurrentOperationCount = 2
queue.addOperations([decode, upload], waitUntilFinished: false)
```


**Then they usually ask**

- How do you cancel an `Operation` that is already running?
- Blocks / GCD vs `NSOperation` — when is the extra type worth it?
- What does `isAsynchronous = true` change?
- When would you still pick GCD over `OperationQueue`?
- How do you force an `OperationQueue` to run one request at a time?

</details>

<h2 id="gcd-vs-async-await">GCD vs async/await</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

GCD is **unstructured queues**: you `async` a block and lose the parent. No automatic cancellation, no `throws` out of the block, easy thread explosion if those blocks *block*. `async`/`await` is **structured tasks** on a cooperative pool: children inherit priority and cancellation, errors propagate through `await`, a suspend does not hold a thread. GCD still wins for a tiny serial lock, a barrier cache, or code that must stay synchronous. New feature work should be tasks and actors. Typical miss: “async/await is just prettier GCD.”



```swift
// GCD — caller cannot cancel or throw through this.
DispatchQueue.global().async {
    let data = try? Data(contentsOf: url)
    DispatchQueue.main.async { self.image = UIImage(data: data ?? Data()) }
}

// Structured — cancel the parent, this work should stop.
func load() async throws -> UIImage {
    let (data, _) = try await URLSession.shared.data(from: url)
    return UIImage(data: data) ?? UIImage()
}
```


**Then they usually ask**

- What does a child `Task` inherit that a GCD block does not?
- When is a private serial queue still the honest tool?
- How do you migrate a completion-handler API without wrapping every call in `Task { }`?
- How do you migrate a large GCD codebase — one module at a time, or a flag day?

</details>

<h2 id="locks">Locks</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A lock makes a critical section exclusive. **`os_unfair_lock`** is the cheap modern mutex (not recursive) — its identity is the **address**, so a struct copy breaks it; heap-allocate or use **`OSAllocatedUnfairLock`** (iOS 16+). **`NSLock`** is the Foundation wrapper, still not recursive, fairer under contention. **`NSRecursiveLock`** lets the same thread lock again — useful, easy to hide a re-entrancy bug. **`pthread_mutex`** is the C version. A **semaphore** (`DispatchSemaphore`) is a counter, not a mutex; using `wait`/`signal` as a lock from `async` code is a deadlock factory. Prefer an **actor** or a serial queue unless you need a synchronous read on the caller’s thread (cell configure, a C callback). Typical mistakes: locking then `await` (the lock does not hop with the task), and forgetting `unlock` on the error path — `defer { lock.unlock() }`.



```swift
final class Counter {
    private var lock = os_unfair_lock_s()
    private var value = 0

    func increment() {
        os_unfair_lock_lock(&lock)
        defer { os_unfair_lock_unlock(&lock) }
        value += 1
    }
}
```


**Then they usually ask**

- Why must you not `await` while holding a lock?
- Unfair lock vs recursive lock vs a serial queue?
- How does this compare to `@MainActor` for UI state?
- Semaphore vs mutex vs lock — which one counts permits?
- Why is a stored `os_unfair_lock` on a struct a trap?

</details>

<h2 id="qos">Quality of Service</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

QoS is a **scheduling hint** to GCD / the kernel: `.userInteractive` (touch → frame), `.userInitiated` (user is waiting), `.utility` (progress bar), `.background` (sync, cleanup), `.default` / `.unspecified`. It is not a lock and not a guarantee. A `.background` item can still run on the main thread if you targeted `DispatchQueue.main`. `Task` priority is the Swift cousin. Typical miss: putting image decode on `.userInteractive` and janking scroll, or expecting QoS to fix a data race.



```swift
DispatchQueue.global(qos: .userInitiated).async {
    let image = decode(data)
    DispatchQueue.main.async { view.image = image }
}
```


**Then they usually ask**

- How does QoS interact with `Task` priority?
- What is priority inversion in one sentence?
- Why is `.background` the wrong queue for a button handler?
- How does overusing `.userInteractive` hurt battery and other apps?

</details>

<h2 id="sendable">Sendable</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`Sendable` means a value is safe to hand across concurrency domains — into a `Task`, an actor, or off `MainActor`. Structs of `Sendable` stored properties can be `Sendable` automatically. Classes are not, unless they are immutable and `final`, or you isolate them (`@MainActor`, an actor). Swift 6 complete checking will refuse to pass a non-`Sendable` class into a detached task. `@unchecked Sendable` is an escape hatch you must justify (you hold the lock). Typical mistake: marking a mutable class `@unchecked Sendable` to silence warnings (an `ImageCache` with a bare `[URL: UIImage]` is the classic lie), or wrapping a `var` array of classes and assuming the struct wrapper made it safe.



```swift
struct User: Sendable {
    let id: UUID
    let name: String
}

final class UnsafeCache {
    var items: [String] = []
}

// Task.detached { print(UnsafeCache().items) } // not Sendable
```


**Then they usually ask**

- Why are actors implicitly `Sendable`?
- When is `@unchecked Sendable` honest vs a lie?
- How do you send a UIKit type off the main actor?
- `@Sendable` closure vs a `Sendable` type — what is each promising?
- Mutable class into a background `Task` — struct, actor, or `final` + `let`s?

</details>

<h2 id="task-cancellation">Task cancellation</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Cancellation is **cooperative**. `task.cancel()` sets a flag; it does not abort the CPU. You check `Task.isCancelled` or call `Task.checkCancellation()` (throws `CancellationError`). `URLSession` async APIs and `Task.sleep` honor it. Structured children are cancelled when the parent is. A `Task { }` you fire-and-forget will keep running unless you store it and cancel, or tie it to `.task` / a scope. Typical mistake: `defer { }` that does not stop a `URLSessionTask`, or ignoring cancellation in a long `for` loop so a dismissed screen keeps downloading.



```swift
func loadAll(_ urls: [URL]) async throws -> [Data] {
    var result: [Data] = []
    for url in urls {
        try Task.checkCancellation()
        result.append(try await URLSession.shared.data(from: url).0)
    }
    return result
}
```


**Then they usually ask**

- What does SwiftUI `.task` cancel when the view disappears?
- How do you cancel a `withCheckedContinuation` that wrapped a callback API?
- Why is cancellation not a substitute for a timeout?
- Debounced search: cancel the previous `Task` — what still races if you skip `isCancelled`?
- Repeating `Timer` + `Task { self }` — who keeps the ViewModel alive?

</details>

<h2 id="taskgroup-vs-async-let">Task groups vs async let</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`async let`** is for a **fixed** set of child tasks you know at compile time: two fetches, then `await (a, b)`. It is structured, cancels with the scope, and reads cleanly. A **task group** is for a **dynamic** count: N URLs, early exit when one fails, or streaming results as they finish. Groups let you `addTask` in a loop and `for await` partial results. Do not build a group for two hardcoded calls — that is what `async let` is for. Do not spawn an unstructured `Task` per item in a `for` loop and hope you join them. Typical mistake: `async let` inside a loop over user data; that does not compile the way people expect, and a group is the tool.



```swift
func profile() async throws -> (User, [Post]) {
    async let user = api.user()
    async let posts = api.posts()
    return try await (user, posts)
}
```


**Then they usually ask**

- How do you cancel remaining group work after the first failure?
- Can `async let` children run in parallel? What starts them?
- When would you use `ThrowingTaskGroup` vs a manual `Task` array?
- How do you put a timeout on one `await` without a third-party library?
- Do group results arrive in add-order? How do you restore it?
- Throwing group vs `TaskGroup<Result<T, Error>>` — all-or-nothing vs partial UI?
- How do you cap a group at N in-flight uploads?

</details>

<h2 id="task-detached-taskgroup">Task vs Task.detached vs TaskGroup</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`Task { }`** is unstructured work that **inherits** actor isolation, priority, and task-local values from the creating context. That is why `Task { await load() }` inside a `@MainActor` view stays on the main actor unless you hop. **`Task.detached`** inherits almost nothing — use it for CPU work you do not want on the caller’s actor, and pass values in explicitly. A **`TaskGroup` / `throwingTaskGroup`** is structured: the parent awaits every child, cancellation propagates down, and you add children dynamically. Prefer structured concurrency (`async let`, task groups) so work cannot outlive the scope. Typical mistake: `Task.detached` from a view for a network call, then touching `@State` without hopping back.



```swift
func thumbnails(for urls: [URL]) async -> [URL: Data] {
    await withTaskGroup(of: (URL, Data?).self) { group in
        for url in urls {
            group.addTask { (url, try? await fetch(url)) }
        }
        var result: [URL: Data] = [:]
        for await (url, data) in group {
            if let data { result[url] = data }
        }
        return result
    }
}
```


**Then they usually ask**

- What does a `Task` created in a SwiftUI `.task` inherit?
- When is `Task.detached` the wrong default?
- How does cancelling the parent affect group children?
- What leaks if you start `Task { }` in a view and never cancel it on disappear?
- `Task.sleep` vs `Thread.sleep` — which one blocks a thread?
- Why is `Task { }` inside an already-`async` function a structured-concurrency bug?

</details>

<h2 id="thread-safe-state">Thread-safe shared state</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Start from the race: two queues mutate the same class properties. Then pick a tool. A **serial queue** (or a barrier on a concurrent one) is the GCD answer. An **`NSLock` / `os_unfair_lock`** is cheaper and easier to deadlock. A **semaphore** is for counting permits, not as a mutex. Prefer an **`actor`**: the compiler serializes access and `await` replaces lock dance. Value types plus copy-on-write avoid sharing if you do not sneak a class inside. Do not sprinkle `DispatchQueue.main.async` as a “fix” for model state — that only makes UI updates legal. Interviewers want one concrete choice and why, not a list of APIs.



```swift
actor ImageStore {
    private var cache: [URL: Data] = [:]

    func data(for url: URL) -> Data? { cache[url] }

    func store(_ data: Data, for url: URL) {
        cache[url] = data
    }
}
```


**Then they usually ask**

- When is a lock better than an actor?
- Why is `nonisolated(unsafe)` a last resort?
- How would you protect a cache that must be read from a cell configure method synchronously?

</details>

<h2 id="main-async-vs-sync">main.async vs main.sync</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`DispatchQueue.main.async` enqueues work and returns. That is the normal hop onto the main thread for UI. `DispatchQueue.main.sync` **blocks the caller** until the block finishes. If the caller is already on the main queue, `sync` waits for the queue to finish the current item — which is the `sync` itself — and the app deadlocks. Nested `main.async` is fine — both blocks still run on main. From a background queue, `sync` is legal but freezes that worker until the main run loop services the block. A `sync` to *another* queue often **keeps the calling thread** to avoid a hop: `otherQueue.sync { Thread.isMainThread }` called from main can still print `true`. Prefer `async` or `await MainActor.run`. Typical mistake: “I need the result now” so you `sync` from a table-view callback that is already on main.



```swift
func applyTitle(_ text: String) {
    if Thread.isMainThread {
        label.text = text
        return
    }
    DispatchQueue.main.async { [weak self] in
        self?.label.text = text
    }
}
```


**Then they usually ask**

- Why is `MainActor.assumeIsolated` sometimes safer than guessing `Thread.isMainThread`?
- What happens if you `sync` to main from a URLSession delegate queue?
- How does `await MainActor.run` differ from `DispatchQueue.main.async`?
- Why can `otherQueue.sync` from main still print `Thread.isMainThread == true`?
- Why does `main.async { main.sync { … } }` never run the inner block?
- Nested `global().async` + `main.async` — what prints first, and why is it not deterministic?

</details>

<h2 id="dispatch-work-item">DispatchWorkItem</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A `DispatchWorkItem` is a GCD block you can **cancel**, notify, or wait on. You still cannot stop work that is already running — `isCancelled` is a flag you must check. Prefer `Task` + `Task.checkCancellation()` in new code. Typical miss: `item.cancel()` and assuming a download aborted.



```swift
let item = DispatchWorkItem { decode() }
queue.async(execute: item)
item.notify(queue: .main) { table.reloadData() }
item.cancel()
```


**Then they usually ask**

- Cancel vs a `Task` that actually tears down I/O?
- `notify` vs `DispatchGroup`?
- Why is this weaker than `Operation` dependencies?

</details>

<h2 id="async-timeout">Timeout on an await</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`await` itself has no timeout. You race the work against a sleeper: `try await withThrowingTaskGroup` — add the real task, add `Task.sleep`, return the first result, cancel the rest. Or wrap `URLSession` with `timeoutIntervalForRequest`. A timeout must **cancel** the loser or you leak a request. Typical miss: `DispatchQueue.asyncAfter` around an `await`, or sleeping on the main actor.



```swift
func withTimeout<T>(seconds: Double, _ work: @escaping @Sendable () async throws -> T) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask { try await work() }
        group.addTask {
            try await Task.sleep(for: .seconds(seconds))
            throw CancellationError()
        }
        let value = try await group.next()!
        group.cancelAll()
        return value
    }
}
```


**Then they usually ask**

- Why must you `cancelAll` after the first finish?
- Session timeout vs your own race — which one actually stops the socket?
- How do you surface “timed out” vs a real `CancellationError` from the user?

</details>

<h2 id="deinit-thread">Which thread runs deinit</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`deinit` runs on whichever thread drops the last strong reference. There is no “deinit queue.” If a background `URLSession` callback releases the object, `deinit` runs there — touching UIKit from that `deinit` is a crash. Isolated `deinit` on an actor (Swift 5.10+) hops to the actor before teardown. `@MainActor` types still need care: if the last release happens off-main, you must not assume main unless isolation says so. Typical mistake: starting a timer or network call in `deinit`, or assuming it pairs with `init` on the same thread.



```swift
final class Token {
    deinit {
        // May not be main. Hop if you must talk to UI.
        print(Thread.isMainThread)
    }
}

Task.detached {
    var token: Token? = Token()
    token = nil
}
```


**Then they usually ask**

- How do you hop to `MainActor` from `deinit` without capturing `self`?
- What did isolated `deinit` change?
- Why is doing I/O in `deinit` a bad idea?

</details>

### Senior

<h2 id="actor-reentrancy">Actor reentrancy</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An actor runs **one task at a time**, but it is not a mutex around the whole method. At every `await` the actor **suspends** and may run another caller before the first one resumes. That is **reentrancy**. After `await load()`, your `cache[url]` may already have been filled — or cleared — by a second `load`. A serial `DispatchQueue.async` block does not yield in the middle unless you schedule more work. Interviewers want the fix: check state again after the `await`, coalesce in-flight work (`[URL: Task]`), or keep the critical section free of suspension. Typical miss: “actors cannot race” and then corrupting a dictionary across two `await`s.



```swift
actor ImageLoader {
    private var cache: [URL: UIImage] = [:]
    private var inflight: [URL: Task<UIImage, Error>] = [:]

    func image(for url: URL) async throws -> UIImage {
        if let hit = cache[url] { return hit }
        if let task = inflight[url] { return try await task.value }
        let task = Task { try await download(url) }
        inflight[url] = task
        defer { inflight[url] = nil }
        let image = try await task.value
        cache[url] = image
        return image
    }
}
```


**Then they usually ask**

- Why does a serial queue *not* reenter the same way?
- How do you coalesce two taps that start the same download?
- `nonisolated` on a cache read — what did you just give up?
- Data race vs race condition — which one does an actor *not* stop?
- A leaked ViewModel and a live one both hit a singleton actor — crash, or two polite purchases?
- After `await pay()`, why must you re-read stock?

</details>

<h2 id="isolation">Isolation domains</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An **isolation domain** is who is allowed to touch a piece of memory. Swift 6’s data-race checks are “did this value cross a domain without being `Sendable`?” Domains you name in an interview: an **actor instance** (its isolated methods), a **global actor** (`@MainActor`, or `@SomeActor` you declare), and **nonisolated** code (the cooperative thread pool, or a `nonisolated` member that must not touch isolated state). `@MainActor` is a global actor pinned to the main executor — UI. A custom `actor` is its own serial executor, off-main, for a cache or store. `nonisolated` on an actor member is a promise it only uses sendable / immutable data. Typical miss: “I put `@MainActor` on everything so I am isolated” — that is one domain, and you just serialized the app on the UI thread.



```swift
@globalActor
actor DBActor { static let shared = DBActor() }

@DBActor
func save(_ row: String) { /* off-main, isolated */ }

@MainActor
func show(_ row: String) { /* UI */ }
```


**Then they usually ask**

- What may a `nonisolated` actor method read?
- When is a custom global actor better than `@MainActor` on a store?
- How does `sending` at a boundary differ from marking the type `Sendable`?
- Does a `Task` *create* isolation, or *carry* the isolation of its creation site?

</details>

<h2 id="swift-6-concurrency">Swift 6 strict concurrency</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift 6 turns data-race checks into **errors**: crossing an isolation domain with a non-`Sendable` value, touching `@MainActor` state from a background task, or capturing `self` in a `@Sendable` closure that hops. The mental model is **isolation** (who may touch this memory) plus **`Sendable`** (what may travel). Migration is incremental: enable complete checking on one target, fix the boundary (`@MainActor` on the UI type, an actor on the store, `sending` / copies at the edge), then the next target. `@unchecked Sendable` and `nonisolated(unsafe)` silence the compiler — they do not make a mutable class safe. Typical miss: flipping the language mode in one PR and “fixing” 400 warnings with `@unchecked`.



```swift
@MainActor
final class FeedViewModel {
    var titles: [String] = []

    func refresh() async {
        let rows = await Self.fetch() // hops off main, then back
        titles = rows
    }

    nonisolated static func fetch() async -> [String] { ["a"] }
}
```


**Then they usually ask**

- Complete checking vs minimal — what still compiles in Swift 5 mode?
- When is `@unchecked Sendable` honest?
- What does Swift 6.2 “approachable concurrency” change about default isolation?
- `@MainActor` vs a custom actor — which isolation domain is which?
- When is `@preconcurrency import` a migration bridge vs a permanent lie?

</details>

<h2 id="thread-explosion">Thread explosion</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

GCD’s pool **grows** when a thread blocks (`sync`, semaphore `wait`, a long CPU loop that never returns). Hundreds of blocked workers each take a ~512 KB stack; the system thrashes. Swift concurrency uses a **cooperative** pool sized around the core count: `await` *releases* the thread. Blocking inside a `Task` (locks, `Thread.sleep`, a sync file read) brings the explosion back. Interviewers want “suspend ≠ block.” Typical miss: `DispatchQueue.global().async` per cell in a 200-row table, or `semaphore.wait()` on the cooperative pool.



```swift
// Explosion risk: each wait occupies a GCD thread.
let sem = DispatchSemaphore(value: 2)
(0..<200).forEach { _ in
    DispatchQueue.global().async {
        sem.wait()
        fetchBlocking()
        sem.signal()
    }
}

// Cooperative: 200 tasks, a handful of threads.
await withTaskGroup(of: Void.self) { group in
    for _ in 0..<200 { group.addTask { await fetch() } }
}
```


**Then they usually ask**

- Why does `Thread.sleep` inside a `Task` hurt more than `Task.sleep`?
- How do you cap in-flight work without a semaphore on the cooperative pool?
- What does Instruments’ Thread State look like during an explosion?

</details>

<h2 id="global-actor">Global actors</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **global actor** is one shared isolation domain for a whole subsystem — `@MainActor` is the one you already use. You declare `@globalActor enum PreferencesActor` with a `shared` actor instance; types and functions marked `@PreferencesActor` all serialize on that executor. Use it when many objects must share **one** resource (defaults, a file, a DB connection) and you want the compiler to insert `await` at the boundary. An instance `actor` is enough when each cache has its own lock. Typical miss: slapping the same global actor on unrelated work and creating a hidden app-wide queue, or using a bare `DispatchQueue` and forgetting one `sync`.



```swift
@globalActor
enum PreferencesActor {
    actor ActorType {}
    static let shared = ActorType()
}

@PreferencesActor
final class PreferencesStore {
    func set(_ v: Int) { UserDefaults.standard.set(v, forKey: "seen") }
}
```


**Then they usually ask**

- Why is `@MainActor` a global actor and not “the main thread API”?
- When do you pick an instance `actor` instead?
- What happens if two global actors both wrap `UserDefaults`?

</details>
