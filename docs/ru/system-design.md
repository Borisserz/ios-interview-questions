# System design

54 карточек · 31 часто спрашивают · [system-design.md](../../topics/system-design.md)

### Mid

<h2 id="eta-polling">Live ETA через polling</h2>

<code>Mid</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Экран райдшеринга должен показывать **live ETA**, который обновляется примерно раз в 10 секунд. Scope: один видимый экран, один водитель. Проговори: start/stop с appear/disappear, отмену in-flight запроса до следующего тика, hop UI на main, `[weak self]`, что в background / плохой сети (backoff, не тугой таймер), и почему одного `Timer` плюс `URLSession.shared` мало.


**Потом обычно спрашивают**

- Timer vs `Task.sleep` в цикле vs WebSocket?
- Как не наложить запросы, если fetch длится дольше 10 секунд?
- Что персистишь, когда scene уходит в background?

</details>

<h2 id="checkout-ui">Собери checkout UI за 60 минут</h2>

<code>Mid</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Собери **экран checkout** за 60 минут из стартера или mock API: позиции, разбивка цены, выбор способа оплаты, кнопка подтверждения. Scope: ViewModel, empty и error, без двойного сабмита. **PCI и 3DS вне scope**, это `{#payment-checkout}`. Рабочий UI к 25-й минуте лучше репозитория, который так и не прикрутил. Чужое готовое решение не вставляй.


**Потом обычно спрашивают**

- На 40-й минуте добавили service fee: какой тип остаётся закрытым?
- Confirm, пока mock API тормозит: что делает кнопка?
- Стартер SwiftUI vs UIKit: дерёшься со стеком, который дали?

</details>

<h2 id="match-simulator">Собери симулятор матча / счёта</h2>

<code>Mid</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Собери **маленький симулятор матча** за 90 минут: выбрать две стороны из bundled JSON, кнопка «следующее событие» кидает **случайный исход** и обновляет табло. Scope: два иннинга (или два тайма), потолок мячей/событий, потолок wickets/жизней, погоня кончается, когда цель пройдена. **Полировка UI вне scope.** Интервью про модуль правил, который можно расширить (новое событие, взвешенные шансы) без переписывания счёта. Чужое готовое решение не вставляй.


**Потом обычно спрашивают**

- Wide / extra / «нельзя выбыть»: какой тип добавляешь и что остаётся закрытым?
- Взвешенные исходы: где живёт случайность, чтобы тесты были детерминированными?
- Первый экран: список сторон с картинками. Локальный JSON или сеть?

</details>

<h2 id="recently-deleted">Спроектируй альбом Recently Deleted</h2>

<code>Mid</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **Recently Deleted** для библиотеки в духе Photos. Scope: tombstone на 30 дней, restore, безопасный purge, давление диска (сначала самые старые) и что синкается на другие устройства. Живая библиотека и корзина это два запроса над одним store, не второе приложение. Камеру проектировать не надо.


**Потом обычно спрашивают**

- Restore после того, как tombstone истёк на устройстве A, но ещё нет на B?
- Мало места: кто решает purge, ты или OS?
- Чем элемент в корзине отличается от hidden / archived?

</details>

<h2 id="live-wallpaper">Спроектируй live wallpaper</h2>

<code>Mid</code> · <code>Редко</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй приложение с анимированными обоями. На iOS нет стороннего live lock screen: так и скажи, потом галерея плюс preview плюс (на iOS) ограниченный набор обоев, или движок Android, если хотят cross-platform.


**Потом обычно спрашивают**

- Что реально можно поставить на iOS vs Android?
- Батарея: как паузить preview, который ушёл с экрана?
- Где живут ассеты: bundle, диск, CDN?
- Как не декодировать видео каждый кадр на main thread?

</details>

<h2 id="recipe-app">Спроектируй приложение рецептов</h2>

<code>Mid</code> · <code>Редко</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй каталог рецептов: browse, поиск, избранное, offline pack. Картинки и список покупок, если останется время.


**Потом обычно спрашивают**

- Что индексируешь на устройстве, а что тянешь при открытии?
- Как избранное синкается между устройствами?
- Политика image cache для каталога, который меняется раз в неделю?

</details>

<h2 id="clock-app">Спроектируй часы</h2>

<code>Mid</code> · <code>Редко</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй Clock: локальное время, мировые часы, будильники, таймеры. Фокус на scheduling, данных таймзон и том, что переживает ребут, а не на красивом циферблате.


**Потом обычно спрашивают**

- `Timer` vs `UNNotification` для будильника?
- Как обработать смену таймзоны, пока таймер тикает?
- Что хранишь, а что считаешь из `Date`?
- Почему RunLoop-таймер плохой инструмент для будильника на 7 утра?

</details>

