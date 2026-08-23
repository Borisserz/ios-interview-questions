# Фреймворки

19 карточек · 1 часто спрашивают · [frameworks.md](../../topics/frameworks.md)

### Junior

<h2 id="attributed-string">NSAttributedString</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NSAttributedString — строка плюс прогон атрибутов: шрифт, цвет, подчёркивание, paragraph style, ссылка, attachment. Лейблы UIKit, text view и заголовки навигации его всё ещё едят; SwiftUI предпочитает AttributedString, value type, и умеет конвертить. Собираешь NSMutableAttributedString или markdown через AttributedString(markdown:). Атрибуты на диапазонах — off-by-one на составном символе обычный баг. Берёшь, когда один лейбл должен смешать стили; не подделывай тремя лейблами, если VoiceOver должен прочитать одно предложение.



```swift
let text = NSMutableAttributedString(string: "Total 24.00")
text.addAttribute(.font, value: UIFont.preferredFont(forTextStyle: .body), range: NSRange(location: 0, length: 5))
text.addAttribute(.foregroundColor, value: UIColor.secondaryLabel, range: NSRange(location: 0, length: 5))
text.addAttribute(.font, value: UIFont.preferredFont(forTextStyle: .headline), range: NSRange(location: 6, length: 5))
label.attributedText = text
```


**Потом обычно спрашивают**

- AttributedString и NSAttributedString — какой API в SwiftUI?
- Как удержать Dynamic Type, если атрибуты прибивают UIFont?
- Как ссылки и attachment ведут себя в UITextView и UILabel?
- Что ломается у NSRange и эмодзи?

</details>

<h2 id="custom-sound">Свой звук</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Короткие UI-звуки можно через AudioServicesPlaySystemSound или play на system sound ID, если это несколько секунд и микширование не нужно. Всё, что важно — громкость, цикл, категория сессии, фон — AVAudioPlayer или AVAudioEngine. Надо настроить AVAudioSession: ambient, чтобы музыка продолжала играть; playback, если звук — смысл — иначе ОС тебя заглушит. Файл в бандле — caf, wav, m4a, mp3 — грузишь из Bundle.main. Главный поток длинным файлом не блокируй: prepare игрока один раз и play на событии.



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


**Потом обычно спрашивают**

- Когда AudioServicesPlaySystemSound — не тот API?
- ambient, playback, playAndRecord — кого каждый приглушает?
- Как играть звук, когда тумблер звонка выключен?
- Почему play вернулся, а тишина?

</details>

### Mid

<h2 id="storekit">StoreKit</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

StoreKit — API покупок в приложении и коммерции App Store. StoreKit 2 — Product, Transaction, PurchaseResult — текущий дефолт: async-загрузка продуктов, Transaction.currentEntitlements на то, чем человек владеет, Transaction.updates на продления и family sharing. Слушатель updates стартуешь на запуске, не когда вылез пейвол: Ask to Buy и шаринг семьи прилетают в это окно. Нужны product ID в App Store Connect, тестовая витрина — StoreKit configuration или sandbox — и сервер, если покупка открывает то, чему клиенту верить нельзя. Каждую проверенную транзакцию finish, иначе она приедет на каждом запуске. Restore — AppStore.sync плюс видимая кнопка Restore по гайдлайну 3.1.1; currentEntitlements кнопку не заменяет. Доступ даёшь в grace и billing-retry, не только в subscribed. SwiftUI SubscriptionStoreView / StoreView с iOS 17 могут держать хром пейвола. Свой парсер чека в 2026 не пиши, если не поддерживаешь StoreKit 1.



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


**Потом обычно спрашивают**

- Как восстановить или пересинковать entitlements на новом девайсе?
- Что на сервере, а что в Transaction.currentEntitlements?
- StoreKit configuration, sandbox, TestFlight — какой баг где всплывёт?
- Как статус подписки и billing retry выглядят в StoreKit 2?
- Что ловит Transaction.updates, чего не видит purchase?
- Intro offer и promotional offer — где читаешь eligibility?
- Airplane mode — открываешь ли из закэшированного entitlement и на сколько?
- Почему Transaction.updates должен стартовать в init / на запуске, не на пейволе?
- AppStore.sync и Transaction.currentEntitlements — что из этого кнопка Restore?
- inGracePeriod / inBillingRetryPeriod — всё ещё открываешь доступ?

