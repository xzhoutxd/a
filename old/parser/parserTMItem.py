#-*- coding:utf-8 -*-
#!/usr/local/bin/python

import re
#import base.Config as Config
import parser.Config as Config
#import base.Common as Common
import parser.Common as Common
from parserItem import Item
#from Deal import Deal
#from TMSku import TMSku

class PTMItem(Item):
    '''A class of tmall item'''
    def __init__(self):
        # parent construct
        Item.__init__(self)

        # 店铺类型
        self.shop_type     = '1'

        # 商品属性
        self.item_spuId    = ''  # SPU ID
        self.item_brandId  = ''  # 商品品牌ID
        self.item_tmCount  = ''  # 天猫积分
        self.item_gradeAvg = ''  # 商品评价得分

        # 预售信息
        self.item_presalePrice  = ''
        self.item_presaleAmount = ''
        self.item_presaleNum    = 0

        # 评价标签
        self.rate_tags          = {}

    # item configuration
    def itemConfig(self):
        url, page = self.item_pages['item-home']

        # 商品链接
        self.item_url = url

        # 店铺ID/商品ID
        m = re.search(r'<div id="LineZing".+?shopid="(\d+)".+?itemid="(\d+)"></div>', page)
        if m: self.shop_id, self.item_id = m.group(1), m.group(2)

        # 店铺Name
        m = re.search(r'<a class="slogo-shopname".+?><strong>(.+?)</strong></a>', page)
        if m: self.shop_name = m.group(1)

        # SPU ID
        m = re.search(r'"spuId":"(\d+)"', page)
        if m: self.item_spuId = m.group(1)

        # 掌柜ID
        m = re.search(r'"sellerId":(\d+)', page)
        if m: self.item_sellerId = m.group(1)

        # 叶子类目ID
        m = re.search(r'"categoryId":"(\d+)"', page)
        if m: self.item_catId = m.group(1)

        # 根类目
        m = re.search(r'"rootCatId":"(\d+)"', page)
        if m: self.item_rootCatId = m.group(1)  

        # 品牌ID
        m = re.search(r'"brandId":"(\d+)"', page)
        if m: self.item_brandId = m.group(1)   

        # 商品名称
        m = re.search(r'<title>(.+?)</title>', page, flags=re.S)
        if m:
            title = Common.htmlDecode_s(m.group(1).strip())
            self.item_name = title.split('-tmall')[0].strip()
            
        # 商品标题
        m = re.search(r'<div class="tb-detail-hd">\s+?<h\d \S+?>(.+?)</h\d>.+?<p>(.+?)</p>', page, flags=re.S)
        if m:
            self.item_title, i_subtitle = Common.htmlContent(m.group(1)).strip(), m.group(2).strip()
            i_subtitles = i_subtitle.split('\n')
            self.item_subtitle = Common.trim_s(','.join(i_subtitles))

        # 商品规格
        p = re.compile(r'<li .*?title="\S+">(.+?)</li>')
        for m in p.finditer(page):
            param  = m.group(1).replace('：', ':')
            p_name, p_value = param.split(':', 1)            
            self.item_params[p_name] = Common.htmlDecode(p_value).strip()

        # 成交记录链接
        m = re.search(r'detail:params="(\S+?),(\w+?)"', page)
        if m:
            d_url = m.group(1)

            # 累积成交数
            r = re.search(r'totalSQ=(\d+)', d_url)
            if r : self.deal_totalNum = r.group(1)

            # 上架时间
            r = re.search(r'starts=(\d+)&', d_url)
            if r : self.item_onTime  = float(r.group(1))/1000

            # 下架时间
            r = re.search(r'ends=(\d+)&', d_url)
            if r : self.item_offTime = float(r.group(1))/1000

        # 商品评价数
        _key = 'item-ratenum'
        if _key not in self.item_pages.keys(): return
        data = self.item_pages[_key][1]

        m = re.search(r'"gradeAvg":(.+?),', data)
        if m: self.item_gradeAvg = m.group(1)
        
        m = re.search(r'"rateTotal":(\d+)', data)
        if m: self.item_rateTotal = m.group(1)

    # 商品服务承诺
    def itemPromises(self):
        page = self.item_pages['item-home'][1]

        m = re.search(r'<ul class="tb-serPromise">(.+?)</ul>', page, flags=re.S)
        if m:
            p = re.compile(r'<li.+?>\s*<a.+?>(.+?)</a></li>', flags=re.S)
            for item in p.finditer(m.group(1)):
                prom = Common.trim_s(Common.htmlContent(item.group(1)))
                self.item_promises.append(prom)

    # 商品图片
    def itemPicture(self):
        page = self.item_pages['item-home'][1]

        # 宝贝主图
        m = re.search(r'<img id="J_ImgBooth" .+? src="(.+?)" .+?/>', page)
        if m: self.item_mPicUrl = m.group(1)

        # 宝贝图片
        m = re.search(r'<ul id="J_UlThumb" class=".+?">(.+?)</ul>', page, flags=re.S)
        if m :
            p = re.compile(r'<li class="">\s+?<a href="#"><img\s+?src="(.+?)"\s+?/>', flags=re.S)
            for u in p.finditer(m.group(1)):
                img_url = u.group(1).strip()
                if img_url.find('imgextra') != -1: self.item_picUrls.append(img_url)

        # 保存宝贝主图
        self.saveItemPicture(self.item_mPicUrl)

    # 商品收藏数
    def itemFavorites(self):
        _key = 'item-favorite'
        if _key not in self.item_pages.keys(): return
        page = self.item_pages[_key][1]

        m = re.search(r'"ICCP_\d_\d+":(\d+)', page)
        if m: self.item_favorites = m.group(1)

    # 商品库存
    def itemStock(self):
        # 移动Web页
        page = self.item_pages['item-wap'][1]
        m = re.search(r'"inventoryDO":{.+?"icTotalQuantity":(\d+),', page)
        if m: self.item_stock = m.group(1)

    '''
    # 商品SKU属性-移动端
    def itemSku(self):
        # 移动Web页
        page = self.item_pages['item-wap'][1]
        
        # 商品月成交
        m = re.search(r'"sellCount":(\d+)', page)
        if m: self.item_sellCount = m.group(1)

        # 商品天猫积分
        m = re.search(r'"tmallPoints":(\d+)', page)
        if m: self.item_tmCount = m.group(1)

        # 商品运费
        m = re.search(r'"postageFree":(\w+),', page)
        if m: self.item_postFree = (m.group(1) != 'false')

        # 优惠信息
        m = re.search(r'"promotionPlan":\["(.+?)"\]', page)
        if m: self.item_coupon = m.group(1).replace('"','')     

        # sku映射
        m = re.search(r'"skuMap":{(.+?})},"skuName"', page, flags=re.S)
        if m:
            #print '# sku map 1 : ', m.group(1)
            u = re.compile(r'";(.*?);":{.*?"price":".+?",.+?,"skuId":(\d+),.+?}')
            for s in u.finditer(m.group(1)):
                sku_attrid, sku_id = Common.trim_s(s.group(1)), s.group(2)
                #print '# sku map 2 : ', sku_attrid, sku_id
                self.item_skumap[sku_id] = sku_attrid
        else:
            # 默认sku处理
            sku_id, sku_attrid = 'def', 'def:def'
            self.item_skumap[sku_id] = sku_attrid

        # sku属性
        m = re.search(r'"skuName":\[(.+?}\]})\],', page, flags=re.S)
        if m:
            attrs = m.group(1)
            p = re.compile(r'{"id":(\d+),"text":"(.+?)","values":\[(.+?)\]}', flags=re.S)

            for attr in p.finditer(attrs):
                prop_id, prop_name, prop_vals = attr.group(1), attr.group(2), attr.group(3)
                #print '# sku attrs : ', prop_id, prop_name, prop_vals
                self.sku_attrmap[prop_id] = prop_name

                r = re.compile(r'{"id":(\d+),"text":"(.+?)"}', flags=re.S)
                for v in r.finditer(prop_vals):
                    v_id, v_val = v.group(1), v.group(2)
                    #print '# sku attr vals : ', v_id, v_val
                    self.sku_attrvalmap[v_id] = v_val
        else:
            # 默认sku处理
            prop_id, prop_name = 'def', '默认'
            self.sku_attrmap[prop_id] = prop_name

            v_id, v_val = 'def', '默认'
            self.sku_attrvalmap[v_id] = v_val
 
        # 商品库存
        sku_stockMap = {}
        m = re.search(r'"inventoryDO":{.+?"icTotalQuantity":(\d+),', page)
        if m: self.item_stock = m.group(1)

        # sku库存
        m = re.search(r'"inventoryDO":{.+?"skuQuantity":{(.*?})},', page)
        if m:
            quantities = m.group(1)
            p = re.compile(r'"(\d+)":{.+?,"quantity":(\d+),')
            for s in p.finditer(quantities):
                sku_id, sku_stock = s.group(1), s.group(2)
                sku_stockMap[sku_id] = sku_stock
                #print '# sku stock : ', self.item_stock, sku_id, sku_stock

        # 默认sku处理
        if len(sku_stockMap) == 0:
            sku_id, sku_stock = 'def', self.item_stock
            sku_stockMap[sku_id] = sku_stock

        # 商品一口价
        m = re.search(r'<section id="s-price">\s+?<div class="item"><b class="ui-yen">&yen;(.+?)</b></div>\s+?</section>', page, flags=re.S)
        if m: self.item_fixPrice = Common.trim_s(m.group(1))

        # sku促销信息
        fix_prices, mobi_prices, promo_prices, jhs_prices, presale_prices, mid_prices = [], [], [], [], [], []
        p = re.compile(r'"(\d+|defaultPriceInfoDO)":{"areaSold":(.+?,"tmallPoints":\d+.*?)},', flags=re.S)
        for s in p.finditer(page):
            # 实例化一个TMSku对象
            a_sku = TMSku()

            sku_id, sku_priceInfo = s.group(1), s.group(2)
            if sku_id == 'defaultPriceInfoDO': sku_id = 'def'
            #print '# sku : ', sku_id, sku_priceInfo

            # 分拆价格信息
            sku_prices, sku_promoPrices, sku_promoList, sku_suggestPromoList, sku_wrtInfo = '', '', '', '', ''
            r = re.search(r'"price":{(.+?)},"', sku_priceInfo)
            if r:  sku_prices = r.group(1)

            r = re.search(r'"promPrice":({.+?}|null)', sku_priceInfo)
            if r:  sku_promoPrices = r.group(1)

            r = re.search(r'"promotionList":(\[.+?\]|null)', sku_priceInfo)
            if r:  sku_promoList = r.group(1)

            r = re.search(r'"suggestivePromotionList":(\[.+?\]|null),', sku_priceInfo)
            if r:  sku_suggestPromoList = r.group(1)
            
            r = re.search(r'"wrtInfo":{(.+?)}', sku_priceInfo)
            if r: sku_wrtInfo = r.group(1)
            #print '# price : ', sku_prices, sku_promoPrices, sku_promoList, sku_suggestPromoList, sku_wrtInfo
            #print '# price : ', sku_id, sku_wrtInfo

            # 初始化变量
            sku_attrid, sku_attrvals, sku_stock, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice, sku_presalePrice, sku_presaleAmount, sku_presaleNum = 'def:def', '', '', '', '', '', '', '', '', 0
            m_promoPrice, m_promoList = False, False

            # sku属性值
            if sku_id in self.item_skumap.keys():
                sku_attrid  = self.item_skumap[sku_id]
                sku_attrvals = self.itemSkuAttr(sku_attrid)
                #print '# sku attrs : ', sku_id, sku_attrid, sku_attrvals

            # sku库存
            if sku_id in sku_stockMap.keys(): sku_stock = sku_stockMap[sku_id]

            # sku一口价
            if sku_prices != 'null' and sku_prices != '':
                r = re.search(r'"amount":(.+?),', sku_prices)
                if r:
                    sku_price = r.group(1)
                    fix_prices.append(float(sku_price))

            # sku促销价格
            if sku_promoPrices != 'null' and sku_promoPrices != '':
                r = re.search(r'"extraPromText":"(\d+)"', sku_promoPrices)
                if r:
                    # sku促销价
                    promoPrice = float(r.group(1))/100
                    sku_promoPrice = '%8.2f' %promoPrice; m_promoPrice = True
                    promo_prices.append(promoPrice)

                    # sku手机专享价
                    r = re.search(r'"price":"(.+?)"', sku_promoPrices)
                    if r:
                        sku_mobiPrice = r.group(1)
                        mobi_prices.append(float(sku_mobiPrice))
                else:
                    # 促销类型
                    promo_type = ''
                    r = re.search(r'"type":"(.+?)"', sku_promoPrices)
                    if r: promo_type = r.group(1)
                    
                    # sku预售价/促销价
                    r = re.search(r'"price":"(.+?)"', sku_promoPrices)
                    if r:
                        if promo_type == '预售价':
                            m_presalePrice = True
                            sku_presalePrice = r.group(1)
                            presale_prices.append(float(sku_presalePrice))
                        else:
                            m_promoPrice = True
                            sku_promoPrice = r.group(1);
                            promo_prices.append(float(sku_promoPrice))

            # 天猫促销
            if not m_promoPrice and sku_promoList != 'null' and sku_promoList != '':
                r = re.search(r'"extraPromText":"(\d+)"', sku_promoList)
                if r:
                    m_promoList = True
                    promoPrice = float(r.group(1))/100
                    sku_promoPrice = '%8.2f' %promoPrice
                    promo_prices.append(promoPrice)
                else:
                    t = re.search(r'"price":"(.+?)"', sku_promoList)
                    if t:
                        m_promoList = True
                        sku_promoPrice = t.group(1)
                        promo_prices.append(float(sku_promoPrice))

            # 聚划算 - jhs
            if sku_suggestPromoList != 'null' and sku_suggestPromoList != '':
                promo_type, promo_price = '', ''

                # 促销类型
                r = re.search(r'"price":"(.+?)".+?"promType":"(.+?)"', sku_suggestPromoList)
                if r:
                    promo_price, promo_type = r.group(1), r.group(2)
                    # 判断是否参加聚划算
                    if promo_type == 'jhs' :
                        sku_jhsPrice = promo_price
                        jhs_prices.append(float(promo_price))
                    elif not m_promoPrice and not m_promoList:
                        sku_promoPrice = promo_price
                        promo_prices.append(float(promo_price))

            # 商品预售 - 双11预售
            if sku_wrtInfo != 'null' and sku_wrtInfo != '':
                t = re.search(r'"groupUC":"(\d+)"', sku_wrtInfo)
                if t: sku_presaleNum = t.group(1)
                 
                t = re.search(r'"price":(\d+),', sku_wrtInfo)
                if t:
                    presaleAmount = float(t.group(1))/100
                    sku_presaleAmount = ('%8.2f' %presaleAmount).strip()
                #print '# presale 1: ', sku_presaleNum, sku_presaleAmount

            # 设置sku基本属性
            a_sku.setSku(sku_id, sku_attrid, sku_attrvals, sku_stock, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice)
            a_sku.setPresale(sku_presalePrice, sku_presaleAmount)
            #print 'set sku : ', sku_id, sku_attrid, ','.join(sku_attrvals), sku_stock, sku_price, sku_promoPrice, sku_mobiPrice, sku_jhsPrice, sku_presalePrice, sku_presaleAmount

            # 放入item对象
            self.skus[sku_id] = a_sku
            
            # 预付人数
            self.item_presaleNum = sku_presaleNum
            # 预付定金
            self.item_presaleAmount = sku_presaleAmount

        # 一口价
        if len(fix_prices) > 0:
            mid_prices.append(Common.median(fix_prices))

        # 商品促销价
        if len(promo_prices) > 0:
            self.item_promoPrice = Common.trim_s(self.itemPrice(promo_prices))
            mid_prices.append(Common.median(promo_prices))

        # 商品移动专享价
        if len(mobi_prices) > 0:
            self.item_mobiPrice = Common.trim_s(self.itemPrice(mobi_prices))
            mid_prices.append(Common.median(mobi_prices))           

        # 商品聚划算价格
        if len(jhs_prices) > 0 :
            self.item_jhsPrice = Common.trim_s(self.itemPrice(jhs_prices))
            mid_prices.append(Common.median(jhs_prices))

        # 商品中位数价格
        if len(mid_prices) > 0:
            self.item_midPrice = ('%8.2f' %min(mid_prices)).strip()

        # 预售价格
        if len(presale_prices)>0: self.item_presalePrice = Common.trim_s(self.itemPrice(presale_prices))

        # 如果sku列表有多于1个sku id，则去掉缺省sku id(def)
        if len(self.skus) > 1 and self.skus.has_key('def') : self.skus.pop('def')

    # 成交记录
    def aDealRecord(self, data):
        # 预处理
        data = data.replace('\\', '')
        d_crawltype = 0; d_timestamps = []

        # 遍历成交记录
        p = re.compile(r'<tr (.+?)</tr>')                
        for m in p.finditer(data):
            deal = m.group(1)
            deal = deal.replace(r'<span class=\"tb-anonymous\">(匿名)</span>', r'')

            # 成交时间
            d_ctime, d_buyer, d_credit, d_member, d_prom, d_price, d_amount = '', '', '', '', '', '', '1'
            d = re.search(r'<td class="dealtime">(.+?)</td>', deal)
            if d: d_ctime = Common.htmlContent(d.group(1)).strip()

            if d_ctime and d_ctime != '':
                d_timestamp = Common.str2timestamp(d_ctime)

                # 到了截止时间1(上次抓取最晚时间), 将抓取类型设置为1, 表示追加的抓取成交
                if self.deal_deadLine > Config.g_zeroValue and d_timestamp <= self.deal_deadLine:
                    d_crawltype = 1

                # 记录成交时间
                if d_crawltype == 0 : d_timestamps.append(d_timestamp)

            # 买家别名
            d = re.search(r'<td class="cell-align-l buyer">(.+?)</div>', deal)
            if d: d_buyer = Common.htmlContent(d.group(1)).strip()

            # 买家信用
            d = re.search(r'<img src="\S+?" title="(\S+?)个买家信用积分" border="\d+" align="\w+" class="rank"\s*/>', deal)
            if d:
                credit_rank = d.group(1)
                if credit_rank in Config.g_TBCreditDict.keys(): d_credit = Config.g_TBCreditDict[credit_rank]

            # 会员级别
            d = re.search(r'<a target="_blank"\s+href="http://vip.taobao.com" title="(\S+?)会员">', deal)
            if d: d_member = d.group(1)

            # 促销类型 ：促销活动
            d = re.search(r'<a title="(.+?)".+?></a>', deal)
            if d: d_prom = d.group(1).strip()
            else:
                # 促销类型 ：手机专享
                d = re.search(r'class="tm-buy-prom"\s+>(\S+?)<', deal)
                if d: d_prom = d.group(1).strip()
                else:
                    # 促销类型 ：预售定金/双11价
                    d = re.search(r'<img src="\S+?" alt="(\S+?)"/>', deal)
                    if d: d_prom = d.group(1).strip()

            # 订单价格
            d = re.search(r'<td class="price"><em>&yen;(\S+?)</em>', deal)
            if d: d_price = d.group(1).strip()

            # <td class="cell-align-l style"> 颜色分类:粉红色<br/>适用年龄:均码<br/>帽围:均码 </td>
            # <img src="http://gi3.md.alicdn.com/tps/i3/T1TTbMXfFmXXbKu7Ha-19-19.png" alt="定金"/>
            # <a title="活动促销 " class="buyer-cu-icon"></a>
            d_attrvals = []
            d = re.search(r'<td class="cell-align-l style">(.+?)</td>', deal)
            if d:
                for val in d.group(1).split('<br/>'):
                    p_val, v_val, attrval = '', '', val.strip()
                    if attrval.find(':') == -1:
                        p_val, v_val = attrval, attrval 
                    else:
                        p_val, v_val = attrval.split(':')

                    attrval = self.defValue(p_val) + ':' + self.defValue(v_val)
                    d_attrvals.append(attrval)

            # 购买数量
            d = re.search(r'<td class="quantity">(\d+)</td>', deal)
            if d: d_amount = d.group(1)

            # 成交抓取类型,买家别名,买家信用级别，买家会员级别,成交时间,购买价格,购买数量,促销类别,属性列表
            a_Deal = Deal()
            
            a_Deal.setDeal(d_crawltype, d_buyer, d_credit, d_member, d_ctime, d_price, d_amount, d_prom, d_attrvals)
            self.deals.append(a_Deal)

        # 返回本页成交时间列表
        return d_timestamps

    # 指定范围内的成交记录
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
        # "ratio":0.1025,"skuId":49797022933,"skuName":"颜色分类:蓝色;尺码:M"
        p = re.compile(r'"ratio":(.+?),"skuId":(\d+),"skuName":"\S+?"')
        for m in p.finditer(data):
            s_ratio, s_id = m.group(1), m.group(2)
            if s_id in self.skus.keys():
                s_percent = '%6.2f' %(float(s_ratio) * 100)
                self.skus[s_id].salePercent = s_percent

    # 评价标签
    def rateTagPercent(self):
        _key = 'item-ratetag'
        if _key not in self.item_pages.keys(): return
        page = self.item_pages[_key][1]

        # 商品评价标签
        m = re.search(r'"innerTagCloudList":\[(.+?)\],"rateSum"', page)
        if m:
            innerTag = m.group(1)
            if innerTag != '': 
                p = re.compile(r'"dimenName":"(.+?)","id":\d+,"tagScaleList":\[(.+?)\],"total"')
                for tag in p.finditer(innerTag):
                    t_name, t_list = tag.group(1), tag.group(2)
                    if t_name not in self.rate_tags.keys():
                        self.rate_tags[t_name] = []
    
                    #"count":13,"index":1,"proportion":41.0,"scale":"偏小"
                    tp = re.compile(r'"count":(\d+),"index":\d+,"proportion":(.+?),"scale":"(\S+?)"')
                    for t in tp.finditer(t_list):
                        t_count, t_prop, t_scale = t.group(1), t.group(2), t.group(3)
                        self.rate_tags[t_name].append((t_scale, t_count, t_prop))
 
        # 大家都在说
        m = re.search(r'"tagClouds":\[(.+?)\],"userTagCloudList"', page)
        if m:
            tagClouds = m.group(1)
            if tagClouds != '':
                p = re.compile(r'"count":(\d+),"id":"\d+","posi":(\w+),"tag":"(.+?)"')
                for t in p.finditer(tagClouds):
                    t_count, t_posi, t_tag = t.group(1), t.group(2), t.group(3).strip()
                    if t_posi == 'true' :
                        t_posi =  '1'  # 正面印象
                    else:
                        t_posi = '-1'  # 负面印象
                    self.everyone_tags.append((t_tag, t_count, t_posi))
                    #print t_name, t_tag, t_count, t_posi
    '''

    # 解析商品网页
    #def antPage(self, _time, _sid, _id, _pages):
    def antPage(self, crawl_obj):
        if crawl_obj.item_pages != {}:
            self.itemPage(crawl_obj.crawling_time, crawl_obj.shop_id, crawl_obj.item_id, crawl_obj.item_pages)

            val  = (crawl_obj.crawling_time,crawl_obj.shop_id,crawl_obj.item_name,'',crawl_obj.deal_deadLine,0.0)
            self.itemCrawl(val)
            self.itemConfig()
            #self.itemPicture()
            #self.itemPromises()
            self.itemFavorites()
            self.itemStock()
            #self.itemSku()

            #self.dealSkuPercent()
            #self.rateTagPercent()
            
            self.itemStatus()
            #self.outItemCrawl()

    # 评价标签序列化
    def tag_s(self):
        s = ''
        for (key, tags) in self.rate_tags.items():
            if len(tags) > 0:
                s_tag = (key + ':')
                for tag in tags: s_tag += (','.join(tag) + ';')
                s += s_tag[:-1] + '|'
        return s[:-1]

    # 输出TMItem
    def outItemSql(self):
        # 宝贝图片链接
        pic1_url,pic2_url,pic3_url,pic4_url = '','','','' 

        if len(self.item_picUrls) > 0: pic1_url = self.item_picUrls[0]
        if len(self.item_picUrls) > 1: pic2_url = self.item_picUrls[1]
        if len(self.item_picUrls) > 2: pic3_url = self.item_picUrls[2]
        if len(self.item_picUrls) > 3: pic4_url = self.item_picUrls[3]

        # 主标题是否变化
        title_change  = ('0' if self.crawled_title == self.item_title else '1') 

        # 主图是否变化
        mainPic_change= ('0' if self.crawled_img == self.item_mPicUrl else '1')

        # 宝贝印象标签
        impr_tag  = self.tag_s()

        # 大家认为
        everyone_tag = self.everyTag_s()

        # 是否包邮
        postageFree = '1' if self.item_postFree else '0'

        # 抓取时间,店铺ID,商品ID,商品名称,商品链接,商品收藏数,商品规格参数,后台父类目ID,后台叶子类目ID,上新时间,上架时间,下架时间,主标题,主标题是否变化,副标题,主图链接,主图是否变化,主图文件路径,图片1链接,图片2链接,图片3链接,图片4链接,一口价,促销价,手机专享价,聚划算价格,预售价格,预付定金,预付人数,优惠信息,天猫积分,月销量,是否包邮,累计评价,商品服务承诺,产品与描述相符得分,大家印象标签列表,大家认为,累计销量,商品中位数价格
        item = (Common.time_s(self.crawling_time),self.shop_id,self.item_id,self.item_name,self.item_url,self.item_favorites,self.outItemParams(),self.item_rootCatId,self.item_catId,Common.day_s(self.item_newTime),Common.time_s(self.item_onTime),Common.time_s(self.item_offTime),self.item_title,title_change,self.item_subtitle,self.item_mPicUrl,mainPic_change,self.item_mPicPath,pic1_url,pic2_url,pic3_url,pic4_url,self.item_fixPrice,self.item_promoPrice,self.item_mobiPrice,self.item_jhsPrice,self.item_presalePrice,self.item_presaleAmount,self.item_presaleNum,self.item_coupon,self.item_tmCount,self.item_sellCount,postageFree,self.item_rateTotal,','.join(self.item_promises),self.item_gradeAvg,impr_tag,everyone_tag,self.deal_totalNum,self.item_midPrice)
        return item
