# Architecture

25 cards · 13 often asked · source [architecture.md](../../topics/architecture.md)

### Junior

<h2 id="delegates">Delegates</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A delegate is an object you ask to make decisions or receive events, almost always through a protocol. `UITableView` does not know your screen — it calls methods like `tableView(_:didSelectRowAt:)` on whatever you assigned as `delegate`. That relationship is one-to-one, not a broadcast. Hold a class delegate `weak`, because the usual UIKit shape is “controller owns the view, view points back at the controller.” If both sides are strong, you leak. Mark the protocol `AnyObject` so `weak` is legal.



```swift
protocol SearchDelegate: AnyObject {
    func searchDidFinish(_ results: [String])
}

final class SearchService {
    weak var delegate: SearchDelegate?

    func run(_ query: String) {
        delegate?.searchDidFinish(["\(query) hit"])
    }
}
```


**Then they usually ask**

- Why is the delegate usually `weak`?
- Delegate vs `NotificationCenter` vs a closure callback?
- Data source vs delegate — what belongs in each?
- What breaks if the protocol is not `AnyObject`?
- Can you implement delegation without a protocol — and why do you still want one?

</details>

<h2 id="mvc">MVC</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

MVC splits a screen into Model, View, and Controller. The model is data and rules with no UIKit. The view draws. The controller loads the model and updates the view — on iOS that is usually a `UIViewController`. Apple’s templates start you there, so name it, then name the failure: the controller absorbs networking, mapping, and navigation until it is thousands of lines. I still use MVC for a small screen. I pull work out the moment the controller starts knowing about URLs or how to format currency. Migrating MVC → MVVM is incremental: extract a ViewModel for one screen, keep UIKit out of it, bind state, leave navigation until the controller is thin — do not rewrite the app in one PR.



```swift
struct Note {
    var text: String
}

final class NoteViewController {
    private let note: Note
    private(set) var labelText = ""

    init(note: Note) {
        self.note = note
        labelText = note.text
    }
}
```


**Then they usually ask**

- What do people mean by Massive View Controller?
- Where should a network call live in MVC?
- MVC vs MVVM — when do you switch?
- Does SwiftUI still have a controller?
- How would you migrate one Massive View Controller to MVVM without a rewrite?

</details>

<h2 id="global-variables">Global variables</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A file-level `var` is shared mutable state with no owner. Tests cannot reset it reliably, two screens fight over it, and you cannot inject a fake. `let` globals for constants (`let maxRetry = 3`) are fine. Need one live service? Inject it, or a narrow `shared` you can still replace in tests. Typical miss: a `var currentUser` at file scope that every VC reads.



```swift
enum Config {
    static let maxRetry = 3
}

struct Session {
    var user: User?
}

final class ProfileViewModel {
    var session: Session
    init(session: Session) { self.session = session }
}
```


**Then they usually ask**

- Global `let` vs global `var` — which one is the actual problem?
- How is this different from a singleton?
- How do you test code that already reads a global?

</details>

<h2 id="oop-pillars">OOP pillars</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Four words interviewers still want, with an iOS example each. **Encapsulation:** hide storage, expose a small API (`private(set)`). **Abstraction:** talk to a protocol, not `URLSession` in the view. **Inheritance:** `UIViewController` subclasses — cheap, easy to overuse. **Polymorphism:** the same `draw()` on different `UIView` subclasses, or `any FeedLoading`. Swift leans on protocols more than deep class trees. Typical miss: reciting the list with no example, or calling “a struct with methods” inheritance.



```swift
protocol Drawable { func draw() }
struct Circle: Drawable { func draw() { /* */ } }
struct Rect: Drawable { func draw() { /* */ } }
func render(_ items: [any Drawable]) { items.forEach { $0.draw() } }
```


**Then they usually ask**

- Which pillar does a Swift protocol primarily serve?
- When is inheritance the wrong tool in UIKit?
- How does encapsulation differ from `private`?
- Can a Swift class inherit from two superclasses?

</details>

### Mid

<h2 id="dependency-injection">Dependency injection</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Dependency injection means a type does not construct its collaborators — they are passed in. Three kinds interviewers name: **initializer** (`init(api:)` — preferred), **property** (set after `init`, common with storyboards), **method** (pass the collaborator into one call). Tests pass a stub, previews pass a fixture, production passes the live client. Calling `Foo.shared` inside a method is the opposite: a hidden dependency. I do not bring in a container for a small app. A composition root that builds the graph, plus a protocol at each I/O boundary, is enough.



