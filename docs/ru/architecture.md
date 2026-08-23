# Архитектура

25 карточек · 13 часто спрашивают · [architecture.md](../../topics/architecture.md)

### Junior

<h2 id="mvc">MVC</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

MVC режет экран на Model, View и Controller. Модель — данные и правила без UIKit. View рисует. Контроллер грузит модель и обновляет View — на iOS это обычно UIViewController. Шаблоны Apple стартуют отсюда, так что назови паттерн, потом назови провал: контроллер впитывает сеть, маппинг и навигацию, пока не станет на тысячи строк. Для маленького экрана MVC всё ещё беру. Вытаскиваю работу в тот момент, когда контроллер начинает знать про URL или как форматировать валюту. Миграция MVC → MVVM поэтапная: вынеси ViewModel на один экран, держи UIKit снаружи, забинди стейт, навигацию оставь, пока контроллер не похудеет — не переписывай приложение одним PR.



```swift
struct Note {
    var text: String
}

final class NoteViewController {
    private let note: Note
    private(set) var labelText = ""

    init(note: Note) {
        self.note = note
        labelText = note.text
    }
}
```


**Потом обычно спрашивают**

- Что люди имеют в виду под Massive View Controller?
- Где в MVC жить сетевому вызову?
- MVC vs MVVM — когда переключаться?
- Есть ли у SwiftUI контроллер?
- Как мигрировать один Massive View Controller на MVVM без рерайта?

</details>

<h2 id="delegates">Делегаты</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Делегат — объект, которого просишь принимать решения или события, почти всегда через протокол. UITableView не знает твой экран — зовёт методы вроде tableView(_:didSelectRowAt:) у того, кого ты назначил delegate. Связь один к одному, не широковещание. Классовый делегат держи weak: обычная форма UIKit — «контроллер владеет вьюхой, вьюха указывает назад на контроллер». Оба strong — утечка. Протокол пометь AnyObject, чтобы weak был легален.



```swift
protocol SearchDelegate: AnyObject {
    func searchDidFinish(_ results: [String])
}

final class SearchService {
    weak var delegate: SearchDelegate?

    func run(_ query: String) {
        delegate?.searchDidFinish(["\(query) hit"])
    }
}
```


**Потом обычно спрашивают**

- Почему делегат обычно weak?
- Делегат vs NotificationCenter vs замыкание-колбэк?
- Data source vs delegate — что куда?
- Что ломается, если протокол не AnyObject?
- Можно ли делегирование без протокола — и зачем он всё равно нужен?

</details>

<h2 id="global-variables">Глобальные переменные</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

var на уровне файла — общий мутабельный стейт без владельца. Тесты не сбросят его надёжно, два экрана дерутся за него, фейк не подсунешь. let-глобалы для констант (let maxRetry = 3) нормальны. Нужен один живой сервис? Заинжекти или узкий shared, который в тестах всё ещё можно подменить. Типичный промах: var currentUser в скоупе файла, который читает каждый VC.



```swift
enum Config {
    static let maxRetry = 3
}

struct Session {
    var user: User?
}

final class ProfileViewModel {
    var session: Session
    init(session: Session) { self.session = session }
}
```


**Потом обычно спрашивают**

- Глобальный let vs глобальный var — в чём реальная проблема?
- Чем это отличается от синглтона?
- Как тестить код, который уже читает глобал?

</details>

<h2 id="oop-pillars">Столпы OOP</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Четыре слова, которые всё ещё хотят, с iOS-примером на каждое. **Инкапсуляция:** спрячь хранилище, отдай маленький API (private(set)). **Абстракция:** говори с протоколом, не с URLSession во View. **Наследование:** сабклассы UIViewController — дёшево, легко перебрать. **Полиморфизм:** один draw() на разных сабклассах UIView или any FeedLoading. Swift опирается на протоколы сильнее, чем на глубокие деревья классов. Типичный промах: перечислить список без примера или назвать «структуру с методами» наследованием.



```swift
protocol Drawable { func draw() }
struct Circle: Drawable { func draw() { /* */ } }
struct Rect: Drawable { func draw() { /* */ } }
func render(_ items: [any Drawable]) { items.forEach { $0.draw() } }
```


**Потом обычно спрашивают**

