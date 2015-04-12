#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
import random
import json
import time
import Queue
import traceback
import base.Common as Common
import base.Config as Config

# 写html文件
def writeLog(pages):
    #path = os.getcwd()
    #print path
    #os.mkdir("file")
    #pages = self.outItemLog()
    for page in pages:
        filepath = Config.pagePath + page[2]
        if not os.path.exists(filepath):
            os.mkdir(filepath)
        filename = filepath + page[0]
        fout = open(filename, 'w')
        fout.write(page[3])
        fout.close()

if __name__ == '__main__':
    pages = [('12312_act-home_ad.htm','act-home','12312_act/','123456twrf23r32'),('12312_act-home-floor1_ada.htm','act-home-floor1','12312_act/','qqweqw123456twrf23r32')]
    writeLog(pages)
    