### Senior

<h2 id="edge-first">Edge-first: кто владеет write</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

В части комнат mobile system design не просят «нарисуй Kafka». Смотрят, **кто владеет write** и **что никогда не уходит с устройства**. Дефолт: телефон (или часы, которые это почувствовали) source of truth, пока offline. Сервер хранит **opaque blob** или ловит конфликт. Третья сторона сырые строки не видит. Вслух скажи порядок доверия: железо / OS / твоё приложение / cloud / partner SDK. Лучше медленный путь, который ты контролируешь, чем CDN, который не твой. Типичный промах: красивый sync, который гонит здоровье или фотки в чужую трубу, или лекция про QPS, когда спросили «два устройства правили одну заметку».



```text
1. Who may write — sensor, phone, server, partner?
2. What does the server see — plaintext, ciphertext, or only a conflict bit?
3. What still works after 72 hours offline?
4. Then boxes. Not before.
```


**Потом обычно спрашивают**

- Watch и телефон спорят об одном sample: чей write побеждает и почему?
- Когда «мы будем медленнее» правильный ответ?
- Партнёр хочет raw read API: что отдаёшь вместо этого?

</details>

<h2 id="sd-interview">Как вести mobile system design</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Сорок пять минут это разговор, не спецификация на прод. Нормальный тайминг: **clarify** (0-5: scope, DAU, offline, платформа), **HLD** (5-15: квадратики), **data и API** (15-25: сущности, pagination), **deep dive** (25-40: два сложных куска), **ops** (40-45: фейлы, метрики, раскатка). Те же идеи, что в мнемонике **SCADET** с курсов: System requirements, Constraints, Architecture, Data и API, Evaluate NFRs, Trade-offs. Сразу зафиксируй **scope**: только клиент, клиент плюс API, или full stack. Закрой **3-5 functional** требований, пару **non-functional** (offline, батарея, consistency) и явное **out of scope**. Mobile system design это не Instagram на доске со стороны бэкенда. Lifecycle, дырявое радио и батарея здесь first-class.

До квадратиков назови **что продаёшь**: короткий список сервисов и данных (история чата, адресная книга, звонок). Потом каждый режешь: клиент, сервер или оба, и выбираешь канал (REST, WebSocket, push, UDP). На каждый list API по умолчанию **pagination**; снимаешь только если набор крошечный. Если спрашивают «самые популярные посты» или «как ловить ботов», две минуты на **формулу** (входы → окно → выход), и только потом Kafka.

Нарисуй high-level схему. Четыре слоя на клиенте хватит: View → ViewModel → use cases → repository (remote плюс local). Deep dive в **один** кусок, который знаешь, потом в **один жёсткий кейс**, который сам возил (image cache и eviction с диска, gap-fill после реконнекта). Спроси, какой квадрат дальше. Типичный промах: прыгнуть в ячейки `UICollectionView`, пока нет data flow.



```swift
enum Scope { case clientOnly, clientAndAPI, fullStack }

struct Brief {
    var scope: Scope
    var functional: [String]   // 3...5
    var nonFunctional: [String]
    var outOfScope: [String]
}
```


**Потом обычно спрашивают**

- Только клиент или ещё и API: что меняется первым?
- Какой non-functional requirement выкинешь, если время кончилось?
- Чем library-design интервью отличается от app-design?
- REST vs GraphQL: когда мобильный клиент причина выбрать одно?
- Что в первые пять минут объявляешь out of scope?
- Какие два subsystem deep-dive на feed и какие на чат?
- Какие «сервисы и данные» назовёшь в первые три минуты WhatsApp-lite?
- Какую NFR-ось проверишь, прежде чем выбрать store (security, offline, размер команды)?
- Когда останавливаешься и пишешь формулу вместо ещё одного квадрата?
- Пройди SCADET на maps-клиенте за 45 минут: куда кладёшь deep dive?
- Privacy model и 72 часа offline: спрашиваешь до первого квадрата?
- High-level архитектура или объектная модель в коде: что фиксируешь в первую минуту?
- Auth, privacy, compliance: называешь сам, пока не спросили?
- Что можно оставить на устройстве, чтобы запрос вообще не ушёл?

</details>

<h2 id="sdui">Спроектируй SDUI-движок</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй клиент, который рисует экраны из дерева компонентов в JSON (или proto). Scope: реестр нативных компонентов, версия схемы, fallback, если сервер прислал неизвестный тип, и хуки аналитики. Браузер изобретать не надо.


**Потом обычно спрашивают**

- Неизвестный компонент: спрятать, placeholder или force-update?
- Как версионировать схему, чтобы старые приложения жили?
- Где живёт навигация: в payload или в приложении?

</details>

