#!/usr/bin/env python
#coding=utf8
#按类别收集，多线程,更完善的错误处理（网络连接错误）
#E-mail:gauss.zh@gmail.com
import urllib2,re,json
import cookielib,urllib
import getAllUrl
from sgmllib import SGMLParser
from Queue import Queue
import threading
from pyquery import PyQuery as pq
import random,time
proxy_support = urllib2.ProxyHandler({'http':'http://127.0.0.1:8087'})
cookie_support= urllib2.HTTPCookieProcessor(cookielib.CookieJar())
opener_proxy = urllib2.build_opener(proxy_support,cookie_support, urllib2.HTTPHandler)
opener_normal= urllib2.build_opener(cookie_support, urllib2.HTTPHandler)

MONTH={'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}

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
        
urlpat=re.compile(r'\.*itunes.apple.com/us/app.*id.*\d')
category=''
folder=''
subcategory=''
queue=Queue()
errorqueue=Queue()#Mozilla/5.0 (X11; Linux x86_64; rv:10.0.5) Gecko/20120606 Firefox/10.0.5
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'}
class ListName(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.infoFlag = ""
        self.appurl=[]
        self.appname=[]
        self.descriptionFlag=''
        self.descriptionPFlag=''
        self.description=[]
        self.appnameFlag=''
        self.info=[]
        self.iphonescreenshots=[]
        self.ipadscreenshots=[]
        self.whatisnewFlag=''
        self.whatisnew=[]
        self.allstartFlag=''
        self.allstart=[]
        self.customerstartFlag=''
        self.customerstart=[]
        self.customerFlag=''
        self.customer=[]
        self.iphonescreenshotsFlag=''
        self.ipadscreenshotsFlag=''
        self.nameFlag=''
        self.name=''
        self.icon=''
    def handle_data(self, text):
        if self.infoFlag == 1:
            self.info.append(text)
        if self.appnameFlag==1:
            self.appname.append(text)
            self.appnameFlag=''
        if self.descriptionFlag==1 and self.descriptionPFlag==1 :
            self.description.append(text)     
        if self.customerFlag==1:
            self.customer.append(text)
        if self.whatisnewFlag==1:
            self.whatisnew.append(text)
        if self.nameFlag==1:
            self.name+=text
    def start_p(self,attrs):
        if self.descriptionFlag==1:
            self.descriptionPFlag=1
    def end_p(self):
        self.descriptionFlag=''
        self.descriptionPFlag=''
    def start_img(self,attrs):
        for n,k in attrs:
            if (k=='landscape' or k=='portrait'):
                if self.ipadscreenshotsFlag==1:
                    self.ipadscreenshots.append(attrs[2][1])
                if self.iphonescreenshotsFlag==1:
                    self.iphonescreenshots.append(attrs[2][1])
            if n=='height' and int(k)>=150:
                self.icon=attrs[4][1]
    def start_a(self,attrs):
        for n,k in attrs:
            if n=='href':
                if re.findall(r'\.*itunes.apple.com/us/app.*id.*\d',k):
                    self.appurl.append(k)
                    self.appnameFlag=1
    def start_div(self,attrs):
        for n,k in attrs:
            if n=='metrics-loc' and k=='Titledbox_Description':#http://itunes.apple.com/us/genre/ios-games/id6014?mt=8
                self.descriptionFlag=1#http://itunes.apple.com/us/app/angry-birds/id343200656?mt=8
            if n=='id' and k=='left-stack':
                self.infoFlag=1
                self.customerFlag=''
            if n=='metrics-loc':
                if re.findall(r"What's New",k):
                    self.whatisnewFlag=1
            if n=='class' and k=='rating' and self.infoFlag==1:
                self.allstart.append(attrs[3][1])
                self.customerstartFlag=1
                self.allstartFlag=1
            if n=='class' and k=='customer-reviews':
                self.customerFlag=1
            if n=='class' and k=='rating' and self.customerFlag==1:
                self.customerstart.append(attrs[3][1])
            if n=='class' :
                if re.findall(r'iphone-screen-shots',k):
                    self.iphonescreenshotsFlag=1
                    self.ipadscreenshotsFlag=''
            if n=='class' :
                if re.findall(r'ipad-screen-shots',k):
                    self.ipadscreenshotsFlag=1
                    self.iphonescreenshotsFlag=''  
    def start_h1(self,attrs):
        self.nameFlag=1  
    def end_h1(self):
        self.nameFlag=''
    def end_div(self):
        self.whatisnewFlag=''
def simplify(lt):
    """去除list中的杂项，比如\n,' '"""
    ret=[]
    for one in lt:
        temp=one.strip()
        if temp:
            ret.append(temp)
    return ret
   
def main(rootUrl):
    global folder,subcategory    
    try:
        homeurl=rootUrl
        (a,b)=getAllUrl.main(homeurl)#ios-abc
        t=re.findall(r'ios-.*/',homeurl)
        
        folder=t[0][4:-1]
       # subcategory=t[0][4:-1]
        urlfilename=folder+'appurl.txt'
        namefilename=folder+'appname.txt'
        urlfile=open(urlfilename,'w')
        namefile=open(namefilename,'w')
        a=json.dumps(a)
        b=json.dumps(b)
        print >>urlfile,a
        print >>namefile,b
        urlfile.close()
        namefile.close()
        
#        global queue
#        logfile=open('F_starerrornameandurl.txt','r')
#        log=logfile.readlines()
#        logfile.close()
#        for one in log:
#            url=re.findall(r'http.*mt=8',one)[0]
#            n='null'
#            queue.put((n,url))
            
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
    for i in range(10):
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
    i=-1
    counts=0
    while True:
        i+=1
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
                    #returnfile=urllib2.urlopen(url=url,timeout=5)
#                    content=returnfile.read()
#                    returnfile.close()
                    timeoutcounts=0
                    break
                except Exception,e:
                    if timeoutcounts<5:
                        timeoutcounts+=1                       
                        time.sleep(timeoutcounts)
                    else:
                        print name,url
                        print str(e)
                        errorqueue.put((name,url))
                        break
            if timeoutcounts>=5:
                try:
                    agent = random.choice(user_agents)
                    opener_proxy.addheaders = [("User-agent",agent),("Accept","*/*"),('Referer','http://www.google.com.hk')]
                    content = opener_proxy.open(url,timeout=5).read()
                    print 'proxy'
                except Exception,e:
                    timeoutcounts=0
                    continue    
            listname=ListName()
            listname.feed(content)
            d=pq(content)
#            name=re.findall(r'app/.*/id',appurl[i])[0]
#            name=name[4:-3]
            name=listname.name
            info={}
            j=0
            tmpinfo=simplify(listname.info[0:50])
        
            info['price']='Free'  
            for one in tmpinfo:
                if re.findall(r'\$\d*',one):
                    info['price']=one
                if one in ['Category:','Released','Updated:','Version:','Size:','Languages:','Language:',\
                           'Seller:','Requirements:','Released:','All Versions:','Current Version:']:
                    info[one]=tmpinfo[j+1]
                    if one=='Seller:':
                        info['copyright:']=tmpinfo[j+2]
                        info['app_rating:']=tmpinfo[j+3]
                        info['reasons:']=tmpinfo[j+4]
                j+=1          
#            if locals().has_key('category'):
#                if category!=info['Category:']:
#                    continue
#            else:
            category=info['Category:'] 
            icon=listname.icon
            id=str(re.findall(r'[\d]{5,}',url)[0])   
            customer=simplify(listname.customer)
            price=info['price']            
            if info.has_key('Released:'):
                Updated=info['Released:']
            elif info.has_key('Updated:'):
                Updated=info['Updated:']
            version=info['Version:']
            size=info['Size:']
            languages=''
            if info.has_key('Languages:'):
                languages=info['Languages:']
            elif info.has_key('Language:'):
                languages=info['Language:']
            
            seller=info['Seller:']
            copyright=info['copyright:']
            app_rating=info['app_rating:']
            reason=info['reasons:']
            requirements=info['Requirements:']
            stars1=rating_counts1=''
            tmpi=0
            if info.has_key('Current Version:'):
                t=listname.allstart[tmpi].split(',')
                tmpi+=1
                stars1=t[0]   
                rating_counts1=info['Current Version:']
            stars2=rating_counts2=''
            if  info.has_key('All Versions:'):
                t=listname.allstart[tmpi].split(',')
                stars2=t[0]
                rating_counts2=info['All Versions:']
            description=''.join(listname.description)
            
            t=simplify(listname.whatisnew[3:])
            whats_new=''.join(t)
            iphonescreenshot=''
            screenshotDictList=[]
            for one in listname.iphonescreenshots:
                iphonescreenshot+='<screenshot type="iphone"><![CDATA[%s]]></screenshot>\n' % one#xml
                # save in mysql throught thinksns
                #########################
                screenshotDictList.append({'screenshots':one,'aid':id})
                
            ipadscreenshot=''
            for one in listname.ipadscreenshots:
                ipadscreenshot+='<screenshot type="ipad"><![CDATA[%s]]></screenshot>\n' % one#xml
                # save in mysql throught thinksns
                #############################
                screenshotDictList.append({'screenshots':one,'aid':id})
            usernameindex=[]
            for k in range(len(customer)):
                if re.findall(r'by\n',customer[k]):
                    usernameindex.append(k)
            review=[]
            reviewDictList=[]
            for k in range(len(usernameindex)):
                if k!=len(usernameindex)-1:
                    t=usernameindex[k+1]-1
                else:
                    t=usernameindex[k]+2
                s='<review>\n<user><![CDATA[%s]]></user>\n<rating><![CDATA[%s]]></rating>\n<title><![CDATA[%s]]></title>\n<content><![CDATA[%s]]></content>\n</review>\n' % \
                (re.findall(r'.*$',customer[usernameindex[k]])[0].strip(),listname.customerstart[k],customer[usernameindex[k]-1],''.join(customer[usernameindex[k]+1:t]))
                #save review in mysql throught by thinksns
                ##########################
                reviewDictList.append({'aid':id,'uname':re.findall(r'.*$',customer[usernameindex[k]])[0].strip(),'rating':\
                            listname.customerstart[k],'title':customer[usernameindex[k]-1],'content':''.join(customer[usernameindex[k]+1:t])})
                
                review.append(s)

            review=''.join(review)#s = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub(' ', str)
            output=template % (id,icon,url,name, price,category,subcategory,Updated,version,size,languages,seller,copyright,app_rating,reason,requirements,\
                 stars1,rating_counts1,stars2,rating_counts2,description,whats_new,iphonescreenshot,ipadscreenshot,review)
            #save appdetail in mysql throught by thinksns
            pydes=d('.product-review').eq(0)
            pydes=pydes.html()#Jan 04, 2011
            Updated=Updated.strip()
            updateTime=Updated[-4:]+'-'+str(MONTH[Updated[:3]])+'-'+Updated[4:6]
            appdetailData=urllib.urlencode({'aid':id,'appurl':url,'name':name,'icon_url':icon,'price':price,'category':category,\
                                             'subcategory':subcategory,'updated':updateTime,'version':version,'size':size,'languages':\
                                             languages,'seller':seller,'copyright':copyright,'des':app_rating,'reason':reason,'requirement':requirements,\
                                             'cstars':stars1,'crating_count':rating_counts1,'stars':stars2,'rating_count':rating_counts2,\
                                             'description':pydes,'whatsnew':whats_new})
##   APPDETAIL
            aid=urllib2.urlopen(saveAppdetailInMysqlByUrl,appdetailData).read()
            for one in reviewDictList:
                one['aid']=aid
                #reivew
                urllib2.urlopen(saveReviewsInMysqlByUrl,urllib.urlencode(one))
            
            for one in screenshotDictList:
                one['aid']=aid
                urllib2.urlopen(saveScreenshortsInMysqlByUrl,urllib.urlencode(one))      
            
            
            
            
            
            
            
            
            print '%s    %dth over!' % (threading.currentThread().getName(),i)
            output = re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub(' ', output)
            print >>outputFile,output
            counts+=1
            if counts==10:
                counts=0
                print >>outputFile,'</apps>'
                outputFile.close()
                tempfilename='%s%d.xml' % (filename,i)
                outputFile=open(tempfilename,'w')
                print >>outputFile,'<?xml version="1.0" encoding="UTF-8"?>\n<apps>'
        except Exception,e:
            print str(e)
            print url
            print info
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
    s=['http://itunes.apple.com/us/genre/ios-music/id6011?mt=8']
    for one in s:
        main(one)
        errorfile=open('log%s.txt' % subcategory,'w')
        tempqueue=[]
        while not errorqueue.empty():
            tempqueue.append(errorqueue.get())
        t=json.dumps(tempqueue)
        print >>errorfile,t    
        print '***********ok**********'
