
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

查找不包含scriptlet(的行
```regex
^(?!.*scriptlet\().*\R
```


VSCODE里面查找所有包含scriptlet的行, 注意vscode里面不支持 \R
^(?=.*scriptlet).*\n



# 反向思路：不删，而是直接提取包含 scriptlet( 的行到新文件
grep 'scriptlet(' 原文件.txt > 结果.txt


# 反向思路：不删，而是直接提取包含 scriptlet( 的行到新文件
grep 'yts' tmp/all_rules_clean.txt > tmp/yts_rules.txt


提取包含指定字符的数据

grep 'js(' tmp/all_rules_clean.txt > tmp/js_rules.txt

grep 'baidu.com' tmp/all_rules_clean.txt > tmp/baidu_rules.txt
grep 'qq.com' tmp/all_rules_clean.txt > tmp/qq_rules.txt
grep 'alimama' tmp/all_rules_clean.txt > tmp/alimama_rules.txt

grep 'tmall' tmp/all_rules_clean.txt > tmp/tmall_rules.txt


grep 'mediav' tmp/all_rules_clean.txt > tmp/mediav_rules.txt


grep 'alicdn' tmp/all_rules_clean.txt > tmp/alicdn_rules.txt








