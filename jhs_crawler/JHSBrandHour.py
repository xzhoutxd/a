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

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()
        self.page_datepath = time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_time))

        # 每小时抓取的时间区间
        self.min_hourslot = 0 # 最小时间段
        self.max_hourslot = -24 # 最大时间段

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
                    print '# hour need delete act: id:%s,name:%s'%(str(delete_r[0]),str(delete_r[3]))
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
                    index = int(Common.subTS_hours(self.crawling_time, starttime_TS)) + 1
                    soldcount_name = 'item_soldcount_h%d'%index
                    hour_index = str(index)
                    # 按照活动Id找出商品信息
                    item_results = self.mysqlAccess.selectJhsItemsHouralive((str(act_r[0]),))
                    if item_results:
                        print '# act id:%s name:%s starttime:%s endtime:%s Items num:%s hour_index:%s'%(str(act_r[0]),str(act_r[3]),str(act_r[5]),str(act_r[6]),str(len(item_results)),hour_index)
                        if len(item_results) > 0:
                            item_val_list = []
                            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            for item in item_results:
                                item = item + (self.begin_time,hour_index)
                                item_val_list.append(item)
                            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            crawler_val_list.append((hour_index,act_r[0],act_r[3],item_val_list))
                    else:
                        print '# hour act id:%s name:%s not find items...'%(str(act_r[0]),str(act_r[3]))

            # 多线程抓商品
            self.run_brandItems(crawler_val_list)
        except Exception as e:
            print '# exception err in antPage info:',e
            print '#####--Traceback Start--#####'
            tp,val,td = sys.exc_info()
            for file, lineno, function, text in traceback.extract_tb(td):
                print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                print text
            print "exception traceback err:%s,%s,%s"%(tp,val,td)
            print '#####--Traceback End--#####'

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list):
        for crawler_val in crawler_val_list:
            hour_index, brandact_id, brandact_name, item_valTuple = crawler_val
            print '# hour activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name

            # 附加的信息
            a_val = (self.begin_time, hour_index)
            # 多线程 控制并发的线程数
            if len(item_valTuple) > Config.item_max_th:
                m_itemsObj = JHSItemM(3, Config.item_max_th, a_val)
            else:
                m_itemsObj = JHSItemM(3, len(item_valTuple), a_val)
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()
            print '# hour activity Items update end: actId:%s, actName:%s'%(brandact_id, brandact_name)

            """
            while True:
                try:
                    print '# hour item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
                    if m_itemsObj.empty_q():
                        item_list = m_itemsObj.items
                        for item in item_list:
                            item_sold, item_stock = item
                            soldcount_name = 'item_soldcount_h%s'%hour_index
                            soldcount_val = (soldcount_name,) + item_sold
                            if item_sold[0]:
                                self.mysqlAccess.updateJhsItemSoldcountForHour(soldcount_val)
                            else:
                                print '# hour item sold count is none: ',soldcount_val
                            stock_name = 'item_stock_h%s'%hour_index
                            stock_val = (stock_name,) + item_stock
                            if item_stock[0]:
                                self.mysqlAccess.updateJhsItemStockForHour(stock_val)
                            else:
                                print '# hour item stock is none: ',stock_val
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
            """

    def run(self, val):
        item = JHSItem()
        item.antPageHour(val)
        return item.outUpdateTupleHour()



if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandHour()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

