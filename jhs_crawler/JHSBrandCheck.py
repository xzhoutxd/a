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
from JHSHomeBrand import JHSHomeBrand
from JHSBActItemM import JHSBActItemM
from JHSItemM import JHSItemM
#from JHSCrawlerM import JHSCrawlerM

class JHSBrandCheck():
    '''A class of brand for every hour check'''
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

        # 需要检查的活动
        self.act_dict = {}

        # 即将开团的最小时间
        self.min_hourslot = 1 # 最小时间段

    def antPage(self):
        try:
            # 得到需要的时间段
            val = (Common.time_s(self.crawling_time),Common.add_hours(self.crawling_time, self.min_hourslot))
            print '# hour need check activity time:',val
            act_results = self.mysqlAccess.selectJhsActAlive(val)
            if act_results:
                print '# hour find need check activity num:',len(act_results)
            else:
                print '# hour need check activity not found..'
                return None

            # 商品默认信息列表
            act_valList = []
            for act_r in act_results:
                # 只抓时尚女士,精品男士
                if int(act_r[2]) == 261000 or int(act_r[2]) == 262000:
                    act_valList.append((str(act_r[1]),act_r[7],act_r[8],self.begin_time,str(act_r[28]),str(act_r[29])))
                    if not self.act_dict.has_key(str(act_r[1])):
                        self.act_dict[str(act_r[1])] = []
                    # 按照活动Id找出商品
                    item_results = self.mysqlAccess.selectJhsItemIdsOfActId((str(act_r[1]),))
                    if item_results:
                        print '# act id:%s name:%s starttime:%s endtime:%s Items num:%s'%(str(act_r[1]),str(act_r[7]),str(act_r[28]),str(act_r[29]),str(len(item_results)))
                        itemid_list = []
                        if len(item_results) > 0:
                            for item in item_results:
                                itemid_list.append(str(item[0]))
                        self.act_dict[str(act_r[1])] = itemid_list

            print '# need check brands num:',len(act_valList)

            #print act_valList
            #print self.act_dict
            self.run_brandAct(act_valList)
        except Exception as e:
            print '# exception err in antPage info:',e

    # 多线程抓去品牌团活动
    def run_brandAct(self, act_valList):
        # Test 只测前两个
        #act_test = []
        #act_test.append(act_valList[0])
        #act_test.append(act_valList[1])
        #act_valList = act_test

        act_num = 0
        newitem_num = 0
        allitem_num = 0
        crawler_val_list = []
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #m_Obj = JHSBActItemM(2, Config.act_max_th)
        # 多线程 控制并发的线程数
        if len(act_valList) > Config.act_max_th:
            m_Obj = JHSBActItemM(2, Config.act_max_th)
        else:
            m_Obj = JHSBActItemM(2, len(act_valList))
        m_Obj.putItems(act_valList)
        m_Obj.createthread()
        m_Obj.run()

        while True:
            try:
                if m_Obj.empty_q():
                    item_list = m_Obj.items
                    for b in item_list:
                        print '#####A activity start#####'
                        brandact_itemVal_list = []
                        brandact_id, brandact_name, brandact_url, brandact_itemVal_list = b
                        act_num += 1
                        # item init val list
                        if brandact_itemVal_list and len(brandact_itemVal_list) > 0:
                            allitem_num = allitem_num + len(brandact_itemVal_list)
                            if self.act_dict.has_key(str(brandact_id)):
                                new_item_val = []
                                new_item_juid = []
                                # 重复商品
                                #if len(self.act_dict[str(brandact_id)]) < len(brandact_itemVal_list):
                                #    print len(self.act_dict[str(brandact_id)]),self.act_dict[str(brandact_id)]
                                #    print len(brandact_itemVal_list),brandact_itemVal_list
                                for item_val in brandact_itemVal_list:
                                    if str(item_val[7]) not in self.act_dict[str(brandact_id)]:
                                        new_item_juid.append(str(item_val[7]))
                                        new_item_val.append(item_val)
                                if len(new_item_val) > 0:
                                    crawler_val_list.append((brandact_id,brandact_name,new_item_val))
                                    newitem_num = newitem_num + len(new_item_val)
                                    print new_item_juid
                                    print self.act_dict[str(brandact_id)]
                                print '# activity id:%s name:%s url:%s'%(brandact_id, brandact_name, brandact_url)
                                print '# old activity items num:', len(self.act_dict[str(brandact_id)])
                                print '# now activity items num:', len(brandact_itemVal_list)
                                print '# add new items num:', len(new_item_val)
                                
                        print '# A activity end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        print '#####A activity end#####'
                    break
            except Exception as e:
                print '# exception err crawl activity item, %s err:'%(sys._getframe().f_back.f_code.co_name),e 
                #traceback.print_exc()
                self.traceback_log()
                break
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# All brand activity num:', len(act_valList)
        print '# Check brand activity num:', act_num
        print '# New add brand activity new items num:', newitem_num
        print '# All get brand activity items num:', allitem_num

        self.run_brandItems(crawler_val_list)

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list):
        i = 0
        for crawler_val in crawler_val_list:
            brandact_id, brandact_name, item_valTuple = crawler_val
            print '# activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name
            # 多线程 控制并发的线程数
            if len(item_valTuple) > Config.item_max_th:
                #m_itemsObj = JHSCrawlerM(2, Config.item_max_th)
                m_itemsObj = JHSItemM(1, Config.item_max_th)
            else: 
                #m_itemsObj = JHSCrawlerM(2, len(item_valTuple))
                m_itemsObj = JHSItemM(1, len(item_valTuple))
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()

            while True:
                try:
                    print '# Item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
                    if m_itemsObj.empty_q():
                        item_list = m_itemsObj.items
                        print '# Activity Items num:', len(item_list)
                        #for item in item_list:
                            #sql, hourSql, stockSql = item
                            #print sql,hourSql,stockSql
                            #self.mysqlAccess.insertJhsItem(sql)
                            #self.mysqlAccess.insertJhsItemSaleForHour(hourSql)
                            #self.mysqlAccess.insertJhsItemStockForHour(stockSql)
                        print '# Activity Item List End: actId:%s, actName:%s'%(brandact_id, brandact_name)
                        break
                except Exception as e:
                    print '# exception err crawl item: ', e
                    print '# crawler_val:', crawler_val
                    #traceback.print_exc()
                    self.traceback_log()
                    break

    def traceback_log(self):
        print '#####--Traceback Start--#####'
        tp,val,td = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(td):
            print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
            print text
        print "exception traceback err:%s,%s,%s"%(tp,val,td)
        print '#####--Traceback End--#####'


if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandCheck()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


