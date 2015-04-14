#-*- coding:utf-8 -*-
#!/usr/bin/env python

from sys import path
path.append(r'../base')

import traceback
import Common as Common
from MongoPool import MongoPool

@Common.singleton
class MongoAccess():
    '''A class of mongodb access'''
    def __init__(self):
        self.mongo_db = MongoPool()

    def __del__(self):
        pass

    # 插入网页列表
    def insertTBPages(self, pages):
        try:
            _key, _pages_d = pages
            data = {"key":_key, "pages":_pages_d}
            c = _key[:8]
            self.mongo_db.insertTBPage(c, data)        
        except Exception, e:
            print '# insertTBPages exception:', e
            traceback.print_exc()

    def insertVipPages(self, pages):
        try:
            _key, _pages_d = pages
            data = {"key":_key, "pages":_pages_d}
            c = _key[:8]
            self.mongo_db.insertVipPage(c, data)  
        except Exception, e:
            print '# insertVipPages exception:', e
            traceback.print_exc()

    def insertJHSPages(self, pages):
        try:
            _key, _pages_d = pages
            data = {"key":_key, "pages":_pages_d}
            c = _key[:8]
            self.mongo_db.insertJHSPage(c, data)
        except Exception, e:
            print '# insertJHSPages exception:', e
            traceback.print_exc()

    # 删除网页
    def removeTBPage(self, _key):
        c = _key[:8]
        self.mongo_db.removeTBPage(c, _key)

    def removeVipPage(self, _key):
        c = _key[:8]
        self.mongo_db.removeVipPage(c, _key)

    def removeJHSPage(self, _key):
        c = _key[:8]
        self.mongo_db.removeJHSPage(c, _key)

    # 查询网页
    def findTBPage(self, _key):
        c = _key[:8]
        return self.mongo_db.findTBPage(c, _key)

    def findVipPage(self, _key):
        c = _key[:8]
        return self.mongo_db.findVipPage(c, _key)

    def findJHSPage(self, _key):
        c = _key[:8]
        return self.mongo_db.findJHSPage(c, _key)

    # 遍历网页
    def scanTBPage(self, c):
        for pg in self.mongo_db.findTBPages(c):
            _key   = pg['key']
            _pages = pg['pages']
            for k in _pages.keys(): print _key, k

    def scanVipPage(self, c):
        for pg in self.mongo_db.findVipPages(c):
            _key   = pg['key']
            _pages = pg['pages']
            for k in _pages.keys(): print _key, k

    def scanJHSPage(self, c):
        for pg in self.mongo_db.findJHSPages(c):
            _key   = pg['key']
            _pages = pg['pages']
            for k in _pages.keys(): print _key, k

    # 创建索引
    def crtTBIndex(self, c):
        self.mongo_db.crtTBIndex(c)

    def crtVipIndex(self, c):
        self.mongo_db.crtVipIndex(c)

    def crtJHSIndex(self, c):
        self.mongo_db.crtJHSIndex(c)

    # 删除表格
    def dropTable(self, c):
        self.mongo_db.dropTable(c)

# if __name__ == '__main__':
#     m = MongoAccess()
#     import base.Common as Common
#     c = Common.today_ss()
#     m.crtTBIndex(c)
#     m.crtVipIndex(c)

if __name__ == '__main__':
    m = MongoAccess()
    vals = m.findTBPage('20150303151645_1_61773004_43790383280')
    #vals = m.findTBPage('20150308003057_1_58501945')
    if vals and vals.has_key('pages'):
        _dict = vals['pages']
        for (_tag, _content) in _dict.items():
            print _tag, _content.encode('utf8', 'ignore')
