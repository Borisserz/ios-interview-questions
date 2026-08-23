# Objective-C runtime

18 cards · 6 often asked · source [objc-runtime.md](../../topics/objc-runtime.md)

### Junior

<h2 id="nserror">NSError</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`NSError` is a Cocoa error object: **domain** (string), **code** (int), **userInfo** (dictionary — localized description, underlying error, failing URL). ObjC APIs take `NSError **` out-parameters. Swift imports many of them as `throws` and you still read `error as NSError` for the code. Prefer a typed Swift `Error` in new APIs; bridge at the boundary. Typical miss: checking only `localizedDescription`, or ignoring `NSUnderlyingErrorKey`.



```swift
do {
    try data.write(to: url)
} catch {
    let ns = error as NSError
    print(ns.domain, ns.code, ns.userInfo[NSUnderlyingErrorKey] as Any)
}
```


**Then they usually ask**

- Domain + code vs a Swift enum `Error`?
- What belongs in `userInfo`?
- How does `try` map an `NSError **` API?

</details>

<h2 id="iskindof-vs-ismember">isKindOfClass vs isMemberOfClass</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`isKindOfClass:` is **this class or a subclass**. `isMemberOfClass:` is **exactly** that class. `isKindOfClass:[UIView class]` is true for `UIButton`. `isMemberOfClass:` is not. Prefer `isKindOfClass` or a Swift `is` / `as?`. Exact-class checks break when UIKit gives you a private subclass. Typical miss: `isMemberOfClass` in a table-view helper that later gets a header subclass.



```objc
[button isKindOfClass:[UIView class]];    // YES
[button isMemberOfClass:[UIView class]];  // NO
```


**Then they usually ask**

- How does Swift `is` map to these?
- Why is an exact-class check brittle with system types?
- `conformsToProtocol:` vs `isKindOfClass:`?

</details>

<h2 id="nil-null">nil, Nil, NULL, NSNull</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`nil`** is an ObjC object pointer (message to `nil` is a no-op). **`Nil`** is a class pointer. **`NULL`** is a C pointer (`void *`). **`NSNull`** is a real object that means “JSON null / missing in a collection” — you cannot put `nil` in an `NSArray`. Swift `nil` is `Optional.none` and is a different model. Typical miss: inserting `nil` into a dictionary and crashing, or treating `NSNull` as `nil` without a check.



```objc
id obj = nil;
NSLog(@"%@", obj);           // (null), no crash
NSArray *a = @[ [NSNull null] ];
```


**Then they usually ask**

- Why does JSON need `NSNull`?
- `nil` messaging vs Swift optional chaining?
- `Nil` vs `nil` when you send a class method?

</details>

### Mid

<h2 id="objc-messaging">Messaging and nil</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`[obj foo]` compiles to `objc_msgSend(obj, @selector(foo), ...)`. The runtime looks up the selector in the class’s method list (and the superclass chain), then jumps to the IMP. **A message to `nil` is a no-op** and returns zero / `nil` — that is not a crash. Swift optional chaining is the cousin. Dynamic dispatch is why categories, swizzling, and KVO work. Typical mistake: “ObjC is just C with objects” without `objc_msgSend`.



```objc
id obj = nil;
NSString *name = [obj description]; // nil, no crash
```


**Then they usually ask**

- What is a selector vs an IMP?
- How does the runtime find a class method vs an instance method?
- What does `_objc_msgForward` do?

</details>

<h2 id="runloop">RunLoop</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A RunLoop is an event loop tied to a **thread**: it waits for sources (touches, ports, timers, GCD main-queue hops) and runs them. The main thread has one that UIKit starts for you. A background thread has none unless you call `[[NSRunLoop currentRunLoop] run]`. **Modes** filter which sources fire. `NSDefaultRunLoopMode` is the usual one; `UITrackingRunLoopMode` is what scrolling uses. `NSRunLoopCommonModes` includes both. Typical mistake: starting a `Timer` on the main run loop in default mode and wondering why it pauses during a scroll.



