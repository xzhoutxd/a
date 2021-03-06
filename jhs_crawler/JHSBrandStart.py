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
from JHSBrandQ import JHSBrandQ

class JHSBrand():
    '''A class of brand'''
    def __init__(self, m_type, _q_type='s'):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        #self.crawler = TBCrawler()
        self.crawler = RetryCrawler()

        # 页面模板解析
        self.brand_temp = JHSBrandTEMP()

        # 获取、解析活动，并抓取商品信息
        self.brand_obj = JHSBrandObj()

        # brand queue
        self.brand_queue = JHSBrandQ()

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

        # 分布式主机标志
        self.m_type = m_type
        # 活动队列标志
        self.q_type = _q_type

    def antPage(self):
        try:
            # 更新即将开团活动的商品信息
            # 主机器需要配置redis队列
            if self.m_type == 'm':
                self.update_items()
            # 附加的信息
            a_val = (self.begin_time,)
            self.brand_queue.brandQ(self.q_type, a_val)

            # 主机器需要抓取品牌团列表，更新活动信息
            if self.m_type == 'm':
                # 获取首页的品牌团
                page = self.crawler.getData(self.ju_home_url, self.refers)
                hb = JHSHomeBrand()
                hb.antPage(page)
                if hb.home_brands == {} or not hb.home_brands:
                    page = self.crawler.getData(self.ju_home_today_url, self.refers)
                    hb.antPage(page)
                self.home_brands = hb.home_brands
                # 保存html文件
                page_datepath = 'act/main/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.begin_time))
                Config.writefile(page_datepath,'home.htm',page)
                #print self.home_brands

                # 获取品牌团列表页数据
                page = self.crawler.getData(self.brand_url, self.ju_home_url)
                self.activityList(page) 
            
        except Exception as e:
            print '# exception err in antPage info:',e
            self.traceback_log()

    def activityList(self, page):
        if not page or page == '': raise Common.InvalidPageException("# activityList: not get JHS brand home.")
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
        # 清空即将开团活动redis队列
        self.brand_queue.clearBrandQ(self.q_type)
        # 保存即将开团活动redis队列
        self.brand_queue.putBrandlistQ(self.q_type, update_val_list)
        print '# brand queue end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

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
    args = sys.argv
    #args = ['JHSBrand','m|s']
    if len(args) < 2:
        print '#err not enough args for JHSBrand...'
        exit()
    # 是否是分布式中主机
    m_type = args[1]
    b = JHSBrand(m_type)
    b.antPage()
    time.sleep(1)
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