</details>

<h2 id="app-intents">App Intents</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

App Intents — современный способ отдать действия и сущности Siri, Spotlight, Shortcuts и кнопке Action: наследник кучи файлов INIntent во многих случаях. Объявляешь структуру с конформом AppIntent, даёшь title и параметры, реализуешь perform. Система может показать это без UI; если нужен экран — возвращаешь сниппет или продолжаешь в приложении. Типичный промах: считать это «только Siri» или сунуть в perform двадцатисекундный сетевой вызов без прогресса.



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


**Потом обычно спрашивают**

- App Intent и старое определение интента SiriKit?
- Как задонатить интент, чтобы Spotlight его предложил?
- Что в perform должно жить не на main actor?

</details>

<h2 id="cadisplaylink">CADisplayLink</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

CADisplayLink — таймер, привязанный к обновлению экрана: 60 или 120 Гц, не «примерно 16 мс». Берёшь на покадровую работу: своя анимация, цикл Metal/игры, часы плеера. Timer и задержки DispatchQueue плывут и не встают на паузу вместе с экраном. Линк кладёшь на main или на run loop, который реально крутится, ставишь preferredFrameRateRange и isPaused, когда сцена уходит в фон. Display link, который каждый кадр делает настоящую работу, всплывёт в Energy Log. Invalidate в stop или когда вью уходит, чтобы колбэк не пережил владельца.



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


**Потом обычно спрашивают**

- Почему не Timer с интервалом 1/60 для анимации?
- Что preferredFrameRateRange меняет на ProMotion?
- Display link в common или default — и почему?
- Как не дать display link жрать батарею в фоне?

</details>

<h2 id="affine-transform">CGAffineTransform</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

CGAffineTransform — двумерная аффинная матрица: сдвиг, скейл, поворот, сдвиг с перекосом. Кладешь на вью через transform, на слой, путь или контекст. Порядок важен: поворот-потом-сдвиг — не сдвиг-потом-поворот, а API конкатенирует справа, что удивляет тех, кто думает «сначала написал эту строку». Identity — CGAffineTransform.identity; сбрасываешь им, не угаданными числами. 3D и перспектива — CATransform3D, не аффин. Autolayout и transform дерутся: frame — нетрансформированные bounds, поэтому хит-зона скейлённой кнопки выглядит неправильно, если смотришь только на frame.



```swift
thumb.transform = CGAffineTransform.identity
    .translatedBy(x: 0, y: -12)
    .rotated(by: .pi / 12)
    .scaledBy(x: 1.05, y: 1.05)

let path = UIBezierPath(rect: CGRect(x: 0, y: 0, width: 40, height: 8))
path.apply(CGAffineTransform(rotationAngle: .pi / 4))
```


**Потом обычно спрашивают**

- Почему «не тот» порядок конкатенации уносит вью за экран?
- frame, bounds и transform после поворота — чем раскладываешь?
- Когда нужен CATransform3D?
- Как инвертировать трансформ, чтобы тап вернуть в пространство модели?

</details>

<h2 id="core-graphics">Core Graphics</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Core Graphics, он же Quartz 2D — C API двумерной отрисовки: пути, градиенты, картинки, PDF и CGContext, который принимает команды. UIBezierPath и UIGraphicsImageRenderer из UIKit сидят сверху; SwiftUI Canvas в итоге тоже. Берёшь, когда нужны пиксели, которых нет ассетом — график, маска, кастомный контрол, страница PDF. Рисуешь в текущем контексте: draw(_:) у UIView или renderer. Это сторона CPU, пока не закэшируешь результат в битмап или CALayer.contents. Забыл перевернуть ось Y или закрыть image context — пустая или перевёрнутая картинка.



```swift
let renderer = UIGraphicsImageRenderer(size: CGSize(width: 80, height: 80))
let image = renderer.image { ctx in
    UIColor.systemBlue.setFill()
    ctx.cgContext.fillEllipse(in: CGRect(x: 8, y: 8, width: 64, height: 64))
}
```


**Потом обычно спрашивают**

