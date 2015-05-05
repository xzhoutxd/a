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
from Queue import Empty
from db.MysqlAccess import MysqlAccess
from JHSItem import JHSItem
sys.path.append('../db')
from RedisAccess import RedisAccess
from MongoAccess import MongoAccess

import warnings
warnings.filterwarnings("ignore")

class JHSGroupItemCrawlerM(MyThread):
    '''A class of jhs item thread manager'''
    def __init__(self, jhs_type, thread_num=10, a_val=None):
        # parent construct
        MyThread.__init__(self, thread_num)

        # thread lock
        self.mutex = threading.Lock()

        # db
        self.mysqlAccess = MysqlAccess() # mysql access
        self.mongoAccess = MongoAccess() # mongodb access

        # jhs queue type
        self.jhs_type = jhs_type # h:每小时, i:商品信息详情

        # appendix val
        self.a_val = a_val
        
        # activity items
        self.items = []

        # dial client
        self.dial_client = DialClient()

        # local ip
        self._ip = Common.local_ip()

        # router tag
        self._tag = 'ikuai'
        #self._tag = 'tpent'

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

    # insert item info
    def insertIteminfo(self, iteminfosql_list, f=False):
        if f or len(iteminfosql_list) >= Config.item_max_arg:
            if len(iteminfosql_list) > 0:
                self.mysqlAccess.insertJhsGroupItemInfo(iteminfosql_list)
                #print '# insert data to database'
            return True
        return False

    # insert item hour
    def insertItemhour(self, itemhoursql_list, f=False):
        if f or len(itemhoursql_list) >= Config.item_max_arg:
            if len(itemhoursql_list) > 0:
                self.mysqlAccess.insertJhsGroupItemForHour(itemhoursql_list)
                #print '# insert hour data to database'
            return True
        return False

    # insert item coming
    def insertItemComing(self, itemsql_list, f=False):
        if f or len(itemsql_list) >= Config.item_max_arg:
            if len(itemsql_list) > 0:
                self.mysqlAccess.insertJhsGroupItemComing(itemsql_list)
                #print '# insert item coming data to database'
            return True
        return False

    # insert item position
    def insertItemPosition(self, itemsql_list, f=False):
        if f or len(itemsql_list) >= Config.item_max_arg:
            if len(itemsql_list) > 0:
                self.mysqlAccess.insertJhsGroupItemPosition(itemsql_list)
                #print '# insert position data to database'
            return True
        return False

    # To crawl item
    def crawl(self):
        # item sql list
        _iteminfosql_list = []
        _itemhoursql_list = []
        _itemcomingsql_list = []
        _itempositionsql_list = []
        while True:
            _data = None
            try:
                try:
                    # 取队列消息
                    _data = self.get_q()
                except Empty as e:
                    # 队列为空，退出
                    #print '# queue is empty', e
                    # info
                    self.insertIteminfo(_iteminfosql_list, True)
                    _iteminfosql_list = []

                    # hour
                    self.insertItemhour(_itemhoursql_list, True)
                    _itemhoursql_list = []

                    # coming
                    self.insertItemComing(_itemcomingsql_list, True)
                    _itemcomingsql_list = []

                    # position
                    self.insertItemPosition(_itempositionsql_list, True)
                    _itempositionsql_list = []

                    break

                item = None
                crawl_type = ''
                if self.jhs_type == 'h':
                    # 每小时一次商品实例
                    item = JHSItem()
                    _val = _data[1]
                    if self.a_val: _val = _val + self.a_val

                    item.antPageGroupItemHour(_val)
                    #print '# Hour To crawl item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    crawl_type = 'grouphour'
                    # 汇聚
                    #self.push_back(self.items, item.outTupleGroupItemHour())

                    hourSql = item.outTupleGroupItemHour()
                    _itemhoursql_list.append(hourSql)
                    if self.insertItemhour(_itemhoursql_list): _itemhoursql_list = []

                elif self.jhs_type == 'i':
                    # 商品信息
                    item = JHSItem()
                    _val = _data[1]
                    if self.a_val: _val = _val + self.a_val

                    item.antPageGroupItem(_val)
                    #print '# To crawl item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    crawl_type = 'groupitem'
                    # 汇聚
                    self.push_back(self.items, item.outTupleGroupItem())

                    iteminfoSql = item.outTupleGroupItem()
                    _iteminfosql_list.append(iteminfoSql)
                    if self.insertIteminfo(_iteminfosql_list): _iteminfosql_list = []
                else:
                    # 通知queue, task结束
                    self.queue.task_done()
                    continue

                # 存网页
                #if item and crawl_type != '':
                #    _pages = item.outItemPage(crawl_type)
                #    self.mongoAccess.insertJHSPages(_pages)


                # 延时
                time.sleep(1)
                # 通知queue, task结束
                self.queue.task_done()

            except Common.NoItemException as e:
                print 'Not item exception :', e
                # 通知queue, task结束
                self.queue.task_done()

            except Common.NoPageException as e:
                print 'Not page exception :', e
                # 通知queue, task结束
                self.queue.task_done()

            except Common.InvalidPageException as e:
                self.crawlRetry(_data)
                print 'Invalid page exception :', e
                # 通知queue, task结束
                self.queue.task_done()

            except Exception as e:
                print 'Unknown exception crawl item :', e
                #traceback.print_exc()
                print '#####--Traceback Start--#####'
                tp,val,td = sys.exc_info()
                for file, lineno, function, text in traceback.extract_tb(td):
                    print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                    print text
                print "exception traceback err:%s,%s,%s"%(tp,val,td)
                print '#####--Traceback End--#####'
                self.crawlRetry(_data)
                # 通知queue, task结束
                self.queue.task_done()
                if str(e).find('Name or service not known') != -1 or str(e).find('Temporary failure in name resolution') != -1:
                    print _data
                # 重新拨号
                try:
                    self.dialRouter(4, 'item')
                except Exception as e:
                    print '# DailClient Exception err:', e 
                    time.sleep(10)
                time.sleep(random.uniform(10,30))

