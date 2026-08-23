# Хранение

16 карточек · 8 часто спрашивают · [persistence.md](../../topics/persistence.md)

### Junior

<h2 id="codable">Codable</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Codable — typealias на Encodable и Decodable. Тип с конформом можно превратить во внешнее представление и обратно — обычно JSON через JSONEncoder / JSONDecoder, иногда plist. Компилятор синтезирует методы, если каждое stored-свойство само Codable. Перехватываешь через enum CodingKeys или пишешь encode(to:) и init(from:). Codable — не формат файла и не база; I/O делает encoder или decoder.

Типичные промахи: force-try на decode; оставить Date на дефолтной стратегии; повесить UIImage или замыкание на модель и удивляться, почему синтез не взлетел.



```swift
struct User: Codable {
    let id: Int
    let displayName: String

    enum CodingKeys: String, CodingKey {
        case id
        case displayName = "display_name"
    }
}

let user = try JSONDecoder().decode(User.self, from: jsonData)
let data = try JSONEncoder().encode(user)
```


**Потом обычно спрашивают**

- Когда пишешь CodingKeys, а не надеешься на синтез?
- Как декодировать дату, которая пришла ISO-8601 строкой?
- Что будет, если non-optional свойства нет в JSON?
- Как декодировать гетерогенный массив — type плюс payload?
- Codable — это что-то большее, чем Encodable и Decodable?

</details>

<h2 id="userdefaults">UserDefaults — куда можно и нельзя</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

UserDefaults — маленький key-value на plist для настроек. Нормально: флаги онбординга, последняя вкладка, отображаемое имя, timestamp кэша, настройки App Group для расширения. Плохо: картинки, большой JSON, документы пользователя или что-то секретное — токены живут в Keychain. Core Data / SwiftData берёшь, когда есть список записей, связи, предикаты или undo — не когда три булева. Записи коалесятся и сбрасываются позже: это не транзакции и не база. Читать в тесном цикле или запихнуть весь граф модели в Data — запах. Нужны запросы, миграции или шифрование — ты из него вырос.



```swift
let defaults = UserDefaults.standard
defaults.set(true, forKey: "hasSeenOnboarding")
let seen = defaults.bool(forKey: "hasSeenOnboarding")

// Wrong: large or secret payloads
// defaults.set(image.jpegData(compressionQuality: 0.8), forKey: "avatar")
// defaults.set(token, forKey: "authToken")
```


**Потом обычно спрашивают**

- Как шарить default с виджетом или app extension?
- Почему UserDefaults плохое место для auth token?
- Что будет, если положить очень большой Data?
- Когда берёшь Core Data вместо UserDefaults?
- Как тестировать код, который читает UserDefaults, без настоящей suite?

</details>

<h2 id="persist-options">Как на iOS хранят данные</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Инструмент называешь по размеру и форме, не по привычке. UserDefaults — флаги и крошечные настройки. Keychain — секреты. Файлы через FileManager, Caches / Documents / App Group — картинки, экспорты, офлайн-паки. Codable плюс диск — JSON-документ, которым владеешь. Core Data / SwiftData — графы объектов, запросы, связи. CloudKit — записи с синком пользователя. URLCache — это HTTP, не твоя модель. На собесе хотят дерево решений и что будет при удалении приложения / нехватке места. Типичный промах: запихнуть ленту в UserDefaults или токены в plist.



```text
onboarding seen     → UserDefaults
auth token          → Keychain
camera draft        → Files (Caches or Documents)
notes with search   → SwiftData / Core Data
shared shopping list → CloudKit or your API
```


**Потом обычно спрашивают**

- Documents и Caches — что система может стереть?
- Когда файла плюс Codable хватает против Core Data?
- Что переживает удаление приложения?

</details>

<h2 id="list-directory">Список файлов в директории</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

API — FileManager. contentsOfDirectory возвращает непосредственных детей папки как URL. Для рекурсии — enumerator, чтобы пропускать скрытые файлы и содержимое пакетов. Предпочитай URL строковым путям. Resource keys проси сразу — isRegularFileKey, fileSizeKey, contentModificationDateKey — чтобы потом не делать stat на каждый файл. Частые косяки: листить бандл приложения вместо Documents; считать, что директория уже есть; гулять по огромному дереву на главном потоке.



```swift
let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
let files = try FileManager.default.contentsOfDirectory(
    at: docs,
    includingPropertiesForKeys: [.isRegularFileKey, .fileSizeKey],
    options: [.skipsHiddenFiles]
)
```


**Потом обычно спрашивают**

- Как листить рекурсивно и не тащить все URL сразу?
- Documents, Caches, Temporary — что куда класть?
- Как отличить файл от подпапки по resource values?

