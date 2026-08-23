# Concurrency

27 карточек · 23 часто спрашивают · [concurrency.md](../../topics/concurrency.md)

### Junior

<h2 id="concurrency-vs-parallelism">Concurrency vs parallelism</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Concurrency** — чередование: много задач продвигаются, не обязательно в один миг. iOS-приложение конкурентно, когда пользователь скроллит, загрузка заканчивается и обрабатывается тап — одно ядро всё это умеет переключением. **Parallelism** — тот же миг на двух ядрах: два фильтра картинки, энкод видео. Хотят «отзывчивость vs пропускная способность». Concurrent-очереди GCD и async let *могут* бежать параллельно; concurrency они дают всегда. Типичный промах: «async значит два CPU» или называть каждую фоновую очередь «параллельной».



```swift
// Concurrent: main keeps scrolling while this suspends.
let data = try await URLSession.shared.data(from: url).0

// Parallel *if* the pool has two cores free:
async let a = decode(left)
async let b = decode(right)
let (l, r) = await (a, b)
```


**Потом обычно спрашивают**

- Бывает ли concurrency на одном ядре?
- Когда на iPhone реально нужен parallelism?
- Sync vs async — та же ось, что serial vs concurrent?

</details>

### Mid

<h2 id="main-actor">@MainActor</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

@MainActor — global actor: всё, что им помечено, бежит на main thread / очереди. View в UIKit и SwiftUI изолированы на MainActor. **DispatchQueue.main.async — прыжок на эту очередь; @MainActor — изоляция, которую понимает компилятор.** main.async не делает следующую строку безопасной для Sendable и не мешает потом тронуть UI из detached task. MainActor.run / await на методе MainActor — это прыжок, и он может не энкьюить, если ты уже изолирован (assumeIsolated). **Зачем main thread:** UIKit не потокобезопасен. Render server и UIWindow ждут мутации на main run loop; UI не на main — undefined (тиаринг, потерянные тачи, крэши). Изолировать весь класс значит: все методы на MainActor, пока не пометишь nonisolated. Типичные ошибки: считать DispatchQueue.main.async ответом Swift 6, Task.detached и потом трогать @State, или @MainActor на тяжёлом парсере — подвесишь UI. Изолируй UI-тип, не сетевой слой.



```swift
@MainActor
final class ProfileScreen {
    var name = ""

    func show(_ user: User) {
        name = user.name // main, safe for UI
    }
}

func fetch() async {
    let user = await api.user()
    await ProfileScreen().show(user)
}
```


**Потом обычно спрашивают**

- @MainActor на функции vs на типе — что наследуется?
- Когда MainActor.assumeIsolated?
- Как это заменяет DispatchQueue.main.async?
- Ты уже на main queue — hopнет ли MainActor.run?
- Почему обновления UIKit должны быть на main thread?
- Когда nonisolated законен на типе с @MainActor?
- Прыгает ли Task { } внутри метода @MainActor с main?
- Блокирует ли @MainActor main thread, пока ты await'ишь сеть?

</details>

<h2 id="actor-vs-serial-queue">Actor vs serial DispatchQueue</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Serial-очередь** — договорённость: трогаешь стейт только на этой очереди. Компилятор не помогает. **actor** — языковая изоляция: переход через границу это await, и Swift 6 откажется от несинхронизированного доступа. Actor реентерится на await; serial-очередь не уступает посреди блока, пока сам не запланируешь ещё работу. Actor складывается с async-функциями и отменой; очереди — с GCD и колбэками. Serial-очередь оставляй, когда сегодня надо звать синхронный API с многих тредов (C-библиотека, lock-free чтение кэша). Для новых модельных объектов начинай с actor. Типичная ошибка: обернуть каждую функцию в queue.async и потом sync'ом вытаскивать return с той же очереди.



```swift
actor SessionStore {
    private var token: String?

    func setToken(_ token: String) { self.token = token }

    func currentToken() -> String? { token }
}

// Older equivalent: private let queue = DispatchQueue(label: "session")
```


**Потом обычно спрашивают**

- Как отдать синхронное чтение из actor?
- Что такое reentrancy у actor и есть ли оно у serial-очереди?
- Когда nonisolated на методе actor?
- Кэш картинок: два load попали в один miss — как склеить после await?

</details>

<h2 id="async-sequence">AsyncSequence</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

