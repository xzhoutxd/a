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
import Common
from TBCrawler import TBCrawler
from TBItem import TBItem
from TMItem import TMItem
from parserTBItem import PTBItem
from parserTMItem import PTMItem

coupon_get_num = 0

class BrandPageThread(threading.Thread):
    '''Brand page'''
    def __init__(self, bPage_list):
        threading.Thread.__init__(self)
        self.bPage_list = bPage_list
        # 抓取设置
        self.crawler = TBCrawler()
        self.brand_url  = 'http://ju.taobao.com/tg/brand.htm'         # 品牌团

    # 品牌团商品
    def run(self):
        global coupon_get_num
        print '# activityPage start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        for activitypage in self.bPage_list:
            bItems_page = self.crawler.getData(activitypage[0], self.activity_url)

            page = bItems_page
            a = activitypage[1]
            b = activitypage[2]
            # 优惠券
            coupon_list = []
            p = re.compile(r'<div class=".+?">\s*<div class="c-price">\s*<i>.+?</i><em>(.+?)</em></div>\s*<div class="c-desc">\s*<span class="c-title"><em>(.+?)</em>(.+?)</span>\s*<span class="c-require">(.+?)</span>\s*</div>', flags=re.S)
            for coupon in p.finditer(page):
                coupon_list.append(''.join(coupon.groups()))
            if coupon_list != []:
                coupon_get_num += 1
                print '# coupons%d (%d):%s'%(a,int(b),' '.join(coupon_list))
            #else:
            #    if a==1:
            #        print '# coupons%d (%d)'%(a,int(b))
        print '# coupon_get_num:',coupon_get_num
        print '# activityPage end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        

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
        self.brand_find = 0
        self.brand_get = 0
        self.brand_coupon_find = 0
        self.brand_coupon_get = 0
        self.bPage_list = []
        #self.brand_floor_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=0'
        # 即将上架
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
                    b_page = self.crawler.getData(b_url, self.brand_url)
                else:
                    b_url = self.brand_page_url + '&page=%d'%i + '&frontCatIds=%s'%f_catid + '&_ksTS=%s'%ts
                    b_page = self.crawler.getData(b_url, self.brand_url)
                try:
                    result = json.loads(b_page)
                    print b_url
                    bResult_list.append([result,f_name,f_catid])
                    # 只取女装
                    #if int(f_catid) == 261000:
                    #    bResult_list.append([result,f_name,f_catid])
                    #self.activityItems(result, f_name, f_catid)
                    #if int(f_catid) == 261000:
                    #    self.activityItems(result, f_name, f_catid)

                    #if f_catid != '' and int(f_catid) == 261000 and result.has_key('totalPage') and int(result['totalPage']) > i:
                    if result.has_key('totalPage') and int(result['totalPage']) > i:
                        for page_i in range(i+1, int(result['totalPage'])+1):
                            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                            b_url = re.sub('&page=\d+&', '&page=%d&'%page_i, b_url)
                            b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                            b_page = self.crawler.getData(b_url, self.brand_url)
                            result = json.loads(b_page)
                            print b_url
                            bResult_list.append([result, f_name, f_catid])
                            #self.activityItems(result, f_name, f_catid)
                except StandardError as err:
                    print '# err:',err
        print '# activityItems start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        for bResult in bResult_list:
            self.activityItems(bResult[0], bResult[1], bResult[2])
        print '# activityItems end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        #for activitypage in self.bPage_list:
        #    bItems_page = self.crawler.getData(activitypage[0], self.activity_url)
        #    self.activityItemsByPage(bItems_page, activitypage[1], activitypage[2])

    # 品牌团品牌
    def activityItems(self, page, floorName, floorCatId):
        #print page
        bPage_list = []
        if page.has_key('brandList') and page['brandList'] != []:
            self.brand_find += len(page['brandList'])
            b_position_start = 0
            if page.has_key('currentPage') and int(page['currentPage']) > 1:
                b_position_start = (int(page['currentPage']) - 1) * 60
            #for activity in page['brandList']: 
            for i in range(0,len(page['brandList'])):
                activity = page['brandList'][i]
                # 1:普通品牌团,2:拼团,3:俪人购
                # 判断拼团、俪人购、普通品牌团
                b_sign = 1
                
                # 其他拼团Ids
                other_activityList = []

                # 品牌活动所属楼层
                b_floorName = floorName
                if not floorCatId:
                    b_floorCatId = 0
                else:
                    b_floorCatId = int(floorCatId)
                # 品牌活动所在位置
                b_position = b_position_start + i + 1

                # 基本信息
                b_id, b_url, b_logopic_url, b_name, b_desc, b_enterpic_url, b_starttime, b_endtime, b_status, b_sellerId, b_sellerName, b_shopId, b_shopName, b_soldCount, b_remindNum, b_discount, b_hasCoupon  = '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
                # b_id, b_url, b_sign,  b_starttime, b_endtime, b_status, b_sellerId, other_activityList
                if activity.has_key('baseInfo'):
                    b_baseInfo = activity['baseInfo']
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
                        other_activityList = b_baseInfo['otherActivityIdList']
                        b_sign = 2
                # b_logopic_url, b_name, b_desc, b_enterpic_url
                if activity.has_key('materials'):
                    b_materials = activity['materials']
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
                # b_soldCount, b_remindNum
                if activity.has_key('remind'):
                    b_remind = activity['remind']
                    if b_remind.has_key('soldCount') and b_remind['soldCount']:
                        b_soldCount = b_remind['soldCount']
                    if b_remind.has_key('remindNum') and b_remind['remindNum']:
                        b_remindNum = b_remind['remindNum']
                # b_discount, b_hasCoupon
                if activity.has_key('price'):
                    b_price = activity['price']
                    if b_price.has_key('discount') and b_price['discount']:
                        b_discount = b_price['discount']
                    if b_price.has_key('hasCoupon'):
                        if b_price['hasCoupon']:
                          b_hasCoupon = 1
                          self.brand_coupon_find += 1
                        else:
                          b_hasCoupon = 0

                print 'b_id, b_url, b_logopic_url, b_name, b_desc, b_enterpic_url, b_starttime, b_endtime, b_status, b_sellerId, b_sellerName, b_shopId, b_shopName, b_soldCount, b_remindNum, b_discount, b_hasCoupon, b_sign, other_activityList,b_position,b_floorName,b_floorCatId'
                print '# activity:%d'%b_position, b_id, b_url, b_logopic_url, b_name, b_desc, b_enterpic_url, b_starttime, b_endtime, b_status, b_sellerId, b_sellerName, b_shopId, b_shopName, b_soldCount, b_remindNum, b_discount, b_hasCoupon, b_sign, other_activityList, b_position, b_floorName, b_floorCatId
                self.brand_get += 1

                bPage_list.append([b_url, b_id, b_sign])
                # 只测试第一个活动
                if b_position == 1:
                    bItems_page = self.crawler.getData(b_url, self.brand_url)
                    self.activityItemsByPage(bItems_page, b_id, b_url)

        # 多线程
        #page_threading = BrandPageThread(bPage_list)
        #page_threading.start()
        # 单线程
        #print '# activityPage start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #for activitypage in bPage_list:
        #    if activitypage[2] != 3:
        #        bItems_page = self.crawler.getData(activitypage[0], self.brand_url)
        #        self.activityItemsByPage(bItems_page, activitypage[1], activitypage[0])
        #print '# activityPage end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
              
    # 品牌团商品
    def activityItemsByPage(self, page, act_id, refer):
        m = re.search(r'<div id="content">(.+?)</div>\s+<div class="crazy-wrap">', page, flags=re.S)
        if m:
            page = m.group(1)

        # 优惠券
        coupon_list = []
        p = re.compile(r'<div class=".+?">\s*<div class="c-price">\s*<i>.+?</i><em>(.+?)</em></div>\s*<div class="c-desc">\s*<span class="c-title"><em>(.+?)</em>(.+?)</span>\s*<span class="c-require">(.+?)</span>\s*</div>', flags=re.S)
        for coupon in p.finditer(page):
            coupon_list.append(''.join(coupon.groups()))
        if coupon_list != []:
            self.brand_coupon_get += 1
            print '# coupons (%d):%s'%(int(act_id),' '.join(coupon_list))

        # 商品
        position = 0
        m = re.search(r'<div class="act-main ju-itemlist">', page, flags=re.S)
        if m:
            # source html floor
            p = re.compile(r'<div class="act-item0">(.+?)</div>\s+<img', flags=re.S)
            position += self.itemByBrandPage(page, act_id, p, position, refer)
            m = re.search(r'<div class="act-item1">\s+<ul>(.+?)</u>\s+</div>', page, flags=re.S)
            if m:
                item1_page = m.group(1)
                p = re.compile(r'<li>(.+?)</li>', flags=re.S)
                position += self.itemByBrandPage(item1_page, act_id, p, position, refer)

            # other floor
            getdata_url = "http://ju.taobao.com/json/tg/ajaxGetItems.htm?stype=ids&styleType=small&includeForecast=true"
            p = re.compile(r'<div class="act-item J_jupicker" data-item="(.+?)">', flags=re.S)
            for floor_url in p.finditer(page):
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                f_url = getdata_url + '&juIds=' + floor_url.group(1) + '&_ksTS=%s'%ts
                print f_url
                f_page = self.crawler.getData(f_url, refer)
                m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
                if m:
                    f_html = m.group(1)
                    p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
                    position += self.itemByBrandPage(f_html, act_id, p, position, f_url)
            
        else:
            # source html floor
            p = re.compile(r'<li class="item-big-v2">(.+?)</li>', flags=re.S)
            position += self.itemByBrandPage(page, act_id, p, position, refer)

            # other floor
            p = re.compile(r'<div class="l-floor J_Floor J_ItemList" .+? data-url="(.+?)">', flags=re.S)
            for floor_url in p.finditer(page):
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                f_url = floor_url.group(1) + '&_ksTS=%s'%ts
                print f_url
                f_page = self.crawler.getData(f_url, refer)
                m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
                if m:
                    f_html = m.group(1)
                    p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
                    position += self.itemByBrandPage(f_html, act_id, p, position, f_url)

    # 品牌团页面商品
    def itemByBrandPage(self, page, act_id, first_p, start, refer):
        # 商品信息
        #p = re.compile(r'<li class="item-big-v2">(.+?)</a>\s+</li>', flags=re.S)
        i = 0
        for ju_item in first_p.finditer(page):
            i += 1
            ju_item_html = ju_item.group(1)

            # i_actId
            i_actId = act_id

            # i_position
            i_position = start + i

            # 基本信息
            i_juId, i_id, i_ju_url, i_juPic_url, i_juName, i_juDesc, i_oriPrice, i_actPrice = '', '', '', '', '', '', '', ''
            # i_ju_url, i_juId, i_id
            m = re.search(r'<a.+?href="(.+?)".+?>', ju_item_html, flags=re.S)
            if m:
                i_ju_url = m.group(1)
                if i_ju_url:
                    ids_list = i_ju_url.split('&')
                    for ids in ids_list:
                        if ids.find('item_id=') != -1:
                            i_id = ids.split('=')[1]
                        elif ids.find('id=') != -1:
                            i_juId = ids.split('=')[1]

            # i_juPic_url
            m = re.search(r'<img class="item-pic" data-ks-lazyload="(.+?)"', ju_item_html, flags=re.S)
            if m:
                i_juPic_url = m.group(1)
            else:
                m = re.search(r'<img data-ks-lazyload="(.+?)"', ju_item_html, flags=re.S)
                if m:
                    i_juPic_url = m.group(1)

            """
            # i_juName
            m = re.search(r'<h3 class="shortname" title="(.+?)">.+?</h3>', ju_item_html, flags=re.S)
            if m:
                i_juName = m.group(1)
            else:
                m = re.search(r'<a .+?>.+?<h3.+?title="(.+?)">.+?</h3>.+?</a>', ju_item_html, flags=re.S)
                if m:
                    i_juName = m.group(1)

            # i_juDesc
            m = re.search(r'<h4 class="longname">(.+?)</h4>', ju_item_html, flags=re.S)
            if m:
                i_juDesc = m.group(1).strip()

            # i_actPrice
            m = re.search(r'<span class="actPrice">.+?<em>(.+?)</em>\s+</span>', ju_item_html, flags=re.S)
            if m:
                i_actPrice = m.group(1).strip()
            else:
                m = re.search(r'<em class="J_actPrice">(.+?)</em>', ju_item_html, flags=re.S)
                if m:
                    i_actPrice = m.group(1).strip()

            # i_oriPrice
            m = re.search(r'<del class="oriPrice">(.+?)</del>', ju_item_html, flags=re.S)
            if m:
                i_oriPrice = m.group(1).strip()
                if i_oriPrice.find(';') != -1:
                    i_oriPrice = i_oriPrice.split(';')[1]
            else:
                m = re.search(r'<del class="orig-price">(.+?)</del>', ju_item_html, flags=re.S)
                if m:
                    i_oriPrice = m.group(1).strip()
                    if i_oriPrice.find(';') != -1:
                        i_oriPrice = i_oriPrice.split(';')[1]
            """
            
            print 'i_actId, i_position, i_juId, i_id, i_ju_url, i_juPic_url, i_juName, i_juDesc, i_oriPrice, i_actPrice'
            print '# activityItem%d:'%i_position, i_actId, i_position, i_juId, i_id, i_ju_url, i_juPic_url, i_juName, i_juDesc, i_oriPrice, i_actPrice

            ## 只测第一个商品
            if i_position == 1:
                self.itemByPage(i_ju_url, refer)
            #self.itemByPage(i_ju_url, refer)
                
        return i

    # 聚划算商品页
    def itemByPage(self, url, refer):
        # i_id, i_juId, i_url, i_juName, i_juDesc, i_oriPrice, i_actPrice, i_sellerName, i_shopId, i_shopName, i_treeId, i_discount, i_prepare, i_remindNum, i_soldCount, i_stock, i_favorites
        # 聚划算商品页信息
        # i_id, i_juId, i_url, i_juName, i_juDesc, i_oriPrice, i_actPrice, i_discount, i_sellerId, i_sellerName, i_remindNum, i_soldCount, i_stock, i_shopType
        i_id, i_juId, i_url, i_juName, i_juDesc, i_oriPrice, i_actPrice, i_discount, i_sellerId, i_sellerName, i_remindNum, i_soldCount, i_stock, i_shopType = '', '', '', '', '', '', '', '', '', '', '', '', '', ''
        page = self.crawler.getData(url, refer)
        m = re.search(r'<div id="content" class="detail">(.+?)</div> <!-- /content -->', page, flags=re.S)
        if m:
            i_page = m.group(1)
            # i_id, i_juId, i_shopType
            m = re.search(r'JU_DETAIL_DYNAMIC = {(.+?)};', i_page, flags=re.S)
            if m:
                m = re.search(r'"item_id": "(.+?)",.+?"id": "(.+?)",.+?"shopType": (.+?)\s+', i_page, flags=re.S)
                if m:
                    i_id, i_juId, i_shopType = m.group(1), m.group(2), m.group(3)

            # i_url
            m = re.search(r'<div class="normal-pic.+?<a href="(.+?)".+?>', i_page, flags=re.S)
            if m:
                i_url = m.group(1)

            # i_sellerId, i_sellerName
            m = re.search(r'<div class="con inf-seller">\s+<a href=".+?user_number_id=(.+?)".+?>(.+?)</a>\s+</div>', i_page, flags=re.S)
            if m:
                i_sellerId, i_sellerName = m.group(1), m.group(2)

            # i_juName
            m = re.search(r'<h2 class="name">(.+?)</h2>', i_page, flags=re.S)
            if m:
                i_juName = m.group(1).strip()

            # i_juDesc
            m = re.search(r'<div class="description">(.+?)</div>', i_page, flags=re.S)
            if m:
                i_juDesc = m.group(1).strip()

            # i_oriPrice
            m = re.search(r'<del class="originPrice">(.+?)</del>', i_page, flags=re.S)
            if m:
                i_oriPrice = m.group(1).strip()
                if i_oriPrice.find(';') != -1:
                    i_oriPrice = i_oriPrice.split(';')[1]

            # i_actPrice
            m = re.search(r'<span class="currentPrice.+?>.+?</small>(.+?)</span>', i_page, flags=re.S)
            if m:
                i_actPrice = m.group(1).strip()

            # i_discount
            m = re.search(r'data-polldiscount="(.+?)"', i_page, flags=re.S)
            if m:
                i_discount = m.group(1)

            # i_remindNum, i_soldCount, i_stock
            i_getdata_url = ''
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            m = re.search(r'JU_DETAIL_DYNAMIC = {.+?"apiItemDynamicInfo": "(.+?)",.+?};', i_page, flags=re.S)
            if m:
                i_getdata_url = m.group(1) + '?item_id=%s'%i_id + '&id=%s'%i_juId + '&_ksTS=%s'%ts
            else:
                i_getdata_url = 'http://dskip.ju.taobao.com/detail/json/item_dynamic.htm' + '?item_id=%s'%i_id + '&id=%s'%i_juId + '&_ksTS=%s'%ts

            if i_getdata_url:
                data_json = self.crawler.getData(i_getdata_url, url)
                result = json.loads(data_json)
                if result.has_key('data'):
                    result_data = result['data']
                    if result_data.has_key('soldCount'):
                        i_soldCount = result_data['soldCount']
                    else:
                        if result_data.has_key('remindNum') and result_data['remindNum']:
                            i_remindNum = result_data['remindNum']

                    if result_data.has_key('stock'):
                        i_stock = result_data['stock']
          
            print 'i_id, i_juId, i_url, i_juName, i_juDesc, i_oriPrice, i_actPrice, i_discount, i_sellerId, i_sellerName, i_remindNum, i_soldCount, i_stock, i_shopType'
            print '# Item:', i_id, i_juId, i_url, i_juName, i_juDesc, i_oriPrice, i_actPrice, i_discount, i_sellerId, i_sellerName, i_remindNum, i_soldCount, i_stock, i_shopType 
                

        # 商品详情页信息
        # i_shopId, i_shopName, i_treeId, i_prepare, i_favorites, i_brand
        i_shopId, i_shopName, i_treeId, i_prepare, i_favorites, i_brand = '', '', '', '', '', ''
        result = None
        if int(i_shopType) == 1:
            T = TMItem()
            T.antPage(i_url)
            PT = PTMItem()
            PT.antPage(T)
            result = PT.outItemCrawl()
            
        elif int(i_shopType) == 2:
            T = TBItem()
            T.antPage(i_url)
            PT = PTBItem()
            result = PT.outItemCrawl()
        print result
        if result:
            i_shopId, i_shopName, i_treeId, i_prepare, i_favorites, i_brand = result
        print 'i_shopId, i_shopName, i_treeId, i_prepare, i_favorites, i_brand'
        print '# ItemshopInfo:', i_shopId, i_shopName, i_treeId, i_prepare, i_favorites, i_brand

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
    print '# Get Result: brand_find brand_get'
    print '# ', j.brand_find, j.brand_get

    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
#    j.todayChannel()
#     j.lifeChannel()
#    j.lifeCity()