- Какому столпу в первую очередь служит протокол в Swift?
- Когда наследование — неправильный инструмент в UIKit?
- Чем инкапсуляция отличается от private?
- Может ли класс в Swift наследоваться от двух суперклассов?

</details>

### Mid

<h2 id="dependency-injection">Dependency injection</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

DI значит: тип не конструирует своих коллабораторов — их передают. Три вида, которые называют на собесе: **initializer** (init(api:) — предпочтительный), **property** (ставишь после init, часто со сторибордами), **method** (коллаборатор в один вызов). Тесты дают стаб, превью — фикстуру, прод — живой клиент. Вызов Foo.shared внутри метода — наоборот: скрытая зависимость. Контейнер в маленькое приложение не тащу. Composition root, который собирает граф, плюс протокол на каждой I/O-границе — достаточно.



```swift
protocol Clock {
    func now() -> Date
}

struct SystemClock: Clock {
    func now() -> Date { Date() }
}

final class Session {
    private let clock: Clock
    init(clock: Clock) { self.clock = clock }

    var isExpired: Bool { clock.now() > Date.distantPast }
}
```


**Потом обычно спрашивают**

- Initializer injection vs property injection vs service locator?
- Как заинжектить в UIViewController из сториборда?
- Когда DI-контейнер на iOS стоит того?
- Как это меняет превью SwiftUI?
- Чем constructor injection отличается от зависимости от протокола (DIP)?

</details>

<h2 id="feature-flags">Feature flags</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Feature flag — **рантайм-переключатель** пути в коде: remote config, локальный оверрайд или compile-time #if. Им шипают тёмным, раскатывают на 10%, глушат плохой релиз или гоняют A/B. Клиент должен считать флаг **недоверенным и поздним** — дефолт на безопасный путь, кэш последнего известного значения офлайн, не блокировать запуск на фетче конфига. Хотят ops-историю: кто владеет флагом, как удаляешь после эксперимента, как kill switch доезжает до девайсов (пуш / background fetch / следующий запуск). Типичный промах: обернуть каждую строку в if flag, пока модуль нечитаем, или флаг, который выключается только новым билдом App Store.



```swift
protocol Flagging {
    func isOn(_ key: FlagKey) -> Bool
}

func makeFeed(flags: Flagging) -> any FeedServing {
    flags.isOn(.newRanking) ? RankingFeed() : LegacyFeed()
}
```


**Потом обычно спрашивают**

- Kill switch vs эксперимент vs постепенный раскат — один флаг?
- Как быстро удалённый флаг доедет до suspended-приложения?
- Куда класть дефолт, когда конфиг-сервер лежит?

</details>

<h2 id="mvvm">MVVM</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

MVVM ставит ViewModel между View и остальным приложением. ViewModel владеет презентационным стейтом и говорит с сервисами; View рисует этот стейт и прокидывает тапы. **В VM:** флаги загрузки, смапленные строки для экрана, валидация, вызовы API / репозитория. **Не в VM:** UIView, UIColor (пока не абстрагируешь), идентификаторы сториборда, Auto Layout. Отдаю что-то биндабельное — @Published, @Observable, паблишер — и держу типы UIKit и SwiftUI снаружи, чтобы юнит-тестить с фейковым API. Навигация — обычная драка: если ViewModel презентует контроллер, разрез уже сломан. Болтливые биндинги, которые пересобирают всё на каждый кейстрок — второй запах. ViewModel — стейт-машина; слой View пусть презентует.



```swift
final class LoginViewModel {
    var username = ""

    var canSubmit: Bool { username.count >= 3 }

    func submit() -> Result<Void, LoginError> {
        canSubmit ? .success(()) : .failure(.tooShort)
    }
}

enum LoginError: Error { case tooShort }
```


**Потом обычно спрашивают**

- Как юнит-тестить ViewModel?
- Куда девать навигацию и алерты?
- MVVM vs MVC на одном экране UIViewController?
- Что ломается у двусторонних биндингов?
- Что обычно живёт в ViewModel, а что во View?
- Какой фейл-мод у MVVM — Massive ViewModel?

</details>

