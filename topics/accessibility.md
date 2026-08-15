# Accessibility

- [Testing with VoiceOver](#voiceover)
- [Accessibility focus in SwiftUI](#accessibility-focus)
- [Dynamic Type](#dynamic-type)
- [Main accessibility problems to solve](#accessibility-problems)
- [Accessibility accommodations](#accessibility-accommodations)

## Testing with VoiceOver {#voiceover}

- Level: Mid
- Frequency: High

### Answer

VoiceOver is the screen reader; you test by using the app with your eyes off the glass, not by glancing at `accessibilityLabel` in the debugger. Enable it in Settings → Accessibility, or use the Accessibility Inspector and the Xcode simulator’s VoiceOver (rotor, swipe, double-tap). Every control needs a spoken name (`accessibilityLabel`), a role (`accessibilityTraits`), and a value when the name is not enough (`accessibilityValue`). Group a visual cluster with `accessibilityElement(children: .combine)` or `shouldGroupAccessibilityChildren` so the user does not hear twenty tiny views. Custom controls must implement `accessibilityActivate()` and announce changes with `UIAccessibility.post(notification: .announcement, ...)`. If a gesture has no VoiceOver equivalent, the feature is not done.

### Example

```swift
button.accessibilityLabel = "Add to bag"
button.accessibilityHint = "Adds the current size to your bag"
button.accessibilityTraits.insert(.button)

card.isAccessibilityElement = true
card.accessibilityLabel = "Navy hoodie, 80 dollars, in stock"
card.accessibilityTraits = .button
```

Spoken pass: turn VoiceOver on, swipe through the screen, and confirm order, names, and that double-tap does the same work as a tap.

### Follow-ups

- How do you fix a custom `UIView` that VoiceOver skips or splits into noise?
- When do you post `.layoutChanged` vs `.announcement` vs `.screenChanged`?
- What does the rotor change about how you should expose headings and links?
- How do you regression-test VoiceOver without doing a full manual pass every PR?
- Label vs value on a slider — what does VoiceOver speak, and which one changes?
- Custom actions vs teaching a swipe gesture — which API, and how does the user find it?
- After a sheet appears — how do you move focus (`UIAccessibility.post` vs `@AccessibilityFocusState`)?

## Accessibility focus in SwiftUI {#accessibility-focus}

- Level: Mid
- Frequency: High

### Answer

`@AccessibilityFocusState` is the VoiceOver / Switch Control cursor, not keyboard `@FocusState`. Bind a `Bool` or an optional `enum` with `.accessibilityFocused($focus, equals: .email)`, then **assign** after a sheet, a search result, or a validation error so the spoken cursor lands on the new work. `UIAccessibility.post(.screenChanged / .layoutChanged)` is the UIKit cousin — use it when you are not in SwiftUI. Limit the wrapper with `@AccessibilityFocusState(for: .voiceOver)` if Switch Control should stay put. Typical miss: moving keyboard focus and thinking VoiceOver followed, or posting `.announcement` when the user needed the rotor to jump to a field.

### Example

```swift
enum Field: Hashable { case email, password }

@AccessibilityFocusState private var focus: Field?

TextField("Email", text: $email)
    .accessibilityFocused($focus, equals: .email)

.onChange(of: submitted) { _, ok in
    if !ok { focus = .email }
}
```

### Follow-ups

- `@FocusState` vs `@AccessibilityFocusState` — can they disagree?
- After a modal appears — assignment on `onAppear` vs `UIAccessibility.post`?
- Why is the enum optional?

## Dynamic Type {#dynamic-type}

- Level: Junior
- Frequency: High

### Answer

Dynamic Type is the system text-size setting. You opt in by using text styles (`UIFont.preferredFont(forTextStyle:)`, SwiftUI `.font(.body)`) and setting `adjustsFontForContentSizeCategory = true` on UIKit labels. Fixed `UIFont.systemFont(ofSize: 14)` will not grow. Layout must be allowed to grow: avoid fixed heights on labels, prefer wrapping over shrinking, and use `adjustsFontSizeToFitWidth` only as a last resort. In SwiftUI, `@ScaledMetric` and `scaledToFit` help images and spacing track the same setting. Test at the largest accessibility sizes, not just “Large” — that is where truncated prices and clipped buttons show up.

### Example

```swift
titleLabel.font = .preferredFont(forTextStyle: .headline)
titleLabel.adjustsFontForContentSizeCategory = true
titleLabel.numberOfLines = 0

// SwiftUI
Text(title)
    .font(.headline)
    .dynamicTypeSize(...DynamicTypeSize.accessibility3)
```

### Follow-ups

- Why does a storyboard label with a custom font ignore the user’s size?
- How do you scale a custom font and still track Dynamic Type?
- What breaks first at AX3 — and how do you redesign instead of shrinking text?
- How does SwiftUI `dynamicTypeSize` differ from just using a text style?

## Main accessibility problems to solve {#accessibility-problems}

- Level: Mid
- Frequency: High

### Answer

The problems that actually fail VoiceOver and App Store review are consistent: unlabeled icon buttons, information that exists only as color, hit targets under 44pt, focus order that does not match the visual reading order, and custom controls with no traits. Dynamic Type clipping and text that overlaps at AX sizes are the next bucket. Decorative images that still speak (“img_header_03”) and modal UI that does not move VoiceOver focus into the sheet are close behind. Fix the API surface first — labels, traits, grouping, `accessibilityViewIsModal` — then the layout. Color contrast and Reduce Motion are separate checks; passing VoiceOver does not mean you passed those.

### Example

Spoken audit of one screen:

1. Icon-only buttons: give each a label, not the asset name.
2. Status shown as a red/green dot: add text or `accessibilityValue` (“out of stock”).
3. Swipe cell actions: expose them as custom actions, not only as a hidden swipe.
4. Sheet: set `accessibilityViewIsModal` so VoiceOver cannot escape into the dimmed parent.

### Follow-ups

- How do you expose a swipe-to-delete action to VoiceOver?
- What is a 44pt target in a dense SwiftUI list, and how do you grow it without wrecking the design?
- How do you keep meaning when you cannot rely on color?
- Which of these will Accessibility Inspector catch vs only a VoiceOver pass?

## Accessibility accommodations {#accessibility-accommodations}

- Level: Mid
- Frequency: Medium

### Answer

Accommodations are the system settings your UI should respect: Reduce Motion, Increase Contrast, Bold Text, Reduce Transparency, Smart Invert, Closed Captions, Switch Control, Voice Control, and the larger Dynamic Type sizes. Read them through `UIAccessibility` (`isReduceMotionEnabled`, `isDarkerSystemColorsEnabled`, …) or SwiftUI `@Environment(\.accessibilityReduceMotion)`. Do not ship a looping hero animation if Reduce Motion is on; swap it for a static frame or a cross-fade. Prefer semantic colors and system materials so Increase Contrast and Dark Mode keep working. Subscribe to `UIAccessibility.notification` / `reduceMotionStatusDidChangeNotification` — users toggle these while the app is open. Accommodations are not a second app; they are branches in the same layout.

### Example

```swift
func playHero() {
    if UIAccessibility.isReduceMotionEnabled {
        imageView.image = heroStill
        return
    }
    imageView.startAnimating()
}

// SwiftUI
@Environment(\.accessibilityReduceMotion) private var reduceMotion
@Environment(\.legibilityWeight) private var legibilityWeight
```

### Follow-ups

- Which animations must you disable or replace under Reduce Motion?
- How do Smart Invert and your image assets interact (`accessibilityIgnoresInvertColors`)?
- What does Switch Control need from your controls that VoiceOver already has?
- How do you test Increase Contrast without guessing at hex values?
