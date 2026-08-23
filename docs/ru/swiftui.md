# SwiftUI

30 карточек · 23 часто спрашивают · [swiftui.md](../../topics/swiftui.md)

### Junior

<h2 id="binding">@Binding</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

@Binding — **окно на чтение и запись** в чужой стейт. Родитель владеет @State / @Bindable; ребёнок получает $value. Мутация биндинга пишет насквозь. Кастомный init принимает Binding (init(text: Binding)). Типичный промах: @Binding у владельца или скопировать значение в @State у ребёнка — родитель никогда не обновится.



```swift
struct Editor: View {
    @Binding var text: String
    var body: some View { TextField("Name", text: $text) }
}

struct Parent: View {
    @State private var name = ""
    var body: some View { Editor(text: $name) }
}
```


**Потом обычно спрашивают**

- @Binding vs @Bindable на @Observable?
- Как написать кастомный init, который принимает биндинг?
- Когда колбэк понятнее биндинга?

</details>

<h2 id="state">@State</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**@State** — хранилище, которое SwiftUI *держит за этот View*. Объявляешь приватное значение; враппер живёт через кучу пересозданий структуры View, а присваивание инвалидирует body. Бери для локального UI: тоггл, выбранный таб, черновик текстового поля. Если ребёнок должен писать — отдай биндинг через $property. Долгоживущий reference type в @State на старых ОС не клади (для этого @StateObject); на iOS 17+ @State с классом @Observable — новый путь владения. Типичные ошибки: сделать @State public и дать родителю писать во враппер, каждый раз инициализировать @State из входящего let (начальное значение берут один раз) и класть в @State данные, которыми владеет сервер.



```swift
struct Counter: View {
    @State private var count = 0

    var body: some View {
        Button("Taps: \(count)") { count += 1 }
    }
}
```


**Потом обычно спрашивают**

- Почему @State обычно private?
- В чём разница между count и $count?
- Почему смена начального значения @State у родителя не сбрасывает ребёнка?

</details>

<h2 id="appstorage">@AppStorage</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

@AppStorage — это UserDefaults как property wrapper SwiftUI. Запись обновляет View. Бери для флага темы или последнего таба — не для токенов и не для ленты. Можно направить на suite App Group. Типичный промах: большой Codable-блоб или ожидание синка между девайсами (это iCloud KVS / CloudKit).



```swift
@AppStorage("usesGrid") private var usesGrid = false
```


**Потом обычно спрашивают**

- @AppStorage vs @SceneStorage?
- Почему сюда нельзя класть auth-токен?
- Как пошарить это с виджетом?

</details>

<h2 id="button-style">ButtonStyle</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**ButtonStyle** — протокол, который перерисовывает лейбл кнопки, не подменяя тап. Реализуешь makeBody(configuration:) и читаешь configuration.label плюс configuration.isPressed. Вешаешь через .buttonStyle(MyStyle()) или static member. Системные стили (.bordered, .borderedProminent, .plain) — тоже ButtonStyle. **PrimitiveButtonStyle** — нижний крючок, если жест хочешь держать сам (кастомный toggle-button). Стили не меняют accessibility-активацию, меняют хром. Типичные ошибки: обернуть Button в onTapGesture вместо стиля и забыть isPressed — контрол никогда не выглядит нажатым.



```swift
struct ScaleStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .opacity(configuration.isPressed ? 0.6 : 1)
            .scaleEffect(configuration.isPressed ? 0.96 : 1)
    }
}

Button("Save") { save() }
    .buttonStyle(ScaleStyle())
```


**Потом обычно спрашивают**

- Чем PrimitiveButtonStyle отличается от ButtonStyle?
- Как сделать стиль дефолтным для целого поддерева?
- Почему не стоит вешать onTapGesture поверх Button?

</details>

### Mid

<h2 id="environmentobject-vs-observedobject">@EnvironmentObject vs @ObservedObject</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Оба подписываются на ObservableObject. **@ObservedObject** — явная зависимость: родитель передаёт инстанс. **@EnvironmentObject** — неявная: инжектишь один раз через .environmentObject(_:) и любой потомок читает по типу. @ObservedObject — когда связь локальная и хочешь видеть поток данных в инициализаторе. @EnvironmentObject — когда куче несвязанных экранов нужен один объект (сессия, тема, корзина) и тащить его через каждый init — шум. Цена environment — непрозрачность: нет .environmentObject — крэш в рантайме, два объекта одного типа в дереве без обёртки не уживутся. Владение всё равно там, где объект создали, обычно @StateObject на корне. Типичная ошибка: запихнуть экранную модель в environment, и следующий push тихо её перезапишет.



