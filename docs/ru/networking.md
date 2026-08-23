# Сеть

18 карточек · 11 часто спрашивают · [networking.md](../../topics/networking.md)

### Junior

<h2 id="http-methods">HTTP-методы</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

GET читает и должен быть safe и идемпотентным — без побочек в теле. POST создаёт или запускает работу; повтор может дать две строки. PUT заменяет ресурс по известному URL и идемпотентен. PATCH — частичное обновление. DELETE удаляет. HEAD — GET без тела, проба. На собесе хотят, какой метод поставишь на «лайк твита» — обычно POST — и почему ретрай PUT безопаснее POST. Типичный промах: GET с телом или POST на выборку, «потому что так сделал чувак с API».



```swift
var like = URLRequest(url: url)
like.httpMethod = "POST"
var replace = URLRequest(url: url)
replace.httpMethod = "PUT"
```


**Потом обычно спрашивают**

- REST и GraphQL на мобильном клиенте — что реально меняется?
- Идемпотентный и safe — какие методы какие?
- Почему второй тап по POST опасен?
- Когда PATCH хуже PUT?

</details>

<h2 id="http-status">HTTP-статусы</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

На собесе хотят семейства, не заученную таблицу. 2xx — успех: 200 OK, 201 created, 204 без тела. 3xx — редирект и 304 not modified для кэша. 4xx — твой запрос: 400 плохой, 401 auth, 403 forbidden, 404 нет, 409 конфликт, 429 лимит. 5xx — их вина: ретрай с backoff, не тесный цикл. Не считай любой не-200 «ошибкой сети». Типичный промах: показать «нет интернета» на 401.



```swift
guard let http = response as? HTTPURLResponse else { throw URLError(.badServerResponse) }
switch http.statusCode {
case 200..<300: break
case 401: throw AuthError.expired
case 429: throw AuthError.throttled
default: throw URLError(.badServerResponse)
}
```


**Потом обычно спрашивают**

- 401 и 403?
- Какие коды безопасно ретраить?
- Как 304 живёт с URLCache?

</details>

<h2 id="json">JSON</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

JSON — текстовый формат: объекты, массивы, строки, числа, булевы, null. На iOS декодируешь JSONDecoder и Codable, не JSONSerialization — если только форма неизвестна. Плюсы: меньше XML, универсальный, удобно смотреть в Charles. Минусы: нет комментариев, даты не first-class (выбираешь стратегию), неизвестные ключи легко молча выкинуть, один огромный документ неудобно стримить. Типичный промах: «JSON — это тип Swift» или запихнуть комментарий в пейлоад.



```swift
struct Tweet: Decodable { var id: String; var text: String }
let tweets = try JSONDecoder().decode([Tweet].self, from: data)
```


**Потом обычно спрашивают**

- JSON, plist и protobuf в проводе?
- Как обрабатываешь поле с датой?
- Во что JSONSerialization превращает NSNull?

</details>

<h2 id="notification-center">NotificationCenter</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NotificationCenter — шина pub/sub внутри процесса, не сетевой API. Постишь Notification.Name; наблюдатели получают на том же потоке, если не указал очередь. Берёшь для рассылки, которая может быть интересна многим несвязанным объектам: клавиатура, логаут, accountDidChange. Не подменяй им делегат, колбэк или AsyncStream между двумя типами, которые и так друг друга знают. Block-based addObserver возвращает токен — его держишь; бросаешь токен или removeObserver, когда слушатель должен умереть.

Типичные баги: пост не с main и трогаешь UI; утекающие наблюдатели; столкновение на сырой строке имени.



```swift
extension Notification.Name {
    static let accountDidChange = Notification.Name("accountDidChange")
}

let token = NotificationCenter.default.addObserver(
    forName: .accountDidChange,
    object: nil,
    queue: .main
) { _ in
    // refresh UI
}

NotificationCenter.default.post(name: .accountDidChange, object: nil)
```


**Потом обычно спрашивают**

