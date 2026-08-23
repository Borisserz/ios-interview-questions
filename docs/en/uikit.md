# UIKit

46 cards · 23 often asked · source [uikit.md](../../topics/uikit.md)

### Junior

<h2 id="iboutlet-vs-ibaction">@IBOutlet vs @IBAction</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`@IBOutlet`** marks a *property* Interface Builder can connect to an object on the canvas — a label, a constraint, a whole view. **`@IBAction`** marks a *method* IB can hook to a control event (`touchUpInside`, `editingChanged`, a gesture’s action). Outlets are almost always `weak` and implicitly unwrapped: the storyboard owns the view; the property is nil until the nib loads, then it must exist or you crash on first use. Actions take a sender (`Any`, or a typed `UIButton`) and sometimes the event. Connecting the same control to two actions is fine; connecting an outlet to the wrong type is a runtime failure. Typical mistakes: `strong` outlets that surprise people in cells, and putting logic in the action that belongs in a view model.



```swift
final class LoginViewController: UIViewController {
    @IBOutlet private weak var emailField: UITextField!
    @IBOutlet private weak var loginButton: UIButton!

    @IBAction private func loginTapped(_ sender: UIButton) {
        submit(email: emailField.text)
    }
}
```


**Then they usually ask**

- Why are outlets usually `weak`?
- When is a `strong` outlet justified?
- What happens if an outlet connection is broken in the storyboard?
- Is a `strong` `@IBOutlet` always a leak, or only when the view graph already owns it?

</details>

<h2 id="aspect-fill-vs-fit">Aspect fill vs aspect fit</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Both are `UIView.ContentMode` values that preserve the image’s aspect ratio. **`scaleAspectFit`** scales the image until it is entirely visible inside the bounds; leftover area is empty (letterboxing). **`scaleAspectFill`** scales until the bounds are fully covered; overflow is drawn past the edges and you only see a crop if `clipsToBounds` is true. Fit is right for logos and anything you must not crop. Fill is right for avatars and hero photos. `scaleToFill` (the default on `UIImageView`) stretches and distorts — that is the third option interviewers expect you to name. Typical mistake: aspect fill without clipping, then wondering why the image paints over neighboring views.



```swift
avatarView.contentMode = .scaleAspectFill
avatarView.clipsToBounds = true

logoView.contentMode = .scaleAspectFit
logoView.clipsToBounds = false
```


**Then they usually ask**

- What does the default `scaleToFill` do to a non-matching image?
- How does this relate to SwiftUI’s `AspectRatio` / `scaledToFill()`?
- When would you use `center` or `top` instead of a scale mode?

</details>

<h2 id="auto-layout-anchors">Auto Layout anchors</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Auto Layout** is a constraint solver: you describe relationships, UIKit computes frames. That is how one layout survives iPhone vs iPad, rotation, Dynamic Type, and a keyboard. Size classes and trait collections are the coarse “regular / compact” switch; constraints are the fine rules. **Anchors** (`NSLayoutAnchor`) are the typed way to write those rules: `leadingAnchor`, `trailingAnchor`, `topAnchor`, `bottomAnchor`, `centerXAnchor`, `widthAnchor`. You must set `translatesAutoresizingMaskIntoConstraints = false` on every view you constrain in code, or UIKit also creates autoresizing constraints and you get unsatisfiable logs. Activate a batch with `NSLayoutConstraint.activate` so the engine solves once. Prefer the superview’s `safeAreaLayoutGuide` (and `readableContentGuide` / `keyboardLayoutGuide` where they apply) over raw `view.topAnchor`. Typical mistakes: constraining a view before it has a superview, mixing frames and constraints on the same view, and activating the same constraint twice.



```swift
button.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(button)
NSLayoutConstraint.activate([
    button.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 16),
    button.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -16),
    button.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor, constant: -12)
])
```


**Then they usually ask**

- What happens if you leave `translatesAutoresizingMaskIntoConstraints` as `true`?
- When do you use `safeAreaLayoutGuide` versus the view’s own anchors?
- How do you temporarily disable a constraint?
- Auto Layout vs frames vs SwiftUI layout — when do you still pick each?

</details>

<h2 id="autolayout-formula">Auto Layout formula</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Every constraint is `item1.attribute = multiplier × item2.attribute + constant` (plus a relation `=`, `≥`, `≤` and a priority). Anchors are just that equation: `title.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16)` is multiplier 1, constant 16. A required constraint is priority **1000**; **1…999** are optional — when the system is unsatisfiable, the engine drops the lowest priority first. You break ambiguity with hugging / compression or a 999-priority extra constraint (a “nice to have” width). Typical miss: two required equal-width constraints that fight, or forgetting the formula has a multiplier (aspect ratio).



```swift
// width = 2 * height + 0
box.widthAnchor.constraint(equalTo: box.heightAnchor, multiplier: 2)
```


**Then they usually ask**

- What does a priority of 999 change?
- How do you write “at least 16 pt from the safe area”?
- Intrinsic size vs an explicit width constraint — who wins?

</details>

<h2 id="reuse-identifiers">Cell reuse identifiers</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Table and collection views keep a small pool of cells and **reuse** them as you scroll. The **reuse identifier** is the key for that pool: you `register` a class or nib for an ID, then `dequeueReusableCell` with the same ID. A mismatch crashes (`unable to dequeue a cell with identifier`). After dequeue, the cell still holds the last row’s text, images, and accessory state — `prepareForReuse` and your configure method must reset everything you do not intend to keep. Diffable data sources still use identifiers; they only change how you apply snapshots. Typical mistakes: registering in the cell and dequeuing a different string, and skipping reset so images “bleed” between rows.



```swift
final class ItemCell: UITableViewCell {
    static let reuseID = "ItemCell"
}

tableView.register(ItemCell.self, forCellReuseIdentifier: ItemCell.reuseID)

func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: ItemCell.reuseID, for: indexPath) as! ItemCell
    cell.apply(items[indexPath.row])
    return cell
}
```


**Then they usually ask**

- What belongs in `prepareForReuse` versus `cellForRowAt`?
- Why does `dequeueReusableCell(withIdentifier:for:)` need a prior `register`?
- How do you handle two cell types in one list?

</details>

