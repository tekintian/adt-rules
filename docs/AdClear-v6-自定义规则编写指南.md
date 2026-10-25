# AdClear v6 自定义规则编写指南

> **适用对象**：AdClear v6（Chrome MV3 扩展）用户，零基础可读
> **配套工具**：Chrome 开发者工具（F12）
> **规则反馈**：失效、误杀问题请通过应用内反馈渠道提交，帮助规则库持续改进

---

## 目录

- 0. 开始之前：两条拦截轨道
- 1. 五分钟上手：写出第一条规则
- 2. 规则类型速查
- 3. 网络拦截规则（轨道 A）
- 4. 元素隐藏规则：CSS 选择器实战（轨道 B）
- 5. CSS 注入规则：不只是隐藏
- 6. Scriptlet 规则：注入脚本逻辑
- 7. HLS 视频广告过滤
- 8. 调试与排错
- 9. 最佳实践清单
- 10. 即用模板库
- 附录 A：uBO 缩写对照 / 附录 B：RE2 与 V8 正则差异 / 附录 C：常见问题 FAQ / 附录 D：术语表

---

## 0. 开始之前：两条拦截轨道

AdClear v6 的规则引擎采用"双轨并行"设计，两套引擎各管一层。写规则之前先弄清你的规则走哪条轨道，这决定了语法写法、能力边界和排错思路——这是本指南最重要的一个心智模型。

**轨道 A：网络拦截（请求层）。** 请求还没发出去就直接掐断，广告脚本、广告图片、追踪器根本不会被下载。它有三个不可替代的优点：省流量、防追踪、效果彻底（源头消失，页面上连"残骸"都不会有）。代价是它只能按 URL 特征匹配——如果广告和正文使用同一个域名、URL 毫无规律，轨道 A 就无能为力。

**轨道 B：页面修饰（显示层）。** 内容已经到达浏览器，AdClear 通过内容脚本向页面注入 CSS 或 JavaScript，把广告"藏掉"或"改掉"。它能精确打击页面上的任何元素，是轨道 A 的完美补充；缺点是流量已经消耗，本质上是"眼不见心不烦"。另外，纯隐藏救不了被反广告脚本破坏的功能（这时要用 Scriptlet，见第 6 章）。

选型决策树：

```
广告有独立的域名 / URL 特征吗？
├─ 有 → 网络拦截规则（第 3 章）    例：||ads.example.com^
└─ 没有（与正文同域、内容内嵌在 DOM 里）
   └─ 页面修饰（第 4 ~ 6 章）
       ├─ 只要把元素藏掉 → 元素隐藏 ##（第 4 章）
       ├─ 要改样式而不是藏（修复布局 / 解锁滚动）→ CSS 注入 #$#（第 5 章）
       └─ 需要"逻辑"（拦截 API、篡改数据、反反广告）→ Scriptlet（第 6 章）
```

两类规则可以（而且经常应该）配合使用：先用网络规则掐掉能掐的，残留的占位元素再用隐藏规则补刀。

---

## 1. 五分钟上手：写出第一条规则

以"隐藏某资讯站信息流里的赞助内容卡片"为例，走完一个完整流程。

**第 1 步：找到广告元素的特征。** 在目标页面按 F12 打开开发者工具，点击检查器左上角的"选择元素"箭头（或直接右键广告 → 检查），DOM 会定位到类似这样的节点：

```html
<div class="feed-item sponsored-card">…</div>
```

**第 2 步：把特征翻译成规则。** 打开 AdClear 的自定义规则入口（设置 → 自定义规则），新增一行：

```
example.com##.feed-item[class*="sponsored"]
```

读法：在 `example.com`（含子域）上，隐藏 class 里同时含 `feed-item` 和 `sponsored` 字样的元素。`##` 是"元素隐藏"分隔符，后面跟的就是一个标准 CSS 选择器。

**第 3 步：保存并验证。** 保存规则，刷新页面。卡片消失即成功。如果页面结构复杂，建议先在控制台里验证选择器再保存（方法见 8.2 节），少走弯路。

三条使用须知：

