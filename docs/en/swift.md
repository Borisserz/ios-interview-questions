# Swift

95 cards · 51 often asked · source [swift.md](../../topics/swift.md)

### Junior

<h2 id="identity-vs-equality">== vs ===</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`==`** is `Equatable` — same *value*. **`===`** is identity — same *instance* (classes only). Two `UIView`s can be `==` if you defined that, and still `!==`. Two structs are never `===`; they have no identity. Typical miss: using `===` on a struct, or `==` on a class that only inherited `NSObject`’s pointer equality and thinking you compared fields.



```swift
class Box { var n: Int; init(_ n: Int) { self.n = n } }
let a = Box(1)
let b = a
let c = Box(1)
a === b   // true
a === c   // false
```


**Then they usually ask**

- Why does `NSObject`’s default `==` often match `===`?
- When do you write `==` on a class by hand?
- How does this show up in a unit test of a cache?

</details>

<h2 id="access-control">Access control</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift access is about **who can name the symbol**. Tightest to loosest: `private` (this declaration), `fileprivate` (this file), `internal` (this module, the default), `package` (this Swift package), `public` (importers can use it), `open` (importers can subclass / override — classes only). **`public` is visible across modules but not subclassable from outside**; `open` is. Apple uses that split on purpose — some `NSManagedObject` hooks are `public` so you can call them but not override them. Framework authors use `open` only when subclassing is the contract. App targets almost never need `open`. Typical miss: marking a type `public` but leaving its `init` `internal`, so clients cannot construct it.



```swift
public struct Token {
    public let raw: String
    public init(raw: String) { self.raw = raw }
}

open class Plugin {           // only if clients must subclass
    open func start() {}
}
```


**Then they usually ask**

- `public` vs `open` — when is `open` a mistake?
- `private` vs `fileprivate` after Swift 4 (same-file extensions)?
- Why does a `public` struct need an explicit `public init`?
- How do you expose a getter but keep the setter inside the type?
- Why would a framework author mark a method `public` instead of `open`?

</details>

<h2 id="any-vs-anyobject">Any vs AnyObject</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`Any` is every type: structs, enums, functions, classes. `AnyObject` is **class instances** only (the Swift name for `id`). You need `AnyObject` for `weak` / ObjC interop / “this must be a reference.” You need `Any` for a heterogeneous box (`[Any]`). Both erase information — you downcast to get work done. Typical miss: `[AnyObject]` for a list of structs, or using `Any` where a protocol would do.



```swift
let mixed: [Any] = [1, "a", { 0 }]
let objects: [AnyObject] = [UIView(), NSString(string: "x")]
```


**Then they usually ask**

- `any Protocol` vs `Any` vs `AnyObject`?
- Why is `weak var x: Any` illegal?
- When is a generic better than `Any`?

</details>

<h2 id="array-vs-set">Array vs set</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An **array** keeps order and allows duplicates. A **set** stores unique `Hashable` elements and answers `contains` in expected constant time. Reach for a set when the question is membership or uniqueness, not “the third item.” Interviewers often follow with “how do you unique an array and keep order” — `Set` alone will not do that. Typical mistakes: using an array and `contains` in a loop (quadratic), or assuming `Set` iteration is stable in a way you should depend on. If you need both fast lookup and a stable display order, keep the array and a set of seen keys.



```swift
let tags = ["ios", "swift", "ios"]
let unique = Set(tags)
unique.contains("swift")

func uniqued(_ values: [String]) -> [String] {
    var seen = Set<String>()
    return values.filter { seen.insert($0).inserted }
}
```


**Then they usually ask**

- Why does `Set` require `Hashable` when `Array` does not?
- How do you test that two sets are equal if order differs?
- When is an array still better even if values must be unique?
- Why is `NSSet` / `Set` a hash lookup and `NSArray` a scan?

</details>

<h2 id="classes-vs-structs">Classes vs structs</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Structs** are value types: assignment copies the value. **Classes** are reference types: assignment copies a pointer to the same instance. Default to a struct unless you need identity (`===`), inheritance, `deinit`, or Objective-C interop. Interviewers want that default plus a real reason to switch, not “classes are more object-oriented.”

A classic trap: two `Person` objects share one `Address` class. Change Brian’s street and Ray moves too — same instance. Fix it with a new `Address` or make `Address` a struct. Another trap: a `mutating` method on a struct is legal, but you cannot call it on a `let` instance. A `let` class can still mutate its properties. Common mistakes: saying structs always live on the stack (they do not), mutating a struct you passed into a function and expecting the caller to see it, or using a class just so two screens can share a bag of mutable state.



```swift
struct Size { var width: Int }
class Box { var size: Size }

var a = Size(width: 10)
var b = a
b.width = 20          // a.width is still 10

let box = Box(size: Size(width: 10))
let also = box
also.size.width = 20  // box.size.width is 20
```


**Then they usually ask**

- When is a class the better model even if you do not need inheritance?
- What does `mutating` mean on a struct method?
- How does copy-on-write change the “structs are copies” story for `Array`?
- Two models share an `Address` class — why does editing one move the other?

</details>

<h2 id="closures">Closures</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **closure** is a function without a name that can capture values from the scope where it was created. Trailing-closure syntax, `$0`, and `{ [weak self] in }` are the interview surface. Closures are **reference types** even when you store them in a struct — two copies of the struct can share the same closure heap object. That is why they participate in retain cycles when they capture `self` strongly and `self` stores the closure. Non-escaping closures (the default for function arguments) run before the callee returns; escaping ones can run later. You can often collapse `{ (a: String, b: String) -> Bool in return a < b }` down to `{ $0 < $1 }` or even `sort(by: <)`. Typical misses: capturing a huge value graph by accident, and using `unowned self` for a view controller that can dismiss first.



```swift
let add: (Int, Int) -> Int = { $0 + $1 }
let names = ["zoe", "ada"].sorted { $0 < $1 }

func makeCounter() -> () -> Int {
    var n = 0
    return { n += 1; return n }
}
```


**Then they usually ask**

- What does a capture list actually do?
- Why can a closure keep an object alive?
- When do you need `self.` inside a closure?
- Is a closure a value type or a reference type?
- What is trailing-closure syntax, and when do you still write the label?

</details>

<h2 id="dictionary-vs-array">Dictionary vs array</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An **array** is an ordered list you index with `Int`. A **dictionary** is a hash map: you look up a value by a `Hashable` key. Interviewers are checking whether you pick the collection for the access pattern, not by habit. Use an array when order and duplicates matter, or when you iterate everything. Use a dictionary when you keep asking “give me the thing with this id.” Typical miss: scanning an array of models with `first(where:)` in a hot path, or treating dictionary iteration as a positional index. Since Swift 4, dictionaries keep insertion order when you iterate, but you still do not subscript them with `0`.



```swift
struct User { let id: String; let name: String }

let users = [User(id: "1", name: "Ada"), User(id: "2", name: "Grace")]
let byID = Dictionary(uniqueKeysWithValues: users.map { ($0.id, $0) })
let ada = byID["1"]
```


**Then they usually ask**

- What happens if you build a dictionary and two keys collide?
- When would you keep both an array and a dictionary of the same data?
- Why must dictionary keys be `Hashable`?

</details>

<h2 id="enums">Enums</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A Swift enum is a value type that is one of a closed set of cases. Add a raw value (`String`, `Int`) when you persist or decode it. Add **associated values** when cases carry different payloads (`Result`, network errors). Enums can have methods, computed properties, and `switch` must be exhaustive — that is the interview win over a pile of booleans. Typical mistake: `isLoading` + `error` + `value` as three optionals instead of `enum State { idle, loading, failed(Error), ready(Value) }`.



```swift
enum LoadState<Value> {
    case idle
    case loading
    case failed(Error)
    case ready(Value)
}
```


**Then they usually ask**

- Raw value vs associated value — can a case have both?
- Why is an exhaustive `switch` safer than `if` on booleans?
- When do you still want a struct instead of an enum?
- What is an `indirect` enum, and why does a tree need it?

</details>

<h2 id="float-double-cgfloat">Float vs Double vs CGFloat</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`Double`** is a 64-bit IEEE float and Swift’s default for literals like `3.14`. **`Float`** is 32-bit — half the precision, smaller, and almost never what you want unless an API or a file format forces it. **`CGFloat`** is Core Graphics’ scalar: on modern 64-bit Apple platforms it is the same width as `Double`, but it is still a different type. Interviewers ask this because UIKit and Core Animation speak `CGFloat` and people slap `as` on numbers until it compiles. Do not mix them without an explicit conversion, and do not store model data as `CGFloat` just because a view used it.



```swift
import CoreGraphics

let temperature: Double = 36.6
let hairline: CGFloat = 1 / 3
let width = CGFloat(temperature) + hairline
let compact = Float(temperature)
```


**Then they usually ask**

- Why does `let x = 1.0` infer `Double` and not `CGFloat`?
- What breaks if you compare `Float` and `Double` values that “look” the same?
- When would you actually choose `Float` in an iOS app?

</details>

<h2 id="hashable-equatable">Hashable, Equatable, Comparable</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`Equatable`** is `==`. **`Hashable`** is `Equatable` plus a stable `hash(into:)` so the type can be a `Set` / `Dictionary` key. **`Comparable`** is `<` (and the rest) so you can sort. Synthesize them when all stored properties already conform — do not write a custom hash that ignores a field you use in `==`. Typical miss: mutating a property that participates in `==` after the value is in a set.



```swift
struct UserID: Hashable, Comparable {
    let raw: String
    static func < (l: Self, r: Self) -> Bool { l.raw < r.raw }
}
```


**Then they usually ask**

- Why must `==` and `hash` agree?
- When do you write `hash(into:)` by hand?
- `Comparable` vs a `sort` closure?
- Two values, same `hashValue`, different `==` — can both live in a `Set`?
- `Identifiable` vs `Hashable` — which one does `ForEach` actually need?

</details>

<h2 id="higher-order-functions">Higher-order functions</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A higher-order function takes or returns a function: `map`, `filter`, `compactMap`, `reduce`, `sorted`, `forEach`. You pass a closure instead of writing a loop. Prefer them when the transform is a one-liner; keep a `for` when you have early exits or multiple outputs. Typical miss: a `forEach` with side effects you then cannot test, or `reduce` that is just a worse `map`.



```swift
let raw = ["1", "3", "4", "6"]
let evenSum = raw.compactMap(Int.init).filter { $0.isMultiple(of: 2) }.reduce(0, +)
```


**Then they usually ask**

