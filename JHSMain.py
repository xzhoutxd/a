#-*- coding:utf-8 -*-
#!/usr/local/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import threading
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler
from JHSBActItem import JHSBActItem
from JHSItem import JHSItem
from db.MysqlAccess import MysqlAccess

class JHSMain():
    '''A class of Juhuasuan Main Site'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler    = TBCrawler()

        # 首页
        self.home_url   = 'http://ju.taobao.com'
        self.refers     = 'http://www.tmall.com'

        # 频道
        self.today_url  = 'http://ju.taobao.com/tg/today_items.htm?type=0' # 商品团

        self.brand_url  = 'http://ju.taobao.com/tg/brand.htm'         # 品牌团
        self.point_url  = 'http://ju.taobao.com/tg/point_list.htm'    # 整点聚
        self.jump_url   = 'http://mingpin.taobao.com'                 # 聚名品
        self.life_url   = 'http://ju.taobao.com/tg/ju_life_home.htm'  # 生活汇
        self.travel_url = 'http://ju.taobao.com/jusp/trip/tp.htm'     # 旅游团
        self.liang_url  = 'http://ju.taobao.com/jusp/liangfan/tp.htm' # 量贩团
        self.te_url     = 'http://ladygo.tmall.com'                   # 特卖汇

        # 城市列表
        self.city_url   = 'http://ju.taobao.com/tg/city/cityList.htm' # 切换城市列表
        self.cities     = {}
        self.categories = {}

        # 页面
        self.site_page  = None
        # 商品团页面
        #self.today_page_url = 'http://ju.taobao.com/json/tg/ajaxGetHomeItemsV2.json?type=0&stype=soldCount&callback=homelist' # 按照销量排行
        self.today_page_url = 'http://ju.taobao.com/json/tg/ajaxGetHomeItemsV2.json?type=0&stype=soldCount' # 按照销量排行
        # 品牌团页面
        self.brand_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=0'
        self.brand_find = 0
        self.brand_get = 0
        self.brand_coupon_find = 0
        self.brand_coupon_get = 0
        self.bPage_list = []

    # 商品团频道
    def todayChannel(self):
        page = self.crawler.getData(self.today_url, self.refers)
        if not page or page == '': return

        #self.todayCategory(page)
        self.todayItems(page)

    # 品牌团频道
    def brandChannel(self):
        page = self.crawler.getData(self.brand_url, self.refers)
        if not page or page == '': return

        self.activityList(page)

    # 生活汇频道
    def lifeChannel(self):
        page = self.crawler.getData(self.life_url, self.refers)
        if not page or page == '': return

        self.lifeCategory(page)

    # 商品团类目
    def todayCategory(self, page):
        #m = re.search(r'<ul class="category J_HomeCates">(.+?)</ul>', page, flags=re.S)
        m = re.search(r'<div class="cat-menu-v" .+?>(.+?)</div>', page, flags=re.S)
        if m:
            cats = m.group(1)
            #p = re.compile(r'<li>\s+<a href="(.+?)" .+?>\s+<span>(.+?)</span>\s+</a>\s+</li>', flags=re.S)
            p = re.compile(r'<td>\s+<a href="(.+?)" .+?>(.+?)</a>\s+</td>', flags=re.S)
            for cat in p.finditer(cats):
                c_url, c_name = cat.group(1), cat.group(2)
                print '# today category:', c_name, c_url
                self.categories[c_name] = c_url

    # 商品团商品
    def todayItems(self, page):
        m = re.search(r'\"totalPage\":(\d+),', page, flags=re.S)
        if m:
            page_num = int(m.group(1))
            for i in range(1, page_num+1):
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                s_url = self.today_page_url + '&_ksTS=%s'%ts + '&page=%d' %i
                print '# today items:', i, s_url

                s_page = self.crawler.getData(s_url, self.today_url)
                self.todayItemsByPage(s_page)

    def todayItemsByPage(self, page):
        try:
            #m = re.search(r'homelist\((.+?)\)$', page, flags=re.S)
            m = re.search(r'^{.+?\"itemList\":\[.+?\].+?}$', page, flags=re.S)
            if m:
                #result = json.loads(m.group(1))
                result = json.loads(page)
                if result.has_key('code') and int(result['code']) == 200 and result.has_key('itemList') and result['itemList'] != []:
                    item_list = result['itemList']
                    for item in item_list:
                        i_url, i_price, i_jhsprice, i_discount, i_favor, i_salenum = '', '', '', '', '', ''
                        i_title, i_subtitle, i_jhstitle, i_img = '', '', '', ''

                        if item.has_key('baseinfo'):
                            item_baseino = item['baseinfo']
                            # item pic
                            if item_baseino.has_key('picUrl') and item_baseino['picUrl'] != '':
                                i_img = item_baseino['picUrl']
                            # item url
                            if item_baseino.has_key('itemUrl') and item_baseino['itemUrl'] != '':
                                i_url = item_baseino['itemUrl']

                        # item jhs title
                        if item.has_key('merit') and item['merit'].has_key('up') and item['merit']['up'] != []:
                            i_jhstitle = ' '.join(item['merit']['up'])

                        if item.has_key('name'):
                            item_name = item['name']
                            # item title, subtitle
                            if item_name.has_key('title') and item_name['title'] != '':
                                i_title = item_name['title']
                            if item_name.has_key('shortName') and item_name['shortName'] != '':
                                i_subtitle = item_name['shortName']

                        # item price
                        if item.has_key('price') and item['price'].has_key('origPrice') and item['price']['origPrice'] != '':
                            i_price = item['price']['origPrice']

                        # item jhs price
                        if item.has_key('price') and item['price'].has_key('actPrice') and item['price']['actPrice'] != '':
                            i_jhsprice = item['price']['actPrice']

                        # item discount
                        if item.has_key('price') and item['price'].has_key('discount') and item['price']['discount'] != '':
                            i_discount = item['price']['discount']

                        # item favor
                        #if item.has_key('') and item[''] != '':
                        #    i_favor = item['']

                        # item sale num
                        if item.has_key('remind') and item['remind'].has_key('soldCount') and item['remind']['soldCount'] != '':
                            i_salenum = item['remind']['soldCount']

                        print '# item:', i_url, i_price, i_jhsprice, i_discount, i_salenum, i_favor, i_title, i_subtitle, i_jhstitle, i_img
                else:
                    print '# err: json result\'s code is not 200 or no itemList'
        except StandardError as err:
            print '# err:', err

    # 品牌团列表
    def activityList(self, page):
        #print page
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

                i = 1
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                if f_activitySignId != '':
                    b_url = self.brand_page_url + '&page=%d'%i + '&activitySignId=%s'%f_activitySignId.replace(',','%2C') + '&stype=ids' + '&_ksTS=%s'%ts
                    b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                else:
                    b_url = self.brand_page_url + '&page=%d'%i + '&frontCatIds=%s'%f_catid + '&_ksTS=%s'%ts
                    b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                try:
                    result = json.loads(b_page)
                    print b_url
                    bResult_list.append([result,f_name,f_catid])
                    # 只取女装
                    #if int(f_catid) == 261000:
                    #    bResult_list.append([result,f_name,f_catid])

                    #if f_catid != '' and int(f_catid) == 261000 and result.has_key('totalPage') and int(result['totalPage']) > i:
                    if result.has_key('totalPage') and int(result['totalPage']) > i:
                        for page_i in range(i+1, int(result['totalPage'])+1):
                            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                            b_url = re.sub('&page=\d+&', '&page=%d&'%page_i, b_url)
                            b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                            b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                            result = json.loads(b_page)
                            print b_url
                            bResult_list.append([result, f_name, f_catid])
                except StandardError as err:
                    print '# err:',err

        act_list = []
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        for page in bResult_list:
            i_page = page[0]
            if i_page.has_key('brandList') and i_page['brandList'] != []:
                #self.brand_find += len(page['brandList'])
                activities = i_page['brandList']
                b_position_start = 0
                if i_page.has_key('currentPage') and int(i_page['currentPage']) > 1:
                    b_position_start = (int(i_page['currentPage']) - 1) * 60
                for i in range(0,len(activities)):
                    print '# A activity start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    activity = activities[i]
                    # 只测第一个
                    #if int(b_position_start+i) == 1 or int(b_position_start+i) == 2 or int(b_position_start+i) == 3:
                    print '#####A activity begin#####'
                    b = None
                    b = JHSBActItem()
                    b.antPage(activity, page[2], page[1], (b_position_start+i))
                    self.mysqlAccess.insertJhsAct(b.outSql())
                    act_list.append([b.brandact_id, b.brandact_name, b.brandact_url])
                    if b.brandact_sign != 3:
                        print '# activity Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                        # Activity Items
                        itemnum = self.activityItems(b.brandact_id, b.brandact_name, b.brandact_url)
                        print '# activity id:%s name:%s url:%s'%(b.brandact_id, b.brandact_name, b.brandact_url)
                        print '# activity item num:', itemnum
                        print '# activity Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print '# A activity end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    print '#####A activity end#####'
                    time.sleep(1)
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# brand activity num:', len(act_list)

        #print '#####All Activity Items Start#####'
        #print '# activity Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #for act in act_list:
        #    print '# A activity Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #    itemnum = self.activityItems(act[0], act[1], act[2])
        #    print '# activity id:%s name:%s url:%s'%(act[0], act[1], act[2])
        #    print '# activity item num:', itemnum
        #    print '# A activity Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #print '# activity Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #print '#####All Activity Items End#####'


    def activityItems(self, actId, actName, actUrl):
        #print '# activity Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        page = self.crawler.getData(actUrl, Config.ju_brand_home)
        m = re.search(r'<div id="content">(.+?)</div>\s+<div class="crazy-wrap">', page, flags=re.S)
        position = 0
        if m:
            page = m.group(1)
            # 商品
            m = re.search(r'<div class="act-main ju-itemlist">', page, flags=re.S)
            if m:
                # source html floor
                p = re.compile(r'<div class="act-item0">(.+?)</div>\s+<img', flags=re.S)
                position += self.itemByBrandPage(page, actId, actName, p, position, actUrl)
                m = re.search(r'<div class="act-item1">\s+<ul>(.+?)</u>\s+</div>', page, flags=re.S)
                if m:
                    item1_page = m.group(1)
                    p = re.compile(r'<li>(.+?)</li>', flags=re.S)
                    position += self.itemByBrandPage(item1_page, actId, actName, p, position, actUrl)

                # other floor
                getdata_url = "http://ju.taobao.com/json/tg/ajaxGetItems.htm?stype=ids&styleType=small&includeForecast=true"
                p = re.compile(r'<div class="act-item J_jupicker" data-item="(.+?)">', flags=re.S)
                for floor_url in p.finditer(page):
                    ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                    f_url = getdata_url + '&juIds=' + floor_url.group(1) + '&_ksTS=%s'%ts
                    print f_url
                    f_page = self.crawler.getData(f_url, actUrl)
                    m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
                    if m:
                        f_html = m.group(1)
                        p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
                        position += self.itemByBrandPage(f_html, actId, actName, p, position, actUrl)
                
            else:
                # source html floor
                p = re.compile(r'<li class="item-big-v2">(.+?)</li>', flags=re.S)
                position += self.itemByBrandPage(page, actId, actName, p, position, actUrl)

                # other floor
                p = re.compile(r'<div class="l-floor J_Floor J_ItemList" .+? data-url="(.+?)">', flags=re.S)
                for floor_url in p.finditer(page):
                    ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                    f_url = floor_url.group(1) + '&_ksTS=%s'%ts
                    print f_url
                    f_page = self.crawler.getData(f_url, actUrl)
                    m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
                    if m:
                        f_html = m.group(1)
                        p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
                        position += self.itemByBrandPage(f_html, actId, actName, p, position, actUrl)
        return position
        #print '# activity Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    def itemByBrandPage(self, page, actId, actName, p, position, actUrl):
        i = 0
        for ju_item in p.finditer(page):
            i += 1
            # 只测第一个
            #if position+i < 10:
            if position+i:
                ju_item_html = ju_item.group(1)
                item = None
                item = JHSItem()
                item.antPage(ju_item_html, actId, actName, actUrl, position+i)
                self.mysqlAccess.insertJhsItem(item.outSql())
                time.sleep(1)

        return i

    # 生活汇类目
    def lifeCategory(self, page):
        m = re.search(r'<ul class="category cate-life">(.+?)</ul>', page, flags=re.S)
        if m:
            cats = m.group(1)
            p = re.compile(r'<li>\s+<a href="(.+?)" .+?>\s+<span>(.+?)</span>\s+</a>\s+</li>', flags=re.S)
            for cat in p.finditer(cats):
                c_url, c_name = cat.group(1), cat.group(2)
                print '# today category:', c_name, c_url

    # 生活汇城市
    def lifeCity(self):
        page = self.crawler.getData(self.city_url, self.life_url)
        if not page or page == '': return

        m = re.search(r'<div class="cities-list-content">(.+?)</div>', page, flags=re.S)
        if m:
            city_list = m.group(1)
            p = re.compile(r'<a href="(.+?)">(.+?)</a>', flags=re.S)
            for city in p.finditer(city_list):
                c_name, c_url = city.group(1), city.group(2)
                print '# life city:', c_name, c_url
                self.cities[c_name] = c_url

if __name__ == '__main__':
    j = JHSMain()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    j.brandChannel()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
