#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import base.Config as Config
import base.Common as Common

class Sku():
    '''A class of sku'''
    def __init__(self):
        # sku
        self.id           = 'def'      # SKU ID
        self.attrid       = 'def:def'  # SKU属性键, attrid1;attrid2;...
        self.attrvals     = ''         # SKU属性值, [attrval1;attrval2;...]
        self.stock        = ''         # 库存
        self.price        = ''         # 一口价
        self.promoPrice   = ''         # 促销价
        self.mobiPrice    = ''         # 手机专享价
        self.jhsPrice     = ''         # 聚划算价
        self.salePercent  = '0.0'        # SKU销售占比

        # 促销
        #self.promos       = {}  # 促销字典

    # SKU基本属性
    def setSku(self, skuId, attrId, attrvals, stock, price, promoPrice, mobiPrice, jhsPrice):
        self.id, self.attrid, self.attrvals, self.stock, self.price, self.promoPrice, self.mobiPrice, self.jhsPrice = skuId, attrId, sorted(attrvals), stock, price.strip(), promoPrice.strip(), mobiPrice.strip(), jhsPrice.strip()

    def isSku(self, attrval_list):
        return sorted(self.attrvals) == sorted(attrval_list)

    def isSkuAttrs(self, attrval_list):
        list_len = len(attrval_list)
        attr_vals= sorted(attrval_list)

        # sku属性值个数不同
        if list_len != len(self.attrvals): return False
        #print '# isSkuAttrs 1:', ','.join(attr_vals)
        #print '# isSkuAttrs 2:', ','.join(self.attrvals)

        for i in range(0, list_len):
            if self.attrvals[i].find(attr_vals[i]) == -1:
                return False
        return True

    # sku属性值
    def outAttrvals(self):
        return ';'.join(sorted(self.attrvals))

class Promotion():
    '''A class of promotion'''
    def __init__(self):
        self.ptype     = ''
        self.price     = ''
        self.startTime = ''
        self.endTime   = ''
 
    # 促销属性
    def setPromotion(self, ptype, price, startTime, endTime):
        self.ptype, self.price, self.startTime, self.endTime = ptype, price, startTime, endTime
 
    def outPromotion(self):
        s = '%s,%s,%s,%s' %(self.ptype, self.price, Common.time_s(self.startTime), Common.time_s(self.endTime))
        return s
