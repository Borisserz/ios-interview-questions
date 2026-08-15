# Persistence

- [Codable](#codable)
- [Key decoding strategies](#key-decoding-strategies)
- [CloudKit vs Core Data](#cloudkit-vs-core-data)
- [Core Data](#core-data)
- [UserDefaults — good and bad uses](#userdefaults)
- [Listing files in a directory](#list-directory)
- [NSSortDescriptor](#sort-descriptor)
- [SwiftData](#swiftdata)
- [NSPredicate](#nspredicate)
- [NSFetchRequest](#nsfetchrequest)
- [NSFetchedResultsController](#fetched-results-controller)
- [NSCoding and archiving](#nscoding)
- [How you persist data on iOS](#persist-options)
- [Core Data delete rules](#core-data-delete-rules)
- [Core Data vs SQLite vs Realm](#core-data-vs-sqlite)
- [Core Data migration](#core-data-migration)

## Codable {#codable}

- Level: Junior
- Frequency: High

### Answer

`Codable` is the typealias for `Encodable & Decodable`. A type that conforms can be turned into an external representation and back — usually JSON through `JSONEncoder` / `JSONDecoder`, sometimes a property list. The compiler synthesizes the methods when every stored property is itself `Codable`. You take over with a `CodingKeys` enum or by writing `encode(to:)` and `init(from:)`. Codable is not a file format and not a database; an encoder or decoder does the I/O. Typical misses: force-trying `decode`, leaving `Date` on the default strategy, and putting `UIImage` or a closure on a model and wondering why synthesis fails.

### Example

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

### Follow-ups

- When do you write `CodingKeys` instead of relying on synthesis?
- How do you decode a date that is an ISO-8601 string?
- What happens if a non-optional property is missing from the JSON?
- How would you decode a heterogeneous array (`type` + payload)?
- Is `Codable` anything more than `Encodable & Decodable`?

## Key decoding strategies {#key-decoding-strategies}

- Level: Mid
- Frequency: High

### Answer

`JSONDecoder.keyDecodingStrategy` controls how JSON key strings are matched to `CodingKeys`. The default, `.useDefaultKeys`, demands an exact match. `.convertFromSnakeCase` maps `user_id` onto `userId` so Swift can stay camelCase without a `CodingKeys` enum. `.custom` is for prefixes, flattened nesting, or one-off aliases the snake-case rule cannot express. Encoding has the counterpart `keyEncodingStrategy` (`.convertToSnakeCase`). This is not `dateDecodingStrategy` or `dataDecodingStrategy` — those convert values, not names. Snake-case conversion will not save you when the names differ in meaning (`id` vs `identifier`); that still needs `CodingKeys`.

### Example

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

### Follow-ups

- What does `.convertFromSnakeCase` do with consecutive underscores or leading `_`?
- When is a `CodingKeys` enum still required after setting a strategy?
- How do you mix a global strategy with one property that should not be converted?

## CloudKit vs Core Data {#cloudkit-vs-core-data}

- Level: Mid
- Frequency: High

### Answer

Core Data is a local object graph and persistence stack: you own the model, the store, and the contexts. CloudKit is Apple's iCloud database — `CKRecord`, private/public/shared databases, subscriptions, and account-scoped sync. They answer different questions. Use Core Data (or SwiftData) when the device is the source of truth and you need relationships, faults, and local queries. Use CloudKit when iCloud is the source of truth and you need multi-device sync or sharing. `NSPersistentCloudKitContainer` can mirror a Core Data store into a CloudKit private database; it is a bridge, not a remote `NSManagedObjectContext`. Schema changes, conflicts, and offline queues stay your problem unless that container is doing the mirroring.

### Example

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

### Follow-ups

- What does `NSPersistentCloudKitContainer` not sync (public DB, shares, large assets)?
- How do you handle a user who is signed out of iCloud?
- When would you talk to CloudKit with `CKDatabase` instead of Core Data?

## Core Data {#core-data}

- Level: Mid
- Frequency: High

### Answer

Core Data is an object-graph persistence framework, not “SQLite with objects.” You describe entities and relationships in a model. `NSPersistentContainer` loads the store and vends `NSManagedObjectContext` instances; you fetch with `NSFetchRequest` and mutate `NSManagedObject` subclasses. Faulting loads related objects lazily. The view context is for UI; heavy work belongs on a private-queue context, then you save and merge. A managed object is confined to the queue that created or fetched it — crossing queues is a crash, not a warning. Interviewers also want `save()` on the context that made the change, and that wiping a file or stuffing blobs into `UserDefaults` is not a substitute for this stack.

### Example

```swift
let container = NSPersistentContainer(name: "Store")
container.loadPersistentStores { _, error in
    if let error { fatalError("\(error)") }
}

let request = NSFetchRequest<NSManagedObject>(entityName: "Note")
request.sortDescriptors = [NSSortDescriptor(key: "updatedAt", ascending: false)]
let notes = try container.viewContext.fetch(request)
```

### Follow-ups

- Main-queue vs private-queue context — who saves, who merges?
- What is a fault, and when does it fire?
- How do you migrate a model without losing user data?
- Why is `NSManagedObject` not safe to pass into a `Task`?
- SQLite vs binary vs in-memory store — when do you pick each?
- What does `NSFetchedResultsController` add on top of a fetch?

## UserDefaults — good and bad uses {#userdefaults}

- Level: Junior
- Frequency: High

### Answer

`UserDefaults` is a small, plist-backed key-value store for preferences. Good uses: onboarding flags, last selected tab, a display name, a cache timestamp, App Group settings shared with an extension. Bad uses: images, large JSON, documents the user created, or anything secret — tokens belong in the Keychain. **Reach for Core Data / SwiftData** when you have a list of records, relationships, predicates, or undo — not when you have three booleans. Writes are coalesced and flushed later; it is not transactional and not a database. Reading it in a tight loop or encoding a whole model graph into `Data` is a smell. If you need queries, migrations, or encryption, you have outgrown it.

### Example

```swift
let defaults = UserDefaults.standard
defaults.set(true, forKey: "hasSeenOnboarding")
let seen = defaults.bool(forKey: "hasSeenOnboarding")

// Wrong: large or secret payloads
// defaults.set(image.jpegData(compressionQuality: 0.8), forKey: "avatar")
// defaults.set(token, forKey: "authToken")
```

### Follow-ups

- How do you share a default with a widget or an app extension?
- Why is `UserDefaults` a poor place for an auth token?
- What happens if you store a very large `Data` value?
- When do you pick Core Data over `UserDefaults`?
- How do you test code that reads `UserDefaults` without the real suite?

## Listing files in a directory {#list-directory}

- Level: Junior
- Frequency: Medium

### Answer

`FileManager` is the API. `contentsOfDirectory(at:includingPropertiesForKeys:options:)` returns the immediate children of a folder as URLs. For a recursive walk, use `enumerator(at:includingPropertiesForKeys:options:)` so you can skip hidden files and package contents. Prefer URLs over `String` paths. Request resource keys up front (`isRegularFileKey`, `fileSizeKey`, `contentModificationDateKey`) to avoid a stat per file later. Common mistakes: listing the app bundle when you meant Documents, assuming the directory already exists, and walking a huge tree on the main thread.

### Example

```swift
let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
let files = try FileManager.default.contentsOfDirectory(
    at: docs,
    includingPropertiesForKeys: [.isRegularFileKey, .fileSizeKey],
    options: [.skipsHiddenFiles]
)
```

### Follow-ups

- How do you list files recursively without loading every URL at once?
- Documents vs Caches vs Temporary — what belongs in each?
- How do you tell a file from a subdirectory with resource values?

## NSSortDescriptor {#sort-descriptor}

- Level: Mid
- Frequency: Low

### Answer

`NSSortDescriptor` describes one sort key and a direction. Core Data fetch requests, `NSFetchedResultsController`, and Foundation collections take an array of them; earlier descriptors win on ties. You can sort by a key path, a selector (`localizedStandardCompare`), or a comparator block. In Swift, `SortDescriptor` is the typed wrapper; `NSFetchRequest.sortDescriptors` is still the usual hook. Sorting on a key that is not in the entity fails at fetch time. Fetching everything and sorting in memory is the trap when the table is large — push the sort into the store on an indexed attribute.

### Example

```swift
let byName = NSSortDescriptor(
    key: "name",
    ascending: true,
    selector: #selector(NSString.localizedStandardCompare(_:))
)
let byDate = NSSortDescriptor(key: "createdAt", ascending: false)
request.sortDescriptors = [byName, byDate]
```

### Follow-ups

- How do you sort on a relationship’s attribute?
- `SortDescriptor` vs `NSSortDescriptor` — when do you need the class?
- Why can a comparator-based descriptor not run in a SQLite store?

## SwiftData {#swiftdata}

- Level: Mid
- Frequency: High

### Answer

SwiftData is Apple’s Swift-native persistence: `@Model` classes, a `ModelContainer`, and `@Query` in SwiftUI. Under the hood it is still a store (SQLite on device) with a context, not magic. Compared with Core Data you write less boilerplate, but you still think in contexts, faults, and background writes — a `@Model` is a class, so identity and threading rules matter. Use it for local relational data you want to fetch with predicates. Do not use it as a bigger `UserDefaults`. CloudKit sync exists but is a product decision, not a default. Typical mistakes: hopping a model object across threads, and treating `@Query` as a view-model.

### Example

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

### Follow-ups

- When do you still pick Core Data over SwiftData?
- How do you do a background insert without touching the view context?
- `@Query` vs fetching in a view model — which is testable?
- `VersionedSchema` / `SchemaMigrationPlan` — when is lightweight migration a lie?

## NSPredicate {#nspredicate}

- Level: Mid
- Frequency: Medium

### Answer

`NSPredicate` is a query object: a format string plus arguments that Core Data, `NSFetchRequest`, and some Cocoa collections can evaluate. `%K` is a key path, `%@` is a value. Compound with `AND` / `OR`, or build with `NSCompoundPredicate`. Prefer `#keyPath` / `NSPredicate(format:)` over concatenating user strings — injection is real. SwiftData and modern Core Data also take `Predicate` macros, which are type-safe. Typical mistake: `predicateWithFormat` and interpolating a search box into the format string.

### Example

```swift
let request = NSFetchRequest<NSManagedObject>(entityName: "Note")
request.predicate = NSPredicate(format: "%K CONTAINS[cd] %@", #keyPath(Note.title), query)
```

### Follow-ups

- `%K` vs `%@`?
- How do you express “in this set of ids”?
- `NSPredicate` vs Swift `Predicate` / `#Predicate`?

## NSFetchRequest {#nsfetchrequest}

- Level: Mid
- Frequency: Medium

### Answer

`NSFetchRequest` is the query object you hand a context: entity name (or type), optional `NSPredicate`, `sortDescriptors`, `fetchLimit` / `fetchOffset`, and `resultType` (managed objects, object IDs, dictionaries, count). Faulting and `relationshipKeyPathsForPrefetching` decide how much graph you pull. A request with no sort is legal for a raw fetch; an `NSFetchedResultsController` requires a sort. Typical miss: fetching every `Note` on the main context and filtering in Swift.

### Example

```swift
let request = NSFetchRequest<Note>(entityName: "Note")
request.predicate = NSPredicate(format: "isPinned == YES")
request.sortDescriptors = [NSSortDescriptor(key: "updatedAt", ascending: false)]
request.fetchLimit = 20
let notes = try context.fetch(request)
```

### Follow-ups

- When do you fetch object IDs instead of objects?
- How do you avoid an N+1 on a relationship?
- Why does FRC refuse a request with no sort?

## NSFetchedResultsController {#fetched-results-controller}

- Level: Mid
- Frequency: Medium

### Answer

`NSFetchedResultsController` sits on a **fetch request + a context** and tells a table/collection view when the result set changes (`controllerDidChangeContent`, per-object insert/delete/move). It can section by a key path and cache the section info. You still own `cellForRow`. Diffable data sources plus a SwiftData / Combine pipeline replace a lot of FRC in new code; FRC is still the UIKit + Core Data interview default. Typical miss: using the view context for a huge unfiltered fetch, or ignoring `controller:didChange` and reloading the whole table.

### Example

```swift
let request = NSFetchRequest<Note>(entityName: "Note")
request.sortDescriptors = [NSSortDescriptor(key: "updatedAt", ascending: false)]
let frc = NSFetchedResultsController(fetchRequest: request,
                                     managedObjectContext: context,
                                     sectionNameKeyPath: nil,
                                     cacheName: nil)
try frc.performFetch()
```

### Follow-ups

- Why must the fetch have a sort descriptor?
- FRC vs a diffable snapshot you build yourself?
- Can you use FRC on a private-queue context for UI?

## NSCoding and archiving {#nscoding}

- Level: Mid
- Frequency: Low

### Answer

`NSCoding` / `NSSecureCoding` is the old Cocoa archive: an object writes its keys into an `NSCoder`, `NSKeyedArchiver` turns the graph into `Data`. `NSSecureCoding` requires you to name expected classes so a crafted file cannot instantiate something else. New code prefers `Codable` (or SwiftData). You still meet archives in `UserDefaults` Data blobs, old documents, and state restoration. Typical miss: `NSKeyedUnarchiver.unarchiveObject` (insecure) on data you did not just write.

### Example

```swift
let data = try NSKeyedArchiver.archivedData(withRootObject: colors, requiringSecureCoding: true)
let colors = try NSKeyedUnarchiver.unarchivedObject(ofClasses: [NSArray.self, UIColor.self], from: data)
```

### Follow-ups

- `NSCoding` vs `Codable` — when is each forced?
- What does `requiringSecureCoding` prevent?
- Why is a Core Data store not “just an archive”?

## How you persist data on iOS {#persist-options}

- Level: Junior
- Frequency: High

### Answer

Name the tool by size and shape, not by habit. **UserDefaults** — flags and tiny prefs. **Keychain** — secrets. **Files** (`FileManager`, Caches / Documents / App Group) — images, exports, offline packs. **Codable + disk** — a JSON document you own. **Core Data / SwiftData** — object graphs, queries, relationships. **CloudKit** — user-synced records. **URLCache** is HTTP, not your model. Interviewers want the decision tree and what happens on uninstall / low storage. Typical miss: stuffing a feed into UserDefaults or putting tokens in a plist.

### Example

```text
onboarding seen     → UserDefaults
auth token          → Keychain
camera draft        → Files (Caches or Documents)
notes with search   → SwiftData / Core Data
shared shopping list → CloudKit or your API
```

### Follow-ups

- Documents vs Caches — which can the system delete?
- When is a file + Codable enough vs Core Data?
- What survives an app delete?

## Core Data delete rules {#core-data-delete-rules}

- Level: Mid
- Frequency: Medium

### Answer

A relationship’s **delete rule** says what happens to the other side when you delete an object. **Nullify** (default): drop the pointer, leave the other object. **Cascade**: delete the related objects too (folder → notes). **Deny**: refuse the delete if anything still points here. **No Action**: do nothing — you can leave dangling references; almost never what you want. Typical miss: cascade on a many-to-many and wiping half the store.

### Example

```text
Folder.notes = Cascade
Note.folder = Nullify
User.profile = Deny if a profile must not exist without a user
```

### Follow-ups

- Cascade vs nullify on a parent-child?
- What does Deny do to `context.save()`?
- How do you test you did not orphan objects?

## Core Data vs SQLite vs Realm {#core-data-vs-sqlite}

- Level: Mid
- Frequency: Medium

### Answer

**SQLite** is a SQL file you query yourself (`sqlite3`, GRDB). **Core Data** is an object graph that *may* sit on SQLite — faults, contexts, migrations, not “just SQL.” **Realm** is a third-party object database with live objects and its own file format. Pick SQLite/GRDB when you want SQL and simple files. Pick Core Data / SwiftData when you want the Apple stack and FRC. Pick Realm only if the team already knows it — it is another vendor. Typical miss: “Core Data is slow SQLite” or expecting Core Data to be encrypted by default (it is not; you add SQLCipher / file protection).

### Example

```text
Need raw SQL reports     → SQLite / GRDB
Need object graph + UI   → Core Data / SwiftData
Need live objects, team knows Realm → Realm
Need encryption at rest  → say so; none of these is magic
```

### Follow-ups

- Is Core Data encrypted?
- How do you pass a managed object across queues?
- When is Realm a trap on a greenfield app?

## Core Data migration {#core-data-migration}

- Level: Mid
- Frequency: High

### Answer

You **version** the model (Editor → Add Model Version). **Lightweight** migration (`NSMigratePersistentStoresAutomaticallyOption` + `NSInferMappingModelAutomaticallyOption`) covers additive changes: new optional attributes, new entities, a renamed property with a renaming ID. **Heavy / custom mapping** is for reshape: split an entity, change a relationship cardinality, transform values. You write a mapping model (or a `NSEntityMigrationPolicy`) and test it on a copy of a real store. Wiping the store is only OK before first ship. Editing the current `.xcdatamodel` in place without a version is how you brick users. Typical miss: “lightweight will infer anything” after you delete an entity the old store still has.

### Example

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

### Follow-ups

- Lightweight vs a custom mapping model — one example each?
- What does a renaming identifier buy you?
- How do you test migration without wiping a tester’s phone?
