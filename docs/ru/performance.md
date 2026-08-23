# Performance

14 карточек · 11 часто спрашивают · [performance.md](../../topics/performance.md)

### Junior

<h2 id="debugging">Отладка на iOS</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Начинай дёшево, потом глубже. Breakpoints — и exception / symbolic — плюс Variables view бьют print по состоянию. os_log / Logger остаются в Console.app и на девайсах; print — нет. View Debugger и Memory Graph ловят вёрстку и retain cycle. Instruments — Time Profiler, Allocations, Leaks, Network — сеньорский дефолт на «тормозит / растёт». Краш-репорты и MetricKit закрывают то, что не воспроизвести. Типичный промах: зашиппить print в цикле или считать Instruments «только про лики».



```swift
import os
let log = Logger(subsystem: "app", category: "feed")
log.debug("page \(cursor, privacy: .public)")
```


**Потом обычно спрашивают**

- Когда breakpoint лучше лога?
- Какой Instrument на scroll hitch, какой на лик?
- Как дебажить краш, который видишь только в Organizer?
- View Hierarchy и Memory Graph — чей это баг?
- Какие уровни логов реально шиппишь: debug, info, error?

</details>

### Mid

<h2 id="hang-hitch-crash">Hang, hitch и краш</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Краш обрывает процесс. Hang — главный поток застрял достаточно долго, чтобы система или человек решили, что приложение умерло: watchdog 0x8badf00d на запуске, замороженный скролл. Hitch (jank) — короткий шип на main, дропнутый кадр, который потом отходит. Китайские лупы часто хотят версию с наблюдателем RunLoop: засекаешь BeforeSources → BeforeWaiting; щель больше примерно 16–100 мс — главный поток был занят. MetricKit и Instruments — Time Profiler, Hangs, Animation Hitches — боевые инструменты. Hang лечишь уводом работы с main; hitch — более дешёвым лейаутом и декодом. Типичный промах: назвать каждый jank «крашем».



```swift
// Hitch: decode a 12 MP JPEG on main during cellForRow.
// Hang: wait on a lock / `main.sync` / a huge `viewDidLoad`.
// Crash: force-unwrap, `fatalError`, `EXC_BAD_ACCESS`.
Task.detached {
    let image = decode(data)
    await MainActor.run { cell.imageView.image = image }
}
```


**Потом обычно спрашивают**

- Какой шаблон Instruments на hitch, какой на hang?
- Как классифицируют watchdog kill?
- Что такое hang report в Xcode Organizer?
- Наблюдатель RunLoop и Instruments — что ответ на собесе?
- Симулятор гладкий, девайс дёргается — чему не веришь первым?

</details>

<h2 id="instruments">Instruments</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Instruments — профайлер, который цепляешь к живому процессу, симулятор или девайс. На собесе хотят шаблон, не «я открыл Instruments». Time Profiler семплит CPU — кто на главном потоке во время hitch. Allocations рисует живые объекты и скажет, вернулась ли память к базе после pop экрана. Leaks находит объекты, которые аллокатор всё ещё держит без оставшихся ссылок — настоящие лики; retain cycle чаще лучше виден в Memory Graph. Дальше Hangs / Animation Hitches и Network. Профилируй сборку, похожую на Release; Debug плюс санитайзеры врут про стоимость. Типичный промах: считать Leaks единственным инструментом памяти или профилировать Debug и «оптимизировать» print.



```text
Hitch while scrolling → Time Profiler, main thread, look for JSON / image decode.
Memory climbs on a feed → Allocations, mark generation, pop the screen, see what stayed.
deinit never fires → Memory Graph first; Leaks if the graph is clean but the heap grew.
```


**Потом обычно спрашивают**

- Time Profiler, Allocations, Leaks — какая жалоба на какой?
- Почему профиль Debug — слабый аргумент про скорость?
- Memory Graph Debugger и инструмент Leaks?
- Шаблон SwiftUI — Update Groups, Long View Body, граф Cause & Effect?
- Какую гипотезу произносишь до того, как открыть шаблон?

</details>

<h2 id="lru-cache">LRU-кэш</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

LRU значит: когда полно, выкидываешь то, к чему обращались давнее всего. На кодинге: словарь для get/set за O(1) плюс двусвязный список или упорядоченная структура, чтобы ключ двигать в «самый свежий» и выселять хвост. И get, и set обновляют свежесть. Ёмкость — счётчик, иногда стоимость в байтах. На iOS продакшен-двоюродный брат — NSCache: выселяет под давлением, это не строгий LRU, которым рулишь сам. Типичный промах: один словарь без порядка выселения или сканировать всю мапу в поисках самого старого.



