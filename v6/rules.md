# CSS4 结构伪类在去广告插件中的应用详解

CSS4 的结构伪类为广告拦截器提供了**基于 DOM 结构和内容特征**精准定位广告元素的能力。uBlock Origin 和 AdBlock Plus 利用这些选择器构建"修饰规则"（cosmetic rules），在页面渲染后隐藏广告内容，弥补了网络请求拦截（URL 过滤）的不足。

## 一、核心结构伪类机制

### 1. `:has()` — 父选择器（"猫头鹰选择器"）
`:has()` 是首个允许**根据子元素反向选择父元素**的伪类，被 uBO 称为" programmatic filters 的基石"。[citation:4]

**语法**：`selector:has(selector_list)`

```css
/* 选择包含特定子元素的父容器 */
article:has(> div.ad-banner) { display: none; }
div.comment-content:has(div.author-name:has-text('Name')) { display: none; }
```

**广告拦截应用**：
- 父容器隐藏：当广告嵌套在多层容器中时，直接隐藏最外层容器
- 条件组合：与其他伪类链式调用，实现复杂逻辑

---

### 2. `:is()` 与 `:where()` — 简化多选择器
| 伪类 | 权重特性 | uBO 应用场景 |
|------|---------|-------------|
| `:is()` | 继承参数中最具体选择器的权重 | 需要保留权重以提升优先级时 |
| `:where()` | 权重始终为 0 | 避免与站点样式冲突，用于"轻微"隐藏 |

```css
/* 同时匹配多种广告容器 */
:is(.ad-banner, .promo-container, [data-track*="ad"]) { display: none; }

/* 低权重隐藏，避免覆盖站点关键样式 */
:where(.social-share, .newsletter-popup) { display: none; }
```

在 uBO 中，`:where()` 常用于**非侵入式隐藏**，防止因权重过高导致页面布局崩溃。[citation:2][citation:3]

---

### 3. `:nth-child` / `:nth-of-type` — 结构定位
`:nth-child` 按 DOM 绝对位置计数（不区标签），`:nth-of-type` 仅统计**同类标签**。

**关键区别**：
```css
/* 第3个子元素且必须为 div（可能是第3个，但标签必须是 div） */
div:nth-child(3) { display: none; }

/* 第3个 div 子元素（只数 div 标签总数） */
div:nth-of-type(3) { display: none; }
```

**广告拦截场景**：当广告插入在固定位置（如"第2个推荐位"），但无法用 class/id 区分时，按位置定位。

---

### 4. `:not()` — 否定伪类
`:not()` 提供**反向匹配**，排除特定元素。支持复杂选择器列表（CSS4 扩展）。

```css
/* 隐藏所有非主要内容区块的固定元素 */
div:not(.main-content):not(.sidebar) > .sticky-ad { display: none; }

/* 排除正常图片，只隐藏广告图 */
img:not([alt]):not([class*="product"]) { visibility: hidden; }
```

**uBO 升级用法**：`:not()` 内部可嵌套 `:has()`，实现 **排除深层结构**：
```css
section:has(section) div:not(section section div) { display: none; }
```
此规则在禁用 `:nth-*` 和属性选择器时，通过 `:has()` + `:not()` 组合精准定位嵌套广告。[citation:16]

---

## 二、去广告插件的扩展选择器

uBO 在标准 CSS4 基础上扩展了一套**程序化美化过滤器**（Procedural Cosmetic Filters），支持链式调用：[citation:34][citation:36]

### 核心扩展伪类

| 语法 | 说明 | 示例 |
|------|------|------|
| `:has-text()` | 匹配**包含特定文本**的元素（支持正则） | `div:has-text(/广告/)` |
| `:matches-css()` | 匹配符合特定 CSS 样式的元素 | `:matches-css(position: fixed)` |
| `:upward(n)` | 选择当前元素的第 n 层祖先 | `.sticky-ad:upward(1)` |
| `:nth-ancestor(n)` | 选择指定层级的祖先元素 | `div:pcf:has-text(广告):nth-ancestor(2)` |
| `:watch-attr()` | 监控属性变化触发隐藏 | `[data-ad]:watch-attr(src)` |
| `:xpath()` | 使用 XPath 表达式选择 | `xpath(//div[contains(@class,'ad')])` |
| `::before` / `::after` | 匹配伪元素生成的广告内容 | `.ad-label::before { display: none; }` |

### 修饰规则语法对比

| 插件 | 基础规则 | 扩展规则 | 权重/选项 |
|------|---------|---------|----------|
| **AdBlock Plus** | `example.com##.ad` | `example.com#?#div:has(span:contains(text))` | 通过 `:style()` 强制样式 |
| **uBlock Origin** | `example.com##.ad` | `example.com##div:has(> .ad-banner):matches-css(position:fixed)` | `:remove()` 移除 DOM、`:style()` 修改样式 |
| **AdGuard** | `example.com##.ad` | `example.com#@#div:has(> img[data-src*="ad"])` | 支持 `remove: true` 参数隐式转换 |

