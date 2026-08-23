# Accessibility

5 карточек · 4 часто спрашивают · [accessibility.md](../../topics/accessibility.md)

### Junior

<h2 id="dynamic-type">Dynamic Type</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Dynamic Type — системный размер текста. Входишь текстовыми стилями: UIFont.preferredFont(forTextStyle:), в SwiftUI font(.body) — и на UIKit-лейблах ставишь adjustsFontForContentSizeCategory. Фиксированный systemFont размера 14 не вырастет. Лейаут должен уметь расти: без фиксированной высоты на лейблах, лучше перенос, чем ужатие; adjustsFontSizeToFitWidth — крайняя мера. В SwiftUI @ScaledMetric и scaledToFit помогают картинкам и отступам ехать за той же настройкой. Тестируй на самых больших accessibility-размерах, не только на Large — там обрезанные цены и срезанные кнопки.



```swift
titleLabel.font = .preferredFont(forTextStyle: .headline)
titleLabel.adjustsFontForContentSizeCategory = true
titleLabel.numberOfLines = 0

// SwiftUI
Text(title)
    .font(.headline)
    .dynamicTypeSize(...DynamicTypeSize.accessibility3)
```


**Потом обычно спрашивают**

- Почему лейбл из storyboard с кастомным шрифтом игнорирует размер пользователя?
- Как скелить кастомный шрифт и всё равно ехать за Dynamic Type?
- Что ломается первым на AX3 — и как пересобрать, а не ужимать текст?
- Чем SwiftUI dynamicTypeSize отличается от просто текстового стиля?

</details>

### Mid

<h2 id="accessibility-problems">Главные проблемы accessibility</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

То, что реально валит VoiceOver и ревью App Store, одно и то же: иконки-кнопки без лейбла, информация только цветом, таргеты меньше 44pt, порядок фокуса не совпадает с визуальным чтением, кастомные контролы без traits. Дальше — обрезка Dynamic Type и текст, который наезжает на AX-размерах. Декоративные картинки, которые всё равно говорят «img_header_03», и модальный UI, который не затаскивает фокус VoiceOver в шит. Сначала поверхность API — лейблы, traits, группировка, accessibilityViewIsModal — потом лейаут. Контраст цвета и Reduce Motion — отдельные проверки: пройти VoiceOver не значит пройти их.



Spoken audit of one screen:

1. Icon-only buttons: give each a label, not the asset name.
2. Status shown as a red/green dot: add text or `accessibilityValue` (“out of stock”).
3. Swipe cell actions: expose them as custom actions, not only as a hidden swipe.
4. Sheet: set `accessibilityViewIsModal` so VoiceOver cannot escape into the dimmed parent.


**Потом обычно спрашивают**

- Как отдать VoiceOver действие swipe-to-delete?
- Что такое таргет 44pt в плотном списке SwiftUI и как его вырастить, не разнеся дизайн?
- Как сохранить смысл, если на цвет нельзя опираться?
- Что поймает Accessibility Inspector, а что только проход VoiceOver?

</details>

<h2 id="voiceover">Тестировать с VoiceOver</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

VoiceOver — скринридер; тестируешь приложением с глазами не на стекле, а не взглядом на accessibilityLabel в дебаггере. Включаешь в Настройки → Универсальный доступ или берёшь Accessibility Inspector и VoiceOver симулятора Xcode: ротор, свайп, double-tap. У каждого контрола должно быть произносимое имя — accessibilityLabel, роль — accessibilityTraits, и значение, когда имени мало — accessibilityValue. Визуальный кластер группируй accessibilityElement(children: .combine) или shouldGroupAccessibilityChildren, чтобы человек не слушал двадцать крошечных вью. Кастомные контролы обязаны реализовать accessibilityActivate и объявлять изменения через UIAccessibility.post с announcement. Если у жеста нет эквивалента VoiceOver — фича не доделана.



```swift
button.accessibilityLabel = "Add to bag"
button.accessibilityHint = "Adds the current size to your bag"
button.accessibilityTraits.insert(.button)

card.isAccessibilityElement = true
card.accessibilityLabel = "Navy hoodie, 80 dollars, in stock"
card.accessibilityTraits = .button
```

Spoken pass: turn VoiceOver on, swipe through the screen, and confirm order, names, and that double-tap does the same work as a tap.


**Потом обычно спрашивают**

- Как починить кастомный UIView, который VoiceOver пропускает или дробит в шум?
- Когда постить layoutChanged, announcement, screenChanged?
- Что ротор меняет в том, как отдаёшь заголовки и ссылки?
- Как регрессионно гонять VoiceOver без полного ручного прохода на каждый PR?
- Label и value на слайдере — что говорит VoiceOver и что меняется?
- Custom actions и обучение свайпу — какой API и как человек это найдёт?
- После появления шита — как двигаешь фокус: UIAccessibility.post или @AccessibilityFocusState?

</details>

<h2 id="accessibility-focus">Фокус accessibility в SwiftUI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

@AccessibilityFocusState — курсор VoiceOver / Switch Control, не клавиатурный @FocusState. Биндишь Bool или optional enum через accessibilityFocused, потом присваиваешь после шита, результата поиска или ошибки валидации, чтобы произносимый курсор сел на новую работу. UIAccessibility.post со screenChanged / layoutChanged — двоюродный брат в UIKit, когда ты не в SwiftUI. Ограничь обёртку @AccessibilityFocusState(for: .voiceOver), если Switch Control должен остаться на месте. Типичный промах: подвинуть клавиатурный фокус и решить, что VoiceOver пошёл следом, или запостить announcement, когда человеку надо, чтобы ротор прыгнул на поле.



```swift
enum Field: Hashable { case email, password }

@AccessibilityFocusState private var focus: Field?

TextField("Email", text: $email)
    .accessibilityFocused($focus, equals: .email)

.onChange(of: submitted) { _, ok in
    if !ok { focus = .email }
}
```


**Потом обычно спрашивают**

- @FocusState и @AccessibilityFocusState — могут разойтись?
- После модалки — присвоение в onAppear или UIAccessibility.post?
- Почему enum optional?

</details>

<h2 id="accessibility-accommodations">Настройки accessibility</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Accommodations — системные настройки, которые UI должен чтить: Reduce Motion, Increase Contrast, Bold Text, Reduce Transparency, Smart Invert, Closed Captions, Switch Control, Voice Control и крупные размеры Dynamic Type. Читаешь через UIAccessibility — isReduceMotionEnabled, isDarkerSystemColorsEnabled — или SwiftUI Environment accessibilityReduceMotion. Не вези зацикленную hero-анимацию, если Reduce Motion включён: статичный кадр или cross-fade. Семантические цвета и системные материалы, чтобы Increase Contrast и Dark Mode продолжали работать. Подписывайся на нотификации UIAccessibility / reduceMotionStatusDidChangeNotification — люди переключают это, пока приложение открыто. Accommodations — не второе приложение, а ветки в том же лейауте.



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


**Потом обычно спрашивают**

- Какие анимации надо выключить или заменить при Reduce Motion?
- Как Smart Invert живёт с ассетами — accessibilityIgnoresInvertColors?
- Что Switch Control нужно от контролов сверх того, что уже есть у VoiceOver?
- Как тестировать Increase Contrast, не гадая hex?

</details>
