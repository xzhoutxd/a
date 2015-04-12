#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import base.Config as Config
import base.Common as Common
from Sku import Sku

class TBSku(Sku):
    '''A class of taobao sku'''
    def __init__(self):
        # parent construct
        Sku.__init__(self)

        self.tjbRed       = ''  # 淘金币
        self.tjbPrice     = ''  # 淘金币价格

    # 淘金币
    def setTjb(self, red, price):
        self.tjbRed, self.tjbPrice = red, price

    def outTjb(self):
        s = '%s%s%s%s' %(Config.delim, self.tjbRed, Config.delim, self.tjbPrice)
        return s

    # 输出sku
    def outSkuSql(self, c_time, c_id, s_id, i_id):
        # 抓取时间,店铺ID,商品ID,SKU ID,叶子类目ID,SKU属性ID,SKU属性值序列,库存,一口价,促销价,手机专享价,聚划算价格,销售占比
        sku = (Common.time_s(c_time),s_id,i_id,self.id,c_id,self.attrid,self.outAttrvals(),self.stock,self.price,self.promoPrice,self.mobiPrice,self.jhsPrice,self.salePercent)
        return sku