- Combine NotificationCenter.Publisher и сохранённый токен наблюдателя — кто отменяет?
- На каком потоке доставит post, если queue nil?
- Когда лучше делегат или AsyncStream?

</details>

<h2 id="url-vs-urlrequest">URL и URLRequest</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

URL — адрес. URLRequest — запрос, который вот-вот пошлёшь: этот URL плюс метод, заголовки, тело, cache policy, таймаут. URLSession.data(from:) хватает на GET. Всё остальное — POST, Authorization, своя cache policy — нужен URLRequest. URLComponents — как собрать URL, не склеивая query руками. Типичный промах: склеить строку с query и удивляться, почему пробелы ломают запрос.



```swift
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
request.httpBody = try JSONEncoder().encode(payload)
let (data, _) = try await URLSession.shared.data(for: request)
```


**Потом обычно спрашивают**

- URL, URLComponents и сырая строка?
- Когда cachePolicy ставишь на запрос, а когда на сессию?
- Как прицепить bearer-токен и не залогировать его?

</details>

<h2 id="network-request">Сетевой запрос</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

URLSession — системный HTTP-клиент. Собираешь URL или URLRequest, вызываешь data(from:) или старый dataTask, смотришь HTTP-статус, декодируешь тело. Для нового кода — async/await; completion-handler всё равно должен уметь написать. URLSession.shared хватает на простой GET; свой URLSessionConfiguration — на таймауты, кэш и background-сессии. Завершённая задача — ещё не успех: читай statusCode у HTTPURLResponse.

Типичные промахи: забыть про ATS, без нужды декодировать JSON на main actor, залить delegate-сессию, так и не вызвав finishTasksAndInvalidate.



```swift
func loadUsers() async throws -> [User] {
    let url = URL(string: "https://example.com/users")!
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
        throw URLError(.badServerResponse)
    }
    return try JSONDecoder().decode([User].self, from: data)
}
```


**Потом обычно спрашивают**

- URLSession.shared и своя сессия — когда своя?
- Как послать JSON POST с заголовком?
- Что меняет background URLSession в колбэках?
- Где декодировать: очередь делегата сессии, Task или main actor?

</details>

<h2 id="local-notifications">Локальные и удалённые уведомления</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Remote push — сервер, APNs, устройство. Local уведомления планируешь на девайсе через UNUserNotificationCenter: календарь, интервал или гео. Обоим нужно одно и то же разрешение пользователя на видимый баннер, оба могут deep-link по тапу. Local не нужен device token, бэкенд и сеть. Local — «напомни через 20 минут» и «ты давно не трогал»; remote — когда момент решает другая система: пришло сообщение, такси через две минуты. Типичный промах: запланировать local и назвать это пушем, или ждать, что триггер сработает после force-quit, если разрешение так и не просил.



```swift
let content = UNMutableNotificationContent()
content.title = "Stand up"
content.body = "20 minutes since the last break"

let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 20 * 60, repeats: false)
let request = UNNotificationRequest(identifier: "stand-up", content: content, trigger: trigger)
try await UNUserNotificationCenter.current().add(request)
```


**Потом обычно спрашивают**

- Какое разрешение всё равно нужно для локального баннера?
- Как отменить один pending local, не вычищая остальные?
- Silent remote и локальный time trigger — кто может разбудить suspended-приложение?

</details>

<h2 id="web-content">Показать веб-контент</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

HTML внутри приложения — WKWebView из WebKit. UIWebView мёртв и ревью не пройдёт. Если нужны куки Safari, reader view и приватный UI без своего браузера — показывай SFSafariViewController. Link в SwiftUI отдаёт URL в Safari; WKWebView оборачиваешь в UIViewRepresentable, когда надо остаться в приложении. Грузишь URLRequest или HTML-строку; JavaScript инжектишь только если страница сама не справляется. На собесе хотят развилку: WKWebView — контроль, SFSafariViewController — Safari-хром внутри приложения, обычный https — уйти из приложения.