AsyncSequence — это Sequence для значений, которые **приходят со временем**: for await x in stream. Обычные источники — URLSession.bytes, NotificationCenter.notifications и AsyncStream. Back-pressure и отмена приходят из конца цикла for await. Типичный промах: буферить безграничный continuation AsyncStream или блокировать внутри next().



```swift
for await note in NotificationCenter.default.notifications(named: .NSSystemTimeZoneDidChange) {
    refreshClocks()
}
```


**Потом обычно спрашивают**

- AsyncStream vs паблишер Combine?
- Что будет с циклом, когда Task отменили?
- Когда AsyncSequence не тот инструмент по сравнению с одним await?

</details>

<h2 id="checked-continuation">Checked continuations</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

withCheckedContinuation / withCheckedThrowingContinuation мостят callback API в async. Resume ровно **один раз**. Два resume — checked-вариант трапает в дебаге, unsafe — undefined. Не утекай continuation: если колбэк может не прийти, resume с ошибкой по timeout или onCancel. Так оборачивают URLSession.dataTask или делегат без async-оверлоада. Если есть настоящий async API (data(from:)) — бери его. Типичная ошибка: сильно захватить self в колбэке и не сделать resume на ошибочном пути.



```swift
func token() async throws -> String {
    try await withCheckedThrowingContinuation { cont in
        auth.renew { result in
            switch result {
            case .success(let value): cont.resume(returning: value)
            case .failure(let error): cont.resume(throwing: error)
            }
        }
    }
}
```


**Потом обычно спрашивают**

- Checked vs unsafe continuation — когда unsafe оправдан?
- Как хукнуть onCancel, чтобы остановить нижележащую работу?
- Почему не оборачивать так каждый паблишер Combine?

</details>

<h2 id="dispatch-group">DispatchGroup</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

DispatchGroup — **счётчик** «эти N async-джобов закончились». enter до работы, leave на каждом пути (включая ошибки), потом notify или wait. Бери, чтобы склеить несколько вызовов GCD / completion-handler, когда не можешь переписать их в async let. wait на main queue — зависон. Оставшихся участников не отменишь так, как throwing task group. Типичный промах: enter без leave на ошибочном пути — notify никогда не стрельнет.



```swift
let group = DispatchGroup()
for url in urls {
    group.enter()
    session.dataTask(with: url) { _, _, _ in
        defer { group.leave() }
        // handle data / error
    }.resume()
}
group.notify(queue: .main) { table.reloadData() }
```


**Потом обычно спрашивают**

- notify vs wait — что легально на main?
- Как оборвать остальных, если одна загрузка упала?
- Чем это заменяют в Swift concurrency?

</details>

<h2 id="dispatch-semaphore">DispatchSemaphore</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

DispatchSemaphore — **счётчик разрешений**. wait уменьшает (блокирует на 0); signal увеличивает. Бери, чтобы ограничить конкурентную *блокирующую* работу — два файловых хэндла, легаси SDK. Это не мьютекс (нет владельца, легко пересигналить) и ловушка в Swift concurrency: wait на треде Task морит кооперативный пул. Лучше task group со скользящим окном или AsyncStream плюс счётчик. Типичный промах: wait на main или семафор на 1 как единственная «потокобезопасность», пока внутри критической секции всё ещё прыгаешь по очередям.



```swift
final class Gate {
    private let sem = DispatchSemaphore(value: 2)

    func limited(_ work: () -> Void) {
        sem.wait()
        defer { sem.signal() }
        work()
    }
}
```


**Потом обычно спрашивают**

- Семафор vs serial-очередь vs actor — какую задачу решает каждый?
- Почему wait внутри Task { } — риск thread explosion?
- Как рейт-лимитить URLSession без семафора?

</details>

<h2 id="gcd">GCD</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Grand Central Dispatch — рантайм очередей за DispatchQueue. Очереди **serial** (один блок за раз) или **concurrent** (много). async планирует работу и возвращается; sync блокирует вызывающего, пока работа не закончится — sync на serial-очереди, на которой ты уже стоишь, это дедлок. DispatchQueue.main — для UI. DispatchQueue.global(qos:) — fire-and-forget. Приватная serial-очередь — обычный способ защитить мутабельный стейт. **DispatchGroup** даёт дождаться нескольких async-джобов (enter / leave / notify). **Barrier** на concurrent-очереди ждёт текущие чтения, потом гоняет эксклюзивные записи — классический reader-writer кэш. Quality of Service — подсказка планировщику, не лок приоритета. Work item в GCD не отменяется так, как Task. Новый код по умолчанию — async / await и actor. На собеседовании всё ещё хотят sync vs async, serial vs concurrent, правило main thread и пример дедлока.



