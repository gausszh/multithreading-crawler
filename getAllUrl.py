#!/usr/bin/env python
#coding=utf8

#E-mail:gauss.zh@gmail.com
import urllib2
import re
import time
import json,pika
from sgmllib import SGMLParser
connection=pika.BlockingConnection(pika.ConnectionParameters(host='192.168.1.102'))
channel=connection.channel()
channel.queue_declare(queue='appurl')
class ListName(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.appurl=[]
        self.appname=[]
        self.appnameFlag=''
        self.tempname=''
    def handle_data(self, text):
        if self.appnameFlag==1:
            self.tempname+=text
            
    def start_a(self,attrs):
        for n,k in attrs:
            if n=='href':
                if re.findall(r'\.*itunes.apple.com/.*/app.*id.*\d',k):
                    self.appurl.append(k)
                    self.appnameFlag=1
    def end_a(self):
        if self.appnameFlag==1:
            self.appname.append(self.tempname)
            self.tempname=''           
            self.appnameFlag=''
def geturl(homeurl,letter,page):
    t='&letter=%s&page=%d' % (letter,page)
    oneappurl=homeurl+t
    print oneappurl
    #oneappurl='http://itunes.apple.com/us/genre/ios-music/id6011?mt=8&letter=A&page=1'
    returl=[]
    retname=[]
    while True:
        try:
            returnfile=urllib2.urlopen(oneappurl)
            content = returnfile.read()
            #print content
            returnfile.close()
            listname = ListName()
            listname.feed(content)
            retname=listname.appname
            returl=listname.appurl
        except Exception,e:
            if e.reason.errno==10054:
                time.sleep(1)
            else:
                break
        break
    for one in returl:
        channel.basic_publish(exchange='',routing_key='appurl',body=one)
    return (returl,retname)
def main(homeurl):
    returl=[]#http://itunes.apple.com/us/genre/ios-games/id6014?mt=8&letter=A&page=26
    retname=[]
    #homeurl='http://itunes.apple.com/us/genre/ios-games/id6014?mt=8'
    for i in range(65,91):#A-Z  还有* 
        page=1#65 66 67 68 69 70
        letter=chr(i)
        while True:            
            (appurl,appname)=geturl(homeurl,letter,page)
            if len(appurl)<=1:
                break
            page+=1
            print 'page%s ok' % page
            returl+=appurl
            retname+=appname
    page=1
    while True:
        (appurl,appname)=geturl(homeurl,'*',page)
        if len(appurl)<=1:
            break
        page+=1
        returl+=appurl
        retname+=appname
    return (returl,retname)
if __name__=='__main__':
    (a,b)=main('http://itunes.apple.com/cn/genre/ios-xiao-lu/id6007?mt=8')
    
#    urlfilename='cn/'+'tu-shuappurl.txt'
#    namefilename='cn/'+'tu-shuappname.txt'
#    urlfile=open(urlfilename,'w')
#    namefile=open(namefilename,'w')
#    a=json.dumps(a)
#    b=json.dumps(b)
#    print >>urlfile,a
#    print >>namefile,b