<h2 id="dark-mode">Dark mode</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Dark Mode is a **trait**: `userInterfaceStyle` is `.light` or `.dark`. Use **dynamic colors** (`.label`, `.systemBackground`, `.secondaryLabel`) and asset-catalog image variants so UIKit / SwiftUI swap automatically. Hard-coded `UIColor.white` on a label fails in dark. Override per screen with `overrideUserInterfaceStyle` only when product demands a locked chrome (a camera, a cinema player). Observe changes in `traitCollectionDidChange` (UIKit) or `@Environment(\.colorScheme)` (SwiftUI). Typical miss: a custom hex that looks fine in light and disappears in dark, or forcing `.dark` on the window to “match the brand” and breaking system alerts.



```swift
view.backgroundColor = .systemBackground
title.textColor = .label
subtitle.textColor = .secondaryLabel

override func traitCollectionDidChange(_ previous: UITraitCollection?) {
    super.traitCollectionDidChange(previous)
    if traitCollection.hasDifferentColorAppearance(comparedTo: previous) {
        redrawShadows() // CGColor does not flip itself
    }
}
```


**Then they usually ask**

- Why does a `CGColor` shadow stay black after a mode flip?
- Asset catalog Appearances vs a runtime `if colorScheme == .dark`?
- How do you snapshot-test both appearances?

</details>

<h2 id="modal-vs-push">Modal vs push</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Push** adds a view controller onto a `UINavigationController` stack — same flow, back button, you can pop. **Present** (`present(_:animated:)`) puts a new VC over the current one (sheet, full-screen, popover). The presenter stays alive underneath; you `dismiss`. Use push for “go deeper in this section.” Use a modal for a self-contained task (compose, pay, login, filter) that should not grow a back stack. A modal can itself *contain* a nav controller if the task has two steps. Typical miss: presenting when the user expected Back, or pushing a login that they cannot pop without leaking the previous screen.



```swift
// Drill-down
navigationController?.pushViewController(DetailViewController(item: item), animated: true)

// Task
let compose = UINavigationController(rootViewController: ComposeViewController())
compose.modalPresentationStyle = .formSheet
present(compose, animated: true)
```


**Then they usually ask**

- `.pageSheet` vs `.fullScreen` — what does a swipe-down do?
- How do you pass a result back from a modal without a singleton?
- Can you push onto a VC that is not inside a navigation controller?

</details>

<h2 id="safe-area">Safe area</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The **safe area** is the rectangle that is not covered by the status bar, notch / Dynamic Island, home indicator, or a navigation / tab / toolbar. Pin to `safeAreaLayoutGuide` (or SwiftUI `safeAreaInset` / ignore only when you mean a full-bleed background). The layout guide moves when bars appear, when you rotate, and when a keyboard or additional safe-area insets land. Typical miss: pinning a title to `view.topAnchor` and watching it sit under the notch, or calling `edgesForExtendedLayout = []` as a substitute for understanding the guide.



```swift
title.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    title.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
    title.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 16),
])
```


**Then they usually ask**

- Safe area vs layout margins vs `readableContentGuide`?
- How do you draw a background edge-to-edge but keep the label safe?
- What extra inset does a keyboard or an additional safe-area inset add?

</details>

<h2 id="storyboards-vs-code">Storyboards vs code layouts</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **storyboard** is a visual graph of scenes, segues, and Auto Layout that Interface Builder compiles into the app. Laying out in **code** means creating views, setting `translatesAutoresizingMaskIntoConstraints = false`, and activating constraints (or using frames) in `loadView` / `viewDidLoad`. Interviewers want the trade-off, not a religion: storyboards are fast for a first screen and for people who think visually, but they merge badly, hide bugs until runtime (`@IBOutlet` typos, missing IDs), and do not review well in a pull request. Code is verbose and has no built-in canvas, but it diffs cleanly, is easy to generate in a loop, and works the same in every module. Mixed apps are normal: a storyboard for a simple flow, programmatic layout for reusable controls and anything that changes with state. Typical mistake: treating “we use storyboards” as an architecture instead of a delivery choice.



```swift
final class ProfileViewController: UIViewController {
    private let nameLabel = UILabel()

    override func viewDidLoad() {
        super.viewDidLoad()
        nameLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(nameLabel)
        NSLayoutConstraint.activate([
            nameLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            nameLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
}
```


**Then they usually ask**

- How do you instantiate a view controller that lives on a storyboard?
- What goes wrong in a git merge of a storyboard?
- When would you still pick a XIB over either of these?

</details>

<h2 id="uiimage-vs-uiimageview">UIImage vs UIImageView</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`UIImage`** is the image *data*: a bitmap, a symbol, or a named asset. It is not in the hierarchy, has no frame, and can be shared by many views. **`UIImageView`** is a `UIView` that *draws* a `UIImage` (or an animation sequence) according to `contentMode`, tint, and highlighted state. You load with `UIImage(named:)` or `UIImage(systemName:)`, then assign `imageView.image`. Mutating pixels means creating a new `UIImage`; changing how it is cropped or aligned means changing the view. Typical mistakes: treating `UIImage` as something you `addSubview`, and creating huge images on the main thread without considering `@2x` / `@3x` scale.



```swift
let icon = UIImage(systemName: "star.fill")
let imageView = UIImageView(image: icon)
imageView.contentMode = .scaleAspectFit
imageView.tintColor = .systemYellow
view.addSubview(imageView)
```


**Then they usually ask**

- Where does `UIImage(named:)` look, and does it cache?
- How do you show a template image that tints with `tintColor`?
- What is `UIImageView`’s `animationImages` for?

</details>

<h2 id="navigation-controller">UINavigationController</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A navigation controller owns a **stack** of view controllers. `push` / `pop` (and `setViewControllers`) change the stack; the nav bar shows the top title and a back item. It is a container: it does not draw your screen, it hosts it. Pass data in the initializer of the next VC, not by digging into `viewControllers`. Typical miss: pushing from a cell with a stale index, or presenting a nav controller when you meant to push onto the existing one.



```swift
let detail = DetailViewController(item: item)
navigationController?.pushViewController(detail, animated: true)
```


**Then they usually ask**

- Push vs present — when is a modal the right move?
- How do you pop to a specific VC without rebuilding the stack?
- What does `UINavigationControllerDelegate` give you (custom transition)?

</details>

<h2 id="stack-view">UIStackView</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`UIStackView` is Auto Layout for a row or column: `axis`, `spacing`, `alignment`, `distribution`, and `isLayoutMarginsRelativeArrangement`. It does not draw — it only creates constraints between arranged subviews. Hiding a child (`isHidden = true`) collapses its space. Nested stacks beat a web of equal-width constraints. Typical miss: expecting a stack to scroll (wrap it in a scroll view) or setting frames on arranged views.



