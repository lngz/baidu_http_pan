#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import cookielib, urllib2
import urllib
import json
import hashlib
import re
import sys
import time
reload(sys)
sys.setdefaultencoding('UTF-8')

from stat import S_IFDIR, S_IFLNK, S_IFREG

import os,sys,socket,re
#!/usr/bin/env python
import io
#获取登陆token
import codecs
import mimetypes
import uuid
import logging ,logging.config

logging.basicConfig(
                    format='%(asctime)s '
                            '%(filename)s: '
                            '%(levelname)s: '
                            '%(lineno)d:\t'
                            '%(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger()
#logging.config.fileConfig('log_conf.ini')
#logger = logging.getLogger("simpleExample")

def md5_file(name):
    m = hashlib.md5()
    a_file = open(name, 'rb')    #需要使用二进制格式读取文件内容
    m.update(a_file.read())
    a_file.close()
    return m.hexdigest()


class Baidu(object):
    def __init__(self,user = '', psw = ''):
        self.user = user
        self.psw  = psw

        if not user or not psw :
            print "Plz enter enter 2 params:user,psw"
            sys.exit(0)


        self.cookiename = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'cookie_%s' % (self.user)
        self.token = ''
        self.bdstoken = ''
        self.BDUSS = ''

        self.allCount  = 0
        self.pageSize  = 10
        self.totalpage = 0
        self.filest = {}
        now = time.time()
        self.filest['/'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.filest['.'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        self.filest['..'] = dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)

        self.logined = False
        self.cj = cookielib.MozillaCookieJar()
        try:
            self.cj.revert(self.cookiename)
            self.logined = True
            logger.info('Load cookie from file')

        except Exception,e:
            logger.info("Can't load cookie from file")

        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [('User-agent','Opera/9.23')]
        urllib2.install_opener(self.opener)

        #socket.setdefaulttimeout(60)

    #登陆百度
    def login(self):
        if self.logined == False :
            #第一次访问一下，目的是为了先保存一个cookie下来
            qurl = '''https://passport.baidu.com/v2/api/?getapi&tpl=yun&apiver=v3&tt=1383192406848&class=login&logintype=basicLogin'''
            r = self.opener.open(qurl)
            self.cj.save(self.cookiename)

            #第二次访问，目的是为了获取token
            qurl = '''https://passport.baidu.com/v2/api/?getapi&tpl=yun&apiver=v3&tt=1383192406848&class=login&logintype=basicLogin'''
            r = self.opener.open(qurl)
            rsp = r.read()
            self.cj.save(self.cookiename)

            #通过正则表达式获取token
            login_tokenStr = '''token" : "(.*?)"'''
            login_tokenObj = re.compile(login_tokenStr,re.DOTALL)
            matched_objs = login_tokenObj.findall(rsp)
            if matched_objs:
                self.token = matched_objs[0]
                logger.debug( self.token )
                #然后用token模拟登陆
                post_data = urllib.urlencode({
                                        'username':self.user,
                                        'password':self.psw,
                                        'token':self.token,
                                        'staticpage':'http://yun.baidu.com/chres/static/js/pass_v3_jump.html',
                                        'charset':'utf-8', 'tpl':'yun',
                                        'apiver':'v3', 'tt':'1383185233025',
                                        'codestring':'', 'isPhone':'false',
                                        'safeflg':'0', 'u':'http://yun.baidu.com/',
                                        'quick_user':'0', 'logintype':'basicLogin',
                                        'verifycode':'', 'mem_pass':'on',
                                        'ppui_logintime':'25955',
                                        'callback':'parent.bd__pcbs__a8jd5z'})
                #path = 'http://passport.baidu.com/?login'
                path = 'https://passport.baidu.com/v2/api/?login'
                self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
                self.opener.addheaders = []
                urllib2.install_opener(self.opener)
                headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language":"zh-CN,zh;q=0.8",
                        "Cache-Control":"max-age=0", "Connection":"keep-alive",
                        "Content-Length":"394", "Host":"passport.baidu.com",
                        "Origin":"http://yun.baidu.com", "Referer":"http://yun.baidu.com/",
                        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
                        }
                req = urllib2.Request(path, post_data, headers=headers, )
                rsp = self.opener.open(req).read()
                logger.debug( rsp )
                if not "err_no=0" in rsp:
                    logger.info("Maybe Login failed!!")

                self.cj.save(self.cookiename)
            else:
                logger.info( "Can't get token" )
                logger.debug(rsp)
                sys.exit(0)
        for cookie in self.cj:
            logger.debug("%s -> %s", cookie.name, cookie.value)
            if cookie.name == 'BDUSS':
                self.BDUSS = cookie.value
                break

    #获取每一页里的博客链接
    def fetchPage(self,url):
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req).read()
        print rsp
        
    def list(self, path='/'):
        list_url = "http://pan.baidu.com/api/list?" + urllib.urlencode({'channel':'chunlei', 'clienttype':'0',
            'web':'1', 'num':'100', 't':time.time(),
            'page':'1', 'dir': path,
            't':0.12579,
            'order':'time', 'desc':1, '_':time.time(),
        })
        logger.debug(list_url)
        rsp = urllib2.urlopen(list_url).read()

        logger.debug( rsp )
        self.file_list = json.loads(rsp)['list']
            
        now = time.time()
        filelist = []

        for f in self.file_list :
            if f['isdir'] == 1 :
                st = dict(st_mode=(S_IFDIR | 0755), st_nlink=2)
            else:
                st = dict(st_mode=(S_IFREG | 0755), st_nlink=1)
            st['st_size'] = int(f['size'])
            st['st_ctime'] = int(f['local_ctime'])
            st['st_mtime'] = int(f['local_mtime'])
            st['st_atime'] = int(f['server_ctime'])
            st['st_uid'] = 0
            st['st_gid'] = 0
            self.filest[f['path']] = st
            filelist.append(f['server_filename'])
        #     print f['fs_id'],f['server_filename'],f['isdir'],  f['size'],f['path']
        print filelist
        return filelist

    def get_bdstoken(self):
        url = 'http://pan.baidu.com/disk/home'
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req).read()
        login_tokenStr = '''FileUtils.bdstoken="(.*?)"'''
        login_tokenObj = re.compile(login_tokenStr,re.DOTALL)
        matched_objs = login_tokenObj.findall(rsp)

        if len(matched_objs) == 0:
            logger.info("Can't get bdstoken, Maybe login failed.")
            return False
        else:
            self.bdstoken = matched_objs[0]
            if self.bdstoken == '' :
                logger.info("Can't get bdstoken, Maybe login failed.")
                return False
            else :
                logger.debug(self.bdstoken)
                return True

    
    def upload_yunpan(self,filename,destdir):
        if self.bdstoken == '' :
            sys.exit(1)


        if self.BDUSS == '' :
            logger.info("login failed,please relogin")
            sys.exit(1)
        starttime = time.time()
        logger.debug(starttime)
        
        upload_file_url = 'http://c.pcs.baidu.com/rest/2.0/pcs/file?' + urllib.urlencode({'BDUSS':self.BDUSS,
                    'method':'upload', 'type':'tmpfile', 'app_id':'250528', })
        logger.debug(upload_file_url)

        # fields = []
        # files = [('Filedata', filename, open(filename, 'rb'))]

        # iterate and write chunk in a socket
        # content_type, body = MultipartFormdataEncoder().encode(fields, files)
        # headers = {
        #     'Content-Type': content_type,
        #     'Content-Length': str(len(body)),
        #     }
        # req = urllib2.Request(upload_file_url,body,headers=headers)
        # page = urllib2.urlopen(req)

        curl_command = [ 'curl', '-b', self.cookiename, '-F', "Filedata=@%s" % filename,
                    upload_file_url ]

        logger.debug(curl_command)

        from subprocess import Popen, PIPE
        process = Popen(curl_command, stdout=PIPE)
        result = process.stdout.read()

        process.wait()              # Wait for it to complete

        file_md5= json.loads(result)['md5']

        logger.debug("update website result string:%s",result)
        logger.debug("update file md5 sume:%s",file_md5)

        create_file_url = 'http://pan.baidu.com/api/create?' + urllib.urlencode({ 'a':'commit',
                            'channel':'chunlei', 'clienttype':'0', 'web':'1',
                            'bdstoken':self.bdstoken,
                        })
        logger.debug("create file file url:%s",create_file_url)


        post_data = urllib.urlencode( {
             'path':destdir + '/' + os.path.basename(filename),
            'isdir':'0',
            'size':os.stat(filename).st_size ,
            'block_list':"[\""+file_md5+"\"]",
            'method':'post',
            })
        urllib2.install_opener(self.opener)
        headers = {
            'Accept':'*/*', 'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'zh-CN,zh;q=0.8', 'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'pan.baidu.com', 'Origin':'http://pan.baidu.com',
            'Referer':'http://pan.baidu.com/disk/home',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest', }
        req = urllib2.Request(create_file_url,post_data,headers=headers)

        result = urllib2.urlopen(req).read()
        logger.debug( result )
        errno = json.loads(result)["errno"]
        if errno != 0 :
            logger.debug( errno )
            logger.info("create file failed")

        endtime = time.time()
        logger.debug(endtime)
        usedtime = endtime - starttime
        speed = json.loads(result)['size'] / usedtime
        logger.info( "It is used :%ds " % usedtime)
        logger.info( "speed :%dbyte/s " % speed)

        logger.info( "upload file to " + json.loads(result)['path'] )
        return file_md5

    def delete(self,filelist):
        
        delete_file_url = 'http://pan.baidu.com/api/filemanager?' + urllib.urlencode(
                        { 'channel':'chunlei',
                            'clienttype':'0',
                            'web':'1',
                            'opera':'delete',
                            'bdstoken':self.bdstoken,
                        })
        headers = {
            'Accept':'*/*', 'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'zh-CN,zh;q=0.8', 'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'pan.baidu.com', 'Origin':'http://pan.baidu.com',
            'Referer':'http://pan.baidu.com/disk/home',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest', }
        logger.debug(delete_file_url)
        logger.debug(filelist)
        post_data = urllib.urlencode( {
             'filelist': '["'+filelist+'"]'
            })
        logger.debug(post_data)
        req = urllib2.Request(delete_file_url,post_data,headers=headers)
        result = urllib2.urlopen(req).read()
        logger.info(result)

def main():
    import password
    user = password.user
    psw  = password.psw

    baidu = Baidu(user,psw)
    baidu.login()

    baidu.get_bdstoken()

    #baidu.delete(sys.argv[1])
    # baidu.list('/01.test')
    #sys.exit(0)

    import platform
    sysstr = platform.system()
    if(sysstr =="Windows"):
        filename = sys.argv[1].decode("gbk")
    else:
        filename = sys.argv[1]
    
    upload_md5 = baidu.upload_yunpan(filename,sys.argv[2])
    check_md5 = md5_file(sys.argv[1])
    if upload_md5 == check_md5 :
        print "upload check success"
    else:
        print "upload check failed"


if __name__ == '__main__':
    main()