```swift
final class Session: ObservableObject {
    @Published var user: String?
}

struct RootView: View {
    @StateObject private var session = Session()
    var body: some View {
        ContentView()
            .environmentObject(session)
    }
}

struct ProfileBadge: View {
    @EnvironmentObject private var session: Session
    var body: some View { Text(session.user ?? "Guest") }
}
```


**Потом обычно спрашивают**

- Почему отсутствующий environmentObject падает, а не опционален?
- Когда прокинуть @ObservedObject понятнее, чем environment?
- Как @Environment(Session.self) меняет это с @Observable?

</details>

<h2 id="published">@Published</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**@Published** — property wrapper из Combine для класса, который конформит ObservableObject. На willSet он шлёт в objectWillChange этого объекта — именно на него подписывается SwiftUI. На структуре не работает и сам по себе вьюху не обновляет: View должен держать объект в @StateObject, @ObservedObject или @EnvironmentObject. Присвоить новое значение @Published-свойству достаточно; мутация ссылки внутри этого значения (например append в класс, который лежит в свойстве) не стрельнет, пока не присвоишь новый враппер или сам не пошлёшь objectWillChange. Фреймворк Observation (@Observable, iOS 17) трекает доступ к свойствам, и на новых типах @Published уже не нужен. Типичная ошибка: повесить @Published на SwiftUI View.



```swift
final class SearchModel: ObservableObject {
    @Published var query = ""
    @Published private(set) var results: [String] = []

    func run() {
        results = query.isEmpty ? [] : ["\(query) — 1"]
    }
}
```


**Потом обычно спрашивают**

- Почему мутация массива внутри published-класса не освежает UI?
- Как @Published связан с objectWillChange?
- Чем это заменяют на типе с @Observable?

</details>

<h2 id="stateobject-vs-observedobject">@StateObject vs @ObservedObject</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Оба враппера подписываются на ObservableObject. **@StateObject** *владеет* инстансом: SwiftUI создаёт его один раз (когда identity этого View впервые появляется) и держит, пока body пересоздают. **@ObservedObject** не владеет — смотрит на объект, который держит кто-то другой. Классический баг: @ObservedObject var model = Model() внутри View — рефреш родителя собирает новый Model, стейт пропадает. Владей через @StateObject у создателя, тот же инстанс отдай вниз как @ObservedObject (или @EnvironmentObject). На iOS 17+ @State + @Observable закрывает кучу этой пары, но на собеседовании всё ещё спрашивают правило владения. Типичная ошибка: @StateObject на View, который не владелец — случайно плодишь второй source of truth.



```swift
final class Cart: ObservableObject {
    @Published var count = 0
}

struct ShopView: View {
    @StateObject private var cart = Cart()
    var body: some View { CartButton(cart: cart) }
}

struct CartButton: View {
    @ObservedObject var cart: Cart
    var body: some View { Text("\(cart.count)") }
}
```


**Потом обычно спрашивают**

- Что ломается с @ObservedObject var model = Model()?
- Когда @EnvironmentObject лучше прокидывать вниз, чем @ObservedObject?
- Как @Bindable меняет это на типах с @Observable?

</details>

<h2 id="environment">Environment в SwiftUI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Environment** — мешок значений, который SwiftUI гонит только вниз по дереву View. Встроенные ключи: colorScheme, dynamicTypeSize, locale, dismiss. Читаешь через @Environment(\.key), пишешь через .environment(\.key, value) или отдельный модификатор вроде .preferredColorScheme. Свои значения — EnvironmentKey плюс свойство на EnvironmentValues. **@EnvironmentObject** — другой слот: инжектит общий ObservableObject по типу, не маленькое значение. Дети видят то, что выставил ближайший предок; вверх никто не ходит. Типичные ошибки: тащить @EnvironmentObject ради одного булева, забыть .environmentObject на корне и упасть в рантайме, ждать, что изменение в листе обновит родителя.



```swift
private struct CardRadiusKey: EnvironmentKey {
    static let defaultValue: CGFloat = 12
}

extension EnvironmentValues {
    var cardRadius: CGFloat {
        get { self[CardRadiusKey.self] }
        set { self[CardRadiusKey.self] = newValue }
    }
}

struct Card: View {
    @Environment(\.cardRadius) private var radius
    var body: some View { RoundedRectangle(cornerRadius: radius) }
}
```


**Потом обычно спрашивают**

