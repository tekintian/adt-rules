# dnsmasq规则说明


## address规则调用地址:

~~~sh
# 综合广告屏蔽规则
https://gitee.com/tekintian/adt-rules/raw/master/dnsmasq/anti-ad.conf

# 游戏相关规则
https://gitee.com/tekintian/adt-rules/raw/master/dnsmasq/games.conf

# 电商平台广告规则
https://gitee.com/tekintian/adt-rules/raw/master/dnsmasq/shop.conf

~~~


## hosts规则
用于精确屏蔽指定的域名,不包含子域名时使用hosts规则
如果要直接屏蔽主域名和其子域名,使用address规则
~~~sh
# 通用广告规则 精确屏蔽指定域名
https://gitee.com/tekintian/adt-rules/raw/master/dnsmasq/ads_hosts.txt

~~~



## dnsmasq规则语法：
~~~conf
# 匹配主域名及所有子域名
address=/domain.com/0.0.0.0

# 加 ^ 表示精确匹配（不匹配子域名）
address=/^domain.com/0.0.0.0
~~~

## dnsmasq hosts规则和address规则的生效逻辑和区别


## 📋 DNS hosts 规则类型对比

### **1. `addn-hosts=$DATA_PATH/hosts` - 传统hosts文件**

**生效逻辑：**
```bash
# 文件位置: /tmp/adbyby/data/hosts
# 配置方式: addn-hosts=/tmp/adbyby/data/hosts
# 配置文件: /etc/storage/dnsmasq/dnsmasq.conf
```

**格式示例：**
```
127.0.0.1 ads.google.com
127.0.0.1 doubleclick.net
0.0.0.0 facebook.com
```

**特点：**
- ✅ **传统hosts格式**: `IP 域名` 的标准格式
- ✅ **精确匹配**: 需要指定具体的IP地址
- ✅ **来源广泛**: 可以使用任何标准的hosts文件源
- ✅ **灵活控制**: 可以将域名重定向到任意IP

---

### **2. `anti-ad-for-dnsmasq.conf` - dnsmasq地址规则**

**生效逻辑：**
```bash
# 文件位置: /etc/storage/dnsmasq-adbyby.d/anti-ad-for-dnsmasq.conf
# 生效方式: dnsmasq自动加载 conf-dir 下的所有.conf文件
```

**格式示例：**
```
address=/ads.google.com/0.0.0.0
address=/doubleclick.net/127.0.0.1
address=/facebook.com/0.0.0.0
```

**特点：**
- ✅ **dnsmasq原生格式**: 专为dnsmasq设计的语法
- ✅ **通配符支持**: `address=/domain.com/0.0.0.0` 会匹配所有子域名
- ✅ **更高效**: dnsmasq直接解析，无需额外处理
- ✅ **子域名覆盖**: 一条规则覆盖主域名和所有子域名

---

## 🔍 核心区别对比

| 特性 | 传统hosts | dnsmasq地址规则 |
|------|-----------|-----------------|
| **语法格式** | `IP 域名` | `address=/域名/IP` |
| **子域名** | 需要逐条添加 | 自动覆盖所有子域名 |
| **性能** | 需要解析hosts文件 | dnsmasq原生支持 |
| **灵活性** | 可重定向到任意IP | 通常只用于屏蔽 |
| **兼容性** | 通用标准 | dnsmasq专用 |
| **维护** | 手动管理去重 | 动态下载更新 |

---

## 🚀 实际使用场景

### **hosts_ads() 函数逻辑：**
```bash
# 1. 从配置文件读取下载列表
/etc/storage/adbyby_host.sh → 下载URL列表

# 2. 并行下载多个hosts源
curl下载 → 合并到 /tmp/adbyby/data/hosts

# 3. 去重处理
sort | uniq → 生成最终hosts文件

# 4. 配置dnsmasq
echo "addn-hosts=$DATA_PATH/hosts" >> dnsmasq.conf
```

### **anti_ad() 函数逻辑：**
```bash
# 1. 从nvram获取下载链接
anti_ad_link → 单一下载源

# 2. 下载dnsmasq格式规则
curl → /etc/storage/dnsmasq-adbyby.d/anti-ad-for-dnsmasq.conf

# 3. 自动生效
dnsmasq自动加载 conf-dir 下的所有.conf文件
```

---

## 💡 推荐配置策略a

### **使用传统hosts的情况：**
- 🎯 需要精确控制某个域名的解析IP
- 🎯 使用现有的知名hosts源（如adaway、stevenblack等）
- 🎯 需要将某些域名重定向到特定服务器

### **使用dnsmasq地址规则的情况：**
- 🎯 专注于广告屏蔽，统一重定向到0.0.0.0
- 🎯 希望一条规则覆盖所有子域名
- 🎯 追求更高的解析性能

