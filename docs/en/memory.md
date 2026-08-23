# Memory

10 cards · 7 often asked · source [memory.md](../../topics/memory.md)

### Junior

<h2 id="explain-arc">Explain ARC</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Automatic Reference Counting is the compiler inserting retain and release around class instances. The **inserts are compile time**; the **count is runtime**. Each instance stores how many strong references point at it. Creating an object starts the count at one; sharing it increments; when the last strong reference goes away the count hits zero and `deinit` runs immediately. There is no GC pause.

ARC applies only to reference types. Weak and unowned refs do not increment the count. The compiler can elide redundant retains, but the interview model is still “strong refs keep it alive.” The failure mode is a retain cycle: two objects that hold each other never reach zero, so you break one side with `weak` or `unowned`. Before ARC, Objective-C used **MRC**: you called `retain`, `release`, and `autorelease` yourself. Forget a `release` and you leak; over-release and you crash. `@autoreleasepool` is the leftover of that world — it still drains temporary objects in a tight loop.



```swift
final class Session {
    deinit { print("Session deinit") }
}

var primary: Session? = Session()  // count = 1
var mirror = primary               // count = 2
primary = nil                      // count = 1
mirror = nil                       // count = 0, deinit runs
```


**Then they usually ask**

- Does ARC run on a background thread?
- What happens to the count when you pass an object into a function?
- Is ARC compile time or runtime — what does the compiler insert vs what the process does?
- Why is `deinit` the first thing you add when hunting a leak?
- How did you manage lifetime in Objective-C without ARC?

</details>

<h2 id="swift-memory-management">How Swift handles memory</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift does not run a tracing garbage collector. Class instances, actors, and closures live on the heap and are owned by Automatic Reference Counting: each strong reference increments a count, and the object is freed the moment that count hits zero. Structs, enums, and tuples are value types — assignment copies the value (copy-on-write for `Array`, `String`, and `Dictionary`), and they are not reference-counted.

Stack versus heap is a secondary detail. Small values often sit on the stack; collections and class instances use the heap. What interviewers want is the ownership model: values copy, references share, and only the latter are counted.

Typical mistakes: saying “Swift has a GC”; claiming every type is ARC-managed; forgetting that a closure is a reference type and can keep `self` alive.



```swift
struct Point { var x: Int }

final class Box {
    var value: Int
    init(_ value: Int) { self.value = value }
}

var a = Point(x: 1)
var b = a
b.x = 2
// a.x is still 1 — value copy

let box1 = Box(1)
let box2 = box1
box2.value = 2
// box1.value is 2 — same instance
```


**Then they usually ask**

- What does ARC actually count, and what does it ignore?
- Why can a closure leak a view controller?
- When does a struct still allocate on the heap?

</details>

### Mid

<h2 id="arc-vs-gc">ARC vs garbage collection</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swift uses **Automatic Reference Counting**, not a tracing garbage collector. Each class instance has a count of how many strong references point at it. When that count hits zero, the object is deallocated immediately. There is no mark-and-sweep pause and no separate GC thread.

That is the contrast interviewers want:

| | ARC | Garbage collection |
| --- | --- | --- |
| When memory is freed | As soon as the last strong reference goes away | Later, when the collector runs |
| Cost | Increment / decrement on retain and release | Periodic heap scans, possible pauses |
| Cycles | A retain cycle keeps objects alive forever | A cycle is still garbage if nothing outside reaches it |
| What it tracks | `class` instances (reference types) | Typically the whole object graph |

Structs, enums, and tuples are value types. They are not reference-counted. Copying them copies the value (copy-on-write for types like `Array` and `String`).

The usual follow-up is cycles. Two objects that hold each other with `strong` never reach a count of zero. Break the cycle with `weak` (optional, zeroes out when the object dies) or `unowned` (non-optional, dangling if you outlive the owner). Closures capture `self` strongly by default; that is the most common leak in UIKit and SwiftUI code.

Typical mistakes: treating ARC as “Swift has a GC”; putting `weak` on a value type; using `unowned` for a view that can disappear before the closure runs; forgetting that `async` work and timers are just more strong captures.



```swift
final class Owner {
    var child: Child?
    deinit { print("Owner deinit") }
}

final class Child {
    weak var owner: Owner?
    deinit { print("Child deinit") }
}

do {
    let owner = Owner()
    let child = Child()
    owner.child = child
    child.owner = owner
}
// Both deinit. If `owner` were strong on Child, neither would.
```


