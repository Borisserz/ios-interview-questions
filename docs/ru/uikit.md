# UIKit

46 карточек · 23 часто спрашивают · [uikit.md](../../topics/uikit.md)

### Junior

<h2 id="iboutlet-vs-ibaction">@IBOutlet и @IBAction</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`@IBOutlet` помечает свойство, которое Interface Builder может связать с объектом на канвасе: лейбл, constraint, целую view. `@IBAction` помечает метод, который IB вешает на событие контрола (`touchUpInside`, `editingChanged`, action жеста). Outlet почти всегда `weak` и implicitly unwrapped: storyboard владеет view; свойство nil, пока nib не загрузился, потом оно должно быть, иначе краш на первом обращении. Action принимает sender (`Any` или типизированный `UIButton`) и иногда event. Один контрол на два action — нормально. Outlet не того типа — падение в runtime. Типичные ошибки: `strong` outlet, которые удивляют в ячейках, и логика в action, которой место в view model.



```swift
final class LoginViewController: UIViewController {
    @IBOutlet private weak var emailField: UITextField!
    @IBOutlet private weak var loginButton: UIButton!

    @IBAction private func loginTapped(_ sender: UIButton) {
        submit(email: emailField.text)
    }
}
```


**Потом обычно спрашивают**

- Почему outlet обычно `weak`?
- Когда оправдан `strong` outlet?
- Что будет, если связь outlet в storyboard оборвалась?
- `strong` `@IBOutlet` всегда утечка, или только когда граф view уже им владеет?

</details>

<h2 id="aspect-fill-vs-fit">Aspect fill и aspect fit</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Оба — значения `UIView.ContentMode`, оба сохраняют пропорции картинки. `scaleAspectFit` масштабирует, пока картинка целиком влезает в bounds; остаток пустой, это letterboxing. `scaleAspectFill` масштабирует, пока bounds полностью закрыты. Лишнее рисуется за краями, кроп виден только если `clipsToBounds` true. Fit — для логотипов и всего, что нельзя резать. Fill — для аватарки и hero-фото. `scaleToFill` (дефолт у `UIImageView`) растягивает и искажает. Это третий вариант, который ждут услышать. Типичная ошибка: aspect fill без клипа, и картинка рисуется поверх соседних view.



```swift
avatarView.contentMode = .scaleAspectFill
avatarView.clipsToBounds = true

logoView.contentMode = .scaleAspectFit
logoView.clipsToBounds = false
```


**Потом обычно спрашивают**

- Что дефолтный `scaleToFill` делает с картинкой не тех пропорций?
- Как это рифмуется со SwiftUI `AspectRatio` / `scaledToFill()`?
- Когда взять `center` или `top` вместо scale-режима?

</details>

<h2 id="auto-layout-anchors">Auto Layout anchors</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Auto Layout — солвер constraints: описываешь отношения, UIKit считает frames. Так один layout переживает iPhone и iPad, поворот, Dynamic Type и клавиатуру. Size classes и trait collections — грубый переключатель regular / compact. Constraints — мелкие правила. Anchors (`NSLayoutAnchor`) — типизированный способ писать эти правила: `leadingAnchor`, `trailingAnchor`, `topAnchor`, `bottomAnchor`, `centerXAnchor`, `widthAnchor`. На каждой view, которую констрейнишь в коде, ставь `translatesAutoresizingMaskIntoConstraints = false`. Иначе UIKit ещё навесит autoresizing constraints и полезут unsatisfiable логи. Активируй пачкой через `NSLayoutConstraint.activate`, чтобы движок решил один раз. Бери у superview `safeAreaLayoutGuide` и, где уместно, `readableContentGuide` / `keyboardLayoutGuide`, не сырой `view.topAnchor`. Типичные ошибки: констрейнить view до того, как у неё появился superview; мешать frames и constraints на одной view; активировать один constraint дважды.



```swift
button.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(button)
NSLayoutConstraint.activate([
    button.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 16),
    button.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor, constant: -16),
    button.bottomAnchor.constraint(equalTo: view.keyboardLayoutGuide.topAnchor, constant: -12)
])
```


**Потом обычно спрашивают**

- Что будет, если оставить `translatesAutoresizingMaskIntoConstraints` как `true`?
- Когда брать `safeAreaLayoutGuide`, а когда собственные anchors view?
- Как временно выключить constraint?
- Auto Layout, frames, SwiftUI layout — когда что всё ещё берёшь?

</details>

<h2 id="dark-mode">Dark Mode</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Dark Mode — trait: `userInterfaceStyle` это `.light` или `.dark`. Бери dynamic colors (`.label`, `.systemBackground`, `.secondaryLabel`) и варианты картинок в asset catalog, чтобы UIKit / SwiftUI сами переключались. Хардкод `UIColor.white` на лейбле в тёмной теме провалится. Оверрайд на экран через `overrideUserInterfaceStyle` только если продукт требует зафиксированный хром: камера, киноплеер. Наблюдай в `traitCollectionDidChange` (UIKit) или `@Environment(\.colorScheme)` (SwiftUI). Типичный промах: свой hex, который нормален в light и пропадает в dark, или форс `.dark` на window «под бренд» и сломанные системные алерты.



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


**Потом обычно спрашивают**

- Почему тень из `CGColor` остаётся чёрной после смены режима?
- Appearances в asset catalog или runtime `if colorScheme == .dark`?
- Как snapshot-тестить оба appearance?

</details>

<h2 id="modal-vs-push">Modal или push</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Push кладёт view controller на стек `UINavigationController`. Тот же флоу, кнопка Back, можно pop. Present (`present(_:animated:)`) кладёт новый VC поверх текущего: sheet, full-screen, popover. Presenter живёт под ним, ты `dismiss`. Push — «глубже в этот раздел». Modal — замкнутая задача: написать, заплатить, залогиниться, фильтр. Ей не нужен back stack. У modal внутри может быть свой nav controller, если в задаче два шага. Типичный промах: present, когда юзер ждал Back, или push логина, с которого нельзя pop, не оставив предыдущий экран висеть.



```swift
// Drill-down
navigationController?.pushViewController(DetailViewController(item: item), animated: true)

// Task
let compose = UINavigationController(rootViewController: ComposeViewController())
compose.modalPresentationStyle = .formSheet
present(compose, animated: true)
```


