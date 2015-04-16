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
from base.RetryCrawler import RetryCrawler
from db.MysqlAccess import MysqlAccess
from JHSBrandTEMP import JHSBrandTEMP
from Jsonpage import Jsonpage
from JHSBActItemM import JHSBActItemM

class JHSBrandComing():
    '''A class of brand coming soon'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler = RetryCrawler()

        # 页面模板解析
        self.brand_temp = JHSBrandTEMP()

        # 获取Json数据
        self.jsonpage = Jsonpage()

        # 首页
        self.ju_home_url = 'http://ju.taobao.com'

        # 品牌团页面
        self.brand_url = 'http://ju.taobao.com/tg/brand.htm'

        # 页面信息
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.begin_time = Common.now()

    def antPage(self):
        try:
            # 获取品牌团列表页数据
            page = self.crawler.getData(self.brand_url, self.ju_home_url)
            self.activityListForComing(page) 
        except Exception as e:
            print '# exception err in antPage info:',e
            self.traceback_log()

    def activityListForComing(self, page):
        if not page or page == '': raise Common.InvalidPageException("# activityListForComing: not get JHS brand home.")
        self.ju_brand_page = page
        #print page
        # 保存html文件
        page_datepath = 'act/coming/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.begin_time))
        Config.writefile(page_datepath,'brand.htm',self.ju_brand_page)

        # 数据接口URL list
        #b_url_valList = self.activityListForComingTemp(page)
        b_url_valList = self.brand_temp.temp(page)

        if b_url_valList != []:
            # 从接口中获取的数据列表
            bResult_list = []
            json_valList = []
            for b_url_val in b_url_valList:
                b_url, f_name, f_catid = b_url_val
                a_val = (f_name,f_catid)
                json_valList.append((b_url,Config.ju_brand_home,a_val))
            bResult_list = self.jsonpage.get_json(json_valList)
            
            act_valList = []
            if bResult_list and bResult_list != []:
                a_val = (self.begin_time,)
                act_valList = self.jsonpage.parser_brandjson(bResult_list,a_val)

            if act_valList != []:
                self.run_brandAct(act_valList)
            else:
                print '# err: not get brandjson parser val list.'
        else:
            print '# err: not find activity json data URL list.'

    # 多线程抓去品牌团活动
    def run_brandAct(self, act_valList):
        try:
            # 多线程爬取即将上线活动
            if len(act_valList) > Config.act_max_th:
                m_Obj = JHSBActItemM(1, Config.act_max_th)
            else:
                m_Obj = JHSBActItemM(1, len(act_valList))
            m_Obj.putItems(act_valList)
            m_Obj.createthread()
            m_Obj.run()

            addact_num = 0
            item_list = m_Obj.items
            for item in item_list:
                crawling_confirm,sql = item
                if crawling_confirm == 1:
                    addact_num += 1
            """
            addact_num = 0
            while True:
                try:
                    if m_Obj.empty_q():
                        item_list = m_Obj.items
                        for item in item_list:
                            crawling_confirm,sql = item
                            if crawling_confirm == 1:
                                addact_num += 1
                        break
                except Exception as e:
                    print '# exception err crawl item :', e
                    self.traceback_log()
                    break
            """
        except Exception as e:
            print '# exception err brand coming :', e
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# brand activity coming soon num:',addact_num

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
    # 即将上线品牌团
    brand_obj = JHSBrandComing()
    brand_obj.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))



