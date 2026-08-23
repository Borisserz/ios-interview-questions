# Безопасность

8 карточек · 6 часто спрашивают · [security.md](../../topics/security.md)

### Junior

<h2 id="ats">App Transport Security</h2>

<code>Junior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

ATS — правило ОС: App Transport / URLSession обязаны ходить HTTPS с современным TLS — TLS 1.2+, forward secrecy, принятые шифры. Чистый http упадёт, пока явно не пропишешь исключение в Info.plist. Ядерный ключ — NSAllowsArbitraryLoads: на собесе это запах; лучше per-domain NSExceptionDomains и причина, которую защитишь. ATS сам по себе не шифрует пейлоад сверх TLS и не заменяет certificate pinning. Локальный http://localhost в дебаге — частое исключение; везти его в прод нельзя.



```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>debug.internal.example</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
            <key>NSIncludesSubdomains</key>
            <true/>
        </dict>
    </dict>
</dict>
```


**Потом обычно спрашивают**

- Почему NSAllowsArbitraryLoads — проблема и ревью, и безопасности?
- Чего ATS требует от сертификата и cipher suite?
- Чем ATS отличается от SSL pinning?
- Когда правильное исключение — NSAllowsLocalNetworking?

</details>

<h2 id="app-sandbox">App Sandbox</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Каждое iOS-приложение живёт в sandbox: процесс видит только свой контейнер — Documents, Library, tmp — плюс файлы, которые явно дал пользователь или система: photo picker, Files, iCloud, App Groups. Чужую директорию не обойдёшь и писать вне контейнера нельзя. Поэтому «просто сохрани в /var» падает, share extension нужен App Group, а Keychain / UserDefaults — per-app или per-group, не глобальные. На собесе хотят историю изоляции, не дамп entitlements с macOS. Типичный промах: считать sandbox настройкой Debug или ждать, что FileManager прочитает камеру без пикера.



```swift
let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
let file = docs.appendingPathComponent("draft.json")
try data.write(to: file, options: .atomic)
// This path is yours. Another app’s Documents is not.
```


**Потом обычно спрашивают**

- App Group и контейнер приложения — что может прочитать виджет?
- Почему Data(contentsOf:) падает на URL ассета из фотобиблиотеки?
- Что всё-таки выходит из sandbox — access group Keychain, iCloud, общий буфер обмена?

</details>

### Mid

<h2 id="api-keys">API-ключи</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

API-ключ в бинарнике приложения достаётся. Строки в IPA, plist или #if DEBUG всё равно уедут, если неаккуратен. Клиентский ключ — идентификатор, не секрет: режь его у провайдера (bundle ID, App Attest, referrer), ставь rate-limit, настоящий секрет держи на своём сервере. Везти приватный ключ третьей стороны — Stripe, AWS — в клиенте это жёсткий провал. Обфускация и нарезка строки только замедляют упрямого читателя. Типичный промах: «лежит в xcconfig, значит безопасно».



```swift
// Client may know a publishable / restricted key.
// The secret stays on the backend.
enum Config {
    static let mapsKey = Bundle.main.object(forInfoDictionaryKey: "MAPS_KEY") as? String
}
```


**Потом обычно спрашивают**

- Почему спрятанный ключ в Swift-строке всё равно не секрет?
- Когда прокси на бэкенде вместо вызова вендора с телефона?
- Как App Attest меняет эту историю?

</details>

<h2 id="encoding-vs-encryption">Encoding, encryption и hashing</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Три разные работы. Encoding — JSON, Base64, UTF-8 — меняет представление, чтобы система могла нести байты: обратимо, секрета нет. Encryption прячет данные: чтобы вернуть plaintext, нужен ключ — AES-GCM в CryptoKit, TLS в проводе. Hashing односторонний: SHA-256, HMAC. На собесе ловушка — Base64: base64EncodedString — не сейф. Типичный промах: «мы шифруем токен» и показать Base64-строку в UserDefaults, или назвать hashValue безопасным хешем.



```swift
import CryptoKit

let bytes = Data("secret".utf8)
let encoded = bytes.base64EncodedString()          // not secret
let digest = SHA256.hash(data: bytes)              // not reversible
let box = try AES.GCM.seal(bytes, using: key)      // secret if the key is
```


**Потом обычно спрашивают**

- Почему Base64 на пейлоаде JWT — не шифрование?
- Hash, HMAC, encrypt — что на пароль, проверку файла, токен at rest?
- Где в этом списке сидит TLS?

</details>

<h2 id="biometrics">Face ID / Touch ID</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Local Authentication доказывает, что у устройства сидит записанный владелец — не то, как ты логинишься на сервер. Создаёшь LAContext, спрашиваешь canEvaluatePolicy, потом evaluatePolicy с deviceOwnerAuthenticationWithBiometrics. Face ID нужен NSFaceIDUsageDescription в Info.plist; у Touch ID usage-строки нет. Совпадение биометрии происходит в Secure Enclave; твой процесс получает только да/нет. Успех трактуй как «открой этот локальный секрет» — потом читаешь токен из Keychain, который уже выдал настоящий логин. Всегда давай запасной проход по паролю — deviceOwnerAuthentication — и обрабатывай userFallback, lockout и «биометрия не записана».