- Чем @Environment отличается от @EnvironmentObject?
- Что будет, если ребёнок так и не получил environmentObject?
- Когда EnvironmentKey лучше, чем просто передать аргумент?
- Почему чтение любого ключа @Environment делает тебя зависимым от всего мешка EnvironmentValues?

</details>

<h2 id="geometry-reader">GeometryReader</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**GeometryReader** — View, который забирает *всё оставшееся место*, потом зовёт твою замыкание с GeometryProxy (size, safeAreaInsets, frame(in:)). В этом растягивании и ловушка: обернуть лейбл ридером, чтобы измерить, часто раздувает родителя на весь экран. Меряй в background или overlay, чтобы ридер взял размер ребёнка, либо Layout / containerRelativeFrame на новых ОС. У фреймов прокси нужно координатное пространство (global, local или именованное), иначе цифры не совпадут с той вьюхой, о которой думаешь. Типичные ошибки: ридер как корень каждого экрана и чтение proxy.size в первом проходе, когда он ещё ноль.



```swift
struct MeasuredBar: View {
    @State private var width = 0.0

    var body: some View {
        Capsule()
            .frame(height: 6)
            .background(
                GeometryReader { proxy in
                    Color.clear.preference(key: WidthKey.self, value: proxy.size.width)
                }
            )
            .onPreferenceChange(WidthKey.self) { width = $0 }
    }
}

private struct WidthKey: PreferenceKey {
    static var defaultValue = 0.0
    static func reduce(value: inout Double, nextValue: () -> Double) { value = nextValue() }
}
```


**Потом обычно спрашивают**

- Почему GeometryReader в HStack разносит лейаут?
- Как измерить View, не меняя его размер?
- Когда лучше взять Layout?
- Как PreferenceKey возвращает измеренный размер родителю?

</details>

<h2 id="init-vs-onappear">Init у View vs onAppear</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

У SwiftUI View **инициализатор бежит каждый раз, когда структуру собирают**, а это часто: родительский body пересчитался, ForEach пересобрался, модификатор сменил identity. Он должен быть дешёвым и без сайд-эффектов — сложить свойства, вывести значение, в сеть не ходить. **onAppear** срабатывает, когда View вставили в отрисованную иерархию (onDisappear — когда убрали). Туда — аналитика, фокус, старт работы; оговорка: навигация и табы могут вызвать его не раз. Для async-работы, которую надо отменить, когда View уходит, лучше хук .task. Голый Task { } внутри onAppear (или body) — неструктурированный: наследует MainActor, но **не отменяется**, когда View уходит, пока сам не сохранишь хэндл. Типичные ошибки: фетч в init (дубли запросов, нет отмены), считать onAppear за viewDidLoad и стартовать Task { } в строке, которая уедет со скроллом.



```swift
struct ProfileView: View {
    let userID: String
    @State private var name = ""

    init(userID: String) {
        self.userID = userID
    }

    var body: some View {
        Text(name)
            .task(id: userID) {
                name = await UserAPI.name(for: userID)
            }
    }
}
```


**Потом обычно спрашивают**

- Почему init может отработать много раз для одного экрана, который пользователь всё ещё видит?
- Когда .task лучше, чем onAppear?
- .task vs onAppear vs Task { } — что отменяется на disappear?
- Что делает onAppear внутри List, который переиспользует строки?

</details>

<h2 id="lazyvstack-vs-vstack">LazyVStack vs VStack</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

VStack собирает **каждого** ребёнка, как только стек попал в дерево. LazyVStack (внутри ScrollView) собирает детей **когда они подходят к видимой области**. Lazy — для длинной ленты; обычный стек — для короткой формы: у lazy есть цена первого лейаута и сюрпризы с таймингом onAppear / @State. List — свой lazy-контейнер с сепараторами и reuse-подобным поведением; не оборачивай List в LazyVStack. Типичный промах: LazyVStack из 10 строк «для перфоманса» или lazy-стек *снаружи* скролла — тогда ничего не ленивое.



```swift
ScrollView {
    LazyVStack(alignment: .leading, spacing: 12) {
        ForEach(items) { item in
            Row(item: item)
        }
    }
}
```


**Потом обычно спрашивают**

- LazyVStack vs List vs LazyVGrid — что брать для экрана настроек?
- Почему @State в lazy-строке может сброситься, когда уезжаешь скроллом?
- Значит ли lazy, что сеть в onAppear безопасна?
- Меняешь размер ячейки в onAppear — какую prefetch-работу ты только что выкинул?

</details>

