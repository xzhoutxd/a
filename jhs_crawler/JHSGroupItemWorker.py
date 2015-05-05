#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys

import time
import random
import traceback
import base.Common as Common
import base.Config as Config
from db.MysqlAccess import MysqlAccess
#from JHSGroupItemM import JHSGroupItemParserM
#from JHSGroupItemM import JHSGroupItemCrawlerM

sys.path.append('../db')
from RedisAccess import RedisAccess
from MongoAccess import MongoAccess

import warnings
warnings.filterwarnings("ignore")

class JHSGroupItemWorker():
    '''A class of JHS group item channel worker'''
    def __init__(self):
        # jhs group item type
        self.worker_type  = Config.JHS_GroupItem

        # 抓取时间设定
        self.crawling_time = Common.now() # 当前爬取时间
        self.begin_time = Common.now()
        self.begin_date = Common.today_s()
        self.begin_hour = Common.nowhour_s()

        # mysql access
        self.mysqlAccess = MysqlAccess()

        # redis access
        self.redisAccess  = RedisAccess()

        # mongodb access
        self.mongoAccess  = MongoAccess()

    # 删除redis数据库过期商品
    def delItem(self, _items):
        for _item in _items:
            keys = [self.worker_type, _item["item_juId"]]
            
            item = self.redisAccess.read_jhsitem(keys)
            if item:
                end_time = item["end_time"]
                now_time = Common.time_s(self.begin_time)
                # 删除过期的商品
                if now_time > end_time: self.redisAccess.delete_jhsitem(keys)

    # 把商品信息存入redis数据库中
    def putItemDB(self, _items):
        for _item in _items:
            # 忽略已经存在的商品ID
            keys = [self.worker_type, _item["item_juId"]]
            if self.redisAccess.exist_jhsitem(keys): continue

            # 将商品基础数据写入redis
            val  = _item["val"]
            self.redisAccess.write_jhsitem(keys, val)

    # 查找新商品
    def selectNewItems(self, _items):
        new_items = []
        for _item in _items:
            keys = [self.worker_type, _item["item_juId"]]
            if self.redisAccess.exist_jhsitem(keys): continue
            new_items.append(_item["val"])
        return new_items

    def scanEndItems(self):
        val = (Common.time_s(self.crawling_time),)
        # 删除已经结束的商品
        _items = self.mysqlAccess.selectJhsGroupItemEnd(val)
        end_items = []
        # 遍历商品
        for _item in _items:
            item_juid = _item[0]
            end_items.append({"item_juId":str(item_juid)})
        self.delItem(end_items)
            
    def scanAliveItems(self):
        val = (Common.time_s(self.crawling_time), Common.time_s(self.crawling_time))
        # 查找已经开团但是没有结束的商品
        _items = self.mysqlAccess.selectJhsGroupItemAlive(val)
        print "# hour all item nums:",len(_items)
        return _items

