#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler
from JHSBrandComing import JHSBrandComing

class JHSMainComing():
    '''A class of Juhuasuan Main Site'''
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
        if not page or page == '': return

    # 品牌团频道
    def brandChannel(self):
        # 即将上线品牌团
        brand_obj = JHSBrandComing()
        brand_obj.antPage()

    # 生活汇频道
    def lifeChannel(self):
        page = self.crawler.getData(self.life_url, self.refers)
        if not page or page == '': return

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
    j = JHSMainComing()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    j.brandChannel()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
