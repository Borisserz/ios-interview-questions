# Frameworks

- [SpriteKit vs SceneKit](#spritekit-vs-scenekit)
- [Core Graphics](#core-graphics)
- [Core Image](#core-image)
- [iBeacons](#ibeacons)
- [StoreKit](#storekit)
- [HealthKit](#healthkit)
- [Playing a custom sound](#custom-sound)
- [NSAttributedString](#attributed-string)
- [GameplayKit](#gameplaykit)
- [ReplayKit](#replaykit)
- [CALayer subclasses](#calayer-subclasses)
- [CADisplayLink](#cadisplaylink)
- [CGAffineTransform](#affine-transform)
- [Core Location](#core-location)
- [App Intents](#app-intents)
- [WidgetKit](#widgetkit)
- [Live Activities](#live-activities)
- [App Clips](#app-clips)
- [Foundation Models](#foundation-models)

## SpriteKit vs SceneKit {#spritekit-vs-scenekit}

- Level: Mid
- Frequency: Low

### Answer

SpriteKit is Apple’s 2D scene graph: sprites, actions, physics, and a `SKView` you drop into UIKit or SwiftUI. SceneKit is the 3D stack: nodes, cameras, lights, geometries, and SCN materials, with an optional SceneKit editor. You pick SpriteKit for card games, 2D platformers, and particle overlays; SceneKit for product viewers, simple 3D games, and ARKit scenes that need a 3D graph. They can share a view (`SK3DNode`, SceneKit overlay) but they are not interchangeable APIs. RealityKit is the newer 3D / AR default; mention it so you do not sound stuck in 2016, then answer the question that was asked.

### Example

```swift
let scene = SKScene(size: view.bounds.size)
let sprite = SKSpriteNode(imageNamed: "tile")
sprite.position = CGPoint(x: 80, y: 120)
scene.addChild(sprite)
skView.presentScene(scene)

let scn = SCNScene()
let box = SCNNode(geometry: SCNBox(width: 1, height: 1, length: 1, chamferRadius: 0))
scn.rootNode.addChildNode(box)
scnView.scene = scn
```

### Follow-ups

- When would you skip both and use Metal or RealityKit?
- How do SpriteKit actions compare to SceneKit animations?
- Can you put a SpriteKit HUD on a SceneKit (or AR) view?
- What does the physics world give you in each framework?

## Core Graphics {#core-graphics}

- Level: Mid
- Frequency: Medium

### Answer

Core Graphics (Quartz 2D) is the C API for 2D drawing: paths, gradients, images, PDF, and a `CGContext` that receives the commands. UIKit’s `UIBezierPath` and `UIGraphicsImageRenderer` sit on top of it; SwiftUI `Canvas` eventually does too. You use it when you need pixels you do not have as an asset — a chart, a mask, a custom control, a PDF page. Drawing happens in the current context (`draw(_:)` on `UIView`, or a renderer). It is CPU-side unless you cache the result in a bitmap or a `CALayer.contents`. Forget to flip the Y axis or to end the image context and you get a blank or an upside-down image.

### Example

```swift
let renderer = UIGraphicsImageRenderer(size: CGSize(width: 80, height: 80))
let image = renderer.image { ctx in
    UIColor.systemBlue.setFill()
    ctx.cgContext.fillEllipse(in: CGRect(x: 8, y: 8, width: 64, height: 64))
}
```

### Follow-ups

- `UIGraphicsImageRenderer` vs `UIGraphicsBeginImageContext` — why the old API is gone?
- When do you draw in `draw(_:)` vs cache a bitmap?
- How does Core Graphics relate to Core Animation and Core Image?
- What is a `CGPath` vs a `UIBezierPath`?

## Core Image {#core-image}

- Level: Mid
- Frequency: Low

### Answer

Core Image is a GPU (and CPU) filter graph: `CIImage` in, `CIFilter` chain, `CIContext` out to a `CGImage` or a pixel buffer. You use it for color, blur, crop, QR detection (`CIDetector` / Vision now), and photo-style adjustments. Filters are lazy — nothing runs until you ask the context to render. Reuse one `CIContext`; creating one per frame is the usual stall. For stills, render to `CGImage`. For camera, render into a Metal texture or `CVPixelBuffer`. Vision and vImage overlap on some jobs; Core Image wins when the filter catalog already does the look you want.

### Example

```swift
let ciImage = CIImage(image: input)!
let filter = CIFilter.gaussianBlur()
filter.inputImage = ciImage
filter.radius = 8
let context = CIContext(options: [.useSoftwareRenderer: false])
let output = context.createCGImage(filter.outputImage!, from: ciImage.extent)
```

### Follow-ups

- Why must you reuse `CIContext` across frames?
- Core Image vs `UIImage` filters vs Vision — who owns detection vs look?
- How do you keep a filter chain in display color space?
- What does `extent` get wrong after a blur, and how do you crop it?

## iBeacons {#ibeacons}

- Level: Mid
- Frequency: Low

### Answer

iBeacon is Apple’s BLE advertising format: a UUID plus 16-bit major and minor values. You monitor a `CLBeaconRegion` to learn enter/exit (even in the background, with location permission) and you range to get proximity (`immediate` / `near` / `far`) while the app is running. Core Location owns the API, not Core Bluetooth — you do not parse advertisements yourself for standard beacons. Permission and battery matter: always-on ranging is expensive; monitoring is the background tool. Region limits (about 20) and the fact that proximity is noisy are the details that separate a real answer from “it’s Bluetooth.”

### Example

```swift
let constraint = CLBeaconIdentityConstraint(uuid: storeUUID)
let region = CLBeaconRegion(beaconIdentityConstraint: constraint, identifier: "store")
manager.requestWhenInUseAuthorization()
manager.startMonitoring(for: region)
manager.startRangingBeacons(satisfying: constraint)
```

### Follow-ups

- Monitoring vs ranging — which works in the background, and what do you get?
- Why is this Core Location and not Core Bluetooth?
- How accurate is `proximity`, and what do you use instead for distance?
- What privacy strings and background modes does a beacon feature need?

## StoreKit {#storekit}

- Level: Mid
- Frequency: High

### Answer

StoreKit is the in-app purchase and App Store commerce API. StoreKit 2 (`Product`, `Transaction`, `PurchaseResult`) is the current default: `async` product loads, `Transaction.currentEntitlements` for what the user owns, and `Transaction.updates` for renewals and family sharing. **Start the `updates` listener at launch**, not when the paywall appears — Ask to Buy and family-sharing land in that window. You still need App Store Connect product IDs, a testing storefront (StoreKit configuration file or sandbox), and a server if the purchase unlocks something you cannot trust the client to honor. Finish every verified transaction or it redelivers on every launch. Restore is `AppStore.sync()` plus a visible Restore button (Guideline 3.1.1); `currentEntitlements` is not a substitute for the button. Grant access in grace and billing-retry, not only `.subscribed`. SwiftUI `SubscriptionStoreView` / `StoreView` (iOS 17+) can own the paywall chrome. Do not build your own receipt parser in 2026 unless you are maintaining StoreKit 1.

### Example

```swift
func buy(_ id: String) async throws {
    let products = try await Product.products(for: [id])
    guard let product = products.first else { return }
    let result = try await product.purchase()
    if case .success(let verification) = result {
        let transaction = try verification.payloadValue
        await transaction.finish()
    }
}
```

### Follow-ups

- How do you restore or re-sync entitlements on a new device?
- What belongs on the server vs `Transaction.currentEntitlements`?
- StoreKit configuration file vs sandbox vs TestFlight — which bug shows up where?
- How do subscription status and billing retry appear in StoreKit 2?
- What does `Transaction.updates` catch that `purchase()` does not?
- Intro offer vs promotional offer — where do you read eligibility?
- Airplane mode — do you unlock from a cached entitlement, and for how long?
- Why must `Transaction.updates` start in `init` / at launch, not on the paywall?
- `AppStore.sync()` vs `Transaction.currentEntitlements` — which one is the Restore button?
- `.inGracePeriod` / `.inBillingRetryPeriod` — do you still unlock?

## HealthKit {#healthkit}

- Level: Mid
- Frequency: Medium

### Answer

HealthKit is the on-device **health store**, not a fitness UI. You talk to `HKHealthStore`: request **read and write separately**, name the types (`HKQuantityType`, `HKCategoryType`, workouts), and put the usage strings in Info.plist. Data is the user’s; you query with predicates and date intervals, you do not dump the whole store into your database. Background delivery and Watch pairing are opt-in and can be delayed. Typical miss: treating HealthKit like a REST API you poll, or shipping without a privacy string and wondering why authorization never appears.

### Example

```swift
let store = HKHealthStore()
let steps = HKQuantityType(.stepCount)
try await store.requestAuthorization(toShare: [], read: [steps])

let now = Date()
let start = Calendar.current.startOfDay(for: now)
let predicate = HKQuery.predicateForSamples(withStart: start, end: now)
```

### Follow-ups

- Read vs write authorization — can the user grant one and deny the other?
- Why is a daily step total a query, not a stored property on `HKHealthStore`?
- What do you do when HealthKit is unavailable (iPad, parental limits)?

## Playing a custom sound {#custom-sound}

- Level: Junior
- Frequency: Medium

### Answer

Short UI sounds can go through `AudioServicesPlaySystemSound` (or `.play` on a system sound ID) if they are a few seconds and you do not need mixing control. Anything you care about — volume, loop, session category, background — uses `AVAudioPlayer` or `AVAudioEngine`. You must configure `AVAudioSession` (`.ambient` so music keeps playing, `.playback` if your sound is the point) or the OS will silence you. Bundle the file (`caf`, `wav`, `m4a`, `mp3`) and load from `Bundle.main`. Do not block the main thread on a long file; prepare the player once and `play()` on the event.

### Example

```swift
import AVFoundation

final class TapSound {
    private var player: AVAudioPlayer?

    func prepare() throws {
        try AVAudioSession.sharedInstance().setCategory(.ambient)
        try AVAudioSession.sharedInstance().setActive(true)
        let url = Bundle.main.url(forResource: "tap", withExtension: "caf")!
        player = try AVAudioPlayer(contentsOf: url)
        player?.prepareToPlay()
    }

    func play() { player?.play() }
}
```

### Follow-ups

- When is `AudioServicesPlaySystemSound` the wrong API?
- `.ambient` vs `.playback` vs `.playAndRecord` — what does each duck?
- How do you play a sound when the ringer switch is off?
- Why would `play()` return and you hear nothing?

## NSAttributedString {#attributed-string}

- Level: Junior
- Frequency: Medium

### Answer

`NSAttributedString` is a string plus a run of attributes: font, color, underline, paragraph style, link, attachment. UIKit labels, text views, and navigation titles still take it; SwiftUI prefers `AttributedString` (the value type) and can convert with `NSAttributedString(attributedString)`. You build one with `NSMutableAttributedString` or with markdown via `AttributedString(markdown:)`. Attributes apply to ranges — off-by-one on a composed character is the usual bug. Use it when one label must mix styles; do not fake that with three labels if VoiceOver should read one sentence.

### Example

```swift
let text = NSMutableAttributedString(string: "Total 24.00")
text.addAttribute(.font, value: UIFont.preferredFont(forTextStyle: .body), range: NSRange(location: 0, length: 5))
text.addAttribute(.foregroundColor, value: UIColor.secondaryLabel, range: NSRange(location: 0, length: 5))
text.addAttribute(.font, value: UIFont.preferredFont(forTextStyle: .headline), range: NSRange(location: 6, length: 5))
label.attributedText = text
```

### Follow-ups

- `AttributedString` vs `NSAttributedString` — which API do you use in SwiftUI?
- How do you keep Dynamic Type when the attributes pin a `UIFont`?
- How do links and attachments behave in `UITextView` vs `UILabel`?
- What goes wrong with `NSRange` and emoji?

## GameplayKit {#gameplaykit}

- Level: Mid
- Frequency: Low

### Answer

GameplayKit is a toolbox for game logic that is not rendering: state machines (`GKStateMachine`), entities and components, pathfinding on a graph, random sources you can seed, and agent/goal steering. It sits next to SpriteKit or SceneKit; it does not draw a frame. The interview use that transfers to apps is `GKStateMachine` for a well-defined flow (onboarding, matchmaking, download) and deterministic `GKRandomSource` for reproducible tests. You would not pull it in for a settings screen. Apple has not made it the center of a new sample in years — say that, then show you still know what is in the box.

### Example

```swift
final class LoadingState: GKState {
    override func isValidNextState(_ stateClass: AnyClass) -> Bool {
        stateClass is ReadyState.Type || stateClass is FailedState.Type
    }
}

let machine = GKStateMachine(states: [LoadingState(), ReadyState(), FailedState()])
machine.enter(LoadingState.self)
```

### Follow-ups

- When is a `GKStateMachine` better than an enum on a view model?
- What does an entity-component split buy you in SpriteKit?
- How do you make a random drop table testable?
- Pathfinding: `GKGridGraph` vs writing A* yourself?

## ReplayKit {#replaykit}

- Level: Mid
- Frequency: Low

### Answer

ReplayKit records the app’s screen (and optional mic / app audio) or broadcasts it to a ReplayKit extension. `RPScreenRecorder.shared()` starts a recording; you get a preview (`RPPreviewViewController`) or raw sample buffers if you asked for them. The user has to consent; you cannot silently record. Broadcast is a separate extension target for Twitch-style streaming. Privacy and performance are the real topics: recording is expensive, and you must stop in the background. For a product clip, ReplayKit is still the supported path; for in-app “save this view as video,” AVFoundation or ReplayKit sample-buffer mode both appear in reviews.

### Example

```swift
import ReplayKit

func toggleRecording() {
    let recorder = RPScreenRecorder.shared()
    if recorder.isRecording {
        recorder.stopRecording { preview, _ in
            if let preview { present(preview, animated: true) }
        }
    } else {
        recorder.startRecording { error in
            if let error { present(error) }
        }
    }
}
```

### Follow-ups

- In-app recording vs broadcast extension — what does each target do?
- Can you record other apps? Why not?
- How do you include mic audio without capturing the whole device?
- What do you stop on `sceneDidEnterBackground`, and what happens if you do not?

## CALayer subclasses {#calayer-subclasses}

- Level: Mid
- Frequency: Medium

### Answer

`CALayer` is the render tree under every `UIView`. Apple ships specialized subclasses so you do not draw by hand: `CAShapeLayer` (paths), `CAGradientLayer`, `CATextLayer`, `CAReplicatorLayer`, `CAEmitterLayer` (particles), `CAScrollLayer`, `CATiledLayer` (huge images), `CATransformLayer` (true 3D without flattening), `CAMetalLayer`. You use them when the effect is cheaper as a layer than as a bitmap you redraw. Views own a layer; you can also build a standalone tree. Animating `path`, `colors`, or `transform` on these layers is Core Animation’s job — that is usually the follow-up.

### Example

```swift
let shape = CAShapeLayer()
shape.path = UIBezierPath(ovalIn: CGRect(x: 0, y: 0, width: 60, height: 60)).cgPath
shape.fillColor = UIColor.systemTeal.cgColor
view.layer.addSublayer(shape)

let gradient = CAGradientLayer()
gradient.colors = [UIColor.systemBlue.cgColor, UIColor.systemPurple.cgColor]
gradient.frame = view.bounds
view.layer.insertSublayer(gradient, at: 0)
```

### Follow-ups

- `CALayer` vs `UIView` — who handles touch, who draws?
- What does a layer object represent relative to its `UIView`?
- When do you pick `CAShapeLayer` over `draw(_:)`?
- What does `CATransformLayer` change about `transform` vs a normal layer?
- Why is `CATiledLayer` the right tool for a large PDF page?
- How do you animate a `CAShapeLayer` path without redrawing in `draw(_:)`?

## CADisplayLink {#cadisplaylink}

- Level: Mid
- Frequency: Medium

### Answer

`CADisplayLink` is a timer tied to the display refresh — 60 or 120 Hz, not “about 16 ms.” You use it for frame-by-frame work: a custom animation, a metal/game loop, a playback clock. `Timer` and `DispatchQueue` delays drift and do not pause with the screen. Add the link to `.main` (or a run loop that is actually running), set `preferredFrameRateRange`, and set `isPaused` when the scene backgrounds. A display link that does real work every frame will show up on Energy Log. Invalidate it in `stop()` or when the view goes away so the callback does not outlive the owner.

### Example

```swift
final class Pulse {
    private var link: CADisplayLink?

    func start() {
        let link = CADisplayLink(target: self, selector: #selector(tick))
        link.preferredFrameRateRange = CAFrameRateRange(minimum: 30, maximum: 60, preferred: 60)
        link.add(to: .main, forMode: .common)
        self.link = link
    }

    @objc private func tick(_ link: CADisplayLink) {
        let dt = link.targetTimestamp - link.timestamp
        advance(by: dt)
    }

    func stop() { link?.invalidate(); link = nil }
}
```

### Follow-ups

- Why not `Timer(timeInterval: 1/60, ...)` for animation?
- What does `preferredFrameRateRange` change on ProMotion?
- Should a display link run in `.common` or `.default`, and why?
- How do you keep a display link from draining battery in the background?

## CGAffineTransform {#affine-transform}

- Level: Mid
- Frequency: Medium

### Answer

A `CGAffineTransform` is a 2D affine matrix: translate, scale, rotate, and shear. You apply it to a view (`view.transform`), a layer, a path, or a context. Order matters — rotate-then-move is not move-then-rotate — and the API concatenates on the right, which surprises people who think in “first I wrote this line.” The identity transform is `CGAffineTransform.identity`; reset with that, not with guessed numbers. 3D and perspective are `CATransform3D`, not affine. Autolayout and `transform` fight: the frame is the untransformed bounds, which is why a scaled button’s hit area looks wrong if you only look at `frame`.

### Example

```swift
thumb.transform = CGAffineTransform.identity
    .translatedBy(x: 0, y: -12)
    .rotated(by: .pi / 12)
    .scaledBy(x: 1.05, y: 1.05)

let path = UIBezierPath(rect: CGRect(x: 0, y: 0, width: 40, height: 8))
path.apply(CGAffineTransform(rotationAngle: .pi / 4))
```

### Follow-ups

- Why does concatenating transforms in the “wrong” order move the view off-screen?
- `frame` vs `bounds` vs `transform` after a rotation — which one do you layout with?
- When do you need `CATransform3D` instead?
- How do you invert a transform to map a tap back into model space?

## Core Location {#core-location}

- Level: Mid
- Frequency: Medium

### Answer

`CLLocationManager` is the GPS / Wi-Fi / cell fusion API. You ask for **When In Use** or **Always**, put a usage string in Info.plist, then start updates, significant-change, or visits. Accuracy vs battery is the interview: `kCLLocationAccuracyBest` on a map is not what a weather app needs. Background location is an entitlement and a review story. Typical miss: starting updates in `init` before authorization, or holding `Always` for a one-shot “find stores near me.”

### Example

```swift
let manager = CLLocationManager()
manager.requestWhenInUseAuthorization()
manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
manager.startUpdatingLocation()
```

### Follow-ups

- When In Use vs Always vs Precise Location?
- Significant-change vs visits vs a standard update stream?
- How do you test location without standing outside?

## App Intents {#app-intents}

- Level: Mid
- Frequency: Medium

### Answer

App Intents is the modern way to expose **actions and entities** to Siri, Spotlight, Shortcuts, and the Action button — the successor to a pile of `INIntent` files for many cases. You declare a struct that conforms to `AppIntent`, give it a title and parameters, and implement `perform()`. The system can show it without opening a UI; if you need a screen, you return a snippet or continue in-app. Typical miss: treating it as “Siri only,” or putting a 20-second network call in `perform()` with no progress.

### Example

```swift
struct LogWater: AppIntent {
    static var title: LocalizedStringResource = "Log water"
    @Parameter(title: "Millilitres") var millilitres: Int

    func perform() async throws -> some IntentResult {
        await WaterStore.shared.add(millilitres)
        return .result()
    }
}
```

### Follow-ups

- App Intent vs an old SiriKit intent definition?
- How do you donate an intent so Spotlight suggests it?
- What must stay off the main actor in `perform()`?

## WidgetKit {#widgetkit}

- Level: Mid
- Frequency: Medium

### Answer

A Home Screen widget is a **timeline of snapshots**, not a live app. WidgetKit asks a `TimelineProvider` for `TimelineEntry` values and a `View`; the system renders that SwiftUI off-process and may freeze it. You cannot run arbitrary timers or keep a socket open. Refresh is a budget: `.atEnd`, `.after(date)`, or a push to `WidgetCenter`. Tap uses a `widgetURL` / App Intent into the main app. Share UI via a package, not copy-paste. Typical miss: treating the widget as a mini `UIViewController` that fetches every second.

### Example

```swift
struct StatusEntry: TimelineEntry {
    let date: Date
    let text: String
}

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> StatusEntry { .init(date: .now, text: "…") }
    func getSnapshot(in context: Context, completion: @escaping (StatusEntry) -> Void) {
        completion(.init(date: .now, text: "OK"))
    }
    func getTimeline(in context: Context, completion: @escaping (Timeline<StatusEntry>) -> Void) {
        completion(Timeline(entries: [.init(date: .now, text: "OK")], policy: .after(.now.addingTimeInterval(3600))))
    }
}
```

### Follow-ups

- Why are animations limited compared with the app?
- How do you share a SwiftUI row between app and widget?
- Timeline reload vs an App Intent button on iOS 17+?

## Live Activities {#live-activities}

- Level: Mid
- Frequency: Medium

### Answer

A Live Activity is a **real-time strip** on the Lock Screen and Dynamic Island for a short-lived event (order, ride, timer). You start it from the app with ActivityKit, push content-state updates (often via APNs), and end it when the event finishes. The UI is SwiftUI in a widget extension — same snapshot rules as WidgetKit, plus compact / minimal / expanded island presentations. It is not a background `Timer` in the app process. Typical miss: starting an activity and never ending it, or stuffing the payload with a full chat history.

### Example

```swift
struct OrderAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable { var eta: String }
    var restaurant: String
}
```

### Follow-ups

- Push update vs the app calling `activity.update` in the foreground?
- What happens if the user force-quits the app mid-activity?
- Dynamic Island compact vs expanded — who decides the layout?

## App Clips {#app-clips}

- Level: Mid
- Frequency: Low

### Answer

An App Clip is a **tiny invocation** of your app (size budget on the order of 15 MB) that runs from a link, QR, or NFC without a full install. You ship a clip target that can later upgrade to the full app. Keep the first experience offline-tolerant and ask for only the permissions that screen needs. Invocation URL is the deep link. Typical miss: dragging the whole app target into the clip and blowing the size limit.

### Example

```text
Clip target → one screen (pay / order) → “Get the full app” → same team ID, shared App Group if you must hand off state.
```

### Follow-ups

- What do you share with the full app — Keychain? App Group? Nothing?
- How is an App Clip different from a Universal Link into the installed app?
- Where does the size budget actually hurt (images, SDKs)?

## Foundation Models {#foundation-models}

- Level: Senior
- Frequency: Medium

### Answer

Apple’s **Foundation Models** framework is an on-device LLM you call like a service — not a chat screen. You send **instructions** (role, refusals, tool policy) plus a prompt; `@Generable` / `@Guide` constrain the output to a typed Swift value. That value is a **DTO**. Persist by mapping into SwiftData / your store — do not slap `@Model` on a generable. Tools are narrow Swift functions the model may call. Hardware is gated (no Neural Engine → explicit fallback). Typical miss: an “Ask AI” button on a flow that needed one tap, or treating the model as a chatbot that owns your domain types.

### Example

```swift
@Generable
struct RecipeDraft {
    @Guide(description: "Short title")
    var title: String
}

// Service layer: session + instructions → RecipeDraft → map to @Model if you save
```

### Follow-ups

- Instructions vs the user prompt — which do you version with the app?
- Why can’t a `@Generable` type be your SwiftData entity?
- Adapter / fine-tune — what artifact do you ship next to the binary?
