# ABP 规则语法示例

> 本文档记录 AdClear 规则库中常用的 ABP 规则语法示例，供规则编写参考。

## 样式规则（Element Hiding）

隐藏页面中匹配 CSS 选择器的元素：

```abp
##.broadcastMe[style="width: 1200px;"]
##.btn.btn-default.hotwords[target="_blank"]
##.con_search + #carousel-example-generic[style^="max-width: 1170px;"]
##.content > a > .topline
##.content-video > .ads
##.his-sign-cont[data-dysign-adid]
##.listok > a > img[src*=".alicdn.com"][width="980"][height="80"]
##.listok > a > img[style^="width:980px;height:"]
##.main-ad-r + .topad
##.main[style="border:#7D8C8E solid 1px;height: 23px;"]
##.maomi-content > .section-banner
##.mod + #bottomBox
##.my-cat.my-cat-header
##.mylist > a[target="_bank"] > img[src*=".alicdn.com/"]
##.spon-img[src*=".alicdn."]
##.subject_link[href$="/thread-index-fid-1-tid-12848.htm"]
##.sxAdBox
##.t5[style="border:1px solid #a6cbe7;"] + .t[style="margin-top:8px"]
##.top_box > li > a[href^="/js/app.htm?"]
##.wordurl[style="   width: 42%; float:left; text-align: center;"]
```

## ID 选择器规则

```abp
###menu + script + #topBox
###results.content-main > .eLeft
###rightCouple
###rightCouple + #leftFloat
###search > a[href="/top1.html"]
###snActive-wrap
###sponsorAdDiv2
###swtleft[style^="position:fixed;"]
###table1[width="468"][height="50"]
###top_box > a[onclick^="javascript"]
###wp > .V-video-floats
###j-new-ad
###toptb + div[align="center"]
##body .has-ad
##body[class|="view"] > .ad-box
##body[onload*="u()"] > #x
##center > a[target="_blank"] > img[style="padding- bottom:5px;width:960px;height:120px;"]
##center > a[target="_blank"] > img[style="padding- bottom:5px;width:960px;height:60px;"]
##div#ad_id
##div#xinxi
##div[id^="ad_thread"]
##form + .div-search-box.col-lg-offset-2.col-lg-8 > a[target="_blank"]
##img[data-link][data-src*="/u/"]:not([data-link*="/i/"])
##img[data-src*=".alicdn.com/img/ibank/"][src="/static/images/loadingerror.gif"]
##img[src$="/img/tianbo.gif"]
##img[src*=".qpic.cn"][width="980"][height="80"]
##img[src*=".sinaimg."][style="width:1025px;height:80px"]
##img[src*=".sinaimg."][style="width:150px;height:300px"]
##script + #coupletBox
##script + #rbbox
##script[src="/js/sy2.js"] + div[align="center"]
```

### 复杂选择器

```abp
##div:not([id]):not([class]):not([style]) > div:not([id]):not([class]):not([style]) > iframe[scrolling="no"][src*="//"][src*="?"][src*="="][src*="&"][width][height][frameborder="0"]:not([src^="http://www.facebook.com/"])
##div[style^="width: 100%;"][style$="margin: 0px;"] iframe[scrolling="no"][src*="//"][src*="?"][src*="="][src*="&"][width][height][frameborder="0"]
##div[style^="width: 100%;"]:not([id]):not([class]) > iframe[scrolling="no"][src^="http"][src*="?"][src*="="][src*="&"][width][height][frameborder="0"]:not([allowfullscreen])
```

## 标签选择规则

```abp
##a[href*=".com/?p="][target="_blank"] > img[src$=".gif"]
##a[href*=".ahhxwavi.cn"]
##a[href*=".bayiyy.com/download."]
##a[href*=".yb2843.vip"]
##a[href*=".yyk2.com/"]
##a[href*="/602034.com"]
##a[href^="https://luolidao.vip/"]
##a[onclick^="javascript:pc_"] > img[src*=".alicdn.com"]
##a[style="display:inline-block;font-weight:bold;color:#f00;border:1px solid #f00;border-radius:15px;padding:2px 5px 2px 5px;margin:5px 5px 5px 0px;"]
```

## URI 规则

