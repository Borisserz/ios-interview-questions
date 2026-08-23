# Поведение и процесс

42 карточек · 23 часто спрашивают · [behavioral.md](../../topics/behavioral.md)

### Junior

<h2 id="spm">Swift Package Manager</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

SPM это пакетный инструмент Apple: манифест Package.swift, продукты (библиотеки или экзешники) и таргеты (модули, которые компилируешь). Xcode умеет взять пакет с git URL и запинить версию, ветку или коммит. Им пользуюсь и для чужого кода, и чтобы резать свои модули, чтобы приложение и тесты жили на одном графе сборки. Рядом с CocoaPods и Carthage в текущем Xcode это дефолт: без хаков воркспейса и без проекта Pods. Смотри пин: плавающий from: "1.0.0" это не lockfile, который ты ревьюил, и платформы в манифесте. Пакет с iOS 17 уронит проект, который ещё на iOS 16. На main я пину версию или коммит, ветку только для своего пакета в разработке. Один пакет делят iOS и виджет, если платформы это позволяют. В пакет кладу переиспользуемую логику, в апп-таргет: Info.plist, entitlements, UI. Если юристы или CI не ходят на GitHub, вендорю через binary XCFramework или зеркало. Новый проект в 2026 начинаю со SPM. pod install генерит Pods-проект и воркспейс, без воркспейса таргеты пакета не подцепятся.



```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "FeedKit",
    platforms: [.iOS(.v16)],
    products: [.library(name: "FeedKit", targets: ["FeedKit"])],
    targets: [
        .target(name: "FeedKit"),
        .testTarget(name: "FeedKitTests", dependencies: ["FeedKit"])
    ]
)
```


**Потом обычно спрашивают**

- Пин версии vs ветки vs коммита: что пускаешь на main?
- Как расшарить один пакет между iOS и widget extension?
- Что класть в таргет пакета, а что в таргет приложения?
- Как вендорить пакет, если юристы или CI не могут ходить на GitHub?
- SPM vs CocoaPods vs Carthage: с чего начнёшь приложение в 2026?
- Что на самом деле делает pod install и почему открываешь воркспейс?

</details>

<h2 id="test-types">Виды тестов</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Unit: один тип, фейки по краям, миллисекунды. Integration: несколько живых типов вместе, например Core Data in-memory плюс репозиторий. UI / functional: XCUIApplication гоняет приложение как пользователь. Acceptance: та же идея языком продукта, «пользователь может оформить заказ». Нужна пирамида: много юнитов, меньше интеграционных, тонкий UI-смоук на логин и покупку, не на каждый лейбл. Сеньорский вопрос про тесты это вопрос про архитектуру: если ViewModel требует живой сервер, зависимость кривая. Типичный промах: назвать UI-тест юнит-тестом, потому что он на XCTest, или перевёрнутая пирамида, которая на CI едет 40 минут. Snapshot сидит рядом с UI, но ловит вёрстку, не сценарий. UI на CI флакуются из-за тайминга, симулятора и анимаций. Acceptance без UI это контракт API или тест на доменном языке. Если три источника данных, фоновый синк и SwiftUI-вьюха, юниты сначала на маппинг и стейт-машину синка. Навигацию и время инжектю: роутер и часы, иначе это самое злое в тестах.



```text
Unit: Cart.canCheckout
Integration: CartStore saves into an in-memory container
UI: tap Checkout, see Receipt
```


**Потом обычно спрашивают**

- Куда садятся snapshot-тесты?
- Почему UI-тесты на CI флакуются сильнее?
- Какой acceptance-тест не является UI-тестом?
- Три источника данных, фоновый синк и SwiftUI-вьюха: какой слой юнитить первым?
- Что сложнее тестировать, навигацию или время, и что инжектишь?

</details>

<h2 id="app-lifecycle">Жизненный цикл приложения и scene</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Современные приложения scene-based. UIApplicationDelegate всё ещё получает didFinishLaunching на процесс: логи, граф зависимостей. SceneDelegate нужен, чтобы один процесс держал несколько окон: Split View на iPad, второе окно на Mac. Классические состояния UIKit всё ещё спрашивают: not running, inactive, active, background, suspended. Подвешенное приложение система может убить. Каждое окно это UIScene: sceneDidBecomeActive, sceneWillResignActive, sceneDidEnterBackground, sceneWillEnterForeground. В фоне сохраняешься, сбрасываешь кэши и добиваешь короткую задачу beginBackgroundTask. В active обновляешь данные. SwiftUI это оборачивает Environment scenePhase: active, inactive, background. Работу «один раз за установку» в sceneDidBecomeActive не кладу, оно стреляет на каждую сцену и на каждый возврат из фона. Типичный промах: считать didFinishLaunching моментом «UI уже стоит» (нет) или стартовать длинную сеть, которую не отменишь, когда сцена уйдёт в фон. Extra time на запись просишь beginBackgroundTask. Inactive это оверлей звонка, background это уже ушли. После джетсама последний экран поднимаешь state restoration, не из didFinishLaunching.



```swift
@main
struct AppMain: App {
    @Environment(\.scenePhase) private var phase

    var body: some Scene {
        WindowGroup {
            RootView()
        }
        .onChange(of: phase) { _, new in
            if new == .background { persist() }
        }
    }
}
```


**Потом обычно спрашивают**

- Что всё ещё живёт в AppDelegate, а что в scene delegate?
- Как попросить лишнее фоновое время на запись?
- inactive vs background: что из этого оверлей телефонного звонка?
- Назови состояния UIKit-приложения по порядку.
- Зачем добавили SceneDelegate и что меняет второе окно?
- Как вернуть последний экран, если система убила suspended-приложение?

</details>

<h2 id="app-store-review">App Store review</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Сторовой билд это не «CI заархивировал». Apple гоняет автопроверки (краш на запуске, private API, дырки в privacy nutrition labels и манифестах) и живое ревью по App Review Guidelines. Частые отказы: логин, который ревьюер не проходит, сломанный IAP, плейсхолдер-контент, нет usage strings, «это обёртка сайта». External в TestFlight получает более лёгкий Beta App Review, internal его пропускает. Ревью не замена твоим тестам, это ворота. Типичный промах: завезти debug-эндпоинт или захардкоженный пароль ревьюера в комментариях бинарника. Перед заливом: демо-аккаунт в заметках App Store Connect, nutrition labels и Privacy Manifest совпадают с тем, что собираешь, IAP живые в sandbox, нет краша на чистой установке без сети. После отказа 2.1 в первые сутки чиню краш или логин, отвечаю в Resolution Center, не спорю про «у меня работает». Privacy Manifest едет в бинарнике, анкета App Privacy живёт в коннекте. Required Reason API без записи в манифесте стор режет или возвращает на доработку.



```text
Checklist before upload:
- Reviewer demo account in App Store Connect notes
- Privacy Nutrition Labels + Privacy Manifest match what you collect
- IAP products ready in the sandbox
- No crash on a clean install / no network
```


**Потом обычно спрашивают**

- Internal TestFlight vs external vs App Store: где живой человек?
- Что делаешь в первые 24 часа после отказа по Guideline 2.1?
- Privacy Manifest vs анкета App Privacy: что из этого в бинарнике?
- Required Reason APIs в манифесте: что будет, если один пропустить?

</details>

<h2 id="arrange-act-assert">Arrange-Act-Assert</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

В юнит-тесте три такта. Arrange: собираешь систему и фейки. Act: один вызов, то поведение, которое проверяешь. Assert: смотришь результат и иногда что коллаборатора дёрнули. Если Act один, падения читаются. XCTest это не навязывает, это твоя дисциплина. Типичный промах: ассертить посреди сетапа или запихнуть три несвязанных действия в один test-метод. Четвёртый такт иногда называют Annihilate: tearDown, чтобы следующий тест не унаследовал мусор. Given-When-Then это тот же ритм другими словами.



```swift
func testCheckoutDisabledWhenEmpty() {
    let cart = Cart()                    // arrange
    let enabled = cart.canCheckout       // act
    XCTAssertFalse(enabled)              // assert
}
```


