#-*- coding:utf-8 -*-
#!/usr/bin/env python
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

class JHSBActItem():
    '''A class of brand Item'''
    def __init__(self):
        # 品牌团抓取设置
        self.crawler    = TBCrawler()
        self.crawling_time   = Common.now() # 当前爬取时间
        self.crawling_beginDate = '' # 本次爬取日期
        self.crawling_beginHour = '' # 本次爬取小时
        self.crawling_confirm = 1 # 本活动是否需要爬取 1:是 2:否
        self.beginH_gap = 1 # 定义新品牌团时间段(小时)

        # 类别
        self.brandact_platform = '聚划算-pc' # 品牌团所在平台
        self.brandact_channel = '品牌闪购' # 品牌团所在频道
        self.brandact_catgoryId = 0 # 品牌团所在类别Id
        self.brandact_catgoryName = '' # 品牌团所在类别Name
        self.brandact_position = 0 # 品牌团所在类别位置

        # 是否在首页展示
        self.home_brands = {} # 首页品牌团信息
        self.brandact_inJuHome = 0 # 是否在首页展示,0:不在,1:存在
        self.brandact_juHome_position = '' # 在首页展示的位置

        # 品牌团信息
        self.brandact_id = '' # 品牌团Id
        self.brandact_url = '' # 品牌团链接
        self.brandact_name = '' # 品牌团Name
        self.brandact_desc = '' # 品牌团描述
        self.brandact_logopic_url = '' # 品牌团Logo图片链接
        self.brandact_enterpic_url = '' # 品牌团展示图片链接
        self.brandact_starttime = 0.0 # 品牌团开团时间
        self.brandact_startdate = '' # 品牌团开团日期
        self.brandact_endtime = 0.0 # 品牌团结束时间
        self.brandact_status = '' # 品牌团状态
        self.brandact_sign = 1 # 品牌团标识 1:普通品牌团,2:拼团,3:俪人购
        self.brandact_other_ids = '' # 如果是拼团, 其他团的ID
        self.brandact_brand = '' # 品牌团品牌信息
        self.brandact_brandId = '' # 品牌团品牌Id

        # 店铺信息
        self.brandact_sellerId = '' # 品牌团卖家Id
        self.brandact_sellerName = '' # 品牌团卖家Name (回填)
        self.brandact_shopId = '' # 品牌团店铺Id (回填)
        self.brandact_shopName = '' # 品牌团店铺Name (回填)

        # 品牌团交易信息
        self.brandact_soldCount = 0 # 品牌团成交数
        self.brandact_remindNum = 0 # 品牌团关注人数
        self.brandact_discount = '' # 品牌团打折
        self.brandact_coupon = 0 # 品牌团优惠券, 默认0没有
        self.brandact_coupons = [] # 优惠券内容list

        # 品牌团商品
        self.brandact_itemVal_list = []

        # 原数据信息
        self.brandact_pagedata = '' # 品牌团所在数据项所有内容
        self.brandact_page = '' # 品牌团页面html内容
        self.brandact_pages = {} # 品牌页面内请求数据列表

    # 品牌团初始化
    def initItem(self, page, catId, catName, position, begin_date, begin_hour, home_brands):
        # 品牌团所在数据项内容
        self.brandact_pagedata = page
        self.brandact_pages['act-init'] = ('', page)
        # 品牌团所在类别Id
        self.brandact_catgoryId = catId
        # 品牌团所在类别Name
        self.brandact_catgoryName = catName
        # 品牌团所在类别位置
        self.brandact_position = position
        # 本次抓取开始日期
        self.crawling_beginDate = begin_date
        # 本次抓取开始小时
        self.crawling_beginHour = begin_hour
        # 首页品牌团信息
        self.home_brands = home_brands

    # 品牌团初始化
    def initItemComing(self, page, catId, catName, position, begin_date, begin_hour):
        # 品牌团所在数据项内容
        self.brandact_pagedata = page
        self.brandact_pages['act-init'] = ('', page)
        # 品牌团所在类别Id
        self.brandact_catgoryId = catId
        # 品牌团所在类别Name
        self.brandact_catgoryName = catName
        # 品牌团所在类别位置
        self.brandact_position = position
        # 本次抓取开始日期
        self.crawling_beginDate = begin_date
        # 本次抓取开始小时
        self.crawling_beginHour = begin_hour

    # Configuration
    def itemConfig(self):
        # 基本信息
        if self.brandact_pagedata.has_key('baseInfo'):
            b_baseInfo = self.brandact_pagedata['baseInfo']
            if b_baseInfo.has_key('activityId') and b_baseInfo['activityId']:
                # 品牌团Id
                self.brandact_id = b_baseInfo['activityId']
            if b_baseInfo.has_key('activityUrl') and b_baseInfo['activityUrl']:
                # 品牌团链接
                self.brandact_url = b_baseInfo['activityUrl']
                if self.brandact_url.find('ladygo.tmall.com') != -1:
                    # 品牌团标识
                    self.brandact_sign = 3
            if b_baseInfo.has_key('ostime') and b_baseInfo['ostime']:
                # 品牌团开团时间
                self.brandact_starttime = b_baseInfo['ostime']
                self.brandact_startdate = Common.add_hours_D(int(float(self.brandact_starttime)/1000), 1)
            if b_baseInfo.has_key('oetime') and b_baseInfo['oetime']:
                # 品牌团结束时间
                self.brandact_endtime = b_baseInfo['oetime']
            if b_baseInfo.has_key('activityStatus') and b_baseInfo['activityStatus']:
                # 品牌团状态
                self.brandact_status = b_baseInfo['activityStatus']
            if b_baseInfo.has_key('sellerId') and b_baseInfo['sellerId']:
                # 品牌团卖家Id
                self.brandact_sellerId = b_baseInfo['sellerId']
            if b_baseInfo.has_key('otherActivityIdList') and b_baseInfo['otherActivityIdList']:
                # 如果是拼团, 其他团的ID
                self.brandact_other_ids = str(self.brandact_id) + ',' + ','.join(b_baseInfo['otherActivityIdList'])
                # 品牌团标识
                self.brandact_sign = 2
            else:
                self.brandact_other_ids = str(self.brandact_id)
            
            if b_baseInfo.has_key('brandId') and b_baseInfo['brandId']:
                # 品牌团Id
                self.brandact_brandId = b_baseInfo['brandId']

        if self.brandact_pagedata.has_key('materials'):
            b_materials = self.brandact_pagedata['materials']
            if b_materials.has_key('brandLogoUrl') and b_materials['brandLogoUrl']:
                # 品牌团Logo图片链接
                self.brandact_logopic_url = b_materials['brandLogoUrl']
            if b_materials.has_key('logoText') and b_materials['logoText']:
                # 品牌团Name
                self.brandact_name = b_materials['logoText']
            if b_materials.has_key('brandDesc') and b_materials['brandDesc']:
                # 品牌团描述
                self.brandact_desc = b_materials['brandDesc']
            if b_materials.has_key('newBrandEnterImgUrl') and b_materials['newBrandEnterImgUrl']:
                # 品牌团展示图片链接
                self.brandact_enterpic_url = b_materials['newBrandEnterImgUrl']
            elif b_materials.has_key('brandEnterImgUrl') and b_materials['brandEnterImgUrl']:
                # 品牌团展示图片链接
                self.brandact_enterpic_url = b_materials['brandEnterImgUrl']

        if self.brandact_pagedata.has_key('remind'):
            b_remind = self.brandact_pagedata['remind']
            if b_remind.has_key('soldCount') and b_remind['soldCount']:
                # 品牌团成交数
                self.brandact_soldCount = b_remind['soldCount']
            if b_remind.has_key('remindNum') and b_remind['remindNum']:
                # 品牌团想买人数
                self.brandact_remindNum = b_remind['remindNum']

        if self.brandact_pagedata.has_key('price'):
            b_price = self.brandact_pagedata['price']
            if b_price.has_key('discount') and b_price['discount']:
                # 品牌团打折
                self.brandact_discount = b_price['discount']
            if b_price.has_key('hasCoupon'):
                if b_price['hasCoupon']:
                  # 品牌团优惠券 有优惠券
                  self.brandact_coupon = 1

        # 判断是否在首页推广
        if self.brandact_id != '' and self.brandact_url != '':
            key1, key2 = str(self.brandact_id), self.brandact_url.split('?')[0]
            if self.home_brands.has_key(key1):
                self.brandact_inJuHome = 1
                self.brandact_juHome_position = self.home_brands[key1]['position']
            elif self.home_brands.has_key(key2):
                self.brandact_inJuHome = 1
                self.brandact_juHome_position = self.home_brands[key2]['position']
        
        # 品牌团页面html
        if self.brandact_url != '':
            data = self.crawler.getData(self.brandact_url, Config.ju_brand_home)
            if not data and data == '': raise Common.InvalidPageException("# itemConfig:not find act page,actid:%s,act_url:%s"%(str(self.brandact_id), self.brandact_url))
            if data and data != '':
                self.brandact_page = data
                self.brandact_pages['act-home'] = (self.brandact_url, data)

    # 品牌团优惠券
    def brandActConpons(self):
        # 优惠券
        """
        #m = re.search(r'<div id="content">(.+?)</div>\s+<div class="crazy-wrap">', self.brandact_page, flags=re.S)
        #if m:
        #    page = m.group(1)
        #    p = re.compile(r'<div class=".+?">\s*<div class="c-price">\s*<i>.+?</i><em>(.+?)</em></div>\s*<div class="c-desc">\s*<span class="c-title"><em>(.+?)</em>(.+?)</span>\s*<span class="c-require">(.+?)</span>\s*</div>', flags=re.S)
        #    for coupon in p.finditer(page):
        #        self.brandact_coupons.append(''.join(coupon.groups()))
        """
        p = re.compile(r'<div class=".+?J_coupons">\s*<div class="c-price">(.+?)</div>\s*<div class="c-desc">\s*<span class="c-title">(.+?)</span>\s*<span class="c-require">(.+?)</span>\s*</div>', flags=re.S)
        for coupon in p.finditer(self.brandact_page):
            price, title, require = coupon.group(1).strip(), coupon.group(2).strip(), coupon.group(3).strip()
            i_coupons = ''
            m = re.search(r'<em>(.+?)</em>', price, flags=re.S)
            if m:
                i_coupons = i_coupons + m.group(1)
            else:
                i_coupons = i_coupons + ''.join(price.spilt())

            m = re.search(r'<em>(.+?)</em>(.+?)$', title, flags=re.S)
            if m:
                i_coupons = i_coupons + ''.join(m.groups())
            else:
                i_coupons = i_coupons + ''.join(title.split())

            i_coupons = i_coupons + require

            self.brandact_coupons.append(i_coupons)

    # 从品牌团页获取商品数据
    def brandActItems(self):
        #page = self.crawler.getData(self.brandact_url, Config.ju_brand_home)
        page = self.brandact_page
        m = re.search(r'<div id="content".+?>(.+?)</div>\s+<div class="crazy-wrap">', page, flags=re.S)
        if m:
            page = m.group(1)

        m = re.search(r'<div class="ju-itemlist">\s+<ul class="clearfix">.+?<li class="item-.+?">.+?</li>.+?</ul>\s+</div>', page, flags=re.S)
        if m:
            self.brandActType1(page)
        else:
            m = re.search(r'<div class="act-main ju-itemlist">', page, flags=re.S)
            if m:
                self.brandActType2(page)
            else:
                m = re.search(r'<div class="ju-itemlist J_JuHomeList">\s+<ul.+?>(.+?)</ul>', page, flags=re.S)
                if m:
                    self.brandActType3(m.group(1))
                else:
                    m = re.search(r'<div class="l-floor J_Floor .+?data-ajaxurl="(.+?)">', page, flags=re.S)
                    if m:
                        self.brandActType4(page)
                    else:
                        self.brandActTypeOther(page)

    # 品牌团页面格式(1)
    def brandActType1(self, page):
        position = 0
        # source html floor
        # 第一层
        p = re.compile(r'<li class="item-.+?">(.+?)</li>', flags=re.S)
        i = 0
        for itemdata in p.finditer(page):
            position += 1
            val = self.itemByBrandPageType1(itemdata.group(1), position)
            self.brandact_itemVal_list.append(val)

        # other floor
        # 其他层数据
        p = re.compile(r'<div class="l-floor J_Floor J_ItemList" .+? data-url="(.+?)">', flags=re.S)
        for floor_url in p.finditer(page):
            f_url = (floor_url.group(1)).replace('&amp;','&')
            print f_url
            self.getItemDataFromInterface(f_url, position)

    # 品牌团页面格式(2)
    def brandActType2(self, page):
        position = 0
        # source html floor
        # 第一层
        p = re.compile(r'<div class="act-item0">(.+?)</div>\s+<img', flags=re.S)
        for itemdata in p.finditer(page):
            position += 1
            val = self.itemByBrandPageType1(itemdata.group(1), position)
            self.brandact_itemVal_list.append(val)
        # 第二层
        m = re.search(r'<div class="act-item1">\s+<ul>(.+?)</u>\s+</div>', page, flags=re.S)
        if m:
            item1_page = m.group(1)
            p = re.compile(r'<li>(.+?)</li>', flags=re.S)
            for itemdata in p.finditer(item1_page):
                position += 1
                val = self.itemByBrandPageType1(itemdata.group(1), position)
                self.brandact_itemVal_list.append(val)

        # other floor
        # 接口数据
        getdata_url = "http://ju.taobao.com/json/tg/ajaxGetItems.htm?stype=ids&styleType=small&includeForecast=true"
        p = re.compile(r'<div class=".+?J_jupicker" data-item="(.+?)">', flags=re.S)
        for floor_url in p.finditer(page):
            f_url = getdata_url + '&juIds=' + floor_url.group(1)
            self.getItemDataFromInterface(f_url, position)


    # 品牌团页面格式(3)
    def brandActType3(self, page):
        position = 0
        p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
        for itemdata in p.finditer(page):
            position += 1
            val = self.itemByBrandPageType1(itemdata.group(1), position)
            self.brandact_itemVal_list.append(val)

    # 品牌团页面格式(4)
    def brandActType4(self, page):
        position = 0
        # 请求接口数据
        p = re.compile(r'<div class="l-floor J_Floor .+? data-ajaxurl="(.+?)"', flags=re.S)
        for floor_url in p.finditer(page):
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            f_url = (floor_url.group(1)).replace('&amp;','&') + '&_ksTS=%s'%ts
            print f_url
            f_page = self.crawler.getData(f_url, self.brandact_url)
            m = re.search(r'^{.+?\"itemList\":\[.+?\].+?}$', f_page, flags=re.S)
            if m:
                result = json.loads(f_page)
                if result.has_key('code') and int(result['code']) == 200 and result.has_key('itemList') and result['itemList'] != []:
                    for itemdata in result['itemList']:
                        position += 1
                        val = self.itemByBrandPageType2(itemdata, position)
                        self.brandact_itemVal_list.append(val)

    # 品牌团页面格式
    def brandActTypeOther(self, page):
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
                    val = (item_ju_url, self.brandact_id, self.brandact_name, self.brandact_url, position, item_ju_url, item_id, item_juId, '')
                    self.brandact_itemVal_list.append(val)
                    items[key] = {'itemid':item_id,'itemjuid':item_juId}
        
        # other floor
        # 接口数据
        getdata_url = "http://ju.taobao.com/json/tg/ajaxGetItems.htm?stype=ids&styleType=small&includeForecast=true"
        p = re.compile(r'<div class=".+?J_jupicker" data-item="(.+?)">', flags=re.S)
        for floor_url in p.finditer(page):
            f_url = getdata_url + '&juIds=' + floor_url.group(1)
            self.getItemDataFromInterface(f_url, position)

    # 从接口获取商品数据列表
    def getItemDataFromInterface(self, url, position):
        ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
        f_url = url + '&_ksTS=%s'%ts
        #print f_url
        f_page = self.crawler.getData(f_url, self.brandact_url)
        m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
        if m:
            f_html = m.group(1)
            p = re.compile(r'<li class="item-small-v3">.+?(<a.+?</a>).+?</li>', flags=re.S)
            for itemdata in p.finditer(f_html):
                position += 1
                val = self.itemByBrandPageType1(itemdata.group(1), position)
                self.brandact_itemVal_list.append(val)

    # 获取商品信息类型1
    def itemByBrandPageType1(self, itemdata, position):
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

        # 商品聚划算展示图片链接
        item_juPic_url = ''
        m = re.search(r'<img class="item-pic" data-ks-lazyload="(.+?)"', itemdata, flags=re.S)
        if m:
            item_juPic_url = m.group(1)
        else:
            m = re.search(r'<img data-ks-lazyload="(.+?)"', itemdata, flags=re.S)
            if m:
                item_juPic_url = m.group(1)

        # 解析聚划算商品
        return (itemdata, self.brandact_id, self.brandact_name, self.brandact_url, position, item_ju_url, item_id, item_juId, item_juPic_url)

    # 获取商品信息类型2
    def itemByBrandPageType2(self, itemdata, position):
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
        return (itemdata, self.brandact_id, self.brandact_name, self.brandact_url, position, item_ju_url, item_id, item_juId, item_juPic_url)

    # 执行
    #def antPageOld(self, page, catId, catName, position, begin_date, begin_hour):
    def antPageOld(self, val):
        page, catId, catName, position, begin_date, begin_hour, home_brands = val
        self.initItem(page, catId, catName, position, begin_date, begin_hour, home_brands)
        self.itemConfig()
        self.brandActConpons()
        # 不抓俪人购的商品
        if self.brandact_sign != 3:
            self.brandActItems()
        #self.outItem()

    # 品牌团信息和其中商品基本信息
    def antPage(self, val):
        page, catId, catName, position, begin_date, begin_hour, home_brands = val
        self.initItem(page, catId, catName, position, begin_date, begin_hour, home_brands)
        self.itemConfig()
        # 只爬一段时间内要开团的活动
        time_gap = Common.subTS_hours(int(float(self.brandact_starttime)/1000), self.crawling_time)
        if self.beginH_gap > time_gap and 0 <= time_gap:
            self.brandActConpons()
            # 不抓俪人购的商品
            if self.brandact_sign != 3:
                self.brandActItems()
        else:
            self.crawling_confirm = 2

    # 即将上线的品牌团信息
    def antPageComing(self, val):
        page, catId, catName, position, begin_date, begin_hour = val
        self.initItemComing(page, catId, catName, position, begin_date, begin_hour)
        self.itemConfig()
        self.brandActConpons()

    # 输出抓取的网页log
    def outItemLog(self):
        pages = []
        for p_tag in self.brandact_pages.keys():
            p_url, p_content = p_val

            # 网页文件名
            f_path = '%s_item/' %(self.brandact_id)
            f_name = '%s-%s_%d.htm' %(self.brandact_id, p_tag, self.crawling_time)

            # 网页文件内容
            f_content = '<!-- url=%s -->\n%s\n' %(p_url, p_content)
            pages.append((f_name, p_tag, f_path, f_content))

        return pages

    # 正点开团
    def outSql(self):
        return (Common.time_s(self.crawling_time),str(self.brandact_id),str(self.brandact_catgoryId),self.brandact_catgoryName,str(self.brandact_position),self.brandact_platform,self.brandact_channel,self.brandact_name,self.brandact_url,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_status,str(self.brandact_sign),self.brandact_other_ids,str(self.brandact_sellerId),self.brandact_sellerName,str(self.brandact_shopId),self.brandact_shopName,self.brandact_discount,str(self.brandact_soldCount),str(self.brandact_remindNum),str(self.brandact_coupon),';'.join(self.brandact_coupons),str(self.brandact_brandId),self.brandact_brand,str(self.brandact_inJuHome),str(self.brandact_juHome_position),Common.time_s(float(self.brandact_starttime)/1000),Common.time_s(float(self.brandact_endtime)/1000),self.crawling_beginDate,self.crawling_beginHour)

    # 即将上线
    def outSqlForComing(self):
        return (Common.time_s(self.crawling_time),str(self.brandact_id),str(self.brandact_catgoryId),self.brandact_catgoryName,str(self.brandact_position),self.brandact_platform,self.brandact_channel,self.brandact_name,self.brandact_url,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_status,str(self.brandact_sign),self.brandact_other_ids,str(self.brandact_sellerId),self.brandact_sellerName,str(self.brandact_shopId),self.brandact_shopName,self.brandact_discount,str(self.brandact_soldCount),str(self.brandact_remindNum),str(self.brandact_coupon),';'.join(self.brandact_coupons),str(self.brandact_brandId),self.brandact_brand,str(self.brandact_inJuHome),str(self.brandact_juHome_position),Common.time_s(float(self.brandact_starttime)/1000),Common.time_s(float(self.brandact_endtime)/1000),self.crawling_beginDate,self.crawling_beginHour)

    # 每天抓取
    def outSqlForDay(self):
        return (str(self.brandact_id),self.brandact_name,self.brandact_url,Common.time_s(float(self.brandact_starttime)/1000),Common.time_s(float(self.brandact_endtime)/1000),self.crawling_beginDate,self.crawling_beginHour)

    # 每小时抓取
    def outSqlForHour(self):
        return (str(self.brandact_id),self.brandact_name,self.brandact_url,Common.time_s(float(self.brandact_starttime)/1000),Common.time_s(float(self.brandact_endtime)/1000),self.crawling_beginDate,self.crawling_beginHour)

    # 输出元组
    def outTuple(self):
        main_sql = self.outSql()
        day_sql = self.outSqlForDay()
        hour_sql = self.outSqlForHour()
        return (self.brandact_itemVal_list, main_sql, day_sql, hour_sql, self.crawling_confirm)

    def outItem(self):
        print 'self.brandact_platform,self.brandact_channel,self.crawling_time,self.brandact_catgoryId,self.brandact_catgoryName,self.brandact_position,self.brandact_id,self.brandact_url,self.brandact_name,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_starttime,self.brandact_endtime,self.brandact_status,self.brandact_sign,self.brandact_other_ids,self.brandact_sellerId,self.brandact_sellerName,self.brandact_shopId,self.brandact_shopName,self.brandact_soldCount,self.brandact_remindNum,self.brandact_discount,self.brandact_coupon,self.brandact_coupons'
        print '# brandActivityItem:',self.brandact_platform,self.brandact_channel,self.crawling_time,self.brandact_catgoryId,self.brandact_catgoryName,self.brandact_position,self.brandact_id,self.brandact_url,self.brandact_name,self.brandact_desc,self.brandact_logopic_url,self.brandact_enterpic_url,self.brandact_starttime,self.brandact_endtime,self.brandact_status,self.brandact_sign,self.brandact_other_ids,self.brandact_sellerId,self.brandact_sellerName,self.brandact_shopId,self.brandact_shopName,self.brandact_soldCount,self.brandact_remindNum,self.brandact_discount,self.brandact_coupon,self.brandact_coupons

        """
        print '原数据信息:'
        print 'brand activity pagedata'
        print self.brandact_pagedata
        print 'brand activity page'
        print self.brandact_page
        print 'brand activity pages'
        print self.brandact_pages
        """



def test():
    pass


#
if __name__ == '__main__':
    test()