<h2 id="protocol-oriented-programming">Protocol-oriented programming</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Protocol-oriented programming значит: проектируешь вокруг способностей, не деревьев классов. Протокол называет, что объект умеет; extension может дать дефолт; структуры и енумы могут конформить — наследование этого не даёт. Протоколы выношу на границах — сеть, диск, часы — чтобы тесты подсунули дабл. Ловушка — протокол на каждый конкретный тип или протокол, которому нужны stored-свойства, которые потом подделываешь шумом associated type. Начни с конкретного типа. Поднимай протокол, когда есть вторая реализация или тестовый фейк.



```swift
protocol Fetching {
    func fetch() async throws -> Data
}

extension Fetching {
    func fetchString() async throws -> String {
        String(decoding: try await fetch(), as: UTF8.self)
    }
}

struct LiveClient: Fetching {
    func fetch() async throws -> Data { Data() }
}
```


**Потом обычно спрашивают**

- POP vs наследование классов — когда базовый класс всё ещё лучше?
- Какую задачу associated types создают для any / some?
- Extension протокола vs свободная функция?
- Когда протокол на один конформ — слишком рано?

</details>

<h2 id="solid">SOLID</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Пять проверок дизайна, не религия. **S**ingle responsibility: VC только биндит UI, сервис только говорит по HTTP. **O**pen/closed: добавь новый конформ PaymentMethod вместо правки свитча. **L**iskov: сабкласс должен чтить контракт родителя — никакого fatalError в оверрайде, который вызывающий ждёт. **I**nterface segregation: маленький Logging лучше 20-методного GodService. **D**ependency inversion: завись от протокола, инжекти живой тип. Типичный промах: развернуть каждую букву в лекцию и ни разу не назвать тип из последнего приложения.



```swift
protocol Paying { func pay() async throws }
struct Checkout {
    let payment: Paying
    func run() async throws { try await payment.pay() }
}
```


**Потом обычно спрашивают**

- Слабая vs сильная связность — какая буква SOLID?
- Какое правило SOLID ломает view controller на 2000 строк?
- Open/closed vs «мы никогда не меняем существующие файлы»?
- Как DIP выглядит как constructor injection?
- DI vs DIP — по одному предложению?

</details>

<h2 id="repository">Паттерн Repository</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Репозиторий — тип, который **прячет, откуда данные**. Остальное приложение просит func user(id:) async throws -> User и не знает, ответ пришёл из URLSession, Core Data, кэша в памяти или тестовой фикстуры. Репозиторий мапит DTO и объекты стора в **доменные** модели и переводит инфраструктурные ошибки в доменные. Отличие от «сервиса»: сервис часто *делает* use case; репозиторий *грузит и сохраняет*. Типичный промах: UserRepository, который возвращает UserDTO и протекает URLError в ViewModel, или один бог-репозиторий на все сущности.



```swift
protocol UserRepository {
    func user(id: UUID) async throws -> User
}

struct RemoteUserRepository: UserRepository {
    let client: HTTPClient
    func user(id: UUID) async throws -> User {
        let dto: UserDTO = try await client.get("/users/\(id)")
        return User(id: dto.id, name: dto.fullName)
    }
}
```


**Потом обычно спрашивают**

- Репозиторий vs use case vs ViewModel — кто чем владеет?
- Как сменить Core Data на SwiftData, не переписывая экраны?
- Почему URLError переводить на этой границе?

</details>

<h2 id="design-patterns">Паттерны в iOS</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Не читай Gang of Four наизусть. Группируй то, что реально шипил. **Порождающие:** фабрики и DI вместо Foo.shared везде; builder для длинного URLRequest. **Структурные:** adapter (обернуть C API), decorator (URLProtocol), facade (тип Session перед Keychain + сетью). **Поведенческие:** делегат (table view), observer (NotificationCenter, Combine), strategy (протокол Pricing), Coordinator / router для навигации. UIKit уже MVC плюс делегаты. SwiftUI толкает к MVVM и Observation. Назови трейдофф на каждый: делегаты один к одному и текут, если strong; синглтоны простые и прячут зависимости; Coordinator добавляет типы, но держит контроллеры маленькими. Типичная ошибка: двадцать паттернов без iOS-примера.