**Потом обычно спрашивают**

- Зачем четвёртый такт Annihilate / teardown?
- Почему больше одного Act это запах?
- Как это ложится на Given-When-Then?

</details>

<h2 id="git-flow">Git Flow</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Git Flow это модель веток: main (или master) всегда можно катить, develop это интеграция, feature/* отпочковывается от develop, release/* готовит версию, hotfix/* чинит main. Многие iOS-команды сейчас на более простом GitHub Flow: короткие feature в main, теги на App Store-билды. На собесе рассказываю модель и что реально используем, и почему трёхмесячная feature-ветка это режим отказа. Типичный промах: нарисовать схему и тут же сказать, что команда форс-пушит develop. Тег на стор режу с main после релиза или с release-ветки. Хотфикс, который должен попасть и в develop, черри-пикню или мержу обратно, иначе develop отстанет.



```text
main      •——•——•tag 1.4——•hotfix
               \         /
develop    •——•——•——•release
                \
feature/pay  •——•
```


**Потом обычно спрашивают**

- Git Flow vs GitHub Flow для еженедельного TestFlight?
- Где режешь тег для App Store?
- Что делаешь с хотфиксом, который должен ещё лечь в develop?

</details>

<h2 id="git-merge-rebase">Git merge vs rebase</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Merge добавляет merge-коммит и оставляет историю как было. Rebase переигрывает твои коммиты поверх нового базиса: прямая линия, SHA переписаны. Свой локальный фича-бранч ребейзю на main перед PR. Коммиты, которые уже кто-то стянул, не ребейзю. reset --soft оставляет изменения в стейдже, --hard выкидывает. stash паркует грязные файлы. cherry-pick копирует один коммит. Типичный промах: ребейз общего main и война force-push. Merge-коммит честнее, когда вливаешь долгоживущую ветку и хочешь видеть стык. В .gitignore на iOS обычно xcuserdata, .DS_Store, DerivedData, секреты, иногда Pods. Хук, который реально ставлю: форматирование или быстрый lint перед коммитом, не тяжёлые тесты.



```text
git fetch origin
git rebase origin/main    # your branch, not shared main
# conflict → fix → rebase --continue
```


**Потом обычно спрашивают**

- Когда merge-коммит это честная история?
- Soft vs hard reset последнего коммита?
- Для чего cherry-pick?
- Что класть в .gitignore в iOS-репо?
- Какой git hook ты бы реально поставил?

</details>

<h2 id="info-plist">Info.plist</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Info.plist это контракт приложения с ОС: bundle ID, версия, usage descriptions, URL-схемы, типы документов, background modes, ATS, scene manifest, экспорт шифрования. С iOS 17 кучу этого генерит из build settings, но privacy-строки всё равно твои: камера, гео, трекинг, Face ID, фото. Нет usage description, краш будет на промпте, не на компиляции. Ещё ждут, что ты ломал билд на CFBundleURLTypes, UIBackgroundModes и NSAppTransportSecurity. Секреты в plist не кладу, его из бандла кто угодно распакует. XML-plist читаемый, бинарный компактнее, оба держат те же типы. URL-схема это фишинг-риск, для логина её почти вытеснили Universal Links. Экспорт шифрования честно декларируешь в App Store Connect и в ключе про encryption.



```xml
<key>NSCameraUsageDescription</key>
<string>Scan a barcode on your receipt.</string>
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>myapp</string>
        </array>
    </dict>
</array>
```


**Потом обычно спрашивают**

- XML vs бинарный plist: что каждый умеет хранить?
- Какие ключи роняют рантайм, если забыть usage string?
- Что уехало из Info.plist во вкладку Info таргета / сгенерированный plist?
- Почему URL-схема это риск фишинга и что её заменило для авторизации?
- Где декларируешь шифрование, чтобы export compliance в сторе был честным?

</details>

<h2 id="scheme-vs-target">Scheme vs target</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Target это продукт, который собираешь: приложение, тестовый бандл, виджет. Scheme это рецепт: какие таргеты билдить, какие гонять / тестировать / профилировать, какие аргументы и окружение. У одного апп-таргета могут быть схемы Debug / Staging / Release, которые берут разные xcconfig. Типичный промах: «я сделал новую схему», когда нужен был новый таргет, или наоборот. Две схемы спокойно делят один таргет. Test plans живут рядом со схемой, в ней же выбираешь какой план гонять. Configuration (Debug/Release) это набор build settings, схема решает, какую конфигурацию взять.



```text
Target: MyApp, MyAppTests, MyWidget
Scheme "MyApp Staging" → build MyApp (Staging xcconfig) + tests
```


**Потом обычно спрашивают**

- Могут ли две схемы делить один таргет?
- Где живут test plans?
- Scheme vs configuration (Debug/Release)?

</details>

<h2 id="testflight">TestFlight</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

TestFlight это бета-труба Apple. Internal тестеры это люди команды в App Store Connect, быстро и без ревью. External это кто угодно по ссылке, первый билд идёт в Beta App Review. Билды живут примерно 90 дней. Distribution-серт и подходящий профиль всё равно нужны. Типичный промах: считать TestFlight заменой юнит-тестам или ждать external-тестеров в тот же час, когда залил. Инженерка и QA внутренние, в тот же день. Внешняя очередь на десять тысяч после беты-ревью. Когда билд протух, ставят новый, старый просто исчезает у тестеров. Ad Hoc это свои девайсы по UDID, enterprise это in-house, не магазин.



```text
Internal: engineering + QA, same day
External: 10k waitlist, after beta review
```


**Потом обычно спрашивают**

- Internal vs external: кому нужно ревью?
- Что происходит, когда билд протухает?
- TestFlight vs Ad Hoc vs enterprise?

</details>

<h2 id="waterfall-vs-agile">Waterfall vs Agile</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Waterfall это один проход: спека, дизайн, сборка, тест, релиз. Требования якобы заморожены. Agile (Scrum, Kanban) катит короткими ломтями, тесты внутри ломтя, и ждёт, что спека поедет. iOS-команды почти всегда в каком-то Agile, потому что App Review, релизы ОС и правки дизайна не ждут годовую фазу. Waterfall ещё жив в фикспрайсе или сертифицированной медицинской сборке. Типичный промах: «мы Agile», а релиз-поезд на полгода без шиппабельного инкремента. App Review заставляет планировать кусок как водопад: IAP, логин для ревьюера, privacy. Спринт это короткий ритм команды, майлстоун это продуктовая веха из нескольких спринтов. Поздний слом API в Agile режешь скоуп спринта, в водопаде это change request и сдвиг даты.



```text
Waterfall: lock the IA, then implement every screen, then QA.
Agile: ship onboarding this sprint, feed next, change the feed when review data lands.
```


**Потом обычно спрашивают**

- Где App Review заставляет планировать больше как waterfall?
- Чем спринт отличается от майлстоуна?
- Как в каждой модели переживаешь поздний слом API?

</details>

### Mid

<h2 id="ci">CI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

CI это машина, которая гоняет проверки на каждый пуш: сборка, юниты, иногда UI и линт. На iOS это Xcode Cloud, GitHub Actions плюс xcodebuild, или Fastlane. Красный PR должен быть немержабельным, не Slack-сообщение, которое все игнорят. TestFlight и внутренний деплой это вторая джоба, не замена тестам. Типичный промах: «у нас есть CI», который только архивирует и никогда не тестит. На каждый PR: сборка и юниты. Ночью можно UI, перф, полный матричный симулятор. UI на каждом PR не держу толстым, иначе 40 минут: один смоук, остальное nightly. Fastlane удобен, когда много полок (сертификаты, TestFlight), сырой xcodebuild проще отладить. CD начинается там, где артефакт уезжает людям: TestFlight это уже CD, не CI.



```yaml
# sketch — GitHub Actions
# xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16'
```


**Потом обычно спрашивают**

- Что держать на CI, а что только в nightly?
- Как не дать симуляторным UI-тестам сделать каждый PR на 40 минут?
- Fastlane vs сырой скрипт на xcodebuild?
- CI vs CD: куда садится TestFlight?

</details>

<h2 id="code-signing">Code signing</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Code signing это проверка ОС, что бинарник собрала известная команда и его не меняли. Нужны сертификат (кто ты), provisioning profile (какой app ID, какие девайсы и entitlements) и identity в связке ключей, которой Xcode подписывает на линковке. Dev-профили привязаны к зарегистрированным девайсам. Дистрибуция это Ad Hoc, App Store или Developer ID / нотаризация на Mac. Entitlements (iCloud, пуши, associated domains, App Groups) должны совпасть с порталом и профилем, иначе установка падает с туманным «valid provisioning profile». Automatic signing нормален, пока не CI. На CI кладёшь distribution-серт и профиль как секреты и перестаёшь жать Try Again в Xcode. Когда девайс не ставит билд: бандл и команда совпадают с порталом, профиль знает этот UDID и твои entitlements, identity в связке не протух, capabilities в Xcode совпали с App ID. В .entitlements то, что просит приложение, в профиле то, что портал разрешил. Виджету и Watch нужен свой профиль, у них свой bundle ID. errSecInternalComponent после ротации серта часто значит, что в связке каша или codesign не дотянулся до identity.



Spoken outline when a device install fails:

1. Bundle ID and team match the portal.
2. The profile includes this device UDID and the entitlements you enabled.
3. The signing identity is in the keychain and not expired.
4. Capabilities in Xcode match the App ID — push, associated domains, App Groups.


**Потом обычно спрашивают**

- Что живёт в .entitlements, а что в provisioning profile?
- Чем сертификат отличается от provisioning profile?
- Почему виджету или Watch-таргету нужен свой профиль?
- Как подписывать на CI без связки ключей с ноутбука разработчика?
- Что обычно значит errSecInternalComponent после ротации сертификата?

</details>

<h2 id="deployment-target">Minimum deployment target</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Deployment target это самая старая ОС, на которую ещё ставишься. Это не SDK, с которым компилируешь: всегда собираешь против свежего SDK и новые API закрываешь @available / if #available. Поднять таргет значит выкинуть ветки #available и пользоваться Swift concurrency, SwiftUI и StoreKit 2 без бэкдеплоя. Опустить или держать низко это продуктовый созвон: аналитика по доле ОС, не любовь к языку. Weak linking и @available не дают бинарнику с iOS 16 трогать символ iOS 18. Данные это отсечка стора и краши на старых ОС, не «мне нравятся API iOS 18». В Xcode SDK и deployment target разные поля, их путают постоянно. Вызов iOS 18 API на 16 без проверки это краш на символе. iOS 16 дропаю, когда доля и краши уже не стоят веток #available. platforms: в SPM и availability в коде разъезжаются, если пакет новее таргета приложения.



```swift
func presentPaywall() {
    if #available(iOS 17.0, *) {
        showStoreKit2Paywall()
    } else {
        showStoreKit1Paywall()
    }
}

@available(iOS 17.0, *)
func showStoreKit2Paywall() { /* Product.products(for:) */ }
```


**Потом обычно спрашивают**

- SDK vs deployment target: что ты только что поменял в Xcode?
- Что будет, если вызвать API iOS 18 на iOS 16 без проверки?
- Как решаешь дропнуть iOS 16 в этом квартале?
- Как Swift availability и platforms: в SPM разъезжаются?

</details>

<h2 id="star">STAR-истории</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Поведенческий ответ это история, не «да, я лидер». STAR: Situation одним предложением, Task что было на тебе, Action большая часть эфира (что сделал ты), Result исход и цифры, если есть. Держу маленький набор: конфликт, сорванный дедлайн, менторство, злой баг, фича, которой горжусь. Говорю вслух, скрипт не зубрю. Личные проекты считаются. Типичный промах: четыре минуты Situation и одно предложение Action. Если рабочей истории нет, беру сайд-проект: там тоже конфликт скоупа и баг в проде у себя. Про провал говорю своими руками и что поменял в процессе, команду не сливаю. Action это то, за что тебя нанимают. Amazon LP, Googleyness, Meta behavioral это одни и те же истории под другими ярлыками, акценты разные: ownership, collaborative, impact.



```text
S: Release week, checkout API started 500ing.
T: I owned the iOS client hotfix.
A: I added a client timeout + retry, shipped a feature flag, wrote the postmortem.
R: Error rate back under 0.2% the same day; we kept the flag for the next API migrate.
```


**Потом обычно спрашивают**

- Если рабочей истории нет, сайд-проект считается?
- Как говорить про провал, не сливая команду?
- Почему большую часть ответа надо отдать Action?
- Amazon LP vs Googleyness vs Meta behavioral: те же истории, другие ярлыки?

</details>

<h2 id="snapshot-tests">Snapshot-тесты</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Snapshot-тест рисует вьюху или контроллер и сравнивает пиксели, либо сериализованное accessibility-дерево, с эталоном. Ловишь случайные сдвиги вёрстки и копирайта, которые юниты пропускают. Они медленнее юнитов и хрупкие на дельтах ОС, шрифта и симулятора, поэтому пинишь симулятор и смотришь диффы в PR. Типичный промах: снимать живой экран с URLSession или считать сьют на две тысячи картинок заменой юнитам. Картинка ловит визуал, accessibility/hierarchy ловит структуру и голос VoiceOver и меньше дрожит от рендера. CI падает при зелёном Маке, когда другая версия Xcode, симулятор или scale. Не снимаю живые фиды, вечный спиннер и что угодно с сетью. Кнопка дизайн-системы snapshot заслуживает, живой фид обычно нет. Если на CI не запинить Xcode, эталоны разъедутся у каждого ноутбука.



```swift
func testEmptyCartLayout() {
    let view = CartView(items: [])
    // assertSnapshot(of: view, as: .image) // swift-snapshot-testing
    XCTAssertEqual(view.accessibilityLabel, "Cart empty")
}
```


**Потом обычно спрашивают**

- Image snapshot vs snapshot accessibility / иерархии?
- Почему CI упал, а у тебя на Маке прошло?
- Что ты как раз не снимаешь snapshot-ом?
- Кнопка из дизайн-системы vs живой фид: кому snapshot нужнее?
- Пин Xcode на CI: что ломается, если у всех ноутбуков разные версии?

</details>

<h2 id="swift-testing">Swift Testing</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift Testing это новый раннер рядом с XCTest: функции @Test без сабкласса XCTestCase, #expect пишет и идёт дальше, #require останавливает, @Suite для групп, параметризованные @Test(arguments:). Трейты скипают или сериализуют: disabled, timeLimit, serialized. Мигрирую на месте: новые тесты в Swift Testing, старый XCTest не трогаю, пока не полез в файл. Оба могут жить в одном таргете, но не внутри XCTestCase. Interop даёт из @Test позвать XCTFail, или Issue.record из XCTest. В complete/strict это ошибка. XCTest оставляю для UI, measure и ObjC-исключений. Типичный промах: в первый день переписать все XCTAssert или относиться к #expect как к ассерту, который абортит. #require берёт try, потому что бросает, #expect нет. try #require(optional) на nil стопит тест, force-unwrap роняет процесс. #expect(throws:) проверяет ошибку без ручного do/catch. confirmation лучше await, когда API на колбэке. Test.cancel рвёт текущий прогон, disabled не стартует, XCTSkip это старый XCTest.



```swift
import Testing

