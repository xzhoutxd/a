#-*- coding:utf-8 -*-
#!/usr/bin/env python

from sys import path
path.append(r'../')

import pymongo  # 只能用2.8版本
import base.Environ as Environ

class MongoPool():
    '''A class of mongodb connection pool'''
    def __init__(self):
        # 数据库配置
        db_config    = Environ.mongodb_config
        _host, _port = db_config['host'], db_config['port']

        # mongodb connect pool
        self.mongo   = pymongo.Connection(host=_host, port=_port)

        # 淘宝/天猫网页库
        self.tb_db   = self.mongo["tb"]

        # Vip网页库
        self.vip_db  = self.mongo["vip"]

    def __del__(self):
         self.mongo.close()

    # 创建索引
    def crtTBIndex(self, c):
        self.tb_db[c].ensure_index('key', unique=True)

    def crtVipIndex(self, c):
        self.vip_db[c].ensure_index('key', unique=True)

    # 删除表格
    def dropTable(self, c):
        self.tb_db[c].drop()
        self.vip_db[c].drop()

    def insertTBPage(self, c, _data):
        self.tb_db[c].insert(_data)

    def insertVipPage(self, c, _data):
        self.vip_db[c].insert(_data)

    def removeTBPage(self, c, _key):
        self.tb_db[c].remove({"key":_key})

    def removeVipPage(self, c, _key):
        self.vip_db[c].remove({"key":_key})

    def findTBPage(self, c, _key):
        return self.tb_db[c].find_one({"key":_key})

    def findVipPage(self, c, _key):
        return self.vip_db[c].find_one({"key":_key})

    def findTBPages(self, c):
        return self.tb_db[c].find()

    def findVipPages(self, c):
        return self.vip_db[c].find()

if __name__ == '__main__':
    mongo = MongoPool()
    mongo = None


