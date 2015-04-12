#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../')
import re
import random
import json
import time
import traceback
import threading
import base.Common as Common
import base.Config as Config
#from db.MysqlAccess import MysqlAccess
from JHSBActItem import JHSBActItem

class testItem():
    '''A class of test item'''
    def __init__(self):
        pass
        # mysql
        #self.mysqlAccess = MysqlAccess()

    def test(self):
        item = JHSBActItem()
        #item.brandact_url = 'http://ju.taobao.com/tg/brand_items.htm?spm=608.7666661.floor7.45.o6UaqZ&act_sign_id=5577923'
        #item.brandact_url = 'http://ju.taobao.com/tg/brand_items.htm?spm=608.7666661.floor7.54.o6UaqZ&act_sign_id=5571938'
        #item.brandact_url = 'http://act.ju.taobao.com/market/ju/beibeipake0406.php'
        #item.brandact_url = 'http://act.ju.taobao.com/market/ju/pegperego0408.php'
        item.brandact_url = 'http://ju.taobao.com/jusp/nv/hjsh/tp.htm'
        # 品牌团页面html
        item.brandPage()

        # open file test
        #file_path = 'brand_test.htm'
        #fout = open(file_path, 'r')
        #page = fout.read()
        #fout.close()
        #item.brandact_url = 'http://act.ju.taobao.com/market/ju/pegperego.php'
        #item.brandact_page = page
        #print item.brandact_page
        # 活动页面商品
        item.brandActItems()
        print len(item.brandact_itemVal_list)

if __name__ == '__main__':
    t = testItem()
    t.test()