<h2 id="analytics-library">Спроектируй analytics-библиотеку</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй пайплайн событий: `track(name, props)` с любого потока, батчинг, backlog на диске, flush в background и privacy (PII, opt-out).


**Потом обычно спрашивают**

- Что будет, если `track` вызвали 200 раз за скролл?
- Как не потерять события на краше?
- Main thread: что в публичном API запрещено?
- Как дропать события, когда пользователь сделал opt-out?
- Flush каждые N событий vs каждые T секунд vs на background: какой дефолт?

</details>

<h2 id="deep-links">Спроектируй deep links</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй Universal Links плюс кастомные URL-схемы для приложения, которого иногда нет на устройстве. Scope: AASA, роутер path → экран, cold start vs warm, deferred link после первой установки. AASA не хости на CDN, который ломает association.


**Потом обычно спрашивают**

- Cold start: `didFinishLaunching` vs scene connection options: кто побеждает?
- Как тестировать Universal Link на девайсе?
- Что сохраняешь, чтобы «открой этот листинг» пережило прыжок в App Store?

</details>

<h2 id="file-downloader">Спроектируй file downloader</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй библиотеку скачивания больших файлов: очередь, pause/resume, progress, куда класть на диск, и что будет, если приложение убили. Сначала публичный API.


**Потом обычно спрашивают**

- Foreground session vs background `URLSession` configuration?
- Как resume с байта `N` (Range / ETag)?
- Max concurrent downloads: кто решает?
- Как не оставлять половинки файлов в Caches?

</details>

<h2 id="home-rails">Спроектируй home из рельс</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **Home** из независимых рельс (hero, continue, trending, ads). Scope: каждая рельса владеет fetch, loading, аналитикой и ячейками. Назови `UICollectionViewCompositionalLayout` плюс diffable snapshot на секцию (или один snapshot с id секций). Один гигантский view controller, который мапит все типы ячеек, это промах. Типы карточек с бэкенда это follow-up, не первый рисунок.


**Потом обычно спрашивают**

- Как двум командам катить две рельсы без merge hell?
- Одна медленная рельса: блочишь first paint?
- Orthogonal (горизонтальная) секция vs вложенная коллекция в ячейке таблицы?

</details>

<h2 id="image-loader">Спроектируй image loader</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй image loader в духе Kingfisher: `url → UIImage` для ленты. Закрой coalescing запросов, memory плюс disk cache, отмену на reuse и публичный API, который сложно сломать.


**Потом обычно спрашивают**

- Две ячейки просят один URL: сколько скачиваний?
- Что делаешь в `prepareForReuse`?
- Memory cache vs `URLCache` vs своя папка на диске?
- Как не декодировать 12 MP JPEG на main thread?

</details>

<h2 id="delivery-tracker">Спроектируй live-трекер доставки</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй экран «ваш заказ едет» в духе DoorDash / Uber Eats. Scope: state machine заказа, геолокация курьера, один Live Activity / Dynamic Island. Транспорт гибрид: WebSocket в foreground, APNs / poll в background. Платежи вне scope.


**Потом обычно спрашивают**

- Какие события в ActivityKit, а какие полным экраном через push?
- Как карте не перерисовываться на каждый тик GPS?
- Что показываешь, если сокет молчит 30 секунд?
- Ближайший supply: geo hash vs опрашивать каждого курьера?
- Протухший GPS: всё равно диспатчишь и что показываешь?

</details>

<h2 id="network-library">Спроектируй networking-библиотеку</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй тонкий HTTP-клиент поверх `URLSession`: request builder, auth plugin, retry, отмена и типизированные ошибки. `URLSession` заново не пиши.


**Потом обычно спрашивают**

- Где живёт refresh access-токена, чтобы два 401 не устроили stampede?
- Как отменить запрос, когда экран умер?
- Retry: какие status code, какой backoff?
- Certificate pinning: в библиотеке или в приложении?

</details>

<h2 id="news-feed">Спроектируй news feed</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй бесконечную ленту в духе Twitter / Instagram / Facebook. Дефолтный scope: скролл, лайк, открыть пост. Offline cache и цена картинок входят. Auth, композ и follow graph выносишь, пока сами не втянут.


**Потом обычно спрашивают**

- Cursor vs offset pagination: что ломается, когда верх ленты едет?
- Кто source of truth на диске после лайка в offline?
- Push vs SSE vs polling для «новые посты»?
- Как держать scroll FPS, если в каждой ячейке remote-картинка?

</details>

<h2 id="offline-sync">Спроектируй offline-first sync</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй local-first store, который синкается, когда сеть вернулась. Scope: dirty-флаги, очередь, политика конфликтов (LWW vs промпт), `BGTaskScheduler`. Одного типа сущности хватит (заметки или задачи). Firebase проектировать не надо.