- `map` vs `compactMap` vs `flatMap`?
- When is a `for` loop clearer?
- What does `sorted(by:)` use under the hood (introsort-family, not Timsort)?
- `for` vs `forEach` — can you `return` / `break`?

</details>

<h2 id="identifiable">Identifiable</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`Identifiable` is a stable **`id`** so SwiftUI / diffable lists can tell rows apart. `ForEach(items)` wants `Identifiable` (or an explicit `id: \.key`). The `id` must not change when the row’s display text does — a UUID or a server primary key, not `name`. `Hashable` is for sets and dictionary keys; you can be `Identifiable` without being a good `Dictionary` key if `id` is the only identity. Typical miss: `ForEach(0..<count)` with a changing array, or `id: \.self` on a `String` that is not unique.



```swift
struct Team: Identifiable, Hashable {
    let id: UUID
    var name: String
}

ForEach(teams) { team in
    Text(team.name)
}
```


**Then they usually ask**

- Why is `id: \.name` a bug when two teams can share a name?
- `Identifiable` + `Hashable` — can `id` and `==` disagree?
- Diffable snapshot item IDs — same rule?

</details>

<h2 id="implicit-vs-explicit">Implicit vs explicit types</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Explicit** means you wrote the type (`var name: String = "a"`). **Implicit** means the compiler inferred it (`var name = "a"`). That is **type inference**: the compiler picks a concrete type from context. It is not dynamic typing — the type is fixed at compile time. Write the type when the right-hand side is ambiguous (`[]`, `nil`, a protocol existential) or when the name does not make the type obvious. Typical miss: `var x = 0` and later assigning a `Double`, or thinking inference is slower at runtime.



```swift
var name = "onthecodepath"           // inferred String
var port: Int = 443                  // explicit
var items: [User] = []               // explicit — [] alone is ambiguous
```


**Then they usually ask**

- When does inference fail (`nil`, empty array)?
- Is an inferred type any less safe than an annotated one?
- When do you annotate a closure’s parameter types?
- Type inference vs type safety — do they conflict?

</details>

<h2 id="nil-coalescing">Nil coalescing</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`??`** unwraps an optional or uses the value on the right. The right-hand side is only evaluated if the left is `nil`, so it is cheap to write `name ?? loadDefault()`. You can chain `a ?? b ?? c`. Interviewers want this instead of `if let` when you truly have a default. Hiding a programming error behind `"unknown"` or `0` is the usual smell — you wanted `guard` or `throw`. The right side must match the unwrapped type; `?? []` is the everyday “empty if missing” move.



```swift
let nickname: String? = nil
let display = nickname ?? "Guest"

let counts: [String: Int] = [:]
let taps = counts["home"] ?? 0
```


**Then they usually ask**

- Is the right-hand side of `??` always evaluated?
- How do you chain several optionals with defaults?
- When is `??` worse than `guard let`?

</details>

<h2 id="optional-chaining">Optional chaining</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`foo?.bar`** reaches into an optional and bails to `nil` if any step is `nil`. The whole expression becomes optional, even if `bar` was not. You can chain methods and subscripts: `user?.address?.street.prefix(1)`. Interviewers contrast this with force unwrap and with `if let` when you need a stable unwrap for several lines. A chain that ends in `Void` is `Void?`, which is why `foo?.doSideEffect()` is legal and easy to ignore. Do not hide a long chain of UI queries behind `?.` and then wonder why nothing happened.



```swift
class Node {
    var next: Node?
    var value = ""
}

let head = Node()
let deep = head.next?.next?.value   // String?
head.next?.value = "child"
```


**Then they usually ask**

- Why is the type of `foo?.count` optional even if `count` is `Int`?
- How does optional chaining interact with assignment?
- When should you stop chaining and bind with `guard let`?

</details>

<h2 id="property-observers">Property observers</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`willSet`** and **`didSet`** run around a stored property assignment. `willSet` sees `newValue` before the write; `didSet` sees `oldValue` after. They do not run when you set the property from the type’s own `init`, which surprises people who put logging there. They are for reacting to change — clamp, notify, sync a side table — not for computing a value; that is a computed property. Setting the same property again inside `didSet` can recurse, so you need a condition. Do not confuse observers with KVO; these are Swift-only and do not fire for wrapped `self.x` mutations the way people hope unless you actually assign the property.



```swift
var score = 0 {
    willSet { print("heading to \(newValue)") }
    didSet { print("was \(oldValue)") }
}

score = 10
```


**Then they usually ask**

- Why don’t observers fire in `init`?
- What happens if `didSet` assigns to the same property?
- How do observers behave on a property inside a struct you mutate through a `var`?

</details>

<h2 id="protocols">Protocols</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **protocol** is a contract: properties and methods a type promises to implement. You use it to talk to “anything that can persist” without naming the concrete class, which is how you test and how you keep UI away from URLSession. Conformance can be on the type or in an extension. Interviewers will push from “it’s like an interface” into existentials (`any`), associated types, and default implementations. The usual mistakes: protocols with twenty optional-ish methods that nobody implements correctly, and putting a protocol on a type just to inject something that should have been a function.



```swift
protocol Describable {
    var summary: String { get }
}

struct User: Describable {
    let name: String
    var summary: String { name }
}

func printSummary(_ item: any Describable) {
    print(item.summary)
}
```


**Then they usually ask**

- What is the difference between `any Describable` and `some Describable`?
- Can a protocol require an initializer?
- When do you use a protocol with an associated type instead of a generic function?

</details>

<h2 id="stored-vs-computed">Stored vs computed properties</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **stored** property occupies memory on the instance (`let` / `var` with no getter). A **computed** property is a getter (and optional setter) that derives a value each time. `willSet` / `didSet` attach only to stored properties. Computed properties can live on enums and in protocol extensions; stored ones cannot (except on classes/structs). Typical miss: a computed property that does I/O or allocates, so a loop that reads `view.frame` five times becomes five times the work — cache it if you need it twice.



```swift
struct Size {
    var width: Double
    var height: Double
    var area: Double { width * height }
}
```


**Then they usually ask**

- Can a computed property be `lazy`?
- Where do property observers fire relative to a custom setter?
- Why might you back a computed property with a private stored cache?

</details>

<h2 id="string-optional-vs-iuo">String? vs String!</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`String?`** is a real optional: you must unwrap it. **`String!`** is an implicitly unwrapped optional — still an optional at heart, but Swift unwraps it for you and crashes if it is `nil`. IUOs exist for two-phase setup: outlets, `awakeFromNib`, and some Objective-C imports. New Swift code should take `String?` or a non-optional once the value exists. Interviewers want “I do not use `!` to avoid typing `?`.” `IBOutlet var title: UILabel!` is historical; many teams now write `?` or load views in `init`.



```swift
var name: String? = "Ada"
var title: String! = "Engineer"

print(name?.count as Any)   // Optional(3)
print(title.count)          // 8 — traps if title is nil
title = nil
```


**Then they usually ask**

- Is `String!` a different type at runtime from `String?`?
- Why did UIKit outlets use `!` for so long?
- What happens if you pass a `String!` into a function that takes `String`?

</details>

<h2 id="collections">Swift collections</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`Array` is a **value type** with copy-on-write — assignment looks like a copy, the buffer is shared until mutation. It is an ordered random-access list — default choice, `O(1)` subscript. `Set` is unordered unique `Hashable` values — membership and uniqueness, not index. `Dictionary` is a hash map from `Hashable` keys. `Range` / `ClosedRange` are intervals, not bags of elements, though they are sequences. All of these sit on `Sequence` / `Collection` so `map` and `filter` work the same. None of them are thread-safe. Pick `Set` when you keep asking “have I seen this id?”; pick `Array` when order matters; do not use a dictionary as an ordered feed. Typical mistake: `contains` on a large `Array` in a hot path instead of a `Set`.



```swift
let ids = Set([1, 2, 2, 3])          // {1, 2, 3}
let names = ["a": 1, "b": 2]
let firstThree = 0..<3
let ordered = [3, 1, 2]
```


**Then they usually ask**

- When is `Set` faster than `Array.contains`?
- Why is `Dictionary` unordered, and what is `Dictionary` iteration order in practice?
- How do `Range` and `Array` both conform to `Collection`?
- Sequence vs Collection — can you walk a Sequence twice?

</details>

<h2 id="type-safety">Type safety</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift checks types **at compile time**. You cannot assign a `String` to an `Int` without a conversion. Optionals make “maybe missing” part of the type, so `nil` is not a silent crash later. Type inference still picks a concrete type — it is not dynamic typing. Typical miss: `as!` / `try!` to “get past” the compiler.



```swift
let n = 3            // Int
// let n: Int = "3"  // does not compile
let parsed = Int("3") // Int?, not Int
```


**Then they usually ask**

- Type safety vs type inference — do they conflict?
- How do optionals fit this story?
- What does `Any` do to the safety?

</details>

<h2 id="value-vs-reference">Value type vs reference type</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **value type** is copied on assignment: structs, enums, tuples. A **reference type** is shared: classes, actors, and closures. This is the semantics question; classes-vs-structs is the language feature that usually implements it. Interviewers want you to talk about identity, mutation you can see from two variables, and what `let` actually protects. Copy-on-write means `Array` and `String` look like values but share storage until a write. The trap is a struct that stores a class — the struct copies, the class does not.



```swift
struct Value { var n: Int }
class Ref { var n: Int; init(n: Int) { self.n = n } }

var v1 = Value(n: 1)
var v2 = v1
v2.n = 2                 // v1.n == 1

let r1 = Ref(n: 1)
let r2 = r1
r2.n = 2                 // r1.n == 2
```


**Then they usually ask**

- Are closures value types or reference types?
- What does `===` tell you that `==` does not?
- How can a struct still share mutable state?
- Why are `Int`, `String`, and `Array` structs instead of classes?

</details>

<h2 id="optionals">What is an optional</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An optional is **`enum Optional<Wrapped> { case none, some(Wrapped) }`**. `nil` is `.none`. That is why `switch`, `map`, and `??` work — it is a real type, not a pointer flag. You unwrap with `if let` / `guard let`, `??`, optional chaining, or (rarely) `!`. IUOs (`String!`) are still optionals that unwrap implicitly and crash if `nil`. Typical mistakes: “optional means a pointer that can be NULL,” and treating `Optional.none` as a value you persist without encoding the absence.



```swift
enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}

let n: Int? = Int("x") // .none
print(n.map { $0 * 2 } ?? 0)
```


**Then they usually ask**

