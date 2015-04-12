#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import traceback
import threading
import base.Common as Common
import base.Config as Config
#from db.MysqlAccess import MysqlAccess
from JHSBrandTEMP import JHSBrandTEMP

class testItem():
    '''A class of test item'''
    def __init__(self):
        # mysql
        #self.mysqlAccess = MysqlAccess()
        # 页面模板解析
        self.brand_temp = JHSBrandTEMP()

    def test(self):
        fout = open('brand.htm', 'r')
        page = fout.read()
        fout.close()
        top_brands = self.brand_temp.activityTopbrandTemp(page)
        print top_brands

if __name__ == '__main__':
    t = testItem()
    t.test()