```swift
protocol Clock {
    func now() -> Date
}

struct SystemClock: Clock {
    func now() -> Date { Date() }
}

final class Session {
    private let clock: Clock
    init(clock: Clock) { self.clock = clock }

    var isExpired: Bool { clock.now() > Date.distantPast }
}
```


**Then they usually ask**

- Initializer injection vs property injection vs a service locator?
- How do you inject into a `UIViewController` from a storyboard?
- When is a DI container worth it on iOS?
- How does this change SwiftUI previews?
- How is constructor injection different from depending on a protocol (DIP)?

</details>

<h2 id="design-patterns">Design patterns in iOS</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Do not recite the Gang of Four. Group what you have actually shipped. **Creational:** factories and DI instead of `Foo.shared` everywhere; builder for a long `URLRequest`. **Structural:** adapter (wrap a C API), decorator (a `URLProtocol`), facade (a `Session` type in front of Keychain + network). **Behavioral:** delegate (table view), observer (`NotificationCenter`, Combine), strategy (a `Pricing` protocol), coordinator / router for navigation. UIKit already is MVC plus delegates. SwiftUI pushes you toward MVVM and observation. Name a tradeoff for each: delegates are one-to-one and leak if strong; singletons are easy and hide dependencies; coordinators add types but keep view controllers small. Typical mistake: listing twenty patterns with no iOS example.



```swift
protocol FeedLoading {
    func load() async throws -> [Post]
}

struct LiveFeed: FeedLoading {
    func load() async throws -> [Post] { try await API.feed() }
}

struct PreviewFeed: FeedLoading {
    func load() async throws -> [Post] { [.placeholder] }
}

final class FeedViewController: UIViewController {
    init(loader: FeedLoading) { /* DI — strategy */ }
}
```


**Then they usually ask**

- Delegate vs closure vs `NotificationCenter` for one event?
- Which patterns does UIKit already implement for you?
- When is a coordinator worth the extra types?
- Where does Memento show up on iOS (`NSCoder`, undo, state restoration)?
- What is a *bad* pattern in an iOS app — Massive VC, singleton god, delegate that is strong?

</details>

<h2 id="feature-flags">Feature flags</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A feature flag is a **runtime switch** for a code path: remote config, a local override, or a compile-time `#if`. You use it to ship dark, roll out to 10%, kill a bad release, or run an A/B. The client must treat the flag as **untrusted and late** — default to the safe path, cache the last known value for offline, and never block launch on the config fetch. Interviewers want the ops story: who owns the flag, how you delete it after the experiment, and how a kill switch reaches devices (push / background fetch / next launch). Typical miss: wrapping every line in `if flag` until the module is unreadable, or a flag that requires an App Store build to turn off.



```swift
protocol Flagging {
    func isOn(_ key: FlagKey) -> Bool
}

func makeFeed(flags: Flagging) -> any FeedServing {
    flags.isOn(.newRanking) ? RankingFeed() : LegacyFeed()
}
```


**Then they usually ask**

- Kill switch vs experiment vs gradual rollout — same flag?
- How fast can a remote flag reach a suspended app?
- Where do you put the default when the config server is down?

</details>

<h2 id="mvvm">MVVM</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

MVVM puts a ViewModel between the view and the rest of the app. The ViewModel owns presentation state and talks to services; the view renders that state and forwards taps. **In the VM:** loading flags, mapped display strings, validation, calls to the API/repository. **Not in the VM:** `UIView`, `UIColor` (unless you abstract them), storyboard identifiers, Auto Layout. I expose something bindable — `@Published`, `@Observable`, a publisher — and I keep UIKit and SwiftUI types out so I can unit-test with a fake API. Navigation is the usual fight: if the ViewModel presents a view controller, the split is already broken. Chatty bindings that rebuild everything on each keystroke are the other smell. Treat the ViewModel as a state machine; let the view layer present.



```swift
final class LoginViewModel {
    var username = ""

    var canSubmit: Bool { username.count >= 3 }

    func submit() -> Result<Void, LoginError> {
        canSubmit ? .success(()) : .failure(.tooShort)
    }
}

enum LoginError: Error { case tooShort }
```


**Then they usually ask**

- How do you unit-test a ViewModel?
- Where do navigation and alerts belong?
- MVVM vs MVC on a single `UIViewController` screen?
- What goes wrong with two-way bindings?
- What typically lives in a ViewModel vs the view?
- What is the MVVM failure mode — a Massive ViewModel?