- How is this different from ObjC `nil` messaging?
- Is `Optional` an enum or a struct?
- What does `map` on an optional return?
- When is `Optional.none` the wrong model (empty string vs missing)?
- Is `nil` a different value from `Optional.none`?
- Name every common unwrap: `if let`, `guard let`, `??`, `?`, `map` / `flatMap`, `!`, IUO — when is each honest?

</details>

<h2 id="deinit">deinit</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`deinit` is the class (or actor) teardown hook: it runs when the last strong reference goes away, just before the object is destroyed. Structs and enums do not have it — they have no identity to tear down. You use it to invalidate a `Timer`, stop a socket, or assert in debug that cleanup ran. You cannot `throw`, you cannot `await` in a non-isolated `deinit` (isolated `deinit` on actors is the newer exception), and you must not start work that needs `self` to stay alive. Typical miss: capturing `self` strongly in a timer you only invalidate in `deinit` — the `deinit` never runs.



```swift
final class Ticker {
    private var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }

    deinit { timer?.invalidate() }
}
```


**Then they usually ask**

- Why is there no `deinit` on a struct?
- Which thread runs `deinit`?
- Isolated `deinit` on an actor — what did that fix?

</details>

<h2 id="guard">guard</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`guard`** is an early-exit check. The condition must be true or you leave the scope immediately. That is why `guard let` can bind names for the rest of the function: the compiler knows they exist after the line. You can `guard` any `Bool`, not just optionals — `guard index < count else { return }`. Interviewers like `guard` because it keeps the happy path flat. The else block cannot fall through; if you write `print` and forget `return`, it will not compile. Nested `guard`s that all return the same error should often become one function that throws.



```swift
func firstWord(in text: String?) -> String? {
    guard let text, !text.isEmpty else { return nil }
    return text.split(separator: " ").first.map(String.init)
}
```


**Then they usually ask**

- Why must `guard`’s else exit the current scope?
- Can you `guard` a boolean that is not an optional bind?
- How do you `guard` several optionals at once?

</details>

<h2 id="if-let-vs-guard-let">if let vs guard let</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`if let`** unwraps for the `if` body only. **`guard let`** unwraps for the rest of the scope and forces you to leave on failure (`return`, `throw`, `break`, `continue`, or something that never returns). Prefer `guard` for preconditions at the top of a function so the happy path stays unindented. Prefer `if let` when both the nil and non-nil paths do real work. Swift’s shorthand `if let name` / `guard let name` binds the same name. The miss is a pyramid of `if let` that should have been three `guard`s.



```swift
func greet(_ name: String?) {
    guard let name else { return }
    print("hi \(name)")
}

func label(_ name: String?) -> String {
    if let name {
        return name
    }
    return "anonymous"
}
```


**Then they usually ask**

- What statements are legal in a `guard` else block?
- When is `if let` clearer than `guard let`?
- How does optional binding interact with `async` / `throws`?

</details>

<h2 id="lazy">lazy</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`lazy var` is a stored property that is computed **once**, the first time you read it, then kept. Use it for work you might never need — building a heavy formatter, opening a file, wiring a child object. It must be `var` because the first read mutates storage. It is **not** thread-safe: two threads can run the initializer twice. It is not `let`, and it is not a computed property (those recompute every time). A `let` that still needs work at init is an immediately-invoked closure: `let area = { Double.pi * r * r }()` — eager, once, and safe to share. Typical mistakes: `lazy` for a cheap `DateFormatter` you always use, and capturing `self` in a `lazy` closure that then leaks.



```swift
final class Report {
    lazy var formatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .medium
        return f
    }()
}
```


**Then they usually ask**

- `lazy var` vs a computed `var` vs `let` initialized in `init`?
- Why is `lazy` unsafe across threads?
- How do you make a `let`-like value that is computed once at runtime?
- Can a struct’s `lazy` property be read from a `let` instance?

</details>

<h2 id="let-vs-var">let vs var</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`let` is a binding you cannot reassign. `var` is a binding you can. For a **value type**, `let` also freezes stored properties — you cannot mutate a `let` struct. For a **class**, `let` only freezes the reference: you cannot point it at another instance, but you can still change the object's properties. That is the follow-up interviewers want. Prefer `let` until mutation is required; it documents intent and lets the compiler catch accidents. Typical mistake: “`let` means the object is immutable” while holding a `let` class full of `var` properties.



```swift
struct Point { var x: Int }
class Box { var value: Int = 0 }

let p = Point(x: 1)
// p.x = 2 // error

let box = Box()
box.value = 2 // ok
// box = Box() // error
```


**Then they usually ask**

- Why can you mutate a `let` class but not a `let` struct?
- How does this interact with `mutating` methods?
- When would you use `let` on a reference type on purpose?

</details>

<h2 id="map-vs-compactmap">map vs compactMap</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`map`** transforms every element and keeps the same count. **`compactMap`** transforms and drops `nil`, so you get a shorter non-optional array. This is the everyday “parse these strings into ints” question. People still reach for `flatMap` on optionals out of muscle memory; that overload moved to `compactMap`. Another miss: `map` + `filter { $0 != nil }` + force-unwrap, which is just `compactMap` written the long way. `flatMap` is still the right name when you map to an array and want one flattened array.



```swift
let raw = ["1", "x", "3"]
let mapped = raw.map(Int.init)         // [1, nil, 3]
let compact = raw.compactMap(Int.init) // [1, 3]

let nested = [[1, 2], [3]]
let flat = nested.flatMap { $0 }       // [1, 2, 3]
```


**Then they usually ask**

- What does `map` on an optional do?
- When is `flatMap` the right choice instead of `compactMap`?
- How would you rewrite `compactMap` with `reduce`?

</details>

<h2 id="mutating">mutating</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A struct/enum method that writes `self` (or a stored property) must be marked **`mutating`**. It replaces the whole value; that is why you cannot call it on a `let` instance. Class methods do not need `mutating` — the reference stays, the object changes. Typical miss: “mutating makes it a class.”



```swift
struct Counter {
    var n = 0
    mutating func bump() { n += 1 }
}

var c = Counter()
c.bump()
// let frozen = Counter(); frozen.bump() // error
```


**Then they usually ask**

- Why is `mutating` illegal on a class?
- What does `self = …` mean inside a mutating method?
- How does this interact with a `let` property that holds a struct?

</details>

<h2 id="static">static</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`static` belongs to the **type**, not an instance. `static let` is a shared constant. `static func` is called as `Foo.bar()`. On a class, `class func` is overridable; `static func` is not (it is `final` on the type). Stored `static var` is shared mutable state — treat it like a singleton field. Typical mistake: using `static var` as a cache and wondering why tests leak state across cases.



```swift
enum Theme {
    static let accent = "teal"
    static func label(_ name: String) -> String { "\(accent)-\(name)" }
}

Theme.label("button")
```


**Then they usually ask**

- `static` vs `class` on a method?
- Where does a `static var` live, and is it thread-safe?
- When is `static` better than a singleton object?

</details>

<h2 id="switch">switch</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift `switch` must be **exhaustive**, can match tuples, ranges, optionals, and enum associated values, and can add `where`. No implicit fallthrough — use `fallthrough` if you really want it. That is why it beats a pile of `if` for state. Typical miss: `default` that swallows a new enum case you should have handled.



```swift
switch state {
case .ready(let value) where value > 0: show(value)
case .ready: showEmpty()
case .loading, .idle: showSpinner()
case .failed: showRetry()
}
```


**Then they usually ask**

- Why is exhaustiveness a safety feature?
- `where` vs a nested `if`?
- How do you match two values at once (a tuple)?

</details>

<h2 id="try-try-try">try vs try? vs try!</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`throws`** marks a function that *may* fail; **`throw`** is the statement that actually produces the error. **`try`** calls a throwing function and lets the error keep going — the caller is `throws` or you are inside `do/catch`. **`try?`** turns failure into `nil` and throws the error away. **`try!`** unwraps and crashes if an error appears. **`rethrows`** only throws if a closure argument throws (`map` is the usual example). Interviewers want a hard rule: `try!` is for “if this fails the program is already wrong,” never for network or decoding. `try?` is fine when you truly do not care why it failed; otherwise catch and log. Mixing `try?` with a later force-unwrap is just `try!` with extra steps.



```swift
enum AgeError: Error { case negative }

func checked(_ age: Int) throws -> Int {
    guard age >= 0 else { throw AgeError.negative }
    return age
}

let ok = try? checked(9)      // Optional(9)
let no = try? checked(-1)     // nil
// let crash = try! checked(-1)
```


**Then they usually ask**

- How do you keep the error when you do not want the function to be `throws`?
- When is `try!` acceptable in app code?
- What does `try?` do to the success type?
- `throw` vs `throws` vs `rethrows`?

</details>

<h2 id="available">#available</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`#available`** is a **runtime** check against OS version (and sometimes platform). `if #available(iOS 17, *)` lets you call a newer API and still run on iOS 16. `@available` on a function is the other half: you mark *your* API as requiring that OS. `*` means “also any other platform at its minimum.” This is not `#if os` and not `#if swift` — those are compile-time. The miss is putting a new API outside the `#available` branch, or using `@available` on a whole type and then forgetting a fallback screen.



```swift
func titleFont() -> String {
    if #available(iOS 17, *) {
        return "iOS 17+ path"
    } else {
        return "fallback"
    }
}

@available(iOS 17, *)
func shimmer() {}
```


**Then they usually ask**

- How is `#available` different from `#if os(iOS)`?
- What does the `*` mean in `#available(iOS 17, *)`?
- When do you mark a method `@available` instead of branching inside it?

</details>

<h2 id="discardable-result">@discardableResult</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`@discardableResult` silences the “result unused” warning on a function whose return value is optional to read. `removeValue(forKey:)` returns the old value; most call sites throw it away. Use it when both styles are honest. Do not slap it on `save() -> Bool` to hide ignored errors — that is the interview trap. Typical miss: marking every factory `discardable` so callers never notice they dropped a cancellable.



```swift
@discardableResult
func updateTitle(_ title: String) -> Bool {
    guard !title.isEmpty else { return false }
    self.title = title
    return true
}

updateTitle("Hi")
```


**Then they usually ask**

- When is ignoring the result a bug (`AnyCancellable`, `Bool` error flags)?
- How is this different from `_ = save()` at the call site?
- Why does `print` not need this attribute?

</details>

<h2 id="main-attribute">@main</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`@main`** marks the type that owns the process entry point. The type must have a `static func main()` or conform to something that provides one, like SwiftUI’s `App`. That replaced the old `UIApplicationMain` / `@UIApplicationMain` story for a lot of new apps. There can be only one `@main` in the target. Interviewers use it as a “where does the app start” check. Putting `@main` on a random helper, or keeping both an `App` and a custom `main` in the same target, is how you get a confusing linker error.



