#-*- coding:utf-8 -*-
#!/usr/bin/env python

import base.Common as Common
import base.Config as Config
#import base.Environ as Environ
#from db.RedisAccess import RedisAccess

class Item():
    '''A class of item parser'''
    def __init__(self):
        self.shop_type       = '1' # 店铺类型

        # redis access
        #self.redisAccess     = RedisAccess()

        # 初始化实例变量
        self.initItem()

    def initItem(self):
        # 商品抓取设置
        self.crawling_time   = None
        self.crawled_time    = Config.g_crawledTime
        self.crawled_title   = ''
        self.crawled_img     = ''
        self.deal_deadLine   = 0.0
        self.crawled_onTime  = 0.0

        self.item_crawled    = True # 是否抓取过？
        self.item_newTime    = 0.0  # 商品上新日期
        self.item_onTime     = 0.0  # 上架时间
        self.item_offTime    = 0.0  # 下架时间

        # item pages
        self.item_pages      = {}
        self.shop_id         = ''   # 店铺ID
        self.shop_name       = ''   # 店铺Name
        self.item_id         = ''   # 商品ID

        # 商品属性
        self.item_sellerId   = ''   # 卖家ID
        self.item_catId      = ''   # 叶子类目ID
        self.item_rootCatId  = ''   # 父类目ID
        self.item_url        = ''   # 商品链接
        self.item_name       = ''   # 商品名称
        self.item_title      = ''   # 商品标题
        self.item_subtitle   = ''   # 商品副标题
        self.item_postFree   = False # 是否包邮
        self.item_stock      = 0    # 商品库存
        self.item_favorites  = 0    # 收藏人气
        self.item_brand      = ''   # 商品品牌

        # 商品交易
        self.item_sellCount  = 0    # 商品成交笔数
        self.item_payCount   = 0    # 商品交易中笔数
        self.item_goodCount  = 0    # 商品成功笔数
        self.item_refundCount= 0    # 商品退款数

        # 商品图片
        self.item_mPicUrl    = ''   # 主图链接
        self.item_mPicPath   = ''   # 主图路径
        self.item_picUrls    = []   # 图片链接

        # 商品价格
        self.item_fixPrice   = ''   # 一口价
        self.item_promoPrice = ''   # 促销价
        self.item_mobiPrice  = ''   # 手机专享价
        self.item_jhsPrice   = ''   # 聚划算价格
        self.item_coupon     = ''   # 优惠信息
        self.item_params     = {}   # 规格参数列表
        self.item_promises   = []   # 服务承诺

        # 商品中位数价格
        self.item_midPrice   = ''   # 中位数价格

        # 商品SKU
        self.item_skumap     = {}   # 商品sku映射
        self.item_skuRmap    = {}   # 商品sku逆映射
        self.item_skuAttrvalRmap = {} # 商品sku属性值逆映射

        # SKU属性
        self.skus            = {}   # sku实例字典
        self.sku_attrmap     = {}   # sku属性映射
        self.sku_attrvalmap  = {}   # sku属性值映射

        # 成交记录
        self.deals           = []
        self.deal_totalNum   = 0
        self.deal_earlyTime  = 0.0
        self.deal_lastTime   = 0.0

        # 评价记录
        self.item_rateTotal  = 0    # 商品评价总数

        # 大家都在说
        self.everyone_tags   = []

    def defValue(self, v):
        return v.strip() if v.find(r'默认') == -1 else u'默认'

    # item页面
    def itemPage(self, _time, _sid, _id, _pages):
        # crawl time
        self.crawling_time = _time

        # shop id
        self.shop_id    = _sid

        # item id
        self.item_id    = _id

        # page list
        self.item_pages = _pages

    # 读redis数据库的历史商品抓取记录
    def itemCrawl(self,i_val):
        keys  = [self.shop_type, self.item_id]
        #i_val = self.redisAccess.read_tbitem(keys)
        if i_val:
            c_time, s_id, i_title, i_img, d_time, on_time = i_val
            self.crawled_time  = c_time
            self.crawled_title = i_title
            self.crawled_img   = i_img
            self.deal_deadLine = d_time
            self.crawled_onTime = on_time
        else:
            # 如果上次抓取的商品列表内没有此商品，初步判断商品为上新
            self.item_crawled = False
    """
    # 读redis数据库的历史商品抓取记录
    def itemCrawl(self):
        keys  = [self.shop_type, self.item_id]
        i_val = self.redisAccess.read_tbitem(keys)
        if i_val:
            c_time, s_id, i_title, i_img, d_time, on_time = i_val
            self.crawled_time  = c_time
            self.crawled_title = i_title
            self.crawled_img   = i_img
            self.deal_deadLine = d_time
            self.crawled_onTime = on_time
        else:
            # 如果上次抓取的商品列表内没有此商品，初步判断商品为上新
            self.item_crawled = False
    """

    # 修正上新状态 - Plan B
    def itemStatus(self):
        # 计算t/on日期
        t    = self.crawling_time       # 本次抓取时间
        T    = int(Common.day_ss(t))    # 本次抓取日期

        t_on = self.item_onTime         # 上架时间
        T_on = int(Common.day_ss(t_on)) # 上架日期

        # 上次没有抓取到,本次抓取日期T抓取到商品,进行如下判断：
        # 如果上架时间为空,则取上架日期T_on; 如果上架时间不为空且上架日期T_on=T,则上新日期为上架日期T_on
        if not self.item_crawled:
            if t_on < Config.g_zeroValue: self.item_newTime = T_on
            if t_on > Config.g_zeroValue and T_on == T: self.item_newTime = T_on

        # 如果上架时间不为空，将上架时间保存到redis内商品对应的上架时间
        if t_on > Config.g_zeroValue and self.crawled_onTime < Config.g_zeroValue: self.crawled_onTime = t_on

    # 计算商品价
    def itemPrice(self, prices):
        if len(prices) == 0: return ''
        p_min, p_max = min(prices), max(prices)

        if p_min == p_max:
            price = '%8.2f' %(p_min)
        else:
            price = '%8.2f-%8.2f' %(p_min, p_max)
        return price

    # sku attr values
    def itemSkuAttr(self, sku_attrid):
        attrval_list = []
        attrs = sku_attrid.split(';')
        #print '# itemSkuAttr() : ', sku_attrid, attrs

        for attr in attrs:
            p_id, v_id = attr.split(':')
            p_val, v_val = '默认', '默认'

            if p_id in self.sku_attrmap.keys(): p_val = self.sku_attrmap[p_id]
            if v_id in self.sku_attrvalmap.keys(): v_val = self.sku_attrvalmap[v_id]

            #print '## itemSkuAttr() : ', p_id, v_id, p_val, v_val
            attrval_list.append('%s:%s' %(p_val, v_val))
        return attrval_list

    # 输出商品规格
    def outItemParams(self):
        params = []
        for (k, v) in self.item_params.items():
            s = '%s:%s' %(k, v)
            params.append(s)
        return ';'.join(params)

    # 存储商品主图
    def saveItemPicture(self, url):
        _tag = Common.now_ss()
        path_name = Config.imagePath + _tag + '/item'
        file_name = 'item_' + self.item_id + '_' + _tag + '.jpg'
        self.item_mPicPath = path_name + '/' + file_name

    # 大家都在说标签序列化
    def everyTag_s(self):
        s = ''
        for tag in self.everyone_tags:
            s += ','.join(tag) + ';'
        return s[:-1]

    # 更新抓取记录 redis
    def outItemCrawl(self):
        return (self.shop_id,self.shop_name,self.item_catId,self.item_stock,self.item_favorites,self.item_brand)

        # 写入redis
        #keys = [self.shop_type, self.item_id]
        #val  = (self.crawling_time,self.shop_id,self.item_title,self.item_mPicUrl,self.deal_lastTime,self.crawled_onTime)
        #self.redisAccess.write_tbitem(keys, val)

    # 输出商品成交记录
    def outItemDeal(self):
        s = ''
        for d in self.deals:
            s += d.outDeal(self.crawling_time, self.shop_id, self.item_id)
        return s

    # 输出商品sku记录
    def outItemSkuSql(self):
        sku_sqls = []
        for sku in self.skus.values():
            sku_sqls.append(sku.outSkuSql(self.crawling_time,self.item_catId, self.shop_id, self.item_id))
        return sku_sqls
