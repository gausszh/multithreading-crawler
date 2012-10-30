#!/usr/bin/python27
#coding=UTF-8
#author:gausszh
#e-mail:gausszh@gmail.com

import urllib2,re,json,os
import cookielib,urllib
import getAllUrl
from Queue import Queue
import threading
from pyquery import PyQuery as pq
import random,time

proxy_support = urllib2.ProxyHandler({'http':'http://127.0.0.1:8087'})
cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
opener_proxy = urllib2.build_opener(proxy_support,cookie_support, urllib2.HTTPHandler)
opener_normal= urllib2.build_opener(cookie_support, urllib2.HTTPHandler)

saveAppdetailInMysqlByUrl='http://192.168.1.125/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveAppdetailInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
saveReviewsInMysqlByUrl='http://192.168.1.125/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveReviewsInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
saveScreenshortsInMysqlByUrl='http://192.168.1.125/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveScreenshortInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
   
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
queue=Queue()
errorqueue=Queue()
def getC(node):
    try:
        return node.text().split(':')[1].strip()
    except Exception,e:
        return node.text().split(u'\uff1a')[1].strip()
def main(rootUrl):
    global folder,subcategory    
    try:
        homeurl=rootUrl
       # (a,b)=getAllUrl.main(homeurl)#ios-abc
        t=re.findall(r'ios-.*/',homeurl)
        
        folder='cn/'+t[0][4:-1]
        os.system('mkdir -p '+folder)
       # subcategory=t[0][4:-1]
        urlfilename=folder+'appurl.txt'
        namefilename=folder+'appname.txt'
#        urlfile=open(urlfilename,'w')
#        namefile=open(namefilename,'w')
#        a=json.dumps(a)
#        b=json.dumps(b)
#        print >>urlfile,a
#        print >>namefile,b
#        urlfile.close()
#        namefile.close()
            
        appnamefile=open(namefilename,'r')
        appname=json.load(appnamefile)
        appurlfile=open(urlfilename,'r')
        appurl=json.load(appurlfile)
        appnamefile.close()
        appurlfile.close()
        for i in range(len(appname)):
            n=appname[i]
            u=appurl[i]
            queue.put((n,u))# (name url) tuple
        templatefile=open('template.xml','r')
        template=''.join(templatefile.readlines())
        templatefile.close()
    except Exception,e:
       print str(e)
    threadlist=[]
#    while True:
#        (name,url)=queue.get()
#        tmpid=re.findall('/id\d*',url)[0][3:]
#        if tmpid=='476005657':
#            break
    for i in range(9):
        add=folder+'/thread%d__' % i
        threadlist.append(threading.Thread(target=threaddownload,args=(add,template,)))
    for i in range(len(threadlist)):
        threadlist[i].start()
    for i in range(len(threadlist)):
        threadlist[i].join()
#    threaddownload('musicData/123/logF_starthreadfive',template,)
                       
