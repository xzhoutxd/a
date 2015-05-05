#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import base.Common as Common
import base.Config as Config
from Jsonpage import Jsonpage
from JHSGroupItemWorker import JHSGroupItemWorker
from JHSItemQ import JHSItemQ
from JHSItemQ import JHSItemQM

class JHSGroupItemHour():
    '''A class of JHS group item hour sale'''
    def __init__(self, m_type, _q_type='h'):
        # 获取Json数据
        self.jsonpage = Jsonpage()

        self.worker = JHSGroupItemWorker()

        # 商品类型标志
        self.item_type = "groupitem"

        # item queue
        self.item_queue = JHSItemQ(self.item_type)

        # 分布式主机标志
        self.m_type = m_type
        # 队列标志
        self.q_type = _q_type

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

    def antPage(self):
        try:
            # 获取已经开团的商品
            hour_items = self.worker.scanAliveItems()
            if hour_items and len(hour_items) > 0:
                # 清空每小时商品redis队列
                self.item_queue.clearItemQ(self.q_type)
                # 保存每小时商品redis队列
                self.item_queue.putItemlistQ(self.q_type,hour_items)
                print '# groupitem hour queue end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            else:
                print '# groupitem not find hour items...'

            # 附加信息
            a_val = (self.begin_time, self.begin_hour)
            self.item_queue.itemQ(self.q_type, a_val)

            """
            m_itemQ = JHSItemQM(self.item_type, self.q_type, 10, a_val)
            m_itemQ.createthread()
            if hour_items and len(hour_items) > 0:
                # 清空每小时商品redis队列
                m_itemQ.clearItemQ()
                # 保存每小时商品redis队列
                m_itemQ.putItemlistQ(hour_items)
                print '# groupitem hour queue end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            else:
                print '# groupitem not find hour items...'
            m_itemQ.run()
            """
        except Exception as e:
            Common.traceback_log()

if __name__ == '__main__':
    args = sys.argv
    #args = ['JHSGroupItemHour','m']
    if len(args) < 2:
        print '#err not enough args for JHSGroupItemHour...'
        exit()
    # 是否是分布式中主机
    m_type = args[1]

    j = JHSGroupItemHour(m_type)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    j.antPage()
    time.sleep(1)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