```swift
RunLoop.main.add(timer, forMode: .common)
```


**Then they usually ask**

- RunLoop vs a GCD queue?
- What happens if a background thread has no RunLoop and you schedule a `Timer`?
- How is a RunLoop implemented at a high level (sleep + sources)?
- Source0 vs source1 — who wakes the thread?
- How do you keep a background thread alive without a busy loop?

</details>

<h2 id="timer-runloop">Timer pauses while scrolling</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`Timer.scheduledTimer` adds the timer to the **current** RunLoop in `.default`. While a `UIScrollView` tracks, the main RunLoop is in `.tracking`, so default-mode timers do not fire. Fix: add the timer to `.common`, or use a `CADisplayLink`, or a GCD timer (`DispatchSourceTimer`) which is not mode-based. `scheduledTimer` on a background thread also fails unless that thread runs a RunLoop. Typical miss: “the timer is broken” without naming modes.



```swift
let timer = Timer(timeInterval: 1, repeats: true) { _ in tick() }
RunLoop.main.add(timer, forMode: .common)
```


**Then they usually ask**

- `.common` vs adding the timer twice (default + tracking)?
- `CADisplayLink` vs `Timer` for a clock on a scrolling screen?
- Why does `Task.sleep` not have this problem?
- How would you fire a timer every minute while the app is backgrounded?

</details>

<h2 id="dynamic">@dynamic</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`@dynamic` tells the compiler: **do not synthesize** getter/setter; they will exist at runtime (Core Data accessors, a scripted property). `@synthesize` (or the modern default) creates the ivar and methods. In Swift the cousin is `@objc dynamic` — required for KVO on a Swift property. Typical miss: marking a normal stored property `@dynamic` and crashing on first access.



```objc
@interface Note : NSManagedObject
@property (nonatomic, copy) NSString *title;
@end
@implementation Note
@dynamic title; // Core Data provides the accessors
@end
```


**Then they usually ask**

- `@dynamic` vs `@synthesize` vs the Swift default?
- Why does KVO need `dynamic` in Swift?
- What happens if the runtime never adds the method?

</details>

<h2 id="category-vs-extension">Category vs class extension</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **category** (`@interface Foo (Bar)`) can be in another file and can target classes you do not compile (`NSString`). It adds methods only — no ivars. A **class extension** (`@interface Foo ()`, sometimes called an anonymous category) must see the class’s `@implementation` at compile time. It can declare extra ivars, redeclare a `readonly` property as `readwrite`, and hide private methods. You cannot write an extension on `NSString`. Typical miss: calling a Swift `extension` on `String` a class extension in the ObjC sense.



```objc
// Foo.m — class extension, private storage
@interface Foo ()
@property (nonatomic, copy) NSString *secret;
@end
```


**Then they usually ask**

- Why can an extension add an ivar when a category cannot?
- Where do you put a private `readwrite` for a public `readonly`?
- How does this map to Swift `private` in the same file?

</details>

<h2 id="category-vs-inheritance">Category vs inheritance</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **category** (Swift: extension) adds methods to an existing class you may not own. **Inheritance** creates a new type and can add ivars and override behavior. Use a category for a small helper (`UIColor.brand`). Use a subclass when you need state or a different `drawRect`. Categories cannot add ivars (use associated objects, carefully). Two categories that implement the same method is undefined. Typical miss: subclassing `NSString` or stuffing app logic into a `UIViewController` category.



```objc
@interface UIColor (Brand)
+ (UIColor *)brand;
@end
```


**Then they usually ask**

- When is a wrapper type better than a category?
- Why is overriding via a category dangerous?
- Swift extension vs ObjC category — associated types?

</details>

<h2 id="underscore-vs-self">_ vs self.</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

