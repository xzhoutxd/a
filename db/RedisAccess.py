#-*- coding:utf-8 -*-
#!/usr/bin/env python

from sys import path
path.append(r'../')

import json
import pickle
import base.Common as Common
from RedisPool import RedisPool

@Common.singleton
class RedisAccess:
    def __init__(self):
        # redis db instance
        self.redis_pool = RedisPool()

        # redis db id
        self.DEFAULT_DB    = 0   # default db
        
        self.TB_SHOP_DB    = 1   # taobao shop
        self.TB_ITEM_DB    = 2   # taobao item

        self.VIP_ACT_DB    = 3   # vip activity        
        self.VIP_ITEM_DB   = 4   # vip item
        self.VIP_SKU_DB    = 5   # vip sku

        self.COOKIE_DB     = 9   # taobao cookie
        self.QUEUE_DB      = 10  # queue db

    ######################## Cookie部分 ########################

    # 判断是否存在cookie
    def exist_cookie(self, keys):
        return self.redis_pool.exists(keys, self.COOKIE_DB)

    # 删除cookie
    def remove_cookie(self, keys):
        return self.redis_pool.remove(keys, self.COOKIE_DB)

    # 查询cookie
    def read_cookie(self, keys):
        try:
            val = self.redis_pool.read(keys, self.COOKIE_DB)
            if val:
                cookie_dict = pickle.loads(val)
                _time  = cookie_dict["time"]            
                _cookie= cookie_dict["cookie"]
                return (_time, _cookie)
        except Exception, e:
            print '# Redis access read cookie exception:', e
            return None

    # 写入cookie
    def write_cookie(self, keys, val):
        try:
            _time, _cookie = val
            cookie_dict = {}
            cookie_dict["time"]   = _time
            cookie_dict["cookie"] = _cookie
            cookie_json = pickle.dumps(cookie_dict)
            
            self.redis_pool.write(keys, cookie_json, self.COOKIE_DB)
        except Exception, e:
            print '# Redis access write cookie exception:', e

    # 扫描cookie
    def scan_cookie(self):
        try:
            cookie_list = []
            cookies = self.redis_pool.scan_db(self.COOKIE_DB)
            for cookie in cookies:
                val = cookie[1]
                if val:
                    cookie_dict = pickle.loads(val)
                    _time   = cookie_dict["time"]   
                    _cookie = cookie_dict["cookie"]
                    cookie_list.append((_time, _cookie))
            return cookie_list
        except Exception, e:
            print '# Redis access scan cookie exception:', e
            return None

    ######################## 天猫/淘宝部分 ########################
    
    # 判断是否存在天猫/淘宝店铺
    def exist_tbshop(self, keys):
        return self.redis_pool.exists(keys, self.TB_SHOP_DB)

    # 判断是否存在天猫/淘宝商品
    def exist_tbitem(self, keys):
        return self.redis_pool.exists(keys, self.TB_ITEM_DB)

    # 查询天猫/淘宝店铺
    def read_tbshop(self, keys):
        try:
            val = self.redis_pool.read(keys, self.TB_SHOP_DB)
            if val:
                shop_dict = json.loads(val)
                c_time   = shop_dict["crawl_time"]
                c_items  = shop_dict["items"]
                c_itemnum= shop_dict["itemnum"] if shop_dict.has_key("itemnum") else ''

                return c_time, c_items, c_itemnum
        except Exception, e:
            print '# Redis access read tb shop exception:', e
            return None

    # 写入天猫/淘宝店铺
    def write_tbshop(self, keys, val):
        try:
            c_time, c_items, c_itemnum = val
            shop_dict = {}
            shop_dict["crawl_time"] = c_time
            shop_dict["items"]      = c_items
            shop_dict["itemnum"]    = c_itemnum
            shop_json = json.dumps(shop_dict)

            self.redis_pool.write(keys, shop_json, self.TB_SHOP_DB)
        except Exception, e:
            print '# Redis access write tb shop exception:', e

    # 查询天猫/淘宝商品
    def read_tbitem(self, keys):
        try:
            val = self.redis_pool.read(keys, self.TB_ITEM_DB)
            if val:
                json_dict = json.loads(val)
                c_time  = json_dict["crawl_time"]            
                s_id    = json_dict["shop_id"]
                i_title = json_dict["item_title"]
                i_img   = json_dict["item_img"]
                d_time  = json_dict["deal_time"]
                on_time = json_dict["on_time"]  if json_dict.has_key("on_time")  else ''
                new_time= json_dict["new_time"] if json_dict.has_key("new_time") else ''

                return (c_time, s_id, i_title, i_img, d_time, on_time, new_time)
        except Exception, e:
            print '# Redis access read tb item exception:', e
            return None

    # 写入天猫/淘宝商品
    def write_tbitem(self, keys, val):
        try:
            c_time, s_id, i_title, i_img, d_time, on_time, new_time = val
            json_dict = {}
            json_dict["crawl_time"] = c_time            
            json_dict["shop_id"]    = s_id
            json_dict["item_title"] = i_title
            json_dict["item_img"]   = i_img
            json_dict["deal_time"]  = d_time
            json_dict["on_time"]    = on_time
            json_dict["new_time"]   = new_time

            item_json = json.dumps(json_dict)
            self.redis_pool.write(keys, item_json, self.TB_ITEM_DB)
        except Exception, e:
            print '# Redis access write tb item exception:', e

    # 扫描天猫/淘宝商品
    def scan_tbitem(self):
        try:
            items = self.redis_pool.scan_db(self.TB_ITEM_DB)
            for item in items:
                key, val = item
                if val:
                    json_dict = json.loads(val)
                    c_time  = json_dict["crawl_time"]            
                    s_id    = json_dict["shop_id"]
                    i_title = json_dict["item_title"]
                    i_img   = json_dict["item_img"]
                    d_time  = json_dict["deal_time"]
                    on_time = json_dict["on_time"]  if json_dict.has_key("on_time")  else ''
                    new_time= json_dict["new_time"] if json_dict.has_key("new_time") else ''

                    print '# scan_tbitem %s:' %key, c_time, s_id, i_title, i_img, d_time, on_time, new_time
        except Exception, e:
            print '# Redis access scan tb item exception:', e
            return None

    ######################## 唯品会部分 ########################

    ######################## VIP Activity ###################
    # 判断是否存在vip频道活动
    def exist_vipact(self, keys):
        return self.redis_pool.exists(keys, self.VIP_ACT_DB)

    # 删除vip频道活动
    def delete_vipact(self, keys):
        self.redis_pool.remove(keys, self.VIP_ACT_DB)

    # 查询vip频道活动
    def read_vipact(self, keys):
        try:
            val = self.redis_pool.read(keys, self.VIP_ACT_DB)
            return json.loads(val) if val else None
        except Exception, e:
            print '# Redis access read vip activity exception:', e
            return None

    # 写入vip频道活动
    def write_vipact(self, keys, val):
        try:
            crawl_time, act_platform, warehouse, act_chn, act_id, act_name, act_url, act_image, act_coupon, act_slogan, brand_name, start_time, end_time, _jit_whs, item_ids = val
            act_dict = {}
            act_dict["crawl_time"]   = crawl_time
            act_dict["platform"]     = act_platform
            act_dict["warehouse"]    = warehouse
            act_dict["act_chn"]      = act_chn
            act_dict["act_id"]       = act_id
            act_dict["act_name"]     = act_name
            act_dict["act_url"]      = act_url
            act_dict["act_image"]    = act_image
            act_dict["act_coupon"]   = act_coupon
            act_dict["act_slogan"]   = act_slogan
            act_dict["brand_name"]   = brand_name
            act_dict["start_time"]   = start_time
            act_dict["end_time"]     = end_time
            act_dict["_jit_whs"]     = _jit_whs
            act_dict["item_ids"]     = item_ids
            act_json = json.dumps(act_dict)
            self.redis_pool.write(keys, act_json, self.VIP_ACT_DB)
        except Exception, e:
            print '# Redis access write vip activity exception:', e

    # 扫描vip频道活动 - 性能不好
    def scan_vipact(self):
        try:
            for act in self.redis_pool.scan_db(self.VIP_ACT_DB):
                key, val = act
                if not val: continue
                act_dict       = json.loads(val)
                crawl_time     = act_dict["crawl_time"]
                act_platform   = act_dict["platform"]
                warehouse      = act_dict["warehouse"]
                act_chn        = act_dict["act_chn"]
                act_id         = act_dict["act_id"]
                act_name       = act_dict["act_name"]
                act_url        = act_dict["act_url"]
                act_image      = act_dict["act_image"]
                act_coupon     = act_dict["act_coupon"]
                act_slogan     = act_dict["act_slogan"]
                brand_name     = act_dict["brand_name"]
                start_time     = act_dict["start_time"]            
                end_time       = act_dict["end_time"]                
                _jit_whs       = act_dict["_jit_whs"]
                item_ids       = act_dict["item_ids"]
                print "# scan_vipact %s:" %key, crawl_time, act_platform, warehouse, act_chn, act_id, act_name, act_url, act_image, act_coupon, act_slogan, brand_name, start_time, end_time, _jit_whs, item_ids
        except Exception, e:
            print '# Redis access scan vip activity exception:', e

    ######################## VIP Sku ###################

    # 判断是否存在vip库存
    def exist_vipsku(self, keys):
        return self.redis_pool.exists(keys, self.VIP_SKU_DB)

    # 删除vip库存
    def delete_vipsku(self, keys):
        self.redis_pool.remove(keys, self.VIP_SKU_DB)

    # 查询vip库存
    def read_vipsku(self, keys):
        try:
            val = self.redis_pool.read(keys, self.VIP_SKU_DB)
            return json.loads(val) if val else None 
        except Exception, e:
            print '# Redis access read vip sku exception:', e
            return None

    # 写入vip库存
    def write_vipsku(self, keys, val):
        try:
            act_platform, warehouse, act_id, act_name, item_id, item_name, item_sn = val
            sku_dict = {}
            sku_dict["platform"]  = act_platform
            sku_dict["warehouse"] = warehouse
            sku_dict["act_id"]    = act_id
            sku_dict["act_name"]  = act_name
            sku_dict["item_id"]   = item_id            
            sku_dict["item_name"] = item_name
            sku_dict["item_sn"]   = item_sn          

            sku_json = json.dumps(sku_dict)
            self.redis_pool.write(keys, sku_json, self.VIP_SKU_DB)
        except Exception, e:
            print '# Redis access write vip sku exception:', e

    # 扫描vip商品sku - 性能不好
    def scan_vipsku(self):
        try:
            for sku in self.redis_pool.scan_db(self.VIP_SKU_DB):
                key, val = sku
                if not val: continue
                sku_dict    = json.loads(val)
                act_platform= sku_dict["platform"]
                warehouse   = sku_dict["warehouse"]
                act_id      = sku_dict["act_id"]
                act_name    = sku_dict["act_name"]
                item_id     = sku_dict["item_id"]            
                item_name   = sku_dict["item_name"]
                item_sn     = sku_dict["item_sn"] 
                print "# scan_vipsku %s:" %key, act_platform, warehouse, act_id, act_name, item_id, item_name, item_sn
        except Exception as e:
             print '# Redis access scan vip sku exception:', e

if __name__ == '__main__1':
    r = RedisAccess()
    cookies = r.scan_cookie()
    for cookie in cookies: print cookie[0]
    r = None

if __name__ == '__main__2':
    r = RedisAccess()
    keys = ['3', '372378']
    vals = r.read_vipact(keys)
    if vals:
        for v in vals : print v

if __name__ == '__main__':
    r = RedisAccess()
    r.scan_vipact()
    #r.scan_vipsku()
    


