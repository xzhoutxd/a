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
from JHSCrawlerM import JHSCrawlerM
from JHSHomeBrand import JHSHomeBrand

class JHSBrandMarketing():
    '''A class of brand marketing'''
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

        # 品牌团页面的最上面推广位
        self.top_brands = {}

        # 品牌团页面
        # 模板1 数据接口URL
        self.brand_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=0'

        # 页面信息
        self.ju_home_page = '' # 聚划算首页
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

        # 抓取间隔
        self.gap_num = 50

        # 并发线程值
        self.act_max_th = 5 # 活动抓取时的最大线程

    def antPage(self):
        retry = 0
        while True:
            try:
                # 获取首页的品牌团
                page = self.crawler.getData(self.ju_home_url, self.refers)
                hb = JHSHomeBrand()
                hb.antPage(page)
                self.home_brands = hb.home_brands
                break
            except Common.InvalidPageException as e:
                if retry >= Config.home_crawl_retry:
                    break
                retry += 1
                print '# Invalid page exception:',e
            except Common.DenypageException as e:
                if retry >= Config.home_crawl_retry:
                    break
                retry += 1
                print '# Deny page exception:',e
            except Exception as e:
                print '# exception err in antPage info:',e
                break
        print '# home activities:', self.home_brands

        retry = 0
        while True:
            try:
                # 获取品牌团列表页数据
                page = self.crawler.getData(self.brand_url, self.ju_home_url)
                self.activityList(page) 
                break
            except Common.InvalidPageException as e:
                if retry >= Config.home_crawl_retry:
                    break
                retry += 1
                print '# Invalid page exception:',e
            except Common.DenypageException as e:
                if retry >= Config.home_crawl_retry:
                    break
                retry += 1
                print '# Deny page exception:',e
            except Exception as e:
                print '# exception err in antPage info:',e
                break

    # 品牌团列表
    def activityList(self, page):
        if not page or page == '': raise Common.InvalidPageException("# brand activityList: not get JHS brand home.")
        self.ju_brand_page = page
        # 数据接口URL list
        b_url_valList = []
        # 模板1
        m = re.search(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', page, flags=re.S)
        if m:
            b_url_valList = self.activityListTemp1(page)
        else:
            # 模板2
            m = re.search(r'<div id="(\d+)" class="l-floor J_Floor placeholder ju-wrapper" data-ajax="(.+?)">\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>', page, flags=re.S)
            if m:
                b_url_valList = self.activityListTemp2(page)
            else:
                print '# err: not matching all templates.'

        if b_url_valList != []:
            # 从接口中获取的数据列表
            bResult_list = []
            for b_url_val in b_url_valList:
                bResult_list += self.get_jsonData(b_url_val)

            activity_list = []
            if bResult_list and bResult_list != []:
                activity_list = self.parser_activities(bResult_list)

            print '# top activities:', self.top_brands
            print '# all activities:', activity_list
        else:
            print '# err: not find activity json data URL list.'

    # 品牌团页面模板1
    def activityListTemp1(self, page):
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div id="floor\d+" class="l-floor J_Floor placeholder ju-wrapper" (.+?)>.+?</div>', flags=re.S)
        for floor in p.finditer(page):
            floor_info = floor.group(1)
            f_name, f_catid, f_activitySignId = '', '', ''
            m = re.search(r'data-floorName="(.+?)"\s+', floor_info, flags=re.S)
            if m:
                f_name = m.group(1)

            m = re.search(r'data-catid=\'(.+?)\'\s+', floor_info, flags=re.S)
            if m:
                f_catid = m.group(1)

            m = re.search(r'data-activitySignId=\"(.+?)\"$', floor_info, flags=re.S)
            if m:
                f_activitySignId = m.group(1)

            begin_page = 1
            if f_activitySignId != '':
                f_url = self.brand_page_url + '&page=%d'%begin_page + '&activitySignId=%s'%f_activitySignId.replace(',','%2C') + '&stype=ids'
                print '# brand activity floor: %s activitySignIds: %s, url: %s'%(f_name, f_activitySignId, f_url)
                act_ids = f_activitySignId.split(',')
                i = 1
                for act_id in act_ids:
                    if not self.top_brands.has_key(str(act_id)):
                        self.top_brands[str(act_id)] = {'position':i,'datatype':f_name}
                    i += 1
            else:
                f_url = self.brand_page_url + '&page=%d'%begin_page + '&frontCatIds=%s'%f_catid
                print '# brand activity floor:', f_name, f_catid, f_url
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 品牌团页面模板2
    def activityListTemp2(self, page):
        # 推荐
        m = re.search(r'<div id="todayBrand".+?>\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>.+?<div class="ju-itemlist">\s+<ul class="clearfix J_BrandList" data-spm="floor1">(.+?)</ul>', page, flags=re.S)
        if m:
            f_name, brand_list = m.group(1), m.group(2)
            today_i = 0
            p = re.compile(r'<li class="brand-mid-v2".+?>.+?<a.+?href="(.+?)".+?>.+?</li>', flags=re.S)
            for act in p.finditer(brand_list):
                act_url = act.group(1)
                act_id = ''
                today_i += 1
                m = re.search(r'act_sign_id=(\d+)', act_url, flags=re.S)
                if m:
                    act_id = m.group(1)
                print '# top brand: position:%s,id:%s,url:%s'%(str(today_i),str(act_id),act_url)
                if not self.top_brands.has_key(str(act_id)):
                    self.top_brands[str(act_id)] = {'position':today_i,'url':act_url,'datatype':f_name}
        # 获取数据接口的URL
        url_valList = []
        p = re.compile(r'<div id="(\d+)" class="l-floor J_Floor placeholder ju-wrapper" data-ajax="(.+?)">\s+<div class="l-f-title">\s+<div class="l-f-tbox">(.+?)</div>', flags=re.S)
        for floor in p.finditer(page):
            f_name, f_catid, f_url, f_activitySignId = '', '', '', ''
            f_catid, f_url, f_name = floor.group(1), floor.group(2), floor.group(3)
            if f_url != '':
                print '# brand activity floor:', f_name, f_catid, f_url
                url_valList.append((f_url, f_name, f_catid))
        return url_valList

    # 通过数据接口获取每一页的数据
    def get_jsonData(self, val):
        bResult_list = []
        try:
            b_url, f_name, f_catid = val
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            b_url = b_url + '&_ksTS=%s'%ts
            b_page = self.crawler.getData(b_url, Config.ju_brand_home)
            result = json.loads(b_page)
            #print b_url
            bResult_list.append([result,f_name,f_catid])
            # 分页从接口中获取数据
            if result.has_key('totalPage') and int(result['totalPage']) > 1:
                for page_i in range(2, int(result['totalPage'])+1):
                    ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                    b_url = re.sub('&page=\d+&', '&page=%d&'%page_i, b_url)
                    b_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, b_url)
                    b_page = self.crawler.getData(b_url, Config.ju_brand_home)
                    result = json.loads(b_page)
                    #print b_url
                    bResult_list.append([result, f_name, f_catid])
        except Exception as e:
            print '# exception err in get_jsonData info:',e

        return bResult_list

    # 解析每一页的数据
    def parser_activities(self, bResult_list):
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 获取多线程需要的字段val
        act_valList = []
        # 前一页的数据量,用于计算活动所在的位置
        prepage_count = 0
        for page in bResult_list:
            i_page = page[0]
            if i_page.has_key('brandList') and i_page['brandList'] != []:
                activities = i_page['brandList']
                b_position_start = 0
                if i_page.has_key('currentPage') and int(i_page['currentPage']) > 1:
                    # 每页取60条数据 ###需要修改（60）###
                    #b_position_start = (int(i_page['currentPage']) - 1) * 60
                    b_position_start = (int(i_page['currentPage']) - 1) * prepage_count
                else:
                    # 保存前一页的数据条数
                    prepage_count = len(activities)
                print '# brand every page num:',len(activities)
                for i in range(0,len(activities)):
                    activity = activities[i]
                    val = (activity, page[2], page[1], (b_position_start+i+1))
                    act_valList.append(val)

        return act_valList

    def traceback_log(self):
        print '#####--Traceback Start--#####'
        tp,val,td = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(td):
            print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
            print text
        print "exception traceback err:%s,%s,%s"%(tp,val,td)
        print '#####--Traceback End--#####'

    def crawler_data(self,url,refer):
        retry = 0
        while True:
            try:
                page = self.crawler.getData(url, refer)
                break
            except Common.InvalidPageException as e:
                if retry >= Config.home_crawl_retry:
                    break
                retry += 1
                print '# Invalid page exception:',e
                time.sleep(2)
            except Common.DenypageException as e:
                if retry >= Config.home_crawl_retry:
                    break
                retry += 1
                print '# Deny page exception:',e
                time.sleep(2)
            except Exception as e:
                print '# exception err in crawler_data info:',e
                break
        return page


if __name__ == '__main__':
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    b = JHSBrandMarketing()
    b.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


