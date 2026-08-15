# Memory

- [ARC vs garbage collection](#arc-vs-gc)

## ARC vs garbage collection {#arc-vs-gc}

- Level: Mid
- Frequency: High

### Answer

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

### Example

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

### Follow-ups

- Weak vs unowned — when is each the right choice?
- What breaks a retain cycle in a closure?
- Why don't structs participate in ARC?
- What does `unowned(unsafe)` change?