**Потом обычно спрашивают**

- `.pageSheet` и `.fullScreen` — что делает свайп вниз?
- Как вернуть результат с modal без синглтона?
- Можно ли push на VC, который не внутри navigation controller?

</details>

<h2 id="reuse-identifiers">Reuse identifiers у ячеек</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Table и collection view держат маленький пул ячеек и переиспользуют их при скролле. Reuse identifier — ключ этого пула: `register` класс или nib на ID, потом `dequeueReusableCell` с тем же ID. Несовпадение крашит (`unable to dequeue a cell with identifier`). После dequeue в ячейке ещё текст, картинки и accessory прошлой строки. `prepareForReuse` и твой configure должны сбросить всё, что не собираешься оставлять. Diffable data source тоже использует identifiers. Меняется только то, как применяешь snapshot. Типичные ошибки: register в ячейке, dequeue с другой строкой, и без сброса картинки «текут» между рядами.



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


**Потом обычно спрашивают**

- Что класть в `prepareForReuse`, а что в `cellForRowAt`?
- Почему `dequeueReusableCell(withIdentifier:for:)` требует предварительный `register`?
- Как в одном списке держать два типа ячеек?

</details>

<h2 id="safe-area">Safe area</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Safe area — прямоугольник, который не перекрыт статус-баром, вырезом / Dynamic Island, home indicator или navigation / tab / toolbar. Пинь к `safeAreaLayoutGuide`. В SwiftUI `safeAreaInset`, ignore только когда правда нужен full-bleed фон. Layout guide едет, когда появляются бары, при повороте, когда приезжает клавиатура или additional safe-area insets. Типичный промах: припинить title к `view.topAnchor` и смотреть, как он сидит под вырезом, или заменить понимание гайда на `edgesForExtendedLayout = []`.



```swift
title.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    title.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
    title.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor, constant: 16),
])
```


**Потом обычно спрашивают**

- Safe area, layout margins и `readableContentGuide`?
- Как нарисовать фон от края до края, а лейбл оставить в safe area?
- Какой extra inset даёт клавиатура или additional safe-area inset?

</details>

<h2 id="storyboards-vs-code">Storyboard или вёрстка в коде</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Storyboard — визуальный граф сцен, segue и Auto Layout. Interface Builder компилирует его в приложение. Вёрстка в коде значит: создаёшь view, ставишь `translatesAutoresizingMaskIntoConstraints = false` и активируешь constraints (или ставишь frames) в `loadView` / `viewDidLoad`. На собеседовании хотят trade-off, не религию. Storyboard быстрый для первого экрана и для тех, кто думает картинкой. Но мержится плохо, баги прячутся до runtime (`@IBOutlet` опечатки, нет ID), в pull request его почти не читают. Код многословный, канваса нет, зато дифф чистый, легко генерить в цикле и везде одинаково в любом модуле. Смешанные приложения нормальны: storyboard на простой флоу, programmatic layout на переиспользуемые контролы и всё, что пляшет от стейта. Типичная ошибка: считать «мы на storyboard» архитектурой, а не способом доставки.



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


**Потом обычно спрашивают**

- Как инстанцировать view controller, который живёт на storyboard?
- Что ломается при git merge storyboard?
- Когда всё равно возьмёшь XIB, а не то и не другое?

</details>

<h2 id="uiimage-vs-uiimageview">UIImage и UIImageView</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIImage` — данные картинки: битмап, символ или named asset. Её нет в иерархии, нет frame, её могут шарить много view. `UIImageView` — `UIView`, которая рисует `UIImage` (или последовательность анимации) по `contentMode`, tint и highlighted. Грузишь `UIImage(named:)` или `UIImage(systemName:)`, потом присваиваешь `imageView.image`. Пиксели меняешь новым `UIImage`. Кроп и выравнивание меняешь у view. Типичные ошибки: сделать `addSubview` на `UIImage` и собирать огромные картинки на main thread без учёта `@2x` / `@3x`.



```swift
let icon = UIImage(systemName: "star.fill")
let imageView = UIImageView(image: icon)
imageView.contentMode = .scaleAspectFit
imageView.tintColor = .systemYellow
view.addSubview(imageView)
```


**Потом обычно спрашивают**

- Куда смотрит `UIImage(named:)`, и кэширует ли он?
- Как показать template-картинку, которая красится в `tintColor`?
- Зачем у `UIImageView` есть `animationImages`?

</details>

<h2 id="navigation-controller">UINavigationController</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Navigation controller владеет стеком view controllers. `push` / `pop` и `setViewControllers` меняют стек. Nav bar показывает title верхнего и back item. Это контейнер: он не рисует твой экран, он его хостит. Данные передавай в initializer следующего VC, не копайся в `viewControllers`. Типичный промах: push из ячейки с протухшим index или present nav controller, когда хотел push в уже существующий.



```swift
let detail = DetailViewController(item: item)
navigationController?.pushViewController(detail, animated: true)
```


**Потом обычно спрашивают**

- Push или present — когда modal правильный ход?
- Как pop до конкретного VC, не пересобирая стек?
- Что даёт `UINavigationControllerDelegate` (кастомный transition)?

</details>

<h2 id="stack-view">UIStackView</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIStackView` — Auto Layout для ряда или колонки: `axis`, `spacing`, `alignment`, `distribution` и `isLayoutMarginsRelativeArrangement`. Он не рисует. Только создаёт constraints между arranged subviews. Спрятать ребёнка (`isHidden = true`) — схлопнется его место. Вложенные стеки лучше паутины equal-width constraints. Типичный промах: ждать, что стек заскроллится (оберни в scroll view), или ставить frames arranged view.



```swift
let stack = UIStackView(arrangedSubviews: [icon, title, spacer])
stack.axis = .horizontal
stack.spacing = 8
stack.alignment = .center
stack.distribution = .fill
```


**Потом обычно спрашивают**

- `fill`, `fillEqually` и `equalSpacing`?
- Почему `isHidden` у arranged view меняет layout?
- Стек или constraints руками — когда перестаёшь вкладывать?

</details>