```swift
let stack = UIStackView(arrangedSubviews: [icon, title, spacer])
stack.axis = .horizontal
stack.spacing = 8
stack.alignment = .center
stack.distribution = .fill
```


**Then they usually ask**

- `fill` vs `fillEqually` vs `equalSpacing`?
- Why does `isHidden` on an arranged view change the layout?
- Stack vs constraints by hand — when do you stop nesting?

</details>

<h2 id="viewcontroller-lifecycle">UIViewController lifecycle</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`init` / `init(coder:)` create the object — no view yet. `loadView` builds the root view (override only if you are not using a storyboard or `loadViewIfNeeded` default). `viewDidLoad` is the first time `view` exists: add subviews, constraints, one-time setup. `viewWillAppear` / `viewDidAppear` run every time it comes on screen — start timers, refresh. `viewWillDisappear` / `viewDidDisappear` are the pair for stopping work. `viewWillLayoutSubviews` / `viewDidLayoutSubviews` run when bounds change; put frame math there, not in `viewDidLoad`. Appearance callbacks can fire more than once (tab switch, split view, a cover). **Remote data:** a mostly static payload can start in `viewDidLoad` (and be cached). Anything that goes stale belongs in `viewWillAppear` / a pull-to-refresh. Either way, fetch off the main thread and cancel when the screen leaves. Typical mistake: starting a network call in `viewDidLoad` and never cancelling in `viewWillDisappear`, or putting constraint setup in `viewDidAppear`.



```swift
final class ProfileViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        view.addSubview(table)
        table.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            table.topAnchor.constraint(equalTo: view.topAnchor),
            table.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            table.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            table.trailingAnchor.constraint(equalTo: view.trailingAnchor),
        ])
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        reload()
    }
}
```


**Then they usually ask**

- `viewDidLoad` vs `viewWillAppear` — what belongs in each?
- When is `viewDidLayoutSubviews` the right place for a gradient frame?
- How do containment and `addChild` change the order?
- `viewDidLoad` vs `viewDidAppear` for a remote feed — which, and why async?
- You start a segue A→B then cancel — which lifecycle methods already ran?

</details>

<h2 id="frame-vs-bounds">frame vs bounds</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`frame`** is the view’s rectangle in the **superview’s** coordinate space (origin + size). **`bounds`** is the same size in the **view’s own** space; origin is usually `.zero` unless you scrolled or set it. A `CGAffineTransform` (rotation, scale) changes how `frame` looks; `bounds.size` stays the untransformed size. Scroll views move `bounds.origin` to reveal content. Auto Layout writes `frame` after layout. Typical mistake: setting `frame` in a transformed view and wondering why it jumps, or using `frame` inside `draw(_:)` instead of `bounds`.



```swift
let child = UIView(frame: CGRect(x: 40, y: 80, width: 100, height: 50))
parent.addSubview(child)
child.frame.origin   // (40, 80) in parent
child.bounds.origin  // (0, 0) in itself
child.transform = CGAffineTransform(rotationAngle: .pi / 8)
// frame is now a larger axis-aligned box; bounds.size is still 100×50
```


**Then they usually ask**

- Why does a `UIScrollView` change `bounds.origin` when you scroll?
- After a rotation transform, which size do you use for hit-testing vs drawing?
- When is `center` a better knob than `frame.origin`?

</details>

<h2 id="prepare-for-reuse">prepareForReuse</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The table/collection view calls **`prepareForReuse`** just before a cell leaves the reuse pool and goes to a new index path. Reset **transient** UI: cancel an in-flight image download, clear `imageView.image`, hide the accessory, drop a highlighted state, invalidate a timer. Do **not** configure the new row here — you do not have the model yet; that belongs in `cellForRowAt` / your `apply(_:)`. Super must be called. Typical bleed: a cancelled request’s completion still sets an image on the reused cell — capture a generation token or the URL and ignore stale callbacks.



```swift
final class PhotoCell: UITableViewCell {
    private var load: Task<Void, Never>?

    override func prepareForReuse() {
        super.prepareForReuse()
        load?.cancel()
        load = nil
        imageView?.image = nil
        textLabel?.text = nil
    }
}
```


**Then they usually ask**

- Why not assign the new model inside `prepareForReuse`?
- How do you ignore a late image callback after reuse?
- Does a SwiftUI `List` have the same problem?

</details>

<h2 id="view-shadow">Add a shadow to a view</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Shadows are drawn by **`CALayer`**, not by `UIView` itself. You set `shadowColor` (a `CGColor`), `shadowOpacity` (0...1), `shadowOffset`, and `shadowRadius` on `view.layer`. The shadow is the silhouette of the layer’s alpha, so a fully opaque rectangle casts a rectangular shadow; a layer with `cornerRadius` casts a rounded one if you also give it a matching `shadowPath`. **`clipsToBounds` / `masksToBounds` clip the shadow**, which is why “I set `cornerRadius` and the shadow vanished” is the classic follow-up. The usual fix is a wrapper view that owns the shadow and an inner view that clips and rounds. Setting `shadowPath` (and rasterizing only when the size is stable) keeps scrolling lists from dropping frames.



```swift
func applyCardShadow(to view: UIView) {
    view.layer.shadowColor = UIColor.black.cgColor
    view.layer.shadowOpacity = 0.2
    view.layer.shadowOffset = CGSize(width: 0, height: 4)
    view.layer.shadowRadius = 8
    view.layer.shadowPath = UIBezierPath(
        roundedRect: view.bounds,
        cornerRadius: view.layer.cornerRadius
    ).cgPath
}
```


**Then they usually ask**

- Why does a shadow disappear after you set `clipsToBounds = true`?
- Why set `shadowPath` instead of letting Core Animation infer it?
- How do you shadow a view that also has rounded, clipped contents?

</details>

<h2 id="gesture-recognizers">Gesture recognizers</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A `UIGestureRecognizer` turns touches into a high-level action: tap, pan, pinch, swipe, long-press, rotation, screen-edge. Attach it to a view; it walks the responder chain. Gestures can **fail**, **require** another to fail, or run **simultaneously** — that is how a pan and a tap coexist. `cancelsTouchesInView` stops the control underneath. Typical miss: a tap on a `UIButton` that never fires because a parent pan ate it, or adding a gesture to a view with `isUserInteractionEnabled == false`.