**关键差异**：
- **ABP** 必须用 `#?#` 标记扩展规则，**uBO** 直接用 `##` 并原生支持 CSS4 伪类
- **uBO** 的 `:remove()` 是**动作操作符**（action operator），直接从 DOM 移除元素，而非仅隐藏
- **AdGuard** 支持 `{ remove: true; }` 语法，uBO 内部会自动转换为 `:remove()` 操作符[citation:36]

---

## 三、实战案例与编写技巧

### 案例 1：基于内容特征隐藏父级元素
场景：广告卡片混在内容流中，无固定 class，但内部含有特定文本（如"赞助内容"）。

**uBO 规则**：
```bash
! 隐藏包含特定作者名的评论块
reddit.com##div.comment-content:has(div.author-name:has-text('/^sponsor/i'))

! 隐藏包含特定文本的推广卡片
twitter.com##div[data-testid="card"]:has-text(/Promoted/)
```
**解析**：`:has()` 选择包含匹配子元素的父级，`:has-text()` 内部支持正则，匹配不区分大小写写作 `/pattern/i`。[citation:40]

---

### 案例 2：精准定位嵌套固定广告
场景：粘性广告用 `position: fixed` 但嵌套层级未知。

**uBO 规则**：
```bash
example.com##div.ad-container:matches-css(position: fixed):upward(1)
```
**解析**：`:matches-css()` 匹配样式，`:upward(1)` 向上一级父容器（即广告的直接外层包裹），避免隐藏范围过大。[citation:34]

---

### 案例 3：基于子元素数量的动态布局广告
场景：广告容器会根据内容数量动态调整（如"相关推荐"列表），需要按子项数量判断。

**uBO 规则**：
```bash
.list:has(> *:nth-child(3)):not(:has(> *:nth-child(5))) { display: none; }
```
**解析**：利用 `:has(*:nth-child(n))` 判断"至少 n 个子项"，结合 `:not()` 排除数量过多的容器，实现"3-4 个子项且符合其他特征才隐藏"。[citation:25]

---

### 案例 4：B站动态流广告黑名单
场景：需要屏蔽特定用户（如广告账号）的整个动态卡片，通过用户名特征识别。

**uBO 规则**：
```bash
t.bilibili.com##div.card:has(span[data-uid="特定UID"]):has-text(/广告|推广/)
```
**解析**：通过 `data-uid` 属性精准定位，再通过 `:has-text()` 确保内容语义匹配，避免误伤正常用户。[citation:39]

---

### 编写核心原则

| 原则 | 说明 |
|------|------|
| **精准优先于泛化** | 用 `:has()`、`:has-text()` 缩小范围，避免 `##*` 全选 |
| **链式调用增强精度** | 如 `div:has(.ad):matches-css(display: block):upward(1)` |
| **权重控制** | 复杂规则用 `:where()` 降低权重，避免覆盖站点关键布局 |
| **性能考虑** | 避免深层嵌套 `:has(:has(...))`，当前浏览器不支持嵌套 `:has()` |
| **移除 vs 隐藏** | 需要彻底移除（如防止广告脚本执行）用 `:remove()`，仅需视觉隐藏用 `display: none` |

---

## 四、兼容性与调试

### 浏览器支持

| 伪类/选择器 | Chrome | Firefox | Safari | 备注 |
|------------|--------|---------|--------|------|
| `:has()` | 105+ | 121+ | 15.4+ | 旧版 Safari 15.4+ 不支持嵌套 `:has()` |
| `:is()` / `:where()` | 88+ | 78+ | 14+ | Safari 对复杂参数有性能考量 |
| `:nth-child` / `:nth-of-type` | 全支持 | 全支持 | 全支持 | :nth-of-type 需注意混合标签场景 |
| `:user-valid` / `:user-invalid` | 102+ | 119+ | 16.4+ | 推荐用于现代表单验证（uBO 未直接利用） |

### uBO 调试技巧
1. **元素选择器工具**：点击滴管图标，自动生成选择器，但通常过于冗长，需手动简化
2. **开发者工具**：F12 → 元素选择器 → 右键 → "检查" 查看 DOM 结构
3. **动态内容**：广告可能异步加载，用 `:watch-attr()` 监控 `data-*` 属性变化
4. **规则测试**：uBO 支持导入/导出规则集，建议先在测试订阅中验证

---

## 五、总结

CSS4 结构伪类与去广告插件的结合，实现了**声明式、结构化、低维护成本**的广告隐藏方案：

```
网络请求拦截（URL/域名）  →  Cosmetic 过滤（CSS选择器）
  ↓                              ↓
阻止资源加载                 阻止元素渲染
（性能/隐私）                （视觉/布局）
```

**最佳实践路径**：
1. **网络层拦截增强**：`||ads.example.com^$third-party,script,image`
2. **元素层精准隐藏**：`example.com##div:has(.ad-unit):has-text(/广告|推广/)`
3. **异常修复**：`example.com###broken-ad-container:remove()`

通过 CSS4 的 `:has()`、`:is()`、`:not()` 组合，uBO 可以构建出媲美 JavaScript 的复杂逻辑，且完全由浏览器渲染引擎调度，无需额外扩展进程，性能优于传统注入方案。[citation:6][citation:9]
