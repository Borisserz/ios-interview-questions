# Objective-C runtime

18 карточек · 6 часто спрашивают · [objc-runtime.md](../../topics/objc-runtime.md)

### Junior

<h2 id="nserror">NSError</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

NSError — объект ошибки Cocoa: domain-строка, целочисленный code, словарь userInfo — локализованное описание, underlying error, падающий URL. API ObjC берут out-параметр NSError **. Swift многие из них импортирует как throws, код всё равно читаешь через error as NSError. В новых API лучше типизированный Swift Error; мост на границе. Типичный промах: смотреть только localizedDescription или игнорить NSUnderlyingErrorKey.



```swift
do {
    try data.write(to: url)
} catch {
    let ns = error as NSError
    print(ns.domain, ns.code, ns.userInfo[NSUnderlyingErrorKey] as Any)
}
```


**Потом обычно спрашивают**

- Domain плюс code и Swift enum Error?
- Что класть в userInfo?
- Как try мапит API с NSError **?

</details>

<h2 id="iskindof-vs-ismember">isKindOfClass и isMemberOfClass</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

isKindOfClass — этот класс или сабкласс. isMemberOfClass — ровно этот класс. isKindOfClass UIView истинен для UIButton. isMemberOfClass — нет. Бери isKindOfClass или Swift is / as?. Проверка точного класса ломается, когда UIKit отдаёт приватный сабкласс. Типичный промах: isMemberOfClass в хелпере таблицы, которому потом прилетит сабкласс хедера.



```objc
[button isKindOfClass:[UIView class]];    // YES
[button isMemberOfClass:[UIView class]];  // NO
```


**Потом обычно спрашивают**

- Как Swift is ложится на это?
- Почему проверка точного класса хрупка с системными типами?
- conformsToProtocol и isKindOfClass?

</details>

<h2 id="nil-null">nil, Nil, NULL, NSNull</h2>

<code>Junior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

nil — указатель на объект ObjC, сообщение в nil — no-op. Nil — указатель на класс. NULL — C-указатель, void *. NSNull — настоящий объект со смыслом «JSON null / дырка в коллекции»: nil в NSArray положить нельзя. Swift nil — Optional.none, другая модель. Типичный промах: вставить nil в словарь и упасть или считать NSNull за nil без проверки.



```objc
id obj = nil;
NSLog(@"%@", obj);           // (null), no crash
NSArray *a = @[ [NSNull null] ];
```


**Потом обычно спрашивают**

- Почему JSON нужен NSNull?
- Сообщение в nil и optional chaining в Swift?
- Nil и nil, когда шлёшь метод класса?

</details>

### Mid

<h2 id="objc-messaging">Messaging и nil</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

[obj foo] компилируется в objc_msgSend с объектом, SEL foo и аргументами. Рантайм ищет селектор в списке методов класса и цепочке суперклассов, потом прыгает в IMP. Сообщение в nil — no-op и возвращает ноль / nil, это не краш. Optional chaining в Swift — двоюродный брат. Динамический диспатч — почему работают категории, swizzling и KVO. Типичный косяк: «ObjC — просто C с объектами» и ни слова про objc_msgSend.



```objc
id obj = nil;
NSString *name = [obj description]; // nil, no crash
```


**Потом обычно спрашивают**

- Чем SEL отличается от IMP?
- Как рантайм находит метод класса против метода экземпляра?
- Что делает _objc_msgForward?

</details>

<h2 id="runloop">RunLoop</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

RunLoop — цикл событий, привязанный к потоку: ждёт sources — тачи, порты, таймеры, прыжки GCD на main — и гоняет их. У главного потока один, UIKit его уже запустил. У фонового нет, пока не вызовешь run у текущего NSRunLoop. Режимы фильтруют, какие sources стреляют. NSDefaultRunLoopMode — обычный; UITrackingRunLoopMode — то, чем пользуется скролл. NSRunLoopCommonModes включает оба. Типичный косяк: запустить Timer на главном run loop в default и удивляться, почему он молчит во время скролла.



```swift
RunLoop.main.add(timer, forMode: .common)
```


**Потом обычно спрашивают**

