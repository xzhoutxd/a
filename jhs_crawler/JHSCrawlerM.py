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

class JHSCrawlerM(MyThread):
    '''A class of jhs crawler thread manager'''
    def __init__(self, jhs_type, thread_num = 10):
        # parent construct
        MyThread.__init__(self, thread_num)

        # thread lock
        self.mutex      = threading.Lock()

        # jhs queue type
        self.jhs_type   = jhs_type # 1:品牌团频道页,2:商品页
        
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

    def push_back(self, v):
        if self.mutex.acquire(1):
            #L.append(v)
            self.items.append(v)
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
                else:
                    # 商品实例
                    # _pageData, _actId, _actName, _actUrl, _position, _ju_url, _id, _juId, _juPic_url = _val
                    item = JHSItem()

                # 信息处理
                _val  = _data[1]
                #time.sleep(1)
                item.antPage(_val)
                if self.jhs_type == 1:
                    print '# To crawl activity val : ', Common.now_s(), _val[1], _val[2], _val[3]
                else:
                    print '# To crawl activity item val : ', Common.now_s(), _val[2], _val[4], _val[6]

                # 汇聚
                #self.push_back(self.items, item)
                self.push_back(item.outTuple())

                # 通知queue, task结束
                self.queue.task_done()

            except Common.NoActivityException as e:
                # 通知queue, task结束
                self.queue.task_done()
                print 'Not activity exception :', e

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
                if self.jhs_type == 1:
                    self.dialRouter(4, 'chn')
                else:
                    self.dialRouter(4, 'item')
                #time.sleep(random.uniform(10,30))

                print 'Unknown exception crawl item :', e
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