@Test("empty cart disables checkout")
func emptyCart() {
    #expect(Cart().canCheckout == false)
}

@Test(arguments: [0, 1, 2])
func quantity(_ n: Int) {
    #expect(n >= 0)
}
```


**Потом обычно спрашивают**

- #expect vs #require vs XCTAssert?
- Как параметризовать тест в XCTest и в Swift Testing?
- UI-тесты уже переезжают на Swift Testing?
- Почему @Test по умолчанию параллельные и что меняет serialized?
- Почему #require нужен try, а #expect нет?
- try #require(optional) vs force-unwrap в тесте: что ещё бежит после nil?
- #expect(throws:) vs ручной do/catch?
- Confirmation / callback: когда это лучше, чем await?
- Issue.record vs XCTFail: когда interop превращает pass в warning?
- Test.cancel vs disabled vs XCTSkip?

</details>

<h2 id="take-home">Take-home</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Take-home судят как PR, не как головоломку. Две частые формы: с нуля (список, пагинация, empty/error, DI, пара тестов) и допилить стартер (закрытую папку не переписывать, привезти empty/error, один лишний экран, тесты). Сначала уточняю бриф: какую архитектуру хотят, таймбокс, must-have vs nice. Дальше: чисто собирается, без ворнингов, короткий README (как запустить, что выкинул и почему), видимая архитектура, тесты там, где окупаются, и я рядом с лимитом времени. Лишние библиотеки не тащу, если не написал зачем. Смотрят структуру и трейдоффы, не полировку. Типичный промах: шедевр на 20 часов под промпт на 2, README без «как запустить», или переписка, которая ломает существующий клиент. Когда время жмёт, первым режу полировку, лишние экраны и третью библиотеку. Архитектуру показываю папками и одним абзацем в README, не эссе на четыре страницы.



```markdown
# Feed
Xcode 16, iOS 17. Open `Feed.xcodeproj` and run the `Feed` scheme.
I skipped pagination to stay in the time box; the list is a `UITableView` + MVVM.
```


**Потом обычно спрашивают**

- Что режешь первым, когда времени мало?
- Когда добавляешь стороннюю сетевую библиотеку?
- Как показать архитектуру без эссе на четыре страницы?
- Список товаров из JSON (картинка, имя, цена, сортировка): что режешь первым?
- Соцфид из JSON users/posts/albums: как моделируешь экраны?
- Бриф в духе GitHub Followers (поиск юзера, пагинированная коллекция, избранное в UserDefaults, без сторонних либ): что привезёшь за четыре часа?
- Кастомная анимированная UI (онбординг / стопка карточек): сначала полировка или скучный рабочий список?
- Machine-coding на 90 минут: рабочее демо vs лишние правила, которые не доделал?
- Живой чекаут на 60 минут (список, итоги, способ оплаты): что на экране к 25-й минуте?
- 90 минут на своём ноуте, интернет можно: когда поиск в гугле это сигнал, а когда промах?
- Стартер с пятью TODO (анимация, async-очередь, список, настройки): какие два привезёшь?
- Они закрывают папку ios-interview-test/: чего не трогаешь?
- Контакты / адресная книга из JSON, офлайн-кэш, фейковый URLSession: что в первом PR?
- Экран на 40 минут clone-into-Xcode vs take-home на 2–4 часа: что выкидываешь?
- «Тестовый проект» маркетплейса на 1–3 недели: считаешь это take-home?

</details>

<h2 id="xctest">XCTest и UI-тесты</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

XCTest это раннер Apple: сабкласс XCTestCase (в ObjC интерфейс от XCTestCase), методы на test, ассерты вроде XCTAssertEqual и XCTUnwrap, плюс async await и XCTestExpectation. setUp / setUpWithError бегут до каждого теста, tearDown после. Это жизненный цикл, не init. Юниты сидят в хост-аппе или пакете и UI не запускают. UI-тесты поднимают XCUIApplication(), ищут XCUIElement и они медленнее и флакучее. Держу тонкий смоук: запуск, логин, одна покупка, логику кладу в юниты. Ещё есть measure и аттачи. Сьют нужен, чтобы зафиксировать поведение, которое можно прогнать снова: рефакторинг должен ронять тест, не пользователя в TestFlight. Мид-ответ называет этот разрез, как ждёшь (fulfill expectation, XCTNSPredicateExpectation или Swift concurrency, не sleep) и почему тест в прод-сеть это не юнит. Фейковый API в UI-тестах инжектю launch arguments или debug-сборкой. На CI UI падает из-за другого симулятора, анимаций и нагрузки. PM продаю не процент покрытия, а «регресс чекаута ловим до ревью». setUpWithError умеет кидать, lazy на тест-кейсе живёт дольше одного теста и это ловушка. После перехода на Swift Testing в XCTest остаются UI, measure и ObjC-исключения.



```swift
final class CartTests: XCTestCase {
    func testEmptyCartDisablesCheckout() {
        let cart = Cart()
        XCTAssertFalse(cart.canCheckout)
    }
}

