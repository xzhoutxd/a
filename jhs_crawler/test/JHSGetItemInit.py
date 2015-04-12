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
from base.TBCrawler import TBCrawler
from db.MysqlAccess import MysqlAccess
from JHSBActItemM import JHSBActItemM
from JHSItem import JHSItem
from JHSItemM import JHSItemM

class JHSGetItemInit():
    '''A class of brand'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler    = TBCrawler()

        # 商品抓取队列
        self.itemcrawler_queue = Queue.Queue()

        # 品牌商品初始化信息
        self.act_id = ''
        self.act_name = ''
        self.act_url = ''
        self.act_itemVal_list = []

        # 抓取开始时间
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

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



