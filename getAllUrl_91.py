#coding=utf8
from pyquery import PyQuery as pq
import urllib,urllib2,cookielib,json,os
from Queue import Queue
urlQueue=[]
def getUrl(homeUrl):
    '''homeUrl such like http://app.91.com/Soft/iPhone/album/旅游/2690_%d_4'''
    global urlQueue
    i=1
    while True:
        url=homeUrl % i
        i+=1
        d=pq(url)
        table=d('#AlbumList')
        td=table('td')
        if len(td)==0:
            break
        for j in range(len(td)):
            onetd=td.eq(j)
            aNode=onetd('a')
            urlQueue.append(aNode.attr('href'))
        print url
    return urlQueue
if __name__=='__main__':
    getUrl('http://app.91.com/soft/iPhone/album/摄影/4886_%d_5')#旅游、导航
    folder='91app/摄影'
    os.system('mkdir -p '+folder)
    jsonstruct=json.dumps(urlQueue)
    urlfile=open(folder+'/appurl.txt','w')
    print >>urlfile,jsonstruct