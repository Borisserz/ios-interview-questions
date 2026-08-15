# System design

Answered cards first. **Practice** cards are prompts only — talk them through; do not treat any public write-up as ground truth.

- [How to run a mobile system design interview](#sd-interview)
- [Edge-first mobile design](#edge-first)
- [Design an image upload pipeline](#image-upload)
- [Design a news feed](#news-feed)
- [Design a chat app](#chat-app)
- [Design an image loading library](#image-loader)
- [Design a caching library](#caching-library)
- [Design a file downloader](#file-downloader)
- [Design a pagination library](#pagination)
- [Design a push notification system](#push-system)
- [Design a file uploader library](#file-uploader)
- [Design a networking library](#network-library)
- [Design an analytics library](#analytics-library)
- [Design Instagram / Facebook stories](#stories)
- [Design a flight booking flow](#flight-booking)
- [Design a location sharing library](#location-sharing)
- [Design an A/B experiment library](#ab-experiments)
- [Design a JSON parsing library](#json-parser)
- [Design a contacts app with live status](#contacts-realtime)
- [Design a clock app](#clock-app)
- [Design a recipe app](#recipe-app)
- [Design a photo editor](#photo-editing)
- [Design a live wallpaper app](#live-wallpaper)
- [Design Notes / Gmail / Facebook (iOS client)](#design-client-app)
- [Real-time ETA polling](#eta-polling)
- [Design a video streaming player](#video-streaming)
- [Design a short-form video feed](#short-video-feed)
- [Design an audio player](#audio-player)
- [Design a collaborative editor](#collaborative-editor)
- [Design video calling](#video-calling)
- [Design a server-driven UI engine](#sdui)
- [Design a payment checkout](#payment-checkout)
- [Build a checkout UI in 60 minutes](#checkout-ui)
- [Design a product catalog](#ecommerce-catalog)
- [Design Airbnb search and booking](#airbnb-booking)
- [Design a calendar client](#calendar-client)
- [Design deep links](#deep-links)
- [Design an offline-first sync engine](#offline-sync)
- [Design search with autocomplete](#search-autocomplete)
- [Design a live delivery tracker](#delivery-tracker)
- [Design a crash reporter](#crash-reporter)
- [Design an on-device LLM assistant](#on-device-llm)
- [Design a ChatGPT-style client](#chatgpt-app)
- [Design a restaurant ordering app](#restaurant-ordering)
- [Design an e-reader](#e-reader)
- [Unread count / badge](#unread-badge)
- [Design a maps / navigation client](#maps)
- [Design a wallet / balances screen](#wallet)
- [Design iCloud-style device sync](#icloud-sync)
- [Design a home screen of rails](#home-rails)
- [Design an offline media catalog](#offline-media)
- [Design clipboard / proximity sync](#clipboard-sync)
- [Design a Recently Deleted album](#recently-deleted)
- [Design a short match / score simulator](#match-simulator)

## How to run a mobile system design interview {#sd-interview}

- Level: Senior
- Frequency: High

### Answer

Forty-five minutes is a conversation, not a shipping spec. A usable clock: **clarify** (0–5: scope, DAU, offline, platform), **HLD** (5–15: boxes), **data & API** (15–25: entities, pagination), **deep dives** (25–40: two hard subsystems), **ops** (40–45: failure, metrics, rollout). Same ideas as the **SCADET** mnemonic some courses teach: System requirements, Constraints / design considerations, Architecture, Data & API, Evaluate NFRs, Trade-offs. Confirm **scope**: client-only, client + API, or full stack. Lock **3–5 functional** requirements, a few **non-functional** ones (offline, battery, consistency), and an explicit **out of scope**. Mobile SD is not backend Instagram-on-a-whiteboard — lifecycle, flaky radio, and battery are first-class.

Before boxes, name **what you sell**: a short list of *services* and *data* (chat history, address book, a call). Then split each: client, server, or both — and pick a channel (REST, WS, push, UDP). Default **pagination** on every list API; drop it only if the set is tiny. If they ask “most popular posts” or “detect bots,” spend two minutes on a **formula** (inputs → window → output) before drawing Kafka.

Draw a high-level box diagram — a 4-layer client (View → ViewModel → use cases → repository / remote+local) is enough. Deep-dive **one** slice you know, then **one hard case** you have shipped (image cache + disk eviction, gap-fill after reconnect). Ask which box they want next. Typical miss: jumping into `UICollectionView` cells before the data flow exists.

### Example

```swift
enum Scope { case clientOnly, clientAndAPI, fullStack }

struct Brief {
    var scope: Scope
    var functional: [String]   // 3...5
    var nonFunctional: [String]
    var outOfScope: [String]
}
```

### Follow-ups

- Client-only vs you also own the API — what changes first?
- Which non-functional requirement would you drop if time is gone?
- When is a library-design interview different from an app-design one?
- REST vs GraphQL — when is the mobile client the reason to pick one?
- What do you say is out of scope in the first five minutes?
- Which two subsystems would you deep-dive on a feed vs a chat?
- What “services and data” would you list in the first three minutes of WhatsApp-lite?
- Which NFR dimension do you check before you pick a store (security, offline, team size)?
- When do you stop and write a formula instead of another box?
- Walk SCADET on a maps client in 45 minutes — where do you spend the deep-dive?
- Privacy model and a 72-hour offline window — do you ask before the first box?
- High-level architecture or a coded object model — which one do you lock in the first minute?
- Auth, privacy, compliance — do you name them before they ask?
- What can stay on device so the request never leaves?

## Edge-first mobile design {#edge-first}

- Level: Senior
- Frequency: High

### Answer

Some mobile SD rooms are not “draw Kafka.” They score **who owns the write** and **what never leaves the device**. Default: the phone (or the watch that sensed it) is the source of truth while offline; the server stores **opaque blobs** or runs conflict detect; a third party does not see raw rows. Ask the trust order out loud: hardware / OS / your app / cloud / a partner SDK. Prefer a slower path you control over a CDN you do not. Typical miss: a technically pretty sync that puts user health or photos on a third-party pipe, or a QPS lecture when they asked “two devices edited the same note.”

### Example

```text
1. Who may write — sensor, phone, server, partner?
2. What does the server see — plaintext, ciphertext, or only a conflict bit?
3. What still works after 72 hours offline?
4. Then boxes. Not before.
```

### Follow-ups

- Watch and phone disagree on the same sample — whose write wins, and why?
- When is “we will be slower” the right answer?
- Partner wants a raw read API — what do you expose instead?

## Design an image upload pipeline {#image-upload}

- Level: Senior
- Frequency: High

### Answer

Start with questions: camera or library, max size, retry, offline, who sees the image, do we need a thumbnail now? Then layers. **Client:** pick → compress / downscale on a background queue → persist a local draft (file + upload state) so a kill mid-flight can resume → `URLSession` upload (background config if the user can leave) → progress → success writes a remote URL into the draft. **API:** presigned PUT to object storage, not a JSON body of base64. **Server:** virus scan / size limits, generate variants, notify via push or websocket. **Failure:** retry with backoff, do not duplicate on a second tap (idempotency key). **Cache:** show the local file immediately, then swap to the CDN URL. Interviewers want the state machine (`queued / uploading / failed / done`) more than a framework name. A “photo app that syncs the camera roll” is the same machine plus a cursor of what is already on the server.

### Example

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

### Follow-ups

- Background `URLSession` vs a foreground task — when?
- How do you avoid uploading the same photo twice?
- Where do thumbnails get generated — client, server, or both?
- How do you resume a camera-roll sync after the process is killed?
- Library API (file uploader) vs this product pipeline — what is different?

## Design a news feed {#news-feed}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design an infinite Twitter / Instagram / Facebook-style feed. Default scope: scroll, like, open a post. Offline cache and image cost are in. Auth, compose, and follow graphs are out unless they pull them in.

### Follow-ups

- Cursor vs offset pagination — which breaks when the top of the feed moves?
- Who is the source of truth on disk after a like while offline?
- Push vs SSE vs polling for “new posts”?
- How do you keep scroll FPS when every cell has a remote image?

## Design a chat app {#chat-app}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a messaging client. Pick 1:1 or group, then 3–5 features: send/receive, offline drafts, media, read receipts. Assume a backend exists; sketch the sync API if they want it.

### Follow-ups

- REST vs WebSocket vs push when the app is backgrounded?
- How do you order messages after a reconnect with gaps?
- What is on disk vs only in RAM?
- How do you show “sending / sent / failed” without double-sending?
- Where does E2EE change the client (keys, attachments, search)?
- One process, many workspaces — one SQLite file or many?
- Message states: draft → sending → sent → delivered → read — what is local vs ack?
- Cursor vs offset for history when messages can be deleted?
- Heartbeat + backoff after a WS drop — who owns the reconnect?
- How do you dedupe a retry that the server already stored?
- Group chat: what is `conversationId` vs a fan-out list on the client?
- App backgrounded: WS is dead — what does the APNs payload contain?

## Design an image loading library {#image-loader}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a Kingfisher-style image loader: `url → UIImage` for a feed. Cover request coalescing, memory + disk cache, cancellation on reuse, and a public API that is hard to misuse.

### Follow-ups

- Two cells request the same URL — how many downloads?
- What do you do in `prepareForReuse`?
- Memory cache vs `URLCache` vs your disk folder?
- How do you avoid decoding a 12 MP JPEG on the main thread?

## Design a caching library {#caching-library}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a generic cache (memory, optional disk). Public API, eviction (LRU / cost / memory warning), thread safety, and what “optional” means for callers.

### Follow-ups

- `NSCache` vs your own dictionary plus a lock?
- How do you key images vs JSON responses?
- What happens on a memory warning mid-write?
- Why must a miss still produce a correct result?

## Design a file downloader {#file-downloader}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a library that downloads large files: queue, pause/resume, progress, disk destination, and what happens if the app is killed. Public API first.

### Follow-ups

- Foreground session vs background `URLSession` configuration?
- How do you resume from byte `N` (Range / ETag)?
- Max concurrent downloads — who decides?
- How do you not leave half-files in Caches?

## Design a pagination library {#pagination}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a pager that a feed can bind to: next/previous page, refresh, local cache, and a single stream of items for the UI.

### Follow-ups

- Cursor vs page number vs `since_id`?
- Where does the remote-mediator sit relative to the database?
- How do you drop a stale page after a pull-to-refresh?
- What does the UI observe — `[Item]` or a diff?

## Design a push notification system {#push-system}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design the client + server path for remote push: permission, device token, APNs, payload, tap → screen, and a silent update. Not the same card as “what is APNs” — this is the whole pipeline.

### Follow-ups

- Token rotation — who stores the mapping user ↔ device?
- Visible alert vs `content-available` — battery and reliability?
- How does a Notification Service Extension change the design?
- What do you persist so a tap works after a cold start?
- Deferred deep link after install — what do you store, and for how long?

## Design a file uploader library {#file-uploader}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a reusable **uploader API** (any file, not only photos): enqueue, progress, cancel, retry, multipart vs presigned PUT. Product-specific album sync stays on `{#image-upload}`.

### Follow-ups

- How do callers learn progress without retaining a view?
- Idempotency key — library concern or app concern?
- Background transfer vs your own retry queue?

## Design a networking library {#network-library}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a thin HTTP client over `URLSession`: request builder, auth plugin, retries, cancellation, and typed errors. Do not rebuild URLSession.

### Follow-ups

- Where does the access-token refresh live so two 401s do not stampede?
- How do you cancel a request when a screen dies?
- Retry: which status codes, which backoff?
- Certificate pinning — in the library or the app?

## Design an analytics library {#analytics-library}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design an event pipeline: `track(name, props)` from any thread, batching, disk backlog, flush on background, and privacy (PII, opt-out).

### Follow-ups

- What happens if `track` is called 200 times during a scroll?
- How do you not lose events on a crash?
- Main thread — what is forbidden in the public API?
- How do you drop events when the user opts out?
- Flush every N events vs every T seconds vs on background — which default?

## Design Instagram / Facebook stories {#stories}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design stories: 24h expiry, tap-through, preload the next clip, seen-state, and a thin composer if they ask. Feed ranking is out.

### Follow-ups

- How do you preload without blowing memory on a 15-item ring?
- Seen-state: server, disk, or both?
- Video vs image — what changes in the loader?
- What do you do when the next story 404s mid-swipe?

## Design a flight booking flow {#flight-booking}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design search → fare → seat → pay. Call out cache of search results, restoring the stack when the user leaves, payment failure, and **seat lock** expiry.

### Follow-ups

- How long is a seat hold, and what does the UI show when it expires?
- What do you keep when they background the app on the payment screen?
- Idempotency on “Pay” — double tap, double charge?
- Which data is safe to cache (fares go stale)?

## Design a location sharing library {#location-sharing}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a library that publishes the user’s location to a backend and draws others on a map. Permissions, accuracy vs battery, background updates, and a small public API.

### Follow-ups

- When vs significant-change vs visits — which mode for which product?
- How do you stop updates when the map is gone?
- What do you send: raw points or a simplified path?
- Privacy: who can see the stream, and how do you revoke it?
- How do you smooth GPS jitter without killing the battery?

## Design an A/B experiment library {#ab-experiments}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a client that fetches assignments, caches them, exposes `variant(for: flag)`, and does not flicker UI on the first launch.

### Follow-ups

- Sticky assignment after a refresh mid-session?
- What if the config request fails — last cache or default?
- How do you avoid a layout jump when the flag arrives late?
- Who owns exposure logging?
- How fast can a remote kill switch reach every client?

## Design a JSON parsing library {#json-parser}

- Level: Senior
- Frequency: Low
- Kind: Practice

### Prompt

Design a Codable-class parser API (think Moshi/Gson): decode `Data` → `T`, custom adapters, error surfaces, and thread expectations. Prefer “why not just `JSONDecoder`” over a hand-rolled lexer.

### Follow-ups

- How do you report a missing key with a path?
- Date / URL strategies — global or per-type?
- Incremental / streaming parse — when is it worth it?
- What is safe to call from the main thread?

## Design a contacts app with live status {#contacts-realtime}

- Level: Senior
- Frequency: Low
- Kind: Practice

### Prompt

Design a contacts list plus presence (online / last seen). Local address book vs server graph, and how presence updates arrive.

### Follow-ups

- Push vs a presence channel — battery on 500 contacts?
- How do you merge device contacts with server profiles?
- What is cached when the user is offline?
- Permissions: what if Contacts access is denied?

## Design a clock app {#clock-app}

- Level: Mid
- Frequency: Low
- Kind: Practice

### Prompt

Design Clock: local time, world clocks, alarms, timers. Focus on scheduling, time-zone data, and what survives a reboot — not a pretty face.

### Follow-ups

- `Timer` vs `UNNotification` for an alarm?
- How do you handle a timezone change while a timer is running?
- What is stored vs computed from `Date`?
- Why is a RunLoop timer the wrong tool for a 7am alarm?

## Design a recipe app {#recipe-app}

- Level: Mid
- Frequency: Low
- Kind: Practice

### Prompt

Design a recipe catalog: browse, search, favorites, offline pack. Images and a shopping list if time remains.

### Follow-ups

- What is indexed on device vs fetched per open?
- How do favorites sync across devices?
- Image cache policy for a catalog that changes weekly?

## Design a photo editor {#photo-editing}

- Level: Senior
- Frequency: Low
- Kind: Practice

### Prompt

Design an editor: crop, filters, export. Memory for a 12 MP bitmap, undo stack, and where Core Image / Metal sit. Sharing is out unless they ask.

### Follow-ups

- Full-res vs preview pipeline — when do you render the final bitmap?
- How big is the undo stack, and what do you store per step?
- Main thread — what is illegal during a filter drag?
- Export: HEIC vs JPEG, and who compresses?

## Design a live wallpaper app {#live-wallpaper}

- Level: Mid
- Frequency: Low
- Kind: Practice

### Prompt

Design an app that shows animated wallpapers. iOS has no third-party live lock screen — say that, then design a gallery + preview + (on iOS) a limited wallpaper set, or discuss Android’s engine if they want cross-platform.

### Follow-ups

- What can you actually set on iOS vs Android?
- Battery: how do you pause a preview off-screen?
- Where do assets live — bundle, disk, CDN?
- How do you avoid decoding a video every frame on the main thread?

## Design Notes / Gmail / Facebook (iOS client) {#design-client-app}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design the **iOS client** for Notes, Gmail, or Facebook. Ask scope first (offline, sync, attachments, search). Then: screens, local store, sync / conflict, image pipeline, and what you push vs pull. For Notes specifically: Core Data / SwiftData on device, CloudKit or your API for multi-device, rich text (TextKit), and whether search is local (`Core Spotlight`) or a server index. Stay on the phone — backend is boxes unless they pull you there.

### Follow-ups

- What do you persist so airplane mode still opens the last inbox?
- How do you handle two devices editing the same note?
- Which Apple frameworks do you actually name (SwiftData, Push, Background Tasks)?
- CloudKit private DB vs your own sync API — what do you give up?
- Where does `Core Spotlight` sit relative to in-app search?

## Real-time ETA polling {#eta-polling}

- Level: Mid
- Frequency: High
- Kind: Practice

### Prompt

A ride-sharing screen must show a **live ETA** that refreshes about every 10 seconds. Scope: one visible screen, one driver. Talk through: start/stop with appear/disappear, cancel the in-flight request before the next tick, hop UI to main, `[weak self]`, what happens in background / poor network (backoff, not a tight timer), and why a `Timer` + `URLSession.shared` is not enough by itself.

### Follow-ups

- Timer vs `Task.sleep` in a loop vs a WebSocket?
- How do you avoid overlapping requests if a fetch takes longer than 10s?
- What do you persist when the scene backgrounds?

## Design a video streaming player {#video-streaming}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a long-form player (Netflix / YouTube). Scope: HLS playback, adaptive bitrate, lock-screen controls, one offline download. FairPlay / DRM and ads are out unless they pull them in. Name `AVPlayer` / `AVPlayerViewController` and what *you* own around it (item lifecycle, errors, resume position).

### Follow-ups

- How do you pick a starting bitrate on a bad network?
- Where is the watch-position stored so a kill mid-episode resumes?
- What do you tear down when the user leaves the screen?
- After an offline download — where does the license live relative to the file?

## Design a short-form video feed {#short-video-feed}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a Reels / TikTok-style vertical feed. Scope: swipe, autoplay the on-screen clip, prefetch neighbors. Default: a pool of a few `AVPlayer`s, not one player per cell. Memory and cellular are in; creator tools are out.

### Follow-ups

- How many players stay warm, and who gets evicted?
- What do you prefetch — next URL, next segment, next thumbnail?
- How do you stop decode when the feed backgrounds?

## Design an audio player {#audio-player}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a Spotify / Apple Music **client**. Default scope is three screens: **library** (playlists / albums), **playlist** (tracks + play), **now playing** (prev / next / shuffle). Playback must survive leaving the screen — a long-lived player service, not a VC. Talk HLS / adaptive bitrate, `AVPlayer`, audio session + lock screen, and one offline album. Gapless and CarPlay are follow-ups.

### Follow-ups

- How do you keep audio alive when the app is backgrounded?
- Queue vs a single item — who owns “up next”?
- Offline file vs streaming URL — same player API?
- Library / playlist / player — which object outlives the navigation stack?
- HLS vs one MP3 URL — what does the client still own?
- 10,000 offline tracks — what do you evict first when the quota is full?

## Design a collaborative editor {#collaborative-editor}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a Notes / Docs client where two devices edit one document. Scope: local typing stays instant, sync a stream of ops, show presence. Ask OT vs CRDT and what you persist as the op log. Rendering a full Word clone is out.

### Follow-ups

- What happens if both sides insert at the same index offline?
- Cursor presence — WebSocket payload vs a separate channel?
- How do you compact the op log so a new device can catch up?
- LWW for an avatar, CRDT for the shared paragraph — how do you choose?

## Design video calling {#video-calling}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a FaceTime / Meet / Zoom client. Scope: 1:1 call, camera + mic permissions, mute, rotate. Sketch signaling vs media (WebRTC: STUN/TURN, SFU). Grid-for-50 and recording are out unless they ask.

### Follow-ups

- What do you do when the app backgrounds — audio only?
- How do you handle thermal / network drops without a black frame forever?
- Who owns the audio session — you or CallKit?

## Design a server-driven UI engine {#sdui}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a client that renders screens from a JSON (or proto) component tree. Scope: a registry of native components, schema version, a fallback when the server sends an unknown type, and analytics hooks. Do not invent a browser.

### Follow-ups

- Unknown component — hide, placeholder, or force-update?
- How do you version the schema so old apps keep working?
- Where does navigation live — in the payload or in the app?

## Design a payment checkout {#payment-checkout}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a checkout screen that charges a card (or Apple Pay). Scope: tokenize on device, idempotent “Pay”, 3DS / SCA, a state machine (`idle → confirming → paid / failed`). You do not store PAN. PCI is “what must never touch our disk.”

### Follow-ups

- Double tap Pay — how do you not double-charge?
- Apple Pay vs a card form — what changes in the client?
- What do you persist if the app is killed during 3DS?

## Build a checkout UI in 60 minutes {#checkout-ui}

- Level: Mid
- Frequency: High
- Kind: Practice

### Prompt

Build a **checkout screen** in 60 minutes from a starter or a mock API: line items, a price breakdown, a payment-method picker, a confirm button. Scope: a ViewModel, empty and error, no double-submit. **PCI and 3DS are out** — that is `{#payment-checkout}`. Working UI by minute 25 beats a repository you never wire. Do not paste a third-party solution.

### Follow-ups

- They add a service fee at minute 40 — which type stays closed?
- Confirm while the mock API is slow — what does the button do?
- SwiftUI vs UIKit starter — do you fight the stack they gave you?

## Design a product catalog {#ecommerce-catalog}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design an Amazon / Shopify-style catalog: search or browse grid, PDP, cart. Scope: image-heavy list, cursor pages, cart that survives a kill. Checkout can be a box. Wishlist offline is a follow-up.

### Follow-ups

- How do you keep the grid at 60 fps with large images?
- Cart on disk vs server — who wins a conflict?
- What is stale: price, stock, or the photo?

## Design Airbnb search and booking {#airbnb-booking}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design search + book for stays. Scope: map and list stay in sync, debounce the query, a booking draft, a short inventory hold. Payments can stay a box. Talk what you cache (search results go stale; a hold has a timer).

### Follow-ups

- Map move vs typing — which request wins?
- What happens when the 15-minute hold expires on the review screen?
- How do you restore a draft after a process kill?
- Offline saved listings / a booking draft — what is still valid when the radio returns?

## Design a calendar client {#calendar-client}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a Google / Apple Calendar iOS client. Scope: month + day, create an event, sync. Recurrence (`RRULE`) and conflicts are the hard part. Infinite scroll of a month grid is in; a full CalDAV server is out.

### Follow-ups

- How do you expand a daily recurring event without materializing 10 years?
- Two devices edit the same event — last-write-wins or a prompt?
- Silent push vs pull-to-refresh vs `BGAppRefresh`?

## Design deep links {#deep-links}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design Universal Links + custom URL schemes for an app that is sometimes not installed. Scope: AASA, a router that maps path → screen, cold start vs warm, a deferred link after first install. Do not host AASA on a CDN that breaks association.

### Follow-ups

- Cold start: `didFinishLaunching` vs the scene connection options — who wins?
- How do you test a Universal Link on a device?
- What do you store so “open this listing” survives the App Store hop?

## Design an offline-first sync engine {#offline-sync}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a local-first store that syncs when the network returns. Scope: dirty flags, a queue, conflict policy (LWW vs prompt), `BGTaskScheduler`. One entity type is enough (notes or tasks). Do not design Firebase.

### Follow-ups

- What is the source of truth while offline?
- How do you avoid a sync loop after a conflict?
- What runs in a 30-second `BGAppRefresh` vs a processing task?
- Change token / delta fetch vs sending the whole store every time?
- When must the server store ciphertext it cannot decrypt?

## Design search with autocomplete {#search-autocomplete}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design in-app search with typeahead. Scope: debounce, cancel the in-flight request when the query changes, show local hits first if you have an index. Ranking on the server can stay a box. Talk the race: a slow “a” must not overwrite a fast “ab”.

### Follow-ups

- `Task` cancellation vs `switchToLatest` — same idea?
- Offline: FTS / trie on device vs empty state?
- How do you log impressions without firing on every keystroke?

## Design a live delivery tracker {#delivery-tracker}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a DoorDash / Uber Eats “your order is arriving” screen. Scope: order state machine, courier location, one Live Activity / Dynamic Island. Transport is a hybrid: WebSocket while foreground, APNs / poll when backgrounded. Payments are out.

### Follow-ups

- Which events are ActivityKit vs a full-screen push?
- How do you keep the map from redrawing every GPS tick?
- What do you show if the socket dies for 30 seconds?
- Nearby supply — geo hash vs querying every courier?
- Stale GPS — do you still dispatch, and what do you show?

## Design a crash reporter {#crash-reporter}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a Crashlytics-style client SDK. Scope: catch a fatal, persist a minidump / stack, upload on next launch, breadcrumbs. Signal-safety: almost nothing in the handler. OOM is a separate path (jetsam ≠ `NSException`).

### Follow-ups

- What is legal inside a signal handler?
- How do you detect “killed for memory” vs a user force-quit?
- Where do dSYMs live, and who symbolicates?

## Design an on-device LLM assistant {#on-device-llm}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design an on-device assistant (summarize this thread, answer from local notes). Scope: model download / update, RAM / thermal budget, token streaming to UI, a small local RAG over user data. Cloud fallback is a follow-up. Do not lecture transformer math.

### Follow-ups

- What happens when the Neural Engine throttles mid-stream?
- Where does user text live — and what must never leave the device?
- How do you version a 2 GB model without blocking first launch?
- `@Generable` DTO vs a SwiftData `@Model` — why not the same type?
- Device without a Neural Engine — what is the non-AI path?

## Design a ChatGPT-style client {#chatgpt-app}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a ChatGPT-like iOS client (cloud model, not on-device). Scope: compose, stream tokens, conversation history on disk, cancel an in-flight reply. Auth and billing are boxes. Talk streaming (`URLSession.bytes` / WebSocket), a message state machine, and what you show when the socket dies mid-sentence.

### Follow-ups

- How do you render tokens without hitching the text view?
- Streaming JSON / `URLSession.bytes` vs waiting for the full payload — where do you parse?
- What is persisted if the user kills the app mid-stream?
- How is this different from the on-device LLM card?

## Design a restaurant ordering app {#restaurant-ordering}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a discovery + order + pay app (DoorDash merchant side, or a single-restaurant app). Scope: menu, cart, checkout, order status. Map/search can be a box. Payments reuse the checkout card; live courier tracking is a follow-up, not the core.

### Follow-ups

- How do you version a menu that changes while the cart is open?
- What do you lock when they tap Place Order?
- Guest checkout vs account — what is on disk?

## Design an e-reader {#e-reader}

- Level: Senior
- Frequency: Low
- Kind: Practice

### Prompt

Design an iBooks / Kindle-style reader. Scope: open a book, paginate or scroll, remember position, one downloaded file. Sync across devices and a storefront are follow-ups. Talk file format (EPUB vs PDF), `CATiledLayer` / TextKit, and what you persist as a bookmark.

### Follow-ups

- How do you jump to chapter 12 without laying out the whole book?
- Dark mode and Dynamic Type — what reflows?
- What happens if the download is only half there?

## Unread count / badge {#unread-badge}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design the unread-message (or unread-notification) counter: tab badge, chat-list row, and a nav-bar label that stay in sync. Scope: one process, one user. Say where the number lives (server cursor vs local “last read”), who increments it, and how a message that arrives while the thread is open does *not* bump the badge.

### Follow-ups

- Observer vs a single store vs polling the API every 30s?
- Two devices: last-read is a server timestamp or a message id?
- App icon badge vs in-app badge — who owns `UNUserNotificationCenter`?
- How do you avoid a flash of “99+” on launch before the local DB loads?

## Design a maps / navigation client {#maps}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a Maps-style **client**: search a place, show it on a map, start turn-by-turn. Scope: one user, one device, online. Talk tile / vector rendering, a location pipeline (`CLLocationManager` accuracy vs battery), route polyline + reroute, and what you cache (recent searches, the last route). Live traffic and offline regions are follow-ups.

### Follow-ups

- Significant-change vs `kCLLocationAccuracyBest` — which mode for browse vs navigate?
- Who owns the map SDK — MapKit, a third-party renderer, or your tiles?
- How do you reroute when the user leaves the polyline without melting the battery?
- Match a rider to nearby drivers — what index, and what if the ping is 30 seconds old?

## Design a wallet / balances screen {#wallet}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design a **wallet** home: several balances (cards, deposits, points) from **different APIs** with different latency. Scope: one user, one device. Talk how you merge the streams, what you show while some calls are still in flight, pagination / local search on history, offline last-known amounts, and where you mask money. Do not design the bank core.

### Follow-ups

- One slow microservice — do you block the whole screen?
- Push vs pull vs open-screen refresh for a balance change?
- Where does the masked amount live so a screenshot is not the real figure?

## Design iCloud-style device sync {#icloud-sync}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design **cross-device sync** for notes or photos. Scope: the **phone is the source of truth** while offline; the server is a replica that may store **opaque blobs**. Talk change tokens / deltas, conflict policy (LWW vs CRDT vs prompt), and what a 30-second `BGAppRefresh` can actually do. Do not design a generic cloud database.

### Follow-ups

- What may the server see — plaintext rows, or ciphertext the SEP never left?
- Four devices reconnect after a week, one clock is skewed — how do you merge?
- LWW for a profile photo vs a CRDT for a shared album — why both?
- Nearby devices over local radio vs the cloud replica — when do you skip the server?
- Version vectors on device, server only detects conflict — when is that better than a server-side diff?

## Design a home screen of rails {#home-rails}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design a **Home** of independent rails (hero, continue, trending, ads). Scope: each rail owns fetch, loading, analytics, and cells. Name `UICollectionViewCompositionalLayout` + a diffable snapshot per section (or one snapshot with section IDs). One giant view controller that maps every cell type is the miss. Backend-driven card types are a follow-up, not the first drawing.

### Follow-ups

- How do two teams ship two rails without merge hell?
- One slow rail — do you block first paint?
- Orthogonal (horizontal) section vs a nested collection in a table cell?

## Design an offline media catalog {#offline-media}

- Level: Senior
- Frequency: High
- Kind: Practice

### Prompt

Design **offline downloads** for a streaming catalog (video or audio). Scope: resumable `URLSession` background transfers, a persistent queue, **disk quota**, license / expiry, and resume-after-kill. Playback is `{#video-streaming}` / `{#audio-player}` — here you own the catalog and the files. Do not hand-wave “save the MP4.”

### Follow-ups

- Where does the DRM license live relative to the bytes?
- User deletes one title vs the OS evicts under storage pressure — same path?
- How do you pick what to evict when the quota is full?

## Design clipboard / proximity sync {#clipboard-sync}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Design **copy on phone, paste on laptop** (and the reverse). Scope: same iCloud account, devices nearby vs far, a size cap, end-to-end encryption. Nearby can use a local radio; far uses the same sync pipe as `{#icloud-sync}`. Conflict is “last copy wins.” Do not design a general file locker.

### Follow-ups

- What do you put on the relay — plaintext, or a blob the SEP unwraps?
- Huge video on the clipboard — do you sync the bytes or a placeholder?
- How do you stop a stolen laptop from reading the last copy forever?

## Design a Recently Deleted album {#recently-deleted}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Design **Recently Deleted** for a Photos-style library. Scope: 30-day tombstones, restore, secure purge, disk pressure (purge oldest first), and what syncs to other devices. The live library and the trash are two queries over one store, not a second app. Do not design the camera.

### Follow-ups

- Restore after the tombstone expired on device A but not yet on device B?
- Low storage — who decides to purge, you or the OS?
- How is a trash item different from a hidden / archived one?

## Design a short match / score simulator {#match-simulator}

- Level: Mid
- Frequency: High
- Kind: Practice

### Prompt

Build a **small match simulator** in 90 minutes: pick two sides from a bundled JSON list, then a “next event” button that applies a **random outcome** and updates a scoreboard. Scope: two innings (or two halves), a ball/event cap, a wicket/life cap, chase ends when the target is passed. **UI polish is out.** The interview is a rules module you can extend (extra event, weighted odds) without rewriting the scorer. Do not paste a third-party solution.

### Follow-ups

- Wide / extra / “cannot be out” — what type do you add, and what stays closed?
- Weighted outcomes — where does randomness live so tests are deterministic?
- First screen is a list of sides with images — local JSON or a network call?
