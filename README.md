#adt rules 广告终结者过滤规则

仓库地址:
https://gitee.com/tekintian/adt-rules


规则调用地址:
https://gitee.com/tekintian/adt-rules/raw/master/adt-base.txt


- 增强规则:
~~~txt
https://gitee.com/tekintian/adt-rules/raw/master/plus/js.txt
https://gitee.com/tekintian/adt-rules/raw/master/plus/html5player.txt
~~~

## 样式规则示例
~~~txt
##.broadcastMe[style="width: 1200px;"]
##.btn.btn-default.hotwords[target="_blank"]

##.con_search + #carousel-example-generic[style^="max-width: 1170px;"]
##.content > a > .topline
##.content-video > .ads

!--演示包含指定属性
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
~~~


## ID选择器规则
~~~txt
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


##div:not([id]):not([class]):not([style]) > div:not([id]):not([class]):not([style]) > iframe[scrolling="no"][src*="//"][src*="?"][src*="="][src*="&"][width][height][frameborder="0"]:not([src^="http://www.facebook.com/"])

##div[style^="width: 100%;"][style$="margin: 0px;"] iframe[scrolling="no"][src*="//"][src*="?"][src*="="][src*="&"][width][height][frameborder="0"]

##div[style^="width: 100%;"]:not([id]):not([class]) > iframe[scrolling="no"][src^="http"][src*="?"][src*="="][src*="&"][width][height][frameborder="0"]:not([allowfullscreen])

##a[href*=".gotourls.bid"]

##a[href^="http://yunbofangbt."]

##div[align="center"] > a[href^="/url/"] > img[src*=".alicdn.com"]

##a[href^="/dasp.php?a="]

##table[style="border:#e8e8e8 1px solid;"] + div[style="margin-top:5px"] > table[style="width:100%;"][cellspacing="0"][cellpadding="1"][bordercolor="#22222"][border="1"]


~~~

## 标签选择规则

~~~txt
##a[href*=".com/?p="][target="_blank"] > img[src$=".gif"]
##a[href*=".ahhxwavi.cn"]
##a[href*=".bayiyy.com/download."]

##a[href*=".yb2843.vip"]
##a[href*=".yyk2.com/"]
##a[href*="/602034.com"]


##a[href^="https://luolidao.vip/"]
##a[onclick^="javascript:pc_"] > img[src*=".alicdn.com"]
##a[style="display:inline-block;font-weight:bold;color:#f00;border:1px solid #f00;border-radius:15px;padding:2px 5px 2px 5px;margin:5px 5px 5px 0px;"]


~~~


## uri规则
~~~txt
!-- uri ads block
/adsbygoogle.js$script,match-case
/advertising.js$script,match-case
/ads.js$script,match-case
/advertising.js$script,match-case
/ads.js$script,match-case
/pagead/show_ads.js
/g\.alicdn\.com\/mm\/yksdk\/0\.2\.\d+\/playersdk\.js/>>>1111.51xiaolu.com/playersdk.js>>>>keyword=playersdk
/static\.iqiyi\.com\/js\/common\/mars_v\.js.*/>>>1111.51xiaolu.com/mars.js?2048>>>>keyword=iqiyi
/s3m.mediav.com/galileo/*.mp4
/104_150/1360_1|
/1linbAte_mplatk/*

/common/cf/*$image,object,domain=~bingfeng.tw|~dahuaiji.com
/content.php?id=148&type=g|$xmlhttprequest
/content/plugins/em_ad/*

/duilian.$domain=~388g.com|~msra.cn|~supfree.net

!--正则
/\.(?:com|com\.cn|cn|cc|net|org|me|tv)\/[0-9a-z]{9,}\.js/$script,domain=023up.com|2345.com

/\.js\?[a-z]+=[a-z]+$/$script,domain=china.cn|eastday.com|fangdaijisuanqi.com

/images/*.gif$domain=2c2.website|2p8.space|adultgao.com

~~~

## 域名规则

~~~txt
! global domain rules
|http://*.cn/ad/
|http://*.hk/ad/$domain=~sunmobile.com.hk
|http://*.in/ad/
|http://*.me/ad/
|http://*.tw/ad/$domain=~ruten.com.tw
|http://*.us/ad/
|http://*/ad.*.js?v=*&sp=
|http://*/ad.js?sn=
|http://*/ad.js?v=$domain=~mgc.qq.com
|http://*/gg1.
|http://*/gg2.
|http://*/gg3.
|http://*/js/ad.$domain=~coolpc.com.tw|~sac.net.cn
|http://*/js/ad/
|http://*/ad_bj.js?

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
||s.ytimg.com/yts/jsbin/www-pagead-id-vfla_fkeg/www-pagead-id.js
||pagead2.googlesyndication.com/pagead/js/adsbygoogle.js
||googletagservices.com/tag/js/gpt.js

