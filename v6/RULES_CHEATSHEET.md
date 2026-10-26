# AdClear V6 规则编写速查手册

> 目标：写规则时打开就能找到对应语法，30 秒内定位到解决方案。

---

## 1. 规则类型总览

| 规则形态 | 轨道 | 用途 | 示例 |
|---|---|---|---|
| `domain##selector` | B | 元素隐藏 | `example.com##.ad-banner` |
| `domain#@#selector` | B | 隐藏例外 | `example.com#@#.sponsor` |
| `||domain^` | A | 网络拦截 | `||ads.example.com^` |
| `@@||domain^` | A | 网络例外 | `@@||api.example.com^` |
| `domain#$#css` | B | CSS 注入 | `example.com#$#body {overflow:auto}` |
| `domain##+js(...)` | B | Scriptlet (uBO) | `example.com##+js(set-constant, ads, false)` |
| `domain#%#//scriptlet(...)` | B | Scriptlet (AG) | `example.com#%#//scriptlet('set-constant', 'ads', 'false')` |
| `dnr-redirect:...` | A | 重定向 | `dnr-redirect:noop-js` |

**轨道差异：**
- **A (DNR)**：有 30,000 条上限，正则受 RE2 限制（无前瞻/后瞻/反向引用）
- **B (Content Script)**：无上限，完整正则，支持扩展选择器

---

## 2. 快速决策流程

```
广告是网络请求？
  ├─ 是 → 用 || 拦截（轨道 A）
  └─ 否 → 页面上的元素？
       ├─ 能选到？ → 用 ## 隐藏（轨道 B）
       └─ 选不到 / 需要改逻辑？ → 用 Scriptlet（轨道 B）
```

---

## 3. 网络拦截规则（轨道 A）

### 3.1 基础语法

| 符号 | 含义 | 示例 |
|---|---|---|
| `*` | 通配任意字符 | `example.com/ads/*.gif` |
| `||` | 从域名开头匹配（含所有子域） | `||ads.example.com^` |
| `^` | 分隔符（`/` `?` `:` 等或地址末尾） | `example.com^` |
| `|` | 规则开头/结尾的精确锚点 | `swf\|` |
| `@@` | 例外规则前缀 | `@@||example.com^` |
| `!` | 注释行 | `! 这是注释` |
| `/regex/` | 正则匹配 | `/banner\d+/` |

### 3.2 常用选项

```
||example.com^$third-party,script
||tracker.io^$domain=site-a.com|site-b.com
/ads/*$image,match-case
```

| 选项 | 作用 |
|---|---|
| `third-party` / `~third-party` | 只匹配跨站 / 同站请求 |
| `script`、`image`、`stylesheet`、`xmlhttprequest` | 限定资源类型 |
| `domain=a.com\|b.com` | 限定生效页面 |
| `match-case` | 区分大小写 |

### 3.3 RE2 正则限制（重要！）

以下写法会被**直接丢弃**：

| 被拒绝的写法 | 原因 | 等效改写 |
|---|---|---|
| `/ads\?(?=.*campaign)/` | 前瞻断言 | `/ads\?.*campaign/` |
| `/(?<=cdn\.)ads\.com/` | 后瞻断言 | `/cdn\.ads\.com/` |
| `/(\d+)\/\1\//` | 反向引用 | 拆成多条规则 |

单条正则长度不能超过 1000 字符。

---

## 4. 元素隐藏规则（轨道 B）

### 4.1 语法骨架

```
domain##selector            ← 基本形态
a.com,b.com##selector       ← 多域名（逗号分隔，## 前不能有空格）
~a.com##selector            ← 排除域名
a.com,~m.a.com##selector    ← 组合：生效但排除子域
##selector                  ← 全局规则（强烈不建议）
```

### 4.2 基础选择器

| 写法 | 匹配什么 | 示例 |
|---|---|---|
| `.className` | 类 | `##.ad-banner` |
| `#idName` | ID | `###pop_ad` |
| `div` / `iframe` | 标签 | `##iframe[src*="ad."]` |
| `.a.b` | 交集（同时拥有两个类） | `##.feed-item.sponsored` |

### 4.3 组合与分组：空格 vs 逗号