```swift
let tap = UITapGestureRecognizer(target: self, action: #selector(tapped))
tap.numberOfTapsRequired = 2
imageView.isUserInteractionEnabled = true
imageView.addGestureRecognizer(tap)
```


**Then they usually ask**

- How do you let a table-view pan and a cell swipe both work?
- Gesture vs `UIControl` target-action?
- What does `require(toFail:)` fix?

</details>

<h2 id="launch-screen">Launch screen</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The launch screen is a **static** storyboard (`UILaunchStoryboardName`) the system shows before your process is up. No custom class, no network, no animation, no code in `viewDidLoad` — the system snapshots it. You can have one launch storyboard; appearance (light/dark) is via asset catalogs and trait variations, not two storyboards you swap in code. Typical miss: putting a spinner you expect to spin, or treating it as `didFinishLaunching`.



```xml
<!-- Info.plist -->
<key>UILaunchStoryboardName</key>
<string>LaunchScreen</string>
```


**Then they usually ask**

- Can you change launch-screen labels at runtime?
- Why does a “wrong” launch screen linger after an update?
- Launch screen vs a branded splash `UIViewController` you present yourself?

</details>

<h2 id="points-vs-pixels">Points vs pixels</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

UIKit layout is in **points**. A point is a density-independent unit; on a 3× device, 1 point is 3 pixels. `UIScreen.main.scale` (or the view’s `traitCollection.displayScale`) is that factor. Images ship as `@2x` / `@3x` so they stay sharp. You almost never layout in pixels; you do when talking to Core Graphics bitmaps or `UIGraphicsImageRenderer` format. Typical miss: dividing a frame by `scale` “to get points” when it was already in points.



```swift
let scale = view.traitCollection.displayScale
let pixels = CGSize(width: view.bounds.width * scale, height: view.bounds.height * scale)
```


**Then they usually ask**

- Why is a 44 pt button not 44 px on iPhone?
- `UIImage.size` — points or pixels?
- When do you still care about pixels?

</details>

<h2 id="round-corners">Round view corners</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The straightforward path is `view.layer.cornerRadius` plus something that **clips** the contents: `masksToBounds` on the layer or `clipsToBounds` on the view (they are the same flag). From iOS 11 you can round a subset of corners with `maskedCorners` (`CACornerMask`). From iOS 13, `cornerCurve = .continuous` matches the system squircle. If you need a hole, a dashed outline, or a shape Auto Layout cannot express, mask with a `CAShapeLayer` whose `path` is a `UIBezierPath`. Do not animate `cornerRadius` by assigning it every frame in `layoutSubviews` without a reason — that fights the render server. And remember: clipping to round the image will also clip a shadow on that same layer.



```swift
imageView.layer.cornerRadius = 12
imageView.layer.maskedCorners = [.layerMinXMinYCorner, .layerMaxXMinYCorner]
imageView.layer.cornerCurve = .continuous
imageView.clipsToBounds = true
```


**Then they usually ask**

- How do you round only the top two corners?
- What is the difference between `masksToBounds` and a `CAShapeLayer` mask?
- Why would you set `cornerCurve`?

</details>

<h2 id="storyboard-identifiers">Storyboard identifiers</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The **Storyboard ID** is a string you set in the Identity inspector so you can instantiate that scene without a segue: `storyboard.instantiateViewController(withIdentifier:)`. It is not the same as a **segue identifier**, a **cell reuse identifier**, or a **restoration identifier** — four different strings, four different crashes if you mix them up. If the ID is missing or misspelled, `instantiateViewController` throws (or the older API aborts). Using the class name as the ID is a common convention so the string exists in one place. Typical mistake: setting the restoration ID and wondering why instantiate still fails.



```swift
enum StoryboardID {
    static let profile = "ProfileViewController"
}

let storyboard = UIStoryboard(name: "Main", bundle: nil)
let profile = storyboard.instantiateViewController(
    identifier: StoryboardID.profile
) as ProfileViewController
```


**Then they usually ask**

- What exception do you get when the identifier is wrong?
- How is a Storyboard ID different from a restoration ID?
- Why might a team use one storyboard per feature instead of IDs in `Main`?

</details>

<h2 id="activity-view-controller">UIActivityViewController</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`UIActivityViewController`** is the system share sheet. You hand it `activityItems` (strings, URLs, images, or a custom `UIActivityItemSource`) and optional `applicationActivities`, then `present` it. Users pick Messages, Mail, Copy, Save Image, or an app that advertised a share extension. You can hide system actions with `excludedActivityTypes` and observe the result via `completionWithItemsHandler`. On iPad it is a popover: you must set `popoverPresentationController?.sourceView` (or `barButtonItem`) or it will crash. Typical mistakes: presenting it on a phone with no popover path tested, and sharing a file URL that is not in a world-readable location.



```swift
let items: [Any] = [text, fileURL]
let sheet = UIActivityViewController(activityItems: items, applicationActivities: nil)
sheet.excludedActivityTypes = [.assignToContact]
sheet.popoverPresentationController?.sourceView = shareButton
present(sheet, animated: true)
```


**Then they usually ask**

- Why does this crash on iPad if you only call `present`?
- What is `UIActivityItemSource` for?
- How do you learn which activity the user picked?

</details>

<h2 id="tab-bar-controller">UITabBarController</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A tab controller hosts **siblings**, not a stack: each tab keeps its own root (often a navigation controller). Selecting a tab does not reset that tab’s nav stack unless you do it. Five visible tabs; more go into “More.” Typical miss: one shared navigation controller for every tab, or putting a tab controller *inside* a nav controller and wondering why the tab bar disappears on push.



```swift
let feed = UINavigationController(rootViewController: FeedViewController())
feed.tabBarItem = UITabBarItem(title: "Feed", image: UIImage(systemName: "list.bullet"), tag: 0)
let tabs = UITabBarController()
tabs.viewControllers = [feed, profile]
```


**Then they usually ask**

- Why does each tab usually wrap a `UINavigationController`?
- What happens to a tab’s state when you leave and come back?
- Tab vs a segmented control on one screen?

</details>