**Then they usually ask**

- Weak vs unowned — when is each the right choice?
- What breaks a retain cycle in a closure?
- Why don't structs participate in ARC?
- What does `unowned(unsafe)` change?

</details>

<h2 id="memory-leak">Identify and resolve a memory leak</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A leak is memory that stays allocated after nothing still needs it. A retain cycle is the usual Swift cause. The three shapes interviewers want named: two classes holding each other strong; a **strong delegate** (protocol back to the owner); a stored closure / `Timer` / Combine sink that captures `self` while `self` owns that work. In **SwiftUI**, the usual tell is a screen that never `deinit`s after you pop it: a `Task { }` in `onAppear` that captures the view model strong, a singleton / `static` store that holds the last screen, or a `UIViewRepresentable` coordinator that points back at `self`. Other leaks: an unbounded cache, an uncancelled `Task`, a `URLSession` you never finish.

You prove it with Instruments Allocations (a graph that never returns to baseline), the Leaks instrument, the Memory Graph Debugger, or a `deinit` that never fires after you pop a screen. Fix the ownership (`weak` / `unowned`, `[weak self]`), cancel work in `deinit` or `onDisappear`, and put a bound on caches.

Interviewers want the distinction: a cycle is one shape of leak; “leak” is the symptom. Not every leak is two objects pointing at each other.



```swift
final class Ticker {
    private var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }

    func stop() {
        timer?.invalidate()
        timer = nil
    }

    private func tick() {}

    deinit {
        stop()
        print("Ticker deinit")
    }
}
```


**Then they usually ask**

- How is a leak different from a retain cycle?
- “Do not change the public API” — which keyword do you still get to add?
- What does a rising Allocations graph after repeated push/pop tell you?
- Why can a singleton be a leak even with no cycle?
- Name the three most common retain-cycle shapes on iOS.
- A SwiftUI screen never deinits after pop — what do you check first?
- App was fine at launch and sluggish 15 minutes later — what accumulated?
- Leak vs zombie — which tool shows each?
- Leaked ViewModel still subscribed — a singleton actor runs the tap twice. Which tool shows two instances?
- Why is “Swift 6 compiles clean” not enough if instance counts keep climbing?

</details>

<h2 id="retain-cycle">Identify and resolve a retain cycle</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A retain cycle is a loop of strong references — A owns B and B owns A — so neither count can reach zero and `deinit` never runs. The shapes that show up in interviews are a parent holding a child that holds the parent, a `strong` delegate, and a stored closure (or `Timer`, Combine sink, `Task`) that captures `self` while `self` owns that work.

You confirm it when `deinit` stays silent after you dismiss a screen, or when the Memory Graph Debugger draws a loop. Break the cycle by making the back-reference `weak` or `unowned`, or by capturing `[weak self]` and using optional chaining.

Typical mistakes: marking everything `weak` without finding the loop; using `unowned` when the object can die first; missing that `Timer` and `NotificationCenter` retain their target.



```swift
final class ProfileLoader {
    var onFinish: (() -> Void)?
    var name = "Ada"

    func load() {
        onFinish = { [weak self] in
            print(self?.name ?? "gone")
        }
    }

    deinit { print("ProfileLoader deinit") }
}
```


**Then they usually ask**

- Why is `[weak self]` not always enough by itself?
- When would you choose `[unowned self]` in a closure?
- How do you spot a cycle that does not involve a closure?

</details>

<h2 id="autoreleasepool">autoreleasepool</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Objective-C objects can be **autoreleased**: the retain is handed to a pool and drained later. The **main thread’s** outer pool drains at the end of each **RunLoop** turn (after the current event / timer / source). A GCD worker has a pool per work item in many cases, but a tight loop on the same item still piles up. `autoreleasepool { }` creates a nested pool and drains it when the brace ends. Pure Swift value types do not use this. You still see it when bridging to Foundation (`NSString`, `NSData`, `UIImage`). Typical mistake: wrapping random Swift code in a pool and expecting ARC to change, or never pooling a loop that creates `UIImage(data:)` a thousand times.



```swift
func thumbnails(from data: [Data]) -> [UIImage] {
    data.compactMap { bytes in
        autoreleasepool {
            UIImage(data: bytes)
        }
    }
}
```