- 自定义规则**每行一条**；以 `!` 开头的行是注释，会被忽略，建议用来记录规则用途和添加日期；
- 规则修改后需要**刷新页面**才能看到效果；
- 拿不准的规则先限定好域名再保存。不写域名的全局规则误杀力巨大（详见第 9 章）。

---

## 2. 规则类型速查

全部规则形态一表流。日常 90% 的需求只用到前三种。

| 规则形态 | 名称 | 轨道 | 一句话用途 |
|---|---|---|---|
| `domain##selector` | 元素隐藏 | B | 隐藏匹配元素（display:none） |
| `domain#@#selector` | 隐藏例外 | B | 在该域名取消某条隐藏规则 |
| `\|\|ads.example.com^` | 网络拦截 | A | 阻断匹配的请求 |
| `@@\|\|example.com^` | 网络例外 | A | 放行（白名单） |
| `domain#$#sel { … }` | CSS 注入 | B | 注入任意 CSS，不止隐藏 |
| `domain##+js(name, args)` | Scriptlet（uBO 写法） | B | 注入脚本逻辑 |
| `domain#%#//scriptlet(…)` | Scriptlet（AdGuard 写法） | B | 同上，另一种语法 |
| `dnr-redirect:…` | 重定向 | A | 自有源重定向规则 |
| `>>>` 前缀规则 | adbyby 重定向 | A | 兼容第三方 adbyby 语法 |

两个全局性认知：

- 轨道 B（元素隐藏、CSS 注入、Scriptlet）**不受 DNR 正则限制**，可以使用完整正则与扩展选择器；
- 轨道 A 的动态规则有总量上限（30,000 条），超限规则会被丢弃。订阅过多时请留意应用内的规则统计信息。

---

## 3. 网络拦截规则（轨道 A）

### 3.1 基础语法

| 符号 | 含义 | 示例 |
|---|---|---|
| `*` | 通配任意字符 | `example.com/ads/*.gif` |
| `\|\|` | 从域名开头匹配（含所有子域），拦广告域名的标准姿势 | `\|\|ads.example.com^` |
| `^` | 分隔符（`/` `?` `:` 等或地址末尾） | `example.com^` 能匹配 `example.com:8000/`，不匹配 `example.com.ar` |
| `\|` | 规则开头/结尾的精确锚点 | `swf\|` 只匹配以 swf 结尾的地址 |
| `@@` | 例外规则前缀，放行匹配的请求 | `@@\|\|example.com^` |
| `!` | 注释行 | `! 这是注释` |
| `/regex/` | 正则匹配 | `/banner\d+/` |

两个实用细节：`||example.com^` 一条规则同时覆盖 http、https 及全部子域；例外规则优先级高于拦截规则，`@@||example.com^$document` 可以在整站范围内停用拦截，是解救被误杀站点的常用手段。

### 3.2 常用选项

选项写在规则末尾，`$` 开头、逗号分隔：

```
||example.com^$third-party,script
||tracker.io^$domain=site-a.com|site-b.com
/ads/*$image,match-case
```

| 选项 | 作用 |
|---|---|
| `third-party` / `~third-party` | 只匹配跨站请求 / 只匹配同站请求 |
| `script`、`image`、`stylesheet`、`xmlhttprequest`、`subdocument`、`other` 等 | 限定资源类型 |
| `domain=a.com\|b.com` / `domain=~a.com` | 限定（或排除）生效页面 |
| `match-case` | 区分大小写 |

AdClear 的写法容忍度更高：支持 `3p`（= third-party）、`xhr`（= xmlhttprequest）等常用缩写，个别格式瑕疵也会在加载时自动归一化。但为了规则在多个拦截器之间可移植，建议按标准写法书写。

### 3.3 正则规则与 RE2 限制

轨道 A 走 Chrome DNR API，正则引擎是 **RE2**——为了保证线性耗时，它牺牲了一部分表达能力。以下写法会在加载时被识别为不兼容而**直接跳过**：