final class CheckoutUITests: XCTestCase {
    func testCheckoutButtonExists() {
        let app = XCUIApplication()
        app.launch()
        XCTAssertTrue(app.buttons["Checkout"].waitForExistence(timeout: 2))
    }
}
```


**Потом обычно спрашивают**

- Как ждать экран с сетью без sleep(3)?
- Что класть в UI-тест, что в snapshot, что в юнит?
- Как инжектнуть фейковый API в UI-тесты?
- Почему UI-тест упал на CI и прошёл на твоём Маке?
- Какую пользу ты реально продаёшь PM, если не процент покрытия?
- setUp vs setUpWithError vs lazy-свойство на тест-кейсе?
- Expectation vs async/await в тесте?
- Что остаётся в XCTest, когда берёшь Swift Testing: UI-тесты, measure, что-то ещё?

</details>

<h2 id="improve-existing-app">Допилить готовый take-home</h2>

<code>Mid</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Тебе дают рабочий стартер: поиск слова и определение или тонкий список. Есть 2–4 часа. С нуля не переписывай. Привези empty и error, один лишний экран или второй эндпоинт, DI через протокол, чтобы тест мог подсунуть фейковую сессию, и README что выкинул. Собес про то, оставил ли ты существующий код живым. Чужое готовое решение не вставляй.


**Потом обычно спрашивают**

- Пасхалка vs обработка ошибок: что они реально скорят?
- Переписать всё на SwiftUI за четыре часа: начинаешь?
- Как показать изменение PR-ом, который просмотрят за десять минут?

</details>

<h2 id="test-async">Как тестировать async</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Асинхронный юнит-тест ждёт работу, а не sleep. В XCTest помечаю тест async throws и await-у функцию. XCTestExpectation оставляю, только если API всё ещё на колбэках. Swift Testing так же: confirmation и await. UI-ассерты гоняю на MainActor или изолирую тип теста. Летающие таски рву в tearDown, чтобы один тест не протекал в следующий. Инжектю часы или фейковый URLProtocol, в сеть не хожу. Типичный промах: wait(for:timeout:) вокруг Task, который не удержал, или ассерт @MainActor-свойства с фонового потока теста. Expectation в 2026 ещё нужен на старых completion-API. Отмену проверяю так: стартую, cancel, смотрю что прогресс или файл не дописался. confirmation в Swift Testing это тот же «подожди сигнал», только без XCTestCase.



```swift
func testLoadSetsTitle() async throws {
    let model = FeedModel(client: FakeClient(rows: ["Hi"]))
    try await model.refresh()
    XCTAssertEqual(model.title, "Hi")
}
```


**Потом обычно спрашивают**

- Когда expectation в 2026 всё ещё обязателен?
- Как проверить, что cancel реально останавливает загрузку?
- confirmation в Swift Testing vs XCTestExpectation: что поменялось?

</details>

<h2 id="code-review">Код-ревью</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Нормальное ревью отвечает на три вопроса: изменение правильное, его безопасно катить, и следующий человек сможет его поменять. Сначала читаю описание PR и тест-план, потом дифф в порядке зависимостей: модель и API раньше вьюхи, которая их ест. Блокирую баги в поведении, потерю данных, прыжки на main, дырки в usage strings и тесты, которые не упадут, если баг вернуть. Стиль оставляю неблокирующим комментом или отдаю форматтеру. Если не понимаю выбор, спрашиваю, а не переписываю PR под свой вкус. Как автор держу дифф маленьким, записываю неочевидное «зачем» и на каждый коммент отвечаю правкой или причиной. На сетевом PR строк на 200 сначала сверяю публичный API и маппинг ошибок с тикетом, потом декодинг и пустые/401 пути, ищу тест, который упадёт, если это отъедет. Смотрю main-thread и новые ATS, Keychain, privacy strings. В конце один саммари-коммент: что проверил и чего не гонял.



Spoken outline for a 200-line networking PR:

1. Confirm the public API and error mapping match the ticket.
2. Check decoding and empty/401 paths; look for a test that would fail if those regress.
3. Flag main-thread work and any new ATS / Keychain / privacy string.
4. Leave one summary comment: what you verified and what you did not run.


**Потом обычно спрашивают**

- За что ты блокируешь мерж, а что оставляешь на потом?
- Как ревьюишь PR в зоне, которой не владеешь?
- Какое описание PR достаточно хорошее, чтобы его можно было ревьюить?
- Что делаешь с ревью, где одни комментарии про стиль?

</details>

<h2 id="third-party-vs-custom">Своё vs стороннее</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

По умолчанию системная библиотека. Зависимость беру, когда это настоящий продукт (карты, платежи, краш-репортинг) или задача, которую сам плохо проживу. Спрашиваю: лицензия, размер, последний коммит, кто обновляет, сможем ли выкинуть через год, не навязывает ли границу модуля. Своё пишу, когда API маленький и центральный, тонкая обёртка над URLSession. Причину пишу в PR. Типичный промах: притащить Alamofire ради одного GET или полгода переписывать форматирование дат. Картинки: Kingfisher или Nuke, либо URLCache плюс NSCache, если экран один. JSON сначала Codable. Третью сторону оборачиваю своим протоколом, чтобы завтра сменить. В 2026 стартую со SPM. В зелёном базисе до фич: линт, CI, SPM, не набор под каждый чих. Один GET это URLSession.



```text
Need image caching → Kingfisher / Nuke, or URLCache + NSCache if the feature is one screen.
Need JSON → Codable first.
```


**Потом обычно спрашивают**

- Как обернуть стороннее, чтобы потом заменить?
- SPM vs CocoaPods vs Carthage в 2026?
- Что класть в зелёный базис (линт, CI, SPM) до фич?
- Один GET: URLSession или Alamofire?

</details>

<h2 id="screening-oa">Скрининг OA</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Первый фильтр часто платформа на 20–80 минут, не живая комната в Xcode. Две формы. Work-sample: починить лик, не трогая публичный API, провязать таблицу, маленький HTTP, протокол. В их редакторе или стартер clone-into-your-IDE. И timed contest: easy/medium алгоритмы до любой iOS-теории. MCQ (мелочи языка, «какие объекты нужны таблице») слабый сигнал, это проверка словаря. Недельный проект маркетплейса это другой продукт, не считай его четырёхчасовым take-home. Типичный промах: гринд Hard-графов к экрану, где retain cycle и UITableView, или вставка дампа платного теста. В браузере не докажешь Instruments и нормальный таргет. Если «не меняй публичный API» на лике, правишь внутренности: capture list, разрыв цикла, не сигнатуру. На contest-фильтр готовлю easy/medium на время, на hosted refactor готовлю чтение чужого кода вслух.



```text
30 min: MCQ + one leak / protocol task in the browser.
60–75 min: clone a starter, fill methods, run their tests.
Contest OA: 2–3 timed problems, then a human room if you pass.
```


**Потом обычно спрашивают**

- Редактор в браузере vs clone-to-Xcode: чего не докажешь?
- Говорят «не меняй публичный API» на лике: что тогда править?
- Contest как первый фильтр vs hosted-рефакторинг: какую подготовку снимаешь?

</details>

<h2 id="test-doubles">Тестовые двойники</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Тестовый двойник стоит вместо зависимости, чтобы юнит остался изолированным. Stub отдаёт консервы, типа User с id 1. Fake это рабочая in-memory подставка, например стор на массиве. Mock записывает вызовы, и ты ассертишь: save вызвали один раз. Spy это живой объект, который ещё и пишет лог вызовов. Я лучше возьму протокол и крошечный fake, чем библиотеку моков. Типичный промах: мок, который переписывает прод-класс, или Core Data-тест, который бьёт в on-disk shared стек. Stub не проверяет вызовы, это делает mock. URLSession фейкаю через протокол или URLProtocol, не хожу в сеть. PersistenceController.shared в тесте это не двойник, это прод. «Сейчас» инжектю как часы или замыкание, иначе тест от даты плавает. UserDefaults фейкаю своей обёрткой или suiteName, не трогаю настоящий plist.



```swift
protocol UserLoading { func load() async throws -> [User] }