</details>

### Mid

<h2 id="cloudkit-vs-core-data">CloudKit и Core Data</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Core Data — локальный граф объектов и стек персистенции: модель, стор и контексты твои. CloudKit — iCloud-база Apple: CKRecord, private/public/shared базы, подписки, синк в рамках аккаунта. Это разные вопросы. Core Data или SwiftData — когда источник правды устройство, нужны связи, fault и локальные запросы. CloudKit — когда источник правды iCloud, нужен синк между девайсами или шаринг. NSPersistentCloudKitContainer может зеркалить стор Core Data в private-базу CloudKit: это мост, не удалённый NSManagedObjectContext. Смена схемы, конфликты и офлайн-очереди остаются твоими, если этот контейнер сам не зеркалит.



```swift
let local = NSPersistentContainer(name: "App")
local.loadPersistentStores { _, error in
    precondition(error == nil)
}

let mirrored = NSPersistentCloudKitContainer(name: "App")
mirrored.loadPersistentStores { _, error in
    precondition(error == nil)
}
```


**Потом обычно спрашивают**

- Чего NSPersistentCloudKitContainer не синкает — public DB, шары, большие ассеты?
- Что делаешь с пользователем, который вышел из iCloud?
- Когда говоришь с CloudKit через CKDatabase, а не через Core Data?

</details>

<h2 id="core-data">Core Data</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Core Data — фреймворк персистенции объектного графа, не «SQLite с объектами». Сущности и связи описываешь в модели. NSPersistentContainer грузит стор и выдаёт NSManagedObjectContext; фетчишь NSFetchRequest, меняешь сабклассы NSManagedObject. Faulting подгружает связанные объекты лениво. View context — для UI; тяжёлая работа — на private-queue контексте, потом save и merge. Managed object привязан к очереди, которая его создала или зафетчила: переход через очереди — краш, не ворнинг. На собесе ещё хотят save на том контексте, который сделал изменение, и что стереть файл или запихнуть блобы в UserDefaults — не замена этому стеку.



```swift
let container = NSPersistentContainer(name: "Store")
container.loadPersistentStores { _, error in
    if let error { fatalError("\(error)") }
}

let request = NSFetchRequest<NSManagedObject>(entityName: "Note")
request.sortDescriptors = [NSSortDescriptor(key: "updatedAt", ascending: false)]
let notes = try container.viewContext.fetch(request)
```


**Потом обычно спрашивают**

- Main-queue и private-queue контекст — кто сейвит, кто мержит?
- Что такое fault и когда он стреляет?
- Как мигрировать модель и не потерять данные пользователя?
- Почему NSManagedObject нельзя спокойно сунуть в Task?
- SQLite, binary и in-memory стор — когда какой?
- Что NSFetchedResultsController добавляет поверх фетча?

</details>

<h2 id="swiftdata">SwiftData</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

SwiftData — нативная персистенция Apple на Swift: классы @Model, ModelContainer и @Query в SwiftUI. Под капотом всё ещё стор, на девайсе SQLite, с контекстом — не магия. По сравнению с Core Data меньше бойлерплейта, но думать всё равно контекстами, fault и фоновыми записями: @Model — класс, поэтому identity и правила потоков важны. Берёшь для локальных реляционных данных, которые хочешь фетчить предикатами. Не делай из него большой UserDefaults. Синк CloudKit есть, но это продуктовое решение, не дефолт.

Классические косяки: перетащить объект модели через потоки; считать @Query view-model.



```swift
@Model
final class Note {
    var title: String
    var createdAt: Date
    init(title: String) {
        self.title = title
        self.createdAt = .now
    }
}

struct NotesView: View {
    @Query(sort: \Note.createdAt, order: .reverse) private var notes: [Note]
    var body: some View { List(notes) { Text($0.title) } }
}
```


**Потом обычно спрашивают**

- Когда всё ещё берёшь Core Data вместо SwiftData?
- Как сделать фоновый insert и не трогать view context?
- @Query и фетч во view model — что тестируется?
- VersionedSchema / SchemaMigrationPlan — когда lightweight-миграция врёт?

</details>

<h2 id="core-data-migration">Миграция Core Data</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Модель версионируешь: Editor → Add Model Version. Lightweight-миграция — флаги NSMigratePersistentStoresAutomaticallyOption и NSInferMappingModelAutomaticallyOption — закрывает аддитивные изменения: новые optional-атрибуты, новые сущности, переименованное свойство с renaming ID. Heavy / custom mapping — когда форму меняешь: разрезать сущность, сменить кардинальность связи, трансформировать значения. Пишешь mapping model или NSEntityMigrationPolicy и гоняешь на копии настоящего стора. Стереть стор можно только до первого шипа. Править текущий xcdatamodel на месте без версии — как закирпичить пользователей. Типичный промах: «lightweight выведет что угодно» после того, как удалил сущность, которая в старом сторе ещё есть.