| 被拒绝的写法 | 原因 | 等效改写 |
|---|---|---|
| `/ads\?(?=.*campaign)/` | 前瞻断言 | `/ads\?.*campaign/` |
| `/(?<=cdn\.)ads\.com/` | 后瞻断言 | `/cdn\.ads\.com/`（把前缀吃进匹配） |
| `/(\d+)\/\1\//` | 反向引用 | 无法等效改写，拆成多条规则 |

另外，单条正则长度不能超过 1000 字符。改写之前先想一想：这条规则是不是非正则不可？多数场景 `||` + `^` + `*` 通配符就够用，而且性能更好。

### 3.4 重定向规则

- `dnr-redirect:` 前缀：AdClear 自有源的重定向规则，同样受 RE2 与动态规则上限约束；
- `>>>` 前缀：兼容 adbyby 生态的第三方重定向语法，需要在设置中显式开启后才会生效。

普通用户一般不需要手写重定向规则；从第三方订阅导入时，这两类规则会被自动识别和处理。

---

## 4. 元素隐藏规则：CSS 选择器实战（轨道 B）

### 4.1 语法骨架与域名限定

```
域名##选择器            ← 基本形态
a.com,b.com##选择器      ← 多域名（逗号分隔，## 前不能有空格）
~a.com##选择器           ← 排除域名：除 a.com 外都生效
a.com,~m.a.com##选择器   ← 组合：a.com 生效，但排除其 m 子域
##选择器                 ← 全局规则（强烈不建议，见第 9 章）
```

域名匹配的规则：写 `example.com` 时，`example.com` 自身**及其所有子域**都会生效；写子域 `m.example.com` 则只匹配该子域，**不会向上覆盖**到 `www.example.com`。另外，域名部分只能写完整域名，不能写路径（`example.com/page##x` 是无效写法）。

### 4.2 基础选择器

| 写法 | 匹配什么 | 广告场景示例 |
|---|---|---|
| `.className` | 类 | `##.ad-banner` |
| `#idName` | ID | `###pop_ad`（前两个 # 是分隔符，第三个才是 ID 选择器） |
| `div` / `iframe` | 标签 | `##iframe[src*="ad."]`（通常配合属性选择器用） |
| `.a.b` | 交集：同一元素同时拥有两个类 | `##.feed-item.sponsored` |

找特征时的优先级：**语义化类名/ID**（含 ad、sponsor、promo、banner、popup 等关键词）＞ **data-\* 自定义属性**（`data-ad-slot`、`data-ad-type`）＞ 布局类名（`col-md-6` 这类，随改版频繁变动，不要用）。

### 4.3 组合与分组：空格与逗号天差地别

新手最容易踩的坑，先背结论：

- **空格 = 嵌套（且）**：`A B` 选中"A 内部任意层级的 B"，最终被隐藏的是 **B**，A 只是范围限定；
- **逗号 = 分组（或）**：`A, B` 等价于两条独立规则，A 和 B **都会**被隐藏。

```html
<div class="feed">
  <div class="ad-card">信息流广告</div>   <!-- ##.feed .ad-card  命中 -->
  <div class="news">正常内容</div>        <!-- ##.feed .ad-card  不含 ad-card，不命中 -->
</div>
<div class="sidebar">
  <div class="ad-card">侧栏推广位</div>   <!-- ##.feed .ad-card  不在 .feed 里，不命中 -->
</div>
```

同一个选择器，把空格误写成逗号（`##.feed, .ad-card`）会变成"隐藏整个信息流 + 隐藏全页所有 ad-card"——典型的一字符惨案。反过来，该写逗号的地方漏写了，两条选择器粘连在一起，又是"规则静默失效"的常见原因。

完整组合符速查：

| 符号 | 名称 | 选中谁 | 示例 |
|---|---|---|---|
| （空格） | 后代 | 后者（任意嵌套深度） | `.feed .ad-card` |
| `>` | 子代 | 直接子元素 | `.feed > .ad-card` |
| `+` | 相邻兄弟 | 紧邻的下一个同级 | `.ad-box + .ad-label` |
| `~` | 通用兄弟 | 之后的全部同级 | `h2 ~ .promo` |
| `,` | 分组 | 逗号分隔的每一个 | `.a, .b` |
| （连写） | 交集 | 同一元素同时满足 | `.card.sponsor` |