struct StubUsers: UserLoading {
    func load() async throws -> [User] { [User(id: 1, name: "Ada")] }
}

final class ListViewModel {
    let loader: UserLoading
    var names: [String] = []
    init(loader: UserLoading) { self.loader = loader }
    func refresh() async throws { names = try await loader.load().map(\.name) }
}
```


**Потом обычно спрашивают**

- Stub vs mock: кто ассертит вызовы?
- Как зафейкать URLSession и не ударить в сеть?
- Почему синглтон PersistenceController.shared плохой тестовый двойник?
- Как инжектнуть «сейчас», чтобы тест от даты был детерминированным?
- Как зафейкать UserDefaults и не трогать настоящий plist?

</details>

<h2 id="background-tasks">Фоновые задачи</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Когда сцена ушла в фон, у тебя секунды, не минуты. beginBackgroundTask покупает короткое окно, чтобы дописать сейв или аплоад. endBackgroundTask вызвать обязан, иначе система убьёт. BGTaskScheduler (BGAppRefreshTask, BGProcessingTask) это современное «разбуди потом»: регистрируешь идентификаторы, сабмитишь запрос, время выбирает система. Background modes (аудио, гео, VoIP, Bluetooth) это entitlements, не общий подарок CPU. Тихий пуш content-available может коротко разбудить, если пользователь разрешил. Типичный промах: Timer, который завёл на экране и ждал, что он тикает в suspended. Не будет. Забыл endBackgroundTask: система режет процесс по expiration handler или раньше. App Review примет фон, который пользователь понимает: музыка, навигация, VoIP. Не «мне просто нужно больше CPU».



```swift
var task: UIBackgroundTaskIdentifier = .invalid
task = UIApplication.shared.beginBackgroundTask {
    UIApplication.shared.endBackgroundTask(task)
    task = .invalid
}
persist()
UIApplication.shared.endBackgroundTask(task)
```


**Потом обычно спрашивают**

- beginBackgroundTask vs BGAppRefreshTask vs тихий пуш?
- Что будет, если забыть endBackgroundTask?
- Какие background modes App Review реально пропускает?

</details>

<h2 id="binary-framework">Binary framework vs SDK</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

SDK это продукт, который отдаёшь чужим приложениям: хедеры или Swift-модуль, дока, иногда сэмпл. Binary framework (xcframework) это одна форма доставки: скомпилированные слайсы, без исходников. Бинарь везу, когда исходники нельзя открыть, хочу быстрее клиентские компиляции или несколько платформ в одном артефакте. SPM умеет и исходники, и xcframework. На собесе про версионирование, module stability (BUILD_LIBRARY_FOR_DISTRIBUTION) и очень простой публичный API. ABI-стабильный Swift на ОС Apple не делает public-типы твоего SDK резиновыми, это отдельный режим компилятора. Типичный промах: назвать SDK любой import Foo или привезти толстый .framework без слайса симулятора. Исходный пакет, если код можно отдать и ловить фиксы. Бинарь, если закрытый или тяжёлый. Статика быстрее на старте и проще в IPA, динамика шарится между таргетами и грузится позже. @_spi и узкий public берегут тебя от чужих зависимостей на внутренности. Команде не с твоего git отдают через XCFramework, Swift Package с binaryTarget или CocoaPods. ABI ОС и module stability твоего XCFramework это разные ручки.



```text
xcodebuild archive … BUILD_LIBRARY_FOR_DISTRIBUTION=YES
xcodebuild -create-xcframework \
  -framework ios.xcarchive/…/Payments.framework \
  -framework sim.xcarchive/…/Payments.framework \
  -output Payments.xcframework