```swift
protocol FeedLoading {
    func load() async throws -> [Post]
}

struct LiveFeed: FeedLoading {
    func load() async throws -> [Post] { try await API.feed() }
}

struct PreviewFeed: FeedLoading {
    func load() async throws -> [Post] { [.placeholder] }
}

final class FeedViewController: UIViewController {
    init(loader: FeedLoading) { /* DI — strategy */ }
}
```


**Потом обычно спрашивают**

- Делегат vs замыкание vs NotificationCenter на одно событие?
- Какие паттерны UIKit уже реализует за тебя?
- Когда Coordinator стоит лишних типов?
- Где на iOS всплывает Memento (NSCoder, undo, state restoration)?
- Какой *плохой* паттерн в iOS-приложении — Massive VC, singleton-бог, strong-делегат?

</details>

<h2 id="singletons">Синглтоны — когда помогают</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Синглтон — один инстанс на процесс, обычно static let shared и private init. Помогает, когда два инстанса были бы неверны или дороги — обёртка над keychain, FileManager.default, сокет, который нельзя открыть дважды. На собесе это **антипаттерн**, когда прячет зависимости: каждый тип, который тянется к Analytics.shared, нетестируемый и зависит от порядка. Цена — глобальный мутабельный стейт: тесты делят объедки, тип, который зовёт Analytics.shared, не может взять no-op в превью. **static let потокобезопасен на создании** (Swift лениво инициализирует его один раз). ObjC-эквивалент, который всё ещё спрашивают — dispatch_once вокруг alloc; не кати @synchronized и голый if (shared == nil). Мутация свойств на shared не потокобезопасна — защити actor, serial-очередью или локом. Синглтон пусть существует, потом передай его. Дефолт параметра в .shared ок на краю, не внутри доменной логики.



```swift
protocol Analytics {
    func track(_ event: String)
}

final class AnalyticsClient: Analytics {
    static let shared = AnalyticsClient()
    private init() {}
    func track(_ event: String) { /* send */ }
}

final class Checkout {
    private let analytics: Analytics
    init(analytics: Analytics = AnalyticsClient.shared) {
        self.analytics = analytics
    }
}
```


**Потом обычно спрашивают**

- Как тестить код, который сегодня ходит в синглтон?
- Синглтон vs shared-инстанс, который всё равно инжектишь?
- Какие проблемы потокобезопасности всплывают на shared?
- Когда синглтон — неправильный инструмент для «мне нужен один»?
- Как делали потокобезопасный синглтон в Objective-C?
- Почему на собесе Singleton называют антипаттерном — и когда его всё равно оставляешь?

</details>

<h2 id="kvc">KVC</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Key-Value Coding — доступ рантайма ObjC по **строковому ключу**: value(forKey:), setValue(_:forKey:). KVO на этом построен. Всё ещё встречаешь в Core Data, NSSortDescriptor, остатках Cocoa bindings и setValue из словаря. Обходит access control Swift и может попасть в неверный ключ в рантайме (valueForUndefinedKey). В новом Swift лучше key path (\Foo.bar) и типизированные свойства. Типичный промах: ставить private-свойство через KVC «потому что работает».



```swift
let label = UILabel()
label.setValue("Hi", forKey: "text")
let text = label.value(forKey: "text") as? String
```


**Потом обычно спрашивают**

- KVC vs KVO vs key path — по одному предложению?
- Почему KVC может обойти твой кастомный сеттер?
- Где Core Data всё ещё этого требует?

</details>

<h2 id="mvp">MVP</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

MVP ставит **Presenter** между View и моделью. View — пассивный протокол (show(items:), showError), часто сам view controller. Presenter грузит данные и говорит View, что показать; типы UIKit не держит, если протокол честный. Отличие от MVVM: presenter **толкает** команды во View; ViewModel **отдаёт стейт**, который View тянет / биндит. MVP проще вести в UIKit без Combine. MVVM лучше садится на SwiftUI и @Published. Типичный промах: presenter, который всё ещё зовёт view.tableView.reloadData().



```swift
protocol LoginViewing: AnyObject {
    func showError(_ text: String)
}

final class LoginPresenter {
    weak var view: LoginViewing?
    func submit(name: String) {
        if name.count < 3 { view?.showError("Too short") }
    }
}
```


**Потом обычно спрашивают**