**注意**：逗号在一条规则里可能出现在两个位置、含义完全不同。`a.com,b.com##.x, .y` 中，`##` **前**的逗号分隔**域名**（不能带空格），`##` **后**的逗号分隔**选择器**（空格随意）。

### 4.4 属性选择器：对抗随机类名

现代网站大量使用构建工具生成"带哈希后缀"的类名（如 `adSlot_container__x7f2b`），直接抄全名，网站一改版规则就失效。正确姿势是用子串匹配锁定稳定部分：

| 写法 | 匹配 | 示例效果 |
|---|---|---|
| `[class^="ad-"]` | 开头匹配 | 命中 `ad-slot__k3j` |
| `[class$="-ad"]` | 结尾匹配 | 命中 `home-banner-ad` |
| `[class*="ad-slot"]` | 包含匹配 | 命中 `xxx__ad-slot__yyy` |
| `[class*="AD-" i]` | 包含 + 忽略大小写 | 命中 `Ad-Slot` |
| `[data-ad-slot]` | 只要属性存在 | 不看属性值的场景 |
| `[href*="doubleclick"]` | 其他属性同样适用 | 按跳转目标识别广告 |

**宽度警告**：`[class*="ad"]` 是高危写法——`read`、`header`、`badge`、`shadow` 全都包含 "ad" 子串，一条规则能误杀半张页面。子串至少带上分隔符或更长上下文（`"ad-"`、`"-ad"`、`"ads_"`）。

### 4.5 结构伪类

适合"位置有规律、自身无特征"的广告位：

```
example.com##.feed-item:nth-child(5n)     ← 信息流每第 5 条是广告
example.com##li:first-child > .promo
example.com##.card:not(.notice)           ← 隐藏所有 card，但排除公告
```

### 4.6 扩展选择器（ExtCss）：标准 CSS 的三大补刀

有一类需求标准 CSS 做不到：选"**包含某种子元素的父容器**"、"**文本内容含某关键词的元素**"、"**计算样式符合某特征的元素**"。AdClear 内置扩展 CSS 引擎支持：

| 扩展伪类 | 解决什么问题 | 示例 |
|---|---|---|
| `:has()` | 反向选父：按"孩子"锁定容器 | `div:has(> iframe[src*="googlesyndication"])` |
| `:contains()` | 按文本内容匹配 | `.feed-item:contains("赞助")` |
| `:matches-css()` | 按计算样式匹配（值可为正则） | `[class*="layer"]:matches-css(position: fixed)` |

`example.com##div:has(> iframe[src*="doubleclick.net"])` 读作：隐藏那些**直接子节点里挂着 doubleclick iframe** 的 div。广告容器自己没有特征、广告 iframe 特征鲜明时，这招几乎是唯一解。

其他扩展伪类（`:upward()`、`:remove()`、`:style()`、`:matches-path()` 等）与 AdGuard 生态用法一致，具体支持清单以当前版本应用内文档为准。

### 4.7 例外规则 #@#

`example.com#@#.sponsor` 表示：在 example.com 上，**取消**所有命中 `.sponsor` 的隐藏规则——无论是订阅里来的还是自己写的。两个典型用途：

- 订阅列表把某站的正常模块误杀了，写一条 `#@#` 救回来，不用改订阅源；
- 自己某个选择器写宽了，想临时豁免某个站点，`#@#` 可以精确豁免。

优先级关系：`#@#` ＞ `##`；网络层同理，`@@` ＞ 拦截规则。

### 4.8 成本阶梯：选择器也有性能档位

同样是"把元素藏掉"，不同写法的运行成本差别很大。按成本从低到高分三档，**永远从低档开始选**：

1. **标准 CSS**（基础、组合、属性、结构伪类）：一次性注入 `<style>` 标签，交给浏览器原生渲染管线，近零持续开销；
2. **ExtCss**（`:has()` 等扩展伪类）：由扩展引擎动态求值并监听 DOM 变化，每次页面变动都要重新匹配，按需使用、控制数量；
3. **Scriptlet**：注入 JS 逻辑，成本最高，只在需要"逻辑"（拦截、篡改）时使用。

