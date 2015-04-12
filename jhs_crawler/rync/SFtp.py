#-*- coding:utf-8 -*-
#!/usr/bin/env python

import os
import paramiko

class SFtp():
    """Sftp Class for sftp host"""
    def __init__(self):
        self.ip   = None
        self.port = 22
        self.user = None
        self.password = None

        # sftp
        self.t    = None
        self.sftp = None
        
        # ssh
        self.ssh  = None

    def initSFtp(self, ip, user, passwd, port=22):
        self.ip   = ip
        self.port = port
        self.user = user
        self.password = passwd

    @staticmethod
    def createPath(p):
        if not os.path.exists(p): os.mkdir(p)

    def sftpConnect(self):
        print "# To connect host %s" %self.ip
        self.t    = paramiko.Transport((self.ip, self.port))
        self.t.connect(username=self.user, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.t)

    def sftpMget(self, node_name, rem_path, loc_path):
        fs = self.sftp.listdir(rem_path)
        for f in fs:
            rem_file = '%s/%s' %(rem_path, f)
            loc_file = '%s/%s_%s' %(loc_path, node_name, f)
            self.sftpGet(rem_file, loc_file)

    def sftpGet(self, rem_file, loc_file):
        print "# To get file from %s to %s" % (rem_file, loc_file)
        self.sftp.get(rem_file, loc_file)

    def sftpPut(self, loc_file, rem_file):
        print "# to put file from loc_file %s to rem_file %s" % (loc_file, rem_file)
        self.sftp.put(loc_file, rem_file)

    def sftpClose(self):
        self.t.close()

# if __name__ == '__main__':
#     s = SFtp()
#     
#     s.initSFtp('192.168.7.1', 'netdata', 'nd!@#$%^')
#     s.sftpConnect()
#     rem_path  = '/home/netdata/data/qzj/20141111'
#     
#     loc_path  = '../../../data/qzj/temp/20141111'; s.createPath(loc_path)
#     loc_path += '/sp01'; s.createPath(loc_path)
# 
#     s.sftpMget(rem_path, loc_path)
#     s.sftpClose()
