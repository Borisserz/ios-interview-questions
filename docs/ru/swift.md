# Swift

95 карточек · 51 часто спрашивают · [swift.md](../../topics/swift.md)

### Junior

<h2 id="identity-vs-equality">== vs ===</h2>

<code>Junior</code> · <code>Часто</code>

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

<h2 id="access-control">Access control</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Access control в Swift про то, **кто может назвать символ**. От самого узкого к широкому: `private` (это объявление), `fileprivate` (этот файл), `internal` (этот module, дефолт), `package` (этот Swift package), `public` (импортёры могут пользоваться), `open` (импортёры могут subclass / override, только class). **`public` виден через module, но снаружи не subclass'ится**; `open` можно. Apple так режет специально: часть хуков `NSManagedObject` сделаны `public`, чтобы звать, но не override. Авторы фреймворков ставят `open`, только когда subclassing это контракт. App target почти никогда не нужен `open`. Типичный промах: тип `public`, а `init` оставить `internal`, и клиенты не могут сконструировать.



```swift
public struct Token {
    public let raw: String
    public init(raw: String) { self.raw = raw }
}

open class Plugin {           // only if clients must subclass
    open func start() {}
}
```


**Потом обычно спрашивают**

- `public` vs `open`: когда `open` ошибка?
- `private` vs `fileprivate` после Swift 4 (extension в том же файле)?
- Почему `public` struct нужен явный `public init`?
- Как отдать геттер, а сеттер оставить внутри типа?
- Зачем автору фреймворка пометить метод `public`, а не `open`?

</details>

<h2 id="any-vs-anyobject">Any vs AnyObject</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`Any` это любой тип: struct, enum, функции, class. `AnyObject` это **только инстансы class** (swift-имя для `id`). `AnyObject` нужен для `weak` / ObjC interop / «это должна быть ссылка». `Any` для гетерогенной коробки (`[Any]`). Оба стирают информацию, чтобы работать, downcast'ишь. Типичный промах: `[AnyObject]` для списка struct, или `Any` там, где хватило бы protocol.



```swift
let mixed: [Any] = [1, "a", { 0 }]
let objects: [AnyObject] = [UIView(), NSString(string: "x")]
```


**Потом обычно спрашивают**

- `any Protocol` vs `Any` vs `AnyObject`?
- Почему `weak var x: Any` нелегально?
- Когда generic лучше, чем `Any`?

</details>

<h2 id="array-vs-set">Array и set — в чём разница</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Array** хранит порядок и допускает дубликаты. **Set** хранит уникальные `Hashable` элементы и отвечает на `contains` за ожидаемое константное время. Set — когда вопрос про membership или уникальность, а не «третий элемент». Часто следом: «как уникалить array и сохранить порядок» — один `Set` этого не сделает. Типичные ошибки: array и `contains` в цикле (квадратично), или рассчитывать на стабильный порядок итерации `Set`. Нужны и быстрый lookup, и стабильный порядок на экране — держи array и set уже виденных ключей.



```swift
let tags = ["ios", "swift", "ios"]
let unique = Set(tags)
unique.contains("swift")

func uniqued(_ values: [String]) -> [String] {
    var seen = Set<String>()
    return values.filter { seen.insert($0).inserted }
}
```


**Потом обычно спрашивают**

- Почему `Set` требует `Hashable`, а `Array` нет?
- Как проверить, что два set равны, если порядок разный?
- Когда array всё равно лучше, даже если значения должны быть уникальными?
- Почему `NSSet` / `Set` — hash lookup, а `NSArray` — сканирование?

</details>

<h2 id="classes-vs-structs">Class и struct — в чём разница</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Struct** — value type: присваивание копирует значение. **Class** — reference type: копируется указатель на тот же instance. По умолчанию struct, пока не нужны identity (`===`), inheritance, `deinit` или Objective-C interop. Хотят именно этот default и живую причину переключиться, а не «class более объектно-ориентированный».

Классическая ловушка: два `Person` делят один `Address` class. Поменял улицу у Brian — Ray тоже переехал, тот же instance. Фикс: новый `Address` или сделать `Address` struct. Другая ловушка: `mutating` метод на struct законный, но на `let` instance его не вызвать. У `let` class свойства всё равно можно менять. Частые ошибки: «struct всегда на стеке» (нет), мутировать struct, который передали в функцию, и ждать, что caller это увидит, или брать class только чтобы два экрана делили кучу mutable state.



```swift
struct Size { var width: Int }
class Box { var size: Size }

var a = Size(width: 10)
var b = a
b.width = 20          // a.width is still 10

let box = Box(size: Size(width: 10))
let also = box
also.size.width = 20  // box.size.width is 20
```


**Потом обычно спрашивают**

- Когда class лучше, даже если inheritance не нужен?
- Что значит `mutating` у метода struct?
- Как copy-on-write меняет историю «struct — это копия» для `Array`?
- Две модели делят `Address` class — почему правка одной двигает другую?

</details>

<h2 id="closures">Closures</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Closure** — безымянная функция, которая может захватить значения из scope, где её создали. На собесе: trailing-closure syntax, `$0`, `{ [weak self] in }`. Closure — **reference type**, даже если лежит в struct: две копии struct могут делить один heap-объект closure. Поэтому retain cycle: closure сильно держит `self`, `self` хранит closure. Non-escaping (дефолт для аргументов функции) бегут до return callee; escaping могут позже. Часто схлопывается `{ (a: String, b: String) -> Bool in return a < b }` до `{ $0 < $1 }` или даже `sort(by: <)`. Типичные промахи: случайно захватить огромный граф значений, и `unowned self` у view controller, который может уйти первым.



```swift
let add: (Int, Int) -> Int = { $0 + $1 }
let names = ["zoe", "ada"].sorted { $0 < $1 }

func makeCounter() -> () -> Int {
    var n = 0
    return { n += 1; return n }
}
```


**Потом обычно спрашивают**

- Что на самом деле делает capture list?
- Почему closure может держать объект живым?
- Когда внутри closure нужен `self.`?
- Closure — value type или reference type?
- Что такое trailing-closure syntax, и когда лейбл всё равно пишешь?

</details>

<h2 id="dictionary-vs-array">Dictionary и array — в чём разница</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Array** — упорядоченный список, индекс `Int`. **Dictionary** — hash map: значение ищешь по `Hashable` ключу. На собесе смотрят, берёшь ли коллекцию под паттерн доступа, а не по привычке. Array — когда важны порядок и дубликаты, или когда идёшь по всему списку. Dictionary — когда снова и снова спрашиваешь «дай объект с этим id». Типичный промах: в hot path гонять `first(where:)` по массиву моделей, или считать итерацию dictionary позиционным индексом. С Swift 4 dictionary при итерации держит порядок вставки, но subscript `0` всё равно не работает.



```swift
struct User { let id: String; let name: String }

let users = [User(id: "1", name: "Ada"), User(id: "2", name: "Grace")]
let byID = Dictionary(uniqueKeysWithValues: users.map { ($0.id, $0) })
let ada = byID["1"]
```


**Потом обычно спрашивают**

- Что будет, если при сборке dictionary два ключа совпадут?
- Когда имеет смысл держать и array, и dictionary одних и тех же данных?
- Почему ключи dictionary должны быть `Hashable`?

</details>

<h2 id="enums">Enums</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift enum это value type: одно из закрытого набора case. Raw value (`String`, `Int`) добавляешь, когда персистишь или декодируешь. **Associated values** когда у case разные payload (`Result`, сетевые ошибки). У enum бывают методы, computed properties, и `switch` обязан быть exhaustive. Вот выигрыш на собесе против кучи булей. Типичная ошибка: `isLoading` + `error` + `value` тремя Optional вместо `enum State { idle, loading, failed(Error), ready(Value) }`.



```swift
enum LoadState<Value> {
    case idle
    case loading
    case failed(Error)
    case ready(Value)
}
```


**Потом обычно спрашивают**

- Raw value vs associated value: может ли case иметь оба?
- Почему exhaustive `switch` безопаснее, чем `if` по булям?
- Когда всё равно хочешь struct, а не enum?
- Что такое `indirect` enum, и зачем он дереву?

</details>

<h2 id="float-double-cgfloat">Float, Double и CGFloat — в чём разница</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`Double`** — 64-битный IEEE float, дефолт Swift для литералов вроде `3.14`. **`Float`** — 32 бита: половина точности, меньше по размеру, почти никогда не нужен, пока API или формат файла не заставят. **`CGFloat`** — скаляр Core Graphics: на современных 64-битных Apple платформах той же ширины, что `Double`, но это другой тип. Спрашивают, потому что UIKit и Core Animation говорят на `CGFloat`, и люди лепят `as`, пока не скомпилируется. Не мешай их без явного conversion. Не клади модельные данные в `CGFloat` только потому, что view так принял.



```swift
import CoreGraphics

let temperature: Double = 36.6
let hairline: CGFloat = 1 / 3
let width = CGFloat(temperature) + hairline
let compact = Float(temperature)
```


**Потом обычно спрашивают**

- Почему `let x = 1.0` выводит `Double`, а не `CGFloat`?
- Что ломается, если сравнивать `Float` и `Double`, которые «выглядят» одинаково?
- Когда в iOS-приложении реально выбрать `Float`?

</details>

<h2 id="hashable-equatable">Hashable, Equatable, Comparable</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`Equatable`** это `==`. **`Hashable`** это `Equatable` плюс стабильный `hash(into:)`, чтобы тип мог быть ключом `Set` / `Dictionary`. **`Comparable`** это `<` (и остальное), чтобы сортировать. Синтезируй, когда все stored properties уже конформят. Не пиши свой hash, который игнорирует поле из `==`. Типичный промах: мутировать свойство, которое участвует в `==`, после того как значение уже в set.



```swift
struct UserID: Hashable, Comparable {
    let raw: String
    static func < (l: Self, r: Self) -> Bool { l.raw < r.raw }
}
```


**Потом обычно спрашивают**

- Почему `==` и `hash` должны соглашаться?
- Когда `hash(into:)` пишешь руками?
- `Comparable` vs closure в `sort`?
- Два значения, один `hashValue`, разный `==`: оба могут жить в `Set`?
- `Identifiable` vs `Hashable`: что на самом деле нужно `ForEach`?

</details>

<h2 id="identifiable">Identifiable</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`Identifiable` это стабильный **`id`**, чтобы SwiftUI и diffable-списки отличали строки. `ForEach(items)` хочет `Identifiable` (или явный `id: \.key`). `id` не должен меняться, когда поменялся текст на экране: UUID или серверный primary key, не `name`. `Hashable` для set и ключей dictionary; можно быть `Identifiable` и плохим ключом `Dictionary`, если идентичность только в `id`. Типичный промах: `ForEach(0..<count)` на меняющемся массиве, или `id: \.self` на `String`, который не уникален.



```swift
struct Team: Identifiable, Hashable {
    let id: UUID
    var name: String
}

ForEach(teams) { team in
    Text(team.name)
}
```


**Потом обычно спрашивают**

- Почему `id: \.name` баг, если две команды могут делить имя?
- `Identifiable` + `Hashable`: могут ли `id` и `==` разойтись?
- Item ID в diffable snapshot: то же правило?

</details>

