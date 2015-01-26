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
from crawler.TBItem import TBItem
from crawler.TMItem import TMItem
from parser.parserTBItem import PTBItem
from parser.parserTMItem import PTMItem

class JHSItem():
    '''A class of Juhuasuan Item'''
    def __init__(self):
        # 商品页面抓取设置
        self.crawler    = TBCrawler()
        self.crawling_time   = Common.now()

        # 商品所在活动
        self.item_actId = '' # 商品所属活动Id
        self.item_actName = '' # 商品所属活动Name
        self.item_act_url = '' # 商品所属活动Url
        self.item_position = 0 # 商品所在活动位置

        # 商品信息
        self.item_juId = '' # 商品聚划算Id
        self.item_ju_url = '' # 商品聚划算链接
        self.item_id = '' # 商品Id
        self.item_url = '' # 商品链接
        self.item_juPic_url = '' # 商品聚划算展示图片链接
        self.item_juName = '' # 商品聚划算Name
        self.item_juDesc = '' # 商品聚划算说明
        self.item_catId = '' # 商品叶子类目Id
        self.item_catName = '' # 商品叶子类目Name
        self.item_brand = '' # 商品品牌
        self.item_isSoldout = 0 # 商品是否售罄 0:没有售罄,1:售罄

        # 商品店铺
        self.item_sellerId = '' # 商品卖家Id
        self.item_sellerName = '' # 商品卖家Name
        self.item_shopId = '' # 商品店铺Id
        self.item_shopName = '' # 商品店铺Name
        self.item_shopType = 0 # 商品店铺类型 0:默认 1:天猫 2:集市

        # 商品交易
        self.item_oriPrice = '' # 商品原价
        self.item_actPrice = '' # 商品活动价
        self.item_discount = '' # 商品打折
        self.item_remindNum = '' # 商品关注人数
        self.item_soldCount = '' # 商品销售数量
        self.item_stock = '' # 商品库存
        self.item_promotions = [] # 商品其他优惠
        self.item_prepare = 0 # 商品活动前备货数
        self.item_favorites = 0 # 商品收藏数

        # 原数据信息
        self.item_pageData = '' # 商品所属数据项内容
        self.item_juPage = '' # 商品聚划算页面html内容
        self.item_pages = {} # 商品页面内请求数据列表

    # 商品初始化
    def initItem(self, page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url):
        # 商品所属数据项内容
        self.item_pageData = page
        self.item_pages['item_init'] = ('',page)
        # 商品所属活动Id
        self.item_actId = actId
        # 商品所属活动Name
        self.item_actName = actName
        # 商品所属活动Url
        self.item_act_url = actUrl
        # 商品所在活动位置
        self.item_position = position
        # 商品聚划算链接
        self.item_ju_url = item_ju_url
        # 商品Id
        self.item_id = item_id
        # 商品聚划算Id
        self.item_juId = item_juId
        # 商品活动展示图片Url
        self.item_juPic_url = item_juPic_url

    # Configuration from html type
    def itemConfigFromHtml(self):
        # 基本信息
        m = re.search(r'<a.+?href="(.+?)".+?>', self.item_pageData, flags=re.S)
        if m:
            # 商品聚划算链接
            self.item_ju_url = m.group(1)
            if self.item_ju_url:
                ids_list = self.item_ju_url.split('&')
                for ids in ids_list:
                    if ids.find('item_id=') != -1:
                        # 商品Id
                        self.item_id = ids.split('=')[1]
                    elif ids.find('id=') != -1:
                        # 商品聚划算Id
                        self.item_juId = ids.split('=')[1]

        # 商品聚划算展示图片链接
        m = re.search(r'<img class="item-pic" data-ks-lazyload="(.+?)"', self.item_pageData, flags=re.S)
        if m:
            self.item_juPic_url = m.group(1)
        else:
            m = re.search(r'<img data-ks-lazyload="(.+?)"', self.item_pageData, flags=re.S)
            if m:
                self.item_juPic_url = m.group(1)

    # Configuration from json type
    def itemConfigFromJson(self):
        # 基本信息
        if self.item_pageData.has_key('baseinfo'):
            item_baseinfo = self.item_pageData['baseinfo']
            # 商品聚划算展示图片链接
            if item_baseinfo.has_key('picUrl') and item_baseinfo['picUrl'] != '':
                self.item_juPic_url = item_baseinfo['picUrl']
            elif item_baseinfo.has_key('picUrlM') and item_baseinfo['picUrlM'] != '':
                self.item_juPic_url = item_baseinfo['picUrlM']
            # 商品聚划算链接
            if item_baseinfo.has_key('itemUrl') and item_baseinfo['itemUrl'] != '':
                self.item_ju_url = item_baseinfo['itemUrl']
                ids_list = self.item_ju_url.split('&')
                for ids in ids_list:
                    if ids.find('item_id=') != -1:
                        if self.item_id == '':
                            # 商品Id
                            self.item_id = ids.split('=')[1]
                    elif ids.find('id=') != -1:
                        # 商品聚划算Id
                        self.item_juId = ids.split('=')[1]
            # 商品Id
            if item_baseinfo.has_key('itemId') and item_baseinfo['itemId'] != '':
                self.item_id = item_baseinfo['itemId']

        # 商品关注人数, 商品销售数量
        if self.item_pageData.has_key('remind'):
            item_remind = self.item_pageData['remind']
            if item_remind.has_key('remindNum'):
                self.item_remindNum = item_remind['remindNum']
            if item_remind.has_key('soldCount'):
                self.item_soldCount = item_remind['soldCount']

        # 商品原价, 商品活动价
        if self.item_pageData.has_key('price'):
            item_price = self.item_pageData['price']
            if item_price.has_key('origPrice'):
                self.item_oriPrice = item_price['origPrice']
            if item_price.has_key('actPrice'):
                self.item_actPrice = item_price['actPrice']

    # 聚划算商品页信息
    def itemConfig(self):
        # 聚划算商品页信息
        page = self.crawler.getData(self.item_ju_url, self.item_act_url)
        if not page or page == '': raise Common.InvalidPageException("# %s:not find ju item page,juid:%s,item_ju_url:%s"%(sys._getframe().f_back.f_code.co_name, str(self.item_juId), self.item_ju_url))
        if page and page != '':
            self.item_juPage = page
            self.item_pages['item_home'] = (self.item_ju_url, page)
            m = re.search(r'<div id="content" class="detail">(.+?)</div> <!-- /content -->', page, flags=re.S)
            if m:
                i_page = m.group(1)
                # 商品Id, 商品聚划算Id, 商品店铺类型 
                m = re.search(r'JU_DETAIL_DYNAMIC = {(.+?)};', i_page, flags=re.S)
                if m:
                    m = re.search(r'"item_id": "(.+?)",.+?"id": "(.+?)",.+?"shopType": (.+?)\s+', i_page, flags=re.S)
                    if m:
                        self.item_id, self.item_juId, self.item_shopType = m.group(1), m.group(2), m.group(3)
                # 商品图片
                if self.item_juPic_url == '':
                    m = re.search(r'<div class="item-pic-wrap">.+?<img.+?src="(.+?)".+?/>', i_page, flags=re.S)
                    if m:
                        self.item_juPic_url = m.group(1)
                    else:
                        m = re.search(r'<div class="normal-pic.+?<img.+?data-ks-imagezoom="(.+?)".+?/>', i_page, flags=re.S)
                        if m:
                            self.item_juPic_url = m.group(1)

                # 商品链接
                m = re.search(r'<div class="normal-pic.+?<a href="(.+?)".+?>', i_page, flags=re.S)
                if m:
                    self.item_url = m.group(1)
                else:
                    m = re.search(r'<div class="pic-box soldout".+?<a href="(.+?)".+?>', i_page, flags=re.S)
                    if m:
                        self.item_url = m.group(1)

                # 商品卖家Id, 商品卖家Name
                m = re.search(r'<div class="con inf-seller">\s+<a href=".+?user_number_id=(.+?)".+?>(.+?)</a>\s+</div>', i_page, flags=re.S)
                if m:
                    self.item_sellerId, self.item_sellerName = m.group(1), m.group(2)

                # 商品聚划算Name
                m = re.search(r'<h2 class="name">(.+?)</h2>', i_page, flags=re.S)
                if m:
                    self.item_juName = m.group(1).strip()

                # 商品聚划算说明
                m = re.search(r'<div class="description">(.+?)</div>', i_page, flags=re.S)
                if m:
                    self.item_juDesc = m.group(1).strip()

                # 商品原价
                m = re.search(r'<del class="originPrice">(.+?)</del>', i_page, flags=re.S)
                if m:
                    self.item_oriPrice = m.group(1).strip()
                    if self.item_oriPrice.find(';') != -1:
                        self.item_oriPrice = self.item_oriPrice.split(';')[1]
                else:
                    m = re.search(r'<span class="originPrice">(.+?)</span>', i_page, flags=re.S)
                    if m:
                        self.item_oriPrice = m.group(1).strip()
                        if self.item_oriPrice.find(';') != -1:
                            self.item_oriPrice = self.item_oriPrice.split(';')[1]

                # 商品活动价
                m = re.search(r'<span class="currentPrice.+?>.+?</small>(.+?)</span>', i_page, flags=re.S)
                if m:
                    self.item_actPrice = m.group(1).strip()

                # 商品打折
                m = re.search(r'data-polldiscount="(.+?)"', i_page, flags=re.S)
                if m:
                    self.item_discount = m.group(1)

                # 商品关注人数, 商品销售数量, 商品库存
                i_getdata_url = ''
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                m = re.search(r'JU_DETAIL_DYNAMIC = {.+?"apiItemDynamicInfo": "(.+?)",.+?};', i_page, flags=re.S)
                if m:
                    i_getdata_url = m.group(1) + '?item_id=%s'%self.item_id + '&id=%s'%self.item_juId + '&_ksTS=%s'%ts
                else:
                    i_getdata_url = 'http://dskip.ju.taobao.com/detail/json/item_dynamic.htm' + '?item_id=%s'%self.item_id + '&id=%s'%self.item_juId + '&_ksTS=%s'%ts

                if i_getdata_url:
                    json_str = self.crawler.getData(i_getdata_url, self.item_ju_url)
                    self.item_pages['item_dynamic'] = (i_getdata_url, json_str)
                    if json_str and json_str != '':
                        result = json.loads(json_str)
                        if result.has_key('data'):
                            result_data = result['data']
                            if result_data.has_key('soldCount'):
                                self.item_soldCount = result_data['soldCount']
                            else:
                                if result_data.has_key('remindNum') and result_data['remindNum']:
                                    self.item_remindNum = result_data['remindNum']

                            if result_data.has_key('stock'):
                                self.item_stock = result_data['stock']
                            if self.item_soldCount != '' and int(self.item_soldCount) != 0 and self.item_stock != '' and int(self.item_stock) == 0:
                                self.item_isSoldout = 1

    # 商品其他优惠信息
    def itemPromotiton(self):
        promot_url = 'http://dskip.ju.taobao.com/promotion/json/get_shop_promotion.do?ju_id=%s'%str(self.item_juId)
        promot_page = self.crawler.getData(promot_url, self.item_ju_url)
        if promot_page and promot_page != '':
            self.item_pages['item_shoppromotion'] = (promot_url,promot_page)
            #m = re.search(r'jsonp\d+\((.+?)\)$', promot_page, flags=re.S)
            #if m:
            #    json_str = m.group(1)
            #    result = json.loads(json_str)
            result = json.loads(promot_page)
            if result.has_key('success') and result.has_key('model') and result['model'] != []:
                for model in result['model']:
                    title = ''
                    if model.has_key('title'):
                        title = model['title']
                    if model.has_key('promLevels') and model['promLevels'] != []:
                        for level in model['promLevels']:
                            if level.has_key('title'):
                                self.item_promotions.append('%s:%s'%(title,level['title']))

    # 商品详情页信息
    def getFromTMTBPage(self):
        try:
            #result = None
            Item = None
            PItem = None
            # 天猫店铺
            if int(self.item_shopType) == 1:
                Item = TMItem()
                Item.antPage(self.item_url)
                if not Item.item_page or Item.item_page == '': raise Common.InvalidPageException("# %s:not find TB or TM item page,juid:%s,id:%s,item_url:%s"%(sys._getframe().f_back.f_code.co_name, str(self.item_juId), str(self.item_id), self.item_url))
                PItem = PTMItem()
                PItem.antPage(Item)
                #result = PItem.outItemCrawl()
            # 集市店铺
            elif int(self.item_shopType) == 2:
                Item = TBItem()
                Item.antPage(self.item_url)
                if not Item.item_page or Item.item_page == '': raise Common.InvalidPageException("# %s:not find TB or TM item page,juid:%s,id:%s,item_url:%s"%(sys._getframe().f_back.f_code.co_name, str(self.item_juId), str(self.item_id), self.item_url))
                PItem = PTBItem()
                PItem.antPage(Item)
                #result = PT.outItemCrawl()
                    
            # 商品店铺Id, 商品店铺Name, 商品叶子类目Id, 商品活动前备货数, 商品收藏数, 商品品牌
            if PItem:
                self.item_shopId, self.item_shopName, self.item_catId, self.item_prepare, self.item_favorites, self.item_brand = PItem.shop_id, PItem.shop_name, PItem.item_catId, PItem.item_stock, PItem.item_favorites, PItem.item_brand
        except Exception as e:
            print "# %s,juid:%s,id:%s,item_url:%s,info:%"%(sys._getframe().f_back.f_code.co_name, str(self.item_juId), str(self.item_id), self.item_url, e)
            traceback.print_exc()

    # 执行
    #def antPage(self, page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url):
    def antPage(self, val):
        try:
            page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url = val
            self.initItem(page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)
            self.itemConfig()
            self.itemPromotiton()
            self.getFromTMTBPage()
            #self.outItem()
        except Exception as e:
            print "# %s,juid:%s,item_url:%s,info:%s"%(sys._getframe().f_back.f_code.co_name, str(self.item_juId), self.item_ju_url, e)
            traceback.print_exc()

    # 输出SQL
    def outSql(self):
        return (Common.time_s(self.crawling_time),str(self.item_juId),str(self.item_actId),self.item_actName,self.item_act_url,str(self.item_position),self.item_ju_url,self.item_juName,self.item_juDesc,self.item_juPic_url,self.item_id,self.item_url,str(self.item_sellerId),self.item_sellerName,str(self.item_shopId),self.item_shopName,str(self.item_shopType),str(self.item_oriPrice),str(self.item_actPrice),str(self.item_discount),str(self.item_remindNum),str(self.item_soldCount),str(self.item_stock),str(self.item_prepare),str(self.item_favorites),';'.join(self.item_promotions),str(self.item_catId),self.item_brand)

    #
    def outItem(self):
        print 'self.crawling_time,self.item_actId,self.item_actName,self.item_act_url,self.item_position,self.item_juId,self.item_ju_url,self.item_id,self.item_url,self.item_juPic_url,self.item_juName,self.item_juDesc,self.item_catId,self.item_catName,self.item_brand,self.item_sellerId,self.item_sellerName,self.item_shopId,self.item_shopName,self.item_shopType,self.item_oriPrice,self.item_actPrice,self.item_discount,self.item_remindNum,self.item_soldCount,self.item_stock,self.item_promotions,self.item_prepare,self.item_favorites'
        print '# Ju Item:',self.crawling_time,self.item_actId,self.item_actName,self.item_act_url,self.item_position,self.item_juId,self.item_ju_url,self.item_id,self.item_url,self.item_juPic_url,self.item_juName,self.item_juDesc,self.item_catId,self.item_catName,self.item_brand,self.item_sellerId,self.item_sellerName,self.item_shopId,self.item_shopName,self.item_shopType,self.item_oriPrice,self.item_actPrice,self.item_discount,self.item_remindNum,self.item_soldCount,self.item_stock,self.item_promotions,self.item_prepare,self.item_favorites

        """
        print '原数据信息'
        print '商品所属数据项内容'
        print self.item_pageData
        print '商品聚划算页面html内容'
        print self.item_juPage
        print '页面所有加载页面'
        print self.item_pages
        """