- RunLoop и очередь GCD?
- Что будет, если у фонового потока нет RunLoop, а ты поставил Timer?
- Как RunLoop устроен на высоком уровне — sleep плюс sources?
- Source0 и source1 — кто будит поток?
- Как держать фоновый поток живым без busy loop?

</details>

<h2 id="timer-runloop">Таймер молчит во время скролла</h2>

<code>Mid</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Timer.scheduledTimer кладёт таймер в текущий RunLoop в режиме default. Пока UIScrollView трекает, главный RunLoop в tracking, поэтому таймеры default не стреляют. Фикс: добавить таймер в common, или взять CADisplayLink, или GCD-таймер DispatchSourceTimer — он не на режимах. scheduledTimer на фоновом потоке тоже молчит, пока этот поток не крутит RunLoop. Типичный промах: «таймер сломан» и ни слова про режимы.



```swift
let timer = Timer(timeInterval: 1, repeats: true) { _ in tick() }
RunLoop.main.add(timer, forMode: .common)
```


**Потом обычно спрашивают**

- common и добавить таймер дважды — default плюс tracking?
- CADisplayLink и Timer для часов на скроллящемся экране?
- Почему у Task.sleep этой проблемы нет?
- Как стрелять таймер раз в минуту, пока приложение в фоне?

</details>

<h2 id="dynamic">@dynamic</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

@dynamic говорит компилятору: геттер/сеттер не синтезировать, они появятся в рантайме — аксессоры Core Data, скриптовое свойство. @synthesize или современный дефолт создаёт ivar и методы. В Swift двоюродный брат — @objc dynamic, нужен для KVO на Swift-свойстве. Типичный промах: повесить @dynamic на обычное stored-свойство и упасть на первом доступе.



```objc
@interface Note : NSManagedObject
@property (nonatomic, copy) NSString *title;
@end
@implementation Note
@dynamic title; // Core Data provides the accessors
@end
```


**Потом обычно спрашивают**

- @dynamic, @synthesize и дефолт Swift?
- Почему KVO в Swift нужен dynamic?
- Что будет, если рантайм так и не добавит метод?

</details>

<h2 id="underscore-vs-self">_ и self.</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

В ObjC _title — ivar; self.title идёт через аксессор: KVO, copy, свой сеттер, atomic-лок. Присвоение в _title это всё пропускает. В init и dealloc обычно трогаешь ivar, чтобы не вызвать оверрайд и не дёрнуть KVO на недособранном объекте. Везде ещё — свойство. Типичный промах: _delegate = d и удивление, почему weak-сеттер не отработал.



```objc
- (void)setTitle:(NSString *)title {
    _title = [title copy];
}
- (instancetype)init {
    if ((self = [super init])) { _title = @""; } // ivar in init
    return self;
}
```


**Потом обычно спрашивают**

- Почему в init / dealloc не писать self.foo = ?
- Как это ложится на Swift — self.title и «ничего»?
- Что свой сеттер меняет в self.?

</details>

<h2 id="ivar-in-category">ivar в категории</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Stored ivar в уже скомпилированный класс из категории добавить нельзя — раскладка экземпляра уже зафиксирована. Обход — associated objects через objc_setAssociatedObject со статическим ключом и политикой памяти вроде OBJC_ASSOCIATION_RETAIN. Так часть библиотек подделывает stored-свойства на UIView. Цена: лишний lookup в таблице, легко залить, если RETAIN вью, которая держит тебя. Лучше сабкласс или своя side table. Типичный промах: @property в категории и надежда, что синтезировалось хранилище.



```objc
static const void *Key = &Key;
objc_setAssociatedObject(self, Key, name, OBJC_ASSOCIATION_COPY_NONATOMIC);
NSString *name = objc_getAssociatedObject(self, Key);
```


**Потом обычно спрашивают**

- Почему раскладка фиксирована после objc_registerClassPair?
- Associated object и ivar сабкласса?
- Какую retain-политику берёшь для ассоциации «как weak»?

</details>

<h2 id="unrecognized-selector">unrecognized selector</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Рантайм кидает, когда IMP не нашёлся и message forwarding тоже не вывез: doesNotRecognizeSelector. До этого спрашивает resolveInstanceMethod, потом forwardingTargetForSelector, потом forwardInvocation. Этот конвейер — как живут часть прокси и моков. В Swift обычно видишь это как краш от @objc-селектора, который переименовали, или storyboard-экшена, которого больше нет. Типичный промах: винить ARC.



