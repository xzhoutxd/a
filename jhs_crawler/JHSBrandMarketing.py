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
#from base.TBCrawler import TBCrawler
from base.RetryCrawler import RetryCrawler
from db.MysqlAccess import MysqlAccess
from JHSBActItemM import JHSBActItemM
from JHSHomeBrand import JHSHomeBrand
from JHSBrandTEMP import JHSBrandTEMP
from Jsonpage import Jsonpage

class JHSBrandMarketing():
    '''A class of brand marketing'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        #self.crawler    = TBCrawler()
        self.crawler = RetryCrawler()

        # 页面模板解析
        self.brand_temp = JHSBrandTEMP()

        # 获取Json数据
        self.jsonpage = Jsonpage()

        # 首页
        self.ju_home_url = 'http://ju.taobao.com'
        self.ju_home_today_url = 'http://ju.taobao.com/tg/today_items.htm'
        self.refers = 'http://www.tmall.com'

        # 品牌团页面
        self.brand_url = 'http://ju.taobao.com/tg/brand.htm'

        # 首页的品牌团列表
        self.home_brands = {}

        # 品牌团页面的最上面推广位
        self.top_brands = {}

        # 页面信息
        self.ju_home_page = '' # 聚划算首页
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.begin_time = Common.now()

    def antPage(self):
        try:
            # 获取首页的品牌团
            page = self.crawler.getData(self.ju_home_url, self.refers)
            hb = JHSHomeBrand()
            hb.antPage(page)
            if not hb.home_brands:
                page = self.crawler.getData(self.ju_home_today_url, self.refers)
                hb.antPage(page)
            self.home_brands = hb.home_brands
            page_datepath = 'act/marketing/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.begin_time))
            Config.writefile(page_datepath,'home.htm',page)
            #print '# home activities:', self.home_brands

            # 获取品牌团列表页数据
            page = self.crawler.getData(self.brand_url, self.ju_home_url)
            self.activityList(page) 
        except Exception as e:
            print '# exception err in antPage info:',e
            self.traceback_log()

    # 品牌团列表
    def activityList(self, page):
        if not page or page == '': raise Common.InvalidPageException("# brand activityList: not get JHS brand home.")
        self.ju_brand_page = page
        # 保存html文件
        page_datepath = 'act/marketing/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.begin_time))
        Config.writefile(page_datepath,'brand.htm',self.ju_brand_page)

        # 数据接口URL list
        self.top_brands = self.brand_temp.activityTopbrandTemp(page)

        b_url_valList = self.brand_temp.activityListTemp(page)
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
                a_val = (self.begin_time,)
                act_valList = self.jsonpage.parser_brandjson(bResult_list,a_val)

            if act_valList != []:
                print '# get brand act num:',len(act_valList)
                self.run_brandAct(act_valList)
            else:
                print '# err: not get brandjson parser val list.'
        else:
            print '# err: not find activity json data URL list.'

    def run_brandAct(self, act_valList):
        repeatact_num = 0
        # 活动数量
        act_num = 0
        # 需要保存活动sql列表
        act_sql_list = []
        # 用于活动去重id dict
        brandact_id_dict = {}
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 多线程 控制并发的线程数
        if len(act_valList) > Config.act_max_th:
            m_Obj = JHSBActItemM(5, Config.act_max_th)
        else:
            m_Obj = JHSBActItemM(5, len(act_valList))
        m_Obj.putItems(act_valList)
        m_Obj.createthread()
        m_Obj.run()
        #while True:
        #    try:
        #        if m_Obj.empty_q():
        item_list = m_Obj.items
        for b in item_list:
            act_num += 1
            brandact_id,brandact_name,brandact_url,val = b
            # 去重
            if brandact_id_dict.has_key(str(brandact_id)):
                repeatact_num += 1
                print '# repeat brand act. activity id:%s name:%s'%(brandact_id, brandact_name)
            else:
                brandact_id_dict[str(brandact_id)] = brandact_name
                if self.home_brands.has_key(str(brandact_id)):
                    val = val + (self.home_brands[str(brandact_id)]["position"],self.home_brands[str(brandact_id)]["datatype"],self.home_brands[str(brandact_id)]["typename"])
                elif self.home_brands.has_key(brandact_url):
                    val = val + (self.home_brands[brandact_url]["position"],self.home_brands[brandact_url]["datatype"],self.home_brands[str(brandact_id)]["typename"])
                else:
                    val = val + (None,None,None)

                if self.top_brands.has_key(str(brandact_id)):
                    val = val + (self.top_brands[str(brandact_id)]["position"],self.top_brands[str(brandact_id)]["datatype"])
                elif self.top_brands.has_key(brandact_url):
                    val = val + (self.top_brands[brandact_url]["position"],self.top_brands[brandact_url]["datatype"])
                else:
                    val = val + (None,None)
                act_sql_list.append(val)
        #        break
        #    except Exception as e:
        #        print '# exception err crawl activity item, %s err:'%(sys._getframe().f_back.f_code.co_name),e
        #        #traceback.print_exc()
        #        self.traceback_log()
        #        break
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        # 品牌团活动位置信息入库
        # 保存
        actsql_list = []
        for sql in act_sql_list:
            actsql_list.append(sql)
            if len(actsql_list) >= Config.act_max_arg:
                self.mysqlAccess.insertJhsActPosition(actsql_list)
                actsql_list = []
        if len(actsql_list) > 0:
            self.mysqlAccess.insertJhsActPosition(actsql_list)

        print '# Find act num:', act_num
        print '# Repeat brand activity num:', repeatact_num


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
    b = JHSBrandMarketing()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


