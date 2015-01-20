#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import re
import json
#import base.Common as Common
import parser.Common as Common
#import base.Config as Config
import parser.Config as Config
from parserItem import Item
#from Deal import Deal
#from TBSku import TBSku

class PTBItem(Item):
    '''A class to parse taobao item page'''
    def __init__(self):
        # parent construct
        Item.__init__(self)

        # 店铺类型
        self.shop_type       = '2'

        # 淘宝商品属性
        self.item_7dReturn   =  False  # 7天无理由退货
        self.tjb_maxPercent  =  ''     # 淘金币
        self.item_deliveryTime= ''     # 卖家承诺发货时间

        # 商品好评，中评，差评和追加
        self.item_goodRateCount  = ''
        self.item_flatRateCount  = ''
        self.item_badRateCount   = ''
        self.item_appendRateCount= ''

        # 评价标签
        self.rate_tags           = []
        
    def itemConfig(self):
        url, page = self.item_pages['item-home']

        # 商品链接
        self.item_url = url

        # 商品名称
        m = re.search(r'<title>(.+?)</title>', page, flags=re.S)
        if m:
            title = Common.htmlDecode_s(m.group(1).strip())
            self.item_name = title.split('-淘宝网')[0].strip()

        # 店铺Name
        m = re.search(r'<div class="tb-shop-name">.+?<strong>\s+<a.+?title="(.+?)".+?>.+?</a>\s+</strong>', page, flags=re.S)
        if m: self.shop_name = m.group(1)

        # Seller ID
        m = re.search(r'sellerId:"(\d+)"', page)
        if m: self.item_sellerId = m.group(1)

        # 叶子类目ID  data-catid ="50010850" data-rootid="16"
        m = re.search(r'data-catid\s="(\d+)"', page)
        if m: self.item_catId = m.group(1)

        # 父类目ID
        m = re.search(r'data-rootid="(\d+)"', page)
        if m: self.item_rootCatId = m.group(1)     

        # 主标题
        m = re.search(r'<h\d class="tb-main-title".*?>(.+?)</h\d>', page, flags=re.S)
        if m: self.item_title = Common.htmlContent(Common.htmlDecode_s(m.group(1))).strip()

        # 副标题
        m = re.search(r'<p class="tb-subtitle">(.+?)</p>', page, flags=re.S)
        if m: self.item_subtitle = Common.htmlContent(Common.htmlDecode_s(m.group(1))).strip()

        # 商品规格参数
        p = re.compile(r'<li title=".+?">(.+?)</li>')
        for m in p.finditer(page):
            param = m.group(1).replace('：', ':')
            p_name, p_value = param.split(':', 1)
            self.item_params[p_name] = Common.trim_s(p_value)
            if p_name.find('品牌') != -1:
                self.item_brand = Common.htmlDecode(p_value).strip()

        # 商品成交链接
        m = re.search(r'data-api="(.+?)"', page)
        if m:
            d_url = m.group(1)
            
            # 上架时间
            r = re.search(r'starts=(\d+)&', d_url)
            if r : self.item_onTime  = float(r.group(1))/1000

            # 下架时间
            r = re.search(r'ends=(\d+)&', d_url)
            if r : self.item_offTime = float(r.group(1))/1000
            
        # 成交数量页
        _key = 'item-dealnum'
        if _key in self.item_pages.keys():
            data = self.item_pages[_key][1]

            r = re.search(r'quanity:\s*(\d+)', data, flags = re.S)
            if r: self.item_sellCount = r.group(1)

            r = re.search(r'confirmGoods:\s*(\d+)', data, flags = re.S)
            if r: self.item_goodCount = r.group(1)

            r = re.search(r'paySuccess:\s*(\d+)', data, flags = re.S)
            if r: self.item_payCount  = r.group(1)
            
            r = re.search(r'refundCount:\s*(\d+)', data, flags = re.S)
            if r: self.item_refundCount = r.group(1)

        # 评价数量页
        _key = 'item-ratenum'
        if _key in self.item_pages.keys():
            data = self.item_pages[_key][1]
            
            r = re.search(r'"SM_\d+_sm-\d+":(\d+.\d+)', data)
            if r: self.item_gradeAvg  = r.group(1)
            
            r = re.search(r'"ICE_3_feedcount-\d+":(\d+)', data)
            if r: self.item_rateTotal = r.group(1)            

    # 商品服务承诺
    def itemPromises(self):
        page = self.item_pages['item-home'][1]
        m = re.search(r'<dd id="J_ServiceIconBd">(.+?)</dd>', page, flags=re.S)
        if m:
            prom_name = Common.htmlContent(m.group(1)).strip()
            self.item_promises.append(prom_name)

        # item detail page
        data = self.item_pages['item-detail'][1]
        m = re.search(r'g_config.ContractList=\[(.+?)\]', data, flags=re.S)
        if m:
            p = re.compile(r'"id":\d+,.+?,"name":"(.+?)",')
            for item in p.finditer(m.group(1)):
                prom_name = item.group(1).strip()
                self.item_promises.append(prom_name)

    # 商品图片
    def itemPicture(self):
        page = self.item_pages['item-home'][1]

        # 宝贝主图
        m = re.search(r'<img id="J_ImgBooth" data-src="(.+?)" .+?/>', page)
        if m: self.item_mPicUrl = m.group(1)

        # 宝贝图片
        m = re.search(r'<ul id="J_UlThumb" class=".+?">(.+?)</ul>', page, flags=re.S)
        if m:
            p = re.compile(r'<div class="tb-pic.+?">\s+<a href="#"><img\s+?data-src="(.+?)"\s+/>', flags=re.S)
            for u in p.finditer(m.group(1)):
                img_url = u.group(1).strip()
                if img_url.find('imgextra') != -1:
                    self.item_picUrls.append(img_url)

        # 保存宝贝主图
        #print self.item_mPicUrl, self.item_id
        self.saveItemPicture(self.item_mPicUrl)

    # 商品收藏数
    def itemFavorites(self):
        _key = 'item-favorite'
        if _key not in self.item_pages.keys(): return
        page = self.item_pages[_key][1]
        
        m = re.search(r'"ICCP_\d_\d+":(\d+)', page)
        if m: self.item_favorites = m.group(1)

    def itemStock(self):
        # 移动Web页
        page = self.item_pages['item-wap'][1]
        page = page.replace('\\','')
        # 月成交 库存
        m = re.search(r'"totalSoldQuantity":"(\d+)",.*?"quantity":"(\d+)"', page)
        if m:
            self.item_sellCount, self.item_stock = m.group(1), m.group(2)
            self.deal_totalNum = self.item_sellCount

    '''
    # item skus
    def itemSku(self):
        # 移动web端商品详情页
        page = self.item_pages['item-wap'][1]
        page = page.replace('\\','')
        #print '# itemSku wap : ', page

        # 月成交
        m = re.search(r'"totalSoldQuantity":"(\d+)",.*?"quantity":"(\d+)"', page)
        if m:
            self.item_sellCount, self.item_stock = m.group(1), m.group(2)
            self.deal_totalNum = self.item_sellCount
        #print '# 月成交 / 库存 :', self.item_sellCount, self.item_stock

        # 优惠信息
        m = re.search(r'"shopPromotion":{"title":"今日活动","descriptions":\["(.+?)"\]', page)
        if m: self.item_coupon = m.group(1).replace('"','')

        # 商品sku映射
        p = re.compile(r'"ppathIdmap":{(.+?)}', flags=re.S)
        for attrs in p.finditer(page):
            q = re.compile(r'"(\S+?;\S+?|\S+?)":"(\d+)"')
            for s in q.finditer(attrs.group(1)):
                sku_attrid, sku_id = Common.trim_s(s.group(1)), s.group(2)
                self.item_skumap[sku_id] = sku_attrid
                self.item_skuRmap[sku_attrid] = sku_id
                #print '# skumap : ', sku_id, sku_attrid

        # 默认商品sku处理        
        if len(self.item_skumap) > 0:
            sku_id, sku_attrid = 'def', 'def:def'
            self.item_skumap[sku_id] = sku_attrid
            self.item_skuRmap[sku_attrid] = sku_id

        # sku属性
        m = re.search(r'"skuProps":\[({.+?}\]})\],', page, flags=re.S)
        if m:
            sku_props = m.group(1)
            #print '# sku_props : ', sku_props
            r = re.compile(r'{"propId":"(\d+)","propName":"(.+?)","values":\[(.+?)\]}', flags=re.S)
            for prop in r.finditer(sku_props):
                prop_id, prop_name, prop_vals = prop.group(1), prop.group(2), prop.group(3)
                #print '## prop : ', prop_id, prop_name, prop_vals

                self.sku_attrmap[prop_id] = prop_name
                p = re.compile(r'{"valueId":"(\d+)","name":"(.+?)".*?}', flags=re.S)
                for v in p.finditer(prop_vals):
                    v_id, v_val = v.group(1), v.group(2)
                    #print '# sku_attrvalmap : ', prop_id, prop_name, v_id, v_val
                    self.sku_attrvalmap[v_id] = v_val
        else:
            # 默认sku处理
            prop_id, prop_name = 'def', '默认'
            self.sku_attrmap[prop_id] = prop_name

            v_id, v_val = 'def', '默认'
            self.sku_attrvalmap[v_id] = v_val

        # 移动端促销信息
        fix_prices, mobi_prices, promo_prices, jhs_prices, mid_prices = [], [], [], [], []
        m = re.search(r'"skus":\{(.+?\})}}', page, flags=re.S)
        if m:
            sku_stocks = m.group(1)
            p = re.compile(r'"(\d+)":\{"quantity":"(\d+)",.*?"priceUnits":\[({.+?})\]}', flags=re.S)

            for item in p.finditer(sku_stocks):
                # 实例化一个TBSku对象
                a_sku = TBSku()
                sku_id, sku_stock, sku_promos = item.group(1), item.group(2), item.group(3)
                #print '# a_sku : ', sku_id, sku_stock, sku_promos

                # 初始化变量
                sku_attrid, sku_attrvals, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice = 'def:def', '', '', '', '', ''

                # sku attrs
                if sku_id in self.item_skumap.keys():
                    sku_attrid   = self.item_skumap[sku_id]
                    sku_attrvals = self.itemSkuAttr(sku_attrid)
                    #print '# sku attrvals : ', sku_id, sku_attrid, sku_attrvals

                # sku移动专享价/一口价
                price_displays = []
                p = re.compile(r'{"name":"(.+?)".+?"price":"(.+?)".+?"display":"(\d+)"}', flags=re.S)
                for promo in p.finditer(sku_promos):
                    p_name, p_price, p_display = promo.group(1), promo.group(2), int(promo.group(3))
                    #print '# sku price : ', p_name, p_price, p_display

                    if p_name == '手机专享价':
                        sku_mobiPrice = p_price
                    elif p_name == '聚划算':
                        price_displays.append(p_display)
                        sku_jhsPrice  = p_price
                    else:
                        price_displays.append(p_display)
                        if p_display == 1: sku_promoPrice = p_price
                        elif p_display> 1: sku_price = p_price

                # sku价格序列
                if len(price_displays) == 1 and sku_price == '': sku_price, sku_promoPrice = sku_promoPrice, ''
    
                # 保存sku促销价格信息
                if len(sku_price)     > 0: fix_prices.append(float(sku_price))
                if len(sku_promoPrice)> 0: promo_prices.append(float(sku_promoPrice))
                if len(sku_mobiPrice) > 0: mobi_prices.append(float(sku_mobiPrice))
                if len(sku_jhsPrice)  > 0: jhs_prices.append(float(sku_jhsPrice))

                # 设置sku基本属性
                a_sku.setSku(sku_id, sku_attrid, sku_attrvals, sku_stock, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice)
                #print '# set sku : ', sku_id, sku_attrid, sku_attrvals, sku_stock, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice

                # 记录属性值到id的逆映射
                attrvals = a_sku.outAttrvals()
                self.item_skuAttrvalRmap[attrvals] = sku_id

                # 存储sku对象
                self.skus[sku_id] = a_sku
        else:
            # 实例化一个TBSku对象
            a_sku = TBSku()
            sku_id, sku_stock = 'def', self.item_stock

            # 初始化变量
            sku_attrid, sku_attrvals, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice = 'def:def', '', '', '', '', ''
            
            # sku attrs
            if sku_id in self.item_skumap.keys():
                sku_attrid = self.item_skumap[sku_id]
                sku_attrvals = self.itemSkuAttr(sku_attrid)

            # sku移动专享价/一口价
            price_displays = []
            p = re.compile(r'{"name":"(.+?)","price":"(.+?)",.*?"display":"(\d+)"}', flags=re.S)
            
            for promo in p.finditer(page):
                p_name, p_price, p_display = promo.group(1), promo.group(2), int(promo.group(3))
                if p_name == '手机专享价':
                    sku_mobiPrice = p_price
                elif p_name == '聚划算':
                    price_displays.append(p_display)
                    sku_jhsPrice  = p_price
                else:
                    price_displays.append(p_display)
                    if p_display == 1: sku_promoPrice = p_price
                    elif p_display> 1: sku_price = p_price

            # sku价格序列
            if len(price_displays) == 1 and sku_price == '': sku_price, sku_promoPrice = sku_promoPrice, ''

            # 保存sku促销价格信息
            if len(sku_price)     > 0: fix_prices.append(float(sku_price))
            if len(sku_promoPrice)> 0: promo_prices.append(float(sku_promoPrice))
            if len(sku_mobiPrice) > 0: mobi_prices.append(float(sku_mobiPrice))
            if len(sku_jhsPrice)  > 0: jhs_prices.append(float(sku_jhsPrice))

            # 设置sku基本属性
            a_sku.setSku(sku_id, sku_attrid, sku_attrvals, sku_stock, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice)
            #print '# set default sku : ', sku_id, sku_attrid, sku_stock, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice

            # 记录属性值到sku id的逆映射
            attrvals = a_sku.outAttrvals()
            self.item_skuAttrvalRmap[attrvals] = sku_id

            # 存储sku对象
            self.skus[sku_id] = a_sku

        # PC端促销信息
        page = self.item_pages['item-detail'][1]
        if page and len(page) > 0:
            #print '# itemSku pc : ', page.replace('\n','').replace('\r','')

            # 促销信息
            m = re.search(r'g_config.PromoData={(.+)\s*\}\s*;\s*g_config', page, flags=re.S)
            if m:
                p = re.compile(r'"(;\S+?;|def)":\[\s+(\{.+?\})\s+\]', flags=re.S)
                for promo in p.finditer(m.group(1)):
                    sku_attrid, sku_promo = promo.group(1), promo.group(2)
                    if sku_attrid != 'def' :
                        sku_attrid = sku_attrid[1:-1]
                    else:
                        sku_attrid = 'def:def'
                    
                    #print '# sku pc 1 : ', sku_attrid, sku_promo
                    if sku_attrid in self.item_skuRmap.keys():
                        sku_id = self.item_skuRmap[sku_attrid]

                        a_sku = None
                        if sku_id in self.skus.keys(): a_sku = self.skus[sku_id]

                        # 更新促销价
                        s = re.compile(r'{(.+?)}', flags=re.S)
                        for items in s.finditer(sku_promo):
                            r = re.compile(r'type:\s+?"(.+?)"\s*?,\s+?price:"(.+?)",\s+?limitTime:\s+?"(.*?)"', flags=re.S)
                            item = items.group(1)
                            for promo in r.finditer(item):
                                #print '## promo pc 1 : ', promo
                                p_type, p_price, p_limitTime = promo.group(1), promo.group(2), promo.group(3)
                                #print '## promo pc 2 : ', p_type, p_price, p_limitTime

                                promo_prices.append(float(p_price))                                
                                self.item_promoPrice = p_price
                                self.item_promoType  = p_type

                                if a_sku : a_sku.promoPrice = p_price

            # 淘金币
            m = re.search(r'g_config.PointData=\[(.+?)};\s+?g_config', page, flags=re.S)
            if m:
                r = re.search(r'"-2":"(.+?)<em class=\'tb-h\'>(.+?)</em>"', page) 
                if r: self.tjb_maxPercent = r.group(1) + r.group(2)

                r = re.search(r'"(\d+)":"<em class=\'tb_red\'><strong>(\d+)</strong>.+?</em>.+?<em class=\'tb_tjb_price\'>￥(.+?)</em>"', page)
                if r:
                    sku_id, tjb_red, tjb_price = r.group(1), r.group(2), r.group(3)
                    if sku_id in self.skus.keys():
                        a_sku = self.skus[sku_id]
                        a_sku.setTjb(tjb_red, tjb_price)
                    #print sku_id, tjb_red, tjb_price
        
        # 商品一口价
        if len(fix_prices) > 0:
            self.item_fixPrice = Common.trim_s(self.itemPrice(fix_prices))
            mid_prices.append(Common.median(fix_prices))

        # 商品促销价
        if len(promo_prices) > 0:
            self.item_promoPrice = Common.trim_s(self.itemPrice(promo_prices))
            mid_prices.append(Common.median(promo_prices))
            
        # 商品移动专享价
        if len(mobi_prices) > 0:
            self.item_mobiPrice  = Common.trim_s(self.itemPrice(mobi_prices))
            mid_prices.append(Common.median(mobi_prices))

        # 商品聚划算价格
        if len(jhs_prices) > 0 :
            self.item_jhsPrice = Common.trim_s(self.itemPrice(jhs_prices))
            mid_prices.append(Common.median(jhs_prices))

        # 商品中位数价格
        if len(mid_prices) > 0:
            self.item_midPrice = ('%8.2f' %min(mid_prices)).strip()

        # 商品运费
        page = self.item_pages['item-detail'][1]
        if page and len(page) > 0:
            m = re.search(r'g_config.DeliveryFee=(\w+)', page, flags=re.S)
            if m: self.item_postFree = (m.group(1) == 'false')

            # 卖家承诺N小时内发货
            m = re.search(r'g_config.PostageFee={(.+?)}', page, flags=re.S)
            if m:
                r = re.search(r'estimation:\'卖家承诺(\d+)小时内发货\'', m.group(1))
                if r: self.item_deliveryTime = r.group(1)

            # 7天退货
            m = re.search(r'g_config.ContractList=\[(.+?)\]', page, flags=re.S)
            if m:
                r = re.search(r'"name":"7天.+?"', m.group(1))
                if r: self.item_7dReturn = True

        # 如果sku列表有多于1个sku id，则去掉缺省sku id(def)
        if len(self.skus) > 1 and self.skus.has_key('def') : self.skus.pop('def')

    def aDealRecord(self, data):
        # 预处理
        data = data.replace('\\', '')
        d_timestamps = []; d_crawltype = 0

        p = re.compile(r'<tbody>(.+?)</tbody>', flags=re.S)
        for pg in p.finditer(data):
            p_data = pg.group(1)
            p_data = p_data.replace(r'<span class=tb-anonymous>**</span>', r'**')

            # 遍历成交记录        
            p = re.compile(r'<tr .+?>(.+?)</tr>')
            for item in p.finditer(p_data):
                deal = item.group(1)

                # 初始化成交记录变量
                d_ctime, d_buyer, d_credit, d_member, d_price, d_prom, d_amount  = '', '', '', '', '', '', '1'

                # deal time
                d = re.search(r'<td class="tb-start">(.+?)</td>', deal)
                if d:
                    d_ctime = d.group(1)
                else: continue
    
                if d_ctime and d_ctime != '':
                    d_timestamp = Common.str2timestamp(d_ctime)
    
                    # 到了截止时间1(上次抓取最晚时间), 将抓取类型设置为1, 表示追加的抓取成交
                    if self.deal_deadLine > Config.g_zeroValue and d_timestamp <= self.deal_deadLine:
                        d_crawltype = 1

                    # 记录成交时间
                    if d_crawltype == 0 : d_timestamps.append(d_timestamp)
    
                # 买家别名
                d = re.search(r'<span class="tb-sellnick">(.+?)</span>', deal)
                if d: d_buyer = Common.htmlContent(d.group(1).strip())

                """
                # 买家信用
                d = re.search(r'<img src="\S+?" title="(\S+?)个买家信用积分" border="\d+" align="\w+" class="rank"\s*/>', deal)
                if d:
                    credit_rank = d.group(1)
                    if credit_rank in Config.g_TBCreditDict.keys(): d_credit = Config.g_TBCreditDict[credit_rank]
                """

                # 会员级别
                d = re.search(r'<a target="_blank"\s+href="http://vip.taobao.com"\s+title="(\S+?)会员">', deal)
                if d: d_member = d.group(1)

                # 促销类型 ：促销活动
                d = re.search(r'<a title="(.+?)" class="tb-promo">', deal)
                if d: d_prom = d.group(1).strip()
    
                #<div class="tb-sku-wrap "> <p>颜色分类:黑色现货</p> <p>尺码:L</p>
                d_attrvals = []
                d = re.search(r'<div class="tb-sku-wrap .*?">(.+?)</div', deal)
                if d:
                    attrvals = d.group(1)
                    s = re.compile(r'<p>(.+?)</p>')
    
                    for val in s.finditer(attrvals):
                        p_val, v_val, attrval = '', '', val.group(1).strip()
    
                        if attrval.find(':') == -1:
                            p_val, v_val = attrval, attrval 
                        else:
                            p_val, v_val = attrval.split(':')
    
                        attrval = self.defValue(p_val) + ':' + self.defValue(v_val)
                        d_attrvals.append(attrval)
    
                d = re.search(r'<em class="tb-rmb-num">(.+?)</em>', deal)
                if d: d_price = d.group(1)
    
                d = re.search(r'<td class="tb-amount">(\d+)</td>', deal)
                if d: d_amount = d.group(1)
    
                # 成交抓取类型,买家别名,买家信用级别，买家会员级别,成交时间,购买价格,购买数量,促销类别,属性列表
                a_Deal = Deal()
                a_Deal.setDeal(d_crawltype, d_buyer, d_credit, d_member, d_ctime, d_price, d_amount, d_prom, d_attrvals)
                self.deals.append(a_Deal)

        # 返回本页成交时间列表
        return d_timestamps

    def dealRecords(self):
        # 成交成交时间戳列表
        min_dtimes, max_dtimes = [], []
        
        # 无成交
        if 'item.deal' not in self.item_pages.keys(): return

        # 有成交
        data = self.item_pages['item.deal']
        d = self.aDealRecord(data)
        if len(d) > 0:
            min_dtimes.append(min(d)); max_dtimes.append(max(d))
 
        if len(min_dtimes) > 0 : self.deal_earlyTime = min(min_dtimes)
        if len(max_dtimes) > 0 : self.deal_lastTime  = max(max_dtimes)

    # 成交记录SKU占比
    def dealSkuPercent(self):
        _key = 'item-dealsku'
        if _key not in self.item_pages.keys(): return
        data = self.item_pages[_key][1]

#         # 买家信用级别分布  - "count":27,"level":"4"
#         p = re.compile(r'"count":(\d+),"level":"(\d)"')
#         for m in p.finditer(data):
#             b_count, b_level = m.group(1), m.group(2)
#             print b_level, b_count

        # SKU销量分布 
        sku = re.search(r'popular\s*:\s*\[(.+?)\]\s*}', data)
        if sku:
            sku_json = Common.jsonDecode(sku.group(1))
            p = re.compile(r'\[\'(\S+)\',(\S+)\]')
            for s in p.finditer(sku_json):
                sku_vals, sku_percent = Common.trim_s(s.group(1)), s.group(2)
                
                #print '# dealSkuPercent 1:', self.item_id, sku_vals, sku_percent
                if sku_vals.find('默认') != -1: sku_vals = '默认'

                # 正常类目
                if sku_vals in self.item_skuAttrvalRmap.keys():
                    sku_id = self.item_skuAttrvalRmap[sku_vals]
                    self.skus[sku_id].salePercent = ('%6.2f' %(float(sku_percent))).strip()
                # 童装类目
                else:
                    # 玫红色/18码/内长约17.5cm => 玫红色 + 18码/内长约17.5cm
                    attr_list = sorted(sku_vals.split('/', 1))
                    for sku in self.skus.values():
                        if sku.isSkuAttrs(attr_list):
                            sku.salePercent = ('%6.2f' %(float(sku_percent))).strip()
                            #print '# dealSkuPercent 2:', self.item_id, sku_percent
                            break

    def rateCumPercent(self):
        # item cum page
        _key = 'item-ratetag'
        if _key not in self.item_pages.keys(): return
        data = self.item_pages[_key][1]

        # 追加评论、好评数、中评数、差评数
        rate_good, rate_normal, rate_bad, rate_add = '', '', '', ''

        m = re.search(r'"good":(\d+)', data)
        if m : rate_good = m.group(1)

        m = re.search(r'"normal":(\d+)', data)
        if m : rate_normal = m.group(1)

        m = re.search(r'"bad":(\d+)', data)
        if m : rate_bad = m.group(1)

        m = re.search(r'"additional":(\d+)', data)
        if m : rate_add = m.group(1)
        #print '# rateCumPercent : ', rate_good, rate_normal, rate_bad, rate_add

        self.item_goodRateCount  = rate_good
        self.item_flatRateCount  = rate_normal
        self.item_badRateCount   = rate_bad
        self.item_appendRateCount= rate_add

    def rateTagPercent(self):
        # item tag page
        _key = 'item-ratetag'
        if _key not in self.item_pages.keys(): return
        data = self.item_pages[_key][1]

        # size and color
        m = re.search(r'"impress":(\[(.+?)\])',data)
        if m:
            t_list = m.group(1)
            p = re.compile(r'"title":"(.+?)","count":(\d+),"value":(.+?),')
            for tag in p.finditer(t_list):
                t_count,t_title,t_posi = tag.group(1),tag.group(2),tag.group(3)
                self.rate_tags.append((t_title, t_count, t_posi))
                #print t_title, t_count, t_posi
    '''

    # 解析商品网页
    #def antPage(self, _time, _sid, _id, _pages):
        #self.itemPage(_time, _sid, _id, _pages)
        #self.itemCrawl()
    def antPage(self, crawl_obj):
        if crawl_obj.item_pages != {}:
            self.itemPage(crawl_obj.crawling_time, crawl_obj.shop_id, crawl_obj.item_id, crawl_obj.item_pages)

            val = (crawl_obj.crawling_time, crawl_obj.shop_id, crawl_obj.item_name, '', crawl_obj.deal_deadLine, 0.0)
            self.itemCrawl(val)
            self.itemConfig()
            #self.itemPicture()
            #self.itemPromises()
            self.itemFavorites()
            self.itemStock()
            #self.itemSku()

            #self.dealSkuPercent()
            #self.rateTagPercent()
            #self.rateCumPercent()
            
            self.itemStatus()
            #self.outItemCrawl()

    # 评价标签序列化
    def tag_s(self):
        s = ''
        for tag in self.rate_tags:
            s += ','.join(tag) + ';'
        return s[:-1]

    # 输出TBItem
    def outItemSql(self):
        # 宝贝图片链接
        pic1_url, pic2_url, pic3_url, pic4_url = '', '', '', ''

        if len(self.item_picUrls) > 0: pic1_url = self.item_picUrls[0]
        if len(self.item_picUrls) > 1: pic2_url = self.item_picUrls[1]
        if len(self.item_picUrls) > 2: pic3_url = self.item_picUrls[2]
        if len(self.item_picUrls) > 3: pic4_url = self.item_picUrls[3]
        
        # 主标题是否变化
        title_change  = ('0' if self.crawled_title == self.item_title else '1') 

        # 主图是否变化
        mainPic_change= ('0' if self.crawled_img == self.item_mPicUrl else '1')

        # 是否包邮
        postageFree   = ('1' if self.item_postFree else '0')

        # 7天退货
        is_7dReturn   = ('1' if self.item_7dReturn else '0')

        # 宝贝印象标签
        impr_tag  = self.tag_s()

        # 抓取时间,店铺ID,商品ID,商品名称,商品链接,商品收藏数,商品规格参数,后台父类目ID,后台叶子类目ID,上新日期,上架时间,下架时间,主标题,主标题是否变化,副标题,主图链接,主图是否变化,主图文件路径,图片1链接,图片2链接,图片3链接,图片4链接,一口价,促销价,手机专享价,聚划算价,优惠信息,30天内售出笔数,交易成功笔数,是否包邮,承诺N个小时发货,7天退货承诺,评价条数,好评数,中评数,差评数,追评数,30天内交易中笔数,30天内交易成功笔数,30天内纠纷退款笔数,大家印象标签列表,商品中位数价格
        item = (Common.time_s(self.crawling_time),self.shop_id,self.item_id,self.item_name,self.item_url,self.item_favorites,self.outItemParams(),self.item_rootCatId,self.item_catId,Common.day_s(self.item_newTime),Common.time_s(self.item_onTime),Common.time_s(self.item_offTime),self.item_title,title_change,self.item_subtitle,self.item_mPicUrl,mainPic_change,self.item_mPicPath,pic1_url,pic2_url,pic3_url,pic4_url,self.item_fixPrice,self.item_promoPrice,self.item_mobiPrice,self.item_jhsPrice,self.item_coupon,self.item_sellCount,self.item_goodCount,postageFree,self.item_deliveryTime,is_7dReturn,self.item_rateTotal,self.item_goodRateCount,self.item_flatRateCount,self.item_badRateCount,self.item_appendRateCount,self.item_payCount,self.item_goodCount,self.item_refundCount,impr_tag,self.item_midPrice)
        return item
    
if __name__ == '__main__':
    i = TBItem()
    i = None
    
