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
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler
from base.RetryCrawler import RetryCrawler
from Jsonpage import Jsonpage
from JHSGroupItemM import JHSGroupItemParserM
from JHSGroupItemM import JHSGroupItemCrawlerM
sys.path.append('../db')
from RedisQueue  import RedisQueue

class JHSGroupItemCatQ():
    '''A class of jhs groupitem category redis queue'''
    def __init__(self,itemtype='groupitemcat',q_type='h'):
        self.jhs_type    = Config.JHS_TYPE   # queue type
        self.item_type   = itemtype          # task type
        # jhs queue type
        self.jhs_queue_type = q_type     # h:每小时
        # queue key
        self._key = '%s_%s_%s' % (self.jhs_type,self.item_type,self.jhs_queue_type)
        # DB
        self.redisQueue  = RedisQueue()      # redis queue

        # result
        self.items = []

        # give up item, retry too many times
        self.giveup_items = []

        # 抓取设置
        #self.crawler = RetryCrawler()
        self.crawler = TBCrawler()

        # 获取Json数据
        self.jsonpage = Jsonpage()

        # 抓取开始时间
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

    # clear item queue
    def clearItemQ(self):
        self.redisQueue.clear_q(self._key)

    # 写入redis queue
    def putItemQ(self, _msg):
        _data = (0, _msg)
        self.redisQueue.put_q(self._key, _data)

    # 转换msg
    def putItemlistQ(self, item_list):
        for _item in item_list:
            msg = _item
            self.putItemQ(msg)

    def push_back_list(self, L, v):
        L.extend(v)

    def push_back_val(self, L, v):
        L.append(v)

    # To crawl retry
    def crawlRetry(self, _data):
        if not _data: return
        _retry, _val = _data
        _retry += 1
        if _retry < Config.home_crawl_retry:
            _data = (_retry, _val)
            self.redisQueue.put_q(self._key, _data)
        else:
            self.push_back_val(self.giveup_items, _val)
            print "# retry too many times, no get info:", _val

    def run_category(self, category_val, refers=''):
        c_url,c_name,c_id = category_val
        print c_url,c_name,c_id
        page = self.crawler.getData(c_url, refers)
        page_val = (page,c_name,c_id)
        ajax_url_list = self.getAjaxurlList(page_val,c_url)
        if len(ajax_url_list) > 0:
            self.get_jsonitems(ajax_url_list)

    # get json ajax url
    def getAjaxurlList(self, page_val, refers=''):
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

    # get item json list in category page from ajax url
    def get_jsonitems(self, ajax_url_list):
        # today all items val
        todayall_item_val = []
        # other sub nav items val
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
                        todayall_item_val = item_result_valList
                else:
                    for item_val in item_result_valList:
                        item_info, a_val = item_val
                        item_list.append((item_info,) + a_val)
        if len(item_list) > 0:
            self.process_items(item_list)

    # parse item list and crawl new items
    def process_items(self, item_list):
        # 解析商品列表
        itemparse_type = 'm'
        # 附加信息
        a_val = (self.begin_time,)
        self.parseItems(item_list,itemparse_type,a_val)

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
        self.push_back_list(self.items,_items)
        print '# queue item num:',len(self.items)
        print '# parse item num:',len(_items)
        print '# parse Group Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 返回数据

    def catQ(self, refers=''):
        i, M = 0, 10
        n = 0
        while True: 
            try:
                _data = self.redisQueue.get_q(self._key)

                # 队列为空
                if not _data:
                    #print '# all get catQ item num:',n
                    #print '# not get catQ of key:',self._key
                    #break
                    i += 1
                    if i > M:
                        print '# all get catQ item num:',n
                        print '# not get catQ of key:',self._key
                        break
                    time.sleep(10)
                    continue
                n += 1
                category_val = _data[1]
                self.run_category(category_val, refers)

            except Exception as e:
                print 'Unknown exception:', e
                print Common.traceback_log()

                self.crawlRetry(_data)
                time.sleep(random.uniform(10,30))