```swift
let lockQueue = DispatchQueue(label: "com.app.state")

func updateTitle(_ text: String) {
    lockQueue.async {
        DispatchQueue.main.async {
            self.label.text = text
        }
    }
}

// Deadlock if this runs on the main queue:
// DispatchQueue.main.sync { print("never") }
```


**Потом обычно спрашивают**

- Serial vs concurrent очередь — куда кладёшь barrier?
- Как QoS в GCD стыкуется с приоритетом Task?
- Reader-writer: много async-чтений, одна запись async(flags: .barrier)?
- OperationQueue vs GCD — когда нужны зависимости и отмена?
- Чем в Swift concurrency заменяют приватную serial-очередь?
- Как дождаться N загрузок картинок через DispatchGroup?
- Почему ставить label.text с global-очереди — баг и как чинить?
- concurrentPerform vs for на concurrent-очереди?
- asyncAfter — это точная задержка?

</details>

<h2 id="gcd-vs-operationqueue">GCD vs OperationQueue</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**GCD** планирует замыкания на очередях. Это дефолт для «убери с main thread» и для приватного serial-лока. **OperationQueue** оборачивает работу в объекты Operation: зависимости (addDependency), отмена, которую можно проверить, max concurrent operation count и KVO на isFinished. maxConcurrentOperationCount = 1 — когда спрашивают, как гонять API-вызовы **сериально** на operation queue; та же идея, что приватный serial DispatchQueue. Операции — когда пайплайн «декод, потом аплоад, отмени аплоад, если пользователь ушёл». Группы GCD умеют ждать пачку, но DAG именованных шагов моделируют хуже. Новый Swift concurrency (Task, TaskGroup) закрывает многое из того, для чего брали операции. Типичная ошибка: писать кастомный Operation, чтобы один раз вызвать async.



```swift
let decode = BlockOperation { decodeOnDisk() }
let upload = BlockOperation { uploadFile() }
upload.addDependency(decode)
upload.completionBlock = { print("done or cancelled") }

let queue = OperationQueue()
queue.maxConcurrentOperationCount = 2
queue.addOperations([decode, upload], waitUntilFinished: false)
```


**Потом обычно спрашивают**

- Как отменить Operation, который уже бежит?
- Блоки / GCD vs NSOperation — когда лишний тип стоит того?
- Что меняет isAsynchronous = true?
- Когда всё ещё возьмёшь GCD, а не OperationQueue?
- Как заставить OperationQueue гонять по одному запросу?

</details>

<h2 id="gcd-vs-async-await">GCD vs async/await</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

GCD — **неструктурированные очереди**: async'нул блок и потерял родителя. Нет автоматической отмены, нет throws из блока, легко словить thread explosion, если эти блоки *блокируют*. async / await — **structured concurrency**, задачи на кооперативном пуле: дети наследуют приоритет и отмену, ошибки идут через await, саспенд не держит тред. GCD всё ещё выигрывает как крошечный serial-лок, barrier-кэш или код, который обязан остаться синхронным. Новая фича — Task и actor. Типичный промах: «async/await — просто красивее GCD».



```swift
// GCD — caller cannot cancel or throw through this.
DispatchQueue.global().async {
    let data = try? Data(contentsOf: url)
    DispatchQueue.main.async { self.image = UIImage(data: data ?? Data()) }
}

// Structured — cancel the parent, this work should stop.
func load() async throws -> UIImage {
    let (data, _) = try await URLSession.shared.data(from: url)
    return UIImage(data: data) ?? UIImage()
}
```


**Потом обычно спрашивают**

- Что наследует дочерний Task, чего нет у блока GCD?
- Когда приватная serial-очередь всё ещё честный инструмент?
- Как мигрировать completion-handler API, не оборачивая каждый вызов в Task { }?
- Как мигрировать большой GCD-кодбейз — по модулю или flag day?

</details>

<h2 id="qos">Quality of Service</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