- **空格 = 嵌套（且）**：`A B` 选中"A 内部的 B"，最终隐藏的是 **B**
- **逗号 = 分组（或）**：`A, B` 等价于两条独立规则，A 和 B **都会**被隐藏

```html
<div class="feed">
  <div class="ad-card">广告</div>    <!-- ##.feed .ad-card 命中 -->
  <div class="news">正常</div>       <!-- 不命中 -->
</div>
<div class="sidebar">
  <div class="ad-card">推荐</div>    <!-- 不在 .feed 里，不命中 -->
</div>
```

**一字符惨案**：`##.feed, .ad-card` 会变成"隐藏整个信息流 + 隐藏全页所有 ad-card"。

完整组合符速查：

| 符号 | 名称 | 选中谁 |
|---|---|---|
| （空格） | 后代 | 后者（任意嵌套深度） |
| `>` | 子代 | 直接子元素 |
| `+` | 相邻兄弟 | 紧邻的下一个同级 |
| `~` | 通用兄弟 | 之后的全部同级 |
| `,` | 分组 | 逗号分隔的每一个 |
| （连写） | 交集 | 同一元素同时满足 |

### 4.4 属性选择器：对抗随机类名

| 写法 | 匹配 | 示例效果 |
|---|---|---|
| `[class^="ad-"]` | 开头匹配 | 命中 `ad-slot__k3j` |
| `[class$="-ad"]` | 结尾匹配 | 命中 `home-banner-ad` |
| `[class*="ad-slot"]` | 包含匹配 | 命中 `xxx__ad-slot__yyy` |
| `[class*="AD-" i]` | 包含 + 忽略大小写 | 命中 `Ad-Slot` |
| `[data-ad-slot]` | 只要属性存在 | 不看属性值 |

**警告**：`[class*="ad"]` 是高危写法——`read`、`header`、`badge` 全都包含 "ad"，能误杀半张页面。

### 4.5 扩展选择器（ExtCss）

| 扩展伪类 | 解决什么问题 | 示例 |
|---|---|---|
| `:has()` | 反向选父：按"孩子"锁定容器 | `div:has(> iframe[src*="googlesyndication"])` |
| `:contains()` | 按文本内容匹配 | `.feed-item:contains("赞助")` |
| `:matches-css()` | 按计算样式匹配 | `[class*="layer"]:matches-css(position: fixed)` |

### 4.6 例外规则 #@#

`example.com#@#.sponsor` 取消所有命中 `.sponsor` 的隐藏规则。

### 4.7 成本阶梯

1. **标准 CSS**（基础、组合、属性、结构伪类）：成本最低
2. **ExtCss**（`:has()` 等）：动态求值，控制数量
3. **Scriptlet**：成本最高，只在需要"逻辑"时使用

---

## 5. CSS 注入规则

```
example.com#$#.article-body { min-height: auto !important; }
example.com#$#body { overflow: auto !important; }
```

高频场景：修复布局塌陷、解除滚动锁定、精细隐藏。

---

## 6. Scriptlet 规则（85 个内置）

### 6.1 三种等价写法

```
example.com##+js(set-constant, adblockDetected, false)                  ← uBO 风格（推荐）
example.com#%#//scriptlet("set-constant", "adblockDetected", "false")   ← AdGuard 风格
example.com##+js(acis, JSON.parse, "adList")                            ← uBO 缩写
```

### 6.2 分类速查

