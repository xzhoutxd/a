#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import base.Common as Common
import base.Config as Config
from base.RetryCrawler import RetryCrawler
from Jsonpage import Jsonpage
from JHSGroupItemWorker import JHSGroupItemWorker
from JHSGroupItemM import JHSGroupItemParserM
from JHSGroupItemM import JHSGroupItemCrawlerM

class JHSGroupItem():
    '''A class of JHS group item channel'''
    def __init__(self):
        # 抓取设置
        self.crawler = RetryCrawler()

        # 获取Json数据
        self.jsonpage = Jsonpage()

        # 
        self.worker = JHSGroupItemWorker()

        # 首页
        self.home_url   = 'http://ju.taobao.com'
        self.refers     = 'http://www.tmall.com'

        # 频道
        self.today_url  = 'http://ju.taobao.com/tg/today_items.htm?type=0' # 商品团

        # 默认类别
        self.category_list = [("http://ju.taobao.com/jusp/nvzhuangpindao/tp.htm#J_FixedNav","女装","1000")]
        """
        self.category_list = [
                ("http://ju.taobao.com/jusp/nvzhuangpindao/tp.htm#J_FixedNav","女装","1000"),
                ("http://ju.taobao.com/jusp/nanzhuangpindao/tp.htm#J_FixedNav","男装","7000"),
                ("http://ju.taobao.com/jusp/xiebaopindao/tp.htm#J_FixedNav","鞋包","3000"),
                ("http://ju.taobao.com/jusp/neiyipindao/tp.htm#J_FixedNav","内衣","4000"),
                ("http://ju.taobao.com/jusp/zhubaoshipin/tp.htm#J_FixedNav","饰品","42000"),
                ("http://ju.taobao.com/jusp/yundongpindao/tp.htm#J_FixedNav","运动","38000"),
                ("http://ju.taobao.com/jusp/meizhuangpindao/tp.htm#J_FixedNav","美妆","2000"),
                ("http://ju.taobao.com/jusp/tongzhuangpindao/tp.htm#J_FixedNav","童装","23000"),
                ("http://ju.taobao.com/jusp/shipinpindao/tp.htm#J_FixedNav","零食","5000"),
                ("http://ju.taobao.com/jusp/muyingpindao/tp.htm#J_FixedNav","母婴","6000"),
                ("http://ju.taobao.com/jusp/baihuopindao/tp.htm#J_FixedNav","百货","37000"),
                ("http://ju.taobao.com/jusp/chepinpindao/tp.htm#J_FixedNav","汽车","36000"),
                ("http://ju.taobao.com/jusp/jiadianpindao/tp.htm#J_FixedNav","家电","34000"),
                ("http://ju.taobao.com/jusp/shumapindao/tp.htm#J_FixedNav","数码","43000"),
                ("http://ju.taobao.com/jusp/jiajunewpindao/tp.htm#J_FixedNav","家装","225000"),
                ("http://ju.taobao.com/jusp/jiajupindao/tp.htm#J_FixedNav","家纺","35000")
                ]
        """

        # 页面
        self.site_page  = None

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

    #
    def antPage(self):
        category_list = self.category_list
        ajax_url_list = []
        for category_val in category_list:
            c_url,c_name,c_id = category_val
            page = self.crawler.getData(c_url, self.today_url)
            page_val = (page,c_name,c_id)
            ajax_url_list = self.getAjaxurlList(page_val,c_url)


        all_item_val = []
        other_item_val = []
        coming_item_val = []

        item_list = []
        # process ajax url list
        item_json_index = 0
        item_soldout_num = 0
        for a_url in ajax_url_list:
            # get json from ajax url
            Result_list = self.jsonpage.get_json([a_url])
            item_result_list = []
            act_result_list = []
            if Result_list and len(Result_list) > 0:
                for result_val in Result_list:
                    result = result_val[0]
                    a_val = result_val[1:]
                    if type(result) is dict and result.has_key('itemList'):
                        item_result_list.append((result,a_val))
                    elif type(result) is str:
                        m = re.search(r'"itemList":\[(.+?}})\]', result, flags=re.S)
                        if m:
                            item_result_list.append((result,a_val))
                        else:
                            m = re.search(r'"brandList":\[(.+?}})\]', result, flags=re.S)
                            if m:
                                act_result_list.append((result,a_val))
                            else:
                                print '# not know the type of the result:',result
                    elif type(result) is dict and result.has_key('brandList'):
                        act_result_list.append((result,a_val))
                    else:
                        print '# not know the type of the result:',result
                # parser item result
                item_result_valList = []
                if len(item_result_list) > 0:
                    item_json_index += 1
                    item_result_valList = self.jsonpage.parser_itemjson(item_result_list)
                # the first item list is all online items
                if item_json_index == 1:
                    if len(item_result_list) > 0:
                        all_item_val = item_result_valList
                else:
                    for item_val in item_result_valList:
                        item_info, a_val = item_val
                        item_list.append((item_info,) + a_val)
        print '# all items num:',len(all_item_val)

        # parser group item data json list
        itemparse_type = 'm'
        # 附加信息
        a_val = (self.begin_time,)
        items = self.parseItems(item_list,itemparse_type,a_val)

        # crawl new item data info
        result_items = []
        for item in items:
            item_status, item_val, o_val = item
            item_juid = item_val[1]
            result_items.append({"item_juId":str(item_juid),"val":o_val})

        new_item_list = self.worker.selectNewItems(result_items)
        print '# new items num:',len(new_item_list)
        itemcrawl_type = 'i'
        # 附加信息
        a_val = (self.begin_time,)
        items = self.crawlNewItems(new_item_list,itemcrawl_type,a_val)

        # 保存item信息到Redis
        new_items = []
        for item in items:
            iteminfoSql = item
            crawling_time,item_juid,item_groupCatId,item_groupCatName,item_ju_url,item_juName,item_id,start_time,end_time = iteminfoSql[0],iteminfoSql[1],iteminfoSql[2],iteminfoSql[3],iteminfoSql[6],iteminfoSql[8],iteminfoSql[10],iteminfoSql[23],iteminfoSql[24]
            item_val = {"item_juId":item_juid,"crawling_time":crawling_time,"item_groupCatId":item_groupCatId,"item_groupCatName":item_groupCatName,"item_ju_url":item_ju_url,"item_juName":item_juName,"item_id":item_id,"start_time":start_time,"end_time":end_time}
            new_items.append({"item_juId":item_juid,"val":item_val})
        self.worker.putItemDB(new_items)

        # 删除结束商品
        self.worker.scanEndItems()

    # 解析从接口中获取的商品数据
    def parseItems(self, item_list, itemparse_type, a_val):
        print '# parse Group Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        # 多线程 控制并发的线程数
        max_th = Config.item_max_th
        if len(item_list) > max_th:
            m_itemsObj = JHSGroupItemParserM(itemparse_type, max_th, a_val)
        else:
            m_itemsObj = JHSGroupItemParserM(itemparse_type, len(item_list), a_val)
        m_itemsObj.createthread()
        m_itemsObj.putItems(item_list)
        m_itemsObj.run()

        _items = m_itemsObj.items
        print '# parse item num:',len(_items)
        print '# parse Group Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return _items

    # 抓取新上的商品详情
    def crawlNewItems(self, _new_items, itemcrawl_type, a_val):
        print '# crawl Group Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 多线程 控制并发的线程数
        max_th = Config.item_max_th
        if len(_new_items) > max_th:
            m_itemsObj = JHSGroupItemCrawlerM(itemcrawl_type, max_th, a_val)
        else:
            m_itemsObj = JHSGroupItemCrawlerM(itemcrawl_type, len(_new_items), a_val)
        m_itemsObj.createthread()
        m_itemsObj.putItems(_new_items)
        m_itemsObj.run()

        _items = m_itemsObj.items
        print '# insert new item num:',len(_items)
        print '# crawl Group Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return _items
 
    # 商品团频道
    def categoryListTEMP(self):
        page = self.crawler.getData(self.today_url, self.home_url)
        if not page or page == '': print '# not get today page'
        category_list = []
        m = re.search(r'<div class="J_CatLeft layout-left">.+?<table>(.+?)</table>.+?</div>',page,flags=re.S)
        if m:
            category_list = self.categoryListType1(m.group(1))
        else:
            m = re.search(r'<div class="catbg">\s+<div class="ju-wrapper">\s+<div class="cat-menu-h".+?>.+?<ul class="clearfix">(.+?)</ul>',page,flags=re.S)

            if m:
                category_list = self.categoryListType2(m.group(1))

        return category_list

    def categoryListType1(self,page):
        category_list = []
        m = re.search(r'<tr class="h2">.+?</tr>(.+?)<tr class="h2">',page,flags=re.S)
        if m:
            cate_list = m.group(1)
            p = re.compile(r'<a.+?href="(.+?)".+?>(.+?)</a>',flags=re.S)
            for cate in p.finditer(cate_list):
                category_list.append((cate.group(1),cate.group(2).strip()))
        return category_list
    
    def categoryListType2(self,page):
        category_list = []
        p = re.compile(r'<a.+?href="(.+?)".+?>(.+?)</a>',flags=re.S)
        for cate in p.finditer(page):
            category_list.append((cate.group(1),cate.group(2).strip()))
        return category_list

    def getAjaxurlList(self,page_val,refers):
        url_list = []
        page, c_name, c_id = page_val
        p = re.compile(r'<.+?data-ajaxurl="(.+?)".+?>(.+?)</div>',flags=re.S)
        i = 0
        for a_info in p.finditer(page):
            c_subNav = c_name
            a_url = a_info.group(1).replace('amp;','')
            info = a_info.group(2)
            m = re.search(r'<span class="l-f-tbox">(.+?)</span>',info,flags=re.S)
            if m:
                c_subNav = m.group(1).strip()
            a_val = (c_id,c_name,refers,c_subNav)
            url_list.append((a_url,refers,a_val))
            i += 1
        return url_list


if __name__ == '__main__':
    j = JHSGroupItem()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    j.antPage()
    print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
