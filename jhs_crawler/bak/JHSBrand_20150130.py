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
        self.item_max_th = 40 # 商品抓取时的最大线程
        

    def antPage(self):
        # 获取首页的品牌团
        page = self.crawler.getData(self.ju_home_url, self.refers)
        self.homeBrandAct(page) 

        # 获取品牌团列表页数据
        page = self.crawler.getData(self.brand_url, self.ju_home_url)
        self.activityList(page) 

    # 首页的品牌团
    def homeBrandAct(self, page):
        if not page or page == '': return

        print '首页品牌团'
        print '# ju home brand start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.ju_home_page = page
        m = re.search(r'<ul id="brandList" class="clearfix">(.+?)</ul>', page, flags=re.S)
        if m:
            brandact_content = m.group(1)
            p = re.compile(r'<li class="brand-mid-v2".+?>(.+?)</li>', flags=re.S)
            i = 0
            for brand_act in p.finditer(brandact_content):
                i += 1
                m = re.search(r'<a class="link-box hover-avil" href="(.+?)".+?>.+?<span class="title">(.+?)</span>.+?</a>', brand_act.group(1), flags=re.S)
                if m:
                    brand_act_id, brand_act_url, brand_act_name = '', '', ''
                    brand_act_url, brand_act_name = m.group(1), m.group(2)
                    m = re.search(r'act_sign_id=(\d+)', brand_act_url, flags=re.S)
                    if m:
                        brand_act_id = str(m.group(1))
                        self.home_brands[brand_act_id] = {'name':brand_act_name,'url':brand_act_url,'position':i}
                    else:
                        m = re.search(r'minisiteId=(\d+)', brand_act_url, flags=re.S)
                        if m:
                            brand_act_id = str(m.group(1))
                            self.home_brands[brand_act_id] = {'name':brand_act_name,'url':brand_act_url,'position':i}
                        else:
                            key = brand_act_url.split('?')[0]
                            if key.find('brand_items.htm') == -1:
                                self.home_brands[key] = {'name':brand_act_name,'url':brand_act_url,'position':i}
                            else:
                                print '# home brand not find info: url:%s'%brand_act_url

                    self.home_brands_list.append({'id':brand_act_id,'name':brand_act_name,'url':brand_act_url,'position':i})
                    print i, brand_act_id, brand_act_url, brand_act_name
        print '# ju home brand end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 品牌团列表
    def activityList(self, page):
        if not page or page == '': return

        self.ju_brand_page = page
        bResult_list = []
        m = re.search(r'<div class="tb-module ju-brand-floor">(.+?)</div>\s*</div>\s*</div>\s*<div class="J_Module skin-default"', page, flags=re.S)
        if m:
            activity_floors = m.group(1)
            p = re.compile(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', flags=re.S)
            for activity_floor in p.finditer(activity_floors):
                activity_floor_info = activity_floor.group(1)
                f_name, f_catid, f_activitySignId = '', '', ''
                m = re.search(r'data-floorName="(.+?)"\s+', activity_floor_info, flags=re.S)
                if m:
                    f_name = m.group(1)

                m = re.search(r'data-catid=\'(.+?)\'\s+', activity_floor_info, flags=re.S)
                if m:
                    f_catid = m.group(1)

                m = re.search(r'data-activitySignId=\"(.+?)\"$', activity_floor_info, flags=re.S)
                if m:
                    f_activitySignId = m.group(1)
                print '# activity floor:', f_name, f_catid, f_activitySignId

                begin_page = 1
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                if f_activitySignId != '':
                    b_url = self.brand_page_url + '&page=%d'%begin_page + '&activitySignId=%s'%f_activitySignId.replace(',','%2C') + '&stype=ids' + '&_ksTS=%s'%ts
                else:
                    b_url = self.brand_page_url + '&page=%d'%begin_page + '&frontCatIds=%s'%f_catid + '&_ksTS=%s'%ts
                try:
                    b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                    result = json.loads(b_page)
                    #print b_url
                    bResult_list.append([result,f_name,f_catid])
                    if result.has_key('totalPage') and int(result['totalPage']) > begin_page:
                        for page_i in range(begin_page+1, int(result['totalPage'])+1):
                            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                            b_url = re.sub('&page=\d+&', '&page=%d&'%page_i, b_url)
                            b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                            b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                            result = json.loads(b_page)
                            #print b_url
                            bResult_list.append([result, f_name, f_catid])
                except StandardError as err:
                    print '# err:',err

        act_valList = []
        for page in bResult_list:
            i_page = page[0]
            if i_page.has_key('brandList') and i_page['brandList'] != []:
                activities = i_page['brandList']
                b_position_start = 0
                if i_page.has_key('currentPage') and int(i_page['currentPage']) > 1:
                    # 每页取60条数据 ###需要修改（60）###
                    b_position_start = (int(i_page['currentPage']) - 1) * 60
                for i in range(0,len(activities)):
                    activity = activities[i]
                    val = (activity, page[2], page[1], (b_position_start+i+1), self.begin_date, self.begin_hour, self.home_brands)
                    act_valList.append(val)
        if len(act_valList) > 0:
            self.run_brandAct(act_valList)

    
    # 多线程抓去品牌团活动
    def run_brandAct(self, act_valList):
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
                        # 判断本活动是否需要爬取
                        if crawling_confirm == 1:
                            newact_num += 1
                            #print sql
                            # 品牌团活动入库
                            self.mysqlAccess.insertJhsAct(sql)
                            self.mysqlAccess.insertJhsActDayalive(daySql)
                            self.mysqlAccess.insertJhsActHouralive(hourSql)
                            #print sql
                            # 只抓取非俪人购商品
                            if brandact_sign != 3:
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
            except StandardError as err:
                print '# %s err:'%(sys._getframe().f_back.f_code.co_name),err  
                traceback.print_exc()
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
            m_itemsObj.putItems(item_valTuple)
            m_itemsObj.createthread()
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
                    print 'Unknown exception item result :', e
                    traceback.print_exc()

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
                        print 'Unknown exception item result :', e
                        traceback.print_exc()
        """


if __name__ == '__main__':
    pass
