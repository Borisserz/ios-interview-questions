# Security

8 cards · 6 often asked · source [security.md](../../topics/security.md)

### Junior

<h2 id="ats">App Transport Security</h2>

<code>Junior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

ATS is the OS rule that App Transport / `URLSession` must use HTTPS with modern TLS (TLS 1.2+, forward secrecy, accepted ciphers). A cleartext `http://` load fails unless you add an explicit Info.plist exception. The nuclear key is `NSAllowsArbitraryLoads` — interviewers treat that as a smell; prefer a per-domain `NSExceptionDomains` entry and a reason you can defend. ATS does not encrypt your payload for you beyond TLS, and it does not replace certificate pinning. Local `http://localhost` in debug is a common exception; shipping that exception to production is not.



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


**Then they usually ask**

- Why is `NSAllowsArbitraryLoads` a review and security problem?
- What does ATS actually require of a certificate and cipher suite?
- How is ATS different from SSL pinning?
- When is `NSAllowsLocalNetworking` the right exception?

</details>

<h2 id="app-sandbox">App Sandbox</h2>

<code>Junior</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Every iOS app runs in a **sandbox**: the process can only see its own container (`Documents`, `Library`, `tmp`) plus the files the user or the system explicitly grants (photo picker, Files, iCloud, App Groups). You cannot walk another app’s directory or write outside the container. That is why “just save to `/var`” fails, why a share extension needs an App Group, and why Keychain / UserDefaults are per-app (or per group) rather than global. Interviewers want the isolation story, not a macOS entitlements dump. Typical miss: treating the sandbox as a Debug setting, or assuming `FileManager.default` can read the camera roll without a picker.



```swift
let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
let file = docs.appendingPathComponent("draft.json")
try data.write(to: file, options: .atomic)
// This path is yours. Another app’s Documents is not.
```


**Then they usually ask**

- App Group vs the app container — what can a widget read?
- Why does `Data(contentsOf: fileURL)` fail for a photo library asset URL?
- What still escapes the sandbox — Keychain access groups, iCloud, shared pasteboard?

</details>

### Mid

<h2 id="api-keys">API keys</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

An API key in the app binary is **extractable**. Strings in the IPA, a plist, or `#if DEBUG` still ship if you are careless. Treat a client key as an identifier, not a secret: restrict it on the provider (bundle ID, App Attest, referrer), rate-limit, and put the real secret on **your** server. Shipping a third-party private key (Stripe, AWS) in the client is a hard fail. Obfuscation and splitting the string only slow a determined reader. Typical miss: “it’s in xcconfig so it’s safe.”



```swift
// Client may know a publishable / restricted key.
// The secret stays on the backend.
enum Config {
    static let mapsKey = Bundle.main.object(forInfoDictionaryKey: "MAPS_KEY") as? String
}
```


**Then they usually ask**

- Why is hiding a key in a Swift string still not a secret?
- When do you use a backend proxy instead of calling the vendor from the phone?
- How does App Attest change this story?

</details>

<h2 id="encoding-vs-encryption">Encoding vs encryption vs hashing</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Three different jobs. **Encoding** (JSON, Base64, UTF-8) changes representation so a system can carry bytes — it is reversible with no secret. **Encryption** hides data; you need a key to get the plaintext back (AES-GCM in CryptoKit, TLS on the wire). **Hashing** is one-way: SHA-256, HMAC. Interviewers use Base64 as the trap: `Data.base64EncodedString()` is not a vault. Typical miss: “we encrypt the token” and then showing a Base64 string in UserDefaults, or calling `hashValue` a secure hash.



```swift
import CryptoKit

let bytes = Data("secret".utf8)
let encoded = bytes.base64EncodedString()          // not secret
let digest = SHA256.hash(data: bytes)              // not reversible
let box = try AES.GCM.seal(bytes, using: key)      // secret if the key is
```


**Then they usually ask**

- Why is Base64 on a JWT payload not encryption?
- Hash vs HMAC vs encrypt — which one for a password, a file check, a token at rest?
- Where does TLS sit in this list?