</details>

<h2 id="protocol-oriented-programming">Protocol-oriented programming</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Protocol-oriented programming means you design around capabilities, not class trees. A protocol names what something can do; an extension can give a default; structs and enums can conform, which inheritance cannot offer. I extract protocols at boundaries — networking, disk, a clock — so tests can supply a double. The trap is a protocol per concrete type, or a protocol that wants stored properties you then fake with associated-type noise. Start with a concrete type. Lift a protocol when you have a second implementation or a test fake.



```swift
protocol Fetching {
    func fetch() async throws -> Data
}

extension Fetching {
    func fetchString() async throws -> String {
        String(decoding: try await fetch(), as: UTF8.self)
    }
}

struct LiveClient: Fetching {
    func fetch() async throws -> Data { Data() }
}
```


**Then they usually ask**

- POP vs class inheritance — when is a base class still better?
- What problem do associated types create for `any` / `some`?
- Protocol extension vs a free function?
- When is a protocol one conformance too early?

</details>

<h2 id="repository">Repository pattern</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A repository is a type that **hides where data comes from**. The rest of the app asks `func user(id:) async throws -> User` and does not know if the answer came from `URLSession`, Core Data, a memory cache, or a test fixture. The repository maps DTOs and store objects into **domain** models and translates infrastructure errors into domain errors. Versus a “service”: a service often *does* a use case; a repository *loads and saves*. Typical miss: a `UserRepository` that returns `UserDTO` and leaks `URLError` into the ViewModel, or one god repository for every entity.



```swift
protocol UserRepository {
    func user(id: UUID) async throws -> User
}

struct RemoteUserRepository: UserRepository {
    let client: HTTPClient
    func user(id: UUID) async throws -> User {
        let dto: UserDTO = try await client.get("/users/\(id)")
        return User(id: dto.id, name: dto.fullName)
    }
}
```


**Then they usually ask**

- Repository vs use case vs ViewModel — who owns what?
- How do you swap Core Data for SwiftData without rewriting screens?
- Why translate `URLError` at this boundary?

</details>

<h2 id="solid">SOLID</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Five design checks, not a religion. **S**ingle responsibility: a VC that only binds UI, a service that only talks HTTP. **O**pen/closed: add a new `PaymentMethod` conformance instead of editing a switch. **L**iskov: a subclass must honor the parent’s contract — no `fatalError` in an override the caller expects. **I**nterface segregation: a small `Logging` beat a 20-method `GodService`. **D**ependency inversion: depend on a protocol, inject the live type. Typical miss: expanding every letter into a lecture and never naming a type in your last app.



```swift
protocol Paying { func pay() async throws }
struct Checkout {
    let payment: Paying
    func run() async throws { try await payment.pay() }
}
```


**Then they usually ask**

- Loosely vs tightly coupled — which SOLID letter is that?
- Which SOLID rule is a 2 000-line view controller breaking?
- Open/closed vs “we never change existing files”?
- How does DIP show up as constructor injection?
- DI vs DIP — one sentence each?

</details>

<h2 id="singletons">Singletons — when they help</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A singleton is one instance for the process, usually `static let shared` and a private `init`. It helps when two instances would be wrong or expensive — a keychain wrapper, `FileManager.default`, a socket you must not open twice. Interviewers call it an **anti-pattern** when it hides dependencies: every type that reaches for `Analytics.shared` is untestable and order-dependent. The cost is global mutable state: tests share leftovers, and a type that calls `Analytics.shared` cannot take a no-op in a preview. **`static let` is thread-safe to create** (Swift lazily initializes it once). The ObjC equivalent they still ask is `dispatch_once` around the alloc — do not roll `@synchronized` or a bare `if (shared == nil)`. Mutating properties on `shared` are not thread-safe — protect them with an actor, a serial queue, or a lock. I let the singleton exist, then pass it in. Defaulting a parameter to `.shared` is fine at the edge, not inside domain logic.



```swift
protocol Analytics {
    func track(_ event: String)
}

final class AnalyticsClient: Analytics {
    static let shared = AnalyticsClient()
    private init() {}
    func track(_ event: String) { /* send */ }
}

final class Checkout {
    private let analytics: Analytics
    init(analytics: Analytics = AnalyticsClient.shared) {
        self.analytics = analytics
    }
}
```


**Then they usually ask**

