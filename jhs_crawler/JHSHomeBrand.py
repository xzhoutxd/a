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
from base.RetryCrawler import RetryCrawler

class JHSHomeBrand():
    '''A class of brand for home hot'''
    def __init__(self):
        # 页面信息
        self.ju_home_page = '' # 聚划算首页

        # 首页的品牌团列表
        self.home_brands = {}

        # 通过首页可以得到品牌团数量
        self.new_brandNum = 0 # 新上线
        self.hot_brandNum = 0 # 正在热卖
        self.total_brandNum = 0 # 所有总数

        # 抓取开始时间
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

    def antPage(self, page):
        if not page or page == '': raise Common.InvalidPageException("# homeBrand antPage: not get JHS home.")
        
        # 获取首页的品牌团
        self.homeBrandAct(page) 

    # 首页的品牌团
    def homeBrandAct(self, page):
        #if not page or page == '': raise Common.InvalidPageException("# homeBrandAct: not get JHS home.")
        print '首页品牌团'
        print '# ju home brand start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.ju_home_page = page

        m = re.search(r'<ul id="brandList" class="clearfix">(.+?)</ul>', page, flags=re.S)
        if m:
            self.homeBrandTemp1(m.group(1))
        else:
            m = re.search(r'<script>\s+window.shangouData = \[(.+?)\];\s+</script>', page, flags=re.S)
            if m:
                self.homeBrandTemp2(m.group(1))
            m1 = re.search(r'<div class="ju-wrapper">.+?<div class="mod-brandbd">\s+<div class="ju-itemlist clearfix".+?<ul class="clearfix">(.+?)</ul>', page, flags=re.S)
            m2 = re.search(r'<div class="ju-wrapper">.+?<div class="mod-brandbd">.+?<div class="logowall brand-footer clearfix".+?>(.+?)</div>', page, flags=re.S)
            if m1 or m2:
                self.homeBrandTemp3(page)
        print '# ju home brand end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

    # 首页品牌团页面模板1
    def homeBrandTemp1(self, page):
        p = re.compile(r'<li class="brand-mid-v2".+?>(.+?)</li>', flags=re.S)
        i = 0
        for brand_act in p.finditer(page):
            i += 1
            m = re.search(r'<a class="link-box hover-avil" href="(.+?)".+?>.+?<span class="title">(.+?)</span>.+?</a>', brand_act.group(1), flags=re.S)
            if m:
                brand_act_id, brand_act_url, brand_act_name = '', '', ''
                a_val = (Common.fix_url(brand_act.group(1)),brand_act.group(2),i)
                self.parser_actinfo(a_val)

    # 首页品牌团页面模板2
    def homeBrandTemp2(self, page):
        dataType_key_list = ["hotBrands","lastBrands","newBrands"]
        dataType_name = {"hotBrands":"正在热卖","lastBrands":"最后疯狂","newBrands":"今日上新"}
        result = json.loads(page)
        #print result
        if result.has_key('indexShanGouVO'):
            index = result['indexShanGouVO']
            # 首页品牌推广展示模块
            for dataType_key in dataType_key_list:
                if index.has_key(dataType_key):
                    print '# %s:'%dataType_key, len(index[dataType_key])
                    brands = self.JsonListConfig(index[dataType_key], dataType_key, dataType_name[dataType_key])
                    if brands and brands != {}:
                        self.home_brands.update(brands)
            if index.has_key('newNum'):
                self.new_brandNum = int(index['newNum'])
                print '# new brandNum:', index['newNum']
            if index.has_key('onlineNum'):
                self.hot_brandNum = int(index['onlineNum'])
                print '# online brandNum:', index['onlineNum']
            if index.has_key('totalNum'):
                self.total_brandNum = int(index['totalNum'])
                print '# total brandNum:', index['totalNum']

    # Json List Configuration
    def JsonListConfig(self, brand_json_list, data_type, type_name):
        brand = {}
        i = 0
        for brand_json in brand_json_list: 
            i += 1
            brand_act_id, brand_act_url, brand_act_name = '', '', ''
            # 基本信息
            if brand_json.has_key('baseInfo'):
                b_baseInfo = brand_json['baseInfo']
                if b_baseInfo.has_key('activityId') and b_baseInfo['activityId']:
                    # 品牌团Id
                    brand_act_id = b_baseInfo['activityId']
                if b_baseInfo.has_key('sgChannelUrl') and b_baseInfo['sgChannelUrl']:
                    # 品牌团链接
                    brand_act_url = Common.fix_url(b_baseInfo['sgChannelUrl'])
            if brand_json.has_key('materials'):
                b_materials = brand_json['materials']
                if b_materials.has_key('logoText') and b_materials['logoText']:
                    # 品牌团Name
                    brand_act_name = b_materials['logoText']
            if brand_act_id != '':
                brand[str(brand_act_id)] = {'act_id':brand_act_id,'act_name':brand_act_name,'url':brand_act_url,'position':i,'datatype':data_type,'typename':type_name}
            print data_type, i, brand_act_id, brand_act_url, brand_act_name
        return brand

    # 首页品牌团页面模板3
    def homeBrandTemp3(self, page):
        position = 0
        m1 = re.search(r'<div class="ju-wrapper">.+?<div class="mod-brandbd">\s+<div class="ju-itemlist clearfix".+?<ul class="clearfix">(.+?)</ul>', page, flags=re.S)
        if m1:
            position = self.brandUlList1(m1.group(1),position)
        m2 = re.search(r'<div class="ju-wrapper">.+?<div class="mod-brandbd">.+?<div class="logowall brand-footer clearfix".+?>(.+?)</div>', page, flags=re.S)
        if m2:
            position = self.logoList1(m2.group(1),position)

    # 解析brand UL list
    def brandUlList1(self,page,position=0):
        i = position
        p = re.compile(r'<li class="brand-mid-v2" title="(.+?)".+?>.+?<a.+?href="(.+?)".+?>.+?</a>.+?</li>', flags=re.S)
        for brand_act in p.finditer(page):
            i += 1
            a_val = (Common.fix_url(brand_act.group(2)),brand_act.group(1),i)
            self.parser_actinfo(a_val)
        return i

    # 解析logo list
    def logoList1(self,page,position=0):
        i = position
        p = re.compile(r'<a class="logo".+?href="(.+?)">\s+<img.+?title="(.+?)"/>\s+</a>', flags=re.S)
        for brand_act in p.finditer(page):
            i += 1
            a_val = (Common.fix_url(brand_act.group(1)),brand_act.group(2),i)
            self.parser_actinfo(a_val)
        return i

    # 解析brand活动信息
    def parser_actinfo(self,val):
        brand_act_url,brand_act_name,position = val
        brand_act_id = ''
        m = re.search(r'act_sign_id=(\d+)', brand_act_url, flags=re.S)
        if m:
            brand_act_id = str(m.group(1))
            self.home_brands[str(brand_act_id)] = {'act_id':brand_act_id,'act_name':brand_act_name,'url':brand_act_url,'position':position,'datatype':'home','typename':'首页'}
        else:
            m = re.search(r'minisiteId=(\d+)', brand_act_url, flags=re.S)
            if m:
                brand_act_id = str(m.group(1))
                self.home_brands[str(brand_act_id)] = {'act_id':brand_act_id,'act_name':brand_act_name,'url':brand_act_url,'position':position,'datatype':'home','typename':'首页'}
            else:
                key = brand_act_url.split('?')[0]
                if key.find('brand_items.htm') == -1:
                    self.home_brands[key] = {'act_id':'-1','act_name':brand_act_name,'url':brand_act_url,'position':position,'datatype':'home','typename':'首页'}
                else:
                    print '# home brand not find info: url:%s'%brand_act_url

        print position, brand_act_id, brand_act_url, brand_act_name


if __name__ == '__main__':
    pass
    """
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    ju_home_url = 'http://ju.taobao.com'
    refers = 'http://www.taobao.com'
    # 抓取设置
    #crawler = TBCrawler()
    crawler = RetryCrawler()
    # 获取首页的品牌团
    page = crawler.getData(ju_home_url, refers)
    hb = JHSHomeBrand()
    hb.antPage(page)
    #print hb.home_brands
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    """



