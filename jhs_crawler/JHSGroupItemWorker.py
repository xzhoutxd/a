#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys

import time
import random
import traceback
import base.Common as Common
import base.Config as Config
from Message import Message
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

        # message
        self.message = Message()

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
            item_val = self.message.itemInfo(_item["r_val"])
            val = self.message.itemMsg(item_val)
            self.redisAccess.write_jhsitem(keys, val)

    # 更新商品信息
    def updateItem(self, _item):
        keys = [self.worker_type, _item["item_juId"]]

        item = self.redisAccess.read_jhsitem(keys)
        if item:
            item_val = self.message.itemParseInfo(_item["r_val"])
            c = False
            if item["start_time"] != item_val["start_time"]:
                item["start_time"] = item_val["start_time"]
                c = True
            if item["end_time"] != item_val["end_time"]:
                item["end_time"] = item_val["end_time"]
                c = True
            if c:
                self.redisAccess.write_jhsitem(keys, item)

    # 查找新商品
    def selectNewItems(self, _items):
        new_items = []
        for _item in _items:
            keys = [self.worker_type, _item["item_juId"]]
            if self.redisAccess.exist_jhsitem(keys): 
                self.updateItem(_item)
                continue
            new_items.append(_item["val"])
        return new_items

    def scanEndItems(self):
        val = (Common.time_s(self.crawling_time),)
        _items = self.mysqlAccess.selectJhsGroupItemEnd(val)
        end_items = []
        # 遍历商品
        for _item in _items:
            item_juid = _item[0]
            end_items.append({"item_juId":str(item_juid)})
        # 删除已经结束的商品
        self.delItem(end_items)
            
    def scanAliveItems(self):
        val = (Common.time_s(self.crawling_time), Common.time_s(self.crawling_time))
        # 查找已经开团但是没有结束的商品
        _items = self.mysqlAccess.selectJhsGroupItemAlive(val)
        print "# hour all item nums:",len(_items)
        return _items

    def scanNotEndItems(self):
        val = (Common.time_s(self.crawling_time),)
        # 查找没有结束的商品
        _items = self.mysqlAccess.selectJhsGroupItemNotEnd(val)
        i = 1
        for _item in _items:
            print i
            item_juid = str(_item[1])
            keys = [self.worker_type, item_juid]

            item = self.redisAccess.read_jhsitem(keys)
            print item
            #_new_item = {"crawling_time":item["crawling_time"],"item_juid":item["item_juId"],"groupcat_id":item["item_groupCatId"],"groupcat_name":item["item_groupCatName"],"item_ju_url":item["item_ju_url"],"item_juname":item["item_juName"],"item_id":item["item_id"],"start_time":item["start_time"],"end_time":item["end_time"]}
            #self.redisAccess.write_jhsitem(keys, _new_item)
            i += 1

    def scanCategories(self):
        category_list = self.mysqlAccess.selectJhsGroupItemCategory()
        return category_list
if __name__ == '__main__':
    pass
    #w = JHSGroupItemWorker()
    #w.scanNotEndItems()
        