**Потом обычно спрашивают**

- Кто source of truth, пока offline?
- Как не зациклить sync после конфликта?
- Что успевает 30-секундный `BGAppRefresh` vs processing task?
- Change token / delta fetch vs слать весь store каждый раз?
- Когда сервер обязан хранить ciphertext, который сам не расшифрует?

</details>

<h2 id="offline-media">Спроектируй offline-каталог медиа</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **offline-загрузки** для стримингового каталога (видео или аудио). Scope: resumable background-трансферы `URLSession`, персистентная очередь, **квота диска**, лицензия / expiry и resume после kill. Playback это `{#video-streaming}` / `{#audio-player}`: здесь ты владеешь каталогом и файлами. «Просто сохранить MP4» руками не отмахивайся.


**Потом обычно спрашивают**

- Где живёт DRM-лицензия относительно байтов?
- Пользователь удалил один тайтл vs OS выселила под давлением стораджа: один путь?
- Как выбираешь, что выселять, когда квота кончилась?

</details>

<h2 id="pagination">Спроектируй pagination-библиотеку</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй pager, к которому лента может привязаться: следующая/предыдущая страница, refresh, локальный cache и один поток items для UI.


**Потом обычно спрашивают**

- Cursor vs номер страницы vs `since_id`?
- Где сидит remote-mediator относительно базы?
- Как выкинуть протухшую страницу после pull-to-refresh?
- Что наблюдает UI: `[Item]` или diff?

</details>

<h2 id="payment-checkout">Спроектируй payment checkout</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй экран оплаты картой (или Apple Pay). Scope: tokenize на устройстве, идемпотентный «Оплатить», 3DS / SCA, state machine (`idle → confirming → paid / failed`). PAN не хранишь. PCI это «что никогда не должно коснуться нашего диска».


**Потом обычно спрашивают**

- Двойной тап Pay: как не списать дважды?
- Apple Pay vs форма карты: что меняется на клиенте?
- Что персистишь, если приложение убили посреди 3DS?

</details>

<h2 id="push-system">Спроектируй push-систему</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй путь клиента и сервера для remote push: permission, device token, APNs, payload, тап → экран, и silent update. Это не карточка «что такое APNs», а весь пайплайн.


**Потом обычно спрашивают**

- Ротация токена: кто хранит маппинг user ↔ device?
- Видимый alert vs `content-available`: батарея и надёжность?
- Как Notification Service Extension меняет дизайн?
- Что персистишь, чтобы тап сработал после cold start?
- Deferred deep link после установки: что хранишь и как долго?

</details>

<h2 id="short-video-feed">Спроектируй short-form видеоленту</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй вертикальную ленту в духе Reels / TikTok. Scope: свайп, autoplay клипа на экране, prefetch соседей. Дефолт: пул из нескольких `AVPlayer`, не плеер на ячейку. Память и cellular входят; инструменты автора вне scope.


**Потом обычно спрашивают**

- Сколько плееров держишь тёплыми и кого выселяешь?
- Что prefetch: следующий URL, следующий сегмент, следующий thumbnail?
- Как остановить decode, когда лента ушла в background?

</details>

<h2 id="icloud-sync">Спроектируй sync устройств как iCloud</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **кросс-девайс sync** заметок или фото. Scope: **телефон source of truth**, пока offline; сервер реплика, которая может хранить **opaque blob**. Говори change token / delta, политику конфликтов (LWW vs CRDT vs промпт) и что реально успевает 30-секундный `BGAppRefresh`. Generic cloud-базу проектировать не надо.


**Потом обычно спрашивают**

- Что сервер может видеть: plaintext-строки или ciphertext, который SEP не отпускал?
- Четыре устройства вернулись через неделю, у одних часы поехали: как мержишь?
- LWW для аватарки vs CRDT для общего альбома: почему оба?
- Соседние устройства по локальному радио vs cloud-реплика: когда сервер пропускаешь?
- Version vector на устройстве, сервер только ловит конфликт: когда это лучше server-side diff?

</details>

<h2 id="audio-player">Спроектируй аудиоплеер</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **клиент** Spotify / Apple Music. Дефолтный scope: три экрана, **library** (плейлисты / альбомы), **playlist** (треки плюс play), **now playing** (prev / next / shuffle). Playback должен жить после ухода с экрана: долгоживущий player service, не VC. Говори HLS / adaptive bitrate, `AVPlayer`, audio session плюс lock screen и один offline-альбом. Gapless и CarPlay это follow-up.


**Потом обычно спрашивают**

- Как оставить звук живым, когда приложение в background?
- Очередь vs один item: кто владеет «up next»?
- Offline-файл vs streaming URL: тот же player API?
- Library / playlist / player: какой объект переживает navigation stack?
- HLS vs один URL на MP3: что клиент всё равно владеет?
- 10 000 offline-треков: что выселяешь первым, когда квота кончилась?