一个订阅里如果塞了成百上千条 ExtCss 规则，在 DOM 操作频繁的 SPA 页面上会明显拖慢速度。自用规则一般无所谓，但不要无脑全上 `:has()`。

---

## 5. CSS 注入规则：不只是隐藏

元素隐藏只能"藏"，`#$#` 可以注入**任意** CSS，是修复型规则的主力：

```
example.com#$#.article-body { min-height: auto !important; }
example.com#$#body { overflow: auto !important; }
example.com#$#.ad-slot:empty { display: none !important; }
```

三个高频场景：

- **修复布局塌陷**：广告被隐藏后外层容器还占着高度，或站点脚本检测到广告消失后把正文挤变形，对相关容器注入样式修正；
- **解除功能锁定**：某些站点检测到广告拦截后锁定滚动（`overflow: hidden`）或给正文加模糊，用 `#$#` 强制还原；
- **精细隐藏**：`:empty`、`:first-of-type` 等配合自定义样式，实现"隐藏但保留布局"之类的高级效果。

对应的例外写法 `#@$#` 可取消某条 CSS 注入规则，逻辑与 `#@#` 相同。

---

## 6. Scriptlet 规则：注入脚本逻辑（轨道 B）

当问题超出"选择 + 隐藏"的范畴——需要**拦截某个 API、篡改某份数据、骗过反广告检测**——就要请出 Scriptlet。AdClear 内置 36 个，全部在页面主世界（MAIN world）执行，能与页面脚本平等对话。

### 6.1 三种等价写法

```
example.com##+js(set-constant, adblockDetected, false)                  ← uBO 风格（最短，推荐）
example.com#%#//scriptlet("set-constant", "adblockDetected", "false")   ← AdGuard 风格
example.com##+js(acis, JSON.parse, "adList")                            ← uBO 缩写风格
```

三种写法完全等价，混用也没问题。缩写对照见附录 A。

### 6.2 内置 Scriptlet 分类速查（36 项）

| 类别 | 名称 | 作用 |
|---|---|---|
| 属性拦截 | `set-constant` | 把对象属性焊死为常量 |
| | `set-property` | 修改对象属性值 |
| | `remove-attr` | 移除 DOM 属性 |
| | `remove-class` | 移除 CSS 类名 |
| API Hook | `json-prune` | 从 JSON 响应中剪掉指定字段 |
| | `xml-prune` | 过滤 XML 响应内容 |
| | `replace-fetch-response` | 替换 fetch 响应 |
| | `replace-xhr-response` | 替换 XHR 响应 |
| | `prevent-fetch` | 阻止 fetch 请求 |
| | `prevent-xhr` | 阻止 XHR 请求 |
| | `prevent-setTimeout` | 拦截 setTimeout |
| | `prevent-setInterval` | 拦截 setInterval |
| | `prevent-addEventListener` | 拦截事件监听 |
| | `prevent-window-open` | 阻止 window.open（弹窗克星） |
| DOM 操作 | `hide` / `hide-if-contains` | 隐藏匹配元素 / 含指定文本则隐藏 |
| | `hide-if-has-and-matches-path` | 组合路径条件的隐藏 |
| | `remove` / `remove-if-contains` | 物理移除匹配元素 |
| | `remove-shadow-dom-elements` | 移除 Shadow DOM 内的元素 |
| SDK Mock | `googletag-manager-gtm` | 模拟 Google Tag Manager |
| | `google-analytics-ga` | 模拟 Google Analytics |
| | `facebook-sdk` | 模拟 Facebook SDK |
| | `amazon-apstag` | 模拟 Amazon APS |
| | `prebid` | 模拟 Prebid.js |
| 反检测 | `abort-current-inline-script` | 中止当前内联脚本 |
| | `abort-on-property-read` | 读取某属性即中止 |
| | `abort-on-property-write` | 写入某属性即中止 |
| | `abort-on-stack-trace` | 按调用栈匹配中止 |
| | `debug-current-inline-script` | 调试内联脚本 |
| | `log` / `log-on-stack-trace` | 打日志辅助排查 |
| 播放器 Hook | `m3u8-prune` | 过滤 m3u8 播放列表 |
| | `vast-prune` | 过滤 VAST 视频广告 |
| | `ima-prune` | 过滤 IMA SDK 广告 |
| | `player-prune` | 通用播放器过滤 |

