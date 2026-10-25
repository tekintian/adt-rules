
匹配超过100个字符的行
^.{101,}$


匹配连续空行
^\s*$(\r\n|\n|\r)\s*$(\r\n|\n|\r)\s*$


匹配所有非特定字符  scriptlet(  的行 正则
^(?!.*scriptlet\().*$

**原理说明：**
- `^` — 定位到行首
- `(?!.*scriptlet\()` — **负向前瞻**：整行任何位置都不能出现 `scriptlet(`（注意 `(` 是特殊字符，必须转义为 `\(`）
- `.*$` — 匹配整行剩余内容

## 各工具具体用法

**1. VS Code / Notepad++（查找替换，删除时建议带上换行符）**

查找（开启正则模式）：
```regex
^(?!.*scriptlet\().*\R
```



提取包含指定字符的数据

grep 'baidu.com' tmp/all_rules_clean.txt > tmp/baidu_rules.txt
grep 'qq.com' tmp/all_rules_clean.txt > tmp/qq_rules.txt
grep 'alimama' tmp/all_rules_clean.txt > tmp/alimama_rules.txt

grep 'tmall' tmp/all_rules_clean.txt > tmp/tmall_rules.txt


grep 'mediav' tmp/all_rules_clean.txt > tmp/mediav_rules.txt


grep 'alicdn' tmp/all_rules_clean.txt > tmp/alicdn_rules.txt