class JHSGroupItemParserM(MyThread):
    '''A class of jhs item thread manager for Parser'''
    def __init__(self, jhs_type, thread_num=10, a_val=None):
        # parent construct
        MyThread.__init__(self, thread_num)

        # thread lock
        self.mutex = threading.Lock()

        # db
        self.mysqlAccess = MysqlAccess() # mysql access
        self.mongoAccess = MongoAccess() # mongodb access

        # jhs queue type
        self.jhs_type = jhs_type # m:解析json数据

        # appendix val
        self.a_val = a_val
        
        # activity items
        self.items = []

        # give up item, retry too many times
        self.giveup_items = []

    def push_back(self, L, v):
        if self.mutex.acquire(1):
            L.append(v)
            self.mutex.release()

    def putItem(self, _item):
        self.put_q((0, _item))

    def putItems(self, _items):
        for _item in _items: self.put_q((0, _item))

    # To parse retry
    def parseRetry(self, _data):
        if not _data: return
        _retry, _val = _data
        _retry += 1
        if _retry < Config.parse_retry:
            _data = (_retry, _val)
            self.put_q(_data)
        else:
            self.push_back(self.giveup_items, _val)
            print "# retry too many times, no get item:", _val

    # insert item coming
    def insertItemComing(self, itemsql_list, f=False):
        if f or len(itemsql_list) >= Config.item_max_arg:
            if len(itemsql_list) > 0:
                self.mysqlAccess.insertJhsGroupItemComing(itemsql_list)
                #print '# insert item coming data to database'
            return True
        return False

    # insert item position
    def insertItemPosition(self, itemsql_list, f=False):
        if f or len(itemsql_list) >= Config.item_max_arg:
            if len(itemsql_list) > 0:
                self.mysqlAccess.insertJhsGroupItemPosition(itemsql_list)
                #print '# insert position data to database'
            return True
        return False

    # To crawl item
    def crawl(self):
        # item sql list
        _itemcomingsql_list = []
        _itempositionsql_list = []
        while True:
            _data = None
            try:
                try:
                    # 取队列消息
                    _data = self.get_q()
                except Empty as e:
                    # 队列为空，退出
                    #print '# queue is empty', e
                    # info
                    # coming
                    self.insertItemComing(_itemcomingsql_list, True)
                    _itemcomingsql_list = []

                    # position
                    self.insertItemPosition(_itempositionsql_list, True)
                    _itempositionsql_list = []

                    break

                item = None
                crawl_type = ''
                if self.jhs_type == 'm':
                    # 商品实例
                    item = JHSItem()
                    _val = _data[1]
                    if self.a_val: _val = _val + self.a_val
                    item.antPageGroupItemParserData(_val)
                    #print '# To crawl activity item val : ', Common.now_s(), _val[2], _val[4], _val[6]

                    # 汇聚
                    self.push_back(self.items, item.outTupleGroupItemParser())

                    # 入库
                    status_type,itemSql,o_val = item.outTupleGroupItemParser()

                    if status_type == 0:
                        # coming
                        crawl_type = 'grouppresale'
                        _itemcomingsql_list.append(itemSql)
                    else:
                        # position
                        crawl_type = 'groupposition'
                        _itempositionsql_list.append(itemSql)

                    if self.insertItemComing(_itemcomingsql_list): _itemcomingsql_list = []
                    if self.insertItemPosition(_itempositionsql_list): _itempositionsql_list = []

                else:
                    # 通知queue, task结束
                    self.queue.task_done()
                    continue

                # 存网页
                #if item and crawl_type != '':
                #    _pages = item.outItemPage(crawl_type)
                #    self.mongoAccess.insertJHSPages(_pages)


                # 延时
                time.sleep(1)
                # 通知queue, task结束
                self.queue.task_done()

            except Common.NoItemException as e:
                print 'Not item exception :', e
                # 通知queue, task结束
                self.queue.task_done()

            except Common.NoPageException as e:
                print 'Not page exception :', e
                # 通知queue, task结束
                self.queue.task_done()

            except Common.InvalidPageException as e:
                self.crawlRetry(_data)
                print 'Invalid page exception :', e
                # 通知queue, task结束
                self.queue.task_done()

            except Exception as e:
                print 'Unknown exception crawl item :', e
                #traceback.print_exc()
                print '#####--Traceback Start--#####'
                tp,val,td = sys.exc_info()
                for file, lineno, function, text in traceback.extract_tb(td):
                    print "exception traceback err:%s,line:%s,in:%s"%(file, lineno, function)
                    print text
                print "exception traceback err:%s,%s,%s"%(tp,val,td)
                print '#####--Traceback End--#####'
                self.crawlRetry(_data)
                # 通知queue, task结束
                self.queue.task_done()
                time.sleep(random.uniform(10,30))


if __name__ == '__main__':
    pass