<h2 id="uiview-lifecycle">UIView lifecycle</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A view is created (`init(frame:)` / `init(coder:)`), added (`willMove(toSuperview:)` / `didMoveToSuperview`), attached to a window (`didMoveToWindow`), then laid out (`layoutSubviews`) and drawn (`draw(_:)` / the layer). Constraints update the layout engine; `layoutSubviews` applies frames. `draw(_:)` is for custom drawing, not for adding subviews. Typical miss: creating a gradient in `init` with a zero bounds, or putting constraint activation in `draw(_:)`.



```swift
final class Badge: UIView {
    override func layoutSubviews() {
        super.layoutSubviews()
        layer.cornerRadius = bounds.height / 2
    }
}
```


**Then they usually ask**

- `didMoveToWindow` vs `didMoveToSuperview`?
- Why is `draw(_:)` the wrong place to `addSubview`?
- How does this differ from a view controller’s `viewDidLayoutSubviews`?

</details>

<h2 id="visual-effect-view">UIVisualEffectView</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`UIVisualEffectView`** composites a live blur or vibrancy effect over whatever is behind it. You create it with a `UIBlurEffect` (system styles like `.systemMaterial`) or wrap a blur in `UIVibrancyEffect` so labels punch through the blur the way Control Center does. Subviews must go on **`contentView`**, not on the effect view itself — adding to the effect view directly is the usual “why is my label gone / why is the blur wrong” bug. The effect samples the content behind the view, so a solid opaque sibling covering that region produces no blur. Vibrancy without a matching blur looks washed out. Treat the view like any other: constrain it, then constrain children to `contentView`.



```swift
let blur = UIVisualEffectView(effect: UIBlurEffect(style: .systemMaterial))
blur.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(blur)

let label = UILabel()
label.text = "Behind the chrome"
blur.contentView.addSubview(label)
```


**Then they usually ask**

- Why must subviews be added to `contentView`?
- What is vibrancy for, relative to blur?
- How do materials differ from the old `.light` / `.dark` blur styles?

</details>

<h2 id="view-hierarchy">UIWindow and the view hierarchy</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **`UIWindow`** is the root surface a scene draws into. It hosts one root view controller; that controller’s `view` is the trunk of the **view hierarchy** — a tree of `UIView`s. UIKit draws back-to-front, hit-tests front-to-back, and lays out children inside their parents. You almost never create a second window on iPhone; on iPad / Mac a second `UIScene` gets its own window. `UIApplication` owns the process; the window owns what is on screen. Typical miss: adding a subview to `UIWindow` to “float” a banner (it ignores rotation and safe area) instead of a child view controller, or treating `view` as optional decoration rather than the controller’s root.



```swift
// UIWindow
// └── rootViewController.view
//     ├── titleLabel
//     └── contentView
//         └── imageView

window.rootViewController = RootViewController()
window.makeKeyAndVisible()
```


**Then they usually ask**

- Who hit-tests a tap — the window, the root VC, or the frontmost view?
- When would you have two windows in one process?
- `addSubview` on the window vs a child view controller — which survives rotation?

</details>

<h2 id="xib-vs-storyboard">XIBs vs storyboards</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **XIB** (nib) archives one view, one cell, or one view controller. A **storyboard** archives a *graph* of scenes plus the segues and relationships between them. XIBs win for reusable pieces — `UITableViewCell`, `UICollectionViewCell`, a custom `UIView` loaded with `Bundle.main.loadNibNamed`, a VC you instantiate from many places — because the file is small and merge conflicts stay local. Storyboards win when you want to see a flow and wire Show/Present connections without writing `present`. Both are Interface Builder; both deserialize at runtime; neither is required if you build the hierarchy in code. Typical mistake: stuffing every screen into one storyboard so every change invalidates the whole file for the rest of the team.



```swift
let nib = UINib(nibName: "AccountCell", bundle: nil)
tableView.register(nib, forCellReuseIdentifier: AccountCell.reuseID)

// Or a standalone view:
let view = Bundle.main.loadNibNamed("EmptyStateView", owner: self, options: nil)?.first as? UIView
```


**Then they usually ask**

- How do you load a view controller from a XIB versus from a storyboard?
- Why do cells so often live in their own XIB?
- What is a nib owner (`File's Owner`)?

</details>

<h2 id="segues">Segues</h2>

<code>Junior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **segue** is a named transition Interface Builder stores on a storyboard: show, show detail, present modally, popover, custom, or unwind. At runtime UIKit instantiates the destination, then calls `prepare(for:sender:)` on the source so you can pass data *before* the destination’s view loads. You can also fire one in code with `performSegue(withIdentifier:sender:)`. Unwind segues walk back up the presented/pushed stack to a method marked `@IBAction func unwindToX(segue:)`. They are asked less now because programmatic `push` / `present` and SwiftUI `NavigationStack` replaced most of them, but older codebases are full of identifier strings. Typical mistakes: configuring the destination in `viewDidLoad` of the *source*, and forgetting that `sender` is whatever you passed, not always a button.



```swift
override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    guard segue.identifier == "showDetail",
          let detail = segue.destination as? DetailViewController,
          let item = sender as? Item else { return }
    detail.item = item
}

func open(_ item: Item) {
    performSegue(withIdentifier: "showDetail", sender: item)
}
```


**Then they usually ask**

- When does `prepare(for:sender:)` run relative to the destination’s `viewDidLoad`?
- What is an unwind segue for?
- How do you pass data if you present in code instead?

</details>

<h2 id="view-with-tag">viewWithTag() pros and cons</h2>

<code>Junior</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`viewWithTag(_:)` walks the receiver’s subtree and returns the first `UIView` whose `tag` matches. The pro is zero outlets: Interface Builder can set an integer and you fish it out in `awakeFromNib`. The cons dominate in any real app. Tags are magic numbers, default to `0` (so an unset view can match), are not typed, and collide the moment two cells or two XIBs reuse the same integer. After reuse, the view you found may belong to a different row than you think. Prefer `@IBOutlet`, a stored subview property, or a typed `viewWithTag` wrapper only as a last resort in unowned legacy code. Interviewers want you to say “it works, I would not add it.”



```swift
// Fragile:
let label = cell.viewWithTag(12) as? UILabel
label?.text = item.title

// Prefer:
final class ItemCell: UITableViewCell {
    @IBOutlet private var titleLabel: UILabel!
    func apply(_ item: Item) { titleLabel.text = item.title }
}
```


**Then they usually ask**

- Why is tag `0` a particularly bad choice?
- What happens to tags when a cell is reused?
- How would you find a subview without tags or outlets?

</details>

### Mid

