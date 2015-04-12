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
from db.MysqlAccess import MysqlAccess
from JHSItem import JHSItem

class testItem():
    '''A class of test item'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

    def test(self):
        item = JHSItem()
        begin_time = Common.now()
        #url = 'http://detail.ju.taobao.com/home.htm?id=10000006139344&amp;item_id=41577218730'
        #item_id = '41577218730'
        #ju_id = '10000006139344'

        #url = 'http://detail.ju.taobao.com/home.htm?id=10000006179624&amp;item_id=43876136248'
        #item_id = '43876136248'
        #ju_id = '10000006179624'

        url = 'http://detail.ju.taobao.com/home.htm?id=10000006194343&item_id=39105724540'
        item_id = '39105724540'
        ju_id = '10000006194343'

        url = 'http://detail.ju.taobao.com/home.htm?id=10000006177132&amp;item_id=38397053227'
        item_id = '38397053227'
        ju_id = '10000006177132'

        """
        # info
        _val = ('', '', '', '', 1, url, item_id, ju_id, '', begin_time, '', '')
        item = JHSItem()
        item.antPage(_val)
        #_iteminfosql_list = []
        #iteminfoSql = item.outTuple()
        #print iteminfoSql
        #_iteminfosql_list.append(iteminfoSql)
        #self.mysqlAccess.insertJhsItemInfo(_iteminfosql_list)
        #print item.item_juName,item.item_juDesc,',',item.item_sellerName
        """

        """
        # day
        #self.item_juId,self.item_actId,self.item_actName,self.item_act_url,self.item_juName,self.item_ju_url,self.item_id,self.item_url,self.item_oriPrice,self.item_actPrice,self.crawling_begintime = val
        _val = (ju_id,'','','','',url,item_id,'','','',begin_time)
        item.antPageDay(_val)
        """

        # hour
        _val = (ju_id,'',url,'',item_id,begin_time,1)
        item.antPageHour(_val)
        print item.crawler.history,len(item.crawler.history)
        #self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime,self.hour_index = val

        """
        # update remind
        _val = (ju_id,'',url,'',item_id,begin_time)
        item.antPageUpdateRemind(_val)
        #self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime = val
        """


if __name__ == '__main__':
    t = testItem()
    t.test()