- MVP vs MVVM — кто владеет стейтом экрана?
- Почему протокол View — AnyObject и weak?
- Когда Clean Architecture больше, чем любой из этих двух?

</details>

<h2 id="atomic-nonatomic">atomic vs nonatomic vs copy</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Это **атрибуты свойств Objective-C**, не ключевые слова Swift. atomic (дефолт ObjC) синтезирует лок вокруг геттера/сеттера, чтобы получить целое значение, не порванный указатель — это **не** потокобезопасная мутация графа объектов. nonatomic лок пропускает; UIKit ставил его везде ради скорости. copy на set шлёт copy, чтобы оставить иммутабельный снимок (NSString, NSArray), а не мутабельный сабкласс, который меняется под тобой. @property (copy) NSMutableArray *array — ловушка: copy даёт **иммутабельный** NSArray, следующий addObject падает. Бери strong плюс защитный copy внутри сеттера или мутабельный ivar. В Swift пишешь var title: String (value semantics) или явный NSLock. Типичная ошибка: «пометил atomic — массив потокобезопасен».



```objc
@property (nonatomic, copy) NSString *title;
@property (atomic, strong) NSNumber *count;
```


**Потом обычно спрашивают**

- Почему atomic не делает коллекцию безопасной для мутации с двух очередей?
- Когда copy всё ещё нужен у свойства Swift с @objc?
- Чем это мышление заменили в Swift (let, actor)?
- copy vs retain / strong — когда нужен снимок?

</details>

<h2 id="functional-programming">Функциональное программирование в Swift</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift — не функциональный язык, но берёт полезные куски. Функции — значения, поэтому map, compactMap, filter и reduce заменяют кучу мутабельных циклов. Предпочитаю преобразовывать значения, а не мутировать общие объекты, и люблю маленькие функции, которые берут данные и возвращают данные. Trailing closures это удобно делают. Чистоту и свои операторы в апп-коде не гоняю. Скрытая мутация внутри map хуже честного for.



```swift
let prices = [9.99, 4.50, 12.00]
let taxedTotal = prices
    .filter { $0 >= 5 }
    .map { $0 * 1.2 }
    .reduce(0, +)
```


**Потом обычно спрашивают**

- map vs compactMap vs flatMap?
- Когда for понятнее пайплайна?
- Что значит, что Array — value type с copy-on-write?
- Как не дать пайплайну Combine / async спрятать сайд-эффекты?
- Functional vs OOP — когда всё ещё хочешь иерархию классов?

</details>

<h2 id="kvo">KVO</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

KVO — Key-Value Observing из рантайма Objective-C. Смотришь key path и получаешь колбэк, когда свойство меняется. В Swift тип должен наследовать NSObject, свойство — @objc dynamic, и надо держать токен NSKeyValueObservation, иначе наблюдение умрёт. Дефолтная реализация Apple **создаёт сабкласс в рантайме**, оверрайдит сеттер и **свизлит isa**, чтобы инстанс выглядел как этот сабкласс — поэтому ручной setValue или прямая запись в ivar могут пропустить KVO, пока не обернёшь willChangeValue / didChangeValue. Новое KVO в Swift не добавляю. Паблишер, Observation или делегат проще читать. Узнавать всё равно надо: часть системных типов публикует только так — AVPlayer, NSProgress, куски UIKit.



```swift
final class Transport: NSObject {
    @objc dynamic var rate: Double = 0
}

let transport = Transport()
let token = transport.observe(\.rate, options: [.new]) { _, change in
    print(change.newValue ?? 0)
}
transport.rate = 1
```


**Потом обычно спрашивают**

- Зачем @objc dynamic и что без него?
- KVO vs Combine vs фреймворк Observation?
- Что делать с токеном наблюдения?
- Делегат vs KVO — когда какой наблюдатель правильный?
- Увидит ли KVO свойство Swift-структуры?
- Как Apple реализует KVO под капотом (свизл isa)?
- Как стрельнуть KVO для изменения, которое не прошло через сеттер?

</details>

### Senior

