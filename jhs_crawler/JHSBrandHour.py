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
import base.Common as Common
import base.Config as Config
from db.MysqlAccess import MysqlAccess
from JHSBrandQ import JHSBrandQ

class JHSBrandHour():
    '''A class of brand for every hour'''
    def __init__(self, m_type, _q_type='h'):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # brand queue
        self.brand_queue = JHSBrandQ()

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

        # 每小时抓取的时间区间
        self.min_hourslot = 0 # 最小时间段
        self.max_hourslot = -24 # 最大时间段

        # 分布式主机标志
        self.m_type = m_type
        # 活动队列标志
        self.q_type = _q_type

    def antPage(self):
        try:
            # 主机器需要配置redis队列
            if self.m_type == 'm':
                self.brandHourList()
            # 附加信息
            a_val = (self.begin_time, self.begin_hour)
            self.brand_queue.brandQ(self.q_type, a_val)
        except Exception as e:
            Common.traceback_log()

    # 清理每小时抓取活动列表 配置活动的redis队列
    def brandHourList(self):
        if self.q_type == 'h':
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
        
        # 商品默认信息列表
        all_item_num = 0
        crawl_val_list = []
        for act_r in act_results:
            #if int(act_r[1]) not in Config.default_catids: continue
            # 按照活动Id找出商品信息
            item_results = self.mysqlAccess.selectJhsItemsHouralive((str(act_r[0]),))
            if item_results:
                print '# act id:%s name:%s starttime:%s endtime:%s Items num:%s hour_index:%s'%(str(act_r[0]),str(act_r[3]),str(act_r[5]),str(act_r[6]),str(len(item_results)),str(self.begin_hour))
                if len(item_results) > 0:
                    crawl_val_list.append((act_r[0],act_r[3],item_results))
                all_item_num += len(item_results)
            else:
                print '# hour act id:%s name:%s not find items...'%(str(act_r[0]),str(act_r[3]))
        print '# hour all item nums:',all_item_num
        # 清空每小时活动redis队列
        self.brand_queue.clearBrandQ(self.q_type)
        # 保存每小时活动redis队列
        self.brand_queue.putBrandlistQ(self.q_type, crawl_val_list)
        print '# brand queue end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    args = sys.argv
    #args = ['JHSBrandHour','m']
    if len(args) < 2:
        print '#err not enough args for JHSBrandHour...'
        exit()
    # 是否是分布式中主机
    m_type = args[1]
    b = JHSBrandHour(m_type)
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

