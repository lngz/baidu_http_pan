#!/usr/bin/env python
from baiduyun import Baidu
from sys import argv, exit
from time import time


from fuse import FUSE, Operations, LoggingMixIn


class baidufs(LoggingMixIn, Operations):
    '''
    A simple baidufs filesystem. Requires paramiko: http://www.lag.net/paramiko/

    You need to be able to login to remote host without entering a password.
    '''

    def __init__(self,  path='.'):
        import password
        user = password.user
        psw  = password.psw

        self.baidu = Baidu(user,psw)
        self.baidu.login()
        self.baidu.get_bdstoken()

    def chmod(self, path, mode):
        pass

    def chown(self, path, uid, gid):
        pass

    # def create(self, path, mode):
    #     f = self.sftp.open(path, 'w')
    #     f.chmod(mode)
    #     f.close()
    #     return 0

    # def destroy(self, path):
    #     self.sftp.close()
    #     self.client.close()

    def getattr(self, path, fh=None):
        if path not in self.baidu.filest:
            now = time.time()
            return dict(st_mode=(S_IFDIR | 0755), st_ctime=now,
                               st_mtime=now, st_atime=now, st_nlink=2)
        print path,'-------'
        st = self.baidu.filest[path]
        return st

    # def mkdir(self, path, mode):
    #     return self.sftp.mkdir(path, mode)

    # def read(self, path, size, offset, fh):
    #     f = self.sftp.open(path)
    #     f.seek(offset, 0)
    #     buf = f.read(size)
    #     f.close()
    #     return buf

    def readdir(self, path, fh):
        return ['.', '..'] + self.baidu.list(path)

    # def readlink(self, path):
    #     return self.sftp.readlink(path)

    # def rename(self, old, new):
    #     return self.sftp.rename(old, self.root + new)

    # def rmdir(self, path):
    #     return self.sftp.rmdir(path)

    # def symlink(self, target, source):
    #     return self.sftp.symlink(source, target)

    # def truncate(self, path, length, fh=None):
    #     return self.sftp.truncate(path, length)

    # def unlink(self, path):
    #     return self.sftp.unlink(path)

    # def utimens(self, path, times=None):
    #     return self.sftp.utime(path, times)

    # def write(self, path, data, offset, fh):
    #     f = self.sftp.open(path, 'r+')
    #     f.seek(offset, 0)
    #     f.write(data)
    #     f.close()
    #     return len(data)


if __name__ == '__main__':
    if len(argv) != 2:
        print('usage: %s  <mountpoint>' % argv[0])
        exit(1)

    fuse = FUSE(baidufs(), argv[1], foreground=True, nothreads=True)
