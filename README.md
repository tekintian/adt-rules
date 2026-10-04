# AdClear 过滤规则 (adt-rules)

AdClear 广告终结者的过滤规则仓库，包含自有源规则、第三方规则和增强规则。

仓库地址：https://gitee.com/tekintian/adt-rules

## 规则订阅地址

### 自有源规则（RSA 签名 + Checksum）

| 规则 | 订阅地址 | 说明 |
|------|---------|------|
| 基础规则 | `https://gitee.com/tekintian/adt-rules/raw/master/adt-base.txt` | 核心广告过滤规则 |
| 热门规则 | `https://gitee.com/tekintian/adt-rules/raw/master/adt-hot.txt` | 热门网站专项优化 |
| 开发规则 | `https://gitee.com/tekintian/adt-rules/raw/master/adt-dev.txt` | 开发者工具/文档站去广告 |
| 视频规则 | `https://gitee.com/tekintian/adt-rules/raw/master/adt-video.txt` | 视频站点广告过滤 |
| 网页规则 | `https://gitee.com/tekintian/adt-rules/raw/master/adt-web.txt` | 网页广告/弹窗过滤 |

### 增强规则

```
https://gitee.com/tekintian/adt-rules/raw/master/plus/js.txt
https://gitee.com/tekintian/adt-rules/raw/master/plus/html5player.txt
```

### 第三方规则

| 规则 | 文件 | 说明 |
|------|------|------|
| DIY 规则 | `diy.txt` | 社区维护的自定义规则 |
| AdByBy 基础 | `adbyby/lazy.txt` | AdByBy 基础过滤规则 |
| AdByBy 视频 | `adbyby/video.txt` | AdByBy 视频过滤规则 |

## 项目结构

```
adt-rules/
├── adt-base.txt              # 自有源基础规则
├── adt-hot.txt               # 自有源热门规则
├── adt-dev.txt               # 自有源开发规则
├── adt-video.txt             # 自有源视频规则
├── adt-web.txt               # 自有源网页规则
├── diy.txt                   # 第三方 DIY 规则
├── adbyby/                   # AdByBy 第三方规则
│   ├── lazy.txt
│   ├── video.txt
│   └── md5.json
├── plus/                     # 增强规则
│   ├── js.txt / js_src.txt
│   └── html5player.txt
├── config/                   # 订阅配置文件
├── dnsmasq/                  # dnsmasq/hosts 格式规则
├── hosts/                    # hosts 格式规则
├── AdGuard/                  # AdGuard DNS 过滤规则
├── lulu/                     # LuLu 防火墙规则
├── docs/                     # 技术文档
│   ├── checksum-signature.md # Checksum 与签名算法详解
│   ├── rule-examples.md      # ABP 规则语法示例
│   └── ...
├── sign_rules.py             # RSA 签名工具
├── update_md5.py             # 版本/checksum 自动更新
├── setup_hooks.sh            # Git hook 安装脚本
├── rsa-public-key.pem        # RSA 公钥（可公开）
├── rsa-private-key.pem       # RSA 私钥（.gitignore 排除）
└── md5.json                  # 全局文件 MD5 校验
```

## Checksum 与签名

自有源规则（adt-*.txt）同时使用 **Checksum**（检测传输损坏）和 **RSA Signature**（防篡改）两种校验机制：

```
! Checksum: 3QjuKP782CzJFwi5L1yckA    ← MD5 + Base64（ABP 官方算法）
! Signature: udYnnsj7qREvuMjzk+We... ← RSA-SHA256 + Base64
```

第三方规则（adbyby 等）仅使用 Checksum（简单算法）。

详细算法说明见 [docs/checksum-signature.md](docs/checksum-signature.md)。

## 工具使用

### 首次克隆后安装 Git Hook

```bash
bash setup_hooks.sh
```

安装后，每次 `git commit` 自动执行：
1. `update_md5.py` — 更新 Version/Checksum + md5.json（增量，仅处理有变化的文件）
2. `sign_rules.py` — 对自有源规则 RSA 签名

### 手动签名

```bash
python3 sign_rules.py
```

输出：
```
=== Signing own-source subscription files ===
  ✓ adt-base.txt: signature=True checksum=True (3QjuKP782CzJFwi5L1yckA)
  ✓ adt-hot.txt: signature=True checksum=True (DIbHaOc8+O9xX//SPEf6qg)
  ✓ adt-dev.txt: signature=True checksum=True (OjYAJVxpKU+lYUnAQVumZw)
  ✓ adt-video.txt: signature=True checksum=True (osS1yR4lqvaKxQjMD5dS0Q)
  ✓ adt-web.txt: signature=True checksum=True (qZURcFMKs59y1Vr3e+22qg)
Done!
```

### 手动更新版本和 Checksum

```bash
python3 update_md5.py
```

### 密钥管理

```bash
# 生成新密钥对（如需更换）
openssl genrsa -out rsa-private-key.pem 2048
openssl rsa -in rsa-private-key.pem -pubout -out rsa-public-key.pem
```

> ⚠️ `rsa-private-key.pem` 已加入 `.gitignore`，不会提交到仓库。

## 文档

| 文档 | 说明 |
|------|------|
| [docs/checksum-signature.md](docs/checksum-signature.md) | ABP Checksum 与 RSA-Signature 算法全解析 |
| [docs/rule-examples.md](docs/rule-examples.md) | ABP 规则语法示例 |
| [docs/baidu_ads_js.src.md](docs/baidu_ads_js.src.md) | 百度广告过滤 JS 脚本源码 |
| [adbyby/ADByBy_语法手册.md](adbyby/ADByBy_语法手册.md) | AdByBy 规则语法手册 |

## License

See [LICENSE](LICENSE).
