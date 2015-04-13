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
    def __init__(self):
        self.jhs_brandhour = JHSBrandHour()

    def antPageForItemlock(self):
        # item islock 
        self.jhs_brandhour.antPage(5)

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandItemLock()
    b.antPageForItemlock()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