QoS — **подсказка планировщику** для GCD / ядра: .userInteractive (тач → кадр), .userInitiated (пользователь ждёт), .utility (прогресс-бар), .background (синк, уборка), .default / .unspecified. Это не лок и не гарантия. Элемент .background всё равно может бежать на main thread, если ты целился в DispatchQueue.main. Приоритет Task — двоюродный брат в Swift. Типичный промах: декод картинки на .userInteractive и дёрганый скролл или ждать, что QoS починит data race.



```swift
DispatchQueue.global(qos: .userInitiated).async {
    let image = decode(data)
    DispatchQueue.main.async { view.image = image }
}
```


**Потом обычно спрашивают**

- Как QoS стыкуется с приоритетом Task?
- Priority inversion одним предложением?
- Почему .background — неправильная очередь для обработчика кнопки?
- Как злоупотребление .userInteractive бьёт по батарее и другим приложениям?

</details>

<h2 id="sendable">Sendable</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Sendable значит: значение безопасно передать через домены concurrency — в Task, в actor, прочь с MainActor. Структуры из Sendable stored-свойств могут стать Sendable сами. Классы — нет, пока они иммутабельны и final, или ты их изолируешь (@MainActor, actor). Complete checking в Swift 6 откажется передавать не-Sendable класс в detached task. @unchecked Sendable — люк, который надо обосновать (держишь лок). Типичная ошибка: пометить мутабельный класс @unchecked Sendable, чтобы заткнуть ворнинги (ImageCache с голым [URL: UIImage] — классическая ложь), или обернуть var-массив классов и решить, что обёртка-структура сделала его безопасным.



```swift
struct User: Sendable {
    let id: UUID
    let name: String
}

final class UnsafeCache {
    var items: [String] = []
}

// Task.detached { print(UnsafeCache().items) } // not Sendable
```


**Потом обычно спрашивают**

- Почему actor неявно Sendable?
- Когда @unchecked Sendable честный, а когда ложь?
- Как отправить UIKit-тип прочь с MainActor?
- Замыкание @Sendable vs тип Sendable — что каждый обещает?
- Мутабельный класс в фоновый Task — структура, actor или final + let?

</details>

<h2 id="taskgroup-vs-async-let">Task group vs async let</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**async let** — для **фиксированного** набора дочерних Task, который знаешь на этапе компиляции: два фетча, потом await (a, b). Это structured concurrency, отменяется со скоупом, читается чисто. **Task group** — для **динамического** числа: N URL, ранний выход когда один упал, или стриминг результатов по мере готовности. В группе addTask в цикле и for await частичных результатов. Не собирай группу ради двух захардкоженных вызовов — для этого async let. Не плоди неструктурированный Task на каждый элемент for и не надейся, что сам их смэтчишь. Типичная ошибка: async let внутри цикла по пользовательским данным; так не компилируется, как ждут, инструмент — группа.



```swift
func profile() async throws -> (User, [Post]) {
    async let user = api.user()
    async let posts = api.posts()
    return try await (user, posts)
}
```


**Потом обычно спрашивают**

- Как отменить оставшуюся работу группы после первой ошибки?
- Могут ли дети async let бежать параллельно? Что их стартует?
- Когда ThrowingTaskGroup, а когда ручной массив Task?
- Как повесить timeout на один await без сторонней библиотеки?
- Результаты группы приходят в порядке add? Как восстановить порядок?
- Throwing-группа vs TaskGroup<Result<T, Error>> — всё или ничего vs частичный UI?
- Как ограничить группу N одновременными аплоадами?

</details>

<h2 id="task-detached-taskgroup">Task vs Task.detached vs TaskGroup</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Task { }** — неструктурированная работа, которая **наследует** изоляцию actor, приоритет и task-local значения из контекста создания. Поэтому Task { await load() } внутри View с @MainActor остаётся на MainActor, пока сам не прыгнешь. **Task.detached** почти ничего не наследует — для CPU-работы, которую не хочешь на actor вызывающего, значения передавай явно. **TaskGroup / throwingTaskGroup** — structured concurrency: родитель await'ит каждого ребёнка, отмена идёт вниз, детей добавляешь динамически. Предпочитай structured concurrency (async let, task group), чтобы работа не пережила скоуп. Типичная ошибка: Task.detached из View на сеть, потом трогать @State без возврата.



