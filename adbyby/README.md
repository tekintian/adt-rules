# adbyby-open 开源广告过滤系统规则

路由器adbyby里面用的规则,和主项目的规则是通用的


下面2个规则为adbyby-open系统内置的默认规则
~~~sh
# adt-base.txt
https://gitee.com/tekintian/adt-rules/raw/master/adbyby/lazy.txt
# adt-video.txt
https://gitee.com/tekintian/adt-rules/raw/master/adbyby/video.txt
~~~


## 规则语法和技术说明文档参考

[ADByBy_语法手册.md](./ADByBy_语法手册.md)



[AdByBy第三方规则使用说明.md](./AdByBy第三方规则使用说明.md)



## dnsmasq规则

详情参考 https://gitee.com/tekintian/adt-rules/tree/master/dnsmasq



adbyby默认加载的dnsmasq规则地址:
https://gitee.com/tekintian/adt-rules/raw/master/dnsmasq/anti-ad.conf


这个是anti-ad的默认规则
https://anti-ad.net/anti-ad-for-dnsmasq.conf
内容有点多,不适合国内用户使用!



## adbyby open可以添加的第三方规则示例:
~~~sh
# 热门广告规则
https://gitee.com/tekintian/adt-rules/raw/master/adt-hot.txt
# 开发人员用的规则
https://gitee.com/tekintian/adt-rules/raw/master/adt-dev.txt

#hosts规则:
https://gitee.com/tekintian/adt-rules/raw/master/hosts/ads_hosts.txt
https://gitee.com/tekintian/adt-rules/raw/master/hosts/stats_hosts.txt

# adaway规则这个太大8w多条 内存小不推荐
https://gitee.com/tekintian/adt-rules/raw/master/hosts/adaway_hosts.txt

~~~


## adbyby示例 rules.txt

/tmp/adbyby/data/rules.txt 示例规则
~~~txt
# AdByBy-Open Rules File
# Format: pattern|type|description
# Types: 0=simple, 1=regex, 2=domain, 3=url, 4=wildcard

# 内置广告域名（程序会自动加载）
# 以下是自定义规则示例

# 常见广告域名
doubleclick.net|2|Google DoubleClick
googleadservices.com|2|Google Ads
googlesyndication.com|2|Google Syndication
google-analytics.com|2|Google Analytics
googletagmanager.com|2|Google Tag Manager

# 社交媒体跟踪
facebook.com/tr|0|Facebook Tracking
connect.facebook.net|2|Facebook Connect

# 其他广告网络
amazon-adsystem.com|2|Amazon Ads
taboola.com|2|Taboola
outbrain.com|2|Outbrain

# 通用广告路径模式
*/ad/*|4|广告路径
*/ads/*|4|广告路径
*/advertisement/*|4|广告页面
*/banner/*|4|横幅广告
*/popup/*|4|弹窗广告

# 跟踪和分析
*analytics*|0|分析服务
*tracking*|0|跟踪服务
*beacon*|0|信标跟踪
*pixel*|0|像素跟踪
~~~


