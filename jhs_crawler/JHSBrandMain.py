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
#from base.TBCrawler import TBCrawler
from base.RetryCrawler import RetryCrawler
from db.MysqlAccess import MysqlAccess
from JHSBrandTEMP import JHSBrandTEMP
from JHSBActItemM import JHSBActItemM
from JHSItemM import JHSItemM
from JHSBrandObj import JHSBrandObj

class JHSBrandMain():
    '''A class of brand'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        #self.crawler = TBCrawler()
        self.crawler = RetryCrawler()

        # 页面模板解析
        self.brand_temp = JHSBrandTEMP()

        # 获取、解析活动，并抓取商品信息
        self.brand_obj = JHSBrandObj()

        # 首页
        self.ju_home_url = 'http://ju.taobao.com'
        self.refers = 'http://www.tmall.com'
        self.ju_home_today_url = 'http://ju.taobao.com/tg/today_items.htm'

        # 品牌团页面
        self.brand_url = 'http://ju.taobao.com/tg/brand.htm'

        # 首页的品牌团列表
        self.home_brands = {}

        # 页面信息
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.begin_time = Common.now()

        # 已经抓取的还没有开团活动id
        self.brandact_id_list = []

    def antPage(self):
        try:
            # 获取品牌团列表页数据
            page = self.crawler.getData(self.brand_url, self.ju_home_url)
            self.activityList(page) 
        except Exception as e:
            print '# exception err in antPage info:',e
            self.traceback_log()

    def activityList(self, page):
        if not page or page == '': raise Common.InvalidPageException("# activityListForComing: not get JHS brand home.")
        self.ju_brand_page = page
        # 保存html文件
        page_datepath = 'act/main/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.begin_time))
        Config.writefile(page_datepath,'main-brand.htm',self.ju_brand_page)

        # 数据接口URL list
        b_url_valList = self.brand_temp.temp(page)

        # 获取还没有开团的活动id
        self.brandact_id_list = self.brand_obj.get_notstart_act()
        a_val = (self.begin_time, self.brandact_id_list)
        b_type = 4
        self.brand_obj.run_brand(b_type, b_url_valList, a_val)

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
    b = JHSBrandMain()
    b.antPage()
    time.sleep(1)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

