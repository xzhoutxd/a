#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import re
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

        # 页面
        self.site_page  = None

    # 商品团频道
    def todayChannel(self):
        page = self.crawler.getData(self.today_url, self.refers)
        #page = self.crawler.getData(self.home_url, self.refers)
        if not page or page == '': return
        #print page

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
        #m = re.search(r'<span class="sum">\s+<em>\s+1\s+</em>\s+/(\d+)</span>', page, flags=re.S)
        m = re.search(r'\"totalPage\":(\d+),', page, flags=re.S)
        print int(m)
        if m:
            page_num = int(m.group(1))
            for i in range(1, page_num):
                s_url = self.today_url + '&page=%d' %i
                print '# today items:', i, s_url

                s_page = self.crawler.getData(s_url, self.today_url)
                self.todayItemsByPage(s_page)

    def todayItemsByPage(self, page):
        m = re.search(r'<ul class="clearfix" data-spm="1" .+?>(.+?)</ul>', page, flags=re.S)
        if m:
            item_list = m.group(1)
            p = re.compile(r'<li class="item-small-v2" .+?">(.+?)</li>', flags=re.S)
            for item in p.finditer(item_list):
                item_data = item.group(1)

                i_url, i_price, i_promoprice, i_discount, i_favor, i_salenum = '', '', '', '', '', ''
                i_title, i_subtitle, i_jhstitle, i_img = '', '', '', ''

                # item pic
                r = re.search(r'<img class="item-pic" data-ks-lazyload="(.+?)"\s/>', item_data, flags=re.S)
                if r: i_img = r.group(1)

                # item jhs title
                r = re.search(r'<h4>\s+(.+?)\s+</h4>', item_data, flags=re.S)
                if r: i_jhstitle = r.group(1).replace('\n',',')

                # item url
                r = re.search(r'<a target="_blank" data-spm="d\d+" class=".+?" aria-label=".+?"\s+href="(\S+?)"\s*>', item_data, flags=re.S)
                if r: i_url = r.group(1).replace('&amp;','&')

                # item title, subtitle
                r = re.search(r'<h3 title="(.+?)" class="nowrap">\s+(.+?)\s+</h3>', item_data, flags=re.S)
                if r: i_subtitle, i_title = r.group(1).replace('\n',','), r.group(2).replace('\n',',')

                # item price
                r = re.search(r'<del class="orig-price">&yen;(.+?)</del>', item_data, flags=re.S)
                if r: i_price = r.group(1)

                # item promotion price
                r = re.search(r'<div class="price">\s+<i>&yen;</i>(.+?)</div>', item_data, flags=re.S)
                if r: i_promoprice = Common.htmlContent(r.group(1)).strip()

                # item discount
                r = re.search(r'<span class="benefit icon-arrow">\s+<em>(.+?)</em>折\s+</span>', item_data, flags=re.S)
                if r: i_discount = r.group(1).strip()

                # item favor
                r = re.search(r'<span class="benefit icon-by">(.+?)</span>', item_data, flags=re.S)
                if r: i_favor = r.group(1)

                # item sale num
                r = re.search(r'<span class="sold-num">\s+<em>(\d+)</em>人已买', item_data, flags=re.S)
                if r: i_salenum = r.group(1)

                print '# item:', i_url, i_price, i_promoprice, i_discount, i_favor, i_salenum, i_title, i_subtitle, i_jhstitle, i_img

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