```swift
import SafariServices
import WebKit

let webView = WKWebView(frame: .zero)
webView.load(URLRequest(url: URL(string: "https://example.com")!))

let safari = SFSafariViewController(url: URL(string: "https://example.com")!)
present(safari, animated: true)
```


**Потом обычно спрашивают**

- Почему для OAuth и чужих страниц берут SFSafariViewController?
- Как загрузить локальный HTML из бандла в WKWebView?
- Зачем WKWebsiteDataStore?

</details>

### Mid

<h2 id="push-notifications">Push-уведомления</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Удалённый пуш — твой сервер, потом APNs, потом устройство. Просишь разрешение, затем registerForRemoteNotifications — на каждом запуске, потому что токен крутится: restore, новый девайс, рефреш APNs. Hex из Data отправляешь на бэкенд. Токены sandbox и production не смешиваются; 410 Unregistered — удали строку. Пейлоад маленький JSON: aps.alert, badge, sound. Тихий подъём — content-available 1; Notification Service Extension нужен mutable-content 1 и примерно 30 секунд до serviceExtensionTimeWillExpire.

Типичные промахи: считать токен вечным; отправить debug-токен в прод; PII в пейлоаде; ждать extension без mutable-content. Локальные уведомления через APNs не ходят.



```swift
func application(_ app: UIApplication,
                 didRegisterForRemoteNotificationsWithDeviceToken token: Data) {
    let hex = token.map { String(format: "%02x", $0) }.joined()
    api.uploadDeviceToken(hex)
}
```


**Потом обычно спрашивают**

- Device token, ключ APNs в p8 и старые p12-сертификаты?
- Что меняется для Notification Service Extension?
- Как обработать тап, который должен открыть конкретный экран?
- Получит ли suspended-приложение пуш — и отработает ли делегат?
- Local и remote — что стрельнет в Airplane Mode?
- Sandbox и production — почему TestFlight жил, а сборка из App Store молчит?
- content-available и mutable-content — кто качает картинку?
- APNs 410 — что сервер удаляет?
- Потолок пейлоада — что будет на 4 КБ плюс один байт?
- Alert, silent, VoIP, critical — кто обходит Focus?

</details>

<h2 id="rest">REST</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

REST — ресурсы плюс HTTP-глаголы плюс представления, обычно JSON, плюс stateless-запросы. Существительные в пути, глаголы в методе. Кэшируемость и ETag / Cache-Control — часть сделки. GraphQL и RPC появляются, когда over-fetch или нужен один круг по графу. Мобильная цена — болтливые эндпоинты и толстые пейлоады. Типичный промах: один POST /api, который свитчится по action, и назвать это REST.



```text
GET    /v1/tweets?cursor=
POST   /v1/tweets/12/likes
DELETE /v1/tweets/12/likes
```


**Потом обычно спрашивают**

- REST, GraphQL и WebSocket API — что возьмёшь на ленту?
- Что stateless значит для access token?
- Как версионируешь: /v1 или заголовок?

</details>

<h2 id="urlsession">URLSession</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

URLSession — конвейер запроса: конфигурация, потом задача, потом resume. default шарит дисковый кэш и хранилище кук. ephemeral держит это в RAM и выбрасывает вместе с сессией. background отдаёт трансферы системе, чтобы они дожили после suspend. URLSession.shared нормален для простых GET; свою сессию делаешь, когда нужен делегат, pinning или свой кэш. Задачи стартуют на паузе — забыть resume — классика. Предпочитай data(from:) и bytes(for:) старому dataTask с completion, если не мостишь легаси.

Классические косяки: одна shared-сессия с делегатом, которого никто не держит; background-конфиг на JSON API, который надо просто await.



```swift
func load(_ url: URL) async throws -> Data {
    let config = URLSessionConfiguration.default
    config.timeoutIntervalForRequest = 15
    let session = URLSession(configuration: config)
    let (data, response) = try await session.data(from: url)
    guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else {
        throw URLError(.badServerResponse)
    }
    return data
}
```