| 类别 | Scriptlet | 作用 |
|---|---|---|
| **属性拦截** | `abort-on-property-read` | 读取属性时抛异常 |
| | `abort-on-property-write` | 写入属性时抛异常 |
| | `set-constant` | 把属性焊死为常量 |
| | `set-noop-object` | 设为 Proxy noop 对象 |
| | `trusted-set-constant` | 可信模式设置常量 |
| **DOM 操作** | `remove-attr` | 移除元素属性 |
| | `remove-class` | 移除元素 class |
| | `set-attr` | 设置元素属性 |
| | `trusted-set-attr` | 可信模式设置属性 |
| | `remove-node-text` | 移除文本节点内容 |
| | `trusted-replace-node-text` | 可信模式替换文本 |
| | `trusted-create-element` | 创建 DOM 元素 |
| | `trusted-click-element` | 模拟点击 |
| | `trusted-dispatch-event` | 触发自定义事件 |
| | `spoof-css` | 伪造 CSS 属性值 |
| | `hide-in-shadow-dom` | 隐藏 Shadow DOM 元素 |
| | `inject-css-in-shadow-dom` | 向 Shadow DOM 注入 CSS |
| | `remove-in-shadow-dom` | 移除 Shadow DOM 元素 |
| **网络拦截** | `prevent-fetch` | 阻止 fetch 请求 |
| | `prevent-xhr` | 阻止 XHR 请求 |
| | `prevent-window-open` | 阻止弹窗 |
| | `prevent-element-src-loading` | 阻止元素 src 加载 |
| | `prevent-navigation` | 阻止页面导航 |
| | `remove-request-query-parameter` | 移除 URL 查询参数 |
| | `trusted-replace-fetch-response` | 替换 fetch 响应 |
| | `trusted-replace-xhr-response` | 替换 XHR 响应 |
| | `json-prune-fetch-response` | 从 fetch JSON 剪枝 |
| | `json-prune-xhr-response` | 从 XHR JSON 剪枝 |
| **定时器/事件** | `prevent-setTimeout` | 拦截 setTimeout |
| | `prevent-setInterval` | 拦截 setInterval |
| | `prevent-addEventListener` | 拦截 addEventListener |
| | `aeld` | addEventListener 高级拦截 |
| | `adjust-setTimeout` | 调整 setTimeout 延迟 |
| | `adjust-setInterval` | 调整 setInterval 延迟 |
| | `prevent-requestAnimationFrame` | 拦截 requestAnimationFrame |
| **内联脚本** | `abort-current-inline-script` | 中止内联脚本 |
| | `remove-current-inline-script` | 移除内联 script 标签 |
| | `abort-on-stack-trace` | 按调用栈匹配中止 |
| | `prevent-eval-if` | 条件拦截 eval |
| | `noeval` | 完全禁用 eval |
| **数据剪枝** | `json-prune` | 从 JSON 剪掉字段 |
| | `xml-prune` | 过滤 XML 响应 |
| | `m3u-prune` | 过滤 m3u8 播放列表 |
| | `evaldata-prune` | 剪枝 eval 数据 |
| | `trusted-prune-inbound-object` | 可信模式剪枝入站对象 |
| | `trusted-json-set` | 可信模式设置 JSON 字段 |
| | `trusted-replace-outbound-text` | 替换出站文本 |
| | `trusted-replace-argument` | 替换函数参数 |
| | `trusted-suppress-native-method` | 抑制原生方法 |
| **Storage** | `set-cookie` | 设置 Cookie |
| | `trusted-set-cookie` | 可信模式设置 Cookie |
| | `set-cookie-reload` | 设置 Cookie 后刷新 |
| | `trusted-set-cookie-reload` | 可信模式设置并刷新 |
| | `remove-cookie` | 移除 Cookie |
| | `set-local-storage-item` | 设置 localStorage |
| | `set-session-storage-item` | 设置 sessionStorage |
| | `trusted-set-local-storage-item` | 可信模式设置 localStorage |
| | `trusted-set-session-storage-item` | 可信模式设置 sessionStorage |
| **SDK Mock** | `google-ima3` | Mock Google IMA SDK |
| | `google-ima3-dai` | Mock Google IMA DAI |
| | `googletagservices-gpt` | Mock Google Publisher Tag |
| | `prebid` | Mock Prebid.js |
| | `youku-ad-sdk` | Mock 优酷广告 SDK |
| | `iqiyi-ad-sdk` | Mock 爱奇艺广告 SDK |
| | `amazon-apstag` | Mock Amazon APS |
| | `gemius` | Mock Gemius 追踪 |
| | `google-analytics` | Mock Google Analytics |
| | `didomi-loader` | Mock Didomi CMP |
| | `fingerprintjs2` | Mock FingerprintJS v2 |
| | `fingerprintjs3` | Mock FingerprintJS v3 |
| **反检测** | `no-fab` | 禁用反广告检测 FAB |
| | `no-webrtc` | 禁用 WebRTC |
| | `prevent-fab-3` | 拦截 FAB v3 |
| | `prevent-bab` | 拦截 BlockAdBlock |
| | `prevent-innerHTML` | 拦截 innerHTML 写入 |
| | `prevent-refresh` | 拦截自动刷新 |
| | `prevent-constructor` | 拦截特定构造函数 |
| | `prevent-canvas` | 拦截 Canvas 指纹 |
| | `no-protected-audience` | 禁用 Protected Audience API |
| | `no-topics` | 禁用 Topics API |
| | `href-sanitizer` | 净化链接 href |
| | `close-window` | 关闭窗口 |
| | `prevent-popads-net` | 拦截 popads.net |
| **播放器** | `video-playback-hook` | Hook HTMLVideoElement |
| | `ubo-json-edit` | uBO 兼容 JSON 编辑 |