```


**Потом обычно спрашивают**

- Исходный пакет vs бинарный XCFramework: когда что берёшь?
- Статическая vs динамическая линковка: что меняется на запуске и в IPA?
- Что покупают @_spi и закрытая public-поверхность?
- Как раздавать команде, которой нет на твоём git remote?
- ABI stability ОС vs module stability твоего XCFramework?

</details>

<h2 id="code-coverage">Code coverage</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Coverage это доля строк или веток, которые сьют реально выполнил. Xcode умеет отдать это по таргету. Это прожектор, не оценка: 90% геттеров хуже, чем 60% на стейт-машине чекаута. Ищу им нетестированные модули, а не валю билд на произвольном числе. Типичный промах: гнаться за 100% и тестировать SwiftUI previews. Line coverage считает строки, branch coverage ещё и false-ветки. CI роняю на падении покрытия, только если это оговорённый модуль ядра, не весь таргет. Файл на 0%, который весь UIKit-клей, оставляю в покое или закрываю одним UI-смоуком, юнитами его не мучаю.



```swift
func canCheckout(items: Int, total: Decimal) -> Bool {
    items > 0 && total > 0
}
// A test that only passes `items: 1, total: 1` leaves the false branches uncovered.
```


**Потом обычно спрашивают**

- Line coverage vs branch coverage?
- Когда ронял бы CI из-за просевшего покрытия?
- Что делать с файлом на 0%, где один UIKit-клей?

</details>

<h2 id="state-restoration">State restoration</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

State restoration возвращает человека туда, где он был, после того как система убила подвешенный процесс. Пишешь маленький restoration identifier и столько id, чтобы собрать стек: user id, playlist id, scroll offset. Не весь граф объектов. В UIKit restorationIdentifier на контроллерах и вьюхах, encodeRestorableState / decodeRestorableState или scene stateRestorationActivity / NSUserActivity. В SwiftUI SceneStorage и NavigationPath, который сам пишешь на диск. Сохраняюсь в sceneDidEnterBackground и не жду applicationWillTerminate, джетсам его пропускает. Типичный промах: запихнуть декодированный фид в UserDefaults или восстановить экран, у которого токен уже мёртв. Холодный старт на Home правильный, если нет осмысленного стека или пользователь разлогинен. Токены и тяжёлые картинки не персистю. Если токен протух, сначала логин, потом restoration, иначе покажешь чужой или пустой экран.



```swift
func sceneDidEnterBackground(_ scene: UIScene) {
    let activity = NSUserActivity(activityType: "com.app.restore")
    activity.userInfo = ["screen": "playlist", "id": currentPlaylistID]
    (scene as? UIWindowScene)?.userActivity = activity
}
```


**Потом обычно спрашивают**

- Restoration vs холодный старт всегда на Home: когда что правильно?
- Что отказываешься персистить: токены, огромные картинки?
- Как это стыкуется со стеной логина после протухшего токена?

</details>

<h2 id="swift-vs-objc">Swift vs Objective-C</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Новое я пишу на Swift: безопаснее дефолты (опционалы, value types, дженерики), нормальный stdlib, и это единственная дорога в SwiftUI и Swift concurrency. Objective-C это runtime, который они всё ещё делят: динамический диспатч, селекторы, KVO и куча старых API UIKit. На ObjC сегодня иду только если модуль уже такой, нужен динамический трюк, который Swift чисто не выражает, или библиотека так и не дала Swift overlay. Перформанс редко причина, ARC есть с обеих сторон. Мид-ответ достаточно двуязычный, чтобы прочитать стекфрейм и написать bridging header, а не ностальгировать по .m. Новую фичу не пихаю в ObjC-таргет, если его нельзя разрезать. ObjC читаю каждую неделю: хедеры UIKit, старые SDK, краш-фреймы. Стабильный ObjC-модуль «чтобы стало Swift» без продуктовой причины не переписываю. Цена interop это часть выбора, не послесловие.



Spoken outline:

1. New feature: Swift, unless it must live inside an ObjC target you cannot split.
2. I read ObjC weekly — UIKit headers, old SDKs, crash frames.
3. I do not rewrite a stable ObjC module “to make it Swift” without a product reason.
4. Interop cost (see the next card) is part of the choice, not an afterthought.


**Потом обычно спрашивают**

- Что Objective-C умеет в рантайме такого, чего Swift всё ещё не умеет?
- Когда переписывать ObjC-модуль стоит риска?
- Как value types меняют дизайн API по сравнению с сабклассами NSObject?
- Почему столько системных API в Swift всё ещё выглядят как Objective-C?

</details>

<h2 id="tdd">TDD</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

TDD значит: сначала падающий тест, который фиксирует поведение, потом минимум кода, чтобы он прошёл, потом рефакторинг, пока тест зелёный. Это инструмент дизайна для логики, которую можно изолировать: парсеры, цены, стейт-машины, маппинг. Плохо ложится на первый набросок SwiftUI-вёрстки или разовый хук в сториборде. На собесе хотят услышать, что тест всё ещё пишешь первым, когда поведение уже сформулировано, и что не притворяешься, будто каждая вьюха так родилась. Ценность в сетке регрессий и в форме API, которую тест вынудил, а не в церемонии red-green-refactor на каждой строке. Пример, который я рассказываю: пишу testEmptyCartDisablesCheckout, он красный, потому что чекаут всегда включён. Ставлю гард, тест зеленеет. Выношу флаг в view model, тест всё ещё зелёный. Добавляю кейс «корзина с одним товаром», чтобы не захардкодить false.



Spoken outline:

1. Write `testEmptyCartDisablesCheckout` — it fails because checkout is always enabled.
2. Implement the guard; test goes green.
3. Refactor the flag into the view model; test still green.
4. Add the “cart with one item” case so you did not hard-code `false`.


**Потом обычно спрашивают**

- Когда пропускаешь TDD и пишешь тест после?
- Как делать TDD типа, который ходит в URLSession, и при этом не бить сеть?
- Чем characterization-тест отличается от TDD-теста?
- Как не получить сьют, который только зеркалит реализацию?

</details>

<h2 id="xcconfig">xcconfig и окружения</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

xcconfig это мешок build settings: PRODUCT_BUNDLE_IDENTIFIER, API_BASE_URL через INFO_PLIST_KEY, SWIFT_ACTIVE_COMPILATION_CONDITIONS. Вешаешь один конфиг на конфигурацию (Debug / Staging / Release), чтобы DEV / SIT / UAT / Prod не делили захардкоженный URL. Секреты в xcconfig, если он в git, не кладу, для этого секреты CI. Типичный промах: #if DEBUG вместо «staging» и в прод уезжает чужой хост. xcconfig собирает бинарь, .env это локальная привычка с бэка, Remote Config крутит флаги уже в рантайме. Staging bundle ID держу рядом с продом отдельной конфигурацией, не копипастой в коде. #if DEBUG на продовом архиве часто ложно, staging от этого не получается.



```text
// Staging.xcconfig
API_BASE_URL = https:/$()/api.staging.example.com
SWIFT_ACTIVE_COMPILATION_CONDITIONS = STAGING
```


**Потом обычно спрашивают**

- xcconfig vs .env vs Remote Config?
- Как держать staging bundle ID рядом с продом?
- Почему #if DEBUG плохая замена окружению?

</details>

<h2 id="swift-since-2014">Как Swift менялся с 2014</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift 1 был новым языком поверх Objective-C runtime: опционалы, type inference, и синтаксис, который ещё плыл от релиза к релизу. На собесе важны несколько сдвигов, не вся хронология. ABI stability в Swift 5, 2019: runtime едет с ОС, бинарники меньше, можно опираться на системный Swift. Потом Codable, protocol-oriented stdlib, structured concurrency (async/await, actors) и SwiftUI как новый дефолт для UI. По дороге Result, property wrappers, opaque result types, Sendable, макросы. После Swift 3 source compatibility стала нормальной, приложение больше не переписываешь под каждый Xcode. Хороший ответ называет пару этих сдвигов и привязывает к шиппингу: concurrency вместо пирамиды колбэков, value types по умолчанию, ABI stability как причина, почему можно брать OS Swift. Я до сих пор читаю Objective-C, если стек смешанный, но новые модули на нём не начинаю.



Spoken outline:

1. 2014–2016: language still moving; Swift 3 source break.
2. 2019: ABI stability — runtime on the OS, smaller apps, binary compatibility.
3. Then: `Codable`, SwiftUI, Combine, then `async`/`await` replacing most callback and Combine networking.
4. Close: “I still read Objective-C when the stack is mixed; I do not start new modules in it.”


**Потом обычно спрашивают**

- Что ABI stability поменяла для бинарников в App Store и для ОС?
- Какие фичи Swift concurrency ты не возьмёшь ниже iOS 15 и почему?
- Что в кодовой базе 2026 всё ещё заставляет трогать Objective-C?
- Как говорить про SwiftUI vs UIKit, чтобы не звучать как неофит?

</details>

<h2 id="learn-framework">Как учу новый фреймворк</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Начинаю с задачи, не с кейноута WWDC. Читаю Apple overview и один сэмпл, потом крошечный спайк: счастливый путь и один фейл (permission denied, пустой стор, истекший background). Записываю, на каком потоке колбэки и что персистю. Документация плюс Instruments бьют сорокаминутный туториал. Типичный промах: тащить фреймворк в прод в тот же день, когда открыл хедер. Спайк готов к коммиту, когда я могу назвать счастливый путь, один фейл и что выкину. Если WWDC и текущая дока расходятся, побеждает дока и то, что реально компилится. Спайк кладу в отдельный таргет или gist, чтобы команда могла его удалить, а не влить в прод.



```text
Need offline notes → SwiftData sample → spike: insert, fetch, fail on disk full → then product API.
```


**Потом обычно спрашивают**

- Как понимаешь, что спайка уже хватит, чтобы коммитить?
- Сессия WWDC vs актуальная дока: что побеждает, если они спорят?
- Как отдаёшь спайк команде так, чтобы его можно было выкинуть?

</details>

<h2 id="objc-to-swift">Переезд с ObjC на Swift</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Приложение на переписку не замораживаю. ObjC-таргет пусть собирается. Добавляю Swift-файлы, они видят ObjC через bridging header. Двигаю по одной границе: новая фича на Swift, потом листовой тип, потом экран, и тонкий @objc-фасад на том, что оставшиеся .m ещё зовут. Тесты и зелёный CI на каждом ломтике лучше ветки, которая полгода живёт отдельно. Типичный промах: в одном PR и конвертировать файл, и поменять поведение, или переписать стабильный UIKit-клей. Сначала обычно модели и хелперы, не экраны. #selector и IB Action живы, пока на фасаде остаётся @objc. Полная переписка дешевле «удавки» только если модуль маленький и уже горит.



```text
1. New feature in Swift, talks to existing ObjC Session via @objc.
2. Port Session’s helpers; keep SessionClient as the ObjC name.
3. Delete the .m when no selector remains.
```


**Потом обычно спрашивают**

- Что портируешь первым: модели, сеть или экраны?
- Как сохранить живыми #selector и IB Action посреди миграции?
- Когда полная переписка дешевле, чем удавка?

</details>

<h2 id="objc-interop">Interop Swift и Objective-C</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift и Objective-C встречаются на одном runtime. Swift импортирует ObjC-хедеры через bridging header в апп-таргете или umbrella header во фреймворке. ObjC видит Swift-типы, которые наследуют NSObject и помечены @objc. Не всё мостится: Swift-структуры, енумы без @objc, дженерики и кортежи остаются на стороне Swift. На селекторы, KVO и #selector выставляешь класс через @objc / @objcMembers, чисто свифтовый API прячешь @nonobjc. Nullability в ObjC (nullable, _Nonnull) становится опционалами, без аннотаций получаешь implicitly unwrapped. Разница имён вроде initWithFoo: → init(foo:) это clang importer, её можно поправить NS_SWIFT_NAME. C и C++ из Swift зову через bridging header или Clang-модуль. Енум без @objc в .m не появится. Ошибку в ObjC-completion отдаю как NSError. @objc стоит динамического диспатча и ObjC-имени, на каждый чих его не вешаю.



```swift
@objc(IIQSessionClient)
final class SessionClient: NSObject {
    @objc func refreshToken(_ completion: @escaping (NSError?) -> Void) {
        Task {
            do {
                try await refresh()
                completion(nil)
            } catch {
                completion(error as NSError)
            }
        }
    }
}
```


**Потом обычно спрашивают**

- Как вызвать C / C++ из Swift: bridging header vs Clang-модуль?
- Bridging header vs module map: когда что нужно?
- Почему Swift enum не видно в .m файле?
- Как передать Swift-ошибку в ObjC completion handler?
- Чего стоит @objc и когда отказываешься его ставить?

</details>

<h2 id="multiplatform">Несколько платформ Apple</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Multiplatform значит: одна команда катит iOS плюс хотя бы iPadOS, macOS, watchOS, tvOS или visionOS. Это не значит, что каждый файл компилится везде. Модели, сеть и тесты живут в Swift-пакете, UI и entitlements режу по платформам. #if os(...), @available и отдельные ассет-каталоги держат граф честным. Catalyst это порт UIKit на Mac, не замена нормальному AppKit или SwiftUI Mac-приложению. На собесе называю, что шарю, что форкаю, и один конкретный рассинхрон: лимиты фона на watchOS, фокус на tvOS, менюбар на Mac, чтобы не звучало как «SwiftUI пишешь один раз». Не шарил бы между iPhone и Watch полный стор и тяжёлую навигацию. Catalyst беру, если уже большой UIKit и нужен Mac быстро. platforms: в пакете режет компиляцию, @available режет вызовы внутри. Виджеты и App Clips это отдельные таргеты с узким куском общей логики.



Spoken outline:

1. Shared: models, API client, persistence in a package.
2. Per platform: app target, Info.plist, capabilities, navigation chrome.
3. `#if os(watchOS)` around HealthKit workout sessions; iOS keeps the full storefront.
4. Test the shared package on the cheapest simulator; UI on the real idiom.


