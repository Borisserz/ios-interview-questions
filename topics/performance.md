# Performance

- [In-memory cache](#in-memory-cache)
- [Battery life issues](#battery)
- [Identify and resolve crashes](#crashes)
- [Debugging on iOS](#debugging)
- [Identify and resolve performance issues](#performance-issues)
- [Compile time](#compile-time)
- [Launch time](#launch-time)
- [NSCache vs Dictionary](#nscache-vs-dictionary)
- [LRU cache](#lru-cache)
- [Hang vs hitch vs crash](#hang-hitch-crash)
- [App Thinning](#app-thinning)
- [dSYM](#dsym)
- [Instruments](#instruments)
- [Binary / IPA size](#binary-size)

## In-memory cache {#in-memory-cache}

- Level: Mid
- Frequency: High

### Answer

An in-memory cache keeps recently used values in RAM so you skip a disk read or a network round trip. On iOS the usual tool is `NSCache`: it evicts objects when the system is under memory pressure, and you can cap it with `countLimit` and `totalCostLimit`. A plain `Dictionary` will not evict anything; it grows until you drop it or the process is jetsam'd. `NSCache` is also safe to touch from multiple queues, which a raw dictionary is not. Pair it with a cost that matches reality (decoded image bytes, not “1 per item”) and treat the cache as optional: a miss must still produce a correct result. HTTP-level reuse is a different layer — `URLCache` stores responses, not your decoded models.

### Example

```swift
final class ImageCache {
    private let cache = NSCache<NSString, UIImage>()

    init() {
        cache.countLimit = 100
        cache.totalCostLimit = 50 * 1024 * 1024
    }

    func image(for key: String) -> UIImage? {
        cache.object(forKey: key as NSString)
    }

    func store(_ image: UIImage, for key: String) {
        let cost = image.pngData()?.count ?? 0
        cache.setObject(image, forKey: key as NSString, cost: cost)
    }
}
```

### Follow-ups

- When would you pick `NSCache` over a dictionary, and when is the dictionary enough?
- How do you choose `totalCostLimit` for decoded images?
- Where does `URLCache` stop and an app-level cache start?
- What happens to an in-memory cache when the app is suspended or killed?
- How would you implement LRU if you could not use `NSCache`?

## Battery life issues {#battery}

- Level: Mid
- Frequency: Medium

### Answer

Battery drain is almost always radios, GPS, or CPU that never idles — not “Swift is slow.” Continuous `kCLLocationAccuracyBest` updates, `UIBackgroundModes` that keep you awake, BLE scanning, and a timer or display-link that fires while the screen is off are the usual suspects. Networking in a tight retry loop and decoding large images on the main thread also keep the CPU out of idle. Measure with Instruments Energy Log or MetricKit `MXAppExitMetric` / energy reports, then confirm with the system Battery screen after a controlled session. Fix the policy first: significant-change or visit monitoring instead of always-on GPS, coalesce network work, stop timers in `sceneDidEnterBackground`, and drop accuracy when the UI does not need it.

### Example

```swift
func startLocationIfNeeded() {
    manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
    manager.distanceFilter = 50
    manager.pausesLocationUpdatesAutomatically = true
    manager.allowsBackgroundLocationUpdates = false
    manager.startUpdatingLocation()
}

func sceneDidEnterBackground() {
    displayLink?.isPaused = true
    locationManager.stopUpdatingLocation()
}
```

### Follow-ups

- Significant-change location vs continuous GPS — what do you give up?
- Which background modes are worth the battery cost, and how do you justify them in review?
- How would you prove a screen is draining battery vs the OS blaming your process?
- What does a spinning `CADisplayLink` do to energy when the app is inactive?

## Identify and resolve crashes {#crashes}

- Level: Mid
- Frequency: High

### Answer

A crash is a process abort: an uncaught Swift error, a forced unwrap, an out-of-bounds access, a failed `fatalError` / assertion, or a low-level signal such as `EXC_BAD_ACCESS`. Start from a symbolicated crash report — Xcode Organizer, a third-party reporter, or MetricKit `MXCrashDiagnostic` — and read the exception type, the faulting thread, and the frames that are actually your code. Reproduce with the same OS, locale, and input; if you cannot, add a breadcrumb log around the top frames and wait for the next hit. Watchdog kills (`0x8badf00d`) are not “random”: the main thread was busy too long at launch or in the background. Fix the root cause, not the symptom — do not wrap a force-unwrap in `try?` and call it done.

### Example

```swift
enum FeedError: Error { case emptyPayload }

func decodeFeed(from data: Data) throws -> [Item] {
    let decoded = try JSONDecoder().decode(Feed.self, from: data)
    guard !decoded.items.isEmpty else { throw FeedError.emptyPayload }
    return decoded.items
}

// In a crash: look at Thread 0 vs the crashing thread,
// then the first frame in your module after UIKit / libswift.
```

### Follow-ups

- How do you symbolicate a crash from a device that is not on your desk?
- What is the difference between `EXC_BAD_ACCESS` and a Swift runtime trap?
- How do you investigate a watchdog kill at launch?
- When is a third-party crash reporter worth it versus Organizer + MetricKit?
- A crash only in production, never on your phone — what do you collect next?
- What is a dSYM, and what happens if you lose it?

## Debugging on iOS {#debugging}

- Level: Junior
- Frequency: High

### Answer

Start cheap, then go deeper. **Breakpoints** (and exception / symbolic breakpoints) plus the Variables view beat `print` for state. **`os_log` / Logger** stays in Console.app and devices; `print` does not. **View Debugger** and **Memory Graph** catch layout and retain cycles. **Instruments** (Time Profiler, Allocations, Leaks, Network) is the senior default for “it’s slow / it grows.” Crash reports and MetricKit cover what you cannot reproduce. Typical miss: shipping `print` in a loop, or treating Instruments as “only for leaks.”

### Example

```swift
import os
let log = Logger(subsystem: "app", category: "feed")
log.debug("page \(cursor, privacy: .public)")
```

### Follow-ups

- When is a breakpoint better than a log?
- Which Instrument for a scroll hitch vs a leak?
- How do you debug a crash you only see in Organizer?
- View Hierarchy vs Memory Graph — which bug is each for?
- What log levels do you actually ship (`debug` vs `info` vs `error`)?

## Identify and resolve performance issues {#performance-issues}

- Level: Mid
- Frequency: High

### Answer

“The app feels slow” is not a diagnosis. Split the complaint into launch, scroll hitching, hang on tap, and time-to-first-frame, then measure. Time Profiler shows who owns CPU; the Main Thread Checker and hang diagnostics show work that should not be on the UI queue; Core Animation / GPU frames show overdraw and offscreen passes; `os_signpost` plus MetricKit hang rate tell you if a fix moved the needle. Typical iOS wins: keep JSON decode, image downsample, and file I/O off the main thread; reuse cells; decode images at display size; avoid layout thrash in `layoutSubviews` / body recompute. Do not optimize a screen you have not profiled — the first Instruments take is usually a surprise.

### Example

```swift
import os.signpost

private let log = OSLog(subsystem: "app.feed", category: "load")

func loadFeed() async {
    let signpostID = OSSignpostID(log: log)
    os_signpost(.begin, log: log, name: "LoadFeed", signpostID: signpostID)
    let data = try? await api.feed()
    let items = await Task.detached { decode(data) }.value
    await MainActor.run { table.reload(items) }
    os_signpost(.end, log: log, name: "LoadFeed", signpostID: signpostID)
}
```

### Follow-ups

- How do you tell a CPU-bound hitch from a commit-hang in Core Animation?
- What belongs on a background queue during table scroll, and what must stay on main?
- How would you use MetricKit to decide whether a release actually got faster?
- When is `os_signpost` better than “add a print and a Date”?

## Compile time {#compile-time}

- Level: Senior
- Frequency: Medium

### Answer

Slow compiles are usually a **wide module** and a noisy expression type-check. Split targets so a change in a view does not rebuild networking. Prefer explicit types on huge literals and nested `map` / `combineLatest` chains. Avoid a dozen CocoaPods that each trigger a full workspace rebuild; SPM with fewer, smaller products helps. `@inlinable` and whole-module optimization trade compile time for runtime. Debug vs Release is not the same clock. Typical miss: “buy a faster Mac” before measuring which file `swift-frontend` sits on (`-Xfrontend -debug-time-function-bodies`).

### Example

```swift
// Helps the type checker on a long Combine chain
let enabled: AnyPublisher<Bool, Never> = email
    .combineLatest(password)
    .map { !$0.isEmpty && $1.count >= 8 }
    .eraseToAnyPublisher()
```

### Follow-ups

- How do you find the one function that takes 10s to type-check?
- When do you split a target vs just an `internal` file?
- Debug vs Release — what actually changes compile time?
- A monorepo with hundreds of local packages — what do you measure before you split again?

## Launch time {#launch-time}

- Level: Senior
- Frequency: High

### Answer

Launch is **pre-main** (dyld maps images, rebase/bind, ObjC setup, `+load` / static inits) plus **post-main** (`didFinishLaunching` to first frame). `DYLD_PRINT_STATISTICS` splits pre-main; MetricKit / `os_signpost` cover the rest — not a `Date()` in `main`. Cuts that move the needle: fewer dynamic libraries, less ObjC metadata, no I/O in `+load`, defer analytics until after first paint. Watchdog kills (~20s) are the failure mode. Typical miss: optimizing SwiftUI `body` when dyld is loading 40 pods before `main`.

### Example

```swift
func application(_ app: UIApplication,
                 didFinishLaunchingWithOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    Appearance.apply()
    Task { await analytics.start() } // after first frame, not here synchronously
    return true
}
```

### Follow-ups

- Pre-main vs post-main — how do you see each in Instruments?
- Why can a static `let` on a type delay `main`?
- What does “first frame” mean for a SwiftUI `@main` app?
- Rebase vs bind vs initializer time — which knob do you turn first?
- MetricKit vs `Date()` in `main` — which number do you trust in a review?

## NSCache vs Dictionary {#nscache-vs-dictionary}

- Level: Mid
- Frequency: High

### Answer

A `Dictionary` keeps everything you put in it until you remove it. `NSCache` is an evicting, thread-safe bag aimed at memory-sensitive objects (decoded images, large data). It can drop entries under memory pressure and respects `countLimit` / `totalCostLimit`. Keys and values are objects (`NSObject` / `AnyObject`); you wrap structs. It does not copy on write and does not preserve insertion order. For a photo feed, `NSCache` is the in-memory layer: a miss is fine, you refetch or recode. A `[URL: UIImage]` dictionary will grow until jetsam. Typical mistake: treating `NSCache` as durable storage, or using a dictionary and hoping iOS will trim it.

### Example

```swift
final class ImageCache {
    private let cache = NSCache<NSURL, UIImage>()

    init() {
        cache.countLimit = 100
        cache.totalCostLimit = 50 * 1_024 * 1_024
    }

    func image(for url: URL) -> UIImage? {
        cache.object(forKey: url as NSURL)
    }

    func store(_ image: UIImage, for url: URL) {
        let cost = Int(image.size.width * image.size.height * 4)
        cache.setObject(image, forKey: url as NSURL, cost: cost)
    }
}
```

### Follow-ups

- Why is `NSCache` not a replacement for disk cache or `URLCache`?
- How do you pick `totalCostLimit` for images?
- When is a plain dictionary still the right tool?

## LRU cache {#lru-cache}

- Level: Mid
- Frequency: High

### Answer

LRU means “when full, drop the item that was used least recently.” Interview coding: a dictionary for `O(1)` get/set plus a doubly linked list (or an ordered structure) so you can move a key to “most recent” and evict the tail. `get` and `set` both refresh recency. Capacity is a count, sometimes a byte cost. On iOS, `NSCache` is the production cousin (evicts under pressure, not a strict LRU you control). Typical miss: a dictionary alone (no eviction order) or scanning the whole map to find the oldest.

### Example

```swift
final class LRUCache<Key: Hashable, Value> {
    private var map: [Key: Value] = [:]
    private var order: [Key] = []
    private let capacity: Int

    init(capacity: Int) { self.capacity = max(1, capacity) }

    func get(_ key: Key) -> Value? {
        guard let value = map[key] else { return nil }
        touch(key)
        return value
    }

    func set(_ key: Key, _ value: Value) {
        map[key] = value
        touch(key)
        while order.count > capacity, let old = order.first {
            order.removeFirst()
            map[old] = nil
        }
    }

    private func touch(_ key: Key) {
        order.removeAll { $0 == key }
        order.append(key)
    }
}
```

### Follow-ups

- Why is `removeAll` on the array not `O(1)` — what would a linked list change?
- LRU vs LFU vs `NSCache` under memory pressure?
- How do you make this thread-safe?
- Capacity as a count vs a byte budget (image cost) — what do you evict?

## Hang vs hitch vs crash {#hang-hitch-crash}

- Level: Mid
- Frequency: High

### Answer

A **crash** aborts the process. A **hang** is the main thread stuck long enough that the system or the user thinks the app is dead (watchdog `0x8badf00d` at launch, a frozen scroll). A **hitch** (jank) is a short main-thread spike — a dropped frame — that recovers. China loops often want the **RunLoop observer** version: time `BeforeSources` → `BeforeWaiting`; if that gap exceeds ~16–100 ms, the main thread was busy. MetricKit and Instruments (Time Profiler, Hangs, Animation Hitches) are the shipping tools. Fix hangs by moving work off main; fix hitches by cheaper layout / decode. Typical miss: calling every jank a “crash.”

### Example

```swift
// Hitch: decode a 12 MP JPEG on main during cellForRow.
// Hang: wait on a lock / `main.sync` / a huge `viewDidLoad`.
// Crash: force-unwrap, `fatalError`, `EXC_BAD_ACCESS`.
Task.detached {
    let image = decode(data)
    await MainActor.run { cell.imageView.image = image }
}
```

### Follow-ups

- Which Instruments template for a hitch vs a hang?
- How is a watchdog kill classified?
- What is a hang report in Xcode Organizer?
- RunLoop observer vs Instruments — when is each the interview answer?
- Simulator is smooth, device hitches — what do you distrust first?

## App Thinning {#app-thinning}

- Level: Mid
- Frequency: Medium

### Answer

App Thinning is how the store delivers **only the slices a device needs**. **Slicing** picks architectures and resources. **On-Demand Resources** download tag-based assets later. **Bitcode** is gone — do not mention it as current. App Size Report in Xcode shows the thinned install size, not the `.ipa` you uploaded. Asset catalogs with device-specific images and `UIRequiredDeviceCapabilities` are the practical levers. Typical miss: shipping `@3x` movies in the main bundle “for everyone,” or quoting the fat archive as the user-facing size.

### Example

```text
Xcode → Product → Archive → Distribute App → App Thinning
  → App Size Report (install size per device)
On-Demand: NSBundleResourceRequest(tags: ["level3"])
```

### Follow-ups

- Install size vs download size vs your `.ipa`?
- When do On-Demand Resources make sense vs a CDN?
- What did Bitcode used to do, and why did it die?

## dSYM {#dsym}

- Level: Mid
- Frequency: High

### Answer

A **dSYM** is the debug-symbols bundle that maps addresses in a crash log back to file and line. The App Store / Xcode archives it with the build; crash reporters need **that exact UUID**. If you lose the dSYM, you get hex frames. Upload dSYMs with the binary (Organizer, Fastlane, the vendor’s upload). Bitcode-era “Apple recompiles, download new dSYMs” is historical. Typical miss: stripping symbols, then filing a crash as “unsymbolicated” for six months.

### Example

```text
# UUID in the crash must match:
dwarfdump -u App.app.dSYM
# Xcode Organizer symbolicates if the archive is still on the Mac.
```

### Follow-ups

- Who symbolicates — the device, the reporter, or your CI?
- What happens if you upload a dSYM from a different build?
- Where do TestFlight / Organizer dSYMs live?

## Instruments {#instruments}

- Level: Mid
- Frequency: High

### Answer

Instruments is the profiler you attach to a running process (sim or device). Interviewers want the **template**, not “I opened Instruments.” **Time Profiler** samples the CPU — who is on the main thread during a hitch. **Allocations** graphs live objects and tells you if memory returns to baseline after you pop a screen. **Leaks** finds objects the allocator still holds with no remaining references (true leaks; retain cycles often show better in the Memory Graph). **Hangs / Animation Hitches** and Network are the next two. Profile a Release-like build; Debug + sanitizers lie about cost. Typical miss: treating Leaks as the only memory tool, or profiling a Debug build and “optimizing” `print`.

### Example

```text
Hitch while scrolling → Time Profiler, main thread, look for JSON / image decode.
Memory climbs on a feed → Allocations, mark generation, pop the screen, see what stayed.
deinit never fires → Memory Graph first; Leaks if the graph is clean but the heap grew.
```

### Follow-ups

- Time Profiler vs Allocations vs Leaks — which complaint maps to which?
- Why is a Debug profile a weak performance argument?
- Memory Graph Debugger vs the Leaks instrument?
- SwiftUI template — Update Groups vs Long View Body vs Cause & Effect graph?
- What theory do you state *before* you open a template?

## Binary / IPA size {#binary-size}

- Level: Senior
- Frequency: High

### Answer

Package size is **not** App Thinning. Thinning is what the store ships to one device; this question is how you shrink what you upload. Read the **Link Map** / App Size Report: large `__TEXT` symbols, fat architectures you still embed, unused resources, and dynamic frameworks that cannot be stripped the way a static archive can. Cuts: asset catalog + HEIC, drop unused localizations, merge first-party dylibs, `-dead_strip`, avoid shipping a second copy of Swift in an old embedding. Typical miss: quoting the fat `.ipa` as the user-facing number, or deleting a resource that On-Demand Resources should have owned.

### Example

```text
Build Settings → Write Link Map File = YES
# then search the map for the biggest .o / metal / strings
```

### Follow-ups

- Link Map vs App Size Report vs a thinned install on a phone?
- Why can a dynamic Swift package bloat `__TEXT` more than the same code in the app target?
- What does `__TEXT` encryption historically do to compressibility?