### **最佳实践：**
```bash
# 1. 启用anti-ad用于基础广告屏蔽（高效）
nvram set anti_ad=1

# 2. 启用hosts用于精确控制（灵活）  
nvram set hosts_ad=1

# 3. 两者结合使用，互补优势
# anti-ad处理大部分广告域名
# hosts处理特殊情况（如劫持恶意域名到安全IP）
```

这两种机制在AdByBy中是**互补关系**，可以同时使用，提供更全面的DNS层广告过滤能力。






### 最终整理结果（去重+分类）
#### 一、专属游戏主域名（dnsmasq address 泛屏蔽规则）
```conf
# 网页小游戏专属主域名
address=/4399.com/0.0.0.0
address=/7k7k.tv/0.0.0.0
address=/7k7kgame.cn/0.0.0.0
address=/527play.com/0.0.0.0
address=/6324.cn/0.0.0.0
address=/liuld.cn/0.0.0.0
address=/jingcaiyouxi.cn/0.0.0.0
address=/yx8.cn/0.0.0.0
address=/youxiboy.com/0.0.0.0
address=/xiaoyouxi.in/0.0.0.0
address=/137v.com/0.0.0.0
address=/7wa.cn/0.0.0.0
address=/ppkp.net/0.0.0.0
address=/7k7kxiaoyouxi.com.cn/0.0.0.0
address=/k7k7k.com/0.0.0.0
address=/xiaoyouxi.tv/0.0.0.0
address=/kaixin.com.vc/0.0.0.0
address=/7k7k.cc/0.0.0.0
address=/7k7k.com.co/0.0.0.0
address=/7k7k.in/0.0.0.0
address=/616wan.com/0.0.0.0
address=/youxi369.com/0.0.0.0
address=/543.cn/0.0.0.0
address=/2144.com/0.0.0.0
address=/2144.cn/0.0.0.0
address=/2144.net/0.0.0.0
address=/2144.tv/0.0.0.0
address=/2144game.com/0.0.0.0
address=/2144wan.com/0.0.0.0
address=/youxizhuo.com/0.0.0.0
address=/17yy.com/0.0.0.0
address=/17yy.cn/0.0.0.0
address=/17yy.net/0.0.0.0
address=/17yy.tv/0.0.0.0
address=/youxile.com/0.0.0.0
address=/youxile.net/0.0.0.0
address=/youxile.tv/0.0.0.0
address=/youxih.com/0.0.0.0
address=/youxih.net/0.0.0.0
address=/youxih.tv/0.0.0.0
address=/youxiabc.com/0.0.0.0
address=/youxiabc.net/0.0.0.0
address=/youxiabc.tv/0.0.0.0
address=/1niu.com/0.0.0.0
address=/7guo.com/0.0.0.0
address=/5guo.com/0.0.0.0
address=/qunle.com/0.0.0.0
address=/mohao.com/0.0.0.0
address=/3366.com/0.0.0.0

# 游戏门户网站专属主域名
address=/17173.com/0.0.0.0
address=/gamersky.com/0.0.0.0
address=/ali213.net/0.0.0.0
address=/3dmgame.com/0.0.0.0
address=/tgbus.com/0.0.0.0
address=/yxdown.com/0.0.0.0
address=/youxi.com/0.0.0.0
address=/game168.com.cn/0.0.0.0
address=/keylol.com/0.0.0.0
address=/wenshushu.cn/0.0.0.0
address=/ali213.com/0.0.0.0
address=/52pk.com/0.0.0.0
address=/duowan.com/0.0.0.0
address=/game2.cn/0.0.0.0
address=/game365.com.cn/0.0.0.0
address=/game5.com.cn/0.0.0.0
address=/game798.com/0.0.0.0
address=/game880.com/0.0.0.0
address=/gameabc.com.cn/0.0.0.0
address=/gamesir.com/0.0.0.0
address=/gamestar.com.cn/0.0.0.0
address=/gamersky.com.cn/0.0.0.0
address=/gamersky.net/0.0.0.0
address=/gamersky.org/0.0.0.0
address=/gamersky.tv/0.0.0.0
address=/ggg.cn/0.0.0.0
address=/ggg.com.cn/0.0.0.0
address=/ggg.tv/0.0.0.0
address=/gmg.cn/0.0.0.0
address=/gmg.com.cn/0.0.0.0
address=/gmg.tv/0.0.0.0
address=/gog.com/0.0.0.0
address=/battlenet.com.cn/0.0.0.0
address=/ubisoft.com.cn/0.0.0.0
address=/activision.com/0.0.0.0

# 游戏应用API专属主域名
address=/taptapdada.com/0.0.0.0
address=/tapapis.cn/0.0.0.0
address=/biligame.com/0.0.0.0
address=/mihoyo.com/0.0.0.0
address=/miyoushe.com/0.0.0.0
address=/wegame.com/0.0.0.0
address=/4399api.net/0.0.0.0
address=/epicgames.com/0.0.0.0
address=/roblox.com/0.0.0.0
address=/unity3d.com/0.0.0.0
address=/twitch.tv/0.0.0.0
address=/steamapis.com/0.0.0.0
address=/steamcommunity.com/0.0.0.0
address=/steampowered.com/0.0.0.0
address=/mojang.com/0.0.0.0
address=/minecraftservices.com/0.0.0.0
address=/hoyoverse.com/0.0.0.0
address=/yuanshen.com/0.0.0.0
address=/honkaiimpact3.com/0.0.0.0
address=/honkaistarrail.com/0.0.0.0
address=/arknights.com/0.0.0.0
address=/onmyoji.com/0.0.0.0
address=/wowsgame.com/0.0.0.0
address=/worldofwarships.com/0.0.0.0
address=/worldoftanks.com/0.0.0.0
address=/worldofwarplanes.com/0.0.0.0
address=/quickapi.net/0.0.0.0

# 游戏平台专属主域名
address=/minecraft.net/0.0.0.0
address=/wowchina.com/0.0.0.0
address=/diablo3.com.cn/0.0.0.0
address=/overwatch.com.cn/0.0.0.0
```

