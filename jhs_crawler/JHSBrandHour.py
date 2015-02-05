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
from multiprocessing.dummy import Pool as ThreadPool
from JHSItem import JHSItem

class JHSBrandHour():
    '''A class of brand for every hour'''
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
        self.page_datepath = time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_time))

        # 并发线程值
        self.item_max_th = 10 # 商品抓取时的最大线程

        # 每小时抓取的时间区间
        self.min_hourslot = -1 # 最小时间段
        self.max_hourslot = -25 # 最大时间段

    def antPage(self):
        try:
            # 得到需要删除的时间点
            val = (Common.add_hours(self.crawling_time, self.max_hourslot),)
            print '# hour need delete time:',val
            # 删除已经超过时间段的活动
            delete_results = self.mysqlAccess.selectDeleteJhsActHouralive(val)
            if delete_results:
                print '# hour need delete act num: ',len(delete_results)
                for delete_r in delete_results:
                    print '# hour need delete act: id:%s,name:%s'%(str(delete_r[0]),str(delete_r[1]))
            else:
                print '# hour need delete act is null...'
            self.mysqlAccess.deleteJhsActHouralive(val)
            # 查找需要每小时统计的活动列表
            # 得到需要的时间段
            val = (Common.add_hours(self.crawling_time, self.min_hourslot), Common.add_hours(self.crawling_time, self.max_hourslot))
            print '# hour crawler time:',val
            act_results = self.mysqlAccess.selectJhsActHouralive(val)
            if act_results:
                print '# hour act num:',len(act_results)
            else:
                print '# hour act not found..'
                return None
            
            # 商品默认信息列表
            crawler_val_list = []
            for act_r in act_results:
                # 只抓时尚女士,精品男士
                if int(act_r[1]) == 261000 or int(act_r[1]) == 262000:
                    starttime_TS = time.mktime(time.strptime(str(act_r[5]), "%Y-%m-%d %H:%M:%S"))
                    index = int(Common.subTS_hours(self.crawling_time, starttime_TS))
                    soldcount_name = 'item_soldcount_h%d'%index
                    # 按照活动Id找出商品信息
                    item_results = self.mysqlAccess.selectJhsItemsHouralive((str(act_r[0]),))
                    if item_results:
                        print '# act id:%s name:%s starttime:%s endtime:%s Items num:%s soldcountName:%s'%(str(act_r[0]),str(act_r[3]),str(act_r[5]),str(act_r[6]),str(len(item_results)),soldcount_name)
                        if len(item_results) > 0:
                            crawler_val_list.append((soldcount_name,act_r[0],act_r[3],item_results))
                    else:
                        print '# hour act id:%s name:%s not find items...'%(str(act_r[0]),str(act_r[3]))

            # 多线程抓商品
            self.run_brandItems(crawler_val_list)
        except Exception as e:
            print '# exception err in antPage info:',e

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list):
        for crawler_val in crawler_val_list:
            soldcount_name, brandact_id, brandact_name, item_valTuple = crawler_val
            print '# hour activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name

            """
            # 多线程方式(1)
            # multiprocessing.dummy Pool
            pool = ThreadPool(50)
            item_list = pool.map(self.run,item_valTuple)
            pool.close()
            pool.join()
            
            try:
                print '# hour item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
                for item in item_list:
                    val = (soldcount_name,) + item
                    self.mysqlAccess.updateJhsItemSoldcountForHour(val)
                print '# hour activity Items update end: actId:%s, actName:%s'%(brandact_id, brandact_name)
            except Exception as e:
                print '# exception error item for hour result :', e
                traceback.print_exc()
            """
            # 多线程 控制并发的线程数
            if len(item_valTuple) > self.item_max_th:
                m_itemsObj = JHSItemM(2, self.item_max_th)
            else:
                m_itemsObj = JHSItemM(2, len(item_valTuple))
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()

            while True:
                try:
                    print '# hour item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
                    if m_itemsObj.empty_q():
                        item_list = m_itemsObj.items
                        for item in item_list:
                            val = (soldcount_name,) + item
                            self.mysqlAccess.updateJhsItemSoldcountForHour(val)
                        print '# hour activity Items update end: actId:%s, actName:%s'%(brandact_id, brandact_name)
                        break
                except Exception as e:
                    print '# exception error item for hour result :', e
                    #traceback.print_exc()
                    print '#####--Traceback Start--#####'
                    tp,val,td = sys.exc_info()
                    for file, lineno, function, text in traceback.extract_tb(td):
                        print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                        print text
                    print "exception traceback err:%s,%s,%s"%(tp,val,td)
                    print '#####--Traceback End--#####'
                    break

    def run(self, val):
        item = JHSItem()
        item.antPageHour(val)
        return item.outUpdateTupleHour()



if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandHour()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

