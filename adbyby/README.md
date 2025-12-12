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



