# Objective-C runtime

Still asked on many CIS / China loops, and anywhere a codebase still talks to UIKit through ObjC.

- [Messaging and nil](#objc-messaging)
- [unrecognized selector](#unrecognized-selector)
- [isa and object layout](#isa)
- [RunLoop](#runloop)
- [Timer pauses while scrolling](#timer-runloop)
- [Method swizzling](#method-swizzling)
- [@dynamic](#dynamic)
- [NSError](#nserror)
- [_ vs self.](#underscore-vs-self)
- [nil, Nil, NULL, NSNull](#nil-null)
- [Category vs inheritance](#category-vs-inheritance)
- [Category vs class extension](#category-vs-extension)
- [@synthesize](#synthesize)
- [ivar in a category](#ivar-in-category)
- [isKindOfClass vs isMemberOfClass](#iskindof-vs-ismember)
- [+load vs +initialize](#load-vs-initialize)
- [Keep-alive thread](#resident-thread)
- [Mach-O and dyld](#mach-o)

## Messaging and nil {#objc-messaging}

- Level: Mid
- Frequency: High

### Answer

`[obj foo]` compiles to `objc_msgSend(obj, @selector(foo), ...)`. The runtime looks up the selector in the class’s method list (and the superclass chain), then jumps to the IMP. **A message to `nil` is a no-op** and returns zero / `nil` — that is not a crash. Swift optional chaining is the cousin. Dynamic dispatch is why categories, swizzling, and KVO work. Typical mistake: “ObjC is just C with objects” without `objc_msgSend`.

### Example

```objc
id obj = nil;
NSString *name = [obj description]; // nil, no crash
```

### Follow-ups

- What is a selector vs an IMP?
- How does the runtime find a class method vs an instance method?
- What does `_objc_msgForward` do?

## unrecognized selector {#unrecognized-selector}

- Level: Mid
- Frequency: Medium

### Answer

The runtime throws when it cannot find an IMP and **message forwarding** also fails: `doesNotRecognizeSelector:`. Before that it asks `resolveInstanceMethod`, then `forwardingTargetForSelector`, then `forwardInvocation`. That pipeline is how some proxies and mock objects work. In Swift you usually see this as a crash from an `@objc` selector you renamed, or a storyboard action that no longer exists. Typical miss: blaming ARC.

### Example

```objc
[self performSelector:@selector(nameThatDoesNotExist)];
// -[AppDelegate nameThatDoesNotExist]: unrecognized selector sent to instance
```

### Follow-ups

- Order of `resolveInstanceMethod` vs forwarding?
- Why can a Swift method be missing at runtime?
- How do you debug this in lldb (`po`, `bt`)?

## isa and object layout {#isa}

- Level: Senior
- Frequency: High

### Answer

An ObjC object is a heap blob: an **`isa`** pointer, then the ivars of the class and its superclasses. `isa` points at the **class object**, which holds the method list; the class’s `isa` points at the metaclass (class methods). KVO and some associated-object tricks replace `isa` with a dynamically created subclass. You cannot add an ivar to a compiled class at runtime (layout is fixed); you can add one when you create a class with `objc_allocateClassPair` before `objc_registerClassPair`. Typical miss: “`isa` points at the superclass.”

### Example

```objc
NSLog(@"%@", NSStringFromClass(object_getClass(obj)));
```

### Follow-ups

- Class object vs metaclass?
- Why can you add a method at runtime but not an ivar?
- How does this enable KVO?

## RunLoop {#runloop}

- Level: Mid
- Frequency: High

### Answer

A RunLoop is an event loop tied to a **thread**: it waits for sources (touches, ports, timers, GCD main-queue hops) and runs them. The main thread has one that UIKit starts for you. A background thread has none unless you call `[[NSRunLoop currentRunLoop] run]`. **Modes** filter which sources fire. `NSDefaultRunLoopMode` is the usual one; `UITrackingRunLoopMode` is what scrolling uses. `NSRunLoopCommonModes` includes both. Typical mistake: starting a `Timer` on the main run loop in default mode and wondering why it pauses during a scroll.

### Example

```swift
RunLoop.main.add(timer, forMode: .common)
```

### Follow-ups

- RunLoop vs a GCD queue?
- What happens if a background thread has no RunLoop and you schedule a `Timer`?
- How is a RunLoop implemented at a high level (sleep + sources)?
- Source0 vs source1 — who wakes the thread?
- How do you keep a background thread alive without a busy loop?

## Timer pauses while scrolling {#timer-runloop}

- Level: Mid
- Frequency: High

### Answer

`Timer.scheduledTimer` adds the timer to the **current** RunLoop in `.default`. While a `UIScrollView` tracks, the main RunLoop is in `.tracking`, so default-mode timers do not fire. Fix: add the timer to `.common`, or use a `CADisplayLink`, or a GCD timer (`DispatchSourceTimer`) which is not mode-based. `scheduledTimer` on a background thread also fails unless that thread runs a RunLoop. Typical miss: “the timer is broken” without naming modes.

### Example

```swift
let timer = Timer(timeInterval: 1, repeats: true) { _ in tick() }
RunLoop.main.add(timer, forMode: .common)
```

### Follow-ups

- `.common` vs adding the timer twice (default + tracking)?
- `CADisplayLink` vs `Timer` for a clock on a scrolling screen?
- Why does `Task.sleep` not have this problem?
- How would you fire a timer every minute while the app is backgrounded?

## Method swizzling {#method-swizzling}

- Level: Senior
- Frequency: Medium

### Answer

Swizzling **swaps two IMPs** for a selector (`method_exchangeImplementations`) so existing callers hit your code. Analytics SDKs and some test doubles still do this. It is global, order-dependent, and breaks when two libraries swizzle the same method. Prefer a wrapper, a subclass, or a `UIViewController` hook you own. If you must, swizzle in `+load` / a one-time `static` and always call the original. Typical miss: swizzling in Swift without `@objc dynamic`, or forgetting the original IMP and recursing.

### Example

```objc
static void swizzle(Class c, SEL a, SEL b) {
    method_exchangeImplementations(class_getInstanceMethod(c, a),
                                   class_getInstanceMethod(c, b));
}
```

### Follow-ups

- `+load` vs `+initialize` for installing a swizzle?
- Why is this a last resort next to a delegate?
- How does KVO’s isa-swizzle differ?

## @dynamic {#dynamic}

- Level: Mid
- Frequency: Medium

### Answer

`@dynamic` tells the compiler: **do not synthesize** getter/setter; they will exist at runtime (Core Data accessors, a scripted property). `@synthesize` (or the modern default) creates the ivar and methods. In Swift the cousin is `@objc dynamic` — required for KVO on a Swift property. Typical miss: marking a normal stored property `@dynamic` and crashing on first access.

### Example

```objc
@interface Note : NSManagedObject
@property (nonatomic, copy) NSString *title;
@end
@implementation Note
@dynamic title; // Core Data provides the accessors
@end
```

### Follow-ups

- `@dynamic` vs `@synthesize` vs the Swift default?
- Why does KVO need `dynamic` in Swift?
- What happens if the runtime never adds the method?

## NSError {#nserror}

- Level: Junior
- Frequency: Medium

### Answer

`NSError` is a Cocoa error object: **domain** (string), **code** (int), **userInfo** (dictionary — localized description, underlying error, failing URL). ObjC APIs take `NSError **` out-parameters. Swift imports many of them as `throws` and you still read `error as NSError` for the code. Prefer a typed Swift `Error` in new APIs; bridge at the boundary. Typical miss: checking only `localizedDescription`, or ignoring `NSUnderlyingErrorKey`.

### Example

```swift
do {
    try data.write(to: url)
} catch {
    let ns = error as NSError
    print(ns.domain, ns.code, ns.userInfo[NSUnderlyingErrorKey] as Any)
}
```

### Follow-ups

- Domain + code vs a Swift enum `Error`?
- What belongs in `userInfo`?
- How does `try` map an `NSError **` API?

## _ vs self. {#underscore-vs-self}

- Level: Mid
- Frequency: Medium

### Answer

In ObjC, `_title` is the **ivar**; `self.title` goes through the **accessor** (KVO, `copy`, custom setter, atomic lock). Assigning `_title = x` skips all of that. Inside `init` and `dealloc` you usually touch the ivar so you do not call an override or trigger KVO on a half-built object. Everywhere else, prefer the property. Typical miss: `_delegate = d` and wondering why the weak setter never ran.

### Example

```objc
- (void)setTitle:(NSString *)title {
    _title = [title copy];
}
- (instancetype)init {
    if ((self = [super init])) { _title = @""; } // ivar in init
    return self;
}
```

### Follow-ups

- Why avoid `self.foo =` in `init` / `dealloc`?
- How does this map to Swift (`self.title` vs nothing)?
- What does a custom setter change about `self.`?

## nil, Nil, NULL, NSNull {#nil-null}

- Level: Junior
- Frequency: Medium

### Answer

**`nil`** is an ObjC object pointer (message to `nil` is a no-op). **`Nil`** is a class pointer. **`NULL`** is a C pointer (`void *`). **`NSNull`** is a real object that means “JSON null / missing in a collection” — you cannot put `nil` in an `NSArray`. Swift `nil` is `Optional.none` and is a different model. Typical miss: inserting `nil` into a dictionary and crashing, or treating `NSNull` as `nil` without a check.

### Example

```objc
id obj = nil;
NSLog(@"%@", obj);           // (null), no crash
NSArray *a = @[ [NSNull null] ];
```

### Follow-ups

- Why does JSON need `NSNull`?
- `nil` messaging vs Swift optional chaining?
- `Nil` vs `nil` when you send a class method?

## Category vs inheritance {#category-vs-inheritance}

- Level: Mid
- Frequency: Medium

### Answer

A **category** (Swift: extension) adds methods to an existing class you may not own. **Inheritance** creates a new type and can add ivars and override behavior. Use a category for a small helper (`UIColor.brand`). Use a subclass when you need state or a different `drawRect`. Categories cannot add ivars (use associated objects, carefully). Two categories that implement the same method is undefined. Typical miss: subclassing `NSString` or stuffing app logic into a `UIViewController` category.

### Example

```objc
@interface UIColor (Brand)
+ (UIColor *)brand;
@end
```

### Follow-ups

- When is a wrapper type better than a category?
- Why is overriding via a category dangerous?
- Swift extension vs ObjC category — associated types?

## Category vs class extension {#category-vs-extension}

- Level: Mid
- Frequency: Medium

### Answer

A **category** (`@interface Foo (Bar)`) can be in another file and can target classes you do not compile (`NSString`). It adds methods only — no ivars. A **class extension** (`@interface Foo ()`, sometimes called an anonymous category) must see the class’s `@implementation` at compile time. It can declare extra ivars, redeclare a `readonly` property as `readwrite`, and hide private methods. You cannot write an extension on `NSString`. Typical miss: calling a Swift `extension` on `String` a class extension in the ObjC sense.

### Example

```objc
// Foo.m — class extension, private storage
@interface Foo ()
@property (nonatomic, copy) NSString *secret;
@end
```

### Follow-ups

- Why can an extension add an ivar when a category cannot?
- Where do you put a private `readwrite` for a public `readonly`?
- How does this map to Swift `private` in the same file?

## @synthesize {#synthesize}

- Level: Mid
- Frequency: Low

### Answer

`@synthesize title = _title;` tells the compiler to **emit the getter/setter and the ivar**. Modern ObjC does this by default for `@property`. You still write it when you implement one accessor yourself and want the other synthesized, or when you need a non-standard ivar name. `@dynamic` is the opposite: no synthesis, accessors come at runtime. Typical miss: writing both a custom setter and `@synthesize` and then wondering which ivar you assigned.

### Example

```objc
@implementation Person
@synthesize name = _name; // default today; needed if you write one accessor
@end
```

### Follow-ups

- When do you still need `@synthesize` in 2026?
- `@synthesize` vs `@dynamic` vs Swift stored properties?
- What ivar name do you get if you omit `= _name`?

## ivar in a category {#ivar-in-category}

- Level: Mid
- Frequency: Medium

### Answer

You **cannot** add a stored ivar to a compiled class from a category — the instance layout is already fixed. The workaround is **associated objects** (`objc_setAssociatedObject`) with a static key and a memory policy (`OBJC_ASSOCIATION_RETAIN`). That is how some libraries fake stored properties on `UIView`. Cost: extra table lookup, easy leaks if you `RETAIN` a view that retains you. Prefer a subclass or a side table you own. Typical miss: `@property` in a category and assuming it synthesized storage.

### Example

```objc
static const void *Key = &Key;
objc_setAssociatedObject(self, Key, name, OBJC_ASSOCIATION_COPY_NONATOMIC);
NSString *name = objc_getAssociatedObject(self, Key);
```

### Follow-ups

- Why is layout fixed after `objc_registerClassPair`?
- Associated object vs a subclass ivar?
- What retain policy do you use for a `weak`-like association?

## isKindOfClass vs isMemberOfClass {#iskindof-vs-ismember}

- Level: Junior
- Frequency: Medium

### Answer

`isKindOfClass:` is **this class or a subclass**. `isMemberOfClass:` is **exactly** that class. `isKindOfClass:[UIView class]` is true for `UIButton`. `isMemberOfClass:` is not. Prefer `isKindOfClass` or a Swift `is` / `as?`. Exact-class checks break when UIKit gives you a private subclass. Typical miss: `isMemberOfClass` in a table-view helper that later gets a header subclass.

### Example

```objc
[button isKindOfClass:[UIView class]];    // YES
[button isMemberOfClass:[UIView class]];  // NO
```

### Follow-ups

- How does Swift `is` map to these?
- Why is an exact-class check brittle with system types?
- `conformsToProtocol:` vs `isKindOfClass:`?

## +load vs +initialize {#load-vs-initialize}

- Level: Senior
- Frequency: High

### Answer

`+load` runs **as the image is mapped**, before `main`, once per class and per category that implements it — even if you never send a message. It is why China loops treat it as a launch-time tax: every `+load` is pre-main work, and categories each get their own. `+initialize` is lazy: the first time that class (or a subclass that does not override it) receives a message. Prefer `+initialize` or a Swift `static` you control; keep `+load` for swizzling you must install before any client code runs, and make it tiny. Typical miss: doing I/O or starting a thread in `+load`, or assuming a category’s `+initialize` runs (it does not — only `+load` is special for categories).

### Example

```objc
+ (void)load { /* once at image load — keep empty if you can */ }
+ (void)initialize {
    if (self == [MyClass class]) { /* first message, lazy */ }
}
```

### Follow-ups

- Why does a category `+load` run but a category `+initialize` does not?
- How do you see `+load` time in `DYLD_PRINT_STATISTICS`?
- Where should swizzling live in 2026 if you refuse `+load`?

## Keep-alive thread {#resident-thread}

- Level: Senior
- Frequency: Medium

### Answer

A background `NSThread` **exits when its start block returns**. To keep it for timers, ports, or a serial “socket thread,” you must run a **RunLoop** on it and give that loop a source — usually an `NSPort` or a `Timer`. `run` with no source returns immediately. `while` + `runMode:beforeDate:` is the controllable form so you can `CFRunLoopStop`. GCD queues do not need this; a `DispatchSource` lives on the workqueue. Typical miss: `[[NSThread alloc] init]` plus `scheduledTimer` and wondering why the timer never fires.

### Example

```objc
[NSThread detachNewThreadWithBlock:^{
    [[NSRunLoop currentRunLoop] addPort:[NSPort port] forMode:NSDefaultRunLoopMode];
    [[NSRunLoop currentRunLoop] run];
}];
```

### Follow-ups

- Why does `run` return if you forget the port?
- GCD timer vs RunLoop timer on that thread?
- When is a dedicated thread the wrong tool in 2026?

## Mach-O and dyld {#mach-o}

- Level: Senior
- Frequency: High

### Answer

The app binary is **Mach-O**: a header, load commands, then segments (`__TEXT`, `__DATA`, …) split into sections. At launch **dyld** maps those images, **rebases** interior pointers (ASLR), **binds** external symbols, sets up ObjC (selectors, categories), then runs initializers (`+load`, C++ statics). More dylibs and more ObjC metadata mean more page-ins before `main`. `DYLD_PRINT_STATISTICS` prints the pre-main split. Merge first-party dynamic frameworks, prefer static where you can, and keep `+load` empty. Typical miss: “launch is `didFinishLaunching`” and never naming rebase/bind.

### Example

```text
DYLD_PRINT_STATISTICS=1
# dylib loading / rebase+bind / ObjC setup / initializer
```

### Follow-ups

- Rebase vs bind — which one grows with ASLR vs imported symbols?
- Why does a pile of dynamic pods hurt cold start more than the same code statically linked?
- What does a Link Map tell you that dyld stats do not?
