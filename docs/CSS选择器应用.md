

# CSS选择器

只有当某个独立单词完全等于指定值时才匹配
[attr~="value"]

匹配值必须完全等于指定值，或以指定值开头后跟连字符
[attr|="value"]


[attr^="value"]  /* 前缀匹配 */
[attr$="value"]  /* 后缀匹配 */


完全不考虑单词边界，只要字符串中包含指定子串就匹配
[attr*="value"]






SEPARATOR_TIER_A 里面的词应用以下匹配, 任意一个匹配就生成规则, 

以下使用ad示例

数字0-5: *="W1/2/3/4/5" 纯子串


ad ad- 完整或后接连接词

##[class|="ad" i]
##[id|="ad" i]

-ad  匹配结尾
[class$="-ad" i]
[id$="-ad" i]

_ad  匹配结尾
[class$="_ad" i]
[id$="_ad" i]

ad_ 匹配开头

[class^="ad_" i]
[id^="ad_" i]

_ad_ 任意匹配
[class*="_ad_" i]
[id*="_ad_" i]

-ad- 任意匹配
[class*="-ad-" i]
[id*="-ad-" i]


特例
所有以 ads开头的
[class^="ads" i]
[id^="ads" i]

所有以 Ads  Ad Adv Advert结尾的
[class$="Ad"]
[id$="Ad"]
[class$="Ads"]
[id$="Ads"]






GLUED_TIER_A 里面的词  任意匹配即生成规则
>=7 的词全部应用 *=
如:
[class*="xxxxxxx" i]
[id*="xxxxxxx" i]


5-6的词应用   ^="W" i, *="-W" i, *="_W" i,
[class^="xxxxx" i]
[id^="xxxxx" i]

[class*="_xxxxx" i]
[id*="_xxxxx" i]

[class*="-xxxxx" i]
[id*="-xxxxx" i]



3-4的词应用
[class|="xxx" i]
[id|="xxx" i]

[class^="xxx_" i]
[id^="xxx_" i]

[class$="_xxx" i]
[id$="_xxx" i]

[class$="-xxx" i]
[id$="-xxx" i]






GLUED_TIER_A 里面的常量太长了, 按照  GLUED_LONG  GLUED_MID   GLUED_SHORT  分为各常量段, 同时分别在每段加上该段的完整匹配模式和生成规则注释示例




###HMcoupletDivleft
###HMimageleft
###HMimageright
###HMRichBox