```swift
@main
struct InterviewApp {
    static func main() {
        print("entry")
    }
}
```


**Then they usually ask**

- How does SwiftUI’s `App` use `@main`?
- What replaced `@UIApplicationMain`?
- Can a target have two `@main` types?

</details>

<h2 id="caseiterable">CaseIterable</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`CaseIterable`** gives you `allCases`: a collection of every enum case. The compiler synthesizes it for enums without associated values (and for most raw-value enums). You use it for pickers, settings screens, and tests that want every case. Associated values block synthesis because there is no finite list of payloads. Interviewers ask this next to `ForEach(Tab.allCases)`. Do not assume `allCases` order is something you can silently change later if you persist the index; persist the case name or a raw value.



```swift
enum Tab: CaseIterable {
    case home, search, profile
}

let titles = Tab.allCases.map(String.init(describing:))
```


**Then they usually ask**

- Why doesn’t an enum with associated values get `allCases` for free?
- Can you provide your own `allCases` implementation?
- Is the order of `allCases` something you should persist?

</details>

<h2 id="class-vs-object">Class vs object</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **class** is the blueprint: stored properties, methods, the type’s identity. An **object** (instance) is one allocation of that blueprint. `UIView` is the class; `UIView()` is an object. Two objects can share a class and still be different identities (`===`). In Swift you also have structs and enums — “object” in casual speech often means “instance of a type,” not only a class. Typical miss: “the class is in memory, the object is the file.”



```swift
class Dog { var name: String; init(name: String) { self.name = name } }
let a = Dog(name: "Rex")
let b = Dog(name: "Rex")
a === b  // false — two objects, one class
```


**Then they usually ask**

- Class vs instance vs type (`Dog.self`)?
- How is this different for a struct?
- What does `===` compare?

</details>

<h2 id="downcasting">Downcasting</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`as` is a guaranteed upcast (or a bridging cast). `as?` is a failable downcast — `nil` if the runtime type does not match. `as!` crashes on mismatch. You downcast when you have `Any` / a base class / an ObjC `id` and you need a concrete type. Prefer `as?` plus `guard`, or `if let view = sender as? UIButton`. Typical miss: `as!` in a table-view cell dequeue you already typed with `dequeueReusableCell(withIdentifier:for:)`.



```swift
func tap(_ sender: Any) {
    guard let button = sender as? UIButton else { return }
    button.isEnabled = false
}
```


**Then they usually ask**

- `as` vs `as?` vs `as!` — one sentence each?
- Conditional cast vs `is` then `as!`?
- How does this interact with `AnyObject`?

</details>

<h2 id="functions-vs-methods">Functions vs methods</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **function** is a named callable that does not belong to a type (`func clamp`). A **method** is a function on a type (`Array.append`). Methods get `self`; `mutating` methods can write a struct’s storage. Free functions are easier to test and do not force a namespace type. Methods win when the operation is part of the type’s vocabulary. Swift also has `static` / `class` methods (on the type, not an instance). Typical miss: “methods are functions that use `self`” without saying where they live.



```swift
func clamp(_ n: Int, to range: ClosedRange<Int>) -> Int {
    min(max(n, range.lowerBound), range.upperBound)
}

extension Int {
    func clamped(to range: ClosedRange<Int>) -> Int { clamp(self, to: range) }
}
```


**Then they usually ask**

- When do you put a helper on the type vs next to it?
- `static` vs `class` vs a free function in the same file?
- How do you pass a method as a function value (`foo.bar`)?

</details>

<h2 id="multiple-inheritance">Multiple inheritance</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A Swift **class has one superclass**. You do not get C++-style multiple inheritance. You compose behavior with **protocols** (a type can conform to many) and protocol extensions. `AnyObject` is the class-bound. Typical miss: “Swift has multiple inheritance because of protocols” — protocols are not superclasses; they have no stored properties.



```swift
protocol Flying { func fly() }
protocol Named { var name: String { get } }
struct Bird: Flying, Named {
    var name: String
    func fly() {}
}
```


**Then they usually ask**

- Protocol composition (`P & Q`) vs a class hierarchy?
- Why can a protocol not add a stored property?
- When do you still need a class for shared storage?

</details>

<h2 id="stored-properties-on-enum">Stored properties on an enum</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An enum case is a tag plus optional associated values — there is **no instance storage** for extra stored properties. You can have `static` stored properties, computed properties, and methods. Need per-instance data? Put it in the associated value or use a struct. Typical miss: `enum Foo { var id: Int }` and wondering why it will not compile.



```swift
enum Load<Value> {
    case ready(Value)
    var isReady: Bool {
        if case .ready = self { return true }
        return false
    }
    static let retryLimit = 3
}
```


**Then they usually ask**

- Associated value vs a stored property?
- Why can an enum still have a computed `var`?
- When do you switch to a struct?

</details>

<h2 id="strings-are-collections">Strings are collections</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`String` conforms to `Collection` (and `BidirectionalCollection`) of `Character`, so you can iterate, `map`, `filter`, and slice it. Characters are extended grapheme clusters, not UTF-16 code units, so `"é".count` can be `1` even when the bytes are not. You cannot subscript with `Int` because indexing is not O(1) in the way people expect from C strings. Interviewers want you to say “use `String.Index` / `first` / `dropFirst`” instead of `string[0]`. The classic miss is `NSString` bridging math (`utf16`) leaking into Swift and breaking emoji.



```swift
let word = "Swift"
for character in word { _ = character }

let first = word.first
let rest = String(word.dropFirst())
let start = word.startIndex
let second = word[word.index(after: start)]
```


**Then they usually ask**

- Why is `String` not `RandomAccessCollection`?
- What is the difference between `Character`, `Unicode.Scalar`, and UTF-8 views?
- How do you safely take the first N characters?

</details>

<h2 id="subscripts">Subscripts</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A subscript is `type[key]` access you define: `collection[i]`, `dict[key]`. You write `subscript(index: Int) -> Element { get set }`. Use it when the type is a bag of values, not when it is a verb. Multiple parameter lists are legal (`grid[x, y]`). Typical miss: a subscript that hides a network call, or one that traps on a missing key instead of returning optional.



```swift
struct Grid {
    private var cells: [Int]
    subscript(x: Int, y: Int) -> Int {
        get { cells[y * width + x] }
        set { cells[y * width + x] = newValue }
    }
    var width = 8
}
```


**Then they usually ask**

- Subscript vs a named method — when is `[]` a lie?
- Can a subscript throw?
- How does `Dictionary`’s subscript differ from `Array`’s?

</details>

<h2 id="swift-module">Swift module</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **module** is the compile unit you `import`: the app target, a Swift package product, a framework. `internal` (the default) is visible inside the module, not outside. One `.swift` file is not a module — `fileprivate` is the file. A module has a name (`import UIKit`) and an interface the compiler serializes. Typical miss: “a module is a file” or expecting `private` to hide a type from the rest of the app target.



```swift
// In module Networking
public struct Endpoint { public let path: String }
internal struct Signer { }   // app cannot see this
```


**Then they usually ask**

- Module vs target vs package product?
- Why does `internal` on an app type still show up in the same app’s tests (or not)?
- What does `@testable import` change?

</details>

<h2 id="tuples">Tuples</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **tuple** is an anonymous grouping of two or more values, with or without labels. It is the cheap way to return two things from a function or to unpack a pair in a `switch`. It is not a type you design an API around: no stored methods of your own, no inheritance, and only a few synthesized protocols when the elements already conform. Interviewers use this to see if you reach for a tuple when a tiny struct would be clearer. The usual miss is a public function returning `(String, Int, Bool)` that nobody can read six months later.



```swift
func splitName(_ full: String) -> (first: String, last: String) {
    let parts = full.split(separator: " ", maxSplits: 1).map(String.init)
    return (parts[0], parts.count > 1 ? parts[1] : "")
}

let person = splitName("Ada Lovelace")
print(person.first)
```


**Then they usually ask**

- When would you replace a tuple with a struct?
- Can a tuple conform to `Equatable`?
- What is the difference between `(Int, String)` and `(id: Int, name: String)`?

</details>

<h2 id="uuid">UUID</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **`UUID`** is a 128-bit identifier. `UUID()` gives you a random (version 4) value that is unique enough for client-side ids, SwiftData models, and “who is this row” without asking a server. It is `Equatable`, `Hashable`, and `Codable`, and you can round-trip the canonical string form. Interviewers ask it when they want to hear “do not use an array index as identity.” Do not treat a UUID as secret, do not parse strings with a hand-rolled regex, and do not generate a new `UUID()` every time you render a SwiftUI `ForEach` or the views will churn.



```swift
struct Item: Identifiable {
    let id: UUID
    var title: String
}

let item = Item(id: UUID(), title: "Draft")
let parsed = UUID(uuidString: "E621E1F8-C36C-495A-93FC-0C247A3E6E5F")
```


**Then they usually ask**

- Why is a UUID a poor `ForEach` id if you recreate it on every render?
- How do you persist a UUID in JSON?
- When would you use a server integer id instead?

</details>

<h2 id="variadic">Variadic functions</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **variadic** parameter (`Int...`) lets the caller pass zero or more values, and inside the function they arrive as an array. `print` is the one everyone already uses. You usually get one variadic parameter; newer Swift allows more if the labels keep calls readable. Interviewers want “it’s an array in the body.” You cannot forward a real `[Int]` as a variadic without splatting, because Swift has no splat operator — you write an overload that takes `[Int]` instead. An empty call is legal unless you add a precondition.



```swift
func average(_ values: Double...) -> Double {
    guard !values.isEmpty else { return 0 }
    return values.reduce(0, +) / Double(values.count)
}

let mean = average(1, 2, 3, 4)
```


**Then they usually ask**

- What is the type of a variadic parameter inside the function?
- How do you pass an existing array into a variadic function?
- Can a function have two variadic parameters?

</details>

<h2 id="assert">assert()</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`assert`** documents a programmer invariant and traps in debug if it is false. In a normal release build the condition is stripped, so you must not put required work or security checks only inside `assert`. **`precondition`** stays in release (unless you compile `-Ounchecked`). **`assertionFailure` / `preconditionFailure`** are the “this branch is impossible” versions. Interviewers want “debug-only vs always.” The common miss is `assert` on a server response and then force-unwrapping the same value in production.