```swift
final class LRUCache<Key: Hashable, Value> {
    private var map: [Key: Value] = [:]
    private var order: [Key] = []
    private let capacity: Int

    init(capacity: Int) { self.capacity = max(1, capacity) }

    func get(_ key: Key) -> Value? {
        guard let value = map[key] else { return nil }
        touch(key)
        return value
    }

    func set(_ key: Key, _ value: Value) {
        map[key] = value
        touch(key)
        while order.count > capacity, let old = order.first {
            order.removeFirst()
            map[old] = nil
        }
    }

    private func touch(_ key: Key) {
        order.removeAll { $0 == key }
        order.append(key)
    }
}
```


**Потом обычно спрашивают**

- Почему removeAll по массиву не O(1) — что даст связный список?
- LRU, LFU и NSCache под давлением памяти?
- Как сделать это потокобезопасным?
- Ёмкость как счётчик и как бюджет байт на картинку — что выселяешь?

</details>

<h2 id="nscache-vs-dictionary">NSCache и Dictionary</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Dictionary держит всё, что положил, пока сам не удалишь. NSCache — выселяющий, потокобезопасный мешок под чувствительные к памяти объекты: декодированные картинки, большие данные. Может выкинуть записи под давлением памяти и чтит countLimit / totalCostLimit. Ключи и значения — объекты NSObject / AnyObject; структуры оборачиваешь. Copy-on-write нет, порядок вставки не хранит. Для фотоленты NSCache — слой в памяти: miss нормален, перезапросишь или перекодируешь. Словарь URL → UIImage будет расти до jetsam. Типичный косяк: считать NSCache постоянным хранилищем или надеяться, что iOS подрежет словарь.



```swift
final class ImageCache {
    private let cache = NSCache<NSURL, UIImage>()

    init() {
        cache.countLimit = 100
        cache.totalCostLimit = 50 * 1_024 * 1_024
    }

    func image(for url: URL) -> UIImage? {
        cache.object(forKey: url as NSURL)
    }

    func store(_ image: UIImage, for url: URL) {
        let cost = Int(image.size.width * image.size.height * 4)
        cache.setObject(image, forKey: url as NSURL, cost: cost)
    }
}
```


**Потом обычно спрашивают**

- Почему NSCache не замена дисковому кэшу или URLCache?
- Как выбираешь totalCostLimit для картинок?
- Когда обычный словарь всё ещё правильный инструмент?

</details>

<h2 id="dsym">dSYM</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

dSYM — бандл отладочных символов, который мапит адреса в краш-логе на файл и строку. App Store / Xcode архивирует его вместе со сборкой; краш-репортерам нужен ровно тот UUID. Потерял dSYM — получишь hex-фреймы. Заливай dSYM вместе с бинарём: Organizer, Fastlane, аплоад вендора. История «Apple перекомпилирует Bitcode, скачай новые dSYM» — прошлое. Типичный промах: состричь символы и полгода жить с «unsymbolicated».



```text
# UUID in the crash must match:
dwarfdump -u App.app.dSYM
# Xcode Organizer symbolicates if the archive is still on the Mac.
```


**Потом обычно спрашивают**

- Кто символицирует — девайс, репортер или твой CI?
- Что будет, если залить dSYM от другой сборки?
- Где живут dSYM TestFlight / Organizer?

</details>

<h2 id="in-memory-cache">Кэш в памяти</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

In-memory кэш держит недавно нужные значения в RAM, чтобы не ходить на диск и не делать сетевой круг. На iOS обычный инструмент — NSCache: выселяет объекты, когда системе тесно по памяти, потолок ставишь countLimit и totalCostLimit. Обычный Dictionary ничего не выселяет: растёт, пока сам не бросишь или процесс не съест jetsam. NSCache ещё безопасно трогать с нескольких очередей, сырой словарь — нет. Стоимость ставь по реальности — байты декодированной картинки, не «единица на элемент» — и кэш считай необязательным: miss всё равно должен дать правильный результат. HTTP-переиспользование — другой слой: URLCache хранит ответы, не твои декодированные модели.



```swift
final class ImageCache {
    private let cache = NSCache<NSString, UIImage>()

    init() {
        cache.countLimit = 100
        cache.totalCostLimit = 50 * 1024 * 1024
    }

    func image(for key: String) -> UIImage? {
        cache.object(forKey: key as NSString)
    }

    func store(_ image: UIImage, for key: String) {
        let cost = image.pngData()?.count ?? 0
        cache.setObject(image, forKey: key as NSString, cost: cost)
    }
}
```


**Потом обычно спрашивают**