<h2 id="collection-vs-table">Collection view vs table view</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`UITableView`** is a vertical list with system cell styles, section headers/footers, swipe actions, reorder controls, and accessories. **`UICollectionView`** is a `UIScrollView` plus a **layout** object: flow, compositional, or a custom `UICollectionViewLayout`. Tables are the fastest honest answer for a settings-style list. Collections win for grids, carousels, orthogonal sections, and any mix of sizes. Compositional layout can imitate a table (`UICollectionLayoutListConfiguration`) and is what newer system apps use, so “table vs collection” is now also “do I need list chrome or a layout.” Typical mistakes: forcing a grid into a table with stacked image views, and using a collection when you only needed `UITableViewStyle.insetGrouped`.



```swift
let layout = UICollectionViewCompositionalLayout { _, _ in
    let item = NSCollectionLayoutItem(layoutSize: .init(
        widthDimension: .fractionalWidth(0.5),
        heightDimension: .fractionalWidth(0.5)
    ))
    let group = NSCollectionLayoutGroup.horizontal(
        layoutSize: .init(widthDimension: .fractionalWidth(1), heightDimension: .fractionalWidth(0.5)),
        subitems: [item, item]
    )
    return NSCollectionLayoutSection(group: group)
}
let grid = UICollectionView(frame: .zero, collectionViewLayout: layout)
```


**Then they usually ask**

- What does a compositional *list* layout give you that `UITableView` already had?
- When is a custom `UICollectionViewLayout` worth it?
- How do prefetching and diffable data sources differ between the two?
- Horizontal rail: nested collection in a table cell vs an orthogonal compositional section?

</details>

<h2 id="diffable-data-source">Diffable data source</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **diffable data source** (`UITableViewDiffableDataSource` / `UICollectionViewDiffableDataSource`) owns the snapshot: you give it a list of **hashable** section and item IDs, it diffs against the last snapshot, and it applies inserts, deletes, and moves without `performBatchUpdates` arithmetic. You still dequeue and configure the cell; you stop computing index paths by hand. Identity must be stable — if `Item` hashes on a display string that changes, rows flicker or crash. Apply snapshots on the main thread. Typical miss: mutating the backing array and calling `reloadData` “just in case,” or using the array index as the item identifier.



```swift
enum Section { case feed }

struct Post: Hashable {
    let id: UUID
    var title: String
}

var snapshot = NSDiffableDataSourceSnapshot<Section, Post>()
snapshot.appendSections([.feed])
snapshot.appendItems(posts, toSection: .feed)
dataSource.apply(snapshot, animatingDifferences: true)
```


**Then they usually ask**

- Why must the item identifier be stable across applies?
- Snapshot vs `NSFetchedResultsController` for a Core Data list?
- What still belongs in `cellProvider` vs the snapshot?
- Why does repeated `reloadData` flicker when one item changed?

</details>

<h2 id="intrinsic-content-size">Intrinsic content size</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Intrinsic content size** is the size a view wants before Auto Layout stretches or compresses it — the text size of a `UILabel`, the image size of a `UIImageView`, the title-plus-insets of a `UIButton`. A plain `UIView` reports `UIView.noIntrinsicMetric` (−1) on both axes, so it needs explicit constraints. Hugging resistance says “do not grow”; compression resistance says “do not shrink”; the higher priority wins when two views fight. You override `intrinsicContentSize` and call `invalidateIntrinsicContentSize()` when the content changes. Typical mistakes: giving a label both a fixed width and expecting wrapping without `numberOfLines = 0`, and pinning a custom view’s edges but never implementing intrinsic size so Interface Builder shows a zero frame.



```swift
final class BadgeView: UIView {
    var text = "" {
        didSet { invalidateIntrinsicContentSize() }
    }

    override var intrinsicContentSize: CGSize {
        let labelSize = (text as NSString).size(withAttributes: [.font: UIFont.systemFont(ofSize: 13)])
        return CGSize(width: labelSize.width + 16, height: 24)
    }
}
```


**Then they usually ask**

- What do content-hugging and compression-resistance priorities do?
- Why does a `UILabel` with no width constraint grow horizontally?
- When do you call `invalidateIntrinsicContentSize()`?

</details>

<h2 id="passing-data">Passing data in iOS</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Name the direction. **Down:** initializer, property, segue `prepare(for:)`, SwiftUI `init` / `@Binding`. **Up / out:** delegate, closure callback, Combine / `AsyncStream`. **Broadcast:** `NotificationCenter` when many strangers care. **Shared:** environment object, a store you inject — not `Foo.shared` unless you can explain why. Pick the narrowest channel. Typical mistake: a notification for a button that only one screen listens to, or a singleton that is really a hidden parameter.



```swift
final class DetailViewController: UIViewController {
    var item: Item!
    var onSave: ((Item) -> Void)?
}

override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    (segue.destination as? DetailViewController)?.item = selected
}
```


**Then they usually ask**

- Delegate vs closure vs notification for one event?
- How do you pass data *back* from a pushed screen?
- What changes in SwiftUI (`Binding`, environment)?

</details>

<h2 id="responder-chain">Responder chain</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The responder chain is how UIKit walks events that a view does not handle: the view → its superviews → the view controller → the window → the app. First responder is who gets keyboard and menu actions (`becomeFirstResponder`). `UIControl` actions are a different path (target-action), but unhandled motion, remote-control, and `canPerformAction` still climb the chain. That is why a `UIViewController` can implement `copy(_:)` for a child label. Typical mistake: adding a gesture that `cancelsTouchesInView` and wondering why buttons below never see the tap.



```swift
final class EditorViewController: UIViewController {
    override var canBecomeFirstResponder: Bool { true }

    override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
        action == #selector(copy(_:))
    }
}
```


**Then they usually ask**

- First responder vs next responder?
- How does a gesture recognizer interact with the chain?
- Where does a shake-to-undo event go?

</details>

<h2 id="size-classes">Size classes</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**Size classes** are a coarse trait: `horizontalSizeClass` and `verticalSizeClass` on `UITraitCollection`, each `.compact`, `.regular`, or `.unspecified`. They describe the *available* width and height, not the device name. A portrait iPhone is compact-regular; most iPhones in landscape are compact-compact; Plus/Max landscape and a full-screen iPad are regular-regular; an iPad in Split View can drop to compact width. Interface Builder variations and Auto Layout “installed” constraints key off these. In code you read `traitCollection` and react in `traitCollectionDidChange` (or `registerForTraitChanges` on modern iOS). Typical mistakes: hard-coding `UIDevice.current.userInterfaceIdiom`, treating compact as “phone”, and forgetting that a slide-over iPad app is compact.



