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
from Jsonpage import Jsonpage
from JHSBActItemM import JHSBActItemM

class JHSBrandComing():
    '''A class of brand coming soon'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler = TBCrawler()

        # 获取Json数据
        self.jsonpage = Jsonpage()

        # 商品抓取队列
        #self.item_queue = Queue.Queue()

        # 首页
        self.ju_home_url = 'http://ju.taobao.com'

        # 品牌团页面
        self.brand_url = 'http://ju.taobao.com/tg/brand.htm'

        # 首页的品牌团列表
        self.home_brands = {}
        self.home_brands_list = []

        # 品牌团页面
        self.brandcoming_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=1'

        # 页面信息
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

    def antPage(self):
        try:
            # 获取品牌团列表页数据
            page = self.crawler.getData(self.brand_url, self.ju_home_url)
            self.activityListForComing(page) 
        except Exception as e:
            print '# exception err in antPage info:',e

    def activityListForComing(self, page):
        if not page or page == '': raise Common.InvalidPageException("# activityListForComing: not get JHS brand home.")
        self.ju_brand_page = page
        #print page

        # 数据接口URL list
        b_url_valList = self.activityListForComingTemp(page)

        if b_url_valList != []:
            # 从接口中获取的数据列表
            bResult_list = []
            json_valList = []
            for b_url_val in b_url_valList:
                #bResult_list += self.get_jsonData(b_url_val)
                b_url, f_name, f_catid = b_url_val
                a_val = (f_name,f_catid)
                json_valList.append((b_url,Config.ju_brand_home,a_val))
                #bResult_list += self.jsonpage.get_jsonPage(b_url,Config.ju_brand_home,a_val)
            bResult_list = self.jsonpage.get_json(json_valList)
            
            act_valList = []
            if bResult_list and bResult_list != []:
                #self.parser_activities(bResult_list)
                a_val = (self.begin_time,)
                act_valList = self.jsonpage.parser_brandjson(bResult_list,a_val)

            if act_valList != []:
                self.run_brandAct(act_valList)
            else:
                print '# err: not get brandjson parser val list.'
        else:
            print '# err: not find activity json data URL list.'

    # 页面模板
    def activityListForComingTemp(self, page):
        # 数据接口URL list
        b_url_valList = []
        # 模板1
        m = re.search(r'<div.+?data-catid=\'(\d+)\' data-forecast="true">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', page, flags=re.S)
        if m:
            b_url_valList = self.activityListForComingTemp1(page)
        else:
            # 模板2
            m = re.search(r'<div.+?id="(subfloor\d+)" data-ajax="(.+?)">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', page, flags=re.S)
            if m:
                b_url_valList = self.activityListForComingTemp2(page)
            else:
                print '# err: not matching all templates.' 
        return b_url_valList
         
    # 品牌团页面模板1
    def activityListForComingTemp1(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div.+?data-catid=\'(\d+)\' data-forecast="true">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', flags=re.S)
        for sub_floor in p.finditer(page):
            f_name, f_catid = '', '', ''
            f_catid, f_name = sub_floor.group(1), sub_floor.group(2)

            print '# Coming activity floor:', f_name, f_catid
            if f_catid != '':
                page_num = 1
                f_url = self.brandcoming_page_url + '&page=%d'%page_num + '&frontCatIds=%s'%f_catid
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 品牌团页面模板2
    def activityListForComingTemp2(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div.+?id="(subfloor\d+)" data-ajax="(.+?)">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', flags=re.S)
        for sub_floor in p.finditer(page):
            f_url, f_name, f_catid = '', '', ''
            f_url, f_name = sub_floor.group(2), sub_floor.group(3)

            if f_url:
                m = re.search(r'frontCatIds=(\d+)', f_url)
                if m:
                    f_catid = m.group(1)
                print '# Coming activity floor:', f_name, f_catid, f_url
                url_valList.append((f_url, f_name, f_catid))
        return url_valList
                
    # 通过数据接口获取每一页的数据
    def get_jsonData(self, val):
        bResult_list = []
        b_url, b_page = '', ''
        try:
            b_url, f_name, f_catid = val
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            b_url = b_url + '&_ksTS=%s'%ts
            b_page = self.crawler.getData(b_url, Config.ju_brand_home)
            result = json.loads(b_page)
            print b_url
            bResult_list.append([result,f_name,f_catid])
            # 分页从接口中获取数据
            if result.has_key('totalPage') and int(result['totalPage']) > 1:
                for page_i in range(2, int(result['totalPage'])+1):
                    ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                    b_url = re.sub('page=\d+&', 'page=%d&'%page_i, b_url)
                    b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                    print b_url
                    b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                    result = json.loads(b_page)
                    bResult_list.append([result, f_name, f_catid])
        except Exception as e:
            print '# exception err in get_jsonData info:',e
            print b_url
            print '# get json data:',b_page

        return bResult_list

    # 解析每一页的数据
    def parser_activities(self, bResult_list):
        print '# coming activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 获取多线程需要的字段val
        act_valList = []
        # 前一页的数据量,用于计算活动所在的位置
        prepage_count = 0
        for page in bResult_list:
            i_page = page[0]
            if i_page.has_key('brandList') and i_page['brandList'] != []:
                activities = i_page['brandList']
                b_position_start = 0
                if i_page.has_key('currentPage') and int(i_page['currentPage']) > 1:
                    # 每页取60条数据
                    #b_position_start = (int(i_page['currentPage']) - 1) * 60
                    b_position_start = (int(i_page['currentPage']) - 1) * prepage_count
                else:
                    # 保存前一页的数据条数
                    prepage_count = len(activities)
                print '# coming every page num:',len(activities)
                for i in range(0,len(activities)):
                    activity = activities[i]
                    act_valList.append((activity, page[2], page[1], (b_position_start+i+1), self.begin_time))

        if len(act_valList) > 0:
            self.run_brandAct(act_valList)
            #return act_valList
        else:
            print '# err: not find activity crawling val list'

    # 多线程抓去品牌团活动
    def run_brandAct(self, act_valList):
        try:
            # 多线程爬取即将上线活动
            #m_Obj = JHSBActItemM(1, Config.act_max_th)
            m_Obj = JHSBActItemM(1, 5)
            m_Obj.putItems(act_valList)
            m_Obj.createthread()
            m_Obj.run()
        except Exception as e:
            print '# exception err brand coming :', e
        """
        while True:
            try:
                if m_Obj.empty_q():
                    item_list = m_Obj.items
                    sql_list = []
                    for itemsql in item_list:
                        self.mysqlAccess.insertJhsActComing(itemsql)
                    print '# Coming Activity List End'
                    break
            except Exception as e:
                print '# exception err crawl item :', e
                #traceback.print_exc()
                print '#####--Traceback Start--#####'
                tp,val,td = sys.exc_info()
                for file, lineno, function, text in traceback.extract_tb(td):
                    print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                    print text
                print "exception traceback err:%s,%s,%s"%(tp,val,td)
                print '#####--Traceback End--#####'
                break
        """
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# brand activity coming soon num:', len(act_valList)

if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # 即将上线品牌团
    brand_obj = JHSBrandComing()
    brand_obj.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))



