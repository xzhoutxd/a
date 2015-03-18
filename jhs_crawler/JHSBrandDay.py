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

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()
        self.page_datepath = time.strftime("%Y/%m/%d/", time.localtime(self.crawling_time))

    def antPage(self):
        try:
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
            print '# day crawler time:',val
            act_results = self.mysqlAccess.selectJhsActDayalive(val)
            if act_results:
                print '# day act num:',len(act_results)
            else:
                print '# day act not found..'
                return None
            
            all_item_num = 0
            # 商品默认信息列表
            crawler_val_list = []
            for act_r in act_results:
                # 只抓时尚女士,精品男士
                #if int(act_r[1]) != 261000 or int(act_r[1]) != 262000: continue
                # 按照活动Id找出商品信息
                item_results = self.mysqlAccess.selectJhsItemsDayalive((str(act_r[0]),))
                if item_results:
                    print "# act id:%s name:%s Items num:%s"%(str(act_r[0]),str(act_r[3]),str(len(item_results)))
                    if len(item_results) > 0:
                        crawler_val_list.append((act_r[0],act_r[3],item_results))
                    all_item_num += len(item_results)
                else:
                    print '# day act id:%s name:%s not find items...'%(str(act_r[0]),str(act_r[3]))

            print '# day all item nums:',all_item_num

            # 多线程抓商品
            self.run_brandItems(crawler_val_list)
        except Exception as e:
            print '# exception err in antPage info:',e

    def antPageForGiveup(self, crawler_val_list):
        try:
            # 多线程抓商品
            self.run_brandItems(crawler_val_list)
        except Exception as e:
            print '# exception err in antPage info:',e


    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list):
        for crawler_val in crawler_val_list:
            brandact_id, brandact_name, item_valTuple = crawler_val
            print '# day activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name
            # 附加的信息
            a_val = (self.begin_time,)
            # 多线程 控制并发的线程数
            if len(item_valTuple) > Config.item_max_th:
                m_itemsObj = JHSItemM(2, Config.item_max_th, a_val)
            else:
                m_itemsObj = JHSItemM(2, len(item_valTuple), a_val)
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()

            while True:
                try:
                    print '# day item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
                    if m_itemsObj.empty_q():
                        # 重试次数太多没有抓下来的商品
                        giveup_item_list = m_itemsObj.giveup_items
                        print '# Give up items num:', len(giveup_item_list)
                        if len(giveup_item_list) > 0:
                            print '###give up###','actId:%s,actName:%s,'%(brandact_id, brandact_name),giveup_item_list,'###give up###'
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