```swift
func thumbnails(for urls: [URL]) async -> [URL: Data] {
    await withTaskGroup(of: (URL, Data?).self) { group in
        for url in urls {
            group.addTask { (url, try? await fetch(url)) }
        }
        var result: [URL: Data] = [:]
        for await (url, data) in group {
            if let data { result[url] = data }
        }
        return result
    }
}
```


**Потом обычно спрашивают**

- Что наследует Task, созданный в .task у SwiftUI?
- Когда Task.detached — плохой дефолт?
- Как отмена родителя бьёт по детям группы?
- Что утечёт, если стартовать Task { } во View и не отменить на disappear?
- Task.sleep vs Thread.sleep — что блокирует тред?
- Почему Task { } внутри уже async-функции — баг structured concurrency?

</details>

<h2 id="main-async-vs-sync">main.async vs main.sync</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

DispatchQueue.main.async кладёт работу в очередь и возвращается. Это обычный прыжок на main thread для UI. DispatchQueue.main.sync **блокирует вызывающего**, пока блок не закончится. Если вызывающий уже на main queue, sync ждёт, пока очередь доделает текущий элемент — а это и есть сам sync — и приложение дедлочится. Вложенный main.async нормален — оба блока всё равно на main. С фоновой очереди sync легален, но морозит воркера, пока main run loop не обслужит блок. sync на *другую* очередь часто **оставляет вызывающий тред**, чтобы не прыгать: otherQueue.sync { Thread.isMainThread } с main может всё ещё напечатать true. Лучше async или await MainActor.run. Типичная ошибка: «мне результат прямо сейчас» — и sync из колбэка table view, который уже на main.



```swift
func applyTitle(_ text: String) {
    if Thread.isMainThread {
        label.text = text
        return
    }
    DispatchQueue.main.async { [weak self] in
        self?.label.text = text
    }
}
```


**Потом обычно спрашивают**

- Почему MainActor.assumeIsolated иногда безопаснее, чем гадать по Thread.isMainThread?
- Что будет, если sync на main с очереди делегата URLSession?
- Чем await MainActor.run отличается от DispatchQueue.main.async?
- Почему otherQueue.sync с main всё ещё может напечатать Thread.isMainThread == true?
- Почему main.async { main.sync { … } } никогда не выполнит внутренний блок?
- Вложенные global().async + main.async — что напечатается первым и почему это не детерминировано?

</details>

<h2 id="locks">Локи</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Лок делает критическую секцию эксклюзивной. **os_unfair_lock** — дешёвый современный мьютекс (не рекурсивный); его identity — **адрес**, копия структуры его ломает; аллоцируй на куче или бери **OSAllocatedUnfairLock** (iOS 16+). **NSLock** — обёртка Foundation, тоже не рекурсивный, честнее под конкуренцией. **NSRecursiveLock** даёт тому же треду залочиться снова — удобно, легко спрятать баг реентерабельности. **pthread_mutex** — C-версия. **Семафор** (DispatchSemaphore) — счётчик, не мьютекс; wait / signal как лок из async-кода — фабрика дедлоков. Лучше **actor** или serial-очередь, пока не нужно синхронное чтение на треде вызывающего (configure ячейки, C-колбэк). Типичные ошибки: залочиться и потом await (лок с Task не прыгает) и забыть unlock на ошибочном пути — defer { lock.unlock() }.



```swift
final class Counter {
    private var lock = os_unfair_lock_s()
    private var value = 0

    func increment() {
        os_unfair_lock_lock(&lock)
        defer { os_unfair_lock_unlock(&lock) }
        value += 1
    }
}
```


**Потом обычно спрашивают**

- Почему нельзя await, держа лок?
- Unfair lock vs recursive lock vs serial-очередь?
- Как это стыкуется с @MainActor для UI-стейта?
- Семафор vs мьютекс vs лок — что считает разрешения?
- Почему stored os_unfair_lock на структуре — ловушка?

</details>

<h2 id="task-cancellation">Отмена Task</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Отмена **кооперативная**. task.cancel() ставит флаг, CPU не абортит. Проверяешь Task.isCancelled или зовёшь Task.checkCancellation() (кидает CancellationError). Async API URLSession и Task.sleep это чтят. Структурированных детей отменяют вместе с родителем. Task { }, который выстрелил и забыл, продолжит бежать, пока не сохранишь и не отменишь или не привяжешь к .task / скоупу. Типичная ошибка: defer { }, который не останавливает URLSessionTask, или игнор отмены в длинном for — закрытый экран продолжает качать.



