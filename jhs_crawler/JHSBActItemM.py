#-*- coding:utf-8 -*-
#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import time
import random
import traceback
import threading
import base.Config as Config
import base.Common as Common
from base.MyThread  import MyThread
from JHSBActItem import JHSBActItem

import warnings
warnings.filterwarnings("ignore")

class JHSBActItemM(MyThread):
    '''A class of jhs item thread manager'''
    def __init__(self, thread_num = 20):
        # parent construct
        MyThread.__init__(self, thread_num)

        # thread lock
        self.mutex      = threading.Lock()

        # jhs queue type
        self.jhs_type   = Config.JUHUASUAN_TYPE
        
        # activity items
        self.items      = []

    def push_back(self, L, v):
        if self.mutex.acquire(1):
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

    # To crawl item
    def crawl(self):
        while True:
            try:
                # 队列为空，退出
                if self.empty_q(): break

                # 取队列消息
                _data = self.get_q()

                # 商品实例
                item = JHSBActItem()

                # 商品信息处理
                # _i_id, a_id, i_wh, _a_id, _i_wh, a_platform, a_name = _val
                _val  = _data[1]
                time.sleep(1)
                item.antPage(_val)
                print '# To crawl activity item val : ', Common.now_s(), _val[1], _val[2], _val[3]

                # 汇聚商品
                self.push_back(self.items, item)

                # 通知queue, task结束
                self.queue.task_done()

            except Exception as e:
                self.crawlRetry(_data)
                time.sleep(random.uniform(1,10))

                print 'Unknown exception crawl item :', e
                traceback.print_exc()

if __name__ == '__main__':
    pass