<h2 id="nil-coalescing">Nil coalescing, `??`</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`??`** разворачивает optional или берёт значение справа. Правая сторона считается, только если слева `nil`, поэтому `name ?? loadDefault()` можно писать спокойно. Можно цепочку `a ?? b ?? c`. Хотят это вместо `if let`, когда default реально есть. Прятать программную ошибку за `"unknown"` или `0` — обычный запах: нужен был `guard` или `throw`. Справа тип должен совпасть с развёрнутым; `?? []` — бытовой ход «пусто, если нет».



```swift
let nickname: String? = nil
let display = nickname ?? "Guest"

let counts: [String: Int] = [:]
let taps = counts["home"] ?? 0
```


**Потом обычно спрашивают**

- Правая сторона `??` всегда вычисляется?
- Как сцепить несколько optional с default?
- Когда `??` хуже, чем `guard let`?

</details>

<h2 id="optional-chaining">Optional chaining</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`foo?.bar`** лезет в optional и уходит в `nil`, если любой шаг `nil`. Всё выражение становится optional, даже если `bar` им не был. Можно цеплять методы и subscript: `user?.address?.street.prefix(1)`. Контрастируют с force unwrap и с `if let`, когда нужен стабильный unwrap на несколько строк. Цепочка, которая кончается `Void`, это `Void?` — поэтому `foo?.doSideEffect()` законно и легко проигнорировать. Не прячь длинную цепочку UI-запросов за `?.`, а потом удивляйся, почему ничего не случилось.



```swift
class Node {
    var next: Node?
    var value = ""
}

let head = Node()
let deep = head.next?.next?.value   // String?
head.next?.value = "child"
```


**Потом обычно спрашивают**

- Почему тип `foo?.count` optional, даже если `count` это `Int`?
- Как optional chaining стыкуется с присваиванием?
- Когда перестать чейнить и забиндить через `guard let`?

</details>

<h2 id="stored-vs-computed">Stored vs computed properties</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Stored** property занимает память на инстансе (`let` / `var` без геттера). **Computed** это геттер (и опциональный сеттер), который каждый раз выводит значение. `willSet` / `didSet` цепляются только к stored. Computed могут жить на enum и в protocol extension; stored нельзя, кроме class и struct. Типичный промах: computed, который делает I/O или аллоцирует, и цикл, читающий `view.frame` пять раз, делает работу пять раз. Закэшируй, если нужно дважды.



```swift
struct Size {
    var width: Double
    var height: Double
    var area: Double { width * height }
}
```


**Потом обычно спрашивают**

- Может ли computed property быть `lazy`?
- Где срабатывают property observers относительно кастомного сеттера?
- Зачем под computed класть private stored кэш?

</details>

<h2 id="string-optional-vs-iuo">String? и String!</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`String?`** — настоящий optional: надо unwrap. **`String!`** — implicitly unwrapped optional: по сути optional, но Swift разворачивает сам и крашится, если `nil`. IUO для two-phase setup: outlet, `awakeFromNib`, часть Objective-C import. Новый Swift-код берёт `String?` или non-optional, когда значение уже есть. Хотят: «я не ставлю `!`, чтобы не писать `?`». `IBOutlet var title: UILabel!` — история; многие команды пишут `?` или грузят view в `init`.



```swift
var name: String? = "Ada"
var title: String! = "Engineer"

print(name?.count as Any)   // Optional(3)
print(title.count)          // 8 — traps if title is nil
title = nil
```


**Потом обычно спрашивают**

- `String!` в runtime другой тип, чем `String?`?
- Почему UIKit outlet так долго были `!`?
- Что будет, если передать `String!` в функцию, которая ждёт `String`?

</details>

<h2 id="type-safety">Type safety</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift проверяет типы **на компиляции**. `String` в `Int` без конверсии не положишь. Optional делает «может не быть» частью типа, поэтому `nil` не тихий краш потом. Type inference всё равно выбирает конкретный тип. Это не динамическая типизация. Типичный промах: `as!` / `try!`, чтобы «проскочить» компилятор.



```swift
let n = 3            // Int
// let n: Int = "3"  // does not compile
let parsed = Int("3") // Int?, not Int
```


**Потом обычно спрашивают**

- Type safety vs type inference: они конфликтуют?
- Как Optional вписывается в эту историю?
- Что `Any` делает с безопасностью?

</details>

<h2 id="value-vs-reference">Value type и reference type</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Value type** копируется при присваивании: struct, enum, tuple. **Reference type** шарится: class, actor, closure. Это вопрос про семантику; class vs struct — языковая фича, которой это обычно делают. Хотят услышать про identity, мутацию, которую видно из двух переменных, и что на самом деле защищает `let`. Copy-on-write: `Array` и `String` выглядят как values, но делят storage до записи. Ловушка: struct хранит class — struct копируется, class нет.



```swift
struct Value { var n: Int }
class Ref { var n: Int; init(n: Int) { self.n = n } }

var v1 = Value(n: 1)
var v2 = v1
v2.n = 2                 // v1.n == 1

let r1 = Ref(n: 1)
let r2 = r1
r2.n = 2                 // r1.n == 2
```


**Потом обычно спрашивают**

- Closure — value type или reference type?
- Что говорит `===`, чего не говорит `==`?
- Как struct всё равно может шарить mutable state?
- Почему `Int`, `String` и `Array` — struct, а не class?

</details>

<h2 id="deinit">deinit</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`deinit` это хук разборки class (или actor): срабатывает, когда ушла последняя strong-ссылка, прямо перед уничтожением объекта. У struct и enum его нет, нечего разбирать, нет идентичности. Им инвалидируешь `Timer`, глушишь сокет или в дебаге assert'ишь, что cleanup прошёл. Нельзя `throw`, нельзя `await` в non-isolated `deinit` (isolated `deinit` у actor это более новое исключение), и нельзя стартовать работу, которой нужно, чтобы `self` остался жив. Типичный промах: сильно захватить `self` в таймере, который инвалидируешь только в `deinit`. Тогда `deinit` никогда не придёт.



```swift
final class Ticker {
    private var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }

    deinit { timer?.invalidate() }
}
```


**Потом обычно спрашивают**

- Почему у struct нет `deinit`?
- На каком потоке бежит `deinit`?
- Isolated `deinit` у actor: что это починило?

</details>

<h2 id="guard">guard</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`guard`** — проверка с ранним выходом. Условие должно быть true, иначе сразу уходишь из scope. Поэтому `guard let` биндит имена на всю функцию: компилятор знает, что после строки они есть. Можно `guard` любой `Bool`, не только optional: `guard index < count else { return }`. Нравится, потому что happy path плоский. Else не может провалиться дальше: написал `print` и забыл `return` — не скомпилируется. Вложенные `guard`, которые все возвращают одну ошибку, часто лучше свернуть в одну throwing функцию.



```swift
func firstWord(in text: String?) -> String? {
    guard let text, !text.isEmpty else { return nil }
    return text.split(separator: " ").first.map(String.init)
}
```


**Потом обычно спрашивают**

- Почему else у `guard` обязан выйти из текущего scope?
- Можно ли `guard` булево, которое не optional bind?
- Как `guard` несколько optional сразу?

</details>

<h2 id="if-let-vs-guard-let">if let и guard let</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`if let`** разворачивает только для тела `if`. **`guard let`** разворачивает на весь остальной scope и на failure заставляет уйти (`return`, `throw`, `break`, `continue`, или что-то, что не возвращается). `guard` — для precondition вверху функции, happy path без отступа. `if let` — когда и nil, и non-nil пути реально работают. Shorthand `if let name` / `guard let name` биндит то же имя. Промах: пирамида `if let`, которая должна была быть тремя `guard`.



```swift
func greet(_ name: String?) {
    guard let name else { return }
    print("hi \(name)")
}

func label(_ name: String?) -> String {
    if let name {
        return name
    }
    return "anonymous"
}
```


**Потом обычно спрашивают**

- Какие statement законны в else у `guard`?
- Когда `if let` яснее, чем `guard let`?
- Как optional binding стыкуется с `async` / `throws`?

</details>

<h2 id="lazy">lazy</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`lazy var` это stored property, которое считают **один раз**, при первом чтении, и потом хранят. Бери для работы, которая может не понадобиться: тяжёлый formatter, открытие файла, сборка дочернего объекта. Это обязан быть `var`, потому что первое чтение мутирует storage. **Не thread-safe**: два потока могут прогнать инициализатор дважды. Это не `let` и не computed property (те пересчитываются каждый раз). `let`, которому всё равно нужна работа в init, это сразу вызванный closure: `let area = { Double.pi * r * r }()`. Eagerly, один раз, и можно шарить. Типичные ошибки: `lazy` на дешёвый `DateFormatter`, который всегда используешь, и захват `self` в `lazy` closure, который потом течёт.



```swift
final class Report {
    lazy var formatter: DateFormatter = {
        let f = DateFormatter()
        f.dateStyle = .medium
        return f
    }()
}
```


**Потом обычно спрашивают**

- `lazy var` vs computed `var` vs `let`, инициализированный в `init`?
- Почему `lazy` опасен между потоками?
- Как сделать значение «как `let`», но посчитать один раз в рантайме?
- Можно ли `lazy` свойство struct читать с `let` инстанса?

</details>

<h2 id="let-vs-var">let vs var</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`let` это биндинг, который нельзя переприсвоить. `var` можно. У **value type** `let` ещё и stored properties замораживает: `let` struct не помутировать. У **class** `let` держит только ссылку: на другой инстанс не перевесишь, а свойства объекта крутить можно. Вот этот follow-up и ждут. Бери `let`, пока мутация не нужна: намерение видно, компилятор ловит случайности. Типичная ошибка: «`let` значит объект иммутабельный», а в руках `let` class с кучей `var` свойств.



```swift
struct Point { var x: Int }
class Box { var value: Int = 0 }

let p = Point(x: 1)
// p.x = 2 // error

let box = Box()
box.value = 2 // ok
// box = Box() // error
```


**Потом обычно спрашивают**

- Почему `let` class мутировать можно, а `let` struct нельзя?
- Как это стыкуется с `mutating` методами?
- Когда `let` на reference type ставят специально?

</details>

<h2 id="map-vs-compactmap">map и compactMap — в чём разница</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`map`** трансформирует каждый элемент и сохраняет count. **`compactMap`** трансформирует и выкидывает `nil` — на выходе короче, без optional. Бытовой вопрос «распарси эти строки в int». По мышечной памяти всё ещё тянутся к `flatMap` на optional; этот overload переехал в `compactMap`. Другой промах: `map` + `filter { $0 != nil }` + force-unwrap — тот же `compactMap`, только длиннее. `flatMap` по-прежнему верное имя, когда мапишь в array и хочешь один плоский массив.



```swift
let raw = ["1", "x", "3"]
let mapped = raw.map(Int.init)         // [1, nil, 3]
let compact = raw.compactMap(Int.init) // [1, 3]

let nested = [[1, 2], [3]]
let flat = nested.flatMap { $0 }       // [1, 2, 3]
```


**Потом обычно спрашивают**

- Что делает `map` на optional?
- Когда `flatMap` правильнее, чем `compactMap`?
- Как переписать `compactMap` через `reduce`?

</details>

<h2 id="mutating">mutating</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Метод struct/enum, который пишет в `self` (или stored property), надо пометить **`mutating`**. Он подменяет всё значение целиком, поэтому на `let` инстансе его не вызвать. Методам class `mutating` не нужен: ссылка та же, объект меняется. Типичный промах: «mutating делает его class».



