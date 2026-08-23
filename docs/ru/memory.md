# Память

10 карточек · 7 часто спрашивают · [memory.md](../../topics/memory.md)

### Junior

<h2 id="swift-memory-management">Как Swift управляет памятью</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

У Swift нет tracing garbage collector. Экземпляры классов, actor и замыкания живут в куче и принадлежат ARC: каждая strong-ссылка поднимает счётчик, объект умирает в тот момент, когда счётчик стал нулём. Структуры, enum и tuple — value types: присваивание копирует значение (у Array, String и Dictionary ещё copy-on-write), их не считают.

Стек против кучи — вторичная деталь. Маленькие значения часто сидят на стеке; коллекции и экземпляры классов — в куче. На собесе хотят модель владения: значения копируются, ссылки шарятся, и считают только ссылки.

Классические косяки: «у Swift есть GC»; «каждый тип под ARC»; забыть, что замыкание — reference type и может держать self живым.



```swift
struct Point { var x: Int }

final class Box {
    var value: Int
    init(_ value: Int) { self.value = value }
}

var a = Point(x: 1)
var b = a
b.x = 2
// a.x is still 1 — value copy

let box1 = Box(1)
let box2 = box1
box2.value = 2
// box1.value is 2 — same instance
```


**Потом обычно спрашивают**

- Что ARC считает, а что игнорирует?
- Почему замыкание может залить view controller?
- Когда структура всё равно окажется в куче?

</details>

<h2 id="explain-arc">Объясни ARC</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Automatic Reference Counting — это компилятор, который вокруг экземпляров классов вставляет retain и release. Вставки — compile time, счётчик — runtime. У экземпляра хранится, сколько strong-ссылок на него смотрит. Создал объект — счётчик единица; расшарил — плюс один; последняя strong-ссылка ушла — ноль, deinit сразу. Паузы GC нет.

ARC работает только для reference types. weak и unowned счётчик не поднимают. Компилятор может выкинуть лишние retain, но модель на собесе всё равно «strong держит живым». Ломается это retain cycle: два объекта держат друг друга и никогда не доходят до нуля — рвёшь одну сторону weak или unowned.

До ARC в Objective-C был MRC: retain, release и autorelease писал сам. Забыл release — лик; лишний release — краш. @autoreleasepool — наследник того мира: в тесном цикле всё ещё сливает временные объекты.



```swift
final class Session {
    deinit { print("Session deinit") }
}

var primary: Session? = Session()  // count = 1
var mirror = primary               // count = 2
primary = nil                      // count = 1
mirror = nil                       // count = 0, deinit runs
```


**Потом обычно спрашивают**

- ARC крутится на фоновом потоке?
- Что происходит со счётчиком, когда объект передаёшь в функцию?
- ARC — compile time или runtime: что вставляет компилятор, а что делает процесс?
- Почему при охоте на лик первым делом ставишь deinit?
- Как жили без ARC в Objective-C?

</details>

### Mid

<h2 id="arc-vs-gc">ARC и garbage collection</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift живёт на ARC — Automatic Reference Counting, не на tracing garbage collector. У каждого экземпляра класса есть счётчик: сколько strong-ссылок на него смотрит. Счётчик стал нулём — объект сразу уходит в deinit. Нет паузы mark-and-sweep и нет отдельного GC-потока.

На собесе хотят именно контраст. ARC освобождает память в тот момент, когда пропала последняя strong-ссылка. Сборщик мусора придёт потом, когда сам решит просканировать кучу — и может стопнуть процесс. Цена ARC — increment/decrement на retain и release. Цена GC — периодические проходы по куче и возможные паузы. Цикл ссылок для ARC — вечная жизнь: два объекта держат друг друга strong и никогда не дойдут до нуля. Для GC цикл — обычный мусор, если снаружи до него никто не дотягивается. Считает ARC только экземпляры class, reference types.

Структуры, enum и tuple — value types, их не считают. Копирование копирует значение; у Array и String ещё copy-on-write.

Дальше почти всегда спрашивают про циклы. Два объекта со взаимными strong не умрут. Разрываешь weak — это optional, обнуляется, когда объект умер — или unowned: не optional, но если переживёшь владельца, поймаешь краш. Замыкания по умолчанию захватывают self сильно — самый частый лик в UIKit и SwiftUI.

Классические косяки: сказать «у Swift есть GC»; повесить weak на value type; взять unowned на экран, который может закрыться раньше колбэка; забыть, что async-работа и таймеры — те же strong-захваты.