```abp
/adsbygoogle.js$script,match-case
/advertising.js$script,match-case
/ads.js$script,match-case
/pagead/show_ads.js
/s3m.mediav.com/galileo/*.mp4
/104_150/1360_1|
/1linbAte_mplatk/*
/common/cf/*$image,object,domain=~bingfeng.tw|~dahuaiji.com
/content.php?id=148&type=g|$xmlhttprequest
/content/plugins/em_ad/*
/duilian.$domain=~388g.com|~msra.cn|~supfree.net
```

### 正则 URI 规则

```abp
/\.(?:com|com\.cn|cn|cc|net|org|me|tv)\/[0-9a-z]{9,}\.js/$script,domain=023up.com|2345.com
/\.js\?[a-z]+=[a-z]+$/$script,domain=china.cn|eastday.com|fangdaijisuanqi.com
/images/*.gif$domain=2c2.website|2p8.space|adultgao.com
```

## 域名规则

```abp
|http://*.cn/ad/
|http://*.hk/ad/$domain=~sunmobile.com.hk
|http://*.in/ad/
|http://*.me/ad/
|http://*.tw/ad/$domain=~ruten.com.tw
|http://*.us/ad/
|http://*/ad.*.js?v=*&sp=
|http://*/ad.js?sn=
|http://*/ad.js?v=$domain=~mgc.qq.com
||219.153.41.175/*.js
||221.5.69.52^*.js
||222.47.26.21/m.js
://*.tv/ad/$domain=~moviedj.tv
://*/gg/$domain=~11185.cn|~chinatax.gov.cn|~dydog.org|~fanfou.com|~gg1z.com|~ha47.cn|~i-moe.eu.org|~jszwfw.gov.cn|~usr.cn|~xzdj.cn
:1314/jiucao/
:8888/mb1/wap_
:8888/zhu/pc_
:8888/zhu/wap_
:8898/ads_
:99/js/ads/
=ad_top_slider&
||coin-hive.com/lib/coinhive.min.js
||static.doubleclick.net/instream/ad_status.js
||pagead2.googlesyndication.com/pagead/js/adsbygoogle.js
||googletagservices.com/tag/js/gpt.js
```

## 例外规则（Whitelist）

```abp
@@||192.168.*.1/$generichide
@@||199it.com^$generichide
@@||360buyimg.com/ad/$domain=jd.com
@@||360buyimg.com/ads/$domain=jd.com
@@/pic/ad/*$domain=ybjk.com
@@/pub/ad/*$domain=ruten.com.tw
@@/image/ad/*$domain=gashpoint.com
@@/images/ad/*$domain=9588.com|casio.com.cn|dod-tec.com|ourgame.com|pro-partner.com.tw|snh48.com|tingbook.com
@@/images/adv/*$domain=gueizu.com|topfilex.com
@@||www.google.*/adsense/$~third-party,domain=google.cn
```

### 淘宝/阿里白名单

```abp
@@||simba.taobao.com/?name=mcad$script
@@||taobao.com/go/app/tmall/login-api.php?
@@||count.taobao.com/counter$script
@@||atanx.alicdn.com/t/tanxssp.js$domain=taojinbi.taobao.com
@@||atanx.alicdn.com/t/tanxssp.js$domain=alimarket.tmall.com|www.taobao.com|www.tmall.com
@@||alicdn.com/mm/tb-page-peel/
@@||ad.alimama.com^$genericblock
@@||alimama.com^$domain=tanx.com
@@||pub.alimama.com/common/adzone/
```

### 百度白名单

```abp
@@||libs.baidu.com^*
@@||baidu.com^*&cb=BaiduSuggestion.
@@||baidu.com/cse/search?*
@@||baidu.com/location/ip?*
@@||baidu.com/share/count?*
@@/adpic/*$domain=baikr.baidu.com|czsrc.com|nieyou.com|ontheup.com.tw|zform.net
@@||captcha.su.baidu.com^
@@||bdimg.com/advert/js/advert.js$domain=music.baidu.com
@@||baidu.com/hm.js$domain=dwz.cn
@@||bdstatic.com/??*,*,*,
@@||bdstatic.com/static/common/widget/ui/admanager/
@@||bdimg.com/libs/*
```

## 参考链接

- [ABP 过滤规则官方文档](https://adblockplus.org/en/filters)
- [EasyList 规则编写指南](https://easylist.to/pages/filterlist-format.html)
- [AdGuard 规则语法](https://kb.adguard.com/en/general/how-to-create-your-own-ad-filters)
