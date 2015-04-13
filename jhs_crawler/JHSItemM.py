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

import warnings
warnings.filterwarnings("ignore")

class JHSItemM(MyThread):
    '''A class of jhs item thread manager'''
    def __init__(self, jhs_type, thread_num=10, a_val=None):
        # parent construct
        MyThread.__init__(self, thread_num)

        # thread lock
        self.mutex = threading.Lock()

        # mysql
        self.mysqlAccess = MysqlAccess()

        # jhs queue type
        self.jhs_type = jhs_type # 1:新增商品, 2:每天一次的商品, 3:每小时一次的商品

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
                self.mysqlAccess.insertJhsItemInfo(iteminfosql_list)
                #print '# insert data to database'
            return True
        return False

    # insert item day
    def insertItemday(self, itemdaysql_list, f=False):
        if f or len(itemdaysql_list) >= Config.item_max_arg:
            if len(itemdaysql_list) > 0:
                self.mysqlAccess.insertJhsItemForDay(itemdaysql_list)
                #print '# day insert data to database'
            return True
        return False

    # insert item hour
    def insertItemhour(self, itemhoursql_list, f=False):
        if f or len(itemhoursql_list) >= Config.item_max_arg:
            if len(itemhoursql_list) > 0:
                self.mysqlAccess.insertJhsItemForHour(itemhoursql_list)
                #print '# hour insert data to database'
            return True
        return False

    # update item
    def updateItem(self, itemsql_list, f=False):
        if f or len(itemsql_list) >= Config.item_max_arg:
            if len(itemsql_list) > 0:
                self.mysqlAccess.updateJhsItem(itemsql_list)
                #print '# update data to database'
            return True
        return False

    # update item remind
    def updateItemRemind(self, itemsql_list, f=False):
        if f or len(itemsql_list) >= Config.item_max_arg:
            if len(itemsql_list) > 0:
                self.mysqlAccess.updateJhsItemRemind(itemsql_list)
                #print '# update remind data to database'
            return True
        return False

    # To crawl item
    def crawl(self):
        # item sql list
        _iteminfosql_list = []
        _itemdaysql_list = []
        _itemhoursql_list = []
        _itemlocksql_list = []
        _itemsql_list = []
        while True:
            _data = None
            try:
                try:
                    # 取队列消息
                    _data = self.get_q()
                except Empty as e:
                    # 队列为空，退出
                    #print '# queue is empty', e
                    #print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                    # info
                    self.insertIteminfo(_iteminfosql_list, True)
                    _iteminfosql_list = []
                    #print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

                    # day
                    self.insertItemday(_itemdaysql_list, True)
                    _itemdaysql_list = []

                    # hour
                    self.insertItemhour(_itemhoursql_list, True)
                    _itemhoursql_list = []

                    self.updateItem(_itemlocksql_list, True)
                    _itemlocksql_list = []

                    # remind
                    self.updateItemRemind(_itemsql_list, True)
                    _itemsql_list = []
                    break

                if self.jhs_type == 1:
                    # 商品实例
                    item = JHSItem()
                    _val = _data[1]
                    item.antPage(_val)
                    #print '# To crawl activity item val : ', Common.now_s(), _val[2], _val[4], _val[6]

                    # 汇聚
                    #sql, saleSql, stockSql, iteminfoSql = item.outTuple()
                    iteminfoSql = item.outTuple()
                    self.push_back(self.items, item.outTuple())

                    # 入库
                    _iteminfosql_list.append(iteminfoSql)
                    if self.insertIteminfo(_iteminfosql_list): _iteminfosql_list = []
                elif self.jhs_type == 2:
                    # 每天一次商品实例
                    item = JHSItem()
                    _val = _data[1]
                    if self.a_val: _val = _val + self.a_val

                    item.antPageDay(_val)
                    #print '# Day To crawl activity item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    # 汇聚
                    #self.push_back(self.items, item.outTupleDay())

                    sql = item.outTupleDay()
                    _itemdaysql_list.append(sql)
                    if self.insertItemday(_itemdaysql_list): _itemdaysql_list = []
                elif self.jhs_type == 3:
                    # 每小时一次商品实例
                    item = JHSItem()
                    _val = _data[1]
                    if self.a_val: _val = _val + self.a_val

                    item.antPageHour(_val)
                    #print '# Hour To crawl activity item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    # 汇聚
                    #self.push_back(self.items, item.outTupleHour())

                    #hourSql,lockSql = item.outTupleHour()
                    hourSql = item.outSqlForHour()
                    _itemhoursql_list.append(hourSql)
                    if self.insertItemhour(_itemhoursql_list): _itemhoursql_list = []

                    #if lockSql:
                    #    _itemlocksql_list.append(lockSql)
                    #if self.updateItem(_itemlocksql_list): _itemlocksql_list = []
                elif self.jhs_type == 4:
                    # 更新商品关注人数
                    item = JHSItem()
                    _val = _data[1]
                    if self.a_val: _val = _val + self.a_val

                    item.antPageUpdateRemind(_val)
                    #print '# Hour To crawl activity item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    # 汇聚
                    self.push_back(self.items, item.outTupleUpdateRemind())

                    updateSql = item.outTupleUpdateRemind()

                    _itemsql_list.append(updateSql)
                    if self.updateItemRemind(_itemsql_list): _itemsql_list = []
                elif self.jhs_type == 5:
                    # 商品islock标志
                    item = JHSItem()
                    _val = _data[1]
                    if self.a_val: _val = _val + self.a_val

                    item.antPageLock(_val)
                    #print '# Hour To crawl activity item val : ', Common.now_s(), _val[0], _val[4], _val[5]
                    # 汇聚
                    #self.push_back(self.items, item.outTupleHour())

                    lockSql = item.outSqlForLock()

                    if lockSql:
                        _itemlocksql_list.append(lockSql)
                    if self.updateItem(_itemlocksql_list): _itemlocksql_list = []


                # 延时
                time.sleep(0.1)
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
                # 重新拨号
                try:
                    self.dialRouter(4, 'item')
                except Exception as e:
                    print '# DailClient Exception err:', e 
                    time.sleep(10)
                #time.sleep(1)
                try:
                    time.sleep((_data[0]+1)*random.uniform(10,30))
                except Exception as e:
                    time.sleep(random.uniform(10,30))
                #time.sleep(random.uniform(10,30))

if __name__ == '__main__':
    pass