<h2 id="swiftui-mv">MV vs MVVM в SwiftUI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**MV** (как обычно выглядят сэмплы Apple по SwiftUI) — View + Model: @Query / @State / маленький стор, логика рядом с данными, без обязательного типа ViewModel на каждый экран. **MVVM** добавляет отдельный observable-объект, чтобы View оставался тупым, а правила юнит-тестировались. SwiftUI и так уже рендерер стейта — ViewModel, который только перепубликует @Query или оборачивает каждый тап, это лишнее движение. MV — когда стейт экрана и есть стор. ViewModel — когда есть маппинг, оркестрация или тест, который не напишешь против View. Типичный промах: «SwiftUI требует MVVM» или объект на 400 строк, который просто View в классе.



```swift
// MV — view talks to the store
struct NotesView: View {
    @Query private var notes: [Note]
    var body: some View { List(notes) { Text($0.title) } }
}

// MVVM — pull this out when load/map/test need a type
@Observable
final class SearchModel {
    var query = ""
    func submit() async { /* debounce, cancel, map DTO */ }
}
```


**Потом обычно спрашивают**

- Куда в MV класть сеть, чтобы View не стал service locator?
- Когда @Query во View делает экран нетестируемым?
- Как мигрировать один экран с MV на ViewModel, не переписывая приложение?
- Предписывает ли команда SwiftUI MVC / MVVM / VIPER?

</details>

<h2 id="swiftui-mvvm">MVVM в SwiftUI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

View — структура, которая рисует стейт. **ViewModel** владеет правилами, загрузкой и маппингом — не типами View. В эпоху Combine это ObservableObject, которым владеешь через @StateObject и отдаёшь вниз. На iOS 17+ это может быть класс с @Observable в @State. В любом случае: View не зовёт API-сервис напрямую, ViewModel тестируется без окна, зависимости приходят через init (или маленькую фабрику), не синглтон, спрятанный в body. Навигацию и флаги шитов держи в ViewModel, если это часть флоу; чисто визуальный стейт (isPressed) — в @State на View. Типичная ошибка: ObservableObject на 400 строк, который просто второй View.



```swift
@Observable
final class ProfileModel {
    private let api: API
    var name = ""
    var isLoading = false

    init(api: API) { self.api = api }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        name = (try? await api.profile())?.name ?? ""
    }
}

struct ProfileView: View {
    @State private var model: ProfileModel
    var body: some View {
        Text(model.name)
            .task { await model.load() }
    }
}
```


**Потом обычно спрашивают**

- Где живёт NavigationPath — во View или в ViewModel?
- Как юнит-тестить ProfileModel без SwiftUI?
- Когда MVVM избыточен для статичного экрана?
- Чем это отличается от паттерна MV в сэмплах Apple?

</details>

<h2 id="observableobject-vs-observable">ObservableObject vs @Observable</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

ObservableObject + @Published — это Combine: любая published-запись шлёт objectWillChange, и SwiftUI инвалидирует каждый View, который держит объект. @Observable (Observation, iOS 17+) трекает **какие свойства прочитал body** и инвалидирует только этих зависимых. Меньше бойлерплейта: нет ObservableObject, нет @Published, нет @StateObject — инстанс кладёшь в @State или передаёшь, для биндингов берёшь @Bindable. Миграция не бесплатная: старые API (@EnvironmentObject, часть библиотек) всё ещё ждут ObservableObject. Типичная ошибка: обернуть @Observable в @StateObject или ждать, что @Published заработает на классе с @Observable.



```swift
@Observable
final class Cart {
    var count = 0
}

struct Badge: View {
    let cart: Cart
    var body: some View { Text("\(cart.count)") } // tracks `count` only
}
```


**Потом обычно спрашивают**

- Почему @Observable может пропустить рефреш, который ObservableObject сделал бы?
- Как наблюдать тип с @Observable из UIKit?
- Что заменяет @Bindable?

</details>

<h2 id="preference-key">PreferenceKey</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Environment гонит данные **вниз**. PreferenceKey гонит данные **вверх**: ребёнок пишет значение, предки редьюсят сиблингов и читают результат через onPreferenceChange. Так измеряют ребёнка, выравнивают подчёркивание с табом или собирают фреймы для своего индикатора скролла. Надо реализовать defaultValue и reduce — reduce сводит двух детей в стеке к одному числу (обычно max или +). Типичный промах: ставить preference на каждом кадре без reduce или тащить @Binding вверх по дереву и словить цикл.



