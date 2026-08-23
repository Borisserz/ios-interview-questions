# iOS Interview Questions

<p align="center">
  <a href="./README.md"><img src="https://img.shields.io/badge/English-8B9099?style=for-the-badge&labelColor=12141A" alt="English"></a>
  <a href="./README.ru.md"><img src="https://img.shields.io/badge/Русский-F05A28?style=for-the-badge&labelColor=12141A" alt="Русский"></a>
</p>

<p align="center">
  <img src="./assets/readme/hero.svg" width="100%" alt="iOS Interview Questions: устные ответы. Счётчики карточек, practice и тем.">
</p>

<p align="center">
  <a href="#start-here">Часто спрашивают</a> · <a href="#study-paths">Маршруты</a> · <a href="docs/ru/swift.md">Swift</a> · <a href="docs/ru/memory.md">Память</a> · <a href="docs/ru/concurrency.md">Concurrency</a> · <a href="docs/ru/architecture.md">Архитектура</a> · <a href="docs/ru/uikit.md">UIKit</a> · <a href="docs/ru/swiftui.md">SwiftUI</a> · <a href="docs/ru/combine.md">Combine</a> · <a href="docs/ru/networking.md">Сеть</a> · <a href="docs/ru/persistence.md">Хранение</a> · <a href="docs/ru/performance.md">Performance</a> · <a href="docs/ru/security.md">Безопасность</a> · <a href="docs/ru/accessibility.md">Accessibility</a> · <a href="docs/ru/frameworks.md">Фреймворки</a> · <a href="docs/ru/objc-runtime.md">Objective-C runtime</a> · <a href="docs/ru/system-design.md">System design</a> · <a href="docs/ru/algorithms.md">Алгоритмы</a> · <a href="docs/ru/behavioral.md">Поведение и процесс</a> · <a href="CONTRIBUTING.md">Contributing</a>
</p>

Конспекты устных ответов на iOS-собеседования. Открой тему, прочитай вопрос, нажми **Показать ответ** — там текст, как его говорят, и Swift.

**458** карточек · **381** с ответом · **77** practice · **249** часто спрашивают · **17** тем

Ответы своими словами, не копипаст. Код и имена API — как в Swift, без перевода.

## Как учить

