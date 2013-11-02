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

class MultipartFormdataEncoder(object):
    def __init__(self):
        self.boundary = uuid.uuid4().hex
        self.content_type = 'multipart/form-data; boundary={}'.format(self.boundary)

    @classmethod
    def u(cls, s):
        if sys.hexversion < 0x03000000 and isinstance(s, str):
            s = s.decode('utf-8')
        if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
            s = s.decode('utf-8')
        return s

    def iter(self, fields, files):
        """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, file-type) elements for data to be uploaded as files
        Yield body's chunk as bytes
        """
        encoder = codecs.getencoder('utf-8')
        for (key, value) in fields:
            key = self.u(key)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"\r\n').format(key))
            yield encoder('\r\n')
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            yield encoder(self.u(value))
            yield encoder('\r\n')
        for (key, filename, fd) in files:
            key = self.u(key)
            filename = self.u(filename)
            yield encoder('--{}\r\n'.format(self.boundary))
            yield encoder(self.u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
            yield encoder('Content-Type: {}\r\n'.format(mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
            yield encoder('\r\n')
            with fd:
                buff = fd.read()
                yield (buff, len(buff))
            yield encoder('\r\n')
        yield encoder('--{}--\r\b'.format(self.boundary))

    def encode(self, fields, files):
        body = io.BytesIO()
        for chunk, chunk_len in self.iter(fields, files):
            body.write(chunk)
        return self.content_type, body.getvalue()


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

        self.allCount  = 0
        self.pageSize  = 10
        self.totalpage = 0

        self.logined = False
        self.cj = cookielib.LWPCookieJar()
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
        #如果没有获取到cookie，就模拟登陆一下
        if not self.logined:
            
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
                                        'charset':'utf-8',
                                        'tpl':'yun',
                                        'apiver':'v3',
                                        'tt':'1383185233025',
                                        'codestring':'',
                                        'isPhone':'false',
                                        'safeflg':'0',
                                        'u':'http://yun.baidu.com/',
                                        'quick_user':'0',
                                        'logintype':'basicLogin',
                                        'verifycode':'',
                                        'mem_pass':'on',
                                        'ppui_logintime':'25955',
                                        'callback':'parent.bd__pcbs__a8jd5z'
                                            })
                #path = 'http://passport.baidu.com/?login'
                path = 'https://passport.baidu.com/v2/api/?login'
                self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
                self.opener.addheaders = []
                urllib2.install_opener(self.opener)
                headers = {"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                        "Accept-Language":"zh-CN,zh;q=0.8",
                        "Cache-Control":"max-age=0",
                        "Connection":"keep-alive",
                        "Content-Length":"394",
                        "Host":"passport.baidu.com",
                        "Origin":"http://yun.baidu.com",
                        "Referer":"http://yun.baidu.com/",
                        "User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",

                }
                req = urllib2.Request(path,
                                post_data,
                                headers=headers,
                                )
                rsp = self.opener.open(req).read()
                logger.debug( rsp )
                if not "err_no=0" in rsp:
                    logger.info("Maybe Login failed!!")
                
                self.cj.save(self.cookiename)
            else:
                logger.info( "Can't get token" )
                logger.debug(rsp)
                sys.exit(0)

    #获取每一页里的博客链接
    def fetchPage(self,url):
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req).read()
        print rsp
        
    def upload_yunpan(self,filename,destdir):
        
        for cookie in self.cj:
            logger.debug("%s -> %s", cookie.name, cookie.value)
            if cookie.name == 'BDUSS':
                BDUSS = cookie.value
                break
        if BDUSS == None :
            logger.info("login failed")
            sys.exit(1)
        starttime = time.time()
        logger.debug(starttime)
        upload_file_url = 'http://c.pcs.baidu.com/rest/2.0/pcs/file?'
        upload_file_url += urllib.urlencode({
                    'BDUSS':BDUSS,
                    'method':'upload',
                    'type':'tmpfile',
                    'app_id':'250528',
                    })
        logger.debug(upload_file_url)

        fields = []
        files = [('Filedata', filename, open(filename, 'rb'))]

        # iterate and write chunk in a socket
        content_type, body = MultipartFormdataEncoder().encode(fields, files)
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(body)),
            }
        req = urllib2.Request(upload_file_url,body,headers=headers)
        page = urllib2.urlopen(req)
        result = page.read()
        file_md5= json.loads(result)['md5']
        logger.debug("update website result string:%s",result)
        logger.debug("update file md5 sume:%s",file_md5)

        param = { 'a':'commit',
            'channel':'chunlei',
            'clienttype':'0',
            'web':'1',
            'bdstoken':self.bdstoken,
        }
        create_file_url = 'http://pan.baidu.com/api/create?'
        create_file_url += urllib.urlencode(param)
        logger.debug("create file file url:%s",create_file_url)


        post_data = urllib.urlencode( {
             'path':destdir + os.path.basename(filename),
            'isdir':'0',
            'size':os.stat(filename).st_size ,
            'block_list':"[\""+file_md5+"\"]",
            'method':'post',
            })
        urllib2.install_opener(self.opener)
        headers = {
            'Accept':'*/*',
            'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'pan.baidu.com',
            'Origin':'http://pan.baidu.com',
            'Referer':'http://pan.baidu.com/disk/home',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest', }
        req = urllib2.Request(create_file_url,post_data,headers=headers)

        page = urllib2.urlopen(req)
        result = page.read()
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


    def get_bdstoken(self):
        url = 'http://pan.baidu.com/disk/home'
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req).read()
        login_tokenStr = '''FileUtils.bdstoken="(.*?)"'''
        login_tokenObj = re.compile(login_tokenStr,re.DOTALL)
        matched_objs = login_tokenObj.findall(rsp)
        self.bdstoken = matched_objs[0]
        logger.debug(self.bdstoken)
        if self.bdstoken == '':
            logger.info("Can't get bdstoken, Maybe login failed.")
 
def main():
    import password
    user = password.user
    psw  = password.psw

    baidu = Baidu(user,psw)
    baidu.login()
    baidu.get_bdstoken()
    upload_md5 = baidu.upload_yunpan(sys.argv[1].decode("gbk"),sys.argv[2])
    check_md5 = md5_file(sys.argv[1])
    if upload_md5 == check_md5 :
        print "upload check success"
    else:
        print "upload check failed"


if __name__ == '__main__':
    main()

