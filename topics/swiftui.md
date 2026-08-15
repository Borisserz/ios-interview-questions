# SwiftUI

- [SwiftUI vs UIKit](#swiftui-vs-uikit)
- [SwiftUI environment](#environment)
- [@Published](#published)
- [@State](#state)
- [View initializer vs onAppear](#init-vs-onappear)
- [@StateObject vs @ObservedObject](#stateobject-vs-observedobject)
- [Environment object vs observed object](#environmentobject-vs-observedobject)
- [How an observable object announces changes](#observable-object-changes)
- [Programmatic navigation](#programmatic-navigation)
- [ButtonStyle](#button-style)
- [GeometryReader](#geometry-reader)
- [Why SwiftUI views are structs](#views-are-structs)
- [MVVM in SwiftUI](#swiftui-mvvm)
- [MV vs MVVM in SwiftUI](#swiftui-mv)
- [ObservableObject vs @Observable](#observableobject-vs-observable)
- [Choosing SwiftUI property wrappers](#swiftui-property-wrappers)
- [SwiftUI view lifecycle](#swiftui-lifecycle)
- [@Binding](#binding)
- [@AppStorage](#appstorage)
- [UIKit in SwiftUI](#uikit-representable)
- [LazyVGrid](#lazyvgrid)
- [ViewModifier](#view-modifier)
- [PreferenceKey](#preference-key)
- [AnyView](#anyview)
- [LazyVStack vs VStack](#lazyvstack-vs-vstack)
- [matchedGeometryEffect](#matched-geometry)
- [EquatableView](#equatable-view)
- [When SwiftUI re-renders a view](#swiftui-rerender)
- [AttributeGraph](#attribute-graph)
- [View identity vs a ViewBuilder property](#view-identity)

## SwiftUI vs UIKit {#swiftui-vs-uikit}

- Level: Mid
- Frequency: High

### Answer

**UIKit** is imperative: you own a view graph, mutate it, and push view controllers. **SwiftUI** is declarative: you return a `View` that is a function of state, and the framework diffs that description and updates the pixels. SwiftUI wins for new screens, previews, and anything that is mostly layout plus bindings. UIKit still owns years of APIs — rich text editing, some collection-view layouts, fine-grained animation, and anything your deployment target cannot express in SwiftUI. The bridge is `UIViewRepresentable` / `UIViewControllerRepresentable` one way and `UIHostingController` the other. Interviewers want coexistence, not a winner: a UIKit app can host SwiftUI features, and a SwiftUI app will still drop to UIKit for the sharp edges. Typical mistake: rewriting a stable UIKit flow “because SwiftUI” without a product reason.

### Example

```swift
struct RatingBadge: UIViewRepresentable {
    var value: Int

    func makeUIView(context: Context) -> UILabel {
        let label = UILabel()
        label.font = .preferredFont(forTextStyle: .caption1)
        return label
    }

    func updateUIView(_ label: UILabel, context: Context) {
        label.text = "★ \(value)"
    }
}
```

### Follow-ups

- When do you pick `UIViewRepresentable` versus rewriting the control?
- How does `UIHostingController` change a UIKit navigation stack?
- What SwiftUI features still require a minimum iOS version that UIKit already had?

## SwiftUI environment {#environment}

- Level: Mid
- Frequency: High

### Answer

The **environment** is a downward-only bag of values SwiftUI passes through the view tree. Built-in keys include `colorScheme`, `dynamicTypeSize`, `locale`, and `dismiss`. You read them with `@Environment(\.key)` and write them with `.environment(\.key, value)` or a dedicated modifier such as `.preferredColorScheme`. Custom values need an `EnvironmentKey` and an `EnvironmentValues` property. **`@EnvironmentObject`** is a different slot: it injects a shared `ObservableObject` by type, not a small value. Children see what the nearest ancestor set; nothing walks upward. Typical mistakes: using `@EnvironmentObject` for a single boolean, forgetting `.environmentObject` at the root and crashing at runtime, and expecting a change at a leaf to update the parent.

### Example

```swift
private struct CardRadiusKey: EnvironmentKey {
    static let defaultValue: CGFloat = 12
}

extension EnvironmentValues {
    var cardRadius: CGFloat {
        get { self[CardRadiusKey.self] }
        set { self[CardRadiusKey.self] = newValue }
    }
}

struct Card: View {
    @Environment(\.cardRadius) private var radius
    var body: some View { RoundedRectangle(cornerRadius: radius) }
}
```

### Follow-ups

- How is `@Environment` different from `@EnvironmentObject`?
- What happens if a child never receives an `environmentObject`?
- When would you use `EnvironmentKey` instead of passing an argument?
- Why does reading *any* `@Environment` key make you depend on the whole `EnvironmentValues` bag?

## @Published {#published}

- Level: Mid
- Frequency: High

### Answer

**`@Published`** is a Combine property wrapper for a class that conforms to `ObservableObject`. On `willSet` it sends through the object’s `objectWillChange` publisher, which is what SwiftUI subscribes to. It does not work on a struct, and it does not by itself make a view update — the view must hold the object in `@StateObject`, `@ObservedObject`, or `@EnvironmentObject`. Assigning a new value to a `@Published` property is enough; mutating a reference *inside* that value (for example appending to a class stored in the property) will not fire unless you assign a new wrapper value or send `objectWillChange` yourself. The Observation framework (`@Observable`, iOS 17) tracks property access and makes `@Published` unnecessary on new types. Typical mistake: putting `@Published` on a SwiftUI `View`.

### Example

```swift
final class SearchModel: ObservableObject {
    @Published var query = ""
    @Published private(set) var results: [String] = []

    func run() {
        results = query.isEmpty ? [] : ["\(query) — 1"]
    }
}
```

### Follow-ups

- Why does mutating an array *inside* a published class not refresh the UI?
- How does `@Published` relate to `objectWillChange`?
- What replaces this on an `@Observable` type?

## @State {#state}

- Level: Junior
- Frequency: High

### Answer

**`@State`** is storage SwiftUI *owns for this view*. You declare a private value; the wrapper keeps it alive across the many times the `View` struct is recreated, and assigning it invalidates `body`. Use it for local UI: a toggle, a selected tab, a text field’s draft. Pass a binding down with `$property` when a child must write. Do not put a long-lived reference type in `@State` on older OS versions (that is what `@StateObject` is for); on iOS 17+ `@State` with an `@Observable` class is the new ownership path. Typical mistakes: marking `@State` `public` and letting a parent write the wrapper, initializing `@State` from an incoming `let` every time (the initial value is only used once), and using `@State` for data the server owns.

### Example

```swift
struct Counter: View {
    @State private var count = 0

    var body: some View {
        Button("Taps: \(count)") { count += 1 }
    }
}
```

### Follow-ups

- Why is `@State` usually `private`?
- What is the difference between `count` and `$count`?
- Why does changing an `@State` initial value in the parent not reset the child?

## View initializer vs onAppear {#init-vs-onappear}

- Level: Mid
- Frequency: High

### Answer

A SwiftUI `View` **initializer runs whenever the struct is constructed**, which is often: parent `body` re-evaluates, a `ForEach` rebuilds, a modifier changes identity. It must be cheap and side-effect free — store properties, derive a value, do not hit the network. **`onAppear`** runs when the view is inserted into the rendered hierarchy (and `onDisappear` when it leaves). That is the right place for analytics, focus, or kicking off work, with the caveat that navigation and tabs can call it more than once. For async work that should cancel when the view goes away, `.task` is the better hook. A bare `Task { }` inside `onAppear` (or `body`) is unstructured: it inherits the main actor but **does not cancel** when the view leaves unless you store the handle. Typical mistakes: fetching in `init` (duplicate requests, no cancellation), treating `onAppear` as `viewDidLoad`, and starting `Task { }` in a row that scrolls away.

### Example

```swift
struct ProfileView: View {
    let userID: String
    @State private var name = ""

    init(userID: String) {
        self.userID = userID
    }

    var body: some View {
        Text(name)
            .task(id: userID) {
                name = await UserAPI.name(for: userID)
            }
    }
}
```

### Follow-ups

- Why can `init` run many times for one screen the user still sees?
- When do you prefer `.task` over `onAppear`?
- `.task` vs `onAppear` vs `Task { }` — which one cancels on disappear?
- What does `onAppear` do inside a `List` that recycles rows?

## @StateObject vs @ObservedObject {#stateobject-vs-observedobject}

- Level: Mid
- Frequency: High

### Answer

Both wrappers subscribe to an `ObservableObject`. **`@StateObject`** *owns* the instance: SwiftUI creates it once (the first time the view’s identity appears) and keeps it when `body` is recreated. **`@ObservedObject`** does *not* own it; it watches an object someone else holds. The classic bug is `@ObservedObject var model = Model()` inside the view — a parent refresh constructs a new `Model` and you lose state. Own it with `@StateObject` at the creator, then pass the same instance down as `@ObservedObject` (or `@EnvironmentObject`). On iOS 17+, `@State` + `@Observable` replaces a lot of this pair, but interviews still ask the ownership rule. Typical mistake: using `@StateObject` in a view that is not the owner, so you accidentally fork a second source of truth.

### Example

```swift
final class Cart: ObservableObject {
    @Published var count = 0
}

struct ShopView: View {
    @StateObject private var cart = Cart()
    var body: some View { CartButton(cart: cart) }
}

struct CartButton: View {
    @ObservedObject var cart: Cart
    var body: some View { Text("\(cart.count)") }
}
```

### Follow-ups

- What goes wrong with `@ObservedObject var model = Model()`?
- When is `@EnvironmentObject` a better pass-down than `@ObservedObject`?
- How does `@Bindable` change this on `@Observable` types?

## Environment object vs observed object {#environmentobject-vs-observedobject}

- Level: Mid
- Frequency: High

### Answer

Both subscribe to an `ObservableObject`. **`@ObservedObject`** is an explicit dependency: the parent passes the instance in. **`@EnvironmentObject`** is implicit: you inject once with `.environmentObject(_:)` and any descendant can read it by type. Use `@ObservedObject` when the relationship is local and you want the data flow visible in the initializer. Use `@EnvironmentObject` when many unrelated screens need the same object (session, theme store, cart) and threading it through every init would be noise. The cost of environment is opacity — a missing `.environmentObject` crashes at runtime, and two objects of the same type cannot share the tree without wrapping. Ownership still lives wherever you created the object, usually `@StateObject` at the root. Typical mistake: putting a screen-specific model in the environment so a later push silently overwrites it.

### Example

```swift
final class Session: ObservableObject {
    @Published var user: String?
}

struct RootView: View {
    @StateObject private var session = Session()
    var body: some View {
        ContentView()
            .environmentObject(session)
    }
}

struct ProfileBadge: View {
    @EnvironmentObject private var session: Session
    var body: some View { Text(session.user ?? "Guest") }
}
```

### Follow-ups

- Why does a missing `environmentObject` crash instead of being optional?
- When is passing `@ObservedObject` clearer than the environment?
- How does `@Environment(Session.self)` change this with `@Observable`?

## How an observable object announces changes {#observable-object-changes}

- Level: Mid
- Frequency: High

### Answer

`ObservableObject` exposes **`objectWillChange`**, a `ObservableObjectPublisher` that fires *before* the UI should refresh. `@Published` properties send on that publisher automatically in `willSet`. You can also call `objectWillChange.send()` yourself when a change is not a stored-property assignment — a computed value backed by a file, a callback from `URLSession`, a mutation inside a nested class. SwiftUI listens, invalidates the views that hold the object, and re-invokes `body`. Combine subscribers can listen too. Timing matters: it is *will* change, so reads during the same turn may still see the old value; that is why SwiftUI schedules the render for later. Typical mistake: sending `objectWillChange` after you mutate, or never sending it when you bypass `@Published`.

### Example

```swift
final class Clock: ObservableObject {
    private(set) var ticks = 0
    private var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            guard let self else { return }
            self.objectWillChange.send()
            self.ticks += 1
        }
    }
}
```

### Follow-ups

- Why is the publisher `willChange` rather than `didChange`?
- When must you call `send()` yourself?
- How does the `@Observable` macro announce a change instead?

## Programmatic navigation {#programmatic-navigation}

- Level: Mid
- Frequency: High

### Answer

Programmatic navigation means the *source of truth* is data, not a tap on a `NavigationLink`. On iOS 16+ that data is a **`NavigationStack` path**: `NavigationPath` or a typed `[Route]` binding. You `append` to push, `removeLast` to pop, and register destinations with `navigationDestination(for:)`. A link can still write into the same path. The older `NavigationLink(isActive:)` and `NavigationView` selection bindings work but are deprecated and easy to desync. Sheets and full-screen covers use a different binding (`item:` / `isPresented:`), not the stack path. Typical mistakes: pushing by constructing a link you never show, and storing the path only in a child so the back button and the model disagree.

### Example

```swift
enum Route: Hashable { case detail(id: String) }

struct Inbox: View {
    @State private var path = [Route]()

    var body: some View {
        NavigationStack(path: $path) {
            Button("Open") { path.append(.detail(id: "42")) }
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .detail(let id): Text(id)
                    }
                }
        }
    }
}
```

### Follow-ups

- How do you pop to root with a `NavigationPath`?
- When do you use `sheet(item:)` instead of pushing?
- What broke about `NavigationLink(isActive:)` in a `List`?
- Why did `NavigationStack` replace `NavigationView`?
- How do you pop several levels (or to root) in one shot?

## ButtonStyle {#button-style}

- Level: Junior
- Frequency: Medium

### Answer

**`ButtonStyle`** is a protocol that redraws a button’s label without replacing the tap behavior. You implement `makeBody(configuration:)` and read `configuration.label` plus `configuration.isPressed`. Apply it with `.buttonStyle(MyStyle())` or a static member. System styles (`.bordered`, `.borderedProminent`, `.plain`) are also `ButtonStyle`s. **`PrimitiveButtonStyle`** is the lower hook if you need to own the gesture yourself (for example a custom toggle-button). Styles do not change accessibility activation; they change chrome. Typical mistakes: wrapping a `Button` in a `onTapGesture` instead of a style, and forgetting `isPressed` so the control never looks down.

### Example

```swift
struct ScaleStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .opacity(configuration.isPressed ? 0.6 : 1)
            .scaleEffect(configuration.isPressed ? 0.96 : 1)
    }
}

Button("Save") { save() }
    .buttonStyle(ScaleStyle())
```

### Follow-ups

- How is `PrimitiveButtonStyle` different from `ButtonStyle`?
- How do you make a style the default for a whole subtree?
- Why not put an `onTapGesture` on top of a `Button`?

## GeometryReader {#geometry-reader}

- Level: Mid
- Frequency: High

### Answer

**`GeometryReader`** is a view that proposes *all remaining space* to itself, then calls your closure with a `GeometryProxy` (`size`, `safeAreaInsets`, `frame(in:)`). That expansion is the trap: wrapping a label in a reader to measure it often stretches the label’s parent to fill the screen. Measure in the background or overlay so the reader takes the child’s size, or use `Layout` / `containerRelativeFrame` on newer OS versions. Proxy frames need a coordinate space (`global`, `local`, or a named space) or the numbers will not match the view you think. Typical mistakes: using a reader as the root of every screen, and reading `proxy.size` during the first pass when it is still zero.

### Example

```swift
struct MeasuredBar: View {
    @State private var width = 0.0

    var body: some View {
        Capsule()
            .frame(height: 6)
            .background(
                GeometryReader { proxy in
                    Color.clear.preference(key: WidthKey.self, value: proxy.size.width)
                }
            )
            .onPreferenceChange(WidthKey.self) { width = $0 }
    }
}

private struct WidthKey: PreferenceKey {
    static var defaultValue = 0.0
    static func reduce(value: inout Double, nextValue: () -> Double) { value = nextValue() }
}
```

### Follow-ups

- Why does a `GeometryReader` in a `HStack` blow out the layout?
- How do you measure a view without changing its size?
- When would you use `Layout` instead?
- How does a `PreferenceKey` get a measured size back to the parent?

## Why SwiftUI views are structs {#views-are-structs}

- Level: Mid
- Frequency: High

### Answer

SwiftUI views are **values**. A struct is cheap to create, has no inherited stored state, and can be copied as the tree is diffed. `body` is a computed property: SwiftUI throws the struct away and makes a new one whenever `@State`, an observable dependency, or the parent’s output changes. Identity is *not* the struct’s memory address — it is structural position plus any explicit `.id`. If views were classes, you would fight reference semantics (shared mutation, identity that outlives the description) and the “UI is a function of state” model would leak. The cost you accept is that `init` is not a lifetime hook and stored properties that are not wrappers do not survive a refresh. Typical mistake: putting a side-effecting class into a view property without `@StateObject` / `@State` and wondering why it resets.

### Example

```swift
struct PriceLabel: View {
    let cents: Int
    // Recreated freely. Only @State / @Binding / @StateObject survive.

    var body: some View {
        Text(cents, format: .currency(code: "USD").precision(.fractionLength(2)))
    }
}
```

### Follow-ups

- How does SwiftUI decide two view values are “the same” view?
- Why is `body` a computed property rather than a stored tree?
- What would break if `View` were a class?

## MVVM in SwiftUI {#swiftui-mvvm}

- Level: Mid
- Frequency: High

### Answer

The view is a struct that renders state. The **view model** owns rules, loading, and mapping — not `View` types. In the Combine era that object is an `ObservableObject` you own with `@StateObject` and pass down. On iOS 17+ it can be an `@Observable` class stored in `@State`. Either way: the view does not call the API service directly, the view model is testable without a window, and dependencies come in through `init` (or a small factory), not a singleton hidden in `body`. Keep navigation and sheet flags in the view model if they are part of the flow; keep purely visual state (`isPressed`) in `@State` on the view. Typical mistake: a 400-line `ObservableObject` that is just a second view.

### Example

```swift
@Observable
final class ProfileModel {
    private let api: API
    var name = ""
    var isLoading = false

    init(api: API) { self.api = api }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        name = (try? await api.profile())?.name ?? ""
    }
}

struct ProfileView: View {
    @State private var model: ProfileModel
    var body: some View {
        Text(model.name)
            .task { await model.load() }
    }
}
```

### Follow-ups

- Where does a `NavigationPath` live — view or view model?
- How do you unit-test `ProfileModel` without SwiftUI?
- When is MVVM overkill for a static screen?
- How is that different from the MV pattern Apple’s samples use?

## ObservableObject vs @Observable {#observableobject-vs-observable}

- Level: Mid
- Frequency: High

### Answer

`ObservableObject` + `@Published` is Combine: any published write sends `objectWillChange`, and SwiftUI invalidates every view that holds the object. `@Observable` (Observation, iOS 17+) tracks **which properties `body` read** and invalidates only those dependents. Less boilerplate: no `ObservableObject`, no `@Published`, no `@StateObject` — you store the instance in `@State` or pass it, and use `@Bindable` for bindings. Migration is not free: older APIs (`@EnvironmentObject`, some libraries) still expect `ObservableObject`. Typical mistake: wrapping `@Observable` in `@StateObject`, or expecting `@Published` to work on an `@Observable` class.

### Example

```swift
@Observable
final class Cart {
    var count = 0
}

struct Badge: View {
    let cart: Cart
    var body: some View { Text("\(cart.count)") } // tracks `count` only
}
```

### Follow-ups

- Why can `@Observable` skip a refresh that `ObservableObject` would do?
- How do you observe an `@Observable` type from UIKit?
- What does `@Bindable` replace?

## Choosing SwiftUI property wrappers {#swiftui-property-wrappers}

- Level: Mid
- Frequency: High

### Answer

Decide **who owns the source of truth**. `@State` — this view owns a value (or, on iOS 17+, an `@Observable` instance). `@StateObject` — this view owns an `ObservableObject`. `@ObservedObject` — someone else owns it; you just subscribe. `@EnvironmentObject` / `@Environment` — injected from an ancestor, not passed through every init. `@Binding` — a write-back into whoever owns it. Do not initialize `@ObservedObject var model = Model()` in the view. Do not put a screen-specific model in the environment. Interviews want this map, not a recitation of property-wrapper syntax.

### Example

```swift
struct Parent: View {
    @StateObject private var session = Session()
    @State private var query = ""

    var body: some View {
        SearchField(text: $query)
            .environmentObject(session)
    }
}

struct SearchField: View {
    @Binding var text: String
    var body: some View { TextField("Search", text: $text) }
}
```

### Follow-ups

- Why is `@StateObject` the owner and `@ObservedObject` the borrower?
- When do you pick `@Environment` over `@EnvironmentObject`?
- How does the map change with `@Observable` and `@Bindable`?

## SwiftUI view lifecycle {#swiftui-lifecycle}

- Level: Mid
- Frequency: High

### Answer

A SwiftUI view has **two clocks**. Identity in the tree — that is how long `@State` / `@StateObject` live. Visibility — `onAppear`, `onDisappear`, `.task`. A `TabView` child can keep its state while `onAppear` fires every time you come back to the tab. `body` can run many times before the first `onAppear`. Init of a child runs when the parent’s `body` runs, which is why `@StateObject` (or `@State` + `@Observable`) must own the model, not `init`. Load-once work needs a flag or `.task(id:)` keyed to data, not “I assumed `onAppear` is `viewDidLoad`.” Typical mistake: starting a network call in `onAppear` of a `List` row that appears and disappears as you scroll.

### Example

```swift
struct FeedView: View {
    @State private var items: [Item] = []

    var body: some View {
        List(items) { Text($0.title) }
            .task {
                guard items.isEmpty else { return }
                items = (try? await API.feed()) ?? []
            }
    }
}
```

### Follow-ups

- Why can `init` run more often than `onAppear`?
- `.task` vs `onAppear` — which one cancels when the view leaves?
- How does `id:` on `.task` change refetch behavior?
- What is view identity, and when does `@State` reset?
- `.refreshable` vs `.task` for a pull-to-refresh list?

## @Binding {#binding}

- Level: Junior
- Frequency: High

### Answer

`@Binding` is a **read-write window** into someone else’s state. The parent owns `@State` / `@Bindable`; the child gets `$value`. Mutating the binding writes through. A custom `init` takes `Binding<T>` (`init(text: Binding<String>)`). Typical miss: `@Binding` on the owner, or copying the value into `@State` in the child so the parent never updates.

### Example

```swift
struct Editor: View {
    @Binding var text: String
    var body: some View { TextField("Name", text: $text) }
}

struct Parent: View {
    @State private var name = ""
    var body: some View { Editor(text: $name) }
}
```

### Follow-ups

- `@Binding` vs `@Bindable` on an `@Observable`?
- How do you write a custom init that takes a binding?
- When is a callback clearer than a binding?

## @AppStorage {#appstorage}

- Level: Junior
- Frequency: Medium

### Answer

`@AppStorage` is `UserDefaults` as a SwiftUI property wrapper. A write updates the view. Use it for a theme flag or last tab — not for tokens or a feed. You can point it at an App Group suite. Typical miss: storing a large `Codable` blob, or expecting it to sync across devices (that is iCloud KVS / CloudKit).

### Example

```swift
@AppStorage("usesGrid") private var usesGrid = false
```

### Follow-ups

- `@AppStorage` vs `@SceneStorage`?
- Why is this the wrong place for an auth token?
- How do you share it with a widget?

## UIKit in SwiftUI {#uikit-representable}

- Level: Mid
- Frequency: High

### Answer

`UIViewRepresentable` wraps a `UIView`; `UIViewControllerRepresentable` wraps a VC. You implement `makeUIView` / `updateUIView` (and a `Coordinator` for delegates). Use it for maps, a `WKWebView`, a battle-tested `UITextView`. Keep the surface small — do not wrap your whole app. Typical miss: doing layout in `updateUIView` every frame, or leaking the coordinator’s delegate.

### Example

```swift
struct Web: UIViewRepresentable {
    let url: URL
    func makeUIView(context: Context) -> WKWebView { WKWebView() }
    func updateUIView(_ view: WKWebView, context: Context) {
        view.load(URLRequest(url: url))
    }
}
```

### Follow-ups

- When do you need a `Coordinator`?
- `updateUIView` vs recreate the view?
- How do you push a UIKit VC from SwiftUI without wrapping it?

## LazyVGrid {#lazyvgrid}

- Level: Mid
- Frequency: Medium

### Answer

`LazyVGrid` lays items in columns and **creates views as they appear**. Columns are `[GridItem]` — `.flexible()` shares space, `.adaptive(minimum:)` packs as many as fit, `.fixed` is a pixel width. Pair with `ForEach` and stable `id`s. A `LazyHGrid` is the same idea sideways. This is not `UICollectionView` compositional layout: you do not get a full flow layout API, and off-screen cells are not a reuse queue you configure. Typical miss: a regular `VStack` of 200 images, or `.adaptive` with a huge minimum so you get one column and wonder why.

### Example

```swift
let columns = [GridItem(.adaptive(minimum: 120), spacing: 8)]

LazyVGrid(columns: columns, spacing: 8) {
    ForEach(photos) { photo in
        PhotoCell(photo)
    }
}
```

### Follow-ups

- `.flexible` vs `.adaptive` vs `.fixed`?
- When do you still want `UICollectionView`?
- How do you toggle list vs grid without resetting scroll?

## ViewModifier {#view-modifier}

- Level: Mid
- Frequency: Medium

### Answer

A `ViewModifier` is a reusable transform: `func body(content: Content) -> some View`. You apply it with `.modifier(CardStyle())` or a `View` extension that hides the type. Use it when the same padding + background + accessibility shows up on many screens. A plain function that returns `some View` is enough for a one-off. Typical miss: a modifier that captures `@State` it does not own, or wrapping every one-line `.font` in a type.

### Example

```swift
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func card() -> some View { modifier(CardStyle()) }
}
```

### Follow-ups

- Modifier vs a wrapper `View` vs a `View` extension?
- How do you pass a `Binding` into a modifier?
- Does a modifier change view identity?

## PreferenceKey {#preference-key}

- Level: Mid
- Frequency: High

### Answer

`Environment` flows data **down**. A `PreferenceKey` flows data **up**: a child writes a value, ancestors reduce siblings and read the result with `onPreferenceChange`. You use it to measure a child, align a underline with a tab, or collect frames for a custom scroll indicator. You must implement `defaultValue` and `reduce` — `reduce` is how two children in a stack become one number (usually `max` or `+`). Typical miss: setting a preference on every frame without reducing, or using `@Binding` up the tree and creating a cycle.

### Example

```swift
struct HeightKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = max(value, nextValue())
    }
}

Text("Hi")
    .background(GeometryReader { Color.clear.preference(key: HeightKey.self, value: $0.size.height) })
    .onPreferenceChange(HeightKey.self) { height = $0 }
```

### Follow-ups

- Why is `reduce` required if you only have one child?
- PreferenceKey vs `@Binding` to the parent — when is each honest?
- How do you measure without a `GeometryReader` stretching the layout?

## AnyView {#anyview}

- Level: Mid
- Frequency: Medium

### Answer

`AnyView` is type erasure for `View`. It lets you return different concrete views from one function, at the cost of **identity and specialization**: SwiftUI sees a box, so diffs get worse and `body` is harder to skip. Prefer `@ViewBuilder`, `Group`, or an enum of destinations so each branch stays a real type. Interviewers treat `AnyView` in a `List` row as a smell. Typical miss: wrapping every cell “to make the compiler happy” and then wondering why scrolling janks.

### Example

```swift
@ViewBuilder
func badge(isOn: Bool) -> some View {
    if isOn { Image(systemName: "star.fill") }
    else { EmptyView() }
}
// Avoid: AnyView(isOn ? AnyView(Image(...)) : AnyView(EmptyView()))
```

### Follow-ups

- When is `AnyView` still the honest tool?
- How does this relate to `some View` vs `any View`?
- What happens to view identity when the boxed type changes?
- Cross-module protocol that returns `some View` vs `AnyView` — which hides the type without the box?

## LazyVStack vs VStack {#lazyvstack-vs-vstack}

- Level: Mid
- Frequency: High

### Answer

`VStack` builds **every** child as soon as the stack is in the tree. `LazyVStack` (inside a `ScrollView`) builds children **as they approach the visible region**. Use lazy for a long feed; use a regular stack for a short form — lazy has a first-layout cost and can surprise you with `onAppear` / `@State` timing. `List` is its own lazy container with separators and reuse-like behavior; do not wrap a `List` in a `LazyVStack`. Typical miss: a `LazyVStack` of 10 rows “for performance,” or putting a lazy stack *outside* a scroll view so nothing is lazy.

### Example

```swift
ScrollView {
    LazyVStack(alignment: .leading, spacing: 12) {
        ForEach(items) { item in
            Row(item: item)
        }
    }
}
```

### Follow-ups

- `LazyVStack` vs `List` vs `LazyVGrid` — which one for a settings screen?
- Why can `@State` in a lazy row reset when you scroll away?
- Does lazy mean the network call in `onAppear` is safe?
- Changing a cell’s size in `onAppear` — what prefetch work did you throw away?

## matchedGeometryEffect {#matched-geometry}

- Level: Mid
- Frequency: Medium

### Answer

`matchedGeometryEffect` tells SwiftUI two views in different trees are **the same thing** for animation: a grid thumbnail and the hero on the detail screen share a namespace `id`. SwiftUI interpolates frame (and optionally other properties) across the transition. Both ends must be in the hierarchy during the animation, and the `id` must be unique in that `Namespace`. Typical miss: matching on a type that is recreated every frame, or expecting it to animate a navigation push without a shared namespace on both sides.

### Example

```swift
struct Gallery: View {
    @Namespace private var ns
    @State private var selected: Item?

    var body: some View {
        Thumb(item: item)
            .matchedGeometryEffect(id: item.id, in: ns)
            .onTapGesture { selected = item }
            .fullScreenCover(item: $selected) { item in
                Hero(item: item)
                    .matchedGeometryEffect(id: item.id, in: ns)
            }
    }
}
```

### Follow-ups

- What does `isSource:` change?
- Why does this fail across a `NavigationStack` push without a shared namespace?
- When is a custom `matchedTransitionSource` / zoom transition the newer API?

## EquatableView {#equatable-view}

- Level: Senior
- Frequency: Medium

### Answer

By default a child `body` can re-run when the parent re-runs, even if the child’s inputs did not change. If the view is `Equatable` and you wrap it with `.equatable()` (or `EquatableView`), SwiftUI calls `==` and **skips `body`** when equal. Write `==` on the data you actually draw — ignore a debug timestamp if the row does not show it. The `==` itself has a cost; it wins on expensive rows, not on a single `Text`. Typical miss: conforming to `Equatable` and forgetting `.equatable()`, or a custom `==` that lies and leaves the UI stale.

### Example

```swift
struct Row: View, Equatable {
    let title: String
    static func == (lhs: Row, rhs: Row) -> Bool { lhs.title == rhs.title }
    var body: some View { Text(title) }
}

Row(title: item.title).equatable()
```

### Follow-ups

- How is this different from `@Observable` skipping unread properties?
- When is the `==` overhead not worth it?
- Can you ignore a field on purpose in `==`?

## When SwiftUI re-renders a view {#swiftui-rerender}

- Level: Mid
- Frequency: High

### Answer

SwiftUI re-runs `body` when **something that `body` depends on changes**, not when “the screen updates.” Dependencies are: `@State` / `@Binding` you read, an `@Observable` property you actually touched, an `ObservableObject` that fired `objectWillChange`, `@Environment` values, and a parent that rebuilt you with new inputs. Identity matters: a new `.id` or a `ForEach` key change is a *new* view, so state resets. `@Observable` can skip a child that never read the dirty field; `ObservableObject` usually cannot. `EquatableView` is a manual skip when `==` says the inputs match. Typical miss: putting a `Date()` or a random UUID in `body` so every parent tick rebuilds the row, or blaming SwiftUI for work you started in `init`.

### Example

```swift
struct Row: View {
    let title: String
    var body: some View { Text(title) } // rebuilds if `title` changes, not if a sibling does
}
```

### Follow-ups

- Why does `@Observable` invalidate fewer views than `ObservableObject`?
- When does a parent rebuild force the child `body` anyway?
- `.id(uuid)` on a form field — what did you just reset?
- Environment value high in the tree — why does half the app re-run `body`?
- SwiftUI Instrument Cause & Effect vs `Self._printChanges` — which first?

## MV vs MVVM in SwiftUI {#swiftui-mv}

- Level: Mid
- Frequency: High

### Answer

**MV** (what Apple’s SwiftUI samples usually look like) is View + Model: `@Query` / `@State` / a small store, logic next to the data, no mandatory ViewModel type per screen. **MVVM** adds a dedicated observable object so the view stays dumb and rules are unit-testable. SwiftUI already *is* a state renderer — a ViewModel that only republishes `@Query` or wraps every tap is extra motion. Use MV for a screen whose state is the store. Use a ViewModel when you have mapping, orchestration, or a test you cannot write against a `View`. Typical miss: “SwiftUI requires MVVM” or a 400-line object that is just the view in a class.

### Example

```swift
// MV — view talks to the store
struct NotesView: View {
    @Query private var notes: [Note]
    var body: some View { List(notes) { Text($0.title) } }
}

// MVVM — pull this out when load/map/test need a type
@Observable
final class SearchModel {
    var query = ""
    func submit() async { /* debounce, cancel, map DTO */ }
}
```

### Follow-ups

- Where do you put a network call in MV without making the view a service locator?
- When does `@Query` in the view make the screen untestable?
- How do you migrate one screen from MV to a ViewModel without rewriting the app?
- Does the SwiftUI team prescribe MVC / MVVM / VIPER?

## AttributeGraph {#attribute-graph}

- Level: Senior
- Frequency: High

### Answer

SwiftUI does not keep your `View` structs alive. It keeps an **AttributeGraph**: nodes are attributes (a `body`, a `@State` box, a parent input), edges are **dependencies**. The struct you write is a value that gets copied into those attributes; **identity stays on the attribute**, not on the temporary struct. When state changes, SwiftUI marks dependent attributes outdated and, on the next frame, re-runs only those `body`s. The graph’s output is a **DisplayList** (what to draw) — you do not build that list yourself. The SwiftUI Instrument’s **Cause & Effect** graph is this dependency chain made visible. Typical miss: “SwiftUI diffs the view tree like UIKit diffs cells,” or doing formatter / decode work inside `body` because you thought the struct was cheap forever.

### Example

```text
Tap → @State attribute dirty → body attribute outdated → new Text value
     → styling attributes → DisplayList → pixels
Cause & Effect: gesture → State → YourView.body (count of updates on the edge)
```

### Follow-ups

- Attribute identity vs the `View` value — which one owns `@State`?
- Why is a long `body` a hitch even if the graph skipped other views?
- `SWIFTUI_PRINT_TREE` / DisplayList — interview toy or production tool?

## View identity vs a ViewBuilder property {#view-identity}

- Level: Senior
- Frequency: High

### Answer

A **separate `View` struct** is its own graph node: its own identity, its own dependency set, it can skip when the parent runs. A `@ViewBuilder` **computed property** is inlined into the parent — it re-evaluates whenever the parent does. Extract a type when that subsection has state or should update alone. Identity also comes from `ForEach` IDs and `.id(...)`: change the id and SwiftUI treats it as a **new** view (state resets). Typical miss: a 200-line `body` of helper properties and wondering why one `@State` in the parent redraws everything.

### Example

```swift
struct Screen: View {
    var header: some View { Header() }          // inlined — runs with Screen
    var body: some View {
        VStack {
            header
            Detail()                            // own identity
        }
    }
}
```

### Follow-ups

- When is a computed `some View` still the right cut?
- `.id(UUID())` in `body` — what did you destroy?
- How does this relate to lazy stacks prefetching the *next* cell’s body?