- How do you test code that uses a singleton today?
- Singleton vs a shared instance you still inject?
- What thread-safety issues show up on `shared`?
- When is a singleton the wrong tool for “I only need one”?
- How did you make a thread-safe singleton in Objective-C?
- Why do interviewers call Singleton an anti-pattern — and when do you still keep one?

</details>

<h2 id="functional-programming">Functional programming in Swift</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift is not a functional language, but it borrows the parts that help. Functions are values, so `map`, `compactMap`, `filter`, and `reduce` replace a lot of mutable loops. I prefer transforming values over mutating shared objects, and I like small functions that take data and return data. Trailing closures make that comfortable. I do not chase purity or custom operators in app code. Hidden mutation inside a `map` is worse than an honest `for` loop.



```swift
let prices = [9.99, 4.50, 12.00]
let taxedTotal = prices
    .filter { $0 >= 5 }
    .map { $0 * 1.2 }
    .reduce(0, +)
```


**Then they usually ask**

- `map` vs `compactMap` vs `flatMap`?
- When is a `for` loop clearer than a pipeline?
- What does it mean that `Array` is a value type with copy-on-write?
- How do you keep a Combine / async pipeline from hiding side effects?
- Functional vs OOP — when do you still want a class hierarchy?

</details>

<h2 id="kvc">KVC</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Key-Value Coding is the ObjC runtime’s **string-key** access: `value(forKey:)`, `setValue(_:forKey:)`. KVO is built on it. You still meet it in Core Data, `NSSortDescriptor`, Cocoa bindings leftovers, and `setValue` from a dictionary. It bypasses your Swift access control and can hit a wrong key at runtime (`valueForUndefinedKey`). In new Swift, prefer key paths (`\Foo.bar`) and typed properties. Typical miss: using KVC to set a private property “because it works.”



```swift
let label = UILabel()
label.setValue("Hi", forKey: "text")
let text = label.value(forKey: "text") as? String
```


**Then they usually ask**

- KVC vs KVO vs key paths — one sentence each?
- Why can KVC skip your custom setter?
- Where does Core Data still require it?

</details>

<h2 id="mvp">MVP</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

MVP puts a **Presenter** between view and model. The view is a passive protocol (`show(items:)`, `showError`) — often the view controller. The presenter loads data and tells the view what to display; it does not own UIKit types if you keep the protocol honest. Versus MVVM: the presenter **pushes** commands into the view; the view model **exposes state** the view pulls/binds. MVP is easier to follow in UIKit without Combine. MVVM fits SwiftUI and `@Published` better. Typical miss: a presenter that still calls `view.tableView.reloadData()`.



```swift
protocol LoginViewing: AnyObject {
    func showError(_ text: String)
}

final class LoginPresenter {
    weak var view: LoginViewing?
    func submit(name: String) {
        if name.count < 3 { view?.showError("Too short") }
    }
}
```


**Then they usually ask**

- MVP vs MVVM — who owns the screen state?
- Why is the view protocol `AnyObject` and `weak`?
- When is Clean Architecture more than either of these?

</details>

<h2 id="atomic-nonatomic">atomic vs nonatomic vs copy</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

These are **Objective-C property attributes**, not Swift keywords. `atomic` (the ObjC default) synthesizes a lock around the getter/setter so you get a whole value, not a torn pointer — it is **not** thread-safe mutation of the object graph. `nonatomic` skips the lock; UIKit used it everywhere for speed. `copy` sends `copy` on set so you keep an immutable snapshot (`NSString`, `NSArray`) instead of a mutable subclass that changes under you. `@property (copy) NSMutableArray *array` is a trap: `copy` produces an **immutable** `NSArray`, and the next `addObject` crashes. Use `strong` plus a defensive `copy` inside the setter, or keep a mutable ivar. In Swift you write `var title: String` (value semantics) or an explicit `NSLock`. Typical mistake: “I marked it atomic, so my array is thread-safe.”



```objc
@property (nonatomic, copy) NSString *title;
@property (atomic, strong) NSNumber *count;
```


**Then they usually ask**

- Why does `atomic` not make a collection safe to mutate from two queues?
- When do you still need `copy` in a Swift `@objc` property?
- What replaced this thinking in Swift (`let`, actors)?
- `copy` vs `retain` / `strong` — when do you want a snapshot?

</details>

<h2 id="kvo">KVO</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