```objc
[self performSelector:@selector(nameThatDoesNotExist)];
// -[AppDelegate nameThatDoesNotExist]: unrecognized selector sent to instance
```


**Потом обычно спрашивают**

- Порядок resolveInstanceMethod и forwarding?
- Почему Swift-метод может пропасть в рантайме?
- Как это дебажить в lldb — po, bt?

</details>

<h2 id="category-vs-extension">Категория и class extension</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Категория @interface Foo (Bar) может жить в другом файле и целиться в классы, которые ты не компилируешь — NSString. Добавляет только методы, без ivar. Class extension — @interface Foo (), иногда «анонимная категория» — должен видеть @implementation класса на этапе компиляции. Может объявить лишние ivar, переобъявить readonly свойство как readwrite и спрятать приватные методы. Extension на NSString не напишешь. Типичный промах: назвать Swift extension на String class extension в смысле ObjC.



```objc
// Foo.m — class extension, private storage
@interface Foo ()
@property (nonatomic, copy) NSString *secret;
@end
```


**Потом обычно спрашивают**

- Почему extension может добавить ivar, а категория нет?
- Куда кладёшь приватный readwrite для публичного readonly?
- Как это ложится на Swift private в том же файле?

</details>

<h2 id="category-vs-inheritance">Категория и наследование</h2>

<code>Mid</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Категория — в Swift extension — добавляет методы существующему классу, которым можешь и не владеть. Наследование создаёт новый тип и может добавить ivar и переопределить поведение. Категория — маленький хелпер вроде UIColor.brand. Сабкласс — когда нужно состояние или другой drawRect. Категории ivar не добавляют: associated objects, осторожно. Две категории с одним методом — undefined. Типичный промах: сабклассить NSString или запихнуть логику приложения в категорию UIViewController.



```objc
@interface UIColor (Brand)
+ (UIColor *)brand;
@end
```


**Потом обычно спрашивают**

- Когда тип-обёртка лучше категории?
- Почему оверрайд через категорию опасен?
- Swift extension и категория ObjC — associated types?

</details>

<h2 id="synthesize">@synthesize</h2>

<code>Mid</code> · <code>Редко</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

@synthesize title = _title говорит компилятору выпустить геттер/сеттер и ivar. Современный ObjC так делает по умолчанию для @property. Пишешь сам, когда один аксессор свой, а второй хочешь синтезировать, или нужен нестандартный имя ivar. @dynamic — наоборот: синтеза нет, аксессоры придут в рантайме. Типичный промах: написать и свой сеттер, и @synthesize, а потом не понять, в какой ivar присвоил.



```objc
@implementation Person
@synthesize name = _name; // default today; needed if you write one accessor
@end
```


**Потом обычно спрашивают**

- Когда @synthesize ещё нужен в 2026?
- @synthesize, @dynamic и stored-свойства Swift?
- Какое имя ivar получишь, если не написать = _name?

</details>

### Senior

<h2 id="load-vs-initialize">+load и +initialize</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

+load бежит, когда образ замапили, до main, по разу на класс и на каждую категорию, которая его реализует — даже если сообщение так и не послал. Поэтому китайские лупы считают это налогом на запуск: каждый +load — работа pre-main, и у категорий свой. +initialize ленивый: в первый раз, когда этот класс — или сабкласс, который его не переопределил — получил сообщение. Лучше +initialize или Swift static, которым рулишь; +load оставь для swizzling, который надо поставить до любого клиентского кода, и сделай крошечным. Типичный промах: I/O или старт потока в +load, или решить, что +initialize категории бежит. Не бежит — для категорий особый только +load.



```objc
+ (void)load { /* once at image load — keep empty if you can */ }
+ (void)initialize {
    if (self == [MyClass class]) { /* first message, lazy */ }
}
```


**Потом обычно спрашивают**

- Почему +load категории бежит, а +initialize категории нет?
- Как увидеть время +load в DYLD_PRINT_STATISTICS?
- Куда в 2026 класть swizzling, если +load принципиально не хочешь?