.com*/ps/psCreat.js
.com/aaasi/*.js
.com/ad777.js
.com/ads/ada.js

~~~


## 例外规则
~~~txt
@@||192.168.*.1/$generichide
@@||192.168.*/advertising_$stylesheet
@@||199it.com^$generichide
@@||360buyimg.com/ad/$domain=jd.com
@@||360buyimg.com/ads/$domain=jd.com
@@||360buyimg.com^*??
@@||3d66.com/??*ad-

@@/pic/ad/*$domain=ybjk.com
@@/pub/ad/*$domain=ruten.com.tw
@@/pub1/??$domain=banggo.com
@@/store_ad/*$domain=pcstore.com.tw

@@/image/ad/*$domain=gashpoint.com
@@/images/*/*.gif$domain=maichun5.info|mc88.info|myhhg.com|yh1.info|yh10.info
@@/images/ad/*$domain=9588.com|casio.com.cn|dod-tec.com|ourgame.com|pro-partner.com.tw|snh48.com|tingbook.com
@@/images/adv/*$domain=gueizu.com|topfilex.com
@@/img/ad_$domain=p9.com.tw|ruten.com.tw
@@/img_ad/*$domain=tkec.com.tw
@@/jquery/*$domain=dm530.net|sobooks.cc


@@||www.google.*/adsense/$~third-party,domain=google.cn



@@||simba.taobao.com/?name=mcad$script
@@||taobao.com/go/app/tmall/login-api.php?
@@||count.taobao.com/counter$script
@@||simba.taobao.com/?name=tcmad&$domain=www.taobao.com
@@||tbskip.taobao.com/json/
@@||atanx.alicdn.com/t/tanxssp.js$domain=taojinbi.taobao.com
@@||atanx.alicdn.com/t/tanxssp.js$domain=alimarket.tmall.com|www.taobao.com|www.tmall.com
@@||alicdn.com/mm/tb-page-peel/
@@||astyle.alicdn.com/??
@@||g.alicdn.com/??*/criteo
@@||g.alicdn.com^*/banner_ad_
@@||alicdn.com/??*/tracker/
@@||alicdn.com/dt/tracker/4.2.0/??tracker.
@@||tce.alicdn.com^$domain=alimama.com
@@||alicdn.com/js/*/xpopup.js
@@||alicdn.com/retcode/log/log.js
@@||alicdn.com/dt/tracker/2.5.1/tracker.js$domain=alimama.com
@@||ad.alimama.com^$genericblock
@@||alimama.com^$domain=tanx.com
@@||pub.alimama.com/common/adzone/
@@||tbcdn.cn^*/click_track.js


!--baidu.com
@@||libs.baidu.com^*
@@||baidu.com^*&cb=BaiduSuggestion.
@@||baidu.com/cse/search?*
@@||baidu.com/location/ip?*
@@||baidu.com/share/count?*
@@|http://0.baidu.com
@@/adpic/*$domain=baike.baidu.com|czsrc.com|nieyou.com|ontheup.com.tw|zform.net
@@||captcha.su.baidu.com^
@@||cb.baidu.com/crossdomain.xml$domain=v.baidu.com
@@||cb.baidu.com/ecom?*.baomihua.$domain=v.baidu.com
@@||eiv.baidu.com/hmt/icon/21.gif
@@/image/share_$domain=pan.baidu.com
@@||bdimg.com/advert/js/advert.js$domain=music.baidu.com
@@||cbjs.baidu.com/js/m.js$domain=fxpan.com|iyingdi.com|pic.tiexue.net|www.pctowap.com
@@||cbjs.baidu.com/js/o.js$domain=jkpan.cc
@@||baidu.com/hm.js$domain=dwz.cn
@@||hao123img.com/resource/zt/widget/service/util/clickTrack.
@@||tb1.bdstatic.com/tb/cms/ngmis/adsense/*.jpg
@@||ss0.bdstatic.com
@@||bdstatic.com/??*,*,*,
@@||bdstatic.com/static/common/widget/ui/admanager/
@@||bdstatic.com/po/??*,*,*,
@@||bdstatic.com^*/share_
@@||ecma.bdimg.com/holmes/*.svg
@@||bdimg.com/libs/*
@@||bdimg.com/static/wenda-pc/widget/share/share_
@@||gtimg.com/libs/$domain=18xs.org
@@||gtimg.cn/qz-proj/wy-pc-v3/static/img/svg/icon-share-


~~~



## Tools

base64加解密
https://www.base64decode.org/

https://www.base64encode.org/

JS美化压缩
https://www.prettifyjs.net/

https://www.uglifycss.com/

https://www.beautifyjson.org/