</details>

<h2 id="biometrics">Face ID / Touch ID</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Local Authentication is how you prove the person at the device is the enrolled owner — not how you authenticate to your server. You create an `LAContext`, call `canEvaluatePolicy(_:error:)`, then `evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, ...)`. Face ID needs `NSFaceIDUsageDescription` in Info.plist; Touch ID does not show a usage string. The biometric match happens in the Secure Enclave; your process only gets a yes/no. Treat a success as “unlock this local secret” — then read a token from Keychain that you already issued after a real login. Always offer a passcode fallback (`deviceOwnerAuthentication`) and handle `.userFallback`, lockout, and “biometry not enrolled.”



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


**Then they usually ask**

- Why is a biometric success not enough to mint a new server session?
- When do you use `.deviceOwnerAuthentication` vs `.deviceOwnerAuthenticationWithBiometrics`?
- How do you bind a Keychain item so it is only readable after Face ID?
- What do you show if the user disables biometrics after enrollment?

</details>

<h2 id="keychain">Keychain</h2>

<code>Mid</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Keychain is the encrypted, OS-managed store for secrets: tokens, passwords, keys. Data is protected by the device passcode and, if you ask, by biometrics; it can survive app delete if you use the right accessibility and access group. You talk to it through Security.framework (`SecItemAdd`, `SecItemCopyMatching`, `SecItemUpdate`, `SecItemDelete`) or a thin wrapper. `UserDefaults` and files on disk are the wrong place for a refresh token. Set `kSecAttrAccessible` to match the threat: `WhenUnlockedThisDeviceOnly` is the usual app-token default; `AfterFirstUnlock` is for background refresh. iCloud Keychain sync is opt-in via `kSecAttrSynchronizable` and is a product decision, not a default.



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


**Then they usually ask**

- `WhenUnlocked` vs `AfterFirstUnlock` vs `ThisDeviceOnly` — which token needs which?
- How do you share a Keychain item with an app extension?
- What happens to Keychain items when the user uninstalls the app?
- Why not store a refresh token in `UserDefaults` “because it is already on a locked phone”?

</details>

<h2 id="secure-hash">Secure hash</h2>

<code>Mid</code> · <code>Medium</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

A cryptographic hash is a one-way, fixed-size digest. On Apple platforms you use CryptoKit (`SHA256`, `SHA384`, `SHA512`) — not `String.hashValue` (not stable, not cryptographic) and not MD5 / SHA-1 for anything security-related. Hashing is not encryption: you cannot get the input back, and you should not store a password as raw SHA-256. Password storage belongs on the server with a slow password hash (Argon2, scrypt, or PBKDF2). Typical client uses are file integrity, a fingerprint of canonical bytes, and HMAC when you also have a key. If an attacker who stole the digest file is in the threat model, a bare hash is not enough — use HMAC or a signature.



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


**Then they usually ask**

- Why is `hashValue` unusable for a cache key you persist?
- Hash vs HMAC vs encrypt — which problem does each solve?
- Where should password hashing run, and which algorithm do you expect?
- When would you use SHA-256 of a file versus a code-signing check?

</details>

### Senior

<h2 id="ssl-pinning">SSL pinning</h2>

<code>Senior</code> · <code>High</code>

<details>
<summary><strong>Show answer and Swift</strong></summary>

Pinning means the app accepts **only a known certificate or public key**, not just “any cert the system trusts.” It blocks a rogue CA / corporate MITM. **Certificate pin** breaks when the server rotates the cert. **Public-key pin** survives a re-issue of the same key. You implement it in `URLSessionDelegate` (`didReceive challenge`) or a pin in the ATS / Info.plist (limited). Always ship a backup pin and a kill-switch — a bad pin **bricks** the app until you ship a store build. Typical miss: pinning the leaf cert with no backup, or pinning in debug against Charles and forgetting to turn it off.



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


**Then they usually ask**

- Certificate pin vs public-key pin?
- How do you rotate a pin without a forced update?
- What does ATS already give you without pinning?

</details>
