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
from JHSBActItemM import JHSBActItemM
from JHSItemM import JHSItemM
from JHSHomeBrand import JHSHomeBrand
from JHSBrandTEMP import JHSBrandTEMP
from JHSBrandObj import JHSBrandObj

class JHSBrand():
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
        self.ju_home_url   = 'http://ju.taobao.com'
        self.refers     = 'http://www.tmall.com'
        self.ju_home_today_url = 'http://ju.taobao.com/tg/today_items.htm'

        # 品牌团页面
        self.brand_url  = 'http://ju.taobao.com/tg/brand.htm'

        # 首页的品牌团列表
        self.home_brands = {}

        # 页面信息
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.crawling_time = Common.now()
        self.begin_time = Common.now()

        # 已经抓取的还没有开团活动id
        self.brandact_id_list = []

        # 即将开团的最小时间
        self.min_hourslot = 1 # 最小时间段

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
            # 保存html文件
            page_datepath = 'act/main/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.begin_time))
            Config.writefile(page_datepath,'home.htm',page)
            #print self.home_brands

            # 更新即将开团活动的商品信息
            self.update_items()
            
            # 获取品牌团列表页数据
            page = self.crawler.getData(self.brand_url, self.ju_home_url)
            self.activityList(page) 
            
        except Exception as e:
            print '# exception err in antPage info:',e
            self.traceback_log()

    def activityList(self, page):
        if not page or page == '': raise Common.InvalidPageException("# activityListForComing: not get JHS brand home.")
        self.ju_brand_page = page
        #print page
        # 保存html文件
        page_datepath = 'act/main/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.begin_time))
        Config.writefile(page_datepath,'brand.htm',self.ju_brand_page)

        # 数据接口URL list
        #b_url_valList = self.activityListTemp(page)
        b_url_valList = self.brand_temp.activityListTemp(page)

        
        # 获取还没有开团的活动id
        self.brandact_id_list = self.brand_obj.get_notstart_act()
        a_val = (self.begin_time, self.home_brands, self.brandact_id_list)
        b_type = 3
        self.brand_obj.run_brand(b_type, b_url_valList, a_val)

    # 更新活动商品关注人数
    def update_items(self):
        print '###### items update start ######'
        # 获取一个小时即将开团的活动
        val = (Common.time_s(self.crawling_time),Common.add_hours(self.crawling_time, self.min_hourslot))
        print '# update activity time:',val
        act_results = self.mysqlAccess.selectJhsActStartForOneHour(val)
        if act_results:
            print '# need update activity num:',len(act_results)
        else:
            print '# need update activity not found..'

        # 商品默认信息列表
        all_item_num = 0
        update_val_list = []
        for act_r in act_results:
            # 按照活动Id找出商品
            item_results = self.mysqlAccess.selectJhsItemsFromActId((str(act_r[1]),))
            if item_results:
                print "# act id:%s name:%s Items num:%s"%(str(act_r[1]),str(act_r[7]),str(len(item_results)))
                if len(item_results) > 0:
                    update_val_list.append((act_r[1],act_r[7],item_results))
                all_item_num += len(item_results)
            else:
                print '# need update act id:%s name:%s not find items...'%(str(act_r[1]),str(act_r[7]))

        print '# need update all item nums:',all_item_num

        self.run_updateItems(update_val_list)
        print '###### items update end ######'

    def run_updateItems(self, update_val_list):
        for update_val in update_val_list:
            brandact_id, brandact_name, item_valTuple = update_val
            print '# activity Items crawler start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name
            # 附加的信息
            a_val = (self.begin_time,)
            # 多线程 控制并发的线程数
            if len(item_valTuple) > Config.item_max_th:
                m_itemsObj = JHSItemM(4, Config.item_max_th, a_val)
            else: 
                m_itemsObj = JHSItemM(4, len(item_valTuple), a_val)
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()

            while True:
                try:
                    print '# Update item: actId:%s, actName:%s'%(brandact_id, brandact_name)
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    if m_itemsObj.empty_q():
                        item_list = m_itemsObj.items
                        print '# Activity find Items num:', len(item_valTuple)
                        print '# Activity update Items num:', len(item_list)
                        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        print '# Update activity Item List End: actId:%s, actName:%s'%(brandact_id, brandact_name)
                        break
                except Exception as e:
                    print '# exception err crawl item: ', e
                    print '# update_val:', update_val
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
    pass
    """
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrand()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    """