```swift
func element(at index: Int, in values: [Int]) -> Int {
    assert(index >= 0 && index < values.count, "index out of range")
    return values[index]
}
```


**Then they usually ask**

- How does `precondition` differ from `assert`?
- What happens to `assert` in a Release build?
- When is `fatalError` the better tool?

</details>

<h2 id="inout">inout</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`inout` lets a function write back into the caller’s variable. The value is copied in, mutated, then written back — it is not a C pointer you keep. The argument must be a mutable `var` (or a computed property with a setter). You cannot pass a `let`, a literal, or something that might disappear mid-call. Typical miss: using `inout` to “avoid a return” on a type that should just return a new value.



```swift
func bump(_ n: inout Int) { n += 1 }

var x = 1
bump(&x) // x == 2
```


**Then they usually ask**

- Why the `&` at the call site?
- `inout` vs returning a new value — when is each clearer?
- Can you pass a computed property?

</details>

<h2 id="private-set">private(set)</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`private(set)` (or `internal(set)`, `fileprivate(set)`) keeps a **wider getter** and a **narrower setter**. Callers can read `count` but only the type (or file) can assign. This is the usual “expose state, hide mutation” knob — a ViewModel’s `items` that the view must not replace. It is not the same as a computed getter over a private stored property, but it reads the same at the call site. Typical miss: `private(set) var` on a struct and then mutating it from a `let` instance.



```swift
struct Counter {
    private(set) var value = 0
    mutating func bump() { value += 1 }
}
```


**Then they usually ask**

- `private(set)` vs a public getter and a private `var`?
- What access does the setter have if you write only `private(set)`?
- Does this work on a class property observed by UI?

</details>

<h2 id="typealias">typealias</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A `typealias` is a **name** for an existing type, not a new type. `typealias Codable = Encodable & Decodable` is the one everyone already uses. You write one for a long closure (`typealias Handler = (Result<Data, Error>) -> Void`), a platform alias (`UIColor` vs `NSColor`), or a shorter generic (`typealias ID = UUID`). It does not add methods or change ABI by itself. Typical miss: treating a typealias as a distinct type that would stop you from passing the original, or using it to hide a 12-parameter tuple instead of a struct.



```swift
typealias JSON = [String: Any]
typealias Done = (Result<User, Error>) -> Void

func load(then: Done) { /* … */ }
```


**Then they usually ask**

- `typealias` vs a wrapper struct — when do you want a real type?
- Why is `Codable` a typealias and not a third protocol with extra methods?
- Can two modules alias the same name to different types?

</details>

<h2 id="compare-tuples">Compare two tuples</h2>

<code>Junior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Tuples compare **lexicographically** when every element is `Comparable` and both tuples have the same shape. Swift checks the first element, then the next, the same way you sort last names then first names. Equality works the same way with `Equatable` elements. This is a small-language question; they want to hear that `(1, 100) < (2, 0)` is true because `1 < 2`. You cannot compare tuples of different arity or mix incomparable types. Do not invent a custom `<` on a tuple when a named struct with `Comparable` would document the order.



```swift
(1, "b") < (1, "c")     // true
(2, 0) < (1, 99)        // false
(1, 2, 3) == (1, 2, 3)  // true
```


**Then they usually ask**

- In what order are elements compared?
- Can you compare `(Int, String)` with `(String, Int)`?
- How would you sort an array of `(score, name)` tuples?

</details>

<h2 id="one-sided-ranges">One-sided ranges</h2>

<code>Junior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **one-sided range** leaves one bound off: `3...` means “from 3 through the end,” `..<3` means “from the start up to but not including 3.” You use them to slice collections and in `switch` patterns. They are not free-floating integers; the collection still has to supply the missing end. Common mistakes: `array[3...]` on an index past `endIndex` (that traps), and treating a `String` as if `"hello"[2...]` compiled. On strings you still walk `String.Index`.



```swift
let names = ["Ann", "Bob", "Cara", "Drew"]
let tail = names[1...]     // Bob, Cara, Drew
let head = names[..<2]     // Ann, Bob

switch 12 {
case 10...: print("at least ten")
default: break
}
```


**Then they usually ask**

- What is the difference between `...` and `..<` on the open side?
- Why can’t you write `"Swift"[1...]`?
- How do one-sided ranges show up in `switch` on numbers?

</details>

<h2 id="raw-strings">Raw strings</h2>

<code>Junior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **raw string** is written `#"..."#` (or more hashes if needed) so backslashes and quotes are mostly literal. You want it for regex-ish patterns, Windows-style paths, and pasted JSON that is full of `"`. Interpolation still works with `\#(value)` instead of `\(value)`. Interviewers treat this as “do you know the syntax,” then move on. The miss is stacking hashes wrong when the payload itself contains `"#`, or forgetting that a normal string still needs `\\` for a single backslash.



```swift
let pattern = #"\d+\.\d+"#
let quote = #"He said "ship it""#
let name = "Ada"
let line = #"Hello \#(name)"#
```


**Then they usually ask**

- How do you interpolate inside a raw string?
- What if the string itself contains `#"#`?
- When is a raw string worse than a normal escaped string?

</details>

<h2 id="omit-return">When functions omit return</h2>

<code>Junior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

If a function or closure is a **single expression**, you can skip `return` and Swift uses that expression as the result. Closures in `map` do this constantly. Newer Swift also lets `if` and `switch` be expressions, so a short function can still omit `return` even with a branch. Interviewers ask it as a syntax check, not a design question. It only works for one expression — a `print` plus a value needs `return` again. Do not hide a throwing call or a side effect in a no-`return` one-liner just to look clever.



```swift
func doubled(_ n: Int) -> Int { n * 2 }

let squares = [1, 2, 3].map { $0 * $0 }

func label(for count: Int) -> String {
    if count == 1 { "one" } else { "many" }
}
```


**Then they usually ask**

- Can you omit `return` when the body has two statements?
- How do `if` expressions change this in recent Swift?
- Does this work for `throw`ing functions?

</details>

<h2 id="print-vs-debugprint">print vs debugPrint</h2>

<code>Junior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`print` uses `CustomStringConvertible` — the user-facing text. `debugPrint` uses `CustomDebugStringConvertible` when it exists, otherwise falls back, and it quotes strings and shows structure that is nicer in a log. For `"hi"` they look similar; for an array of strings, `debugPrint` adds quotes so you can see whitespace. In interviews this is a “do you read the stdlib” check, not a design question. Prefer structured logging (`Logger`) in production; these two are for consoles and playgrounds.



```swift
let words = ["a", "b c"]
print(words)       // [a, b c]
debugPrint(words)  // ["a", "b c"]
```


**Then they usually ask**

- Which protocol does each one prefer?
- When would you implement `CustomDebugStringConvertible` separately from `description`?
- Why is `Logger` a better default in an app?

</details>

### Mid

<h2 id="associated-types">Associated types</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An associated type is a placeholder the conforming type fills in — `Collection.Element`, `Iterator.Element`. The protocol is then a **PAT**: it is not a concrete type by itself, because the compiler does not know the placeholders. You cannot write `let c: Collection`. You use a generic (`func sum<C: Collection>(_ c: C)`), an opaque `some Collection<Int>`, or `any Collection<Int>` (primary associated types). Type erasure (`AnyCollection`) is the older escape hatch. Interviewers want “why `let x: Iterator` does not compile,” not a recitation of `associatedtype`. Typical mistake: adding an associated type when a generic method on the protocol would do.



```swift
protocol Stack {
    associatedtype Element
    mutating func push(_ value: Element)
    mutating func pop() -> Element?
}

struct IntStack: Stack {
    private var storage: [Int] = []
    mutating func push(_ value: Int) { storage.append(value) }
    mutating func pop() -> Int? { storage.popLast() }
}

func peekCount<S: Stack>(_ stack: S) -> String { "stack" }
```


**Then they usually ask**

- Why did `any Collection` need primary associated types to be useful?
- Associated type vs a generic on the protocol method?
- How would you type-erase a PAT without `any`?

</details>

<h2 id="copy-on-write">Copy-on-Write</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Copy-on-write means assignment **shares storage** until someone mutates. `Array`, `String`, and `Dictionary` do this: `var b = a` is cheap; `b.append` copies only if the buffer is not uniquely referenced. You build the same thing with a class heap buffer plus `isKnownUniquelyReferenced`. If the buffer is unique, mutate in place; if not, copy, then mutate. Interviewers want the uniqueness check, not “structs are cheap.” Typical mistakes: putting a class inside a struct and thinking you got value semantics, or copying on every write even when the buffer is unique.



```swift
final class Storage { var values: [Int] }

struct List {
    private var storage: Storage

    init(_ values: [Int]) { storage = Storage(values: values) }

    mutating func append(_ value: Int) {
        if !isKnownUniquelyReferenced(&storage) {
            storage = Storage(values: storage.values)
        }
        storage.values.append(value)
    }
}
```


**Then they usually ask**

- Why must `append` be `mutating` if the class can change in place?
- What happens if two threads mutate CoW storage without synchronization?
- Why don't most of your model structs need custom CoW?
- Copy an `[Class]`, `popLast` one array, mutate an element — who sees the new name?

</details>

<h2 id="property-wrappers">Custom property wrappers</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **property wrapper** is a type marked `@propertyWrapper` with a `wrappedValue`. Writing `@Clamped var score` is sugar for storing a `Clamped` instance and talking to its wrapped value. `$score` is the `projectedValue` if you define one — that is how `@State` exposes a `Binding`. You write wrappers for clamping, UserDefaults, analytics, and locking. Interviewers want you to know they are types, not compiler magic, and that composition and `init` rules get awkward. Do not wrap everything; a function is clearer when there is no reused pattern.



```swift
@propertyWrapper
struct Clamped {
    private var value: Int
    var wrappedValue: Int {
        get { value }
        set { value = min(max(newValue, 0), 10) }
    }
    init(wrappedValue: Int) {
        value = min(max(wrappedValue, 0), 10)
    }
}

struct Game {
    @Clamped var lives = 3
}
```


**Then they usually ask**

- What is `projectedValue` and how do you read it?
- How does `@State` use a property wrapper?
- What are the limits of composing two wrappers on one property?

</details>

<h2 id="enum-associated-values">Enum associated values</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An enum case can carry a **payload**: `case loaded(Data)`, `case failed(Error)`. That is how Swift models a state machine without a pile of optional properties that can be inconsistent. Associated values are not raw values — raw values are a single compile-time companion like `String` for every case. You unwrap with `switch` or `if case`. Interviewers love “loadable” enums versus `isLoading` + `value` + `error`. The miss is putting a mutable class in the payload and then wondering why two `.loaded` values share storage.