</details>

<h2 id="ab-experiments">Спроектируй библиотеку A/B экспериментов</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй клиент, который тянет assignments, кэширует их, отдаёт `variant(for: flag)` и не мигает UI на первом запуске.


**Потом обычно спрашивают**

- Sticky assignment после refresh посреди сессии?
- Конфиг-запрос упал: последний cache или default?
- Как не прыгнуть лейаутом, если флаг приехал поздно?
- Кто владеет exposure logging?
- Как быстро remote kill switch доедет до всех клиентов?

</details>

<h2 id="location-sharing">Спроектируй библиотеку шаринга геолокации</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй библиотеку, которая публикует геолокацию пользователя на бэкенд и рисует других на карте. Permissions, точность vs батарея, обновления в background и маленький публичный API.


**Потом обычно спрашивают**

- When vs significant-change vs visits: какой режим под какой продукт?
- Как остановить апдейты, когда карты уже нет?
- Что шлёшь: сырые точки или упрощённый путь?
- Privacy: кто видит стрим и как его отозвать?
- Как сгладить GPS jitter, не убив батарею?

</details>

<h2 id="video-streaming">Спроектируй видеоплеер</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй long-form плеер (Netflix / YouTube). Scope: HLS playback, adaptive bitrate, контролы на lock screen, одна offline-загрузка. FairPlay / DRM и реклама вне scope, пока сами не втянут. Назови `AVPlayer` / `AVPlayerViewController` и что **ты** владеешь вокруг (lifecycle item, ошибки, позиция resume).


**Потом обычно спрашивают**

- Как выбираешь стартовый bitrate на плохой сети?
- Где хранится watch-position, чтобы после kill посреди серии продолжить?
- Что рвёшь, когда человек уходит с экрана?
- После offline-загрузки: где живёт лицензия относительно файла?

</details>

<h2 id="design-client-app">Спроектируй клиент Notes / Gmail / Facebook</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **iOS-клиент** Notes, Gmail или Facebook. Сначала спроси scope (offline, sync, вложения, поиск). Потом: экраны, локальный store, sync / конфликт, пайплайн картинок, что пушишь vs что пуллишь. Для Notes отдельно: Core Data / SwiftData на устройстве, CloudKit или своё API на несколько устройств, rich text (TextKit), и поиск локальный (`Core Spotlight`) или серверный индекс. Оставайся на телефоне. Бэкенд это квадратики, пока сами не утащат.


**Потом обычно спрашивают**

- Что персистишь, чтобы в airplane mode открылся последний inbox?
- Как обрабатываешь два устройства, которые правят одну заметку?
- Какие Apple-фреймворки реально называешь (SwiftData, Push, Background Tasks)?
- CloudKit private DB vs свой sync API: от чего отказываешься?
- Где сидит `Core Spotlight` относительно поиска внутри приложения?

</details>

<h2 id="caching-library">Спроектируй кэш-библиотеку</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй generic cache (память, диск по желанию). Публичный API, eviction (LRU / cost / memory warning), thread safety и что значит «optional» для вызывающего.


**Потом обычно спрашивают**

- `NSCache` vs свой словарь плюс lock?
- Как ключуешь картинки vs JSON-ответы?
- Что будет на memory warning посреди записи?
- Почему miss всё равно должен дать корректный результат?

</details>

<h2 id="image-upload">Спроектируй пайплайн загрузки картинок</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Начни с вопросов: камера или библиотека, max size, retry, offline, кто видит картинку, нужен ли thumbnail сразу. Потом слои. **Клиент:** pick → compress / downscale на background queue → локальный draft (файл плюс состояние аплоада), чтобы после kill mid-flight можно было resume → upload через `URLSession` (background config, если человек может уйти) → progress → на success пишешь remote URL в draft. **API:** presigned PUT в object storage, не JSON с base64. **Сервер:** virus scan, лимиты размера, варианты, нотификация через push или WebSocket. **Фейл:** retry с backoff, второй тап не дублирует (idempotency key). **Cache:** сразу показываешь локальный файл, потом меняешь на CDN URL. Интервьюеру нужна state machine (`queued / uploading / failed / done`), а не имя фреймворка. «Фотоприложение, которое синкает camera roll» это та же машина плюс cursor того, что уже на сервере.



```swift
enum UploadState: String {
    case queued, uploading, failed, done
}

struct Draft {
    var localURL: URL
    var remoteURL: URL?
    var state: UploadState
    var idempotencyKey: UUID
}
```


**Потом обычно спрашивают**

