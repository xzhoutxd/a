#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import traceback
import base.Common as Common
import base.Config as Config
from JHSItemM import JHSItemM
#from Message import Message
sys.path.append('../db')
from RedisQueue  import RedisQueue
from RedisAccess import RedisAccess

class JHSBrandQ():
    '''A class of jhs act redis queue'''
    def __init__(self):
        # DB
        self.jhs_type    = Config.JHS_TYPE   # queue type
        self.redisQueue  = RedisQueue()      # redis queue
        self.redisAccess = RedisAccess()     # redis db

    # clear activity queue
    def clearBrandQ(self,q_type):
        _key = '%s_act_%s' % (self.jhs_type,q_type)
        self.redisQueue.clear_q(_key)

    # 写入redis queue
    def putBrandQ(self, q_type, _msg):
        _key = '%s_act_%s' % (self.jhs_type,q_type)
        _data = _msg
        self.redisQueue.put_q(_key, _data)

    # 转换msg
    def putBrandlistQ(self, q_type, brandact_list):
        for _act in brandact_list:
            #msg = self.q_message.actMsg(_act)
            msg = _act
            self.putBrandQ(q_type, msg)

    # 多线程抓去品牌团商品
    def run_brandItems(self, _val, item_type, a_val):
        brandact_id, brandact_name, item_valTuple = _val
        print '# activity Items start:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), brandact_id, brandact_name

        # 多线程 控制并发的线程数
        max_th = Config.item_max_th
        if item_type == 'l':
            max_th = Config.item_mid_th
        if len(item_valTuple) > max_th:
            m_itemsObj = JHSItemM(item_type, max_th, a_val)
        else:
            m_itemsObj = JHSItemM(item_type, len(item_valTuple), a_val)
        m_itemsObj.createthread()
        m_itemsObj.putItems(item_valTuple)
        m_itemsObj.run()

        try:
            print '# item Check: actId:%s, actName:%s'%(brandact_id, brandact_name)
            if m_itemsObj.empty_q():
                # 重试次数太多没有抓下来的商品
                giveup_item_list = m_itemsObj.giveup_items
                print '# Give up items num:', len(giveup_item_list)
                if len(giveup_item_list) > 0:
                    print '###give up###','actId:%s,actName:%s,'%(brandact_id, brandact_name),giveup_item_list,'###give up###'
        except Exception as e:
            print 'Unknown exception item result :', e
        print '# activity Items end:',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),brandact_id, brandact_name

    def brandQ(self, q_type, a_val):
        i, M = 0, 10
        n = 0
        while True: 
            _key = '%s_act_%s' % (self.jhs_type,q_type)
            _data = self.redisQueue.get_q(_key)

            # 队列为空
            if not _data:
                i += 1
                if i > M:
                    print '# all get brandQ item num:',n
                    print '# not get brandQ of key:',_key
                    break
                time.sleep(10)
                continue
            n += 1
            self.run_brandItems(_data, q_type, a_val)



