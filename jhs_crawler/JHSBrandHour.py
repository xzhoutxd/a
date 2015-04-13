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
from db.MysqlAccess import MysqlAccess
from JHSItemM import JHSItemM
from JHSItem import JHSItem

class JHSBrandHour():
    '''A class of brand for every hour'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

        # 每小时抓取的时间区间
        self.min_hourslot = 0 # 最小时间段
        self.max_hourslot = -24 # 最大时间段

    def anPageForItemlock(self):
        # item islock 
        self.antPage(4)

    def antPage(self, item_type=3):
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
            all_item_num = 0
            crawler_val_list = []
            for act_r in act_results:
                #if int(act_r[1]) not in Config.default_catids: continue
                # 按照活动Id找出商品信息
                item_results = self.mysqlAccess.selectJhsItemsHouralive((str(act_r[0]),))
                if item_results:
                    print '# act id:%s name:%s starttime:%s endtime:%s Items num:%s hour_index:%s'%(str(act_r[0]),str(act_r[3]),str(act_r[5]),str(act_r[6]),str(len(item_results)),str(self.begin_hour))
                    if len(item_results) > 0:
                        crawler_val_list.append((act_r[0],act_r[3],item_results))
                    all_item_num += len(item_results)
                else:
                    print '# hour act id:%s name:%s not find items...'%(str(act_r[0]),str(act_r[3]))
            print '# hour all item nums:',all_item_num

            # 多线程抓商品
            self.run_brandItems(crawler_val_list,item_type)
        except Exception as e:
            Common.traceback_log()

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list, item_type):
        for crawler_val in crawler_val_list:
            brandact_id, brandact_name, item_valTuple = crawler_val
            print '# hour activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name

            # 附加的信息
            a_val = (self.begin_time, self.begin_hour)
            # 多线程 控制并发的线程数
            if len(item_valTuple) > Config.item_max_th:
                m_itemsObj = JHSItemM(item_type, Config.item_max_th, a_val)
            else:
                m_itemsObj = JHSItemM(item_type, len(item_valTuple), a_val)
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()
            print '# hour activity Items update end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),brandact_id, brandact_name


if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandHour()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