```swift
struct HeightKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = max(value, nextValue())
    }
}

Text("Hi")
    .background(GeometryReader { Color.clear.preference(key: HeightKey.self, value: $0.size.height) })
    .onPreferenceChange(HeightKey.self) { height = $0 }
```


**Потом обычно спрашивают**

- Зачем reduce, если ребёнок один?
- PreferenceKey vs @Binding родителю — когда какой честнее?
- Как измерить, чтобы GeometryReader не растянул лейаут?

</details>

<h2 id="swiftui-vs-uikit">SwiftUI vs UIKit</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**UIKit** — императивный: ты сам держишь дерево вьюх, мутируешь его и пушишь контроллеры. **SwiftUI** — декларативный: возвращаешь View как функцию от стейта, фреймворк диффит это описание и обновляет пиксели. SwiftUI выигрывает на новых экранах, в превью и там, где в основном вёрстка плюс биндинги. UIKit по-прежнему держит годы API — богатый текст, часть коллекшн-лейаутов, тонкая анимация и всё, чего нет на твоём deployment target. Мост в одну сторону — UIViewRepresentable / UIViewControllerRepresentable, в другую — UIHostingController. На собеседовании хотят сосуществование, не победителя: UIKit-приложение может хостить фичи на SwiftUI, а SwiftUI-приложение всё равно уйдёт в UIKit на острых углах. Типичная ошибка: переписывать стабильный UIKit-флоу «потому что SwiftUI», без продуктовой причины.



```swift
struct RatingBadge: UIViewRepresentable {
    var value: Int

    func makeUIView(context: Context) -> UILabel {
        let label = UILabel()
        label.font = .preferredFont(forTextStyle: .caption1)
        return label
    }

    func updateUIView(_ label: UILabel, context: Context) {
        label.text = "★ \(value)"
    }
}
```


**Потом обычно спрашивают**

- Когда берёшь UIViewRepresentable, а когда переписываешь контрол?
- Как UIHostingController меняет UIKit-стек навигации?
- Какие фичи SwiftUI всё ещё требуют минимальную iOS, которую UIKit уже давно умеет?

</details>

<h2 id="uikit-representable">UIKit в SwiftUI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

UIViewRepresentable оборачивает UIView; UIViewControllerRepresentable — контроллер. Реализуешь makeUIView / updateUIView (и Coordinator для делегатов). Бери для карт, WKWebView, проверенного боем UITextView. Поверхность держи маленькой — не оборачивай всё приложение. Типичный промах: лейаут в updateUIView на каждом кадре или утечка делегата у Coordinator.



```swift
struct Web: UIViewRepresentable {
    let url: URL
    func makeUIView(context: Context) -> WKWebView { WKWebView() }
    func updateUIView(_ view: WKWebView, context: Context) {
        view.load(URLRequest(url: url))
    }
}
```


**Потом обычно спрашивают**

- Когда нужен Coordinator?
- updateUIView vs пересоздать View?
- Как запушить UIKit-контроллер из SwiftUI, не оборачивая его?

</details>

<h2 id="swiftui-lifecycle">Жизненный цикл View в SwiftUI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

У View в SwiftUI **двое часов**. Identity в дереве — сколько живут @State / @StateObject. Видимость — onAppear, onDisappear, .task. Ребёнок TabView может сохранить стейт, а onAppear стреляет каждый раз, когда возвращаешься на таб. body может пробежать много раз до первого onAppear. Init ребёнка бежит, когда бежит body родителя — поэтому моделью должен владеть @StateObject (или @State + @Observable), не init. Работу «загрузить один раз» закрывай флагом или .task(id:), привязанным к данным, а не фразой «я думал, onAppear — это viewDidLoad». Типичная ошибка: сеть в onAppear у строки List, которая появляется и пропадает при скролле.



```swift
struct FeedView: View {
    @State private var items: [Item] = []

    var body: some View {
        List(items) { Text($0.title) }
            .task {
                guard items.isEmpty else { return }
                items = (try? await API.feed()) ?? []
            }
    }
}
```


**Потом обычно спрашивают**

- Почему init может бежать чаще, чем onAppear?
- .task vs onAppear — что отменяется, когда View уходит?
- Как id: у .task меняет перезагрузку?
- Что такое identity View и когда сбрасывается @State?
- .refreshable vs .task для списка с pull-to-refresh?

</details>

<h2 id="observable-object-changes">Как ObservableObject сообщает об изменениях</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