In ObjC, `_title` is the **ivar**; `self.title` goes through the **accessor** (KVO, `copy`, custom setter, atomic lock). Assigning `_title = x` skips all of that. Inside `init` and `dealloc` you usually touch the ivar so you do not call an override or trigger KVO on a half-built object. Everywhere else, prefer the property. Typical miss: `_delegate = d` and wondering why the weak setter never ran.



```objc
- (void)setTitle:(NSString *)title {
    _title = [title copy];
}
- (instancetype)init {
    if ((self = [super init])) { _title = @""; } // ivar in init
    return self;
}
```


**Then they usually ask**

- Why avoid `self.foo =` in `init` / `dealloc`?
- How does this map to Swift (`self.title` vs nothing)?
- What does a custom setter change about `self.`?

</details>

<h2 id="ivar-in-category">ivar in a category</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

You **cannot** add a stored ivar to a compiled class from a category — the instance layout is already fixed. The workaround is **associated objects** (`objc_setAssociatedObject`) with a static key and a memory policy (`OBJC_ASSOCIATION_RETAIN`). That is how some libraries fake stored properties on `UIView`. Cost: extra table lookup, easy leaks if you `RETAIN` a view that retains you. Prefer a subclass or a side table you own. Typical miss: `@property` in a category and assuming it synthesized storage.



```objc
static const void *Key = &Key;
objc_setAssociatedObject(self, Key, name, OBJC_ASSOCIATION_COPY_NONATOMIC);
NSString *name = objc_getAssociatedObject(self, Key);
```


**Then they usually ask**

- Why is layout fixed after `objc_registerClassPair`?
- Associated object vs a subclass ivar?
- What retain policy do you use for a `weak`-like association?

</details>

<h2 id="unrecognized-selector">unrecognized selector</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The runtime throws when it cannot find an IMP and **message forwarding** also fails: `doesNotRecognizeSelector:`. Before that it asks `resolveInstanceMethod`, then `forwardingTargetForSelector`, then `forwardInvocation`. That pipeline is how some proxies and mock objects work. In Swift you usually see this as a crash from an `@objc` selector you renamed, or a storyboard action that no longer exists. Typical miss: blaming ARC.



```objc
[self performSelector:@selector(nameThatDoesNotExist)];
// -[AppDelegate nameThatDoesNotExist]: unrecognized selector sent to instance
```


**Then they usually ask**

- Order of `resolveInstanceMethod` vs forwarding?
- Why can a Swift method be missing at runtime?
- How do you debug this in lldb (`po`, `bt`)?

</details>

<h2 id="synthesize">@synthesize</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`@synthesize title = _title;` tells the compiler to **emit the getter/setter and the ivar**. Modern ObjC does this by default for `@property`. You still write it when you implement one accessor yourself and want the other synthesized, or when you need a non-standard ivar name. `@dynamic` is the opposite: no synthesis, accessors come at runtime. Typical miss: writing both a custom setter and `@synthesize` and then wondering which ivar you assigned.



```objc
@implementation Person
@synthesize name = _name; // default today; needed if you write one accessor
@end
```


**Then they usually ask**

- When do you still need `@synthesize` in 2026?
- `@synthesize` vs `@dynamic` vs Swift stored properties?
- What ivar name do you get if you omit `= _name`?

</details>

### Senior

<h2 id="load-vs-initialize">+load vs +initialize</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`+load` runs **as the image is mapped**, before `main`, once per class and per category that implements it — even if you never send a message. It is why China loops treat it as a launch-time tax: every `+load` is pre-main work, and categories each get their own. `+initialize` is lazy: the first time that class (or a subclass that does not override it) receives a message. Prefer `+initialize` or a Swift `static` you control; keep `+load` for swizzling you must install before any client code runs, and make it tiny. Typical miss: doing I/O or starting a thread in `+load`, or assuming a category’s `+initialize` runs (it does not — only `+load` is special for categories).



```objc
+ (void)load { /* once at image load — keep empty if you can */ }
+ (void)initialize {
    if (self == [MyClass class]) { /* first message, lazy */ }
}
```