KVO is Key-Value Observing from the Objective-C runtime. You watch a key path and get a callback when that property changes. In Swift the type must inherit `NSObject`, the property must be `@objc dynamic`, and you keep the `NSKeyValueObservation` token or the observation dies. Apple’s default implementation **creates a subclass at runtime**, overrides the setter, and **swizzles `isa`** so the instance looks like that subclass — that is why a manual `setValue` or a direct ivar write can skip KVO unless you wrap it in `willChangeValue` / `didChangeValue`. I do not add new KVO in Swift. A publisher, `Observation`, or a delegate is easier to follow. I still need to recognize it, because some system types only publish this way — `AVPlayer`, `NSProgress`, a few UIKit bits.



```swift
final class Transport: NSObject {
    @objc dynamic var rate: Double = 0
}

let transport = Transport()
let token = transport.observe(\.rate, options: [.new]) { _, change in
    print(change.newValue ?? 0)
}
transport.rate = 1
```


**Then they usually ask**

- Why `@objc dynamic`, and what happens without it?
- KVO vs Combine vs the Observation framework?
- What do you do with the observation token?
- Delegate vs KVO — when is each the right observer?
- Will KVO see a Swift `struct` property?
- How does Apple implement KVO under the hood (`isa` swizzle)?
- How do you fire KVO for a change that did not go through the setter?

</details>

### Senior

<h2 id="clean-architecture">Clean Architecture</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Clean Architecture (and VIPER / “use case” variants) puts **entities and use cases** in the middle, then adapters (presenters, gateways), then frameworks (UIKit, URLSession, Core Data) on the outside. Dependencies point **inward**: a use case does not import SwiftUI. Versus MVVM: MVVM is a screen pattern; Clean is a dependency rule for the whole app. You reach for it when the same business rules must survive a UI rewrite or a second client. The cost is types: `LoginUseCase`, `LoginRepository`, three protocols for one button. Typical miss: folders named Domain / Data / Presentation that still import UIKit in the “domain.”



```swift
protocol AuthGateway {
    func login(name: String, password: String) async throws -> User
}

struct LoginUseCase {
    let auth: AuthGateway
    func run(name: String, password: String) async throws -> User {
        try await auth.login(name: name, password: password)
    }
}
```


**Then they usually ask**

- Clean vs MVVM — can you use both?
- What is a use case vs a ViewModel method?
- When is this overkill for a three-screen app?
- Why must a `URLError` never reach the ViewModel unchanged?

</details>

<h2 id="mvvm-c">MVVM-C</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

MVVM-C is MVVM plus a **Coordinator** (or router) that owns navigation. The view model says “login succeeded”; the coordinator pushes the next screen. That keeps UIKit / `NavigationPath` out of the view model so you can test flow without a window. Cost: another type per module and a debate about who holds the `UINavigationController`. Typical miss: a coordinator that still builds views *and* calls the API.



```swift
protocol Coordinating: AnyObject { func loginDidSucceed() }

final class LoginViewModel {
    weak var coordinator: Coordinating?
    func submit() { coordinator?.loginDidSucceed() }
}
```


**Then they usually ask**

- Coordinator vs the view model owning `NavigationPath`?
- How do you test a coordinator?
- When is plain MVVM enough?
- Can you use a coordinator without calling the pattern “MVVM-C”?

</details>

<h2 id="viper">VIPER</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

VIPER splits a screen into **View, Interactor, Presenter, Entity, Router**. The view is dumb. The presenter formats and reacts to taps. The interactor runs use cases and talks to services. The router owns navigation. Entities are the models. Versus MVVM: more types, clearer navigation, heavier for a single form. Use it when a module is large and several people own slices. Typical miss: a presenter that still imports UIKit, or five empty files for a settings toggle.



```swift
protocol LoginViewing: AnyObject { func show(error: String) }
protocol LoginRouting: AnyObject { func finish() }

final class LoginPresenter {
    weak var view: LoginViewing?
    var router: LoginRouting?
    func submit() { /* interactor, then view or router */ }
}
```


**Then they usually ask**

- VIPER vs Clean vs MVVM — which problem does each extra type solve?
- Where does a network client live?
- When is this overkill?
- What is the VIPER failure mode on a one-person team?

</details>

<h2 id="kmp">Kotlin Multiplatform from iOS</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

KMP shares **Kotlin** business logic (network models, validation, a store) compiled to a framework the iOS app links. UI stays SwiftUI / UIKit. The interview is the **boundary**: `expect`/`actual` for platform APIs, what types cross (primitives and Kotlin-exported classes, not Swift structs), and who owns concurrency (Kotlin coroutines vs Swift `async` — you usually wrap). Do not share views. Typical miss: treating KMP as “write the app once,” or passing a Swift class into Kotlin and wondering why the compiler refuses.