```swift
struct Counter {
    var n = 0
    mutating func bump() { n += 1 }
}

var c = Counter()
c.bump()
// let frozen = Counter(); frozen.bump() // error
```


**Потом обычно спрашивают**

- Почему `mutating` нелегален на class?
- Что значит `self = …` внутри mutating метода?
- Как это стыкуется с `let` свойством, в котором лежит struct?

</details>

<h2 id="static">static</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`static` принадлежит **типу**, не инстансу. `static let` это общая константа. `static func` зовут как `Foo.bar()`. На class `class func` можно override, `static func` нельзя (это `final` на типе). Stored `static var` это общее мутабельное состояние, относись как к полю синглтона. Типичная ошибка: `static var` как кэш и потом удивляться, почему тесты текут состоянием между кейсами.



```swift
enum Theme {
    static let accent = "teal"
    static func label(_ name: String) -> String { "\(accent)-\(name)" }
}

Theme.label("button")
```


**Потом обычно спрашивают**

- `static` vs `class` на методе?
- Где живёт `static var`, и он thread-safe?
- Когда `static` лучше синглтон-объекта?

</details>

<h2 id="switch">switch</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift `switch` обязан быть **exhaustive**, умеет матчить tuples, ranges, Optional и associated values у enum, плюс `where`. Неявного fallthrough нет. Пиши `fallthrough`, если правда хочешь. Поэтому он бьёт кучу `if` по состоянию. Типичный промах: `default`, который проглатывает новый case enum, который надо было обработать.



```swift
switch state {
case .ready(let value) where value > 0: show(value)
case .ready: showEmpty()
case .loading, .idle: showSpinner()
case .failed: showRetry()
}
```


**Потом обычно спрашивают**

- Почему exhaustiveness это фича безопасности?
- `where` vs вложенный `if`?
- Как матчить два значения сразу (tuple)?

</details>

<h2 id="try-try-try">try, try? и try!</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`throws`** помечает функцию, которая *может* упасть; **`throw`** — statement, который реально рождает ошибку. **`try`** зовёт throwing функцию и пускает ошибку дальше: caller сам `throws` или ты в `do/catch`. **`try?`** превращает failure в `nil` и выкидывает ошибку. **`try!`** разворачивает и крашится, если ошибка есть. **`rethrows`** бросает, только если closure-аргумент бросил (обычно `map`). Жёсткое правило: `try!` это «если упало — программа уже неправа», никогда сеть и decoding. `try?` ок, когда правда плевать почему упало; иначе catch и лог. `try?` плюс потом force-unwrap — тот же `try!` лишними шагами.



```swift
enum AgeError: Error { case negative }

func checked(_ age: Int) throws -> Int {
    guard age >= 0 else { throw AgeError.negative }
    return age
}

let ok = try? checked(9)      // Optional(9)
let no = try? checked(-1)     // nil
// let crash = try! checked(-1)
```


**Потом обычно спрашивают**

- Как сохранить ошибку, если функция не должна быть `throws`?
- Когда `try!` приемлем в app-коде?
- Что `try?` делает с success type?
- `throw` vs `throws` vs `rethrows`?

</details>

<h2 id="property-observers">willSet и didSet</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`willSet`** и **`didSet`** срабатывают вокруг присваивания stored property. `willSet` видит `newValue` до записи, `didSet` видит `oldValue` после. Из собственного `init` типа они не стреляют — сюрприз для тех, кто туда кладёт логи. Это реакция на изменение: clamp, notify, синхронизировать побочную таблицу. Не для вычисления значения — это computed property. Если снова присвоить то же свойство внутри `didSet`, можно уйти в рекурсию, нужна проверка. Не путай с KVO: это только Swift, и на мутации обёрнутого `self.x` они не стреляют так, как надеются, пока ты реально не присвоишь свойство.



```swift
var score = 0 {
    willSet { print("heading to \(newValue)") }
    didSet { print("was \(oldValue)") }
}

score = 10
```


**Потом обычно спрашивают**

- Почему observers не стреляют в `init`?
- Что будет, если `didSet` присвоит то же свойство?
- Как observers ведут себя у свойства внутри struct, который мутируешь через `var`?

</details>

<h2 id="collections">Коллекции в Swift</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`Array` это **value type** с copy-on-write: присваивание выглядит как копия, буфер шарится до мутации. Упорядоченный random-access список, выбор по умолчанию, subscript за `O(1)`. `Set` это неупорядоченные уникальные `Hashable` значения: членство и уникальность, не индекс. `Dictionary` это hash map по `Hashable` ключам. `Range` / `ClosedRange` это интервалы, не мешок элементов, хотя они sequence. Всё это сидит на `Sequence` / `Collection`, поэтому `map` и `filter` работают одинаково. Ни одна из них не thread-safe. Бери `Set`, когда снова и снова спрашиваешь «я уже видел этот id?»; `Array`, когда важен порядок; dictionary как упорядоченную ленту не используй. Типичная ошибка: `contains` по большому `Array` на горячем пути вместо `Set`.



```swift
let ids = Set([1, 2, 2, 3])          // {1, 2, 3}
let names = ["a": 1, "b": 2]
let firstThree = 0..<3
let ordered = [3, 1, 2]
```


**Потом обычно спрашивают**

- Когда `Set` быстрее, чем `Array.contains`?
- Почему `Dictionary` unordered, и какой на практике порядок итерации?
- Как `Range` и `Array` оба конформят `Collection`?
- Sequence vs Collection: можно ли пройти Sequence дважды?

</details>

<h2 id="implicit-vs-explicit">Неявные и явные типы</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Явный** тип ты написал сам (`var name: String = "a"`). **Неявный** вывел компилятор (`var name = "a"`). Это **type inference**: конкретный тип берут из контекста. Это не динамическая типизация, тип фиксируется на компиляции. Пиши аннотацию, когда правая сторона двусмысленна (`[]`, `nil`, protocol existential) или имя само тип не выдаёт. Типичный промах: `var x = 0`, а потом присвоить `Double`, или думать, что inference тормозит в рантайме.



```swift
var name = "onthecodepath"           // inferred String
var port: Int = 443                  // explicit
var items: [User] = []               // explicit — [] alone is ambiguous
```


**Потом обычно спрашивают**

- Когда inference ломается (`nil`, пустой массив)?
- Выведенный тип менее безопасен, чем аннотированный?
- Когда аннотируешь типы параметров у closure?
- Type inference и type safety: они конфликтуют?

</details>

<h2 id="higher-order-functions">Функции высшего порядка</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Функция высшего порядка принимает или возвращает функцию: `map`, `filter`, `compactMap`, `reduce`, `sorted`, `forEach`. Передаёшь closure вместо цикла. Бери их, когда трансформ в одну строку; оставляй `for`, когда есть ранний выход или несколько выходов. Типичный промах: `forEach` с сайд-эффектами, которые потом не протестировать, или `reduce`, который просто хуже `map`.



```swift
let raw = ["1", "3", "4", "6"]
let evenSum = raw.compactMap(Int.init).filter { $0.isMultiple(of: 2) }.reduce(0, +)
```


**Потом обычно спрашивают**

- `map` vs `compactMap` vs `flatMap`?
- Когда цикл `for` яснее?
- Что под капотом у `sorted(by:)` (семейство introsort, не Timsort)?
- `for` vs `forEach`: можно ли `return` / `break`?

</details>

<h2 id="optionals">Что такое Optional</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Optional это **`enum Optional<Wrapped> { case none, some(Wrapped) }`**. `nil` это `.none`. Поэтому работают `switch`, `map` и `??`: это настоящий тип, не флаг указателя. Разворачиваешь через `if let` / `guard let`, `??`, optional chaining или (редко) `!`. IUO (`String!`) всё ещё Optional, просто разворачивается неявно и падает, если `nil`. Типичные ошибки: «optional значит указатель, который может быть NULL», и тащить `Optional.none` как значение в персист без кодирования отсутствия.



```swift
enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}

let n: Int? = Int("x") // .none
print(n.map { $0 * 2 } ?? 0)
```


**Потом обычно спрашивают**

- Чем это отличается от ObjC `nil` messaging?
- `Optional` это enum или struct?
- Что возвращает `map` на Optional?
- Когда `Optional.none` неправильная модель (пустая строка vs отсутствует)?
- `nil` это другое значение, чем `Optional.none`?
- Назови все обычные unwrap: `if let`, `guard let`, `??`, `?`, `map` / `flatMap`, `!`, IUO. Когда какой честный?

</details>

<h2 id="protocols">Что такое protocol</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Protocol** — контракт: свойства и методы, которые тип обещает реализовать. Говоришь с «чем угодно, что умеет persist», не называя конкретный class. Так тестируешь и держишь UI подальше от URLSession. Conformance — на типе или в extension. С «это как interface» уводят в existentials (`any`), associated types и default implementations. Обычные ошибки: protocol на двадцать методов, которые как будто optional, и никто их нормально не реализует. Или protocol на тип только чтобы заинжектить то, что должно было быть функцией.



```swift
protocol Describable {
    var summary: String { get }
}

struct User: Describable {
    let name: String
    var summary: String { name }
}

func printSummary(_ item: any Describable) {
    print(item.summary)
}
```


**Потом обычно спрашивают**

- Чем `any Describable` отличается от `some Describable`?
- Может ли protocol требовать initializer?
- Когда protocol с associated type лучше, чем generic функция?

</details>

<h2 id="available">#available</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`#available`** — runtime проверка версии OS (иногда платформы). `if #available(iOS 17, *)` даёт новый API и при этом бежать на iOS 16. `@available` на функции — вторая половина: помечаешь *свой* API как требующий эту OS. `*` значит «и любая другая платформа на своём минимуме». Это не `#if os` и не `#if swift` — те compile-time. Промах: новый API вне ветки `#available`, или `@available` на весь тип и забыть fallback экран.



```swift
func titleFont() -> String {
    if #available(iOS 17, *) {
        return "iOS 17+ path"
    } else {
        return "fallback"
    }
}

@available(iOS 17, *)
func shimmer() {}
```


**Потом обычно спрашивают**

- Чем `#available` отличается от `#if os(iOS)`?
- Что значит `*` в `#available(iOS 17, *)`?
- Когда пометить метод `@available`, а не ветвиться внутри?

</details>

<h2 id="discardable-result">@discardableResult</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`@discardableResult` глушит варнинг «result unused» у функции, чей возврат читать необязательно. `removeValue(forKey:)` возвращает старое значение; большинство call site его выбрасывают. Ставь, когда оба стиля честные. Не лепи на `save() -> Bool`, чтобы спрятать проигнорированные ошибки. Вот ловушка на собесе. Типичный промах: пометить каждую фабрику discardable, и вызывающие не замечают, что дропнули cancellable.



```swift
@discardableResult
func updateTitle(_ title: String) -> Bool {
    guard !title.isEmpty else { return false }
    self.title = title
    return true
}

updateTitle("Hi")
```


**Потом обычно спрашивают**

- Когда игнор результата это баг (`AnyCancellable`, `Bool` флаги ошибок)?
- Чем это отличается от `_ = save()` на месте вызова?
- Почему `print` этот атрибут не нужен?

</details>