У ObservableObject есть **objectWillChange** — ObservableObjectPublisher, который стреляет *до* того, как UI должен обновиться. Свойства с @Published шлют туда сами в willSet. Можно вызвать objectWillChange.send() самому, когда изменение — не присваивание stored-свойства: вычисляемое значение с файла, колбэк URLSession, мутация внутри вложенного класса. SwiftUI слушает, инвалидирует View, которые держат объект, и снова зовёт body. Подписчики Combine тоже могут слушать. Тайминг важен: это *will* change, поэтому чтения в том же ходе ещё могут увидеть старое значение — поэтому SwiftUI планирует рендер на потом. Типичная ошибка: слать objectWillChange после мутации или не слать вовсе, когда обошёл @Published.



```swift
final class Clock: ObservableObject {
    private(set) var ticks = 0
    private var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            guard let self else { return }
            self.objectWillChange.send()
            self.ticks += 1
        }
    }
}
```


**Потом обычно спрашивают**

- Почему паблишер willChange, а не didChange?
- Когда send() надо звать самому?
- Как макрос @Observable сообщает об изменении вместо этого?

</details>

<h2 id="swiftui-property-wrappers">Какой property wrapper брать в SwiftUI</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Сначала реши, **кто владеет source of truth**. @State — этот View владеет значением (или, на iOS 17+, инстансом @Observable). @StateObject — этот View владеет ObservableObject. @ObservedObject — владеет кто-то другой, ты только подписываешься. @EnvironmentObject / @Environment — пришло от предка, не через каждый init. @Binding — окно записи туда, кто владеет. Не инициализируй @ObservedObject var model = Model() во View. Не клади экранную модель в environment. На собеседовании хотят эту карту, не пересказ синтаксиса property wrapper.



```swift
struct Parent: View {
    @StateObject private var session = Session()
    @State private var query = ""

    var body: some View {
        SearchField(text: $query)
            .environmentObject(session)
    }
}

struct SearchField: View {
    @Binding var text: String
    var body: some View { TextField("Search", text: $text) }
}
```


**Потом обычно спрашивают**

- Почему @StateObject — владелец, а @ObservedObject — заёмщик?
- Когда брать @Environment, а не @EnvironmentObject?
- Как карта меняется с @Observable и @Bindable?

</details>

<h2 id="swiftui-rerender">Когда SwiftUI перерисовывает View</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

SwiftUI перезапускает body, когда **меняется то, от чего body зависит**, а не когда «экран обновился». Зависимости: @State / @Binding, которые прочитал, свойство @Observable, к которому реально прикоснулся, ObservableObject, который стрельнул objectWillChange, значения @Environment и родитель, который пересобрал тебя с новыми входами. Identity важна: новый .id или смена ключа ForEach — это *новый* View, стейт сбрасывается. @Observable может пропустить ребёнка, который грязное поле не читал; ObservableObject обычно нет. EquatableView — ручной пропуск, когда == говорит, что входы совпали. Типичный промах: Date() или случайный UUID в body, чтобы каждый тик родителя пересобирал строку, или винить SwiftUI за работу, которую начал в init.



```swift
struct Row: View {
    let title: String
    var body: some View { Text(title) } // rebuilds if `title` changes, not if a sibling does
}
```


**Потом обычно спрашивают**

- Почему @Observable инвалидирует меньше View, чем ObservableObject?
- Когда пересборка родителя всё равно форсит body ребёнка?
- .id(uuid) на поле формы — что ты только что сбросил?
- Environment-значение высоко в дереве — почему полприложения перезапускает body?
- SwiftUI Instrument Cause & Effect vs Self._printChanges — что первым?

</details>

<h2 id="views-are-structs">Почему View в SwiftUI — структуры</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

View в SwiftUI — **значения**. Структуру дёшево создать, у неё нет унаследованного stored-стейта, её копируют, пока дерево диффят. body — computed property: SwiftUI выбрасывает структуру и делает новую, когда меняется @State, наблюдаемая зависимость или выход родителя. Identity — *не* адрес в памяти, а структурная позиция плюс явный .id. Если бы View были классами, ты бы дрался с reference-семантикой (общая мутация, identity, которая переживает описание), и модель «UI — функция стейта» потекла бы. Цена: init — не хук жизни, а stored-свойства без врапперов не переживают рефреш. Типичная ошибка: положить класс с сайд-эффектом в свойство View без @StateObject / @State и удивляться, что он сбрасывается.



```swift
struct PriceLabel: View {
    let cents: Int
    // Recreated freely. Only @State / @Binding / @StateObject survive.

    var body: some View {
        Text(cents, format: .currency(code: "USD").precision(.fractionLength(2)))
    }
}
```


**Потом обычно спрашивают**