def test():
    print '# activity Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    crawler = TBCrawler()
    actId = '4484443'
    actName = '全场1.4折起'
    actUrl = 'http://ju.taobao.com/tg/brand_items.htm?act_sign_id=4484443'
    page = crawler.getData(actUrl, Config.ju_brand_home)
    m = re.search(r'<div id="content">(.+?)</div>\s+<div class="crazy-wrap">', page, flags=re.S)
    if m:
        page = m.group(1)
        # 商品
        position = 0
        m = re.search(r'<div class="act-main ju-itemlist">', page, flags=re.S)
        if m:
            # source html floor
            p = re.compile(r'<div class="act-item0">(.+?)</div>\s+<img', flags=re.S)
            position += itemByBrandPage(page, actId, actName, p, position, actUrl)
            m = re.search(r'<div class="act-item1">\s+<ul>(.+?)</u>\s+</div>', page, flags=re.S)
            if m:
                item1_page = m.group(1)
                p = re.compile(r'<li>(.+?)</li>', flags=re.S)
                position += itemByBrandPage(item1_page, actId, actName, p, position, actUrl)

            # other floor
            getdata_url = "http://ju.taobao.com/json/tg/ajaxGetItems.htm?stype=ids&styleType=small&includeForecast=true"
            p = re.compile(r'<div class="act-item J_jupicker" data-item="(.+?)">', flags=re.S)
            for floor_url in p.finditer(page):
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                f_url = getdata_url + '&juIds=' + floor_url.group(1) + '&_ksTS=%s'%ts
                print f_url
                f_page = crawler.getData(f_url, actUrl)
                m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
                if m:
                    f_html = m.group(1)
                    p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
                    position += itemByBrandPage(f_html, actId, actName, p, position, actUrl)
            
        else:
            # source html floor
            p = re.compile(r'<li class="item-big-v2">(.+?)</li>', flags=re.S)
            position += itemByBrandPage(page, actId, actName, p, position, actUrl)

            # other floor
            p = re.compile(r'<div class="l-floor J_Floor J_ItemList" .+? data-url="(.+?)">', flags=re.S)
            for floor_url in p.finditer(page):
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                f_url = floor_url.group(1) + '&_ksTS=%s'%ts
                print f_url
                f_page = crawler.getData(f_url, actUrl)
                m = re.search(r'html\":\'(.+?)\'', f_page, flags=re.S)
                if m:
                    f_html = m.group(1)
                    p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
                    position += itemByBrandPage(f_html, actId, actName, p, position, actUrl)
    print '# activity Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

def itemByBrandPage(page, actId, actName, p, position, actUrl):
    i = 0
    for ju_item in p.finditer(page):
        i += 1
        item = JHSItem()
        item.antPage(page, actId, actName, actUrl, position+i)

    return i

if __name__ == '__main__':
    test()