```swift
override func traitCollectionDidChange(_ previous: UITraitCollection?) {
    super.traitCollectionDidChange(previous)
    let isWide = traitCollection.horizontalSizeClass == .regular
    stackView.axis = isWide ? .horizontal : .vertical
}
```


**Then they usually ask**

- What size classes does a full-screen iPad use versus Split View?
- How is this different from Dynamic Type / `UIContentSizeCategory`?
- How do you install different constraints for compact vs regular in a storyboard?
- Why is `UIDevice.current.orientation` a bad stand-in for size class?
- Storyboards vs traits vs constraints-in-code — how do you cover every device?

</details>

<h2 id="remote-images-table">Table view with remote images</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Three rules interviewers want in order. **1. Lazy:** start the download in `cellForRow` / `willDisplay`, not for every row in `viewDidLoad`. **2. Off the main thread:** decode on a background queue / `Task`, then hop to main to assign `image`. **`Data(contentsOf: url)` on the main thread is the classic fail** — it blocks scrolling and has no cache and no cancel. **3. Identity after reuse:** when the request finishes, the cell may now show a different row — compare the URL (or a generation token) and discard the bitmap if it does not match. Cancel in `prepareForReuse`. Cache decoded images (`NSCache`) so a scroll-back is instant. Typical miss: a beautiful spinner that still sets the wrong photo on a reused cell.



```swift
func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: PhotoCell.reuseID, for: indexPath) as! PhotoCell
    let url = items[indexPath.row].url
    cell.apply(url: url) // cancel previous, then load; ignore if url changed
    return cell
}
```


**Then they usually ask**

- What do you do if the user scrolls faster than the network?
- Memory cache vs `URLCache` for these thumbnails?
- How do you keep 60 fps while decoding JPEGs?

</details>

<h2 id="setneedslayout">setNeedsLayout vs layoutIfNeeded</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`setNeedsLayout()`** marks the view dirty; layout runs later in the turn (cheap, coalesced). **`layoutIfNeeded()`** runs layout **now** if dirty — you need the new `frame` this line (animation setup, snapshot). **`layoutSubviews()`** is the method UIKit calls; you override it, you do not call it. Typical miss: `layoutIfNeeded()` in a tight loop, or overriding `layoutSubviews` without `super`.



```swift
header.invalidateIntrinsicContentSize()
header.setNeedsLayout()
UIView.animate(withDuration: 0.25) {
    self.view.layoutIfNeeded()
}
```


**Then they usually ask**

- `setNeedsDisplay` vs `setNeedsLayout`?
- Why animate `layoutIfNeeded` and not `layoutSubviews`?
- What does `updateConstraints` add to this story?

</details>

<h2 id="child-view-controllers">Child view controllers</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A **child view controller** is a real `UIViewController` whose view you embed in a parent, using the containment API so rotation, appearance, trait, and `addChild` callbacks stay correct. The add sequence is `addChild(_:)`, add the child’s view to the hierarchy, then `didMove(toParent:)`. The remove sequence is `willMove(toParent: nil)`, remove the view, `removeFromParent()`. Skipping those calls is the bug: the child view is on screen but `viewWillAppear`, status-bar style, and `parent` are wrong. This is how custom tabs, pager containers, and “add a map VC into this card” should work — not `addSubview` of another VC’s view with no containment. `UINavigationController` and `UITabBarController` are just specialized parents.



```swift
func embed(_ child: UIViewController, in container: UIView) {
    addChild(child)
    child.view.translatesAutoresizingMaskIntoConstraints = false
    container.addSubview(child.view)
    NSLayoutConstraint.activate([
        child.view.topAnchor.constraint(equalTo: container.topAnchor),
        child.view.leadingAnchor.constraint(equalTo: container.leadingAnchor),
        child.view.trailingAnchor.constraint(equalTo: container.trailingAnchor),
        child.view.bottomAnchor.constraint(equalTo: container.bottomAnchor)
    ])
    child.didMove(toParent: self)
}
```


**Then they usually ask**

- What breaks if you `addSubview` a child’s view and never call `addChild`?
- How do you remove a child without leaking it?
- When would you use a container VC instead of a child `UIView`?

</details>

<h2 id="nested-collection">Collection view inside a table cell</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A horizontal rail in a table row is a **`UICollectionView` owned by the cell** (or a child VC). The hard parts are **reuse and layout**, not “add a collection view.” Give the inner collection a stable data source for *this* row, reset it in `prepareForReuse`, and remember the **scroll offset** if the product wants the rail to stay where the user left it. Height is usually fixed or measured once; a self-sizing inner collection that invalidates the table on every scroll is the hitch. Prefer compositional orthogonal sections when the whole screen is already a collection. Typical miss: one shared collection data source across reused cells, so rails swap content as you scroll.



```swift
final class RailCell: UITableViewCell {
    let rail = UICollectionView(frame: .zero, collectionViewLayout: RailCell.layout())
    private var items: [URL] = []

    override func prepareForReuse() {
        super.prepareForReuse()
        items = []
        rail.setContentOffset(.zero, animated: false)
        rail.reloadData()
    }
}
```


**Then they usually ask**

- Where do you store per-row scroll offsets so they survive reuse?
- Why can Auto Layout on the inner collection hitch the outer table?
- When do you switch the whole Home to compositional sections instead?

</details>

<h2 id="orientation">Device orientation</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Do not drive layout off `UIDevice.current.orientation`. Use **size** and **traits**: `viewWillTransition(to:with:)` for the new bounds, `traitCollectionDidChange` / `traitCollection.horizontalSizeClass` for compact vs regular. Auto Layout plus size classes already rotate most screens. Lock orientation per VC with `supportedInterfaceOrientations` when a camera or a game needs landscape-only. Typical miss: `if UIDevice.current.orientation == .landscapeLeft` that is wrong on iPad Split View (compact width, device still “landscape”) and wrong during an animation.



```swift
override func viewWillTransition(to size: CGSize, with coordinator: UIViewControllerTransitionCoordinator) {
    super.viewWillTransition(to: size, with: coordinator)
    coordinator.animate { _ in
        self.columns = size.width > size.height ? 3 : 1
        self.collectionView.collectionViewLayout.invalidateLayout()
    }
}
```