- Как SwiftUI решает, что два значения View — «тот же» View?
- Почему body — computed property, а не сохранённое дерево?
- Что сломается, если View будет классом?

</details>

<h2 id="programmatic-navigation">Программная навигация</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Программная навигация значит, что *source of truth* — данные, а не тап по NavigationLink. На iOS 16+ это **path у NavigationStack**: NavigationPath или типизированный биндинг [Route]. append — пуш, removeLast — поп, экраны регистрируешь через navigationDestination(for:). Линк может писать в тот же path. Старые NavigationLink(isActive:) и selection-биндинги у NavigationView ещё работают, но deprecated и легко разъезжаются. Шиты и full-screen cover — другой биндинг (item: / isPresented:), не path стека. Типичные ошибки: пушить, собрав линк, который никогда не показываешь, и хранить path только в ребёнке — тогда кнопка назад и модель спорят.



```swift
enum Route: Hashable { case detail(id: String) }

struct Inbox: View {
    @State private var path = [Route]()

    var body: some View {
        NavigationStack(path: $path) {
            Button("Open") { path.append(.detail(id: "42")) }
                .navigationDestination(for: Route.self) { route in
                    switch route {
                    case .detail(let id): Text(id)
                    }
                }
        }
    }
}
```


**Потом обычно спрашивают**

- Как попасть в корень через NavigationPath?
- Когда sheet(item:), а не пуш?
- Что ломалось у NavigationLink(isActive:) в List?
- Почему NavigationStack заменил NavigationView?
- Как попнуть несколько уровней (или в корень) за один раз?

</details>

<h2 id="anyview">AnyView</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

AnyView — type erasure для View. Можно вернуть разные конкретные View из одной функции ценой **identity и специализации**: SwiftUI видит коробку, диффы хуже, body сложнее пропустить. Лучше @ViewBuilder, Group или enum направлений, чтобы каждая ветка осталась настоящим типом. AnyView в строке List на собеседовании — запах. Типичный промах: обернуть каждую ячейку «чтобы компилятор был доволен» и потом удивляться, почему скролл дёргается.



```swift
@ViewBuilder
func badge(isOn: Bool) -> some View {
    if isOn { Image(systemName: "star.fill") }
    else { EmptyView() }
}
// Avoid: AnyView(isOn ? AnyView(Image(...)) : AnyView(EmptyView()))
```


**Потом обычно спрашивают**

- Когда AnyView всё ещё честный инструмент?
- Как это связано с some View vs any View?
- Что будет с identity View, когда тип в коробке меняется?
- Протокол из другого модуля, который возвращает some View vs AnyView — что прячет тип без коробки?

</details>

<h2 id="lazyvgrid">LazyVGrid</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

LazyVGrid раскладывает элементы по колонкам и **создаёт View, когда они появляются**. Колонки — [GridItem]: .flexible() делит место, .adaptive(minimum:) набивает сколько влезет, .fixed — ширина в пикселях. Пара с ForEach и стабильными id. LazyHGrid — та же идея боком. Это не compositional layout UICollectionView: полного flow-API нет, оффскрин-ячейки — не reuse-очередь, которую ты конфигурируешь. Типичный промах: обычный VStack из 200 картинок или .adaptive с огромным minimum — одна колонка, и непонятно почему.



```swift
let columns = [GridItem(.adaptive(minimum: 120), spacing: 8)]

LazyVGrid(columns: columns, spacing: 8) {
    ForEach(photos) { photo in
        PhotoCell(photo)
    }
}
```


**Потом обычно спрашивают**

- .flexible vs .adaptive vs .fixed?
- Когда всё ещё хочешь UICollectionView?
- Как переключить список и сетку, не сбросив скролл?

</details>

<h2 id="view-modifier">ViewModifier</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

ViewModifier — переиспользуемое преобразование: func body(content: Content) -> some View. Вешаешь через .modifier(CardStyle()) или расширение View, которое прячет тип. Бери, когда одни и те же padding + background + accessibility всплывают на многих экранах. Обычной функции, которая возвращает some View, хватает для разового случая. Типичный промах: модификатор, который захватывает @State, которым не владеет, или оборачивать каждый однострочный .font в тип.



```swift
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

extension View {
    func card() -> some View { modifier(CardStyle()) }
}
```


**Потом обычно спрашивают**

- Модификатор vs обёрточный View vs расширение View?
- Как передать Binding в модификатор?
- Меняет ли модификатор identity View?

</details>

<h2 id="matched-geometry">matchedGeometryEffect</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

