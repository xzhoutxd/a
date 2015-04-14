#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
from JHSBrandHour import JHSBrandHour

class JHSBrandItemLock():
    '''A class of brand get item islock'''
    def __init__(self, m, _q_type='l'):
        # 分布式主机标志
        self.m = m
        # 活动队列标志
        self.q_type = _q_type
        # 每小时抓取实例
        self.jhs_brandhour = JHSBrandHour(self.m,self.q_type)

    def antPageForItemlock(self):
        # item islock 
        self.jhs_brandhour.antPage()

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    args = sys.argv
    #args = ['JHSBrandItemLock','m']
    if len(args) < 2:
        print '#err not enough args for JHSBrandItemLock...'
        exit()
    # 是否是分布式中主机
    m = args[1]
    b = JHSBrandItemLock(m)
    b.antPageForItemlock()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