- Background `URLSession` vs foreground task: когда что?
- Как не залить одну и ту же фотку дважды?
- Где генеришь thumbnail: клиент, сервер или оба?
- Как resume sync camera roll после того, как процесс убили?
- Library API (file uploader) vs этот продуктовый пайплайн: в чём разница?

</details>

<h2 id="search-autocomplete">Спроектируй поиск с autocomplete</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй поиск в приложении с typeahead. Scope: debounce, отмена in-flight запроса при смене query, сначала локальные хиты, если есть индекс. Ранжирование на сервере может остаться квадратиком. Проговори гонку: медленная «а» не должна перетереть быструю «аб».


**Потом обычно спрашивают**

- Отмена `Task` vs `switchToLatest`: одна идея?
- Offline: FTS / trie на устройстве vs пустой стейт?
- Как логировать impression, не стреляя на каждую букву?

</details>

<h2 id="chat-app">Спроектируй чат</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй messaging-клиент. Выбери 1:1 или группу, потом 3-5 фич: send/receive, offline draft, медиа, read receipt. Бэкенд считай существующим; sync API набросай, если попросят.


**Потом обычно спрашивают**

- REST vs WebSocket vs push, когда приложение в background?
- Как упорядочить сообщения после реконнекта с дырками?
- Что на диске, а что только в RAM?
- Как показать «sending / sent / failed» и не задвоить отправку?
- Где E2EE меняет клиент (ключи, вложения, поиск)?
- Один процесс, много workspace: один файл SQLite или много?
- Состояния сообщения: draft → sending → sent → delivered → read. Что локальное, что ack?
- Cursor vs offset для истории, если сообщения можно удалять?
- Heartbeat плюс backoff после падения WebSocket: кто владеет reconnect?
- Как дедупить retry, который сервер уже сохранил?
- Групповой чат: что такое `conversationId` vs fan-out список на клиенте?
- Приложение в background, WebSocket мёртв: что в payload APNs?

</details>

<h2 id="unread-badge">Счётчик unread и badge</h2>

<code>Senior</code> · <code>Часто</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй счётчик непрочитанных (сообщений или нотификаций): badge на табе, строка в списке чатов и лейбл в nav bar, которые остаются в синхроне. Scope: один процесс, один пользователь. Скажи, где живёт число (cursor на сервере vs локальный «last read»), кто его увеличивает, и как сообщение, пришедшее при открытом треде, **не** бампает badge.


**Потом обычно спрашивают**

- Observer vs один store vs polling API каждые 30 секунд?
- Два устройства: last-read это timestamp на сервере или id сообщения?
- Badge иконки vs badge в приложении: кто владеет `UNUserNotificationCenter`?
- Как не вспыхнуть «99+» на запуске, пока локальная база не загрузилась?

</details>

<h2 id="crash-reporter">Спроектируй crash reporter</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй клиентский SDK в духе Crashlytics. Scope: поймать fatal, сохранить minidump / стек, залить на следующем запуске, breadcrumbs. Signal-safety: в хендлере почти ничего нельзя. OOM это отдельный путь (jetsam ≠ `NSException`).


**Потом обычно спрашивают**

- Что легально внутри signal handler?
- Как отличить «убили за память» от force-quit пользователем?
- Где живут dSYM и кто символицирует?

</details>

<h2 id="file-uploader">Спроектируй file uploader</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй переиспользуемый **uploader API** (любой файл, не только фотки): enqueue, progress, cancel, retry, multipart vs presigned PUT. Продуктовый sync альбома остаётся на `{#image-upload}`.


**Потом обычно спрашивают**

- Как вызывающий узнаёт progress, не держа view?
- Idempotency key: забота библиотеки или приложения?
- Background transfer vs своя очередь retry?

</details>

<h2 id="on-device-llm">Спроектируй on-device LLM-ассистента</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй on-device ассистента (суммируй тред, ответь из локальных заметок). Scope: скачивание / обновление модели, бюджет RAM / thermal, стриминг токенов в UI, маленький локальный RAG по данным пользователя. Cloud fallback это follow-up. Лекцию про математику трансформеров не читай.


**Потом обычно спрашивают**

- Что будет, если Neural Engine троттлит посреди стрима?
- Где живёт текст пользователя и что никогда не должно уйти с устройства?
- Как версионировать модель на 2 GB, не блокируя первый запуск?
- `@Generable` DTO vs SwiftData `@Model`: почему это не один тип?
- Устройство без Neural Engine: какой путь без AI?

</details>

<h2 id="stories">Спроектируй stories</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй stories: истечение через 24 часа, tap-through, preload следующего клипа, seen-state и тонкий композ, если попросят. Ранжирование ленты вне scope.


**Потом обычно спрашивают**

- Как preload, не взорвав память на кольце из 15 штук?
- Seen-state: сервер, диск или оба?
- Видео vs картинка: что меняется в loader?
- Что делаешь, если следующая story отдала 404 посреди свайпа?