<h2 id="frame-vs-bounds">frame и bounds</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`frame` — прямоугольник view в координатах superview: origin плюс size. `bounds` — тот же размер в собственном пространстве view. Origin обычно `.zero`, пока не заскроллил или не выставил сам. `CGAffineTransform` (поворот, скейл) меняет, как выглядит `frame`. `bounds.size` остаётся нетрансформированным размером. Scroll view двигает `bounds.origin`, чтобы показать контент. Auto Layout пишет `frame` после layout. Типичная ошибка: ставить `frame` у трансформированной view и удивляться прыжку, или брать `frame` внутри `draw(_:)` вместо `bounds`.



```swift
let child = UIView(frame: CGRect(x: 40, y: 80, width: 100, height: 50))
parent.addSubview(child)
child.frame.origin   // (40, 80) in parent
child.bounds.origin  // (0, 0) in itself
child.transform = CGAffineTransform(rotationAngle: .pi / 8)
// frame is now a larger axis-aligned box; bounds.size is still 100×50
```


**Потом обычно спрашивают**

- Почему `UIScrollView` меняет `bounds.origin`, когда скроллишь?
- После transform с поворотом какой размер брать для hit-testing, а какой для отрисовки?
- Когда `center` удобнее, чем `frame.origin`?

</details>

<h2 id="prepare-for-reuse">prepareForReuse</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Table/collection view зовёт `prepareForReuse` прямо перед тем, как ячейка выходит из пула reuse на новый index path. Сбрасывай транзиентный UI: отмени загрузку картинки в полёте, почисти `imageView.image`, спрячь accessory, сними highlight, инвалидируй таймер. Не конфигурируй новый ряд здесь. Модели ещё нет, это `cellForRowAt` / твой `apply(_:)`. Super вызвать надо. Классическое протекание: completion отменённого запроса всё равно ставит картинку на переиспользованную ячейку. Лови generation token или URL и игнорируй устаревшие колбэки.



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


**Потом обычно спрашивают**

- Почему новую модель не присваивают внутри `prepareForReuse`?
- Как игнорировать поздний колбэк картинки после reuse?
- Есть ли та же проблема у SwiftUI `List`?

</details>

<h2 id="viewcontroller-lifecycle">Жизненный цикл UIViewController</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`init` / `init(coder:)` создают объект, view ещё нет. `loadView` собирает корневую view. Оверрайдь только если нет storyboard и дефолта `loadViewIfNeeded`. `viewDidLoad` — первый момент, когда `view` есть: сабвью, constraints, разовая настройка. `viewWillAppear` / `viewDidAppear` бегут каждый раз, когда экран выходит на сцену: таймеры, refresh. `viewWillDisappear` / `viewDidDisappear` — пара, чтобы остановить работу. `viewWillLayoutSubviews` / `viewDidLayoutSubviews` при смене bounds. Frame-математика туда, не в `viewDidLoad`. Appearance может стрельнуть不止 один раз: переключение таба, split view, перекрыли экраном. Удалённые данные: почти статичный payload можно стартовать в `viewDidLoad` и кэшировать. Всё, что протухает, клади в `viewWillAppear` или pull-to-refresh. В любом случае fetch не на main thread и cancel, когда экран уходит. Типичная ошибка: сеть в `viewDidLoad` без cancel в `viewWillDisappear`, или constraints в `viewDidAppear`.



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


**Потом обычно спрашивают**

- `viewDidLoad` и `viewWillAppear` — что куда класть?
- Когда `viewDidLayoutSubviews` правильное место для frame градиента?
- Как containment и `addChild` меняют порядок?
- `viewDidLoad` или `viewDidAppear` для удалённой ленты — что, и почему async?
- Стартовал segue A→B и отменил. Какие методы жизненного цикла уже успели пробежать?

</details>

<h2 id="autolayout-formula">Формула Auto Layout</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Каждый constraint — это `item1.attribute = multiplier × item2.attribute + constant`, плюс отношение `=`, `≥`, `≤` и priority. Anchors — та же формула: `title.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16)` это multiplier 1, constant 16. Required constraint имеет priority 1000. Диапазон 1…999 — optional: если система unsatisfiable, движок сначала сбрасывает самый низкий priority. Неоднозначность ломаешь hugging / compression или лишним constraint с 999, «хорошо бы такая ширина». Типичный промах: два required equal-width, которые дерутся, или забыть, что в формуле есть multiplier (aspect ratio).



```swift
// width = 2 * height + 0
box.widthAnchor.constraint(equalTo: box.heightAnchor, multiplier: 2)
```


**Потом обычно спрашивают**

- Что меняет priority 999?
- Как записать «не меньше 16 pt от safe area»?
- Intrinsic size против явного width constraint — кто победит?

</details>