```swift
enum LoadState {
    case idle
    case loaded(Data)
    case failed(Error)
}

func title(for state: LoadState) -> String {
    switch state {
    case .idle: return "—"
    case .loaded(let data): return "\(data.count) bytes"
    case .failed: return "failed"
    }
}
```


**Then they usually ask**

- How do associated values differ from raw values?
- Can a case have more than one associated value?
- Why is an enum safer than three optionals for loading UI?

</details>

<h2 id="escaping-closures">Escaping vs non-escaping closures</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A closure is **non-escaping** when it is called before the function returns — that is the default for arguments. **`@escaping`** means the function stores it or calls it later: completion handlers, `DispatchQueue.async`, Combine sinks. Escaping closures can outlive `self`, so they capture strongly unless you write `[weak self]`. Non-escaping closures can use `self` without writing `self.` in many cases, because the compiler knows the cycle cannot form that way. Interviewers will ask why `@escaping` appeared on your completion handler. Marking something `@escaping` “just in case” when you call it synchronously is a lie to the compiler and to readers.



```swift
var handlers: [() -> Void] = []

func store(_ handler: @escaping () -> Void) {
    handlers.append(handler)
}

func runNow(_ handler: () -> Void) {
    handler()
}
```


**Then they usually ask**

- Why can non-escaping closures skip `self.` in instance methods?
- How does `@escaping` interact with `async`?
- What retain cycle does a stored completion handler usually create?
- `@escaping` vs `@autoclosure` — can a parameter be both?

</details>

<h2 id="extension-vs-protocol-extension">Extension vs protocol extension</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **type extension** adds methods, computed properties, or conformances to one concrete type. A **protocol extension** adds a default implementation to every current and future conformer. Neither can add stored properties. The interview trap is dispatch: if a method lives only in a protocol extension and is **not** a protocol requirement, it is statically dispatched from the compile-time type. Override it on a class and call it through the protocol, and you may still run the default. Put the method on the protocol if you want dynamic dispatch. Use type extensions for conveniences; use protocol extensions for shared behavior you are willing to make a default.



```swift
protocol Speaker {
    func greet()
}

extension Speaker {
    func greet() { print("hello") }
    func wave() { print("wave") }   // not a requirement
}

struct Person: Speaker {
    func greet() { print("hi") }
}

let speaker: any Speaker = Person()
speaker.greet()   // hi
speaker.wave()    // wave — static if only on the extension
```


**Then they usually ask**

- Why can’t extensions add stored properties?
- What is the witness-table vs static-dispatch gotcha?
- When is a free function clearer than a protocol extension?

</details>

<h2 id="generics">Generics</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Generics** let a function or type work with a placeholder (`T`) that is filled in at the call site. Constraints (`T: Hashable`) are how you keep that placeholder from being “anything” when you need `==` or a hash. You use them for collections, parsers, and “this algorithm does not care what the element is.” Interviewers will walk from `func first<T>` to associated types on protocols. The misses: over-generic APIs nobody can spell, and using `Any` because the generic signature got awkward. A generic type is still one concrete type at runtime for each specialization the compiler builds.



```swift
func first<T>(_ items: [T]) -> T? { items.first }

struct Stack<Element> {
    private var items: [Element] = []
    mutating func push(_ item: Element) { items.append(item) }
    mutating func pop() -> Element? { items.popLast() }
}
```


**Then they usually ask**

- How do you constrain `T` to more than one protocol?
- When do you use an associated type instead of a generic on the protocol itself?
- What is type specialization?

</details>

<h2 id="method-dispatch">Method dispatch</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift picks one of three paths. **Static dispatch** (direct call) is the default for structs, enums, `final` class methods, and `private` members the compiler can prove. **Table dispatch** uses a vtable on classes and a **protocol witness table** on protocol existentials — the callee is chosen at runtime. **Objective-C message send** (`objc_msgSend`) is what `@objc dynamic` and most UIKit overrides use: you can swizzle it, and it is slower. `final` and value types are not just style — they let the compiler devirtualize and sometimes inline. Typical mistake: putting a hot method on a protocol existential in a tight loop and wondering why it does not optimize like a generic.



```swift
protocol Drawable { func draw() }
struct Circle: Drawable { func draw() {} }

final class Icon {
    func render() {} // static — class is final
}

func paint(_ item: any Drawable) {
    item.draw() // witness table
}
```


**Then they usually ask**

- What does `dynamic` change?
- Generic `func paint<T: Drawable>(_ item: T)` vs `any Drawable` — which can specialize?
- Why does `final` help performance?
- Can you `override` a method that lives only in a class `extension`?
- A method exists only in a protocol extension — static or witness-table?

</details>

<h2 id="opaque-return-types">Opaque return types</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`some Protocol`** means “one concrete type that conforms, but I will not name it.” The compiler knows the type; the caller only sees the protocol. That preserves identity and lets the compiler specialize, which is why SwiftUI’s `some View` works. `any Protocol` is a box that can hold different conformers at runtime. With `some`, both branches of an `if` must return the same underlying type — hence `Group` / `AnyView` when they do not. Interviewers want that contrast. Returning `some View` and then changing the body to two different view types is the compile error everyone hits.



```swift
func badge() -> some Equatable {
    "new"
}

func label(highlighted: Bool) -> some Equatable {
    highlighted ? "on" : "off"
}
```


**Then they usually ask**

- How does `some` differ from `any`?
- Why does SwiftUI use `some View` instead of `any View` everywhere?
- What do you do when two branches need different concrete types?

</details>

<h2 id="result-builders">Result builders</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **result builder** (`@resultBuilder`) turns a stack of statements in a closure into one value by calling `buildBlock`, `buildIf`, `buildEither`, and friends. SwiftUI’s `@ViewBuilder` is the one you already use: a `VStack` body can list views without returning an array. You can write a tiny builder for strings or for test steps. Interviewers want the mechanism, not a SwiftUI tutorial. Builders hide control flow — `if` becomes `buildEither` — so debugging a generic `some View` error is painful. Do not invent a builder when a `[Item]` parameter would do.



```swift
@resultBuilder
struct StringBuilder {
    static func buildBlock(_ parts: String...) -> String {
        parts.joined()
    }
}

@StringBuilder
func title() -> String {
    "Hello"
    " "
    "Swift"
}
```


**Then they usually ask**

- Which `build*` methods does `if/else` need?
- How does `@ViewBuilder` use this?
- When is a result builder the wrong abstraction?
- Why does a `body` with more than ten children need a `Group` / `TupleView` split?

</details>

<h2 id="result-type">Result type</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`Result<Success, Failure>`** is an enum with `.success` and `.failure` where `Failure` is an `Error`. You use it when a value has to travel through a callback, a cache, or Combine and you cannot `throw` across that boundary. `get()` turns it back into `throws`; `Result { try … }` goes the other way. Interviewers compare it with optionals (`nil` is not a reason) and with `async`/`throws` (often cleaner at a function boundary). Swallowing the error with `try?` just to stuff a `Result` somewhere is the usual smell.



```swift
enum ParseError: Error { case empty }

func parse(_ text: String) -> Result<Int, ParseError> {
    text.isEmpty ? .failure(.empty) : .success(text.count)
}

switch parse("hi") {
case .success(let count): print(count)
case .failure(let error): print(error)
}
```


**Then they usually ask**

- How do you convert `Result` to `throws` and back?
- When do you prefer `async throws` over `Result`?
- Why is `Result<T, Error>` sometimes worse than a typed failure?

</details>

<h2 id="immutability">Why immutability matters</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Immutability** means a value does not change after you create it: `let` bindings, value types, and APIs that return a new value instead of mutating in place. Interviewers are not grading whether you type `let` by habit. They want the reasons: local reasoning (no surprise mutation behind a shared reference), safer concurrent reads, and fewer side effects when you pass data into a view or a test. `let` on a class instance only freezes the pointer, not the object’s properties. The other miss is treating “I used a struct” as thread-safe while that struct still holds a class or a callback that mutates something else.



```swift
struct Account {
    let id: String
    var balance: Int
}

let frozen = Account(id: "a1", balance: 10)
var working = frozen
working.balance += 5
// frozen.balance is still 10
```


**Then they usually ask**

- Does `let` on a class make the object immutable?
- How does copy-on-write interact with `let` arrays?
- When is a mutable class still the honest model?

</details>

<h2 id="defer">defer</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`defer`** schedules work for when the current scope exits — `return`, `throw`, `break`, or falling off the end. Several `defer`s run in reverse order, last-in first-out. A `defer` nested *inside* another `defer` runs when that inner block exits, not as a fourth item on the outer stack. You use it so cleanup sits next to setup: close the file, end the activity, unlock. It does not catch errors and it does not create a new scope for failures; it just delays statements. Interviewers like “unlock even if we throw.” Putting `return` inside `defer` is illegal. Reading a variable in `defer` sees the value at exit time, not at the `defer` line.



```swift
func parse() -> Int {
    var step = "start"
    defer { print(step) }
    defer { print("second") }
    step = "done"
    return 1
}
// prints "second" then "done"
```


**Then they usually ask**

- In what order do stacked `defer` blocks run?
- Does `defer` run if the function throws?
- Why is `defer` better than duplicating cleanup before every `return`?
- What prints if one `defer` contains another `defer`?

</details>

<h2 id="final">final keyword</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`final`** on a class (or method) forbids subclassing or overriding. That is both a design signal — “this type is not an extension point” — and a performance hint, because the compiler can skip vtable dispatch. You see it on helpers, view models, and anything you do not want people to inherit from just to poke at internals. Interviewers also want: `final` is implied for structs and enums already. Marking a class `final` does not make it a value type. The miss is leaving every UIKit subclass open “just in case,” then discovering override soup.



```swift
final class ImageCache {
    func data(for key: String) -> Data? { nil }
}

// class DiskCache: ImageCache {} // error
```


**Then they usually ask**

- Does `final` change ARC or value semantics?
- Why might the compiler generate faster code for `final` methods?
- When do you mark a single method `final` but leave the class open?

</details>

<h2 id="self-vs-self">self vs Self</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`self`** is the current instance. **`Self`** is the current type — the class, struct, or the concrete conformer in a protocol. You use `Self` in protocol requirements (`func copy() -> Self`), in static factories, and when a subclass should return its own type. **`Self.self`** is the metatype value (`Point.Type`) — what you pass to `JSONDecoder.decode(User.self)`. `self` is what you write in escaping closures and to disambiguate a property from a parameter. Interviewers will put both on a whiteboard because the words sound the same when spoken. `Self` in a protocol is a PAT constraint; it is one reason those protocols needed type erasure for so long.