**Потом обычно спрашивают**

- Чем бы отказался делиться между iPhone и Apple Watch?
- Catalyst vs SwiftUI multiplatform-таргет: как выбираешь?
- Как availability и platforms: в пакете взаимодействуют?
- Куда в этом разрезе садятся виджеты и App Clips?

</details>

### Senior

<h2 id="faang-ios-loop">FAANG iOS-луп</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Большой тех iOS-луп это не викторина по UIKit. Луп mid-размера в 2026 часто 4–5 комнат: экран по Swift и памяти, живой Xcode (маленькая фича или лик, процесс важнее автокомплита), mobile system design (кэш, офлайн, чат, клиентские ограничения), behavioral со STAR на iOS-истории, фит с нанимающим. Большой тех всё ещё добавляет DSA. Где-то есть комната IDE build-a-screen: сначала рабочий UI, Clean Architecture потом. Железные конторы копают приватность и ограничения девайса, прежде чем ты нарисуешь балансировщик. Уровень чаще сидит на дизайне и поведении, не на том, добил ли ты Hard LeetCode. Хотят, чтобы ты говорил: уточнил, сложность, потом код. Типичный промах: вызубрить делегаты UITableView и ни разу не потренировать 45-минутный дизайн чата или фида, или рассказать одну STAR-историю в двух комнатах. Если говорят «iOS domain» и дают граф, всё равно проговариваю brute force и сложность. Mobile SD про батарею, фон, офлайн и App Review, не про Kafka. Behavioral, который кончился на 10 минут раньше, часто значит мало Action. В живом Xcode скорят рассказ и пустой/ошибка, не только компиляцию. На deadlock или data race первый инструмент это поток мысли и что откроешь в Instruments, не сразу «поставлю актор».



```text
Meta L5-ish: screen (2 coding) → onsite (behavior + mobile SD + 3 coding).
Amazon senior: every room mixes LP + coding; one long mobile SD.
Google L4 iOS: DSA (sometimes in Swift) + a short iOS-concepts tail; team match later.
```


