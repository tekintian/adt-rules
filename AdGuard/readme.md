# AdGuard rules

自用的AdGuard rules

官方的规则文件太大, 精简一些不必要的和添加自己常用的规则

hosts.txt 官方规则
https://adaway.org/hosts.txt




删除所有注释
~~~txt
\!(.*)$

~~~


dnsfilter.txt 官方规则
https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt
~~~txt
! Homepage: https://github.com/AdguardTeam/AdguardSDNSFilter
! License: https://github.com/AdguardTeam/AdguardSDNSFilter/blob/master/LICENSE
! Last modified: 2024-01-10T06:01:14.356Z
!
! Compiled by @adguard/hostlist-compiler v1.0.22
!
!
! Source name: AdGuard Base filter ad servers
! Source: https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers.txt
!
!
! This section contains the list of third-party advertising networks domains.
! Note, that we only put rules that block full domains here and not URL parts (there's `general_url.txt` for that). Also, it must be domains that are used in a third-party context.
! The rules with hints are at the end of file.

! Good: ||doubleclick.net^$third-party
! Bad: /banner.jpg (should be in general_url.txt)
! Bad: ||adssubdomain.legitwebsite.com^ (should be in adservers_firstparty.txt)
!
~~~