- UIGraphicsImageRenderer и UIGraphicsBeginImageContext — почему старый API умер?
- Когда рисовать в draw(_:), а когда кэшировать битмап?
- Как Core Graphics связан с Core Animation и Core Image?
- Чем CGPath отличается от UIBezierPath?

</details>

<h2 id="core-location">Core Location</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

CLLocationManager — API сплава GPS / Wi-Fi / соты. Просишь When In Use или Always, кладёшь usage-строку в Info.plist, потом стартуешь апдейты, significant-change или visits. На собесе — точность против батареи: kCLLocationAccuracyBest на карте — не то, что нужно погодному приложению. Фоновая локация — entitlement и история для ревью. Типичный промах: стартовать апдейты в init до авторизации или держать Always ради разового «магазины рядом».



```swift
let manager = CLLocationManager()
manager.requestWhenInUseAuthorization()
manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
manager.startUpdatingLocation()
```


**Потом обычно спрашивают**

- When In Use, Always и Precise Location?
- Significant-change, visits и обычный поток апдейтов?
- Как тестировать локацию, не стоя на улице?

</details>

<h2 id="healthkit">HealthKit</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

HealthKit — health store на девайсе, не фитнес-UI. Говоришь с HKHealthStore: read и write просишь отдельно, называешь типы — HKQuantityType, HKCategoryType, тренировки — и кладёшь usage-строки в Info.plist. Данные пользователя: запрашиваешь предикатами и интервалами дат, весь стор в свою базу не вываливаешь. Фоновая доставка и пара с Watch — opt-in и могут задержаться. Типичный промах: считать HealthKit REST API, который поллишь, или шиппить без privacy-строки и удивляться, почему диалог авторизации не вылез.



```swift
let store = HKHealthStore()
let steps = HKQuantityType(.stepCount)
try await store.requestAuthorization(toShare: [], read: [steps])

let now = Date()
let start = Calendar.current.startOfDay(for: now)
let predicate = HKQuery.predicateForSamples(withStart: start, end: now)
```


**Потом обычно спрашивают**

- Авторизация read и write — может дать одно и отказать в другом?
- Почему дневная сумма шагов — запрос, а не свойство на HKHealthStore?
- Что делаешь, когда HealthKit недоступен — iPad, родительские ограничения?

</details>

<h2 id="live-activities">Live Activities</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Live Activity — полоска реального времени на Lock Screen и Dynamic Island для короткого события: заказ, поездка, таймер. Стартуешь из приложения через ActivityKit, пушишь обновления content-state — часто через APNs — и заканчиваешь, когда событие умерло. UI — SwiftUI в расширении виджета: те же правила снимков, что у WidgetKit, плюс compact / minimal / expanded остров. Это не фоновый Timer в процессе приложения. Типичный промах: стартовать активность и никогда не закончить или запихнуть в пейлоад всю историю чата.



```swift
struct OrderAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable { var eta: String }
    var restaurant: String
}
```


**Потом обычно спрашивают**

- Пуш-апдейт и вызов activity.update из приложения на переднем плане?
- Что будет, если пользователь force-quit посреди активности?
- Compact и expanded Dynamic Island — кто решает лейаут?

</details>

<h2 id="widgetkit">WidgetKit</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Виджет на Home Screen — таймлайн снимков, не живое приложение. WidgetKit просит у TimelineProvider значения TimelineEntry и View; система рисует этот SwiftUI вне процесса и может заморозить. Произвольные таймеры и открытый сокет нельзя. Рефреш — бюджет: atEnd, after(date) или пуш в WidgetCenter. Тап идёт через widgetURL / App Intent в основное приложение. UI шарь пакетом, не копипастой. Типичный промах: считать виджет мини-UIViewController, который каждую секунду фетчит.



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


**Потом обычно спрашивают**

- Почему анимации беднее, чем в приложении?
- Как шарить строку SwiftUI между приложением и виджетом?
- Reload таймлайна и кнопка App Intent на iOS 17+?

</details>

<h2 id="calayer-subclasses">Сабклассы CALayer</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

