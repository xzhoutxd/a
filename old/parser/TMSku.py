#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import base.Config as Config
import base.Common as Common
from Sku import Sku

class TMSku(Sku):
    '''A class of tmall sku'''
    def __init__(self):
        # parent construct
        Sku.__init__(self)

        self.presalePrice = ''  # 预售价
        self.presaleAmount= ''  # 预付金额

    # SKU预售属性
    def setPresale(self, presalePrice, presaleAmount):
        self.presalePrice, self.presaleAmount = presalePrice, presaleAmount

    # 输出sku
    def outSkuSql(self, c_time, c_id, s_id, i_id):
        # 抓取时间,店铺ID,商品ID,SKU ID,叶子类目ID,SKU属性ID,SKU属性值序列,库存,一口价,促销价,手机专享价,聚划算价格,预售价格,预付金额,销售占比
        sku = (Common.time_s(c_time),s_id,i_id,self.id,c_id,self.attrid,self.outAttrvals(),self.stock,self.price,self.promoPrice,self.mobiPrice,self.jhsPrice,self.presalePrice,self.presaleAmount,self.salePercent)
        return sku