<h2 id="gesture-recognizers">Gesture recognizers</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIGestureRecognizer` превращает touches в действие верхнего уровня: tap, pan, pinch, swipe, long-press, rotation, screen-edge. Вешаешь на view. Он ходит по responder chain. Жесты могут fail, require, чтобы другой упал, или работать simultaneously. Так сосуществуют pan и tap. `cancelsTouchesInView` глушит контрол под ним. Типичный промах: тап по `UIButton` не стреляет, потому что родительский pan его съел, или жест на view с `isUserInteractionEnabled == false`.



```swift
let tap = UITapGestureRecognizer(target: self, action: #selector(tapped))
tap.numberOfTapsRequired = 2
imageView.isUserInteractionEnabled = true
imageView.addGestureRecognizer(tap)
```


**Потом обычно спрашивают**

- Как дать одновременно работать pan таблицы и swipe ячейки?
- Жест или target-action у `UIControl`?
- Что чинит `require(toFail:)`?

</details>

<h2 id="launch-screen">Launch screen</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Launch screen — статичный storyboard (`UILaunchStoryboardName`), который система показывает, пока процесс ещё не встал. Никакого кастомного класса, сети, анимации, кода в `viewDidLoad`. Система делает snapshot. Launch storyboard один. Light/dark идут через asset catalog и trait variations, не через два storyboard, которые меняешь в коде. Типичный промах: спиннер, который должен крутиться, или путать это с `didFinishLaunching`.



```xml
<!-- Info.plist -->
<key>UILaunchStoryboardName</key>
<string>LaunchScreen</string>
```


**Потом обычно спрашивают**

- Можно ли менять лейблы launch screen в runtime?
- Почему «неправильный» launch screen висит после обновления?
- Launch screen или брендированный splash-`UIViewController`, который сам презентишь?

</details>

<h2 id="points-vs-pixels">Points и pixels</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Вёрстка UIKit идёт в points. Point — единица, независимая от плотности. На 3× девайсе 1 point это 3 pixels. `UIScreen.main.scale` или `traitCollection.displayScale` у view — этот коэффициент. Картинки кладут `@2x` / `@3x`, чтобы оставались резкими. Почти никогда не верстаешь в pixels. Pixels нужны, когда говоришь с битмапами Core Graphics или форматом `UIGraphicsImageRenderer`. Типичный промах: делить frame на `scale` «чтобы получить points», хотя он уже в points.



```swift
let scale = view.traitCollection.displayScale
let pixels = CGSize(width: view.bounds.width * scale, height: view.bounds.height * scale)
```


**Потом обычно спрашивают**

- Почему кнопка 44 pt на iPhone это не 44 px?
- `UIImage.size` — points или pixels?
- Когда pixels всё ещё важны?

</details>

<h2 id="storyboard-identifiers">Storyboard identifiers</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Storyboard ID — строка в Identity inspector, чтобы инстанцировать сцену без segue: `storyboard.instantiateViewController(withIdentifier:)`. Это не segue identifier, не cell reuse identifier и не restoration identifier. Четыре разные строки, четыре разных краша, если перепутать. Нет ID или опечатка — `instantiateViewController` бросает, а старый API абортит. Класс как ID — частая конвенция, строка живёт в одном месте. Типичная ошибка: поставить restoration ID и удивляться, почему instantiate всё ещё падает.



```swift
enum StoryboardID {
    static let profile = "ProfileViewController"
}

let storyboard = UIStoryboard(name: "Main", bundle: nil)
let profile = storyboard.instantiateViewController(
    identifier: StoryboardID.profile
) as ProfileViewController
```


**Потом обычно спрашивают**

- Какой exception будет, если identifier неверный?
- Чем Storyboard ID отличается от restoration ID?
- Зачем команде один storyboard на фичу вместо ID в `Main`?

</details>

<h2 id="activity-view-controller">UIActivityViewController</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIActivityViewController` — системный share sheet. Отдаёшь `activityItems` (строки, URL, картинки или свой `UIActivityItemSource`) и опционально `applicationActivities`, потом `present`. Юзер выбирает Messages, Mail, Copy, Save Image или приложение, которое заявило share extension. Системные действия прячешь через `excludedActivityTypes`, результат смотришь в `completionWithItemsHandler`. На iPad это popover: надо поставить `popoverPresentationController?.sourceView` (или `barButtonItem`), иначе краш. Типичные ошибки: показать на телефоне и не проверить popover-путь, шарить file URL не из world-readable места.



```swift
let items: [Any] = [text, fileURL]
let sheet = UIActivityViewController(activityItems: items, applicationActivities: nil)
sheet.excludedActivityTypes = [.assignToContact]
sheet.popoverPresentationController?.sourceView = shareButton
present(sheet, animated: true)
```


**Потом обычно спрашивают**

- Почему на iPad это крашится, если только вызвать `present`?
- Зачем нужен `UIActivityItemSource`?
- Как узнать, какую activity выбрал юзер?

</details>

<h2 id="tab-bar-controller">UITabBarController</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Tab controller хостит сиблингов, не стек. У каждого таба свой root, часто navigation controller. Выбор таба не сбрасывает его nav stack, пока ты сам это не сделаешь. Пять видимых табов, остальные уходят в «More». Типичный промах: один общий navigation controller на все табы или tab controller внутри nav controller — и удивление, почему tab bar пропадает на push.



```swift
let feed = UINavigationController(rootViewController: FeedViewController())
feed.tabBarItem = UITabBarItem(title: "Feed", image: UIImage(systemName: "list.bullet"), tag: 0)
let tabs = UITabBarController()
tabs.viewControllers = [feed, profile]
```


**Потом обычно спрашивают**

- Почему каждый таб обычно оборачивают в `UINavigationController`?
- Что происходит со стейтом таба, когда ушёл и вернулся?
- Таб или segmented control на одном экране?

</details>

<h2 id="visual-effect-view">UIVisualEffectView</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIVisualEffectView` композитит живой blur или vibrancy поверх того, что сзади. Создаёшь с `UIBlurEffect` (системные стили вроде `.systemMaterial`) или оборачиваешь blur в `UIVibrancyEffect`, чтобы лейблы пробивались сквозь блюр, как в Control Center. Сабвью кладёшь на `contentView`, не на сам effect view. Иначе классика «куда делся лейбл / почему блюр кривой». Эффект сэмплит контент позади view. Сплошной непрозрачный сосед на этом месте — блюра нет. Vibrancy без парного blur выглядит выцветшим. Дальше как обычная view: констрейнишь её, детей — к `contentView`.



```swift
let blur = UIVisualEffectView(effect: UIBlurEffect(style: .systemMaterial))
blur.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(blur)

let label = UILabel()
label.text = "Behind the chrome"
blur.contentView.addSubview(label)
```


**Потом обычно спрашивают**

- Почему сабвью надо добавлять на `contentView`?
- Зачем vibrancy относительно blur?
- Чем materials отличаются от старых blur-стилей `.light` / `.dark`?

</details>

<h2 id="view-hierarchy">UIWindow и иерархия view</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIWindow` — корневая поверхность, в которую рисует scene. На ней один root view controller. Его `view` — ствол иерархии view, дерева `UIView`. UIKit рисует сзади вперёд, hit-test идёт спереди назад, детей раскладывает внутри родителей. Второй window на iPhone почти никогда не создаёшь. На iPad / Mac вторая `UIScene` получает своё окно. `UIApplication` владеет процессом. Window владеет тем, что на экране. Типичный промах: `addSubview` на `UIWindow`, чтобы «повесить» баннер. Он игнорит поворот и safe area. Нужен child view controller. Или считать `view` необязательным украшением, а не корнем контроллера.



```swift
// UIWindow
// └── rootViewController.view
//     ├── titleLabel
//     └── contentView
//         └── imageView

window.rootViewController = RootViewController()
window.makeKeyAndVisible()
```


**Потом обычно спрашивают**

- Кто hit-testит тап: window, root VC или самая передняя view?
- Когда в одном процессе будут два window?
- `addSubview` на window или child view controller — что переживает поворот?

</details>

<h2 id="xib-vs-storyboard">XIB или storyboard</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

XIB (nib) архивирует одну view, одну ячейку или один view controller. Storyboard архивирует граф сцен плюс segue и связи между ними. XIB выигрывает на переиспользуемых кусках: `UITableViewCell`, `UICollectionViewCell`, кастомный `UIView` через `Bundle.main.loadNibNamed`, VC, который инстанцируешь из многих мест. Файл маленький, конфликты локальные. Storyboard выигрывает, когда хочешь видеть флоу и проводку Show/Present без вызова `present`. Оба — Interface Builder. Оба десериализуются в runtime. Оба не обязательны, если иерархию собираешь в коде. Типичная ошибка: запихнуть все экраны в один storyboard, чтобы каждое изменение инвалидировало файл всей команде.



```swift
let nib = UINib(nibName: "AccountCell", bundle: nil)
tableView.register(nib, forCellReuseIdentifier: AccountCell.reuseID)

// Or a standalone view:
let view = Bundle.main.loadNibNamed("EmptyStateView", owner: self, options: nil)?.first as? UIView
```


**Потом обычно спрашивают**

- Как загрузить view controller из XIB и как из storyboard?
- Почему ячейки так часто живут в своём XIB?
- Что такое nib owner (`File's Owner`)?

</details>

<h2 id="uiview-lifecycle">Жизненный цикл UIView</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

View создаётся (`init(frame:)` / `init(coder:)`), добавляется (`willMove(toSuperview:)` / `didMoveToSuperview`), цепляется к window (`didMoveToWindow`), потом идёт layout (`layoutSubviews`) и отрисовка (`draw(_:)` / слой). Constraints обновляют layout engine. `layoutSubviews` проставляет frames. `draw(_:)` — для кастомной отрисовки, не для добавления сабвью. Типичный промах: градиент в `init` с нулевым bounds или активация constraints в `draw(_:)`.



```swift
final class Badge: UIView {
    override func layoutSubviews() {
        super.layoutSubviews()
        layer.cornerRadius = bounds.height / 2
    }
}
```


**Потом обычно спрашивают**

- `didMoveToWindow` или `didMoveToSuperview`?
- Почему `draw(_:)` плохое место для `addSubview`?
- Чем это отличается от `viewDidLayoutSubviews` у view controller?

</details>

<h2 id="view-shadow">Как накинуть тень на view</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Тени рисует CALayer, не сам UIView. На `view.layer` ставишь `shadowColor` (это `CGColor`), `shadowOpacity` (0...1), `shadowOffset` и `shadowRadius`. Тень — силуэт по альфе слоя: полностью непрозрачный прямоугольник даёт прямоугольную тень; слой с `cornerRadius` даст круглую, если ещё задать подходящий `shadowPath`. `clipsToBounds` / `masksToBounds` обрезают тень. Отсюда классика «поставил `cornerRadius` и тень пропала». Обычно делают обёртку: внешний view держит тень, внутренний клипает и скругляет. `shadowPath` (и rasterize, только когда размер уже стабильный) спасает скролл-листы от просадок по кадрам.



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


**Потом обычно спрашивают**

- Почему тень пропадает после `clipsToBounds = true`?
- Зачем задавать `shadowPath`, а не дать Core Animation самому его вывести?
- Как накинуть тень на view, у которой ещё и скруглённый, клипнутый контент?

</details>

<h2 id="round-corners">Скруглить углы у view</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Простой путь: `view.layer.cornerRadius` плюс что-то, что клипает содержимое. `masksToBounds` на слое или `clipsToBounds` на view — это один и тот же флаг. С iOS 11 можно скруглить часть углов через `maskedCorners` (`CACornerMask`). С iOS 13 `cornerCurve = .continuous` даёт системный squircle. Если нужна дырка, пунктирный контур или форма, которую Auto Layout не выразит, маскируй `CAShapeLayer`, у которого `path` из `UIBezierPath`. Не анимируй `cornerRadius`, присваивая его каждый кадр в `layoutSubviews` без причины: это орёт на render server. И помни: клип, чтобы скруглить картинку, обрежет и тень на том же слое.



```swift
imageView.layer.cornerRadius = 12
imageView.layer.maskedCorners = [.layerMinXMinYCorner, .layerMaxXMinYCorner]
imageView.layer.cornerCurve = .continuous
imageView.clipsToBounds = true
```


**Потом обычно спрашивают**

- Как скруглить только два верхних угла?
- Чем `masksToBounds` отличается от маски через `CAShapeLayer`?
- Зачем ставить `cornerCurve`?

</details>

<h2 id="segues">Segue</h2>

<code>Junior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Segue — именованный переход, который Interface Builder хранит на storyboard: show, show detail, present modally, popover, custom или unwind. В runtime UIKit создаёт destination, потом зовёт `prepare(for:sender:)` у source, чтобы ты прокинул данные до того, как у destination загрузится view. Можно стрельнуть из кода через `performSegue(withIdentifier:sender:)`. Unwind segue идёт назад по presented/pushed стеку к методу с меткой `@IBAction func unwindToX(segue:)`. Спрашивают реже: programmatic `push` / `present` и SwiftUI `NavigationStack` почти всё заменили, но в старых кодовых базах полно строк-идентификаторов. Типичные ошибки: настраивать destination в `viewDidLoad` у source и забывать, что `sender` — то, что ты передал, не всегда кнопка.



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


**Потом обычно спрашивают**

- Когда бежит `prepare(for:sender:)` относительно `viewDidLoad` у destination?
- Зачем нужен unwind segue?
- Как прокинуть данные, если present идёт из кода?

</details>

<h2 id="view-with-tag">Плюсы и минусы viewWithTag()</h2>

<code>Junior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`viewWithTag(_:)` обходит поддерево получателя и возвращает первый `UIView`, у которого совпал `tag`. Плюс: ноль outlet. Interface Builder ставит число, ты вылавливаешь его в `awakeFromNib`. В реальном приложении минусы побеждают. Теги — магические числа, по умолчанию `0` (невыставленный view может совпасть), без типов, сталкиваются, как только две ячейки или два XIB переиспользуют одно число. После reuse найденная view может быть от другой строки, чем ты думаешь. Лучше `@IBOutlet`, свойство-сабвью или типизированная обёртка над `viewWithTag` только в чужом легаси. Хотят услышать: «работает, я бы не добавлял».



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


**Потом обычно спрашивают**

- Почему тег `0` особенно плохой выбор?
- Что происходит с тегами, когда ячейку переиспользуют?
- Как найти сабвью без тегов и без outlet?

</details>

### Mid

<h2 id="collection-vs-table">Collection view или table view</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UITableView` — вертикальный список с системными стилями ячеек, header/footer секций, swipe actions, reorder и accessories. `UICollectionView` — `UIScrollView` плюс объект layout: flow, compositional или свой `UICollectionViewLayout`. Таблица — самый честный ответ для settings-списка. Collection выигрывает на сетках, каруселях, orthogonal секциях и смеси размеров. Compositional layout умеет притвориться таблицей через `UICollectionLayoutListConfiguration`. Новые системные приложения так и живут, так что «table vs collection» ещё и вопрос «нужен list chrome или layout». Типичные ошибки: впихнуть сетку в таблицу стопкой image view и взять collection, когда хватило бы `UITableViewStyle.insetGrouped`.



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


**Потом обычно спрашивают**

- Что даёт compositional list layout из того, что у `UITableView` уже было?
- Когда свой `UICollectionViewLayout` того стоит?
- Чем prefetching и diffable data source отличаются у таблицы и коллекции?
- Горизонтальный рейл: вложенная коллекция в ячейке таблицы или orthogonal compositional секция?

</details>

<h2 id="diffable-data-source">Diffable data source</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Diffable data source (`UITableViewDiffableDataSource` / `UICollectionViewDiffableDataSource`) владеет snapshot. Даёшь список hashable ID секций и айтемов, он диффит с прошлым snapshot и применяет insert, delete и move без арифметики `performBatchUpdates`. Ячейку по-прежнему dequeue и конфигурируешь. Index path руками больше не считаешь. Identity должна быть стабильной. Если `Item` хешируется по строке на экране, и она меняется, ряды мигают или крашатся. Snapshot применяй на main thread. Типичный промах: мутировать backing array и на всякий случай звать `reloadData`, или взять индекс массива как item identifier.



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


**Потом обычно спрашивают**

- Почему item identifier должен быть стабильным между apply?
- Snapshot или `NSFetchedResultsController` для списка из Core Data?
- Что всё ещё живёт в `cellProvider`, а что в snapshot?
- Почему повторный `reloadData` мигает, когда поменялся один айтем?

</details>

<h2 id="intrinsic-content-size">Intrinsic content size</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Intrinsic content size — размер, который view хочет до того, как Auto Layout её растянет или сожмёт. Размер текста у `UILabel`, картинки у `UIImageView`, title плюс insets у `UIButton`. Обычный `UIView` отдаёт `UIView.noIntrinsicMetric` (−1) по обеим осям, ему нужны явные constraints. Hugging resistance говорит «не расти». Compression resistance говорит «не сжимай». У кого priority выше, тот побеждает, когда две view дерутся. Переопределяешь `intrinsicContentSize` и зовёшь `invalidateIntrinsicContentSize()`, когда контент меняется. Типичные ошибки: дать лейблу фиксированную ширину и ждать перенос без `numberOfLines = 0`; припинить края кастомной view и не реализовать intrinsic size — Interface Builder покажет нулевой frame.



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


**Потом обычно спрашивают**

- Что делают content-hugging и compression-resistance priorities?
- Почему `UILabel` без width constraint растёт по горизонтали?
- Когда звать `invalidateIntrinsicContentSize()`?

</details>

<h2 id="responder-chain">Responder chain</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Responder chain — как UIKit гуляет события, которые view не обработала: view → её superview → view controller → window → app. First responder получает клавиатуру и menu actions (`becomeFirstResponder`). Action у `UIControl` — другой путь, target-action. Но необработанные motion, remote-control и `canPerformAction` всё равно лезут по цепочке. Поэтому `UIViewController` может реализовать `copy(_:)` для дочернего лейбла. Типичная ошибка: повесить жест с `cancelsTouchesInView` и удивляться, почему кнопки ниже не видят тап.



```swift
final class EditorViewController: UIViewController {
    override var canBecomeFirstResponder: Bool { true }

    override func canPerformAction(_ action: Selector, withSender sender: Any?) -> Bool {
        action == #selector(copy(_:))
    }
}
```


**Потом обычно спрашивают**

- First responder и next responder?
- Как gesture recognizer стыкуется с цепочкой?
- Куда уходит событие shake-to-undo?

</details>

<h2 id="size-classes">Size classes</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Size classes — грубый trait: `horizontalSizeClass` и `verticalSizeClass` у `UITraitCollection`, каждое `.compact`, `.regular` или `.unspecified`. Это про доступную ширину и высоту, не про имя девайса. Портретный iPhone — compact-regular. Большинство iPhone в ландшафте — compact-compact. Plus/Max в ландшафте и полноэкранный iPad — regular-regular. iPad в Split View может упасть в compact по ширине. Вариации в Interface Builder и «installed» constraints в Auto Layout завязаны именно на это. В коде читаешь `traitCollection` и реагируешь в `traitCollectionDidChange` (или `registerForTraitChanges` на свежем iOS). Типичные ошибки: хардкодить `UIDevice.current.userInterfaceIdiom`, считать compact «телефоном» и забыть, что slide-over на iPad тоже compact.



```swift
override func traitCollectionDidChange(_ previous: UITraitCollection?) {
    super.traitCollectionDidChange(previous)
    let isWide = traitCollection.horizontalSizeClass == .regular
    stackView.axis = isWide ? .horizontal : .vertical
}
```


**Потом обычно спрашивают**

- Какие size classes у полноэкранного iPad и у Split View?
- Чем это отличается от Dynamic Type / `UIContentSizeCategory`?
- Как в storyboard поставить разные constraints для compact и regular?
- Почему `UIDevice.current.orientation` плохая замена size class?
- Storyboard, traits, constraints в коде — как закрыть все девайсы?

</details>

<h2 id="setneedslayout">setNeedsLayout и layoutIfNeeded</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`setNeedsLayout()` помечает view грязной. Layout пройдёт позже в этом проходе run loop: дёшево, coalesced. `layoutIfNeeded()` гоняет layout сейчас, если view грязная. Нужен новый `frame` на этой же строке: подготовка анимации, snapshot. `layoutSubviews()` — метод, который зовёт UIKit. Ты его оверрайдишь, не вызываешь сам. Типичный промах: `layoutIfNeeded()` в тугом цикле или оверрайд `layoutSubviews` без `super`.



```swift
header.invalidateIntrinsicContentSize()
header.setNeedsLayout()
UIView.animate(withDuration: 0.25) {
    self.view.layoutIfNeeded()
}
```


**Потом обычно спрашивают**

- `setNeedsDisplay` и `setNeedsLayout`?
- Почему анимируют `layoutIfNeeded`, а не `layoutSubviews`?
- Что в эту историю добавляет `updateConstraints`?

</details>

<h2 id="passing-data">Как передавать данные в iOS</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Назови направление. Вниз: initializer, свойство, segue `prepare(for:)`, SwiftUI `init` / `@Binding`. Вверх и наружу: delegate, closure callback, Combine / `AsyncStream`. Broadcast: `NotificationCenter`, когда много чужих слушателей. Shared: environment object, store, который инжектишь. Не `Foo.shared`, пока не объяснишь зачем. Бери самый узкий канал. Типичная ошибка: notification на кнопку, которую слушает один экран, или синглтон, который на самом деле спрятанный параметр.



```swift
final class DetailViewController: UIViewController {
    var item: Item!
    var onSave: ((Item) -> Void)?
}

override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    (segue.destination as? DetailViewController)?.item = selected
}
```


**Потом обычно спрашивают**

- Delegate, closure или notification для одного события?
- Как вернуть данные назад с запушенного экрана?
- Что меняется в SwiftUI (`Binding`, environment)?

</details>

<h2 id="remote-images-table">Таблица с картинками из сети</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Три правила, и их хотят услышать по порядку. Первое, lazy: стартуй загрузку в `cellForRow` / `willDisplay`, не для всех рядов в `viewDidLoad`. Второе, не на main thread: декодируй на background queue / `Task`, на main только присваивай `image`. `Data(contentsOf: url)` на main thread — классический провал. Блокирует скролл, нет кэша, нет cancel. Третье, identity после reuse: когда запрос вернулся, ячейка уже может показывать другой ряд. Сравни URL или generation token и выброси битмап, если не совпало. Cancel в `prepareForReuse`. Кэшируй декодированные картинки в `NSCache`, чтобы обратный скролл был мгновенным. Типичный промах: красивый спиннер, который всё равно ставит чужое фото на переиспользованную ячейку.



```swift
func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
    let cell = tableView.dequeueReusableCell(withIdentifier: PhotoCell.reuseID, for: indexPath) as! PhotoCell
    let url = items[indexPath.row].url
    cell.apply(url: url) // cancel previous, then load; ignore if url changed
    return cell
}
```


**Потом обычно спрашивают**

- Что делать, если юзер скроллит быстрее сети?
- Memory cache или `URLCache` для этих превью?
- Как держать 60 fps, пока декодируешь JPEG?

</details>

<h2 id="child-view-controllers">Child view controllers</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Child view controller — настоящий `UIViewController`, чью view встраиваешь в родителя через containment API. Тогда rotation, appearance, trait и колбэки `addChild` остаются правильными. Добавление: `addChild(_:)`, view ребёнка в иерархию, потом `didMove(toParent:)`. Снятие: `willMove(toParent: nil)`, убрать view, `removeFromParent()`. Пропустишь вызовы — баг: view ребёнка на экране, а `viewWillAppear`, стиль статус-бара и `parent` кривые. Так делают кастомные табы, пейджеры и «вставь map VC в эту карточку». Не `addSubview` чужой view без containment. `UINavigationController` и `UITabBarController` — просто специализированные родители.



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


**Потом обычно спрашивают**

- Что ломается, если сделать `addSubview` view ребёнка и никогда не вызвать `addChild`?
- Как снять child, не утекая им?
- Когда брать container VC, а не child `UIView`?

</details>

<h2 id="nested-collection">Collection view внутри ячейки таблицы</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Горизонтальный рейл в ряду таблицы — `UICollectionView`, которым владеет ячейка или child VC. Сложное тут reuse и layout, не «добавить collection view». Внутренней коллекции нужен стабильный data source именно этого ряда. Сбрось его в `prepareForReuse`. Запомни scroll offset, если продукт хочет, чтобы рейл остался там, где юзер его оставил. Высота обычно фиксированная или меряется один раз. Self-sizing внутренняя коллекция, которая инвалидирует таблицу на каждый скролл, даёт hitch. Если весь экран уже collection, лучше compositional orthogonal sections. Типичный промах: один общий data source на переиспользуемые ячейки. Рейлы меняют контент при скролле.



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


**Потом обычно спрашивают**

- Где хранить scroll offset каждого ряда, чтобы он пережил reuse?
- Почему Auto Layout на внутренней коллекции может тормозить внешнюю таблицу?
- Когда весь Home лучше перевести на compositional секции?

</details>

<h2 id="file-owner">File’s Owner</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

File’s Owner — placeholder в nib/xib для объекта, который будет грузить файл. Обычно это view controller, который зовёт `init(nibName:)` или `Bundle.loadNibNamed`. Это не объект, сохранённый в файле. Outlet и action в xib цепляются к этому будущему инстансу. Не тот класс owner, или xib загрузили с view, которая не owner, — outlet будут `nil`. Storyboard прячет это за view controller сцены. Типичный промах: «File’s Owner — это первая view в xib».



```swift
// ProfileViewController is File's Owner of ProfileViewController.xib
let vc = ProfileViewController(nibName: "ProfileViewController", bundle: nil)
```


**Потом обычно спрашивают**

- Owner или top-level объект view в xib?
- Почему `@IBOutlet` может быть `nil` после `loadNibNamed`?
- Чем это отличается от сцены на storyboard?

</details>

<h2 id="ibdesignable">IBDesignable</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`@IBDesignable` говорит Interface Builder скомпилировать сабкласс `UIView` и создать его на канвасе, чтобы видеть живой рисунок. `@IBInspectable` выносит выбранные свойства в Attributes inspector: цвета, числа, строки, картинки. `prepareForInterfaceBuilder()` бежит только в IB. Там стабишь сетевые вызовы или `UIApplication.shared`. IB собирает отдельный target. Что этому target не видно (часть SPM-сборок, флаги только для app extension, нет ассетов) рисуется как краш или серый квадрат на канвасе, не в симуляторе. Спрашивают реже: SwiftUI previews закрывают ту же задачу с меньшей машинерией IB. Типичная ошибка: сайд-эффекты в `init(frame:)`, которые IB исполняет, пока ты печатаешь.



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


**Потом обычно спрашивают**

- Что класть в `prepareForInterfaceBuilder()`, чего не должно быть в приложении?
- Почему view рисуется в симуляторе, а на канвасе падает?
- Как `@IBInspectable` мапит типы Swift на контролы инспектора?

</details>

<h2 id="memory-warning">Memory warning</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Система говорит, что RAM впритык: `UIApplication.didReceiveMemoryWarningNotification` и `UIViewController.didReceiveMemoryWarning`. Сбрасывай кэши, которые можно собрать заново: декодированные картинки, `NSCache`, скачанный файл, который можно взять снова. Черновик юзера не трогай. `NSCache` и так выселяет под давлением. Свой словарь `[URL: UIImage]` — нет. На warning ещё останови speculative prefetch. Типичный промах: игнорировать warning или отпустить единственную копию данных, которые не восстановить.



```swift
override func didReceiveMemoryWarning() {
    super.didReceiveMemoryWarning()
    imageCache.removeAllObjects()
}
```


**Потом обычно спрашивают**

- Что безопасно сбросить, а что сначала надо сохранить?
- Как это стыкуется с `NSCache`?
- Jetsam или memory warning — что приходит первым?

</details>

<h2 id="orientation">Ориентация устройства</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Не гони layout от `UIDevice.current.orientation`. Смотри size и traits: `viewWillTransition(to:with:)` на новые bounds, `traitCollectionDidChange` / `traitCollection.horizontalSizeClass` на compact vs regular. Auto Layout плюс size classes и так поворачивают большинство экранов. Лочь ориентацию на конкретном VC через `supportedInterfaceOrientations`, когда камере или игре нужен только landscape. Типичный промах: `if UIDevice.current.orientation == .landscapeLeft`. Врёт на iPad Split View: ширина compact, девайс всё ещё «landscape». И врёт во время анимации.



```swift
override func viewWillTransition(to size: CGSize, with coordinator: UIViewControllerTransitionCoordinator) {
    super.viewWillTransition(to: size, with: coordinator)
    coordinator.animate { _ in
        self.columns = size.width > size.height ? 3 : 1
        self.collectionView.collectionViewLayout.invalidateLayout()
    }
}
```


**Потом обычно спрашивают**

- Size class или ориентация девайса — что из этого Split View?
- Как залочить один экран в landscape, не лоча всё приложение?
- В SwiftUI — `verticalSizeClass` или читать `UIDevice`?

</details>

<h2 id="uicontrol-target-nil">UIControl с target nil</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`addTarget(nil, action: #selector(foo), for: .touchUpInside)` не значит «никто не услышит». Nil target идёт по responder chain, пока кто-то не реализует `foo`. Так кнопка в ячейке может дернуть action у view controller без явного target. Никто не реализовал — ничего не будет, без краша. В новом коде лучше явный target. Nil-target остроумно и плохо грепается. Типичная ошибка: думать, что nil target выключает контрол.



```swift
button.addTarget(nil, action: #selector(EditorViewController.save), for: .touchUpInside)
```


**Потом обычно спрашивают**

- Чем это отличается от `addTarget(self, ...)`?
- Почему nil-target action тяжело дебажить?
- Что из этого сильно заменил SwiftUI?

</details>

<h2 id="menu-controller">UIMenuController</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIMenuController` — старое плавающее Edit-меню: Cut, Copy, Paste и свои `UIMenuItem`. View должна уметь стать first responder (`canBecomeFirstResponder` плюс `becomeFirstResponder`). Реализуешь `canPerformAction(_:withSender:)` и парные `@objc` методы, потом зовёшь `showMenu(from:rect:)`. Deprecated с iOS 16. Новый код берёт `UIEditMenuInteraction` для меню выделения и `UIContextMenuInteraction` / `contextMenuConfigurationForItemsAt` для long-press. На собесах ещё всплывает, потому что text view и WebView исторически на нём сидели, и «сделай лейбл копируемым» часто дают на take-home. Типичная ошибка: пункты меню добавил, first responder не сделал — меню не появляется.



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


**Потом обычно спрашивают**

- Чем заменили `UIMenuController` на iOS 16 и новее?
- Почему view должна стать first responder?
- Как добавить свой пункт рядом с Copy?

</details>

<h2 id="color-out-of-range">Цвет вне диапазона 0...1</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`UIColor(red:green:blue:alpha:)` ждёт компоненты `CGFloat` в 0...1, не 0...255. Ниже 0 станет 0, выше 1 станет 1. Передать `red: 255` не значит получить «веб-красный»: значение зажмётся в 1, канал полностью насыщен. Если все каналы были 255, часто выходит случайный белый. Шкала 0...255 живёт в записи вроде `UIColor(red: 255/255, green: 0, blue: 0, alpha: 1)` или в asset catalog. Wide-gamut инициализаторы вроде `UIColor(displayP3Red:green:blue:alpha:)` умеют цвета, которые при конвертации в sRGB дают компоненты вне 0...1. Тогда `getRed(_:green:blue:alpha:)` может вернуть числа, которые нельзя скормить обратно sRGB-инициализатору. Обычно ловят clamp и ошибку с 255, глубже — Display P3.



```swift
let wrong = UIColor(red: 255, green: 0, blue: 0, alpha: 1)   // clamped → not "255 red"
let sRGB = UIColor(red: 255 / 255, green: 0, blue: 0, alpha: 1)
let p3 = UIColor(displayP3Red: 1, green: 0, blue: 0, alpha: 1)
```


**Потом обычно спрашивают**

- Какой цвет на самом деле даст `UIColor(red: 255, green: 128, blue: 0, alpha: 1)`?
- Когда `getRed` может вернуть компонент больше 1?
- Почему asset catalog закрывает этот класс багов?

</details>