CALayer — дерево отрисовки под каждым UIView. Apple шлёт узкие сабклассы, чтобы не рисовать руками: CAShapeLayer для путей, CAGradientLayer, CATextLayer, CAReplicatorLayer, CAEmitterLayer для частиц, CAScrollLayer, CATiledLayer для огромных картинок, CATransformLayer для настоящего 3D без сплющивания, CAMetalLayer. Берёшь, когда эффект дешевле слоем, чем битмапом, который перерисовываешь. Вью владеет слоем; можно собрать и отдельное дерево. Анимация path, colors или transform на этих слоях — работа Core Animation, обычно это и есть follow-up.



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


**Потом обычно спрашивают**

- CALayer и UIView — кто трогает тач, кто рисует?
- Что объект слоя значит относительно своего UIView?
- Когда CAShapeLayer лучше draw(_:)?
- Что CATransformLayer меняет в transform против обычного слоя?
- Почему CATiledLayer — правильный инструмент на большую страницу PDF?
- Как анимировать path у CAShapeLayer, не перерисовывая в draw(_:)?

</details>

<h2 id="app-clips">App Clips</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

App Clip — крошечный вызов твоего приложения, бюджет порядка 15 МБ, с ссылки, QR или NFC без полной установки. Шлёшь clip-таргет, который потом может вырасти в полное приложение. Первый опыт должен терпеть офлайн и просить только те разрешения, которые нужны этому экрану. URL вызова — deep link. Типичный промах: затащить весь таргет приложения в клип и взорвать лимит размера.



```text
Clip target → one screen (pay / order) → “Get the full app” → same team ID, shared App Group if you must hand off state.
```


**Потом обычно спрашивают**

- Что шаришь с полным приложением — Keychain, App Group, ничего?
- Чем App Clip отличается от Universal Link в уже установленное приложение?
- Где бюджет размера реально бьёт — картинки, SDK?

</details>

<h2 id="core-image">Core Image</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Core Image — граф фильтров на GPU (и CPU): на входе CIImage, цепочка CIFilter, CIContext наружу в CGImage или пиксельный буфер. Берёшь на цвет, блюр, кроп, детекцию QR — CIDetector / сейчас чаще Vision — и фото-правки. Фильтры ленивые: ничего не бежит, пока не попросишь контекст отрендерить. Один CIContext переиспользуй; создавать на каждый кадр — обычный стопор. Для стоп-кадров рендерь в CGImage. Для камеры — в Metal-текстуру или CVPixelBuffer. Vision и vImage пересекаются на части задач; Core Image побеждает, когда каталог фильтров уже даёт нужный вид.



```swift
let ciImage = CIImage(image: input)!
let filter = CIFilter.gaussianBlur()
filter.inputImage = ciImage
filter.radius = 8
let context = CIContext(options: [.useSoftwareRenderer: false])
let output = context.createCGImage(filter.outputImage!, from: ciImage.extent)
```


**Потом обычно спрашивают**

- Почему CIContext надо переиспользовать между кадрами?
- Core Image, фильтры UIImage и Vision — кто владеет детекцией, кто видом?
- Как удержать цепочку фильтров в display color space?
- Что extent портит после блюра и как кропаешь?

</details>

<h2 id="gameplaykit">GameplayKit</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

GameplayKit — ящик с игровой логикой, которая не рисует: стейт-машины GKStateMachine, сущности и компоненты, pathfinding по графу, сидируемые источники случайности, агенты и цели. Сидит рядом со SpriteKit или SceneKit, кадр не рисует. То, что переносится в приложения — GKStateMachine на понятный поток: онбординг, матчмейкинг, загрузка — и детерминированный GKRandomSource для воспроизводимых тестов. На экран настроек не потащишь. Apple давно не ставит его в центр новых семплов — так и скажи, потом покажи, что в ящике знаешь.



```swift
final class LoadingState: GKState {
    override func isValidNextState(_ stateClass: AnyClass) -> Bool {
        stateClass is ReadyState.Type || stateClass is FailedState.Type
    }
}

let machine = GKStateMachine(states: [LoadingState(), ReadyState(), FailedState()])
machine.enter(LoadingState.self)
```


**Потом обычно спрашивают**

- Когда GKStateMachine лучше enum на view model?
- Что даёт split entity-component в SpriteKit?
- Как сделать таблицу дропа тестируемой?
- Pathfinding: GKGridGraph или свой A*?

</details>

<h2 id="replaykit">ReplayKit</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

