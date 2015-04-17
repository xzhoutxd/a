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

class JHSBrandDay():
    '''A class of brand for every day'''
    def __init__(self, m_type, _q_type='d'):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # brand queue
        self.brand_queue = JHSBrandQ()

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()

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
            a_val = (self.begin_time,)
            self.brand_queue.brandQ(self.q_type, a_val)
        except Exception as e:
            Common.traceback_log()

    # 清理每小时抓取活动列表 配置活动的redis队列
    def brandHourList(self):
        # 当前时刻减去24小时
        val = (Common.add_hours(self.crawling_time, -24),) 
        print '# day need delete time:',val
        # 删除已经结束的活动
        delete_results  = self.mysqlAccess.selectDeleteJhsActDayalive(val)
        if delete_results:
            print '# day need delete act num: ',len(delete_results)
            for delete_r in delete_results:
                print '# day need delete act: id:%s,name:%s'%(str(delete_r[0]),str(delete_r[3]))
        else:
            print '# day need delete act num is null...'
        self.mysqlAccess.deleteJhsActDayalive(val)

        # 查找需要每天统计的活动列表
        #val = (Common.time_s(self.crawling_time),Common.add_hours(self.crawling_time, -24))
        val = (Common.today_s()+" 00:00:00",Common.add_hours(self.crawling_time, -24))
        print '# day crawler time:',val
        act_results = self.mysqlAccess.selectJhsActDayalive(val)
        if act_results:
            print '# day act num:',len(act_results)
        else:
            print '# day act not found..'
        
        all_item_num = 0
        # 商品默认信息列表
        crawl_val_list = []
        for act_r in act_results:
            #if int(act_r[1]) not in Config.default_catids_day: continue
            # 按照活动Id找出商品信息
            item_results = self.mysqlAccess.selectJhsItemsDayalive((str(act_r[0]),))
            if item_results:
                print "# act id:%s name:%s Items num:%s"%(str(act_r[0]),str(act_r[3]),str(len(item_results)))
                if len(item_results) > 0:
                    crawl_val_list.append((act_r[0],act_r[3],item_results))
                all_item_num += len(item_results)
            else:
                print '# day act id:%s name:%s not find items...'%(str(act_r[0]),str(act_r[3]))

        print '# day all item nums:',all_item_num
        # 清空每天活动redis队列
        self.brand_queue.clearBrandQ(self.q_type)
        # 保存每天活动redis队列
        self.brand_queue.putBrandlistQ(self.q_type, crawl_val_list)
        print '# brand queue end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def antPageForGiveup(self, crawl_val_list):
        try:
            # 多线程抓商品
            self.run_brandItems(crawl_val_list)
        except Exception as e:
            print '# exception err in antPage info:',e


if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    args = sys.argv
    #args = ['JHSBrandDay','m|s']
    if len(args) < 2:
        print '#err not enough args for JHSBrandDay...'
        exit()
    # 是否是分布式中主机
    m_type = args[1]
    b = JHSBrandDay(m_type)
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

