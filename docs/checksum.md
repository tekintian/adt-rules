# ABP 订阅文件 Checksum 算法

> 基于 Adblock Plus 官方源码 `combineSubscriptions.py` 逆向分析。

## 1. Checksum 校验机制

| 机制 | 算法 | 用途 | 适用文件 |
|------|------|------|---------|
| **Checksum** | MD5 + Base64 | 检测传输损坏 | 所有 .txt 规则文件 |

> ABP 从 3.x 版本起已不再验证 checksum，但 EasyList 等第三方仍生成，因此作为订阅消费者必须正确验证。

## 2. ABP 官方 Checksum 算法

用于自有源规则（adt-*.txt）和国际标准订阅（EasyList 等）。

源码出处：[combineSubscriptions.py](https://github.com/adblockplus/sitescripts/blob/master/sitescripts/subscriptions/combineSubscriptions.py)

### 算法步骤

```
1. lines = raw.splitlines()           // 按行分割（自动处理 CRLF/LF）
2. header = lines.pop(0)              // 弹出首行 [Adblock Plus ...]
3. seen = {'checksum', 'version'}     // 关键！预置这两个键
4. 对 lines 中每一行:
   a. 匹配 /^!\s*(Redirect|Homepage|Title|Checksum|Version|Expires)\s*:/i
   b. 若匹配且 key ∈ seen → 移除该行
   c. 若匹配且 key ∉ seen → seen.add(key)，保留该行
   d. 若不匹配 → 保留该行
5. content = header + '\n' + lines.join('\n')
6. md5_digest = MD5(content.encode('utf-8'))
7. checksum = base64(md5_digest).rstrip('=')
```

### 关键细节

- `seen` 集合预置了 `{'checksum', 'version'}`，**首次出现的 Checksum 和 Version 行也被移除**
- header 行参与 MD5 计算，且位于最前面
- Base64 编码后去掉尾部 `=`
- 使用 `splitlines()` 而非 `split('\n')`

### 典型 checksum 格式

22 字符，如 `3QjuKP782CzJFwi5L1yckA`

## 3. 简单 Checksum 算法（国内第三方）

用于 adbyby、diy 等国内第三方规则文件。

### 算法步骤

```
1. lines = raw.split('\n')            // 注意：不是 splitlines()
2. filtered = [l for l in lines if not match('! Checksum:', l)]
3. normalized = '\n'.join(filtered).replace('\r', '')
4. md5_digest = MD5(normalized.encode('utf-8'))
5. checksum = base64(md5_digest)      // 保留 == 尾部
```

### 与 ABP 官方算法的区别

| 特征 | ABP 官方算法 | 简单算法 |
|------|------------|---------|
| 行分割 | `splitlines()` | `split('\n')` |
| Header 处理 | 弹出后拼接到最前 | 不弹出 |
| Checksum 行 | 预置 seen 移除 | 直接过滤移除 |
| Version 行 | 预置 seen 移除 | 保留 |
| Base64 尾部 | `rstrip('=')` | 保留 `==` |
| 典型长度 | 22 字符 | 24 字符 |

### 典型 checksum 格式

24 字符，如 `5DsPIzUs6i9TN+K9a+yByQ==`

## 4. 前端验证策略

由于存在多种 checksum 格式，前端验证时按优先级依次尝试：

1. ABP 官方算法 + MD5 base64 stripped（自有源 / EasyList）
2. ABP 官方算法 + MD5 base64 with padding
3. ABP 官方算法 + MD5 hex
4. 简单算法 + MD5 base64 with padding（adbyby 等国内第三方）
5. 简单算法 + MD5 base64 stripped
6. 简单算法 + MD5 hex
7. 全部不匹配 → 抛 SubscriptionChecksumError

## 5. 常见误区

### 以为只需移除 Checksum 行

ABP 的 `seen` 集合预置了 `{'checksum', 'version'}`，首次出现的 Checksum 和 Version 行也被移除。

### 用 `split('\n')` 代替 `splitlines()`

| 方法 | `'a\nb\n'` 结果 | `'a\r\nb'` 结果 |
|------|-----------------|-----------------|
| `split('\n')` | `['a', 'b', '']` | `['a\r', 'b']` |
| `splitlines()` | `['a', 'b']` | `['a', 'b']` |

ABP 使用 `splitlines()`，简单算法使用 `split('\n')`。

## 6. 参考链接

- [ABP 官方 checksum 算法源码](https://github.com/adblockplus/sitescripts/blob/master/sitescripts/subscriptions/combineSubscriptions.py)
- [python-abp 库](https://github.com/adblockplus/python-abp)
- [ABP 过滤规则文档](https://adblockplus.org/en/filters#checksums)（已归档）
- [update_md5.py](../update_md5.py) — 版本/checksum 自动更新