```swift
let options = [
    NSMigratePersistentStoresAutomaticallyOption: true,
    NSInferMappingModelAutomaticallyOption: true
]
try container.persistentStoreCoordinator.addPersistentStore(
    ofType: NSSQLiteStoreType,
    configurationName: nil,
    at: storeURL,
    options: options
)
```


**Потом обычно спрашивают**

- Lightweight и своя mapping model — по одному примеру?
- Что даёт renaming identifier?
- Как тестировать миграцию, не стирая телефон тестера?

</details>

<h2 id="key-decoding-strategies">Стратегии ключей при декоде</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

JSONDecoder.keyDecodingStrategy говорит, как строки ключей JSON сопоставляются с CodingKeys. Дефолт useDefaultKeys требует точного совпадения. convertFromSnakeCase мапит user_id на userId, чтобы Swift остался camelCase без enum CodingKeys. custom — для префиксов, сплющенной вложенности или разовых алиасов, которые правило snake-case не выразит. На энкоде зеркало — keyEncodingStrategy convertToSnakeCase. Это не dateDecodingStrategy и не dataDecodingStrategy: те конвертят значения, не имена. Snake-case не спасёт, когда имена значат разное — id и identifier: тут всё равно нужны CodingKeys.



```swift
struct Payload: Codable {
    let userId: Int
    let createdAt: String
}

let decoder = JSONDecoder()
decoder.keyDecodingStrategy = .convertFromSnakeCase
let payload = try decoder.decode(Payload.self, from: jsonData)
// JSON: { "user_id": 1, "created_at": "..." }
```


**Потом обычно спрашивают**

- Что convertFromSnakeCase делает с подряд идущими подчёркиваниями или ведущим _?
- Когда enum CodingKeys всё равно нужен после стратегии?
- Как смешать глобальную стратегию и одно свойство, которое конвертить нельзя?

</details>

<h2 id="core-data-vs-sqlite">Core Data, SQLite и Realm</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

SQLite — SQL-файл, который запрашиваешь сам: sqlite3, GRDB. Для Core Data объектный граф, который может сидеть на SQLite — fault, контексты, миграции, не «просто SQL». Realm — сторонняя объектная база с живыми объектами и своим форматом файла. SQLite/GRDB — когда хочешь SQL и простые файлы. Core Data / SwiftData — когда хочешь стек Apple и FRC. Realm — только если команда его уже знает, это ещё один вендор. Типичный промах: «Core Data — медленный SQLite» или ждать, что Core Data зашифрован по умолчанию. Нет: добавляешь SQLCipher или file protection.



```text
Need raw SQL reports     → SQLite / GRDB
Need object graph + UI   → Core Data / SwiftData
Need live objects, team knows Realm → Realm
Need encryption at rest  → say so; none of these is magic
```


**Потом обычно спрашивают**

- Core Data зашифрован?
- Как передать managed object через очереди?
- Когда Realm — ловушка на greenfield?

</details>

<h2 id="core-data-delete-rules">Delete rules в Core Data</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Delete rule у связи говорит, что будет с другой стороной, когда удаляешь объект. Nullify — дефолт: бросаешь указатель, другой объект оставляешь. Cascade: удаляешь связанные тоже, папка тянет за собой заметки. Deny: отказ удалять, если кто-то ещё сюда указывает. No Action: ничего не делать — можно оставить висячие ссылки, почти никогда не то, что нужно. Типичный промах: cascade на many-to-many и снести половину стора.



```text
Folder.notes = Cascade
Note.folder = Nullify
User.profile = Deny if a profile must not exist without a user
```


**Потом обычно спрашивают**

- Cascade и nullify на parent-child?
- Что Deny делает с context.save?
- Как проверить, что не оставил сирот?

</details>

<h2 id="nsfetchrequest">NSFetchRequest</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NSFetchRequest — объект запроса, который отдаёшь контексту: имя сущности или тип, опциональный NSPredicate, sortDescriptors, fetchLimit / fetchOffset и resultType — managed objects, object ID, словари, count. Faulting и relationshipKeyPathsForPrefetching решают, сколько графа вытащишь. Запрос без сорта законен для сырого фетча; NSFetchedResultsController сорт требует. Типичный промах: зафетчить все Note на main-контексте и отфильтровать в Swift.