```swift
struct Point {
    var x: Int
    static func zero() -> Self { Self(x: 0) }
    func doubled() -> Self { Self(x: x * 2) }
}

extension Point {
    func offset(_ x: Int) -> Point {
        var copy = self
        copy.x += x
        return copy
    }
}
```


**Then they usually ask**

- Why do some protocols use `Self` in a return type?
- When must you write `self.` inside a closure?
- How does `Self` behave in a class hierarchy versus a struct?
- `self` vs `Self` vs `Self.self` — one sentence each?

</details>

<h2 id="some-vs-any">some vs any</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`some P` is an **opaque** type: the caller knows it conforms to `P`, the compiler still knows the concrete type. That lets it specialize and keep a small fixed layout. `any P` is an **existential**: the value is boxed, the concrete type can change at runtime, and calls go through a witness table. Use `some` for a return type you control (`some View`). Use `any` when you must store mixed conformers or the type changes. A protocol with associated types often cannot be a bare type — you write `any Collection` or a generic. Typical mistake: “`any` is just the new spelling of the protocol name” without the box cost, or returning `any View` from a SwiftUI `body`.



```swift
func label() -> some Equatable { "ok" }
// let a = label(); let b = label(); a == b // same underlying type

var items: [any Equatable] = [1, "x"]
```


**Then they usually ask**

- Why is `some View` required in `body` instead of `any View`?
- How does this relate to PAT (protocol with associated types)?
- When is the existential box a real performance problem?
- `func f<T: Equatable>(_: T)` vs `func f(_: some Equatable)` — same idea?

</details>

<h2 id="autoclosure">@autoclosure</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`@autoclosure`** wraps an argument expression in a `() -> T` for you, so the callee decides whether to evaluate it. `assert` and `precondition` use this so a heavy failure message is not built when the check passes. `&&` / `||` are the conceptual cousins: the second operand may never run. You write `@autoclosure` on your own APIs when the argument is a default or a diagnostic. Interviewers want “it delays evaluation.” Calling the closure twice evaluates the expression twice — do not pass something with side effects unless that is the point. It does not make a closure escaping unless you also mark `@escaping`.



```swift
func expect(_ condition: @autoclosure () -> Bool, _ message: @autoclosure () -> String) {
    if !condition() {
        print(message())
    }
}

let count = 0
expect(count > 0, "expensive \(Array(repeating: "!", count: 1000).joined())")
```


**Then they usually ask**

- Why do `assert` and `precondition` take autoclosures?
- What happens if the callee invokes the autoclosure twice?
- How does `@autoclosure @escaping` differ from a plain `@autoclosure`?

</details>

<h2 id="frozen">@frozen</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`@frozen` is a **library-evolution** promise: this enum or struct will not grow public cases or stored properties in a way that breaks clients compiled against an older SDK. The compiler can then omit the “unknown future case” path — exhaustive `switch` without `@unknown default`, and cheaper layout. You put it on stdlib-style types (`Result`, `Optional`) and on your own ABI-stable modules. App code that is not a binary framework almost never needs it. Typical miss: `@frozen` on an app enum “for performance,” or adding a case to a frozen public enum and shipping a silent ABI break.



```swift
@frozen public enum Load<Value> {
    case idle
    case ready(Value)
}

func label<Value>(_ load: Load<Value>) -> String {
    switch load {
    case .idle: return "…"
    case .ready: return "ok"
    }
}
```


**Then they usually ask**

- `@frozen` vs `@unknown default` on a non-frozen enum?
- When does an app target actually need this?
- What breaks if you add a stored property to a frozen public struct?

</details>

<h2 id="abstract-class">Abstract class in Swift</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift has no `abstract` keyword. You get the same shape with a **protocol** (required methods, no default) plus a protocol extension for shared code, or a class you never instantiate whose methods you expect subclasses to override — which the compiler will not enforce. Prefer the protocol. `required init` and factory methods cover “must construct a subclass.” Typical mistake: an empty base class that only exists so two types can share a name.



```swift
protocol Feed {
    func load() async throws -> [String]
}

extension Feed {
    func loadOrEmpty() async -> [String] {
        (try? await load()) ?? []
    }
}
```


**Then they usually ask**

- Why not a base class with `fatalError("override")`?
- How do PAT and `some Feed` change this?
- When is a class hierarchy still the right model?

</details>

<h2 id="composition-over-inheritance">Composition over inheritance</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Prefer **has-a** over **is-a**. A `Player` *has* a `Health` and a `Mover` instead of a 6-level `GameObject` tree. Swift pushes this with protocols and structs. Inheritance still wins for UIKit (`UIViewController`) and a real “is a” (a `UIButton` is a `UIView`). Typical miss: a base class with `fatalError("override")` for every feature.



```swift
struct Health { var hp: Int }
struct Player { var health: Health; var name: String }
```


**Then they usually ask**

- When is a class hierarchy still the right model?
- How does this show up as protocol composition (`P & Q`)?
- What does this have to do with testing?

</details>

<h2 id="conditional-conformances">Conditional conformances</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A type can conform to a protocol **only when its parameters do**: `Array` is `Equatable` when `Element` is. You write `extension Box: Equatable where T: Equatable`. That is how generic wrappers stay honest — a box of functions is not `Equatable` just because `Box` exists. Interviewers ask this after generics. You cannot conditionally conform in a way that overlaps another conformance, and the `where` clause has to be something the compiler can prove at the use site. The miss is implementing `==` on the wrapper unconditionally and crashing or lying when `T` cannot compare.



```swift
struct Box<T> {
    var value: T
}

extension Box: Equatable where T: Equatable {}

let a = Box(value: 1)
let b = Box(value: 1)
_ = a == b
```


**Then they usually ask**

- Why is `[Int]` equatable but `[() -> Void]` is not?
- Can you add a conditional `Codable` conformance the same way?
- What happens if two conditional conformances overlap?

</details>

<h2 id="designated-convenience-init">Designated vs convenience initializers</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **designated** init fully initializes the type and calls `super.init` (classes). A **convenience** init must call another init on `self` and exists to fill defaults. Swift structs have memberwise inits; classes need you to be explicit. The two-phase rule: set your own stored properties, then `super`, then customize. Typical miss: a subclass designated init that does not call `super`, or a convenience init that tries to set a superclass property directly.



```swift
class Vehicle {
    let wheels: Int
    init(wheels: Int) { self.wheels = wheels }
    convenience init() { self.init(wheels: 4) }
}
```


**Then they usually ask**

- Why must a convenience init call `self.init`?
- Required init — when does a subclass inherit it?
- How does this differ from a struct’s memberwise init?

</details>

<h2 id="failable-throwing-init">Failable and throwing initializers</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`init?` can return `nil` when input is illegal (`Int("x")`, `URL(string:)`). `init(...) throws` fails with an `Error` when you have more than one reason. Pick `init?` for a simple “this string is not a value.” Pick `throws` when the caller should switch on *why*. A class failable init must assign stored properties before returning `nil` on the failure path after `super.init` rules are satisfied — the usual trap is a convenience `init?` that forgets the designated path. Typical miss: `try!` on a throwing init in production.



```swift
struct Port {
    let value: Int
    init?(raw: String) {
        guard let n = Int(raw), (1...65535).contains(n) else { return nil }
        value = n
    }
}
```


**Then they usually ask**

- `init?` vs `init!` vs `throws`?
- Can a failable init call a throwing one?
- Why is `UIImage(named:)` failable?

</details>

<h2 id="key-paths">Key paths</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **key path** is a typed pointer to a property: `\User.name`. You pass it to `map`, `sorted(by:)`, KVO-style APIs, and SwiftUI. `\ .self` is the identity path, useful for `Set` of simple values. There are read-only, writable, and reference-writable variants depending on `let` / `var` and value vs class. Interviewers want this instead of `{ $0.name }` when the closure is only a property access. Key paths are values — you can store them — but they are not a general query language, and they will not call methods with arguments.



```swift
struct User {
    var name: String
    var age: Int
}

let users = [User(name: "Ada", age: 36), User(name: "Grace", age: 85)]
let names = users.map(\.name)
let oldest = users.sorted(by: \.age).last
```


**Then they usually ask**

- What is the difference between `KeyPath` and `WritableKeyPath`?
- How do you write a key path through several properties?
- Where does SwiftUI use key paths?

</details>

<h2 id="macros">Macros</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A Swift **macro** is compile-time code that writes more Swift (`@Observable`, `#Preview`, `#expect`). Freestanding macros look like `#name`; attached macros look like `@name` on a type or member. They run in a sandbox and expand to source you can show in Xcode. Use them to kill boilerplate you would otherwise generate by hand — not to hide control flow. Typical miss: treating a macro as runtime reflection, or shipping a macro plugin that is not versioned with the module.



```swift
@Observable
final class Cart {
    var items: [Item] = []
}

#Preview {
    CartView()
}
```


**Then they usually ask**

- Freestanding vs attached — one example each?
- How is this different from a property wrapper?
- What do you expand in Xcode when a macro misbehaves?

</details>

<h2 id="mirror">Mirror and reflection</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`Mirror` is Swift’s **read-only reflection**: give it an instance and you can walk `children` (label + value) and a display style. It is for debug dumps, a naive serializer, or tests that assert stored properties. It is not KVC, it will not call methods, and it is slow and brittle across module boundaries (`private` children disappear). `type(of:)` / `.Type` / `.self` are **metatypes** — you construct or compare types, you do not walk stored properties. Typical miss: building production persistence on `Mirror`, or expecting it to see a computed property as a child.



```swift
struct User { let name: String; let age: Int }
for child in Mirror(reflecting: User(name: "Ada", age: 36)).children {
    print(child.label ?? "?", child.value)
}
```


**Then they usually ask**

- Mirror vs `dump` vs a `CustomDebugStringConvertible`?
- Why is this a bad Core Data / SwiftData substitute?
- Metatype (`User.Type`) vs an instance `Mirror` — which question were they asking?

</details>

<h2 id="never">Never</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`Never` is a type with **no values**. A function that returns `Never` cannot return — `fatalError`, `preconditionFailure`, an infinite `while true`. A publisher or `Result` that uses `Never` as `Failure` cannot fail. `switch` on `Never` needs no cases. Interviewers want “uninhabited type,” not “void.” `Void` has one value `()`. Typical miss: writing `-> Never` on a function that sometimes returns, or thinking `fatalError` returns `Void`.