```swift
func loadAll(_ urls: [URL]) async throws -> [Data] {
    var result: [Data] = []
    for url in urls {
        try Task.checkCancellation()
        result.append(try await URLSession.shared.data(from: url).0)
    }
    return result
}
```


**Потом обычно спрашивают**

- Что отменяет .task в SwiftUI, когда View пропадает?
- Как отменить withCheckedContinuation, который обернул callback API?
- Почему отмена — не замена timeout?
- Debounce-поиск: отменил предыдущий Task — что всё ещё гоняется, если пропустить isCancelled?
- Повторяющийся Timer + Task { self } — кто держит ViewModel живым?

</details>

<h2 id="thread-safe-state">Потокобезопасный общий стейт</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Начни с гонки: две очереди мутируют одни и те же свойства класса. Потом выбери инструмент. **Serial-очередь** (или barrier на concurrent) — ответ GCD. **NSLock / os_unfair_lock** дешевле и проще словить дедлок. **Семафор** — счётчик разрешений, не мьютекс. Лучше **actor**: компилятор сериализует доступ, await вместо танца с локами. Value types плюс copy-on-write не шарят память, если внутрь не протащить класс. Не сыпь DispatchQueue.main.async как «фикс» модельного стейта — это только легализует обновления UI. Хотят один конкретный выбор и почему, не список API.



```swift
actor ImageStore {
    private var cache: [URL: Data] = [:]

    func data(for url: URL) -> Data? { cache[url] }

    func store(_ data: Data, for url: URL) {
        cache[url] = data
    }
}
```


**Потом обычно спрашивают**

- Когда лок лучше actor?
- Почему nonisolated(unsafe) — крайняя мера?
- Как защитить кэш, который надо читать синхронно из configure ячейки?

</details>

<h2 id="concurrency-problems">Проблемы concurrency</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Назови сбой, потом фикс. **Data race** — несинхронизированные чтение и запись одной памяти; Swift 6 при complete checking делает это ошибкой компиляции. **Race condition** — логический баг: оба порядка событий «валидны», но один неверный (check-then-act). **Deadlock** — двое ждут то, что держит другой; классика iOS — DispatchQueue.main.sync с main thread. **Priority inversion** — низкоприоритетный держатель блокирует высокоприоритетного ждущего; наследование QoS и actor это смягчают. **Reentrancy у actor** — не гонка: await внутри actor пускает другие Task, инварианты могут измениться через точку саспенда. Хотят правильное слово, не «баг с тредами».



```swift
actor Counter {
    private var value = 0

    func bumpIfPositive() async {
        guard value > 0 else { return }
        await Task.yield() // other tasks can enter here
        value += 1         // value may no longer be > 0
    }
}
```


**Потом обычно спрашивают**

- Data race vs race condition — по одному предложению?
- Как complete concurrency checking в Swift 6 меняет ответ на собесе?
- Практичный фикс reentrancy у actor — проверить снова после await?
- Deadlock vs livelock — по одному предложению?
- Как поймать data race в Xcode (Thread Sanitizer)?
- «Reentrancy очереди» в GCD (sync на той же serial-очереди) vs reentrancy у actor — что дедлочится?
- Дают висящий проект в Xcode — первый шаг отличить deadlock от data race?

</details>

<h2 id="dispatch-work-item">DispatchWorkItem</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

DispatchWorkItem — блок GCD, который можно **отменить**, нотифаить или дождаться. Уже бегущую работу всё равно не остановишь — isCancelled это флаг, который надо проверять. В новом коде лучше Task + Task.checkCancellation(). Типичный промах: item.cancel() и уверенность, что загрузка оборвалась.



```swift
let item = DispatchWorkItem { decode() }
queue.async(execute: item)
item.notify(queue: .main) { table.reloadData() }
item.cancel()
```


**Потом обычно спрашивают**

- Cancel vs Task, который реально рвёт I/O?
- notify vs DispatchGroup?
- Почему это слабее зависимостей Operation?

</details>

<h2 id="async-timeout">Timeout на await</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