</details>

<h2 id="clipboard-sync">Спроектируй sync буфера / proximity</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **скопировал на телефоне, вставил на ноуте** (и наоборот). Scope: один аккаунт iCloud, устройства рядом vs далеко, лимит размера, end-to-end encryption. Рядом можно локальное радио; далеко та же sync-труба, что `{#icloud-sync}`. Конфликт: «последний copy побеждает». Общий файловый локер проектировать не надо.


**Потом обычно спрашивают**

- Что кладёшь на relay: plaintext или blob, который разворачивает SEP?
- Огромное видео в буфере: синкаешь байты или placeholder?
- Как украденному ноуту не читать последний copy вечно?

</details>

<h2 id="video-calling">Спроектируй видеозвонок</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй клиент FaceTime / Meet / Zoom. Scope: звонок 1:1, permissions на камеру и микрофон, mute, поворот. Набросай signaling vs media (WebRTC: STUN/TURN, SFU). Сетка на 50 и запись вне scope, пока не попросят.


**Потом обычно спрашивают**

- Что делаешь, когда приложение в background: только звук?
- Как обработать thermal / просадку сети, чтобы чёрный кадр не висел вечно?
- Кто владеет audio session: ты или CallKit?

</details>

<h2 id="restaurant-ordering">Спроектируй заказ в ресторане</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй приложение discovery плюс заказ плюс оплата (сторона мерчанта DoorDash или одно заведение). Scope: меню, корзина, checkout, статус заказа. Карта/поиск могут быть квадратиком. Платежи переиспользуют карточку checkout; live-трекинг курьера это follow-up, не ядро.


**Потом обычно спрашивают**

- Как версионировать меню, которое меняется, пока корзина открыта?
- Что лочишь, когда тапают Place Order?
- Guest checkout vs аккаунт: что на диске?

</details>

<h2 id="calendar-client">Спроектируй календарь</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй iOS-клиент Google / Apple Calendar. Scope: месяц плюс день, создать событие, sync. Recurrence (`RRULE`) и конфликты это жёсткая часть. Бесконечный скролл сетки месяца входит; полный CalDAV-сервер вне scope.


**Потом обычно спрашивают**

- Как развернуть ежедневное recurring-событие, не материализуя 10 лет?
- Два устройства правят одно событие: last-write-wins или промпт?
- Silent push vs pull-to-refresh vs `BGAppRefresh`?

</details>

<h2 id="ecommerce-catalog">Спроектируй каталог товаров</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй каталог в духе Amazon / Shopify: поиск или сетка browse, PDP, корзина. Scope: тяжёлая на картинки лента, cursor-страницы, корзина переживает kill. Checkout может быть квадратиком. Wishlist offline это follow-up.


**Потом обычно спрашивают**

- Как держать сетку на 60 fps с большими картинками?
- Корзина на диске vs сервер: кто побеждает в конфликте?
- Что протухло: цена, сток или фото?

</details>

<h2 id="chatgpt-app">Спроектируй клиент в духе ChatGPT</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй iOS-клиент в духе ChatGPT (модель в облаке, не on-device). Scope: композ, стрим токенов, история диалога на диске, отмена in-flight ответа. Auth и биллинг это квадратики. Говори стриминг (`URLSession.bytes` / WebSocket), state machine сообщения и что показываешь, если сокет умер посреди фразы.


**Потом обычно спрашивают**

- Как рисовать токены, не дёргая text view?
- Стриминг JSON / `URLSession.bytes` vs ждать весь payload: где парсишь?
- Что персистится, если пользователь убил приложение посреди стрима?
- Чем это отличается от карточки on-device LLM?

</details>

<h2 id="maps">Спроектируй клиент карт / навигации</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй **клиент** в духе Maps: найти место, показать на карте, начать turn-by-turn. Scope: один пользователь, одно устройство, online. Говори тайлы / vector rendering, пайплайн геолокации (`CLLocationManager`: точность vs батарея), polyline маршрута плюс reroute и что кэшируешь (недавние поиски, последний маршрут). Live traffic и offline-регионы это follow-up.


**Потом обычно спрашивают**

- Significant-change vs `kCLLocationAccuracyBest`: какой режим для browse vs навигации?
- Кто владеет map SDK: MapKit, чужой рендерер или свои тайлы?
- Как перестроить маршрут, когда человек сошёл с polyline, не расплавив батарею?
- Сматчить райдера с ближайшими водителями: какой индекс и что если пинг 30 секунд назад?

</details>