<h2 id="clean-architecture">Clean Architecture</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Clean Architecture (и варианты VIPER / «use case») кладёт **entity и use case** в середину, потом адаптеры (presenter, gateway), потом фреймворки (UIKit, URLSession, Core Data) снаружи. Зависимости смотрят **внутрь**: use case не импортит SwiftUI. Отличие от MVVM: MVVM — паттерн экрана; Clean — правило зависимостей на всё приложение. Тянешься, когда одни и те же бизнес-правила должны пережить рерайт UI или второго клиента. Цена — типы: LoginUseCase, LoginRepository, три протокола на одну кнопку. Типичный промах: папки Domain / Data / Presentation, которые всё ещё импортят UIKit в «домене».



```swift
protocol AuthGateway {
    func login(name: String, password: String) async throws -> User
}

struct LoginUseCase {
    let auth: AuthGateway
    func run(name: String, password: String) async throws -> User {
        try await auth.login(name: name, password: password)
    }
}
```


**Потом обычно спрашивают**

- Clean vs MVVM — можно ли оба?
- Чем use case отличается от метода ViewModel?
- Когда это overkill для приложения из трёх экранов?
- Почему URLError не должен дойти до ViewModel как есть?

</details>

<h2 id="mvvm-c">MVVM-C</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

MVVM-C — это MVVM плюс **Coordinator** (или router), который владеет навигацией. ViewModel говорит «логин прошёл»; Coordinator пушит следующий экран. Так UIKit / NavigationPath остаются вне ViewModel, и флоу можно тестить без окна. Цена: ещё один тип на модуль и спор, кто держит UINavigationController. Типичный промах: Coordinator, который всё ещё собирает View *и* зовёт API.



```swift
protocol Coordinating: AnyObject { func loginDidSucceed() }

final class LoginViewModel {
    weak var coordinator: Coordinating?
    func submit() { coordinator?.loginDidSucceed() }
}
```


**Потом обычно спрашивают**

- Coordinator vs ViewModel, который владеет NavigationPath?
- Как тестить Coordinator?
- Когда хватает обычного MVVM?
- Можно ли взять Coordinator, не называя паттерн «MVVM-C»?

</details>

<h2 id="viper">VIPER</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

VIPER режет экран на **View, Interactor, Presenter, Entity, Router**. View тупой. Presenter форматирует и реагирует на тапы. Interactor гоняет use case и говорит с сервисами. Router владеет навигацией. Entity — модели. Отличие от MVVM: больше типов, навигация яснее, тяжелее для одной формы. Бери, когда модуль большой и куски держат несколько людей. Типичный промах: presenter, который всё ещё импортит UIKit, или пять пустых файлов ради тоггла в настройках.



```swift
protocol LoginViewing: AnyObject { func show(error: String) }
protocol LoginRouting: AnyObject { func finish() }

final class LoginPresenter {
    weak var view: LoginViewing?
    var router: LoginRouting?
    func submit() { /* interactor, then view or router */ }
}
```


**Потом обычно спрашивают**

- VIPER vs Clean vs MVVM — какую задачу решает каждый лишний тип?
- Где живёт сетевой клиент?
- Когда это overkill?
- Какой фейл-мод VIPER у команды из одного человека?

</details>

<h2 id="kmp">Kotlin Multiplatform с iOS</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

KMP шарит **Kotlin**-бизнес-логику (сетевые модели, валидацию, стор), скомпилированную во фреймворк, который линкует iOS-приложение. UI остаётся SwiftUI / UIKit. Собес про **границу**: expect / actual для платформенных API, какие типы пересекают (примитивы и классы, которые экспортирует Kotlin, не структуры Swift), и кто владеет concurrency (корутины Kotlin vs async в Swift — обычно оборачиваешь). View не шарь. Типичный промах: считать KMP «написать приложение один раз» или передать Swift-класс в Kotlin и удивляться, почему компилятор отказывается.



```text
shared/ (Kotlin) → XCFramework
iosApp/ imports Shared, maps SharedUser → Swift User in one adapter
```


**Потом обычно спрашивают**

- Что не пересекает границу Kotlin/Swift чисто?
- Кто отменяет in-flight вызов Ktor, когда View SwiftUI пропадает?
- Когда общий модуль — неправильный разрез (UI, Keychain, WidgetKit)?

</details>

<h2 id="tca">TCA</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