```swift
func die(_ message: String) -> Never {
    fatalError(message)
}

let taps = PassthroughSubject<Void, Never>()
```


**Then they usually ask**

- `Never` vs `Void` — one sentence each?
- Why can `Result<Int, Never>`’s `get()` be non-throwing?
- Where does SwiftUI use `Never` (e.g. `EmptyView` body)?

</details>

<h2 id="string-count">String.count complexity</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`String` is a collection of **extended grapheme clusters**, not UTF-16 units. `count` walks the string, so it is **O(n)** in the number of clusters — `"👨‍👩‍👧‍👦".count` is 1, not 4. `utf8.count` / `utf16.count` are cheaper views when you need bytes or NSString length. Do not cache `count` as if it were `Array.count` (O(1)) unless you measured and the string is huge. Typical miss: using `count` in a loop condition that rescans every time, or assuming `NSString.length` matches `String.count`.



```swift
let s = "👨‍👩‍👧‍👦"
s.count          // 1
s.utf16.count    // 11
(s as NSString).length
```


**Then they usually ask**

- Why is `index(offsetBy:)` also O(n)?
- `count` vs `isEmpty` — which do you use as a boolean?
- How did this differ in very old Swift (`countElements`)?

</details>

<h2 id="typed-throws">Typed throws</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift 6 can throw a **concrete error type**: `func load() throws(LoadError)`. Callers `catch` that type without an existential `any Error` box, and the compiler knows the failure set. `throws` still means `throws(any Error)`. Use a typed throw when the API has two or three recoverable cases you want the caller to switch on; keep `any Error` at a system boundary (URLSession, disk) and map inward. Typical miss: typing every helper and then `throws(any Error)` at the UI anyway, or inventing an error enum with twenty cases nobody handles.



```swift
enum LoadError: Error { case missing, forbidden }

func load() throws(LoadError) -> String {
    throw .missing
}

do {
    _ = try load()
} catch .missing {
    // typed
} catch {
    // forbidden
}
```


**Then they usually ask**

- When do you still want `any Error`?
- How do you map `URLError` into a typed domain error?
- Does typed throws change `Result`?

</details>

<h2 id="error-directive">#error directive</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`#error("message")`** is a compile-time hard stop. The build fails and the string shows up in Xcode. You use it for “this configuration is not allowed” or to mark a stub that must not ship. `#warning` is the same idea without failing the build. This is not `fatalError` and not `assert` — those run later, if they run at all. Interviewers want you to separate preprocessor diagnostics from runtime traps. Leaving `#error` inside an inactive `#if` branch is fine; that is how you forbid a target combination.



```swift
#if DEBUG
#else
#error("Local runs must use the Debug configuration")
#endif
```


**Then they usually ask**

- How is `#error` different from `fatalError`?
- When would you choose `#warning` instead?
- Can `#error` sit inside `#if os(iOS)`?

</details>

<h2 id="if-swift">#if swift</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`#if swift(>=5.9)`** (and friends) is compile-time code that depends on the **language version**, not the OS. You use it when a module still builds with more than one Swift toolchain, or when a feature only exists after a compiler cut. `#available` is the runtime OS check; mixing them up is the whole question. There is also `#if compiler(>=5.7)` when you care about the compiler, not the language mode. Dead branches are stripped, so you can call APIs that do not exist on the older side. Do not use this to detect iOS 17.



```swift
#if swift(>=5.9)
func featureFlag() -> String { "macros-era Swift" }
#else
func featureFlag() -> String { "older Swift" }
#endif
```


**Then they usually ask**

- How is `#if swift` different from `#available`?
- When do you use `#if compiler` instead?
- Does the inactive branch get type-checked against the current SDK?

</details>

<h2 id="multi-pattern-catch">Multi-pattern catch</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **`catch`** clause can list several patterns: `catch LoadError.offline, LoadError.timeout`. One body handles all of them. You still want a final `catch` if the function can throw other errors, or the `do` is not exhaustive. Interviewers ask this after `do/try` to see if you know patterns beyond `catch { }`. You can bind values in a pattern (`catch LoadError.http(let code) where code >= 500`). Do not smash unrelated failures into one clause just to save lines — retrying a decode error like a timeout is the bug.



```swift
enum LoadError: Error { case offline, timeout, decoding }

func handle(_ work: () throws -> Void) {
    do {
        try work()
    } catch LoadError.offline, LoadError.timeout {
        print("retry")
    } catch {
        print(error)
    }
}
```


**Then they usually ask**

- Can you bind associated values in a multi-pattern `catch`?
- What happens if no `catch` matches?
- When is a `where` clause on `catch` useful?

</details>

<h2 id="operator-overloading">Operator overloading</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift lets you define `+`, `==`, and even custom operators as `static` functions on a type. Use it when the operation is obvious (`Seconds + Seconds`) and people will not have to guess precedence. Interviewers treat this as a taste question: synthesized `Equatable` / `Comparable` beats a hand-rolled `==` most of the time, and a named method beats `>>>` in app code. Overloading `+` to mutate a database or concatenate unrelated types is the red flag. If you add an operator, keep it in the same module as the type and write the identity and inverse the way math would.



```swift
struct Seconds {
    var value: Int

    static func + (lhs: Seconds, rhs: Seconds) -> Seconds {
        Seconds(value: lhs.value + rhs.value)
    }
}

let total = Seconds(value: 10) + Seconds(value: 5)
```


**Then they usually ask**

- When should you implement `Equatable` yourself instead of letting the compiler do it?
- What goes wrong with a custom operator that has surprising precedence?
- How do you overload `+=` versus `+`?

</details>

<h2 id="can-import">canImport()</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`#if canImport(UIKit)`** compiles a branch only if that module exists for the current target. It is how one file talks to UIKit on iOS and AppKit on macOS, or optionally uses a package that might not be linked. This is compile-time, like the rest of `#if`. Interviewers contrast it with `targetEnvironment` and `os()`. `canImport` is about the module graph, not “am I on a phone.” A miss is wrapping `import` in `canImport` but still using the type outside the same `#if`.



```swift
#if canImport(UIKit)
import UIKit
typealias NativeColor = UIColor
#elseif canImport(AppKit)
import AppKit
typealias NativeColor = NSColor
#endif
```


**Then they usually ask**

- How is `canImport` different from `#if os(iOS)`?
- When would a Swift package use `canImport`?
- Why must the `import` sit inside the same `#if` as the types?

</details>

<h2 id="target-environment">targetEnvironment()</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`#if targetEnvironment(simulator)`** (or `macCatalyst`) is compile-time code for how the binary is built, not which OS APIs exist. You use it for simulator-only logging, skipping a hardware feature, or Catalyst layout. It is not `#available` and not `canImport`. A device build will not contain the simulator branch at all. Interviewers ask this when someone says “ifdef simulator.” The miss is using it to detect iOS vs macOS — that is `#if os` — or thinking it is a runtime `if`.



```swift
func analyticsEndpoint() -> String {
    #if targetEnvironment(simulator)
    "https://localhost:8080"
    #else
    "https://api.example.com"
    #endif
}
```


**Then they usually ask**

- How is `targetEnvironment(simulator)` different from `#available`?
- What other `targetEnvironment` values do you actually see?
- Why can’t you toggle this at runtime?

</details>

### Senior

<h2 id="struct-memory-layout">Struct memory layout</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A struct is a contiguous bag of stored properties plus **padding** so each field meets its **alignment**. `MemoryLayout<T>.size` is the payload, `stride` is how far to the next element in an array (size rounded up to alignment), `alignment` is the address multiple. Reordering fields can shrink the stride — `Bool` then `Int64` then `Bool` wastes more than `Int64` then two `Bool`s. That matters in huge arrays and when you pass structs to C. The compiler may also use extra spare bits (for example optionals). Typical mistake: summing `MemoryLayout` of fields and expecting that to equal the struct.



```swift
struct Padded {
    var flag: Bool
    var value: Int64
}

struct Tight {
    var value: Int64
    var flag: Bool
}

MemoryLayout<Padded>.stride // often 16
MemoryLayout<Tight>.stride  // often 16 still on 64-bit, but size can differ
```


**Then they usually ask**

- Why is `stride` what an `Array` uses, not `size`?
- How does this change with `@frozen` and library evolution?
- When would you care enough to reorder properties?

</details>

<h2 id="type-erasure">Type erasure</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Type erasure** hides a concrete type behind a box that only promises a protocol (or a fixed generic parameter). You need it when callers should not see `IntStore` vs `DiskStore`, or when a protocol has `associatedtype` / `Self` and used to be illegal as a type. `AnySequence`, `AnyPublisher`, `AnyHashable`, and `AnyView` are the standard-library versions of that box. Swift’s `any Protocol` is language-level erasure; `some Protocol` is the opposite — the compiler still knows the concrete type. Interviewers want the “why,” not a memorized `AnyCancellable`. Building your own eraser is easy to get wrong: you forget to forward a method, or you erase so hard you lose `Equatable` and identity.



```swift
protocol Store {
    associatedtype Item
    func all() -> [Item]
}

struct AnyStore<Item>: Store {
    private let _all: () -> [Item]

    init<S: Store>(_ store: S) where S.Item == Item {
        _all = store.all
    }

    func all() -> [Item] { _all() }
}
```


**Then they usually ask**

- How does `any Sequence` differ from `some Sequence`?
- Why did protocols with associated types need `AnySequence` for so long?
- What do you lose when you wrap something in `AnyView`?

</details>

<h2 id="abi-stability">ABI and module stability</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**ABI stability** (Swift 5 on Apple platforms) means a Swift runtime on the OS can load binaries compiled with a newer compiler — you do not ship `libswiftCore` in every app anymore. **Module stability** is different: a client compiled against your `.swiftinterface` still links after you ship a new binary. That needs `BUILD_LIBRARY_FOR_DISTRIBUTION` and a **resilient** public API: no adding a stored property to an open class, no renaming a `public` method, `@frozen` only when you mean it. The app target does not need this. A binary XCFramework you give other teams does. Typical miss: treating “Swift is ABI-stable” as “I can change any `public` type in my SDK.”



```text
// SDK: enable library evolution
BUILD_LIBRARY_FOR_DISTRIBUTION = YES

// Safe later: add a method with a default.
// Breaking: add a stored property to an open class; change a public struct layout without @frozen care.
```


**Then they usually ask**

- ABI stability vs module stability vs source compatibility — three different promises?
- Why does `@frozen` on a public enum matter to clients?
- When do you ship source SPM instead of a resilient XCFramework?

</details>
