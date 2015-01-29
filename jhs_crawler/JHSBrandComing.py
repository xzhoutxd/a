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

class JHSBrandComing():
    '''A class of brand Item'''
    def __init__(self):
        # mysql
        self.mysqlAccess = MysqlAccess()

        # 抓取设置
        self.crawler    = TBCrawler()

        # 商品抓取队列
        self.item_queue = Queue.Queue()

        # 首页
        self.ju_home_url   = 'http://ju.taobao.com'

        # 品牌团页面
        self.brand_url  = 'http://ju.taobao.com/tg/brand.htm'

        # 首页的品牌团列表
        self.home_brands = {}
        self.home_brands_list = []

        # 品牌团页面
        self.brandcoming_page_url = 'http://ju.taobao.com/json/tg/ajaxGetBrandsV2.json?psize=60&btypes=1%2C2&showType=1'

        # 页面信息
        self.ju_brand_page = '' # 聚划算品牌团页面

        # 抓取开始时间
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

    def antPage(self):
        # 获取品牌团列表页数据
        page = self.crawler.getData(self.brand_url, self.ju_home_url)
        self.activityListForComing(page) 

    def activityListForComing(self, page):
        if not page or page == '': return

        self.ju_brand_page = page
        # 从接口中获取的数据列表
        bResult_list = []
        #print page
        m = re.search(r'<div.+?data-catid=\'(\d+)\' data-forecast="true">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', page, flags=re.S)
        if m:
            print m.group(1)

        # 分类按接口获取即将上线json
        p = re.compile(r'<div.+?data-catid=\'(\d+)\' data-forecast="true">\s+<div class="f-sub-floor">\s+<span>(.+?)</span>\s+</div>', flags=re.S)
        for activity_floor in p.finditer(page):
            f_name, f_catid, f_activitySignId = '', '', ''
            f_catid, f_name = activity_floor.group(1), activity_floor.group(2)

            print '# Coming activity floor:', f_name, f_catid, f_activitySignId
            i = 1
            ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
            if f_catid != '':
                b_url = self.brandcoming_page_url + '&page=%d'%i + '&frontCatIds=%s'%f_catid + '&_ksTS=%s'%ts
                b_page = self.crawler.getData(b_url, Config.ju_brand_home)
            try:
                result = json.loads(b_page)
                print b_url
                bResult_list.append([result,f_name,f_catid])
                # 分页从接口中获取数据
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

        act_valList = []
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
                    activity = activities[i]
                    act_valList.append((activity, page[2], page[1], (b_position_start+i+1), self.begin_date, self.begin_hour))

        if len(act_valList) > 0:
            # 多线程爬取即将上线活动
            m_Obj = JHSBActItemM(1)
            m_Obj.putItems(act_valList)
            m_Obj.createthread()
            m_Obj.run()
            while True:
                try:
                    if m_Obj.empty_q():
                        item_list = m_Obj.items
                        for item in item_list:
                            self.mysqlAccess.insertJhsActComing(item.outSqlForComing())
                            #print item.outSqlForComing()
                        print '# Activity List End'
                        break
                except Exception as e:
                    print 'Unknown exception crawl item :', e
                    traceback.print_exc()
                    break
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        print '# brand activity coming soon num:', len(act_valList)

if __name__ == '__main__':
    pass
#    actId, actName, actUrl = '4790221', '四大徽茶国礼茶', 'http://act.ju.taobao.com/market/sidahuicha.php'
#    B = JHSBrand()
#    B.activityItems(actId, actName, actUrl)



