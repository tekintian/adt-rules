# AdClear v6 过滤规则指引

> 本文档列出 AdClear v6 **已实际实现并生效**的所有过滤规则类型、语法、示例及注意事项。
> 用户编写自定义规则或维护订阅文件时，请严格遵循本文档中的支持范围。

## 目录

- [1. 订阅文件格式](#1-订阅文件格式)
- [2. 网络拦截规则（Network Rules）](#2-网络拦截规则network-rules)
- [3. 白名单规则（Allowlist Rules）](#3-白名单规则allowlist-rules)
- [4. 元素隐藏规则（Element Hiding）](#4-元素隐藏规则element-hiding)
- [5. 元素隐藏例外规则](#5-元素隐藏例外规则)
- [6. 扩展 CSS 选择器](#6-扩展-css-选择器)
- [7. CSS 注入规则](#7-css-注入规则)
- [8. Scriptlet 规则](#8-scriptlet-规则)
- [9. DNR 重定向规则（dnr-redirect:）](#9-dnr-重定向规则dnr-redirect)
- [10. Adbyby 重定向规则（>>>）](#10-adbyby-重定向规则)
- [11. HLS 广告分片过滤](#11-hls-广告分片过滤)
- [12. 不支持的规则语法](#12-不支持的规则语法)
- [附录：资源类型速查](#附录资源类型速查)

---

## 1. 订阅文件格式

订阅文件必须以 ABP header 开头：

```
[Adblock Plus 2.0]
```

支持的可选 metadata header：

```
! Title: 我的自定义规则
! Description: 描述信息
! Homepage: https://example.com
! Version: 2025010101
! Expires: 2 days
! Last modified: 01 Jan 2025 00:00 UTC
! Checksum: xxxx
```

- `Expires` 支持 `N hours` 或 `N days` 格式
- `Checksum` 使用 ABP 标准 MD5 Base64 算法校验

---

## 2. 网络拦截规则（Network Rules）

网络规则通过 Chrome Declarative Net Request (DNR) API 在网络层拦截请求，是最高效的拦截方式。

### 2.1 域名锚定拦截

用 `||` 锚定域名开头，用 `^` 标记域名/路径分隔符：

```
||clarity.ms^
||ads.example.com^
||doubleclick.net^
```

- 拦截所有指向该域名**及其所有子域名**的请求
- `||clarity.ms^` **已经覆盖** `www.clarity.ms`、`api.clarity.ms`、`deep.sub.clarity.ms` 等所有子域名
- `^` 等效于域名边界或路径分隔符（`/`、`:`、`?`、`#`）
- 不会误匹配域名后缀：`||clarity.ms^` **不会**匹配 `clarity.ms.evil.com`

> **关键**：`||` 的语义是"域名锚定"——匹配该域名本身 + 所有子域名，无需额外通配符。

### 2.2 域名通配符拦截

`||` 后的 `*` 通配符用于匹配**子域名部分**，但**不匹配域名本身**：

```
||*.aliyuncs.com^
||ads*.example.com^
```

- `||*.aliyuncs.com^`：匹配 `xxx.aliyuncs.com`，**不匹配** `aliyuncs.com` 本身
- `||ads*.example.com^`：匹配 `ads1.example.com`、`ads2.example.com` 等
- `*` 匹配任意字符序列

> **注意**：`||*.domain^` 与 `||domain^` 的区别——前者**仅匹配子域名**，后者**匹配域名 + 所有子域名**。大多数场景下直接用 `||domain^` 即可。

### 2.3 URL 路径匹配拦截

```
/ads/banner.js$script
/banners/*.gif$image
```

- 匹配 URL 中包含指定路径片段的请求

### 2.4 协议锚定拦截

```
|http://ads.example.com/
|https://tracker.example.com^
```

- `|` 在最左侧锚定协议开头

### 2.5 完整 URL 拦截

```
||example.com/ads/banner.js$script
||ad.server.com/path/to/ad$xmlhttprequest
```

### 2.6 带资源类型修饰符

```
||ads.example.com^$script
||tracker.example.com^$image
||analytics.example.com^$xmlhttprequest
||ads.example.com^$script,xmlhttprequest
||adframe.example.com^$subdocument
||fontad.example.com^$font
||mediaad.example.com^$media
||stylead.example.com^$stylesheet
||objad.example.com^$object
```

### 2.7 第三方请求拦截

```
||ads.example.com^$third-party
||tracker.net^$script,third-party
```

- `$third-party`：仅拦截跨域请求（请求域名 ≠ 页面域名）

### 2.8 非第三方限定

```
||cdn.example.com^$~third-party
```

- `$~third-party`：仅拦截同域请求

### 2.9 域名限定

```
||ads.example.com^$domain=example.com
||ads.example.com^$domain=example.com|another.com
||ads.example.com^$domain=~excluded.com
||ads.example.com^$domain=example.com,~sub.example.com
```

- `$domain=`：仅在指定域名页面上生效
- `~` 前缀排除指定域名
- 多域名用 `|` 分隔

### 2.10 排除资源类型

```
||example.com^$~script
||example.com^$~image,~script
```

- `$~script`：拦截除 script 外的所有资源类型请求

---

## 3. 白名单规则（Allowlist Rules）

用 `@@` 前缀将匹配的请求排除在拦截之外。

### 3.1 域名白名单

```
@@||example.com^
@@||ads.example.com^$domain=partner.example.com
```

- 放行所有指向 `example.com` 的请求

### 3.2 带域名限定的白名单

```
@@||ad.vivo.com.cn^$~third-party
@@||ads.alafish.cn^$~third-party
```

- 仅在非第三方场景放行

### 3.3 Generic 元素隐藏白名单

```
@@||example.com^$generichide
```

- `$generichide`：在该域名上禁用所有通用元素隐藏规则（不限定域名的 `##` 规则）

### 3.4 元素隐藏白名单

```
@@||example.com^$elemhide
```

- `$elemhide`：在该域名上禁用所有元素隐藏规则

### 3.5 路径白名单

```
@@||example.com/api/track$xmlhttprequest
```

- 仅放行指定路径的 xmlhttprequest 请求

---

## 4. 元素隐藏规则（Element Hiding）

用 `##` 分隔域名限定和 CSS 选择器，在页面上隐藏匹配的 DOM 元素。

### 4.1 通用元素隐藏

不限定域名，对所有页面生效：

```
##.ad-banner
##.sponsor-links
###ad-container
```

### 4.2 域名限定元素隐藏

仅在指定域名上生效：

```
example.com##.ad-wrapper
example.com,another.com##.sponsor
baidu.com##.container:has(> .bottom-section > .item_voice_room)
```

### 4.3 域名排除元素隐藏

用 `~` 排除特定域名：

```
~excluded.com##.ad-banner
~weibo.com##.con_ad
~a.com,~b.com##.ad_box
```

### 4.4 class / id 通配符匹配

> **核心结论**：CSS 选择器中 **不支持** `*` 通配符写在 class/id 名内（如 `.ad-*`），但**完全支持**属性选择器实现等效通配。

#### ❌ 不合法的写法

```
##.ad-*
##div.ad-*
##[class="ad-*"]
```

- `.ad-*` 不是合法 CSS 选择器，浏览器 `querySelectorAll('.ad-*')` 会抛异常
- tsurlfilter 引擎可能接受解析，但注入到页面后**无法生效**

#### ✅ 正确写法：属性选择器

| 属性选择器 | 含义 | 等效通配语义 | 示例 |
|-----------|------|-------------|------|
| `[attr^="val"]` | 属性值以 val **开头** | 前缀通配 `val*` | `##[class^="ad-"]` |
| `[attr*="val"]` | 属性值**包含** val | 包含通配 `*val*` | `##[class*="-ad"]` |
| `[attr$="val"]` | 属性值以 val **结尾** | 后缀通配 `*val` | `##[class$="-ad"]` |

#### class 通配符示例

```
##[class^="ad-"]
##[class*="-ad"]
##[class$="_ad"]
##div[class^="ad-"]
##div[class*="ad-banner"]
```

- `[class^="ad-"]`：匹配 class 以 `ad-` 开头的元素，如 `ad-banner`、`ad-footer`、`ad-popup`
- `[class*="-ad"]`：匹配 class 中含 `-ad` 的元素，如 `top-ad`、`sidebar-ad`、`inline-ad-box`
- `[class$="_ad"]`：匹配 class 以 `_ad` 结尾的元素，如 `float_ad`、`popup_ad`

#### id 通配符示例

```
##[id^="ad-"]
##[id*="ad"]
##[id$="-ad"]
##div[id^="ad-"]
```

- `[id^="ad-"]`：匹配 id 以 `ad-` 开头的元素
- `[id*="ad"]`：匹配 id 中含 `ad` 的元素
- `[id$="-ad"]`：匹配 id 以 `-ad` 结尾的元素

#### 其他属性通配符示例

```
##[onclick^="window.location"]
##[onclick*=".apk"]
##a[href^="http"][href$=".exe"]
##[style^="width:960"]
##[style*="display:none"]
##img[src*=".sinaimg."]
##a[href*=".taobao.com"]
```

#### 组合选择器示例

```
##.ads > a > img[src*=".alicdn.com"]
##div[class^="ad"] > span
###aatop[class^="top_box"]
##img[src$=".gif"][style*="width:960"]
```

#### style 多属性组合匹配（无 class/id 的广告浮层）

很多广告元素**没有 class 和 id**，所有特征都写在 inline `style` 里。此时需要用**多个独立的 `[style*="..."]` 属性选择器叠加匹配**。

**核心要点**：
- 每个 `[style*="..."]` 独立在整个 style 字符串中找子串，**与属性声明顺序无关**
- 选择器中的空格/标点必须与原始 style **精确对齐**（`position: fixed` 不能写成 `position:fixed`）
- `!important` 不影响匹配（`height: 130px !important` 仍可被 `[style*="height: 130px"]` 命中，因为 `*=` 是子串包含）

**反例（联合匹配，顺序敏感，容易失效）**：
```
❌ ##div[style*="position: fixed; bottom: 0px"]
   如果原始 style 中 bottom 出现在 position 之前，就匹配不上
```

**正例（独立选择器，顺序无关，推荐）**：
```
✅ ##div[style*="position: fixed"][style*="bottom: 0px"]
   两个选择器各自独立匹配，无论 style 属性顺序如何都能命中
```

**实战场景**：匹配一个无 class/id 的底部悬浮广告 div

```html
<div style="width: 1230px; margin: 0px auto; bottom: 0px; left: 50%;
            position: fixed; z-index: 999999; height: 130px !important; ...">
```

规则（4 特征组合，零误杀）：
```
##div[style*="position: fixed"][style*="bottom: 0px"][style*="z-index: 999999"][style*="height: 130px"]
```

特征逐层降级（按需取舍）：

| 降级层级 | 规则 | 适用场景 |
|---------|------|---------|
| 4 特征（推荐） | `##div[style*="position: fixed"][style*="bottom: 0px"][style*="z-index: 999999"][style*="height: 130px"]` | 精准匹配，几乎零误杀 |
| 3 特征 | `##div[style*="position: fixed"][style*="bottom: 0px"][style*="z-index: 999999"]` | 广告高度可能变化时 |
| 2 特征 | `##div[style*="position: fixed"][style*="bottom: 0px"]` | 页面没有其他底部固定元素时 |

**性能说明**：纯 CSS 属性选择器，不触发 ExtCss 流程，直接注入 `<style>` 标签，浏览器原生引擎匹配，性能最优。

#### 自定义属性匹配

广告元素经常带有自定义属性（非标准 HTML 属性），属性名固定但值随机（如 `c="20351"`、`data-ad-id="abc123"`）。

**匹配有某属性的元素（不关心值）**：

```
##div[c]
##div[data-ad]
##div[adid]
```

项目已有同类规则：
```
adt-base.txt:  ##div[data-ggsrc]
adt-base.txt:  ##article[data-ggclick]
adt-video.txt: iqiyi.com##div[adid]
```

**属性值有规律时**（如全部以某前缀开头、包含某子串）：

```
##div[c^="ad_"]            ← c 值以 "ad_" 开头
##div[c*="ad"]             ← c 值包含 "ad"
##div[c$="_ad"]            ← c 值以 "_ad" 结尾
##div[c="20351"]           ← c 值精确等于（仅当值固定时）
```

**值是随机数字但属性名固定**的场景（如 `<div c="20351">`、`<div c="45298">`）：
- CSS 属性选择器**不支持正则**（无法写 `[c="\d+"]`）
- 直接用 `##div[c]` 即可 — 因为自定义属性名 `c` 本身很罕见，正常页面几乎不会使用
- 如果混入了正常元素，加 style 或父元素特征缩小范围：`##div[c][style*="position: relative"]`

**完整对照**：

| 需求 | 规则 | 性能 |
|------|------|------|
| 只要有某属性就匹配 | `##div[c]` | ⭐⭐⭐⭐⭐ 最优 |
| 属性值以某字符串开头 | `##div[c^="ad_"]` | ⭐⭐⭐⭐⭐ |
| 属性值包含某字符串 | `##div[c*="ad"]` | ⭐⭐⭐⭐⭐ |
| 属性值以某字符串结尾 | `##div[c$="_ad"]` | ⭐⭐⭐⭐⭐ |
| 属性值精确匹配 | `##div[c="20351"]` | ⭐⭐⭐⭐⭐ |
| 属性值需正则匹配 | `##:xpath(//div[@c[matches(.,'^\d+$')]])` | ⭐⭐ ExtCss，尽量避免 |

---

## 5. 元素隐藏例外规则

用 `#@#` 在指定域名上取消元素隐藏规则：

```
example.com#@#.ad-banner
hubei.gov.cn#@##ad-side
abbao.cn#@##adContent
```

- 当通用规则 `##.ad-banner` 在 `example.com` 上误杀时，用 `example.com#@#.ad-banner` 恢复

---

## 6. 扩展 CSS 选择器

支持 `:has()`、`:xpath()` 等 Procedural Selector（由 tsurlfilter CosmeticEngine 处理）：

```
bing.com##.b_algo:has(.ad_esltitle)
bing.com##li[class="b_algo"]:has(.b_attribution[data-partnertag]+p[class])
baidu.com##.container:has(> .bottom-section > .item_voice_room[data-yysid])
```

支持的完整 ExtCss 列表：

| 选择器 | 功能 | 示例 |
|--------|------|------|
| `:has(selector)` | 匹配包含指定子元素的父元素 | `##div:has(> .ad)` |
| `:xpath(expr)` | XPath 表达式选择 | `##:xpath(//div[@class="ad"])` |
| `:-abp-has(sel)` | AdGuard 兼容 :has() | `##div:-abp-has(.ad)` |
| `:contains(text)` | 匹配包含指定文本的元素 | `##div:contains(广告)` |
| `:matches-css(...)` | 匹配指定 CSS 样式的元素 | `##div:matches-css(width: 300px)` |
| `:remove()` | 移除元素（而非隐藏） | `##.ad-banner:remove()` |
| `:upward(n)` | 向上选择第 n 级祖先 | `##.ad:upward(2)` |

- `:has()` 选择器匹配包含指定子元素的父元素
- 这些选择器由 content script 在 DOM 层面执行，性能开销高于普通 CSS 选择器

---

## 7. CSS 注入规则

用 `#$#` 注入自定义 CSS 样式（AdGuard 风格）：

```
example.com#$#.ad-wrapper { display: none !important; }
example.com#$#body { background: none !important; }
```

- 与 `##` 的区别：`#$#` 可以注入任意 CSS 声明，`##` 只能隐藏元素

---

## 8. Scriptlet 规则

Scriptlet 是在页面主世界（MAIN world）执行的 JavaScript 片段，用于处理无法通过简单拦截/隐藏解决的广告场景。

### 8.1 AdGuard 风格

```
example.com#$#abort-on-property-read(adsLoader)
example.com#$#set-constant(adConfig.enabled, false)
example.com#$#prevent-fetch(/ads\.example\.com/)
example.com#$#prevent-window-open(/popup\.ads\./)
example.com#$#remove-attr(onclick, .ad-btn)
example.com#$#remove-class(ad-visible, .content)
```

### 8.2 uBO 风格

```
example.com#+js(abort-on-property-read, adsLoader)
example.com#+js(set-constant, adConfig.enabled, false)
example.com#+js(prevent-fetch, /ads\.example\.com/)
example.com#+js(prevent-window-open, /popup\.ads\./)
example.com#+js(remove-attr, onclick, .ad-btn)
example.com#+js(remove-class, ad-visible, .content)
```

### 8.3 已支持的 Scriptlet 列表

| Scriptlet | 功能 | 示例 |
|-----------|------|------|
| `abort-on-property-read` | 读取指定属性时抛异常 | `#$#abort-on-property-read(adsLoader)` |
| `abort-on-property-write` | 写入指定属性时抛异常 | `#$#abort-on-property-write(window.adData)` |
| `set-constant` | 将属性设为常量 | `#$#set-constant(adEnabled, false)` |
| `prevent-fetch` | 拦截匹配 URL 的 fetch 请求 | `#$#prevent-fetch(/\/ads\//)` |
| `prevent-window-open` | 拦截匹配 URL 的 window.open | `#$#prevent-window-open(/popup/)` |
| `remove-attr` | 移除匹配元素的指定属性 | `#$#remove-attr(onclick, .ad-btn)` |
| `remove-class` | 移除匹配元素的指定 class | `#$#remove-class(ad-show, .box)` |
| `noop-ads` | 视频广告占位（预留） | `#$#noop-ads()` |

### 8.4 安全约束

以下 scriptlet **永远不支持**（安全红线）：

- 含 `eval` / `new Function` 的 scriptlet
- 引用 `document.cookie` 的 scriptlet
- 发起 `fetch` / `XHR` 的 scriptlet（`prevent-fetch` 除外）

---

## 9. DNR 重定向规则（dnr-redirect:）

AdClear 自定义语法，将匹配的请求重定向到指定 URL。这是**唯一的 redirect 配置源**，始终生效。

### 语法

```
dnr-redirect: regex=<RE2正则> url=<重定向目标URL> [resourceTypes=<资源类型>]
```

- `regex`：RE2 正则表达式（Chrome DNR regexFilter 语法，不支持 lookahead/lookbehind）
- `url`：重定向目标 URL（必须是合法 URL，含协议）
- `resourceTypes`：可选，逗号分隔的资源类型，默认 `script,xmlhttprequest,other`

### 示例

```
! 搜狐视频去广告：将含 fee=0 的请求重定向到 fee=1 版本
dnr-redirect: regex=^http://v\.aty\.sohu\.com/v\?cat=.*fee=0$ url=http://v.aty.sohu.com/v?cat=&act=&autoPlay=1&fee=1 resourceTypes=script,xmlhttprequest,other

! 优酷播放器替换
dnr-redirect: regex=g\.alicdn\.com/player/ykplayer/0\.6\.[0-9]+/youku-player\.min\.js url=https://g.alicdn.com/player/ykplayer/0.5.90/youku-player.min.js resourceTypes=script
```

### 注意事项

- `regex` 中的 `.` 需转义为 `\.`
- `url` 必须是完整合法 URL（含协议 `http://` 或 `https://`）
- **不支持**重定向到裸 IP（如 `127.0.0.1`），如需快速拒绝请求请用 block 规则
- `resourceTypes` 可选值见[附录](#附录资源类型速查)

---

## 10. Adbyby 重定向规则（>>>）

兼容第三方 adbyby 规则的重定向语法，**默认关闭**（需在设置中开启"第三方重定向转换"）。

### 语法

```
[正则匹配模式/]>>>重定向目标URL>>>>keyword=标签
```

### 示例

```
/g\.alicdn\.com\/mm\/yksdk\/0\.2\.\d+\/playersdk\.js/>>>1111.51xiaolu.com/playersdk.js>>>>keyword=playersdk
```

### 注意事项

- 默认关闭，需用户主动开启（`enableRedirectConversion` 设置项）
- 第三方重定向有安全风险（可能将请求导向恶意站点），请仅在信任的规则源上开启
- 重定向目标不以 `http` 开头时自动补 `https://`

---

## 11. HLS 广告分片过滤

针对 HLS (m3u8) 视频流的广告分片过滤，通过 7 信号加权检测算法识别并剔除广告分片。

### 内置规则

系统内置 3 组站点规则：

| 规则 ID | 名称 | 适用场景 |
|---------|------|---------|
| `generic-ad-CDN` | 通用广告 CDN 域名 | 所有站点，匹配 doubleclick、googlesyndication 等广告 CDN |
| `streaming-preroll` | 免费影视站 preroll/midroll | 影视站，匹配 /ads/、/preroll/、/midroll/ 等路径 |
| `live-broadcast-scte35` | 直播/体育 SCTE-35 广告 | 直播站，匹配 /adN/、/clip/、/bumper/ 等路径 |

### 用户自定义规则

用户可通过 HLS 规则管理接口添加自定义站点规则，包含：

- `hostPattern`：站点域名正则
- `adUrlPatterns`：广告 URL 正则数组
- `scoreThreshold`：检测阈值（默认 3，直播站可放宽到 2）
- `forceKeep`：强制保留的分片 URL 正则（防误杀）

---

## 12. 不支持的规则语法

以下 ABP/uBO/AdGuard 修饰符在当前实现中**不支持**，规则会被忽略或转换失败：

| 修饰符 | 状态 | 说明 |
|--------|------|------|
| `$redirect` / `$redirect-rule` | ❌ 不支持 | DNR API 不支持裸 IP 重定向；用 block 规则替代 |
| `$popup` | ⚠️ 受限 | DNR 无法拦截弹窗，转换时降级忽略 |
| `$csp` | ⚠️ 受限 | DNR 可部分用 modifyHeaders 实现，但完整 CSP 注入受限 |
| `$replace` | ❌ 不支持 | MV3 DNR 无响应体修改能力 |
| `$cookie` | ❌ 不支持 | MV3 DNR 不支持 |
| `$rewrite` | ❌ 不支持 | ABP 资源重写，DNR 无对应能力 |
| `$removeparam` | ❌ 不支持 | DNR 无 URL 参数移除能力 |
| `$document` / `$doc` | ⚠️ 受限 | 仅在白名单规则中有效 |
| `$badfilter` | ❌ 不支持 | tsurlfilter 不解析 |
| `$important` | ⚠️ 受限 | DNR 优先级机制不同，部分场景等效 |
| `$match-case` | ⚠️ 受限 | DNR urlFilter 默认大小写不敏感 |
| `$all` | ❌ 不支持 | tsurlfilter 不解析 |
| `$app` / `$network` | ❌ 不支持 | 非浏览器场景修饰符 |
| `$permissions` | ❌ 不支持 | MV3 不支持 |
| `$stealth` / `$urlblock` | ❌ 不支持 | AdGuard 专有修饰符 |
| `$cname` | ❌ 不支持 | CNAME 解密需额外 DNS 查询 |
| `$header` / `$removeheader` | ❌ 不支持 | DNR modifyHeaders 能力有限 |

**替代方案**：

- 需要 `$redirect=127.0.0.1` 的场景 → 直接用 block 规则（`||domain^`），效果更好
- 需要 `$csp` 的场景 → 用 scriptlet `set-constant` 或 `abort-on-property-read` 替代
- 需要 `$popup` 的场景 → 用 scriptlet `prevent-window-open` 替代

---

## 附录：资源类型速查

网络规则 `$type` 修饰符与 Chrome 资源类型对照：

| 修饰符 | Chrome 资源类型 | 说明 |
|--------|----------------|------|
| `$script` | `script` | JavaScript 脚本 |
| `$image` | `image` | 图片 |
| `$stylesheet` | `stylesheet` | CSS 样式表 |
| `$font` | `font` | 字体文件 |
| `$object` | `object` | Flash/Java 等插件对象 |
| `$media` | `media` | 音视频 |
| `$subdocument` | `sub_frame` | iframe 嵌入页 |
| `$xmlhttprequest` | `xmlhttprequest` | XHR/Fetch 请求 |
| `$other` | `other` | 其他未分类请求 |
| `$document` / `$doc` | `main_frame` | 主文档（仅白名单有效） |
| `$popup` | — | 弹窗（DNR 受限） |

排除写法：`$~script`、`$~image` 等，表示"除该类型外的所有类型"。

---

> **文档版本**：v6 开发阶段 | **最后更新**：2026-10-05
> 
> 如发现规则不生效或文档与实际行为不符，请提交 Issue 反馈。