</details>

<h2 id="mach-o">Mach-O и dyld</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Бинарник приложения — Mach-O: заголовок, load commands, потом сегменты __TEXT, __DATA и остальные, нарезанные на секции. На запуске dyld мапит эти образы, rebase внутренних указателей из-за ASLR, bind внешних символов, поднимает ObjC — селекторы, категории — потом гоняет инициализаторы: +load, C++ statics. Больше dylib и больше ObjC-метаданных — больше page-in до main. DYLD_PRINT_STATISTICS печатает разрез pre-main. Сливай свои динамические фреймворки, где можно бери static, +load держи пустым. Типичный промах: «запуск — это didFinishLaunching» и ни слова про rebase/bind.



```text
DYLD_PRINT_STATISTICS=1
# dylib loading / rebase+bind / ObjC setup / initializer
```


**Потом обычно спрашивают**

- Rebase и bind — что растёт с ASLR, что с импортированными символами?
- Почему куча динамических подов бьёт cold start сильнее того же кода, слинкованного статически?
- Что Link Map скажет такого, чего нет в статистике dyld?

</details>

<h2 id="isa">isa и раскладка объекта</h2>

<code>Senior</code> · <code>Часто</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Объект ObjC — блоб в куче: указатель isa, потом ivar класса и суперклассов. isa смотрит на объект класса, у которого список методов; isa класса смотрит на метакласс — методы класса. KVO и часть трюков с associated objects подменяют isa динамически созданным сабклассом. Ivar в уже скомпилированный класс в рантайме не добавить — раскладка фиксирована; добавить можно, когда создаёшь класс objc_allocateClassPair до objc_registerClassPair. Типичный промах: «isa смотрит на суперкласс».



```objc
NSLog(@"%@", NSStringFromClass(object_getClass(obj)));
```


**Потом обычно спрашивают**

- Объект класса и метакласс?
- Почему метод в рантайме добавить можно, а ivar нет?
- Как это включает KVO?

</details>

<h2 id="method-swizzling">Method swizzling</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Swizzling меняет местами два IMP у селектора через method_exchangeImplementations, чтобы существующие вызывающие попали в твой код. Аналитические SDK и часть тестовых даблов до сих пор так делают. Это глобально, зависит от порядка и ломается, когда две библиотеки свозлят один метод. Лучше обёртка, сабкласс или свой хук UIViewController. Если надо — свозлить в +load или одноразовом static и всегда звать оригинал. Типичный промах: свозлить в Swift без @objc dynamic или забыть исходный IMP и уйти в рекурсию.



```objc
static void swizzle(Class c, SEL a, SEL b) {
    method_exchangeImplementations(class_getInstanceMethod(c, a),
                                   class_getInstanceMethod(c, b));
}
```


**Потом обычно спрашивают**

- +load и +initialize для установки swizzle?
- Почему это крайняя мера рядом с делегатом?
- Чем isa-swizzle у KVO отличается?

</details>

<h2 id="resident-thread">Поток, который не умирает</h2>

<code>Senior</code> · <code>Средне</code>

<details>
<summary><strong>Показать ответ и Swift</strong></summary>

Фоновый NSThread выходит, когда стартовый блок вернулся. Чтобы держать его под таймеры, порты или серийный «сокетный поток», на нём надо крутить RunLoop и дать циклу source — обычно NSPort или Timer. run без source возвращается сразу. while плюс runMode:beforeDate: — управляемая форма, чтобы потом CFRunLoopStop. Очередям GCD это не нужно: DispatchSource живёт на workqueue. Типичный промах: alloc/init NSThread плюс scheduledTimer и удивление, почему таймер молчит.



```objc
[NSThread detachNewThreadWithBlock:^{
    [[NSRunLoop currentRunLoop] addPort:[NSPort port] forMode:NSDefaultRunLoopMode];
    [[NSRunLoop currentRunLoop] run];
}];
```


**Потом обычно спрашивают**

- Почему run возвращается, если забыл порт?
- GCD-таймер и RunLoop-таймер на этом потоке?
- Когда выделенный поток в 2026 — не тот инструмент?

</details>