ReplayKit пишет экран приложения — опционально микрофон и звук приложения — или вещает в расширение ReplayKit. RPScreenRecorder.shared стартует запись; получаешь превью RPPreviewViewController или сырые sample buffer, если просил. Согласие пользователя обязательно, молча писать нельзя. Broadcast — отдельный таргет расширения под стрим вроде Twitch. Настоящие темы — приватность и перформанс: запись дорогая, в фоне надо стопать. Для продуктового клипа ReplayKit всё ещё поддерживаемый путь; для «сохрани это вью как видео» в ревью встречаются и AVFoundation, и режим sample buffer ReplayKit.



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


**Потом обычно спрашивают**

- Запись внутри приложения и broadcast extension — что делает каждый таргет?
- Можно ли писать другие приложения? Почему нет?
- Как взять звук микрофона и не схватить весь девайс?
- Что стопаешь в sceneDidEnterBackground и что будет, если не стопнешь?

</details>

<h2 id="spritekit-vs-scenekit">SpriteKit и SceneKit</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

SpriteKit — 2D scene graph Apple: спрайты, экшены, физика и SKView, который кладёшь в UIKit или SwiftUI. SceneKit — 3D-стек: ноды, камеры, свет, геометрии, SCN-материалы, опционально редактор. SpriteKit — карточные игры, 2D-платформеры, частицы поверх. SceneKit — просмотрщики продуктов, простые 3D-игры, сцены ARKit, которым нужен 3D-граф. Могут делить вью — SK3DNode, оверлей SceneKit — но API не взаимозаменяемые. RealityKit — более новый дефолт 3D / AR; упомяни, чтобы не звучать как 2016, потом отвечай на заданный вопрос.



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


**Потом обычно спрашивают**

- Когда пропускаешь оба и берёшь Metal или RealityKit?
- Чем экшены SpriteKit отличаются от анимаций SceneKit?
- Можно ли HUD SpriteKit на вью SceneKit или AR?
- Что даёт physics world в каждом фреймворке?

</details>

<h2 id="ibeacons">iBeacons</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

iBeacon — формат BLE-рекламы Apple: UUID плюс 16-битные major и minor. Мониторишь CLBeaconRegion, чтобы узнать enter/exit — даже в фоне, с разрешением локации — и range, чтобы получить proximity immediate / near / far, пока приложение запущено. API у Core Location, не у Core Bluetooth: стандартные маяки сам из рекламы не парсишь. Разрешение и батарея важны: range всегда дорогой, мониторинг — фоновый инструмент. Лимит регионов около 20 и шумный proximity отделяют настоящий ответ от «это Bluetooth».



```swift
let constraint = CLBeaconIdentityConstraint(uuid: storeUUID)
let region = CLBeaconRegion(beaconIdentityConstraint: constraint, identifier: "store")
manager.requestWhenInUseAuthorization()
manager.startMonitoring(for: region)
manager.startRangingBeacons(satisfying: constraint)
```


**Потом обычно спрашивают**

- Monitoring и ranging — что работает в фоне и что получаешь?
- Почему это Core Location, а не Core Bluetooth?
- Насколько точен proximity и чем меришь расстояние?
- Какие privacy-строки и background modes нужны фиче с маяками?

</details>

### Senior

<h2 id="foundation-models">Foundation Models</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Фреймворк Foundation Models у Apple — on-device LLM, который вызываешь как сервис, не чат-экран. Шлёшь instructions — роль, отказы, политика тулов — плюс промпт; @Generable / @Guide зажимают выход в типизированное значение Swift. Это DTO. Персистишь маппингом в SwiftData / свой стор — не лепи @Model на generable. Тулы — узкие Swift-функции, которые модель может вызвать. Железо гейтится: нет Neural Engine — явный fallback. Типичный промах: кнопка «Спроси AI» на флоу, которому хватало одного тапа, или считать модель чатботом, который владеет твоими доменными типами.



```swift
@Generable
struct RecipeDraft {
    @Guide(description: "Short title")
    var title: String
}

// Service layer: session + instructions → RecipeDraft → map to @Model if you save
```


**Потом обычно спрашивают**

- Instructions и пользовательский промпт — что версионируешь вместе с приложением?
- Почему тип @Generable не может быть сущностью SwiftData?
- Adapter / fine-tune — какой артефакт везёшь рядом с бинарём?

</details>
