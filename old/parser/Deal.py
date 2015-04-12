#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import base.Config as Config
import base.Common as Common

class Deal():
    '''A class of Deal'''
    def __init__(self):
        # Deal
        self.crawlType  = 0
        self.buyerNick  = ''
        self.creditLevel= ''
        self.memberLevel= ''
        self.chargeTime = ''
        self.price      = ''
        self.amount     = 1
        self.promType   = ''
        self.attrvals   = None

    # Deal属性
    def setDeal(self, crawl_type, buyer, credit, member, ctime, price, amount, prom, attrs):
        self.crawlType, self.buyerNick, self.creditLevel, self.memberLevel, self.chargeTime, self.price, self.amount, self.promType, self.attrvals = crawl_type, buyer, credit, member, ctime, price, amount, prom, attrs

    # 输出Deal
    def outDeal(self, c_time, s_id, i_id):
        # 抓取时间,抓取类型,店铺ID,商品ID,买家别名,买家信用级别,买家会员级别,成交时间,拍下价格,购买数量,促销类别,属性列表
        s = '%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n' % (Common.time_s(c_time), Config.delim, self.crawlType, Config.delim, s_id, Config.delim, i_id, Config.delim, self.buyerNick, Config.delim, self.creditLevel, Config.delim, self.memberLevel, Config.delim, self.chargeTime, Config.delim, self.price, Config.delim, self.amount, Config.delim, self.promType, Config.delim, ';'.join(sorted(self.attrvals)))
        return s
