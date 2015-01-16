#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import base.Common as Common
import base.Config as Config
from db.RedisAccess import RedisAccess
from TBCrawler import TBCrawler

class Item():
    '''A class of item'''
    def __init__(self):
        # crawler
        self.crawler         = TBCrawler()

        # shop
        self.shop_id         = ''
        self.shop_type       = '1' # 店铺类型

        # 成交抓取参数
        self.deal_pageSize   = 15
        self.deal_maxPages   = 100
        self.deal_bufferdays = 3   # 往前追溯3天

        # 评价抓取参数
        self.rate_pageSize   = 20
        self.rate_maxPages   = 100

        # redis access
        self.redisAccess     = RedisAccess()

        # 初始化实例变量
        self.initItem()

    def initItem(self):
        # 商品抓取设置
        self.crawling_time   = Common.now()

        # 商品属性
        self.item_id         = ''   # 商品ID
        self.item_name       = ''   # 商品名称
        self.item_url        = ''   # 商品链接
        self.item_sellerId   = ''   # 卖家ID
        self.item_spuId      = ''   # SPU ID
        self.item_sellCount  = 0    # 月销售数

        # 商品页
        self.item_page       = None # 商品首页

        # item html urls
        self.item_urls       = []   # 商品链接列表

        # item html pages
        self.item_pages      = []   # 商品网页列表

        # 成交记录
        self.deal_url        = ''
        self.deal_stopCrawl  = False
        self.deal_deadLine   = 0.0  # 上次抓取的成交记录最晚时间
        self.deal_deadLine2  = 0.0  # 本次抓取的成交记录最早时间

    def itemCrawl(self):
        # 检查商品ID有效性
        if not self.item_id or self.item_id == '': return

        # 写入redis数据库
        keys = [self.shop_type, self.item_id]
        val  = self.redisAccess.read_item(keys)
        if val:
            c_time, d_time = val[0], val[4]
            self.crawled_time  = c_time
            self.deal_deadLine = d_time

            if self.crawled_time and self.crawled_time > Config.g_zeroValue:  # 1天86400秒
                self.deal_deadLine2  = self.crawled_time - self.deal_bufferdays * 86400

    # 输出抓取的网页log
    def outItemLog(self):
        pages = []
        for p_val in self.item_pages:
            p_tag, p_url, p_content = p_val

            # 网页文件名
            f_path = '%s_item/%s' %(self.shop_type, self.item_id)
            f_name = '%s_%s-%s_%s_%d.htm' %(self.shop_type, self.shop_id, self.item_id, p_tag, self.crawling_time)

            # 网页文件内容
            f_content = '<!-- url=%s -->\n%s\n' %(p_url, p_content)
            pages.append((f_name, p_tag, f_path, f_content))

        return pages

    # 输出抓取的网页sql
    def outItemSql(self):
        sqls, pages_d = [], {}
        key = '%s_%s_%s_%s' %(Common.time_ss(self.crawling_time), self.shop_type, self.shop_id, self.item_id)
        for p_val in self.item_pages:
            p_tag, p_url, p_content = p_val
            sqls.append((Common.time_s(self.crawling_time), self.shop_id, self.item_id, self.item_name, p_tag, p_url))
            pages_d[p_tag] = p_content.strip()
        return sqls, (key, pages_d)
