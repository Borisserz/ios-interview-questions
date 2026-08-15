# Networking

- [Making a network request](#network-request)
- [Showing web content](#web-content)
- [NotificationCenter](#notification-center)
- [URLSession](#urlsession)
- [URL vs URLRequest](#url-vs-urlrequest)
- [URLCache](#url-cache)
- [Push notifications](#push-notifications)
- [Token authentication](#token-auth)
- [HTTP methods](#http-methods)
- [JSON](#json)
- [REST](#rest)
- [REST vs GraphQL](#rest-vs-graphql)
- [REST vs RPC](#rest-vs-rpc)
- [WebSocket](#websocket)
- [HTTP status codes](#http-status)
- [Reachability](#reachability)
- [Retry with backoff](#retry-backoff)
- [Local vs remote notifications](#local-notifications)

## Making a network request {#network-request}

- Level: Junior
- Frequency: High

### Answer

`URLSession` is the system HTTP client. Build a `URL` or `URLRequest`, call `data(from:)` (or the older `dataTask`), check the HTTP status, then decode the body. Prefer `async`/`await` for new code; still be able to write the completion-handler form. `URLSession.shared` is enough for a simple GET; a custom `URLSessionConfiguration` is for timeouts, caches, and background sessions. Never treat a completed task as success — read `(response as? HTTPURLResponse)?.statusCode`. Typical misses: ignoring App Transport Security, decoding JSON on the main actor for no reason, and leaking a delegate-based session by never calling `finishTasksAndInvalidate()`.

### Example

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

### Follow-ups

- `URLSession.shared` vs a configured session — when do you need your own?
- How do you send a JSON POST with a header?
- What does a background `URLSession` change about callbacks?
- Where should you decode: the session’s delegate queue, a task, or the main actor?

## Showing web content {#web-content}

- Level: Junior
- Frequency: Medium

### Answer

In-app HTML is `WKWebView` (WebKit). `UIWebView` is gone and will not pass review. If you want Safari’s cookies, reader view, and privacy UI without building a browser, present `SFSafariViewController`. `Link` in SwiftUI hands the URL to Safari; wrap `WKWebView` in `UIViewRepresentable` when you need to stay inside the app. Load a `URLRequest` or an HTML string; inject JavaScript only when the page cannot do the job. The distinction interviewers want: `WKWebView` for control, `SFSafariViewController` for in-app Safari chrome, a plain `https` open for leaving the app.

### Example

```swift
import SafariServices
import WebKit

let webView = WKWebView(frame: .zero)
webView.load(URLRequest(url: URL(string: "https://example.com")!))

let safari = SFSafariViewController(url: URL(string: "https://example.com")!)
present(safari, animated: true)
```

### Follow-ups

- Why is `SFSafariViewController` preferred for OAuth or third-party pages?
- How do you load local HTML from the bundle in `WKWebView`?
- What is `WKWebsiteDataStore` for?

## NotificationCenter {#notification-center}

- Level: Junior
- Frequency: High

### Answer

`NotificationCenter` is an in-process pub/sub bus, not a networking API. You post a `Notification.Name`; observers receive it on the posting thread unless you specify a queue. Use it for broadcasts that many unrelated objects might care about — keyboard frame, a logout, `accountDidChange`. Do not use it as a stand-in for a delegate, a callback, or an `AsyncStream` between two types that already know each other. Block-based `addObserver` returns a token you retain; drop the token (or `removeObserver`) when the listener should die. Typical bugs: posting off the main queue and touching UI, leaking observers, and colliding on a raw string name.

### Example

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

### Follow-ups

- Combine `NotificationCenter.Publisher` vs a stored observer token — who cancels?
- What thread does `post` deliver on if you pass `queue: nil`?
- When is a delegate or `AsyncStream` the better tool?

## URLSession {#urlsession}

- Level: Mid
- Frequency: High

### Answer

`URLSession` is the request pipeline: a **configuration**, then a **task**, then `resume()`. `.default` shares a disk cache and cookie store. `.ephemeral` keeps that in RAM and drops it with the session. `.background` hands transfers to the system so they can finish after the app suspends. `URLSession.shared` is fine for simple GETs; make your own session when you need a delegate, pinning, or a custom cache. Tasks start suspended — forgetting `resume()` is the classic bug. Prefer `data(from:)` / `bytes(for:)` over the completion-handler `dataTask` unless you are bridging. Typical mistakes: one shared session with a delegate you never keep alive, and using background config for a JSON API call that should just `await`.

### Example

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

### Follow-ups

- When do you need a session delegate instead of `async`?
- `shared` vs a custom session — cookies, cache, invalidateAndCancel?
- What does a background configuration change about completion?
- When is Alamofire still worth a dependency?

## URL vs URLRequest {#url-vs-urlrequest}

- Level: Junior
- Frequency: High

### Answer

A **`URL`** is the address. A **`URLRequest`** is a request you are about to send: that URL plus method, headers, body, cache policy, timeout. `URLSession.data(from:)` is enough for a GET. Anything else — `POST`, `Authorization`, a custom cache policy — needs a `URLRequest`. `URLComponents` is how you build a URL without string-concatenating query items. Typical miss: `URL(string: "https://api/q?q=" + query)` and wondering why spaces break.

### Example

```swift
var request = URLRequest(url: url)
request.httpMethod = "POST"
request.setValue("application/json", forHTTPHeaderField: "Content-Type")
request.httpBody = try JSONEncoder().encode(payload)
let (data, _) = try await URLSession.shared.data(for: request)
```

### Follow-ups

- `URL` vs `URLComponents` vs a raw string?
- When do you set `cachePolicy` on the request vs the session?
- How do you attach a bearer token without logging it?

## URLCache {#url-cache}

- Level: Mid
- Frequency: Medium

### Answer

`URLCache` stores HTTP responses on disk/memory according to the request’s cache policy and the response headers (`Cache-Control`, `ETag`). It is not `NSCache` and not your decoded models. `.useProtocolCachePolicy` is the default and usually correct. `.reloadIgnoringLocalCacheData` is for pull-to-refresh. `.returnCacheDataElseLoad` is for offline-first reads. A custom `URLSessionConfiguration.urlCache` lets you size memory and disk. Typical mistakes: expecting `URLCache` to hold `UIImage` objects, and disabling the cache globally because one endpoint was stale — fix that request’s policy instead.

### Example

```swift
let config = URLSessionConfiguration.default
config.urlCache = URLCache(memoryCapacity: 10_000_000, diskCapacity: 50_000_000)
config.requestCachePolicy = .useProtocolCachePolicy
let session = URLSession(configuration: config)
```

### Follow-ups

- How do `ETag` and `304 Not Modified` interact with `URLCache`?
- `URLCache` vs `NSCache` vs a file you write yourself?
- When is `.reloadIgnoringLocalAndRemoteCacheData` the wrong hammer?

## Push notifications {#push-notifications}

- Level: Mid
- Frequency: High

### Answer

Remote push is **your server → APNs → the device**. Ask permission, then `registerForRemoteNotifications()` — **every launch**, because the token rotates (restore, new device, APNs refresh). Send the hex `Data` to your backend. Sandbox (`api.sandbox.push.apple.com`) and production (`api.push.apple.com`) tokens **do not mix**; a 410 Unregistered means delete the row. Payload is small JSON (`aps.alert`, `badge`, `sound`). Silent wake is `content-available: 1`; a Notification Service Extension needs `mutable-content: 1` and has **~30 seconds** (`serviceExtensionTimeWillExpire`). Typical misses: treating the token as forever, shipping a debug token to prod, PII in the payload, or expecting the extension without `mutable-content`. Local notifications do not go through APNs.

### Example

```swift
func application(_ app: UIApplication,
                 didRegisterForRemoteNotificationsWithDeviceToken token: Data) {
    let hex = token.map { String(format: "%02x", $0) }.joined()
    api.uploadDeviceToken(hex)
}
```

### Follow-ups

- Device token vs APNs auth key (`.p8`) vs old `.p12` certs?
- What changes for a Notification Service Extension?
- How do you handle a tap that should open a specific screen?
- Does a suspended app still receive a push — and does your delegate run?
- Local vs remote — which one still fires in Airplane Mode?
- Sandbox vs production — why did TestFlight work and the App Store build go silent?
- `content-available` vs `mutable-content` — which one downloads the image?
- APNs 410 — what does the server delete?
- Payload cap — what happens at 4 KB + 1?
- Alert vs silent vs VoIP vs critical — which one bypasses Focus?

## Token authentication {#token-auth}

- Level: Mid
- Frequency: High

### Answer

After login the server issues a short-lived **access token** (often JWT) and a longer **refresh token**. You put `Authorization: Bearer …` on API calls. Store both in the **Keychain**, not `UserDefaults`. On `401`, one refresh at a time (a single-flight actor), then retry the original request; if refresh fails, drop to login. Do not log tokens. Typical mistakes: putting the access token in the URL query, refreshing on every call, and keeping the refresh token in memory only so a process kill logs the user out for no reason.

### Example

```swift
actor AuthHeader {
    private var access: String
    init(access: String) { self.access = access }

    func apply(_ request: inout URLRequest) {
        request.setValue("Bearer \(access)", forHTTPHeaderField: "Authorization")
    }
}
```

### Follow-ups

- Where do you put token refresh so two 401s do not stampede?
- Access token vs refresh token vs API key — which lives where?
- What does PKCE add to a mobile OAuth / SSO flow?
- What do you do with tokens on logout?

## HTTP methods {#http-methods}

- Level: Junior
- Frequency: High

### Answer

**GET** reads and should be safe/idempotent — no body side effects. **POST** creates or triggers work; repeating it may create two rows. **PUT** replaces a resource at a known URL (idempotent). **PATCH** applies a partial update. **DELETE** removes. **HEAD** is GET without a body (probe). Interviewers want which one you put on “like a tweet” (usually POST) and why a retry of PUT is safer than POST. Typical miss: GET with a body, or POST for a fetch because “the API guy did it.”

### Example

```swift
var like = URLRequest(url: url)
like.httpMethod = "POST"
var replace = URLRequest(url: url)
replace.httpMethod = "PUT"
```

### Follow-ups

- REST vs GraphQL on a mobile client — what actually changes?
- Idempotent vs safe — which methods are which?
- Why is a second tap on POST dangerous?
- When is PATCH the wrong tool vs PUT?

## REST vs GraphQL {#rest-vs-graphql}

- Level: Mid
- Frequency: Medium

### Answer

**REST** is resources and HTTP verbs; the client knows the URLs. **GraphQL** is one endpoint and a query that asks for fields — fewer round trips, bigger payloads to parse, a schema to version. On iOS, REST + `Codable` is the default. GraphQL wins when the same screen would otherwise need three REST calls, or when web and mobile share a graph. Cost: generated clients, caching is harder than `URLCache`, and a “flexible query” can become an unbounded download. Typical miss: picking GraphQL to look modern, then fetching the same bag of fields every time.

### Example

```text
REST:    GET /users/1 + GET /users/1/posts
GraphQL: { user(id: 1) { name posts { title } } }
```

### Follow-ups

- How do you cache a GraphQL response vs a REST URL?
- Who owns pagination — connections or your own cursor?
- When is REST still the right call for a 2026 app?

## REST vs RPC {#rest-vs-rpc}

- Level: Mid
- Frequency: Medium

### Answer

**REST** names a resource and an HTTP verb (`GET /users/12`). **RPC** names a procedure (`/getUser`, gRPC `UserService.Get`, JSON-RPC `{"method":"getUser"}`). Under the hood an RPC is still bytes on a socket — often HTTP/2 + protobuf — plus a stub that looks like a local function. On iOS you care about: codegen (`.proto` → Swift), streaming vs one-shot, and that a “method” is harder to cache than a GET URL. Chat and internal BFF APIs often look like RPC even when they speak JSON. Typical miss: calling every POST an RPC, or saying RPC has no HTTP.

### Example

```text
REST:  GET /orders/42
RPC:   POST /twirp/orders.v1.Orders/Get  { "id": "42" }
gRPC:  Orders.Get(OrderId) → Order   // generated client
```

### Follow-ups

- When is gRPC worth a mobile dependency vs JSON REST?
- How do you cache an RPC that is not a GET?
- REST vs GraphQL vs RPC — which problem does each solve?

## JSON {#json}

- Level: Junior
- Frequency: High

### Answer

JSON is a text format: objects, arrays, strings, numbers, booleans, `null`. On iOS you decode with `JSONDecoder` / `Codable`, not `JSONSerialization` unless the shape is unknown. **Pros:** small compared with XML, universal, easy to read in Charles. **Cons:** no comments, no dates as a first-class type (you pick a strategy), easy to silently drop unknown keys, a single huge document is awkward to stream. Typical miss: “JSON is a Swift type” or stuffing a comment in a payload.

### Example

```swift
struct Tweet: Decodable { var id: String; var text: String }
let tweets = try JSONDecoder().decode([Tweet].self, from: data)
```

### Follow-ups

- JSON vs plist vs protobuf on the wire?
- How do you handle a date field?
- What does `NSNull` become in `JSONSerialization`?

## REST {#rest}

- Level: Mid
- Frequency: High

### Answer

REST is resources + HTTP verbs + representations (usually JSON) + stateless requests. Nouns in the path (`/tweets/12`), verbs in the method. Cacheability and `ETag` / `Cache-Control` are part of the deal. GraphQL and RPC exist when you over-fetch or need one round trip for a graph. Mobile cost: chatty endpoints and large payloads. Typical miss: a single `/api` POST that switches on `action=` and calling it REST.

### Example

```text
GET    /v1/tweets?cursor=
POST   /v1/tweets/12/likes
DELETE /v1/tweets/12/likes
```

### Follow-ups

- REST vs GraphQL vs a WebSocket API — pick for a feed?
- What does stateless mean for an access token?
- How do you version (`/v1` vs a header)?

## WebSocket {#websocket}

- Level: Mid
- Frequency: Medium

### Answer

A WebSocket is a **persistent, bidirectional** TCP connection upgraded from HTTP. Use it for chat, live scores, collaborative cursors — not for a once-a-day settings fetch. Cost: battery, server connection count, reconnect/backoff, and what happens when the app backgrounds (iOS will often kill it; you fall back to push). `URLSessionWebSocketTask` is the system client. Typical miss: keeping a socket open for a feed that a silent push could update.

### Example

```swift
let task = URLSession.shared.webSocketTask(with: url)
task.resume()
let message = try await task.receive()
```

### Follow-ups

- WebSocket vs SSE vs long poll vs APNs?
- What do you persist so a reconnect does not duplicate messages?
- Why is a socket a poor choice while the app is suspended?

## HTTP status codes {#http-status}

- Level: Junior
- Frequency: High

### Answer

Interviewers want the families, not a memorized table. **2xx** success (`200` OK, `201` created, `204` no body). **3xx** redirect / `304` not modified (cache). **4xx** your request (`400` bad, `401` auth, `403` forbidden, `404` missing, `409` conflict, `429` rate limit). **5xx** their fault — retry with backoff, not a tight loop. Do not treat every non-200 as “network error.” Typical miss: showing “no internet” on a `401`.

### Example

```swift
guard let http = response as? HTTPURLResponse else { throw URLError(.badServerResponse) }
switch http.statusCode {
case 200..<300: break
case 401: throw AuthError.expired
case 429: throw AuthError.throttled
default: throw URLError(.badServerResponse)
}
```

### Follow-ups

- `401` vs `403`?
- Which codes are safe to retry?
- How does `304` interact with `URLCache`?

## Reachability {#reachability}

- Level: Mid
- Frequency: Medium

### Answer

“Do we have a path to the network?” is **`NWPathMonitor`** (Network framework), not a ping to google.com on every tap. A satisfied path is not “the API is up” — you still try the request and handle errors. Use the monitor to change UI (offline banner) and to kick a retry queue when the path returns. The old `Reachability` / `SCNetworkReachability` samples are dated. Typical miss: blocking a request because Wi-Fi is off while the user is on cellular.

### Example

```swift
let monitor = NWPathMonitor()
monitor.pathUpdateHandler = { path in
    let online = path.status == .satisfied
    Task { @MainActor in banner.isHidden = online }
}
monitor.start(queue: .global(qos: .utility))
```

### Follow-ups

- Path satisfied vs a successful `URLSession` call?
- What do you do when the path flips mid-upload?
- Why not ICMP ping as your only check?

## Retry with backoff {#retry-backoff}

- Level: Mid
- Frequency: High

### Answer

Retry only **idempotent** or safely repeatable calls (`GET`, a put with an idempotency key), and only on transient failures (`408`, `429`, `5xx`, timeouts) — not on `400` or `401`. **Exponential backoff** waits `base * 2^attempt`, usually with jitter so a fleet does not stampede. Cap attempts and total time. Honour `Retry-After`. A tight loop on a 500 is how you DDoS yourself. Typical miss: retrying `POST /charge` and double-billing, or sleeping on the main actor.

### Example

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

### Follow-ups

- Which status codes are safe to retry?
- Why add jitter?
- How do you retry a `POST` without duplicating a side effect?

## Local vs remote notifications {#local-notifications}

- Level: Junior
- Frequency: Medium

### Answer

**Remote** push is a server → APNs → device. **Local** notifications are scheduled on the device with `UNUserNotificationCenter` — a calendar trigger, a time interval, or a location. Both need the same user permission for a visible banner, and both can deep-link on tap. Local does not need a device token, a backend, or a network. Use local for “remind me in 20 minutes” and “you have been idle”; use remote when another system decides the moment (a message arrived, a ride is 2 minutes away). Typical miss: scheduling a local notification and calling it a push, or expecting a local trigger to fire after the user force-quit if you never requested authorization.

### Example

```swift
let content = UNMutableNotificationContent()
content.title = "Stand up"
content.body = "20 minutes since the last break"

let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 20 * 60, repeats: false)
let request = UNNotificationRequest(identifier: "stand-up", content: content, trigger: trigger)
try await UNUserNotificationCenter.current().add(request)
```

### Follow-ups

- What permission do you still need for a local banner?
- How do you cancel one pending local request without wiping the rest?
- Silent remote vs a local time trigger — which one can wake a suspended app?
