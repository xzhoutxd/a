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
from JHSItem import JHSItem

import warnings
warnings.filterwarnings("ignore")

class JHSItemM(MyThread):
    '''A class of jhs item thread manager'''
    def __init__(self, jhs_type, thread_num = 10):
        # parent construct
        MyThread.__init__(self, thread_num)

        # thread lock
        self.mutex      = threading.Lock()

        # jhs queue type
        self.jhs_type   = jhs_type # 1:每天一次的商品, 2:每小时一次的商品
        
        # activity items
        self.items      = []

        # dial client
        self.dial_client = DialClient()

        # local ip
        #self._ip = Common.local_ip()
        self._ip = '192.168.1.35'

        # router tag
        self._tag = 'ikuai'

        # give up item, retry too many times
        self.giveup_items = []

    # To dial router
    def dialRouter(self, _type, _obj):
        try:
            _module = '%s_%s' %(_type, _obj)
            self.dial_client.send((_module, self._ip, self._tag))
        except Exception as e:
            print '# To dial router exception :', e

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
        if not _data: return
        _retry, _val = _data
        _retry += 1
        if _retry < Config.crawl_retry:
            _data = (_retry, _val)
            self.put_q(_data)
        else:
            self.push_back(self.giveup_items, _val)
            print "# retry too many times, no get item:", _val

    # To crawl item
    def crawl(self):
        while True:
            _data = None
            try:
                try:
                    # 取队列消息
                    _data = self.get_q()
                except Empty as e:
                    # 队列为空，退出
                    #print '# queue is empty', e
                    break

                # 商品实例
                item = JHSItem()

                # 信息处理
                _val  = _data[1]
                if self.jhs_type == 1:
                    # 每天一次商品实例
                    # _juid,act_id,act_name,act_url,_juname,_ju_url,_id,_url,_oriprice,_actprice = _val
                    item.antPageDay(_val)
                    print '# Day To crawl activity item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    # 汇聚
                    self.push_back(self.items, item.outTupleDay())
                else:
                    # 每小时一次商品实例
                    # _juid,act_id,act_name,act_url,_juname,_ju_url,_id,_url,_oriprice,_actprice = _val
                    item.antPageHour(_val)
                    print '# Hour To crawl activity item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    # 汇聚
                    self.push_back(self.items, item.outUpdateTupleHour())

                # 通知queue, task结束
                self.queue.task_done()

            except Common.NoItemException as e:
                # 通知queue, task结束
                self.queue.task_done()
                print 'Not item exception :', e

            except Common.NoPageException as e:
                # 通知queue, task结束
                self.queue.task_done()
                print 'Not page exception :', e

            except Common.InvalidPageException as e:
                # 通知queue, task结束
                self.queue.task_done()

                self.crawlRetry(_data)
                print 'Invalid page exception :', e

            except Exception as e:
                # 通知queue, task结束
                self.queue.task_done()

                self.crawlRetry(_data)
                # 重新拨号
                self.dialRouter(4, 'item')

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
                #time.sleep((_data[0]+1)*random.uniform(10,30))

if __name__ == '__main__':
    pass

