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
from JHSCrawlerM import JHSCrawlerM
from JHSHomeBrand import JHSHomeBrand

class JHSBrand():
    '''A class of brand'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler    = TBCrawler()

        # 商品抓取队列
        self.itemcrawler_queue = Queue.Queue()

        # 首页
        self.ju_home_url   = 'http://ju.taobao.com'
        self.refers     = 'http://www.tmall.com'

        # 品牌团页面
        self.brand_url  = 'http://ju.taobao.com/tg/brand.htm'

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
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

        # 抓取间隔
        self.gap_num = 50

        # 并发线程值
        self.act_max_th = 5 # 活动抓取时的最大线程
        self.item_max_th = 10 # 商品抓取时的最大线程
        

    def antPage(self):
        try:
            # 获取首页的品牌团
            page = self.crawler.getData(self.ju_home_url, self.refers)
            hb = JHSHomeBrand()
            hb.antPage(page)
            self.home_brands = hb.home_brands
            #print self.home_brands

            # 获取品牌团列表页数据
            page = self.crawler.getData(self.brand_url, self.ju_home_url)
            self.activityList(page) 
        except Exception as e:
            print '# exception err in antPage info:',e

    # 品牌团列表
    def activityList(self, page):
        if not page or page == '': raise Common.InvalidPageException("# brand activityList: not get JHS brand home.")
        self.ju_brand_page = page
        # 数据接口URL list
        b_url_valList = []
        # 模板1
        m = re.search(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', page, flags=re.S)
        if m:
            b_url_valList = self.activityListTemp1(page)
        else:
            # 模板2
            m = re.search(r'<div id="(\d+)" class="l-floor J_Floor placeholder ju-wrapper" data-ajax="(.+?)">\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>', page, flags=re.S)
            if m:
                b_url_valList = self.activityListTemp2(page)
            else:
                print '# err: not matching all templates.'

        if b_url_valList != []:
            # 从接口中获取的数据列表
            bResult_list = []
            for b_url_val in b_url_valList:
                bResult_list += self.get_jsonData(b_url_val)

            if bResult_list and bResult_list != []:
                self.parser_activities(bResult_list)
        else:
            print '# err: not find activity json data URL list.'

    # 品牌团页面模板1
    def activityListTemp1(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', flags=re.S)
        for floor in p.finditer(page):
            floor_info = floor.group(1)
            f_name, f_catid, f_activitySignId = '', '', ''
            m = re.search(r'data-floorName="(.+?)"\s+', floor_info, flags=re.S)
            if m:
                f_name = m.group(1)

            m = re.search(r'data-catid=\'(.+?)\'\s+', floor_info, flags=re.S)
            if m:
                f_catid = m.group(1)

            m = re.search(r'data-activitySignId=\"(.+?)\"$', floor_info, flags=re.S)
            if m:
                f_activitySignId = m.group(1)
            print '# activity floor:', f_name, f_catid, f_activitySignId

            begin_page = 1
            if f_activitySignId != '':
                f_url = self.brand_page_url + '&page=%d'%begin_page + '&activitySignId=%s'%f_activitySignId.replace(',','%2C') + '&stype=ids'
                print '# brand activity floor: %s activitySignIds: %s, url: %s'%(f_name, f_activitySignId, f_url)
            else:
                f_url = self.brand_page_url + '&page=%d'%begin_page + '&frontCatIds=%s'%f_catid
                print '# brand activity floor:', f_name, f_catid, f_url
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 品牌团页面模板2
    def activityListTemp2(self, page):
        # 推荐
        m = re.search(r'<div id="todayBrand".+?>.+?<div class="ju-itemlist">\s+<ul class="clearfix J_BrandList" data-spm="floor1">(.+?)</ul>', page, flags=re.S)
        if m:
            brand_list = m.group(1)
            today_i = 0
            p = re.compile(r'<li class="brand-mid-v2".+?>.+?<a.+?href="(.+?)".+?>.+?</li>', flags=re.S)
            for act in p.finditer(brand_list):
                act_url = act.group(1)
                act_id = ''
                today_i += 1
                m = re.search(r'act_sign_id=(\d+)', act_url, flags=re.S)
                if m:
                    act_id = m.group(1)
                print '# today brand: position:%s,id:%s,url:%s'%(str(today_i),str(act_id),act_url)
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div id="(\d+)" class="l-floor J_Floor placeholder ju-wrapper" data-ajax="(.+?)">\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>', flags=re.S)
        for floor in p.finditer(page):
            f_name, f_catid, f_url, f_activitySignId = '', '', '', ''
            f_catid, f_url, f_name = floor.group(1), floor.group(2), floor.group(3)
            if f_url != '':
                print '# brand activity floor:', f_name, f_catid, f_url
                # 只抓时尚女士,精品男士
                if int(f_catid) == 261000 or int(f_catid) == 262000:
                    url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 通过数据接口获取每一页的数据
    def get_jsonData(self, val):
        bResult_list = []
        try:
            b_url, f_name, f_catid = val
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            b_url = b_url + '&_ksTS=%s'%ts
            b_page = self.crawler.getData(b_url, Config.ju_brand_home)
            result = json.loads(b_page)
            #print b_url
            bResult_list.append([result,f_name,f_catid])
            # 分页从接口中获取数据
            if result.has_key('totalPage') and int(result['totalPage']) > 1:
                for page_i in range(2, int(result['totalPage'])+1):
                    ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                    b_url = re.sub('&page=\d+&', '&page=%d&'%page_i, b_url)
                    b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                    b_page = self.crawler.getData(b_url, Config.ju_brand_home)
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
                    val = (activity, page[2], page[1], (b_position_start+i+1), self.begin_date, self.begin_hour, self.home_brands)
                    act_valList.append(val)
        if len(act_valList) > 0:
            self.run_brandAct(act_valList)
        else:
            print '# err: not find activity crawling val list'
    
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
        m_Obj = JHSCrawlerM(1, self.act_max_th)
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
                            # 品牌团活动入库
                            self.mysqlAccess.insertJhsAct(sql)
                            self.mysqlAccess.insertJhsActDayalive(daySql)
                            self.mysqlAccess.insertJhsActHouralive(hourSql)
                            #print sql,daySql,hourSql
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
                                ladygo_num += 1
                            print '# A activity end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                            print '#####A activity end#####'
                            #time.sleep(1)
                        else:
                            print '# Not New activity, id:%s name:%s url:%s'%(brandact_id, brandact_name, brandact_url)
                    #del item_list
                    #del m_Obj
                    break
            except Exception as e:
                print '# exception err crawl activity item, %s err:'%(sys._getframe().f_back.f_code.co_name),e 
                #traceback.print_exc()
                print '#####--Traceback Start--#####'
                tp,val,td = sys.exc_info()
                for file, lineno, function, text in traceback.extract_tb(td):
                    print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                    print text
                print "exception traceback err:%s,%s,%s"%(tp,val,td)
                print '#####--Traceback End--#####'
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
            if len(item_valTuple) > self.item_max_th:
                m_itemsObj = JHSCrawlerM(2, self.item_max_th)
            else: 
                m_itemsObj = JHSCrawlerM(2, len(item_valTuple))
            m_itemsObj.createthread()
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.run()

            while True:
                try:
                    print '# Item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
                    if m_itemsObj.empty_q():
                        item_list = m_itemsObj.items
                        for item in item_list:
                            sql, hourSql = item
                            #print sql,hourSql
                            self.mysqlAccess.insertJhsItem(sql)
                            self.mysqlAccess.insertJhsItemForHour(hourSql)
                        print '# Activity Item List End: actId:%s, actName:%s'%(brandact_id, brandact_name)
                        break
                except Exception as e:
                    print '# exception err crawl item: ', e
                    print '# crawler_val:', crawler_val
                    print '#####--Traceback Start--#####'
                    tp,val,td = sys.exc_info()
                    for file, lineno, function, text in traceback.extract_tb(td):
                        print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                        print text
                    print "exception traceback err:%s,%s,%s"%(tp,val,td)
                    print '#####--Traceback End--#####'
                    #traceback.print_exc()
                    break

        """
            self.itemcrawler_queue.put((brandact_id, brandact_name, m_itemsObj))
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.createthread()
            m_itemsObj.run()
            i += 1
            if i % self.gap_num == 0 or i == len(crawler_val_list):
                while True:
                    try:
                        #print 'item queue'
                        # 队列为空，退出
                        if self.itemcrawler_queue.empty(): break
                        _item = self.itemcrawler_queue.get()
                        actid, actname, obj = _item
                        print '# Item Check: actId:%s, actName:%s'%(actid, actname)
                        if obj.empty_q():
                            item_list = obj.items
                            for item in item_list:
                                sql, hourSql = item
                                #self.mysqlAccess.insertJhsItem(item.outSql())
                                self.mysqlAccess.insertJhsItem(sql)
                                self.mysqlAccess.insertJhsItemForHour(hourSql)
                            #del obj
                            #del item_list
                            print '# Activity Item List End: actId:%s, actName:%s'%(actid, actname)
                            break
                        else:
                            self.itemcrawler_queue.put(_item)
                    except Exception as e:
                        print '# exception err crawl item: ', e
                        traceback.print_exc()
                        break
        """

if __name__ == '__main__':
    pass
    """
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrand()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    """


