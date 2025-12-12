# 📋 AdByBy第三方规则使用说明

AdByBy第三方规则支持的格式和机制分析

## 🏗️ **双层架构设计**

AdByBy采用**Shell脚本+C程序**的双层架构：

### 1. **Shell脚本层** (`adbyby.sh`) - 规则获取与预处理
- 下载第三方规则源
- 格式转换和过滤  
- 合并到最终规则文件

### 2. **C程序层** (`rules.c`) - 规则加载与执行
- 将预处理后的规则加载到内存
- 高性能模式匹配引擎
- 实时统计和拦截

---

## 🔧 **规则处理流程**

### Shell层预处理 (行532-549)
```bash
# 下载第三方规则
curl -k -s -o /tmp/adbyby/user2.txt --connect-timeout 5 --retry 3 $rules_address

# 过滤有效规则格式
grep -v '^!' /tmp/adbyby/user2.txt | \
grep -E '^(@@\||\||[[:alnum:]])' | \
sort -u | \
grep -v "^$" >> $DATA_PATH/user3adblocks.txt

# 合并到最终规则文件
grep -v '^!' $DATA_PATH/user3adblocks.txt | grep -v "^$" >> $DATA_PATH/user.txt
```

### C层规则加载 (`rules.c:177-210`)
```c
// 解析规则格式: pattern|type|description
char* pipe1 = strchr(line, '|');
if (pipe1) {
    *pipe1 = '\0';
    strncpy(pattern, line, sizeof(pattern) - 1);
    
    char* pipe2 = strchr(pipe1 + 1, '|');
    if (pipe2) {
        *pipe2 = '\0';
        strncpy(type_str, pipe1 + 1, sizeof(type_str) - 1);
        strncpy(description, pipe2 + 1, sizeof(description) - 1);
    }
}
```

---

## ✅ **支持的规则格式详解**

### 1. **排除规则格式** (`@@||`) - 优先级最高
```bash
@@||127.0.*              # 排除本地IP段
@@||192.168.*            # 排除内网IP段  
@@||10.0.*               # 排除内网IP段
@@||bootcss.com/*        # 排除CDN域名
@@||jsdelivr.net/*       # 排除CDN域名
```

**C层处理逻辑**：
```c
// 排除规则具有最高优先级
if (pattern[0] == '@' && pattern[1] == '@') {
    // 白名单处理逻辑
    return 0; // 允许通过
}
```

### 2. **域名拦截格式** (`||`) - 精确域名匹配
```bash
||googleads.g.doubleclick.net^    # 拦截Google广告域名
||googlesyndication.com^         # 拦截Google联盟
||doubleclick.net^                # 拦截DoubleClick
||adsystem.google.com^           # 拦截Google广告系统
```

**C层处理** (`RULE_TYPE_DOMAIN`)：
```c
case RULE_TYPE_DOMAIN:
    // 检查域名匹配
    if (strcmp(text, pattern) == 0) return 1;
    if (ends_with(text, pattern)) {
        int text_len = strlen(text);
        int pattern_len = strlen(pattern);
        if (text_len > pattern_len && text[text_len - pattern_len - 1] == '.') {
            return 1; // 子域名匹配
        }
    }
    return 0;
```

### 3. **精确匹配格式** (`|`) - URL精确匹配
```bash
|http://ads.example.com/banner.jpg     # 精确匹配URL
|https://tracker.example.com/collect   # 精确匹配HTTPS URL
```

### 4. **基础域名/IP格式** - 简单字符串匹配
```bash
example.com                    # 域名匹配
ads.example.com               # 子域名匹配  
192.168.1.100                # IP地址匹配
```

**C层处理** (`RULE_TYPE_SIMPLE`)：
```c
case RULE_TYPE_SIMPLE:
    return strstr(text, pattern) != NULL;
```

### 5. **通配符格式** (`*`) - 高级模式匹配
```bash
*ads*                         # 包含"ads"的URL
*/banner*                     # 包含"banner"的路径
*.doubleclick.net/*           # DoubleClick子域匹配
```

**C层处理** (`RULE_TYPE_WILDCARD`)：
```c
case RULE_TYPE_WILDCARD: {
    // 通配符转正则表达式
    char* regex_pattern = malloc(strlen(pattern) * 2 + 3);
    // 转换逻辑: * -> .*
    // 边界处理: ^...$
    regex_t regex;
    int result = regcomp(&regex, regex_pattern, REG_EXTENDED | REG_NOSUB);
    result = regexec(&regex, text, 0, NULL, 0);
    return result == 0;
}
```

### 6. **高级规则格式** (`pattern|type|description`)
```c
// 完整格式示例
doubleclick.net|2|Google广告平台域名
*/banner*|4|通用横幅广告模式
|http://tracker.example.com/*|3|精确跟踪URL拦截
```

