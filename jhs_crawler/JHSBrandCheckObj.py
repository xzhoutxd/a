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
from JHSBActItemM import JHSBActItemM
from JHSItemM import JHSItemM

class JHSBrandCheckObj():
    '''A class for brand item check'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 需要检查的活动
        self.act_dict = {}
        # 所有已经存在数据库中的item
        self.all_itemjuid = {}

    def antPage(self, act_valList, act_dict, all_itemjuid):
        self.act_dict = act_dict
        self.all_itemjuid = all_itemjuid
        self.run_brandAct(act_valList)

    # 多线程抓去品牌团活动
    def run_brandAct(self, act_valList):
        act_num = 0
        newitem_num = 0
        allitem_num = 0
        # 新商品
        crawler_val_list = []
        # 新活动商品关系
        act_item_val_list = []
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
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
                        brandact_id, brandact_name, brandact_url, brandact_itemVal_list, crawling_time = b
                        act_num += 1
                        # item init val list
                        if brandact_itemVal_list and len(brandact_itemVal_list) > 0:
                            allitem_num = allitem_num + len(brandact_itemVal_list)
                            if self.act_dict.has_key(str(brandact_id)):
                                new_item_val = []
                                new_item_juid = []
                                hadin_otheract_juid = []
                                # 重复商品
                                #if len(self.act_dict[str(brandact_id)]) < len(brandact_itemVal_list):
                                #    print len(self.act_dict[str(brandact_id)]),self.act_dict[str(brandact_id)]
                                #    print len(brandact_itemVal_list),brandact_itemVal_list
                                for item_val in brandact_itemVal_list:
                                    if str(item_val[7]) not in self.act_dict[str(brandact_id)] and str(item_val[6]) not in self.act_dict[str(brandact_id)]:
                                        if str(item_val[7]) in self.all_itemjuid:
                                            hadin_otheract_juid.append((str(item_val[7]),self.all_itemjuid[str(item_val[7])]))
                                        else:
                                            if str(item_val[7]) != '':
                                                new_item_juid.append(str(item_val[7]))
                                            else:
                                                new_item_juid.append(str(item_val[6])))
                                            new_item_val.append(item_val)
                                        if str(item_val[7]) != '':
                                            act_item_val_list.append((crawling_time,str(item_val[7]),str(brandact_id)))
                                if len(new_item_val) > 0:
                                    crawler_val_list.append((brandact_id,brandact_name,new_item_val))
                                    newitem_num = newitem_num + len(new_item_val)
                                    print new_item_juid
                                    print self.act_dict[str(brandact_id)]
                                print '# activity id:%s name:%s'%(brandact_id, brandact_name)
                                print '# old activity items num:', len(self.act_dict[str(brandact_id)])
                                print '# now activity items num:', len(brandact_itemVal_list)
                                print '# add new items num:', len(new_item_val)
                                if len(hadin_otheract_juid) > 0:
                                    print hadin_otheract_juid
                                    print '# repeat items, had in other act num:', len(hadin_otheract_juid)

                                
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

        # 保存活动商品关系
        sql_list = []
        for sql in act_item_val_list:
            sql_list.append(sql)
            if len(sql_list) >= Config.act_max_arg:
                self.mysqlAccess.insertJhsActItemRelation(sql_list)
                sql_list = []
        if len(sql_list) > 0:
            self.mysqlAccess.insertJhsActItemRelation(sql_list)

        # 抓取新加商品
        self.run_brandItems(crawler_val_list)

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list):
        i = 0
        for crawler_val in crawler_val_list:
            brandact_id, brandact_name, item_valTuple = crawler_val
            print '# activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name
            # 多线程 控制并发的线程数
            if len(item_valTuple) > Config.item_max_th:
                m_itemsObj = JHSItemM(1, Config.item_max_th)
            else: 
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
                        print '# Activity Item List End: actId:%s, actName:%s'%(brandact_id, brandact_name)
                        break
                except Exception as e:
                    print '# exception err crawl item: ', e
                    print '# crawler_val:', crawler_val
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
    #b = JHSBrandCheckObj()
    #b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


