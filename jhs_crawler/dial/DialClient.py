#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#sys.path.append('../')
#sys.path.append('../base')
import json
from socket import AF_INET, SOCK_STREAM, socket
import base.Common as Common
import base.Config as Config

class DialClient():
    ''' A class of Dial client, to send dial request '''
    def __init__(self):
        self.magic_num = Config.magic_num
        self.dial_ip   = Config.dial_ip
        self.dial_port = Config.dial_port
        self.dial_addr = (self.dial_ip, self.dial_port)
        
        self.client    = socket(AF_INET, SOCK_STREAM)
        self.client.settimeout(60)
        self.client.connect(self.dial_addr)
        self.bufsize   = 1024

    def __del__(self):
        self.client.close()

    def buildMsg(self, _content):
        _module, _ip, _tag = _content
        msg_d = {}
        msg_d['magic']  = self.magic_num
        msg_d['module'] = _module
        msg_d['ip']     = _ip
        msg_d['tag']    = _tag
        s = json.dumps(msg_d)
        return s
 
    def send(self, _content):
        s = self.buildMsg(_content)
        try:
            self.client.sendall(s)
        except Exception as e:
            print '# DailClient send exception 1 times ', e
            self.client.close()
            self.client = socket(AF_INET, SOCK_STREAM)
            self.client.connect(self.dial_addr)
            try:
                self.client.sendall(s)
            except Exception as e:        
                print '# DailClient send exception 2 times ', e

    def recv(self):
        return self.client.recv(self.bufsize)  

if __name__ == "__main__":
    args = sys.argv
    args = ['DialClient', '3_act', '192.168.1.110', 'ikuai']
    if len(args) < 3:
        print 'python DialClient module ip tag'
        exit()

    # 处理输入参数
    _module, _ip, _tag = args[1], args[2], args[3]
    print '# DialClient :',  _module, _ip, _tag

    c = DialClient()
    c_time = Common.now_ss() 
    c.send((_module, _ip, _tag))
    #r = c.recv(); print r