### 6.3 六个典型用例

```
! 1. 反反广告：把检测标记焊死为"未检测到"
example.com##+js(set-constant, adblockDetected, false)

! 2. 站点一读某属性就弹广告窗 → 读取即中止
example.com##+js(abort-on-property-read, showAdModal)

! 3. 接口返回的数据里混着广告列表 → 从 JSON 里剪掉
example.com##+js(json-prune, data.adItems)

! 4. 无限弹窗治理
example.com##+js(prevent-window-open)

! 5. 正文被加了模糊类名锁付费 → 移除类名解锁
example.com##+js(remove-class, vip-blur, .article-content)

! 6. 视频播放列表里混着广告分片（与第 7 章 HLS 模块配合）
example.com##+js(m3u8-prune)
```

参数格式与可用清单详见应用内《Scriptlet 语法规则技术参考》。安全方面你需要知道两件事：Scriptlet 禁止 `eval` 与网络请求、必须可序列化——所以它们只能"改"，不能"夹带私货"。

---

## 7. HLS 视频广告过滤

HLS 视频广告过滤是独立模块，**默认自动运行，无需写规则**。它解析 m3u8 播放列表，用多路信号（SCTE-35 广播标记、广告区间标记、序列号跳跃、异常短分片、URL 特征、来源域名变化等）加权打分，总分达到阈值即判定为广告分片并跳过；拦截成功的分片会计算内容指纹进入自学习库，越用越准。

用户能做的三件事：

1. **反馈误杀/漏杀**：视频片段被误跳过或广告漏网时，通过应用内反馈提交，帮助校正指纹库；
2. **申请强制保留**：特定内容被反复误杀时，可在反馈中申请加入豁免名单（forceKeep）；
3. **叠加 Scriptlet**：顽固的 VAST/IMA 类视频广告可配合 `vast-prune`、`ima-prune`（见 6.2）使用。

---

## 8. 调试与排错

### 8.1 标准检查流程

1. F12 → 检查元素，确认你选中的是**广告本体**还是它的子节点/父容器（优先隐藏最外层容器，避免留白）；
2. 在 Elements 面板读特征：类名、ID、data-\* 属性、iframe 的 src；
3. 判断特征稳定性：带随机哈希的部分（`__x7f2b`）会变，用 `^=` `*=` 截取稳定段；
4. 写成规则 → 保存 → 刷新验证。

### 8.2 控制台验证选择器（强烈推荐：写规则前先测）

在目标页面按 F12 → Console，粘贴：

```js
// 标准 CSS 选择器：返回匹配到的元素列表
document.querySelectorAll('.feed-item[class*="sponsored"]')

// 想确认某元素当前是否可见（$0 是 Elements 面板里选中的元素）
getComputedStyle($0).display
```

- 返回空列表 `NodeList []` → 选择器没匹配上，规则必然无效，先改选择器再保存；
- 返回了元素但混进了正常内容 → 选择器太宽，加限定条件收窄。

`:has()` 在新版 Chrome 控制台可直接测试；`:contains()`、`:matches-css()` 是扩展伪类，控制台测不了，以应用内实际生效结果为准。

### 8.3 规则不生效排查清单

按命中率从高到低过一遍：