**Then they usually ask**

- When does the main run loop drain the outer pool?
- Why is this a non-issue for `[UInt8]` but a real one for `UIImage`?
- How do you confirm the pool is the leak with Allocations?

</details>

<h2 id="weak-vs-unowned">weak vs unowned</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Both skip the retain count, so they cannot form a cycle. `weak` is an optional that becomes `nil` when the object deallocates — safe when the lifetime is unknown. `unowned` is non-optional: you assert the object outlives this reference. If it doesn't, you crash (`unowned` traps; `unowned(unsafe)` is undefined).

Reach for `weak` on delegates, view controllers captured by network or animation callbacks, and anything that might dismiss first. Reach for `unowned` when the relationship is structural — a child that cannot exist without its parent, a credit card that cannot exist without its customer, a closure that only runs while you still own `self`. If you read `unowned` after the owner is gone, the process traps. That is why “always `unowned self` in closures” is bad advice.

Typical mistakes: `unowned` on a screen that can disappear before an async callback returns; putting `weak` on a struct (it will not compile); treating the two as interchangeable ways to silence a warning.



```swift
protocol FormDelegate: AnyObject {
    func formDidSubmit()
}

final class Form {
    weak var delegate: FormDelegate?  // owner may go away
}

final class Field {
    unowned let form: Form            // Field is created by Form, dies with it
    init(form: Form) { self.form = form }
}
```


**Then they usually ask**

- What happens if you read an `unowned` reference after the object is gone?
- Why must a `weak` property be `var` and optional?
- When is `unowned(unsafe)` ever justified?

</details>

<h2 id="deep-vs-shallow">Deep vs shallow copy</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **shallow** copy duplicates the container and **shares** the elements (same object identities). A **deep** copy duplicates the graph so mutating a child does not change the original. `Array` of structs copies values (deep at that level). `Array` of classes copies the array, not the objects. `copy` on `NSArray` is shallow; `NSArray` of `NSString` still shares the strings (usually fine because they are immutable). Typical miss: `array.map { $0 }` on classes and calling it a deep copy.



```swift
class Box { var n = 0 }
let a = [Box()]
let shallow = a // same Box
let deep = a.map { b in Box(); /* copy fields */ }
```


**Then they usually ask**

- `copy` vs `mutableCopy` on `NSArray`?
- How does CoW change this answer for `Array<Int>`?
- When must a copy be deep for thread safety?

</details>

<h2 id="stack-vs-heap">Stack vs heap</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The **stack** is per-thread scratch: frames push and pop in LIFO as functions enter and return. Locals and return addresses live there. The **heap** is the process-wide pool for dynamic lifetime — `malloc` / ARC objects. **Do not say “structs are on the stack, classes on the heap.”** A class instance is on the heap; a struct may be on the stack, inlined in a class, or heap-promoted (escaping closure, `Array` buffer). ObjC objects are heap objects. Typical miss: using stack-vs-heap as a synonym for value vs reference.



```swift
func demo() {
    var n = 1              // typically stack
    let view = UIView()    // the UIView is on the heap; `view` is a stack pointer
}
```


**Then they usually ask**

- Why can a large `Array` live on the heap even though `Array` is a struct?
- What happens to stack memory when the function returns?
- How does ARC interact with heap objects only?
- Where does a struct property of a class live?

</details>

### Senior

<h2 id="side-tables">Side tables</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A Swift class instance starts as a small heap object: a metadata pointer plus an inline refcount. The first time you need extra bookkeeping — a **weak** reference, an unowned refcount that does not fit, or some ObjC interop — the runtime allocates a **side table** next to the object. Weak refs point at that table, not at the object, so they can go `nil` after `deinit` without dangling. That is why `weak` is slower and larger than `unowned`: you pay for the table and an extra hop. Interviewers who go deep want this picture, not “weak is optional.” You do not manage side tables yourself; you just know why a type that is only ever `unowned` stays cheaper.



```swift
final class Node {
    weak var parent: Node? // first weak ref can allocate a side table
    var child: Node?
}
```


**Then they usually ask**

- Why can `unowned` avoid a side table that `weak` cannot?
- Why do people say `weak` is slower than `strong`?
- What happens to weak refs during `deinit`?
- How does this show up in Allocations if you create millions of weakly pointed objects?

</details>