```swift
import LocalAuthentication

func unlockLocalSecret() async throws {
    let context = LAContext()
    var error: NSError?
    guard context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error) else {
        throw error ?? LAError(.biometryNotAvailable)
    }
    try await context.evaluatePolicy(
        .deviceOwnerAuthentication,
        localizedReason: "Unlock your saved session"
    )
    // Now read the token from Keychain — do not invent a new session here.
}
```


**Потом обычно спрашивают**

- Почему успеха биометрии мало, чтобы выписать новую серверную сессию?
- Когда deviceOwnerAuthentication, а когда WithBiometrics?
- Как привязать элемент Keychain, чтобы его читали только после Face ID?
- Что показываешь, если человек выключил биометрию после записи?

</details>

<h2 id="keychain">Keychain</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Keychain — зашифрованное, ОС-управляемое хранилище секретов: токены, пароли, ключи. Данные защищены паролем устройства и, если попросишь, биометрией; могут пережить удаление приложения при правильном accessibility и access group. Говоришь через Security.framework — SecItemAdd, SecItemCopyMatching, SecItemUpdate, SecItemDelete — или тонкую обёртку. UserDefaults и файлы на диске — не место для refresh token. kSecAttrAccessible ставь под угрозу: WhenUnlockedThisDeviceOnly — обычный дефолт для токена приложения; AfterFirstUnlock — для фонового рефреша. Синк iCloud Keychain — opt-in через kSecAttrSynchronizable, продуктовое решение, не дефолт.



```swift
func saveToken(_ token: String) throws {
    let data = Data(token.utf8)
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrService as String: "com.example.session",
        kSecAttrAccount as String: "refresh",
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
    ]
    SecItemDelete(query as CFDictionary)
    let status = SecItemAdd(query as CFDictionary, nil)
    guard status == errSecSuccess else { throw KeychainError.status(status) }
}
```


**Потом обычно спрашивают**

- WhenUnlocked, AfterFirstUnlock, ThisDeviceOnly — какому токену что?
- Как шарить элемент Keychain с app extension?
- Что будет с элементами Keychain, когда пользователь снесёт приложение?
- Почему refresh token не класть в UserDefaults «телефон и так под паролем»?

</details>

<h2 id="secure-hash">Криптографический хеш</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Криптографический хеш — односторонний дайджест фиксированного размера. На платформах Apple берёшь CryptoKit: SHA256, SHA384, SHA512 — не String.hashValue (не стабилен, не крипто) и не MD5 / SHA-1 для чего-то секретного. Хеш — не шифрование: вход обратно не достанешь, пароль сырым SHA-256 не хранишь. Пароли хеширует сервер медленной функцией: Argon2, scrypt или PBKDF2. На клиенте обычно целостность файла, отпечаток канонических байт и HMAC, когда ещё есть ключ. Если в модели угроз вор, который украл файл дайджестов, голого хеша мало — HMAC или подпись.



```swift
import CryptoKit

func sha256Hex(_ data: Data) -> String {
    let digest = SHA256.hash(data: data)
    return digest.map { String(format: "%02x", $0) }.joined()
}

func hmac(_ data: Data, key: SymmetricKey) -> String {
    let mac = HMAC<SHA256>.authenticationCode(for: data, using: key)
    return Data(mac).base64EncodedString()
}
```


**Потом обычно спрашивают**

- Почему hashValue нельзя на ключ кэша, который персистишь?
- Hash, HMAC, encrypt — какую задачу каждый решает?
- Где должен бежать хеш пароля и какой алгоритм ждёшь?
- Когда SHA-256 файла, а когда проверка code signing?

</details>

### Senior

<h2 id="ssl-pinning">SSL pinning</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Pinning значит: приложение принимает только известный сертификат или публичный ключ, не «любой сертификат, которому система доверяет». Режет мошеннический CA и корпоративный MITM. Pin на сертификат ломается, когда сервер ротирует сертификат. Pin на публичный ключ переживает перевыпуск того же ключа. Делаешь в URLSessionDelegate на didReceive challenge или ограниченный pin в ATS / Info.plist. Всегда вези запасной pin и kill-switch — плохой pin кирпичит приложение, пока не выйдет сборка из стора. Типичный промах: запинить leaf без бэкапа или запинить в дебаге под Charles и забыть выключить.



```swift
func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge,
                completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
    guard let trust = challenge.protectionSpace.serverTrust,
          pinned(trust) else {
        completionHandler(.cancelAuthenticationChallenge, nil)
        return
    }
    completionHandler(.useCredential, URLCredential(trust: trust))
}
```


**Потом обычно спрашивают**

- Pin сертификата и pin публичного ключа?
- Как ротировать pin без принудительного апдейта?
- Что ATS уже даёт без pinning?

</details>
