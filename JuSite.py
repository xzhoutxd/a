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

        # 页面
        self.site_page  = None
        # 商品团页面
        #self.today_page_url = 'http://ju.taobao.com/json/tg/ajaxGetHomeItemsV2.json?type=0&stype=soldCount&callback=homelist' # 按照销量排行
        self.today_page_url = 'http://ju.taobao.com/json/tg/ajaxGetHomeItemsV2.json?type=0&stype=soldCount' # 按照销量排行
        # 品牌团页面
        self.brand_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=0'
        #self.brand_floor_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=0'
        #http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?page=1&psize=60&btypes=1%2C2&showType=1&frontCatIds=262000&_ksTS=1421213914984_706&callback=brandList_10

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
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                s_url = self.today_page_url + '&_ksTS=%s'%ts + '&page=%d' %i
                print '# today items:', i, s_url

                s_page = self.crawler.getData(s_url, self.today_url)
                self.todayItemsByPage(s_page)

    def todayItemsByPage(self, page):
        try:
            #m = re.search(r'homelist\((.+?)\)$', page, flags=re.S)
            m = re.search(r'\"itemList\":\[.+?\]', page, flags=re.S)
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
    def brandList(self, page):
        #print page
        m = re.search(r'<div class="tb-module ju-brand-floor">(.+?)</div>\s*</div>\s*</div>\s*<div class="J_Module skin-default"', page, flags=re.S)
        if m:
            brand_floors = m.group(1)
            p = re.compile(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', flags=re.S)
            for brand_floor in p.finditer(brand_floors):
                brand_floor_info = brand_floor.group(1)
                f_name, f_catid, f_activitySignId = '', '', ''
                m = re.search(r'data-floorName="(.+?)"\s+', brand_floor_info, flags=re.S)
                if m:
                    f_name = m.group(1)

                m = re.search(r'data-catid=\'(.+?)\'\s+', brand_floor_info, flags=re.S)
                if m:
                    f_catid = m.group(1)

                m = re.search(r'data-activitySignId=\"(.+?)\"$', brand_floor_info, flags=re.S)
                if m:
                    f_activitySignId = m.group(1)
                print '# brand floor:', f_name, f_catid, f_activitySignId

                i = 1
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                if f_activitySignId != '':
                    b_url = self.brand_page_url + '&page=%d'%i + '&activitySignId=%s'%f_activitySignId.replace(',','%2C') + '&stype=ids' + '&_ksTS=%s'%ts
                    b_page = self.crawler.getData(b_url, self.brand_url)
                else:
                    b_url = self.brand_page_url + '&page=%d'%i + '&frontCatIds=%s'%f_catid + '&_ksTS=%s'%ts
                    b_page = self.crawler.getData(b_url, self.brand_url)
                try:
                    result = json.loads(b_page)
                    print b_url
                    self.brandItems(result, f_name, f_catid)
                    #if int(f_catid) == 261000:
                    #    self.brandItems(result, f_name, f_catid)

                    #if int(f_catid) == 261000 and result.has_key('totalPage') and int(result['totalPage']) > i:
                    if result.has_key('totalPage') and int(result['totalPage']) > i:
                        for page_i in range(i+1, int(result['totalPage'])+1):
                            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                            #b_url = b_url.replace('&page=\d+&','&page=%d&'%page_i)
                            #b_url = b_url.replace('&_ksTS=\d+_\d+','&_ksTS=%s'%ts)
                            b_url = re.sub('&page=\d+&', '&page=%d&'%page_i, b_url)
                            b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                            b_page = self.crawler.getData(b_url, self.brand_url)
                            result = json.loads(b_page)
                            print b_url
                            self.brandItems(result, f_name, f_catid)
                except StandardError as err:
                    print '# err:',err

    # 品牌团品牌
    def brandItems(self, page, floorName, floorCatId):
        print page
        if page.has_key('brandList') and page['brandList'] != []:
            b_position_start = 0
            if page.has_key('currentPage') and int(page['currentPage']) > 1:
                b_position_start = (int(page['currentPage']) - 1) * 60
            #for brand in page['brandList']: 
            for i in range(0,len(page['brandList'])):
                brand = page['brandList'][i]
                # 基本信息
                b_id, b_url, b_logopic_url, b_name, b_desc, b_enterpic_url, b_starttime, b_endtime, b_status, b_sellerId, b_sellerName, b_shopId, b_shopName, b_soldCount, b_remindNum, b_discount, b_hasCoupon  = '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
                # 1:普通品牌团,2:拼团,3:俪人购
                # 判断拼团、俪人购、普通品牌团
                b_sign = 1
                
                # 其他拼团Ids
                other_brandList = []

                # 品牌活动所属楼层
                b_floorName = floorName
                if not floorCatId:
                    b_floorCatId = 0
                else:
                    b_floorCatId = int(floorCatId)
                # 品牌活动所在位置
                b_position = b_position_start + i + 1

                if brand.has_key('baseInfo'):
                    b_baseInfo = brand['baseInfo']
                    if b_baseInfo.has_key('activityId') and b_baseInfo['activityId']:
                        b_id = b_baseInfo['activityId']
                    if b_baseInfo.has_key('activityUrl') and b_baseInfo['activityUrl']:
                        b_url = b_baseInfo['activityUrl']
                        if b_url.find('ladygo.tmall.com') != -1:
                            b_sign = 3
                    if b_baseInfo.has_key('ostime') and b_baseInfo['ostime']:
                        b_starttime = b_baseInfo['ostime']
                    if b_baseInfo.has_key('oetime') and b_baseInfo['oetime']:
                        b_endtime = b_baseInfo['oetime']
                    if b_baseInfo.has_key('activityStatus') and b_baseInfo['activityStatus']:
                        b_status = b_baseInfo['activityStatus']
                    if b_baseInfo.has_key('sellerId') and b_baseInfo['sellerId']:
                        b_sellerId = b_baseInfo['sellerId']
                    if b_baseInfo.has_key('otherActivityIdList') and b_baseInfo['otherActivityIdList']:
                        other_brandList = b_baseInfo['otherActivityIdList']
                        b_sign = 2
                if brand.has_key('materials'):
                    b_materials = brand['materials']
                    if b_materials.has_key('brandLogoUrl') and b_materials['brandLogoUrl']:
                        b_logopic_url = b_materials['brandLogoUrl']
                    if b_materials.has_key('logoText') and b_materials['logoText']:
                        b_name = b_materials['logoText']
                    if b_materials.has_key('brandDesc') and b_materials['brandDesc']:
                        b_desc = b_materials['brandDesc']
                    if b_materials.has_key('newBrandEnterImgUrl') and b_materials['newBrandEnterImgUrl']:
                        b_enterpic_url = b_materials['newBrandEnterImgUrl']
                    elif b_materials.has_key('brandEnterImgUrl') and b_materials['brandEnterImgUrl']:
                        b_enterpic_url = b_materials['brandEnterImgUrl']
                if brand.has_key('remind'):
                    b_remind = brand['remind']
                    if b_remind.has_key('soldCount') and b_remind['soldCount']:
                        b_soldCount = b_remind['soldCount']
                    if b_remind.has_key('remindNum') and b_remind['remindNum']:
                        b_remindNum = b_remind['remindNum']
                if brand.has_key('price'):
                    b_price = brand['price']
                    if b_price.has_key('discount') and b_price['discount']:
                        b_discount = b_price['discount']
                    if b_price.has_key('hasCoupon'):
                        if b_price['hasCoupon']:
                          b_hasCoupon = 1
                        else:
                          b_hasCoupon = 0

                print 'b_id, b_url, b_logopic_url, b_name, b_desc, b_enterpic_url, b_starttime, b_endtime, b_status, b_sellerId, b_sellerName, b_shopId, b_shopName, b_soldCount, b_remindNum, b_discount, b_hasCoupon, b_sign, other_brandList,b_position,b_floorName,b_floorCatId'
                print '# brand:', b_id, b_url, b_logopic_url, b_name, b_desc, b_enterpic_url, b_starttime, b_endtime, b_status, b_sellerId, b_sellerName, b_shopId, b_shopName, b_soldCount, b_remindNum, b_discount, b_hasCoupon, b_sign, other_brandList, b_position, b_floorName, b_floorCatId
                
    # 品牌团商品
    def brandItemsByPage(self, page):
        pass

    # 聚划算商品页
    def itemByPage(self, page):
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
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    j.brandChannel()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#    j.todayChannel()
#     j.lifeChannel()
#    j.lifeCity()

