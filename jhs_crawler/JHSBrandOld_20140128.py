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
from memory_profiler import profile
from base.TBCrawler import TBCrawler
from db.MysqlAccess import MysqlAccess
from JHSCrawlerM import JHSCrawlerM
#from JHSBActItemM import JHSBActItemM
from JHSItem import JHSItem
#from JHSItemM import JHSItemM

class JHSBrand():
    '''A class of brand Item'''
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
        self.item_max_th = 30 # 商品抓取时的最大线程
        

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
                    val = (activity, page[2], page[1], (b_position_start+i+1), self.begin_date, self.begin_hour)
                    act_valList.append(val)
                    # 分隔抓取
                    #if len(act_valList) == self.gap_num:
                    #self.run_brandAct(act_valList)
                    #act_valList = []
        if len(act_valList) > 0:
            self.run_brandAct(act_valList)

    
    @profile
    # 多线程抓去品牌团活动
    def run_brandAct(self, act_valList):
        ladygo_num = 0
        allitem_num = 0
        crawler_list = []
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #m_Obj = JHSBActItemM()
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
                        key1, key2 = str(b.brandact_id), b.brandact_url.split('?')[0]
                        # 判断是否在首页推广
                        if self.home_brands.has_key(key1):
                            b.brandact_inJuHome = 1
                            b.brandact_juHome_position = self.home_brands[key1]['position']
                        elif self.home_brands.has_key(key2):
                            b.brandact_inJuHome = 1
                            b.brandact_juHome_position = self.home_brands[key2]['position']
                        # 品牌团活动入库
                        self.mysqlAccess.insertJhsAct(b.outSql())
                        #print b.outSql()
                        # 只抓取非俪人购商品
                        if b.brandact_sign != 3:
                            print '# activity Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), b.brandact_id, b.brandact_name
                            # Activity Items
                            # item init val list
                            item_valList = None
                            item_valList = b.brandact_itemVal_list
                            if len(item_valList) > 0:
                                # 多线程 控制并发的线程数
                                if len(item_valList) > self.item_max_th:
                                    m_itemsObj = JHSCrawlerM(2, self.item_max_th)
                                else:
                                    m_itemsObj = JHSCrawlerM(2,len(item_valList))
                                m_itemsObj.putItems(item_valList)
                                crawler_list.append((b.brandact_id,b.brandact_name,m_itemsObj))
                                allitem_num = allitem_num + len(item_valList)
                                print '# activity id:%s name:%s url:%s'%(b.brandact_id, b.brandact_name, b.brandact_url)
                                print '# activity items num:', len(item_valList)
                                print '# activity Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        else:
                            ladygo_num += 1
                        print '# A activity end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        print '#####A activity end#####'
                        # 分隔抓取
                        if len(crawler_list) == self.gap_num:
                            result = self.run_brandItems(crawler_list)
                            crawler_list = []
                        #time.sleep(1)
                    del item_list
                    del m_Obj
                    break
            except StandardError as err:
                print '# %s err:'%(sys._getframe().f_back.f_code.co_name),err  
                traceback.print_exc()
        if len(crawler_list) > 0:
            self.run_brandItems(crawler_list)
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# brand activity num:', len(act_valList)
        print '# brand activity(ladygo) num:', ladygo_num
        print '# brand activity items num:', allitem_num

    # 多线程抓去品牌团商品
    def run_brandItems(self, crawler_list):
        i = 0
        for crawler_thread in crawler_list:
            i += 1
            self.itemcrawler_queue.put(crawler_thread)
            m_itemsObj = crawler_thread[2]
            m_itemsObj.createthread()
            m_itemsObj.run()

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
                        self.mysqlAccess.insertJhsItem(item.outSql())
                        #print item.outSql()
                    del obj
                    del item_list
                    print '# Activity Item List End: actId:%s, actName:%s'%(actid, actname)
                else:
                    self.itemcrawler_queue.put(_item)
            except Exception as e:
                print 'Unknown exception item result :', e
                traceback.print_exc()
                #return 'Unknown exception item result :%s'%e
        #return 'ok'


    # 从品牌团页获取数据
    def activityItems(self, actId, actName, actUrl, item_valList):
        page = self.crawler.getData(actUrl, Config.ju_brand_home)
        m = re.search(r'<div id="content".+?>(.+?)</div>\s+<div class="crazy-wrap">', page, flags=re.S)
        if m:
            page = m.group(1)

        m = re.search(r'<div class="ju-itemlist">\s+<ul class="clearfix">.+?<li class="item-.+?">.+?</li>.+?</ul>\s+</div>', page, flags=re.S)
        if m:
            self.activityType1(page, actId, actName, actUrl, item_valList)
        else:
            m = re.search(r'<div class="act-main ju-itemlist">', page, flags=re.S)
            if m:
                self.activityType2(m.group(1), actId, actName, actUrl, item_valList)
            else:
                m = re.search(r'<div class="ju-itemlist J_JuHomeList">\s+<ul.+?>(.+?)</ul>', page, flags=re.S)
                if m:
                    self.activityType3(m.group(1), actId, actName, actUrl, item_valList)
                else:
                    m = re.search(r'<div class="l-floor J_Floor .+?data-ajaxurl="(.+?)">', page, flags=re.S)
                    if m:
                        self.activityType4(page, actId, actName, actUrl, item_valList)
                    else:
                        self.activityTypeOther(page, actId, actName, actUrl, item_valList)

    # 品牌团页面格式(1)
    def activityType1(self, page, actId, actName, actUrl, item_valList):
        position = 0
        # source html floor
        # 第一层
        p = re.compile(r'<li class="item-.+?">(.+?)</li>', flags=re.S)
        i = 0
        for itemdata in p.finditer(page):
            position += 1
            val = self.itemByBrandPageType1(itemdata.group(1), actId, actName, actUrl, position)
            item_valList.append(val)

        # other floor
        # 其他层数据
        p = re.compile(r'<div class="l-floor J_Floor J_ItemList" .+? data-url="(.+?)">', flags=re.S)
        for floor_url in p.finditer(page):
            f_url = (floor_url.group(1)).replace('&amp;','&')
            print f_url
            self.getItemDataFromInterface(f_url, actId, actName, actUrl, position, item_valList)

    # 品牌团页面格式(2)
    def activityType2(self, page, actId, actName, actUrl, item_valList):
        position = 0
        # source html floor
        # 第一层
        p = re.compile(r'<div class="act-item0">(.+?)</div>\s+<img', flags=re.S)
        for itemdata in p.finditer(page):
            position += 1
            val = self.itemByBrandPageType1(itemdata.group(1), actId, actName, actUrl, position)
            item_valList.append(val)
        # 第二层
        m = re.search(r'<div class="act-item1">\s+<ul>(.+?)</u>\s+</div>', page, flags=re.S)
        if m:
            item1_page = m.group(1)
            p = re.compile(r'<li>(.+?)</li>', flags=re.S)
            for itemdata in p.finditer(item1_page):
                position += 1
                val = self.itemByBrandPageType1(itemdata.group(1), actId, actName, actUrl, position)
                item_valList.append(val)

        # other floor
        # 接口数据
        getdata_url = "http://ju.taobao.com/json/tg/ajaxGetItems.htm?stype=ids&styleType=small&includeForecast=true"
        p = re.compile(r'<div class=".+?J_jupicker" data-item="(.+?)">', flags=re.S)
        for floor_url in p.finditer(page):
            f_url = getdata_url + '&juIds=' + floor_url.group(1)
            self.getItemDataFromInterface(f_url, actId, actName, actUrl, position, item_valList)


    # 品牌团页面格式(3)
    def activityType3(self, page, actId, actName, actUrl, item_valList):
        position = 0
        p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
        for itemdata in p.finditer(page):
            position += 1
            val = self.itemByBrandPageType1(itemdata.group(1), actId, actName, actUrl, position)
            item_valList.append(val)

    # 品牌团页面格式(4)
    def activityType4(self, page, actId, actName, actUrl, item_valList):
        position = 0
        # 请求接口数据
        p = re.compile(r'<div class="l-floor J_Floor .+? data-ajaxurl="(.+?)"', flags=re.S)
        for floor_url in p.finditer(page):
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            f_url = (floor_url.group(1)).replace('&amp;','&') + '&_ksTS=%s'%ts
            print f_url
            f_page = self.crawler.getData(f_url, actUrl)
            m = re.search(r'^{.+?\"itemList\":\[.+?\].+?}$', f_page, flags=re.S)
            if m:
                result = json.loads(f_page)
                if result.has_key('code') and int(result['code']) == 200 and result.has_key('itemList') and result['itemList'] != []:
                    for itemdata in result['itemList']:
                        position += 1
                        val = self.itemByBrandPageType2(itemdata, actId, actName, actUrl, position)
                        item_valList.append(val)

    # 品牌团页面格式
    def activityTypeOther(self, page, actId, actName, actUrl, item_valList):
        position = 0
        items = {}
        p = re.compile(r'<.+? href="http://detail.ju.taobao.com/home.htm?(.+?)".+?>', flags=re.S)
        for ids_str in p.finditer(page):
            ids = ids_str.group(1)
            item_id, item_juId = '', ''
            m = re.search(r'itemId=(\d+)', ids, flags=re.S)
            if m:
                item_id = m.group(1)
            m = re.search(r'item_id=(\d+)', ids, flags=re.S)
            if m:
                item_id = m.group(1)
            m = re.search(r'&id=(\d+)', ids, flags=re.S)
            if m:
                item_juId = m.group(1)
            """
            ids_list = (ids_str.group(1)).split('&')
            for s in ids_list:
                print s
                if s.find('itemId=') != -1:
                    item_id = s.split('=')[1]
                elif s.find('item_id=') != -1:
                    item_id = s.split('=')[1]
                elif s.find('id=') != -1:
                    item_juId = s.split('=')[1]
            """
             
            key = '-%s-%s'%(item_id, item_juId)
            if not items.has_key(key):
                position += 1
                item_ju_url = ''
                if item_juId != '' and item_id != '':
                    item_ju_url = 'http://detail.ju.taobao.com/home.htm?item_id=%s&id=%s'%(item_id, item_juId)
                elif item_juId != '':
                    item_ju_url = 'http://detail.ju.taobao.com/home.htm?id=%s'%item_juId
                elif item_juId != '':
                    item_ju_url = 'http://detail.ju.taobao.com/home.htm?item_id=%s'%item_id
                    
                if item_ju_url != '':
                    #self.parseItem(item_ju_url, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, '')
                    val = (item_ju_url, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, '')
                    item_valList.append(val)
                    items[key] = {'itemid':item_id,'itemjuid':item_juId}
        
        # other floor
        # 接口数据
        getdata_url = "http://ju.taobao.com/json/tg/ajaxGetItems.htm?stype=ids&styleType=small&includeForecast=true"
        p = re.compile(r'<div class=".+?J_jupicker" data-item="(.+?)">', flags=re.S)
        for floor_url in p.finditer(page):
            f_url = getdata_url + '&juIds=' + floor_url.group(1)
            self.getItemDataFromInterface(f_url, actId, actName, actUrl, position, item_valList)

    # 从接口获取数据
    def getItemDataFromInterface(self, url, actId, actName, actUrl, position, item_valList):
        ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
        f_url = url + '&_ksTS=%s'%ts
        #print f_url
        f_page = self.crawler.getData(f_url, actUrl)
        m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
        if m:
            f_html = m.group(1)
            p = re.compile(r'<li class="item-small-v3">.+?(<a.+?</a>).+?</li>', flags=re.S)
            for itemdata in p.finditer(f_html):
                position += 1
                val = self.itemByBrandPageType1(itemdata.group(1), actId, actName, actUrl, position)
                item_valList.append(val)

    # 获取商品信息类型1
    def itemByBrandPageType1(self, itemdata, actId, actName, actUrl, position):
        # 基本信息
        item_ju_url, item_id, item_juId = '', '', ''
        m = re.search(r'<a.+?href="(.+?)".+?>', itemdata, flags=re.S)
        if m:
            # 商品聚划算链接
            item_ju_url = m.group(1)
            if item_ju_url:
                ids_list = item_ju_url.split('&')
                for ids in ids_list:
                    if ids.find('item_id=') != -1:
                        # 商品Id
                        item_id = ids.split('=')[1]
                    elif ids.find('id=') != -1:
                        # 商品聚划算Id
                        item_juId = ids.split('=')[1]
        #else:
        #    print '# err: Not find item info'
        #    return

        # 商品聚划算展示图片链接
        item_juPic_url = ''
        m = re.search(r'<img class="item-pic" data-ks-lazyload="(.+?)"', itemdata, flags=re.S)
        if m:
            item_juPic_url = m.group(1)
        else:
            m = re.search(r'<img data-ks-lazyload="(.+?)"', itemdata, flags=re.S)
            if m:
                item_juPic_url = m.group(1)
            #else:
            #    print '# err: Not find item ju pic'
            #    return

        # 解析聚划算商品
        #self.parseItem(itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)
        return (itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)

    # 获取商品信息类型2
    def itemByBrandPageType2(self, itemdata, actId, actName, actUrl, position):
        # 基本信息
        item_juPic_url, item_ju_url, item_id, item_juId = '', '', '', ''
        # 基本信息
        if itemdata.has_key('baseinfo'):
            item_baseinfo = itemdata['baseinfo']
            # 商品Id
            if item_baseinfo.has_key('itemId') and item_baseinfo['itemId'] != '':
                item_id = item_baseinfo['itemId']
            # 商品juId
            if item_baseinfo.has_key('juId') and item_baseinfo['juId'] != '':
                item_juId = item_baseinfo['juId']

            # 商品聚划算展示图片链接
            if item_baseinfo.has_key('picUrl') and item_baseinfo['picUrl'] != '':
                item_juPic_url = item_baseinfo['picUrl']
            elif item_baseinfo.has_key('picUrlM') and item_baseinfo['picUrlM'] != '':
                item_juPic_url = item_baseinfo['picUrlM']
            # 商品聚划算链接
            if item_baseinfo.has_key('itemUrl') and item_baseinfo['itemUrl'] != '':
                item_ju_url = item_baseinfo['itemUrl']
                ids_list = item_ju_url.split('&')
                for ids in ids_list:
                    if ids.find('item_id=') != -1:
                        # 商品Id
                        if item_id == '':
                            item_id = ids.split('=')[1]
                    elif ids.find('id=') != -1:
                        # 商品聚划算Id
                        if item_juId == '':
                            item_juId = ids.split('=')[1]

        # 解析聚划算商品
        #self.parseItem(itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)
        return (itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)

    # 解析商品信息
    def parseItem(self, itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url):
        if int(position) < 2:
        #if int(position) > 0:
            item = None
            item = JHSItem()
            item.antPage(itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)
            self.mysqlAccess.insertJhsItem(item.outSql())
            time.sleep(1)


if __name__ == '__main__':
  
    actId, actName, actUrl = '4790221', '四大徽茶国礼茶', 'http://act.ju.taobao.com/market/sidahuicha.php'
    B = JHSBrand()
    B.activityItems(actId, actName, actUrl)