- Когда NSCache лучше словаря, а когда словаря хватает?
- Как выбираешь totalCostLimit для декодированных картинок?
- Где кончается URLCache и начинается кэш уровня приложения?
- Что будет с in-memory кэшем, когда приложение suspended или убито?
- Как сделаешь LRU, если NSCache нельзя?

</details>

<h2 id="crashes">Найти и починить краш</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Краш — процесс оборвался: непойманная ошибка Swift, force unwrap, выход за границы, fatalError / assertion, низкоуровневый сигнал вроде EXC_BAD_ACCESS. Начинаешь с символицированного краш-репорта — Xcode Organizer, сторонний репортер или MetricKit MXCrashDiagnostic — и читаешь тип исключения, падающий поток и фреймы, которые реально твои. Воспроизводишь на той же ОС, локали и вводе; не вышло — хлебные крошки вокруг верхних фреймов и ждёшь следующий удар. Watchdog 0x8badf00d — не «рандом»: главный поток слишком долго был занят на запуске или в фоне. Чинишь причину, не симптом: не оборачивай force-unwrap в try? и не называй это победой.



```swift
enum FeedError: Error { case emptyPayload }

func decodeFeed(from data: Data) throws -> [Item] {
    let decoded = try JSONDecoder().decode(Feed.self, from: data)
    guard !decoded.items.isEmpty else { throw FeedError.emptyPayload }
    return decoded.items
}

// In a crash: look at Thread 0 vs the crashing thread,
// then the first frame in your module after UIKit / libswift.
```


**Потом обычно спрашивают**

- Как символицировать краш с девайса, которого нет на столе?
- Чем EXC_BAD_ACCESS отличается от Swift runtime trap?
- Как копать watchdog kill на запуске?
- Когда сторонний crash reporter стоит Organizer плюс MetricKit?
- Краш только в проде, на твоём телефоне никогда — что собираешь дальше?
- Что такое dSYM и что будет, если его потерять?

</details>

<h2 id="performance-issues">Найти и починить проблемы производительности</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

«Приложение тормозит» — не диагноз. Режь жалобу на запуск, hitch при скролле, hang по тапу и time-to-first-frame, потом меряй. Time Profiler показывает, кто держит CPU; Main Thread Checker и hang-диагностика — работу, которой не место на UI-очереди; Core Animation / GPU frames — overdraw и offscreen-проходы; os_signpost плюс hang rate MetricKit скажут, сдвинул ли фикс стрелку. Типичные победы на iOS: JSON decode, downsample картинок и файловый I/O не на главном потоке; переиспользовать ячейки; декодировать картинки в размер экрана; не молотить лейаут в layoutSubviews / пересчёте body. Не оптимизируй экран, который не профилировал — первый заход в Instruments обычно сюрприз.



```swift
import os.signpost

private let log = OSLog(subsystem: "app.feed", category: "load")

func loadFeed() async {
    let signpostID = OSSignpostID(log: log)
    os_signpost(.begin, log: log, name: "LoadFeed", signpostID: signpostID)
    let data = try? await api.feed()
    let items = await Task.detached { decode(data) }.value
    await MainActor.run { table.reload(items) }
    os_signpost(.end, log: log, name: "LoadFeed", signpostID: signpostID)
}
```


**Потом обычно спрашивают**

- Как отличить CPU-bound hitch от commit-hang в Core Animation?
- Что во время скролла таблицы на фон, что обязано остаться на main?
- Как MetricKit решит, стал ли релиз быстрее?
- Когда os_signpost лучше, чем «print и Date»?

</details>

<h2 id="app-thinning">App Thinning</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

App Thinning — как стор отдаёт только слайсы, нужные девайсу. Slicing выбирает архитектуры и ресурсы. On-Demand Resources качают ассеты по тегам позже. Bitcode умер — не называй его актуальным. App Size Report в Xcode показывает утончённый install size, не ipa, который залил. Практические рычаги — asset catalog с картинками под девайс и UIRequiredDeviceCapabilities. Типичный промах: положить @3x-ролики в основной бандл «для всех» или назвать жирный архив размером, который видит пользователь.



```text
Xcode → Product → Archive → Distribute App → App Thinning
  → App Size Report (install size per device)
On-Demand: NSBundleResourceRequest(tags: ["level3"])
```


**Потом обычно спрашивают**

- Install size, download size и твой ipa?
- Когда On-Demand Resources имеют смысл против CDN?
- Что Bitcode делал раньше и почему умер?

</details>

