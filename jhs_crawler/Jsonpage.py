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
from Queue import Empty
import traceback
import base.Common as Common
import base.Config as Config
from base.TBCrawler import TBCrawler

class Jsonpage():
    '''A class of json page'''
    def __init__(self):
        # 抓取设置
        self.crawler = TBCrawler()
        self.val_queue = Queue.Queue()

    def putVal(self, _val):
        self.val_queue.put((0,_val),block=False)

    def putVals(self, _vals):
        for _val in _vals: self.val_queue.put((0, _val),block=False)

    # To crawl retry
    def crawlRetry(self, _data):
        if not _data: return
        _retry, _val = _data
        _retry += 1
        if _retry < Config.json_crawl_retry:
            _data = (_retry, _val)
            self.val_queue.put(_data,block=False)
        else:
            print "# retry too many times, no get json:", _val

    def get_json(self, json_valList):
        bResult_list = []
        if json_valList and json_valList != []:
            self.putVals(json_valList)
            while True:
                _data = None
                try:
                    try:
                        # 取队列消息
                        _data = self.val_queue.get(block=False)
                    except Empty as e:
                        break
                    _val = _data[1]
                    b_url, refers, a_val = _val
                    bResult_list += self.get_jsonPage(b_url,refers,a_val)
                    # 通知queue, task结束
                    self.val_queue.task_done()
                except Common.InvalidPageException as e:
                    print '# Invalid page exception:',e
                    # 通知queue, task结束
                    self.val_queue.task_done()
                    self.crawlRetry(_data)
                except Common.DenypageException as e:
                    print '# Deny page exception:',e
                    # 通知queue, task结束
                    self.val_queue.task_done()
                    self.crawlRetry(_data)
                    time.sleep(60)
                except Common.SystemBusyException as e:
                    print '# System busy exception:',e
                    # 通知queue, task结束
                    self.val_queue.task_done()
                    self.crawlRetry(_data)
        return bResult_list

    # 通过数据接口获取每一页的数据
    def get_jsonPage(self, url, refers='', a_val=()):
        bResult_list = []
        ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
        p_url = url + '&_ksTS=%s'%ts
        #print p_url
        result = self.get_jsonData(p_url, refers)
        bResult_list.append((result,)+a_val)
        # 分页从接口中获取数据
        totalPage = 1
        if type(result) is dict and result.has_key('totalPage'):
            totalPage = int(result['totalPage'])
        elif type(result) is str:
            m = re.search(r'"totalPage":(\d+),', result, flags=re.S)
            if m:
                totalPage = int(m.group(1))
        if totalPage > 1:
            for page_i in range(2, totalPage+1):
                ts = str(int(time.time()*1000)) + '_' + str(random.randint(0,9999))
                p_url = re.sub('page=\d+&', 'page=%d&'%page_i, p_url)
                p_url = re.sub('&_ksTS=\d+_\d+', '&_ksTS=%s'%ts, p_url)
                #print p_url
                result = self.get_jsonData(p_url, refers)
                if result:
                    bResult_list.append((result,)+a_val)

        return bResult_list

    # 获取每一页数据
    def get_jsonData(self, url, refers=''):
        result = None
        b_page = self.crawler.getData(url, refers)
        if not b_page or b_page == '': raise Common.InvalidPageException("# Jsonpage get_jsonData: not get jsondata url:%s."%(url))
        try:
            b_page = re.sub('^]', '', b_page)
            result = json.loads(b_page)
        except Exception as e:
            print '# exception err in get_jsonData load json:',e
            print '# return string:',b_page
            return b_page
        return result

    # 解析每一页的数据
    def parser_brandjson(self, bResult_list, a_val=None):
        print '# brand activities start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # 获取多线程需要的字段val
        act_valList = []
        # 前一页的数据量,用于计算活动所在的位置
        prepage_count = 0
        for page in bResult_list:
            page_info = page[0]
            activities = []
            currentPage = 1
            if type(page_info) is dict and page_info.has_key('brandList') and page_info['brandList'] != []:
                activities = page_info['brandList']
                if page_info.has_key('currentPage'):
                    currentPage = int(page_info['currentPage'])
            elif type(page_info) is str:
                m = re.search(r'"brandList":\[(.+?}})\]', page_info, flags=re.S)
                if m:
                    brandlist_info = m.group(1)
                    p = re.compile(r'({"baseInfo":.+?}})')
                    for brand_info in p.finditer(brandlist_info):
                        brand = brand_info.group(1)
                        activities.append(brand)
                m = re.search(r'"currentPage":(\d+),', page_info, flags=re.S)
                if m:
                    currentPage = int(m.group(1))
            print '# brand every page num:',len(activities)

            b_position_start = 0
            if currentPage > 1:
                b_position_start = (currentPage - 1) * prepage_count
            else:
                # 保存前一页的数据条数
                prepage_count = len(activities)

            for i in range(0,len(activities)):
                activity = activities[i]
                if a_val:
                    val = (activity, page[2], page[1], (b_position_start+i+1)) + a_val
                else:
                    val = (activity, page[2], page[1], (b_position_start+i+1))
                act_valList.append(val)
        print '# brand activities end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return act_valList
    
    def traceback_log(self):
        print '#####--Traceback Start--#####'
        tp,val,td = sys.exc_info()
        for file, lineno, function, text in traceback.extract_tb(td):
            print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
            print text
        print "exception traceback err:%s,%s,%s"%(tp,val,td)
        print '#####--Traceback End--#####'


if __name__ == '__main__':
    pass