```swift
final class Owner {
    var child: Child?
    deinit { print("Owner deinit") }
}

final class Child {
    weak var owner: Owner?
    deinit { print("Child deinit") }
}

do {
    let owner = Owner()
    let child = Child()
    owner.child = child
    child.owner = owner
}
// Both deinit. If `owner` were strong on Child, neither would.
```


**Потом обычно спрашивают**

- weak и unowned — когда что брать?
- Чем рвёшь retain cycle в замыкании?
- Почему структуры не участвуют в ARC?
- Что меняет unowned(unsafe)?

</details>

<h2 id="autoreleasepool">autoreleasepool</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Объекты Objective-C можно autorelease: retain отдаётся пулу и сольётся позже. Внешний пул главного потока сливается в конце каждого оборота RunLoop — после текущего события, таймера или source. У воркера GCD часто свой пул на work item, но тесный цикл внутри того же item всё равно копит. autoreleasepool создаёт вложенный пул и сливает его, когда скобка закрылась. Чистые Swift value types этим не пользуются. Встречаешь, когда мостишь во Foundation: NSString, NSData, UIImage. Классический косяк: обернуть случайный Swift-код в пул и ждать, что ARC изменится — или ни разу не обернуть цикл, который тысячу раз делает UIImage из Data.



```swift
func thumbnails(from data: [Data]) -> [UIImage] {
    data.compactMap { bytes in
        autoreleasepool {
            UIImage(data: bytes)
        }
    }
}
```


**Потом обычно спрашивают**

- Когда главный run loop сливает внешний пул?
- Почему для массива UInt8 это не тема, а для UIImage — да?
- Как в Allocations убедиться, что течёт именно пул?

</details>

<h2 id="weak-vs-unowned">weak и unowned</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Оба не трогают retain count, поэтому цикл из них не собрать. weak — optional, становится nil, когда объект умер: безопасно, если время жизни неизвестно. unowned — не optional: ты утверждаешь, что объект переживёт эту ссылку. Если нет — краш (unowned ловит trap; unowned(unsafe) — undefined).

weak берёшь на делегаты, на view controller в сетевых и анимационных колбэках, на всё, что может закрыться первым. unowned — когда связь структурная: ребёнок не существует без родителя, кредитная карта не живёт без клиента, замыкание живёт только пока ты владеешь self. Прочитал unowned после смерти владельца — процесс падает. Поэтому совет «всегда unowned self в замыканиях» — плохой.

Классические косяки: unowned на экран, который может исчезнуть до возврата async-колбэка; weak на структуру (не скомпилируется); считать их взаимозаменяемым способом заткнуть ворнинг.



```swift
protocol FormDelegate: AnyObject {
    func formDidSubmit()
}

final class Form {
    weak var delegate: FormDelegate?  // owner may go away
}

final class Field {
    unowned let form: Form            // Field is created by Form, dies with it
    init(form: Form) { self.form = form }
}
```


**Потом обычно спрашивают**

- Что будет, если прочитать unowned после того, как объект умер?
- Почему weak-свойство должно быть var и optional?
- Когда unowned(unsafe) вообще оправдан?

</details>

<h2 id="memory-leak">Найти и починить утечку памяти</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Утечка — память, которая осталась выделенной, хотя она уже никому не нужна. В Swift обычная причина — retain cycle. Три формы, которые хотят услышать по именам: два класса держат друг друга strong; strong-делегат (протокол назад к владельцу); сохранённое замыкание / Timer / Combine sink, которое захватило self, а self владеет этой работой.

В SwiftUI типичный сигнал — экран после pop так и не делает deinit: Task в onAppear, который сильно держит view model; синглтон или static-стор, который помнит последний экран; координатор UIViewRepresentable, который смотрит назад на self. Другие лики: безразмерный кэш, не отменённый Task, URLSession, который так и не довели до конца.

Доказываешь Instruments Allocations (график не возвращается к базе), инструментом Leaks, Memory Graph Debugger или deinit, который молчит после pop. Чинишь владение — weak / unowned, [weak self] — отменяешь работу в deinit или onDisappear, ставишь потолок кэшам.

На собесе хотят различение: цикл — одна форма утечки, «лик» — симптом. Не каждая утечка — два объекта, которые смотрят друг на друга.



```swift
final class Ticker {
    private var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            self?.tick()
        }
    }

    func stop() {
        timer?.invalidate()
        timer = nil
    }

    private func tick() {}

    deinit {
        stop()
        print("Ticker deinit")
    }
}
```


**Потом обычно спрашивают**