| # | 检查项 | 说明 |
|---|---|---|
| 1 | 选择器本身错了？ | 用 8.2 先测，空列表 = 白搭 |
| 2 | 空格/逗号用错？ | 见 4.3，最高频事故点 |
| 3 | 混入了全角符号？ | 中文输入法打出的 `“”` `＃` `｜` 都会**静默失效** |
| 4 | 域名不匹配？ | 规则写 `m.example.com`、页面在 `www.example.com` → 不生效（子域不向上兼容） |
| 5 | 类名大小写？ | class 区分大小写；必要时加 `i` 忽略大小写标志 |
| 6 | 用了不支持的伪类？ | 以 4.6 支持清单为准 |
| 7 | 订阅里已有 `#@#` 豁免？ | 例外规则优先级更高，检查是否冲突 |
| 8 | 网络正则被 RE2 丢弃？ | 前瞻/后瞻/反向引用/超长，见 3.3 |
| 9 | 元素是 JS 后建的且特征变化？ | 换更稳定的属性，或改用 `:has()` / Scriptlet |
| 10 | 动态 DNR 规则超限？ | 30,000 条上限，检查应用内规则统计 |
| 11 | 缓存/时机问题？ | Ctrl+Shift+R 强制刷新再试；广告"闪一下才消失"属于注入时机的正常现象 |

### 8.4 误杀排查

页面某功能消失或排版崩坏时：先停用全部自定义规则，确认问题出在自己的规则还是订阅；再二分定位到具体规则；最后决定**收窄选择器**还是**写 `#@#`/`@@` 豁免**。别急着删规则——行首加 `!` 注释掉、保留现场，更利于复盘。

---

## 9. 最佳实践清单

1. **域名限定是底线**。不写域名的全局规则是误杀之王；
2. **稳定特征优先**：语义类名、data-\* 属性 ＞ 哈希类名；哈希类名用 `[class^=]` / `[class*=]` 截取稳定段；
3. **宁窄勿宽**：`[class*="ad"]` 会命中 `read`、`header`、`badge`，子串要带分隔符或更长上下文；
4. **隐藏最外层容器**，不给页面留占位空白；
5. **网络规则优先，隐藏规则补刀**：能从源头掐断的，就不浪费页面修饰；
6. **成本阶梯**：标准 CSS ＞ ExtCss ＞ Scriptlet，够用就好；
7. **正则避开 RE2 禁区**（前瞻/后瞻/反向引用），仅轨道 A 受此限制；
8. **例外优于删除**：`#@#` / `@@` 豁免可逆、可追溯，改坏了随时恢复；
9. **每条规则配注释**：`! 2026-10 某站信息流广告`，规则失效时好定位；
10. **定期清理失效规则**，关注应用内规则统计；
11. **先测后存**：控制台跑一遍选择器（8.2 节），比刷新页面试错快十倍。

---

## 10. 即用模板库

把 `example.com` 替换成目标站点即可直接使用。

```
! ========== 元素隐藏（第 4 章） ==========

! 信息流广告：外层限定 + 子串匹配，逗号分组覆盖多种命名
example.com##.feed [class*="ad-"], .feed [class*="sponsored"]

! 弹窗 / 浮层：按 fixed 定位特征锁定
example.com##div[class]:matches-css(position: fixed)
example.com##div[class*="mask"]:matches-css(z-index: /^9{4,}$/)

! 广告容器无特征、子 iframe 特征鲜明 → :has() 反锁容器
example.com##div:has(> iframe[src*="googlesyndication"])
example.com##div:has(> a[href*="ad.doubleclick.net"])

! 完全无特征 → 文本兜底
example.com##.feed-item:contains("赞助")

! ========== CSS 注入（第 5 章） ==========

! 修复隐藏广告后的布局塌陷
example.com#$#.article-body { min-height: auto !important; }

! 解除滚动锁定
example.com#$#body { overflow: auto !important; }

! ========== Scriptlet（第 6 章） ==========

! 反反广告检测
example.com##+js(set-constant, adblockDetected, false)
example.com##+js(abort-on-property-read, showAdModal)

! 接口数据去广告
example.com##+js(json-prune, data.adItems)

! 弹窗治理
example.com##+js(prevent-window-open)

! ========== 网络 + 隐藏组合拳 ==========

! 先掐独立广告域，再清残留占位
||ads.example.com^
example.com##.ad-slot

! ========== 例外豁免 ==========

! 救回被误杀的正常模块
example.com#@#.sponsor

! 放行被误杀的接口
@@||api.example.com^
```

---

## 附录 A：uBO 缩写对照