```text
shared/ (Kotlin) → XCFramework
iosApp/ imports Shared, maps SharedUser → Swift User in one adapter
```


**Then they usually ask**

- What cannot cross the Kotlin/Swift boundary cleanly?
- Who cancels an in-flight Ktor call when the SwiftUI view disappears?
- When is a shared module the wrong cut (UI, Keychain, WidgetKit)?

</details>

<h2 id="modular-architecture">Modular architecture</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Modular means **physical** boundaries: local Swift packages (or targets) so Feature A cannot import Feature B’s internals. Shared contracts live in a thin module; implementations stay `internal`. The app target is the composition root. This is how multiple teams ship without a single `User.swift` that grows fifty optionals. SPM refuses circular dependencies — the fix is a third module of protocols, not “just import each other.” Typical miss: a `Core` package that imports everything, or making every type `public` “for tests.”



```swift
// AppContracts
public protocol CurrentUserProviding {
    var userId: String { get }
}

// CheckoutFeature depends on AppContracts, never on ProfileFeature
public struct CheckoutFactory {
    public static func make(user: CurrentUserProviding) -> some View {
        CheckoutView(userId: user.userId)
    }
}
```


**Then they usually ask**

- How do you break a cycle between Checkout and Profile?
- What belongs in `AppContracts` vs a CoreUI package?
- Strangler Fig — how do you migrate UIKit → SwiftUI one screen at a time?
- 200+ SPM modules — what blows compile time first?

</details>

<h2 id="optimistic-updates">Optimistic updates</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Optimistic UI applies the change **before** the server confirms, then rolls back if the request fails. The user sees a like, a send, or a rename instantly. You keep a snapshot of the previous state (or an inverse operation) and a stable id so a late 409 / 500 can undo without clobbering a newer local edit. Conflict policy is the interview: last-write-wins, version tokens, or “ask the user.” Typical miss: mutating the only copy of the model and having nothing to restore, or showing success chrome before you even enqueued the request.



```swift
func toggleLike(_ post: Post) async {
    let before = post.isLiked
    store.setLiked(post.id, !before)          // immediate
    do {
        try await api.setLiked(post.id, !before)
    } catch {
        store.setLiked(post.id, before)       // rollback
    }
}
```


**Then they usually ask**

- How do you reconcile two optimistic likes if the user taps twice?
- What do you persist if the app is killed mid-flight?
- When is pessimistic (wait for 200) the better default?

</details>

<h2 id="tca">TCA</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The Composable Architecture (Point-Free) is a **unidirectional** loop: `State`, `Action`, `Reducer`, `Store`, and `Effect` for I/O. Every change is an action; effects are values you can fail in tests. It scales a feature tree and makes time-travel / exhaustive tests cheap. Cost: boilerplate and a learning curve; a three-screen app rarely needs it. Typical miss: calling it “just Redux” and skipping effects.



```swift
struct Counter: Equatable { var count = 0 }
enum CounterAction { case increment }
// reducer: (inout State, Action) -> Effect<Action>
```


**Then they usually ask**

- TCA vs MVVM — what problem does the reducer solve?
- Where do network calls live (`Effect`)?
- When is this overkill next to `@Observable`?

</details>

<h2 id="phantom-types">Phantom types</h2>

<code>Senior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A phantom type is a generic parameter you never store. It exists so the compiler can tell two otherwise identical values apart. `ID<User>` and `ID<Order>` can both wrap a `String`, but you cannot pass one where the other is required. You can also encode a workflow: `Request<Unsigned>` versus `Request<Signed>`, and `send` only accepts the signed one. There is no extra runtime state. I use it when a mix-up is a real bug — IDs, units, validation — not as decoration on every model.



```swift
struct ID<Entity>: Hashable {
    let raw: String
}

enum UserTag {}
enum OrderTag {}

func loadUser(_ id: ID<UserTag>) {}

let user = ID<UserTag>(raw: "u1")
loadUser(user)
// loadUser(ID<OrderTag>(raw: "o1")) // does not compile
```


**Then they usually ask**

- Phantom type vs a wrapper struct with a distinct name?
- How would you model `Draft` vs `Paid` so `submit` cannot take a draft?
- Any runtime cost, and does `Entity` need instances?
- When is this overkill compared with `UUID` plus a comment?

</details>
