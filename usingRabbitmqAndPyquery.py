#coding=utf8

import pika,urllib2,urllib,cookielib,random,time
import re
from pyquery import PyQuery as pq
from Queue import Queue
saveAppdetailInMysqlByUrl='http://192.168.1.125/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveAppdetailInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
saveReviewsInMysqlByUrl='http://192.168.1.125/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveReviewsInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
saveScreenshortsInMysqlByUrl='http://192.168.1.125/ThinkSNS_2_5_forlove/index.php?app=api&mod=apps&act=saveScreenshortInMysql&oauth_token=cba6e111235ed535957be29d6436087d&oauth_token_secret=7cec9ee898ca22743eb2e1b32203304e'
   
htmlStringQ=Queue()
c=pika.ConnectionParameters(host='192.168.1.102')
conn=pika.BlockingConnection(c)
channel=conn.channel()
channel.queue_declare(queue='appurl')
channel.queue_declare(queue='webstring')
COUNTS=1
XML_COUNTS=1
templatefile=open('template.xml','r')
template=''.join(templatefile.readlines())
outputFile=open('samsung.xml','w')
print >>outputFile,'<?xml version="1.0" encoding="UTF-8"?>\n<apps>'

def getC(node):
    try:
        return node.text().split(':')[1].strip()
    except Exception,e:
        return node.text().split(u'\uff1a')[1].strip()
def convertHtmlToXmlAndDatabase(htmlString):
    global XML_COUNTS,COUNTS
    d=pq(htmlString)  
    name=d('h1').text()
    link=d('link')
    url=link.attr('href')
    print url
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
    output = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub(' ', output)
    if XML_COUNTS==1000:
        XML_COUNTS=0
        print >>outputFile,'</apps>'
        outputFile.close()
        tempfilename='samsung%d.xml' % (COUNTS)
        outputFile=open(tempfilename,'w')
        print >>outputFile,'<?xml version="1.0" encoding="UTF-8"?>\n<apps>'
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
    print '%dth over!' % (COUNTS)
    COUNTS+=1
def callback(cn,method,pro,body):
    htmlString=str(body)
    htmlStringQ.put(htmlString)
    try:
        convertHtmlToXmlAndDatabase(htmlString)
    except Exception,e:
        print str(e)
    cn.basic_ack(delivery_tag=method.delivery_tag)
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,queue='webstring')
print 'start...'
channel.start_consuming()