**Then they usually ask**

- Why does a category `+load` run but a category `+initialize` does not?
- How do you see `+load` time in `DYLD_PRINT_STATISTICS`?
- Where should swizzling live in 2026 if you refuse `+load`?

</details>

<h2 id="mach-o">Mach-O and dyld</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The app binary is **Mach-O**: a header, load commands, then segments (`__TEXT`, `__DATA`, …) split into sections. At launch **dyld** maps those images, **rebases** interior pointers (ASLR), **binds** external symbols, sets up ObjC (selectors, categories), then runs initializers (`+load`, C++ statics). More dylibs and more ObjC metadata mean more page-ins before `main`. `DYLD_PRINT_STATISTICS` prints the pre-main split. Merge first-party dynamic frameworks, prefer static where you can, and keep `+load` empty. Typical miss: “launch is `didFinishLaunching`” and never naming rebase/bind.



```text
DYLD_PRINT_STATISTICS=1
# dylib loading / rebase+bind / ObjC setup / initializer
```


**Then they usually ask**

- Rebase vs bind — which one grows with ASLR vs imported symbols?
- Why does a pile of dynamic pods hurt cold start more than the same code statically linked?
- What does a Link Map tell you that dyld stats do not?

</details>

<h2 id="isa">isa and object layout</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An ObjC object is a heap blob: an **`isa`** pointer, then the ivars of the class and its superclasses. `isa` points at the **class object**, which holds the method list; the class’s `isa` points at the metaclass (class methods). KVO and some associated-object tricks replace `isa` with a dynamically created subclass. You cannot add an ivar to a compiled class at runtime (layout is fixed); you can add one when you create a class with `objc_allocateClassPair` before `objc_registerClassPair`. Typical miss: “`isa` points at the superclass.”



```objc
NSLog(@"%@", NSStringFromClass(object_getClass(obj)));
```


**Then they usually ask**

- Class object vs metaclass?
- Why can you add a method at runtime but not an ivar?
- How does this enable KVO?

</details>

<h2 id="resident-thread">Keep-alive thread</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A background `NSThread` **exits when its start block returns**. To keep it for timers, ports, or a serial “socket thread,” you must run a **RunLoop** on it and give that loop a source — usually an `NSPort` or a `Timer`. `run` with no source returns immediately. `while` + `runMode:beforeDate:` is the controllable form so you can `CFRunLoopStop`. GCD queues do not need this; a `DispatchSource` lives on the workqueue. Typical miss: `[[NSThread alloc] init]` plus `scheduledTimer` and wondering why the timer never fires.



```objc
[NSThread detachNewThreadWithBlock:^{
    [[NSRunLoop currentRunLoop] addPort:[NSPort port] forMode:NSDefaultRunLoopMode];
    [[NSRunLoop currentRunLoop] run];
}];
```


**Then they usually ask**

- Why does `run` return if you forget the port?
- GCD timer vs RunLoop timer on that thread?
- When is a dedicated thread the wrong tool in 2026?

</details>

<h2 id="method-swizzling">Method swizzling</h2>

<code>Senior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Swizzling **swaps two IMPs** for a selector (`method_exchangeImplementations`) so existing callers hit your code. Analytics SDKs and some test doubles still do this. It is global, order-dependent, and breaks when two libraries swizzle the same method. Prefer a wrapper, a subclass, or a `UIViewController` hook you own. If you must, swizzle in `+load` / a one-time `static` and always call the original. Typical miss: swizzling in Swift without `@objc dynamic`, or forgetting the original IMP and recursing.



```objc
static void swizzle(Class c, SEL a, SEL b) {
    method_exchangeImplementations(class_getInstanceMethod(c, a),
                                   class_getInstanceMethod(c, b));
}
```


**Then they usually ask**

- `+load` vs `+initialize` for installing a swizzle?
- Why is this a last resort next to a delegate?
- How does KVO’s isa-swizzle differ?

</details>