def threaddownload(filename,template):
    global queue
    global errorqueue
    timeoutcounts=0
    outputFile=open(filename+'.xml','w')
    print >>outputFile,'<?xml version="1.0" encoding="UTF-8"?>\n<apps>'
    cases=-1
    counts=0
    while True:
        cases+=1
        if queue.empty():
            break    
        try:
            (name,url)=queue.get()
            while  True:
                try: 
                   # req = urllib2.Request(url = "http://itunes.apple.com/us/a5pp/numbers/id361304891?mt=8",headers = headers)
                    agent = random.choice(user_agents)
                    opener_normal.addheaders = [("User-agent",agent),("Accept","*/*"),('Referer','http://www.google.com.hk')]
                    content = opener_normal.open(url,timeout=5).read()
                    timeoutcounts=0
                    break
                except Exception,e:
                    if timeoutcounts<5:
                        timeoutcounts+=1                       
                        time.sleep(timeoutcounts)
                    else:
                        break
            if timeoutcounts>=5:
                try:
                    agent = random.choice(user_agents)
                    opener_proxy.addheaders = [("User-agent",agent),("Accept","*/*"),('Referer','http://www.google.com.hk')]
                    content = opener_proxy.open(url,timeout=5).read()
                    print 'proxy'
                    timeoutcounts=0
                except Exception,e:
                    print name,url
                    print str(e)
                    errorqueue.put((name,url))
                    timeoutcounts=0
                    continue  
            d=pq(content)  
            name=d('h1').text()
            id=re.findall('\d{5,}',url)[0]
            ls=d('#left-stack')
            lschildren=ls.children()
            detail=lschildren.eq(0)
            price=detail('.price').text()
            icon=detail('img').attr('src')
            detail_ul=detail('ul')
            categoryN=detail_ul('.genre')
            dateN=categoryN.next()
            versionN=dateN.next()
            sizeN=versionN.next()
            languagesN=sizeN.next()
            sellerN=languagesN.next()
            copyrightN=sellerN.next()
            ratingN=detail_ul.next()
            requirementsN=ratingN.next()
            stars1=rating_counts1=stars2=rating_counts2=''
            list_customer_ratingN=detail.next()
            customer_ratingN=list_customer_ratingN('.rating')
            if len(customer_ratingN)==2:
                aria_label=customer_ratingN.eq(0).attr('aria-label')
                aria_label=re.findall('[\d\.]+',aria_label)
                stars1=aria_label[0]
                rating_counts1=aria_label[1]
                aria_label=customer_ratingN.eq(1).attr('aria-label')
                aria_label=re.findall('[\d\.]+',aria_label)
                stars2=aria_label[0]
                rating_counts2=aria_label[1]
            elif len(customer_ratingN)==1:
                pN=customer_ratingN.eq(0).prev()#上一个节点
                aria_label=customer_ratingN.eq(0).attr('aria-label')
                aria_label=re.findall('[\d\.]+',aria_label)
                if pN.text().find(u'\u5f53'):                   
                    stars1=aria_label[0]
                    rating_counts1=aria_label[1]
                else:
                    stars2=aria_label[0]
                    rating_counts2=aria_label[1]
            description=d('.product-review').eq(0)
            descriptionData=description.html()
            descriptionXml=description.text()
            whats_new=d('.product-review').eq(1)
            whats_newData=whats_new.html()
            whats_newXml=whats_new.text()
            date='-'.join(re.findall('\d+',getC(dateN)))
            output=template % (id,url,name,getC(categoryN),'',descriptionXml,whats_newXml)
            appdetailData=urllib.urlencode({'aid':id,'appurl':url,'name':name,'icon_url':icon,'price':price,'category':getC(categoryN),\
                                             'subcategory':'','updated':date,'version':getC(versionN),'size':getC(sizeN),'languages':\
                                             getC(languagesN),'seller':getC(sellerN),'copyright':copyrightN.text(),'des':ratingN('a').text(),\
                                             'reason':ratingN('ul').text(),'requirement':getC(requirementsN),'cstars':stars1,'crating_count':rating_counts1,\
                                             'stars':stars2,'rating_count':rating_counts2,'description':descriptionData,'whatsnew':whats_newData})
            aid=urllib2.urlopen(saveAppdetailInMysqlByUrl,appdetailData).read()   
            reviewN=d('.customer-review')
            for i in range(len(reviewN)):
                oneN=reviewN.eq(i)
                s=oneN('.rating').attr('aria-label')
                c_rating=re.findall('[\d\.]+',s)[0]
                data={'aid':aid,'uname':getC(oneN('.user-info')),'rating':c_rating,'title':oneN('.customerReviewTitle').text(),'content':oneN('.content').text()}
                urllib2.urlopen(saveReviewsInMysqlByUrl,urllib.urlencode(data))
            screenshotsN=d('.swoosh.lockup-container.application.large.screenshots')('img')
            for i in range(len(screenshotsN)):
                urllib2.urlopen(saveScreenshortsInMysqlByUrl,urllib.urlencode({'screenshots':screenshotsN.eq(i).attr('src'),'aid':aid}))    
            print '%s    %dth over!' % (threading.currentThread().getName(),cases)
            output = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub(' ', output)
            print >>outputFile,output
            counts+=1
            if counts==1000:
                counts=0
                print >>outputFile,'</apps>'
                outputFile.close()
                tempfilename='%s%d.xml' % (filename,i)
                outputFile=open(tempfilename,'w')
                print >>outputFile,'<?xml version="1.0" encoding="UTF-8"?>\n<apps>'
        except Exception,e:
            print str(e)
            print url
            errorqueue.put((name,url))
            print >>outputFile,'</apps>'
            outputFile.close()
            tempfilename='%s%d.xml' % (filename,i)
            outputFile=open(tempfilename,'w')
            print >>outputFile,'<?xml version="1.0" encoding="UTF8"?>\n<apps>'
    if not counts==0:
        print >>outputFile,'</apps>' 
        outputFile.close()
   # outputFile.close()
if __name__=='__main__':
    s=['http://itunes.apple.com/cn/genre/ios-tu-shu/id6018?mt=8']
    for one in s:
        main(one)
        errorfile=open('%slog.txt' % folder,'w')
        tempqueue=[]
        while not errorqueue.empty():
            tempqueue.append(errorqueue.get())
        t=json.dumps(tempqueue)
        print >>errorfile,t    
        print '***********ok**********'