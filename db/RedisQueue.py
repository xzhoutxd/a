#-*- coding:utf-8 -*-
#!/usr/bin/env python
# 2014-10-08

from sys import path
path.append(r'../')

from hotqueue import HotQueue
import base.Environ as Environ

class RedisQueue:
    def __init__(self):
        # redis数据库设置
        self.QUEUE_DB = 100

        # redis配置
        self.redis_ip, self.redis_port, self.redis_passwd = Environ.redis_config[self.QUEUE_DB]

        # 抓取队列   tm:1, tb:2, vip:3, jhs:4
        self.q_list = [
                '1_shop', '1_shopitem', '1_item',    # 天猫shop, shopitem, item
                '2_shop', '2_shopitem', '2_item',    # 淘宝shop, shopitem, item
                '3_act',  '3_sku_h',    '3_sku_d'    # 唯品会activity, 每小时sku, 每日sku
                '4_act_h','4_act_d', '4_item_h', '4_item_d' # 聚划算每日/每小时activity, 每日/每小时item
            ]

        # 初始化队列
        self.initQueue()

    def initQueue(self):
        # hotqueue队列字典表
        self.q_dict = {}

        # 抓取队列
        for q in self.q_list:
            self.q_dict[q] = HotQueue(q, host=self.redis_ip, port=self.redis_port, password=self.redis_passwd, db=self.QUEUE_DB)

    # To put queue
    def put_q(self, _key, _val):
        try:
            if self.q_dict.has_key(_key):
                q = self.q_dict[_key]
                q.put(_val)
        except Exception as e:
            print '# put_q exception ', e

    # To get queue
    def get_q(self, _key):
        _val = None
        try:
            if self.q_dict.has_key(_key):
                q = self.q_dict[_key]
                _val = q.get()
        except Exception as e:
            print '# get_q exception ', e        
        return _val

    # 清空队列
    def clear_q(self, _key):
        if self.q_dict.has_key(_key):
            q = self.q_dict[_key]
            q.clear()

if __name__ == "__main__":
    q = RedisQueue()
#     q.clear_q('3_act')
#     q.clear_q('3_sku_h')
#     q.clear_q('3_sku_d')