**Потом обычно спрашивают**

- Что тренируешь, если говорят «iOS domain», а потом дают граф?
- Чем mobile SD отличается от Instagram на доске со стороны бэка?
- Почему behavioral, который кончился на 10 минут раньше, тебя напрягает?
- Живой Xcode vs общий док: что скорят кроме компиляции?
- Продуктовая iOS-команда, без LeetCode: вставляют deadlock или data race в Xcode. Какой твой первый инструмент?
- Плотный кодинг-луп: два-три medium за 45 минут. Путешествие или бегущий ответ?
- Чем луп банка или маркетплейса в СНГ другой: рефакторинг и архитектура вместо трёх LeetCode?
- Первые уточнения на device-first SD: модель приватности, 72 часа офлайна, что сервер имеет право видеть?
- IDE-раунд: когда перестаёшь украшать архитектуру и везёшь список?
- Удалённый луп для кандидата из Бразилии: те же комнаты, часто на английском. Что меняется в подготовке?

</details>

<h2 id="marketplace-ios-loop">iOS-луп маркетплейса</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Потребительские маркетплейсы (доставка, поездки, чекаут) обычно гоняют рекрутера, 60 минут живой фичи, mobile SD, behavioral. Не стопку графов. Живая комната это рабочий экран: список позиций, итоги, выбор оплаты или поиск по мок-API. Хотят ViewModel, empty/error и что-то, что бежит к 25-й минуте. Полировку и слой репозитория проговариваю как «докину потом». System design про офлайн, GPS, батарею, диспатч, не про Kafka. Соседние лупы иногда дают 90 минут на твоём ноуте с интернетом: модуль тарифа или правил, который переживёт новое требование на 50-й минуте. Типичный промах: гринд Hard LeetCode и ни одного списка, или красивый чекаут, который по двойному тапу Pay списывает дважды. К 25-й на экране список и итоги, архитектура без компиляции не считается. Городской сбор на 50-й минуте переживает закрытый протокол расчёта, не ещё один if в вьюхе. Если на скрине граф с гео-историей, brute force всё равно пишу первым.



```text
5 min: skim the starter, lock the happy path.
25 min: list + totals on screen.
45 min: pay method / confirm + empty and error.
SD: offline cart, stale GPS, what you persist across a kill.
```


**Потом обычно спрашивают**

- Рабочий UI к 25-й vs идеальная архитектура, которая не компилится?
- На 50-й минуте добавили городской сбор. Что у тебя было закрыто?
- Графы на телефонном скрине с гео-историей: всё равно сначала пишешь brute force?

</details>

<h2 id="brazil-ios-loop">iOS-луп продуктовой компании в Бразилии</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Крупные продуктовые компании Бразилии и удалённые лупы US/EU, которые оттуда нанимают, обычно гоняют скрининг, живой Xcode, mobile system design, behavioral, HM. Не викторину и не 90-минутный dump machine-coding. Скрининг это Swift, память, UIKit vs SwiftUI. Живой Xcode 60–90 минут: фича или лик, процесс и рассказ, не автокомплит. System design device-first: офлайн-синк, батарея, лимиты фона App Store. Офлайн-вопрос им обычно больше всего нравится. Behavioral хотят гибридную миграцию UIKit/SwiftUI или историю про Instruments, не «я привёз список». Удалённые комнаты часто на английском. Курсы учат Swift, не учат говорить, пока пишешь. Типичный промах: вызубрить 50 вопросов junior/pleno/sênior и зависнуть на «пользователь теряет сеть по дороге к чекауту». Offline-first: сначала что персистишь на девайсе, потом уже ящик сервера. Язык посреди ответа не скачу, если комната на английском. Локальный курс без устного прогона HWS оставляет дыру: думать вслух. С маркетплейс-лупа с FAANG-подготовки снимаю стопку Hard LeetCode.



```text
30–45 min screen: Swift, ARC, UIKit vs SwiftUI.
60–90 min live Xcode: small feature, narrate, handle the empty state.
45 min SD: offline-first feed or checkout; battery and background last.
45 min STAR + HM.
```


**Потом обычно спрашивают**

- Offline-first SD: что персистишь, прежде чем рисовать ящик сервера?
- Технические комнаты на английском: переключаешь язык посреди ответа?
- Локальный курс vs устный прогон HWS: чего всё ещё не хватает?
- Луп маркетплейса (живой чекаут, почти без LeetCode): что снимаешь с FAANG-подготовки?

</details>

<h2 id="india-ios-loop">iOS-луп продуктовой компании в Индии</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Крупные продуктовые компании Индии часто гоняют OA / DSA, комнату machine-coding, разбор, HM. Не стопку UIKit-викторины. Machine coding это 90–120 минут: маленькое рабочее приложение или in-memory LLD (список плюс движок правил), MVVM или понятные модули, правильная логика, имена, которые защитишь. Полировка UI обычно вне скоупа. Потом садятся и спрашивают: как добавить новое правило, не переписывая скорер. Типичный промах: красивый экран и switch, который не переживёт wide или extra event, или 40 минут диаграмм и ничего, что запускается. Сначала 30 минут на сущности и лишние правила как протоколы, потом два экрана или драйвер с тестами и демо счастливого пути, потом разбор расширяемости. Рабочее демо с двумя дырками бьёт идеальный дизайн, который не бежит. Новые правила матча или заказа живут в протоколе плюс енум, не в ещё одном if. Библиотеку картинок не тащу, если время жмёт, хватит плейсхолдера. Бразильский луп это живой Xcode и offline-first SD, не 90-минутный движок правил.



```text
30 min: read the brief, lock entities + extra rules as protocols.
90 min: two screens or a driver + tests; demo the happy path.
45 min: walkthrough — extensibility, edge cases, complexity.
```


**Потом обычно спрашивают**

- Рабочее демо с двумя недоделанными extras vs идеальный дизайн, который не запускается?
- Где живут новые правила матча или заказа: енум плюс протокол или ещё один if?
- Разрешают любую библиотеку картинок. Добавляешь?
- Чем луп продуктовой компании в Бразилии другой: живой Xcode и offline-first SD, не 90-минутный движок правил?

</details>

<h2 id="cis-ios-loop">iOS-луп продуктовой компании в СНГ</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Крупные продуктовые компании СНГ (банки, классифайды, супер-аппы) обычно гоняют HR, теорию и платформу, практическую комнату, team match. Не стопку графов как в FAANG. Практическая комната часто из двух половин: hosted-рефакторинг (заставь этот Playground или веб-редактор собраться, назови запахи, добавь тест) и архитектурная доска (фича, не Pastebin). Живой кодинг, если он есть, easy/medium в Playground, и они скорят думание вслух сильнее оптимального дерева. Теория, которую реально скорят: память, GCD и изоляция, персистенс, Swift, UI, паттерны. Типичный промах: гринд только LeetCode Hard и завис, когда вставили ViewController на 80 строк и сказали «почисти». На рефакторинге первым называю, что сломано для продакшена: цикл удержания, отсутствие теста, потом имена. Если бриф меняют посреди архитектуры, режу niceties и оставляю данные и границы. В Playground не покажешь таргеты, подпись и нормальный граф модулей. Индийский machine-coding это 90 минут рабочего приложения, не чистка чужого VC. Timed contest OA готовит скорость задач, Playground-рефакторинг готовит чтение кода.



```text
60 min screen: code review + 3 theory (easy / mid / senior).
90–120 min: refactor on a shared editor → feature architecture on a board.
30–60 min: team / hiring manager.
```


**Потом обычно спрашивают**

- Что говоришь первым на рефакторинге: тесты, имена или retain cycle?
- Бриф поменяли посреди архитектуры: что выкидываешь?
- Playground vs нормальный проект Xcode: чего не покажешь?
- Чем отличается индийский machine-coding на 90 минут?
- Timed contest OA как первый фильтр: что тренируешь такого, чего нет в рефакторинге Playground?

</details>
