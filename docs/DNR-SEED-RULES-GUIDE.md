# DNR 种子规则编写指引

> **本文档用于维护 `data/dnr/` 目录下的种子规则文件。**
>
> 目标：所有编写的规则必须能被 `scripts/build-static-rulesets.ts` → tsurlfilter 完整转换为 Chrome MV3 DNR 静态规则（`.json`），不丢失、不降级。
>
> 构建流程：
> ```
> data/res/*.txt（原始订阅源）
>   │  classifyRules() 分类
>   ├─ DNR 候选  → data/dnr/{id}.txt（种子） → tsurlfilter → src/public/rulesets/{id}.json
>   └─ 不支持的  → data/{id}_dyn.txt（动态加载，不走 DNR）
> ```

---

## 目录

- [1. 规则编写三原则](#1-规则编写三原则)
- [2. 种子文件格式](#2-种子文件格式)
- [3. URL 匹配模式](#3-url-匹配模式)
- [4. 资源类型修饰符](#4-资源类型修饰符)
- [5. 请求来源控制](#5-请求来源控制)
- [6. 作用域控制](#6-作用域控制)
- [7. 白名单规则](#7-白名单规则)
- [8. 重定向规则](#8-重定向规则)
- [9. 大小写敏感](#9-大小写敏感)
- [10. 常见组合模式](#10-常见组合模式)
- [11. 禁用清单（禁止写入种子）](#11-禁用清单禁止写入种子)
- [12. 编写自检清单](#12-编写自检清单)
- [13. 完整场景示例集](#13-完整场景示例集)

---

## 1. 规则编写三原则

### 原则一：先精确，后宽泛

```
❌ 不好:  ||ads.com^          （拦截所有 ads.com，可能误伤合法资源）
✅ 好:   ||ads.com^$script,third-party   （只拦第三方嵌入的脚本）
✅ 更好: ||ads.com/banner/*.js$script,third-party   （精确到路径）
```

### 原则二：`$third-party` 是你的默认选择

拦截广告域名时，**90% 以上的场景都应该加 `$third-party`**：

```
✅ ||doubleclick.net^$third-party
✅ ||googlesyndication.com^$script,third-party
```

原因：广告域名通常只在**别人网站上**作为第三方出现，自己不会访问自己。加了 `$third-party` 能：
- 防止用户直接访问这些广告域名时被拦截
- 减少对同源嵌入式资源的误伤

### 原则三：优先匹配域名锚定 `||`

```
❌ 不好:  https://www.baidu.com/ads.js         （太精确，子域一变就失效）
❌ 不好:  /ads.js                              （太宽泛，可能匹配到合法 ads.js）
✅ 好:   ||baidu.com/ads.js                    （域名锚定 + 精确路径）
✅ 好:   ||baidu.com^$script                   （域名锚定 + 资源类型）
```

---

## 2. 种子文件格式

### 文件头

每个种子文件必须以 ABP header 开头：

```
[Adblock Plus 2.0]
```

### 规则结构

每行一条规则，基本格式：

```
<URL匹配模式>$<修饰符1>,<修饰符2>,...
```

### 注释

以 `!` 开头的行：

```
! === 百度广告 ===
||eclick.baidu.com^$third-party
||cpro.baidustatic.com^$script
```

### 空行

空行合法，用于分组。构建脚本自动跳过。

### 完整示例

```
[Adblock Plus 2.0]
! Source: AdClear Core Rules
! 说明: 通用广告域名拦截

! === Google AdSense ===
||pagead2.googlesyndication.com^$script,third-party
||tpc.googlesyndication.com/simgad/$image,third-party

! === 百度广告 ===
||eclick.baidu.com^$third-party
||cpro.baidustatic.com^$script
```

---

## 3. URL 匹配模式

### 3.1 域名锚定 `||`（最常用）

匹配任何协议下的该域名及其子域：

```
规则: ||example.com^
匹配:
  ✅ https://example.com/ad.js
  ✅ http://ads.example.com/banner.gif
  ✅ https://sub.sub2.example.com/tracker?x=1
不匹配:
  ❌ https://example.com.cn/ad.js       （.cn 不是 example.com 的子域）
```

**分隔符 `^`**：表示域名在此结束，后接分隔符字符 `/ ? : = & \ #` 之一。

```
规则: ||example.com^
匹配:
  ✅ https://example.com/ad.js          (^ 匹配 /)
  ✅ https://example.com?ad=1           (^ 匹配 ?)
  ✅ https://example.com:8080/ad         (^ 匹配 :)
不匹配:
  ❌ https://example.com.cn/ad          （域名后面紧跟 .cn，无分隔符）
  ❌ https://example.com/abc            （有 ^ 就能匹配后面的 /）
```

### 3.2 路径锚定 `/`

匹配 URL 中的路径片段：

```
规则: /ad/banner/
匹配:
  ✅ https://example.com/ad/banner/top.js
  ✅ https://ads.com/ad/banner/bottom.gif
❌ 但过于宽泛，通常配合修饰符使用:
  /ad/banner/$script,third-party          ← 推荐写法
```

### 3.3 起始锚定 `|`

匹配 URL 的开头：

```
规则: |https://tracker.com/collect
匹配:
  ✅ https://tracker.com/collect
  ❌ http://tracker.com/collect           （http ≠ https）
  ❌ https://tracker.com/collect?x=1      （有 query 参数，开头不一样）
```

### 3.4 结束锚定 `|`

放在规则末尾，匹配 URL 的结尾：

```
规则: /tracker.js|
匹配:
  ✅ https://example.com/tracker.js
  ❌ https://example.com/tracker.js?x=1   （结尾不是 .js）
```

### 3.5 精确锚定 `|...|`（首尾都加）

```
规则: |https://ads.com/|
只匹配:
  ✅ https://ads.com/
  ❌ 任何其他 URL
```

### 3.6 正则表达式 `/regex/`

```
规则: /^https?:\/\/ads\d+\.com\/.*\.js/$script
匹配:
  ✅ https://ads12.com/banner.js
  ✅ http://ads99.com/tracker.js
```

⚠ **使用警告**：
- 转换后 regexFilter 长度不能超过 **2000 字符**（Chrome 硬限制）
- 建议不超过 **180 字符**（保证匹配性能）
- 复杂 regex 容易被 tsurlfilter 拒绝（`More complex regex than allowed`）
- **能用 urlFilter 就别用 regexFilter**

### 3.7 通配符 `*`

```
规则: ||cdn.com/*.js$script
匹配任何 .js 文件
```

`*` 在 urlFilter 中匹配任意字符（包括 `/`），但匹配效率低于精确模式，**谨慎使用**。

---

## 4. 资源类型修饰符

指定规则仅对某些请求类型生效。

### 支持的类型

| 修饰符 | DNR resourceType | 适用场景 |
|---|---|---|
| `$script` | `script` | JS 脚本（广告联盟追踪、反绕过检测） |
| `$image` | `image` | 图片广告（banner、sprite 图） |
| `$media` | `media` | 音频/视频广告（片头、插屏） |
| `$object` | `object` | Flash/插件资源（老式广告） |
| `$subdocument` 或 `$frame` | `subdocument` | iframe 嵌入的广告页面 |
| `$xmlhttprequest` 或 `$xhr` | `xmlhttprequest` | AJAX 请求（JSON API 广告、实时竞价） |

### 类型组合

逗号分隔，**OR 逻辑**（匹配任一类型即生效）：

```
||ads.com^$script,image,third-party
```

### 排除某类型 `$~type`

只拦非 script 的类型：

```
||tracker.com^$~script
```

### 匹配所有类型 `$all`

除 `xmlhttprequest` 和 `websocket` 之外的全部类型：

```
||evil-tracker.com^$all
```

### 场景示例

```
! 只拦第三方脚本广告
||doubleclick.net^$script,third-party

! 只拦图片广告（不拦脚本）
||ads.example.com^$image,third-party

! 视频片头广告
||vod-ads.com/start/$media

! iframe 弹窗广告页面
||popup-ads.com^$subdocument,third-party

! AJAX 实时竞价请求
||ads-api.com/rtb/$xmlhttprequest,third-party
```

---

## 5. 请求来源控制

### `$third-party` — 仅拦第三方请求（最常用）

请求的发起页面域名 ≠ 请求目标域名：

```
规则: ||ads.com^$third-party

在 myblog.com 页面加载 ads.com 广告 → ✅ 拦截（第三方）
在 ads.com 自己页面加载 ads.com 资源 → ❌ 放行（同源）
```

### `$first-party` / `$1p` — 仅拦同源请求

```
规则: ||my-blog.com/ad/$first-party
只拦截 my-blog.com 自己页面里加载的 ad/ 资源
（通常用于屏蔽站点自身的广告位）
```

### `$third-party` 与资源类型组合

```
! 最常见的组合：第三方脚本
||ads.com^$script,third-party

! 第三方图片
||ads.com^$image,third-party

! 第三方 iframe
||ads.com^$frame,third-party
```

### 场景示例

```
! 通用第三方广告拦截（基础入门）
||googletagservices.com^$script,third-party
||doubleclick.net^$third-party
||moatads.com^$third-party

! 头条系广告（在别的网站上嵌头条的广告）
||snssdk.com^$script,third-party

! 腾讯广告（联盟投放）
||eqqwl.com^$third-party
||pgdt.gtimg.cn^$image,third-party
```

---

## 6. 作用域控制

### `$domain=X|Y` — 仅在指定站点生效

规则**只**在 `X` 或 `Y` 域名的页面上匹配：

```
! 只在知乎和微博上拦这条
||ads.qq.com^$domain=zhihu.com|weibo.com

! 等价 DNR: initiatorDomains: ["zhihu.com", "weibo.com"]
```

### `$domain=~X` — 排除指定站点

在**除了 X 之外的**所有站点上生效：

```
! 拦 ads.com，但在 myblog.com 上放行
||ads.com^$third-party,domain=~myblog.com

! 等价 DNR: excludedInitiatorDomains: ["myblog.com"]
```

### 组合使用

```
! 在知乎拦脚本，在微博拦所有
||ads.com^$script,domain=zhihu.com
||ads.com^$third-party,domain=weibo.com

! 排除多个站点
||tracker.com^$third-party,domain=~baidu.com|~google.com|~github.com
```

### 场景示例

```
! 知乎专栏里经常嵌的"相关推荐"iframe
||t.coral.qq.com^$frame,domain=zhihu.com

! 微博上的推广链接跟踪
||s.click.taobao.com^$xmlhttprequest,domain=weibo.com|weibo.cn

! 排除自家业务域名（重要！防止误伤）
||analytics.com^$script,third-party,domain=~mycompany.com|~staging.mycompany.com
```

---

## 7. 白名单规则

### 基本写法

以 `@@` 开头，**放行请求**：

```
@@||analytics.com^                    ← 永远放行 analytics.com
@@||myblog.com/ad/                    ← 放行 myblog.com 的 ad/ 路径
```

### 带修饰符的白名单

```
@@||ads.com^$script,third-party       ← 只放行第三方脚本，其他类型仍拦
@@/track/$xmlhttprequest             ← 放行 /track/ 的 AJAX 请求
@@||ads.com^$domain=myblog.com        ← 只在 myblog.com 上放行
```

### 常见用途

| 用途 | 示例 |
|---|---|
| 放行 CDN 公共库 | `@@||jsdelivr.net/*` |
| 放行 Google 资源 | `@@||ajax.googleapis.com/*` |
| 放行自家业务 | `@@||myapi.com^` |
| 修复被误杀的功能 | `@@||tracker.com/collect$domain=myblog.com` |
| 局域网内网 | `@@||192.168.*`, `@@||10.0.*` |

### 白名单原则

1. **精确到路径，不要全域名放行**
   ```
   ❌ @@||qq.com^                    ← 太宽，放行整个 qq.com 的所有请求
   ✅ @@||qq.com/cgi-bin/*?sid=ads   ← 精确放行某个功能点
   ```

2. **能用修饰符就别裸放**
   ```
   ❌ @@||analytics.com^
   ✅ @@||analytics.com/collect$xmlhttprequest   ← 只放行采集 API，图片脚本仍可拦
   ```

3. **放行规则优先精确拦截规则编写** — 先写好拦截规则，测试中发现误伤再加白名单

---

## 8. URL 参数移除规则（`$removeparam=`）

### 基本写法

```
||ads.com^$removeparam=adid
```

tsurlfilter 会将 `$removeparam=xxx` 转换为 DNR 的 `redirect.transform.queryTransform.removeParams` 格式，移除 URL query 中的指定参数。

### 组合使用

```
! 移除 tracker 参数（仅在第三方请求上）
||tracker.com^$third-party,removeparam=sid

! 移除视频广告相关参数（仅 NBA 站点）
||clips-manifests-aka.warnermediacdn.com^$xhrremoveparam=caiddomain=nba.com
```

> 💡 这是本项目中**唯一的 redirect 来源**（共 3 条，均来自 ublock-filters.txt）。分类器会将所有 `$redirect=` / `$redirect-rule=` 规则分流到 dyn.txt，种子文件中**禁止**出现 `$redirect=` 修饰符。

### ⚠ `$redirect=` vs `$removeparam=` 的区别

| 修饰符 | 本项目分类 | 原因 |
|---|---|---|
| `$redirect=noopjs` / `$redirect=1x1-transparent.gif` | ❌ **分流到 dyn.txt** | 需要扩展内预置 redirect 资源（`src/public/redirects/` 目录），项目未采用此方案 |
| `$redirect-rule=...` | ❌ **分流到 dyn.txt** | uBlock 高级语法，tsurlfilter 不支持 |
| `$removeparam=name` | ✅ **进入静态 DNR** | tsurlfilter 自动转换为 `redirect.transform` 格式，无需预置资源 |

---

## 9. 大小写敏感

默认规则**不区分大小写**。需要区分时加 `$match-case`：

```
规则: /Ad/$match-case
匹配:
  ✅ https://example.com/Ad.js
  ❌ https://example.com/ad.js
  ❌ https://example.com/AD.js
```

### 使用场景

```
! 区分路径大小写（有些服务器是区分的）
/myPath/Ad/$script,match-case

! 区分文件名
/Tracker.JS/$match-case
```

---

## 10. 常见组合模式

以下是实践中验证过的高效果规则模式，**推荐直接套用**：

### 模式一：基础域名拦截（新手入门）

```
||doubleclick.net^$third-party
||googlesyndication.com^$third-party
||googletagservices.com^$script,third-party
```

### 模式二：精准路径拦截

```
||ads.com/banner/*.gif$image,third-party
||cdn.com/ad/tracker.js$script,third-party
```

### 模式三：站点专属规则

```
! 知乎
||t.coral.qq.com^$frame,domain=zhihu.com
||pagead.l.doubleclick.net^$domain=zhihu.com

! B站
||cn-hangzhou-video.bilibili.com/ad/$media,domain=bilibili.com
||api.bilibili.com/x/ad/$domain=bilibili.com

! 微博
||s.weibo.com/universal/aj/reload/$xmlhttprequest,domain=weibo.com
```

### 模式四：排除误伤

```
! 拦但排除自家
||tracker.com^$script,third-party,domain=~mycompany.com

! 多站点排除
||ads.com^$third-party,domain=~github.com|~stackoverflow.com|~developer.mozilla.org
```

### 模式五：局域网/内网放行

```
@@||192.168.*
@@||127.0.*
@@||10.0.*
@@||172.17.*
```

### 模式六：CDN 公共库放行

```
@@||jsdelivr.net/*
@@||bootcss.com/*
@@||cdnjs.cloudflare.com/*
@@||unpkg.com/*
```

---

## 11. 禁用清单（禁止写入种子）

以下规则写入种子文件后，**构建脚本分类器 `shouldGoToDynamic()` 会直接分流到 dyn.txt**，请写入 `data/res/*.txt` 原始源文件（让构建脚本自动分流到动态规则），**不要手动写进 `data/dnr/`**。

### ❌ Element Hiding（CSS 选择器隐藏）

```
ifeng.com##[class*="index_topBox_"]
weibo.com##.ad-wrap
youtube.com##+js(click2loop)         ← uBlock scriptlet 形式的 EH
```

### ❌ EH 例外规则

```
stackoverflow.com#@#.ad-sidebar
```

### ❌ Scriptlets / Extended

```
ifeng.com#%#//scriptlet('set-noop-object', 'IfengAmgr')
reddit.com#%#//scriptlet('prevent-ad-popups')
```

### ❌ `$popup` / `$popunder`

```
||evil.com$popup                    ← 分类器直接分流，无例外
||evil.com$script,popup,third-party ← 同样分流，分类器不做"有其他修饰符则保留"的例外判断
```

### ❌ `$redirect=` / `$redirect-rule=`

```
||ads.com$redirect=noopjs           ← 需扩展预置 redirect 资源（本项目未使用）
||ads.com$redirect-rule=noopjs     ← uBlock 高级语法，tsurlfilter 不支持
```

### ❌ `$denyallow=`

```
||ads.com^$denyallow=trusted.com
```

### ❌ `$replace=`（响应体替换）

```
||ads.com/response$replace=/ad/''/
```

### ❌ `$badfilter`

```
||ads.com$badfilter
```

### ❌ `$rewrite=`

```
||tracker.com^$rewrite=remove-query
```

### ❌ Cosmetic 修饰符（分类器 COSMETIC_PATTERNS 匹配）

```
||ads.com^$generichide              ← generic hide
||ads.com^$ghide                    ← generic hide 简写
||ads.com^$elemhide                 ← element hiding trigger
||ads.com^$shide                    ← specific hide
||ads.com^$genericblock             ← generic blocking
```

### ❌ 超长 regexFilter（> 180 字符）

会被构建脚本主动跳过。

### ✅ 允许的"边缘"修饰符

| 修饰符 | 分类器行为 | 说明 |
|---|---|---|
| `$removeparam=name` | ✅ 进入静态 DNR | 转换为 `redirect.transform.queryTransform.removeParams`（**本项目唯一的 redirect 来源**） |

### 快速判断

| 规则看起来像什么 | 放哪 |
|---|---|
| URL + `$script/$image/$third-party/$domain=` 等 | ✅ `data/dnr/{id}.txt`（DNR 种子） |
| `domain##selector` | ❌ 原始源文件，让构建脚本分流 |
| `domain#%#//scriptlet` | ❌ 同上 |
| URL + `$popup/$redirect=/$denyallow=` | ❌ 分类器分流到 dyn.txt |
| URL + `$generichide/$ghide` | ❌ 分类器分流到 dyn.txt |

---

## 12. 编写自检清单

写完一条规则后，按此顺序检查：

### 基础检查

- [ ] 有明确的目标 URL（不是空的）
- [ ] 有域名锚定 `||` 或路径锚定 `/`
- [ ] 不使用禁用清单中的修饰符

### 修饰符检查

- [ ] 是否应该加 `$third-party`？（90% 场景应该加）
- [ ] 是否应该加资源类型 `$script` / `$image` 等？
- [ ] 是否应该加 `$domain=` 限定作用域？
- [ ] 如果用了 `$removeparam=`，确认参数名正确

### 反例检查（防止误伤）

- [ ] 这条规则会不会拦截合法资源？
- [ ] 是否需要 `$domain=~` 排除特定站点？
- [ ] 是否过于宽泛？能不能更精确？

### 构建验证

```bash
# 1. 把规则加入 data/res/{id}.txt
# 2. 跑构建，看是否被正确提取到种子
bun run scripts/build-static-rulesets.ts
# 看输出中你的规则是否在 DNR candidates 中，而不是 errors

# 3. 如果写进 data/dnr/{id}.txt 了，直接转 DNR
#    检查 rulesets-config.json 的 errors 字段
npm run build
# 看 tsurlfilter 输出是否有 errors
```

---

## 13. 完整场景示例集

### 场景一：通用广告域名拦截

覆盖主流广告联盟、追踪平台：

```
! === Google AdSense / DoubleClick ===
||pagead2.googlesyndication.com^$script,third-party
||tpc.googlesyndication.com/simgad/$image,third-party
||googleadservices.com^$third-party
||googletagservices.com^$script,third-party
||doubleclick.net^$third-party
||dcm.gdoubleclick.net^$third-party

! === Facebook Audience Network ===
||an.facebook.com^$third-party
||connect.facebook.net/en_US/fbevents.js$script,third-party

! === Amazon Associates ===
||z-na.amazon-adsystem.com^$third-party
||z0.assets-yammer.com^$third-party

! === 腾讯广告 ===
||eqqwl.com^$third-party
||pgdt.gtimg.cn^$image,third-party
||rtbcdn.goofish.com^$third-party

! === 百度广告 ===
||eclick.baidu.com^$third-party
||cpro.baidustatic.com^$script
||pos.baidu.com^$third-party

! === 字节跳动/头条 ===
||snssdk.com^$script,third-party
||ad.oceanengine.com^$third-party
||pangolin-sdk-toutiao.com^$script

! === 微博广告 ===
||weibo.com/ajax/ad^$xmlhttprequest,domain=weibo.com|weibo.cn
||s.weibo.com/universal/aj/$xmlhttprequest,domain=weibo.com

! === 快手 ===
||ad.kwai.com^$third-party

! === 360 ===
||e.360.cn^$third-party
||p.360.cn^$script,third-party
```

### 场景二：视频站点广告

片头/插屏广告通常是 media 类型，或需要 redirect 替换：

```
! === B 站 ===
||cn-hangzhou-video.bilibili.com/ad/$media,domain=bilibili.com
||api.bilibili.com/x/ad/$domain=bilibili.com
||s1.hdslb.com/bfs/ad/$image,domain=bilibili.com

! === 爱奇艺 ===
||iqiyi.com/ad_front/$script,domain=iqiyi.com
||dispatcher.video.qiyi.com/jp/$media,domain=iqiyi.com
||stc.iqiyi.com/images/template/$image,domain=iqiyi.com

! === 腾讯视频 ===
||v.qq.com/xtvideo/ad/$script,domain=v.qq.com
||pbaccess.video.qq.com/trpc/$xmlhttprequest,domain=v.qq.com

! === 优酷 ===
||acs.youku.com/h5/mtop.youku/$xmlhttprequest,domain=youku.com
||acs.youku.com/h5/mtop.youku.live/$xmlhttprequest,domain=youku.com

! === 芒果 TV ===
||ad.mgtv.com/a/$third-party
||pc.mgtv.com/ad/$script,domain=mgtv.com

! === 西瓜视频 ===
||ad.streakapi.com/request/$xmlhttprequest,third-party
||snssdk.com/ad/$script,third-party
```

### 场景三：资讯/新闻站点

```
! === 今日头条 ===
||toutiao.com/ad/$script,domain=toutiao.com
||pangolin-sdk-toutiao.com^$script

! === 知乎 ===
||t.coral.qq.com^$frame,domain=zhihu.com
||pagead.l.doubleclick.net^$domain=zhihu.com
||shortmsg.zol.com.cn^$image,domain=zhihu.com

! === 微博 ===
||s.weibo.com/universal/aj/$xmlhttprequest,domain=weibo.com|weibo.cn
||weibo.com/ajax/friendships/$xmlhttprequest,domain=weibo.com
||ad.weibo.cn^$third-party

! === 百度资讯 ===
||cpro.baidustatic.com^$script,domain=news.baidu.com
||pos.baidu.com^$domain=news.baidu.com

! === 360 资讯 ===
||p.360.cn^$script,third-party
||e.360.cn^$third-party,domain=news.360.cn

! === 澎湃新闻 ===
||t.coral.qq.com^$frame,domain=thepaper.cn
||ads.thepaper.cn^$third-party
```

### 场景四：电商站点

电商广告竞争激烈，白名单要谨慎：

```
! === 淘宝/天猫 ===
||p.l.taobao.com^$script,third-party
||t.taobao.com/exchange/$third-party
||img.alicdn.com/tps/$image,third-party
||gm.mmstat.com^$script,third-party

! === 京东 ===
||mstatic.jd.com/ad/$script,third-party
||jads.jd.com^$third-party
||click.jd.com^$third-party,domain=jd.com

! === 拼多多 ===
||mobile.yangkeduo.com/api.php/$xmlhttprequest,domain=yangkeduo.com
||u0.ad.kuaishou.com^$third-party

! === 唯品会 ===
||cps.baixin.com.cn^$third-party
||union.kuaixiu.com^$third-party,domain=vip.com

! === 小红书 ===
||r.xiaohongshu.com/ad/$xmlhttprequest,domain=xiaohongshu.com
||adservice.xiaohongshu.com^$third-party
```

### 场景五：开发者/技术站点

```
! === 知乎 ===
||t.coral.qq.com^$frame,domain=zhihu.com
||pagead.l.doubleclick.net^$domain=zhihu.com
||shortmsg.zol.com.cn^$image,domain=zhihu.com

! === CSDN ===
||i.csdnimg.cn/ad/$image,domain=csdn.net
||click.csdn.net^$third-party,domain=csdn.net
||static.kuaishou.com^$script,third-party,domain=csdn.net

! === SegmentFault ===
||ads.tencentyun.com^$domain=segmentfault.com
||pgdt.gtimg.cn^$image,domain=segmentfault.com

! === Stack Overflow ===
||adservice.google.com^$domain=stackoverflow.com
||googletagservices.com^$script,domain=stackoverflow.com

! === GitHub ===
! GitHub 本身广告少，主要拦截追踪
||github.com/collect/$xmlhttprequest,domain=github.com

! === 掘金 ===
||i.snssdk.com^$script,third-party,domain=juejin.cn
||ad.oceanengine.com^$domain=juejin.cn
```

### 场景六：隐私/追踪通用拦截

跨站点的行为追踪，高优先级：

```
! === Google Analytics ===
||google-analytics.com/collect$xmlhttprequest,third-party
||ssl.google-analytics.com/collect$xmlhttprequest,third-party
||analytics.google.com/collect$xmlhttprequest,third-party

! === Facebook Pixel ===
||facebook.com/tr/$xmlhttprequest,third-party
||connect.facebook.net/fbevents.js$script,third-party

! === 字节跳动追踪 ===
||mcs.snssdk.com/log/$xmlhttprequest,third-party
||mcs.zijieapi.com/log/$xmlhttprequest,third-party

! === 友盟 ===
||log.umeng.com/api/$xmlhttprequest,third-party
||log.umeng.com/v2/$xmlhttprequest,third-party

! === 神策 ===
||sa.sensorsdata.cn/sa/$xmlhttprequest,third-party

! === GrowingIO ===
||vio.growingio.com/gio/$xmlhttprequest,third-party

! === Hotjar ===
||hotjar.com/api/$xmlhttprequest,third-party
||h-usr.hotjar.com^$script,third-party

! === Mixpanel ===
||mixpanel.com/track/$xmlhttprequest,third-party
```

### 场景七：白名单（防误伤）

```
! === CDN 公共资源库 ===
@@||jsdelivr.net/*
@@||bootcss.com/*
@@||cdnjs.cloudflare.com/*
@@||unpkg.com/*
@@||cdn.jsdelivr.net/*

! === Google 常用资源 ===
@@||ajax.googleapis.com/*
@@||fonts.googleapis.com/*
@@||fonts.gstatic.com/*
@@||gstatic.com/*

! === GitHub 资源 ===
@@||github.com/*
@@||githubusercontent.com/*

! === 局域网内网 ===
@@||192.168.*
@@||127.0.*
@@||10.0.*
@@||172.17.*
@@||localhost^
@@||0.0.0.0^

! === 开发者常用工具 ===
@@||npmjs.com/*
@@||registry.npmjs.org/*
@@||pypi.org/*
@@||registry.nuget.org/*

! === 业务豁免（自定义） ===
@@||mycompany.com^                    ← 放行自家业务域
@@||myapp.com/api/$domain=myapp.com   ← 放行自家 API
```

---

## 文档维护

本文档应随以下事件同步更新：

1. 新增 tsurlfilter 支持的修饰符
2. 发现新的 DNR 转换边界
3. 种子文件结构调整
4. 项目发布新版本

文档位置：`docs/DNR-SEED-RULES-GUIDE.md`
技术详解参考：`docs/DNR-RULE-REFERENCE.md`
构建脚本：`scripts/build-static-rulesets.ts`
