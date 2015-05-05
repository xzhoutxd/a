#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import traceback
import threading
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler
from crawler.TBItem import TBItem
from crawler.TMItem import TMItem

class JHSItem():
    '''A class of Juhuasuan Item'''
    def __init__(self):
        # 商品页面抓取设置
        self.crawler = TBCrawler()
        self.crawling_time = Common.now() # 当前爬取时间
        self.crawling_begintime = '' # 本次抓取开始时间
        self.crawling_beginDate = '' # 本次爬取日期
        self.crawling_beginHour = '' # 本次爬取小时

        # 商品所在活动
        self.item_actId = '' # 商品所属活动Id
        self.item_actName = '' # 商品所属活动Name
        self.item_act_url = '' # 商品所属活动Url
        self.item_position = 0 # 商品所在活动位置
        self.item_act_starttime = 0.0 # 商品所在活动开团时间
        self.item_act_endtime = 0.0 # 商品所在活动结束时间

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
        self.item_isLock = 1 # 商品是否锁定 0:锁定,1:没有锁定 售罄和结束为0
        self.item_isLock_time = None # 抓到锁定的时间
        self.item_merit = '' # 商品特色

        # 商品时间信息
        self.item_starttime = 0.0 # 商品开团时间
        self.item_endtime = 0.0 # 商品结束时间

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

        # 商品商品团信息
        self.item_status = '' # 商品状态
        self.item_groupCatId = '' # 商品所属分类Id
        self.item_groupCatName = '' # 商品所属分类Name
        self.item_groupCat_url = '' # 商品所属分类Url
        self.item_position = 0 # 商品所在分类位置
        self.item_subNavName = '' # 商品所在分类下子导航Name

        # 原数据信息
        self.item_pageData = '' # 商品所属数据项内容
        self.item_juPage = '' # 商品聚划算页面html内容
        self.item_pages = {} # 商品页面内请求数据列表

        # 每小时
        self.hour_index = 0 # 每小时的时刻

        # 商品状态类型
        self.item_status_type = 0 # 0:预热 1:售卖 2:售罄

    # 商品初始化
    def initItem(self, page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url, begin_time, start_time, end_time):
        # 商品所属数据项内容
        self.item_pageData = page
        self.item_pages['item-init'] = ('',page)
        # 商品所属活动Id
        self.item_actId = actId
        # 商品所属活动Name
        self.item_actName = actName
        # 商品所属活动Url
        self.item_act_url = Common.fix_url(actUrl)
        # 商品所在活动位置
        self.item_position = position
        # 商品聚划算链接
        self.item_ju_url = Common.fix_url(item_ju_url)
        # 商品Id
        self.item_id = item_id
        # 商品聚划算Id
        self.item_juId = item_juId
        # 商品活动展示图片Url
        self.item_juPic_url = Common.fix_url(item_juPic_url)
        # 本次抓取开始时间
        self.crawling_begintime = begin_time
        # 商品所在活动的开团时间
        self.item_act_starttime = start_time
        # 商品所在活动的结束时间
        self.item_act_endtime = end_time

    # 聚划算商品页信息
    def itemConfig(self):
        # 聚划算商品页信息
        self.itemPage()
        page = self.item_juPage
        self.item_pages['item-home'] = (self.item_ju_url, page)
        m = re.search(r'<div id="content" class="detail">(.+?)</div> <!-- /content -->', page, flags=re.S)
        if m:
            i_page = m.group(1)
        else:
            i_page = page

        m = re.search(r'JU_DETAIL_DYNAMIC = {(.+?)};', i_page, flags=re.S)
        if m:
            # 商品Id, 商品聚划算Id, 商品店铺类型
            m = re.search(r'"item_id": "(.+?)",.+?"id": "(.+?)",.+?"shopType": (.+?)\s+', i_page, flags=re.S)
            if m:
                self.item_id, self.item_juId, self.item_shopType = m.group(1), m.group(2), m.group(3)
            # 商品开始结束时间
            m = re.search(r'"onlineStartTime": "(.+?)",.+?"onlineEndTime": "(.+?)",.+?', i_page, flags=re.S)
            if m:
                self.item_starttime, self.item_endtime = m.group(1), m.group(2)

        # 商品图片
        if self.item_juPic_url == '':
            m = re.search(r'<div class="item-pic-wrap">.+?<img.+?src="(.+?)".+?/>', i_page, flags=re.S)
            if m:
                self.item_juPic_url = Common.fix_url(m.group(1))
            else:
                m = re.search(r'<div class="normal-pic.+?<img.+?data-ks-imagezoom="(.+?)".+?/>', i_page, flags=re.S)
                if m:
                    self.item_juPic_url = Common.fix_url(m.group(1))

        # 商品链接
        m = re.search(r'<div class="normal-pic.+?<a href="(.+?)".+?>', i_page, flags=re.S)
        if m:
            self.item_url = Common.fix_url(m.group(1))
        else:
            m = re.search(r'<div class="pic-box soldout".+?<a href="(.+?)".+?>', i_page, flags=re.S)
            if m:
                self.item_url = Common.fix_url(m.group(1))

        # 商品卖家Id, 商品卖家Name
        m = re.search(r'<a class="sellername" href=".+?user_number_id=(.+?)".+?>(.+?)</a>', i_page, flags=re.S)
        if m:
            self.item_sellerId, self.item_sellerName = m.group(1), m.group(2)
        else:
            m = re.search(r'<a href=".+?user_number_id=(.+?)".+?>(.+?)</a>', i_page, flags=re.S)
            if m:
                self.item_sellerId, self.item_sellerName = m.group(1), m.group(2)

        # 商品聚划算Name
        m = re.search(r'data-shortName="(.+?)"', i_page, flags=re.S)
        if m:
            self.item_juName = m.group(1)
        else:
            m = re.search(r'<title>(.+?)-(聚划算.+?)</title>', i_page, flags=re.S)
            if m:
                self.item_juName = m.group(1)
            else:
                m = re.search(r'<h2 class="[name|title]+">(.+?)</h2>', i_page, flags=re.S)
                if m:
                    self.item_juName = m.group(1).strip()

        # 商品聚划算说明
        m = re.search(r'<div class="description">(.+?)</div>', i_page, flags=re.S)
        if m:
            description = Common.htmlContent(m.group(1).strip())
            self.item_juDesc = ' '.join(description.split())

        # 商品原价
        m = re.search(r'<.+? class="originPrice">(.+?)</.+?>', i_page, flags=re.S)
        if m:
            self.item_oriPrice = m.group(1).strip()
            if self.item_oriPrice.find(';') != -1:
                self.item_oriPrice = self.item_oriPrice.split(';')[1]
        else:
            m = re.search(r'data-originalprice="(.+?)"', i_page, flags=re.S)
            if m:
                self.item_oriPrice = m.group(1)

        # 商品活动价
        m = re.search(r'<.+? class="currentPrice.+?>.+?</small>(.+?)</.+?>', i_page, flags=re.S)
        if m:
            self.item_actPrice = m.group(1).strip()
        else:
            m = re.search(r'data-itemprice="(.+?)"', i_page, flags=re.S)
            if m:
                self.item_actPrice = m.group(1)

        # 商品打折
        m = re.search(r'data-polldiscount="(.+?)"', i_page, flags=re.S)
        if m:
            self.item_discount = m.group(1)

        if self.item_id == '' or self.item_juId == '' or self.item_url == '' or self.item_actPrice == '': raise Common.InvalidPageException("# itemConfig: not find ju item params,juid:%s,item_ju_url:%s,%s,%s,%s,%s,%s"%(str(self.item_juId), self.item_ju_url,self.item_id,self.item_juId,self.item_url,self.item_actPrice,self.item_discount))
        # 商品关注人数, 商品销售数量, 商品库存
        self.itemDynamic(i_page)

    # 商品详情页html
    def itemPage(self):
        if self.item_ju_url != '':
            refer_url = ''
            if self.item_act_url != '':
                refer_url = self.item_act_url
            elif self.item_groupCat_url != '':
                refer_url = self.item_groupCat_url
            page = self.crawler.getData(self.item_ju_url, refer_url)

            if page and re.search(r'<title>【聚划算】无所不能聚</title>', str(page), flags=re.S):
                raise Common.NoPageException("# itemConfig: not find ju item page, redirecting to juhuasuan home,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
            elif type(self.crawler.history) is list and len(self.crawler.history) != 0 and re.search(r'302',str(self.crawler.history[0])):
                raise Common.NoPageException("# itemConfig: not find ju item page, redirecting to other page,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))

            if not page or page == '': 
                print '#crawler history:',self.crawler.history
                raise Common.InvalidPageException("# antPageDay: not find ju item page,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
            self.item_juPage = page
        else:
            raise Common.NoPageException("# itemConfig: not find ju item page, url is null,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))

    def itemDynamic(self, page):
        # 商品关注人数, 商品销售数量, 商品库存
        i_getdata_url = ''
        ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
        m = re.search(r'JU_DETAIL_DYNAMIC = {.+?"apiItemDynamicInfo": "(.+?)",.+?};', page, flags=re.S)
        if m:
            i_url = Common.fix_url(m.group(1))
            i_getdata_url = i_url + '?item_id=%s'%self.item_id + '&id=%s'%self.item_juId + '&_ksTS=%s'%ts
        else:
            i_getdata_url = 'http://dskip.ju.taobao.com/detail/json/item_dynamic.htm' + '?item_id=%s'%self.item_id + '&id=%s'%self.item_juId + '&_ksTS=%s'%ts

        if i_getdata_url:
            json_str = self.crawler.getData(i_getdata_url, self.item_ju_url)
            if not json_str or json_str == '': raise Common.InvalidPageException("# itemDynamic: not find ju item dynamic page,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
            self.item_pages['item-dynamic'] = (i_getdata_url, json_str)
            if json_str and json_str != '':
                m = re.search(r'"success":\s*"false"', json_str, flags=re.S)
                if m:
                    m = re.search(r'"data":\s*"NULL_ITEM.+?', json_str, flags=re.S)
                    if m:
                        raise Common.NoItemException("# itemDynamic: find dynamic page null,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))
                    else:
                        raise Common.InvalidPageException("# itemDynamic: find dynamic page false,juid:%s,item_ju_url:%s"%(str(self.item_juId), self.item_ju_url))

                m = re.search(r'"soldCount":\s*"(.+?)",', json_str, flags=re.S)
                if m:
                    self.item_soldCount = m.group(1)

                m = re.search(r'"remindNum":\s*"(.+?)",', json_str, flags=re.S)
                if m:
                    remindNum = m.group(1)
                    if self.item_soldCount == '':
                        self.item_remindNum = remindNum
                    else:
                        if remindNum != '' and int(remindNum) != 0:
                            self.item_remindNum = remindNum

                m = re.search(r'"stock":\s*"(.+?)",', json_str, flags=re.S)
                if m:           
                    self.item_stock = m.group(1)

                if self.item_soldCount != '' and int(self.item_soldCount) != 0 and self.item_stock != '' and int(self.item_stock) == 0:
                    self.item_isSoldout = 1

    # 商品锁定信息
    def itemLock(self, page):
        if page != '':
            m = re.search(r'JU_DETAIL_DYNAMIC = {.+?"isLock":\s*"(.+?)",.+?};', page, flags=re.S)
            if m:
                isLock = m.group(1)
                if isLock != '':
                    self.item_isLock = isLock
                    self.item_isLock_time = Common.now()
            
    # 商品其他优惠信息
    def itemPromotiton(self):
        promot_url = 'http://dskip.ju.taobao.com/promotion/json/get_shop_promotion.do?ju_id=%s'%str(self.item_juId)
        promot_page = self.crawler.getData(promot_url, self.item_ju_url)
        if not promot_page and promot_page == '': raise Common.InvalidPageException("# itemPromotion: not find promotion page")
        if promot_page and promot_page != '':
            self.item_pages['item-shoppromotion'] = (promot_url,promot_page)
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

    # parser item
    def itemParser(self):
        # 基本信息
        if type(self.item_pageData) is str:
            try:
                self.item_pageData = json.loads(self.item_pageData)
                self.itemDict()
            except Exception as e:
                print '# item itemParser json loads error:',self.item_pageData
                self.itemString()
        else:
            self.itemDict()
        self.item_pages['item-init'] = ('',self.item_pageData)

    # json string
    def itemString(self):
        if self.item_pageData != '':
            baseInfo = ''
            m = re.search(r'"baseinfo":({.+?}),"bizTagText":', self.item_pageData, flags=re.S|re.I)
            if m:
                baseInfo = m.group(1)
            else:
                m = re.search(r'"baseinfo":({.+?})', self.item_pageData, flags=re.S|re.I)
                if m:
                    baseInfo = m.group(1)

            if baseInfo != '':
                try:
                    i_baseInfo = json.loads(baseInfo)
                    self.item_baseInfoDict(i_baseInfo)
                except Exception as e:
                    self.item_baseInfoString(baseInfo)

            name = ''
            m = re.search(r'"name":({.+?}),"price":', self.item_pageData, flags=re.S)
            if m:
                name = m.group(1)
            else:
                m = re.search(r'"name":({.+?})', self.item_pageData, flags=re.S)
                if m:
                    name = m.group(1)
            if name != '':
                try:
                    i_name = json.loads(name)
                    self.item_nameDict(i_name)
                except Exception as e:
                    self.item_nameString(name)

            m = re.search(r'"remind":({.+?})', self.item_pageData, flags=re.S)
            if m:
                remind = m.group(1)
                try:
                    i_remind = json.loads(remind)
                    self.item_remindDict(i_remind)
                except Exception as e:
                    self.item_remindString(remind)
        
            m = re.search(r'"price":({.+?}),"remind"', self.item_pageData, flags=re.S)
            if m:
                price = m.group(1)
                try:
                    i_price = json.loads(price)
                    self.item_priceDict(i_price)
                except Exception as e:
                    self.item_priceString(price)

            m = re.search(r'"merit":({.+?}),"name"', self.item_pageData, flags=re.S)
            if m:
                merit = m.group(1)
                try:
                    i_merit = json.loads(merit)
                    self.item_meritDict(i_merit)
                except Exception as e:
                    self.item_meritString(merit)

    # Json string baseInfo
    def item_baseInfoString(self, i_baseInfo):
        if i_baseInfo:
            m = re.search(r'"itemId":(.+?),', i_baseInfo, flags=re.S)
            if m:
                # 商品Id
                self.item_id = m.group(1)
            m = re.search(r'"juId":(.+?),', i_baseInfo, flags=re.S)
            if m:
                # 商品juId
                self.item_juId = m.group(1)
            m = re.search(r'"itemUrl":"(.+?)",', i_baseInfo, flags=re.S)
            if m:
                # 商品聚划算链接
                self.item_ju_url = m.group(1)
            m = re.search(r'"ostime":(.+?),', i_baseInfo, flags=re.S)
            if m:
                # 商品开团时间
                self.item_starttime = m.group(1)
                #self.item_startdate = Common.add_hours_D(int(float(self.item_starttime)/1000), 1)
            m = re.search(r'"oetime":(.+?),', i_baseInfo, flags=re.S)
            if m:
                # 商品结束时间
                self.item_endtime = m.group(1)
            m = re.search(r'"itemStatus":"(.+?)",', i_baseInfo, flags=re.S)
            if m:
                # 商品状态
                self.item_status = m.group(1)
            # 商品聚划算展示图片链接
            m = re.search(r'"picUrl":"(.+?)",', i_baseInfo, flags=re.S)
            if m:
                self.item_juPic_url = m.group(1)
            else:
                m = re.search(r'"picUrlM":"(.+?)",', i_baseInfo, flags=re.S)
                if m:
                    self.item_juPic_url = m.group(1)
                else:
                    m = re.search(r'"picUrlW":"(.+?)",', i_baseInfo, flags=re.S)
                    if m:
                        self.item_juPic_url = m.group(1)

    # Json string name
    def item_nameString(self, i_name):
        if i_name:
            # 商品聚划算Name
            m = re.search(r'"title":"(.+?)",', i_name, flags=re.S)
            if m:
                self.item_juName = m.group(1)
            else:
                m = re.search(r'"shortName":"(.+?)",', i_name, flags=re.S)
                if m:
                    self.item_juName = m.group(1)
            m = re.search(r'"longName":"(.+?)",', i_name, flags=re.S)
            if m:
                # 商品聚划算说明
                self.item_juDesc = m.group(1)

    # Json dict remind
    def item_remindString(self, i_remind):
        if i_remind:
            m = re.search(r'"soldCount":(\d+)', i_remind, flags=re.S)
            if m:
                # 商品成交数
                self.item_soldCount = m.group(1)
            m = re.search(r'"remindNum":(\d+)', i_remind, flags=re.S)
            if m:
                # 商品想买人数
                self.item_remindNum = m.group(1)

    # Json string price
    def item_priceString(self, i_price):
        if i_price:
            m = re.search(r'"discount":"(.+?)",', i_price, flags=re.S)
            if m:
                # 商品打折
                self.item_discount = m.group(1)
            m = re.search(r'"origPrice":"(.+?)"', i_price, flags=re.S)
            if m:
                # 商品原价
                self.item_oriPrice = m.group(1)
            m = re.search(r'"actPrice":"(.+?)",', i_price, flags=re.S)
            if m:
                # 商品活动价
                self.item_actPrice = m.group(1)

    # Json string merit
    def item_meritString(self, i_merit):
        if i_merit:
            # 商品特色
            m = re.search(r'"down":\[(.+?)\]', i_merit, flags=re.S)
            if m:
                self.item_merit += m.group(1).replace('"','') + ';'
            m = re.search(r'"up":\[(.+?)\]', i_merit, flags=re.S)
            if m:
                self.item_merit += m.group(1).replace('"','') + ';'
            if self.item_merit == '':
                p = re.compile(r'"\w+":(.+?),',flags=re.S)
                for s in p.finditer(i_merit):
                    self.item_merit += s.group(1).replace('"','') + ';'

    # Json dict
    def itemDict(self):
        if self.item_pageData:
            if self.item_pageData.has_key('baseInfo'):
                i_baseInfo = self.item_pageData['baseInfo']
            elif self.item_pageData.has_key('baseinfo'):
                i_baseInfo = self.item_pageData['baseinfo']
            else:
                i_baseInfo = {}
                print '# item not find baseinfo in data',self.item_pageData
            self.item_baseInfoDict(i_baseInfo)
        if self.item_pageData.has_key('name'):
            i_name = self.item_pageData['name']
            self.item_nameDict(i_name)
        if self.item_pageData.has_key('remind'):
            i_remind = self.item_pageData['remind']
            self.item_remindDict(i_remind)
        if self.item_pageData.has_key('price'):
            i_price = self.item_pageData['price']
            self.item_priceDict(i_price)
        if self.item_pageData.has_key('merit'):
            i_merit = self.item_pageData['merit']
            self.item_meritDict(i_merit)

    # Json dict baseInfo
    def item_baseInfoDict(self, i_baseInfo):
        if i_baseInfo:
            if i_baseInfo.has_key('itemId') and i_baseInfo['itemId']:
                # 商品Id
                self.item_id = i_baseInfo['itemId']
            if i_baseInfo.has_key('juId') and i_baseInfo['juId']:
                # 商品juId
                self.item_juId = i_baseInfo['juId']
            if i_baseInfo.has_key('itemUrl') and i_baseInfo['itemUrl']:
                # 商品聚划算链接
                self.item_ju_url = i_baseInfo['itemUrl']
            if i_baseInfo.has_key('ostime') and i_baseInfo['ostime']:
                # 商品开团时间
                self.item_starttime = i_baseInfo['ostime']
                #self.item_startdate = Common.add_hours_D(int(float(self.item_starttime)/1000), 1)
            if i_baseInfo.has_key('oetime') and i_baseInfo['oetime']:
                # 商品结束时间
                self.item_endtime = i_baseInfo['oetime']
            if i_baseInfo.has_key('itemStatus') and i_baseInfo['itemStatus']:
                # 商品状态
                self.item_status = i_baseInfo['itemStatus']
            # 商品聚划算展示图片链接
            if i_baseInfo.has_key('picUrl') and i_baseInfo['picUrl']:
                self.item_juPic_url = i_baseInfo['picUrl']
            elif i_baseInfo.has_key('picUrlM') and i_baseInfo['picUrlM']:
                self.item_juPic_url = i_baseInfo['picUrlM']
            elif i_baseInfo.has_key('picUrlW') and i_baseInfo['picUrlW']:
                self.item_juPic_url = i_baseInfo['picUrlW']

    # Json dict name
    def item_nameDict(self, i_name):
        if i_name:
            # 商品聚划算Name
            if i_name.has_key('title') and i_name['title']:
                self.item_juName = i_name['title']
            elif i_name.has_key('shortName') and i_name['shortName']:
                self.item_juName = i_name['shortName']
            if i_name.has_key('longName') and i_name['longName']:
                # 商品聚划算说明
                self.item_juDesc = i_name['longName']

    # Json dict remind
    def item_remindDict(self, i_remind):
        if i_remind:
            if i_remind.has_key('soldCount'):
                # 商品成交数
                self.item_soldCount = i_remind['soldCount']
            if i_remind.has_key('remindNum'):
                # 商品想买人数
                self.item_remindNum = i_remind['remindNum']

    # Json dict price
    def item_priceDict(self, i_price):
        if i_price:
            if i_price.has_key('discount') and i_price['discount']:
                # 商品打折
                self.item_discount = i_price['discount']
            if i_price.has_key('origPrice') and i_price['origPrice']:
                # 商品原价
                self.item_oriPrice = i_price['origPrice']
            if i_price.has_key('actPrice') and i_price['actPrice']:
                # 商品活动价
                self.item_actPrice = i_price['actPrice']

    # Json dict merit
    def item_meritDict(self, i_merit):
        if i_merit:
            # 商品特色
            if i_merit.has_key('down') and i_merit['down']:
                self.item_merit += ','.join(i_merit['down']) + ';'
            if i_merit.has_key('up') and i_merit['up']:
                self.item_merit += ','.join(i_merit['up']) + ';'
            if self.item_merit == '':
                for key in i_merit.keys():
                    self.item_merit += ','.join(i_merit[key]) + ';'

    # 执行
    def antPage(self, val):
        page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url, begin_time, start_time,end_time = val
        self.initItem(page, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url, begin_time, start_time, end_time)
        self.itemConfig()
        self.itemPromotiton()
        page_datepath = 'item/main/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # Day
    def antPageDay(self, val):
        self.item_juId,self.item_actId,self.item_actName,self.item_act_url,self.item_juName,self.item_ju_url,self.item_id,self.item_url,self.item_oriPrice,self.item_actPrice,self.crawling_begintime = val

        # 本次抓取开始日期
        self.crawling_beginDate = time.strftime("%Y-%m-%d", time.localtime(self.crawling_begintime))
        # 本次抓取开始小时
        self.crawling_beginHour = time.strftime("%H", time.localtime(self.crawling_begintime))

        # 聚划算商品页信息
        self.itemPage()
        self.item_pages['item-home-day'] = (self.item_ju_url, self.item_juPage)
        # 是否售卖
        self.itemLock(self.item_juPage)
        # 商品关注人数, 商品销售数量, 商品库存
        self.itemDynamic(self.item_juPage)
        if self.item_soldCount == '' or self.item_stock == '':
            print '# item not get soldcount or stock,item_juid:%s,item_id:%s,item_actid:%s'%(str(self.item_juId),str(self.item_id),str(self.item_actId))
        page_datepath = 'item/day/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # Hour
    def antPageHour(self, val):
        self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime,self.hour_index = val
        # 聚划算商品页信息
        self.itemPage()
        self.item_pages['item-home-hour'] = (self.item_ju_url, self.item_juPage)
        # 是否售卖
        self.itemLock(self.item_juPage)
        # 商品关注人数, 商品销售数量, 商品库存
        self.itemDynamic(self.item_juPage)
        if self.item_soldCount == '' or self.item_stock == '':
            print '# item not get soldcount or stock,item_juid:%s,item_id:%s,item_actid:%s'%(str(self.item_juId),str(self.item_id),str(self.item_actId))
        page_datepath = 'item/hour/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # item islock
    def antPageLock(self, val):
        self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime,self.hour_index = val
        # 聚划算商品页信息
        self.itemPage()
        self.item_pages['item-home-hour'] = (self.item_ju_url, self.item_juPage)
        # 商品锁定信息
        self.itemLock(self.item_juPage)
        page_datepath = 'item/hour/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # update remind
    def antPageUpdateRemind(self, val):
        self.item_juId,self.item_actId,self.item_ju_url,self.item_act_url,self.item_id,self.crawling_begintime = val
        # 商品关注人数
        self.itemDynamic(self.item_juPage)
        if self.item_remindNum == '':
            # 聚划算商品页信息
            self.itemPage()
            self.item_pages['item-home-update'] = (self.item_ju_url, self.item_juPage)
            # 商品关注人数, 商品销售数量, 商品库存
            self.itemDynamic(self.item_juPage)
            if self.item_remindNum == '':
                print '# item not get remind num,item_juid:%s,item_id:%s,item_actid:%s'%(str(self.item_juId),str(self.item_id),str(self.item_actId))
        page_datepath = 'item/update/' + time.strftime("%Y/%m/%d/%H/", time.localtime(self.crawling_begintime))
        self.writeLog(page_datepath)

    # 商品团
    def antPageGroupItem(self, val):
        self.item_pageData,self.item_groupCatId,self.item_groupCatName,self.item_groupCat_url,self.item_subNavName,self.item_position,self.crawling_begintime = val
        self.itemParser()
        self.itemConfig()
        self.itemPromotiton()
        self.itemStatus()

    # parser item data
    # 解析商品数据
    def antPageGroupItemParserData(self, val):
        self.item_pageData,self.item_groupCatId,self.item_groupCatName,self.item_groupCat_url,self.item_subNavName,self.item_position,self.crawling_begintime = val
        # 本次抓取开始日期
        self.crawling_beginDate = time.strftime("%Y-%m-%d", time.localtime(self.crawling_begintime))
        # 本次抓取开始小时
        self.crawling_beginHour = time.strftime("%H", time.localtime(self.crawling_begintime))
        self.itemParser()
        self.itemStatus()

    # Hour
    def antPageGroupItemHour(self, val):
        self.item_groupCat_url,self.item_juId,self.item_id,self.item_ju_url,self.crawling_begintime,self.hour_index = val
        # 商品关注人数, 商品销售数量, 商品库存
        self.itemDynamic(self.item_juPage)
        if self.item_soldCount == '' or self.item_stock == '':
            # 聚划算商品页信息
            self.itemPage()
            self.item_pages['item-home-hour'] = (self.item_ju_url, self.item_juPage)
            # 商品关注人数, 商品销售数量, 商品库存
            self.itemDynamic(self.item_juPage)
            if self.item_soldCount == '' or self.item_stock == '':
                print '# item not get soldcount or stock,item_juid:%s,item_id:%s'%(str(self.item_juId),str(self.item_id))

    def itemStatus(self):
        if self.item_status:
            if self.item_status == 'blank':
                self.item_status_type = 0
            elif self.item_status == 'avil':
                self.item_status_type = 1
            elif self.item_status == 'soldout':
                self.item_status_type = 2
            else:
                self.item_status_type = 2

    # 输出item info SQL
    def outIteminfoSql(self):
        return (Common.time_s(self.crawling_time),str(self.item_juId),str(self.item_actId),self.item_actName,Common.fix_url(self.item_act_url),str(self.item_position),Common.fix_url(self.item_ju_url),self.item_juName,self.item_juDesc,Common.fix_url(self.item_juPic_url),self.item_id,Common.fix_url(self.item_url),str(self.item_sellerId),self.item_sellerName,str(self.item_shopType),str(self.item_oriPrice),str(self.item_actPrice),str(self.item_discount),str(self.item_remindNum),';'.join(self.item_promotions),self.item_act_starttime,self.item_act_endtime)

    # 每天的SQL
    def outSqlForDay(self):
        return (Common.time_s(self.crawling_time),str(self.item_juId),str(self.item_actId),self.item_actName,Common.fix_url(self.item_act_url),self.item_juName,Common.fix_url(self.item_ju_url),self.item_id,Common.fix_url(self.item_url),str(self.item_oriPrice),str(self.item_actPrice),str(self.item_soldCount),str(self.item_stock),self.crawling_beginDate,self.crawling_beginHour)

    # 每小时的SQL
    def outSqlForHour(self):
        return (Common.date_s(self.crawling_time),str(self.hour_index),str(self.item_juId),str(self.item_actId),str(self.item_soldCount),str(self.item_stock))

    # 商品锁定信息
    def outSqlForLock(self):
        try:
            if self.item_isLock_time:
                return (self.item_juId,Common.time_s(self.item_isLock_time),self.item_isLock)
            else:
                return None
        except Exception as e:
            print '# out item Lock Sql err:',e
            return None

    # 更新item remind SQL
    def outSqlForUpdateRemind(self):
        if str(self.item_remindNum) != '':
            return (str(self.item_juId),str(self.item_remindNum))
        else:
            return None

    # 输出Tuple
    def outTuple(self):
        iteminfoSql = self.outIteminfoSql()
        return iteminfoSql

    # 输出每天Tuple
    def outTupleDay(self):
        sql = self.outSqlForDay()
        lockSql = self.outSqlForLock()
        return (sql,lockSql)

    # 输出每小时Tuple
    def outTupleHour(self):
        sql = self.outSqlForHour()
        lockSql = self.outSqlForLock()
        return (sql,lockSql)

    # 更新item remind Tuple
    def outTupleUpdateRemind(self):
        sql = self.outSqlForUpdateRemind()
        return sql

    # 商品团商品全部信息sql
    def outGroupIteminfoSql(self):
        return (Common.time_s(self.crawling_time),str(self.item_juId),str(self.item_groupCatId),self.item_groupCatName,self.item_subNavName,str(self.item_position),Common.fix_url(self.item_ju_url),Common.fix_url(self.item_juPic_url),self.item_juName,self.item_juDesc,str(self.item_id),Common.fix_url(self.item_url),self.item_status,self.item_merit,str(self.item_sellerId),self.item_sellerName,str(self.item_shopType),str(self.item_oriPrice),str(self.item_actPrice),str(self.item_discount),str(self.item_remindNum),str(self.item_soldCount),';'.join(self.item_promotions),Common.time_s(float(self.item_starttime)/1000),Common.time_s(float(self.item_endtime)/1000)) 
    # 商品团商品的解析信息
    def outGroupItemParserSql(self):
        return (Common.time_s(self.crawling_time),str(self.item_juId),str(self.item_groupCatId),self.item_groupCatName,self.item_subNavName,str(self.item_position),Common.fix_url(self.item_ju_url),Common.fix_url(self.item_juPic_url),self.item_juName,self.item_juDesc,str(self.item_id),self.item_status,self.item_merit,str(self.item_oriPrice),str(self.item_actPrice),str(self.item_discount),str(self.item_remindNum),str(self.item_soldCount),Common.time_s(float(self.item_starttime)/1000),Common.time_s(float(self.item_endtime)/1000),self.crawling_beginDate,self.crawling_beginHour)
    # 商品团每小时销量库存的SQL
    def outGroupItemSqlForHour(self):
        return (Common.date_s(self.crawling_time),str(self.hour_index),str(self.item_juId),str(self.item_soldCount),str(self.item_stock))


    # 商品团商品信息
    def outTupleGroupItem(self):
        return self.outGroupIteminfoSql()
    # 商品团商品json数据解析信息
    def outTupleGroupItemParser(self):
        return (self.item_status_type,self.outGroupItemParserSql(),(self.item_pageData,self.item_groupCatId,self.item_groupCatName,self.item_groupCat_url,self.item_subNavName,self.item_position))
    # 商品团商品每小时销售信息
    def outTupleGroupItemHour(self):
        return self.outGroupItemSqlForHour()

    # 输出商品的网页
    def outItemPage(self,crawl_type):
        if self.crawling_begintime != '':
            time_s = time.strftime("%Y%m%d%H", time.localtime(self.crawling_begintime))
        else:
            time_s = time.strftime("%Y%m%d%H", time.localtime(self.crawling_time))
        # timeStr_jhstype_webtype_item_crawltype_itemjuid
        key = '%s_%s_%s_%s_%s_%s' % (time_s,Config.JHS_TYPE,'1','item',crawl_type,str(self.item_juId))
        pages = {}
        for p_tag in self.item_pages.keys():
            p_url, p_content = self.item_pages[p_tag]
            f_content = '<!-- url=%s --> %s' %(p_url, p_content)
            pages[p_tag] = f_content.strip()
        return (key,pages)

    # 写html文件
    def writeLog(self,time_path):
        try:
            return None
            pages = self.outItemLog()
            for page in pages:
                filepath = Config.pagePath + time_path + page[2]
                Config.createPath(filepath)
                #if not os.path.exists(filepath):
                #    os.mkdir(filepath)
                filename = filepath + page[0]
                fout = open(filename, 'w')
                fout.write(page[3])
                fout.close()
        except Exception as e:
            print '# exception err in writeLog info:',e

    # 输出抓取的网页log
    def outItemLog(self):
        pages = []
        for p_tag in self.item_pages.keys():
            p_url, p_content = self.item_pages[p_tag]

            # 网页文件名
            f_path = '%s_item/%s/' %(self.item_actId, self.item_juId)
            f_name = '%s-%s_%s_%d.htm' %(self.item_actId, self.item_juId, p_tag, self.crawling_time)

            # 网页文件内容
            f_content = '<!-- url=%s -->\n%s\n' %(p_url, p_content)
            pages.append((f_name, p_tag, f_path, f_content))

        return pages

def test():
    #(itemdata, actId, actName, actUrl, position, item_ju_url, item_id, item_juId, item_juPic_url)

    url = 'http://detail.ju.taobao.com/home.htm?id=10000006058022&amp;item_id=42860458287'
    item_id = '42860458287'
    ju_id = '10000006058022'
    item = JHSItem()
    begin_time = Common.now()
    val = ('', '', '', '', 1, url, item_id, ju_id, '', begin_time, '', '')
    item.antPage(val)
    print item.outTuple()
    #item.outItem()
    #print item.item_remindNum
    #print item.item_soldCount
    #print item.item_stock

if __name__ == '__main__':
    test()

