#-*- coding:utf-8 -*-
#!/usr/bin/python
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
from JHSBActItem import JHSBActItem
from JHSItem import JHSItem
from db.MysqlAccess import MysqlAccess


class JHSBrand():
    '''A class of brand Item'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler    = TBCrawler()

        # 首页
        self.ju_home_url   = 'http://ju.taobao.com'
        self.refers     = 'http://www.tmall.com'

        # 品牌团页面
        self.brand_url  = 'http://ju.taobao.com/tg/brand.htm'

        # 首页的品牌团列表
        self.home_brands = {}
        self.home_brands_list = []

        # 品牌团页面
        self.brand_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=0'

        # 页面信息
        self.ju_home_page = '' # 聚划算首页
        self.ju_brand_page = '' # 聚划算品牌团页面

    def antPage(self):
        # 获取首页的品牌团
        page = self.crawler.getData(self.ju_home_url, self.refers)
        self.homeBrandAct(page) 

        # 获取品牌团列表页数据
        page = self.crawler.getData(self.brand_url, self.ju_home_url)
        self.activityList(page) 

    # 首页的品牌团
    def homeBrandAct(self, page):
        if not page or page == '': return

        print '首页品牌团'
        print '# ju home brand start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.ju_home_page = page
        m = re.search(r'<ul id="brandList" class="clearfix">(.+?)</ul>', page, flags=re.S)
        if m:
            brandact_content = m.group(1)
            p = re.compile(r'<li class="brand-mid-v2".+?>(.+?)</li>', flags=re.S)
            i = 0
            for brand_act in p.finditer(brandact_content):
                i += 1
                m = re.search(r'<a class="link-box hover-avil" href="(.+?)".+?>.+?<span class="title">(.+?)</span>.+?</a>', brand_act.group(1), flags=re.S)
                if m:
                    brand_act_id, brand_act_url, brand_act_name = '', '', ''
                    brand_act_url, brand_act_name = m.group(1), m.group(2)
                    m = re.search(r'act_sign_id=(\d+)', brand_act_url, flags=re.S)
                    if m:
                        brand_act_id = str(m.group(1))
                        self.home_brands[brand_act_id] = {'name':brand_act_name,'url':brand_act_url,'position':i}
                    self.home_brands_list.append({'id':brand_act_id,'name':brand_act_name,'url':brand_act_url,'position':i})
                    print i, brand_act_id, brand_act_url, brand_act_name
        print '# ju home brand end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 品牌团列表
    def activityList(self, page):
        if not page or page == '': return

        self.ju_brand_page = page
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
                activities = i_page['brandList']
                b_position_start = 0
                if i_page.has_key('currentPage') and int(i_page['currentPage']) > 1:
                    # 每页取60条数据
                    b_position_start = (int(i_page['currentPage']) - 1) * 60
                for i in range(0,len(activities)):
                    print '# A activity start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    activity = activities[i]
                    # 只测前几个
                    if int(b_position_start+i) >= 0:
                        print '#####A activity begin#####'
                        b = None
                        b = JHSBActItem()
                        b.antPage(activity, page[2], page[1], (b_position_start+i+1))
                        # 判断是否在首页推广
                        if self.home_brands.has_key(str(b.brandact_id)):
                            b.brandact_inJuHome = 1
                            b.brandact_juHome_position = self.home_brands[str(b.brandact_id)]['position']
                        # 入库
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


    # 从品牌团页获取数据
    def activityItems(self, actId, actName, actUrl):
        page = self.crawler.getData(actUrl, Config.ju_brand_home)
        m = re.search(r'<div id="content".+?>(.+?)</div>\s+<div class="crazy-wrap">', page, flags=re.S)
        if m:
            page = m.group(1)

        m = re.search(r'<div class="act-main ju-itemlist">', page, flags=re.S)
        if m:
            self.activitytemp2(m.group(1), actId, actName, actUrl)
        else:
            m = re.search(r'<div class="ju-itemlist J_JuHomeList">\s+<ul.+?>(.+?)</ul>', page, flags=re.S)
            if m:
                self.activitytemp3(m.group(1), actId, actName, actUrl)
            else:
                m = re.search(r'<div class="l-floor J_Floor .+?data-ajaxurl="(.+?)">', page, flags=re.S)
                if m:
                    self.activitytemp4(page, actId, actName, actUrl)
                else:
                    m = re.search(r'<table.+?>.+?<td>.+?<map.+?>.+?</map></td>.+?</table>', page, flags=re.S)
                    if m:
                        self.activitytemp5(page, actId, actName, actUrl)
                    else:
                        self.activitytemp1(page, actId, actName, actUrl)

    # 品牌团页面格式(1)
    def activitytemp1(self, page, actId, actName, actUrl):
        position = 0
        # source html floor
        # 第一层
        p = re.compile(r'<li class="item-big-v2">(.+?)</li>', flags=re.S)
        position += self.itemByBrandPage(p.finditer(page), actId, actName, actUrl, position, 'html')

        # other floor
        # 其他层数据
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
                position += self.itemByBrandPage(p.finditer(f_html), actId, actName, actUrl, position, 'html')
        return position


    # 品牌团页面格式(2)
    def activitytemp2(self, page, actId, actName, actUrl):
        position = 0
        # source html floor
        # 第一层
        p = re.compile(r'<div class="act-item0">(.+?)</div>\s+<img', flags=re.S)
        position += self.itemByBrandPage(p.finditer(page), actId, actName, actUrl, position, 'html')
        # 第二层
        m = re.search(r'<div class="act-item1">\s+<ul>(.+?)</u>\s+</div>', page, flags=re.S)
        if m:
            item1_page = m.group(1)
            p = re.compile(r'<li>(.+?)</li>', flags=re.S)
            position += self.itemByBrandPage(p.finditer(item1_page), actId, actName, actUrl, position, 'html')

        # other floor
        # 其他层数据
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
                position += self.itemByBrandPage(p.finditer(f_html), actId, actName, actUrl, position, 'html')
        return position

    # 品牌团页面格式(3)
    def activitytemp3(self, page, actId, actName, actUrl):
        position = 0
        p = re.compile(r'<li class="item-small-v3">(.+?)</li>', flags=re.S)
        position += self.itemByBrandPage(p.finditer(page), actId, actName, actUrl, position, 'html')
        return position

    # 品牌团页面格式(4)
    def activitytemp4(self, page, actId, actName, actUrl):
        position = 0
        # 请求接口数据
        p = re.compile(r'<div class="l-floor J_Floor .+? data-ajaxurl="(.+?)"', flags=re.S)
        for floor_url in p.finditer(page):
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            f_url = floor_url.group(1) + '&_ksTS=%s'%ts
            print f_url
            f_page = self.crawler.getData(f_url, actUrl)
            m = re.search(r'^{.+?\"itemList\":\[.+?\].+?}$', f_page, flags=re.S)
            if m:
                result = json.loads(f_page)
                if result.has_key('code') and int(result['code']) == 200 and result.has_key('itemList') and result['itemList'] != []:
                    item_list = result['itemList']
                    position += self.itemByBrandPage(item_list, actId, actName, actUrl, position, 'json')
        return position

    # 品牌团页面格式(5)
    def activitytemp5(self, page, actId, actName, actUrl):
        itemid_list = []
        items = {}
        p = re.compile(r'<area.+? href="http://detail.ju.taobao.com/home.htm?(.+?)".+?>', flags=re.S)
        for ids_str in p.finditer(page):
            ids_list = ids_str.split('&')
            for s in ids_list:
                itemid, juid = '', ''
                if s.find('itemId=') != -1:
                    itemid = s.split('itemId=')[1]
                elif s.find('item_id=') != -1:
                    itemid = s.split('item_id=')[1]
                elif s.find('&id=') != -1:
                    juid = s.split('id=')[1]
                    
                    
        return position

    # 获取商品信息
    def itemByBrandPage(self, itemdata_list, actId, actName, actUrl, position, page_type):
        i = 0
        for itemdata in itemdata_list:
            i += 1
            # 只测前几个数据
            if position+i < 2:
                if page_type == 'html':
                    ju_item_data = itemdata.group(1)
                else:
                    ju_item_data = itemdata
                item = None
                item = JHSItem()
                item.antPage(ju_item_data, actId, actName, actUrl, position+i, page_type)
                self.mysqlAccess.insertJhsItem(item.outSql())
                time.sleep(1)

        return i

    # 获取商品信息
    def itemByBrandPageFromJson(self, itemjson_list, actId, actName, position, actUrl):
        i = 0
        for itemjson in itemjson_list:
            i += 1
            # 只测前几个数据
            if position+i < 2:
                item = None
                item = JHSItem()
                item.antPage(itemjson, actId, actName, actUrl, position+i, 'json')
                self.mysqlAccess.insertJhsItem(item.outSql())
                time.sleep(1)

        return i