The Composable Architecture (Point-Free) — **однонаправленный** цикл: State, Action, Reducer, Store и Effect для I/O. Каждое изменение — action; эффекты — значения, которые можно зафейлить в тестах. Масштабирует дерево фич, time-travel и исчерпывающие тесты дешевеют. Цена: бойлерплейт и кривая обучения; приложению из трёх экранов редко нужно. Типичный промах: назвать это «просто Redux» и пропустить эффекты.



```swift
struct Counter: Equatable { var count = 0 }
enum CounterAction { case increment }
// reducer: (inout State, Action) -> Effect<Action>
```


**Потом обычно спрашивают**

- TCA vs MVVM — какую задачу решает reducer?
- Где живут сетевые вызовы (Effect)?
- Когда это overkill рядом с @Observable?

</details>

<h2 id="modular-architecture">Модульная архитектура</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Модульность — **физические** границы: локальные Swift-пакеты (или таргеты), чтобы Feature A не импортила внутренности Feature B. Общие контракты живут в тонком модуле; реализации остаются internal. Таргет приложения — composition root. Так несколько команд шипают без одного User.swift, который обрастает пятьюдесятью опционалами. SPM отказывается от циклических зависимостей — фикс это третий модуль протоколов, не «просто импортните друг друга». Типичный промах: пакет Core, который импортит всё, или сделать каждый тип public «для тестов».



```swift
// AppContracts
public protocol CurrentUserProviding {
    var userId: String { get }
}

// CheckoutFeature depends on AppContracts, never on ProfileFeature
public struct CheckoutFactory {
    public static func make(user: CurrentUserProviding) -> some View {
        CheckoutView(userId: user.userId)
    }
}
```


**Потом обычно спрашивают**

- Как разорвать цикл между Checkout и Profile?
- Что класть в AppContracts vs пакет CoreUI?
- Strangler Fig — как мигрировать UIKit → SwiftUI по одному экрану?
- 200+ модулей SPM — что первым взрывает время компиляции?

</details>

<h2 id="optimistic-updates">Оптимистичные обновления</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Оптимистичный UI применяет изменение **до** подтверждения сервера и откатывает, если запрос упал. Пользователь сразу видит лайк, отправку или переименование. Держишь снимок прошлого стейта (или обратную операцию) и стабильный id, чтобы поздний 409 / 500 откатил, не затерев более новый локальный эдит. Политика конфликтов — тема собеса: last-write-wins, version tokens или «спросить пользователя». Типичный промах: мутировать единственную копию модели и нечем восстановить — или показать хром успеха, ещё не поставив запрос в очередь.



```swift
func toggleLike(_ post: Post) async {
    let before = post.isLiked
    store.setLiked(post.id, !before)          // immediate
    do {
        try await api.setLiked(post.id, !before)
    } catch {
        store.setLiked(post.id, before)       // rollback
    }
}
```


**Потом обычно спрашивают**

- Как свести два оптимистичных лайка, если тапнули дважды?
- Что персистить, если приложение убили mid-flight?
- Когда пессимистичный путь (ждать 200) лучше как дефолт?

</details>

<h2 id="phantom-types">Phantom types</h2>

<code>Senior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Phantom type — дженерик-параметр, который ты никогда не хранишь. Он нужен, чтобы компилятор отличал два иначе одинаковых значения. ID<User> и ID<Order> оба могут обернуть String, но одно туда, где ждут другое, не передашь. Так же кодируешь флоу: Request<Unsigned> против Request<Signed>, и send принимает только подписанный. Лишнего рантайм-стейта нет. Беру, когда путаница — настоящий баг: ID, единицы, валидация. Не как украшение на каждую модель.



```swift
struct ID<Entity>: Hashable {
    let raw: String
}

enum UserTag {}
enum OrderTag {}

func loadUser(_ id: ID<UserTag>) {}

let user = ID<UserTag>(raw: "u1")
loadUser(user)
// loadUser(ID<OrderTag>(raw: "o1")) // does not compile
```


**Потом обычно спрашивают**

- Phantom type vs структура-обёртка с отдельным именем?
- Как смоделировать Draft vs Paid, чтобы submit не принял черновик?
- Есть ли цена в рантайме и нужны ли инстансы Entity?
- Когда это overkill рядом с UUID плюс комментарий?

</details>