<h2 id="main-attribute">@main</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`@main`** помечает тип, которому принадлежит entry point процесса. Нужен `static func main()` или conformance к тому, кто его даёт, например SwiftUI `App`. Для многих новых приложений это заменило `UIApplicationMain` / `@UIApplicationMain`. В target только один `@main`. Проверка «где стартует приложение». Повесить `@main` на случайный хелпер или держать и `App`, и свой `main` в одном target — получишь запутанную linker error.



```swift
@main
struct InterviewApp {
    static func main() {
        print("entry")
    }
}
```


**Потом обычно спрашивают**

- Как SwiftUI `App` использует `@main`?
- Что заменило `@UIApplicationMain`?
- Может ли в target быть два типа с `@main`?

</details>

<h2 id="caseiterable">CaseIterable</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`CaseIterable`** даёт `allCases`: коллекцию всех case enum. Компилятор синтезирует для enum без associated values (и для большинства raw-value enum). Пикеры, настройки, тесты, которым нужны все case. Associated values блокируют synthesis: конечного списка payload нет. Спрашивают рядом с `ForEach(Tab.allCases)`. Не считай порядок `allCases` тем, что потом тихо поменяешь, если сохранил индекс: сохраняй имя case или raw value.



```swift
enum Tab: CaseIterable {
    case home, search, profile
}

let titles = Tab.allCases.map(String.init(describing:))
```


**Потом обычно спрашивают**

- Почему enum с associated values не получает `allCases` бесплатно?
- Можно ли написать свой `allCases`?
- Стоит ли сохранять порядок `allCases`?

</details>

<h2 id="class-vs-object">Class vs object</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Class** это чертёж: stored properties, методы, идентичность типа. **Object** (инстанс) это одно выделение по этому чертежу. `UIView` это class, `UIView()` это object. Два объекта могут быть одного class и всё равно разные идентичности (`===`). В Swift ещё есть struct и enum. В разговорной речи «объект» часто значит «инстанс типа», не только class. Типичный промах: «class лежит в памяти, а object это файл».



```swift
class Dog { var name: String; init(name: String) { self.name = name } }
let a = Dog(name: "Rex")
let b = Dog(name: "Rex")
a === b  // false — two objects, one class
```


**Потом обычно спрашивают**

- Class vs instance vs type (`Dog.self`)?
- Чем это отличается у struct?
- Что сравнивает `===`?

</details>

<h2 id="downcasting">Downcasting</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`as` это гарантированный upcast (или bridging cast). `as?` это failable downcast: `nil`, если runtime тип не совпал. `as!` падает при несовпадении. Downcast нужен, когда на руках `Any` / базовый class / ObjC `id`, а нужен конкретный тип. Бери `as?` плюс `guard`, или `if let view = sender as? UIButton`. Типичный промах: `as!` на dequeue ячейки, которую ты уже типизировал через `dequeueReusableCell(withIdentifier:for:)`.



```swift
func tap(_ sender: Any) {
    guard let button = sender as? UIButton else { return }
    button.isEnabled = false
}
```


**Потом обычно спрашивают**

- `as` vs `as?` vs `as!`: по одному предложению?
- Conditional cast vs `is` и потом `as!`?
- Как это стыкуется с `AnyObject`?

</details>

<h2 id="functions-vs-methods">Functions vs methods</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Function** это именованный вызываемый, который не принадлежит типу (`func clamp`). **Method** это функция на типе (`Array.append`). Методам дают `self`; `mutating` методы могут писать storage struct. Свободные функции проще тестировать и не требуют namespace-типа. Методы выигрывают, когда операция часть словаря типа. В Swift ещё есть `static` / `class` методы (на типе, не на инстансе). Типичный промах: «методы это функции, которые используют `self`», не сказав, где они живут.



```swift
func clamp(_ n: Int, to range: ClosedRange<Int>) -> Int {
    min(max(n, range.lowerBound), range.upperBound)
}

extension Int {
    func clamped(to range: ClosedRange<Int>) -> Int { clamp(self, to: range) }
}
```


**Потом обычно спрашивают**

- Когда хелпер кладёшь на тип, а когда рядом?
- `static` vs `class` vs свободная функция в том же файле?
- Как передать метод как значение функции (`foo.bar`)?

</details>

<h2 id="stored-properties-on-enum">Stored properties у enum</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Case enum это тег плюс опциональные associated values. **Отдельного instance storage** под лишние stored properties нет. Можно `static` stored, computed properties и методы. Нужны данные на инстанс? Клади в associated value или бери struct. Типичный промах: `enum Foo { var id: Int }` и удивление, почему не компилируется.



```swift
enum Load<Value> {
    case ready(Value)
    var isReady: Bool {
        if case .ready = self { return true }
        return false
    }
    static let retryLimit = 3
}
```


**Потом обычно спрашивают**

- Associated value vs stored property?
- Почему у enum всё равно может быть computed `var`?
- Когда переключаешься на struct?

</details>

<h2 id="strings-are-collections">String — это collection?</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`String` соответствует `Collection` (и `BidirectionalCollection`) из `Character`: можно итерировать, `map`, `filter`, резать. Character — extended grapheme cluster, не UTF-16 code unit, поэтому `"é".count` может быть `1`, даже если байтов больше. Subscript через `Int` нельзя: индексация не O(1), как ждут от C-строк. Хотят услышать: `String.Index` / `first` / `dropFirst`, а не `string[0]`. Классика: математика bridging с `NSString` (`utf16`) протекает в Swift и ломает emoji.



```swift
let word = "Swift"
for character in word { _ = character }

let first = word.first
let rest = String(word.dropFirst())
let start = word.startIndex
let second = word[word.index(after: start)]
```


**Потом обычно спрашивают**

- Почему `String` не `RandomAccessCollection`?
- Чем отличаются `Character`, `Unicode.Scalar` и UTF-8 views?
- Как безопасно взять первые N символов?

</details>

<h2 id="subscripts">Subscripts</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Subscript это доступ `type[key]`, который ты определяешь: `collection[i]`, `dict[key]`. Пишешь `subscript(index: Int) -> Element { get set }`. Ставь, когда тип это мешок значений, не когда это глагол. Несколько списков параметров законны (`grid[x, y]`). Типичный промах: subscript, который прячет сетевой вызов, или тот, что трапается на отсутствующем ключе вместо Optional.



```swift
struct Grid {
    private var cells: [Int]
    subscript(x: Int, y: Int) -> Int {
        get { cells[y * width + x] }
        set { cells[y * width + x] = newValue }
    }
    var width = 8
}
```


**Потом обычно спрашивают**

- Subscript vs именованный метод: когда `[]` врёт?
- Может ли subscript бросать?
- Чем subscript у `Dictionary` отличается от `Array`?

</details>

<h2 id="swift-module">Swift module</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Module** это единица компиляции, которую `import`: app target, продукт Swift package, фреймворк. `internal` (дефолт) виден внутри module, снаружи нет. Один `.swift` файл это не module. Для файла есть `fileprivate`. У module есть имя (`import UIKit`) и интерфейс, который компилятор сериализует. Типичный промах: «module это файл» или ждать, что `private` спрячет тип от остального app target.



```swift
// In module Networking
public struct Endpoint { public let path: String }
internal struct Signer { }   // app cannot see this
```


**Потом обычно спрашивают**

- Module vs target vs package product?
- Почему `internal` на типе приложения всё равно виден (или нет) в тестах того же приложения?
- Что меняет `@testable import`?

</details>

<h2 id="variadic">Variadic functions</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Variadic** параметр (`Int...`) принимает ноль или больше значений, внутри функции это array. `print` все уже знают. Обычно один variadic; в новом Swift можно больше, если лейблы держат вызовы читаемыми. Хотят: «в теле это array». Настоящий `[Int]` в variadic без splat не пробросишь: splat-оператора в Swift нет — пишешь overload на `[Int]`. Пустой вызов законный, пока не добавишь precondition.



```swift
func average(_ values: Double...) -> Double {
    guard !values.isEmpty else { return 0 }
    return values.reduce(0, +) / Double(values.count)
}

let mean = average(1, 2, 3, 4)
```


**Потом обычно спрашивают**

- Какой тип у variadic параметра внутри функции?
- Как передать уже существующий array в variadic функцию?
- Может ли функция иметь два variadic параметра?

</details>

<h2 id="assert">assert</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`assert`** фиксирует инвариант программиста и в debug ловит trap, если ложь. В обычном release condition вырезают: обязательную работу и security checks нельзя класть только в `assert`. **`precondition`** остаётся в release (если не собрал `-Ounchecked`). **`assertionFailure` / `preconditionFailure`** — версии «эта ветка невозможна». Хотят «только debug vs всегда». Частый промах: `assert` на ответ сервера, а в production тот же value force-unwrap.



```swift
func element(at index: Int, in values: [Int]) -> Int {
    assert(index >= 0 && index < values.count, "index out of range")
    return values[index]
}
```


**Потом обычно спрашивают**

- Чем `precondition` отличается от `assert`?
- Что происходит с `assert` в Release?
- Когда `fatalError` лучше?

</details>

<h2 id="inout">inout</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`inout` даёт функции записать обратно в переменную вызывающего. Значение копируют внутрь, мутируют, потом пишут назад. Это не C-указатель, который ты держишь. Аргумент должен быть мутабельный `var` (или computed property с сеттером). Нельзя передать `let`, литерал или то, что может исчезнуть посреди вызова. Типичный промах: `inout`, чтобы «не возвращать», на типе, которому честнее вернуть новое значение.



```swift
func bump(_ n: inout Int) { n += 1 }

var x = 1
bump(&x) // x == 2
```


**Потом обычно спрашивают**

- Зачем `&` на месте вызова?
- `inout` vs вернуть новое значение: когда что яснее?
- Можно ли передать computed property?

</details>

<h2 id="private-set">private(set)</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`private(set)` (или `internal(set)`, `fileprivate(set)`) оставляет **шире геттер** и **уже сеттер**. Снаружи читают `count`, присваивать может только тип (или файл). Это обычная ручка «состояние показать, мутацию спрятать»: `items` у ViewModel, которые view не должен подменять. Это не то же самое, что computed геттер над private stored, но на месте вызова читается так же. Типичный промах: `private(set) var` на struct и мутация с `let` инстанса.



```swift
struct Counter {
    private(set) var value = 0
    mutating func bump() { value += 1 }
}
```


**Потом обычно спрашивают**

- `private(set)` vs публичный геттер и private `var`?
- Какой access у сеттера, если написал только `private(set)`?
- Работает ли это на свойстве class, за которым смотрит UI?

</details>

<h2 id="typealias">typealias</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`typealias` это **имя** существующего типа, не новый тип. `typealias Codable = Encodable & Decodable` все уже знают. Пишешь для длинного closure (`typealias Handler = (Result<Data, Error>) -> Void`), платформенного алиаса (`UIColor` vs `NSColor`) или короткого generic (`typealias ID = UUID`). Сам по себе методы не добавляет и ABI не меняет. Типичный промах: считать typealias отдельным типом, который не даст передать оригинал, или прятать за ним tuple на 12 параметров вместо struct.



```swift
typealias JSON = [String: Any]
typealias Done = (Result<User, Error>) -> Void

func load(then: Done) { /* … */ }
```


**Потом обычно спрашивают**

- `typealias` vs wrapper struct: когда нужен настоящий тип?
- Почему `Codable` это typealias, а не третий protocol с лишними методами?
- Могут ли два module заалиасить одно имя на разные типы?

</details>