```swift
let request = NSFetchRequest<Note>(entityName: "Note")
request.predicate = NSPredicate(format: "isPinned == YES")
request.sortDescriptors = [NSSortDescriptor(key: "updatedAt", ascending: false)]
request.fetchLimit = 20
let notes = try context.fetch(request)
```


**Потом обычно спрашивают**

- Когда фетчишь object ID вместо объектов?
- Как не словить N+1 на связи?
- Почему FRC отказывается от запроса без сорта?

</details>

<h2 id="fetched-results-controller">NSFetchedResultsController</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NSFetchedResultsController сидит на fetch request плюс контексте и говорит table/collection view, когда результат изменился: controllerDidChangeContent, точечные insert/delete/move. Умеет секции по key path и кэшировать информацию о секциях. cellForRow всё равно твой. Diffable data source плюс пайплайн SwiftData / Combine в новом коде часто заменяют FRC; на собесе UIKit плюс Core Data дефолт всё ещё FRC. Типичный промах: view context на огромный нефильтрованный фетч или игнор didChange и reload всей таблицы.



```swift
let request = NSFetchRequest<Note>(entityName: "Note")
request.sortDescriptors = [NSSortDescriptor(key: "updatedAt", ascending: false)]
let frc = NSFetchedResultsController(fetchRequest: request,
                                     managedObjectContext: context,
                                     sectionNameKeyPath: nil,
                                     cacheName: nil)
try frc.performFetch()
```


**Потом обычно спрашивают**

- Почему у фетча обязан быть sort descriptor?
- FRC и diffable snapshot, который собираешь сам?
- Можно ли FRC на private-queue контексте для UI?

</details>

<h2 id="nspredicate">NSPredicate</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NSPredicate — объект запроса: format-строка плюс аргументы, которые умеют Core Data, NSFetchRequest и часть Cocoa-коллекций. %K — key path, %@ — значение. Склеиваешь AND / OR или собираешь NSCompoundPredicate. Бери #keyPath и NSPredicate(format:), не конкатенируй пользовательские строки — инъекция реальна. SwiftData и современный Core Data ещё принимают макросы Predicate, они type-safe. Типичный косяк: predicateWithFormat и интерполяция поисковой строки прямо в format.



```swift
let request = NSFetchRequest<NSManagedObject>(entityName: "Note")
request.predicate = NSPredicate(format: "%K CONTAINS[cd] %@", #keyPath(Note.title), query)
```


**Потом обычно спрашивают**

- %K и %@?
- Как сказать «в этом наборе id»?
- NSPredicate и Swift Predicate / #Predicate?

</details>

<h2 id="nscoding">NSCoding и архивация</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NSCoding / NSSecureCoding — старый Cocoa-архив: объект пишет ключи в NSCoder, NSKeyedArchiver превращает граф в Data. NSSecureCoding требует назвать ожидаемые классы, чтобы хитро сделанный файл не инстанцировал что попало. Новый код предпочитает Codable или SwiftData. Архивы всё ещё встречаешь в Data-блобах UserDefaults, старых документах и state restoration. Типичный промах: небезопасный unarchiveObject на данных, которые сам только что не писал.



```swift
let data = try NSKeyedArchiver.archivedData(withRootObject: colors, requiringSecureCoding: true)
let colors = try NSKeyedUnarchiver.unarchivedObject(ofClasses: [NSArray.self, UIColor.self], from: data)
```


**Потом обычно спрашивают**

- NSCoding и Codable — когда какой вынужден?
- Что предотвращает requiringSecureCoding?
- Почему стор Core Data — не «просто архив»?

</details>

<h2 id="sort-descriptor">NSSortDescriptor</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NSSortDescriptor описывает один ключ сортировки и направление. Fetch request Core Data, NSFetchedResultsController и коллекции Foundation принимают массив: более ранние дескрипторы побеждают на ничьих. Сортируешь по key path, селектору вроде localizedStandardCompare или блоку-компаратору. В Swift типизированная обёртка — SortDescriptor; крючок всё равно обычно NSFetchRequest.sortDescriptors. Сортировка по ключу, которого нет в сущности, падает в момент фетча. Зафетчить всё и отсортировать в памяти — ловушка на большой таблице: толкай сорт в стор по индексированному атрибуту.



```swift
let byName = NSSortDescriptor(
    key: "name",
    ascending: true,
    selector: #selector(NSString.localizedStandardCompare(_:))
)
let byDate = NSSortDescriptor(key: "createdAt", ascending: false)
request.sortDescriptors = [byName, byDate]
```


**Потом обычно спрашивают**

- Как сортировать по атрибуту связи?
- SortDescriptor и NSSortDescriptor — когда нужен класс?
- Почему дескриптор на компараторе не поедет в SQLite-сторе?

</details>
