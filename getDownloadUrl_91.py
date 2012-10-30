#!/usr/bin/env python
#coding=utf8
#按类别收集，多线程,更完善的错误处理（网络连接错误）
#E-mail:gauss.zh@gmail.com
import urllib2,re,json
import cookielib,urllib
import getAllUrl_91
from sgmllib import SGMLParser
from Queue import Queue
import threading
from pyquery import PyQuery as pq
import random,time
proxy_support = urllib2.ProxyHandler({'http':'http://127.0.0.1:8087'})
cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
opener_proxy = urllib2.build_opener(proxy_support,cookie_support, urllib2.HTTPHandler)
opener_normal= urllib2.build_opener(cookie_support, urllib2.HTTPHandler)

saveAppdetailInMysqlByUrl='http://192.168.1.104/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveAppdetailInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
saveReviewsInMysqlByUrl='http://192.168.1.104/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveReviewsInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
saveScreenshortsInMysqlByUrl='http://192.168.1.104/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveScreenshortInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
saveDownloadAppInfo='http://192.168.1.104/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveDownloadAppInfo&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
isExistTheId_91='http://192.168.1.104/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=isExistTheId_91&id_91=%s&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'

urlQueue=Queue()   
logQueue=Queue()
user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
] 
rootUrl='http://app.91.com'
L='摄影'
folder='91app/'+L
def main(homeUrl):
    
    urlfile=open(folder+'/appurl.txt','r')
    appurlList=json.load(urlfile)
    for one in appurlList:
        urlQueue.put(one)
    threadList=[]
    threadNum=5
    for i in range(threadNum):
        threadList.append(threading.Thread(target=parserHtmlGetDownloadUrl,args=()))
    for i in range(threadNum):
        threadList[i].start()
    for i in range(threadNum):
        threadList[i].join()
def parserHtmlGetDownloadUrl():
     
    aflag=True
    while not urlQueue.empty():
        url=urlQueue.get()
        agent = random.choice(user_agents)
        download_url=id_91=url_91=url_apple=id_apple=version=name=content=''
        try:
            opener_proxy.addheaders = [("User-agent",agent),("Accept","*/*"),('Referer','http://www.google.com.hk')]
            content = opener_proxy.open(url,timeout=5).read()
        except Exception,e:
            content = opener_proxy.open(url,timeout=10).read()
        if not content:
            continue
        d=pq(content)
        try:
            detail=d('.soft_detail_h3')
            name=detail('h3').text()
            version=re.findall('[\d\.]+',detail('span').text())[0]
            download=d('div.soft_detail_btn')
            link=download('a')
            for j in range(len(link)):
                onea=link.eq(j)
                if onea.attr('title')==u'iTunes \u4e0b\u8f7d':#iTunes 下载
                    url_apple=onea.attr('href')
                    id_apple=re.findall('\d{5,}',url_apple)[0]
                if onea.text()==u'\u4e0b\u8f7d\u5230\u7535\u8111':#下载到电脑
                    download_url=rootUrl+onea.attr('href')
                    id_91=re.findall('\d{5,10}',download_url)[0]
            if not download_url:
                script=d('script').text()  
                download_url=re.findall(r'http://app.91.com/soft/download/.+?\.[ipaz]{3}',script)[0]
                id_91=re.findall('\d{5,10}',download_url)[0]
            count=urllib2.urlopen(isExistTheId_91 % id_91).read()
            if count  == '0':
                returnid=urllib2.urlopen(saveDownloadAppInfo,urllib.urlencode({'url_apple':url_apple,'id_apple':id_apple,'id_91':id_91,\
                                'url_91':url,'download_url':download_url,'version':version,'name':name,'category':L,'download_link':"<a href='%s'>%s</a>" % (download_url,download_url)})).read()
                print url,returnid 
            else:
                print 'It is already exist ',name,url_91
        except Exception,e:
            print str(e),url
            print link.text()
            logQueue.put(url)
       
if __name__=='__main__':
    main('34')
    t=[]
    while not logQueue.empty():
        t.append(logQueue.get())
    jsonstruct=json.dumps(t)
    urlfile=open(folder+'/log.txt','w')
    print >>urlfile,jsonstruct