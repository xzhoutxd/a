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
from Jsonpage import Jsonpage

class JHSBrandObj():
    '''A class of brand obj'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 获取Json数据
        self.jsonpage = Jsonpage()

    # 获取还没有开团的活动
    def get_notstart_act(self):
        actid_list = []
        results = self.mysqlAccess.selectJhsActNotStart()
        if results:
            for r in results:
                actid_list.append(str(r[1]))
        return actid_list

    # 获取接口数据并解析
    def run_brand(self, b_type, b_url_valList, a_val=()):
        if b_url_valList != []:
            # 从接口中获取的数据列表
            bResult_list = []
            json_valList = []
            for b_url_val in b_url_valList:
                b_url, f_name, f_catid = b_url_val
                json_valList.append((b_url,Config.ju_brand_home,(f_name,f_catid)))
            bResult_list = self.jsonpage.get_json(json_valList)

            act_valList = []
            if bResult_list and bResult_list != []:
                act_valList = self.jsonpage.parser_brandjson(bResult_list,a_val)

            if act_valList != []:
                print '# get brand act num:',len(act_valList)
                self.run_brandAct(b_type,act_valList)
            else:
                print '# err: not get brandjson parser val list.'
        else:
            print '# err: not find activity json data URL list.'

    # 多线程抓去品牌团活动
    def run_brandAct(self, b_type, act_valList):
        newact_num = 0
        repeatact_num = 0
        ladygo_num = 0
        allitem_num = 0
        updateact_num = 0
        # 用于活动去重id dict
        brandact_id_dict = {}
        # 商品val列表
        crawler_val_list = []
        # 需要保存活动sql列表
        act_sql_list = []
        # 需要更新活动sql列表
        updateact_sql_list = []
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 多线程 控制并发的线程数
        if len(act_valList) > Config.act_max_th:
            m_Obj = JHSBActItemM(b_type, Config.act_max_th)
        else:
            m_Obj = JHSBActItemM(b_type, len(act_valList))
        m_Obj.putItems(act_valList)
        m_Obj.createthread()
        m_Obj.run()

        
        #while True:
        #    try:
        #        if m_Obj.empty_q():
        #            item_list = m_Obj.items
        item_list = m_Obj.items
        for b in item_list:
            print '#####A activity start#####'
            crawling_confirm, brandact_id, brandact_name, other_val = b
            # 去重
            if brandact_id_dict.has_key(str(brandact_id)):
                repeatact_num += 1
                print '# repeat brand act. activity id:%s name:%s'%(brandact_id, brandact_name)
            else:
                brandact_id_dict[str(brandact_id)] = brandact_name
                # 判断本活动是不是即将开团
                if crawling_confirm == 1:
                    brandact_itemVal_list = []
                    brandact_itemVal_list, sql, daySql, hourSql = other_val
                    brandact_url, brandact_sign, brandact_cateId = sql[8], sql[13], sql[2]
                    newact_num += 1
                    act_sql_list.append((sql,daySql,hourSql))
                    # 只抓取非俪人购商品
                    if int(brandact_sign) != 3:
                        # Activity Items
                        # item init val list
                        if brandact_itemVal_list and len(brandact_itemVal_list) > 0:
                            crawler_val_list.append((brandact_id,brandact_name,brandact_itemVal_list))
                            allitem_num = allitem_num + len(brandact_itemVal_list)
                            print '# activity id:%s name:%s'%(brandact_id, brandact_name)
                            print '# activity items num:', len(brandact_itemVal_list)
                    else:
                        print '# ladygo activity id:%s name:%s'%(brandact_id, brandact_name)
                        ladygo_num += 1
                # 需要更新的活动
                elif crawling_confirm == 0:
                    updateSql = other_val
                    updateact_sql_list.append(updateSql)
                    updateact_num += 1
                    print '# update activity, id:%s name:%s'%(brandact_id, brandact_name)
                else:
                    print '# Not New activity, id:%s name:%s'%(brandact_id, brandact_name)
            print '#####A activity end#####'
        #            break
        #    except Exception as e:
        #        print '# exception err crawl activity item, %s err:'%(sys._getframe().f_back.f_code.co_name),e 
        #        #traceback.print_exc()
        #        self.traceback_log()
        #        break
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# All brand activity num:', len(act_valList)
        print '# Repeat brand activity num:', repeatact_num
        print '# New add brand activity num:', newact_num
        print '# New add brand activity(ladygo) num:', ladygo_num
        print '# New add brand activity items num:', allitem_num
        print '# Update brand activity num:', updateact_num

        # 品牌团活动入库
        # 保存
        actsql_list, actdaysql_list, acthoursql_list = [], [], []
        for act_sql in act_sql_list:
            sql,daySql,hourSql = act_sql
            actsql_list.append(sql)
            actdaysql_list.append(daySql)
            acthoursql_list.append(hourSql)
            if len(actsql_list) >= Config.act_max_arg:
                self.mysqlAccess.insertJhsAct(actsql_list)
                actsql_list = []
            if len(actdaysql_list) >= Config.act_max_arg:
                self.mysqlAccess.insertJhsActDayalive(actdaysql_list)
                actdaysql_list = []
            if len(acthoursql_list) >= Config.act_max_arg:
                self.mysqlAccess.insertJhsActHouralive(acthoursql_list)
                acthoursql_list = []
        if len(actsql_list) > 0:
            self.mysqlAccess.insertJhsAct(actsql_list)
        if len(actdaysql_list) > 0:
            self.mysqlAccess.insertJhsActDayalive(actdaysql_list)
        if len(acthoursql_list) > 0:
            self.mysqlAccess.insertJhsActHouralive(acthoursql_list)

        # 更新
        if len(updateact_sql_list) > 0:
            actupdatesql_list = []
            for updateSql in updateact_sql_list:
                actupdatesql_list.append(updateSql)
                if len(actupdatesql_list) >= Config.act_max_arg:
                    self.mysqlAccess.updateJhsAct(actupdatesql_list)
                    actupdatesql_list = []
            if len(actupdatesql_list) > 0:
                self.mysqlAccess.updateJhsAct(actupdatesql_list)

        # 多线程抓商品
        self.run_brandItems(crawler_val_list)

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_val_list):
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

            #while True:
            #    try:
            #        print '# Item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
            #        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            #        if m_itemsObj.empty_q():
            item_list = m_itemsObj.items
            print '# Activity find Items num:', len(item_valTuple)
            print '# Activity insert Items num:', len(item_list)
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            print '# Activity Item List End: actId:%s, actName:%s'%(brandact_id, brandact_name)
            #            break
            #    except Exception as e:
            #        print '# exception err crawl item: ', e
            #        print '# crawler_val:', crawler_val
            #        #traceback.print_exc()
            #        self.traceback_log()
            #        break

    def traceback_log(self):
        print '#####--Traceback Start--#####'
        tp,val,td = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(td):
            print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
            print text
        print "exception traceback err:%s,%s,%s"%(tp,val,td)
        print '#####--Traceback End--#####'


if __name__ == '__main__':
    pass
    """
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandObj()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    """


