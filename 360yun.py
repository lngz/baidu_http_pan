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


class yun360(object):
    def __init__(self,user = '', psw = ''):
        self.user = user
        self.psw  = psw

        if not user or not psw :
            print "Plz enter enter 2 params:user,psw"
            sys.exit(0)


        self.cookiename = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'cookie360%s' % (self.user)
        self.token = ''
        self.bdstoken = ''

        self.allCount  = 0
        self.pageSize  = 10
        self.totalpage = 0

        self.logined = False
        self.cj = cookielib.MozillaCookieJar()
        try:
            self.cj.revert(self.cookiename,ignore_discard=True,ignore_expires=True)
            self.logined = True
            logger.info('Load cookie from file')

        except Exception,e:
            logger.info("Can't load cookie from file")

        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36')]
        urllib2.install_opener(self.opener)

        #socket.setdefaulttimeout(60)

    #登陆百度
    def login(self):
        #如果没有获取到cookie，就模拟登陆一下
        if not self.logined:
            
            #第一次访问一下，目的是为了先保存一个cookie下来
            qurl = '''http://360.cn'''
            r = self.opener.open(qurl)
            self.cj.save(self.cookiename,ignore_discard=True,ignore_expires=True)

            #第二次访问，目的是为了获取token
            qurl = '''https://login.360.cn/?'''
            qurl += urllib.urlencode({'callback':'QiUserJsonP1383703030590',
                    'func':'QHPass.loginUtils.tokenCallback',
                    'm':'getToken',
                    'o' :  'sso',
                    'rand':    0.13556829378752877,
                    'userName' :   self.user,
                    })
            
            r = self.opener.open(qurl)
            rsp = r.read()
            print rsp
            self.cj.save(self.cookiename,ignore_discard=True,ignore_expires=True)

            #通过正则表达式获取token
            login_tokenStr = '''token":"(.*?)"'''
            login_tokenObj = re.compile(login_tokenStr,re.DOTALL)
            matched_objs = login_tokenObj.findall(rsp)
            if matched_objs:
                self.token = matched_objs[0]
                logger.debug( self.token )
                login_url = 'https://login.360.cn/?'
                login_url += urllib.urlencode({
                    'callback' :   'QiUserJsonP1383703030591',
                    'captCode' :   '',
                    'captFlag' :   '1',
                    'captId' : 'i360',
                    'from'   : 'pcw_cloud',
                    'func'   : 'QHPass.loginUtils.loginCallback',
                    'isKeepAlive': 0,
                    'm'  : 'login',
                    'o'  : 'sso',
                    'password'  :  hashlib.md5(self.psw).hexdigest(),
                    'pwdmethod' :  1,
                    'r' :  time.time(),
                    'rtype' :  'data',
                    'token'  : self.token,
                    'userName' :   self.user,
                    })
                r = self.opener.open(login_url)
                rsp = r.read()
                #print rsp
                self.cj.save(self.cookiename,ignore_discard=True,ignore_expires=True)



                login_url = 'http://yunpan.360.cn/user/login?st=187'
                r = self.opener.open(login_url)
                # rsp = r.read()
                # print rsp
                self.cj.save(self.cookiename,ignore_discard=True,ignore_expires=True)
               
            else:
                logger.info( "Can't get token" )
                logger.debug(rsp)
                sys.exit(0)

    #获取每一页里的博客链接
    def fetchPage(self,url):
        req = urllib2.Request(url)
        rsp = urllib2.urlopen(req).read()
        print rsp
        


    def list(self, path='/'):
        file_list = 'http://c18.yunpan.360.cn/file/list'
        r = self.opener.open(file_list)
        rsp = r.read()
        print rsp
        #self.cj.save(self.cookiename)

        

    def upload_yunpan(self,filename,destdir):
        
        starttime = time.time()
        logger.debug(starttime)
        upload_file_url = 'http://c18.yunpan.360.cn/upload/getuploadaddress/'
        
        logger.debug(upload_file_url)

        post_data = urllib.urlencode( {
            'ajax':1,
            })
        urllib2.install_opener(self.opener)
        headers = {
            'Accept':'*/*',
            'Accept-Language':'zh-CN,zh;q=0.8',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
            'X-Requested-With':'XMLHttpRequest', }
        req = urllib2.Request(upload_file_url,post_data,headers=headers)
        page = urllib2.urlopen(req)
        result = page.read()
        logger.debug(result)

        tk = json.loads(result)['data']['tk']
        up = json.loads(result)['data']['up']
        print tk,up

        for cookie in self.cj:
            logger.debug("%s -> %s", cookie.name, cookie.value)
            if cookie.name == 'token':
                token = cookie.value
                break


        fields = {('qid','376091399'),
                  (  'ofmt','json'),
                  (  'method','Upload.web'),
                  (  'token',token),
                  (  'v','1.01'),
                  (  'tk',tk),
                  (  'Upload','Submit Query'),
                  (  'devtype','web'),
                  (  'pid','ajax'),
                  (  'Filename',filename),
                  (  'path',destdir),

                }
        files = [('file', filename, open(filename, 'rb'))]

        # iterate and write chunk in a socket
        content_type, body = MultipartFormdataEncoder().encode(fields, files)
        headers = {
            'Content-Type': content_type,
            'Content-Length': str(len(body)),
            }
        upload_file_url = 'http://up18.yunpan.360.cn/webupload?devtype=web'
        req = urllib2.Request(upload_file_url,body,headers=headers)
        page = urllib2.urlopen(req)
        result = page.read()
        logger.debug( result)

        tk = json.loads(result)['data']['tk']

        create_file_url = 'http://c18.yunpan.360.cn/upload/addfile/'
        

        post_data = urllib.urlencode( {
             'ajax':'1',
            'tk':tk,
            })
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))

        urllib2.install_opener(self.opener)
        headers = {
         
            }
        req = urllib2.Request(create_file_url,post_data,headers=headers)

        page = urllib2.urlopen(req)
        result = page.read()
        logger.debug( result )
        print json.loads(result)['errmsg']
       

def main():
    import password
    user = password.user
    psw  = password.psw

    yun = yun360(user,psw)
    yun.login()
    yun.list()
    import platform
    sysstr = platform.system()
    if(sysstr =="Windows"):
        filename = sys.argv[1].decode("gbk")
    else:
        filename = sys.argv[1]
    
    yun.upload_yunpan(filename,sys.argv[2])
    

if __name__ == '__main__':
    main()