- Чем утечка отличается от retain cycle?
- «Публичный API не трогать» — какое слово всё равно можно добавить?
- Что говорит растущий график Allocations после серии push/pop?
- Почему синглтон может течь даже без цикла?
- Назови три самые частые формы retain cycle на iOS.
- Экран SwiftUI после pop не умирает — куда смотришь первым?
- На старте всё было нормально, через 15 минут тормозит — что накопилось?
- Leak vs zombie — какой инструмент что показывает?
- Утёкший ViewModel всё ещё подписан, синглтон-actor жмёт тап дважды. Какой инструмент покажет два экземпляра?
- Почему «Swift 6 компилируется чисто» не спасает, если счётчики экземпляров ползут вверх?

</details>

<h2 id="retain-cycle">Найти и разорвать retain cycle</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Retain cycle — петля strong-ссылок: A владеет B, B владеет A. Ни один счётчик не дойдёт до нуля, deinit не вызовется. На собесе три формы: родитель держит ребёнка, ребёнок держит родителя; strong-делегат; сохранённое замыкание (или Timer, Combine sink, Task), которое захватило self, а self владеет этой работой.

Ловишь это, когда после закрытия экрана deinit молчит, или Memory Graph Debugger рисует петлю. Рвёшь цикл: обратную ссылку делаешь weak или unowned, либо пишешь [weak self] и идёшь через optional chaining.

Классические косяки: навесить weak на всё подряд, так и не найдя петлю; взять unowned, когда объект может умереть первым; забыть, что Timer и NotificationCenter удерживают target.



```swift
final class ProfileLoader {
    var onFinish: (() -> Void)?
    var name = "Ada"

    func load() {
        onFinish = { [weak self] in
            print(self?.name ?? "gone")
        }
    }

    deinit { print("ProfileLoader deinit") }
}
```


**Потом обычно спрашивают**

- Почему одного [weak self] иногда мало?
- Когда в замыкании берёшь [unowned self]?
- Как поймать цикл, в котором нет замыкания?

</details>

<h2 id="deep-vs-shallow">Deep и shallow copy</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Shallow-копия дублирует контейнер и шарит элементы — те же identity объектов. Deep-копия дублирует граф: поменял ребёнка — оригинал не изменился. Array структур копирует значения (на этом уровне это deep). Array классов копирует массив, не объекты. copy у NSArray — shallow; NSArray из NSString всё равно шарит строки, и обычно это нормально, они иммутабельны. Типичный промах: array.map с теми же экземплярами классов и назвать это deep copy.



```swift
class Box { var n = 0 }
let a = [Box()]
let shallow = a // same Box
let deep = a.map { b in Box(); /* copy fields */ }
```


**Потом обычно спрашивают**

- copy и mutableCopy у NSArray?
- Как CoW меняет ответ для Array из Int?
- Когда копия должна быть deep ради потокобезопасности?

</details>

<h2 id="stack-vs-heap">Стек и куча</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Стек — черновик потока: кадры пушатся и снимаются по LIFO, когда функции входят и выходят. Там локальные и адреса возврата. Куча — общий пул процесса на динамическое время жизни: malloc и объекты ARC. Не говори «структуры на стеке, классы в куче». Экземпляр класса — в куче; структура может быть на стеке, заинлайнена в классе или промоутнута в кучу (escaping-замыкание, буфер Array). Объекты ObjC — объекты кучи. Типичный промах: путать stack-vs-heap с value vs reference.



```swift
func demo() {
    var n = 1              // typically stack
    let view = UIView()    // the UIView is on the heap; `view` is a stack pointer
}
```


**Потом обычно спрашивают**

- Почему большой Array может жить в куче, хотя Array — структура?
- Что происходит с памятью стека, когда функция вернулась?
- Как ARC связан только с объектами кучи?
- Где живёт свойство-структура у класса?

</details>

### Senior

<h2 id="side-tables">Side tables</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Экземпляр Swift-класса начинается как маленький объект в куче: указатель на метаданные плюс inline-refcount. В первый раз, когда нужна лишняя бухгалтерия — weak-ссылка, unowned-счётчик, который не влезает, или ObjC-interop — рантайм рядом кладёт side table. Weak-ссылки смотрят в эту таблицу, не в сам объект, поэтому после deinit могут стать nil и не висеть в воздухе. Поэтому weak медленнее и толще unowned: платишь за таблицу и лишний прыжок. На глубоком собесе хотят эту картинку, а не «weak — это optional». Side table сам не управляешь — просто понимаешь, почему тип, который всегда только unowned, дешевле.



```swift
final class Node {
    weak var parent: Node? // first weak ref can allocate a side table
    var child: Node?
}
```


**Потом обычно спрашивают**

- Почему unowned может обойтись без side table, а weak нет?
- Почему говорят, что weak медленнее strong?
- Что происходит с weak-ссылками во время deinit?
- Как это всплывёт в Allocations, если создать миллионы объектов с weak-указателями?

</details>