matchedGeometryEffect говорит SwiftUI, что два View в разных деревьях — **одна и та же вещь** для анимации: превью в сетке и герой на деталке делят namespace id. SwiftUI интерполирует фрейм (и опционально другие свойства) через переход. Оба конца должны быть в иерархии во время анимации, id — уникален в этом Namespace. Типичный промах: матчить тип, который пересоздаётся каждый кадр, или ждать анимацию пуша навигации без общего namespace с обеих сторон.



```swift
struct Gallery: View {
    @Namespace private var ns
    @State private var selected: Item?

    var body: some View {
        Thumb(item: item)
            .matchedGeometryEffect(id: item.id, in: ns)
            .onTapGesture { selected = item }
            .fullScreenCover(item: $selected) { item in
                Hero(item: item)
                    .matchedGeometryEffect(id: item.id, in: ns)
            }
    }
}
```


**Потом обычно спрашивают**

- Что меняет isSource:?
- Почему это падает через пуш NavigationStack без общего namespace?
- Когда более новый API — свой matchedTransitionSource / zoom transition?

</details>

### Senior

<h2 id="attribute-graph">AttributeGraph</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

SwiftUI не держит твои структуры View живыми. Он держит **AttributeGraph**: узлы — атрибуты (body, коробка @State, вход родителя), рёбра — **зависимости**. Структура, которую ты пишешь, — значение, которое копируют в эти атрибуты; **identity живёт на атрибуте**, не на временной структуре. Когда стейт меняется, SwiftUI помечает зависимые атрибуты устаревшими и на следующем кадре перезапускает только эти body. Выход графа — **DisplayList** (что рисовать); этот список ты сам не собираешь. Граф Cause & Effect в SwiftUI Instrument — эта цепочка зависимостей, сделанная видимой. Типичный промах: «SwiftUI диффит дерево View, как UIKit диффит ячейки» или делать форматтер / декод внутри body, потому что структура казалась вечно дешёвой.



```text
Tap → @State attribute dirty → body attribute outdated → new Text value
     → styling attributes → DisplayList → pixels
Cause & Effect: gesture → State → YourView.body (count of updates on the edge)
```


**Потом обычно спрашивают**

- Identity атрибута vs значение View — кто владеет @State?
- Почему длинный body даёт хитч, даже если граф пропустил другие View?
- SWIFTUI_PRINT_TREE / DisplayList — игрушка для собеса или прод-инструмент?

</details>

<h2 id="view-identity">Идентичность View vs свойство с ViewBuilder</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

**Отдельная структура View** — свой узел графа: своя identity, свой набор зависимостей, может скипнуться, когда родитель бежит. **Computed property** с @ViewBuilder инлайнится в родителя — пересчитывается вместе с ним. Выноси тип, когда у куска есть стейт или он должен обновляться отдельно. Identity также дают id у ForEach и .id(...): сменил id — SwiftUI считает это **новым** View (стейт сбрасывается). Типичный промах: body на 200 строк из хелпер-свойств и удивление, почему один @State у родителя перерисовывает всё.



```swift
struct Screen: View {
    var header: some View { Header() }          // inlined — runs with Screen
    var body: some View {
        VStack {
            header
            Detail()                            // own identity
        }
    }
}
```


**Потом обычно спрашивают**

- Когда computed some View всё ещё правильный разрез?
- .id(UUID()) в body — что ты уничтожил?
- Как это связано с тем, что lazy-стеки префетчат body *следующей* ячейки?

</details>

<h2 id="equatable-view">EquatableView</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

По умолчанию body ребёнка может перезапуститься, когда перезапустился родитель, даже если входы ребёнка не менялись. Если View конформит Equatable и обернуть его .equatable() (или EquatableView), SwiftUI зовёт == и **пропускает body**, когда равно. Пиши == по тем данным, которые реально рисуешь — игнорируй дебаг-таймстамп, если строка его не показывает. У самого == есть цена; выигрывает на дорогих строках, не на одном Text. Типичный промах: законформить Equatable и забыть .equatable() или написать ==, который врёт и оставляет UI протухшим.



```swift
struct Row: View, Equatable {
    let title: String
    static func == (lhs: Row, rhs: Row) -> Bool { lhs.title == rhs.title }
    var body: some View { Text(title) }
}

Row(title: item.title).equatable()
```


**Потом обычно спрашивают**

- Чем это отличается от того, как @Observable пропускает непрочитанные свойства?
- Когда оверхед == не стоит того?
- Можно ли нарочно игнорировать поле в ==?

</details>