### 6.3 典型用例

```
! 反反广告检测
example.com##+js(set-constant, adblockDetected, false)

! 阻止弹窗
example.com##+js(prevent-window-open)

! 从 API 响应中移除广告字段
example.com##+js(json-prune, data.adItems)

! 拦截 fetch 到广告域
example.com##+js(prevent-fetch, /googlesyndication\.com/)

! 设置 Cookie 绕过检测
example.com##+js(set-cookie, cookieConsent, accepted)

! Mock 视频广告 SDK
example.com##+js(google-ima3)
```

---

## 7. 调试与排错

### 7.1 控制台验证选择器

```js
// 测试选择器是否匹配
document.querySelectorAll('.feed-item[class*="sponsored"]')

// 检查元素是否可见
getComputedStyle($0).display
```

### 7.2 规则不生效排查清单

| # | 检查项 | 说明 |
|---|---|---|
| 1 | 选择器错了？ | 控制台先测，空列表 = 白搭 |
| 2 | 空格/逗号用错？ | 最高频事故点 |
| 3 | 全角符号？ | `“”` `＃` `｜` 会静默失效 |
| 4 | 域名不匹配？ | 子域不向上兼容 |
| 5 | 类名大小写？ | class 区分大小写 |
| 6 | 不支持的伪类？ | 以支持清单为准 |
| 7 | 已有 #@# 豁免？ | 例外优先级更高 |
| 8 | 正则被 RE2 丢弃？ | 见 3.3 |
| 9 | 元素是 JS 后建的？ | 换稳定属性或改用 Scriptlet |
| 10 | DNR 规则超限？ | 30,000 条上限 |

---

## 8. 最佳实践

1. **域名限定是底线**，不写全局规则
2. **稳定特征优先**：语义类名 > data-* 属性 > 哈希类名
3. **宁窄勿宽**：`[class*="ad"]` 会误杀 `read`、`header`
4. **隐藏最外层容器**，不留空白
5. **网络规则优先，隐藏补刀**
6. **成本阶梯**：标准 CSS > ExtCss > Scriptlet
7. **正则避开 RE2 禁区**
8. **例外优于删除**：`#@#` / `@@` 可逆可追溯
9. **每条规则配注释**：`! 2026-10 某站信息流广告`
10. **先测后存**：控制台跑一遍比刷新页面快十倍

---

## 9. 即用模板

```
! 信息流广告
example.com##.feed [class*="ad-"], .feed [class*="sponsored"]

! 弹窗 / 浮层
example.com##div[class]:matches-css(position: fixed)

! 广告容器无特征、子 iframe 有特征
example.com##div:has(> iframe[src*="googlesyndication"])

! 文本兜底
example.com##.feed-item:contains("赞助")

! 修复布局塌陷
example.com#$#.article-body { min-height: auto !important; }

! 解除滚动锁定
example.com#$#body { overflow: auto !important; }

! 反反广告检测
example.com##+js(set-constant, adblockDetected, false)

! 接口数据去广告
example.com##+js(json-prune, data.adItems)

! 弹窗治理
example.com##+js(prevent-window-open)

! 网络 + 隐藏组合拳
||ads.example.com^
example.com##.ad-slot

! 例外豁免
example.com#@#.sponsor
@@||api.example.com^
```

---

## 附录 A：Scriptlet 缩写对照

| 缩写 | 完整名称 |
|---|---|
| `acis` | `abort-current-inline-script` |
| `aeld` | `addEventListener-defuser` |
| `nano-stb` | `nano-setTimeout-booster` |
| `nano-sib` | `nano-setInterval-booster` |

---

*本文档对应 AdClear V6 规则引擎。Scriptlet 完整参数说明见应用内《Scriptlet 语法规则技术参考》。*