<h2 id="wallet">Спроектируй кошелёк / балансы</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй домашний экран **кошелька**: несколько балансов (карты, депозиты, баллы) из **разных API** с разной латентностью. Scope: один пользователь, одно устройство. Говори, как мержишь стримы, что показываешь, пока часть вызовов ещё летит, pagination / локальный поиск по истории, offline last-known суммы и где маскируешь деньги. Ядро банка проектировать не надо.


**Потом обычно спрашивают**

- Один медленный микросервис: блочишь весь экран?
- Push vs pull vs refresh при открытии экрана для смены баланса?
- Где живёт замаскированная сумма, чтобы скриншот не был настоящей цифрой?

</details>

<h2 id="airbnb-booking">Спроектируй поиск и бронь Airbnb</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй search плюс book для жилья. Scope: карта и список в синхроне, debounce запроса, draft брони, короткий inventory hold. Платежи могут остаться квадратиком. Скажи, что кэшируешь (результаты поиска протухают; у hold есть таймер).


**Потом обычно спрашивают**

- Движение карты vs набор текста: чей запрос побеждает?
- Что будет, когда 15-минутный hold истёк на экране review?
- Как восстановить draft после kill процесса?
- Offline сохранённые листинги / draft брони: что ещё валидно, когда радио вернулось?

</details>

<h2 id="collaborative-editor">Спроектируй совместный редактор</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй клиент Notes / Docs, где два устройства правят один документ. Scope: локальный ввод мгновенный, sync потока ops, показать presence. Спроси OT vs CRDT и что персистишь как op log. Рисовать полный клон Word не надо.


**Потом обычно спрашивают**

- Что если обе стороны вставили в один индекс, пока были offline?
- Cursor presence: payload WebSocket vs отдельный канал?
- Как уплотнить op log, чтобы новое устройство догнало?
- LWW для аватарки, CRDT для общего абзаца: как выбираешь?

</details>

<h2 id="flight-booking">Спроектируй флоу бронирования рейса</h2>

<code>Senior</code> · <code>Средне</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй search → fare → место → оплата. Отдельно скажи про cache результатов поиска, восстановление стека, если человек ушёл, фейл оплаты и истечение **seat lock**.


**Потом обычно спрашивают**

- Сколько живёт hold места и что UI показывает, когда он истёк?
- Что оставляешь, если приложение ушло в background на экране оплаты?
- Idempotency на «Оплатить»: двойной тап, двойное списание?
- Какие данные безопасно кэшировать (тарифы протухают)?

</details>

<h2 id="json-parser">Спроектируй JSON-парсер</h2>

<code>Senior</code> · <code>Редко</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй parser API уровня Codable (думай Moshi/Gson): decode `Data` → `T`, кастомные adapter, поверхность ошибок и ожидания по потокам. Лучше ответить «зачем не просто `JSONDecoder`», чем писать лексер руками.


**Потом обычно спрашивают**

- Как репортить отсутствующий ключ с путём?
- Стратегии Date / URL: глобально или per-type?
- Incremental / streaming parse: когда оно того стоит?
- Что безопасно звать с main thread?

</details>

<h2 id="e-reader">Спроектируй e-reader</h2>

<code>Senior</code> · <code>Редко</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй ридер в духе iBooks / Kindle. Scope: открыть книгу, pagination или скролл, запомнить позицию, один скачанный файл. Sync между устройствами и витрина это follow-up. Говори формат (EPUB vs PDF), `CATiledLayer` / TextKit и что персистишь как закладку.


**Потом обычно спрашивают**

- Как прыгнуть в главу 12, не раскладывая всю книгу?
- Dark mode и Dynamic Type: что рефловится?
- Что если скачана только половина файла?

</details>

<h2 id="contacts-realtime">Спроектируй контакты с live-статусом</h2>

<code>Senior</code> · <code>Редко</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй список контактов плюс presence (online / last seen). Локальная адресная книга vs граф на сервере и как приезжают апдейты presence.


**Потом обычно спрашивают**

- Push vs presence-канал: батарея на 500 контактах?
- Как смержить контакты с устройства с профилями на сервере?
- Что кэшируется, когда пользователь offline?
- Permissions: что если доступ к Contacts отказали?

</details>

<h2 id="photo-editing">Спроектируй фоторедактор</h2>

<code>Senior</code> · <code>Редко</code> · <code>Practice</code>

<details>
<summary><strong>Показать формулировку</strong></summary>

Спроектируй редактор: crop, фильтры, export. Память под 12 MP bitmap, undo stack и где сидят Core Image / Metal. Шаринг вне scope, пока не попросят.


**Потом обычно спрашивают**

- Full-res vs preview пайплайн: когда рендеришь финальный bitmap?
- Какого размера undo stack и что хранишь на шаг?
- Main thread: что нельзя во время драга фильтра?
- Export: HEIC vs JPEG, и кто жмёт?

</details>
