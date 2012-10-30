#!/usr/bin/python
#coding=utf8
#author:gausszh
#E-mail:gauss.zh@gmail.com
#2012-09-25
from pyquery import PyQuery as pq
import re,urllib2,cookielib

proxy_support = urllib2.ProxyHandler({'http':'http://127.0.0.1:8087'})
cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
opener_proxy = urllib2.build_opener(proxy_support,cookie_support, urllib2.HTTPHandler)
opener_normal= urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
MAXINF=999999
reg=re.compile('id\d{7,}')

def download_one_subcategory(beginUrl):
    """beginUrl like "http://apple.shiwan.com/list/cat-371" """
    
    beginUrl+='/pf-0/price-0/age-0/ft-0/ps-0/order-0/p-%d'
    for i in range(1,MAXINF):
        theUrl=beginUrl % i 
        try:
            content=opener_normal.open(theUrl,timeout=5).read()
        except Exception,e:
            print str(e),theUrl
        d=pq(content)
        dir_ido=d('div.dir_ido')
        if not re.findall('\d{3,}',dir_ido.eq(0)('a').attr('href')):
            break
        for alink in range(len(dir_ido)):
            div=dir_ido.eq(alink)
            s=div.html()
            regid=reg.findall(s)
            if regid:
                id=regid[0][2:]
                print id
            else:
                print s
if __name__=='__main__':
    download_one_subcategory('http://apple.shiwan.com/list/cat-371')
                