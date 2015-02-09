#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import random
import traceback
import threading
import base.Config as Config
import base.Common as Common
from dial.DialClient import DialClient
from base.MyThread  import MyThread
from JHSBActItem import JHSBActItem
from JHSItem import JHSItem

import warnings
warnings.filterwarnings("ignore")

class JHSBActItemM(MyThread):
    '''A class of jhs activity item thread manager'''
    def __init__(self, jhs_type, thread_num = 15):
        # parent construct
        MyThread.__init__(self, thread_num)

        # thread lock
        self.mutex      = threading.Lock()

        # jhs queue type
        self.jhs_type   = jhs_type # 1:即将上线品牌团频道页,2:检查每天还没结束的活动
        
        # activity items
        self.items      = []

        # dial client
        self.dial_client = DialClient()

        # local ip
        #self._ip = Common.local_ip()
        self._ip = '192.168.1.35'

        # router tag
        self._tag = 'ikuai'

    # To dial router
    def dialRouter(self, _type, _obj):
        try:
            _module = '%s_%s' %(_type, _obj)
            self.dial_client.send((_module, self._ip, self._tag))
        except Exception as e:
            print '# To dial router exception :', e

    def push_back(self, L, v):
        if self.mutex.acquire(1):
            #self.items.append(v)
            L.append(v)
            self.mutex.release()

    def putItem(self, _item):
        self.put_q((0, _item))

    def putItems(self, _items):
        for _item in _items: self.put_q((0, _item))

    # To crawl retry
    def crawlRetry(self, _data):
        _retry, _val = _data
        _retry += 1
        if _retry < Config.crawl_retry:
            _data = (_retry, _val)
            self.put_q(_data)
        else:
            print "# retry too many times, no get item:", _val

    # To crawl item
    def crawl(self):
        while True:
            try:
                # 队列为空，退出
                if self.empty_q(): break

                # 取队列消息
                _data = self.get_q()

                if self.jhs_type == 1:
                    # 品牌团实例
                    # _pageData, _catid, _catname, _position, _begin_date, _begin_hour = _val
                    item = JHSBActItem()

                    # 信息处理
                    _val  = _data[1]
                    item.antPageComing(_val)
                    print '# To crawl coming activity val : ', Common.now_s(), _val[1], _val[2]
                    # 汇聚
                    self.push_back(self.items, item.outSqlForComing())
                elif self.jhs_type == 2:
                    # 品牌团实例
                    # _catid, _catname, _caturl = _val
                    item = JHSBActItem()

                    # 信息处理
                    _val  = _data[1]
                    item.antPageHourcheck(_val)
                    print '# To check activity val : ', Common.now_s(), _val[0], _val[1]
                    # 汇聚
                    self.push_back(self.items, item.outTupleForHourcheck())
                
                    
                # 通知queue, task结束
                self.queue.task_done()

                time.sleep(1)
            except Exception as e:
                # 通知queue, task结束
                self.queue.task_done()

                self.crawlRetry(_data)
                # 重新拨号
                if self.jhs_type == 1 or self.jhs_type == 2:
                    self.dialRouter(4, 'chn')
                #time.sleep(random.uniform(10,30))

                print 'Unknown exception crawl item :', e
                #traceback.print_exc()
                print '#####--Traceback Start--#####'
                tp,val,td = sys.exc_info()
                for file, lineno, function, text in traceback.extract_tb(td):
                    print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                    print text
                print "exception traceback err:%s,%s,%s"%(tp,val,td)
                print '#####--Traceback End--#####'
                time.sleep(1)

if __name__ == '__main__':
    pass

