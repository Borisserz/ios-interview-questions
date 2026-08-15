# Algorithms

Coding-interview prompts that showed up in iOS loops. **Practice** cards are prompts only.

- [Two-sum](#two-sum)
- [Balanced parentheses](#balanced-parens)
- [Binary tree by column](#tree-columns)
- [Remove duplicates from a sorted list](#sorted-list-dups)
- [Big-O](#big-o)
- [Recursion](#recursion)
- [Fibonacci](#fibonacci)
- [Reverse an integer](#reverse-integer)
- [Palindrome](#palindrome)
- [Second largest](#second-largest)
- [Sliding window](#sliding-window)
- [Graph traversal](#graph-traversal)
- [Product except self](#product-except-self)
- [Peak element](#peak-element)
- [Anagram](#anagram)
- [Three-sum](#three-sum)
- [Linked-list cycle](#linked-list-cycle)
- [Merge intervals](#merge-intervals)
- [Prefix trie](#trie)
- [Reverse a linked list](#reverse-list)
- [Odd-even linked list](#odd-even-list)
- [Merge two sorted lists](#merge-lists)
- [Serialize a binary tree](#serialize-tree)
- [Phone keypad combinations](#phone-keypad)
- [Circular buffer](#circular-buffer)
- [Rate limiter](#rate-limiter)
- [Merge k sorted lists](#merge-k-lists)
- [In-memory file system](#in-memory-fs)

## Two-sum {#two-sum}

- Level: Mid
- Frequency: High
- Kind: Practice

### Prompt

Given an array of integers and a target sum, return the indices of two numbers that add up to the target (or say it is impossible). Talk through the `O(n)` hash-map pass, then what changes for 3-sum.

### Follow-ups

- What if the same index must not be used twice?
- Sorted input — can you do it with two pointers?
- How do you extend this to 3-sum without `O(n³)`?

## Balanced parentheses {#balanced-parens}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Given a string of brackets `()[]{}`, decide if every opener has a matching closer in the right order. Stack: push openers, pop on a closer, fail on mismatch or leftover.

### Follow-ups

- What about only `()` — can you use a counter?
- How do you report the first bad index?
- Unicode / other opener-closer pairs?

## Binary tree by column {#tree-columns}

- Level: Senior
- Frequency: Low
- Kind: Practice

### Prompt

Print (or return) a binary tree in **column order**: nodes with the same horizontal index together, left to right, top to bottom. BFS with `(node, column)`, group by column, then sort columns.

### Follow-ups

- What is the column of the root, and of a left child?
- How do you keep order inside a column without a sort?
- What if they ask for a vertical zigzag instead?
- Largest value in each row — BFS level vs DFS with a depth map?

## Remove duplicates from a sorted list {#sorted-list-dups}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Given the head of a **sorted** singly linked list, delete duplicates so each value appears once. Walk with a `current` pointer: if `current.val == current.next.val`, skip the next node; else advance. Talk through the unsorted variant (`Set` of seen values) and why sorted lets you do it in `O(1)` extra space.

### Follow-ups

- What if they ask to drop *all* copies of a duplicated value, not keep one?
- Doubly linked — does the algorithm change?
- Array input instead of a list — in-place two pointers?

## Big-O {#big-o}

- Level: Junior
- Frequency: High

### Answer

Big-O is how an algorithm’s cost **grows** with input size — time or extra memory, worst case unless you say otherwise. Interviewers want the common iOS ones: array index `O(1)`, `contains` on an array `O(n)`, `Set` / `Dictionary` lookup average `O(1)`, sort `O(n log n)`, nested loops `O(n²)`. It is not “this function is slow on my phone.” A hash table can still be `O(n)` if you hash badly. Typical miss: calling `filter` + `contains` in a loop and saying the code is `O(n)`.

### Example

```swift
func hasOverlap(_ ids: [Int]) -> Bool {
    var seen = Set<Int>()          // lookup O(1) average
    for id in ids {                // n
        if seen.contains(id) { return true }
        seen.insert(id)
    }
    return false
}
```

### Follow-ups

- Average vs worst case for `Dictionary`?
- What is the complexity of `String.count` in Swift?
- Space complexity of this `Set` approach?

## Recursion {#recursion}

- Level: Junior
- Frequency: Medium

### Answer

A function that calls itself with a **smaller** problem and a **base case** that stops. Trees, DFS, and `Codable` containers are the usual iOS examples. Each call needs a stack frame — a deep list can overflow. Tail-call optimization is not something you should count on in Swift. Prefer an explicit stack / queue when the depth is user data. Typical miss: no base case, or recursing on the same value.

### Example

```swift
func depth(_ node: Node?) -> Int {
    guard let node else { return 0 }
    return 1 + max(depth(node.left), depth(node.right))
}
```

### Follow-ups

- Recursion vs an explicit stack — when do you switch?
- What fails first on a 100k-node linked list — time or stack?
- How does this show up in a JSON decoder?

## Fibonacci {#fibonacci}

- Level: Junior
- Frequency: High
- Kind: Practice

### Prompt

Given `n`, return the `n`th Fibonacci number (or the first `n` terms). Talk through the naive recursive tree (`O(φ^n)`), then the `O(n)` loop with two running values. Mention overflow (`Int`) and why memoization still uses linear space.

### Follow-ups

- Why is the recursive version a bad interview default?
- Iterative vs matrix exponentiation — when would you mention `O(log n)`?
- How do you test `n = 0` and `n = 1`?

## Reverse an integer {#reverse-integer}

- Level: Junior
- Frequency: Medium
- Kind: Practice

### Prompt

Given a signed 32-bit integer, reverse its digits (`1234 → 4321`, `-120 → -21`). Handle overflow: if the reverse does not fit in `Int32`, say so. Prefer arithmetic (`result = result * 10 + digit`) over `String` if they want complexity talk.

### Follow-ups

- What do you return on overflow — `0`, `nil`, or `throw`?
- Why is `String(n).reversed()` a weaker answer?
- How does this change if leading zeros matter (they do not, for an `Int`)?

## Palindrome {#palindrome}

- Level: Junior
- Frequency: Medium
- Kind: Practice

### Prompt

Decide if an integer (or a string) reads the same forwards and backwards. For an `Int`, reverse half the digits or compare to the reversed value and watch overflow. For a `String`, two pointers on `Character` (not UTF-8 indexes) after you define the alphabet (ignore case / punctuation?).

### Follow-ups

- Half-reverse so you never build the full reversed `Int`?
- Unicode — is `"é"` one character?
- Linked-list palindrome — extra `O(n)` memory vs reverse-second-half?

## Second largest {#second-largest}

- Level: Junior
- Frequency: Medium
- Kind: Practice

### Prompt

One pass over `[Int]`: keep `largest` and `second`. Define ties (two copies of the max — is the second the same value or the next distinct?). Empty and one-element arrays are the traps. Sorting then picking `n-2` is `O(n log n)` and they will ask you to do better.

### Follow-ups

- Distinct vs allowing duplicates?
- What if every value is equal?
- `k`th largest — heap vs Quickselect?

## Sliding window {#sliding-window}

- Level: Mid
- Frequency: High
- Kind: Practice

### Prompt

A string (or array) and a constraint: longest substring with ≤ K distinct characters, or the first window that matches a condition. Talk the two-pointer move: expand right, shrink left, keep a count map. Name `O(n)` time if each index enters and leaves once. Follow-up they like: the input becomes a *stream* — what do you keep in the buffer?

### Follow-ups

- Fixed window vs variable window — which map do you need?
- Unicode: do you window on `Character` or UTF-8?
- Stream / “print matching queries” — queue vs the same two pointers?

## Graph traversal {#graph-traversal}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

An acyclic connected graph (or a tree with extra edges). Walk BFS vs DFS in Swift: adjacency list `[Node: [Node]]`, a `Set` for visited, a queue (`Array` + index, not `removeFirst` in a loop). Say when you need a parent map (shortest unweighted path) vs a color / two-set split (bipartite). Do not claim you will write a matrix unless V is tiny.

### Follow-ups

- Why is `removeFirst()` on `Array` a trap for BFS?
- Directed vs undirected — what do you store twice?
- Nodes painted black/white — what extra state do you keep?

## Product except self {#product-except-self}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Given `[Int]`, return an array where `out[i]` is the product of every element except `nums[i]`. Do it in `O(n)` without using division (zeros make division a trap anyway). Talk prefix products from the left, then a running suffix from the right into the same output buffer.

### Follow-ups

- What do you do with one zero? With two zeros?
- Can you do it in `O(1)` extra space besides the output array?
- Why is “divide the total product” a weaker answer?

## Peak element {#peak-element}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

A peak is an index whose value is strictly greater than its neighbors (ends compare to one neighbor). Return any peak. The usual follow-up is `O(log n)`: binary search on an unsorted array — if `mid < mid+1`, a peak exists on the right; else on the left. Say why that is legal even though the array is not sorted.

### Follow-ups

- Any peak vs the global maximum — which one did they ask for?
- How do plateaus (`[1,2,2,1]`) change the comparison?
- 2D peak — what is the interview-sized approach?

## Anagram {#anagram}

- Level: Junior
- Frequency: Medium
- Kind: Practice

### Prompt

Decide if two strings are anagrams (same characters, same counts, order ignored). Define the alphabet first: ASCII letters only, or Unicode `Character`? Counting sort / `[Int]` of size 26 is the fast English answer; a `[Character: Int]` map is the honest Unicode one. Sorting both and comparing is `O(n log n)` and they will ask you to do better.

### Follow-ups

- Case and spaces — do `"Listen"` and `"Silent"` match?
- How do you return the grouped anagrams of a list of words?
- Why is `String` sorted comparison a weaker default?

## Three-sum {#three-sum}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Find all unique triplets in an `Int` array that sum to zero (or to a target). Scope: `O(n²)` is the expected spoken answer — sort, then for each index two-pointer the rest; skip duplicates. Do not paste a playground solution. Mention why a nested `O(n³)` triple loop dies in an interview, and how this relates to two-sum.

### Follow-ups

- How do you skip duplicate triplets after the sort?
- Three-sum closest vs exact zero — what changes?
- Would a hash set per index beat two pointers here?

## Linked-list cycle {#linked-list-cycle}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Detect whether a singly linked list has a cycle. Speak Floyd: slow +1, fast +2; they meet iff a cycle exists. Mention the `O(n)` set-of-nodes answer and why they want `O(1)` extra space. Finding the cycle *start* is the follow-up (reset one pointer to head, walk together).

### Follow-ups

- How do you find the node where the cycle begins?
- What if the list is empty or has one node?
- Why does meeting prove a cycle, not just “fast lapped slow once”?

## Merge intervals {#merge-intervals}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Given half-open or closed intervals `[start, end]`, return the merged set. Sort by start, then fold: if the next start is `<=` current end, extend the end; else emit and start a new one. Speak `O(n log n)` from the sort. Calendars and download ranges are the usual story.

### Follow-ups

- Inclusive vs exclusive ends — does `[1,2]` touch `[2,3]`?
- Insert one new interval into an already-merged list — can you do better than re-sort?
- How does this relate to “meeting rooms” / calendar conflicts?

## Prefix trie {#trie}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Implement a prefix tree: `insert`, `contains`, and `autocomplete(prefix, limit)`. Each node is a map of character → child plus an “end of word” (and optional frequency). Speak `O(L)` insert/search. Keyboard / on-device search is the story; do not build a full Spotlight index.

### Follow-ups

- How do you rank top-K completions without walking the whole subtree every keystroke?
- Delete a word — when can you prune a node?
- Trie vs a sorted array + binary search for a fixed dictionary?

## Reverse a linked list {#reverse-list}

- Level: Mid
- Frequency: High
- Kind: Practice

### Prompt

Reverse a singly linked list in place. Speak the three-pointer walk (`prev`, `curr`, `next`) and `O(1)` extra space. Recursive reverse is the follow-up (stack is `O(n)`). Empty list and a single node must stay correct.

### Follow-ups

- Reverse only nodes `m…n` (a sublist)?
- Recursive vs iterative — what is the space trade-off?
- How do you reverse a doubly linked list?

## Odd-even linked list {#odd-even-list}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Group a singly linked list as **odd-index nodes, then even-index nodes**, relative order kept, **in place**. Index 1 is odd. Speak two tails (`odd`, `even`) and splice `evenHead` after the last odd. Do not allocate a new list. Dry-run a 1–5 list before you claim done.

### Follow-ups

- Even count vs odd count — where does `even.next` become `nil`?
- One node / two nodes — what must not break?
- How is this different from “values that are odd, then even”?

## Merge two sorted lists {#merge-lists}

- Level: Junior
- Frequency: High
- Kind: Practice

### Prompt

Merge two sorted singly linked lists into one sorted list. Dummy head + two pointers, always take the smaller `val`, then append the leftover tail. `O(n+m)` time, `O(1)` extra if you reuse nodes.

### Follow-ups

- Merge `k` sorted lists — heap vs pairwise?
- Arrays instead of lists — same idea?
- What if a list can contain duplicates?

## Serialize a binary tree {#serialize-tree}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Turn a binary tree into a string (or array) and rebuild the same shape. Preorder with explicit nulls (`1,2,#,#,3,4,#,#,5,#,#`) is the usual spoken answer; BFS level-order with nulls also works. Speak why you must encode missing children or the rebuild is ambiguous.

### Follow-ups

- Why is inorder alone not enough?
- How do you bound the payload for a sync blob?
- BST — can you drop the null markers?

## Phone keypad combinations {#phone-keypad}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Given a digit string (`"23"`), return all letter combinations from the phone keypad (`2→abc` … `9→wxyz`). Backtrack: for each digit append one letter, recurse, pop. Speak `O(4^n)` worst case. `0`/`1` have no letters — skip or reject.

### Follow-ups

- Iterative queue vs recursion — same complexity?
- How do you cap output if `n` is 12?
- Map as an array of 10 strings vs a dictionary?

## Circular buffer {#circular-buffer}

- Level: Mid
- Frequency: Medium

### Answer

A **ring buffer** is a fixed array plus `head` / `count` (or head and tail). Write advances the tail; read advances the head; both wrap with `% capacity`. When full you either **drop the oldest** (audio / telemetry) or **refuse the write**. No `remove(at: 0)` on an `Array` — that is `O(n)`. Interview story: a real-time audio or sensor queue that must not allocate under load. Typical miss: off-by-one when `count == capacity`, or forgetting the wrap so you overwrite unread samples.

### Example

```swift
struct RingBuffer<T> {
    private var slots: [T?]
    private var head = 0
    private var count = 0

    init(capacity: Int) { slots = .init(repeating: nil, count: max(1, capacity)) }

    mutating func push(_ value: T) {
        let i = (head + count) % slots.count
        if count == slots.count { head = (head + 1) % slots.count }
        else { count += 1 }
        slots[i] = value
    }

    mutating func pop() -> T? {
        guard count > 0 else { return nil }
        defer { slots[head] = nil; head = (head + 1) % slots.count; count -= 1 }
        return slots[head]
    }
}
```

### Follow-ups

- Drop-oldest vs back-pressure — which for a mic callback?
- How do you make push/pop safe across two threads?
- Why not `Array` + `removeFirst()` for a 48 kHz stream?

## Rate limiter {#rate-limiter}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Allow at most `N` events per key in a sliding window of `W` seconds. Speak a deque of timestamps: drop those older than `now - W`, then accept or reject. Mention token bucket as the follow-up (refill rate, burst). Concurrency: one lock per key, not one global lock. Do not paste a production Redis design unless they pull you there.

### Follow-ups

- Sliding-window log vs counter vs token bucket — one sentence each?
- What is the space bound if every unique key stays forever?
- How do you avoid one lock for the whole process?

## Merge k sorted lists {#merge-k-lists}

- Level: Mid
- Frequency: Medium
- Kind: Practice

### Prompt

Merge `k` sorted singly linked lists into one sorted list. Heap of the current head of each list is `O(N log k)`. Pairwise merge is simpler and `O(N log k)` if you tournament-merge. Speak why comparing only `val` can crash when two nodes are equal (tie-break with an index). `{#merge-lists}` is the `k = 2` case.

### Follow-ups

- Heap vs flatten-and-sort — when is sort honest?
- How do you keep stability when two heads have the same `val`?
- What if `k` is huge and most lists are empty?

## In-memory file system {#in-memory-fs}

- Level: Senior
- Frequency: Medium
- Kind: Practice

### Prompt

Implement `mkdir`, `addContent` (append), `readContent`, and `ls` on a path tree. Each directory node is a map of name → child; a file node holds a string. Speak path split, create-on-write, and what `ls` returns for a file vs a directory. Locks and huge-file storage are follow-ups, not the first API.

### Follow-ups

- One global lock vs a lock per directory — what deadlocks?
- How do you represent a 2 GB file without one `String`?
- `ls /a/b` when `b` is a file — names or the file name only?
- They say “code the file system, not the boxes” — which four methods do you lock first?