<h2 id="battery">Проблемы с батареей</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Батарею почти всегда жрут радио, GPS или CPU, который никогда не idle — не «Swift медленный». Непрерывные апдейты kCLLocationAccuracyBest, UIBackgroundModes, которые не дают уснуть, сканирование BLE, таймер или display-link, который тикает при выключенном экране — обычные подозреваемые. Сеть в тесном ретрае и декод больших картинок на главном потоке тоже не дают CPU уснуть. Меришь Instruments Energy Log или отчётами MetricKit MXAppExitMetric / energy, потом подтверждаешь системным экраном Battery после контролируемой сессии. Сначала политику: significant-change или visit monitoring вместо GPS всегда, коалесь сеть, стопай таймеры в sceneDidEnterBackground, роняй точность, когда UI она не нужна.



```swift
func startLocationIfNeeded() {
    manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
    manager.distanceFilter = 50
    manager.pausesLocationUpdatesAutomatically = true
    manager.allowsBackgroundLocationUpdates = false
    manager.startUpdatingLocation()
}

func sceneDidEnterBackground() {
    displayLink?.isPaused = true
    locationManager.stopUpdatingLocation()
}
```


**Потом обычно спрашивают**

- Significant-change location и непрерывный GPS — чем платишь?
- Какие background modes стоят батареи и как это защищаешь на ревью?
- Как доказать, что батарею жрёт экран, а не ОС валит на твой процесс?
- Что крутящийся CADisplayLink делает с энергией, когда приложение inactive?

</details>

### Senior

<h2 id="launch-time">Время запуска</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Запуск — pre-main: dyld мапит образы, rebase/bind, настройка ObjC, +load и static init — плюс post-main: от didFinishLaunching до первого кадра. DYLD_PRINT_STATISTICS режет pre-main; MetricKit / os_signpost закрывают остальное — не Date в main. Что двигает стрелку: меньше динамических библиотек, меньше ObjC-метаданных, никакого I/O в +load, аналитику отложить до после первой отрисовки. Watchdog примерно 20 секунд — режим отказа. Типичный промах: оптимизировать SwiftUI body, пока dyld грузит 40 подов до main.



```swift
func application(_ app: UIApplication,
                 didFinishLaunchingWithOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    Appearance.apply()
    Task { await analytics.start() } // after first frame, not here synchronously
    return true
}
```


**Потом обычно спрашивают**

- Pre-main и post-main — как увидеть каждый в Instruments?
- Почему static let на типе может задержать main?
- Что значит «первый кадр» для SwiftUI-приложения с @main?
- Rebase, bind, время инициализаторов — какую ручку крутишь первой?
- MetricKit и Date в main — какой цифре веришь на ревью?

</details>

<h2 id="binary-size">Размер бинарника / IPA</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Размер пакета — не App Thinning. Thinning — что стор шлёт на один девайс; этот вопрос — как ужать то, что заливаешь. Читай Link Map / App Size Report: жирные символы __TEXT, толстые архитектуры, которые всё ещё эмбедишь, мёртвые ресурсы, динамические фреймворки, которые не стрипаются как статический архив. Режешь: asset catalog плюс HEIC, выкидываешь неиспользуемые локали, сливаешь свои dylib, dead_strip, не возишь вторую копию Swift в старом эмбеде. Типичный промах: назвать жирный ipa цифрой для пользователя или удалить ресурс, который должны были держать On-Demand Resources.



```text
Build Settings → Write Link Map File = YES
# then search the map for the biggest .o / metal / strings
```


**Потом обычно спрашивают**

- Link Map, App Size Report и утончённая установка на телефоне?
- Почему динамический Swift-пакет может раздуть __TEXT сильнее того же кода в таргете приложения?
- Что исторически делало шифрование __TEXT со сжимаемостью?

</details>

<h2 id="compile-time">Время компиляции</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Медленная компиляция обычно широкий модуль и шумный type-check выражения. Режь таргеты, чтобы правка вью не пересобирала сеть. На огромных литералах и вложенных цепочках map / combineLatest ставь явные типы. Не тащи дюжину CocoaPods, каждый из которых валит весь workspace; SPM с меньшим числом мелких продуктов помогает. @inlinable и whole-module optimization меняют compile time на runtime. Debug и Release — разные часы. Типичный промах: «купи быстрее Mac» до того, как измерил, на каком файле сидит swift-frontend — флаг debug-time-function-bodies.



```swift
// Helps the type checker on a long Combine chain
let enabled: AnyPublisher<Bool, Never> = email
    .combineLatest(password)
    .map { !$0.isEmpty && $1.count >= 8 }
    .eraseToAnyPublisher()
```


**Потом обычно спрашивают**

- Как найти одну функцию, которую type-check ест 10 секунд?
- Когда резать таргет, а когда хватит internal-файла?
- Debug и Release — что реально меняет время компиляции?
- Монорепа с сотнями локальных пакетов — что меряешь, прежде чем резать ещё раз?

</details>