<h2 id="multiple-inheritance">Множественное наследование</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

У Swift **class один superclass**. C++-шного множественного наследования нет. Поведение собираешь **protocol** (тип может конформить многим) и protocol extension. `AnyObject` это class-bound. Типичный промах: «в Swift множественное наследование, потому что protocol». Protocol не superclass, stored properties у них нет.



```swift
protocol Flying { func fly() }
protocol Named { var name: String { get } }
struct Bird: Flying, Named {
    var name: String
    func fly() {}
}
```


**Потом обычно спрашивают**

- Protocol composition (`P & Q`) vs иерархия class?
- Почему protocol не может добавить stored property?
- Когда class всё ещё нужен ради общего storage?

</details>

<h2 id="uuid">Что такое UUID</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`UUID`** — 128-битный идентификатор. `UUID()` даёт случайное значение (version 4), достаточно уникальное для client-side id, моделей SwiftData и «кто эта строка» без сервера. Он `Equatable`, `Hashable`, `Codable`, каноническую строку можно прогнать туда-обратно. Спрашивают, чтобы услышать: не бери индекс массива как identity. UUID не секрет. Не парси строку самодельным regex. Не генерируй новый `UUID()` на каждый render SwiftUI `ForEach` — views начнут дёргаться.



```swift
struct Item: Identifiable {
    let id: UUID
    var title: String
}

let item = Item(id: UUID(), title: "Draft")
let parsed = UUID(uuidString: "E621E1F8-C36C-495A-93FC-0C247A3E6E5F")
```


**Потом обычно спрашивают**

- Почему UUID плохой id для `ForEach`, если создаёшь его на каждый render?
- Как сохранить UUID в JSON?
- Когда лучше серверный integer id?

</details>

<h2 id="tuples">Что такое tuple</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Tuple** — безымянная группировка двух и больше значений, с лейблами или без. Короткий путь вернуть из функции две вещи или распаковать пару в `switch`. Это не тип, вокруг которого проектируешь API: своих stored methods нет, inheritance нет, и synthesised protocols только если элементы уже им соответствуют. Смотрят, не хватаешься ли за tuple там, где крошечный struct читаемее. Обычный промах: public функция возвращает `(String, Int, Bool)`, и через полгода никто не помнит, что это.



```swift
func splitName(_ full: String) -> (first: String, last: String) {
    let parts = full.split(separator: " ", maxSplits: 1).map(String.init)
    return (parts[0], parts.count > 1 ? parts[1] : "")
}

let person = splitName("Ada Lovelace")
print(person.first)
```


**Потом обычно спрашивают**

- Когда tuple стоит заменить на struct?
- Может ли tuple соответствовать `Equatable`?
- Чем `(Int, String)` отличается от `(id: Int, name: String)`?

</details>

<h2 id="one-sided-ranges">One-sided ranges</h2>

<code>Junior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**One-sided range** — одна граница снята: `3...` это «с 3 до конца», `..<3` — «с начала до 3, не включая». Режут коллекции и ловят в `switch`. Это не свободные целые; коллекция всё равно подставляет недостающий конец. Частые ошибки: `array[3...]` с индексом за `endIndex` (trap), и думать, что `"hello"[2...]` скомпилируется. На строках ходишь через `String.Index`.



```swift
let names = ["Ann", "Bob", "Cara", "Drew"]
let tail = names[1...]     // Bob, Cara, Drew
let head = names[..<2]     // Ann, Bob

switch 12 {
case 10...: print("at least ten")
default: break
}
```


**Потом обычно спрашивают**

- Чем `...` отличается от `..<` на открытой стороне?
- Почему нельзя написать `"Swift"[1...]`?
- Как one-sided ranges появляются в `switch` по числам?

</details>

<h2 id="raw-strings">Raw strings</h2>

<code>Junior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Raw string** пишется `#"..."#` (или больше hash, если надо), чтобы backslash и кавычки были почти литералами. Нужен для regex-подобных паттернов, Windows-путей и вставленного JSON, где полно `"`. Интерполяция работает через `\#(value)`, не `\(value)`. Смотрят «знаешь ли синтаксис» и идут дальше. Промах: неправильно наслоить hash, когда в payload есть `#"#`, или забыть, что обычной строке для одного backslash всё ещё нужен `\\`.



```swift
let pattern = #"\d+\.\d+"#
let quote = #"He said "ship it""#
let name = "Ada"
let line = #"Hello \#(name)"#
```


**Потом обычно спрашивают**

- Как интерполировать внутри raw string?
- Что если сама строка содержит `#"#`?
- Когда raw string хуже обычной escaped строки?

</details>

<h2 id="print-vs-debugprint">print vs debugPrint</h2>

<code>Junior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`print` берёт `CustomStringConvertible`, текст для человека. `debugPrint` берёт `CustomDebugStringConvertible`, если он есть, иначе падает назад, плюс кавычит строки и показывает структуру, удобнее в логе. Для `"hi"` они похожи; для массива строк `debugPrint` добавит кавычки, чтобы было видно пробелы. На собесе это проверка «читал ли stdlib», не дизайн. В проде лучше structured logging (`Logger`); эти двое для консоли и playground.



```swift
let words = ["a", "b c"]
print(words)       // [a, b c]
debugPrint(words)  // ["a", "b c"]
```


**Потом обычно спрашивают**

- Какой protocol каждый предпочитает?
- Когда `CustomDebugStringConvertible` пишешь отдельно от `description`?
- Почему в приложении дефолтом лучше `Logger`?

</details>

<h2 id="compare-tuples">Как сравнивают два tuple</h2>

<code>Junior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Tuple сравниваются лексикографически, если каждый элемент `Comparable` и форма одинаковая. Swift смотрит первый элемент, потом следующий — как сортируешь фамилии, потом имена. Равенство так же, если элементы `Equatable`. Мелкий языковой вопрос: хотят услышать, что `(1, 100) < (2, 0)` true, потому что `1 < 2`. Разной arity не сравнишь, несовместимые типы не смешаешь. Не выдумывай свой `<` на tuple, если именованный struct с `Comparable` лучше задокументирует порядок.



```swift
(1, "b") < (1, "c")     // true
(2, 0) < (1, 99)        // false
(1, 2, 3) == (1, 2, 3)  // true
```


**Потом обычно спрашивают**

- В каком порядке сравниваются элементы?
- Можно ли сравнить `(Int, String)` с `(String, Int)`?
- Как отсортировать массив tuple `(score, name)`?

</details>

<h2 id="omit-return">Когда функцию можно писать без return</h2>

<code>Junior</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Если функция или closure — одно выражение, `return` можно не писать: Swift берёт это выражение как результат. Closures в `map` так делают постоянно. В новом Swift `if` и `switch` тоже выражения, так что короткая функция может обойтись без `return` даже с веткой. Это проверка синтаксиса, не дизайн. Работает только для одного выражения: `print` плюс значение — снова нужен `return`. Не прячь throwing вызов или side effect в one-liner без `return`, чтобы казаться умным.



```swift
func doubled(_ n: Int) -> Int { n * 2 }

let squares = [1, 2, 3].map { $0 * $0 }

func label(for count: Int) -> String {
    if count == 1 { "one" } else { "many" }
}
```


**Потом обычно спрашивают**

- Можно ли опустить `return`, если в теле два statement?
- Как `if` expressions это меняют в свежем Swift?
- Работает ли это для функций с `throws`?

</details>

### Mid

<h2 id="associated-types">Associated types</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Associated type это плейсхолдер, который заполняет конформер: `Collection.Element`, `Iterator.Element`. Protocol тогда становится **PAT**: сам по себе это не конкретный тип, компилятор не знает плейсхолдеры. Нельзя написать `let c: Collection`. Берёшь generic (`func sum<C: Collection>(_ c: C)`), opaque `some Collection<Int>` или `any Collection<Int>` (primary associated types). Type erasure (`AnyCollection`) это старый люк. На собесе хотят «почему `let x: Iterator` не компилируется», а не декламацию `associatedtype`. Типичная ошибка: навесить associated type, когда хватило бы generic метода на protocol.



```swift
protocol Stack {
    associatedtype Element
    mutating func push(_ value: Element)
    mutating func pop() -> Element?
}

struct IntStack: Stack {
    private var storage: [Int] = []
    mutating func push(_ value: Int) { storage.append(value) }
    mutating func pop() -> Int? { storage.popLast() }
}

func peekCount<S: Stack>(_ stack: S) -> String { "stack" }
```


**Потом обычно спрашивают**

- Почему `any Collection` стал полезным только с primary associated types?
- Associated type vs generic на методе protocol?
- Как type-erase PAT без `any`?

</details>

<h2 id="enum-associated-values">Associated values у enum</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

У case enum может быть **payload**: `case loaded(Data)`, `case failed(Error)`. Так Swift моделирует state machine без кучи optional свойств, которые разъезжаются. Associated values — не raw values. Raw value — один compile-time компаньон вроде `String` на каждый case. Разворачиваешь через `switch` или `if case`. Любят «loadable» enum против `isLoading` + `value` + `error`. Промах: положить mutable class в payload и удивляться, почему два `.loaded` делят storage.



```swift
enum LoadState {
    case idle
    case loaded(Data)
    case failed(Error)
}

func title(for state: LoadState) -> String {
    switch state {
    case .idle: return "—"
    case .loaded(let data): return "\(data.count) bytes"
    case .failed: return "failed"
    }
}
```


**Потом обычно спрашивают**

- Чем associated values отличаются от raw values?
- Может ли case нести больше одного associated value?
- Почему enum безопаснее трёх optional для loading UI?

</details>

<h2 id="copy-on-write">Copy-on-Write</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Copy-on-write значит: присваивание **шарит storage**, пока кто-то не мутирует. Так живут `Array`, `String` и `Dictionary`: `var b = a` дёшево; `b.append` копирует, только если буфер не uniquely referenced. То же самое собираешь сам: class-буфер на куче плюс `isKnownUniquelyReferenced`. Буфер уникален, мутируй на месте; нет, скопируй, потом мутируй. На собесе хотят uniqueness check, а не «struct дешёвые». Типичные ошибки: положить class внутрь struct и решить, что получил value semantics, или копировать на каждую запись, даже когда буфер уникален.



```swift
final class Storage { var values: [Int] }

struct List {
    private var storage: Storage

    init(_ values: [Int]) { storage = Storage(values: values) }

    mutating func append(_ value: Int) {
        if !isKnownUniquelyReferenced(&storage) {
            storage = Storage(values: storage.values)
        }
        storage.values.append(value)
    }
}
```


**Потом обычно спрашивают**

- Почему `append` должен быть `mutating`, если class и так меняется на месте?
- Что будет, если два потока мутируют CoW storage без синхронизации?
- Почему большинству модельных struct свой CoW не нужен?
- Скопировал `[Class]`, у одного массива `popLast`, мутировал элемент: кто видит новое имя?

</details>

<h2 id="escaping-closures">Escaping и non-escaping closures</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Closure **non-escaping**, если её зовут до return функции — дефолт для аргументов. **`@escaping`** значит функция сохраняет её или зовёт позже: completion handler, `DispatchQueue.async`, Combine sink. Escaping может пережить `self`, поэтому capture сильный, пока не напишешь `[weak self]`. Non-escaping во многих случаях может брать `self` без `self.`: компилятор знает, что цикл так не сложится. Спросят, почему на completion handler появился `@escaping`. Пометить `@escaping` «на всякий», а звать синхронно — ложь компилятору и читателю.



