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
#from JHSCrawlerM import JHSCrawlerM
from JHSBActItemM import JHSBActItemM
from JHSItemM import JHSItemM
from JHSHomeBrand import JHSHomeBrand

class JHSBrand():
    '''A class of brand'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler    = TBCrawler()

        # 首页
        self.ju_home_url   = 'http://ju.taobao.com'
        self.refers     = 'http://www.tmall.com'

        # 品牌团页面
        self.brand_url  = 'http://ju.taobao.com/tg/brand.htm'
        self.brand38_url  = 'http://act.ju.taobao.com/go/rgn/ju/brand38.php'

        # 首页的品牌团列表
        self.home_brands = {}
        self.home_brands_list = []

        # 品牌团页面
        # 模板1 数据接口URL
        self.brand_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=0'

        # 页面信息
        self.ju_home_page = '' # 聚划算首页
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

    def antPage(self):
        try:
            # 获取品牌团列表页数据
            self.channel_activity()
        except Exception as e:
            print '# exception err in antPage info:',e
            
    def channel_activity(self):
        # 数据接口URL list
        b_url_valList = []
        # 品牌闪购
        page = self.crawler.getData(self.brand_url, self.ju_home_url)
        b_url_valList = self.activityList(page) 
        # 38女神节
        page = self.crawler.getData(self.brand38_url, self.ju_home_url)
        b_url_valList = b_url_valList + self.activityList(page)

        if b_url_valList != []:
            # 从接口中获取的数据列表
            bResult_list = []
            for b_url_val in b_url_valList:
                bResult_list += self.get_jsonData(b_url_val)
            print bResult_list

            if bResult_list and bResult_list != []:
                self.parser_activities(bResult_list)
        else:
            print '# err: not find activity json data URL list.'

    # 品牌团列表
    def activityList(self, page):
        if not page or page == '': raise Common.InvalidPageException("# brand activityList: not get JHS brand home.")
        self.ju_brand_page = page
        # 数据接口URL list
        b_url_valList = []
        # 模板1
        m = re.search(r'<div id="floor(\d+_\d+)".+?data-spm="floor\d+_\d+".+?data-ids="(.+?)"', page, flags=re.S)
        if m:
            b_url_valList = self.activityListTemp1(page)
        return b_url_valList

    # 品牌团页面模板1
    def activityListTemp1(self, page):
        #print page
        # 获取数据接口的URL
        floor_name = {}
        m = re.search(r'<div id="J_FixedNav" class="fixed-nav".+?>\s+<ul>(.+?)</ul>.+?</div>', page, flags=re.S)
        if m:
            floorname_info = m.group(1)
            p = re.compile(r'<li.+?>\s+<a href="#floor(\d+)".+?><span>(.+?)</span></a>\s+</li>', flags=re.S)
            for floor in p.finditer(floorname_info):
                i, name = floor.group(1), floor.group(2)
                floor_name[i] = name

        f_preurl = ''
        m = re.search(r'lazy.destroy\(\);\s+S\.IO\({\s+url: "(.+?)",\s+"data": {(.+?)},.+?\)}', page, flags=re.S)
        if m:
            url, data_s = m.group(1), ''.join(m.group(2).split())
            data_list = data_s.split(',"')
            add_data = ''
            for data in data_list:
                data = data.replace('"','')
                if data.find('brandIds') == -1:
                    add_data = add_data + "=".join(data.split(':')) + '&'
            f_preurl = url + '?' + add_data
        if f_preurl == '':
            f_preurl = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?btypes=1,2&stype=bindex,saima1,biscore,bscore,sscore&reverse=down,down,down,down,down&showType=2&includeForecast=true&'
            
        url_valList = []
        p = re.compile(r'<div id="floor(\d+_\d+)".+?data-spm="floor\d+_\d+".+?data-ids="(.+?)"', flags=re.S)
        for floor in p.finditer(page):
            f_id, f_activitySignId = floor.group(1), floor.group(2)
            print '# activity floor:', f_id, f_activitySignId
            f_url = f_preurl + 'brandIds=%s'%f_activitySignId
            f_catid = f_id.split('_')[0]
            f_catname = ''
            if floor_name.has_key(f_catid):
                f_catname = floor_name[f_catid]
            url_valList.append((f_url,f_catname,f_catid))

        return url_valList

    # 通过数据接口获取每一页的数据
    def get_jsonData(self, val):
        bResult_list = []
        try:
            b_url, f_name, f_catid = val
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            b_url = b_url + '&_ksTS=%s'%ts
            b_page = self.crawler.getData(b_url, Config.ju_brand_home)
            if not b_page or b_page == '': raise Common.InvalidPageException("# brand get_jsonData: not get jsondata url:%s,floorname:%s,floorid:%s."%(b_url, f_name, f_catid))
            result = json.loads(b_page)
            #print b_url
            bResult_list.append([result,f_name,f_catid])
            # 分页从接口中获取数据
            if result.has_key('totalPage') and int(result['totalPage']) > 1:
                for page_i in range(2, int(result['totalPage'])+1):
                    ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                    b_url = re.sub('page=\d+&', 'page=%d&'%page_i, b_url)
                    b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                    b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                    if not b_page or b_page == '': raise Common.InvalidPageException("# brand get_jsonData: not get jsondata url:%s,floorname:%s,floorid:%s."%(b_url, f_name, f_catid))
                    result = json.loads(b_page)
                    #print b_url
                    bResult_list.append([result, f_name, f_catid])
        except Exception as e:
            print '# exception err in get_jsonData info:',e

        return bResult_list

    # 解析每一页的数据
    def parser_activities(self, bResult_list):
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
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
                    # 每页取60条数据 ###需要修改（60）###
                    #b_position_start = (int(i_page['currentPage']) - 1) * 60
                    b_position_start = (int(i_page['currentPage']) - 1) * prepage_count
                else:
                    # 保存前一页的数据条数
                    prepage_count = len(activities)
                print '# brand every page num:',len(activities)
                for i in range(0,len(activities)):
                    activity = activities[i]
                    val = (activity, page[2], page[1], (b_position_start+i+1), self.begin_time, self.home_brands)
                    act_valList.append(val)
        print '# activity num:',len(act_valList)
        #if len(act_valList) > 0:
        #    self.run_brandAct(act_valList)
        #else:
        #    print '# err: not find activity crawling val list'
    
    # 多线程抓去品牌团活动
    def run_brandAct(self, act_valList):
        # Test 只测前两个
        #act_test = []
        #act_test.append(act_valList[0])
        #act_test.append(act_valList[1])
        #act_valList = act_test

        newact_num = 0
        ladygo_num = 0
        allitem_num = 0
        crawler_val_list = []
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #m_Obj = JHSCrawlerM(1, Config.act_max_th)
        m_Obj = JHSBActItemM(3, Config.act_max_th)
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
                        brandact_itemVal_list, sql, daySql, hourSql, crawling_confirm = b
                        brandact_id, brandact_name, brandact_url, brandact_sign = sql[1], sql[7], sql[8], sql[13]
                        # 判断本活动是不是即将开团
                        if crawling_confirm == 1:
                            newact_num += 1
                            #print sql
                            #print sql,daySql,hourSql
                            # 品牌团活动入库
                            #self.mysqlAccess.insertJhsAct(sql)
                            #self.mysqlAccess.insertJhsActDayalive(daySql)
                            #self.mysqlAccess.insertJhsActHouralive(hourSql)
                            # 只抓取非俪人购商品
                            if int(brandact_sign) != 3:
                                # Activity Items
                                # item init val list
                                if brandact_itemVal_list and len(brandact_itemVal_list) > 0:
                                    crawler_val_list.append((brandact_id,brandact_name,brandact_itemVal_list))
                                    allitem_num = allitem_num + len(brandact_itemVal_list)
                                    print '# activity id:%s name:%s url:%s'%(brandact_id, brandact_name, brandact_url)
                                    print '# activity items num:', len(brandact_itemVal_list)
                            else:
                                print '# activity id:%s name:%s url:%s'%(brandact_id, brandact_name, brandact_url)
                                ladygo_num += 1
                            print '# A activity end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            print '#####A activity end#####'
                        else:
                            print '# Not New activity, id:%s name:%s url:%s'%(brandact_id, brandact_name, brandact_url)
                    break
            except Exception as e:
                print '# exception err crawl activity item, %s err:'%(sys._getframe().f_back.f_code.co_name),e 
                #traceback.print_exc()
                self.traceback_log()
                break
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# All brand activity num:', len(act_valList)
        print '# New add brand activity num:', newact_num
        print '# New add brand activity(ladygo) num:', ladygo_num
        print '# New add brand activity items num:', allitem_num

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
                    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    if m_itemsObj.empty_q():
                        item_list = m_itemsObj.items
                        print '# Activity Items num:', len(item_list)
                        """
                        itemsql_list, itemhoursql_list, itemstocksql_list = [], [], []
                        for item in item_list:
                            sql, hourSql, stockSql = item
                            #print sql,hourSql,stockSql
                            if len(itemsql_list) >= Config.item_max_arg:
                                self.mysqlAccess.insertJhsItem(itemsql_list)
                                itemsql_list = []
                            else:
                                itemsql_list.append(sql)
                            if len(itemhoursql_list) >= Config.item_max_arg:
                                self.mysqlAccess.insertJhsItemSaleForHour(itemhoursql_list)
                                itemhoursql_list = []
                            else:
                                itemhoursql_list.append(hourSql)
                            if len(itemstocksql_list) >= Config.item_max_arg:
                                self.mysqlAccess.insertJhsItemStockForHour(itemstocksql_list)
                                itemstocksql_list = []
                            else:
                                itemstocksql_list.append(stockSql)
                        if len(itemsql_list) > 0:
                            self.mysqlAccess.insertJhsItem(itemsql_list)
                        if len(itemhoursql_list) > 0:
                            self.mysqlAccess.insertJhsItemSaleForHour(itemhoursql_list)
                        if len(itemstocksql_list) > 0:
                            self.mysqlAccess.insertJhsItemStockForHour(itemstocksql_list)
                        """
                        print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
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
    pass
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrand()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


