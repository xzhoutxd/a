#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import re
import random
import json
import time
import Common
from TBCrawler import TBCrawler

class JhsSite():
    '''A class of Juhuasuan Site'''
    def __init__(self):
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

        # 获取每页JSON数据
        self.datapage_url = 'http://ju.taobao.com/json/tg/ajaxGetHomeItemsV2.json?type=0&stype=soldCount&callback=homelist' # 按照销量排行

        # 页面
        self.site_page  = None

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

        self.brandList(page)

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
                date_str = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                s_url = self.datapage_url + '&_ksTS=%s'%date_str + '&page=%d' %i
                print '# today items:', i, s_url

                s_page = self.crawler.getData(s_url, self.today_url)
                self.todayItemsByPage(s_page)

    def todayItemsByPage(self, page):
        try:
            m = re.search(r'homelist\((.+?)\)$', page, flags=re.S)
            if m:
                result = json.loads(m.group(1))
                if result.has_key("code") and int(result["code"]) == 200 and result.has_key("itemList") and result["itemList"] != []:
                    item_list = result["itemList"]
                    for item in item_list:
                        i_url, i_price, i_jhsprice, i_discount, i_favor, i_salenum = '', '', '', '', '', ''
                        i_title, i_subtitle, i_jhstitle, i_img = '', '', '', ''

                        if item.has_key("baseinfo"):
                            item_baseino = item["baseinfo"]
                            # item pic
                            if item_baseino.has_key("picUrl") and item_baseino["picUrl"] != '':
                                i_img = item_baseino["picUrl"]
                            # item url
                            if item_baseino.has_key("itemUrl") and item_baseino["itemUrl"] != '':
                                i_url = item_baseino["itemUrl"]



                        # item jhs title
                        if item.has_key("merit") and item["merit"].has_key("up") and item["merit"]["up"] != []:
                            i_jhstitle = ' '.join(item["merit"]["up"])


                        if item.has_key("name"):
                            item_name = item["name"]
                            # item title, subtitle
                            if item_name.has_key("title") and item_name["title"] != '':
                                i_title = item_name["title"]
                            if item_name.has_key("shortName") and item_name["shortName"] != '':
                                i_subtitle = item_name["shortName"]

                        # item price
                        if item.has_key("price") and item["price"].has_key("origPrice") and item["price"]["origPrice"] != '':
                            i_price = item["price"]["origPrice"]

                        # item jhs price
                        if item.has_key("price") and item["price"].has_key("actPrice") and item["price"]["actPrice"] != '':
                            i_jhsprice = item["price"]["actPrice"]

                        # item discount
                        if item.has_key("price") and item["price"].has_key("discount") and item["price"]["discount"] != '':
                            i_discount = item["price"]["discount"]

                        # item favor
                        #if item.has_key() and item[""] != '':
                        #    i_favor = item[""]

                        # item sale num
                        if item.has_key("remind") and item["remind"].has_key("soldCount") and item["remind"]["soldCount"] != '':
                            i_salenum = item["remind"]["soldCount"]

                        print '# item:', i_url, i_price, i_jhsprice, i_discount, i_salenum, i_favor, i_title, i_subtitle, i_jhstitle, i_img
                else:
                    print '# err: json result\'s code is not 200 or no itemList'
        except StandardError as err:
            print '# err:', err

    # 品牌团列表
    def brandList(self, page):
        m = re.search(r'<div class="slide-logos" data-spm="a">(.+?)</div>', page, flags=re.S)
        if m:
            pass

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
    j = JhsSite()
    j.todayChannel()
#     j.lifeChannel()
#    j.lifeCity()