```swift
var handlers: [() -> Void] = []

func store(_ handler: @escaping () -> Void) {
    handlers.append(handler)
}

func runNow(_ handler: () -> Void) {
    handler()
}
```


**Потом обычно спрашивают**

- Почему non-escaping closures в instance methods могут не писать `self.`?
- Как `@escaping` стыкуется с `async`?
- Какой retain cycle обычно делает сохранённый completion handler?
- `@escaping` vs `@autoclosure` — может ли параметр быть обоими?

</details>

<h2 id="extension-vs-protocol-extension">Extension и protocol extension</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Type extension** добавляет методы, computed properties или conformance одному конкретному типу. **Protocol extension** даёт default implementation всем текущим и будущим conformer. Stored properties не добавит ни тот, ни другой. Ловушка — dispatch: метод живёт только в protocol extension и **не** requirement — статически диспатчится с compile-time типа. Переопределил на class, позвал через protocol — можешь всё равно попасть в default. Хочешь dynamic dispatch — метод на protocol. Type extension для удобств; protocol extension для общего поведения, которое готов сделать default.



```swift
protocol Speaker {
    func greet()
}

extension Speaker {
    func greet() { print("hello") }
    func wave() { print("wave") }   // not a requirement
}

struct Person: Speaker {
    func greet() { print("hi") }
}

let speaker: any Speaker = Person()
speaker.greet()   // hi
speaker.wave()    // wave — static if only on the extension
```


**Потом обычно спрашивают**

- Почему extension не может добавить stored properties?
- В чём подвох witness-table vs static dispatch?
- Когда свободная функция яснее protocol extension?

</details>

<h2 id="generics">Generics</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Generics** дают функции или типу работать с placeholder (`T`), который заполняется на call site. Constraints (`T: Hashable`) не дают placeholder стать «чем угодно», когда нужны `==` или hash. Коллекции, парсеры, «алгоритму плевать, какой элемент». Ведут от `func first<T>` к associated types на protocol. Промахи: слишком generic API, который никто не выговорит, и `Any`, потому что generic сигнатура стала кривой. Generic тип в runtime всё равно конкретный — по одной specialization, которую собрал компилятор.



```swift
func first<T>(_ items: [T]) -> T? { items.first }

struct Stack<Element> {
    private var items: [Element] = []
    mutating func push(_ item: Element) { items.append(item) }
    mutating func pop() -> Element? { items.popLast() }
}
```


**Потом обычно спрашивают**

- Как ограничить `T` больше чем одним protocol?
- Когда associated type, а не generic на самом protocol?
- Что такое type specialization?

</details>

<h2 id="method-dispatch">Method dispatch</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift выбирает один из трёх путей. **Static dispatch** (прямой вызов) это дефолт для struct, enum, `final` методов class и `private` членов, которые компилятор может доказать. **Table dispatch** идёт через vtable у class и **protocol witness table** у protocol existential: кого звать, решают в рантайме. **Objective-C message send** (`objc_msgSend`) это `@objc dynamic` и почти все override в UIKit: можно свизлить, и это медленнее. `final` и value types не просто стиль: компилятор девиртуализирует и иногда инлайнит. Типичная ошибка: горячий метод повесить на protocol existential в тесном цикле и удивляться, почему не оптимизируется как generic.



```swift
protocol Drawable { func draw() }
struct Circle: Drawable { func draw() {} }

final class Icon {
    func render() {} // static — class is final
}

func paint(_ item: any Drawable) {
    item.draw() // witness table
}
```


**Потом обычно спрашивают**

- Что меняет `dynamic`?
- Generic `func paint<T: Drawable>(_ item: T)` vs `any Drawable`: что умеет специализироваться?
- Почему `final` помогает по скорости?
- Можно ли `override` метод, который живёт только в class `extension`?
- Метод есть только в protocol extension: static или witness-table?

</details>

<h2 id="opaque-return-types">Opaque return types, `some`</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`some Protocol`** — «один конкретный тип, который соответствует, но имя не скажу». Компилятор тип знает, caller видит только protocol. Identity сохраняется, компилятор может specialize — поэтому работает `some View` в SwiftUI. `any Protocol` — коробка, в runtime разные conformer. С `some` обе ветки `if` должны вернуть один underlying type — отсюда `Group` / `AnyView`, когда не так. Хотят этот контраст. Вернул `some View`, а в body два разных view type — compile error, в который все упираются.



```swift
func badge() -> some Equatable {
    "new"
}

func label(highlighted: Bool) -> some Equatable {
    highlighted ? "on" : "off"
}
```


**Потом обычно спрашивают**

- Чем `some` отличается от `any`?
- Почему SwiftUI везде `some View`, а не `any View`?
- Что делать, если двум веткам нужны разные конкретные типы?

</details>

<h2 id="property-wrappers">Property wrappers</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Property wrapper** — тип с `@propertyWrapper` и `wrappedValue`. `@Clamped var score` — сахар: хранишь instance `Clamped` и говоришь с его wrapped value. `$score` это `projectedValue`, если его объявил — так `@State` отдаёт `Binding`. Пишут для clamp, UserDefaults, analytics, locking. Хотят знать: это типы, не магия компилятора, а composition и правила `init` быстро становятся кривыми. Не оборачивай всё; функция яснее, когда паттерна на переиспользование нет.



```swift
@propertyWrapper
struct Clamped {
    private var value: Int
    var wrappedValue: Int {
        get { value }
        set { value = min(max(newValue, 0), 10) }
    }
    init(wrappedValue: Int) {
        value = min(max(wrappedValue, 0), 10)
    }
}

struct Game {
    @Clamped var lives = 3
}
```


**Потом обычно спрашивают**

- Что такое `projectedValue` и как его прочитать?
- Как `@State` использует property wrapper?
- Какие пределы у композиции двух wrapper на одном свойстве?

</details>

<h2 id="result-type">Result</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`Result<Success, Failure>`** — enum с `.success` и `.failure`, где `Failure` это `Error`. Нужен, когда значение едет через callback, cache или Combine, и `throw` через эту границу не пролезет. `get()` возвращает в `throws`; `Result { try … }` — обратно. Сравнивают с optional (`nil` — не причина) и с `async`/`throws` (на границе функции часто чище). Проглотить ошибку через `try?`, чтобы куда-то запихнуть `Result` — обычный запах.



```swift
enum ParseError: Error { case empty }

func parse(_ text: String) -> Result<Int, ParseError> {
    text.isEmpty ? .failure(.empty) : .success(text.count)
}

switch parse("hi") {
case .success(let count): print(count)
case .failure(let error): print(error)
}
```


**Потом обычно спрашивают**

- Как конвертировать `Result` в `throws` и обратно?
- Когда `async throws` лучше, чем `Result`?
- Почему `Result<T, Error>` иногда хуже typed failure?

</details>

<h2 id="result-builders">Result builders</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Result builder** (`@resultBuilder`) собирает пачку statements в closure в одно значение через `buildBlock`, `buildIf`, `buildEither` и компанию. `@ViewBuilder` в SwiftUI все уже используют: в body `VStack` можно перечислить view без array. Можно написать крошечный builder для строк или шагов теста. Хотят механизм, не туториал SwiftUI. Builder прячет control flow: `if` становится `buildEither`, поэтому дебажить generic ошибку `some View` больно. Не выдумывай builder, если хватит параметра `[Item]`.



```swift
@resultBuilder
struct StringBuilder {
    static func buildBlock(_ parts: String...) -> String {
        parts.joined()
    }
}

@StringBuilder
func title() -> String {
    "Hello"
    " "
    "Swift"
}
```


**Потом обычно спрашивают**

- Какие `build*` методы нужны для `if/else`?
- Как этим пользуется `@ViewBuilder`?
- Когда result builder неправильная абстракция?
- Почему `body` больше чем с десятью детьми нужен `Group` / `TupleView` split?

</details>

<h2 id="defer">defer</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`defer`** откладывает работу на выход из текущего scope: `return`, `throw`, `break` или просто конец. Несколько `defer` бегут в обратном порядке, last-in first-out. `defer` *внутри* другого `defer` бежит, когда выходит внутренний блок, не как четвёртый пункт внешнего стека. Cleanup рядом с setup: закрыть файл, закончить activity, unlock. Ошибки не ловит и новый scope для failure не создаёт — только откладывает statements. Любят «unlock даже если throw». `return` внутри `defer` нельзя. Переменная в `defer` читается на момент выхода, не на строке `defer`.



```swift
func parse() -> Int {
    var step = "start"
    defer { print(step) }
    defer { print("second") }
    step = "done"
    return 1
}
// prints "second" then "done"
```


**Потом обычно спрашивают**

- В каком порядке бегут сложенные `defer`?
- Бежит ли `defer`, если функция бросила?
- Почему `defer` лучше, чем дублировать cleanup перед каждым `return`?
- Что напечатается, если один `defer` содержит другой `defer`?

</details>

<h2 id="final">final</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`final`** на class (или методе) запрещает subclassing и override. И сигнал дизайна — «это не точка расширения» — и намёк компилятору: можно не ходить в vtable. Видишь на хелперах, view model и на том, от чего не хочешь, чтобы наследовались ради внутренностей. Ещё хотят: у struct и enum `final` уже подразумевается. Пометить class `final` не делает его value type. Промах: оставить каждый UIKit subclass open «на всякий», а потом каша из override.



```swift
final class ImageCache {
    func data(for key: String) -> Data? { nil }
}

// class DiskCache: ImageCache {} // error
```


**Потом обычно спрашивают**

- Меняет ли `final` ARC или value semantics?
- Почему компилятор может сгенерировать более быстрый код для `final` методов?
- Когда пометить `final` один метод, а class оставить open?

</details>

<h2 id="self-vs-self">self и Self</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`self`** — текущий instance. **`Self`** — текущий тип: class, struct или конкретный conformer в protocol. `Self` в requirement protocol (`func copy() -> Self`), в static factory, когда subclass должен вернуть свой тип. **`Self.self`** — значение metatype (`Point.Type`), то что передаёшь в `JSONDecoder.decode(User.self)`. `self` пишешь в escaping closures и чтобы отличить свойство от параметра. Оба на доске, потому что вслух звучат одинаково. `Self` в protocol — PAT constraint; одна из причин, почему таким protocol так долго нужен был type erasure.



```swift
struct Point {
    var x: Int
    static func zero() -> Self { Self(x: 0) }
    func doubled() -> Self { Self(x: x * 2) }
}

extension Point {
    func offset(_ x: Int) -> Point {
        var copy = self
        copy.x += x
        return copy
    }
}
```


**Потом обычно спрашивают**

- Почему некоторые protocol пишут `Self` в return type?
- Когда внутри closure обязательно писать `self.`?
- Как `Self` ведёт себя в иерархии class vs в struct?
- `self` vs `Self` vs `Self.self` — по одному предложению?

</details>

<h2 id="some-vs-any">some vs any</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`some P` это **opaque** тип: вызывающий знает, что это `P`, компилятор всё ещё знает конкретный тип. Поэтому он специализирует и держит маленький фиксированный layout. `any P` это **existential**: значение в коробке, конкретный тип может смениться в рантайме, вызовы идут через witness table. `some` для return type, который ты контролируешь (`some View`). `any`, когда надо хранить разные конформеры или тип меняется. Protocol с associated types часто нельзя писать голым типом: пишешь `any Collection` или generic. Типичный промах: «`any` это просто новое написание имени protocol» без цены коробки, или вернуть `any View` из SwiftUI `body`.