1. Попробуй **[одну карточку](#identity-vs-equality)** ниже — скажи ответ, потом раскрой.
2. Возьми **[маршрут](#study-paths)** (~20 мин). Или начни с [Часто спрашивают](#start-here).
3. Колоды в `docs/ru/` (английские близнецы в `docs/en/`). Карточки лежат по **Junior / Mid / Senior**.
4. Practice — только формулировка. Проговори вслух. Готового решения в карточке нет.

## Одна карточка

Скажи ответ вслух, потом раскрой. Около 60 секунд.

<h2 id="identity-vs-equality">== vs ===</h2>

<code>Junior</code> · <code>Часто</code><br>[Полная карточка](docs/ru/swift.md#identity-vs-equality)

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`==`** это `Equatable`: одно и то же *значение*. **`===`** это идентичность: один и тот же *инстанс* (только class). Два `UIView` могут быть `==`, если ты так определил, и всё равно `!==`. Два struct никогда не `===`: у них нет идентичности. Типичный промах: `===` на struct, или `==` на class, который унаследовал pointer equality `NSObject`, и ты думаешь, что сравнил поля.



```swift
class Box { var n: Int; init(_ n: Int) { self.n = n } }
let a = Box(1)
let b = a
let c = Box(1)
a === b   // true
a === c   // false
```


**Потом обычно спрашивают**

- Почему дефолтный `==` у `NSObject` часто совпадает с `===`?
- Когда `==` на class пишешь руками?
- Как это всплывает в юнит-тесте кэша?

</details>

<h2 id="study-paths">Маршруты</h2>

Конечные списки. Галочки только здесь — не на карточках. Сессия около 20 минут.

- [Junior, часто спрашивают](paths/junior-high-freq.md) — ~5 сессий
- [7 дней, Mid](paths/7-day-mid.md) — 8–12 карточек в день
- [14 дней, Senior](paths/14-day-senior.md) — плюс system design и behavioral

<h2 id="start-here">Часто спрашивают</h2>

Только названия. Открой карточку, скажи ответ, потом раскрой.

### Swift · 51 часто спрашивают

- [== vs ===](docs/ru/swift.md#identity-vs-equality) · Junior
- [Access control](docs/ru/swift.md#access-control) · Junior
- [Any vs AnyObject](docs/ru/swift.md#any-vs-anyobject) · Junior
- [Array и set — в чём разница](docs/ru/swift.md#array-vs-set) · Junior
- [Class и struct — в чём разница](docs/ru/swift.md#classes-vs-structs) · Junior
- [Closures](docs/ru/swift.md#closures) · Junior
- [Dictionary и array — в чём разница](docs/ru/swift.md#dictionary-vs-array) · Junior
- [Enums](docs/ru/swift.md#enums) · Junior
- [Float, Double и CGFloat — в чём разница](docs/ru/swift.md#float-double-cgfloat) · Junior
- [Hashable, Equatable, Comparable](docs/ru/swift.md#hashable-equatable) · Junior
- [Identifiable](docs/ru/swift.md#identifiable) · Junior
- [Nil coalescing, `??`](docs/ru/swift.md#nil-coalescing) · Junior
- [Optional chaining](docs/ru/swift.md#optional-chaining) · Junior
- [Stored vs computed properties](docs/ru/swift.md#stored-vs-computed) · Junior
- [String? и String!](docs/ru/swift.md#string-optional-vs-iuo) · Junior
- [Type safety](docs/ru/swift.md#type-safety) · Junior
- [Value type и reference type](docs/ru/swift.md#value-vs-reference) · Junior
- [deinit](docs/ru/swift.md#deinit) · Junior
- [guard](docs/ru/swift.md#guard) · Junior
- [if let и guard let](docs/ru/swift.md#if-let-vs-guard-let) · Junior
- [lazy](docs/ru/swift.md#lazy) · Junior
- [let vs var](docs/ru/swift.md#let-vs-var) · Junior
- [map и compactMap — в чём разница](docs/ru/swift.md#map-vs-compactmap) · Junior
- [mutating](docs/ru/swift.md#mutating) · Junior
- [static](docs/ru/swift.md#static) · Junior
- [switch](docs/ru/swift.md#switch) · Junior
- [try, try? и try!](docs/ru/swift.md#try-try-try) · Junior
- [willSet и didSet](docs/ru/swift.md#property-observers) · Junior
- [Коллекции в Swift](docs/ru/swift.md#collections) · Junior
- [Неявные и явные типы](docs/ru/swift.md#implicit-vs-explicit) · Junior
- [Функции высшего порядка](docs/ru/swift.md#higher-order-functions) · Junior
- [Что такое Optional](docs/ru/swift.md#optionals) · Junior
- [Что такое protocol](docs/ru/swift.md#protocols) · Junior
- [Associated types](docs/ru/swift.md#associated-types) · Mid
- [Associated values у enum](docs/ru/swift.md#enum-associated-values) · Mid
- [Copy-on-Write](docs/ru/swift.md#copy-on-write) · Mid
- [Escaping и non-escaping closures](docs/ru/swift.md#escaping-closures) · Mid
- [Extension и protocol extension](docs/ru/swift.md#extension-vs-protocol-extension) · Mid
- [Generics](docs/ru/swift.md#generics) · Mid
- [Method dispatch](docs/ru/swift.md#method-dispatch) · Mid
- [Opaque return types, `some`](docs/ru/swift.md#opaque-return-types) · Mid
- [Property wrappers](docs/ru/swift.md#property-wrappers) · Mid
- [Result](docs/ru/swift.md#result-type) · Mid
- [Result builders](docs/ru/swift.md#result-builders) · Mid
- [defer](docs/ru/swift.md#defer) · Mid
- [final](docs/ru/swift.md#final) · Mid
- [self и Self](docs/ru/swift.md#self-vs-self) · Mid
- [some vs any](docs/ru/swift.md#some-vs-any) · Mid
- [Почему immutability важна](docs/ru/swift.md#immutability) · Mid
- [Type erasure](docs/ru/swift.md#type-erasure) · Senior
- [Раскладка struct в памяти](docs/ru/swift.md#struct-memory-layout) · Senior

### Память · 7 часто спрашивают

- [Как Swift управляет памятью](docs/ru/memory.md#swift-memory-management) · Junior
- [Объясни ARC](docs/ru/memory.md#explain-arc) · Junior
- [ARC и garbage collection](docs/ru/memory.md#arc-vs-gc) · Mid
- [autoreleasepool](docs/ru/memory.md#autoreleasepool) · Mid
- [weak и unowned](docs/ru/memory.md#weak-vs-unowned) · Mid
- [Найти и починить утечку памяти](docs/ru/memory.md#memory-leak) · Mid
- [Найти и разорвать retain cycle](docs/ru/memory.md#retain-cycle) · Mid

### Concurrency · 23 часто спрашивают

- [Concurrency vs parallelism](docs/ru/concurrency.md#concurrency-vs-parallelism) · Junior
- [@MainActor](docs/ru/concurrency.md#main-actor) · Mid
- [Actor vs serial DispatchQueue](docs/ru/concurrency.md#actor-vs-serial-queue) · Mid
- [AsyncSequence](docs/ru/concurrency.md#async-sequence) · Mid
- [Checked continuations](docs/ru/concurrency.md#checked-continuation) · Mid
- [DispatchGroup](docs/ru/concurrency.md#dispatch-group) · Mid
- [DispatchSemaphore](docs/ru/concurrency.md#dispatch-semaphore) · Mid
- [GCD](docs/ru/concurrency.md#gcd) · Mid
- [GCD vs OperationQueue](docs/ru/concurrency.md#gcd-vs-operationqueue) · Mid
- [GCD vs async/await](docs/ru/concurrency.md#gcd-vs-async-await) · Mid
- [Quality of Service](docs/ru/concurrency.md#qos) · Mid
- [Sendable](docs/ru/concurrency.md#sendable) · Mid
- [Task group vs async let](docs/ru/concurrency.md#taskgroup-vs-async-let) · Mid
- [Task vs Task.detached vs TaskGroup](docs/ru/concurrency.md#task-detached-taskgroup) · Mid
- [main.async vs main.sync](docs/ru/concurrency.md#main-async-vs-sync) · Mid
- [Локи](docs/ru/concurrency.md#locks) · Mid
- [Отмена Task](docs/ru/concurrency.md#task-cancellation) · Mid
- [Потокобезопасный общий стейт](docs/ru/concurrency.md#thread-safe-state) · Mid
- [Проблемы concurrency](docs/ru/concurrency.md#concurrency-problems) · Mid
- [Reentrancy у actor](docs/ru/concurrency.md#actor-reentrancy) · Senior
- [Thread explosion](docs/ru/concurrency.md#thread-explosion) · Senior
- [Домены изоляции](docs/ru/concurrency.md#isolation) · Senior
- [Строгая concurrency в Swift 6](docs/ru/concurrency.md#swift-6-concurrency) · Senior

### Архитектура · 13 часто спрашивают

- [MVC](docs/ru/architecture.md#mvc) · Junior
- [Делегаты](docs/ru/architecture.md#delegates) · Junior
- [Dependency injection](docs/ru/architecture.md#dependency-injection) · Mid
- [Feature flags](docs/ru/architecture.md#feature-flags) · Mid
- [MVVM](docs/ru/architecture.md#mvvm) · Mid
- [Protocol-oriented programming](docs/ru/architecture.md#protocol-oriented-programming) · Mid
- [SOLID](docs/ru/architecture.md#solid) · Mid
- [Паттерн Repository](docs/ru/architecture.md#repository) · Mid
- [Паттерны в iOS](docs/ru/architecture.md#design-patterns) · Mid
- [Синглтоны — когда помогают](docs/ru/architecture.md#singletons) · Mid
- [Clean Architecture](docs/ru/architecture.md#clean-architecture) · Senior
- [MVVM-C](docs/ru/architecture.md#mvvm-c) · Senior
- [VIPER](docs/ru/architecture.md#viper) · Senior

### UIKit · 23 часто спрашивают

- [@IBOutlet и @IBAction](docs/ru/uikit.md#iboutlet-vs-ibaction) · Junior
- [Aspect fill и aspect fit](docs/ru/uikit.md#aspect-fill-vs-fit) · Junior
- [Auto Layout anchors](docs/ru/uikit.md#auto-layout-anchors) · Junior
- [Dark Mode](docs/ru/uikit.md#dark-mode) · Junior
- [Modal или push](docs/ru/uikit.md#modal-vs-push) · Junior
- [Reuse identifiers у ячеек](docs/ru/uikit.md#reuse-identifiers) · Junior
- [Safe area](docs/ru/uikit.md#safe-area) · Junior
- [Storyboard или вёрстка в коде](docs/ru/uikit.md#storyboards-vs-code) · Junior
- [UIImage и UIImageView](docs/ru/uikit.md#uiimage-vs-uiimageview) · Junior
- [UINavigationController](docs/ru/uikit.md#navigation-controller) · Junior
- [UIStackView](docs/ru/uikit.md#stack-view) · Junior
- [frame и bounds](docs/ru/uikit.md#frame-vs-bounds) · Junior
- [prepareForReuse](docs/ru/uikit.md#prepare-for-reuse) · Junior
- [Жизненный цикл UIViewController](docs/ru/uikit.md#viewcontroller-lifecycle) · Junior
- [Формула Auto Layout](docs/ru/uikit.md#autolayout-formula) · Junior
- [Collection view или table view](docs/ru/uikit.md#collection-vs-table) · Mid
- [Diffable data source](docs/ru/uikit.md#diffable-data-source) · Mid
- [Intrinsic content size](docs/ru/uikit.md#intrinsic-content-size) · Mid
- [Responder chain](docs/ru/uikit.md#responder-chain) · Mid
- [Size classes](docs/ru/uikit.md#size-classes) · Mid
- [setNeedsLayout и layoutIfNeeded](docs/ru/uikit.md#setneedslayout) · Mid
- [Как передавать данные в iOS](docs/ru/uikit.md#passing-data) · Mid
- [Таблица с картинками из сети](docs/ru/uikit.md#remote-images-table) · Mid

### SwiftUI · 23 часто спрашивают

- [@Binding](docs/ru/swiftui.md#binding) · Junior
- [@State](docs/ru/swiftui.md#state) · Junior
- [@EnvironmentObject vs @ObservedObject](docs/ru/swiftui.md#environmentobject-vs-observedobject) · Mid
- [@Published](docs/ru/swiftui.md#published) · Mid
- [@StateObject vs @ObservedObject](docs/ru/swiftui.md#stateobject-vs-observedobject) · Mid
- [Environment в SwiftUI](docs/ru/swiftui.md#environment) · Mid
- [GeometryReader](docs/ru/swiftui.md#geometry-reader) · Mid
- [Init у View vs onAppear](docs/ru/swiftui.md#init-vs-onappear) · Mid
- [LazyVStack vs VStack](docs/ru/swiftui.md#lazyvstack-vs-vstack) · Mid
- [MV vs MVVM в SwiftUI](docs/ru/swiftui.md#swiftui-mv) · Mid
- [MVVM в SwiftUI](docs/ru/swiftui.md#swiftui-mvvm) · Mid
- [ObservableObject vs @Observable](docs/ru/swiftui.md#observableobject-vs-observable) · Mid
- [PreferenceKey](docs/ru/swiftui.md#preference-key) · Mid
- [SwiftUI vs UIKit](docs/ru/swiftui.md#swiftui-vs-uikit) · Mid
- [UIKit в SwiftUI](docs/ru/swiftui.md#uikit-representable) · Mid
- [Жизненный цикл View в SwiftUI](docs/ru/swiftui.md#swiftui-lifecycle) · Mid
- [Как ObservableObject сообщает об изменениях](docs/ru/swiftui.md#observable-object-changes) · Mid
- [Какой property wrapper брать в SwiftUI](docs/ru/swiftui.md#swiftui-property-wrappers) · Mid
- [Когда SwiftUI перерисовывает View](docs/ru/swiftui.md#swiftui-rerender) · Mid
- [Почему View в SwiftUI — структуры](docs/ru/swiftui.md#views-are-structs) · Mid
- [Программная навигация](docs/ru/swiftui.md#programmatic-navigation) · Mid
- [AttributeGraph](docs/ru/swiftui.md#attribute-graph) · Senior
- [Идентичность View vs свойство с ViewBuilder](docs/ru/swiftui.md#view-identity) · Senior

### Combine · 2 часто спрашивают

- [Combine и реактивное программирование](docs/ru/combine.md#combine) · Mid
- [Как склеивать Publisher](docs/ru/combine.md#combine-operators) · Mid

### Сеть · 11 часто спрашивают

- [HTTP-методы](docs/ru/networking.md#http-methods) · Junior
- [HTTP-статусы](docs/ru/networking.md#http-status) · Junior
- [JSON](docs/ru/networking.md#json) · Junior
- [NotificationCenter](docs/ru/networking.md#notification-center) · Junior
- [URL и URLRequest](docs/ru/networking.md#url-vs-urlrequest) · Junior
- [Сетевой запрос](docs/ru/networking.md#network-request) · Junior
- [Push-уведомления](docs/ru/networking.md#push-notifications) · Mid
- [REST](docs/ru/networking.md#rest) · Mid
- [URLSession](docs/ru/networking.md#urlsession) · Mid
- [Ретрай с backoff](docs/ru/networking.md#retry-backoff) · Mid
- [Токенная аутентификация](docs/ru/networking.md#token-auth) · Mid

### Хранение · 8 часто спрашивают

- [Codable](docs/ru/persistence.md#codable) · Junior
- [UserDefaults — куда можно и нельзя](docs/ru/persistence.md#userdefaults) · Junior
- [Как на iOS хранят данные](docs/ru/persistence.md#persist-options) · Junior
- [CloudKit и Core Data](docs/ru/persistence.md#cloudkit-vs-core-data) · Mid
- [Core Data](docs/ru/persistence.md#core-data) · Mid
- [SwiftData](docs/ru/persistence.md#swiftdata) · Mid
- [Миграция Core Data](docs/ru/persistence.md#core-data-migration) · Mid
- [Стратегии ключей при декоде](docs/ru/persistence.md#key-decoding-strategies) · Mid

### Performance · 11 часто спрашивают

- [Отладка на iOS](docs/ru/performance.md#debugging) · Junior
- [Hang, hitch и краш](docs/ru/performance.md#hang-hitch-crash) · Mid
- [Instruments](docs/ru/performance.md#instruments) · Mid
- [LRU-кэш](docs/ru/performance.md#lru-cache) · Mid
- [NSCache и Dictionary](docs/ru/performance.md#nscache-vs-dictionary) · Mid
- [dSYM](docs/ru/performance.md#dsym) · Mid
- [Кэш в памяти](docs/ru/performance.md#in-memory-cache) · Mid
- [Найти и починить краш](docs/ru/performance.md#crashes) · Mid
- [Найти и починить проблемы производительности](docs/ru/performance.md#performance-issues) · Mid
- [Время запуска](docs/ru/performance.md#launch-time) · Senior
- [Размер бинарника / IPA](docs/ru/performance.md#binary-size) · Senior

### Безопасность · 6 часто спрашивают

- [App Transport Security](docs/ru/security.md#ats) · Junior
- [API-ключи](docs/ru/security.md#api-keys) · Mid
- [Encoding, encryption и hashing](docs/ru/security.md#encoding-vs-encryption) · Mid
- [Face ID / Touch ID](docs/ru/security.md#biometrics) · Mid
- [Keychain](docs/ru/security.md#keychain) · Mid
- [SSL pinning](docs/ru/security.md#ssl-pinning) · Senior

### Accessibility · 4 часто спрашивают

- [Dynamic Type](docs/ru/accessibility.md#dynamic-type) · Junior
- [Главные проблемы accessibility](docs/ru/accessibility.md#accessibility-problems) · Mid
- [Тестировать с VoiceOver](docs/ru/accessibility.md#voiceover) · Mid
- [Фокус accessibility в SwiftUI](docs/ru/accessibility.md#accessibility-focus) · Mid

### Фреймворки · 1 часто спрашивают

- [StoreKit](docs/ru/frameworks.md#storekit) · Mid

### Objective-C runtime · 6 часто спрашивают

- [Messaging и nil](docs/ru/objc-runtime.md#objc-messaging) · Mid
- [RunLoop](docs/ru/objc-runtime.md#runloop) · Mid
- [Таймер молчит во время скролла](docs/ru/objc-runtime.md#timer-runloop) · Mid
- [+load и +initialize](docs/ru/objc-runtime.md#load-vs-initialize) · Senior
- [Mach-O и dyld](docs/ru/objc-runtime.md#mach-o) · Senior
- [isa и раскладка объекта](docs/ru/objc-runtime.md#isa) · Senior

### System design · 31 часто спрашивают

- [Live ETA через polling](docs/ru/system-design.md#eta-polling) · Mid
- [Собери checkout UI за 60 минут](docs/ru/system-design.md#checkout-ui) · Mid
- [Собери симулятор матча / счёта](docs/ru/system-design.md#match-simulator) · Mid
- [Edge-first: кто владеет write](docs/ru/system-design.md#edge-first) · Senior
- [Как вести mobile system design](docs/ru/system-design.md#sd-interview) · Senior
- [Спроектируй SDUI-движок](docs/ru/system-design.md#sdui) · Senior
- [Спроектируй analytics-библиотеку](docs/ru/system-design.md#analytics-library) · Senior
- [Спроектируй deep links](docs/ru/system-design.md#deep-links) · Senior
- [Спроектируй file downloader](docs/ru/system-design.md#file-downloader) · Senior
- [Спроектируй home из рельс](docs/ru/system-design.md#home-rails) · Senior
- [Спроектируй image loader](docs/ru/system-design.md#image-loader) · Senior
- [Спроектируй live-трекер доставки](docs/ru/system-design.md#delivery-tracker) · Senior
- [Спроектируй networking-библиотеку](docs/ru/system-design.md#network-library) · Senior
- [Спроектируй news feed](docs/ru/system-design.md#news-feed) · Senior
- [Спроектируй offline-first sync](docs/ru/system-design.md#offline-sync) · Senior
- [Спроектируй offline-каталог медиа](docs/ru/system-design.md#offline-media) · Senior
- [Спроектируй pagination-библиотеку](docs/ru/system-design.md#pagination) · Senior
- [Спроектируй payment checkout](docs/ru/system-design.md#payment-checkout) · Senior
- [Спроектируй push-систему](docs/ru/system-design.md#push-system) · Senior
- [Спроектируй short-form видеоленту](docs/ru/system-design.md#short-video-feed) · Senior
- [Спроектируй sync устройств как iCloud](docs/ru/system-design.md#icloud-sync) · Senior
- [Спроектируй аудиоплеер](docs/ru/system-design.md#audio-player) · Senior
- [Спроектируй библиотеку A/B экспериментов](docs/ru/system-design.md#ab-experiments) · Senior
- [Спроектируй библиотеку шаринга геолокации](docs/ru/system-design.md#location-sharing) · Senior
- [Спроектируй видеоплеер](docs/ru/system-design.md#video-streaming) · Senior
- [Спроектируй клиент Notes / Gmail / Facebook](docs/ru/system-design.md#design-client-app) · Senior
- [Спроектируй кэш-библиотеку](docs/ru/system-design.md#caching-library) · Senior
- [Спроектируй пайплайн загрузки картинок](docs/ru/system-design.md#image-upload) · Senior
- [Спроектируй поиск с autocomplete](docs/ru/system-design.md#search-autocomplete) · Senior
- [Спроектируй чат](docs/ru/system-design.md#chat-app) · Senior
- [Счётчик unread и badge](docs/ru/system-design.md#unread-badge) · Senior

### Алгоритмы · 6 часто спрашивают

- [Big-O](docs/ru/algorithms.md#big-o) · Junior
- [Fibonacci](docs/ru/algorithms.md#fibonacci) · Junior
- [Слить два отсортированных списка](docs/ru/algorithms.md#merge-lists) · Junior
- [Sliding window](docs/ru/algorithms.md#sliding-window) · Mid
- [Two-sum](docs/ru/algorithms.md#two-sum) · Mid
- [Развернуть связный список](docs/ru/algorithms.md#reverse-list) · Mid

### Поведение и процесс · 23 часто спрашивают

- [Swift Package Manager](docs/ru/behavioral.md#spm) · Junior
- [Виды тестов](docs/ru/behavioral.md#test-types) · Junior
- [Жизненный цикл приложения и scene](docs/ru/behavioral.md#app-lifecycle) · Junior
- [CI](docs/ru/behavioral.md#ci) · Mid
- [Code signing](docs/ru/behavioral.md#code-signing) · Mid
- [Minimum deployment target](docs/ru/behavioral.md#deployment-target) · Mid
- [STAR-истории](docs/ru/behavioral.md#star) · Mid
- [Snapshot-тесты](docs/ru/behavioral.md#snapshot-tests) · Mid
- [Swift Testing](docs/ru/behavioral.md#swift-testing) · Mid
- [Take-home](docs/ru/behavioral.md#take-home) · Mid
- [XCTest и UI-тесты](docs/ru/behavioral.md#xctest) · Mid
- [Допилить готовый take-home](docs/ru/behavioral.md#improve-existing-app) · Mid
- [Как тестировать async](docs/ru/behavioral.md#test-async) · Mid
- [Код-ревью](docs/ru/behavioral.md#code-review) · Mid
- [Своё vs стороннее](docs/ru/behavioral.md#third-party-vs-custom) · Mid
- [Скрининг OA](docs/ru/behavioral.md#screening-oa) · Mid
- [Тестовые двойники](docs/ru/behavioral.md#test-doubles) · Mid
- [Фоновые задачи](docs/ru/behavioral.md#background-tasks) · Mid
- [FAANG iOS-луп](docs/ru/behavioral.md#faang-ios-loop) · Senior
- [iOS-луп маркетплейса](docs/ru/behavioral.md#marketplace-ios-loop) · Senior
- [iOS-луп продуктовой компании в Бразилии](docs/ru/behavioral.md#brazil-ios-loop) · Senior
- [iOS-луп продуктовой компании в Индии](docs/ru/behavioral.md#india-ios-loop) · Senior
- [iOS-луп продуктовой компании в СНГ](docs/ru/behavioral.md#cis-ios-loop) · Senior

## Темы

- [Swift](docs/ru/swift.md) — 95 карточек · 51 часто спрашивают
- [Память](docs/ru/memory.md) — 10 карточек · 7 часто спрашивают
- [Concurrency](docs/ru/concurrency.md) — 27 карточек · 23 часто спрашивают
- [Архитектура](docs/ru/architecture.md) — 25 карточек · 13 часто спрашивают
- [UIKit](docs/ru/uikit.md) — 46 карточек · 23 часто спрашивают
- [SwiftUI](docs/ru/swiftui.md) — 30 карточек · 23 часто спрашивают
- [Combine](docs/ru/combine.md) — 3 карточек · 2 часто спрашивают
- [Сеть](docs/ru/networking.md) — 18 карточек · 11 часто спрашивают
- [Хранение](docs/ru/persistence.md) — 16 карточек · 8 часто спрашивают
- [Performance](docs/ru/performance.md) — 14 карточек · 11 часто спрашивают
- [Безопасность](docs/ru/security.md) — 8 карточек · 6 часто спрашивают
- [Accessibility](docs/ru/accessibility.md) — 5 карточек · 4 часто спрашивают
- [Фреймворки](docs/ru/frameworks.md) — 19 карточек · 1 часто спрашивают
- [Objective-C runtime](docs/ru/objc-runtime.md) — 18 карточек · 6 часто спрашивают
- [System design](docs/ru/system-design.md) — 54 карточек · 31 часто спрашивают
- [Алгоритмы](docs/ru/algorithms.md) — 28 карточек · 6 часто спрашивают
- [Поведение и процесс](docs/ru/behavioral.md) — 42 карточек · 23 часто спрашивают

## Как добавлять вопросы

Новые вопросы — по ритуалу в [CONTRIBUTING.md](CONTRIBUTING.md): один источник за раз, один смысл — одна карточка, ответ своими словами, потом `python3 scripts/generate_readme.py`.

Лог источников лежит в `inbox/` и в git не попадает.

## Чего здесь нет

- Не дамп чужого репо, курса или платного банка.
- Без тегов компаний. Рекап из Сбера или Flipkart может дополнить карточку — на самой карточке компании нет.
- Не чеклист с галочками на карточках. Прогресс — в маршруте или в локальном `STUDY.local.md`.
- В practice нет чужих решений.
