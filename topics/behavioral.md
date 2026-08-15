# Behavioral

- [How Swift has changed since 2014](#swift-since-2014)
- [Code review process](#code-review)
- [Test-driven development](#tdd)
- [Arrange-Act-Assert](#arrange-act-assert)
- [Test doubles](#test-doubles)
- [Test types](#test-types)
- [Snapshot tests](#snapshot-tests)
- [Swift vs Objective-C](#swift-vs-objc)
- [Objective-C interop](#objc-interop)
- [Porting ObjC to Swift](#objc-to-swift)
- [Learning a new framework](#learn-framework)
- [Swift Package Manager](#spm)
- [Working across Apple platforms](#multiplatform)
- [Code signing](#code-signing)
- [Scheme vs target](#scheme-vs-target)
- [xcconfig and environments](#xcconfig)
- [TestFlight](#testflight)
- [Git merge vs rebase](#git-merge-rebase)
- [Git Flow](#git-flow)
- [Info.plist settings](#info-plist)
- [Minimum deployment target](#deployment-target)
- [XCTest and UI tests](#xctest)
- [Testing async code](#test-async)
- [Waterfall vs Agile](#waterfall-vs-agile)
- [App and scene lifecycle](#app-lifecycle)
- [State restoration](#state-restoration)
- [Background tasks](#background-tasks)
- [Swift Testing](#swift-testing)
- [Take-home interview](#take-home)
- [Improve an existing take-home app](#improve-existing-app)
- [Screening OA / assessment platform](#screening-oa)
- [STAR stories](#star)
- [Continuous integration](#ci)
- [Code coverage](#code-coverage)
- [Third-party vs custom](#third-party-vs-custom)
- [Binary framework vs SDK](#binary-framework)
- [FAANG iOS loop](#faang-ios-loop)
- [CIS product-company iOS loop](#cis-ios-loop)
- [India product-company iOS loop](#india-ios-loop)
- [Brazil product-company iOS loop](#brazil-ios-loop)
- [Marketplace iOS loop](#marketplace-ios-loop)
- [App Store review](#app-store-review)

## How Swift has changed since 2014 {#swift-since-2014}

- Level: Mid
- Frequency: Medium

### Answer

Swift 1 was a new language on top of the Objective-C runtime: optionals, type inference, and a syntax that still moved every release. The years that matter in an interview are ABI stability (Swift 5, 2019) so the runtime ships with the OS, `Codable`, protocol-oriented stdlib work, then structured concurrency (`async`/`await`, actors) and SwiftUI as the new UI default. Along the way: `Result`, property wrappers, opaque result types, Sendable, and macros. Source compatibility got better after Swift 3; you no longer rewrite the app every Xcode. A strong answer names a few of those shifts and ties them to shipping decisions — concurrency instead of callback pyramids, value types by default, ABI stability as the reason you can use the OS Swift.

### Example

Spoken outline:

1. 2014–2016: language still moving; Swift 3 source break.
2. 2019: ABI stability — runtime on the OS, smaller apps, binary compatibility.
3. Then: `Codable`, SwiftUI, Combine, then `async`/`await` replacing most callback and Combine networking.
4. Close: “I still read Objective-C when the stack is mixed; I do not start new modules in it.”

### Follow-ups

- What did ABI stability change for App Store binaries and the OS?
- Which Swift concurrency features would you not use below iOS 15, and why?
- What still forces you to touch Objective-C in a 2026 codebase?
- How do you talk about SwiftUI vs UIKit without sounding like a convert?

## Code review process {#code-review}

- Level: Mid
- Frequency: High

### Answer

A useful review answers three questions: is the change correct, is it safe to ship, and can the next person change it. Read the PR description and the test plan first, then the diff in dependency order — model and API before the view that consumes them. Block on behavior bugs, data loss, thread hops onto main, missing usage strings, and tests that do not fail when the bug is reintroduced. Style nits go as non-blocking comments or a formatter. Ask questions when you do not understand a choice; do not rewrite the PR in your own taste. As an author, keep the diff small, record the non-obvious “why,” and reply to every comment with a change or a reason.

### Example

Spoken outline for a 200-line networking PR:

1. Confirm the public API and error mapping match the ticket.
2. Check decoding and empty/401 paths; look for a test that would fail if those regress.
3. Flag main-thread work and any new ATS / Keychain / privacy string.
4. Leave one summary comment: what you verified and what you did not run.

### Follow-ups

- What do you block a merge for vs leave as a follow-up?
- How do you review a PR in an area you do not own?
- What makes a PR description good enough that you can review it?
- How do you handle a review that is only style comments?

## Test-driven development {#tdd}

- Level: Mid
- Frequency: Medium

### Answer

TDD means you write a failing test that states the behavior, then the minimum code that passes, then you refactor while the test stays green. It is a design tool for logic you can isolate: parsers, pricing, state machines, mapping layers. It is a poor fit for the first sketch of a SwiftUI layout or a one-off storyboard hook. Interviewers want to hear that you still write the test first when the behavior is specified, and that you do not pretend every view was born that way. The value is the regression net and the API shape the test forced — not the ceremony of red-green-refactor on every line.

### Example

Spoken outline:

1. Write `testEmptyCartDisablesCheckout` — it fails because checkout is always enabled.
2. Implement the guard; test goes green.
3. Refactor the flag into the view model; test still green.
4. Add the “cart with one item” case so you did not hard-code `false`.

### Follow-ups

- When do you skip TDD and write the test after?
- How do you TDD a type that talks to `URLSession` without hitting the network?
- What is the difference between a characterization test and a TDD test?
- How do you keep TDD from producing a test suite that only mirrors the implementation?

## Arrange-Act-Assert {#arrange-act-assert}

- Level: Junior
- Frequency: Medium

### Answer

A unit test has three beats. **Arrange:** build the system and its fakes. **Act:** one call — the behavior under test. **Assert:** check the outcome (and maybe that a collaborator was called). Keeping Act to one action makes failures readable. XCTest does not enforce this; you do. Typical miss: asserting in the middle of setup, or three unrelated acts in one `test` method.

### Example

```swift
func testCheckoutDisabledWhenEmpty() {
    let cart = Cart()                    // arrange
    let enabled = cart.canCheckout       // act
    XCTAssertFalse(enabled)              // assert
}
```

### Follow-ups

- What is a fourth “Annihilate” / teardown for?
- Why is more than one act a smell?
- How does this map to Given-When-Then?

## Test doubles {#test-doubles}

- Level: Mid
- Frequency: High

### Answer

A test double stands in for a dependency so the unit under test stays isolated. **Stub:** returns canned data (`User(id: 1)`). **Fake:** a working in-memory stand-in (an array-backed store). **Mock:** records calls and you assert “`save` was called once.” **Spy:** a real object that also records. Prefer a protocol + a tiny fake over a mocking library. Typical miss: a mock that reimplements the production class, or a Core Data test that hits the on-disk `shared` stack.

### Example

```swift
protocol UserLoading { func load() async throws -> [User] }

struct StubUsers: UserLoading {
    func load() async throws -> [User] { [User(id: 1, name: "Ada")] }
}

final class ListViewModel {
    let loader: UserLoading
    var names: [String] = []
    init(loader: UserLoading) { self.loader = loader }
    func refresh() async throws { names = try await loader.load().map(\.name) }
}
```

### Follow-ups

- Stub vs mock — which one asserts on calls?
- How do you fake `URLSession` without hitting the network?
- Why is a singleton `PersistenceController.shared` a bad test double?
- How do you inject “now” so a date-based test is deterministic?
- How do you fake `UserDefaults` without touching the real plist?

## Test types {#test-types}

- Level: Junior
- Frequency: High

### Answer

**Unit:** one type, fakes at the edge, milliseconds. **Integration:** a few real types together (Core Data in-memory + a repository). **UI / functional:** `XCUIApplication` drives the app like a user. **Acceptance:** the same idea at product language (“user can check out”). You want a pyramid: many unit, fewer integration, a thin UI smoke (login / purchase, not every label). A senior testing question is an **architecture** question: if the ViewModel needs a live server, the dependency is wrong. Typical miss: calling a UI test a unit test because it uses XCTest, or an inverted pyramid that takes 40 minutes on CI.

### Example

```text
Unit: Cart.canCheckout
Integration: CartStore saves into an in-memory container
UI: tap Checkout, see Receipt
```

### Follow-ups

- Where do snapshot tests sit?
- Why are UI tests flakier on CI?
- What is an acceptance test that is not a UI test?
- Three data sources + a background sync + a SwiftUI view — which layer gets unit tests first?
- Hardest to test: navigation or time — what do you inject?

## Snapshot tests {#snapshot-tests}

- Level: Mid
- Frequency: High

### Answer

A snapshot test renders a view (or a view controller) and compares pixels — or a serialized accessibility tree — to a recorded reference. You catch accidental layout and copy changes that unit tests miss. They are slower than unit tests and brittle on OS / font / simulator deltas, so you pin the simulator and review diffs in PRs. Typical miss: snapshotting a live `URLSession` screen, or treating a 2 000-image suite as a unit-test replacement.

### Example

```swift
func testEmptyCartLayout() {
    let view = CartView(items: [])
    // assertSnapshot(of: view, as: .image) // swift-snapshot-testing
    XCTAssertEqual(view.accessibilityLabel, "Cart empty")
}
```

### Follow-ups

- Image snapshot vs accessibility / hierarchy snapshot?
- Why did CI fail when your Mac passed?
- What do you *not* snapshot?
- Design-system button vs a live feed screen — which one earns a snapshot?
- Pin Xcode on CI — what breaks if every laptop uses a different version?

## Swift vs Objective-C {#swift-vs-objc}

- Level: Mid
- Frequency: Medium

### Answer

Swift is the language you start in: safer defaults (optionals, value types, generics), a modern stdlib, and the only path to SwiftUI and Swift concurrency. Objective-C is the runtime both still share — dynamic dispatch, selectors, KVO, and most of UIKit’s older APIs. You choose Objective-C today only for an existing module, a dynamic runtime trick Swift cannot express cleanly, or a library that never shipped a Swift overlay. Performance is rarely the reason; ARC exists on both sides. A mid-level answer is bilingual enough to read a stack frame and write a bridging header, not nostalgic about `.m` files.

### Example

Spoken outline:

1. New feature: Swift, unless it must live inside an ObjC target you cannot split.
2. I read ObjC weekly — UIKit headers, old SDKs, crash frames.
3. I do not rewrite a stable ObjC module “to make it Swift” without a product reason.
4. Interop cost (see the next card) is part of the choice, not an afterthought.

### Follow-ups

- What can Objective-C do at runtime that Swift still cannot?
- When is a rewrite of an ObjC module worth the risk?
- How do value types change API design compared to `NSObject` subclasses?
- Why do so many system APIs still look like Objective-C in Swift?

## Objective-C interop {#objc-interop}

- Level: Mid
- Frequency: Low

### Answer

Swift and Objective-C meet at the same runtime. Swift can import ObjC headers through a bridging header (app target) or an umbrella header (framework); ObjC can see Swift types that inherit `NSObject` and are marked `@objc`. Not everything bridges: Swift structs, enums without `@objc`, generics, and tuples stay on the Swift side. You expose a class to selectors, KVO, and `#selector` with `@objc` / `@objcMembers`, and you hide Swift-only API with `@nonobjc`. Nullability annotations in ObjC (`nullable`, `_Nonnull`) become optionals; missing annotations become implicitly unwrapped. Name mismatches (`initWithFoo:` → `init(foo:)`) are the clang importer, and you can reshape them with `NS_SWIFT_NAME`.

### Example

```swift
@objc(IIQSessionClient)
final class SessionClient: NSObject {
    @objc func refreshToken(_ completion: @escaping (NSError?) -> Void) {
        Task {
            do {
                try await refresh()
                completion(nil)
            } catch {
                completion(error as NSError)
            }
        }
    }
}
```

### Follow-ups

- How do you call C / C++ from Swift (bridging header vs a Clang module)?
- Bridging header vs module map — when do you need each?
- Why does a Swift `enum` fail to show up in a `.m` file?
- How do you pass a Swift error into an ObjC completion handler?
- What does `@objc` cost, and when do you refuse to add it?

## Porting ObjC to Swift {#objc-to-swift}

- Level: Mid
- Frequency: Medium

### Answer

Do not freeze the app for a rewrite. Keep the ObjC target building. Add Swift files; they see ObjC through the bridging header. Move **one boundary at a time** — a new feature in Swift, then a leaf type, then a screen — and leave a thin `@objc` facade on anything the remaining `.m` still calls. Tests and a green CI on each slice beat a branch that diverges for months. Typical miss: converting a file and changing behavior in the same PR, or rewriting UIKit glue that was already stable.

### Example

```text
1. New feature in Swift, talks to existing ObjC Session via @objc.
2. Port Session’s helpers; keep SessionClient as the ObjC name.
3. Delete the .m when no selector remains.
```

### Follow-ups

- What do you port first — models, networking, or screens?
- How do you keep `#selector` and IB actions alive mid-migration?
- When is a full rewrite cheaper than strangling?

## Learning a new framework {#learn-framework}

- Level: Mid
- Frequency: Medium

### Answer

Start from the problem, not the WWDC keynote. Read the Apple overview and one sample, then build a **tiny spike** that hits the happy path and one failure (permission denied, empty store, background expire). Note the thread the callbacks use and what you persist. Docs + Instruments beat a 40-minute tutorial. Typical miss: adding the framework to production the same day you open the header.

### Example

```text
Need offline notes → SwiftData sample → spike: insert, fetch, fail on disk full → then product API.
```

### Follow-ups

- How do you decide the spike is enough to commit?
- WWDC session vs the current doc — which wins when they disagree?
- How do you share the spike so the team can delete it?

## Swift Package Manager {#spm}

- Level: Junior
- Frequency: High

### Answer

SPM is Apple’s package tool: a `Package.swift` manifest, products (libraries or executables), and targets (the modules you compile). Xcode can add a package from a git URL and pin a version, branch, or commit. You use it for third-party code and for splitting your own modules so app and tests share one build graph. Compared with CocoaPods / Carthage, SPM is the default in current Xcode: no workspace hacks, no Pods project. Watch the pin (a floating `from: "1.0.0"` is not a lockfile you reviewed) and the platforms you declare — a package that requires iOS 17 will fail a project still on iOS 16.

### Example

```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FeedKit",
    platforms: [.iOS(.v16)],
    products: [.library(name: "FeedKit", targets: ["FeedKit"])],
    targets: [
        .target(name: "FeedKit"),
        .testTarget(name: "FeedKitTests", dependencies: ["FeedKit"])
    ]
)
```

### Follow-ups

- Version vs branch vs commit pin — what do you allow on `main`?
- How do you share one package across iOS and a widget extension?
- What belongs in a package target vs the app target?
- How do you vendor a package when legal or CI cannot hit GitHub?
- SPM vs CocoaPods vs Carthage — which do you start a 2026 app with?
- What does `pod install` actually generate, and why do you open the workspace?

## Working across Apple platforms {#multiplatform}

- Level: Mid
- Frequency: Low

### Answer

“Multiplatform” means one team ships iOS plus at least one of iPadOS, macOS, watchOS, tvOS, or visionOS — not that every file compiles everywhere. You share models, networking, and tests in a Swift package; you isolate UI and entitlements per platform. `#if os(...)`, `@available`, and separate asset catalogs keep the compile graph honest. Catalyst is a UIKit Mac port, not a substitute for a real AppKit / SwiftUI Mac app. The interview answer names what you share, what you fork, and one concrete mismatch (watchOS background limits, tvOS focus, Mac menu bar) so it does not sound like “SwiftUI writes once.”

### Example

Spoken outline:

1. Shared: models, API client, persistence in a package.
2. Per platform: app target, Info.plist, capabilities, navigation chrome.
3. `#if os(watchOS)` around HealthKit workout sessions; iOS keeps the full storefront.
4. Test the shared package on the cheapest simulator; UI on the real idiom.

### Follow-ups

- What would you refuse to share between iPhone and Apple Watch?
- Catalyst vs a SwiftUI multiplatform target — how do you choose?
- How do availability and package `platforms:` interact?
- Where do widgets and App Clips sit in that split?

## Code signing {#code-signing}

- Level: Mid
- Frequency: High

### Answer

Code signing is the OS check that this binary was built by a known team and has not been altered. You need a certificate (who you are), a provisioning profile (which app ID, devices, and entitlements), and an identity in the keychain that Xcode uses at link time. Development profiles are tied to registered devices; distribution uses Ad Hoc, App Store, or Developer ID / notarization on Mac. Entitlements (iCloud, push, associated domains, App Groups) must match the portal and the profile, or install fails with a vague “valid provisioning profile” error. Automatic signing is fine until CI; then you install a distribution cert and a profile as secrets and stop clicking “Try Again” in Xcode.

### Example

Spoken outline when a device install fails:

1. Bundle ID and team match the portal.
2. The profile includes this device UDID and the entitlements you enabled.
3. The signing identity is in the keychain and not expired.
4. Capabilities in Xcode match the App ID — push, associated domains, App Groups.

### Follow-ups

- What lives in an `.entitlements` file vs the provisioning profile?
- What is the difference between a certificate and a provisioning profile?
- Why does a widget or Watch target need its own profile?
- How do you sign on CI without a developer’s laptop keychain?
- What does “errSecInternalComponent” usually mean after a cert rotation?

## Scheme vs target {#scheme-vs-target}

- Level: Junior
- Frequency: Medium

### Answer

A **target** is a product you build (the app, a test bundle, a widget). A **scheme** is a recipe: which targets to build, which to run/test/profile, which arguments and environment. One app target can have Debug / Staging / Release schemes that pick different xcconfigs. Typical miss: “I made a new scheme” when you needed a new target (or the reverse).

### Example

```text
Target: MyApp, MyAppTests, MyWidget
Scheme "MyApp Staging" → build MyApp (Staging xcconfig) + tests
```

### Follow-ups

- Can two schemes share one target?
- Where do test plans live?
- Scheme vs configuration (Debug/Release)?

## xcconfig and environments {#xcconfig}

- Level: Mid
- Frequency: Medium

### Answer

An `.xcconfig` is a bag of build settings (`PRODUCT_BUNDLE_IDENTIFIER`, `API_BASE_URL` via `INFO_PLIST_KEY` / Swift `ACTIVE_COMPILATION_CONDITIONS`). You attach one config per configuration (Debug / Staging / Release) so DEV / SIT / UAT / Prod do not share a hardcoded URL. Do not put secrets in xcconfig if it is in git — use CI secrets. Typical miss: `#if DEBUG` for “staging” and shipping the wrong host.

### Example

```text
// Staging.xcconfig
API_BASE_URL = https:/$()/api.staging.example.com
SWIFT_ACTIVE_COMPILATION_CONDITIONS = STAGING
```

### Follow-ups

- xcconfig vs `.env` vs Remote Config?
- How do you keep a staging bundle ID next to prod?
- Why is `#if DEBUG` a bad stand-in for environment?

## TestFlight {#testflight}

- Level: Junior
- Frequency: Medium

### Answer

TestFlight is Apple’s beta pipe. **Internal** testers are App Store Connect users on the team — fast, no review. **External** testers are anyone with a public/invite link — first build gets a Beta App Review. Builds expire (~90 days). You still need a distribution cert and a matching profile. Typical miss: treating TestFlight as a substitute for unit tests, or expecting external testers the same hour you upload.

### Example

```text
Internal: engineering + QA, same day
External: 10k waitlist, after beta review
```

### Follow-ups

- Internal vs external — who needs review?
- What happens when a build expires?
- TestFlight vs Ad Hoc vs enterprise?

## Git merge vs rebase {#git-merge-rebase}

- Level: Junior
- Frequency: Medium

### Answer

**Merge** adds a merge commit and keeps history as it happened. **Rebase** replays your commits on top of the new base — a straight line, rewritten SHAs. Rebase your *local* feature onto `main` before a PR; do not rebase commits others already pulled. `reset --soft` keeps changes staged; `--hard` throws them away. `stash` parks dirty files. `cherry-pick` copies one commit. Typical miss: rebase of `main` that everyone shares, then a force-push war.

### Example

```text
git fetch origin
git rebase origin/main    # your branch, not shared main
# conflict → fix → rebase --continue
```

### Follow-ups

- When is a merge commit the honest history?
- Soft vs hard reset of the last commit?
- What is `cherry-pick` for?
- What belongs in `.gitignore` on an iOS repo?
- What is a git hook you would actually install?

## Git Flow {#git-flow}

- Level: Junior
- Frequency: Medium

### Answer

Git Flow is a **branching model**: `main` (or `master`) is always releasable, `develop` is integration, `feature/*` branches off develop, `release/*` prepares a version, `hotfix/*` patches main. Many iOS teams now use a simpler GitHub-flow: short `feature` branches into `main`, tags for App Store builds. The interview answer is the model plus what *you* actually use — and why a three-month `feature` branch is the failure mode. Typical miss: reciting the diagram and then saying the team force-pushes `develop`.

### Example

```text
main      •——•——•tag 1.4——•hotfix
               \         /
develop    •——•——•——•release
                \
feature/pay  •——•
```

### Follow-ups

- Git Flow vs GitHub Flow for a weekly TestFlight?
- Where do you cut the App Store tag?
- What do you do with a hotfix that must also land on `develop`?

## Info.plist settings {#info-plist}

- Level: Junior
- Frequency: Medium

### Answer

Info.plist is the app’s declared contract with the OS: bundle ID, version, usage descriptions, URL schemes, document types, background modes, ATS, scene manifest, and encryption export. iOS 17+ can generate much of it from build settings, but the privacy strings are still yours — camera, location, tracking, Face ID, photo library. A missing usage description crashes at the prompt, not at compile time. Interviewers also expect `CFBundleURLTypes`, `UIBackgroundModes`, and `NSAppTransportSecurity` as the keys you have actually broken a build with. Keep secrets out of the plist; it is in the bundle anyone can unzip.

### Example

```xml
<key>NSCameraUsageDescription</key>
<string>Scan a barcode on your receipt.</string>
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>myapp</string>
        </array>
    </dict>
</array>
```

### Follow-ups

- XML vs binary plist — what can each store?
- Which keys crash at runtime if you omit the usage string?
- What moved from Info.plist into the target’s Info tab / generated plist?
- Why is a URL scheme a phishing risk, and what replaced it for auth?
- Where do you declare encryption so App Store export compliance is honest?

## Minimum deployment target {#deployment-target}

- Level: Mid
- Frequency: High

### Answer

The deployment target is the oldest OS you still install on. It is not the SDK you compile with — you always build against the newest SDK and gate new APIs with `@available` / `if #available`. Raising the target deletes `#available` branches and lets you use Swift concurrency, SwiftUI, and StoreKit 2 without back-deploys. Lowering it (or keeping it low) is a product call: analytics on OS share, not a language preference. Weak linking and `@available` keep a binary that runs on iOS 16 from touching an iOS 18 symbol. The App Store’s own cutoff and your crash rate on old OS versions are the data; “I like iOS 18 APIs” is not.

### Example

```swift
func presentPaywall() {
    if #available(iOS 17.0, *) {
        showStoreKit2Paywall()
    } else {
        showStoreKit1Paywall()
    }
}

@available(iOS 17.0, *)
func showStoreKit2Paywall() { /* Product.products(for:) */ }
```

### Follow-ups

- SDK vs deployment target — which one did you just change in Xcode?
- What actually happens if you call an iOS 18 API on iOS 16 without a check?
- How do you decide to drop iOS 16 this quarter?
- How do Swift availability and SPM `platforms:` get out of sync?

## XCTest and UI tests {#xctest}

- Level: Mid
- Frequency: High

### Answer

XCTest is the Apple test runner: a subclass of **`XCTestCase`** (ObjC: `@interface MyTests : XCTestCase`), methods that start with `test`, assertions (`XCTAssertEqual`, `XCTUnwrap`), and async `await` / **`XCTestExpectation`**. `setUp` / `setUpWithError` run before each test; `tearDown` after — that is the lifecycle, not `init`. Unit tests sit in a host app or a package and should not launch UI. UI tests launch `XCUIApplication()`, query `XCUIElement`s, and are slower and flakier — you keep a thin smoke path (launch, login, one purchase) and put logic in unit tests. `XCTest` also covers performance (`measure`) and attachments. The point of the suite is to lock **behavior you can rerun** — a refactor should fail a test, not a TestFlight user. A mid answer names the split, how you wait (`fulfill` an expectation, `XCTNSPredicateExpectation`, or Swift concurrency — not `sleep`), and why a test that talks to production is not a unit test.

### Example

```swift
final class CartTests: XCTestCase {
    func testEmptyCartDisablesCheckout() {
        let cart = Cart()
        XCTAssertFalse(cart.canCheckout)
    }
}

final class CheckoutUITests: XCTestCase {
    func testCheckoutButtonExists() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.buttons["Checkout"].waitForExistence(timeout: 2))
    }
}
```

### Follow-ups

- How do you wait for a network-backed screen without `sleep(3)`?
- What belongs in a UI test vs a snapshot test vs a unit test?
- How do you inject a fake API into UI tests?
- Why did a UI test fail on CI but pass on your Mac?
- What benefit do you actually sell a PM — not “coverage %”?
- `setUp` vs `setUpWithError` vs a lazy property on the test case?
- Expectation vs `async`/`await` in a test?
- What stays in XCTest after you adopt Swift Testing — UI tests, `measure`, something else?

## Testing async code {#test-async}

- Level: Mid
- Frequency: High

### Answer

An async unit test **awaits the work**, it does not `sleep`. In XCTest, mark the test `async throws` and `await` the function; use `XCTestExpectation` only when the API is still callback-based. Swift Testing uses `confirmation` / `await` the same way. Hop UI assertions onto `@MainActor` (or isolate the test type). Cancel in-flight tasks in `tearDown` so one test does not leak into the next. Inject a clock or a fake `URLProtocol` — do not hit the network. Typical miss: `wait(for:timeout:)` around a `Task { }` you never retain, or asserting on a `@MainActor` property from a background test thread.

### Example

```swift
func testLoadSetsTitle() async throws {
    let model = FeedModel(client: FakeClient(rows: ["Hi"]))
    try await model.refresh()
    XCTAssertEqual(model.title, "Hi")
}
```

### Follow-ups

- When is an expectation still required in 2026?
- How do you test that cancel actually stops the download?
- Swift Testing `confirmation` vs `XCTestExpectation` — what changed?

## Waterfall vs Agile {#waterfall-vs-agile}

- Level: Junior
- Frequency: Medium

### Answer

**Waterfall** is one pass: spec → design → build → test → ship. Requirements are supposed to be frozen. **Agile** (Scrum, Kanban) ships in short slices, tests inside the slice, and expects the spec to move. iOS teams almost always run some Agile flavor because App Review, OS releases, and design tweaks do not wait for a year-long phase. Waterfall still shows up in a fixed-bid contract or a certified medical build. Typical miss: “we are Agile” and a six-month release train with no shippable increment.

### Example

```text
Waterfall: lock the IA, then implement every screen, then QA.
Agile: ship onboarding this sprint, feed next, change the feed when review data lands.
```

### Follow-ups

- Where does App Review force you to plan more like waterfall?
- What is a sprint vs a milestone?
- How do you handle a late API change in each model?

## App and scene lifecycle {#app-lifecycle}

- Level: Junior
- Frequency: High

### Answer

Modern apps are **scene-based**. `UIApplicationDelegate` still gets `didFinishLaunching` for process-wide setup (logging, dependency graph). **`SceneDelegate` exists so one process can own multiple windows** (iPad Split View, a second window on Mac). The classic UIKit process states still get asked: **not running → inactive → active → background → suspended** (the system may kill a suspended app). Each window is a `UIScene`: `sceneDidBecomeActive`, `sceneWillResignActive`, `sceneDidEnterBackground`, `sceneWillEnterForeground`. Background is where you save, drop caches, and finish a short task (`beginBackgroundTask`). Active is where you refresh. SwiftUI wraps this with `@Environment(\.scenePhase)` — `.active`, `.inactive`, `.background`. Do not put “run once per install” work in `sceneDidBecomeActive`; it fires per scene and per return from background. Typical mistake: treating `didFinishLaunching` as “the UI is up” (it is not) or starting a long network call you cannot cancel when the scene backgrounds.

### Example

```swift
@main
struct AppMain: App {
    @Environment(\.scenePhase) private var phase

    var body: some Scene {
        WindowGroup {
            RootView()
        }
        .onChange(of: phase) { _, new in
            if new == .background { persist() }
        }
    }
}
```

### Follow-ups

- What still belongs in `AppDelegate` vs a scene delegate?
- How do you request extra background time for a write?
- `inactive` vs `background` — which one is a phone call overlay?
- Name the UIKit application states in order.
- Why was `SceneDelegate` added — what does a second window change?
- How do you restore the last screen after the system kills a suspended app?

## State restoration {#state-restoration}

- Level: Mid
- Frequency: Medium

### Answer

**State restoration** puts the user back where they were after the system kills a suspended process. You persist a small **restoration identifier** plus enough IDs to rebuild the stack (user id, playlist id, scroll offset) — not the whole object graph. UIKit: `restorationIdentifier` on VCs / views, encode in `encodeRestorableState`, decode in `decodeRestorableState` (or scene `stateRestorationActivity` / `NSUserActivity`). SwiftUI: `@SceneStorage` / `NavigationPath` you write to disk. Save in `sceneDidEnterBackground`; never wait for `applicationWillTerminate` (jetsam skips it). Typical miss: stuffing a decoded feed into UserDefaults, or restoring a screen whose auth token is already dead.

### Example

```swift
func sceneDidEnterBackground(_ scene: UIScene) {
    let activity = NSUserActivity(activityType: "com.app.restore")
    activity.userInfo = ["screen": "playlist", "id": currentPlaylistID]
    (scene as? UIWindowScene)?.userActivity = activity
}
```

### Follow-ups

- Restoration vs a cold launch that always opens Home — when is each right?
- What do you refuse to persist (tokens, huge images)?
- How does this interact with a login wall after a token expire?

## Background tasks {#background-tasks}

- Level: Mid
- Frequency: High

### Answer

Once the scene backgrounds, you have seconds, not minutes. **`beginBackgroundTask`** buys a short expiration window to finish a save or upload; you must call `endBackgroundTask` or the system kills you. **`BGTaskScheduler`** (`BGAppRefreshTask`, `BGProcessingTask`) is the modern “wake me later” API — you register identifiers, submit a request, and the system decides when. Background modes (audio, location, VoIP, Bluetooth) are entitlements, not a general CPU grant. Silent push (`content-available`) can wake you briefly if the user allowed it. Typical miss: a `Timer` you started on screen and expected to keep firing while suspended — it will not.

### Example

```swift
var task: UIBackgroundTaskIdentifier = .invalid
task = UIApplication.shared.beginBackgroundTask {
    UIApplication.shared.endBackgroundTask(task)
    task = .invalid
}
persist()
UIApplication.shared.endBackgroundTask(task)
```

### Follow-ups

- `beginBackgroundTask` vs `BGAppRefreshTask` vs a silent push?
- What happens if you forget `endBackgroundTask`?
- Which background modes will App Review actually accept?

## Swift Testing {#swift-testing}

- Level: Mid
- Frequency: High

### Answer

Swift Testing is the newer runner next to XCTest: `@Test` functions (no `XCTestCase` subclass), `#expect` (records and continues) vs `#require` (stops), `@Suite` for grouping, and **parameterized** `@Test(arguments:)`. Traits skip or serialize (`.disabled`, `.timeLimit`, `.serialized`). **Migrate in place:** new tests in Swift Testing, leave old XCTest until you touch it; both can live in one target (not inside an `XCTestCase`). Interop lets a helper call `XCTFail` from a `@Test` (or `Issue.record` from XCTest) — complete/strict mode keeps that an error. Keep XCTest for UI automation, `measure`, and ObjC exceptions. Typical miss: rewriting every `XCTAssert` on day one, or treating `#expect` like `XCTAssert` that aborts.

### Example

```swift
import Testing

@Test("empty cart disables checkout")
func emptyCart() {
    #expect(Cart().canCheckout == false)
}

@Test(arguments: [0, 1, 2])
func quantity(_ n: Int) {
    #expect(n >= 0)
}
```

### Follow-ups

- `#expect` vs `#require` vs `XCTAssert`?
- How do you parameterize a test in XCTest vs Swift Testing?
- Do UI tests move to Swift Testing yet?
- Why do `@Test`s run in parallel by default — what does `.serialized` change?
- Why does `#require` need `try` when `#expect` does not?
- `try #require(optional)` vs force-unwrap in a test — what do you still run after `nil`?
- `#expect(throws:)` vs a `do` / `catch` you wrote by hand?
- Confirmation / callback — when is that better than `await`?
- `Issue.record` vs `XCTFail` — when does interop turn a pass into a warning?
- `Test.cancel` vs `.disabled` vs `XCTSkip`?

## Take-home interview {#take-home}

- Level: Mid
- Frequency: High

### Answer

A take-home is judged like a PR, not a puzzle. Two common shapes: **greenfield** (list + pagination + empty/error + DI + a few tests) and **improve a starter** (do not rewrite the locked folder; ship empty/error, one extra screen, tests). Clarify the brief first (architecture they want, time box, must-have vs nice). Then: it builds clean, no warnings, a short README (how to run, what you skipped and why), a visible architecture, tests where they pay off, and you stay near the time limit. Skip extra libraries unless you write why. Interviewers look at structure and tradeoffs more than polish. Typical miss: a 20-hour masterpiece for a 2-hour prompt, a README that does not say how to run it, or a rewrite that breaks the existing client.

### Example

```markdown
# Feed
Xcode 16, iOS 17. Open `Feed.xcodeproj` and run the `Feed` scheme.
I skipped pagination to stay in the time box; the list is a `UITableView` + MVVM.
```

### Follow-ups

- What do you cut first when time is short?
- When do you add a third-party networking library?
- How do you show architecture without a 4-page essay?
- Product list from JSON (image, name, price, sort) — what do you cut first?
- Social feed from users/posts/albums JSON — how do you model the screens?
- GitHub Followers-style brief (search user, paginated collection, favorites in UserDefaults, no third-party libs) — what do you ship in four hours?
- Custom animated UI (onboarding / card stack) — polish first or a boring working list?
- 90-minute machine-coding: working demo vs extra rules you did not finish?
- 60-minute live checkout (list, totals, pay method) — what is on screen at minute 25?
- 90-minute laptop, internet allowed — when is a search a signal vs a miss?
- Starter with five TODOs (animation, async queue, list, settings) — which two do you ship?
- They lock `ios-interview-test/` — what do you refuse to touch?
- Contacts / address book from JSON, offline cache, fake `URLSession` — what is in the first PR?
- 40-minute clone-into-Xcode screen vs a 2–4 hour take-home — what do you drop?
- A 1–3 week marketplace “test project” — do you treat it like a take-home?

## Improve an existing take-home app {#improve-existing-app}

- Level: Mid
- Frequency: High
- Kind: Practice

### Prompt

You get a **working starter** (search a word, show a definition, or a thin list). You have **2–4 hours**. Do not rewrite it from scratch. Ship: empty and error states, one extra screen or a second endpoint, protocol-based DI so a test can fake the session, and a README of what you skipped. The interview is “did you leave the existing code running?” Do not paste a third-party solution.

### Follow-ups

- Easter egg vs error handling — which one do they actually score?
- SwiftUI rewrite of the whole app in four hours — do you start it?
- How do you show the change in a PR they can review in ten minutes?

## Screening OA / assessment platform {#screening-oa}

- Level: Mid
- Frequency: High

### Answer

The first filter is often a **20–80 minute platform**, not a live Xcode room. Two shapes: **work-sample** (fix a leak without changing the public API, wire a table, a small HTTP call, a protocol) in their editor or a **clone-into-your-IDE** starter; and a **timed contest** (easy/medium algo) before any iOS theory. MCQ screens (language trivia, “which objects does a table need”) are a weak signal — treat them as a vocabulary check. A week-long marketplace project is a different product; do not treat it as a 4-hour take-home. Typical miss: grinding Hard graphs for a screen that is a retain cycle and a `UITableView`, or pasting a premium-test dump.

### Example

```text
30 min: MCQ + one leak / protocol task in the browser.
60–75 min: clone a starter, fill methods, run their tests.
Contest OA: 2–3 timed problems, then a human room if you pass.
```

### Follow-ups

- Browser editor vs clone-to-Xcode — what can you not prove?
- They say “do not change the public API” on a leak — what is left to edit?
- Contest first filter vs a hosted refactor — which prep do you drop?

## STAR stories {#star}

- Level: Mid
- Frequency: High

### Answer

Behavioral answers need a story, not “yes I am a leader.” **STAR:** Situation (one sentence), Task (what you owned), Action (most of the airtime — what *you* did), Result (outcome, numbers if you have them). Prepare a small set: conflict, missed deadline, mentoring, a hard bug, a proud feature. Practice out loud; do not memorize a script. Personal projects count. Typical miss: a 4-minute Situation and one sentence of Action.

### Example

```text
S: Release week, checkout API started 500ing.
T: I owned the iOS client hotfix.
A: I added a client timeout + retry, shipped a feature flag, wrote the postmortem.
R: Error rate back under 0.2% the same day; we kept the flag for the next API migrate.
```

### Follow-ups

- What if you do not have a work story — can a side project count?
- How do you talk about a failure without dumping on your team?
- Why spend most of the answer on Action?
- Amazon LP vs Googleyness vs Meta behavioral — same stories, different labels?

## Continuous integration {#ci}

- Level: Mid
- Frequency: High

### Answer

CI is a machine that runs your checks on every push: build, unit tests, sometimes UI tests and lint. On iOS that is Xcode Cloud, GitHub Actions + `xcodebuild`, or Fastlane. You want a failing PR to be unmergeable, not a Slack message someone ignores. Add TestFlight / internal deploy as a second job, not as a substitute for tests. Typical miss: “we have CI” that only archives, never tests.

### Example

```yaml
# sketch — GitHub Actions
# xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'
```

### Follow-ups

- What belongs on CI vs only on a nightly?
- How do you keep simulator UI tests from making every PR 40 minutes?
- Fastlane vs a raw `xcodebuild` script?
- CI vs CD — where does TestFlight sit?

## Code coverage {#code-coverage}

- Level: Mid
- Frequency: Medium

### Answer

Coverage is the percent of lines (or branches) a test suite executed. Xcode can emit it per target. It is a **spotlight**, not a grade: 90% of getters is worse than 60% on the checkout state machine. Use it to find untested modules, not to fail the build at an arbitrary number. Typical miss: chasing 100% and testing SwiftUI previews.

### Example

```swift
func canCheckout(items: Int, total: Decimal) -> Bool {
    items > 0 && total > 0
}
// A test that only passes `items: 1, total: 1` leaves the false branches uncovered.
```

### Follow-ups

- Line coverage vs branch coverage?
- When would you fail CI on coverage dropping?
- What do you do with a 0% file that is all UIKit glue?

## Third-party vs custom {#third-party-vs-custom}

- Level: Mid
- Frequency: High

### Answer

Default to the system library. Take a dependency when it is a real product (maps, payments, crash reporting) or a problem you will not maintain well. Ask: license, size, last commit, who owns updates, can we delete it in a year, does it force a module boundary. Roll your own when the API is small and central (a thin `URLSession` wrapper). Write the reason in the PR. Typical miss: adding Alamofire for one GET, or rewriting Date formatting for six months.

### Example

```text
Need image caching → Kingfisher / Nuke, or URLCache + NSCache if the feature is one screen.
Need JSON → Codable first.
```

### Follow-ups

- How do you wrap a third-party so you can replace it?
- SPM vs CocoaPods vs Carthage in 2026?
- What goes in a greenfield baseline (lint, CI, SPM) before features?
- One GET — `URLSession` or Alamofire?

## Binary framework vs SDK {#binary-framework}

- Level: Mid
- Frequency: Medium

### Answer

An **SDK** is the product you give other apps: headers or a Swift module, docs, maybe a sample. A **binary framework** (`.xcframework`) is one delivery shape — compiled slices, no source. You ship a binary when you cannot open-source the code, want faster client compiles, or must support multiple platforms in one artifact. SPM can vend source *or* an `.xcframework`. Versioning, module stability (`BUILD_LIBRARY_FOR_DISTRIBUTION`), and a dead-simple public API are the interview. ABI-stable Swift on Apple OSes does **not** make your SDK’s `public` types resilient — that is a separate compiler mode. Typical miss: calling any `import Foo` an SDK, or shipping a fat `.framework` that does not contain the Simulator slice.

### Example

```text
xcodebuild archive … BUILD_LIBRARY_FOR_DISTRIBUTION=YES
xcodebuild -create-xcframework \
  -framework ios.xcarchive/…/Payments.framework \
  -framework sim.xcarchive/…/Payments.framework \
  -output Payments.xcframework
```

### Follow-ups

- Source package vs binary XCFramework — when do you pick each?
- Static vs dynamic linking — what changes at launch and in the IPA?
- What does `@_spi` / a closed `public` surface buy you?
- How do you distribute to a team that is not on your git remote?
- ABI stability of the OS vs module stability of *your* XCFramework?

## FAANG iOS loop {#faang-ios-loop}

- Level: Senior
- Frequency: High

### Answer

Big-tech iOS loops are **not** a UIKit trivia quiz. A 2026 mid-size loop is often **4–5 rooms**: Swift / memory screen, **live Xcode** (a small feature or a leak, process over autocomplete), **mobile system design** (cache, offline, chat — client constraints), **behavioral** (STAR with an iOS story), hiring-manager fit. Big-tech still adds DSA. Some loops add an **IDE build-a-screen** room — working UI first, Clean Architecture later. Hardware-first orgs probe **privacy and device constraints** before you draw a load balancer. Leveling often sits on design + behavior, not on whether you finished the hard LeetCode. They want you talking: clarify, complexity, then code. Typical miss: memorizing `UITableView` delegates and never practicing a 45-minute chat/feed design, or repeating the same STAR story in two rooms.

### Example

```text
Meta L5-ish: screen (2 coding) → onsite (behavior + mobile SD + 3 coding).
Amazon senior: every room mixes LP + coding; one long mobile SD.
Google L4 iOS: DSA (sometimes in Swift) + a short iOS-concepts tail; team match later.
```

### Follow-ups

- What do you practice if they say “iOS domain” and then hand you a graph?
- How is mobile SD different from backend Instagram-on-a-whiteboard?
- Why does a behavioral that ends 10 minutes early worry you?
- Live Xcode vs a shared doc — what are they scoring besides the compile?
- Product iOS team: no LeetCode — they paste a deadlock or a data race in Xcode. What is your first instrument?
- High-volume coding loop: two or three mediums in 45 minutes — journey or a running answer?
- How is a CIS bank/marketplace loop different — refactor + architecture instead of three LeetCodes?
- First clarifying questions on a device-first SD — privacy model, 72-hour offline, what the server may see?
- IDE round: when do you stop decorating architecture and ship a list?
- Remote loop for a Brazil-based candidate — same rooms, often in English. What changes in how you practice?

## CIS product-company iOS loop {#cis-ios-loop}

- Level: Senior
- Frequency: High

### Answer

Large CIS product companies (banks, classifieds, super-apps) usually run **HR → theory / platform → a practical room → team match**, not a FAANG-style stack of graphs. The practical room is often **two halves**: a **hosted refactor** (make this Playground / web editor compile, name the smells, add a test) and an **architecture whiteboard** (a feature, not Pastebin). Live-coding, when it exists, is easy/medium in a Playground and they grade thinking-out-loud more than the optimal tree. Theory blocks they actually score: memory, GCD / isolation, persistence, Swift, UI, patterns. Typical miss: grinding only LeetCode Hard and freezing when they paste a 80-line ViewController and say “clean this up.”

### Example

```text
60 min screen: code review + 3 theory (easy / mid / senior).
90–120 min: refactor on a shared editor → feature architecture on a board.
30–60 min: team / hiring manager.
```

### Follow-ups

- What do you say first on a refactor — tests, naming, or the retain cycle?
- They change the brief mid-architecture — what do you drop?
- Playground vs a real Xcode project — what can you not demonstrate?
- How is an India-style 90-minute machine-coding room different?
- Timed contest OA as the first filter — what do you practice that a Playground refactor does not?

## India product-company iOS loop {#india-ios-loop}

- Level: Senior
- Frequency: High

### Answer

Large India product companies often run **OA / DSA → a machine-coding room → a walkthrough → HM**, not a stack of UIKit trivia. Machine coding is **90–120 minutes**: a small working app or an in-memory LLD (list + a rules engine), **MVVM or clear modules**, correct logic, names you can defend. UI polish is usually out of scope. They then sit with you and ask “how would you add a new rule without rewriting the scorer?” Typical miss: a pretty screen and a `switch` that cannot take a wide / extra event, or spending 40 minutes on architecture diagrams and shipping nothing that runs.

### Example

```text
30 min: read the brief, lock entities + extra rules as protocols.
90 min: two screens or a driver + tests; demo the happy path.
45 min: walkthrough — extensibility, edge cases, complexity.
```

### Follow-ups

- Working demo with two missing extras vs a perfect design that does not run?
- Where do new match / order rules live — enum + protocol, or another `if`?
- They allow any image library — do you add one?
- How is a Brazil product-company loop different — live Xcode + offline-first SD, not a 90-minute rules engine?

## Brazil product-company iOS loop {#brazil-ios-loop}

- Level: Senior
- Frequency: High

### Answer

Large Brazil product companies (and remote US/EU loops that hire from there) usually run **screen → live Xcode → mobile system design → behavioral → HM**, not a trivia quiz and not a 90-minute machine-coding dump. The screen is Swift / memory / UIKit vs SwiftUI. Live Xcode is 60–90 minutes: a feature or a leak, **process and narration**, not autocomplete. System design is **device-first**: offline-first sync, battery, App Store background limits — that offline question is the one they actually like. Behavioral wants a hybrid UIKit/SwiftUI migration or an Instruments story, not “I shipped a list.” Remote rooms are often **in English**. Course platforms teach Swift; they do not teach talking while you code. Typical miss: memorizing 50 junior/pleno/sênior Q&A and freezing when they say “the user loses the network on the way to checkout.”

### Example

```text
30–45 min screen: Swift, ARC, UIKit vs SwiftUI.
60–90 min live Xcode: small feature, narrate, handle the empty state.
45 min SD: offline-first feed or checkout; battery and background last.
45 min STAR + HM.
```

### Follow-ups

- Offline-first SD — what do you persist before you draw a server box?
- Technical rooms in English — do you switch language mid-answer?
- A local course track vs a spoken HWS pass — what is still missing?
- Marketplace loop (live checkout, almost no LeetCode) — what do you drop from FAANG prep?

## Marketplace iOS loop {#marketplace-ios-loop}

- Level: Senior
- Frequency: High

### Answer

Consumer-marketplace iOS loops (delivery, rides, checkout) usually run **recruiter → 60-minute live feature → mobile SD → behavioral**, not a stack of graphs. The live room is a **working screen**: item list, totals, a pay-method picker, or a search list from a mock API. They want a ViewModel, empty/error, and something that runs by minute 25 — polish and a repository layer you narrate as “I would add later.” System design is **offline, GPS, battery, dispatch**, not Kafka. Some neighbor loops add a **90-minute laptop** on your machine (internet on): a fare / rules module that survives a new requirement at minute 50. Typical miss: grinding Hard LeetCode and shipping no list, or a pretty checkout that double-taps Pay.

### Example

```text
5 min: skim the starter, lock the happy path.
25 min: list + totals on screen.
45 min: pay method / confirm + empty and error.
SD: offline cart, stale GPS, what you persist across a kill.
```

### Follow-ups

- Working UI at 25 vs a perfect architecture that does not compile?
- They add a city fee at minute 50 — what did you leave closed?
- Phone-screen graphs with a geo story — do you still write the brute force first?

## App Store review {#app-store-review}

- Level: Junior
- Frequency: Medium

### Answer

A store build is not “CI archived it.” Apple runs **automated checks** (crash on launch, private API, missing privacy nutrition labels / manifests) and a **human review** against the App Review Guidelines. Common rejects: a login that reviewers cannot pass, broken IAP, placeholder content, missing usage strings, and “this is a website wrapper.” TestFlight **external** testers get a lighter Beta App Review; **internal** testers skip it. Review is not a substitute for your tests — it is a gate. Typical miss: shipping a debug endpoint or a hardcoded reviewer password in the binary comments.

### Example

```text
Checklist before upload:
- Reviewer demo account in App Store Connect notes
- Privacy Nutrition Labels + Privacy Manifest match what you collect
- IAP products ready in the sandbox
- No crash on a clean install / no network
```

### Follow-ups

- Internal TestFlight vs external vs App Store — which ones get a human?
- What do you do in the first 24 hours after a Guideline 2.1 reject?
- Privacy Manifest vs the App Privacy questionnaire — which one is in the binary?
- Required Reason APIs in the manifest — what happens if you omit one?
