# Combine

3 карточек · 2 часто спрашивают · [combine.md](../../topics/combine.md)

### Mid

<h2 id="combine">Combine и реактивное программирование</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Реактивный код моделирует значения во времени: Publisher шлёт события, оператор их превращает, подписчик делает работу. Combine — версия Apple; RxSwift старше и кроссплатформенный. Берёшь для поиска по мере набора, склейки двух сетевых вызовов, биндинга view model к UIKit. Выигрыш — композиция и отмена через AnyCancellable и store(in:). Цена — стек вызовов, который никто не читает, когда всё сломалось, плюс надо знать потоки: receive(on:). Swift concurrency закрывает много новой работы; Combine всё ещё живёт в старых приложениях и на собесах.

Классические косяки: забыть подписку и получить лик; трогать UI на потоке паблишера.



```swift
cancellable = NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
    .receive(on: RunLoop.main)
    .sink { _ in refresh() }
```


**Потом обычно спрашивают**

- Future / Promise против долгоживущего Publisher?
- Publisher, Subject и @Published — в чём разница?
- Как отменяешь и что будет, если забыть?
- Когда берёшь async/await вместо Combine?
- debounce и throttle на поисковой строке?
- Зачем [weak self] в sink и что меняет receive(on:)?

</details>

<h2 id="combine-operators">Как склеивать Publisher</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

combineLatest стреляет, когда сработал любой вход, и отдаёт последние значения каждого — форма, которой нужны и email, и пароль. zip склеивает события один к одному и ждёт более медленную сторону. merge смешивает потоки одного Output в один стрим. switchToLatest — часто после map на поиске — отменяет предыдущий внутренний Publisher, побеждает только последний запрос. flatMap запускает внутренние и даёт им пересекаться. Типичный промах: zip на двух @Published полях и удивление, почему кнопка после первой пары больше не оживает.



```swift
let canSubmit = email.combineLatest(password)
    .map { !$0.isEmpty && $1.count >= 8 }

query
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .map { api.search($0) }
    .switchToLatest()
```


**Потом обычно спрашивают**

- combineLatest, zip, merge — по одному предложению?
- Когда flatMap хуже switchToLatest?
- Куда ставишь receive(on: DispatchQueue.main)?
- Как напишешь debounce или throttle без Combine — какой таймер отменяешь?

</details>

<h2 id="combine-subjects">Subject в Combine</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Subject — это Publisher, в который ещё и сам можешь послать значение. PassthroughSubject текущего значения не держит: опоздавший подписчик прошлые события не увидит — тапы, разовые события. CurrentValueSubject всегда знает последнее и реплеит его — например isLoggedIn экрана. @Published — это CurrentValueSubject с проводкой SwiftUI/Combine. На границе API стираешь в AnyPublisher. Типичный промах: Passthrough для состояния, которое вью нужно уже в момент appear.



```swift
let taps = PassthroughSubject<Void, Never>()
let name = CurrentValueSubject<String, Never>("")
taps.send(())
name.send("Ada")
```


**Потом обычно спрашивают**

- Subject, @Published и AsyncStream?
- Зачем стирать в AnyPublisher?
- Что share() меняет у холодного Publisher?

</details>