**Потом обычно спрашивают**

- Когда нужен делегат сессии вместо async?
- shared и своя сессия — куки, кэш, invalidateAndCancel?
- Что меняет background-конфигурация в completion?
- Когда Alamofire ещё стоит зависимости?

</details>

<h2 id="retry-backoff">Ретрай с backoff</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Ретраишь только идемпотентные или безопасно повторяемые вызовы — GET, put с ключом идемпотентности — и только на переходных сбоях: 408, 429, 5xx, таймауты. Не на 400 и не на 401. Exponential backoff ждёт base умножить на два в степени попытки, обычно с jitter, чтобы флот не устроил stampede. Ставь потолок попыткам и общему времени. Чти Retry-After. Тесный цикл на 500 — как устроить себе DDoS. Типичный промах: ретраить POST /charge и списать дважды, или спать на main actor.



```swift
func get(_ url: URL) async throws -> Data {
    var delay: UInt64 = 200_000_000
    for attempt in 0..<4 {
        do {
            let (data, response) = try await URLSession.shared.data(from: url)
            let code = (response as? HTTPURLResponse)?.statusCode ?? 0
            if (200..<300).contains(code) { return data }
            if code == 400 || code == 401 || code == 403 { throw URLError(.userAuthenticationRequired) }
        } catch is CancellationError { throw CancellationError() }
        try await Task.sleep(nanoseconds: delay)
        delay *= 2
    }
    throw URLError(.cannotConnectToHost)
}
```


**Потом обычно спрашивают**

- Какие статусы безопасно ретраить?
- Зачем jitter?
- Как ретраить POST и не задублировать побочку?

</details>

<h2 id="token-auth">Токенная аутентификация</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

После логина сервер выдаёт короткий access token — часто JWT — и более длинный refresh token. На API-вызовы ставишь Authorization Bearer. Оба кладёшь в Keychain, не в UserDefaults. На 401 один refresh за раз — single-flight actor — потом ретрай исходного запроса; refresh не вышел — на логин. Токены не логируешь.

Классические косяки: access token в query URL; рефреш на каждый вызов; держать refresh только в памяти, чтобы убийство процесса выкидывало пользователя без причины.



```swift
actor AuthHeader {
    private var access: String
    init(access: String) { self.access = access }

    func apply(_ request: inout URLRequest) {
        request.setValue("Bearer \(access)", forHTTPHeaderField: "Authorization")
    }
}
```


**Потом обычно спрашивают**

- Куда кладёшь refresh, чтобы два 401 не устроили stampede?
- Access token, refresh token, API key — что где живёт?
- Что PKCE добавляет мобильному OAuth / SSO?
- Что делаешь с токенами на логауте?

</details>

<h2 id="rest-vs-graphql">REST и GraphQL</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

REST — ресурсы и HTTP-глаголы; клиент знает URL. GraphQL — один эндпоинт и запрос полей: меньше кругов, больше парсить, схему надо версионировать. На iOS дефолт — REST плюс Codable. GraphQL выигрывает, когда одному экрану иначе нужны три REST-вызова, или когда веб и мобайл делят один граф. Цена: сгенерированные клиенты, кэш сложнее URLCache, «гибкий запрос» может стать безразмерной загрузкой. Типичный промах: взять GraphQL «чтобы быть современным» и каждый раз тащить один и тот же мешок полей.



```text
REST:    GET /users/1 + GET /users/1/posts
GraphQL: { user(id: 1) { name posts { title } } }
```


**Потом обычно спрашивают**

- Как кэшируешь GraphQL-ответ против REST URL?
- Кто владеет пагинацией — connections или свой cursor?
- Когда REST всё ещё правильный выбор в 2026?

</details>

<h2 id="rest-vs-rpc">REST и RPC</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