```swift
func label() -> some Equatable { "ok" }
// let a = label(); let b = label(); a == b // same underlying type

var items: [any Equatable] = [1, "x"]
```


**Потом обычно спрашивают**

- Почему в `body` нужен `some View`, а не `any View`?
- Как это связано с PAT (protocol with associated types)?
- Когда existential box реально бьёт по performance?
- `func f<T: Equatable>(_: T)` vs `func f(_: some Equatable)`: одна идея?

</details>

<h2 id="immutability">Почему immutability важна</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Immutability** — значение не меняется после создания: `let` bindings, value types, API, которые возвращают новое значение вместо мутации на месте. Оценку за привычку писать `let` не ставят. Хотят причины: локальное рассуждение (нет неожиданной мутации за shared reference), безопаснее concurrent reads, меньше side effects, когда данные уходят во view или в тест. `let` на class instance замораживает только указатель, не свойства объекта. Другой промах: «я взял struct» считают thread-safe, а внутри class или callback, который мутирует что-то ещё.



```swift
struct Account {
    let id: String
    var balance: Int
}

let frozen = Account(id: "a1", balance: 10)
var working = frozen
working.balance += 5
// frozen.balance is still 10
```


**Потом обычно спрашивают**

- Делает ли `let` на class объект immutable?
- Как copy-on-write стыкуется с `let` array?
- Когда mutable class всё ещё честная модель?

</details>

<h2 id="frozen">@frozen</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`@frozen` это обещание **library evolution**: этот enum или struct не нарастит public case или stored properties так, чтобы сломать клиентов, собранных против старого SDK. Тогда компилятор может выкинуть путь «неизвестный будущий case»: exhaustive `switch` без `@unknown default` и дешевле layout. Ставят на типы в духе stdlib (`Result`, `Optional`) и на свои ABI-stable module. App-коду, который не бинарный фреймворк, почти никогда не нужно. Типичный промах: `@frozen` на app enum «ради performance», или добавить case в frozen public enum и тихо сломать ABI.



```swift
@frozen public enum Load<Value> {
    case idle
    case ready(Value)
}

func label<Value>(_ load: Load<Value>) -> String {
    switch load {
    case .idle: return "…"
    case .ready: return "ok"
    }
}
```


**Потом обычно спрашивают**

- `@frozen` vs `@unknown default` на не-frozen enum?
- Когда app target это реально нужно?
- Что ломается, если в frozen public struct добавить stored property?

</details>

<h2 id="conditional-conformances">Conditional conformances</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Тип может соответствовать protocol **только когда его параметры тоже**: `Array` это `Equatable`, когда `Element` такой. Пишешь `extension Box: Equatable where T: Equatable`. Так generic-обёртки остаются честными: коробка функций не `Equatable` только потому что есть `Box`. Спрашивают после generics. Нельзя условно соответствовать так, чтобы пересечься с другим conformance, и `where` должен быть тем, что компилятор докажет на use site. Промах: написать `==` на обёртке безусловно и крашнуться или соврать, когда `T` сравнивать нельзя.



```swift
struct Box<T> {
    var value: T
}

extension Box: Equatable where T: Equatable {}

let a = Box(value: 1)
let b = Box(value: 1)
_ = a == b
```


**Потом обычно спрашивают**

- Почему `[Int]` equatable, а `[() -> Void]` нет?
- Можно ли так же добавить условный `Codable`?
- Что если два conditional conformance пересекаются?

</details>

<h2 id="designated-convenience-init">Designated vs convenience init</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Designated** init полностью инициализирует тип и зовёт `super.init` (у class). **Convenience** init обязан позвать другой init на `self` и существует, чтобы заполнить дефолты. У Swift struct есть memberwise init; у class надо быть явным. Правило двух фаз: свои stored properties, потом `super`, потом кастомизация. Типичный промах: designated init сабкласса без `super`, или convenience, который пытается напрямую выставить свойство суперкласса.



```swift
class Vehicle {
    let wheels: Int
    init(wheels: Int) { self.wheels = wheels }
    convenience init() { self.init(wheels: 4) }
}
```


**Потом обычно спрашивают**

- Почему convenience init обязан звать `self.init`?
- Required init: когда сабкласс его наследует?
- Чем это отличается от memberwise init у struct?

</details>

<h2 id="failable-throwing-init">Failable и throwing init</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`init?` может вернуть `nil`, когда вход нелегальный (`Int("x")`, `URL(string:)`). `init(...) throws` падает с `Error`, когда причин больше одной. Бери `init?` для простого «эта строка не значение». Бери `throws`, когда вызывающий должен `switch` по *почему*. Failable init у class обязан присвоить stored properties до `return nil` на failure path, после правил `super.init`. Обычная ловушка: convenience `init?`, который забыл designated путь. Типичный промах: `try!` на throwing init в проде.



```swift
struct Port {
    let value: Int
    init?(raw: String) {
        guard let n = Int(raw), (1...65535).contains(n) else { return nil }
        value = n
    }
}
```


**Потом обычно спрашивают**

- `init?` vs `init!` vs `throws`?
- Может ли failable init позвать throwing?
- Почему `UIImage(named:)` failable?

</details>

<h2 id="key-paths">Key paths</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Key path** — типизированный указатель на свойство: `\User.name`. Передаёшь в `map`, `sorted(by:)`, KVO-подобные API и SwiftUI. `\.self` — identity path, удобно для `Set` простых значений. Есть read-only, writable и reference-writable — зависит от `let` / `var` и value vs class. Хотят это вместо `{ $0.name }`, когда closure только читает свойство. Key path — значения, их можно хранить. Это не общий query language и методы с аргументами не вызовет.



```swift
struct User {
    var name: String
    var age: Int
}

let users = [User(name: "Ada", age: 36), User(name: "Grace", age: 85)]
let names = users.map(\.name)
let oldest = users.sorted(by: \.age).last
```


**Потом обычно спрашивают**

- Чем `KeyPath` отличается от `WritableKeyPath`?
- Как написать key path через несколько свойств?
- Где SwiftUI использует key paths?

</details>

<h2 id="macros">Macros</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift **macro** это код на этапе компиляции, который пишет ещё Swift (`@Observable`, `#Preview`, `#expect`). Freestanding выглядят как `#name`; attached как `@name` на типе или члене. Крутятся в песочнице и раскрываются в исходник, который можно показать в Xcode. Бери, чтобы убить бойлерплейт, который иначе генерировал бы руками, не чтобы прятать control flow. Типичный промах: считать macro runtime reflection или везти macro plugin без версии вместе с module.



```swift
@Observable
final class Cart {
    var items: [Item] = []
}

#Preview {
    CartView()
}
```


**Потом обычно спрашивают**

- Freestanding vs attached: по одному примеру?
- Чем это отличается от property wrapper?
- Что раскрываешь в Xcode, когда macro ведёт себя странно?

</details>

<h2 id="mirror">Mirror и reflection</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`Mirror` это **read-only reflection** в Swift: даёшь инстанс, идёшь по `children` (label + value) и display style. Для дебаг-дампов, наивного сериализатора или тестов, которые проверяют stored properties. Это не KVC, методы не зовёт, медленно и хрупко через границы module (`private` children пропадают). `type(of:)` / `.Type` / `.self` это **metatypes**: конструируешь или сравниваешь типы, stored properties не обходишь. Типичный промах: строить продовый персист на `Mirror` или ждать, что computed property увидит как child.



```swift
struct User { let name: String; let age: Int }
for child in Mirror(reflecting: User(name: "Ada", age: 36)).children {
    print(child.label ?? "?", child.value)
}
```


**Потом обычно спрашивают**

- Mirror vs `dump` vs `CustomDebugStringConvertible`?
- Почему это плохая замена Core Data / SwiftData?
- Metatype (`User.Type`) vs `Mirror` инстанса: какой вопрос они задавали?

</details>

<h2 id="never">Never</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`Never` это тип **без значений**. Функция с `-> Never` не может вернуться: `fatalError`, `preconditionFailure`, бесконечный `while true`. Publisher или `Result` с `Never` как `Failure` не умеет фейлиться. `switch` по `Never` без case. На собесе хотят «uninhabited type», не «void». У `Void` одно значение `()`. Типичный промах: написать `-> Never` у функции, которая иногда возвращается, или думать, что `fatalError` возвращает `Void`.



```swift
func die(_ message: String) -> Never {
    fatalError(message)
}

let taps = PassthroughSubject<Void, Never>()
```


**Потом обычно спрашивают**

- `Never` vs `Void`: по одному предложению?
- Почему `get()` у `Result<Int, Never>` может быть без `throws`?
- Где SwiftUI использует `Never` (например body у `EmptyView`)?

</details>

<h2 id="typed-throws">Typed throws</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift 6 умеет бросать **конкретный тип ошибки**: `func load() throws(LoadError)`. Вызывающие `catch` этот тип без коробки `any Error`, и компилятор знает набор фейлов. Голый `throws` по-прежнему значит `throws(any Error)`. Typed throw бери, когда у API два-три восстанавливаемых случая, по которым вызывающий должен `switch`. На системной границе (`URLSession`, диск) оставляй `any Error` и мапь внутрь. Типичный промах: типизировать каждый хелпер, а на UI всё равно `throws(any Error)`, или выдумать enum ошибки на двадцать case, которые никто не обрабатывает.



```swift
enum LoadError: Error { case missing, forbidden }

func load() throws(LoadError) -> String {
    throw .missing
}

do {
    _ = try load()
} catch .missing {
    // typed
} catch {
    // forbidden
}
```


**Потом обычно спрашивают**

- Когда всё равно хочешь `any Error`?
- Как замапить `URLError` в typed domain error?
- Меняет ли typed throws `Result`?

</details>

<h2 id="abstract-class">Абстрактный class в Swift</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

В Swift нет ключевого слова `abstract`. Ту же форму дают **protocol** (обязательные методы, без дефолта) плюс protocol extension для общего кода, либо class, который никто не инстанцирует, а методы «надо override». Компилятор за этим не следит. Бери protocol. `required init` и фабрики закрывают «надо сконструировать сабкласс». Типичная ошибка: пустой базовый class, который существует только чтобы два типа делили имя.



```swift
protocol Feed {
    func load() async throws -> [String]
}

extension Feed {
    func loadOrEmpty() async -> [String] {
        (try? await load()) ?? []
    }
}
```


**Потом обычно спрашивают**

- Почему не базовый class с `fatalError("override")`?
- Как PAT и `some Feed` это меняют?
- Когда иерархия class всё ещё правильная модель?

</details>

<h2 id="composition-over-inheritance">Композиция вместо наследования</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Бери **has-a**, не **is-a**. У `Player` есть `Health` и `Mover`, а не дерево `GameObject` на шесть уровней. Swift к этому толкает protocol и struct. Наследование всё ещё выигрывает в UIKit (`UIViewController`) и в настоящем is-a (`UIButton` это `UIView`). Типичный промах: базовый class с `fatalError("override")` на каждую фичу.



```swift
struct Health { var hp: Int }
struct Player { var health: Health; var name: String }
```


**Потом обычно спрашивают**