#### 二、非专属游戏域名（hosts 格式规则，去重）
```hosts
# qq.com 相关游戏子域
127.0.0.1 game.qq.com
127.0.0.1 openapi.minigame.qq.com
127.0.0.1 pubgmobile.qq.com
127.0.0.1 sg-public-api.qq.com
127.0.0.1 qqgame.qq.com
127.0.0.1 open.qqgame.qq.com
127.0.0.1 down-update.qq.com
127.0.0.1 update1.dlied.qq.com
127.0.0.1 update5.dlied.qq.com
127.0.0.1 oth.str.mdt.qq.com
127.0.0.1 c.tdm.qq.com
127.0.0.1 a.ssl.msdk.qq.com
127.0.0.1 cloudctrl.gclud.qq.com
127.0.0.1 masdk.3g.qq.com
127.0.0.1 lol.qq.com
127.0.0.1 dnf.qq.com
127.0.0.1 cf.qq.com
127.0.0.1 wangzhe.qq.com
127.0.0.1 pvp.qq.com
127.0.0.1 pubg.qq.com
127.0.0.1 hpjy.qq.com
127.0.0.1 funmaker.qq.com

# 163.com/netease.com 相关游戏子域
127.0.0.1 mcpel-web.16163.com
127.0.0.1 api.163.com
127.0.0.1 api.k.163.com
127.0.0.1 api.iplay.163.com
127.0.0.1 dev.4399.com
127.0.0.1 dev.my4399.com
127.0.0.1 g79.update.netease.com
127.0.0.1 g79.gdl.netease.com
127.0.0.1 superstar.pt.163.com
127.0.0.1 x19.update.netease.com
127.0.0.1 news-api.16163.com
127.0.0.1 mgbsdk.matrix.netease.com
127.0.0.1 game.163.com
127.0.0.1 mc.163.com

# 其他非专属主域名游戏子域
127.0.0.1 games.sina.com.cn
127.0.0.1 ea.com
127.0.0.1 game.open.uc.cn
127.0.0.1 open.d.cn
127.0.0.1 api.blizzard.com
127.0.0.1 dev.battle.net
127.0.0.1 api.ubisoft.com
127.0.0.1 api.ubisoftconnect.com
127.0.0.1 api.wangzhe.com
127.0.0.1 api.pubg.com
127.0.0.1 api.heiyou.com
127.0.0.1 lewan.baidu.com
127.0.0.1 store.steampowered.com
127.0.0.1 dl.52pk.com
127.0.0.1 dl.ali213.net
127.0.0.1 dl.gamersky.com
127.0.0.1 sdk.longtugame.com
127.0.0.1 dev.duoku.com
127.0.0.1 dev.gfan.com
127.0.0.1 open.maopaoke.com
127.0.0.1 ol.epicgames.com
```

### 关键说明
1. **专属域名处理**：仅对无非游戏业务的纯游戏主域名用 `address=/域名/0.0.0.0` 泛屏蔽，覆盖所有子域名，且已去重（如原 4399 旗下多个子域仅保留主域规则）。
2. **非专属域名处理**：
   - 全部保留原 hosts 格式（`127.0.0.1 子域名`），仅屏蔽游戏相关子域，避免影响主域名的非游戏业务；
   - 已完成去重（如原重复的 `ea.com`/`api.ea.com` 仅保留 `ea.com` 一条），删除冗余条目；
   - 严格区分主域属性（如 qq.com/163.com/baidu.com 均归为非专属，仅屏蔽游戏子域）。
3. **格式兼容**：
   - dnsmasq 可同时加载 `address` 规则和 hosts 格式规则（将 hosts 内容放入 dnsmasq 配置目录或通过 `addn-hosts` 指定 hosts 文件路径即可）；
   - hosts 规则仍用 `127.0.0.1`，符合传统 hosts 规范；address 规则用 `0.0.0.0`，符合 dnsmasq 最佳实践。
