#coding=utf8

import pika,urllib2,urllib,cookielib,random,time
import threading
from Queue import Queue
q=Queue()
webBuff=Queue()
c=pika.ConnectionParameters(host='192.168.1.102')
conn=pika.BlockingConnection(c)
channel=conn.channel()
channel.queue_declare(queue='appurl')
channel.queue_declare(queue='webstring')
proxy_suport=urllib2.ProxyHandler({'http':'http://127.0.0.1:8087'})
cookie_suport=urllib2.HTTPCookieProcessor(cookielib.CookieJar())
opener_proxy=urllib2.build_opener(proxy_suport,cookie_suport,urllib2.HTTPHandler)
opener_normal=urllib2.build_opener(cookie_suport,urllib2.HTTPHandler)

class downloadWeb(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global q
        while True:
            while not q.empty():
                url=q.get()
                retF=''
                print 'Downloading %s' % url
                flag=False
                for i in range(3):
                    try:
                        retF=opener_normal.open(url,timeout=5).read()
                        flag=True
                        break
                    except Exception,e:
                        print 'error'
                        time.sleep(i)
                if not flag:
                    try:
                        retF=opener_proxy.open(url,timeout=5).read()
                        flag=True
                    except Exception,e:
                        print 'error'
                if flag and webBuff.qsize()<100:
                    webBuff.put(retF)
                while webBuff.qsize()>=100:
                    time.sleep(1)
               

threadList=[]
threadNum=2
def cleanWebBuff():
    while True:
        while not webBuff.empty():
            s=webBuff.get()
            channel.basic_publish(exchange='',routing_key='webstring',body=s)
threading.Thread(target=cleanWebBuff,args=()).start()
for i in range(threadNum):
    threadList.append(downloadWeb())
for one in threadList:
    one.start()
def callback(cn,method,pro,body):
    url=str(body)
    print 'Received %s' %url
    q.put(url)
    while q.qsize()>3:
        time.sleep(1)
    cn.basic_ack(delivery_tag=method.delivery_tag)
    

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,queue='appurl')
print 'start...'
try:
    channel.start_consuming()
except Exception,e:
    channel.start_consuming()