- Когда иерархия class всё ещё правильная модель?
- Как это выглядит как protocol composition (`P & Q`)?
- При чём тут тесты?

</details>

<h2 id="string-count">Сложность String.count</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

`String` это коллекция **extended grapheme clusters**, не UTF-16 юнитов. `count` идёт по строке, поэтому это **O(n)** по числу кластеров: семейный эмодзи даёт `count` 1, не 4. `utf8.count` / `utf16.count` дешевле, когда нужны байты или длина `NSString`. Не кэшируй `count` так, будто это `Array.count` (`O(1)`), пока не померил и строка не огромная. Типичный промах: `count` в условии цикла, который каждый раз сканирует заново, или считать, что `NSString.length` совпадает с `String.count`.



```swift
let s = "👨‍👩‍👧‍👦"
s.count          // 1
s.utf16.count    // 11
(s as NSString).length
```


**Потом обычно спрашивают**

- Почему `index(offsetBy:)` тоже O(n)?
- `count` vs `isEmpty`: что берёшь как буль?
- Как это отличалось в очень старом Swift (`countElements`)?

</details>

<h2 id="autoclosure">Что такое @autoclosure?</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`@autoclosure`** сам заворачивает выражение аргумента в `() -> T`, и уже вызываемый код решает, вычислять его или нет. Так живут `assert` и `precondition`: тяжёлое сообщение об ошибке не собирают, если проверка прошла. По смыслу те же `&&` и `||`: второй операнд может вообще не выполниться. На своём API ставишь `@autoclosure`, когда аргумент это дефолт или диагностика. На собесе хотят услышать «откладывает вычисление». Если closure вызвать дважды, выражение посчитается дважды. Не передавай побочные эффекты, если это не смысл. Само по себе это не делает closure escaping: для этого нужен ещё `@escaping`.



```swift
func expect(_ condition: @autoclosure () -> Bool, _ message: @autoclosure () -> String) {
    if !condition() {
        print(message())
    }
}

let count = 0
expect(count > 0, "expensive \(Array(repeating: "!", count: 1000).joined())")
```


**Потом обычно спрашивают**

- Зачем `assert` и `precondition` берут autoclosure?
- Что будет, если callee вызовет autoclosure дважды?
- Чем `@autoclosure @escaping` отличается от обычного `@autoclosure`?

</details>

<h2 id="error-directive">#error</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`#error("message")`** — жёсткий стоп на compile time. Сборка падает, строка видна в Xcode. Для «эта конфигурация запрещена» или пометить stub, который нельзя выпускать. `#warning` — та же идея, но сборка не падает. Это не `fatalError` и не `assert`: те бегут позже, если вообще бегут. Хотят отделить preprocessor diagnostics от runtime trap. `#error` в неактивной ветке `#if` нормально: так запрещаешь комбинацию target.



```swift
#if DEBUG
#else
#error("Local runs must use the Debug configuration")
#endif
```


**Потом обычно спрашивают**

- Чем `#error` отличается от `fatalError`?
- Когда взять `#warning`?
- Может ли `#error` сидеть внутри `#if os(iOS)`?

</details>

<h2 id="if-swift">#if swift</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`#if swift(>=5.9)`** (и компания) — compile-time код от версии языка, не OS. Нужен, когда module ещё собирается несколькими Swift toolchain, или фича появилась только после отсечки компилятора. `#available` — runtime проверка OS; их путают, в этом и вопрос. Есть ещё `#if compiler(>=5.7)`, когда важен компилятор, не language mode. Мёртвые ветки вырезаются, можно звать API, которых нет на старой стороне. Не этим детектишь iOS 17.



```swift
#if swift(>=5.9)
func featureFlag() -> String { "macros-era Swift" }
#else
func featureFlag() -> String { "older Swift" }
#endif
```


**Потом обычно спрашивают**

- Чем `#if swift` отличается от `#available`?
- Когда брать `#if compiler`?
- Проверяет ли компилятор неактивную ветку против текущего SDK?

</details>

<h2 id="operator-overloading">Operator overloading</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

В Swift можно определить `+`, `==` и даже свои операторы как `static` функции на типе. Имеет смысл, когда операция очевидна (`Seconds + Seconds`) и precedence не надо угадывать. Вопрос вкуса: synthesised `Equatable` / `Comparable` почти всегда лучше самописного `==`, а именованный метод в app-коде лучше `>>>`. Перегрузить `+`, чтобы мутировать базу или склеить несвязанные типы — красный флаг. Добавил оператор — держи в том же module, что и тип, и пиши identity и inverse как в математике.



```swift
struct Seconds {
    var value: Int

    static func + (lhs: Seconds, rhs: Seconds) -> Seconds {
        Seconds(value: lhs.value + rhs.value)
    }
}

let total = Seconds(value: 10) + Seconds(value: 5)
```


**Потом обычно спрашивают**

- Когда `Equatable` писать самому, а не отдавать компилятору?
- Что ломается у custom operator с неожиданным precedence?
- Как перегрузить `+=` и `+`?

</details>

<h2 id="can-import">canImport</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`#if canImport(UIKit)`** компилирует ветку, только если этот module есть у текущего target. Так один файл говорит с UIKit на iOS и AppKit на macOS, или опционально тянет package, который могут не линковать. Это compile-time, как весь `#if`. Контрастируют с `targetEnvironment` и `os()`. `canImport` про module graph, не «я на телефоне». Промах: обернуть `import` в `canImport`, а тип использовать вне того же `#if`.



```swift
#if canImport(UIKit)
import UIKit
typealias NativeColor = UIColor
#elseif canImport(AppKit)
import AppKit
typealias NativeColor = NSColor
#endif
```


**Потом обычно спрашивают**

- Чем `canImport` отличается от `#if os(iOS)`?
- Когда Swift package использует `canImport`?
- Почему `import` должен сидеть в том же `#if`, что и типы?

</details>

<h2 id="target-environment">targetEnvironment</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**`#if targetEnvironment(simulator)`** (или `macCatalyst`) — compile-time код про то, как собран бинарь, не какие OS API есть. Simulator-only логи, пропуск железа, вёрстка Catalyst. Это не `#available` и не `canImport`. Device-сборка ветку simulator вообще не содержит. Спрашивают, когда кто-то говорит «ifdef simulator». Промах: этим отличать iOS от macOS — это `#if os` — или думать, что это runtime `if`.



```swift
func analyticsEndpoint() -> String {
    #if targetEnvironment(simulator)
    "https://localhost:8080"
    #else
    "https://api.example.com"
    #endif
}
```


**Потом обычно спрашивают**

- Чем `targetEnvironment(simulator)` отличается от `#available`?
- Какие ещё значения `targetEnvironment` реально встречаются?
- Почему это нельзя переключить в runtime?

</details>

<h2 id="multi-pattern-catch">Несколько паттернов в catch</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

В **`catch`** можно несколько паттернов: `catch LoadError.offline, LoadError.timeout`. Одно тело на все. Финальный `catch` всё равно нужен, если функция может бросить другое, иначе `do` не exhaustive. Спрашивают после `do/try`: знаешь ли паттерны шире `catch { }`. В паттерне можно биндить (`catch LoadError.http(let code) where code >= 500`). Не сваливай несвязанные failure в один `catch` ради строк: ретраить decode как timeout — баг.



```swift
enum LoadError: Error { case offline, timeout, decoding }

func handle(_ work: () throws -> Void) {
    do {
        try work()
    } catch LoadError.offline, LoadError.timeout {
        print("retry")
    } catch {
        print(error)
    }
}
```


**Потом обычно спрашивают**

- Можно ли биндить associated values в multi-pattern `catch`?
- Что если ни один `catch` не совпал?
- Когда `where` на `catch` полезен?

</details>

### Senior

<h2 id="type-erasure">Type erasure</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Type erasure** прячет конкретный тип за коробкой, которая обещает только protocol (или фиксированный generic параметр). Нужно, когда caller не должен видеть `IntStore` vs `DiskStore`, или когда у protocol есть `associatedtype` / `Self` и его раньше нельзя было взять как тип. `AnySequence`, `AnyPublisher`, `AnyHashable`, `AnyView` — такие коробки из стандартной библиотеки. `any Protocol` — erasure на уровне языка; `some Protocol` наоборот: компилятор всё ещё знает конкретный тип. Хотят «зачем», а не заученный `AnyCancellable`. Свой eraser легко сломать: забыл пробросить метод, или стёр так, что пропали `Equatable` и identity.



```swift
protocol Store {
    associatedtype Item
    func all() -> [Item]
}

struct AnyStore<Item>: Store {
    private let _all: () -> [Item]

    init<S: Store>(_ store: S) where S.Item == Item {
        _all = store.all
    }

    func all() -> [Item] { _all() }
}
```


**Потом обычно спрашивают**

- Чем `any Sequence` отличается от `some Sequence`?
- Почему protocol с associated types так долго нуждался в `AnySequence`?
- Что теряешь, когда оборачиваешь что-то в `AnyView`?

</details>

<h2 id="struct-memory-layout">Раскладка struct в памяти</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Struct это сплошной мешок stored properties плюс **padding**, чтобы каждое поле попало в свою **alignment**. `MemoryLayout<T>.size` это payload, `stride` это шаг до следующего элемента в массиве (size, округлённый вверх до alignment), `alignment` это кратность адреса. Перестановка полей может ужать stride: `Bool`, потом `Int64`, потом `Bool` жрёт больше, чем `Int64` и два `Bool`. Это важно в огромных массивах и когда struct отдаёшь в C. Компилятор ещё может занять spare bits, например у Optional. Типичная ошибка: сложить `MemoryLayout` полей и ждать, что получится размер struct.



```swift
struct Padded {
    var flag: Bool
    var value: Int64
}

struct Tight {
    var value: Int64
    var flag: Bool
}

MemoryLayout<Padded>.stride // often 16
MemoryLayout<Tight>.stride  // often 16 still on 64-bit, but size can differ
```


**Потом обычно спрашивают**

- Почему `Array` смотрит на `stride`, а не на `size`?
- Как это меняется с `@frozen` и library evolution?
- Когда вообще стоит переставлять свойства ради layout?

</details>

<h2 id="abi-stability">ABI и module stability</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**ABI stability** (Swift 5 на платформах Apple) значит: runtime Swift на ОС может загрузить бинарники, собранные более новым компилятором. `libswiftCore` в каждое приложение больше не кладут. **Module stability** другое: клиент, собранный против твоего `.swiftinterface`, линкуется и после нового бинарника. Для этого нужны `BUILD_LIBRARY_FOR_DISTRIBUTION` и **resilient** public API: не добавлять stored property в `open` class, не переименовывать `public` метод, `@frozen` только когда правда имеешь в виду. App target это не нужно. Бинарный XCFramework, который отдаёшь другим командам, да. Типичный промах: «Swift ABI-stable» прочитать как «любой `public` тип в моём SDK можно менять».



```text
// SDK: enable library evolution
BUILD_LIBRARY_FOR_DISTRIBUTION = YES

// Safe later: add a method with a default.
// Breaking: add a stored property to an open class; change a public struct layout without @frozen care.
```


**Потом обычно спрашивают**

- ABI stability vs module stability vs source compatibility: три разных обещания?
- Почему `@frozen` на public enum важен клиентам?
- Когда отдаёшь source SPM вместо resilient XCFramework?

</details>