**规则类型定义** (`rules.h`)：
```c
typedef enum {
    RULE_TYPE_SIMPLE = 0,  // 简单字符串匹配
    RULE_TYPE_REGEX = 1,    // 正则表达式
    RULE_TYPE_DOMAIN = 2,   // 域名匹配
    RULE_TYPE_URL = 3,      // URL匹配
    RULE_TYPE_WILDCARD = 4  // 通配符匹配
} rule_type_t;
```

---

## 🎯 **规则匹配引擎**

### 匹配优先级 (`rules.c:327-361`)
```c
int rule_manager_is_blocked(rule_manager_t* rm, const char* url, const char* host) {
    for (int i = 0; i < rm->count; i++) {
        ad_rule_t* rule = &rm->rules[i];
        if (!rule->enabled) continue;
        
        int matched = 0;
        
        if (rule->type == RULE_TYPE_DOMAIN) {
            // 优先匹配域名
            if (host && rule_manager_match_pattern(host, rule->pattern, rule->type)) {
                matched = 1;
            }
        } else if (rule->type == RULE_TYPE_URL) {
            // 其次匹配URL
            if (url && rule_manager_match_pattern(url, rule->pattern, rule->type)) {
                matched = 1;
            }
        } else {
            // 最后通用匹配
            if (url && rule_manager_match_pattern(url, rule->pattern, rule->type)) {
                matched = 1;
            } else if (host && rule_manager_match_pattern(host, rule->pattern, rule->type)) {
                matched = 1;
            }
        }
        
        if (matched) {
            rule->hit_count++;  // 统计命中次数
            return 1;  // 拦截请求
        }
    }
    return 0;  // 允许通过
}
```

---

## 📝 **完整配置示例**

### 1. **Web界面配置**
```bash
# 规则1 - 主要广告拦截
nvram set adbybyrules_x0="https://gitee.com/tekintian/adt-rules/raw/master/adbyby/adblock.txt"
nvram set adbybyrules_road_x0="1"

# 规则2 - 视频广告拦截  
nvram set adbybyrules_x1="https://gitee.com/tekintian/adt-rules/raw/master/adbyby/video.txt"
nvram set adbybyrules_road_x1="1"

# 规则3 - 自定义规则
nvram set adbybyrules_x2="https://example.com/custom-adbyby-rules.txt"
nvram set adbybyrules_road_x2="1"

# 规则数量
nvram set adbybyrules_staticnum_x="3"

# 启用第三方规则
nvram set adbyby_rules_x="1"
```

### 2. **第三方规则文件示例**
```txt
! ====== 广告拦截规则示例 ======
! 规则格式: pattern|type|description

! 高级格式 - 精确控制
googleads.g.doubleclick.net|2|Google广告系统域名
googlesyndication.com|2|Google联盟
doubleclick.net|2|DoubleClick广告平台

! 高级格式 - 通配符匹配
*/banner*|4|通用横幅广告
*/advertisement*|4|广告路径
*/popup*|4|弹窗广告

! 高级格式 - 精确URL
|http://ads.example.com/banner.jpg|3|精确广告图片
|https://tracker.example.com/collect|3|跟踪器URL

! 传统格式 - 简单匹配
facebook.com/tr
connect.facebook.net
ads.example.com
tracker.example.org

! 排除规则 - 白名单
@@||whitelist-site.com/*
@@||essential-cdn.net/*
@@||127.0.*
@@||192.168.*
```

### 3. **规则统计和监控**
```c
// C层提供统计功能
void rule_manager_get_stats(rule_manager_t* rm, int* total_rules, int* enabled_rules, int* total_hits);

// 状态页面显示
// 总规则数: 1250
// 启用规则数: 1198  
// 命中次数: 5421
```

---

## ⚡ **性能优化特性**

### 1. **内存管理**
```c
// 动态扩容机制
if (rm->count >= rm->capacity) {
    int new_capacity = rm->capacity * 2;
    ad_rule_t* new_rules = realloc(rm->rules, sizeof(ad_rule_t) * new_capacity);
    rm->rules = new_rules;
    rm->capacity = new_capacity;
}
```

### 2. **高效匹配**
- 域名匹配优先级最高
- 正则表达式缓存
- 早期退出机制

### 3. **统计追踪**
```c
rule->hit_count++;  // 每次匹配自动计数
log_message(LOG_DEBUG, "Blocked by rule: %s (hits: %d)", rule->pattern, rule->hit_count);
```

---

## 🎯 **最佳实践建议**

1. **规则组织**：按功能分类（广告、跟踪、恶意软件）
2. **性能优化**：优先使用简单格式，避免过度使用正则表达式
3. **维护更新**：定期更新规则源，确保过滤效果
4. **监控统计**：关注命中次数，调整规则优先级

这个双层架构设计既保证了规则的灵活性，又确保了运行时的高性能，是AdByBy能够高效处理大量规则的关键所在。