AdClear 支持 9 项 uBO scriptlet 缩写，常用如下（完整映射以应用内《Scriptlet 语法规则技术参考》为准）：

| 缩写 | 完整名称 |
|---|---|
| `acis` | `abort-current-inline-script` |
| `aopr` | `abort-on-property-read` |
| `aopw` | `abort-on-property-write` |
| `aost` | `abort-on-stack-trace` |
| `ra` | `remove-attr` |
| `rc` | `remove-class` |

## 附录 B：RE2 与 V8 正则差异

轨道 A（DNR 网络规则）使用 RE2，轨道 B（元素隐藏 / CSS 注入 / Scriptlet）使用 V8 完整正则：

| 特性 | RE2（仅轨道 A） | V8（轨道 B） |
|---|---|---|
| 前瞻 `(?=…)` / 负前瞻 `(?!…)` | 不支持 | 支持 |
| 后瞻 `(?<=…)` | 不支持 | 支持 |
| 反向引用 `\1` | 不支持 | 支持 |
| 命名捕获 `(?<name>…)` | 不支持 | 支持 |
| 单条长度上限 | 1000 字符 | 无限制 |
| 时间复杂度 | 线性保证 | 极端情况可能回溯爆炸 |

## 附录 C：常见问题 FAQ

**Q1：为什么我的正则网络规则没生效？**
大概率被 RE2 兼容性校验拦截（前瞻/后瞻/反向引用/超过 1000 字符），见 3.3 的等效改写表；也可能是动态规则总量超过 30,000 条被丢弃，检查应用内统计。

**Q2：广告藏掉了但留了一块空白？**
你隐藏的是广告的内层元素，外层容器还在。用 F12 往上找最外层容器（或用 `:has()` 反锁），把规则目标换成它。

**Q3：规则保存后要刷新吗？**
要。元素隐藏和 CSS 注入在页面加载时注入；网络规则即时生效，但已建立的连接不受影响。排查时建议 Ctrl+Shift+R 强制刷新。

**Q4：多条规则会冲突吗？**
隐藏规则相互叠加，都命中就都应用；例外（`#@#` / `@@`）永远优先。CSS 层面的最终效果由选择器命中与 `!important` 决定，与规则书写顺序无关。

**Q5：为什么同一条规则在别的拦截器有效，在 AdClear 无效？**
各家支持的扩展伪类、scriptlet 名称与参数格式并不通用。核对 4.6 的支持清单与 6.2 的内置清单，换成 AdClear 支持的等价写法。

**Q6：class 名区分大小写吗？**
区分。`##.Ad-Banner` 命中不了 `ad-banner`；属性选择器可用 `[class*="ad-" i]` 忽略大小写。

**Q7：能拦截视频广告吗？**
HLS 流内广告由第 7 章的独立模块自动处理；网页播放器里的 VAST/IMA 广告可叠加 `vast-prune` / `ima-prune` scriptlet。

**Q8：全局规则到底多危险？**
`##.ad` 会在**所有网站**隐藏一切命中元素，包括把某站一个恰好叫 `.ad` 的正常按钮藏掉，而且极难排查。永远写域名限定。

## 附录 D：术语表

| 术语 | 含义 |
|---|---|
| 轨道 A / DNR | 网络拦截引擎，走 Chrome declarativeNetRequest API，RE2 正则，3 万条动态规则上限 |
| 轨道 B / tsurlfilter | 页面修饰引擎（元素隐藏、CSS 注入、Scriptlet），V8 完整正则 |
| EH（Element Hiding） | 元素隐藏，`##` 规则 |
| ExtCss | 扩展 CSS（`:has()` 等），由扩展引擎而非浏览器原生支持 |
| Scriptlet | 预置的注入脚本片段，AdClear 内置 36 个 |
| RE2 | Google 的线性时间正则引擎，DNR 专用，不支持前瞻/后瞻/反向引用 |
| MAIN world | 与页面脚本相同的执行环境（区别于扩展的隔离环境） |
| SPA | 单页应用，页面内容由 JS 动态渲染 |
| forceKeep | HLS 模块的强制保留豁免名单，防止特定内容被误判为广告 |




---

