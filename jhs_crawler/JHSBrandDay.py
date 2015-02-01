#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import Queue
import traceback
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler
from db.MysqlAccess import MysqlAccess
from JHSItemM import JHSItemM

class JHSBrandDay():
    '''A class of brand for every day'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler    = TBCrawler()

        # 商品抓取队列
        self.itemcrawler_queue = Queue.Queue()

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()
        # 并发线程值
        self.item_max_th = 40 # 商品抓取时的最大线程

    def antPage(self):
        try:
            # 当前时刻减去24小时
            val = (Common.add_hours(self.crawling_time, -24))
            print '# day crawler time:',val
            # 删除已经结束的活动
            self.mysqlAccess.deleteJhsActDayalive(val)
            # 查找需要每天统计的活动列表
            act_results = self.mysqlAccess.selectJhsActDayalive(val)
            print '# day act num:',len(act_results)
            
            # 商品默认信息列表
            crawler_val_list = []
            for act_r in act_results:
                # 按照活动Id找出商品信息
                item_results = self.mysqlAccess.selectJhsItemsDayalive((act_r[0]))
                print "# act id:%s name:%s Items num:%s"%(str(act_r[0]),str(act_r[1]),str(len(item_results)))
                if len(item_results) > 0:
                    crawler_val_list.append((act_r[0],act_r[1],item_results))

            # 多线程抓商品
            self.run_brandItems(crawler_val_list)
        except Exception as e:
            print '# exception err in antPage info:',e

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list):
        for crawler_val in crawler_val_list:
            brandact_id, brandact_name, item_valTuple = crawler_val
            print '# day activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name
            # 多线程 控制并发的线程数
            if len(item_valTuple) > self.item_max_th:
                m_itemsObj = JHSItemM(1, self.item_max_th)
            else:
                m_itemsObj = JHSItemM(1, len(item_valTuple))
            #item_valTuple = item_valTuple + (self.begin_date,self.begin_hour)
            #print item_valTuple
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()

            while True:
                try:
                    print '# day item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
                    if m_itemsObj.empty_q():
                        item_list = m_itemsObj.items
                        for item in item_list:
                            item = item + (self.begin_date,self.begin_hour)
                            self.mysqlAccess.insertJhsItemForDay(item)
                            #print item
                        print '# day activity Items crawler end: actId:%s, actName:%s'%(brandact_id, brandact_name)
                        break
                except Exception as e:
                    print 'Unknown exception item for day result :', e
                    #traceback.print_exc()
                    print '#####--Traceback Start--#####'
                    tp,val,td = sys.exc_info()
                    for file, lineno, function, text in traceback.extract_tb(td):
                        print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                        print text
                    print "exception traceback err:%s,%s,%s"%(tp,val,td)
                    print '#####--Traceback End--#####'
                    break


if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandDay()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