У самого await таймаута нет. Гоняешь работу против слипера: try await withThrowingTaskGroup — добавь настоящую задачу, добавь Task.sleep, верни первый результат, остальное отмени. Или оберни URLSession через timeoutIntervalForRequest. Timeout обязан **отменить** проигравшего, иначе утечёт запрос. Типичный промах: DispatchQueue.asyncAfter вокруг await или спать на MainActor.



```swift
func withTimeout<T>(seconds: Double, _ work: @escaping @Sendable () async throws -> T) async throws -> T {
    try await withThrowingTaskGroup(of: T.self) { group in
        group.addTask { try await work() }
        group.addTask {
            try await Task.sleep(for: .seconds(seconds))
            throw CancellationError()
        }
        let value = try await group.next()!
        group.cancelAll()
        return value
    }
}
```


**Потом обычно спрашивают**

- Почему после первого финиша надо cancelAll?
- Таймаут сессии vs своя гонка — что реально глушит сокет?
- Как отличить «timed out» от настоящего CancellationError от пользователя?

</details>

<h2 id="deinit-thread">На каком треде бежит deinit</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

deinit бежит на том треде, который уронил последнюю strong-ссылку. Очереди «для deinit» нет. Если объект отпустил колбэк URLSession с фона, deinit будет там — трогать UIKit из такого deinit это крэш. Isolated deinit у actor (Swift 5.10+) перед разборкой перепрыгивает на actor. Типы с @MainActor всё равно требуют осторожности: если последний релиз случился не на main, не считай что ты на main, пока isolation этого не говорит. Типичная ошибка: стартовать таймер или сеть в deinit или считать, что он парный с init на том же треде.



```swift
final class Token {
    deinit {
        // May not be main. Hop if you must talk to UI.
        print(Thread.isMainThread)
    }
}

Task.detached {
    var token: Token? = Token()
    token = nil
}
```


**Потом обычно спрашивают**

- Как прыгнуть на MainActor из deinit, не захватив self?
- Что изменил isolated deinit?
- Почему I/O в deinit — плохая идея?

</details>

### Senior

<h2 id="actor-reentrancy">Reentrancy у actor</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Actor гоняет **одну Task за раз**, но это не мьютекс вокруг всего метода. На каждом await actor **саспендится** и может прогнать другого вызывающего, пока первый не возобновится. Это **reentrancy**. После await load() твой cache[url] уже мог заполнить — или почистить — второй load. Блок serial DispatchQueue.async посредине не уступает, пока сам не запланируешь ещё работу. Хотят фикс: проверить стейт снова после await, склеить in-flight работу ([URL: Task]) или держать критическую секцию без саспенда. Типичный промах: «у actor не бывает гонок» — и потом портить словарь через два await.



```swift
actor ImageLoader {
    private var cache: [URL: UIImage] = [:]
    private var inflight: [URL: Task<UIImage, Error>] = [:]

    func image(for url: URL) async throws -> UIImage {
        if let hit = cache[url] { return hit }
        if let task = inflight[url] { return try await task.value }
        let task = Task { try await download(url) }
        inflight[url] = task
        defer { inflight[url] = nil }
        let image = try await task.value
        cache[url] = image
        return image
    }
}
```


**Потом обычно спрашивают**

- Почему serial-очередь *не* реентерится так же?
- Как склеить два тапа, которые стартуют одну загрузку?
- nonisolated на чтении кэша — от чего ты только что отказался?
- Data race vs race condition — что actor *не* останавливает?
- Утекший ViewModel и живой оба бьют в singleton actor — крэш или две вежливые покупки?
- После await pay() почему надо перечитать сток?

</details>

<h2 id="thread-explosion">Thread explosion</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Пул GCD **растёт**, когда тред блокируется (sync, wait семафора, длинный CPU-цикл, который не возвращается). Сотни заблокированных воркеров, у каждого стек ~512 KB — система трэшится. Swift concurrency использует **кооперативный** пул размером примерно с число ядер: await *отдаёт* тред. Блокировка внутри Task (локи, Thread.sleep, синхронное чтение файла) возвращает взрыв. Хотят «саспенд ≠ блок». Типичный промах: DispatchQueue.global().async на каждую ячейку таблицы из 200 строк или semaphore.wait() на кооперативном пуле.