**Then they usually ask**

- Size class vs device orientation — which one is Split View?
- How do you lock one screen to landscape without locking the app?
- SwiftUI — `verticalSizeClass` vs reading `UIDevice`?

</details>

<h2 id="file-owner">File’s Owner</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**File’s Owner** is a **placeholder** in a nib/xib for the object that will **load** it — usually the view controller that calls `init(nibName:)` or `Bundle.loadNibNamed`. It is not an object stored in the file. Outlets and actions in the xib connect to that future instance. A wrong owner class (or a xib loaded from a view that is not the owner) means `nil` outlets. Storyboards hide this behind the scene’s view controller. Typical miss: “File’s Owner is the first view in the xib.”



```swift
// ProfileViewController is File's Owner of ProfileViewController.xib
let vc = ProfileViewController(nibName: "ProfileViewController", bundle: nil)
```


**Then they usually ask**

- Owner vs the top-level view object in the xib?
- Why can an `@IBOutlet` be `nil` after `loadNibNamed`?
- How does this differ from a storyboard scene?

</details>

<h2 id="ibdesignable">IBDesignable</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`@IBDesignable`** tells Interface Builder to compile a `UIView` subclass and instantiate it on the canvas so you see live drawing. **`@IBInspectable`** exposes selected properties in the Attributes inspector (colors, numbers, strings, images). `prepareForInterfaceBuilder()` runs only in IB, which is where you stub network calls or `UIApplication.shared`. IB builds a separate target; anything that is not visible to that target — some SPM setups, app-extension-only flags, missing assets — renders as a crash or a gray box on the canvas, not in the simulator. The feature is asked less now because SwiftUI previews cover the same job with less IB machinery. Typical mistake: putting side effects in `init(frame:)` that IB executes while you type.



```swift
@IBDesignable
final class DottedCircleView: UIView {
    @IBInspectable var lineColor: UIColor = .systemBlue {
        didSet { setNeedsDisplay() }
    }

    override func prepareForInterfaceBuilder() {
        super.prepareForInterfaceBuilder()
        backgroundColor = .clear
    }
}
```


**Then they usually ask**

- What belongs in `prepareForInterfaceBuilder()` that should not run in the app?
- Why might a view render in the simulator but crash on the canvas?
- How does `@IBInspectable` map Swift types to inspector controls?

</details>

<h2 id="memory-warning">Memory warning</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

The system tells you RAM is tight: `UIApplication.didReceiveMemoryWarningNotification` and `UIViewController.didReceiveMemoryWarning`. Drop **rebuildable** caches (decoded images, `NSCache`, a downloaded file you can fetch again). Do not drop the user’s unsaved draft. `NSCache` already evicts under pressure; your own `[URL: UIImage]` does not. On a warning, also stop speculative prefetch. Typical miss: ignoring the warning, or releasing the only copy of data you cannot recreate.



```swift
override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    imageCache.removeAllObjects()
}
```


**Then they usually ask**

- What is safe to drop vs what must be persisted first?
- How does this interact with `NSCache`?
- Jetsam vs a memory warning — which do you get first?

</details>

<h2 id="color-out-of-range">Color values outside 0...1</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`UIColor(red:green:blue:alpha:)` takes **`CGFloat` components in 0...1**, not 0...255. Values below 0 become 0; values above 1 become 1. Passing `red: 255` therefore does not make “web red” — it clamps to 1 and you get a fully saturated channel (often an accidental white if every channel was 255). The 0...255 scale belongs in `UIColor(red: 255/255, green: 0, blue: 0, alpha: 1)` or in asset catalogs. Wide-gamut initializers such as `UIColor(displayP3Red:green:blue:alpha:)` can represent colors that, when converted to sRGB, have components **outside** 0...1; `getRed(_:green:blue:alpha:)` may then return numbers you would not feed back into the sRGB initializer. Interviewers are usually fishing for the clamp and the 255 mistake, then for Display P3 if you go deeper.



```swift
let wrong = UIColor(red: 255, green: 0, blue: 0, alpha: 1)   // clamped → not "255 red"
let sRGB = UIColor(red: 255 / 255, green: 0, blue: 0, alpha: 1)
let p3 = UIColor(displayP3Red: 1, green: 0, blue: 0, alpha: 1)
```


**Then they usually ask**

- What color do you actually get from `UIColor(red: 255, green: 128, blue: 0, alpha: 1)`?
- When can `getRed` return a component greater than 1?
- Why do asset catalogs avoid this class of bug?

</details>

<h2 id="uicontrol-target-nil">UIControl target is nil</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

`addTarget(nil, action: #selector(foo), for: .touchUpInside)` does not mean “no one hears this.” A **nil target** walks the **responder chain** until something implements `foo`. That is how a button in a cell can call an action on the view controller without an explicit target. If nobody implements it, nothing happens (no crash). Prefer an explicit target in new code — nil-target is clever and hard to grep. Typical mistake: thinking nil target disables the control.



```swift
button.addTarget(nil, action: #selector(EditorViewController.save), for: .touchUpInside)
```


**Then they usually ask**

- How is this different from `addTarget(self, ...)`?
- Why is it hard to debug a nil-target action?
- What replaced a lot of this in SwiftUI?

</details>

<h2 id="menu-controller">UIMenuController</h2>

<code>Mid</code> · <code>Low</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

**`UIMenuController`** is the old floating Edit menu (Cut, Copy, Paste, and custom `UIMenuItem`s). The view must be able to become first responder (`canBecomeFirstResponder` + `becomeFirstResponder`), you implement `canPerformAction(_:withSender:)` and the matching `@objc` methods, then call `showMenu(from:rect:)`. It is **deprecated since iOS 16**. New code should use `UIEditMenuInteraction` for the selection menu and `UIContextMenuInteraction` / `contextMenuConfigurationForItemsAt` for long-press actions. Interviews still bring it up because text views and WebViews historically depended on it, and because “make this label copyable” was a common take-home. Typical mistake: adding menu items but never making the view first responder, so the menu never appears.



```swift
final class CopyableLabel: UILabel {
    override var canBecomeFirstResponder: Bool { true }

    override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
        action == #selector(copy(_:))
    }

    override func copy(_ sender: Any?) {
        UIPasteboard.general.string = text
    }
}
```


**Then they usually ask**

- What replaced `UIMenuController` on iOS 16 and later?
- Why must the view become first responder?
- How do you add a custom item next to Copy?

</details>