REST называет ресурс и HTTP-глагол: GET /users/12. RPC называет процедуру: /getUser, gRPC UserService.Get, JSON-RPC с method getUser. Под капотом RPC всё равно байты в сокете — часто HTTP/2 плюс protobuf — плюс стаб, который выглядит как локальная функция. На iOS важно: кодоген из proto в Swift, стриминг против one-shot, и то, что «метод» кэшировать труднее, чем GET URL. Чат и внутренние BFF часто выглядят как RPC, даже если говорят JSON. Типичный промах: назвать каждый POST RPC или сказать, что у RPC нет HTTP.



```text
REST:  GET /orders/42
RPC:   POST /twirp/orders.v1.Orders/Get  { "id": "42" }
gRPC:  Orders.Get(OrderId) → Order   // generated client
```


**Потом обычно спрашивают**

- Когда gRPC стоит мобильной зависимости против JSON REST?
- Как кэшировать RPC, который не GET?
- REST, GraphQL, RPC — какую задачу каждый решает?

</details>

<h2 id="reachability">Reachability</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

«Есть ли путь в сеть?» — это NWPathMonitor из Network, не пинг google.com на каждый тап. Satisfied path — ещё не «API жив»: запрос всё равно делаешь и обрабатываешь ошибки. Монитор — чтобы сменить UI (офлайн-баннер) и пнуть очередь ретраев, когда путь вернулся. Старые семплы Reachability / SCNetworkReachability уже пыльные. Типичный промах: блокировать запрос, потому что Wi-Fi выключен, а человек на сотовой.



```swift
let monitor = NWPathMonitor()
monitor.pathUpdateHandler = { path in
    let online = path.status == .satisfied
    Task { @MainActor in banner.isHidden = online }
}
monitor.start(queue: .global(qos: .utility))
```


**Потом обычно спрашивают**

- Path satisfied и успешный вызов URLSession?
- Что делаешь, если путь перевернулся посреди аплоада?
- Почему ICMP ping — плохая единственная проверка?

</details>

<h2 id="url-cache">URLCache</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

URLCache кладёт HTTP-ответы на диск и в память по cache policy запроса и заголовкам ответа — Cache-Control, ETag. Это не NSCache и не твои декодированные модели. useProtocolCachePolicy — дефолт и обычно правильный выбор. reloadIgnoringLocalCacheData — для pull-to-refresh. returnCacheDataElseLoad — для offline-first чтения. Свой URLSessionConfiguration.urlCache даёт размер памяти и диска.

Классические косяки: ждать, что URLCache будет хранить объекты UIImage; выключить кэш глобально из-за одного протухшего эндпоинта — чини policy этого запроса.



```swift
let config = URLSessionConfiguration.default
config.urlCache = URLCache(memoryCapacity: 10_000_000, diskCapacity: 50_000_000)
config.requestCachePolicy = .useProtocolCachePolicy
let session = URLSession(configuration: config)
```


**Потом обычно спрашивают**

- Как ETag и 304 Not Modified живут с URLCache?
- URLCache, NSCache и файл, который пишешь сам?
- Когда reloadIgnoringLocalAndRemoteCacheData — не тот молоток?

</details>

<h2 id="websocket">WebSocket</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

WebSocket — постоянное двустороннее TCP-соединение, апгрейд из HTTP. Берёшь на чат, лайв-счёт, совместные курсоры — не на раз в день настройки. Цена: батарея, число соединений на сервере, reconnect с backoff и то, что будет, когда приложение уйдёт в фон: iOS часто убьёт сокет, падаешь на пуш. Системный клиент — URLSessionWebSocketTask. Типичный промах: держать сокет ради ленты, которую мог бы обновить silent push.



```swift
let task = URLSession.shared.webSocketTask(with: url)
task.resume()
let message = try await task.receive()
```


**Потом обычно спрашивают**

- WebSocket, SSE, long poll, APNs?
- Что сохраняешь, чтобы reconnect не задублировал сообщения?
- Почему сокет плохой выбор, пока приложение suspended?

</details>
