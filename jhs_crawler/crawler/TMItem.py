#-*- coding:utf-8 -*-
#!/usr/bin/env python

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
#sys.path.append('../')

import re
import base.Common as Common
#import Common
import base.Config as Config
#import Config
from Item import Item

class TMItem(Item):
    '''A class of tmall item'''
    def __init__(self):
        # parent construct
        Item.__init__(self)

        # 店铺类型
        self.shop_type = Config.TMALL_TYPE

        # 抓取设置
        #self.deal_pageSize = Config.tmall_dealPageSize
        #self.deal_maxPages = Config.tmall_dealMaxPages

    # 商品页面
    def itemPage(self, url):
        # 商品链接
        self.item_url = url

        # 商品详情页
        page = self.crawler.getData(url, Config.tmall_home)
        if not page or page == '': raise Common.InvalidPageException("Invalid Item Found")

        # 没有找到相应的商品信息 - 天猫
        m = re.search(r'<div class="errorDetail">\s+?<h2>很抱歉，您查看的商品找不到了！</h2>', page, flags=re.S)
        if m:
            self.item_page   = None
            raise Common.NoItemException("# itemPage : No tm item found")

        # 匹配shop_id, item_id
        #<div id="LineZing" pagetype="2" shopid="73217422" tmplid="" itemid="40348828982"></div>
        m = re.search(r'<div id="LineZing".*?shopid="(\d+)".*?itemid="(\d+)"></div>', page)
        if m:
            self.item_page = page
            self.shop_id, self.item_id = m.group(1), m.group(2)
        else:
            print '# itemPage: Invalid item page, url=%s' %url
            raise Common.InvalidPageException("# itemPage %s : Invalid shop/item id found" %self.item_url)

        # 保存商品页
        #self.item_pages.append(('%s-item-home' %self.shop_type, self.item_url, self.item_page))
        self.item_pages['item-home'] = (self.item_url, self.item_page)

    # item configuration
    def itemConfig(self):
        page = self.item_page

        # 商品名称
        m = re.search(r'<title>(.+?)</title>', page, flags=re.S)
        if m:
            title = Common.htmlDecode_s(m.group(1).strip())
            self.item_name = title.split('-tmall')[0].strip()

        # SPU ID
        m = re.search(r'"spuId":"(\d+)"', page)
        if m: self.item_spuId = m.group(1)
        else: raise Common.InvalidPageException("# itemPage : Invalid item spu id found")

        # 掌柜ID
        m = re.search(r'"sellerId":(\d+)', page)
        if m: self.item_sellerId = m.group(1)
        else: raise Common.InvalidPageException("# itemPage : Invalid item seller id found")

        # 移动web页
        wap_url  = 'http://detail.m.tmall.com/item.htm?id=%s' % (self.item_id)
        wap_page = self.crawler.getData(wap_url, self.item_url, terminal='1')
        if not wap_page or wap_page == '':
            raise Common.InvalidPageException("# itemConfig : Invalid item wap page found")

        #self.item_pages.append(('%s-item-wap' %self.shop_type, wap_url, wap_page))
        self.item_pages['item-wap'] = (wap_url, wap_page)

        # 商品月成交
        m = re.search(r'"sellCount":(\d+)', wap_page)
        if m: self.item_sellCount = m.group(1)

        # 评价记录数
        r_url = 'http://dsr.rate.tmall.com/list_dsr_info.htm?itemId=%s&spuId=%s&sellerId=%s&callback=%s' %(self.item_id, self.item_spuId, self.item_sellerId, Common.jsonCallback())
        ratenum_page = self.crawler.getData(r_url, self.item_url)
        if not ratenum_page or ratenum_page == '': return

        # 保存评价记录数页
        #self.item_pages.append(('%s-item-ratenum' %self.shop_type, r_url, ratenum_page))
        self.item_pages['item-ratenum'] = (r_url, ratenum_page)

    # 商品收藏数
    def itemFavorites(self):
        page = self.item_page
        m = re.search(r'"apiBeans":"(http://count.tbcdn.cn/counter3\?keys=(.+?),(.+?))"', page)
        if m:
            url = m.group(1) + '&callback=' + Common.jsonCallback()
            data = self.crawler.getData(url, self.item_url)

            if data and data != '':
                #self.item_pages.append(('%s-item-favorite' %self.shop_type, url, data))
                self.item_pages['item-favorite'] = (url, data)

    """
    # 成交记录SKU占比
    def dealSkuPercent(self):
        m = re.search(r'"recordExtUrl":"(\S+?)"', self.item_page)
        if m:
            deal_sku_url  = m.group(1) + '&callback=' + Common.jsonCallback()
            data = self.crawler.getData(deal_sku_url, self.item_url)
            if not data or len(data) == 0: return
            #self.item_pages.append(('%s-item-dealsku' %self.shop_type, deal_sku_url, data))
            self.item_pages['item-dealsku'] = (deal_sku_url, data)

    # 评价标签
    def rateTagPercent(self):
        # order=1 按时间倒排
        rate_tagUrl = 'http://rate.tmall.com/listTagClouds.htm?isAll=true&isInner=true&itemId=%s&callback=%s' %(self.item_id, Common.jsonCallback())
        page = self.crawler.getData(rate_tagUrl, self.item_url)

        # 保存评价标签页
        if not page or page == '': return
        #self.item_pages.append(('%s-item-ratetag' %self.shop_type, rate_tagUrl, page))
        self.item_pages['item-ratetag'] = (rate_tagUrl, page)

    # 成交记录
    def aDealRecord(self, data):
        # To check deal page
        if not data or data == '': 
            raise Common.InvalidPageException('# aDealRecord : Invalid deal page found')

        # 去掉转义符
        data = data.replace('\\', '')

        # 无成交记录
        m = re.search(r'<p class="attention naked">暂时还没有买家购买此宝贝。</p>', data)
        if m:
            #print '# aDealRecord : no deal', self.shop_type, self.item_id, data
            return
        
        # 系统太累了
        m = re.search(r'<p class=\"attention naked\">系统太累了，要不您过段时间再来看吧。</p>', data)
        if m:
            print '# aDealRecord : busy website', self.shop_type, self.item_id, data
            raise Common.InvalidPageException('# aDealRecord : busy website')

        # 有成交记录
        m = re.search(r'<table summary="成交记录"', data)
        if not m:
            print '# aDealRecord : invalid deal page', self.shop_type, self.item_id, data
            raise Common.InvalidPageException('# aDealRecord : Invalid deal page found')

        p = re.compile(r'<tr (.+?)</tr>')
        for m in p.finditer(data):
            d = re.search(r'<td class="dealtime">(.+?)</td>', m.group(1))
            if not d: continue

            d_ctime = Common.htmlContent(d.group(1)).strip()
            d_timestamp = Common.str2timestamp(d_ctime)

            # 到了截止时间2(本次抓取最早时间,追加抓取)，不再抓取
            if self.deal_deadLine2 > Config.g_zeroValue and d_timestamp <= self.deal_deadLine2:
                self.deal_stopCrawl = True
                break

    # 指定范围内的成交记录
    def dealRecords(self):
        # 成交记录第1页
        data = self.crawler.getData(self.deal_url, self.item_url)
        self.aDealRecord(data)
        d_content = data

        # monthly deals
        monthly_deals = (int)(self.item_sellCount)
        if monthly_deals > self.deal_pageSize:
            d_url = self.deal_url
            pages = int(monthly_deals / self.deal_pageSize) + 1
            if pages > self.deal_maxPages: pages = self.deal_maxPages

            for i in range(1, pages):
                if self.deal_stopCrawl: break

                d_url = re.sub(r'bid_page=' + str(i), r'bid_page=' + str(i + 1), d_url)
                data = self.crawler.getData(d_url, self.item_url)
                self.aDealRecord(data)

                d_header   = '<!-- url=%s -->\n' %d_url
                d_content += (d_header + data)

        # 保存成交页全部页
        #self.item_pages.append(('item.deal', self.deal_url, d_content))
        self.item_pages['item.deal'] = (self.deal_url, d_content)
    """

    # 解析商品详细内容
    def antPage(self, url):
        self.itemPage(url)
        if self.item_page and self.item_page != '':
            self.itemConfig()
            self.itemFavorites()
            #self.rateTagPercent()
        
            #self.crawler.useCookie(True)
            #self.dealSkuPercent()

# if __name__ == '__main__':
#     items = [41966174962]
#     for i_id in items:
#         url = 'http://detail.tmall.com/item.htm?id=%d' %i_id
#         print '# ', i_id, url
#         i = TMItem()
#         i.antPage(url)
#         i.outItem()


        