```swift
// Explosion risk: each wait occupies a GCD thread.
let sem = DispatchSemaphore(value: 2)
(0..<200).forEach { _ in
    DispatchQueue.global().async {
        sem.wait()
        fetchBlocking()
        sem.signal()
    }
}

// Cooperative: 200 tasks, a handful of threads.
await withTaskGroup(of: Void.self) { group in
    for _ in 0..<200 { group.addTask { await fetch() } }
}
```


**Потом обычно спрашивают**

- Почему Thread.sleep внутри Task больнее, чем Task.sleep?
- Как ограничить in-flight работу без семафора на кооперативном пуле?
- Как выглядит Thread State в Instruments во время взрыва?

</details>

<h2 id="isolation">Домены изоляции</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Домен изоляции** — кто имеет право трогать кусок памяти. Проверки data race в Swift 6 это «перешло ли значение домен, не будучи Sendable?». Домены, которые называют на собесе: **инстанс actor** (его изолированные методы), **global actor** (@MainActor или свой @SomeActor) и **nonisolated** код (кооперативный пул тредов или nonisolated-член, который не должен трогать изолированный стейт). @MainActor — global actor, прибитый к main executor, то есть UI. Свой actor — свой serial executor, не на main, для кэша или стора. nonisolated на члене actor — обещание, что он использует только sendable / иммутабельные данные. Типичный промах: «повесил @MainActor на всё, значит я изолирован» — это один домен, и ты только что сериализовал приложение на UI-треде.



```swift
@globalActor
actor DBActor { static let shared = DBActor() }

@DBActor
func save(_ row: String) { /* off-main, isolated */ }

@MainActor
func show(_ row: String) { /* UI */ }
```


**Потом обычно спрашивают**

- Что может читать nonisolated-метод actor?
- Когда свой global actor лучше, чем @MainActor на сторе?
- Чем sending на границе отличается от пометки типа Sendable?
- Создаёт ли Task изоляцию или *несёт* изоляцию места создания?

</details>

<h2 id="swift-6-concurrency">Строгая concurrency в Swift 6</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swift 6 делает проверки data race **ошибками**: переход через домен изоляции с не-Sendable значением, трогание стейта @MainActor из фоновой Task, захват self в замыкании @Sendable, которое прыгает. Ментальная модель — **изоляция** (кто может трогать эту память) плюс **Sendable** (что может путешествовать). Миграция поэтапная: включи complete checking на одном таргете, почини границу (@MainActor на UI-типе, actor на сторе, sending / копии на краю), потом следующий таргет. @unchecked Sendable и nonisolated(unsafe) затыкают компилятор — мутабельный класс от этого безопасным не становится. Типичный промах: переключить language mode одним PR и «починить» 400 ворнингов через @unchecked.



```swift
@MainActor
final class FeedViewModel {
    var titles: [String] = []

    func refresh() async {
        let rows = await Self.fetch() // hops off main, then back
        titles = rows
    }

    nonisolated static func fetch() async -> [String] { ["a"] }
}
```


**Потом обычно спрашивают**

- Complete checking vs minimal — что ещё компилируется в режиме Swift 5?
- Когда @unchecked Sendable честный?
- Что меняет «approachable concurrency» в Swift 6.2 про дефолтную изоляцию?
- @MainActor vs свой actor — какой домен изоляции какой?
- Когда @preconcurrency import — мост миграции, а когда вечная ложь?

</details>

<h2 id="global-actor">Global actors</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Global actor** — один общий домен изоляции на целую подсистему; @MainActor — тот, которым ты уже пользуешься. Объявляешь @globalActor enum PreferencesActor с shared-инстансом actor; типы и функции с @PreferencesActor сериализуются на этом executor. Бери, когда много объектов должны делить **один** ресурс (defaults, файл, соединение с БД) и хочешь, чтобы компилятор вставлял await на границе. Инстанс actor достаточен, когда у каждого кэша свой лок. Типичный промах: повесить один и тот же global actor на несвязанную работу и получить скрытую очередь на всё приложение — или голый DispatchQueue и забыть один sync.



```swift
@globalActor
enum PreferencesActor {
    actor ActorType {}
    static let shared = ActorType()
}

@PreferencesActor
final class PreferencesStore {
    func set(_ v: Int) { UserDefaults.standard.set(v, forKey: "seen") }
}
```


**Потом обычно спрашивают**

- Почему @MainActor — global actor, а не «API main thread»?
- Когда брать инстанс actor вместо этого?
- Что будет, если два global actor оба обернут UserDefaults?

</details>
